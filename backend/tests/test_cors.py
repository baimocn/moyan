"""CORS 白名单（双前端地基）单测：默认拒绝跨源 / 白名单放行预检"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.settings import app_settings


def _app(origins: str) -> FastAPI:
    """与 main.py 相同的 CORS 装配逻辑（白名单解析在此处统一验证）。"""
    a = FastAPI()
    o = [x.strip() for x in (origins or "").split(",") if x.strip()]
    if o:
        a.add_middleware(CORSMiddleware, allow_origins=o,
                         allow_methods=["*"], allow_headers=["*"])

    @a.get("/ping")
    def ping():
        return {"ok": True}
    return a


def test_default_config_blocks_cross_origin():
    """默认 cors_origins=""（当前 .env 状态）：跨源请求不带 ACAO 头 = 拒绝。"""
    client = TestClient(_app(app_settings.cors_origins))
    r = client.get("/ping", headers={"Origin": "https://evil.example"})
    assert r.status_code == 200            # 请求本身可达（同源部署不受影响）
    assert r.headers.get("access-control-allow-origin") is None


def test_whitelist_allows_preflight():
    a = _app("https://moyan.example, http://localhost:5173")
    client = TestClient(a)
    r = client.options("/ping", headers={
        "Origin": "https://moyan.example",
        "Access-Control-Request-Method": "GET"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "https://moyan.example"
    # 白名单外的源仍被拒
    r2 = client.options("/ping", headers={
        "Origin": "https://evil.example",
        "Access-Control-Request-Method": "GET"})
    assert r.headers.get("access-control-allow-origin", "") == "https://moyan.example"
    assert "evil.example" not in (r2.headers.get("access-control-allow-origin") or "")
