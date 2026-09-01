"""端到端测试：生成测试 PDF → 解析为 Markdown → 按章节切割。

运行：
    python -m backend.tests.test_pipeline
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # 项目根

from backend.services.chapter_splitter import split_markdown
from backend.services.pdf_parser import parse_pdf
from backend.tests.make_test_pdf import build

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  [PASS] {name}")
    else:
        FAILURES.append(name)
        print(f"  [FAIL] {name}  {detail}")


def main() -> int:
    print("① 生成测试 PDF")
    pdf_path = build()
    print(f"   文件：{pdf_path}，大小 {pdf_path.stat().st_size} 字节")

    print("② PDF → Markdown")
    result = parse_pdf(str(pdf_path))
    md = result.markdown or ""
    check("提取出非空文本", len(md) > 100, f"得到 {len(md)} 字符")
    check("页眉被过滤", "操作系统 · 期末复习资料" not in md, "页眉出现在正文里")
    check("页码被过滤", "第 1 页" not in md, "页码出现在正文里")
    check("识别出多个标题", len(result.headings) >= 4, f"只识别 {result.headings}")
    check("一级标题正确", any(h.level == 1 and "第一章" in h.text for h in result.headings),
          str([h.text for h in result.headings]))
    check("二级标题正确", any(h.level == 2 and "1.1" in h.text for h in result.headings),
          str([(h.level, h.text) for h in result.headings]))
    print(f"   识别标题：{[ (h.level, h.text) for h in result.headings ]}")
    if result.warnings:
        print(f"   警告：{result.warnings}")

    print("③ Markdown → 章节")
    split = split_markdown(md)
    check("切出 >=3 章", len(split.chapters) >= 3, f"只有 {len(split.chapters)} 章")
    for ch in split.chapters:
        check(f"   章节[{ch.index}] 标题非空且字数>0",
              bool(ch.title) and ch.char_count > 0,
              f"title={ch.title!r} chars={ch.char_count}")
    titles = [c.title for c in split.chapters]
    print(f"   章节列表：{titles}")
    check("第一章排在最前", titles and "第一章" in titles[0], str(titles))
    check("章内子标题进入 toc",
          any(t.title.startswith("1.1") for t in split.chapters[0].toc),
          str(split.chapters[0].toc))

    print("④ 章节示例预览（第一章前 120 字）")
    print("   " + (split.chapters[0].markdown or "")[:120].replace("\n", " ⏎ "))

    if FAILURES:
        print(f"\n共 {len(FAILURES)} 项失败：{FAILURES}")
        return 1
    print("\n全部通过 ✓ 解析地基（上传PDF→Markdown→分章节）可用")
    return 0


if __name__ == "__main__":
    sys.exit(main())