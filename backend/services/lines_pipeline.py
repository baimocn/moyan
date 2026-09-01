"""墨衍 · 统一行流 → Markdown 管线

两种来源共用一条管线，只是"标题识别"策略不同：
- source="pdf"：文本层。按【字号】聚类定标题层级（字号差异真实存在）。
- source="ocr" ：Windows OCR。字号(行高)区分度小，改用【模式匹配】为主：
  第X章/篇 = 一级；第X节 = 二级；数字/罗马编号 = 三级；汉序号 = 四级；
  行高显著 + 短行 = 章级候选兜底。

公共步骤：
1. 页眉/页脚区过滤（跨页重复行 + 页码模式）；
2. （OCR）噪声行清洗、目录页整页剔除（防止目录里的"第X章…页码"污染切章）；
3. 标题识别；
4. 组装 Markdown。

输出"原原本本"的文本，不做内容改写。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

# ---------- 参数 ----------

HEADER_ZONE = 0.12          # 页面上部 12% 视为页眉区
FOOTER_ZONE = 0.85          # 页面下部 15% 视为页脚区
REPEAT_PAGE_RATIO = 0.6     # 某行在 >=60% 的页面出现 → 重复帧行
TITLE_MAX_CHARS = 60        # 标题行长度上限（模式匹配时）

# PDF 源：字号启发式
PDF_HEADING_FONT_RATIO = 1.15
PDF_CLUSTER_GAP = 1.2       # 标题字号聚类容差(pt)
PDF_PARA_GAP_RATIO = 1.3    # 行距 > 1.3×字号 → 段间隔

# OCR 源
OCR_PARA_GAP_RATIO = 2.2    # OCR 行距/行高；正文行距≈1.5×行高，段间隔更大
OCR_TITLE_HEIGHT_RATIO = 1.35  # 无编号但行高显著 → 章级候选
OCR_DIRECTORY_MIN_HITS = 4     # 一页 >=4 个"第X章/篇/卷/节"行 → 整页判为目录页
OCR_HEADER_MIN_PAGES = 2       # 页眉主干在 >=2 页出现 → 页眉，删（OCR 每页变体多）
OCR_HEADER_MAX_SPAN_MULT = 4   # 出现页跨度 <= 页数×4（连续段）才算页眉
OCR_HEADER_HEIGHT_RATIO = 1.25 # 行高超过中位数×该值（真·大标题）不当作页眉删

# 页眉主干：剥离"第X章/节"编号后留下的章名（OCR 噪声下按主干聚合比全文可靠）
_HEADER_STEM_RE = re.compile(r"^第[^\s]{1,5}(?:[章篇卷节])")

# 页码模式（帧区内命中的行删除）
_PAGE_NUM_RE = re.compile(
    r"^\s*(\d{1,4}"
    r"|第\s*[0-9一二三四五六七八九十百千]+\s*[页pP]"
    r"|page\s*\d+"
    r"|-\s*\d+\s*-"
    r"|\d+\s*/\s*\d+"
    r")\s*$",
    re.IGNORECASE,
)

# OCR 标题模式（按级别）
_OCR_TITLE_PATTERNS: list[tuple[int, re.Pattern]] = [
    (1, re.compile(r"^第\s*[0-9一二三四五六七八九十百千万零]+\s*[章篇卷]")),
    (1, re.compile(r"^第[^\s]{1,4}[章篇卷]")),            # 宽松兜底（容忍 OCR 错字）
    (2, re.compile(r"^第\s*[0-9一二三四五六七八九十百千零]+\s*节")),
    (2, re.compile(r"^第[^\s]{1,4}节")),
    (3, re.compile(r"^[（(]?[0-9]{1,2}[)）]?[.．、]")),   # 1． / （1） / 1.
    (3, re.compile(r"^[IVXLC]+[.．、]")),                   # I. / II、
    (4, re.compile(r"^[（(][一二三四五六七八九十]+[)）][,，、]?")),  # （一）
    (4, re.compile(r"^[一二三四五六七八九十]+[,，、]")),    # 一、
]

# 行清洗（OCR 噪声）
_SCRUB_RE = re.compile(r"^[\s·•●◆■□▲△★※→←↑↓\-—–_=+|/\\~#*]+$")   # 纯符号行
_TAIL_PUNCT_RE = re.compile(r"^[、．。，,．·;；:：]+\s*$")            # 孤立标点行

# 教材常见的书眉/附属残件（任意位置出现即排除出标题候选，不参与切章）
_NOISE_TITLE_RE = re.compile(r"(教学课件|思考题参考答案|本章小结|本章思考题|参考答案|自测题)")


@dataclass
class Heading:
    level: int
    text: str
    font_size: float


def _char_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


# ---------- 公有步骤 ----------

def _filter_frame_lines(lines: list[dict], page_count: int) -> list[dict]:
    """过滤页眉/页脚：只在页面上下边缘区内判断。"""
    if not lines:
        return lines
    counts: dict[str, int] = {}
    for ln in lines:
        if ln.get("rel_y", 0.5) < HEADER_ZONE or ln.get("rel_y", 0.5) > FOOTER_ZONE:
            counts[ln["text"]] = counts.get(ln["text"], 0) + 1
    threshold = max(2, int(page_count * REPEAT_PAGE_RATIO))
    repeated = {t for t, c in counts.items() if c >= threshold}

    kept: list[dict] = []
    for ln in lines:
        in_zone = ln.get("rel_y", 0.5) < HEADER_ZONE or ln.get("rel_y", 0.5) > FOOTER_ZONE
        if not in_zone:
            kept.append(ln)
            continue
        if _PAGE_NUM_RE.match(ln["text"]) or ln["text"] in repeated:
            continue
        kept.append(ln)
    return kept


def _scrub_ocr_lines(lines: list[dict]) -> list[dict]:
    """剔除 OCR 噪声行：纯符号、孤立标点、单字符（页眉/表格碎片）、行首装饰号。"""
    kept = []
    for ln in lines:
        t = ln["text"]
        t = re.sub(r"^[?？]+", "", t)  # OCR 常把装饰符识别成问号
        if _SCRUB_RE.match(t) or _TAIL_PUNCT_RE.match(t):
            continue
        if len(t) <= 1:
            continue
        ln = dict(ln, text=t)
        kept.append(ln)
    return kept


def _match_ocr_level(text: str) -> Optional[int]:
    for level, pat in _OCR_TITLE_PATTERNS:
        if pat.match(text):
            return level
    return None


def _header_stem(text: str) -> str:
    m = _HEADER_STEM_RE.match(text)
    body = text[m.end():] if m else text
    return re.sub(r"[\s·．.、,，:：]+", "", body)


def _drop_directory_pages(lines: list[dict]) -> list[dict]:
    """目录页整页剔除：页面顶部页眉已删的前提下，
    一页若有 >=4 个"第X章/篇/卷/节"行（真·章节标题样式），判为目录页。

    正文章页绝少同时出现 4 个章节级标题；目录页全是这类条目。
    """
    top_patterns = _OCR_TITLE_PATTERNS[:4]  # 只数 1/2 级（章/篇/节开头）

    def is_top_hit(t: str) -> bool:
        return len(t) <= TITLE_MAX_CHARS and any(p.match(t) for _, p in top_patterns)

    keep_flags = [True] * len(lines)
    by_page: dict[int, list[int]] = {}
    for i, ln in enumerate(lines):
        by_page.setdefault(ln["page"], []).append(i)

    dropped = 0
    for page, idxs in by_page.items():
        hits = sum(1 for i in idxs if is_top_hit(lines[i]["text"]))
        if hits >= OCR_DIRECTORY_MIN_HITS:
            for i in idxs:
                keep_flags[i] = False
            dropped += 1
            print(f"[lines_pipeline] 第 {page} 页判定为目录页，整页剔除（{hits} 个章节级标题行）")
    if dropped:
        lines = [ln for ln, keep in zip(lines, keep_flags) if keep]
    return lines


def _drop_repeated_headers(lines: list[dict]) -> list[dict]:
    """剔除印在每页顶部的章节页眉（"第一章 细胞"这类）。

    OCR 噪声会让同一页眉每次识别略有差异（"组织、器官和系统" vs
    "纟目织、器宫和系统"），因此用 **bigram 相似度模糊聚类**：
    页眉位（页上部）+ 标题模式 + 普通行高 的行两两比较相似度，
    相似（>=0.5）归为一簇；簇覆盖 >=3 个跨页紧凑的页面 → 整簇删除。
    真·大字号章首页标题（行高 > 中位数×1.25）不参与。
    """

    def bigrams(t: str) -> set[str]:
        z = re.sub(r"[\s·．.、,，:：]+", "", t)
        return {z[i:i + 2] for i in range(len(z) - 1)} if len(z) >= 2 else {z}

    def sim(a: str, b: str) -> float:
        ba, bb = bigrams(a), bigrams(b)
        if not ba or not bb:
            return 0.0
        return 2.0 * len(ba & bb) / (len(ba) + len(bb))

    if not lines:
        return lines
    median_h = sorted(ln["size"] for ln in lines)[len(lines) // 2]
    header_cap = median_h * OCR_HEADER_HEIGHT_RATIO

    cands = [
        ln for ln in lines
        if ln.get("rel_y", 0.5) < HEADER_ZONE
        and _match_ocr_level(ln["text"])
        and ln["size"] <= header_cap
        and len(ln["text"]) <= TITLE_MAX_CHARS
    ]
    if len(cands) < 2:
        return lines

    # 并查集：相似度 >= 0.5 的行归入同一簇
    parent = list(range(len(cands)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    n = len(cands)
    for i in range(n):
        for j in range(i + 1, n):
            if sim(cands[i]["text"], cands[j]["text"]) >= 0.5:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj

    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(i)

    drop_ids: set[int] = set()
    dropped = 0
    for root, members in clusters.items():
        if len(members) < OCR_HEADER_MIN_PAGES:
            continue
        pages = sorted({cands[i]["page"] for i in members})
        if len(pages) < OCR_HEADER_MIN_PAGES:
            continue
        span = pages[-1] - pages[0]
        if span > max(OCR_HEADER_MIN_PAGES, len(pages) * OCR_HEADER_MAX_SPAN_MULT):
            continue
        for i in members:
            drop_ids.add(id(cands[i]))
            dropped += 1
    if dropped:
        print(f"[lines_pipeline] 剔除 {dropped} 条章节页眉（{len(cands)} 候选中 {len(drop_ids)} 条）")
    return [ln for ln in lines if id(ln) not in drop_ids]


# ---------- 标题识别 ----------

def _cluster_sizes_to_levels(candidate_sizes: set[float]) -> dict[float, int]:
    sizes = sorted(candidate_sizes, reverse=True)
    clusters: list[list[float]] = []
    for s in sizes:
        if clusters and (clusters[-1][-1] - s) <= max(PDF_CLUSTER_GAP, 0.06 * s):
            clusters[-1].append(s)
        else:
            clusters.append([s])
    size_to_level: dict[float, int] = {}
    for i, cl in enumerate(clusters):
        level = min(i + 1, 6)
        for s in cl:
            size_to_level[s] = level
    return size_to_level


def _headings_by_font(lines: list[dict], median_size: float) -> list[Heading]:
    """PDF 源：字号启发式。"""
    candidates = [
        ln for ln in lines
        if ln["size"] >= median_size * PDF_HEADING_FONT_RATIO
        and len(ln["text"]) <= TITLE_MAX_CHARS
    ]
    if not candidates:
        return []
    size_to_level = _cluster_sizes_to_levels({round(ln["size"], 1) for ln in candidates})
    return [
        Heading(level=size_to_level[round(ln["size"], 1)], text=ln["text"], font_size=ln["size"])
        for ln in lines if any(ln is c for c in candidates)
    ]


_FALLBACK_HEADING_RE = re.compile(
    r"^\s*(第[一二三四五六七八九十百千万0-9]+[章节篇卷]"
    r"|Chapter\s+[0-9IVXLCDM]+"
    r"|[0-9]+(?:\.[0-9]+)*[、.．]\s*\S)"
)


def _headings_by_pattern(lines: list[dict]) -> list[Heading]:
    """OCR 源：模式优先 + 行高兜底（兜底要求 >=4 字，防页眉碎片误升标题）。

    章首页大标题常被 OCR 拆成两行（"第二章" + "组织丶器官和系统"），
    这里把同页相邻的"编号标题行 + 无编号章名行"合并为一个完整标题。
    """
    heights = [ln["size"] for ln in lines]
    median = sorted(heights)[len(heights) // 2] if heights else 0

    cands: list[dict] = []
    for ln in lines:
        t = ln["text"]
        if len(t) > TITLE_MAX_CHARS or _NOISE_TITLE_RE.search(t):
            continue
        level = _match_ocr_level(t)
        via_pattern = level is not None
        if level is None and len(t) >= 4 and ln["size"] >= median * OCR_TITLE_HEIGHT_RATIO and len(t) <= 30:
            # 无编号兜底：超大行高（>=1.5x，章名特征）+ 页上部 → 章级；否则节级
            if ln.get("rel_y", 0.5) < 0.3 and ln["size"] >= median * 1.5:
                level = 1
            else:
                level = 2
        if level is not None:
            cands.append({
                "level": level, "text": t, "font_size": ln["size"],
                "page": ln["page"], "y0": ln["y0"], "via_pattern": via_pattern,
                "short_num": bool(re.match(r"^第[^\s]{1,4}[章篇卷][^\s]{0,2}$", t)),
            })

    # 合并同页相邻标题（编号行 + 紧随的章名行）
    cands.sort(key=lambda c: (c["page"], c["y0"]))
    merged: list[dict] = []
    i = 0
    while i < len(cands):
        cur = cands[i]
        j = i + 1
        while (
            j < len(cands)
            and cands[j]["page"] == cur["page"]
            and cur["level"] <= 2
            and cur["via_pattern"]
            and not cands[j]["via_pattern"]
            and cands[j]["y0"] - cur["y0"]
            <= max(60.0, 2.0 * max(cur["font_size"], cands[j]["font_size"]))
        ):
            cur["text"] = cur["text"] + cands[j]["text"]
            cur["font_size"] = max(cur["font_size"], cands[j]["font_size"])
            cur["short_num"] = False  # 已带上章名，恢复章级地位
            j += 1
        if cur["short_num"] and cur["font_size"] <= median * OCR_HEADER_HEIGHT_RATIO:
            # 普通行高的纯"第X章"编号行、后面没跟章名 → 大概率是页眉残件，
            # 降级不参与切章；大行高（真章首页大标题）保留。
            cur["level"] = 4
        merged.append(cur)
        i = j

    return [Heading(level=c["level"], text=c["text"], font_size=c["font_size"]) for c in merged]


def _fallback_headings(lines: list[dict]) -> list[Heading]:
    headings: list[Heading] = []
    for ln in lines:
        m = _FALLBACK_HEADING_RE.match(ln["text"])
        if not m:
            continue
        prefix = m.group(0).strip()
        level = 1 if (prefix.startswith("第") or prefix.upper().startswith("CHAPTER")) else 2
        headings.append(Heading(level=level, text=ln["text"], font_size=ln["size"]))
    return headings


# ---------- 组装 Markdown ----------

def _assemble_md(lines: list[dict], headings: list[Heading], *, para_gap_ratio: float) -> str:
    heading_by_text: dict[str, Heading] = {h.text: h for h in headings}
    chunks: list[str] = []
    buffer: list[str] = []
    prev_bottom: Optional[float] = None
    prev_size = 0.0

    def flush() -> None:
        nonlocal buffer
        if buffer:
            chunks.append(" ".join(buffer).strip())
            buffer = []

    for ln in lines:
        h = heading_by_text.get(ln["text"])
        if (buffer and prev_bottom is not None
                and ln["y0"] - prev_bottom > para_gap_ratio * prev_size
                and not h):
            flush()
        if h:
            flush()
            chunks.append(f"{'#' * h.level} {ln['text']}")
        else:
            buffer.append(ln["text"])
        prev_bottom = ln["y0"] + ln["size"]
        prev_size = ln["size"]
    flush()

    md = "\n\n".join(chunks)
    return re.sub(r"\n{3,}", "\n\n", md).strip()


# ---------- 主入口 ----------

def build_markdown(
    lines: list[dict],
    *,
    source: Literal["pdf", "ocr"] = "pdf",
    page_count: Optional[int] = None,
) -> tuple[str, list[Heading], list[str]]:
    """行流 → (markdown, headings, warnings)。"""
    warnings: list[str] = []
    page_count = page_count or (max((ln.get("page", 0) for ln in lines), default=0) + 1)
    lines = _filter_frame_lines(lines, page_count)
    if source == "ocr":
        lines = _scrub_ocr_lines(lines)
        lines = _drop_repeated_headers(lines)
        lines = _drop_directory_pages(lines)
        if not lines:
            return "", [], [*warnings, "OCR 未识别出可用文本（可能整本为纯图/乱码）"]

    heights = [ln["size"] or ln.get("height", 0) for ln in lines]
    median_size = sorted(heights)[len(heights) // 2] if heights else 0

    if source == "pdf":
        headings = _headings_by_font(lines, median_size)
        if not headings:
            headings = _fallback_headings(lines)
            if headings:
                warnings.append("未检测到字号差异的标题，已用正则规则（第X章/Chapter/数字编号）兜底识别。")
        para_gap_ratio = PDF_PARA_GAP_RATIO
    else:
        headings = _headings_by_pattern(lines)
        if not headings:
            warnings.append("OCR 未识别出任何标题样式，整份将作为单章处理。")
        para_gap_ratio = OCR_PARA_GAP_RATIO

    md = _assemble_md(lines, headings, para_gap_ratio=para_gap_ratio)
    return md, headings, warnings


def count_chars(text: str) -> int:
    return _char_count(text)