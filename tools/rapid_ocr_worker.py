"""墨衍 · RapidOCR 批量识别 worker（独立进程，文件通信）

用法：python rapid_ocr_worker.py <png目录> <输出.jsonl> <页号CSV>
输出：JSONL，每行 {"page","text","y0","height","rel_y","width","score"}
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# 多进程并行时限制每进程 ONNX 线程，避免超额订阅把机器拖死
# （RapidOCR 创建 SessionOptions 时不设 intra_op_num_threads，会默认吃满所有核）
INTRA_THREADS = int(os.environ.get("RAPID_OCR_WORKER_THREADS", "2"))


def _patch_onnx_threads() -> None:
    """RapidOCR 创建 SessionOptions 时不设 intra_op_num_threads（默认吃满所有核），
    多进程并行时互相争抢；这里替换 OrtInferSession.__init__，强制限制线程数。"""
    import onnxruntime as ort
    from onnxruntime import get_available_providers, get_device
    import rapidocr_onnxruntime.utils as u

    def limited_init(self, config):
        sess_opt = ort.SessionOptions()
        sess_opt.log_severity_level = 4
        sess_opt.enable_cpu_mem_arena = False
        sess_opt.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_opt.intra_op_num_threads = INTRA_THREADS  # ← 关键行

        cpu_ep = "CPUExecutionProvider"
        cpu_provider_options = {"arena_extend_strategy": "kSameAsRequested"}
        cuda_ep = "CUDAExecutionProvider"
        cuda_provider_options = {
            "device_id": 0,
            "arena_extend_strategy": "kNextPowerOfTwo",
            "cudnn_conv_algo_search": "EXHAUSTIVE",
            "do_copy_in_default_stream": True,
        }
        EP_list = []
        if config["use_cuda"] and get_device() == "GPU" and cuda_ep in get_available_providers():
            EP_list = [(cuda_ep, cuda_provider_options)]
        EP_list.append((cpu_ep, cpu_provider_options))

        self._verify_model(config["model_path"])
        self.session = ort.InferenceSession(
            config["model_path"], sess_options=sess_opt, providers=EP_list,
        )

    u.OrtInferSession.__init__ = limited_init


def _dim_png(path: str) -> tuple[int, int]:
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def main() -> int:
    png_dir = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    pages_csv = sys.argv[3]

    _patch_onnx_threads()
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()

    pages = [int(x) for x in pages_csv.split(",") if x]
    skipped = 0
    errs = 0
    with out_path.open("w", encoding="utf-8") as f:
        for i, page in enumerate(pages, 1):
            png = png_dir / f"p{page:04d}.png"
            if not png.exists():
                skipped += 1
                continue
            try:
                res, _ = engine(str(png))
            except Exception as exc:  # 单页容错，不让整块崩
                errs += 1
                print(f"[worker] 页 {page} 识别失败：{exc}", flush=True)
                continue
            w, h = _dim_png(str(png))
            rows = []
            for box, text, score in res or []:
                text = (text or "").strip()
                if not text:
                    continue
                xs = [pt[0] for pt in box]
                ys = [pt[1] for pt in box]
                y0 = min(ys)
                x0 = min(xs)
                rows.append({
                    "page": page,
                    "text": text,
                    "y0": round(y0, 1),
                    "height": round(max(ys) - y0, 1),
                    "rel_y": round(y0 / h, 4),
                    "width": round(max(xs) - x0, 1),
                    "score": round(float(score), 3),
                })
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()  # 每页落盘，避免缓冲导致"0 字节"假死
            if i % 20 == 0 or i == len(pages):
                print(f"[worker] {i}/{len(pages)}", flush=True)
    if skipped:
        print(f"[worker] 跳过 {skipped} 个不存在页面", flush=True)
    if errs:
        print(f"[worker] 失败 {errs} 页", flush=True)
    print(f"[worker] 完成 -> {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())