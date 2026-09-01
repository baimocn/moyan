"""墨衍 · 历史 CLI 产物导入 DB（一次性迁移，幂等可重跑）

背景：2026-08-27 之前用旧版 CLI（tools/ocr_convert.py → backend.processing）跑过
《普通生物学》OCR，产物只登记在旧 data/documents.json（且文件名乱码），DB 里没有。
本脚本把已在磁盘的 md + 章节切片登记进 DB documents 表，让应用端能直接使用。

用法：python tools/import_legacy_docs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config, storage
from backend.models import Document, SessionLocal

# doc_id -> (文件名展示名, 来源)
LEGACY = [
    ("qlsb-verified", "普通生物学（第3版）-已校对", "ocr"),
    ("qlsb-rapid", "普通生物学（第3版）-rapid", "ocr"),
]


def _char_count(text: str) -> int:
    import re
    return len(re.sub(r"\s+", "", text or ""))


def main() -> int:
    ok = 0
    for doc_id, label, source in LEGACY:
        md_path = config.MARKDOWN_DIR / f"{doc_id}.md"
        manifest_path = config.CHAPTERS_DIR / doc_id / "chapters.json"
        if not md_path.exists() or not manifest_path.exists():
            print(f"跳过 {doc_id}：缺 md 或章节清单")
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"跳过 {doc_id}：清单解析失败 {exc}")
            continue
        md = md_path.read_text(encoding="utf-8")
        chapter_count = len(manifest)
        page_count = max((int(c.get("index", 0)) for c in manifest), default=0) or 466
        headings = [{"level": c.get("level", 1), "text": c.get("title", "")}
                    for c in manifest]
        with SessionLocal() as db:
            row = db.get(Document, doc_id)
            fields = dict(
                filename=label + ".pdf", format="pdf", page_count=page_count,
                source=source, md_chars=_char_count(md), chapter_count=chapter_count,
                headings=headings, warnings=["历史 CLI 产物导入"], stats={},
                manifest=manifest, status="done",
            )
            if row is None:
                db.add(Document(doc_id=doc_id, **fields))
                print(f"导入 {doc_id}（{label}）：{chapter_count} 章 / {_char_count(md):,} 字")
            else:
                for k, v in fields.items():
                    setattr(row, k, v)
                print(f"更新 {doc_id}：{chapter_count} 章 / {_char_count(md):,} 字")
            db.commit()
        ok += 1
    print(f"\n完成：{ok} 个历史文档已导入 DB，可用 /api/documents 查看。")
    return 0


if __name__ == "__main__":
    sys.exit(main())