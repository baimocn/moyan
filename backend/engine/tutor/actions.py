"""教学动作（讲解 / 判定分支 / 章末考）

依赖注入：TutorActions 由 Service 容器装配（router/judge/quiz），
不再引用模块级单例。流程编排在 service.py；这儿只做"一个动作"。
"""
from __future__ import annotations

import asyncio
import re
import time
from typing import AsyncIterator

from ... import storage
from ...models import repo
from ..persona import persona_book_hits
from ..prompts import (TEACHER_SYSTEM_PROMPT, TEACHER_TURN_HINT,
                       student_profile)
from ..providers import EV_FINISH, EV_META, EV_TEXT
from ..schemas import Correctness, Decision, Difficulty, QuestionSpec, TutorState
from .session import TutorSession

# 学生施压的粗判（宽松苏格拉底策略 D3 + arXiv 2607.19371 五类施压）：
# 直接要答案 / 逐步套取 / 角色重构 / 情绪施压 → 计入施压计数；连续 ≥3 次强制 hint_level=3
_SOLICIT_PATTERNS = (
    "答案", "告诉我", "直接说", "别卖关子", "说人话", "给提示也没用",
    "再提示", "多一点提示", "再说一点", "那第二步", "下一步呢", "你就说是不是",
    "假如你是学生", "你现在是学生", "假装你是",
    "很急", "好烦", "烦死了",
)

def _bump_solicit(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in _SOLICIT_PATTERNS)


def fetch_context(ses: TutorSession, kp_name: str) -> str:
    """按知识点检索章节相关片段（D9 微点注入；无嵌入时的简化检索：文本定位）。"""
    try:
        md = (storage.get_chapter(ses.doc_id, ses.chapter_index) or {}).get("markdown", "")
    except Exception:
        md = ""
    if not md:
        return ""
    pos = md.find(kp_name)
    if pos < 0 and len(kp_name) >= 4:
        pos = md.find(kp_name[:4])
    if pos >= 0:
        start = max(0, pos - 100)
        return md[start:start + 550].replace("\n", " ")
    return md[:400].replace("\n", " ")


def _question_payload(q: QuestionSpec) -> dict:
    return {
        "question_id": q.question_id, "type": q.question_type.value,
        "stem": q.stem,
        "options": [{"key": o.key, "text": o.text} for o in q.options],
        "difficulty": q.difficulty.value,
    }


# 判断反馈不能泄漏答案（真实引擎验收发现的支架崩塌变体）：
# LLM 反馈可能点名"选对了答案 A"或引用正确选项文字，学生看后可直接复选通关。
_OPTION_KEY_RE = re.compile(r"\b[A-F]\b")


def _sanitize_feedback(text: str, q: QuestionSpec | None) -> str:
    """对展示给学生的反馈做程序级兜底：只遮正确项的文字与字母，保留引导。

    2026-08-29 试聊教训：此前把全部选项文字都打码，指向性提示变成"是□、□还是□"，
    学生无从选择——干扰项文字不构成泄漏，应保留。
    """
    if not text or q is None or not q.options:
        return text
    out = text
    correct_keys = set(q.correct_answer or [])
    for o in q.options:
        t = (o.text or "").strip()
        if o.key in correct_keys and len(t) >= 2:
            out = out.replace(t, "□")          # 正确项文字（唯一泄漏点）
    for k in [o.key for o in q.options]:
        out = _OPTION_KEY_RE.sub("□", out)     # 裸选项字母 A-F（含正确字母）
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip().strip("□").strip()


