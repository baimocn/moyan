"""墨衍 · 文档查询路由（从 PostgreSQL 读取）"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import storage
from ..models import Document, SessionLocal

router = APIRouter(prefix="/api", tags=["documents"])


def _repair_mojibake(name: str) -> str:
    """历史遗留：multipart/导入的文件名被按 latin-1 误解码成乱码，尝试还原。

    实测两种来源：UTF-8 字节被 latin-1 解码（email 场景）、GBK 字节被 latin-1
    解码（Windows 客户端场景，本项目真题文件即此类）。"""
    if not name:
        return name
    try:
        raw = name.encode("latin-1")
    except UnicodeEncodeError:
        return name  # 已是正常 Unicode 文本
    for enc in ("utf-8", "gbk"):
        try:
            fixed = raw.decode(enc)
            if fixed != name and not any(_looks_mojibake(ch) for ch in fixed):
                return fixed
        except (UnicodeDecodeError, ValueError):
            continue
    return name


def _looks_mojibake(ch: str) -> bool:
    """典型 latin-1 乱码字符（Ã/Ê/Ý 等）残留则视为修复失败。"""
    return ord(ch) in range(0xC0, 0x100) and ch not in "×÷"


def _display_name(doc: Document, db=None) -> str:
    """展示名：title 优先；filename 乱码则顺手修复并落库（幂等）。"""
    if doc.title:
        return doc.title
    fixed = _repair_mojibake(doc.filename or "")
    if fixed != (doc.filename or ""):
        doc.title = fixed
        try:
            if db is not None:
                db.commit()
            else:
                with SessionLocal() as s2:
                    row = s2.get(Document, doc.doc_id)
                    if row is not None and not row.title:
                        row.title = fixed
                        s2.commit()
        except Exception:  # noqa: BLE001 修复失败不影响展示
            pass
        return fixed
    return doc.filename or ""


def _doc_to_dict(doc: Document, db=None) -> dict:
    return {
        "doc_id": doc.doc_id,
        "filename": doc.filename,
        "title": _display_name(doc, db),
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


class RenameIn(BaseModel):
    title: str


@router.patch("/documents/{doc_id}")
def rename_document(doc_id: str, body: RenameIn):
    """书籍自定义命名（教学计划列表展示用，不动底层文件名）。"""
    title = body.title.strip()
    if not title:
        raise HTTPException(400, detail="名称不能为空")
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            raise HTTPException(404, detail="文档不存在")
        doc.title = title[:200]
        db.commit()
        data = _doc_to_dict(doc)
    return {"ok": True, "document": data}


@router.get("/documents")
def list_documents():
    with SessionLocal() as db:
        docs = db.query(Document).order_by(Document.created_at.desc()).limit(200).all()
        items = []
        for d in docs:
            item = _doc_to_dict(d, db)
            item.pop("manifest", None)
            items.append(item)
    return {"ok": True, "documents": items}


@router.get("/documents/{doc_id}")
def document_detail(doc_id: str):
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            raise HTTPException(404, detail="文档不存在")
        data = _doc_to_dict(doc, db)
    return {"ok": True, "document": data}


@router.get("/documents/{doc_id}/chapters/{index}")
def chapter_detail(doc_id: str, index: int):
    item = storage.get_chapter(doc_id, index)
    if item is None:
        raise HTTPException(404, detail="章节不存在")
    return {"ok": True, "chapter": item}