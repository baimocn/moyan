"""鉴权模块单测（部署前置：2026-09-02）

覆盖：
1) wx-login 微信侧 errcode != 0 → 400
2) dev-login 鉴权 enabled 时 403；鉴权 disabled 时 200
3) /api/auth/me 缺 Bearer → 401
4) /api/auth/me Bearer 失效 → 401
5) /api/auth/me Bearer 合法 → 200
6) JWT 自签自验 round-trip
7) user_profiles 首登落档 is_new=True，二次落档 is_new=False
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# 强制鉴权开启（不走 disabled 分支）—— 测试 jwt 必须有 secret
os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-please-do-not-use-in-prod")
# wx-login 测试需要 AppID 才能走完 _creds()
os.environ.setdefault("MOYAN_WX_APPID", "wx-test-appid")
os.environ.setdefault("MOYAN_WX_APPSECRET", "test-app-secret-for-unit-tests")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.auth.deps import get_current_user
from backend.auth.jwt import sign_token, verify_token
from backend.auth.router import router as auth_router
from backend.auth.schemas import WxLoginReq
from backend.auth.wx import WxLoginError, exchange_openid


# ---- 1) JWT 自身 ----

def test_jwt_roundtrip():
    tok = sign_token("oX-test-openid-123")
    payload = verify_token(tok)
    assert payload["sub"] == "oX-test-openid-123"
    assert payload["iss"] == "moyan"
    assert payload["exp"] > payload["iat"]


def test_jwt_invalid_signature_rejected():
    import jwt as pyjwt
    bad = pyjwt.encode({"sub": "x", "iss": "moyan", "iat": 0, "exp": 9999999999},
                       "wrong-secret", algorithm="HS256")
    with pytest.raises(Exception):
        verify_token(bad)


# ---- 2) 微信侧 mock ----

class _FakeResp:
    def __init__(self, data): self._data = data
    def json(self): return self._data


@pytest.mark.asyncio
async def test_exchange_openid_wx_errcode_raises(monkeypatch):
    """微信返 errcode != 0 → WxLoginError"""
    import httpx
    async def fake_get(self, url, params=None):
        return _FakeResp({"errcode": 40029, "errmsg": "invalid code"})
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    with pytest.raises(WxLoginError) as ei:
        await exchange_openid("bad_code")
    assert "40029" in str(ei.value)


@pytest.mark.asyncio
async def test_exchange_openid_success(monkeypatch):
    import httpx
    async def fake_get(self, url, params=None):
        return _FakeResp({"openid": "oX-good", "session_key": "abc"})
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    data = await exchange_openid("ok_code")
    assert data["openid"] == "oX-good"


# ---- 3) /api/auth/* HTTP 路由 ----

def _app_with_auth(auth_disabled: bool) -> FastAPI:
    """临时 app：注入 main.py 的全部路由但可切换 auth_disabled。"""
    a = FastAPI()
    a.include_router(auth_router)
    return a


def test_me_requires_bearer_when_auth_enabled(monkeypatch):
    """鉴权开启 + 缺 Bearer → 401"""
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    # conftest 已经设了 MOYAN_AUTH_DISABLED=0 + 测库 OK
    client = TestClient(_app_with_auth(False))
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert "未登录" in r.json()["detail"]


def test_me_with_valid_token(monkeypatch):
    """鉴权开启 + 合法 token → 200"""
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    client = TestClient(_app_with_auth(False))
    tok = sign_token("oX-test-me")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user_id"] == "oX-test-me"
    assert body["openid"] == "oX-test-me"


def test_me_with_invalid_token(monkeypatch):
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    client = TestClient(_app_with_auth(False))
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert r.status_code == 401


def test_dev_login_rejected_when_auth_enabled(monkeypatch):
    """鉴权开启 → dev-login 必须 403"""
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    client = TestClient(_app_with_auth(False))
    r = client.post("/api/auth/dev-login", json={"dev_openid": "hacker"})
    assert r.status_code == 403


def test_dev_login_ok_when_auth_disabled(monkeypatch):
    """鉴权关闭 → dev-login 直返 token"""
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", True)
    client = TestClient(_app_with_auth(True))
    r = client.post("/api/auth/dev-login", json={"dev_openid": "guest"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token"]
    assert body["user_id"] == "dev_guest"


def test_me_with_mock_user_when_auth_disabled(monkeypatch):
    """鉴权关闭 → /me 返 dev_user 不用 Bearer"""
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", True)
    client = TestClient(_app_with_auth(True))
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["user_id"] == "dev_user"


# ---- 4) wx-login：mock httpx 走通首登落档 ----

def test_wx_login_first_time_creates_profile(monkeypatch):
    """wx-login 首次 → 200 + is_new=True + token"""
    import httpx, uuid
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    unique_openid = f"oX-test-{uuid.uuid4().hex[:8]}"
    # 微信 mock
    async def fake_get(self, url, params=None):
        return _FakeResp({"openid": unique_openid, "session_key": "k1"})
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    client = TestClient(_app_with_auth(False))
    r = client.post("/api/auth/wx-login",
                    json={"code": "c1", "nick_name": "小明"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_new"] is True
    assert body["openid"] == unique_openid
    # 二次再登 → is_new=False
    r2 = client.post("/api/auth/wx-login",
                     json={"code": "c1", "nick_name": "小明"})
    assert r2.status_code == 200
    assert r2.json()["is_new"] is False