class TutorActions:
    """把一个教学动作做成可独立测试的类。"""

    def __init__(self, router, judge, quiz, reviewer=None, container=None):
        self.router = router
        self.judge = judge
        self.quiz = quiz
        if reviewer is None:
            from ..reviewer import Reviewer
            reviewer = Reviewer(router, container=container)
        self.reviewer = reviewer
        self._review_count = 0

    def _should_review(self, ses: TutorSession, solicit_was: int = 0) -> bool:
        """输出后裁判采样（off|sample|on，MOYAN_TEACHING_REVIEWER）。

        sample：第 1 次判定不审（裁判 ~30s+，开局就拖慢首体验），之后每 5 判一审；
        高风险（重讲≥2 / 学生施压≥3）必审。
        """
        from ...settings import app_settings
        mode = (app_settings.teaching_reviewer or "sample").lower()
        if mode == "on":
            return True
        if mode == "off":
            return False
        return ((self._review_count > 1 and (self._review_count - 1) % 5 == 0)
                or ses.reteach_count >= 2 or solicit_was >= 3)

    # ---------- 讲解 ----------

    async def explain(self, ses: TutorSession, user_text: str = "") -> AsyncIterator[dict]:
        # 讲解态收到用户插话：显式收束一句（此前被静默忽略，用户困惑"怎么不判分"）
        if user_text.strip():
            yield {"type": EV_TEXT, "delta": "（你插的那句我记下了——先讲完这段就回你。）\n\n"}
        kp = ses.plan.kps[ses.kp_idx] if ses.plan and ses.kp_idx < len(ses.plan.kps) else None
        if kp is None:
            yield {"type": EV_TEXT, "delta": "知识点已讲完，进入章节考核。"}
            async for ev in self._start_exam(ses):
                yield ev
            return
        mode = "换一种讲法" if ses.reteach_count >= 2 else \
            ("再讲一遍" if ses.last_decision == Decision.reteach else "讲解")
        # 数据驱动（synapse Groove/Tracer）：历史效果更偏好"换讲法"则跳级
        if ses.reteach_count < 2 and kp is not None:
            data_mode = repo.best_strategy(ses.doc_id, kp.skill_id, min_samples=3)
            if data_mode == "alternative_explanation":
                mode = "换一种讲法"
        ses.last_context = fetch_context(ses, kp.name)
        profile = student_profile(weaknesses=list(ses.weak.values()))
        hint = TEACHER_TURN_HINT.format(
            context=ses.last_context or "（教材该处扫描不清晰，尽量结合前后文）",
            kp_name=kp.name,
            student_profile=profile,
        )
        msgs = [
            {"role": "system", "content": TEACHER_SYSTEM_PROMPT.format(student_profile=profile)},
            {"role": "user", "content": f"请{mode}知识点「{kp.name}」。{hint}"},
        ]
        # 出题与讲解流并行（2026-08-29 性能：此前串行空等 ~28s，题目参数在开流前已齐备）
        quiz_task = asyncio.create_task(self.quiz.make_question(
            context=ses.last_context, weak_points=kp.skill_id or kp.name,
            difficulty=Difficulty.easy,
            topic=f"{ses.chapter_title}/{kp.name}",
            question_id=f"{kp.id}/q1",
        ))
        explain_buf: list[str] = []
        usage: dict = {}
        async for ev in self.router.chat_stream(msgs, temperature=0.4):
            if ev["type"] == EV_TEXT:
                explain_buf.append(ev["delta"])
            elif ev["type"] == EV_FINISH:
                usage = ev.get("usage") or {}
            yield ev
        ses.last_explain = "".join(explain_buf)
        ses.turn_history.append({"role": "assistant", "kind": "explain",
                                 "content": ses.last_explain, "usage": usage})

        q = await quiz_task
        # 出题 tokens 并进本轮 usage（成本审计）
        qu = getattr(q, "usage", {}) or {}
        if qu:
            usage["prompt_tokens"] = usage.get("prompt_tokens", 0) + qu.get("prompt_tokens", 0)
            usage["completion_tokens"] = usage.get("completion_tokens", 0) + qu.get("completion_tokens", 0)
        ses.current_question = q
        ses.state = TutorState.question
        yield {"type": "question", "question": _question_payload(q)}
        yield {"type": EV_META, "state": ses.state.value, "kp": kp.name,
               "quiz_ms": getattr(q, "latency_ms", None)}
        yield {"type": EV_FINISH, "finish_reason": "question"}

    # ---------- 判定 ＋ 分支 ----------

    async def evaluate(self, ses: TutorSession, user_text: str) -> AsyncIterator[dict]:
        q = ses.current_question
        if q is None:
            ses.state = TutorState.explain
            yield {"type": EV_TEXT, "delta": "（回到讲解）"}
            yield {"type": EV_FINISH, "finish_reason": "reset"}
            return

        # 施压计数：命中即 +1，连续 ≥3 次强制 hint_level=3（D3 宽松策略）
        ses.solicit_count = ses.solicit_count + 1 if _bump_solicit(user_text) else 0
        effective_level = 3 if ses.solicit_count >= 3 else ses.hint_level
        _t0 = time.perf_counter()
        j = await self.judge.judge(q, user_text, ses.last_context, ses.solicit_count,
                                   hint_level=effective_level)
        perf = {"judge_ms": int((time.perf_counter() - _t0) * 1000)}
        solicit_was = ses.solicit_count
        ses.solicit_count = 0
        # 脚手架阶梯：答错/部分对升一级（最多 3），答对降一级（fading 撤除支持）
        if j.correctness_level == Correctness.correct:
            ses.hint_level = max(ses.hint_level - 1, 0)
        elif j.correctness_level in (Correctness.incorrect, Correctness.partial_correct):
            ses.hint_level = min(ses.hint_level + 1, 3)
        for wp in j.weak_points:
            ses.weak[wp.skill_id] = wp.mastery
        ses.turn_history.append({"role": "user", "kind": "answer", "content": user_text})
        ses.turn_history.append({"role": "assistant", "kind": "judge", "content": j.model_dump_json()})

        feedback_text = j.feedback.positive
        for part in (j.feedback.correction, j.feedback.hint):
            if part:
                feedback_text += f"\n{part}"
        # 防答案泄漏（程序级兜底）：仅在同题还会再见时需要；skip 后不再回看本题，
        # 抹除只会把"删除异常"这类答对关键词也打码（2026-08-29 实测），故按分支豁免。
        if j.decision != Decision.skip:
            feedback_text = _sanitize_feedback(feedback_text, q)

        # 分支状态先更新，巩固题任务才能在裁判期间并行出题（2026-08-29 性能改造）
        ses.last_decision = j.decision
        correct_now = j.correctness_level.value in ("correct", "partial_correct")
        ses.wrong_streak = 0 if correct_now else ses.wrong_streak + 1
        if correct_now:
            ses.reteach_count = 0   # 答对即重置"重讲次数"（修：原来在 explain 里被提前清零，保护永不触发）
        quiz_task = None
        if j.decision == Decision.practice_question and ses.wrong_streak < 3:
            wp = j.weak_points[0].skill_id if j.weak_points else \
                (q.knowledge_points[0] if q.knowledge_points else "")
            quiz_task = asyncio.create_task(self.quiz.make_question(
                context=ses.last_context, weak_points=wp,
                difficulty=Difficulty.easy if ses.wrong_streak >= 2 else Difficulty.medium,
                topic=f"{ses.chapter_title}/{wp}",
                question_id=f"{wp}/q{ses.wrong_streak + 1}",
            ))

        # 输出后裁判（防支架崩塌）：与巩固题并行跑；每次判定计数（第 1 次不审）
        review = None
        self._review_count += 1
        if self._should_review(ses, solicit_was):
            _t1 = time.perf_counter()
            review = await self.reviewer.review_feedback(
                stem=q.stem, correct="；".join(q.correct_answer),
                student=user_text, feedback=feedback_text)
            perf["review_ms"] = int((time.perf_counter() - _t1) * 1000)
            if review and review.get("violations"):
                yield {"type": "meta", "guard": review}
            else:
                scores = (review or {}).get("scores") or {}
                if scores and min(scores.values()) < 0.5:
                    # 质量四维有一维不达标：显式暴露给前端/审计（此前 note 只落库不处置）
                    yield {"type": "meta", "guard": {"quality_low": True, "scores": scores,
                                                     "note": review.get("note", "")}}

        yield {"type": EV_TEXT, "delta": feedback_text}
        judgement_payload = {
            "correctness": j.correctness_level.value, "score": j.score,
            "decision": j.decision.value, "confidence": j.confidence,
            "weak_points": [{"skill_id": w.skill_id, "mastery": w.mastery} for w in j.weak_points],
            "usage": getattr(j, "usage", {}),
        }
        if review:
            judgement_payload["review"] = review
        yield {"type": "judge", "judgement": judgement_payload}
        yield {"type": EV_META, "perf": perf}

        # 策略反馈入账（Groove）：skill × 分支 → 短程效果 + 裁判质量
        try:
            skill = next((w.skill_id for w in j.weak_points), None) \
                or (q.knowledge_points[0] if q.knowledge_points else "")
            repo.save_strategy_feedback(
                ses.doc_id, skill, j.decision.value, j.score,
                bool(review and review.get("passed")) if review else True,
                ses.session_id,
                user_id=ses.user_id or None,
            )
        except Exception:  # noqa: BLE001 反馈日志失败不影响教学
            pass

        # 转移表（服务端写死）
        if j.decision == Decision.skip:
            ses.kp_idx += 1
            ses.reteach_count = 0   # 进入新知识点，重讲计数归零
            ses.hint_level = 0      # 新知识点脚手架归零（重新从诊断级开始）
            ses.state = TutorState.explain
            next_kp = ses.plan.kps[ses.kp_idx].name if ses.plan and ses.kp_idx < len(ses.plan.kps) else None
            yield {"type": EV_META, "branch": "next", "next": next_kp or "章节考", "correct": True}
            # 过渡报站（2026-08-29 试聊：换知识点无桥句，用户迷路）
            if next_kp:
                yield {"type": EV_TEXT, "delta": f"（这题过了。下一站：「{next_kp}」。）\n\n"}
                async for ev in self.explain(ses):
                    yield ev
            else:
                yield {"type": EV_TEXT, "delta": "（最后一个知识点过完——章末考开始。）\n\n"}
                async for ev in self._start_exam(ses):
                    yield ev
            return

        if j.decision in (Decision.reteach, Decision.alternative_explanation):
            ses.reteach_count = min(ses.reteach_count + 1, 2)
            ses.state = TutorState.explain
            yield {"type": EV_META, "branch": j.decision.value}
            async for ev in self.explain(ses):
                yield ev
            return

        if j.decision == Decision.practice_question:
            if ses.wrong_streak >= 3:
                ses.wrong_streak = 0
                ses.last_decision = Decision.alternative_explanation
                ses.reteach_count = 2   # 强制走"换一种讲法"（降档）
                ses.state = TutorState.explain
                yield {"type": EV_META, "branch": "downgrade"}
                async for ev in self.explain(ses):
                    yield ev
                return
            nq = await quiz_task
            ses.current_question = nq
            perf["quiz_ms"] = getattr(nq, "latency_ms", None)
            ses.state = TutorState.question
            yield {"type": "question", "question": _question_payload(nq)}
            yield {"type": EV_FINISH, "finish_reason": "question"}
            return

    # ---------- 章末考 ----------

    async def _start_exam(self, ses: TutorSession) -> AsyncIterator[dict]:
        keys = list(ses.weak.keys())[:5] or \
            ([p.name for p in (ses.plan.kps if ses.plan else [])[:3]] or ["本章要点"])
        # 考题也要教材上下文（此前 context="" 违反"只依据教材"）：skill_id → 知识点名 → 微点
        name_of: dict[str, str] = {}
        for p in (ses.plan.kps if ses.plan else []):
            name_of.setdefault(p.skill_id, p.name)
            name_of.setdefault(p.name, p.name)
        contexts = {k: fetch_context(ses, name_of.get(k, k)) for k in keys}
        exam = await self.quiz.chapter_exam(ses.chapter_title, ses.chapter_title, keys,
                                            contexts=contexts)
        ses.exam_questions = [eq.question for eq in exam.questions][:3]
        ses.exam_idx = 0
        ses.state = TutorState.chapter_exam
        yield {"type": "question-batch", "questions": [
            {"index": i, "stem": q.stem, "type": q.question_type.value,
             "options": [{"key": o.key, "text": o.text} for o in q.options]}
            for i, q in enumerate(ses.exam_questions)
        ]}
        yield {"type": EV_FINISH, "finish_reason": "exam"}

    async def exam_turn(self, ses: TutorSession, answer: str) -> AsyncIterator[dict]:
        if ses.exam_idx >= len(ses.exam_questions):
            report = self._aggregate_exam(ses)
            ses.state = TutorState.done
            yield {"type": "report", "report": report}
            yield {"type": EV_TEXT, "delta": report["summary"]}
            yield {"type": EV_FINISH, "finish_reason": "exam-done"}
            return
        q = ses.exam_questions[ses.exam_idx]
        j = await self.judge.judge(q, answer, ses.last_context)
        ses.exam_scores[q.question_id] = j.score
        for wp in j.weak_points:
            ses.weak[wp.skill_id] = wp.mastery
        ses.exam_idx += 1
        yield {"type": "judge", "judgement": {
            "correctness": j.correctness_level.value, "score": j.score,
            "decision": j.decision.value,
        }}
        feedback = j.feedback.positive + (f"\n💡 {j.feedback.hint}" if j.feedback.hint else "")
        feedback = _sanitize_feedback(feedback, q)   # 防答案泄漏
        yield {"type": EV_TEXT, "delta": feedback}
        if ses.exam_idx < len(ses.exam_questions):
            yield {"type": "question", "question": _question_payload(ses.exam_questions[ses.exam_idx])}
        yield {"type": EV_META, "exam_progress": f"{ses.exam_idx}/{len(ses.exam_questions)}"}
        yield {"type": EV_FINISH, "finish_reason": "exam-turn"}

    def _aggregate_exam(self, ses: TutorSession) -> dict:
        scores = ses.exam_scores
        avg = (sum(scores.values()) / len(scores)) if scores else 0.0
        weak = [k for k, v in ses.weak.items() if v == "low"]
        summary = f"本章掌握度 {avg * 100:.0f}%" + \
            (f"；需要复习：{'、'.join(weak[:4])}" if weak else "；本章掌握不错")
        return {
            "chapter": ses.chapter_title,
            "avg_score": round(avg, 2),
            "weak_points": weak,
            "scores": {k: round(v, 2) for k, v in scores.items()},
            "summary": summary,
        }