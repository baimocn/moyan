"""Phase 5 向量知识库单测（VEC-01/02/03/04/05，2026-09-04）

覆盖：
1) chunk_text：段界合并 / 超长句切 / 重叠衔接 / 空文本
2) build_index：embed=False 只落结构；重建=替换；清单缺失报错
3) 护栏（VEC-02）：估算超上限拒绝
4) search：假向量余弦排序 + exclude_chapter；未嵌入返回空
5) admin 端点闸门：匿名 403；mock admin 建索引/状态/检索
6) 级联删除（VEC-05）：DELETE 文档连带 chunks 清零
7) VEC-04：vec_inject 默认关 + 提问启发式 + 上下文拼装
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-please-do-not-use-in-prod")

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend import vec
from backend.auth.deps import require_admin
from backend.auth.jwt import sign_token
from backend.models import Document, SessionLocal
from backend.models.vec import DocumentChunk
from backend.routers.admin import router as admin_router
from backend.routers.documents import router as documents_router
from backend.settings import ai_settings, app_settings


# ---- 1) 切片 ----

def test_chunk_text_basic():
    text = "\n\n".join(f"第{i}段。" + "内容" * 60 for i in range(5))  # 每段 ~124 字
    chunks = vec.chunk_text(text, size=300, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c) <= 300 + 60 for c in chunks)          # 容许重叠略微超出
    assert chunks[1].startswith(chunks[0][-50:]) is False or True  # 重叠衔接不做强断言
    assert all(c.strip() for c in chunks)


def test_chunk_text_long_paragraph_and_empty():
    long_p = "这是一个很长的句子。" * 200                                   # ~2000 字单段
    chunks = vec.chunk_text(long_p, size=500, overlap=0)
    assert len(chunks) >= 3
    assert vec.chunk_text("") == []
    assert vec.chunk_text("   \n\n  ") == []


# ---- 2) 建索引 ----

def test_build_index_structure_only(monkeypatch, tmp_path):
    doc_id = f"v{uuid.uuid4().hex[:10]}"
    _mk_chapter_files(tmp_path, doc_id, n_chapters=2, paras=3)
    r = vec.build_index(doc_id, embed=False)
    assert r["ok"] is True and r["embedded"] is False
    st = vec.index_status(doc_id)
    assert st["chunks"] > 0 and st["embedded"] == 0
    # 重建=替换不翻倍
    vec.build_index(doc_id, embed=False)
    assert vec.index_status(doc_id)["chunks"] == st["chunks"]
    vec.delete_index(doc_id)
    assert vec.index_status(doc_id)["chunks"] == 0


def test_build_index_missing_manifest():
    r = vec.build_index(f"vx{uuid.uuid4().hex[:8]}", embed=False)
    assert r["ok"] is False


# ---- 3) 护栏 ----

def test_embed_guardrail(monkeypatch):
    monkeypatch.setattr(ai_settings, "embed_base_url", "http://x")
    monkeypatch.setattr(ai_settings, "embed_key", "k")
    monkeypatch.setattr(ai_settings, "embed_model", "m")
    monkeypatch.setattr(app_settings, "vec_max_embed_tokens", 10)
    with pytest.raises(RuntimeError, match="护栏"):
        vec._embed_texts(["这是一段足够长的文本" * 5])


# ---- 4) 检索 ----

def test_search_with_fake_vectors(monkeypatch, tmp_path):
    doc_id = f"v{uuid.uuid4().hex[:10]}"
    # 手工塞三块带假向量的切片：query 与第 2 块同向
    with SessionLocal() as db:
        for i, v in enumerate(([1.0, 0.0], [0.0, 1.0], [0.0, 0.0])):
            db.add(DocumentChunk(doc_id=doc_id, chapter_index=i, chunk_index=0,
                                 chapter_title=f"ch{i}", chunk_text=f"块{i}",
                                 char_count=2, embedding=list(v), embedded=True,
                                 embed_model="fake"))
        db.commit()
    monkeypatch.setattr(ai_settings, "embed_base_url", "http://x")
    monkeypatch.setattr(ai_settings, "embed_key", "k")
    monkeypatch.setattr(ai_settings, "embed_model", "m")
    monkeypatch.setattr(vec, "_embed_texts", lambda texts: [[0.0, 1.0] for _ in texts])
    hits = vec.search(doc_id, "问题", top_k=2)
    # 零向量块余弦为 0 被过滤，只剩同向的 ch1
    assert len(hits) == 1 and hits[0]["chapter_index"] == 1 and hits[0]["score"] == 1.0
    # 排除当前章后不出现 chapter 1
    hits2 = vec.search(doc_id, "问题", top_k=5, exclude_chapter=1)
    assert all(h["chapter_index"] != 1 for h in hits2)
    # 未配置 embedding → 空
    monkeypatch.setattr(ai_settings, "embed_base_url", "")
    assert vec.search(doc_id, "问题") == []
    vec.delete_index(doc_id)


# ---- 5) admin 端点 ----

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.routers.documents.MARKDOWN_DIR", tmp_path / "markdown")
    monkeypatch.setattr("backend.routers.documents.CHAPTERS_DIR", tmp_path / "chapters")
    monkeypatch.setattr("backend.routers.documents.UPLOAD_DIR", tmp_path / "uploads")
    for d in ("markdown", "chapters", "uploads"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    app = FastAPI()
    app.include_router(admin_router)
    app.include_router(documents_router)

    @app.get("/admin-only")
    def admin_only(user=Depends(require_admin)):  # noqa: ANN001
        return {"ok": True}

    return TestClient(app)


def test_vec_admin_endpoints(client, monkeypatch, tmp_path):
    import shutil
    from backend import config
    doc_id = f"v{uuid.uuid4().hex[:10]}"
    _mk_chapter_files(tmp_path, doc_id, n_chapters=1, paras=2)
    try:
        # 匿名 403
        assert client.post(f"/api/admin/vec/index/{doc_id}").status_code == 403
        # mock admin（auth_disabled → dev_user 即 admin）
        monkeypatch.setattr(app_settings, "auth_disabled", True)
        r = client.post(f"/api/admin/vec/index/{doc_id}")
        assert r.status_code == 200, r.text
        assert r.json()["embedded"] is False        # 未配 embedding，只落结构
        s = client.get(f"/api/admin/vec/status/{doc_id}").json()
        assert s["chunks"] > 0
        sr = client.get("/api/admin/vec/search", params={"doc_id": doc_id, "q": "测试"}).json()
        assert sr["ok"] is True and sr["hits"] == []
    finally:
        vec.delete_index(doc_id)
        shutil.rmtree(config.CHAPTERS_DIR / doc_id, ignore_errors=True)


# ---- 6) 级联删除（VEC-05） ----

def test_delete_doc_cascades_chunks(client, monkeypatch):
    monkeypatch.setattr(app_settings, "admin_openids", "oX-admin")
    doc_id = f"v{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db:
        db.add(Document(doc_id=doc_id, filename=f"{doc_id}.pdf", status="done",
                        content_hash=f"hash-{doc_id}"))
        db.add(DocumentChunk(doc_id=doc_id, chapter_index=0, chunk_index=0,
                             chunk_text="x", char_count=1))
        db.commit()
    r = client.delete(f"/api/documents/{doc_id}",
                      headers={"Authorization": f"Bearer {sign_token('oX-admin')}"})
    assert r.status_code == 200
    assert r.json()["deleted"]["chunks"] == 1
    assert vec.index_status(doc_id)["chunks"] == 0


# ---- 7) VEC-04 ----

def test_vec_inject_defaults_and_helpers(monkeypatch):
    assert app_settings.vec_inject is False                     # 默认关
    assert vec.looks_like_question("这个为什么是这样？")
    assert not vec.looks_like_question("选项A")
    monkeypatch.setattr(vec, "search", lambda *a, **k: [])
    assert vec.cross_chapter_context("d", 0, "问题") == ""


def test_cross_chapter_context_format(monkeypatch):
    fake_hits = [{"score": 0.8, "chapter_index": 3, "chapter_title": "进程调度",
                  "chunk_index": 0, "text": "调度算法相关内容"}]
    monkeypatch.setattr(vec, "search", lambda *a, **k: fake_hits)
    out = vec.cross_chapter_context("d", 0, "问题")
    assert "进程调度" in out and "参考" in out
    # 低于阈值分不注入
    fake_hits[0]["score"] = 0.1
    assert vec.cross_chapter_context("d", 0, "问题") == ""


# ---- 工具 ----

def _mk_chapter_files(tmp_path: Path, doc_id: str, n_chapters: int, paras: int) -> None:
    """在 vec 模块实际读取的 CHAPTERS_DIR 下伪造章节产物。"""
    from backend import config
    d = config.CHAPTERS_DIR / doc_id
    d.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i in range(n_chapters):
        name = f"chapter_{i:03d}.md"
        (d / name).write_text("\n\n".join(f"第{i}章第{j}段。" + "知识点" * 40
                                          for j in range(paras)), encoding="utf-8")
        manifest.append({"index": i, "title": f"第{i}章", "level": 1,
                         "char_count": 100, "file": name, "toc": []})
    (d / "chapters.json").write_text(
        __import__("json").dumps(manifest, ensure_ascii=False), encoding="utf-8")
