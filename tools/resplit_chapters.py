# -*- coding: utf-8 -*-
"""一次性修复脚本：用修复后的 chapter_splitter 重切已有文档。

背景：旧版切割把 docling 的整行页码注释 `<!-- 第 1 页 -->` 当前言内容，
产出碎章（标题=注释原文）。修复 splitter 后，已有落库文档需要重切。

用法（项目根目录）：
    python tools/resplit_chapters.py          # 全部重切
    python tools/resplit_chapters.py --dry    # 只预览不落盘
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.services.chapter_splitter import split_markdown  # noqa: E402
from backend import storage  # noqa: E402
from backend.models.db import SessionLocal, init_db  # noqa: E402
from backend.models.documents import Document  # noqa: E402


def main() -> int:
    dry = "--dry" in sys.argv
    init_db()
    session = SessionLocal()
    docs = session.query(Document).filter(Document.status == "done").all()
    changed = 0
    for doc in docs:
        md_path = ROOT / "data" / "markdown" / f"{doc.doc_id}.md"
        if not md_path.exists():
            print(f"[skip] {doc.doc_id}: markdown 文件不存在")
            continue
        markdown = md_path.read_text(encoding="utf-8")
        old_titles = [c.get("title", "?") for c in (doc.manifest or [])]
        split = split_markdown(markdown)
        new_titles = [c.title for c in split.chapters]
        if old_titles == new_titles:
            print(f"[ok]   {doc.doc_id}: 章节无变化（{len(new_titles)} 章）")
            continue
        changed += 1
        print(f"[fix]  {doc.doc_id}:")
        print(f"       旧: {json.dumps(old_titles, ensure_ascii=False)}")
        print(f"       新: {json.dumps(new_titles, ensure_ascii=False)}")
        if dry:
            continue
        storage.save_chapters(doc.doc_id, split.chapters)
        doc.chapter_count = len(split.chapters)
        doc.md_chars = split.total_chars
        doc.manifest = [
            {
                "index": c.index, "title": c.title, "level": c.level,
                "char_count": c.char_count,
                "toc": [{"level": t.level, "title": t.title} for t in c.toc],
            }
            for c in split.chapters
        ]
    if not dry:
        session.commit()
    session.close()
    print(f"\n{'（dry-run 预览）' if dry else '已落盘'}共 {changed} 份文档章节有变化")
    return 0


if __name__ == "__main__":
    sys.exit(main())
