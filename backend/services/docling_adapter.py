"""墨衍 · Docling 解析适配层（主解析引擎）

本机约束：后端跑 Python 3.14，Docling 依赖（torch 等）无 3.14 轮子 →
在 `.docling-venv`（Python 3.13）内用独立子进程 + 文件通信（与 RapidOCR worker 同模式）。

职责：
- docling_available()：环境就绪判定
- preflight(path, ext)：低成本分类（md/txt 直读 | office 快件 | pdf文本层 | pdf扫描 | image）
- convert_sync() / convert_async()：子进程桥（同步等结果 / 后台线程执行）
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from .. import config

_DOCLING_CACHE: dict | None = None


def docling_venv_python() -> Path:
    return Path(config.DOCLING_VENV_PY)


def docling_available() -> bool:
    """venv 与 worker 脚本是否都就绪。"""
    global _DOCLING_CACHE
    if _DOCLING_CACHE is None:
        _DOCLING_CACHE = (
            docling_venv_python().exists() and config.DOCLING_WORKER.exists()
        )
    return _DOCLING_CACHE


def set_docling_available(flag: bool) -> None:
    """测试钩子：允许注入可用/不可用。"""
    global _DOCLING_CACHE
    _DOCLING_CACHE = bool(flag)


def _is_pdf_scanned(path: Path) -> bool:
    """低成本判断：PDF 有无文本层（无 → 扫描件，docling 自行 OCR）。"""
    try:
        import pymupdf as fitz
    except ImportError:  # pragma: no cover
        import fitz
    try:
        doc = fitz.open(str(path))
        n = doc.page_count
        total = sum(len(p.get_text("text") or "") for p in doc)
        doc.close()
        return total / max(1, n) < 50
    except Exception:
        return True


def preflight(path: Path, ext: str) -> dict:
    """上传分诊：决定同步直读 / 异步 docling / 快路径。"""
    size_mb = path.stat().st_size / 1024 / 1024
    if ext in (".md", ".txt"):
        return {"kind": "md", "sync": True}
    if ext in (".png", ".jpg", ".jpeg", ".tiff"):
        return {"kind": "image", "sync": False}
    if ext in (".docx", ".pptx", ".xlsx", ".html", ".epub"):
        # 办公格式 docling 直读很快（PPT 实测 ~0s）→ 小件同步
        return {"kind": "office", "sync": size_mb <= config.OFFICE_SYNC_MAX_MB}
    if ext == ".pdf":
        scanned = _is_pdf_scanned(path)
        return {"kind": "pdf-text" if not scanned else "pdf-scanned",
                "sync": False}   # PDF 一律异步（docling 布局模型 14-40s/页）
    return {"kind": "unknown", "sync": False}


def _clean_worker_env() -> dict:
    """docling 子进程环境：剥离沙箱/系统代理，强制离线读本地模型缓存。

    背景：docling 每次启动都会向 HuggingFace 校验/下载模型权重，若继承
    http(s)_proxy（如沙箱会话注入的本地代理）会经代理访问 → ProxyError:
    502 Bad Gateway，转换在 50s+ 后失败。模型权重已在本机缓存
    （~/.cache/huggingface/hub, docling-project/*），HF_HUB_OFFLINE=1
    直接纯离线加载最稳。仅影响 docling 解析子进程，不影响后端 AI 引擎联网。
    """
    env = dict(os.environ)
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY", "no_proxy", "NO_PROXY"):
        env.pop(k, None)
    env["HF_HUB_OFFLINE"] = "1"
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    return env


def _run_worker(src: Path, out_md: Path, out_json: Path, timeout_s: int = 3600) -> dict:
    """子进程执行 docling_worker；返回 meta。"""
    out_md.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(docling_venv_python()), str(config.DOCLING_WORKER),
        str(src), str(out_md), str(out_json),
    ]
    proc = subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_s,
        cwd=str(config.PROJECT_ROOT),
        env=_clean_worker_env(),
    )
    if out_json.exists():
        try:
            return json.loads(out_json.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"ok": False, "error": f"worker exit={proc.returncode}"}


def convert_sync(src: Path, work_dir: Path) -> dict:
    """同步转换（office/md 小件）：返回 {ok, markdown, page_count, ...}。"""
    out_md = work_dir / f"{src.stem}_docling.md"
    out_json = work_dir / f"{src.stem}_docling.json"
    meta = _run_worker(src, out_md, out_json)
    meta["markdown"] = out_md.read_text(encoding="utf-8") if out_md.exists() else ""
    return meta


def convert_async(src: Path, work_dir: Path, done_cb=None, timeout_s: int = 7200):
    """后台线程转换（pdf/image/大件）：完成回调带回 meta dict。"""
    out_md = work_dir / f"{src.stem}_docling.md"
    out_json = work_dir / f"{src.stem}_docling.json"

    def _job():
        meta = _run_worker(src, out_md, out_json, timeout_s=timeout_s)
        meta.setdefault("markdown", "")
        meta["markdown"] = out_md.read_text(encoding="utf-8") if out_md.exists() else ""
        if done_cb:
            done_cb(meta)
    t = threading.Thread(target=_job, name="docling-convert", daemon=True)
    t.start()
    return t