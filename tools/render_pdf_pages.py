"""墨衍 · PDF 逐页渲染为 PNG（供 Windows OCR 使用）

用法：
    python tools/render_pdf_pages.py <pdf路径> <输出目录> [dpi]
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf as fitz


def render_pages(pdf_path: str, out_dir: str, dpi: int = 200) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    n = doc.page_count
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat)
        pix.save(str(out / f"p{i + 1:04d}.png"))
        if (i + 1) % 50 == 0 or i + 1 == n:
            print(f"渲染 {i + 1}/{n}")
    doc.close()
    return n


if __name__ == "__main__":
    pdf, outp = sys.argv[1], sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    render_pages(pdf, outp, dpi)
    print(f"完成：{outp}")