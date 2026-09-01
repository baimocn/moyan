"""墨衍 · 任务路由（OCR 进度轮询）"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import SessionLocal, Task

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks/{task_id}")
def task_detail(task_id: str):
    with SessionLocal() as db:
        t = db.get(Task, task_id)
        if t is None:
            raise HTTPException(404, detail="任务不存在")
        return {
            "ok": True,
            "task": {
                "id": t.id,
                "doc_id": t.doc_id,
                "kind": t.kind,
                "status": t.status,
                "total_pages": t.total_pages,
                "done_pages": t.done_pages,
                "progress": round(t.progress or 0, 3),
                "message": t.message,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "finished_at": t.finished_at.isoformat() if t.finished_at else None,
            },
        }