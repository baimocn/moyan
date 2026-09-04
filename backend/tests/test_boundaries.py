"""边界测试（2026-09-04，Spec=out/边界测试_spec.md）

矩阵行→测试：
R1/R2 空白标题 400 · R3 404 · R4 同名短路 · R5 无 markdown 放行 ·
R6 超长截断 · R7 特殊字符 · R8 拒绝回归 · R9 admin 绕过回归 ·
L1-L5 admin/login 边界 · P1-P4 pv 边界 · Q1-Q3 读路径
（D1-D3 依赖真实鉴权实例，live curl 执行；R10 已有单测）
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-boundary")

import pytest
from fastapi.testclient import TestClient

from backend.main import app as real_app
from backend.models import Document, SessionLocal
from backend.rate_limit import limiter

ANON = {"X-Device-Id": "boundtest001"}


def _mk_doc(title: str | None = None, status: str = "done") -> str:
    doc_id = f"bd{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db:
        db.add(Document(doc_id=doc_id, filename=f"{doc_id}.md", status=status,
                        title=title))
        db.commit()
    return doc_id


def _patch_check(monkeypatch, match: bool = True, reason: str = "相符"):
    calls = []

    async def _inner(title, markdown, chapter_titles):  # noqa: ANN001
        calls.append({"title": title, "md_len": len(markdown or "")})
        return {"match": match, "reason": reason, "engine": "fake", "skipped": ""}

    monkeypatch.setattr("backend.routers.documents.check_title_async", _inner)
    return calls


@pytest.fixture()
def client():
    try:
        limiter.reset()
    except Exception:  # noqa: BLE001
        pass
    return TestClient(real_app)


# ---- REN ----

def test_r1_r2_blank_title_400(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc("旧名")
    _patch_check_boom(monkeypatch)
    for bad in ("", "  \n\t "):
        r = client.patch(f"/api/documents/{doc_id}", json={"title": bad}, headers=ANON)
        assert r.status_code == 400, r.text
        assert "名称不能为空" in r.json()["detail"]


def test_r3_missing_doc_404(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    _patch_check_boom(monkeypatch)
    r = client.patch("/api/documents/no-such-doc", json={"title": "x"}, headers=ANON)
    assert r.status_code == 404


def test_r4_same_title_short_circuit(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc("现名")
    _patch_check_boom(monkeypatch)  # 同名不应触发 AI
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "现名"}, headers=ANON)
    assert r.status_code == 200 and r.json().get("unchanged") is True
    with SessionLocal() as db:
        assert db.get(Document, doc_id).title == "现名"


def test_r5_no_markdown_passes(client, monkeypatch):
    """processing 文档（markdown 不存在）→ AI skip(empty) 放行。"""
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc("解析中", status="processing")
    calls = _patch_check(monkeypatch, match=True)
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "新书名"},
                     headers=ANON)
    assert r.status_code == 200, r.text
    assert calls and calls[0]["md_len"] == 0  # AI 被调用但空内容（函数自身 skip）


def test_r6_long_title_truncated(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc("旧名")
    calls = _patch_check(monkeypatch, match=True)
    long_title = "数据库系统概论" + "附录补充说明内容很长的部分" * 30  # ~270 字
    r = client.patch(f"/api/documents/{doc_id}", json={"title": long_title},
                     headers=ANON)
    assert r.status_code == 200, r.text
    assert len(calls) == 1 and len(calls[0]["title"]) == 200  # AI 收到截断版
    with SessionLocal() as db:
        assert len(db.get(Document, doc_id).title) == 200


def test_r7_special_chars(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc("旧名")
    _patch_check(monkeypatch, match=True)
    weird = "《机器学习》📘\n第二版"
    r = client.patch(f"/api/documents/{doc_id}", json={"title": weird}, headers=ANON)
    assert r.status_code == 200, r.text
    assert r.json()["document"]["title"] == weird.strip()[:200]


def test_r8_reject_regression(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    doc_id = _mk_doc("旧名")
    _patch_check(monkeypatch, match=False, reason="不符")
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "无关名"}, headers=ANON)
    assert r.status_code == 422
    with SessionLocal() as db:
        assert db.get(Document, doc_id).title == "旧名"


def test_r9_admin_bypass_regression(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    doc_id = _mk_doc("旧名")
    _patch_check_boom(monkeypatch)
    r = client.patch(f"/api/documents/{doc_id}", json={"title": "管理员改名"})
    assert r.status_code == 200


def _patch_check_boom(monkeypatch):
    async def _boom(title, markdown, chapter_titles):  # noqa: ANN001
        raise AssertionError("此路径不应调用 AI 审核")

    monkeypatch.setattr("backend.routers.documents.check_title_async", _boom)


# ---- LOGIN ----

def _login(client, monkeypatch, password="pw-boundary-123"):
    monkeypatch.setattr("backend.settings.app_settings.admin_web_password", password)
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oA,oB")
    return client


def test_l1_l2_login_wrong(client, monkeypatch):
    _login(client, monkeypatch)
    r0 = client.post("/api/admin/login", json={})
    assert r0.status_code == 403  # 空 body = 空口令 → 403 非 422
    r = client.post("/api/admin/login", json={"password": "wrong"})
    assert r.status_code == 403


def test_l3_login_not_configured(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_web_password", "")
    r = client.post("/api/admin/login", json={"password": "x"})
    assert r.status_code == 404
    assert "未开启" in r.json()["detail"]


def test_l4_login_rate_limited(client, monkeypatch):
    _login(client, monkeypatch)
    try:
        limiter.reset()
    except Exception:  # noqa: BLE001
        pass
    codes = [client.post("/api/admin/login",
                         json={"password": "wrong"}).status_code for _ in range(11)]
    assert codes[:10] == [403] * 10
    assert codes[10] == 429


def test_l5_login_ok(client, monkeypatch):
    _login(client, monkeypatch)
    r = client.post("/api/admin/login", json={"password": "pw-boundary-123"})
    assert r.status_code == 200
    assert r.json()["role"] == "admin" and r.json()["token"]


# ---- PV ----

def test_p1_p4_pv_boundaries(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    # P1 空 body
    r = client.post("/api/metrics/pv", json={}, headers=ANON)
    assert r.status_code == 200
    # P2 非法 source 归一 web
    r = client.post("/api/metrics/pv", json={"source": "hack", "page": "home"},
                    headers=ANON)
    assert r.status_code == 200
    # P3 page 超长
    r = client.post("/api/metrics/pv", json={"page": "x" * 100}, headers=ANON)
    assert r.status_code == 200
    # P4 非法 device_id
    r = client.post("/api/metrics/pv", json={"device_id": "有中文 ok?"}, headers=ANON)
    assert r.status_code == 200
    # P5 非 JSON body → FastAPI 422
    r = client.post("/api/metrics/pv", content=b"not-json",
                    headers={**ANON, "Content-Type": "application/json"})
    assert r.status_code == 422


# ---- READ ----

def test_q1_q3_read_paths(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", False)
    r = client.get("/api/documents", params={"q": "<script>alert(1)</script>"})
    assert r.status_code == 200 and r.json()["documents"] == []
    r = client.get("/api/documents/no-such-doc")
    assert r.status_code == 404
    r = client.get("/api/documents/no-such-doc/chapters/999")
    assert r.status_code == 404
