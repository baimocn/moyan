# -*- coding: utf-8 -*-
"""chapter_splitter 碎章修复测试：HTML 注释不应成为章节/标题。

背景：docling 转出的 markdown 常含整行页码注释 `<!-- 第 1 页 -->`，
旧逻辑会把首个标题前的注释行当成"前言"内容，标题取注释原文，
导致选课页 picker 出现 `<!-- 第 1 页 -->` 碎章。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.services.chapter_splitter import split_markdown


def test_comment_prelude_not_chapter():
    """文件开头的整行注释不应产生碎章（真实场景：数据库真题 cba7e4）。"""
    md = """<!-- 第 1 页 -->

# 数据库原理与技术

（课程代码13009)

## 注意事项：

1. 本试卷共5页。
"""
    split = split_markdown(md)
    titles = [c.title for c in split.chapters]
    assert titles == ["数据库原理与技术"], titles
    # 正文里也不应残留整行注释
    assert "<!--" not in (split.chapters[0].markdown or "")


def test_inline_comment_in_heading_stripped():
    """标题内嵌注释片段应被剥离，剥离后为空的标题行不是锚点。"""
    md = """# <!-- 第 1 页 -->

## 真正的<!-- 杂音 -->标题

正文内容。
"""
    split = split_markdown(md)
    titles = [c.title for c in split.chapters]
    # `# <!-- 第 1 页 -->` 清洗后为空 → 不算标题；整份只剩一个真标题
    assert titles == ["真正的标题"], titles


def test_all_comment_headings_fallback_fulltext():
    """全是注释标题时应兜底成"全文"一章，而不是碎章集合。"""
    md = """<!-- 第 1 页 -->

正文第一段。

<!-- 第 2 页 -->

正文第二段。
"""
    split = split_markdown(md)
    assert len(split.chapters) == 1
    assert split.chapters[0].title == "全文"
    assert "正文第一段" in (split.chapters[0].markdown or "")
    assert "<!--" not in (split.chapters[0].markdown or "")


def test_prelude_real_content_kept():
    """标题前若有真实内容（非注释），前言章仍应保留，但标题不受注释污染。"""
    md = """<!-- 封面注释 -->

考试说明：闭卷，120分钟。

# 第一章 概述

内容。
"""
    split = split_markdown(md)
    titles = [c.title for c in split.chapters]
    assert titles[0] == "考试说明：闭卷，120分钟。", titles
    assert titles[1] == "第一章 概述", titles
