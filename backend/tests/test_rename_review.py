"""REN-01 重命名 AI 审核单测（2026-09-04）

覆盖：
1) 非 admin 改名「名称-内容不符」→ 422 + 标题不变
2) 非 admin 改名「相符」→ 200 + 标题更新
3) admin 改名跳过审核（审核函数不应被调用）
4) 审核服务异常 → fail-open 放行（check_title_async 自身语义）
5) MOYAN_RENAME_REVIEW=0 → 跳过（check_title_async 自身语义）
"""
from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-rename")

import pytest
from fastapi.testclient import TestClient

from backend.engine.title_check import check_title_async
from backend.main import app as real_app
from backend.models import Document, SessionLocal
from backend.rate_limit import limiter


def _mk_doc(prefix: str = "rn") -> str:
    doc_id = f"{prefix}{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db:
        db.add(Document(doc_id=doc_id, filename=f"{doc_id}.md", status="done",
                        title=f"原标题{doc_id[:8]}"))
        db.commit()
    return doc_id


def _patch_check(monkeypatch, match: bool, reason: str = "名称与内容不符"):
    calls = []

    async def _inner(title, markdown, chapter_titles):  # noqa: ANN001
        calls.append(title)
        return {"match": match, "reason": reason, "engine": "fake", "skipped": ""}

    monkeypatch.setattr("backend.routers.documents.check_title_async", _inner)
    return calls


def _patch_check_boom(monkeypatch):
    async def _inner(*a, **k):  # noqa: ANN002,ANN003
        raise AssertionError("admin 改名不应触发 AI 审核")

    monkeypatch.setattr("backend.routers.documents.check_title_async", _inner)


@pytest.fixture()
def client():
    try:
        limiter.reset()
    except Exception:  # noqa: BLE001
        pass
    return TestClient(real_app)


# ---- 1) 不符 → 422 + 标题不变 ----

def test_user_rename_mismatch_rejected(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc()
    _patch_check(monkeypatch, match=False, reason="内容是高等数学，名称是养殖大全")
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "养殖技术大全"},
                     headers={"X-Device-Id": "renametest01"})
    assert r.status_code == 422, r.text
    assert "改名未通过审核" in r.json()["detail"]
    assert "高等数学" in r.json()["detail"]
    with SessionLocal() as db:
        assert db.get(Document, doc_id).title.startswith("原标题")


# ---- 2) 相符 → 200 + 标题更新 ----

def test_user_rename_match_ok(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc()
    _patch_check(monkeypatch, match=True, reason="名称与内容相符")
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "高数入门"},
                     headers={"X-Device-Id": "renametest02"})
    assert r.status_code == 200, r.text
    assert r.json()["document"]["title"] == "高数入门"
    with SessionLocal() as db:
        assert db.get(Document, doc_id).title == "高数入门"


# ---- 3) admin 跳过审核 ----

def test_admin_rename_bypasses_review(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)  # mock dev_user=admin
    doc_id = _mk_doc()
    _patch_check_boom(monkeypatch)
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "随便改"})
    assert r.status_code == 200, r.text
    with SessionLocal() as db:
        assert db.get(Document, doc_id).title == "随便改"


# ---- 4) 审核服务异常 fail-open ----

def test_check_engine_error_fails_open(monkeypatch):
    from backend.container import services
    monkeypatch.setattr("backend.settings.app_settings.rename_review", True)
    monkeypatch.setattr("backend.engine.title_check.services.mock", False)

    def _boom(cheap=False):  # noqa: ANN001,ARG001
        raise RuntimeError("engine down")

    monkeypatch.setattr("backend.engine.title_check.services.engine_factory.require_engine",
                        _boom)
    out = asyncio.run(check_title_async("任意名", "有一些内容", ["第一章"]))
    assert out["match"] is True and out["skipped"] == "error"
    assert "fail" in out["reason"] or "异常" in out["reason"] or out["reason"]


# ---- 5) 开关关闭 → 跳过 ----

def test_check_disabled_skips(monkeypatch):
    from backend.container import services
    monkeypatch.setattr("backend.settings.app_settings.rename_review", False)
    monkeypatch.setattr("backend.engine.title_check.services.mock", False)
    out = asyncio.run(check_title_async("任意名", "有一些内容", []))
    assert out["match"] is True and out["skipped"] == "disabled"
