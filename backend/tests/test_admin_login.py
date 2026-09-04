"""Phase 4 网页管理台口令登录单测（ADMIN-04，2026-09-04）

覆盖：
1) 口令未配置 → 404（入口关闭）
2) 口令错误 → 403
3) 口令正确 → 200 + token；token 打管理端点 role=admin
4) 配了口令但管理员清单为空 → 409
5) 签出的 token 实际有效期 ≈ 30 天
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os_env = __import__("os").environ
os_env.setdefault("MOYAN_AUTH_DISABLED", "0")
os_env.setdefault("MOYAN_JWT_SECRET", "test-secret-please-do-not-use-in-prod")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.auth.jwt import decode_unsafe
from backend.routers.admin import router as admin_router
from backend.settings import app_settings


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(admin_router)
    return TestClient(app)


@pytest.fixture()
def cfg(monkeypatch):
    """显式控制口令与管理员清单（共享单例，勿用模块级 setdefault）。"""
    def _set(password: str, openids: str):
        monkeypatch.setattr(app_settings, "admin_web_password", password)
        monkeypatch.setattr(app_settings, "admin_openids", openids)
    return _set


def test_login_disabled_when_no_password(client, cfg):
    cfg("", "oX123")
    r = client.post("/api/admin/login", json={"password": "whatever"})
    assert r.status_code == 404


def test_login_wrong_password(client, cfg):
    cfg("right-pass", "oX123")
    r = client.post("/api/admin/login", json={"password": "wrong"})
    assert r.status_code == 403


def test_login_ok_token_is_admin(client, cfg):
    cfg("right-pass", "oX123,oX456")
    r = client.post("/api/admin/login", json={"password": " right-pass "})  # 容忍首尾空白
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True and body["role"] == "admin"
    # 签给排序后的首个管理员 openid
    payload = decode_unsafe(body["token"])
    assert payload["sub"] == "oX123"
    # 有效期 ≈ 30 天（容差 5 分钟）
    span = payload["exp"] - payload["iat"]
    assert abs(span - 30 * 24 * 3600) < 300


def test_login_token_passes_admin_gate(client, cfg):
    """登录换到的 token 能过 require_admin 闸门（挂真实 admin 路由验证）。"""
    cfg("right-pass", "oX123")
    r = client.post("/api/admin/login", json={"password": "right-pass"})
    token = r.json()["token"]
    r2 = client.get("/api/admin/stats",
                    headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["ok"] is True


def test_login_without_admin_openids_conflict(client, cfg):
    cfg("right-pass", "")
    r = client.post("/api/admin/login", json={"password": "right-pass"})
    assert r.status_code == 409
