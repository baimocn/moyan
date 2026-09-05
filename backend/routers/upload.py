"""墨衍 · 上传路由（服务器模式，Docling 主解析引擎）

分流逻辑：
- md/txt：直读为 Markdown，秒级同步返回；
- 办公格式（docx/pptx/xlsx/html/epub）小件：Docling 直读，同步返回（实测 ~0s）；
- PDF / 图片 / 大件办公：进后台 Docling 任务（布局模型 14~40s/页），返回 task_id 轮询；
- Docling 环境缺失：PDF 回落 legacy（文本层同步 + 扫描件 RapidOCR 异步），其余格式 415。

user_id 注入：用 ContextVar 在请求开始时（依赖注入后）写入，模块级 _save_document_record
            不需参数化即可读，写入 documents 表。
"""
from __future__ import annotations

import contextvars
import hashlib
import shutil

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile

from .. import config, storage, tasks
from ..auth.deps import CurrentUser, get_requester
from ..engine.moderation import (ModerationUnavailable,
                                moderate_markdown_async, stats_entry as mod_stats)
from ..engine.proofread import cleanup_original
from ..models import Document, SessionLocal
from ..rate_limit import L_UPLOAD, limiter
from ..services.chapter_splitter import split_markdown
from ..services.docling_adapter import (convert_sync, docling_available,
                                        preflight)
from ..services.pdf_parser import parse_pdf

router = APIRouter(prefix="/api", tags=["upload"])

# 上下文用户：依赖注入时设置；模块函数读它
_current_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "moyan_current_user_id", default=None
)
# 共享书库去重（2026-09-03）：upload 时算好 sha256，落库自动带上
_current_content_hash: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "moyan_content_hash", default=None
)


# 浏览器/客户端文件名常被 Starlette 按 latin-1 解码（中文乱码），这里尝试还原 UTF-8
def _clean_filename(name: str) -> str:
    if not name:
        return "upload"
    if any(ord(c) > 127 for c in name):
        return name  # 已是正常 Unicode
    try:
        fixed = name.encode("latin-1").decode("utf-8")
        return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def _save_document_record(db, doc_id: str, *, status: str, title: str = "",
                         user_id: str | None = None, **fields) -> None:
    db.add(Document(doc_id=doc_id, status=status, title=title,
                    user_id=user_id,
                    content_hash=_current_content_hash.get(),
                    **fields))
    db.commit()


def _raise_rejected(doc_id: str, mod: dict) -> None:
    """同步路径审核拒绝：清理上传残壳并 422（不落任何库记录与产物）。"""
    shutil.rmtree(config.UPLOAD_DIR / doc_id, ignore_errors=True)
    raise HTTPException(422, detail=f"内容审核未通过：{mod.get('reason') or '内容违规'}")


def _doc_response(doc_id: str, filename: str, ext: str, split, headings,
                  source: str, page_count: int, stats: dict, warnings: list,
                  title: str = "") -> dict:
    """落盘 + 注册 + 组装同步响应。headings 为空时由章节标题推导。"""
    if not headings and split:
        headings = [{"level": c.level, "text": c.title} for c in split.chapters]
    manifest = [
        {
            "index": c.index, "title": c.title, "level": c.level,
            "char_count": c.char_count,
            "toc": [{"level": t.level, "title": t.title} for t in c.toc],
        }
        for c in split.chapters
    ]
    with SessionLocal() as db:
        _save_document_record(
            db, doc_id, status="done", title=title,
            filename=filename, format=ext.lstrip("."),
            page_count=page_count, source=source,
            md_chars=split.total_chars, chapter_count=len(split.chapters),
            headings=[{"level": h.get("level", 1), "text": h.get("text", "")}
                      for h in headings][:200],
            warnings=warnings, stats=stats, manifest=manifest,
        )
    return {
        "ok": True,
        "doc_id": doc_id,
        "status": "done",
        "document": {
            "doc_id": doc_id, "filename": filename,
            "page_count": page_count, "source": source,
            "md_chars": split.total_chars, "chapter_count": len(split.chapters),
            "headings": headings[:200],
            "warnings": warnings, "stats": stats, "manifest": manifest,
        },
    }


