"""墨衍 · AI 用量台账 + 浏览量记账（Phase 3 COST-01 / STATS-01，2026-09-04）

设计原则：
- fire-and-forget：记账失败只打日志，绝不影响主流程；
- ai_scope：调用链入口设 endpoint/user_id/doc_id/session_id 上下文，
  下游所有真实引擎调用（providers / structured）自动带上下文入账；
- 重试与 failover 的每次真实调用各记一行（如实反映消耗）；
- mock 引擎不记账（无真实成本）。
"""
from __future__ import annotations

import contextvars
import logging
from contextlib import contextmanager

from .models import AiUsage, PageView, SessionLocal

log = logging.getLogger("moyan.ledger")

_scope: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "moyan_ai_ledger_scope", default=None
)


@contextmanager
def ai_scope(endpoint: str, *, user_id: str | None = None,
             doc_id: str | None = None, session_id: str | None = None):
    """标注一段调用链的 AI 台账上下文（tutor_turn / proofread / moderation / ...）。"""
    old = _scope.get()
    _scope.set({"endpoint": endpoint, "user_id": user_id,
                "doc_id": doc_id, "session_id": session_id})
    try:
        yield
    finally:
        _scope.set(old)


def _usage_ints(usage: dict | None) -> tuple[int, int, int, bool]:
    """归一化 usage：真实三值 或 流中断 estimated_tokens 兜底。"""
    u = usage or {}
    if u.get("estimated_tokens") and not u.get("total_tokens"):
        return 0, 0, int(u["estimated_tokens"]), True
    pt = int(u.get("prompt_tokens") or 0)
    ct = int(u.get("completion_tokens") or 0)
    tt = int(u.get("total_tokens") or (pt + ct))
    return pt, ct, tt, False


def record(engine: str = "", model: str = "", usage: dict | None = None,
           *, endpoint: str | None = None) -> None:
    """记一笔 AI 调用（providers / structured 出口调用；endpoint 缺省取 scope）。"""
    try:
        sc = _scope.get() or {}
        pt, ct, tt, est = _usage_ints(usage)
        if tt <= 0:
            return
        with SessionLocal() as db:
            db.add(AiUsage(
                endpoint=endpoint or sc.get("endpoint") or "misc",
                engine=engine or "", model=model or "",
                prompt_tokens=pt, completion_tokens=ct, total_tokens=tt,
                estimated=est,
                user_id=sc.get("user_id"), doc_id=sc.get("doc_id"),
                session_id=sc.get("session_id"),
            ))
            db.commit()
    except Exception as exc:  # noqa: BLE001 记账绝不影响主流程
        log.warning("AI 用量记账失败（忽略）：%s", exc)


def record_pv(source: str, page: str, device_id: str,
              user_id: str | None = None) -> None:
    """记一笔页面浏览（metrics/pv 接口调用；失败忽略）。"""
    try:
        with SessionLocal() as db:
            db.add(PageView(source=source[:8], page=page[:64],
                            device_id=device_id[:64] or "anon", user_id=user_id))
            db.commit()
    except Exception as exc:  # noqa: BLE001
        log.warning("PV 记账失败（忽略）：%s", exc)
