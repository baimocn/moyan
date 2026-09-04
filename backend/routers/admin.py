"""墨衍 · 管理统计接口（Phase 3 COST-01 / STATS-03，require_admin 闸门）

GET  /api/admin/usage  AI token 台账：按天×endpoint×模型聚合（默认近30天）+ 总计
GET  /api/admin/stats  平台总览：PV/UV/来源分布 + 教学轮次/文档数 + token 消耗
POST /api/admin/login  网页管理台口令登录（Phase 4）：口令 → 管理员 openid 长效 JWT
                       （非用户登录层：网页端仍免登录，只是管理员开门锁）
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel
from sqlalchemy import distinct, func

from ..auth.deps import CurrentUser, require_admin
from ..auth.jwt import sign_token
from ..models import AiUsage, Document, PageView, SessionLocal, TeachingSession, Turn
from ..rate_limit import limiter
from ..settings import app_settings

router = APIRouter(prefix="/api/admin", tags=["admin"])

# "今日"按北京时间 0 点切（用户在中国；created_at 存 UTC timestamptz，比较即时区自洽）
_CST = timezone(timedelta(hours=8))


def _day_start() -> datetime:
    now_cst = datetime.now(_CST)
    return now_cst.replace(hour=0, minute=0, second=0, microsecond=0)


# ---- Phase 4：网页管理台口令登录（ADMIN-04）----

_ADMIN_TOKEN_DAYS = 30


class AdminLoginReq(BaseModel):
    password: str = ""


@router.post("/login")
@limiter.limit("10/minute")  # 防口令爆破（限流档与 L_HEAVY 同级）
def admin_login(request: Request, response: Response, body: AdminLoginReq):
    """口令 → 管理员 JWT。

    语义：口令 = 站长钥匙，不是用户账号体系。正确则给首个管理员 openid 签
    30 天 token（role=admin 由 ADMIN_OPENIDS 判定，天然自洽）。
    """
    expected = (app_settings.admin_web_password or "").strip()
    if not expected:
        raise HTTPException(404, detail="管理台入口未开启（未配置管理口令）")
    if not secrets.compare_digest((body.password or "").strip(), expected):
        raise HTTPException(403, detail="口令错误")
    openid = next(iter(sorted(app_settings.admin_set)), "")
    if not openid:
        raise HTTPException(
            409, detail="已配置口令但未配置管理员清单（MOYAN_ADMIN_OPENIDS），无法签发身份")
    token = sign_token(openid, exp_seconds=_ADMIN_TOKEN_DAYS * 24 * 3600)
    return {"ok": True, "token": token, "role": "admin",
            "expires_in_days": _ADMIN_TOKEN_DAYS}


# ---- Phase 5：向量知识库管理（VEC-01/02/03，管理员显式触发防烧钱）----

@router.post("/vec/index/{doc_id}")
def vec_build_index(doc_id: str, admin: CurrentUser = Depends(require_admin)):
    """为教材建向量索引（切片+嵌入）。重复调用=重建。未配 embedding 时只落切片。"""
    from .. import vec
    result = vec.build_index(doc_id)
    if not result.get("ok"):
        raise HTTPException(422, detail=result.get("error") or "建索引失败")
    return result


@router.get("/vec/status/{doc_id}")
def vec_index_status(doc_id: str, admin: CurrentUser = Depends(require_admin)):
    from .. import vec
    return {"ok": True, **vec.index_status(doc_id)}


@router.get("/vec/search")
def vec_search(doc_id: str, q: str, top_k: int = Query(default=4, ge=1, le=20),
               admin: CurrentUser = Depends(require_admin)):
    """检索调试：验证某本书的向量索引质量。"""
    from .. import vec
    hits = vec.search(doc_id, q, top_k=top_k)
    return {"ok": True, "doc_id": doc_id, "q": q, "hits": hits}


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
