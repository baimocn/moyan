"""墨衍 · 出题与知识点计划服务（依赖容器注入 client，mock 显式开关）"""
from __future__ import annotations

import logging
import random
import re
import time
import uuid

from .prompts import KNOWLEDGE_PLAN_INSTRUCTION, QUIZ_INSTRUCTION
from .schemas import (ChapterExam, Difficulty, ExamQuestion, KnowledgePlan,
                      KnowledgePoint, QuestionSpec, QuestionType)
from .structured import chat_json

logger = logging.getLogger(__name__)


def _repair_correct_answer(q: QuestionSpec) -> QuestionSpec:
    """键-文一致性校对：模型偶发把 correct_answer 的键标错（文字对、键错），
    洗牌会忠实保留该错误 → 判定按错误键对照，把答对判成不一致（2026-08-29 实测）。
    以模型声明的正确选项文字为准，反向定位 key 并修正。
    """
    want = (q.correct_answer_text or "").strip()
    if not want or not q.correct_answer or not q.options:
        return q
    for o in q.options:
        t = (o.text or "").strip()
        if t == want or (len(want) >= 6 and (want in t or t in want)):
            if [o.key] != q.correct_answer:
                logger.warning("出题键-文不一致已修正：correct_answer %s -> %s",
                               q.correct_answer, o.key)
                q.correct_answer = [o.key]
            break
    return q


def shuffle_options(q: QuestionSpec) -> QuestionSpec:
    """选项洗牌：正确项位置每次随机（同一题源复用时不让学生"背字母"）。

    依据：真实引擎验收发现——判定反馈泄漏"选对了 A"后，若下一题正确项仍在 A，
    学生无脑复选即可通关（支架崩塌变体）。洗牌 + 反馈过滤双保险。
    """
    if len(q.options) <= 1:
        return q
    shuffled = list(q.options)
    random.shuffle(shuffled)
    new_keys = ["A", "B", "C", "D", "E", "F"][:len(shuffled)]
    mapping: dict[str, str] = {}          # 原 key -> 新 key（按洗牌后位置）
    for i, o in enumerate(shuffled):
        mapping[o.key] = new_keys[i]
        o.key = new_keys[i]
    q.options = shuffled
    if q.correct_answer:
        q.correct_answer = [mapping[k] for k in q.correct_answer if k in mapping]
    return q


