"""复习调度单测（官方 py-fsrs D4）+ 章节聚合 + 复习会话（engram 失败回收）

运行：pytest backend/tests/test_review.py
说明：确定性断言使用 enable_fuzzing=False 的 Scheduler（生产默认开 fuzz）。
"""
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from fsrs import Scheduler

from backend.models import repo

_DET = Scheduler(enable_fuzzing=False)   # 测试专用：关闭随机 fuzz


@pytest.fixture(autouse=True)
def _clean_weaknesses():
    """用例间清空测试库薄弱点。"""
    from backend.models import SessionLocal, Weakness
    with SessionLocal() as db:
        db.query(Weakness).delete()
        db.commit()
    yield


def _make(name="知识点一", skill="k1", chapter=0, mastery="low"):
    repo.upsert_weakness("doc-r", skill, name, mastery,
                         chapter_index=chapter, chapter_title=f"第{chapter + 1}章")


# ---------- FSRS 内核 ----------

def test_new_weakness_is_due_immediately():
    """新薄弱点入账即到期（尽快首学）。"""
    _make()
    due = repo.due_reviews("doc-r")
    assert any(r["skill_id"] == "k1" for r in due)


def test_good_review_enters_learning_then_review():
    """新卡答 good：先走学习步（分钟级），再答进入 Review 且间隔 ≥1 天。"""
    _make()
    r1 = repo.record_review("doc-r", "k1", "good", scheduler=_DET)
    assert r1["state"] == 1 and r1["reps"] == 1        # Learning 步
    r2 = repo.record_review("doc-r", "k1", "good", scheduler=_DET)
    assert r2["state"] == 2 and r2["interval_days"] >= 1   # Review，天级
    assert r2["stability"] and r2["stability"] > 0


def test_spaced_repetition_growth():
    """Review 间隔天数推进：稳定性与间隔随复习次数增长（模拟真实天级节奏）。"""
    _make()
    for _ in range(2):   # 学习步完成进入 Review
        repo.record_review("doc-r", "k1", "good", scheduler=_DET)
    now = repo._now()
    intervals = []
    stabilities = []
    for _ in range(6):
        r = repo.record_review("doc-r", "k1", "good", scheduler=_DET,
                               review_datetime=now)
        intervals.append(r["interval_days"])
        stabilities.append(r["stability"])
        now += timedelta(days=max(1, r["interval_days"]))   # 按排程推进到下一次
    assert intervals == sorted(intervals)
    assert stabilities == sorted(stabilities)
    assert stabilities[-1] > stabilities[0]               # 稳定性确实在涨
    assert intervals[-1] > intervals[0]


def test_again_during_learning_resets_step():
    """学习步内答 again：留在 Learning 重头学，lapses+1（不进入重学态）。"""
    _make()
    repo.record_review("doc-r", "k1", "good", scheduler=_DET)   # Learning step1
    r = repo.record_review("doc-r", "k1", "again", scheduler=_DET)
    assert r["state"] == 1 and r["lapses"] == 1


def test_again_in_review_enters_relearning():
    """进入 Review 后答 again：转入 Relearning（重学步，分钟级到期）。"""
    _make()
    repo.record_review("doc-r", "k1", "good", scheduler=_DET)
    repo.record_review("doc-r", "k1", "good", scheduler=_DET)
    assert repo.record_review("doc-r", "k1", "good", scheduler=_DET)["state"] == 2
    r = repo.record_review("doc-r", "k1", "again", scheduler=_DET)
    assert r["state"] == 3 and r["lapses"] == 1
    assert r["mastery"] == "low"
    assert r["due_at"]  # 到期（重学步，约 10 分钟内）


