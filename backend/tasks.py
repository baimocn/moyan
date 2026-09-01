"""墨衍 · 后台任务队列（服务器模式）

扫描件 OCR（大文件 10-30 分钟）不能阻塞请求，用进程内单 worker 串行队列：
    POST /api/upload → 创建 Task(queued) → 入队 → 立即返回 task_id
    前端轮询 GET /api/tasks/{id} 看进度（0~100%）
    worker 完成 → 切章落盘 → Document 置 done

2G/2核 服务器上不引 Celery/Redis：单 worker 线程 + PG 状态表足够。
"""
from __future__ import annotations

import queue
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from . import config, storage
from .models import Document, SessionLocal, Task
from .engine.proofread import cleanup_original
from .container import services
from .services.chapter_splitter import split_markdown
from .services.ocr_engine import ocr_pdf_to_markdown
from .services.pdf_parser import parse_pdf

_task_queue: "queue.Queue[str]" = queue.Queue()
_worker_thread: threading.Thread | None = None


def start_worker() -> None:
    """应用启动时调用：拉起单 worker 线程（幂等）。"""
    global _worker_thread
    if _worker_thread is not None and _worker_thread.is_alive():
        return
    _worker_thread = threading.Thread(target=_worker_loop, name="moyan-ocr-worker", daemon=True)
    _worker_thread.start()


def enqueue(doc_id: str, kind: str = "ocr") -> str:
    """创建任务并入队，返回 task_id。kind: docling（主解析）| ocr（legacy 扫描兜底）。"""
    import uuid
    task_id = "t_" + uuid.uuid4().hex[:10]
    with SessionLocal() as db:
        db.add(Task(id=task_id, doc_id=doc_id, kind=kind, status="queued"))
        db.commit()
    _task_queue.put(task_id)
    return task_id


def _update_task(task_id: str, **fields) -> None:
    with SessionLocal() as db:
        task = db.get(Task, task_id)
        if task is None:
            return
        for k, v in fields.items():
            setattr(task, k, v)
        task.updated_at = datetime.now(timezone.utc)
        db.commit()


def _update_document(doc_id: str, **fields) -> None:
    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        if doc is None:
            return
        for k, v in fields.items():
            setattr(doc, k, v)
        doc.updated_at = datetime.now(timezone.utc)
        db.commit()


def _run_ocr_task(task_id: str) -> None:
    """执行一个 OCR 任务：渲染→OCR(带进度)→切章→落盘→完成。"""
    with SessionLocal() as db:
        task = db.get(Task, task_id)
        doc = db.get(Document, task.doc_id) if task else None
        if not task or not doc:
            return
        doc_id = doc.doc_id
        filename = doc.filename
        upload_dir = config.UPLOAD_DIR / doc_id
        upload_path = next(upload_dir.iterdir(), None) if upload_dir.exists() else None
        if upload_path is None:
            _update_task(task_id, status="failed", message="上传文件缺失")
            _update_document(doc_id, status="failed")
            return

    _update_task(task_id, status="running", message="渲染页面…")
    work = config.WORK_DIR / f"ocr_{doc_id}"

    def on_progress(done: int, total: int) -> None:
        _update_task(
            task_id,
            done_pages=done,
            total_pages=total,
            progress=round(done / max(1, total), 3),
            message=f"OCR 识别中 {done}/{total} 页",
        )

    try:
        # reuse=True：同一 doc_id 已有产物直接复用（断点续跑语义）
        ocr_result = ocr_pdf_to_markdown(
            str(upload_path),
            work_dir=work,
            dpi=config.OCR_DPI,
            reuse=True,
        )
        _update_task(task_id, progress=1.0, message="切割章节…")

        markdown = ocr_result.markdown or ""
        # D8：教材校对（定点纠错，教材可信度最高）+ 原件清理
        corrected, n_corrected = services.proofread.proofread_markdown(markdown, work)
        if n_corrected:
            print(f"[task {task_id}] 校对修正 {n_corrected} 处")
            markdown = corrected
        _update_task(task_id, progress=1.0, message="切割章节…")

        split = split_markdown(markdown)
        storage.save_markdown(doc_id, markdown)
        storage.save_chapters(doc_id, split.chapters)
        cleanup_original(doc_id)
        # 存储最小化：OCR 已出结果 + 已切章，PNG 页图不再需要（保留 ocr_lines.json 供校对/复用）
        _cleanup_ocr_pngs(work)

        manifest = [
            {
                "index": c.index, "title": c.title, "level": c.level,
                "char_count": c.char_count,
                "toc": [{"level": t.level, "title": t.title} for t in c.toc],
            }
            for c in split.chapters
        ]
        _update_document(
            doc_id,
            page_count=ocr_result.page_count,
            source=ocr_result.source,
            md_chars=split.total_chars,
            chapter_count=len(split.chapters),
            headings=[{"level": h.level, "text": h.text} for h in ocr_result.headings][:200],
            warnings=ocr_result.warnings,
            stats=ocr_result.stats,
            manifest=manifest,
            status="done",
        )
        _update_task(
            task_id, status="done", progress=1.0,
            message=f"完成：{len(split.chapters)} 章",
            finished_at=datetime.now(timezone.utc),
        )
    except Exception as exc:  # noqa: BLE001 任务级兜底
        tb = traceback.format_exc()
        print(f"[task {task_id}] 失败：{exc}\n{tb}")
        _update_task(task_id, status="failed", message=f"{exc}", finished_at=datetime.now(timezone.utc))
        _update_document(doc_id, status="failed")
        raise


