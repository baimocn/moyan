"""墨衍 · OCR 断点续跑：只补缺失页，合并回 ocr_lines.json

用法：python tools/resume_ocr.py <work目录> [workers]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config

WORKER = config.PROJECT_ROOT / "tools" / "rapid_ocr_worker.py"


def main() -> int:
    work = Path(sys.argv[1])
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    png_dir = work / "pngs"
    out_json = work / "ocr_lines.json"

    if not out_json.exists():
        print("没有既有产物，请先跑完整 OCR")
        return 1
    try:
        existing = json.loads(out_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        existing = [json.loads(l) for l in out_json.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not isinstance(existing, list):
        return 1
    have_pages = {r["page"] for r in existing}
    total = len(list(png_dir.glob("p*.png")))
    missing = sorted(p for p in range(1, total + 1) if p not in have_pages)
    print(f"已有 {len(have_pages)}/{total} 页，缺失 {len(missing)} 页")

    if not missing:
        print("无缺失，无需续跑")
        return 0

    chunks = [missing[i::workers] for i in range(workers)]
    chunks = [c for c in chunks if c]
    procs = []
    for i, chunk in enumerate(chunks):
        chunk_file = work / f"chunk_{i}.jsonl"
        cmd = [sys.executable, str(WORKER), str(png_dir), str(chunk_file), ",".join(map(str, chunk))]
        procs.append((subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), chunk_file))

    from backend.services import ocr_engine  # noqa: 复用合并逻辑入口
    for proc, _cf in procs:
        proc.wait()

    for _cf in [c for _, c in procs]:
        if _cf.exists():
            for line in _cf.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    existing.append(json.loads(line))
            _cf.unlink()
    existing.sort(key=lambda r: (r["page"], r["y0"]))
    out_json.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
    pages = {r["page"] for r in existing}
    print(f"合并完成：{len(existing)} 行，覆盖 {len(pages)}/{total} 页")
    return 0


if __name__ == "__main__":
    sys.exit(main())