async def _finalize_docling_sync(doc_id: str, filename: str, ext: str,
                                 upload_path, work, title: str = "") -> dict:
    """Docling 同步转换（office 小件）。"""
    meta = convert_sync(upload_path, work)
    markdown = (meta.get("markdown") or "").strip()
    if not markdown:
        raise HTTPException(422, detail=meta.get("error") or "Docling 未产出内容")
    try:
        mod = await moderate_markdown_async(markdown)
    except ModerationUnavailable as exc:
        # CMP-02 fail-closed：审核挂掉拒收并清理残壳，未审内容绝不入库
        shutil.rmtree(config.UPLOAD_DIR / doc_id, ignore_errors=True)
        raise HTTPException(503, detail=str(exc) or "审核服务暂不可用，请稍后重试") from exc
    if mod["verdict"] == "reject":
        _raise_rejected(doc_id, mod)
    split = split_markdown(markdown)
    storage.save_markdown(doc_id, markdown)
    storage.save_chapters(doc_id, split.chapters)
    cleanup_original(doc_id)
    return _doc_response(
        doc_id, filename, ext, split, None,
        source="docling", page_count=meta.get("page_count", 0),
        stats={"docling": {k: meta.get(k) for k in ("page_count", "chars", "seconds", "ok")},
               "moderation": mod_stats(mod)},
        warnings=[f"Docling 同步转换 {meta.get('seconds', '?')}s"],
        title=title,
    )


async def _legacy_pdf_upload(doc_id: str, filename: str, upload_path, title: str = "") -> dict:
    """Docling 环境缺失时的 PDF 回落：文本层同步 / 扫描件异步（旧行为）。"""
    result = parse_pdf(str(upload_path))
    markdown = result.markdown or ""
    with SessionLocal() as db:
        if markdown:
            try:
                mod = await moderate_markdown_async(markdown)
            except ModerationUnavailable as exc:
                # CMP-02 fail-closed：审核挂掉拒收并清理残壳，未审内容绝不入库
                shutil.rmtree(config.UPLOAD_DIR / doc_id, ignore_errors=True)
                raise HTTPException(503, detail=str(exc) or "审核服务暂不可用，请稍后重试") from exc
            if mod["verdict"] == "reject":
                _raise_rejected(doc_id, mod)
            split = split_markdown(markdown)
            storage.save_markdown(doc_id, markdown)
            storage.save_chapters(doc_id, split.chapters)
            cleanup_original(doc_id)
            manifest = [
                {"index": c.index, "title": c.title, "level": c.level,
                 "char_count": c.char_count,
                 "toc": [{"level": t.level, "title": t.title} for t in c.toc]}
                for c in split.chapters
            ]
            _save_document_record(
                db, doc_id, filename=filename, format="pdf", status="done",
                title=title,
                page_count=result.page_count, source="text-layer",
                md_chars=split.total_chars, chapter_count=len(split.chapters),
                headings=[{"level": h.level, "text": h.text} for h in result.headings][:200],
                warnings=result.warnings,
                stats={**result.stats, "moderation": mod_stats(mod)},
                manifest=manifest,
            )
            return {"ok": True, "doc_id": doc_id, "status": "done",
                    "document": {"doc_id": doc_id, "filename": filename,
                                 "page_count": result.page_count, "source": "text-layer",
                                 "md_chars": split.total_chars,
                                 "chapter_count": len(split.chapters),
                                 "warnings": result.warnings, "stats": result.stats,
                                 "manifest": manifest}}

        _save_document_record(
            db, doc_id, filename=filename, format="pdf", status="processing",
            title=title,
            page_count=result.page_count, source="",
            md_chars=0, chapter_count=0, headings=[],
            warnings=[*result.warnings, "扫描件，已进入后台 OCR 队列…"],
            stats=result.stats, manifest=[],)
        task_id = tasks.enqueue(doc_id, kind="ocr")
        return {"ok": True, "doc_id": doc_id, "status": "processing",
                "task_id": task_id, "message": "扫描件已进入后台 OCR 队列，可轮询 /api/tasks/" + task_id}


