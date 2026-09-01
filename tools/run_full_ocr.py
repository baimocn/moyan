"""临时统筹：对指定 work 目录跑全本 RapidOCR（分块子进程）"""
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Desktop\墨衍-项目")
from backend.services import ocr_engine

work = Path(sys.argv[1])
workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
ocr_engine.run_rapid_ocr(work / "pngs", work / "ocr_lines.json", workers=workers)
print("DONE")