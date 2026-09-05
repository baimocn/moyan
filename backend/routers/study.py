"""墨衍 · 学习档案路由（会话历史 / 薄弱点 / 掌握度 / 续学）"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth.deps import CurrentUser, get_requester
from ..container import EngineNotReadyError, get_services
from ..models import repo

router = APIRouter(prefix="/api/study", tags=["study"])


def _ensure_review_owner(srv, session_id: str, user: CurrentUser) -> None:
    """SEC-01：复习会话归属校验；不存在/不属于请求者一律 404。"""
    ses = srv.review.get(session_id)
    if ses is None:
        raise HTTPException(404, detail="复习会话不存在（服务重启后需重新 start）")
    if not repo.session_owned_by(ses.owner or None, user.openid, user.role):
        raise HTTPException(404, detail="复习会话不存在（服务重启后需重新 start）")


class ResumeReq(BaseModel):
    session_id: str


@router.get("/{doc_id}/sessions")
def sessions(doc_id: str):
    return {"ok": True, "sessions": repo.list_sessions(doc_id)}


@router.get("/{doc_id}/weaknesses")
def weaknesses(doc_id: str):
    return {"ok": True, "weaknesses": repo.list_weaknesses(doc_id)}


@router.get("/{doc_id}/stats")
def stats(doc_id: str):
    return {"ok": True, "stats": repo.study_stats(doc_id)}


@router.get("/{doc_id}/reviews")
def due_reviews(doc_id: str, limit: int = 30):
    """到期待复习的薄弱点（复习调度 = due ∩ 薄弱，FSRS 排序）。"""
    return {"ok": True, "reviews": repo.due_reviews(doc_id, limit=min(limit, 100))}


@router.get("/{doc_id}/chapters")
def chapter_overview(doc_id: str):
    """概念级 → 章节级聚合：每章到期/掌握度画像（复习/导航用）。"""
    return {"ok": True, "overview": repo.chapter_overview(doc_id)}


@router.get("/{doc_id}/strategy-stats")
def strategy_stats(doc_id: str, skill_id: str = ""):
    """教学策略效果聚合（Groove）：skill × 讲法 → 样本/平均效果/裁判通过率。"""
    return {"ok": True, "stats": repo.strategy_stats(doc_id, skill_id)}


@router.get("/{doc_id}/traces/{skill_id}")
def traces(doc_id: str, skill_id: str):
    """学习轨迹（Tracer）：某知识点的判定/掌握度/策略反馈时间线。"""
    return {"ok": True, "trace": repo.traces(doc_id, skill_id)}


class ReviewReq(BaseModel):
    doc_id: str
    skill_id: str
    rating: str = Field(pattern="^(again|hard|good|easy)$")


@router.post("/review")
def record_review(req: ReviewReq):
    """记录一次复习结果并按 FSRS 重排（again/hard/good/easy）。"""
    try:
        row = repo.record_review(req.doc_id, req.skill_id, req.rating)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    if row is None:
        raise HTTPException(404, detail="薄弱点不存在")
    return {"ok": True, "review": row}


class ReviewStartReq(BaseModel):
    doc_id: str
    limit: int = Field(default=20, ge=1, le=100)


@router.post("/review-session/start")
def review_session_start(req: ReviewStartReq, user: CurrentUser = Depends(get_requester)):
    """开始复习会话：取到期队列（含教材微点，供失败回收重讲）。SEC-01：落 owner。"""
    ses = get_services().review.start(req.doc_id, limit=req.limit, owner=user.openid)
    return {
        "ok": True,
        "session_id": ses.session_id,
        "count": len(ses.queue),
        "queue": [it.to_event() for it in ses.queue],
    }


class ReviewAnswerReq(BaseModel):
    skill_id: str
    rating: str = Field(pattern="^(again|hard|good|easy)$")


@router.post("/review-session/{session_id}/answer")
def review_session_answer(session_id: str, req: ReviewAnswerReq,
                          user: CurrentUser = Depends(get_requester)):
    """答一项：非 again 出队；again 触发失败回收（片段重讲 + 留队再答）。"""
    srv = get_services()
    _ensure_review_owner(srv, session_id, user)
    try:
        return srv.review.answer(session_id, req.skill_id, req.rating)
    except KeyError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.get("/review-session/{session_id}")
def review_session_summary(session_id: str, user: CurrentUser = Depends(get_requester)):
    srv = get_services()
    _ensure_review_owner(srv, session_id, user)
    try:
        return {"ok": True, "summary": srv.review.summary(session_id)}
    except KeyError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.post("/resume")
def resume(req: ResumeReq, user: CurrentUser = Depends(get_requester)):
    srv = get_services()
    try:
        srv.require_real()
    except EngineNotReadyError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    rec = repo.load_session(req.session_id)
    if rec is None or not repo.session_owned_by(rec.get("user_id"), user.openid, user.role):
        raise HTTPException(404, detail="会话不存在或不属于本服务")
    ses = srv.tutor.resume_session(req.session_id)
    if ses is None:
        raise HTTPException(404, detail="会话不存在或不属于本服务")
    return {
        "ok": True,
        "session_id": ses.session_id,
        "doc_id": ses.doc_id,
        "chapter": ses.chapter_title,
        "state": ses.state.value,
        "kp_idx": ses.kp_idx,
        "weak": ses.weak,
        "plan": [{"id": k.id, "name": k.name, "summary": k.summary} for k in ses.plan.kps],
    }