def _cleanup_ocr_pngs(work: Path) -> None:
    """删除 OCR 中间 PNG（一部教材常数百 MB），保留 ocr_lines.json。"""
    png_dir = work / "pngs"
    if png_dir.exists():
        n = 0
        for f in png_dir.glob("p*.png"):
            try:
                f.unlink()
                n += 1
            except OSError:
                pass
        if n:
            print(f"[task] 已清理 OCR 页面图 {n} 张（{work.name}）")
        try:
            png_dir.rmdir()   # 目录空则一并移除
        except OSError:
            pass


def _run_docling_task(task_id: str) -> None:
    """执行一个 Docling 转换任务（主解析引擎）：转换→校对→切章→落盘→完成。"""
    from .services.docling_adapter import convert_sync
    with SessionLocal() as db:
        task = db.get(Task, task_id)
        doc = db.get(Document, task.doc_id) if task else None
        if not task or not doc:
            return
        doc_id = doc.doc_id
        upload_dir = config.UPLOAD_DIR / doc_id
        upload_path = next(upload_dir.iterdir(), None) if upload_dir.exists() else None
        if upload_path is None:
            _update_task(task_id, status="failed", message="上传文件缺失")
            _update_document(doc_id, status="failed")
            return

    _update_task(task_id, status="running", message="Docling 解析中（慢页备注：含版面/表格/OCR）")
    work = config.WORK_DIR / f"docling_{doc_id}"
    try:
        meta = convert_sync(upload_path, work)
        markdown = (meta.get("markdown") or "").strip()
        if not markdown:
            err = meta.get("error") or "Docling 未产出内容"
            _update_task(task_id, status="failed", message=err,
                         finished_at=datetime.now(timezone.utc))
            _update_document(doc_id, status="failed")
            return

        corrected, n_corrected = services.proofread.proofread_markdown(markdown, work)
        if n_corrected:
            print(f"[task {task_id}] 校对修正 {n_corrected} 处")
            markdown = corrected
        _update_task(task_id, progress=1.0, message="切割章节…")

        split = split_markdown(markdown)
        storage.save_markdown(doc_id, markdown)
        storage.save_chapters(doc_id, split.chapters)
        cleanup_original(doc_id)

        manifest = [
            {
                "index": c.index, "title": c.title, "level": c.level,
                "char_count": c.char_count,
                "toc": [{"level": t.level, "title": t.title} for t in c.toc],
            }
            for c in split.chapters
        ]
        _update_document(
            doc_id,
            page_count=meta.get("page_count", 0),
            source="docling",
            md_chars=split.total_chars,
            chapter_count=len(split.chapters),
            headings=[{"level": c.level, "text": c.title} for c in split.chapters][:200],
            warnings=[f"Docling 转换 {meta.get('seconds', '?')}s（docling_worker）"],
            stats={"docling": {k: meta.get(k) for k in ("page_count", "chars", "seconds", "ok")}},
            manifest=manifest,
            status="done",
        )
        _update_task(
            task_id, status="done", progress=1.0,
            message=f"完成：{len(split.chapters)} 章",
            finished_at=datetime.now(timezone.utc),
        )
    except Exception as exc:  # noqa: BLE001 任务级兜底
        tb = traceback.format_exc()
        print(f"[task {task_id}] Docling 失败：{exc}\n{tb}")
        _update_task(task_id, status="failed", message=f"{exc}",
                     finished_at=datetime.now(timezone.utc))
        _update_document(doc_id, status="failed")
        raise


def _worker_loop() -> None:
    """单 worker：串行消费任务队列。"""
    while True:
        task_id = _task_queue.get()
        try:
            with SessionLocal() as db:
                kind = db.get(Task, task_id).kind if db.get(Task, task_id) else "ocr"
            if kind == "docling":
                _run_docling_task(task_id)
            else:
                _run_ocr_task(task_id)
        except Exception:  # noqa: BLE001 记录但不死循环
            pass
        finally:
            _task_queue.task_done()