@router.post("/upload")
@limiter.limit(L_UPLOAD)
async def upload(request: Request, response: Response, file: UploadFile = File(...),
                 display_name: str = Form(""),
                 user: CurrentUser = Depends(get_requester)):
    """上传教材（5/hour/requester）。匿名走 X-Device-Id 设备身份；同文件命中共享书库直接复用。"""
    # 把 user_id 写入 ContextVar（_save_document_record 自动取）
    _current_user_id.set(user.openid if user else None)
    _current_content_hash.set(None)
    if not file.filename:
        raise HTTPException(400, detail="请选择要上传的文件")
    filename = _clean_filename(file.filename)
    # 用户自定义命名优先；否则用修复后的文件名（历史乱码同样在这里兜底修复）
    title = (display_name or "").strip()[:200]
    if not title:
        try:
            title = filename.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            title = filename
        title = title.rsplit(".", 1)[0] if "." in title else title  # 去扩展名当书名
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    if ext not in config.SUPPORTED_FORMATS:
        raise HTTPException(
            415,
            detail=f"暂不支持 {ext} 格式。当前支持：{', '.join(sorted(config.SUPPORTED_FORMATS))}",
        )

    # ---- 共享书库去重：流式 sha256（1MB 分块，不整读入内存），同 hash 的 done 文档直接复用 ----
    digest = hashlib.sha256()
    while True:
        chunk = file.file.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    file.file.seek(0)  # 复位，后续 save_upload / 解析仍从头读
    content_hash = digest.hexdigest()
    _current_content_hash.set(content_hash)
    with SessionLocal() as db:
        existing = (db.query(Document)
                    .filter(Document.content_hash == content_hash,
                            Document.status == "done")
                    .order_by(Document.created_at.desc())
                    .first())
    if existing is not None:
        return {
            "ok": True,
            "doc_id": existing.doc_id,
            "status": "done",
            "reused": True,
            "message": "书库已有此书，直接使用",
            "document": {
                "doc_id": existing.doc_id,
                "filename": existing.filename,
                "title": existing.title or existing.filename or "未命名教材",
                "chapter_count": existing.chapter_count,
                "manifest": existing.manifest or [],
            },
        }

    doc_id = storage.new_doc_id()
    upload_path = storage.save_upload(doc_id, file)

    max_bytes = config.MAX_UPLOAD_MB * 1024 * 1024
    if upload_path.stat().st_size > max_bytes:
        try:
            upload_path.unlink()
        except OSError:
            pass
        raise HTTPException(413, detail=f"文件超过 {config.MAX_UPLOAD_MB}MB 上限")

    kind = preflight(upload_path, ext)

    # md/txt：直读
    if kind["kind"] == "md":
        markdown = upload_path.read_text(encoding="utf-8")
        try:
            mod = await moderate_markdown_async(markdown)
        except ModerationUnavailable as exc:
            # CMP-02 fail-closed：审核挂掉拒收并清理残壳，未审内容绝不入库
            shutil.rmtree(config.UPLOAD_DIR / doc_id, ignore_errors=True)
            raise HTTPException(503, detail=str(exc) or "审核服务暂不可用，请稍后重试") from exc
        if mod["verdict"] == "reject":
            _raise_rejected(doc_id, mod)
        warnings = ["Markdown 直读"]
        if mod.get("skipped") == "error":
            warnings.append(mod.get("reason") or "审核服务异常")
        split = split_markdown(markdown)
        storage.save_markdown(doc_id, markdown)
        storage.save_chapters(doc_id, split.chapters)
        cleanup_original(doc_id)
        return _doc_response(
            doc_id, filename, ext, split, None,
            source="text-layer", page_count=0,
            stats={"source": "md", "moderation": mod_stats(mod)},
            warnings=warnings,
            title=title,
        )

    # Docling 缺失 → 回落
    if not docling_available():
        if ext == ".pdf":
            return await _legacy_pdf_upload(doc_id, filename, upload_path, title=title)
        raise HTTPException(
            415,
            detail="Docling 环境未就绪（缺 .docling-venv），暂只有 PDF 支持回落。"
                   "先安装：uv venv --python 3.13 .docling-venv。",
        )

    # 办公格式小件：同步
    if kind["sync"] and kind["kind"] in ("office",):
        work = config.WORK_DIR / f"docling_{doc_id}"
        work.mkdir(parents=True, exist_ok=True)
        return await _finalize_docling_sync(doc_id, filename, ext, upload_path, work, title=title)

    # PDF / 图片 / 大件办公：异步 Docling 任务
    with SessionLocal() as db:
        _save_document_record(
            db, doc_id,
            filename=filename, format=ext.lstrip("."), status="processing",
            title=title,
            page_count=0, source="",
            md_chars=0, chapter_count=0,
            headings=[], warnings=[f"{ext} 已进入 Docling 异步解析队列（版面/表格/OCR）…"],
            stats={}, manifest=[],
        )
    task_id = tasks.enqueue(doc_id, kind="docling")
    return {
        "ok": True,
        "doc_id": doc_id,
        "status": "processing",
        "task_id": task_id,
        "message": "已进入 Docling 后台队列，可轮询 /api/tasks/" + task_id,
    }