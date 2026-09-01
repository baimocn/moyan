"""墨衍 · 主引擎横向评测（真实调用，耗 token）

同一组样例 → 各候选模型跑三任务：
  ① 讲解（TEACHER 体系，固定教材片段/知识点）
  ② 判定（同一题/同一错误回答 → AnswerJudgement）
  ③ 出题（同一知识点 → QuestionSpec）
并让裁判模型对讲解打分（teaching_quality 0-5 + 判据违规）。
结果存 data/work/model_bench/results.json，控制台打印摘要。

运行：python tools/model_bench.py [模型名...]（缺省跑候选全部）
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import dotenv_values
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from backend.engine.prompts import (JUDGE_INSTRUCTION, KNOWLEDGE_PLAN_INSTRUCTION,
                                    QUIZ_INSTRUCTION, TEACHER_SYSTEM_PROMPT,
                                    TEACHER_TURN_HINT)
from backend.engine.schemas import (AnswerJudgement, Difficulty, QuestionSpec,
                                    QuestionType)
from backend.engine.structured import chat_json
from backend import storage

DOC_ID = "20260828-203702-a3ee19"      # docling 导入的《操作系统》文档
CHAPTER = 4                              # 第二章 进程管理
KP_NAME = "进程的状态与转换"
CONTEXT = ""

BENCH_REVIEW_PROMPT = """你是教学质检员。请评审一次 AI 讲解是否符合"苏格拉底教学铁律"，并打质量分。
判据：
1. 一次只讲一个知识点（禁止一次堆砌 3 个以上新概念/列表轰炸）；
2. 以一个问题收尾（讲完应停下来等学生答，不自问自答）；
3. 严格依据教材（教材没有的内容须声明"不在教材里"或承认不知道）；
4. 不泄漏最终答案/不替学生解完整题；
5. 有类比但不过度发挥。
输出 JSON：{{"passed": bool, "violations": [{{"criterion","severity","evidence"}}],
"teaching_quality": 0-5 整数, "comment": "一句话点评"}}
【教材片段】{context}
【讲解文本】{text}"""


class BenchReview(BaseModel):
    passed: bool = True
    violations: list = Field(default_factory=list)
    teaching_quality: int = Field(3, ge=0, le=5)
    comment: str = ""


CANDIDATES = [
    "deepseek-v4-flash", "deepseek-v4-pro", "glm-5.3", "kimi-k3",
    "minimax-m3", "qwen3.8-max", "gpt-5.6-luna",
]


def _load_context() -> str:
    global CONTEXT
    md = (storage.get_chapter(DOC_ID, CHAPTER) or {}).get("markdown", "")
    pos = md.find(KP_NAME)
    start = max(0, pos - 120) if pos >= 0 else 0
    CONTEXT = md[start:start + 900].replace("\n", " ") or "（无上下文）"


def _user_msgs(system: str, user: str) -> list[dict]:
    return [{"role": "system", "content": system},
            {"role": "user", "content": user}]


async def task_explain(client, model) -> dict:
    hint = TEACHER_TURN_HINT.format(context=CONTEXT, kp_name=KP_NAME,
                                    student_profile="学段：大学生；薄弱点：暂无；最近表现：暂无")
    msgs = _user_msgs(TEACHER_SYSTEM_PROMPT.format(student_profile="大学生"), f"请讲解知识点「{KP_NAME}」。{hint}")
    t0 = time.time()
    r = await client.chat.completions.create(model=model, messages=msgs, temperature=0.4)
    text = r.choices[0].message.content or ""
    usage = r.usage
    return {"text": text, "latency_s": round(time.time() - t0, 1),
            "tokens": {"p": getattr(usage, "prompt_tokens", 0) or 0,
                       "c": getattr(usage, "completion_tokens", 0) or 0}}


async def task_judge(client, model) -> dict:
    question = "根据教材，进程和程序是一回事吗？请说明两者的区别。"
    answer = "进程就是一个程序文件，存在硬盘上的那种。"
    msgs = [{"role": "system", "content": JUDGE_INSTRUCTION.format(
        context=CONTEXT, question_stem=question,
        correct_answer="进程是程序运行时的实例；程序是静态文件", student_answer=answer)},
        {"role": "user", "content": "学生累计索要答案次数：0；请按 schema 判定。"}]
    t0 = time.time()
    try:
        j, usage = await chat_json(client, model, msgs, AnswerJudgement, temperature=0,
                                   max_retries=1,
                                   schema_hint="correctness_level/decision 取枚举值",
                                   aliases={"question_id": ["id", "question"]})
        return {"ok": True, "correctness": j.correctness_level.value,
                "decision": j.decision.value, "score": j.score,
                "weak": [w.skill_id for w in j.weak_points],
                "feedback": j.feedback.positive + (f"\n{j.feedback.hint}" if j.feedback.hint else ""),
                "latency_s": round(time.time() - t0, 1),
                "tokens": {k: usage.get(k, 0) for k in ("prompt_tokens", "completion_tokens")}}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}",
                "latency_s": round(time.time() - t0, 1)}


async def task_quiz(client, model) -> dict:
    msgs = [{"role": "user", "content": QUIZ_INSTRUCTION.format(
        context=CONTEXT, weak_points="os/process/state-transition",
        difficulty=Difficulty.medium.value)}]
    t0 = time.time()
    try:
        q, usage = await chat_json(client, model, msgs, QuestionSpec, temperature=0.3,
                                   max_retries=1, aliases={"stem": ["question", "text"]},
                                   schema_hint="question_type 枚举；options [{key,text}]")
        return {"ok": True, "type": q.question_type.value, "stem": q.stem,
                "options": [f"{o.key}:{o.text}" for o in q.options][:6],
                "correct": q.correct_answer, "difficulty": q.difficulty.value,
                "latency_s": round(time.time() - t0, 1),
                "tokens": {k: usage.get(k, 0) for k in ("prompt_tokens", "completion_tokens")}}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}",
                "latency_s": round(time.time() - t0, 1)}


async def task_review(client, model, explain_text: str) -> dict:
    prompt = BENCH_REVIEW_PROMPT.format(context=CONTEXT[:500], text=explain_text[:1600])
    try:
        rv, _ = await chat_json(client, model, [{"role": "user", "content": prompt}],
                                BenchReview, temperature=0, max_retries=1,
                                schema_hint="teaching_quality 0-5 整数")
        return {"passed": rv.passed,
                "teaching_quality": rv.teaching_quality,
                "violations": rv.violations,
                "comment": rv.comment}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:100]}"}


async def main(selected: list[str]) -> int:
    v = dotenv_values(Path(__file__).resolve().parent.parent / ".env")
    client = AsyncOpenAI(base_url=v["MOYAN_AI_MAIN_BASE_URL"],
                         api_key=v["MOYAN_AI_MAIN_KEY"], timeout=300)
    _load_context()
    out_dir = Path(__file__).resolve().parent.parent / "data" / "work" / "model_bench"
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict = {"context_head": CONTEXT[:300], "models": {}}
    for model in selected:
        print(f"\n===== {model} =====", flush=True)
        try:
            ex = await task_explain(client, model)
            print(f"  讲解 {ex['latency_s']}s, {len(ex['text'])}字", flush=True)
            rev = await task_review(client, "deepseek-v4-flash", ex["text"])
            print(f"  裁判: quality={rev.get('teaching_quality')} passed={rev.get('passed')} cm={rev.get('comment','')[:50]}", flush=True)
            jd = await task_judge(client, model)
            print(f"  判定: {jd.get('ok')} correct={jd.get('correctness')}/{jd.get('decision')} {jd.get('latency_s')}s", flush=True)
            qz = await task_quiz(client, model)
            print(f"  出题: {qz.get('ok')} type={qz.get('type')} {qz.get('latency_s')}s", flush=True)
            results["models"][model] = {"explain": ex, "review": rev, "judge": jd, "quiz": qz}
            (out_dir / "results.json").write_text(
                json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
            (out_dir / f"{model.replace('/', '_')}.txt").write_text(ex["text"], encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL: {type(e).__name__}: {str(e)[:160]}", flush=True)
            results["models"][model] = {"error": str(e)[:200]}
    print("\nDONE -> data/work/model_bench/results.json")
    return 0


if __name__ == "__main__":
    sel = sys.argv[1:] or CANDIDATES
    sys.exit(asyncio.run(main(sel)))