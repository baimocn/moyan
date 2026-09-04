"""墨衍 · 文档查询路由（从 PostgreSQL 读取）"""
from __future__ import annotations

import logging
import shutil

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, or_, text

from .. import storage
from ..auth.deps import require_admin
from ..auth.deps import CurrentUser, get_requester
from ..config import CHAPTERS_DIR, MARKDOWN_DIR, UPLOAD_DIR
from ..engine.title_check import check_title_async
from ..models import Document, SessionLocal
from ..models.study import Judgement, StrategyLog, TeachingSession, Turn, Weakness
from ..models.tasks import Task
from ..models.vec import DocumentChunk

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


_DOC_EXTS = (".pdf", ".md", ".docx", ".doc", ".txt", ".wps", ".ppt", ".pptx")


def _clean_display_title(title: str, filename: str) -> str:
    """书架展示名：title 非空且不等于 filename 时原样返回；
    否则去掉常见文档扩展名（大小写不敏感），结果为空则兜底。"""
    name = title or filename or ""
    low = name.lower()
    for ext in _DOC_EXTS:
        if low.endswith(ext):
            name = name[: -len(ext)].strip()
            break
    return name or "未命名教材"


def _doc_to_dict(doc: Document, db=None) -> dict:
    title = _display_name(doc, db)
    return {
        "doc_id": doc.doc_id,
        "filename": doc.filename,
        "title": title,
        "display_title": _clean_display_title(title, doc.filename or ""),
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
async def rename_document(doc_id: str, body: RenameIn,
                          user: CurrentUser = Depends(get_requester)):
    """书籍自定义命名（教学计划列表展示用，不动底层文件名）。

    权限策略（REN-01，2026-09-04）：删除收敛到管理台（ADMIN-02）；重命名保留给
    用户层，但非 admin 改名需先过 AI「新名称-内容相符」审核，不符 422 拒绝。
    fail-open：审核服务异常放行（见 engine/title_check.py）。
    """
    title = body.title.strip()
    if not title:
        raise HTTPException(400, detail="名称不能为空")
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            raise HTTPException(404, detail="文档不存在")
        if user.role != "admin":
            md = ""
            try:
                md_path = MARKDOWN_DIR / f"{doc_id}.md"
                if md_path.exists():
                    md = md_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                md = ""
            chapter_titles = [c.get("title", "")
                              for c in (doc.manifest or []) if isinstance(c, dict)]
            check = await check_title_async(title[:200], md, chapter_titles)
            if not check["match"]:
                raise HTTPException(
                    422, detail=f"改名未通过审核：{check['reason'] or '新名称与文档内容不符'}")
        doc.title = title[:200]
        db.commit()
        data = _doc_to_dict(doc)
    return {"ok": True, "document": data}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, admin: CurrentUser = Depends(require_admin)):
    """删除文档（ADMIN-02 首个真实挂载点，require_admin 403 闸门）。

    级联清理（单事务，PG FK 安全顺序）：
    turns / judgements（该书会话的子行）→ weaknesses / strategy_logs（按 doc_id）
    → teaching_sessions → tasks → documents。
    文件产物（markdown / chapters / uploads 残壳）在事务提交后尽力删，缺失不报错。
    content_hash 行随文档消失 → 同书之后可重新完整上传，去重不受污染。
    """
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            raise HTTPException(404, detail="文档不存在")

        session_ids = [
            row[0]
            for row in db.execute(
                text("SELECT id FROM teaching_sessions WHERE doc_id=:d"),
                {"d": doc_id},
            ).fetchall()
        ]
        counts = {"sessions": len(session_ids)}
        if session_ids:
            counts["turns"] = db.execute(
                sa_delete(Turn).where(Turn.session_id.in_(session_ids))
            ).rowcount
            counts["judgements"] = db.execute(
                sa_delete(Judgement).where(Judgement.session_id.in_(session_ids))
            ).rowcount
        else:
            counts["turns"] = counts["judgements"] = 0
        counts["weaknesses"] = db.execute(
            sa_delete(Weakness).where(Weakness.doc_id == doc_id)
        ).rowcount
        counts["strategy_logs"] = db.execute(
            sa_delete(StrategyLog).where(StrategyLog.doc_id == doc_id)
        ).rowcount
        db.execute(sa_delete(TeachingSession).where(TeachingSession.doc_id == doc_id))
        counts["tasks"] = db.execute(sa_delete(Task).where(Task.doc_id == doc_id)).rowcount
        # 向量切片（Phase 5 VEC-05：挂在 DOC-01 清理链上）
        counts["chunks"] = db.execute(
            sa_delete(DocumentChunk).where(DocumentChunk.doc_id == doc_id)).rowcount
        db.delete(doc)
        db.commit()

    # 文件清理：DB 已提交，尽力删（缺失/权限失败不影响响应，仅记日志）
    for path in (MARKDOWN_DIR / f"{doc_id}.md",):
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:  # noqa: BLE001
            logging.getLogger("moyan.documents").warning("删除文件失败 %s: %s", path, exc)
    for dir_path in (CHAPTERS_DIR / doc_id, UPLOAD_DIR / doc_id):
        try:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        except OSError as exc:  # noqa: BLE001
            logging.getLogger("moyan.documents").warning("删除目录失败 %s: %s", dir_path, exc)

    return {"ok": True, "deleted": counts}


@router.get("/documents")
def list_documents(q: str = ""):
    """共享书架（全用户 done 文档可见）。q 非空时按 title/filename 过滤（共享书库搜索）。

    多词 AND：按空白拆词，每个词都须命中（大小写不敏感子串）——"python 快速"
    能命中《Python 快速上手》，整段 LIKE 匹配不到。
    """
    raw = (q or "").strip().lower()
    keywords = [w for w in raw.split() if w]
    with SessionLocal() as db:
        query = db.query(Document)
        for w in keywords:
            like = f"%{w}%"
            query = query.filter(or_(
                func.lower(Document.title).contains(like),
                func.lower(Document.filename).contains(like),
            ))
        docs = query.order_by(Document.created_at.desc()).limit(200).all()
        items = []
        for d in docs:
            item = _doc_to_dict(d, db)
            item.pop("manifest", None)
            items.append(item)
    return {"ok": True, "documents": items, "q": raw}


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