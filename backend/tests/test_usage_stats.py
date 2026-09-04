"""Phase 3 用量观测单测（COST-01 / STATS-01/03，2026-09-04）

覆盖：
1) ledger.record：scope 上下文入账（endpoint/user/doc/session）
2) PV 接口：匿名上报落库（source/page/device 校验与兜底）
3) /api/admin/usage 聚合：按天分组 + 总计
4) /api/admin/stats：PV/UV/教学计数/token 汇总
5) 管理闸门：非 admin 403
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-usage-stats")

import pytest
from fastapi.testclient import TestClient

from backend import ledger
from backend.main import app as real_app
from backend.models import AiUsage, PageView, SessionLocal
from backend.rate_limit import limiter


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    try:
        limiter.reset()
    except Exception:  # noqa: BLE001
        pass
    return TestClient(real_app)


def _clean():
    with SessionLocal() as db:
        db.query(AiUsage).delete()
        db.query(PageView).delete()
        db.commit()


# ---- 1) ledger scope 入账 ----

def test_ledger_record_with_scope():
    _clean()
    with ledger.ai_scope("proofread", doc_id="doc-x", user_id="oX-u1", session_id="s-1"):
        ledger.record("cheap", "deepseek-chat",
                      {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150})
    with SessionLocal() as db:
        row = db.query(AiUsage).order_by(AiUsage.id.desc()).first()
    assert row is not None
    assert row.endpoint == "proofread"
    assert row.prompt_tokens == 100 and row.completion_tokens == 50
    assert row.total_tokens == 150
    assert row.doc_id == "doc-x" and row.user_id == "oX-u1" and row.session_id == "s-1"
    assert row.estimated is False


def test_ledger_estimated_tokens_flagged():
    _clean()
    ledger.record("main", "gpt-x", {"estimated_tokens": 42})
    with SessionLocal() as db:
        row = db.query(AiUsage).order_by(AiUsage.id.desc()).first()
    assert row.endpoint == "misc"          # 无 scope 兜底
    assert row.total_tokens == 42 and row.estimated is True


def test_ledger_zero_usage_skipped():
    _clean()
    ledger.record("main", "gpt-x", {"prompt_tokens": 0, "completion_tokens": 0})
    with SessionLocal() as db:
        assert db.query(AiUsage).count() == 0


# ---- 2) PV 接口 ----

def test_pv_anon_report(client):
    _clean()
    marker = uuid.uuid4().hex[:10]
    r = client.post("/api/metrics/pv", json={
        "source": "web", "page": "home", "device_id": f"dev-{marker}"})
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True
    with SessionLocal() as db:
        row = (db.query(PageView).filter_by(device_id=f"dev-{marker}")
               .order_by(PageView.id.desc()).first())
    assert row is not None
    assert row.source == "web" and row.page == "home" and row.user_id is None


def test_pv_invalid_source_and_device(client):
    _clean()
    r = client.post("/api/metrics/pv", json={
        "source": "hacker", "page": "x" * 200, "device_id": "../bad path"})
    assert r.status_code == 200
    with SessionLocal() as db:
        row = db.query(PageView).order_by(PageView.id.desc()).first()
    assert row.source == "web"       # 非法来源归一 web
    assert len(row.page) <= 64       # 截断
    assert row.device_id == "anon"   # 非法设备码兜底


# ---- 3/4) 管理统计聚合 ----

def test_admin_usage_and_stats_aggregation(client):
    _clean()
    with ledger.ai_scope("tutor_turn", session_id="s-agg", user_id="oX-a"):
        ledger.record("main", "model-a", {"prompt_tokens": 10, "completion_tokens": 20})
        ledger.record("main", "model-a", {"prompt_tokens": 5, "completion_tokens": 5})
    with ledger.ai_scope("moderation", doc_id="doc-agg"):
        ledger.record("cheap", "model-b", {"prompt_tokens": 7, "completion_tokens": 3})
    client.post("/api/metrics/pv", json={"source": "web", "page": "home",
                                         "device_id": "uv-dev-1"})
    client.post("/api/metrics/pv", json={"source": "web", "page": "tutor",
                                         "device_id": "uv-dev-1"})
    client.post("/api/metrics/pv", json={"source": "mp", "page": "home",
                                         "device_id": "uv-dev-2"})

    r1 = client.get("/api/admin/usage?days=30")
    assert r1.status_code == 200, r1.text
    body = r1.json()
    assert body["total"]["total_tokens"] == 50          # 30+10+10
    assert body["total"]["calls"] == 3
    endpoints = {(d["endpoint"], d["model"]) for d in body["daily"]}
    assert ("tutor_turn", "model-a") in endpoints
    assert ("moderation", "model-b") in endpoints

    r2 = client.get("/api/admin/stats")
    assert r2.status_code == 200, r2.text
    s = r2.json()
    assert s["pv"]["total"] == 3 and s["uv"]["total"] == 2
    assert s["sources"]["web"] == 2 and s["sources"]["mp"] == 1
    assert s["tokens"]["total"] == 50 and s["tokens"]["calls"] == 3
    assert "turns" in s["teaching"] and "docs_done" in s["teaching"]


# ---- 5) 管理闸门 ----

def test_admin_stats_requires_admin(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    c = TestClient(real_app)
    assert c.get("/api/admin/stats").status_code == 403
    assert c.get("/api/admin/usage").status_code == 403
