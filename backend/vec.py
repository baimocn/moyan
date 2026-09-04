"""墨衍 · 向量知识库（Phase 5 VEC-01/02/03，2026-09-04）

能力：教材切片 → embedding（可选）→ 余弦检索 → 跨章参考上下文。

成本与降级原则（用户成本敏感）：
- 建索引只由管理员显式触发（POST /api/admin/vec/index/{doc_id}），上传不自动烧钱；
- 未配 MOYAN_AI_EMBED_* 时优雅降级：切片照落库（embedding=None），检索返回空；
- 护栏（VEC-02）：单本 embedding token 估算超 settings.vec_max_embed_tokens 拒绝执行；
- embedding 调用如实记入 ai_usage 台账（endpoint=embedding）。

MVP 存储：向量 JSON 列 + Python 余弦（库规模小，毫秒级）；pgvector 上量后再迁。
"""
from __future__ import annotations

import logging
import math
import re

from sqlalchemy import select

from . import storage
from .models import DocumentChunk, SessionLocal
from .settings import ai_settings, app_settings

log = logging.getLogger("moyan.vec")

# 切片参数：约 500 字/块，80 字重叠（衔接语义），段界优先
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
_EMBED_BATCH = 16


# ---------- 切片 ----------

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """段界优先切分：段落自然合并到 ~size；单段超长再按句硬切。"""
    text = (text or "").strip()
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paras:
        paras = [p.strip() for p in text.splitlines() if p.strip()]

    # 单段超长：按句子再切
    pieces: list[str] = []
    for p in paras:
        if len(p) <= size:
            pieces.append(p)
            continue
        sents = re.split(r"(?<=[。！？!?；;.])\s*", p)
        buf = ""
        for s in sents:
            if buf and len(buf) + len(s) > size:
                pieces.append(buf)
                buf = s
            else:
                buf += s
        if buf:
            pieces.append(buf)

    # 合并到块（带重叠：块首带上块尾 overlap 字符，保证语义衔接）
    chunks: list[str] = []
    buf = ""
    for piece in pieces:
        if buf and len(buf) + len(piece) + 1 > size:
            chunks.append(buf)
            tail = buf[-overlap:] if overlap > 0 else ""
            buf = (tail + piece) if len(tail) + len(piece) <= size + overlap else piece
        else:
            buf = f"{buf}\n{piece}" if buf else piece
    if buf:
        chunks.append(buf)
    return chunks


# ---------- embedding（OpenAI 兼容 /embeddings） ----------

def embed_ready() -> bool:
    return ai_settings.embed_ready


def _sync_embed_client():
    from openai import OpenAI
    return OpenAI(base_url=ai_settings.embed_base_url,
                  api_key=ai_settings.embed_key, timeout=120.0, max_retries=1)


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """批量嵌入。护栏：估算 token 超上限直接抛错（VEC-02），绝不悄悄烧钱。"""
    est = sum(len(t) for t in texts)
    cap = app_settings.vec_max_embed_tokens
    if est > cap:
        raise RuntimeError(f"embedding 护栏触发：估算 {est} tokens > 上限 {cap}（VEC-02），已拒绝")
    client = _sync_embed_client()
    out: list[list[float]] = []
    total_usage = {"prompt_tokens": 0, "total_tokens": 0}
    for i in range(0, len(texts), _EMBED_BATCH):
        batch = [t[:6000] for t in texts[i:i + _EMBED_BATCH]]   # 单条硬上限防异常长块
        resp = client.embeddings.create(model=ai_settings.embed_model, input=batch)
        out.extend(d.embedding for d in resp.data)
        u = getattr(resp, "usage", None)
        if u is not None:
            total_usage["prompt_tokens"] += int(getattr(u, "prompt_tokens", 0) or 0)
            total_usage["total_tokens"] += int(getattr(u, "total_tokens", 0) or 0)
    # embedding 消耗如实入台账（endpoint=embedding；doc_id 上下文由调用方 scope 标注）
    if total_usage["total_tokens"]:
        try:
            from .ledger import record
            record("embedding", ai_settings.embed_model, dict(total_usage),
                   endpoint="embedding")
        except Exception:  # noqa: BLE001
            pass
    return out


# ---------- 建索引（管理员触发） ----------

