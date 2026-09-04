"""墨衍 · 浏览量埋点（STATS-01/02，双前端共用，有人点进来就算）

POST /api/metrics/pv：免鉴权 fire-and-forget；失败恒返回 200（绝不影响前端主流程）。
身份：get_requester——Bearer 有效自动带真实 user_id；网页匿名走 X-Device-Id。
限流：L_GENERAL 120/min 兜底。
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from ..auth.deps import CurrentUser, get_requester
from ..ledger import record_pv
from ..rate_limit import L_GENERAL, limiter

router = APIRouter(prefix="/api", tags=["metrics"])

_DID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class PvIn(BaseModel):
    source: str = "web"      # web | mp
    page: str = ""           # home / tutor / admin ...
    device_id: str = ""      # 前端设备码（网页=uuid，小程序=随机持久 id）


@router.post("/metrics/pv")
@limiter.limit(L_GENERAL)
async def pv(request: Request, response: Response, body: PvIn,
             user: CurrentUser = Depends(get_requester)):
    source = body.source if body.source in ("web", "mp") else "web"
    page = (body.page or "").strip()[:64]
    # 真实用户才落 user_id（mock dev / web 匿名设备都不算）
    real_openid = (user.openid
                   if (user and not user.is_mock and not user.openid.startswith("web_"))
                   else None)
    did = (body.device_id or "").strip()
    if not _DID_RE.match(did):
        did = real_openid or "anon"
    record_pv(source, page, did, user_id=real_openid)
    return {"ok": True}
