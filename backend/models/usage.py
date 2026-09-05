"""用量观测模型（Phase 3，2026-09-04）：AI 调用台账 + 页面浏览明细"""
from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base, BigIntPK, DateTime, _tznow


class AiUsage(Base):
    """AI 调用统一台账：每次真实引擎调用记一行（fire-and-forget，失败不影响主流程）。

    - 教学轮（讲解流+判定+出题）在 tutor_turn scope 内逐次记账，与 turns.usage 明细并存；
    - proofread / moderation / reviewer 等后台调用经 ai_scope 标注 endpoint；
    - 重试/failover 每次真实调用各记一行（如实反映消耗）。
    """
    __tablename__ = "ai_usage"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime(timezone=True), default=_tznow, index=True)
    endpoint: Mapped[str] = mapped_column(String(32), default="misc", index=True)
    engine: Mapped[str] = mapped_column(String(32), default="")
    model: Mapped[str] = mapped_column(String(64), default="")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated: Mapped[bool] = mapped_column(Boolean, default=False)  # 流中断估算兜底
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    doc_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(40), nullable=True)


class PageView(Base):
    """页面浏览明细（STATS-01，双前端共用，有人点进来就算）。"""
    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime(timezone=True), default=_tznow, index=True)
    source: Mapped[str] = mapped_column(String(8), default="web")   # web | mp
    page: Mapped[str] = mapped_column(String(64), default="")
    device_id: Mapped[str] = mapped_column(String(64), default="anon", index=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