class QuizService:
    """出题 + 章内知识点计划。引擎：cheap 优先（出题是粗活，省钱），缺省回落 main。"""

    def __init__(self, container=None, mock: bool = False):
        self._client = None
        self._model = ""
        self.mock = bool(mock)
        if container is None or self.mock:
            return
        try:
            base, key, model = container.engine_factory.require_engine(cheap=True)
            self._client = container.engine_factory.build_async_client(base, key)
            self._model = model
        except Exception:
            self.mock = True

    async def plan_knowledge(
        self, chapter_id: str, chapter_title: str,
        heading_structure: str, preview: str = "",
    ) -> KnowledgePlan:
        if self.mock or self._client is None:
            return self._mock_plan(chapter_id, chapter_title, heading_structure, preview)
        messages = [{"role": "user", "content": KNOWLEDGE_PLAN_INSTRUCTION.format(
            chapter_title=chapter_title,
            heading_structure=heading_structure or "（无子标题结构）",
            preview=preview[:800],
        )}]
        try:
            plan, _usage = await chat_json(
                self._client, self._model, messages,
                KnowledgePlan, temperature=0.3, max_retries=1,
                schema_hint="kps 为知识点数组，含 id/name/summary/skill_id",
            )
            plan.chapter_id = chapter_id
            plan.chapter_title = chapter_title
            # 数量硬约束：LLM 只给 1-2 站时视为不合格，退回增强兜底（保证 >=3 站）
            if len(plan.kps) < 3:
                logger.warning(
                    "知识点计划仅 %d 站（不合格），退回增强兜底：%s", len(plan.kps), chapter_title)
                return self._mock_plan(chapter_id, chapter_title, heading_structure, preview)
            return plan
        except Exception as exc:  # noqa: BLE001
            logger.warning("知识点计划生成失败，退回 mock 计划（教学序列会退化）：%s", exc)
            return self._mock_plan(chapter_id, chapter_title, heading_structure, preview)

    def _mock_plan(self, chapter_id: str, chapter_title: str,
                   heading_structure: str, preview: str = "") -> KnowledgePlan:
        """无 LLM 可用时的兜底教学序列：heading → 教材句子 → 三段框架，保证 >=3 站。"""
        heads = [h.strip() for h in (heading_structure or "").split("|") if h.strip()]
        kps = []
        for i, h in enumerate(heads[:8], 1):
            name = h.lstrip("0123456789.、 ") or f"知识点{i}"
            kps.append(KnowledgePoint(
                id=f"{chapter_id}/kp-{i:02d}", name=name,
                summary=f"来自小节：{name}",
                skill_id=f"kp-{i:02d}",
            ))

        # 无子标题结构但有教材片段：按句切分归纳，至少 3 站
        if len(kps) < 3 and preview:
            sents = [s.strip() for s in re.split(r"[。！？；\n]+", preview or "")
                     if s.strip() and len(s.strip()) > 6]
            for i, s in enumerate(sents[:8], len(kps) + 1):
                name = s[:16] + ("…" if len(s) > 16 else "")
                kps.append(KnowledgePoint(
                    id=f"{chapter_id}/kp-{i:02d}", name=name,
                    summary=s[:48],
                    skill_id=f"kp-{i:02d}",
                ))

        # 仍不足 3 站：按"引入→核心概念→应用/小结"三段框架补足（禁整章名当唯一知识点）
        if len(kps) < 3:
            base = chapter_title or "本章"
            frames = [
                ("引入与背景", f"为什么学{base}、解决什么问题"),
                ("核心概念", f"{base}的核心概念与原理"),
                ("应用与小结", f"{base}的典型应用与本节小结"),
            ]
            for i, (name, summary) in enumerate(frames[:8], len(kps) + 1):
                kps.append(KnowledgePoint(
                    id=f"{chapter_id}/kp-{i:02d}", name=name,
                    summary=summary, skill_id=f"kp-{i:02d}",
                ))
                if len(kps) >= 3:
                    break

        return KnowledgePlan(chapter_id=chapter_id, chapter_title=chapter_title, kps=kps[:8])

    async def make_question(
        self, *, context: str, weak_points: str,
        difficulty: Difficulty = Difficulty.medium,
        topic: str = "", question_id: str = "",
    ) -> QuestionSpec:
        if self.mock or self._client is None:
            return self._mock_question(context, weak_points, difficulty, topic, question_id)
        messages = [{"role": "user", "content": QUIZ_INSTRUCTION.format(
            context=context or "（无教材上下文）",
            weak_points=weak_points or "（新知识点）",
            difficulty=difficulty.value,
        )}]
        _t0 = time.perf_counter()
        try:
            q, _usage = await chat_json(
                self._client, self._model, messages,
                QuestionSpec, temperature=0.3, max_retries=1,
                schema_hint="question_type 取枚举值(single_choice 优先)；正确项必须含 correct_answer 选项 key 数组；options 为 [{key,text}]",
                aliases={"stem": ["question", "text"], "question_type": ["type"]},
                list_renames={"options": {"label": "key"}},
            )
            setattr(q, "usage", _usage)   # 成本审计：出题 tokens 挂对象供 actions 合并落库
            setattr(q, "latency_ms", int((time.perf_counter() - _t0) * 1000))
            # question_id 以调用方为准（防 LLM 自拟 id 破坏审计关联）
            q.question_id = question_id or q.question_id or f"{topic}/q-{uuid.uuid4().hex[:6]}"
            q = _repair_correct_answer(q)
            shuffle_options(q)
            return q
        except Exception as exc:  # noqa: BLE001
            logger.warning("出题结构化输出失败，退回 mock 题目：%s", exc)
            return self._mock_question(context, weak_points, difficulty, topic, question_id)

    def _mock_question(self, context: str, weak_points: str, difficulty: Difficulty,
                       topic: str, question_id: str) -> QuestionSpec:
        sentence = next((s for s in re.split(r"[。！？]", context or "")
                         if len(s) >= 12), "教材里的一句话")
        qid = question_id or f"{topic or 'mock'}/q-{uuid.uuid4().hex[:6]}"
        return QuestionSpec(
            question_id=qid, topic=topic,
            question_type=QuestionType.true_false,
            stem=f"判断对错：{sentence}",
            correct_answer=["对"],
            knowledge_points=[weak_points or "kp-mock"],
            difficulty=difficulty,
            explanation="（模拟引擎生成的判断题，配置 MOYAN_AI_MAIN_* 后由 AI 出题）",
        )

    async def chapter_exam(self, chapter_id: str, chapter_title: str,
                           wp_names: list[str],
                           contexts: dict[str, str] | None = None) -> ChapterExam:
        questions: list[ExamQuestion] = []
        for i, w in enumerate(wp_names[:5], 1):
            q = await self.make_question(
                context=(contexts or {}).get(w, ""),
                weak_points=w,
                difficulty=Difficulty.medium if i <= 3 else Difficulty.easy,
                topic=chapter_id, question_id=f"{chapter_id}/exam/{i}",
            )
            questions.append(ExamQuestion(question=q, difficulty=q.difficulty))
        return ChapterExam(chapter_id=chapter_id, chapter_title=chapter_title,
                           questions=questions, summary="出题完成")