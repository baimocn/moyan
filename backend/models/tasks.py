"""后台任务模型"""
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base, DateTime, _tznow


class Task(Base):
    """后台任务（主要是扫描件 OCR）。"""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(40), ForeignKey("documents.doc_id"))
    kind: Mapped[str] = mapped_column(String(16), default="ocr")
    status: Mapped[str] = mapped_column(String(16), default="queued")
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    done_pages: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    message: Mapped[str] = mapped_column(Text, default="")
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)
    updated_at = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)
    finished_at = mapped_column(DateTime(timezone=True), nullable=True)