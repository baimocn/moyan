"""网页版注册/登录单测（2026-09-03 网页版 MVP 阶段1）

覆盖：
1) 密码哈希 round-trip（scrypt）+ 错误密码拒绝 + 坏格式不抛异常
2) register 成功 → 200 + is_new=True + user_id web_ 前缀
3) register 邮箱重复 → 409
4) register 邮箱格式无效 / 密码过短 → 422
5) login 成功 → 200 + token 可访问 /me
6) login 密码错误 → 401；邮箱不存在 → 401（同样文案防枚举）
7) login 大小写邮箱归一化
8) wx 用户（无 email）不受影响：register 新邮箱不冲突
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-please-do-not-use-in-prod")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.auth.passwords import hash_password, verify_password
from backend.auth.router import router as auth_router
from backend.models.db import SessionLocal
from sqlalchemy import text


# ---- 1) 密码哈希 ----

def test_password_hash_roundtrip():
    h = hash_password("S3cure-passw0rd!")
    assert h.startswith("scrypt$")
    assert verify_password("S3cure-passw0rd!", h) is True


def test_password_hash_wrong_password_rejected():
    h = hash_password("correct-horse")
    assert verify_password("wrong-battery", h) is False


def test_password_hash_bad_format_safe():
    """坏格式/None 不抛异常，一律 False。"""
    assert verify_password("x", "not-a-valid-format") is False
    assert verify_password("x", "") is False
    assert verify_password("x", "bcrypt$1$2$zz$zz") is False


def test_password_hash_unique_salt():
    a, b = hash_password("same"), hash_password("same")
    assert a != b  # 盐随机


# ---- 2-8) HTTP 路由 ----

def _client() -> TestClient:
    a = FastAPI()
    a.include_router(auth_router)
    return TestClient(a)


def _unique_email() -> str:
    return f"t-{uuid.uuid4().hex[:10]}@moyan.test"


def test_register_success():
    email = _unique_email()
    r = _client().post("/api/auth/register",
                       json={"email": email, "password": "password123", "nick_name": "网页用户"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_new"] is True
    assert body["user_id"].startswith("web_")
    assert body["token"]
    # 落库校验
    db = SessionLocal()
    try:
        row = db.execute(text(
            "SELECT auth_type, email, nick_name, password_hash FROM user_profiles "
            "WHERE user_id=:u"), {"u": body["user_id"]}).first()
    finally:
        db.close()
    assert row is not None
    assert row[0] == "web"
    assert row[1] == email
    assert verify_password("password123", row[3])


def test_register_duplicate_email_409():
    email = _unique_email()
    c = _client()
    r1 = c.post("/api/auth/register", json={"email": email, "password": "password123"})
    assert r1.status_code == 200
    r2 = c.post("/api/auth/register", json={"email": email, "password": "other-pass-9"})
    assert r2.status_code == 409


def test_register_invalid_email_422():
    r = _client().post("/api/auth/register",
                       json={"email": "not-an-email", "password": "password123"})
    assert r.status_code == 422


def test_register_short_password_422():
    r = _client().post("/api/auth/register",
                       json={"email": _unique_email(), "password": "short"})
    assert r.status_code == 422


def test_login_success_and_me():
    email = _unique_email()
    c = _client()
    c.post("/api/auth/register", json={"email": email, "password": "password123"})
    r = c.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_new"] is False
    assert body["user_id"].startswith("web_")
    # token 可访问 /me
    r2 = c.get("/api/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
    assert r2.status_code == 200
    assert r2.json()["user_id"] == body["user_id"]


def test_login_wrong_password_401():
    email = _unique_email()
    c = _client()
    c.post("/api/auth/register", json={"email": email, "password": "password123"})
    r = c.post("/api/auth/login", json={"email": email, "password": "wrong-pass-1"})
    assert r.status_code == 401
    assert "邮箱或密码错误" in r.json()["detail"]


def test_login_unknown_email_same_message():
    """邮箱不存在与密码错误返回同一文案（防用户枚举）。"""
    c = _client()
    r = c.post("/api/auth/login",
               json={"email": f"ghost-{uuid.uuid4().hex[:6]}@moyan.test",
                     "password": "whatever-123"})
    assert r.status_code == 401
    assert r.json()["detail"] == "邮箱或密码错误"


def test_login_email_case_insensitive():
    email = _unique_email()
    c = _client()
    c.post("/api/auth/register", json={"email": email, "password": "password123"})
    r = c.post("/api/auth/login",
               json={"email": email.upper(), "password": "password123"})
    assert r.status_code == 200, r.text


def test_register_new_email_no_conflict_with_wx_users():
    """老 wx 用户（email=NULL）不与新注册冲突。"""
    from backend.auth.router import _upsert_profile
    openid = f"oX-wxlegacy-{uuid.uuid4().hex[:8]}"
    db = SessionLocal()
    try:
        assert _upsert_profile(db, openid, "", "") is True
    finally:
        db.close()
    email = _unique_email()
    r = _client().post("/api/auth/register",
                       json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.text