def build_index(doc_id: str, *, embed: bool | None = None) -> dict:
    """为教材全章切片并（可选）嵌入入库。重复调用=重建（先清旧块）。

    embed=None 时按 embed_ready() 自动决定；显式 False 可只落结构不花钱。
    """
    manifest = storage.get_chapter_manifest(doc_id)
    if not manifest:
        return {"ok": False, "error": "章节清单不存在（文档未完成解析？）"}
    do_embed = embed_ready() if embed is None else (embed and embed_ready())
    if embed and not embed_ready():
        return {"ok": False, "error": "未配置 MOYAN_AI_EMBED_*，无法嵌入（可 embed=False 只落切片）"}

    rows: list[dict] = []
    for ch in manifest:
        from .config import CHAPTERS_DIR
        p = CHAPTERS_DIR / doc_id / ch["file"]
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for ci, chunk in enumerate(chunk_text(text)):
            rows.append({
                "doc_id": doc_id, "chapter_index": ch["index"],
                "chunk_index": ci, "chapter_title": ch.get("title", ""),
                "chunk_text": chunk, "char_count": len(chunk),
            })
    if not rows:
        return {"ok": False, "error": "无可用章节内容"}

    vectors: list[list[float]] | None = None
    if do_embed:
        vectors = _embed_texts([r["chunk_text"] for r in rows])

    with SessionLocal() as db:
        db.query(DocumentChunk).filter(DocumentChunk.doc_id == doc_id) \
            .delete(synchronize_session=False)
        for i, r in enumerate(rows):
            db.add(DocumentChunk(
                **r,
                embedding=vectors[i] if vectors else None,
                embed_model=ai_settings.embed_model if vectors else "",
            ))
        db.commit()
    log.info("vec index built: doc=%s chunks=%s embedded=%s", doc_id, len(rows), bool(vectors))
    return {"ok": True, "doc_id": doc_id, "chunks": len(rows), "embedded": bool(vectors)}


def delete_index(doc_id: str) -> int:
    with SessionLocal() as db:
        n = db.query(DocumentChunk).filter(DocumentChunk.doc_id == doc_id) \
            .delete(synchronize_session=False)
        db.commit()
    return n


def index_status(doc_id: str) -> dict:
    with SessionLocal() as db:
        total = db.query(DocumentChunk).filter(DocumentChunk.doc_id == doc_id).count()
        embedded = db.query(DocumentChunk).filter(
            DocumentChunk.doc_id == doc_id, DocumentChunk.embedded.is_(True)).count()
    return {"doc_id": doc_id, "chunks": total, "embedded": embedded}


# ---------- 检索（VEC-03） ----------

def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / math.sqrt(na * nb)


def search(doc_id: str, query: str, top_k: int = 4,
           exclude_chapter: int | None = None) -> list[dict]:
    """余弦 top-k。未嵌入/未配置 → 空列表（调用方自行降级）。"""
    if not (query or "").strip() or not embed_ready():
        return []
    with SessionLocal() as db:
        q = (db.query(DocumentChunk)
             .filter(DocumentChunk.doc_id == doc_id,
                     DocumentChunk.embedded.is_(True)))
        if exclude_chapter is not None:
            q = q.filter(DocumentChunk.chapter_index != exclude_chapter)
        rows = q.all()
    if not rows:
        return []
    qvec = _embed_texts([query])[0]
    scored = sorted(
        (( _cosine(qvec, r.embedding), r) for r in rows),
        key=lambda t: t[0], reverse=True)[:max(1, int(top_k))]
    return [{
        "score": round(s, 4), "chapter_index": r.chapter_index,
        "chapter_title": r.chapter_title, "chunk_index": r.chunk_index,
        "text": r.chunk_text,
    } for s, r in scored if s > 0]


def cross_chapter_context(doc_id: str, chapter_index: int, query: str,
                          top_k: int = 2, min_score: float = 0.35) -> str:
    """教学注入用（VEC-04）：跨章参考片段拼为一段上下文；无命中返回空串。"""
    try:
        hits = search(doc_id, query, top_k=top_k, exclude_chapter=chapter_index)
    except Exception as exc:  # noqa: BLE001 检索失败绝不阻断教学
        log.warning("跨章检索失败（忽略）：%s", exc)
        return ""
    parts = [h for h in hits if h["score"] >= min_score]
    if not parts:
        return ""
    blocks = []
    for h in parts:
        title = h["chapter_title"] or f"第{h['chapter_index']}章"
        blocks.append(f"【{title}】{h['text'][:300]}")
    return "以下是本书其他章节中可能与学生问题相关的原文片段（仅作参考，不要据此改判答案对错）：\n" \
        + "\n---\n".join(blocks)


# 疑似提问启发式（VEC-04 gate）：答案里夹带提问时才值得跨章检索，省 token
_QUESTION_RE = re.compile(r"[？?]|为什么|怎么回事|怎么办|是什么意思|如何|请问|能不能讲|帮我讲")


def looks_like_question(text: str) -> bool:
    return bool(_QUESTION_RE.search(text or ""))
