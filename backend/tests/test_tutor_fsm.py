"""教学状态机单测（mock 模式：剑锋指向转移表与分支逻辑）

运行：pytest backend/tests/test_tutor_fsm.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from backend.engine.schemas import (AnswerJudgement, Feedback, QuestionSpec,
                                    TutorState)
from backend.engine.tutor.service import TutorService


class _FakeJudge:
    """可按用例返回预定判定的假判定器。"""

    def __init__(self, results: list[AnswerJudgement]):
        self.results = list(results)
        self.calls = 0

    async def judge(self, question, answer, context="", solicit_count=0, hint_level=0):
        r = self.results[min(self.calls, len(self.results) - 1)]
        self.calls += 1
        return r


class _FakeQuiz:
    """返回固定题目/计划的假出题器。"""

    def __init__(self, plan=None):
        from backend.engine.schemas import KnowledgePlan, KnowledgePoint
        self.plan = plan or KnowledgePlan(chapter_id="ch0", chapter_title="第一章",
                                          kps=[KnowledgePoint(id="ch0/kp-1", name="知识点一", skill_id="k1"),
                                               KnowledgePoint(id="ch0/kp-2", name="知识点二", skill_id="k2")])
        self.asked = []

    async def plan_knowledge(self, chapter_id, chapter_title, heading_structure="", preview=""):
        return self.plan

    async def make_question(self, **kw):
        from backend.engine.schemas import Difficulty, QuestionType
        q = QuestionSpec(question_id=kw.get("question_id", "q1"), stem=f"关于{kw.get('weak_points')}的题？",
                         question_type=QuestionType.single_choice,
                         correct_answer=["A"],
                         options=[], knowledge_points=[kw.get("weak_points", "k")],
                         difficulty=kw.get("difficulty") or Difficulty.medium)
        self.asked.append(q)
        return q

    async def chapter_exam(self, chapter_id, chapter_title, wp_names, contexts=None):
        from backend.engine.schemas import ChapterExam, ExamQuestion
        items = []
        for i, w in enumerate(wp_names[:2]):
            q = await self.make_question(weak_points=w, question_id=f"exam-{i}")
            items.append(ExamQuestion(question=q, difficulty=q.difficulty))
        return ChapterExam(chapter_id=chapter_id, chapter_title=chapter_title, questions=items)


class _FakeRouter:
    """假对话路由：固定讲解文本，记录最近一次请求内容（断言讲解模式用）。"""

    def __init__(self):
        self.last_content = ""

    async def chat_stream(self, messages, temperature=0.4):
        self.last_content = messages[-1].get("content", "")
        yield {"type": "start", "model": "fake"}
        for ch in "这是讲解内容。":
            yield {"type": "text-delta", "delta": ch}
        yield {"type": "finish", "finish_reason": "stop"}


@pytest.fixture(autouse=True)
def _fake_storage(monkeypatch):
    """start_chapter 已校验 doc/chapter 存在：用内存清单替代磁盘读取。"""
    from backend.engine.tutor import service as svc
    manifest = [{"index": 0, "title": "第一章", "toc": []}]
    monkeypatch.setattr(svc.storage, "get_chapter_manifest", lambda doc_id: manifest)
    monkeypatch.setattr(svc.storage, "get_chapter",
                        lambda doc_id, idx: {"markdown": "第一章 内容片段。"})


def make_service(judge_results, plan=None) -> TutorService:
    svc = TutorService()
    router = _FakeRouter()
    svc.actions.router = router
    svc.actions.judge = _FakeJudge(judge_results)
    svc.actions.quiz = _FakeQuiz(plan)
    svc._quiz = svc.actions.quiz
    svc._router_for_test = router
    return svc


def grade(correct: bool, decision="skip") -> AnswerJudgement:
    from backend.engine.schemas import Correctness, Decision
    return AnswerJudgement(
        question_id="q1",
        correctness_level=Correctness.correct if correct else Correctness.incorrect,
        score=1.0 if correct else 0.0,
        decision=Decision(decision),
        feedback=Feedback(positive="好", correction="错", hint="想想"),
        confidence=0.9,
    )


async def collect(agen):
    return [ev async for ev in agen]


@pytest.mark.asyncio
async def test_skip_advances_to_next_kp():
    """答对 → skip → 推进到下一个知识点并出下一题。"""
    svc = make_service([grade(True, "skip")])
    ses = await svc.start_chapter("doc-x", 0)
    assert ses.state == TutorState.explain
    await collect(svc.handle_turn(ses.session_id, "开始"))
    assert ses.state == TutorState.question          # 讲解后出题
    events = await collect(svc.handle_turn(ses.session_id, "答案：A"))
    assert any(e["type"] == "judge" for e in events)
    metas = [e for e in events if e["type"] == "meta" and e.get("branch") == "next"]
    assert metas and metas[0]["next"] == "知识点二"    # 推进到 kp-2
    assert ses.kp_idx == 1
    assert ses.state == TutorState.question


@pytest.mark.asyncio
async def test_incorrect_leads_practice_or_reteach():
    """答错 → 薄弱点入账 + 进入练习/重讲分支。"""
    svc = make_service([grade(False, "practice_question")])
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, "开始"))
    events = await collect(svc.handle_turn(ses.session_id, "答案：B"))
    assert any(e["type"] == "judge" for e in events)
    assert any(e["type"] == "question" for e in events)   # 巩固题
    assert ses.state == TutorState.question
    assert ses.wrong_streak == 1


@pytest.mark.asyncio
async def test_three_wrong_downgrades_to_retell():
    """连续 3 次错 → 降档换讲法（发生 downgrade 分支并重新讲解）。"""
    svc = make_service([grade(False, "practice_question")])
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, "开始"))
    seen_downgrade = False
    for _ in range(3):
        evs = await collect(svc.handle_turn(ses.session_id, "答案：B"))
        seen_downgrade = seen_downgrade or any(
            e["type"] == "meta" and e.get("branch") == "downgrade" for e in evs)
    assert seen_downgrade                       # 触发过降档
    assert ses.wrong_streak == 0                # 计数已复位
    assert ses.last_decision.value == "alternative_explanation"


@pytest.mark.asyncio
async def test_exam_flow_reaches_report():
    """知识点全部 skip → 章末考 → 逐题 → 报告 → done。"""
    svc = make_service([grade(True, "skip"), grade(True, "skip"), grade(True, "skip")])
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, "开始"))     # kp1 explain
    await collect(svc.handle_turn(ses.session_id, "A"))        # kp1 skip -> kp2
    evs = await collect(svc.handle_turn(ses.session_id, "A"))  # kp2 skip -> exam
    assert any(e["type"] == "question-batch" for e in evs)
    assert ses.state == TutorState.chapter_exam
    evs = await collect(svc.handle_turn(ses.session_id, "A"))  # 答第一题
    assert any(e["type"] == "judge" for e in evs)
    evs = await collect(svc.handle_turn(ses.session_id, "A"))  # 答第二题（最后一题）
    evs = await collect(svc.handle_turn(ses.session_id, ""))   # 收尾 → 报告
    assert any(e["type"] == "report" for e in evs)
    assert ses.state == TutorState.done


@pytest.mark.asyncio
async def test_unknown_session_returns_error_event():
    svc = make_service([grade(True, "skip")])
    evs = await collect(svc.handle_turn("nope", "hi"))
    assert evs[0]["type"] == "error"


@pytest.mark.asyncio
async def test_reteach_twice_switches_explanation_mode():
    """同知识点连续 reteach：第 1 次"再讲一遍"，第 2 次"换一种讲法"（计数不再被提前清零）。"""
    svc = make_service([grade(False, "reteach"), grade(False, "reteach"),
                        grade(False, "reteach")])
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, "开始"))          # 讲解（首讲）
    assert "请讲解知识点" in svc._router_for_test.last_content
    await collect(svc.handle_turn(ses.session_id, "A"))             # reteach #1
    assert "请再讲一遍知识点" in svc._router_for_test.last_content
    await collect(svc.handle_turn(ses.session_id, "A"))             # reteach #2
    assert "请换一种讲法知识点" in svc._router_for_test.last_content
    assert ses.reteach_count == 2


@pytest.mark.asyncio
async def test_strict_guard_reteach_explains_mock():
    """宽松策略降档：practice_question 连续 3 错 → 强制'换一种讲法'（reteach_count=2）。"""
    svc = make_service([grade(False, "practice_question")])
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, "开始"))
    for _ in range(3):
        await collect(svc.handle_turn(ses.session_id, "答案：B"))
    assert "换一种讲法" in svc._router_for_test.last_content