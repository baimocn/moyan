"""墨衍 · Docling 转换 worker（在 .docling-venv / Python 3.13 内运行）

用法：<venv-python> tools/docling_worker.py <输入文件> <输出md> <输出meta.json>

- 由 backend/services/docling_adapter.py 通过 subprocess 调用（本机沙箱禁命名管道 → 文件通信）；
- 输入支持 docling 全部类型：pdf/docx/pptx/xlsx/html/epub/images/…
- 输出：export_to_markdown() 写入 <输出md>；<输出meta.json> 含 page_count/source/耗时。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import warnings
warnings.filterwarnings("ignore")


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: docling_worker.py <input> <out.md> <out.json>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    out_md = Path(sys.argv[2])
    out_json = Path(sys.argv[3])
    out_md.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    meta = {"ok": False, "source": str(src), "page_count": 0, "chars": 0, "seconds": 0.0}
    try:
        from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
        from docling.document_converter import (DocumentConverter, InputFormat,
                                                PdfFormatOption)
        # PDF 强制 pypdfium2 后端：docling_parse 的 C 解析器对中文路径资源解析不稳
        # （RuntimeError: additional.dat not exists），且本机验证 pypdfium2 无需额外资源。
        if src.suffix.lower() == ".pdf":
            conv = DocumentConverter(format_options={
                InputFormat.PDF: PdfFormatOption(backend=PyPdfiumDocumentBackend),
            })
        else:
            conv = DocumentConverter()
        res = conv.convert(src)
        md = res.document.export_to_markdown()
        out_md.write_text(md or "", encoding="utf-8")
        meta["markdown"] = str(out_md)
        try:
            meta["page_count"] = len(res.document.pages)
        except Exception:
            meta["page_count"] = 0
        meta["chars"] = len(md)
        meta["seconds"] = round(time.time() - t0, 1)
        meta["ok"] = True
    except Exception as exc:  # noqa: BLE001 单文档失败不崩进程
        meta["error"] = f"{type(exc).__name__}: {str(exc)[:400]}"
        meta["seconds"] = round(time.time() - t0, 1)
    out_json.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return 0 if meta["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())