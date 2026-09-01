"""PP-Structure 精修 worker：单个 PDF 的逐页预测，逐页落 JSON 片段。

由 exam_ppstructure_md.py 以 subprocess 调用：段崩（无法 try/except 的原生崩溃）
只死本进程，主进程按缺失页自动降 dpi 重试。

用法：
  .ocr-venv/Scripts/python.exe tools/exam_pp_worker.py --pdf <pdf> \
      --work <png目录> --out <片段目录> [--dpi 200] [--only 1,2]
"""
import argparse
import faulthandler
import json
import os
import sys
import time
import warnings
from pathlib import Path

faulthandler.enable()
warnings.filterwarnings("ignore")
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "False")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "1")


def render_pngs(pdf: Path, work: Path, dpi: int) -> list[Path]:
    import pymupdf

    doc = pymupdf.open(str(pdf))
    mat = pymupdf.Matrix(dpi / 72, dpi / 72)
    d = work / str(dpi)
    d.mkdir(parents=True, exist_ok=True)
    pngs = []
    for i, page in enumerate(doc, 1):
        p = d / f"p{i:04d}.png"
        if not p.exists():
            page.get_pixmap(matrix=mat).save(str(p))
        pngs.append(p)
    doc.close()
    return pngs


def extract_blocks(rec) -> list[dict]:
    """parsing_res_list → 可 JSON 化的块列表。

    实测字段名是 label/content/bbox/index（2026-08-29 页1 片段验证），
    并非旧脚本假设的 block_label/block_content/block_order——那会全取空。
    """
    par = rec.get("parsing_res_list") or []
    blocks = []
    for i, b in enumerate(par):
        def get(k, d=None, _b=b):
            if hasattr(_b, "get"):
                v = _b.get(k, d)
            else:
                v = getattr(_b, k, d)
            return d if v is None else v
        bbox = get("bbox") or []
        blocks.append({
            "order": get("index", i),
            "bbox": [float(x) for x in bbox],
            "label": str(get("label", "") or ""),
            "content": str(get("content", "") or ""),
            "_repr": str(b)[:600] if i == 0 else "",
        })
    return blocks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--only", default="", help="逗号分隔 1-based 页号，空=全部")
    args = ap.parse_args()

    pdf, work, out = Path(args.pdf), Path(args.work), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    only = {int(x) for x in args.only.split(",") if x.strip()}

    pngs = render_pngs(pdf, work, args.dpi)
    todo = [i for i in range(1, len(pngs) + 1)
            if (not only or i in only)
            and not (out / f"page_{i:04d}.json").exists()]
    print(f"[worker] {pdf.name} dpi={args.dpi} pages={len(pngs)} todo={todo}",
          flush=True)
    if not todo:
        print("[worker] nothing to do", flush=True)
        return 0

    from paddleocr import PPStructureV3

    struct = PPStructureV3(use_doc_orientation_classify=False,
                           use_doc_unwarping=False,
                           use_textline_orientation=False, lang="ch")
    print(f"[worker] init done {time.strftime('%H:%M:%S')}", flush=True)

    t0 = time.time()
    for i in todo:
        t = time.time()
        res = struct.predict(input=str(pngs[i - 1]), use_table_recognition=True,
                             use_formula_recognition=True)
        rec = res[0]
        data = {
            "page": i,
            "dpi": args.dpi,
            "blocks": extract_blocks(rec),
            "tables": len(rec.get("table_res_list") or []),
            "formulas": len(rec.get("formula_res_list") or []),
            "secs": round(time.time() - t, 1),
        }
        fp = out / f"page_{i:04d}.json"
        fp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"[worker] page {i}: {data['secs']}s blocks={len(data['blocks'])} "
              f"tables={data['tables']} formulas={data['formulas']} -> {fp.name}",
              flush=True)
    print(f"[worker] ALL DONE {(time.time() - t0) / 60:.1f}min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