def test_retention_priority_orders_due_queue():
    """队列排序：遗忘风险/遗忘次数高的排前（'预计挽回记忆/分钟'代理）。"""
    _make(skill="fresh", mastery="mid")                    # 无 lapse
    _make(skill="forgetful", mastery="low")
    # forgetful 先被复习+遗忘一次，产生 lapse 且到期
    repo.record_review("doc-r", "fresh", "good", scheduler=_DET)
    repo.record_review("doc-r", "forgetful", "good", scheduler=_DET)
    repo.record_review("doc-r", "forgetful", "again", scheduler=_DET)
    due = repo.due_reviews("doc-r")
    if len(due) >= 2:
        ranks = {d["skill_id"]: i for i, d in enumerate(due)}
        assert ranks["forgetful"] < ranks.get("fresh", len(due) + 1)


def test_unknown_review_rating_rejected():
    _make()
    with pytest.raises(ValueError):
        repo.record_review("doc-r", "k1", "perfect")


def test_upsert_updates_name_and_times_low():
    repo.upsert_weakness("doc-r", "k1", "知识点一", "mid", chapter_index=0)
    repo.upsert_weakness("doc-r", "k1", "知识点一（新名字）", "low", chapter_index=0)
    rows = repo.list_weaknesses("doc-r")
    assert rows and rows[0]["name"] == "知识点一（新名字）"
    assert rows[0]["times_low"] == 2


def test_stats_survives_even_if_sqlite_datetime_naive():
    """SQLite 读回的 due_at 无 tz：stats 不能炸（回归：offset-naive vs aware）。"""
    _make()
    stats = repo.study_stats("doc-r")
    assert stats["skills"] == 1 and stats["review_due"] == 1


# ---------- 概念→章节聚合 ----------

def test_chapter_overview_groups_concepts():
    _make(skill="k1", chapter=0)
    _make(skill="k2", chapter=0, mastery="high")
    _make(skill="k3", chapter=1)
    ov = repo.chapter_overview("doc-r")
    assert ov["summary"]["total_weakness"] == 3
    ch0 = next(c for c in ov["chapters"] if c["chapter_index"] == 0)
    ch1 = next(c for c in ov["chapters"] if c["chapter_index"] == 1)
    assert ch0["total"] == 2 and ch0["by_mastery"]["low"] == 1
    assert ch1["total"] == 1 and ch1["due"] == 1
    # 排序：到期多的章排前
    assert ov["chapters"][0]["chapter_index"] in (0, 1)
    assert ov["chapters"][0]["due"] >= ov["chapters"][1]["due"]


# ---------- 复习会话（engram 失败回收） ----------

def test_review_session_recovery_loop(monkeypatch):
    from backend.engine.review import ReviewService
    from backend.storage import get_chapter

    monkeypatch.setattr("backend.engine.review.service.storage.get_chapter",
                        lambda doc_id, idx: {"markdown": "第一章 知识点一的核心定义，学生在掌握这个概念。"})
    _make(skill="k1", chapter=0)
    svc = ReviewService()
    ses = svc.start("doc-r", limit=10)
    assert ses.queue and ses.queue[0].skill_id == "k1"
    first = ses.queue[0]

    # 第一次答错 → 失败回收：给片段、留队再答
    out = svc.answer(ses.session_id, "k1", "again")
    assert out["recovery"] and out["recovery"]["snippet"]
    assert out["next"]["skill_id"] == "k1"          # 仍在队列
    assert out["progress"]["remaining"] == 1

    # 第二次答对 → 出队
    out2 = svc.answer(ses.session_id, "k1", "good")
    assert out2["recovery"] is None
    assert out2["finished"] is True
    summary = svc.summary(ses.session_id)
    assert summary["by_rating"]["again"] == 1 and summary["by_rating"]["good"] == 1


def test_review_session_answers_unknown_item():
    from backend.engine.review import ReviewService
    _make(skill="k1", chapter=0)
    svc = ReviewService()
    ses = svc.start("doc-r", limit=10)
    with pytest.raises(KeyError):
        svc.answer(ses.session_id, "no-such", "good")
    with pytest.raises(KeyError):
        svc.answer("rv_missing", "k1", "good")