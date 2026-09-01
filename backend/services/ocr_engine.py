"""墨衍 · 扫描件 OCR 引擎

主后端：RapidOCR（PP-OCR 模型 + ONNX Runtime，CPU）——中文印刷体质量远优于
Windows 自带 OCR，本地免费。多进程并行控制速度（466 页约 5 分钟）。

备用后端：Windows OCR（tools/winocr.ps1，winocr 函数），RapidOCR 不可用时降级。

流程：渲染页为 PNG（PyMuPDF） → 批量 OCR → 行流（text/size/y0/rel_y/page）
      → 统一 lines_pipeline（模式识别标题）→ Markdown + 标题结构。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .. import config
from .lines_pipeline import build_markdown
from .pdf_parser import PdfParseResult

OCR_SCRIPT = config.PROJECT_ROOT / "tools" / "winocr.ps1"


def render_pages(pdf_path: str, png_dir: Path, dpi: int = 200, force: bool = False) -> int:
    """逐页渲染 PNG（已存在的页跳过，支持断点续跑）。"""
    try:
        import pymupdf as fitz
    except ImportError:  # pragma: no cover
        import fitz
    png_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    n = doc.page_count
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    done = 0
    for i, page in enumerate(doc):
        out = png_dir / f"p{i + 1:04d}.png"
        if not force and out.exists():
            done += 1
            continue
        page.get_pixmap(matrix=mat).save(str(out))
        done += 1
    doc.close()
    return n


def run_rapid_ocr(
    png_dir: Path,
    out_json: Path,
    workers: int | None = None,
    progress_cb=None,
) -> None:
    """RapidOCR 多进程批量识别 → 行流 JSON。

    沙箱环境下 multiprocessing 的命名管道被禁，改用"独立子进程 + 文件通信"：
    每个 worker 进程负责一段页号区间，各自写 JSONL，主进程再合并。
    progress_cb(done_pages, total_pages) 每个块完成时回调（任务进度用）。
    """
    from PIL import Image  # noqa: 确保 PIL 可用（RapidOCR 依赖）

    pngs = sorted(png_dir.glob("p*.png"))
    if not pngs:
        raise RuntimeError(f"png 目录为空：{png_dir}")
    workers = workers or getattr(config, "OCR_WORKERS", 4)
    pages = [int(p.stem.lstrip("p")) for p in pngs]

    chunks = [pages[i::workers] for i in range(workers)]
    chunks = [c for c in chunks if c]  # 去掉空块

    worker_script = config.PROJECT_ROOT / "tools" / "rapid_ocr_worker.py"
    procs = []
    for i, chunk in enumerate(chunks):
        chunk_file = out_json.with_name(f"chunk_{i}.jsonl")
        cmd = [
            sys.executable, str(worker_script),
            str(png_dir), str(chunk_file), ",".join(map(str, chunk)),
        ]
        procs.append((
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
            chunk_file, len(chunk),
        ))

    merged: list[dict] = []
    done_pages = 0
    total_pages = len(pages)
    for proc, chunk_file, chunk_n in procs:
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"RapidOCR worker 退出码 {proc.returncode}")
        if chunk_file.exists():
            for line in chunk_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    merged.append(json.loads(line))
            chunk_file.unlink()
        done_pages += chunk_n
        if progress_cb:
            progress_cb(done_pages, total_pages)
    merged.sort(key=lambda r: (r["page"], r["y0"]))
    out_json.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    print(f"[rapid-ocr] {len(pngs)} 页 -> {len(merged)} 行 -> {out_json.name}")


def run_windows_ocr(png_dir: Path, out_json: Path) -> None:
    """备用：Windows OCR 批量识别（tools/winocr.ps1）。"""
    cmd = [
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(OCR_SCRIPT),
        "-PngDir", str(png_dir),
        "-OutJson", str(out_json),
    ]
    proc = subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Windows OCR 失败（exit={proc.returncode}）")


def load_ocr_lines(json_path: Path) -> tuple[list[dict], int]:
    """OCR 行流 JSON → 统一行流（text/size/y0/rel_y/page），按视觉顺序排序。"""
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    rows: list[dict] = []
    for r in data:
        text = (r.get("text") or "").strip()
        if not text:
            continue
        try:
            page = int(r["page"])
        except (KeyError, ValueError, TypeError):
            continue
        rows.append({
            "text": text,
            "size": float(r.get("height") or 0) or 24.0,
            "y0": float(r.get("y0") or 0),
            "rel_y": float(r.get("rel_y") or 0),
            "page": page,
        })
    rows.sort(key=lambda ln: (ln["page"], ln["y0"]))
    last_page = max((r["page"] for r in rows), default=0)
    return rows, last_page


def ocr_pdf_to_markdown(
    pdf_path: str,
    work_dir: Path | None = None,
    dpi: int = 200,
    reuse: bool = True,
) -> PdfParseResult:
    """扫描件 PDF → Markdown + 标题结构（渲染 + OCR + 管线）。"""
    work_dir = work_dir or (config.WORK_DIR / "ocr")
    png_dir = work_dir / "pngs"
    out_json = work_dir / "ocr_lines.json"
    png_dir.mkdir(parents=True, exist_ok=True)

    if reuse and out_json.exists() and any(png_dir.glob("p*.png")):
        pass  # 复用已有产物
    else:
        render_pages(pdf_path, png_dir, dpi=dpi, force=not reuse)
        engine = getattr(config, "OCR_ENGINE", "rapid")
        if engine == "win":
            run_windows_ocr(png_dir, out_json)
        else:
            run_rapid_ocr(png_dir, out_json)
    rows, last_page = load_ocr_lines(out_json)

    result = PdfParseResult(source="ocr", page_count=last_page)
    if not rows:
        result.warnings.append("OCR 未识别出任何行（页面可能为纯图片/空白）。")
        return result

    md, headings, warnings = build_markdown(
        rows, source="ocr", page_count=last_page or None,
    )
    result.markdown = md
    result.headings = headings
    result.warnings = warnings
    result.stats = {
        "line_count": len(rows),
        "heading_count": len(headings),
        "source": "rapid-ocr",
    }
    return result