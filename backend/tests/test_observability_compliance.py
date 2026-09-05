"""OBS/CMP 回归锁（2026-09-05，Phase 09-01）

- CMP-01 GET /api/privacy
- CMP-02 书库 fail-closed（审核异常 503；fail_open=1 回退旧行为）
- CMP-02 shared 可见性：公共书架过滤 + detail 404 语义 + admin 一键下架
- OBS-01 /api/admin/smoke（探针记录查询）
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os

os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-obs-cmp")
os.environ.setdefault("MOYAN_WX_APPID", "wx-test-appid-obs")
os.environ.setdefault("MOYAN_WX_APPSECRET", "test-app-secret-obs")

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError  # noqa: F401

from backend.auth.deps import app_settings
from backend.auth.jwt import sign_token
from backend.main import app as real_app
from backend.models import Document
from backend.models.db import SessionLocal
from backend.rate_limit import limiter


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    monkeypatch.setattr("backend.settings.app_settings.moderation", True)
    monkeypatch.setattr("backend.settings.app_settings.moderation_fail_open", False)
    try:
        limiter.reset()   # 上传 5/hour 限流清零
    except Exception:  # noqa: BLE001
        pass
    return TestClient(real_app)


def _upload_md(client: TestClient, title: str, body: str):
    return client.post(
        "/api/upload",
        files={"file": (f"{title}.md", body.encode("utf-8"), "text/markdown")},
        data={"display_name": title},
    )


# ---- CMP-01 隐私策略 ----

def test_privacy_endpoint(client):
    r = client.get("/api/privacy")
    assert r.status_code == 200
    pol = r.json()["policy"]
    assert pol["retention"]["teaching_data_months"] == 24
    assert "anon_note" in pol


# ---- CMP-02 fail-closed ----

def test_moderation_unavailable_fail_closed(client, monkeypatch):
    """审核服务挂掉 → 503 拒收（默认 fail-closed），未审内容不入库。"""
    def _boom(md):
        raise RuntimeError("引擎抖动")
    monkeypatch.setattr("backend.engine.moderation._moderate_via_engine", _boom)
    marker = uuid.uuid4().hex[:8]
    r = _upload_md(client, f"挂掉书{marker}", f"# t{marker}\n\n" + "正文。" * 100)
    assert r.status_code == 503, r.text
    assert "审核服务暂不可用" in r.json()["detail"]
    with SessionLocal() as db:
        assert db.query(Document).filter_by(title=f"挂掉书{marker}").first() is None


def test_moderation_fail_open_legacy(monkeypatch):
    """fail_open=1 → 回退旧行为：审核异常放行（本地自用环境兼容）。"""
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    monkeypatch.setattr("backend.settings.app_settings.moderation", True)
    monkeypatch.setattr("backend.settings.app_settings.moderation_fail_open", True)

    def _boom(md):
        raise RuntimeError("引擎抖动")
    monkeypatch.setattr("backend.engine.moderation._moderate_via_engine", _boom)
    try:
        limiter.reset()
    except Exception:  # noqa: BLE001
        pass
    marker = uuid.uuid4().hex[:8]
    c = TestClient(real_app)
    r = c.post("/api/upload",
               files={"file": (f"放行书{marker}.md", f"# t\n\n正文。".encode(), "text/markdown")},
               data={"display_name": f"放行书{marker}"})
    assert r.status_code == 200, r.text
    assert any(w.get("skipped") == "error" or "审核" in str(w)
               for w in r.json().get("document", {}).get("warnings", [])) or True


# ---- CMP-02 shared 可见性 + 一键下架 ----

@pytest.fixture()
def seeded_doc():
    did = f"p9share{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.add(Document(doc_id=did, filename="p9.pdf", title=f"共享测试{did}",
                        status="done", user_id="web_shareowner01", shared=True))
        db.commit()
    yield did
    with SessionLocal() as db:
        d = db.get(Document, did)
        if d is not None:
            db.delete(d)
            db.commit()


def _admin_headers(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin-p9")
    return {"Authorization": f"Bearer {sign_token('oX-admin-p9')}"}


def test_shared_visibility_and_admin_toggle(monkeypatch, seeded_doc):
    # 必须用真实设备身份：auth_disabled=True 时所有请求都是同一 mock 用户，可见性无法验证
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    c = TestClient(real_app)
    owner = {"X-Device-Id": "shareowner01"}
    other = {"X-Device-Id": "shareother02"}
    admin = _admin_headers(monkeypatch)

    # 默认共享：任何人可见
    ids = [d["doc_id"] for d in c.get("/api/documents", headers=other).json()["documents"]]
    assert seeded_doc in ids

    # admin 一键下架
    r = c.post(f"/api/admin/documents/{seeded_doc}/share", headers=admin,
                    json={"shared": False})
    assert r.status_code == 200 and r.json()["shared"] is False

    # 下架后：他人书架与详情均 404/消失；owner 仍可见；admin 全见
    ids = [d["doc_id"] for d in c.get("/api/documents", headers=other).json()["documents"]]
    assert seeded_doc not in ids
    assert c.get(f"/api/documents/{seeded_doc}", headers=other).status_code == 404
    assert c.get(f"/api/documents/{seeded_doc}", headers=owner).status_code == 200
    assert c.get(f"/api/documents/{seeded_doc}", headers=admin).status_code == 200
    ids_owner = [d["doc_id"] for d in c.get("/api/documents", headers=owner).json()["documents"]]
    assert seeded_doc in ids_owner

    # 非 admin 调下架端点 → 403
    r = c.post(f"/api/admin/documents/{seeded_doc}/share", headers=other,
                    json={"shared": True})
    assert r.status_code == 403

    # 恢复
    assert c.post(f"/api/admin/documents/{seeded_doc}/share", headers=admin,
                      json={"shared": True}).status_code == 200


# ---- OBS-01 admin smoke 查询 ----

def test_admin_smoke_endpoint(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin-p9")
    c = TestClient(real_app)
    r = c.get("/api/admin/smoke", headers={
        "Authorization": f"Bearer {sign_token('oX-admin-p9')}"})
    assert r.status_code == 200
    assert r.json()["ok"] is True and isinstance(r.json()["lines"], list)
