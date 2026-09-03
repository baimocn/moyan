"""学习档案模型：教学会话 / 每轮 / 判定 / 薄弱点

粒度：以「文档 → 章节」为档案单元（单用户阶段）；未来接用户系统时加 user_id 维。
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base, DateTime, _tznow


def _nid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class TeachingSession(Base):
    """一次章节导航式教学会话（可恢复续学）。"""
    __tablename__ = "teaching_sessions"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)   # s_xxx
    # 鉴权落档（2026-09-02）：openid。NULL = 鉴权前老数据 / 游客模式
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    doc_id: Mapped[str] = mapped_column(String(40), ForeignKey("documents.doc_id"), index=True)
    chapter_index: Mapped[int] = mapped_column(Integer, default=0)
    chapter_title: Mapped[str] = mapped_column(String(200), default="")
    state: Mapped[str] = mapped_column(String(16), default="explain")
    kp_idx: Mapped[int] = mapped_column(Integer, default=0)
    hint_level: Mapped[int] = mapped_column(Integer, default=0)   # 脚手架阶梯 0-3（2026-08-29）
    plan: Mapped[list] = mapped_column(JSON, default=list)          # 知识点序列快照（续学用）
    weak: Mapped[dict] = mapped_column(JSON, default=dict)          # skill_id -> mastery
    current_question: Mapped[dict] = mapped_column(JSON, default=dict)  # 当前题目快照（续学恢复）
    exam_questions: Mapped[list] = mapped_column(JSON, default=list)    # 章末考题快照（2026-08-29 续学缺口）
    exam_idx: Mapped[int] = mapped_column(Integer, default=0)
    exam_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)
    updated_at = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)


class Turn(Base):
    """会话中的每一轮（讲解/提问/判定/学生回答），审计与回放用。"""
    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    # 鉴权落档（2026-09-02）：冗余存 openid，列表/统计走 user_id 走索引不走 JOIN session
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    session_id: Mapped[str] = mapped_column(String(40), ForeignKey("teaching_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(16), default="")       # user / assistant
    kind: Mapped[str] = mapped_column(String(16), default="")       # explain/question/answer/judge
    content: Mapped[str] = mapped_column(Text, default="")
    usage: Mapped[dict] = mapped_column(JSON, default=dict)         # token 用量（成本核算，见 AI 用量）
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)


class Judgement(Base):
    """每次判定全量审计（可复盘/校准 prompt）。"""
    __tablename__ = "judgements"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    # 鉴权落档（2026-09-02）：按用户隔离判定审计
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    session_id: Mapped[str] = mapped_column(String(40), ForeignKey("teaching_sessions.id"), index=True)
    question_id: Mapped[str] = mapped_column(String(120), default="")
    correctness: Mapped[str] = mapped_column(String(20), default="")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    decision: Mapped[str] = mapped_column(String(32), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)       # 判定 JSON 全量
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)


class Weakness(Base):
    """薄弱点档案（skill_id -> 掌握度），复习系统直接消费。

    复习调度（D4 修订：官方 py-fsrs，FSRS 现行模型）：fsrs_state/step/stability/
    difficulty/last_review 为完整卡片状态；due_at 即卡片到期时间；mastery 为产品级
    展示口径（again→low / hard|good→mid / easy→high）；interval_days 仅作展示换算。
    chapter_index/chapter_title 支撑"概念级→章节级"聚合（复习任务 = due ∩ 章节）。
    """
    __tablename__ = "weaknesses"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    doc_id: Mapped[str] = mapped_column(String(40), index=True)
    skill_id: Mapped[str] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(200), default="")      # 中文名（检索注入用）
    mastery: Mapped[str] = mapped_column(String(8), default="low")  # low/mid/high（展示口径）
    times_low: Mapped[int] = mapped_column(Integer, default=1)      # 被判弱的次数
    # ---- 概念→章节 聚合 ----
    chapter_index: Mapped[int] = mapped_column(Integer, default=-1, nullable=True)
    chapter_title: Mapped[str] = mapped_column(String(200), default="")
    # ---- FSRS 卡片（官方 py-fsrs） ----
    due_at = mapped_column(DateTime(timezone=True), default=_tznow, nullable=True)   # 卡片到期
    fsrs_state: Mapped[int] = mapped_column(Integer, default=1)     # 1=Learning 2=Review 3=Relearning
    fsrs_step: Mapped[int] = mapped_column(Integer, nullable=True)  # 学习步骤（Learning/Relearning 用）
    stability: Mapped[float] = mapped_column(Float, nullable=True)  # 记忆稳定性
    difficulty: Mapped[float] = mapped_column(Float, nullable=True) # 记忆难度（越难越高）
    last_review = mapped_column(DateTime(timezone=True), nullable=True)
    reps: Mapped[int] = mapped_column(Integer, default=0)           # 复习次数
    interval_days: Mapped[int] = mapped_column(Integer, default=0)  # 展示换算（due-last_review）
    lapses: Mapped[int] = mapped_column(Integer, default=0)         # 遗忘次数（rating=again 累计）
    ease: Mapped[float] = mapped_column(Float, default=2.5)         # 遗留（SM-2 时代字段，仅展示保留）
    last_seen_at = mapped_column(DateTime(timezone=True), default=_tznow)
    updated_at = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)


class StrategyLog(Base):
    """教学策略反馈日志（借鉴 synapse Groove：哪个讲法/策略对哪个知识点有效）。

    每轮判定落一条：strategy=本次分支（skip/reteach/alternative_explanation/practice_question/
    exam 等）；effect=本次判定分数（0~1）；review_passed=输出后裁判是否通过。
    由 strategy_stats 聚合 → 数据驱动"下次讲解方式"（Tracer 记忆复用）。
    """
    __tablename__ = "strategy_logs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(40), index=True)
    skill_id: Mapped[str] = mapped_column(String(120), index=True)
    strategy: Mapped[str] = mapped_column(String(32), default="")
    effect: Mapped[float] = mapped_column(Float, default=0.0)        # 判定分数（短程效果）
    review_passed: Mapped[bool] = mapped_column(default=True)        # 裁判是否通过
    session_id: Mapped[str] = mapped_column(String(40), default="")
    user_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)


class UserProfile(Base):
    """用户档案（鉴权后落档，2026-09-02 部署前置）。

    user_id 形如 openid（开发期为 dev_xxx / wx_dev_user 等）。
    关键查询：按 user_id 拿 sessions/turns/judgements 计数（me 接口）。

    2026-09-03 网页版：auth_type 区分 wx | web；email/password_hash 仅网页用户有值。
    """
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    auth_type: Mapped[str] = mapped_column(String(16), default="wx")   # wx | web
    email: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nick_name: Mapped[str] = mapped_column(String(64), default="")
    avatar_url: Mapped[str] = mapped_column(String(512), default="")
    created_at = mapped_column(DateTime(timezone=True), default=_tznow)
    last_active = mapped_column(DateTime(timezone=True), default=_tznow, onupdate=_tznow)