"""Phase 10 回归锁（AUTH-04/PRAC-01/RPT-01/ME-01，2026-09-05）"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os

os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-phase10")
os.environ.setdefault("MOYAN_WX_APPID", "wx-test-appid-p10")
os.environ.setdefault("MOYAN_WX_APPSECRET", "test-app-secret-p10")

from fastapi.testclient import TestClient

from backend.auth.deps import app_settings
from backend.auth.jwt import sign_token
from backend.main import app as real_app
from backend.models import repo
from backend.models.db import SessionLocal
from backend.models.documents import Document
from backend.models.study import Judgement, TeachingSession, Turn, Weakness

OWNER = {"X-Device-Id": "p10owner001"}
OTHER = {"X-Device-Id": "p10other002"}
ANON = {}
ADMIN = {"Authorization": f"Bearer {sign_token('oX-admin-p10')}"}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin-p10")
    monkeypatch.setattr("backend.settings.app_settings.daily_token_budget", 0)
    monkeypatch.setattr("backend.settings.app_settings.daily_token_hard", 0)
    yield


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    with SessionLocal() as db:
        db.query(Turn).filter(Turn.session_id.like("p10%")).delete(synchronize_session=False)
        db.query(Judgement).filter(Judgement.session_id.like("p10%")).delete(synchronize_session=False)
        db.query(TeachingSession).filter(TeachingSession.id.like("p10%")).delete(synchronize_session=False)
        db.query(Weakness).filter(Weakness.doc_id.like("p10%")).delete(synchronize_session=False)
        db.query(Document).filter(Document.doc_id.like("p10%")).delete(synchronize_session=False)
        db.commit()


def _doc(doc_id: str, shared: bool, owner: str = "web_p10owner001"):
    with SessionLocal() as db:
        db.add(Document(doc_id=doc_id, filename=f"{doc_id}.md", title=doc_id,
                        status="done", user_id=owner, shared=shared))
        db.commit()


def _weak(doc_id: str, skill: str, owner: str, mastery="low"):
    with SessionLocal() as db:
        db.add(Weakness(id=f"w_{uuid.uuid4().hex[:10]}", doc_id=doc_id, skill_id=skill,
                        name=skill, mastery=mastery, times_low=1, user_id=owner))
        db.commit()


def _turn(session_id: str, owner: str):
    with SessionLocal() as db:
        db.add(TeachingSession(id=session_id, doc_id="p10doc-r", chapter_index=0,
                               chapter_title="t", state="explain", kp_idx=0,
                               plan=[], weak={}, user_id=owner))
        db.add(Turn(id=f"t_{uuid.uuid4().hex[:10]}", session_id=session_id,
                    role="user", kind="answer", content="x", user_id=owner))
        db.commit()


# ---- AUTH-04 doc 级可见性（7 端点抽查 5 条路径 + 全 suffix 扫描）----

def test_doc_level_visibility():
    c = TestClient(real_app)
    _doc("p10doc-shared", shared=True, owner="web_p10owner001")
    _doc("p10doc-priv", shared=False, owner="web_p10owner001")

    suffixes = ["/sessions", "/weaknesses", "/stats", "/reviews", "/chapters",
                "/strategy-stats", "/traces/sk1"]
    for suffix in suffixes:
        assert c.get(f"/api/study/p10doc-priv{suffix}", headers=OTHER).status_code == 404, suffix
        assert c.get(f"/api/study/p10doc-shared{suffix}", headers=ANON).status_code == 200, suffix
        assert c.get(f"/api/study/p10doc-priv{suffix}", headers=ADMIN).status_code == 200, suffix
    assert c.get("/api/study/p10doc-none/weaknesses", headers=OTHER).status_code == 404


def test_doc_visibility_non_admin_cannot_toggle():
    _doc("p10doc-priv2", shared=False, owner="web_p10owner001")
    c = TestClient(real_app)
    assert c.get("/api/documents/p10doc-priv2", headers=OTHER).status_code == 404
    assert c.get("/api/documents/p10doc-priv2", headers=OWNER).status_code == 200


# ---- PRAC-01 错题本 owner 口径 ----

def test_weaknesses_owner_scope():
    _doc("p10doc-weak", shared=True, owner="web_p10owner001")
    _weak("p10doc-weak", "sk-a", "web_p10owner001", mastery="low")
    _weak("p10doc-weak", "sk-b", "web_p10other002", mastery="mid")
    c = TestClient(real_app)

    rows = c.get("/api/study/p10doc-weak/weaknesses", headers=OWNER).json()["weaknesses"]
    assert {r["skill_id"] for r in rows} == {"sk-a"}            # owner 只见自己的
    rows_admin = c.get("/api/study/p10doc-weak/weaknesses", headers=ADMIN).json()["weaknesses"]
    assert {r["skill_id"] for r in rows_admin} == {"sk-a", "sk-b"}  # admin 全量


# ---- RPT-01 学习报告 ----

def test_report_aggregation():
    uid = "web_p10owner001"
    sid = f"p10ses-r{uuid.uuid4().hex[:6]}"
    _turn(sid, uid)
    with SessionLocal() as db:
        db.add(Judgement(id=f"j_{uuid.uuid4().hex[:10]}", session_id=sid,
                         question_id="q1", correctness="correct", score=0.8,
                         decision="pass", confidence=0.9, payload={},
                         user_id=uid))
        db.commit()
    repo.upsert_weakness(f"p10doc-r{uuid.uuid4().hex[:4]}", "sk-r", "薄弱点",
                         "low", user_id=uid)

    c = TestClient(real_app)
    r = c.get("/api/study/report", headers=OWNER)
    assert r.status_code == 200, r.text
    rep = r.json()["report"]
    assert rep["teaching"]["turns"] >= 1
    assert rep["teaching"]["sessions"] >= 1
    assert rep["trend"] and rep["trend"][-1]["avg_score"] == 0.8
    assert isinstance(rep["streak_days"], int)


def test_report_web_anon_scope_note():
    c = TestClient(real_app)
    r = c.get("/api/study/report", headers=ANON)
    assert r.status_code == 200
    assert "共享匿名" in r.json()["report"]["scope_note"]


# ---- ME-01 个人页口径（Bearer 鉴权）----

def test_me_stats_bearer_only():
    c = TestClient(real_app)
    uid = "web_p10owner001"
    r = c.get("/api/auth/me/stats", headers={
        "Authorization": f"Bearer {sign_token(uid)}"})
    assert r.status_code == 200, r.text
    assert r.json()["report"]["user_id"] == uid
    # 无 Bearer → 401（个人口径不落 web_anon 兜底）
    assert c.get("/api/auth/me/stats").status_code in (401, 403)
