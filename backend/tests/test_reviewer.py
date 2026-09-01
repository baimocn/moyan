"""输出后裁判单测（纯单元，不耗 token）：verdict 解析 + 采样逻辑"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from backend.engine.reviewer import ReviewVerdict
from backend.engine.tutor.actions import TutorActions
from backend.engine.tutor.session import TutorSession


def test_verdict_parses_json():
    v = ReviewVerdict.model_validate_json(
        '{"passed": false, "violations": [{"criterion": "答案泄漏", '
        '"severity": "high", "evidence": "你选对了答案 A"}], "note": "x"}')
    assert v.passed is False
    assert v.violations[0].criterion == "答案泄漏"


def test_verdict_empty_pass():
    v = ReviewVerdict.model_validate_json('{"passed": true, "violations": []}')
    assert v.passed and not v.violations


def _actions(mode):
    a = TutorActions(None, None, None, reviewer=object())
    import backend.settings as s
    return a


def _ses():
    return TutorSession(session_id="s", doc_id="d", chapter_index=0)


def test_review_sampling_off(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.teaching_reviewer", "off")
    a = _actions("off")
    assert a._should_review(_ses()) is False


def test_review_sampling_on(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.teaching_reviewer", "on")
    a = _actions("on")
    assert a._should_review(_ses()) is True


def test_review_sampling_sample_every_five(monkeypatch):
    """2026-08-29 新采样：第 1 次判定不审（首体验不被 ~30s 裁判拖慢），第 6/11/… 次审。"""
    monkeypatch.setattr("backend.settings.app_settings.teaching_reviewer", "sample")
    a = _actions("sample")
    assert a._should_review(_ses()) is False    # 第 1 次不审
    a._review_count = 3
    assert a._should_review(_ses()) is False    # 非整 5、无高风险
    a._review_count = 6
    assert a._should_review(_ses()) is True     # 第 6 次审


def test_review_sampling_high_risk(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.teaching_reviewer", "sample")
    a = _actions("sample")
    ses = _ses()
    ses.reteach_count = 2
    assert a._should_review(ses) is True        # 重讲≥2 必审
    ses2 = _ses()
    assert a._should_review(ses2, solicit_was=3) is True  # 索要答案≥3 必审


# ---------- 教学策略反馈（Groove/Tracer） ----------

def _clean_strategy(monkeypatch):
    from backend.models import SessionLocal, StrategyLog
    with SessionLocal() as db:
        db.query(StrategyLog).delete()
        db.commit()


def test_strategy_feedback_and_best_strategy(tmp_path):
    from backend.models import repo
    _clean_strategy(None)
    # alternative_explanation 效果好（0.9×3 次） vs reteach 差（0.2）
    for _ in range(3):
        repo.save_strategy_feedback("doc-s", "k1", "alternative_explanation", 0.9, True)
    repo.save_strategy_feedback("doc-s", "k1", "reteach", 0.2, False)
    stats = repo.strategy_stats("doc-s", "k1")
    alt = next(s for s in stats if s["strategy"] == "alternative_explanation")
    assert alt["samples"] == 3 and abs(alt["avg_effect"] - 0.9) < 1e-6
    assert alt["pass_rate"] == 1.0
    assert repo.best_strategy("doc-s", "k1") == "alternative_explanation"
    # 样本不足 → 走原逻辑
    assert repo.best_strategy("doc-s", "k2") is None


def test_traces_timeline(tmp_path):
    from backend.models import repo
    _clean_strategy(None)
    repo.upsert_weakness("doc-s", "k1", "知识点一", "low", chapter_index=0)
    repo.save_strategy_feedback("doc-s", "k1", "practice_question", 0.5, True)
    repo.upsert_weakness("doc-s", "k1", "知识点一", "high", chapter_index=0)
    tr = repo.traces("doc-s", "k1")
    assert tr["skill_id"] == "k1"
    assert len(tr["strategies"]) == 1 and tr["strategies"][0]["strategy"] == "practice_question"
    assert tr["mastery"][-1]["mastery"] == "high"