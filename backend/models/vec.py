"""向量知识库模型（Phase 5 VEC-01，2026-09-04）：文档切片 + 嵌入

MVP 决策：embedding 以 JSON 列存（SQLite/PG 通用），检索 Python 侧余弦——
当前库规模（个位数教材 × 数百块）毫秒级够用；语料上量后再迁 pgvector。
"""
from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .db import Base, DateTime, _tznow

# SQLite 用 JSON，PG 用 JSONB（same shape；编译期按方言选择会引入 import 复杂度，
# 这里用运行时探测：JSON 在 PG 上也完全可用，仅索引能力弱——检索不依赖该索引）
EmbeddingType = JSON().with_variant(JSONB(), "postgresql")


class DocumentChunk(Base):
    """教材切片：一章切多块，embedding 可空（未配 embedding 服务时先落结构）。

    embedded 布尔列冗余标记是否已嵌入：SQLite 方言下对 JSON 列做 IS NOT NULL
    过滤会把字面量 None 序列化成 JSON 'null' 参与比较导致全部命中（2026-09-04
    实测），显式布尔列在 SQLite/PG 上语义都可靠。
    """
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime(timezone=True), default=_tznow, index=True)
    doc_id: Mapped[str] = mapped_column(String(40), index=True)
    chapter_index: Mapped[int] = mapped_column(Integer, default=0)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    chapter_title: Mapped[str] = mapped_column(String(200), default="")
    chunk_text: Mapped[str] = mapped_column(Text, default="")
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding = mapped_column(EmbeddingType, nullable=True)   # list[float] | None
    embedded: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    embed_model: Mapped[str] = mapped_column(String(64), default="")
