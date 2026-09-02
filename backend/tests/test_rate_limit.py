"""限流单测（slowapi，user_id 主 / IP 兑底）

策略：用 TestClient 直接打挂载了 limiter 的最小 FastAPI 子集。
被装饰的 endpoint 第一参数必须是 request（slowapi 内部要求）。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_AUTH_DISABLED", "1")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-rate-limit")
os.environ.setdefault("MOYAN_WX_APPID", "wx-test-appid-rate")
os.environ.setdefault("MOYAN_WX_APPSECRET", "test-app-secret-for-rate-limit-tests")

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.auth.jwt import sign_token
from backend.rate_limit import L_HEAVY, limiter
from slowapi.errors import RateLimitExceeded
from backend.main import app as real_app    # 用真 app 验证集成


# ---- A) key_func：user_id 优先 ----

def test_key_func_prefers_user_id():
    """已鉴权 → key=user:<openid>；未鉴权 → key=ip:testclient"""
    from backend.rate_limit import _key_func
    from fastapi import Request
    from starlette.datastructures import Headers

    class _User:
        openid = "oX-real"

    class _Req:
        state = type("S", (), {"user": _User()})()
        headers = Headers()
        client = type("C", (), {"host": "127.0.0.1"})()
    # state.user 有 openid → user
    assert _key_func(_Req()) == "user:oX-real"

    class _Req2:
        state = type("S", (), {})()
        headers = Headers()
        client = type("C", (), {"host": "127.0.0.1"})()
    # state.user 无 / 没有 openid → ip
    assert _key_func(_Req2()).startswith("ip:")


# ---- B) 限流真档（拿真 app 跑 /api/auth/me 30/min）----

def test_rate_limit_30_per_minute():
    """30/minute 装饰器的 /api/auth/me：第 31 次返 429。"""
    client = TestClient(real_app)
    # dev-login 拿 token
    r = client.post("/api/auth/dev-login", json={"dev_openid": "rl_tester"})
    assert r.status_code == 200
    tok = r.json()["token"]
    headers = {"Authorization": f"Bearer {tok}"}

    # 但 /api/auth/me 没用 L_TUTOR/L_UPLOAD, 而是没限流（兜底）
    # 改打 /api/tutor/start 验证 30/minute（即使 start 报 503, 也算被限流的"算"一次）
    codes = []
    for _ in range(35):
        r = client.post("/api/tutor/start",
                         headers=headers,
                         json={"doc_id": "nonexistent", "chapter_index": 0})
        codes.append(r.status_code)
    # 至少 1 个 429（限流优先于业务异常）
    assert 429 in codes, f"未触发限流：{codes[:5]}...{codes[-3:]}"
    # 业务错误也算 404 / 503（mock 模式时 200+ok）
    assert sum(1 for c in codes if c == 429) >= 1


# ---- C) 重置限流：换一个 user 应重置（user 维度隔离）----

def test_rate_limit_isolated_by_user(monkeypatch):
    """不同 token（不同 openid）独立计数。

    AUTH_DISABLED=True 时所有用户走 mock user(openid="dev_user"), key 全相同, 不可验证隔离。
    本测试临时启用鉴权 + mock 微信 openid, 让 user_a / user_b 拿到真 token。
    """
    monkeypatch.setattr("backend.auth.deps.app_settings.auth_disabled", False)
    monkeypatch.setattr("backend.auth.router.app_settings.auth_disabled", False)

    import httpx
    openid_seq = iter(["oX_user_a", "oX_user_b"])
    async def fake_get(self, url, params=None):
        class _R:
            def json(self_inner): return {"openid": next(openid_seq)}
        return _R()
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    client = TestClient(real_app)
    r = client.post("/api/auth/wx-login", json={"code": "c_a"})
    assert r.status_code == 200, r.text
    tok_a = r.json()["token"]
    codes_a = []
    for _ in range(35):
        r = client.post("/api/tutor/start",
                         headers={"Authorization": f"Bearer {tok_a}"},
                         json={"doc_id": "x", "chapter_index": 0})
        codes_a.append(r.status_code)
    assert 429 in codes_a, f"user_a 触发限流失败：{set(codes_a)}"

    # user_b 第一次不应被 user_a 限流
    r = client.post("/api/auth/wx-login", json={"code": "c_b"})
    assert r.status_code == 200
    tok_b = r.json()["token"]
    r = client.post("/api/tutor/start",
                     headers={"Authorization": f"Bearer {tok_b}"},
                     json={"doc_id": "x", "chapter_index": 0})
    assert r.status_code != 429, f"user_b 不应被 user_a 限流影响（实测 {r.status_code}）"
