"""墨衍 · 试卷文件夹批量转 MD（质量优先：300dpi 渲染 + Docling 逐页 OCR → 合并）

用法：python tools/exam_folder_md.py "D:\\Desktop\\26年4月计算机科学与技术真题"
产出：每份 PDF 同目录 "<原名>.md"；中间 PNG 存临时目录，转换后清理。
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT = Path(__file__).resolve().parent.parent
VENV_PY = PROJECT / ".docling-venv" / "Scripts" / "python.exe"
WORKER = PROJECT / "tools" / "docling_worker.py"
DPI = 300                       # 质量优先：中文印刷体 OCR 高分档

SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".docx", ".pptx", ".xlsx", ".html", ".epub"}


def render_pdf_pngs(pdf: Path, work_dir: Path) -> list[Path]:
    import fitz
    doc = fitz.open(str(pdf))
    mat = fitz.Matrix(DPI / 72, DPI / 72)
    pngs = []
    for i, page in enumerate(doc, 1):
        out = work_dir / f"p{i:04d}.png"
        page.get_pixmap(matrix=mat).save(str(out))
        pngs.append(out)
    doc.close()
    return pngs


def docling_convert(src: Path, out_md: Path, out_json: Path, timeout: int = 1800) -> dict:
    cmd = [str(VENV_PY), str(WORKER), str(src), str(out_md), str(out_json)]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          timeout=timeout, cwd=str(PROJECT))
    meta = {"ok": False, "error": f"worker exit={proc.returncode}"}
    if out_json.exists():
        try:
            meta = json.loads(out_json.read_text(encoding="utf-8"))
        except Exception:
            pass
    meta["markdown"] = out_md.read_text(encoding="utf-8") if out_md.exists() else ""
    return meta


def convert_pdf(pdf: Path, work_dir: Path) -> tuple[str, dict]:
    pngs = render_pdf_pngs(pdf, work_dir)
    parts: list[str] = []
    total_s = 0.0
    stats = {"pages": len(pngs), "per_page_s": [], "chars": 0}
    for i, png in enumerate(pngs, 1):
        out_md = work_dir / f"p{i:04d}.md"
        meta = docling_convert(png, out_md, work_dir / f"p{i:04d}.json")
        total_s += meta.get("seconds", 0) or 0
        stats["per_page_s"].append(round(meta.get("seconds", 0) or 0, 1))
        stats["chars"] += meta.get("chars", 0)
        parts.append(f"\n\n<!-- 第 {i} 页 -->\n\n{meta.get('markdown', '').strip()}")
        png.unlink(missing_ok=True)   # 用完即删，控存储
    md = "\n".join(parts).strip()
    stats["seconds"] = round(total_s, 1)
    return md, stats


def main(folder: str) -> int:
    src_dir = Path(folder)
    if not src_dir.is_dir():
        print(f"目录不存在：{src_dir}")
        return 1
    if not VENV_PY.exists():
        print("缺 .docling-venv（先 uv venv --python 3.13 .docling-venv && uv pip install docling）")
        return 1
    work_root = PROJECT / "data" / "work" / "exam_convert"
    files = [f for f in sorted(src_dir.iterdir()) if f.suffix.lower() in SUPPORTED]
    print(f"待转换 {len(files)} 个文件")
    for f in files:
        work_dir = work_root / f.stem
        work_dir.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        try:
            if f.suffix.lower() == ".pdf":
                md, stats = convert_pdf(f, work_dir)
            else:
                out_md = work_dir / (f.stem + ".md")
                meta = docling_convert(f, out_md, work_dir / (f.stem + ".json"))
                md = meta.get("markdown", "")
                stats = meta
            out = src_dir / (f.stem + ".md")
            out.write_text(md or "", encoding="utf-8")
            secs = stats.get("seconds", 0) or 0
            print(f"[{f.name}] {secs:.0f}s -> {out.name}（{len(md):,} 字符，{len(md):,}）",
                  flush=True)
            if not md:
                print(f"   ⚠ 空输出：{stats.get('error', '未知')}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[{f.name}] 失败：{type(exc).__name__}: {str(exc)[:160]}", flush=True)
        print(f"  用时 {time.time() - t0:.0f}s", flush=True)
    print("\n完成。MD 已写入源文件夹。")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"D:\Desktop\26年4月计算机科学与技术真题"
    sys.exit(main(target))