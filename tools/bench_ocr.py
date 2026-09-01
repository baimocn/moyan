"""墨衍 · OCR 引擎对比基准：Windows OCR vs RapidOCR（同一批页面）

用法：python tools/bench_ocr.py <png目录> <页号...> [--dpi 200]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def bench_rapid(png: Path):
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()
    t0 = time.time()
    result, elapse = engine(str(png))
    dt = time.time() - t0
    rows = []
    for item in (result or []):
        box, text, score = item
        ys = [p[1] for p in box]
        rows.append((min(ys), text, score))
    rows.sort()
    return dt, rows


def bench_windows(png: Path):
    import subprocess, json
    out = png.parent / "_win_tmp.json"
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(Path(__file__).parent / "winocr.ps1"),
           "-PngDir", str(png.parent), "-OutJson", str(out), "-MaxPages", "0"]
    # 只识别单页：临时目录
    tmpdir = png.parent / "_single"
    tmpdir.mkdir(exist_ok=True)
    (tmpdir / png.name).write_bytes(png.read_bytes())
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(Path(__file__).parent / "winocr.ps1"),
           "-PngDir", str(tmpdir), "-OutJson", str(out)]
    t0 = time.time()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    dt = time.time() - t0
    data = json.loads(out.read_text(encoding="utf-8-sig"))
    rows = sorted(((r["y0"], r["text"], 1.0) for r in data), key=lambda x: x[0])
    return dt, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("png_dir")
    ap.add_argument("pages", nargs="+", help="页号（对应 pXXXX.png）")
    ap.add_argument("--engine", default="rapid", choices=["rapid", "win", "both"])
    args = ap.parse_args()
    d = Path(args.png_dir)

    for pno in args.pages:
        png = d / f"p{int(pno):04d}.png"
        if not png.exists():
            print(f"缺页：{png}")
            continue
        print(f"\n========== 第 {pno} 页（{png.name}） ==========")
        if args.engine in ("rapid", "both"):
            dt, rows = bench_rapid(png)
            print(f"--- RapidOCR  用时 {dt:.2f}s，{len(rows)} 行（前 12 行）")
            for y, t, s in rows[:12]:
                print(f"  y={y:6.1f} {t[:46]}")
        if args.engine in ("win", "both"):
            dt, rows = bench_windows(png)
            print(f"--- Windows  用时 {dt:.2f}s，{len(rows)} 行（前 12 行）")
            for y, t, s in rows[:12]:
                print(f"  y={y:6.1f} {t[:46]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())