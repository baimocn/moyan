"""从逐页片段重拼真题 MD（v2.1）：title→Markdown 标题、aside_text（密封区）丢弃。

背景：v2 拼版把 title 块当普通文本，导致上传后无标题结构 → 切章器整卷一章「全文」
→ 知识点规划退化。本脚本只动结构（加 # / 丢密封区碎片），正文一字不改；
片段是事实源，随时可重拼，原 v2 产物无丢失风险。

运行：python tools/exam_pp_rehead.py [--out 覆盖写回真题文件夹]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exam_ppstructure_md import _FOOTER, html_table_to_md  # noqa: E402

ROOT = Path(r"D:\Desktop\墨衍-项目")
WORK = ROOT / "data" / "work" / "exam_pp_v2"

PDF_NAMES = {
    "pdf01": "26.4 数据库原理与技术(1).md",
    "pdf02": "26.4 数据结构与算法.md",
    "pdf03": "26.4 计算机系统原理(1).md",
    "pdf04": "26.4 计算机网络与信息安全(1).md",
    "pdf05": "26.4 软件工程.md",
    "pdf06": "26.4 高级语言程序设计(1).md",
}


def page_md(frag: dict) -> str:
    lines = []
    for b in sorted(frag.get("blocks") or [], key=lambda x: (0, x["order"])
                    if x.get("order") is not None else (1, (x.get("bbox") or [0])[1])):
        label, content = b.get("label", ""), (b.get("content") or "").strip()
        if label in ("header", "footer", "number", "aside_text"):
            continue                                   # 页眉/页脚/页码/密封区剔除
        if _FOOTER.match(content):
            continue                                   # 「试题第N页(共M页)」兜底
        if label == "doc_title":
            lines.append(f"# {content}" if content else "")
        elif label == "paragraph_title":
            lines.append(f"## {content}" if content else "")
        elif label == "table":
            lines.append(html_table_to_md(content) if "<table" in content else content)
        elif label == "image":
            lines.append("<!-- 图片 -->")
        elif content:
            lines.append(content)
    return "\n\n".join(x for x in lines if x).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\Desktop\26年4月计算机科学与技术真题")
    args = ap.parse_args()
    out_dir = Path(args.out)
    for key, name in PDF_NAMES.items():
        frag_dir = WORK / key / "frag"
        if not frag_dir.exists():
            print(f"跳过 {key}：缺片段目录")
            continue
        pages = sorted(frag_dir.glob("page_*.json"))
        parts = []
        for fp in pages:
            frag = json.loads(fp.read_text(encoding="utf-8"))
            parts.append(f"\n\n<!-- 第 {frag['page']} 页 -->\n\n{page_md(frag)}")
        md = "\n".join(parts).strip() + "\n"
        out = out_dir / name
        out.write_text(md, encoding="utf-8")
        n_h1 = md.count("\n# ") + md.startswith("# ")
        n_h2 = md.count("\n## ")
        print(f"{name}: {len(pages)} 页，{len(md):,} 字，# x{n_h1}，## x{n_h2}")
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
