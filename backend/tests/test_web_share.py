"""网页版免登录 + 共享书库单测（2026-09-03）

覆盖：
1) get_requester：X-Device-Id → web_<did>；非法 did → web_anon；Bearer 优先于 did
2) 上传去重：同内容二次上传 reused=True 且 doc_id 相同（不重复建档）
3) 共享书库搜索：q 按 title/filename 大小写不敏感过滤，空 q 全量
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-web-share")
os.environ.setdefault("MOYAN_WX_APPID", "wx-test-appid-share")
os.environ.setdefault("MOYAN_WX_APPSECRET", "test-app-secret-for-share-tests")

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.auth.deps import CurrentUser, get_requester
from backend.main import app as real_app


# ---- 1) get_requester 匿名身份 ----

def _probe_app() -> TestClient:
    a = FastAPI()

    @a.get("/probe")
    def probe(user: CurrentUser = Depends(get_requester)):
        return {"openid": user.openid}

    return TestClient(a)


def test_requester_device_id(monkeypatch):
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    c = _probe_app()
    r = c.get("/probe", headers={"X-Device-Id": "abcDEF123-xyz_456"})
    assert r.status_code == 200, r.text
    assert r.json()["openid"] == "web_abcDEF123-xyz_456"


def test_requester_bad_device_id_falls_back_anon(monkeypatch):
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    c = _probe_app()
    for bad in ("short7", "../etc", "x" * 100, ""):
        r = c.get("/probe", headers={"X-Device-Id": bad})
        assert r.status_code == 200
        assert r.json()["openid"] == "web_anon", f"did={bad!r}"


def test_requester_bearer_beats_device_id(monkeypatch):
    from backend.auth.jwt import sign_token

    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    c = _probe_app()
    tok = sign_token("oX_real_wx_user")
    r = c.get("/probe", headers={
        "Authorization": f"Bearer {tok}",
        "X-Device-Id": "device-should-lose",
    })
    assert r.status_code == 200
    assert r.json()["openid"] == "oX_real_wx_user"


# ---- 2/3) 上传去重 + 搜索（真 app + md 直读路径，免 docling）----

def _upload_md(client: TestClient, text: str, title: str):
    return client.post(
        "/api/upload",
        files={"file": (f"{title}.md", text.encode("utf-8"), "text/markdown")},
        data={"display_name": title},
    )


def test_upload_dedupe_and_search(monkeypatch):
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", True)
    client = TestClient(real_app)

    marker = uuid.uuid4().hex[:8]
    title = f"共享书库测试之{marker}"
    body = f"# {title}\n\n第一章内容 {marker}。\n\n" + "正文。" * 200

    r1 = _upload_md(client, body, title)
    assert r1.status_code == 200, r1.text
    j1 = r1.json()
    assert j1["ok"] is True
    assert not j1.get("reused")

    # 同内容不同文件名再传 → reused，doc_id 相同
    r2 = client.post(
        "/api/upload",
        files={"file": (f"换了名字{marker}.md", body.encode("utf-8"), "text/markdown")},
        data={"display_name": f"换名{marker}"},
    )
    assert r2.status_code == 200, r2.text
    j2 = r2.json()
    assert j2.get("reused") is True, j2
    assert j2["doc_id"] == j1["doc_id"]

    # 搜索：title 命中
    rs = client.get("/api/documents", params={"q": marker})
    assert rs.status_code == 200
    items = rs.json()["documents"]
    assert len(items) == 1
    assert items[0]["doc_id"] == j1["doc_id"]

    # 搜索：大小写不敏感（标题混英文）
    title2 = f"PyThOn 快速上手 {marker}"
    body2 = f"# {title2}\n\n" + "内容。" * 200
    r3 = _upload_md(client, body2, title2)
    assert r3.status_code == 200, r3.text
    rs2 = client.get("/api/documents", params={"q": f"python 快速 {marker}"})
    assert rs2.status_code == 200
    assert any(d["doc_id"] == r3.json()["doc_id"] for d in rs2.json()["documents"])

    # 无命中 → 空
    rs3 = client.get("/api/documents", params={"q": "zzz_no_such_book_marker"})
    assert rs3.status_code == 200
    assert rs3.json()["documents"] == []
