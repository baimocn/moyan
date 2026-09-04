"""数据访问层（domain models + 数据库基座）"""
from .documents import Document
from .tasks import Task
from .study import Judgement, StrategyLog, TeachingSession, Turn, Weakness
from .usage import AiUsage, PageView
from .vec import DocumentChunk
from .db import Base, SessionLocal, engine, get_db, init_db

__all__ = [
    "Document", "Task", "TeachingSession", "Turn", "Judgement", "Weakness",
    "StrategyLog", "AiUsage", "PageView", "DocumentChunk",
    "Base", "SessionLocal", "engine", "get_db", "init_db",
]