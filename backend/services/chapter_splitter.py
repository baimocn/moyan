"""墨衍 · Markdown → 章节切割服务

对齐规划核心差别化："按章节切割、上下文隔离"——每章独立存储、独立处理，
防止上下文过大、注意力分散、答串题。

切割规则：
1. 一级标题（#）是章节锚点；
2. 整份文档没有一级标题时，取"最低级别标题"当顶层章节（例如全是 ## → 按 ## 切）；
3. 首个标题之前的内容（前言/目录等）如果不为空，归为"前言"章（index 0）；
4. 章内的小标题（##/###…）保留在章节原文里，同时收集成章内目录 toc 供前端展示。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# 匹配 Markdown 标题行：^#{1,6} 一个空格 内容
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

# 整行 HTML 注释（docling 常见的页码占位 `<!-- 第 1 页 -->` 等）
# 替换成空串后该行变空行，行号保持不变，不影响标题锚点定位。
_COMMENT_LINE_RE = re.compile(r"^[ \t]*<!--.*?-->[ \t]*$", re.MULTILINE)
# "纯注释标题行"：`# <!-- 第 1 页 -->` —— 剥掉注释只剩 # 残骸，整行清空
_COMMENT_HEADING_RE = re.compile(r"^[ \t]*#{1,6}[ \t]*<!--.*?-->[ \t]*$", re.MULTILINE)
# 标题文本内嵌的注释片段
_COMMENT_INLINE_RE = re.compile(r"<!--.*?-->")


def _clean_title(title: str) -> str:
    """剥离标题里的 HTML 注释；剥离后为空的标题不是有效标题。"""
    return _COMMENT_INLINE_RE.sub("", title).strip()


@dataclass
class TocItem:
    """章内目录条目。"""
    level: int
    title: str


@dataclass
class Chapter:
    """切割产物：一个章节。"""
    index: int                 # 0 起
    title: str
    level: int                 # 顶层标题在原文中的级别（1 或更低标题级别）
    char_count: int            # 正文字符数（不含空白）
    markdown: Optional[str] = None
    toc: list = field(default_factory=list)  # list[TocItem]，章内小标题


@dataclass
class SplitResult:
    """一次切割的完整产物。"""
    chapters: list = field(default_factory=list)  # list[Chapter]
    top_level: int = 1
    total_chars: int = 0


_COUNT_WS_RE = re.compile(r"\s+")  # 统计时剔除空白


def _char_count(text: str) -> int:
    return len(_COUNT_WS_RE.sub("", text))


def _parse_headings(markdown: str) -> list[tuple[int, int, str]]:
    """返回 (level, 起始行号, 标题文本) 列表，按出现顺序。行号从 0 起。"""
    out: list[tuple[int, int, str]] = []
    for lineno, line in enumerate(markdown.splitlines()):
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = _clean_title(m.group(2))
            if title:
                out.append((level, lineno, title))
    return out


def split_markdown(markdown: str) -> SplitResult:
    """把 Markdown 切成章节。"""
    # 整行 HTML 注释（如 docling 的 `<!-- 第 1 页 -->` 页码占位）清成空行：
    # 行号不变，标题锚点定位不受影响；避免注释行被当前言内容或碎章标题。
    # 纯注释标题行（`# <!-- 第 1 页 -->`）同理整行清空，防止 # 残骸入标题。
    md = _COMMENT_HEADING_RE.sub("", _COMMENT_LINE_RE.sub("", markdown or "")).strip()
    result = SplitResult()
    if not md:
        return result

    lines = md.splitlines()
    headings = _parse_headings(md)
    if not headings:
        # 无任何标题：整份当作一章（标题=文件名占位"全文"）
        result.chapters = [Chapter(
            index=0, title="全文", level=1,
            char_count=_char_count(md), markdown=md,
        )]
        result.total_chars = result.chapters[0].char_count
        result.top_level = 1
        return result

    # 顶层章节级别：所有标题里的最小级别（# 为 1）
    top_level = min(h[0] for h in headings)
    result.top_level = top_level

    # 顶层标题作为切分点
    top_anchors = [(lineno, title) for (lv, lineno, title) in headings if lv == top_level]

    sections: list[tuple[str, str, list[TocItem], bool]] = []
    # (标题, 内容, 章内toc, 是否顶层锚点章)
    for i, (lineno, title) in enumerate(top_anchors):
        start = lineno
        end = top_anchors[i + 1][0] if i + 1 < len(top_anchors) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        toc: list[TocItem] = []
        for (lv, ln, t) in headings:
            if ln > start and ln < end:
                toc.append(TocItem(level=lv, title=t))
        sections.append((title, body, toc, True))

    # 首个标题之前的内容 → 前言
    first_anchor_line = top_anchors[0][0]
    prelude = "\n".join(lines[:first_anchor_line]).strip()
    if prelude:
        first_line = _clean_title(prelude.splitlines()[0])
        sections.insert(0, (first_line[:20] or "前言", prelude, [], False))

    chapters: list[Chapter] = []
    for idx, (title, body, toc, _is_top) in enumerate(sections):
        chapters.append(Chapter(
            index=idx,
            title=title,
            level=top_level,
            char_count=_char_count(body or title),
            markdown=(f"{'#' * top_level} {title}\n\n{body}".strip() if body else f"{'#' * top_level} {title}"),
            toc=toc,
        ))

    result.chapters = chapters
    result.total_chars = sum(c.char_count for c in chapters)
    return result