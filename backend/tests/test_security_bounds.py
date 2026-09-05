"""SEC-01..04 安全与成本边界回归锁（2026-09-05，Phase 07-01）

覆盖：
- SEC-01 会话归属：session_owned_by 真值表 + tutor turn/resume + review-session API 级 404
- SEC-02 生成上限：_default_max_tokens 注入 + Provider.chat kwargs 实证
- SEC-03 并发锁：try_begin_turn/end_turn 语义 + API 级 409 + 异常释放
- SEC-04 预算熔断：budget_state 三态 + Router 硬顶抛 BudgetExceeded / 软顶优先 cheap

约定：本模块全程关闭 slowapi（避免与 test_rate_limit 共享 ip:testclient 窗口互相污染）。
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os

os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-security-bounds")
os.environ.setdefault("MOYAN_WX_APPID", "wx-test-appid-sec")
os.environ.setdefault("MOYAN_WX_APPSECRET", "test-app-secret-sec-bounds")

from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.auth.deps import app_settings
from backend.engine import EngineConfig
from backend.engine.providers import BudgetExceeded, Provider, _default_max_tokens
from backend.engine.review.service import ReviewService
from backend.engine.router import Router
from backend.engine.tutor.service import TutorService
from backend.main import app as real_app
from backend.models import repo
from backend.rate_limit import limiter

A_DID = "owneraaa123"          # → web_owneraaa123
B_DID = "ownerbbb123"          # → web_ownerbbb123
A_HDR = {"X-Device-Id": A_DID}
B_HDR = {"X-Device-Id": B_DID}
ANON_HDR = {}                  # 无 header → web_anon


@pytest.fixture(autouse=True)
def _env_setup(monkeypatch):
    """关限流 + 实名鉴权开启 + 预算默认关。"""
    monkeypatch.setattr(limiter, "enabled", False)
    monkeypatch.setattr(app_settings, "auth_disabled", False)
    monkeypatch.setattr(app_settings, "daily_token_budget", 0)
    monkeypatch.setattr(app_settings, "daily_token_hard", 0)
    yield


def _stub_container(tutor_svc=None, review_svc=None):
    return SimpleNamespace(
        require_real=lambda: None, mock=True,
        tutor=tutor_svc or TutorService(),
        review=review_svc or ReviewService(),
    )


# ================= SEC-01：归属判定 =================

def test_session_owned_by_truth_table():
    f = repo.session_owned_by
    assert f("web_a", "web_a") is True
    assert f("web_a", "web_b") is False
    assert f(None, "web_a") is False                    # NULL owner 对实名不可见
    assert f(None, "web_anon") is True                  # 仅 web_anon 可续游客会话
    assert f(None, "web_a", role="admin") is True       # admin 豁免
    assert f("web_a", "web_b", role="admin") is True
    assert f("", "web_anon") is True                    # 空串视同 NULL
    assert f("web_a", "web_anon") is False              # 匿名不能冒实名


def _seed(session_id: str, user_id: str | None) -> None:
    repo.save_session(session_id, "doc-secx", 0, "第1章", "explain", 0, [], {},
                      user_id=user_id)


def test_turn_ownership_404_and_owner_200(monkeypatch):
    _seed("s_secown1", f"web_{A_DID}")
    svc = TutorService()
    monkeypatch.setattr("backend.routers.tutor.get_services", lambda: _stub_container(svc))
    c = TestClient(real_app)

    r_b = c.post("/api/tutor/turn", headers=B_HDR,
                 json={"session_id": "s_secown1", "user_text": "hi"})
    assert r_b.status_code == 404, r_b.text            # B 访问 A 的会话 → 404

    r_a = c.post("/api/tutor/turn", headers=A_HDR,
                 json={"session_id": "s_secown1", "user_text": "hi"})
    assert r_a.status_code == 200, r_a.text            # owner 正常进入流

    r_missing = c.post("/api/tutor/turn", headers=A_HDR,
                       json={"session_id": "s_nosuch", "user_text": "hi"})
    assert r_missing.status_code == 404


def test_resume_ownership_and_null_owner_rule(monkeypatch):
    _seed("s_secown2", f"web_{A_DID}")
    _seed("s_secnull", None)
    svc = TutorService()
    monkeypatch.setattr("backend.routers.study.get_services", lambda: _stub_container(svc))
    c = TestClient(real_app)

    assert c.post("/api/study/resume", headers=B_HDR,
                  json={"session_id": "s_secown2"}).status_code == 404
    assert c.post("/api/study/resume", headers=A_HDR,
                  json={"session_id": "s_secown2"}).status_code == 200
    # NULL-owner：实名用户不可见，web_anon 可续
    assert c.post("/api/study/resume", headers=A_HDR,
                  json={"session_id": "s_secnull"}).status_code == 404
    assert c.post("/api/study/resume", headers=ANON_HDR,
                  json={"session_id": "s_secnull"}).status_code == 200


def test_review_session_ownership(monkeypatch):
    rsvc = ReviewService()
    monkeypatch.setattr("backend.routers.study.get_services",
                        lambda: _stub_container(review_svc=rsvc))
    c = TestClient(real_app)

    r = c.post("/api/study/review-session/start", headers=A_HDR,
               json={"doc_id": "doc-secx", "limit": 5})
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]
    assert rsvc.get(sid).owner == f"web_{A_DID}"       # start 落 owner

    assert c.post(f"/api/study/review-session/{sid}/answer", headers=B_HDR,
                  json={"skill_id": "kp1", "rating": "good"}).status_code == 404
    assert c.get(f"/api/study/review-session/{sid}", headers=B_HDR).status_code == 404
    assert c.get(f"/api/study/review-session/{sid}", headers=A_HDR).status_code == 200


# ================= SEC-03：同会话并发锁 =================

def test_turn_lock_semantics_and_release():
    svc = TutorService()
    assert svc.try_begin_turn("s_lk") is True
    assert svc.try_begin_turn("s_lk") is False          # 在飞 → 拒绝
    svc.end_turn("s_lk")
    assert svc.try_begin_turn("s_lk") is True           # 释放后可再入
    svc.end_turn("s_lk")
    svc.end_turn("s_lk")                                # 幂等


def test_turn_lock_api_409(monkeypatch):
    _seed("s_secown3", f"web_{A_DID}")
    svc = TutorService()
    monkeypatch.setattr("backend.routers.tutor.get_services", lambda: _stub_container(svc))
    c = TestClient(real_app)

    assert svc.try_begin_turn("s_secown3") is True      # 模拟上一轮在飞
    r = c.post("/api/tutor/turn", headers=A_HDR,
               json={"session_id": "s_secown3", "user_text": "hi"})
    assert r.status_code == 409, r.text
    svc.end_turn("s_secown3")
    r2 = c.post("/api/tutor/turn", headers=A_HDR,
                json={"session_id": "s_secown3", "user_text": "hi"})
    assert r2.status_code == 200                        # 释放后恢复


# ================= SEC-02：生成上限 =================

def test_default_max_tokens_settings_and_cheap_halved(monkeypatch):
    monkeypatch.setattr(app_settings, "gen_max_tokens", 4000)
    assert _default_max_tokens("main") == 4000
    assert _default_max_tokens("fallback") == 4000
    assert _default_max_tokens("cheap") == 1500         # cheap 档自动减半封顶
    monkeypatch.setattr(app_settings, "gen_max_tokens", 2000)
    assert _default_max_tokens("main") == 2000
    assert _default_max_tokens("cheap") == 1500
    monkeypatch.setattr(app_settings, "gen_max_tokens", 800)
    assert _default_max_tokens("cheap") == 800          # 低于 1500 时取实际值


def test_provider_chat_injects_max_tokens(monkeypatch):
    captured: dict = {}

    class _CapClient:
        class completions:
            pass

    def _make_cap():
        async def create(**kw):
            captured.update(kw)
            return SimpleNamespace(model=kw["model"],
                      usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                      choices=[SimpleNamespace(message=SimpleNamespace(content="ok"), finish_reason="stop")])
        return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    monkeypatch.setattr(app_settings, "gen_max_tokens", 1234)
    p = Provider(EngineConfig(name="main", base_url="http://cap", api_key="k",
                              model="cap-model", enabled=True))
    monkeypatch.setattr(p, "_get_client", lambda: _make_cap())
    monkeypatch.setattr("backend.engine.providers._ledger_record", lambda *a, **k: None)

    import asyncio
    r = asyncio.get_event_loop_policy().new_event_loop().run_until_complete(
        p.chat([{"role": "user", "content": "x"}]))
    assert captured["max_tokens"] == 1234               # 未显式传 → 注入 settings 值
    assert r["content"] == "ok"

    captured.clear()
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.run_until_complete(p.chat([{"role": "user", "content": "x"}], max_tokens=77))
    assert captured["max_tokens"] == 77                 # 显式传参不被覆盖


# ================= SEC-04：预算熔断 =================

def test_budget_state_transitions(monkeypatch):
    from backend import ledger
    monkeypatch.setattr(ledger, "tokens_today", lambda: 100)
    monkeypatch.setattr(app_settings, "daily_token_budget", 0)
    monkeypatch.setattr(app_settings, "daily_token_hard", 0)
    assert ledger.budget_state() == "ok"                # 默认关闭
    monkeypatch.setattr(app_settings, "daily_token_budget", 50)
    assert ledger.budget_state() == "soft"              # 超软顶
    monkeypatch.setattr(app_settings, "daily_token_hard", 80)
    assert ledger.budget_state() == "hard"              # 超硬顶优先
    monkeypatch.setattr(ledger, "tokens_today", lambda: 10)
    assert ledger.budget_state() == "ok"


def test_router_hard_budget_raises(monkeypatch):
    monkeypatch.setattr("backend.engine.router._budget_state", lambda: "hard")
    router = Router(engines=[EngineConfig(name="main", base_url="http://x",
                                          api_key="k", model="m", enabled=True)])
    with pytest.raises(BudgetExceeded):
        import asyncio
        asyncio.get_event_loop_policy().new_event_loop().run_until_complete(
            router.chat([{"role": "user", "content": "x"}]))


def test_router_soft_budget_prefers_cheap(monkeypatch):
    monkeypatch.setattr("backend.engine.router._budget_state", lambda: "soft")

    class _CheapStub:
        cfg = EngineConfig(name="cheap", base_url="http://c", api_key="k", model="cm")

        async def chat(self, messages, **kw):
            return {"content": "cheap-ok", "engine": "cheap"}

    router = Router(engines=[EngineConfig(name="main", base_url="http://x",
                                          api_key="k", model="m", enabled=True)])
    monkeypatch.setattr("backend.engine.router._cheap_provider", lambda: _CheapStub())

    import asyncio
    r = asyncio.get_event_loop_policy().new_event_loop().run_until_complete(
        router.chat([{"role": "user", "content": "x"}]))
    assert r["engine"] == "cheap"                       # 软顶 → cheap 被优先选中
