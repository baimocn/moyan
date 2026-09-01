"""墨衍 · 本地文件存储与文档清单

数据布局（data/ 目录，已 gitignore）：
    data/uploads/{doc_id}/{原文件名}     原始上传
    data/markdown/{doc_id}.md            转换后的 Markdown（原原本本）
    data/chapters/{doc_id}/chapter_XXX.md 章节切片
    data/chapters/{doc_id}/chapters.json   章节清单（含 toc）
    data/documents.json                    全库文档索引（清单）
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

from . import config
from .services.chapter_splitter import Chapter

_SAFE_NAME_RE = re.compile(r"[^\w.\-\u4e00-\u9fff]+")


def _safe_name(name: str) -> str:
    return _SAFE_NAME_RE.sub("_", name).strip("_") or "file"


def new_doc_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]


def save_upload(doc_id: str, file_storage) -> Path:
    """保存上传的原始文件，返回落盘路径（同时兼容 Flask 的 FileStorage 与 FastAPI 的 UploadFile）。"""
    safe = _safe_name(getattr(file_storage, "filename", None) or "upload")
    dest_dir = config.UPLOAD_DIR / doc_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / safe
    try:
        file_storage.save(dest)  # Flask 风格
    except AttributeError:
        import shutil
        with dest.open("wb") as f:
            shutil.copyfileobj(file_storage.file, f)  # FastAPI 风格
    return dest


def save_markdown(doc_id: str, markdown: str) -> Path:
    config.ensure_dirs()
    dest = config.MARKDOWN_DIR / f"{doc_id}.md"
    dest.write_text(markdown or "", encoding="utf-8")
    return dest


def save_chapters(doc_id: str, chapters: list[Chapter]) -> Path:
    """章节切片落盘：每章一个 md + 一个 chapters.json 清单（先清空旧产物）。"""
    config.ensure_dirs()
    dir_ = config.CHAPTERS_DIR / doc_id
    if dir_.exists():
        for old in dir_.glob("*"):
            if old.is_file():
                old.unlink()
    dir_.mkdir(parents=True, exist_ok=True)
    manifest = []
    for ch in chapters:
        name = f"chapter_{ch.index:03d}.md"
        (dir_ / name).write_text(ch.markdown or "", encoding="utf-8")
        manifest.append({
            "index": ch.index,
            "title": ch.title,
            "level": ch.level,
            "char_count": ch.char_count,
            "file": name,
            "toc": [{"level": t.level, "title": t.title} for t in ch.toc],
        })
    (dir_ / "chapters.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return dir_


def add_document(record: dict) -> None:
    """（已废弃，保留兼容：旧 JSON 清单时代的注册入口，新逻辑走 DB documents 表。）"""
    return None


def list_documents() -> list[dict]:
    """（已废弃：新逻辑走 DB documents 表。）"""
    return []


def get_document(doc_id: str) -> dict | None:
    """（已废弃。）"""
    return None


def get_markdown(doc_id: str) -> str | None:
    p = config.MARKDOWN_DIR / f"{doc_id}.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


def get_chapter_manifest(doc_id: str) -> list[dict] | None:
    p = config.CHAPTERS_DIR / doc_id / "chapters.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def get_chapter(doc_id: str, index: int) -> dict | None:
    manifest = get_chapter_manifest(doc_id)
    if not manifest:
        return None
    for item in manifest:
        if item["index"] == index:
            p = config.CHAPTERS_DIR / doc_id / item["file"]
            item = dict(item)
            item["markdown"] = p.read_text(encoding="utf-8") if p.exists() else ""
            return item
    return None


# ---------- 章内知识点计划缓存（真实引擎验证：plan 生成 ~80s，只该每章一次） ----------

def _plan_path(doc_id: str, chapter_index: int) -> Path:
    return config.CHAPTERS_DIR / doc_id / f"plan_{chapter_index}.json"


def save_learning_plan(doc_id: str, chapter_index: int, kps: list[dict]) -> None:
    """缓存 LLM 生成的知识点计划（kps=[{id,name,summary,skill_id}]）。"""
    p = _plan_path(doc_id, chapter_index)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(kps, ensure_ascii=False), encoding="utf-8")


def load_learning_plan(doc_id: str, chapter_index: int) -> list[dict] | None:
    p = _plan_path(doc_id, chapter_index)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else None
    except Exception:
        return None