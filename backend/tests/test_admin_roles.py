"""Phase 1 权限分层与生产安全硬校验单测（ADMIN-01/02/03，2026-09-04）

覆盖：
1) admin_set 解析（空/多值/中文逗号/空格）
2) role 计算：管理员命中 admin、普通 Bearer user、设备 anon、mock admin
3) require_admin：admin 放行 200，user/anon 403（API 级，挂临时路由）
4) /me 返回 role
5) apply_production_safety：production + auth_disabled → 强制 False
6) dev-login 生产环境 403（双保险）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os_env = __import__("os").environ
os_env.setdefault("MOYAN_AUTH_DISABLED", "0")
os_env.setdefault("MOYAN_JWT_SECRET", "test-secret-please-do-not-use-in-prod")

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.auth.deps import get_requester, require_admin
from backend.auth.jwt import sign_token
from backend.auth.router import router as auth_router
from backend.settings import app_settings, apply_production_safety


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(auth_router)

    @app.get("/admin-only")
    def admin_only(user=Depends(require_admin)):  # noqa: ANN001
        return {"ok": True, "role": user.role}

    return TestClient(app)


@pytest.fixture()
def set_admins(monkeypatch):
    """显式控制管理员清单（不用模块级 setdefault——共享单例顺序坑）。"""
    def _set(raw: str):
        monkeypatch.setattr("backend.settings.app_settings.admin_openids", raw)
    return _set


# ---- 1) admin_set 解析 ----

def test_admin_set_parsing(set_admins):
    set_admins("")
    assert app_settings.admin_set == frozenset()
    set_admins("oX123, oX456，oX789  oX000")
    assert app_settings.admin_set == frozenset({"oX123", "oX456", "oX789", "oX000"})


def test_is_production_flag(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.env", "dev")
    assert not app_settings.is_production
    monkeypatch.setattr("backend.settings.app_settings.env", "production")
    assert app_settings.is_production


# ---- 2) role 计算 ----

def test_role_admin_when_listed(client, set_admins):
    set_admins("oX-admin-001")
    tok = sign_token("oX-admin-001")
    r = client.get("/admin-only", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200 and r.json()["role"] == "admin"


def test_role_user_when_not_listed(client, set_admins):
    set_admins("oX-someone-else")
    tok = sign_token("oX-normal-user")
    r = client.get("/admin-only", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 403


def test_role_anon_device_rejected(client, set_admins):
    set_admins("oX-admin-001")
    r = client.get("/admin-only", headers={"X-Device-Id": "abcd1234wxyz"})
    assert r.status_code == 403


def test_role_anon_no_headers_rejected(client, set_admins):
    set_admins("")
    r = client.get("/admin-only")
    assert r.status_code == 403


def test_me_returns_role(client, set_admins):
    set_admins("oX-admin-001")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {sign_token('oX-admin-001')}"})
    # /me 需要查 user_profiles；测试库已由 conftest 初始化。首查可能无档案走兜底分支——两种分支都应带 role
    assert r.status_code == 200
    assert r.json().get("role") == "admin"


# ---- 3) 生产安全硬校验 ----

def test_production_forces_auth_disabled_off(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.env", "production")
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    actions = apply_production_safety()
    assert app_settings.auth_disabled is False
    assert any("auth_disabled" in a for a in actions)


def test_dev_keeps_auth_disabled(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.env", "dev")
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    actions = apply_production_safety()
    assert app_settings.auth_disabled is True
    assert actions == []


def test_dev_login_blocked_in_production(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.env", "production")
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    r = client.post("/api/auth/dev-login", json={"dev_openid": "someone"})
    assert r.status_code == 403


def test_dev_login_still_works_in_dev(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.env", "dev")
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    r = client.post("/api/auth/dev-login", json={"dev_openid": "someone"})
    assert r.status_code == 200
