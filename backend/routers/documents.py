"""墨衍 · 文档查询路由（从 PostgreSQL 读取）"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import storage
from ..models import Document, SessionLocal

router = APIRouter(prefix="/api", tags=["documents"])


def _doc_to_dict(doc: Document) -> dict:
    return {
        "doc_id": doc.doc_id,
        "filename": doc.filename,
        "format": doc.format,
        "page_count": doc.page_count,
        "source": doc.source,
        "md_chars": doc.md_chars,
        "chapter_count": doc.chapter_count,
        "status": doc.status,
        "warnings": doc.warnings or [],
        "stats": doc.stats or {},
        "manifest": doc.manifest or [],
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }


@router.get("/documents")
def list_documents():
    with SessionLocal() as db:
        docs = db.query(Document).order_by(Document.created_at.desc()).limit(200).all()
    items = []
    for d in docs:
        item = _doc_to_dict(d)
        item.pop("manifest", None)
        items.append(item)
    return {"ok": True, "documents": items}


@router.get("/documents/{doc_id}")
def document_detail(doc_id: str):
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            raise HTTPException(404, detail="文档不存在")
        data = _doc_to_dict(doc)
    return {"ok": True, "document": data}


@router.get("/documents/{doc_id}/chapters/{index}")
def chapter_detail(doc_id: str, index: int):
    item = storage.get_chapter(doc_id, index)
    if item is None:
        raise HTTPException(404, detail="章节不存在")
    return {"ok": True, "chapter": item}