import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Desktop\墨衍-项目")
from backend.services import ocr_engine

work = Path(r"D:\Desktop\墨衍-项目\data\work\qlsb150")
merged = []
for f in sorted(work.glob("chunk_*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip():
            merged.append(json.loads(line))
merged.sort(key=lambda r: (r["page"], r["y0"]))
out = work / "ocr_lines.json"
out.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")

pages = sorted({r["page"] for r in merged})
missing = [p for p in range(1, 467) if p not in pages]
print(f"总行数 {len(merged)}，覆盖页数 {len(pages)}/466，缺失页: {missing[:10]}")

rows, last = ocr_engine.load_ocr_lines(out)
print(f"load 校验: {len(rows)} 行，末页 {last}")
# 抽查质量：第三章附近页 p105 应该出现\"营养\"
samp = [r for r in rows if r["page"] == 105][:6]
for r in samp:
    print(f"  p105 {r['text'][:50]}")