"""墨衍 · 数据库层（PostgreSQL + SQLAlchemy）

起步即正餐：文档、任务、章节清单落 PG；文件本体仍存磁盘（data/）。
任务表支撑"上传→异步 OCR→轮询进度"的服务器模式。
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from . import config


def _tznow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Document(Base):
    """一份上传资料的解析结果索引。"""
    __tablename__ = "documents"

    doc_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    format: Mapped[str] = mapped_column(String(16), default="pdf")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(32), default="")      # text-layer | rapid-ocr | win-ocr
    md_chars: Mapped[int] = mapped_column(Integer, default=0)
    chapter_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="processing")  # processing|done|failed
    headings: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    manifest: Mapped[list] = mapped_column(JSON, default=list)       # 章节清单（含 toc）
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_tznow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)


class Task(Base):
    """后台任务（主要是扫描件 OCR）。"""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(40), ForeignKey("documents.doc_id"))
    kind: Mapped[str] = mapped_column(String(16), default="ocr")
    status: Mapped[str] = mapped_column(String(16), default="queued")  # queued|running|done|failed
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    done_pages: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[float] = mapped_column(Float, default=0.0)       # 0~1
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_tznow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# 引擎：本地开发默认 SQLite；服务器部署用环境变量 MOYAN_DB_URL 指到 PostgreSQL
_DB_URL = os.environ.get("MOYAN_DB_URL", config.DATABASE_URL)

if _DB_URL.startswith("sqlite"):
    # 本地垫底：允许 FastAPI 请求线程与后台 worker 线程共用连接
    engine = create_engine(_DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        _DB_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """建表（幂等）。"""
    Base.metadata.create_all(engine)


def get_db():
    """FastAPI 依赖：请求级 session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()