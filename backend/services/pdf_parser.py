"""墨衍 · PDF → Markdown 解析服务（文本层）

设计要点（对齐规划"解析地基"）：
1. 文本型 PDF 直接用 PyMuPDF 提取；行先按 (页码, y) 视觉顺序重排；
2. 识别/过滤/组装统一下沉到 lines_pipeline（与 OCR 场景共用）；
3. 扫描件（几乎没有内嵌文本）检测出来打警告并返回空产物——
   扫描件走 ocr_engine（Windows OCR / 后续 PaddleOCR）。

已知局限（第 1 阶段可接受）：多栏阅读顺序、表格、公式、图片不处理。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

try:  # PyMuPDF 新版推荐 import pymupdf，旧版兼容 import fitz
    import pymupdf as fitz
except ImportError:  # pragma: no cover
    import fitz

from .lines_pipeline import Heading, build_markdown

SCANNED_MIN_CHARS_PER_PAGE = 50   # 平均每页字符数低于该值 → 疑似扫描件


@dataclass
class PdfParseResult:
    """一次 PDF 解析的完整产物（文本层 / OCR 共用）。"""
    markdown: Optional[str] = None
    page_count: int = 0
    headings: list = field(default_factory=list)      # list[Heading]
    warnings: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    source: str = "pdf"                                # pdf | ocr


def extract_text_lines(doc) -> list[dict]:
    """提取文本层行流并按视觉顺序排序。"""
    lines: list[dict] = []
    for page in doc:
        height = page.rect.height or 1.0
        tp = page.get_text("dict")
        for block in tp.get("blocks", []):
            if block.get("type") != 0:  # 0=文本，1=图片
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s.get("text", "") for s in spans).strip()
                if not text:
                    continue
                size = max(s.get("size", 0) or 0 for s in spans)
                bbox = line.get("bbox", [0, 0, 0, 0])
                lines.append({
                    "text": text,
                    "size": size,
                    "y0": bbox[1],
                    "rel_y": bbox[1] / height,
                    "page": page.number + 1,
                })
    lines.sort(key=lambda ln: (ln["page"], round(ln["y0"], 1)))
    return lines


def is_scanned(doc, lines: list[dict]) -> bool:
    if not lines:
        return True
    total_chars = sum(len(ln["text"]) for ln in lines)
    avg = total_chars / max(1, doc.page_count)
    return avg < SCANNED_MIN_CHARS_PER_PAGE


def parse_pdf(path: str) -> PdfParseResult:
    """解析文本型 PDF → Markdown + 标题结构。"""
    result = PdfParseResult()
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise ValueError(f"无法打开 PDF 文件：{exc}") from exc

    page_count = doc.page_count
    result.page_count = page_count
    lines = extract_text_lines(doc)

    if is_scanned(doc, lines):
        result.warnings.append(
            "未检测到内嵌文本：疑似扫描件/图片型PDF。当前不支持直接解析，"
            "已自动切换本地 OCR（Windows 引擎）…"
        )
        result.stats = {"line_count": 0}
        doc.close()
        return result

    md, headings, warnings = build_markdown(lines, source="pdf", page_count=page_count)
    result.markdown = md
    result.headings = headings
    result.warnings = warnings
    result.stats = {
        "line_count": len(lines),
        "heading_count": len(headings),
        "source": "text-layer",
    }
    doc.close()
    return result