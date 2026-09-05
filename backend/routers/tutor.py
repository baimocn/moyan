"""墨衍 · 教学路由（章节导航式：start / turn-SSE）

依赖注入：服务从容器取（container.get_services）；未配置 AI 且 mock 未开 → 503。
鉴权：start / turn 用 get_requester（Bearer 有效走真实用户；网页匿名走 X-Device-Id 设备身份）。
限流：L_TUTOR（30/minute，按 user_id / IP 兑底）。
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..auth.deps import CurrentUser, get_requester
from ..container import EngineNotReadyError, get_services
from ..ledger import ai_scope, budget_state
from ..models import repo
from ..rate_limit import L_TUTOR, limiter

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


def _ensure_session_owner(srv, session_id: str, user: CurrentUser) -> None:
    """SEC-01：会话存在且属于请求者，否则一律 404（不暴露存在性）。

    在飞内存会话优先取 user_id；否则查档案（load_session 已带 user_id）。
    """
    ses = srv.tutor.sessions.get(session_id)
    if ses is not None:
        owner = ses.user_id or None
    else:
        rec = repo.load_session(session_id)
        if rec is None:
            raise HTTPException(404, detail="会话不存在（请先 POST /api/tutor/start 或 /api/study/resume）")
        owner = rec.get("user_id")
    if not repo.session_owned_by(owner, user.openid, user.role):
        raise HTTPException(404, detail="会话不存在（请先 POST /api/tutor/start 或 /api/study/resume）")


class StartReq(BaseModel):
    doc_id: str
    chapter_index: int = Field(default=0, ge=0)


class TurnReq(BaseModel):
    session_id: str
    user_text: str = Field(default="")


@router.post("/start")
@limiter.limit(L_TUTOR)
async def tutor_start(request: Request, response: Response, req: StartReq,
                      user: CurrentUser = Depends(get_requester)):
    srv = get_services()
    try:
        srv.require_real()
    except EngineNotReadyError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    if budget_state() == "hard":
        raise HTTPException(429, detail="今日 AI 预算已用尽")
    try:
        ses = await srv.tutor.start_chapter(req.doc_id, req.chapter_index,
                                             user_id=user.openid)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    return {
        "ok": True,
        "session_id": ses.session_id,
        "doc_id": ses.doc_id,
        "chapter": ses.chapter_title,
        "state": ses.state.value,
        "engine": "mock" if srv.mock else "real",
        "greeting": getattr(ses, "greeting", ""),
        "plan": [{"id": k.id, "name": k.name, "summary": k.summary} for k in ses.plan.kps],
        "user_id": user.openid,
    }


@router.post("/turn")
@limiter.limit(L_TUTOR)
async def tutor_turn(request: Request, response: Response, req: TurnReq,
                     user: CurrentUser = Depends(get_requester)):
    srv = get_services()
    try:
        srv.require_real()
    except EngineNotReadyError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    if budget_state() == "hard":
        raise HTTPException(429, detail="今日 AI 预算已用尽")
    _ensure_session_owner(srv, req.session_id, user)
    if not srv.tutor.try_begin_turn(req.session_id):
        raise HTTPException(409, detail="上一轮仍在进行中，请稍候")

    async def gen():
        try:
            # 本轮所有真实 AI 调用（讲解流/判定/出题/质检）统一记 tutor_turn 台账
            with ai_scope("tutor_turn", session_id=req.session_id,
                          user_id=user.openid or None):
                async for ev in srv.tutor.handle_turn(req.session_id, req.user_text,
                                                      user_id=user.openid):
                    yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as exc:  # noqa: BLE001 流中兜底，前端可感知而非挂死
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)}, ensure_ascii=False)}\n\n"
        finally:
            srv.tutor.end_turn(req.session_id)   # SEC-03：异常/断连路径必然释放
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )