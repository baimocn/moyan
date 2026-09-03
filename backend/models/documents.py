"""文档模型"""
from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base, DateTime, _tznow


class Document(Base):
    """一份上传资料的解析结果索引。"""
    __tablename__ = "documents"

    doc_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    # 鉴权落档（2026-09-02 部署前置）：NULL = 鉴权前老数据 / 游客
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    # 共享书库去重（2026-09-03）：文件 sha256，同 hash 的 done 文档上传时直接复用
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    # 展示名（用户可改）；空串时回退 filename。2026-09-01 书籍自定义命名。
    title: Mapped[str] = mapped_column(String(255), default="")
    format: Mapped[str] = mapped_column(String(16), default="pdf")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(32), default="")
    md_chars: Mapped[int] = mapped_column(Integer, default=0)
    chapter_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="processing")
    headings: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    manifest: Mapped[list] = mapped_column(JSON, default=list)
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)
    updated_at = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)