"""墨衍 · 试卷 PP-Structure 精修 v2（分辨率安全 + 段崩隔离）

v2 变更（2026-08-29，依据 E1/E2 判别实验）：
- 300dpi 触发 PP-OCRv5_server_det 原生 access violation（150/200dpi 正常）→ 默认 200dpi；
- 逐 PDF subprocess 隔离：段崩只死 worker，缺页自动降 fallback dpi 逐页重试；
- 工作目录纯 ASCII，避开本项目已知的「原生库中文路径」坑类；
- 每页结果落 JSON 片段，字段名以实际产出为准（首块带原始 repr 供校验）。

流程：pymupdf 渲染 → PPStructureV3（server OCR + 版面 + 表格 HTML + 公式 LaTeX）
→ 按版面顺序拼 Markdown（表格 HTML→MD、页眉页码剔除、图片占位）→ 写回同名 .md。

运行：.ocr-venv/Scripts/python.exe tools/exam_ppstructure_md.py "文件夹路径" [--dpi 200] [--max-pages N]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\Desktop\墨衍-项目")
PY = ROOT / ".ocr-venv" / "Scripts" / "python.exe"
WORKER = ROOT / "tools" / "exam_pp_worker.py"
WORK = ROOT / "data" / "work" / "exam_pp_v2"
DIAG = ROOT / "data" / "work" / "exam_pp_diag"

_HTML_TAG = re.compile(r"<[^>]+>")
_TR_KEY = re.compile(r"<tr[^>]*>(.*?)</tr>", re.I | re.S)
_TD_KEY = re.compile(r"<t[hd][^>]*>(.*?)</t[hd]>", re.I | re.S)
_FOOTER = re.compile(r"^.{0,24}试题\s*第\s*\d+\s*页\s*[（(]\s*共\s*\d+\s*页\s*[)）]\s*$")


def html_table_to_md(html: str) -> str:
    """<table><tr><td>..</td></tr>...</table> → Markdown 表格。"""
    rows = []
    for tr in _TR_KEY.findall(html):
        cells = [_HTML_TAG.sub("", td).replace("$", "").strip()
                 for td in _TD_KEY.findall(tr)]
        if cells:
            rows.append(cells)
    if not rows:
        return html
    out = [f"| {' | '.join(rows[0])} |",
           f"| {' | '.join(['---'] * len(rows[0]))} |"]
    out += [f"| {' | '.join(r)} |" for r in rows[1:]]
    return "\n".join(out)


def page_md_from_fragment(frag: dict) -> str:
    def key(b):
        if b.get("order") is not None:
            return (0, b["order"])
        box = b.get("bbox") or [0, 0, 0, 0]
        return (1, box[1])

    lines = []
    for b in sorted(frag.get("blocks") or [], key=key):
        label = b.get("label", "")
        content = (b.get("content") or "").strip()
        if label in ("number", "header", "footer", "page_footer", "page_header"):
            continue                                  # 页码/页眉/页脚剔除
        if _FOOTER.match(content):
            continue                                  # 「试题第N页(共M页)」标签漏判的页脚兜底
        if label == "table":
            lines.append(html_table_to_md(content) if "<table" in content else content)
        elif label == "image":
            lines.append("<!-- 图片 -->")
        elif content:                                 # text/formula/title 等含文本照收
            lines.append(content)
    return "\n\n".join(lines).strip()


def run_worker(args_list: list[str], log_path: Path, timeout: int) -> int:
    DIAG.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        try:
            p = subprocess.run([str(PY), str(WORKER), *args_list],
                               stdout=lf, stderr=subprocess.STDOUT,
                               cwd=str(ROOT), timeout=timeout)
            return p.returncode
        except subprocess.TimeoutExpired:
            print(f"    [timeout] worker 超时 {timeout}s，已终止", flush=True)
            return -9


def process_pdf(pdf: Path, idx: int, dpi: int, fallback_dpi: int,
                max_pages: int) -> tuple[int, list[int], float]:
    stem_ascii = f"pdf{idx:02d}"
    work = WORK / stem_ascii
    frag = work / "frag"

    import pymupdf

    doc = pymupdf.open(str(pdf))
    n_pages = doc.page_count
    doc.close()
    if max_pages:
        n_pages = min(n_pages, max_pages)

    t0 = time.time()
    only = ",".join(str(i) for i in range(1, n_pages + 1))
    rc = run_worker(["--pdf", str(pdf), "--work", str(work), "--out", str(frag),
                     "--dpi", str(dpi), "--only", only],
                    DIAG / f"worker_{stem_ascii}.log", timeout=60 * 45)
    if rc != 0:
        print(f"    [worker] 整册退出码 {rc}（段崩/异常），细节见 {DIAG.name}\\worker_{stem_ascii}.log",
              flush=True)

    done = {i for i in range(1, n_pages + 1)
            if (frag / f"page_{i:04d}.json").exists()}
    missing = sorted(set(range(1, n_pages + 1)) - done)
    if missing:
        print(f"    [retry] 缺页 {missing}，降 {fallback_dpi}dpi 逐页重试", flush=True)
    for i in missing:
        rc2 = run_worker(["--pdf", str(pdf), "--work", str(work), "--out", str(frag),
                          "--dpi", str(fallback_dpi), "--only", str(i)],
                         DIAG / f"worker_{stem_ascii}_p{i}.log", timeout=60 * 15)
        if rc2 != 0:
            print(f"    [retry] 第 {i} 页 {fallback_dpi}dpi 仍失败（退出码 {rc2}）",
                  flush=True)
        done |= {i for i in range(1, n_pages + 1)
                 if (frag / f"page_{i:04d}.json").exists()}

    final_missing = sorted(set(range(1, n_pages + 1)) - done)
    parts = []
    for i in range(1, n_pages + 1):
        fp = frag / f"page_{i:04d}.json"
        if fp.exists():
            body = page_md_from_fragment(json.loads(fp.read_text(encoding="utf-8")))
        else:
            body = "（本页精修失败，待重跑）"
        parts.append(f"\n\n<!-- 第 {i} 页 -->\n\n{body}")
    md = "\n".join(parts).strip()
    out_md = pdf.parent / (pdf.stem + ".md")
    out_md.write_text(md, encoding="utf-8")

    dt = (time.time() - t0) / 60
    print(f"[{pdf.name}] {dt:.1f}min {dpi}dpi（缺页重试 {fallback_dpi}dpi）"
          f" -> {out_md.name}（{len(md):,} 字）"
          f"{' 失败页:' + str(final_missing) if final_missing else ''}",
          flush=True)
    return len(done), final_missing, dt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--fallback-dpi", type=int, default=150)
    ap.add_argument("--max-pages", type=int, default=0, help="调试限每册页数")
    args = ap.parse_args()

    src_dir = Path(args.folder)
    WORK.mkdir(parents=True, exist_ok=True)
    total_done, total_fail, total_min = 0, [], 0.0
    for idx, pdf in enumerate(sorted(src_dir.glob("*.pdf")), 1):
        n, miss, dt = process_pdf(pdf, idx, args.dpi, args.fallback_dpi,
                                  args.max_pages)
        total_done += n
        total_fail += miss
        total_min += dt
    print(f"ALL DONE: {total_done} 页成功 / 失败 {len(total_fail)} 页"
          f"{total_fail}，共 {total_min:.1f}min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
