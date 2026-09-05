"""引擎柔性参数单测（2026-09-05 放松，Spec=out/引擎放松_spec.md）

1) solicit_loose_threshold 参数化：阈值=1 时施压 1 次即强制阶梯顶格
2) scaffold_max_level 钳制：上限=1 时答错两次阶梯停在 1
3) reviewer_sample_every 参数化：_should_review 采样间隔可配
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from backend.engine.schemas import (AnswerJudgement, Correctness, Decision,
                                    Feedback)
from backend.settings import app_settings


class _RecordingJudge:
    """记录每次 hint_level 的假判定器（其余与 fsm _FakeJudge 同构）。"""

    def __init__(self, results):
        self.results = list(results)
        self.calls = 0
        self.hint_levels = []

    async def judge(self, question, answer, context="", solicit_count=0, hint_level=0):
        r = self.results[min(self.calls, len(self.results) - 1)]
        self.calls += 1
        self.hint_levels.append(hint_level)
        return r


@pytest.fixture(autouse=True)
def _fake_storage(monkeypatch):
    from backend.engine.tutor import service as svc
    manifest = [{"index": 0, "title": "第一章", "toc": []}]
    monkeypatch.setattr(svc.storage, "get_chapter_manifest", lambda doc_id: manifest)
    monkeypatch.setattr(svc.storage, "get_chapter",
                        lambda doc_id, idx: {"markdown": "第一章 内容片段。"})


def _grade(decision="practice_question", level=Correctness.incorrect):
    return AnswerJudgement(
        question_id="q1", correctness_level=level, score=0.2,
        decision=Decision(decision),
        feedback=Feedback(positive="好", correction="错", hint="想想"),
        confidence=0.9,
    )


@pytest.mark.asyncio
async def test_solicit_threshold_from_settings(monkeypatch):
    """施压阈值=1：学生要 1 次答案，**施压当轮**判定强制阶梯顶格（原来写死 3）。"""
    from backend.tests.test_tutor_fsm import make_service, collect
    monkeypatch.setattr(app_settings, "solicit_loose_threshold", 1)

    rj = _RecordingJudge([_grade(), _grade(), _grade()])
    svc = make_service([])
    svc.actions.judge = rj
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, ""))          # 讲解+出题
    await collect(svc.handle_turn(ses.session_id, "随便答一个"))  # 判定1（未施压）
    await collect(svc.handle_turn(ses.session_id, "直接给我答案"))  # 施压1次=判定2
    await collect(svc.handle_turn(ses.session_id, "再答一次"))    # 判定3

    assert rj.hint_levels[0] == 0                 # 首判：无施压
    assert rj.hint_levels[1] == app_settings.scaffold_max_level, \
        f"回归:施压阈值参数化失效(施压当轮未顶格),实际={rj.hint_levels}"


@pytest.mark.asyncio
async def test_scaffold_cap_from_settings(monkeypatch):
    """阶梯上限=1：连续答错，hint_level 钳在 1（原来写死 3）。"""
    from backend.tests.test_tutor_fsm import make_service, collect
    monkeypatch.setattr(app_settings, "scaffold_max_level", 1)

    rj = _RecordingJudge([_grade(), _grade(), _grade(), _grade()])
    svc = make_service([])
    svc.actions.judge = rj
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, ""))
    for _ in range(3):
        await collect(svc.handle_turn(ses.session_id, "又答错了"))

    assert max(rj.hint_levels) <= 1, \
        f"回归:阶梯上限参数化失效,实际={rj.hint_levels}"
    assert rj.hint_levels[-1] == 1


def test_reviewer_sample_every_from_settings():
    """采样间隔可配：every=2 时第 3 次判定触发审查（原来写死 5）。"""
    from backend.engine.tutor.actions import TutorActions
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(app_settings, "reviewer_sample_every", 2)
        acts = TutorActions.__new__(TutorActions)   # 只测 _should_review，不走 __init__
        acts._review_count = 3
        ses = SimpleNamespace(reteach_count=0)
        assert acts._should_review(ses, solicit_was=0) is True
        monkeypatch.setattr(app_settings, "reviewer_sample_every", 5)
        assert acts._should_review(ses, solicit_was=0) is False
    finally:
        monkeypatch.undo()


def test_provider_chat_stream_is_method():
    """P0 回归锁（2026-09-05）：chat_stream 必须是 Provider 的方法——Phase 3 的 Edit
    事故曾把它挤成模块级函数，导致生产讲解流全挂（'Provider' object has no attribute）。"""
    from backend.engine.providers import Provider
    assert callable(getattr(Provider, "chat_stream", None)), \
        "回归:chat_stream 不在 Provider 类上,讲解流必挂"
