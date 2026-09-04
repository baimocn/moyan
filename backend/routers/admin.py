"""墨衍 · 管理统计接口（Phase 3 COST-01 / STATS-03，require_admin 闸门）

GET /api/admin/usage  AI token 台账：按天×endpoint×模型聚合（默认近30天）+ 总计
GET /api/admin/stats  平台总览：PV/UV/来源分布 + 教学轮次/文档数 + token 消耗
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func

from ..auth.deps import CurrentUser, require_admin
from ..models import AiUsage, Document, PageView, SessionLocal, TeachingSession, Turn

router = APIRouter(prefix="/api/admin", tags=["admin"])

# "今日"按北京时间 0 点切（用户在中国；created_at 存 UTC timestamptz，比较即时区自洽）
_CST = timezone(timedelta(hours=8))


def _day_start() -> datetime:
    now_cst = datetime.now(_CST)
    return now_cst.replace(hour=0, minute=0, second=0, microsecond=0)


@router.get("/usage")
def usage_ledger(days: int = Query(default=30, ge=1, le=365),
                 admin: CurrentUser = Depends(require_admin)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    with SessionLocal() as db:
        rows = (db.query(
                    func.date(AiUsage.created_at).label("day"),
                    AiUsage.endpoint,
                    AiUsage.model,
                    func.coalesce(func.sum(AiUsage.prompt_tokens), 0).label("pt"),
                    func.coalesce(func.sum(AiUsage.completion_tokens), 0).label("ct"),
                    func.coalesce(func.sum(AiUsage.total_tokens), 0).label("tt"),
                    func.count(AiUsage.id).label("calls"),
                )
                .filter(AiUsage.created_at >= since)
                .group_by(func.date(AiUsage.created_at), AiUsage.endpoint, AiUsage.model)
                .order_by(func.date(AiUsage.created_at))
                .all())
        tot = (db.query(
                    func.coalesce(func.sum(AiUsage.prompt_tokens), 0),
                    func.coalesce(func.sum(AiUsage.completion_tokens), 0),
                    func.coalesce(func.sum(AiUsage.total_tokens), 0),
                    func.count(AiUsage.id),
                ).first())
    daily = [{
        "date": str(r.day), "endpoint": r.endpoint, "model": r.model,
        "prompt_tokens": int(r.pt), "completion_tokens": int(r.ct),
        "total_tokens": int(r.tt), "calls": int(r.calls),
    } for r in rows]
    return {
        "ok": True,
        "days": days,
        "total": {
            "prompt_tokens": int(tot[0]), "completion_tokens": int(tot[1]),
            "total_tokens": int(tot[2]), "calls": int(tot[3]),
        },
        "daily": daily,
    }


@router.get("/stats")
def platform_stats(admin: CurrentUser = Depends(require_admin)):
    day0 = _day_start()
    with SessionLocal() as db:
        pv_total = db.query(func.count(PageView.id)).scalar() or 0
        pv_today = (db.query(func.count(PageView.id))
                    .filter(PageView.created_at >= day0).scalar() or 0)
        uv_total = db.query(func.count(distinct(PageView.device_id))).scalar() or 0
        uv_today = (db.query(func.count(distinct(PageView.device_id)))
                    .filter(PageView.created_at >= day0).scalar() or 0)
        src_rows = (db.query(PageView.source, func.count(PageView.id))
                    .group_by(PageView.source).all())
        sources = {r[0] or "unknown": int(r[1]) for r in src_rows}

        turns = db.query(func.count(Turn.id)).scalar() or 0
        sessions = db.query(func.count(TeachingSession.id)).scalar() or 0
        docs_done = (db.query(func.count(Document.doc_id))
                     .filter(Document.status == "done").scalar() or 0)

        tok_today = (db.query(func.coalesce(func.sum(AiUsage.total_tokens), 0))
                     .filter(AiUsage.created_at >= day0).scalar() or 0)
        tok_total = (db.query(func.coalesce(func.sum(AiUsage.total_tokens), 0))
                     .scalar() or 0)
        calls_total = db.query(func.count(AiUsage.id)).scalar() or 0

    return {
        "ok": True,
        "pv": {"today": int(pv_today), "total": int(pv_total)},
        "uv": {"today": int(uv_today), "total": int(uv_total)},
        "sources": sources,
        "teaching": {"turns": int(turns), "sessions": int(sessions), "docs_done": int(docs_done)},
        "tokens": {"today": int(tok_today), "total": int(tok_total), "calls": int(calls_total)},
    }
