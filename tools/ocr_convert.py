"""墨衍 · 本地大文件/扫描件转换 CLI（对齐当前架构：routers/tasks/services 分层）

把本地 PDF（含扫描件）完整跑一遍"解析 → Markdown → 分章节 → 落盘 → 注册到 DB"，
打印章节摘要供验收切割准确度。

用法：
    python tools/ocr_convert.py "D:\\Desktop\\电子书\\普通生物学.pdf" [doc_id]
    python tools/ocr_convert.py "..." doc_id --work data/work/qlsb   # 复用已有渲染/OCR 产物
    # 复用已渲染 png / 已 OCR 行流时（断点续跑），二次运行同 doc_id 即复用。
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 项目根

from backend import config, storage
from backend.engine.proofread import cleanup_original
from backend.models import Document, SessionLocal
from backend.services.chapter_splitter import split_markdown
from backend.services.ocr_engine import ocr_pdf_to_markdown
from backend.services.pdf_parser import parse_pdf


def _register_document(doc_id: str, filename: str, *, source: str, page_count: int,
                       split, headings: list) -> None:
    """注册/更新 Document 记录（幂等：二次运行覆盖旧记录）。"""
    with SessionLocal() as db:
        row = db.get(Document, doc_id)
        fields = dict(
            filename=filename, format="pdf", page_count=page_count, source=source,
            md_chars=split.total_chars, chapter_count=len(split.chapters),
            headings=headings[:200], warnings=[], stats={},
            manifest=[
                {"index": c.index, "title": c.title, "level": c.level,
                 "char_count": c.char_count,
                 "toc": [{"level": t.level, "title": t.title} for t in c.toc]}
                for c in split.chapters
            ],
            status="done",
        )
        if row is None:
            db.add(Document(doc_id=doc_id, **fields))
        else:
            for k, v in fields.items():
                setattr(row, k, v)
        db.commit()


def main() -> int:
    ap = argparse.ArgumentParser(description="墨衍 · 本地 PDF（含扫描件）转 Markdown + 分章节")
    ap.add_argument("pdf", help="PDF 路径")
    ap.add_argument("doc_id", nargs="?", default=None, help="文档 ID（缺省自动生成）")
    ap.add_argument("--work", default=None, help="复用已有 OCR 产物目录（pngs/ + ocr_lines.json）")
    ap.add_argument("--no-proofread", action="store_true", help="跳过 AI 校对（无 key 时自动跳过）")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"文件不存在：{pdf}")
        return 1
    doc_id = args.doc_id or storage.new_doc_id()

    config.ensure_dirs()
    upload_dir = config.UPLOAD_DIR / doc_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / pdf.name
    if not upload_path.exists():
        shutil.copy2(pdf, upload_path)

    t0 = time.time()
    print(f"处理 {pdf.name}（{pdf.stat().st_size / 1024 / 1024:.1f}MB, {doc_id}）…")

    # 1) 先试文本层
    result = parse_pdf(str(upload_path))
    markdown = result.markdown or ""
    if markdown:
        source, page_count = "text-layer", result.page_count
        headings = result.headings
        print(f"  文本层 ✓（{len(markdown):,} 字符）")
    else:
        # 2) 扫描件 → OCR
        work = Path(args.work) if args.work else (config.WORK_DIR / f"ocr_{doc_id}")
        ocr = ocr_pdf_to_markdown(str(upload_path), work_dir=work, dpi=config.OCR_DPI)
        markdown = ocr.markdown or ""
        source, page_count = ocr.source, ocr.page_count
        headings = ocr.headings
        if not markdown:
            print("解析失败：既无文本层，OCR 也未产出内容。")
            return 1
        # 3) D8 教材校对（有 key 且未跳过时，定点纠错）
        if not args.no_proofread:
            from backend.container import services
            corrected, n = services.proofread.proofread_markdown(markdown, work)
            if n:
                print(f"  校对修正 {n} 处")
                markdown = corrected

    # 4) 切章 + 落盘
    split = split_markdown(markdown)
    storage.save_markdown(doc_id, markdown)
    storage.save_chapters(doc_id, split.chapters)
    cleanup_original(doc_id)
    _register_document(doc_id, pdf.name, source=source, page_count=page_count,
                       split=split, headings=headings)

    print(f"\n[{source}] 用时 {time.time() - t0:.1f}s | {page_count} 页 | "
          f"Markdown {split.total_chars:,} 字 | {len(split.chapters)} 章")
    print("\n===== 章节目录 =====")
    for ch in split.chapters:
        sub = "｜".join(t["title"][:18] for t in ch.toc[:4])
        mark = f" +{len(ch.toc) - 4}" if len(ch.toc) > 4 else ""
        print(f"  {ch.index + 1:>3}. {ch.title[:40]}（{ch.char_count}字）")
        if sub:
            print(f"        ├ {sub}{mark}")
    print(f"\n落盘：{config.MARKDOWN_DIR / (doc_id + '.md')} / {config.CHAPTERS_DIR / doc_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())