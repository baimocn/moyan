"""数据库基座：engine / session / Base / 建表（与具体模型分离）"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, create_engine, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.types import JSON


def _tznow() -> datetime:
    return datetime.now(timezone.utc)


# SCHEMA-03（2026-09-05）：PG 用 JSONB（可 GIN/可查询），SQLite 用 JSON——统一出口
JSONType = JSON().with_variant(JSONB(), "postgresql")
# SCHEMA-02（2026-09-05）：PG 用 BIGINT，SQLite 必须回退 INTEGER 才有 rowid 自增
BigIntPK = BigInteger().with_variant(Integer(), "sqlite")


class Base(DeclarativeBase):
    """所有模型继承此基类。"""


def _build_engine():
    # 统一配置入口：settings.db_settings（MOYAN_DB_URL 覆盖，默认本地 SQLite）
    from ..settings import db_settings
    url = db_settings.db_url
    if url.startswith("sqlite"):
        eng = create_engine(url, connect_args={"check_same_thread": False})
        # 并发写地基（2026-08-29）：WAL 允许读写并行，busy_timeout 防写锁立刻报错
        from sqlalchemy import event

        @event.listens_for(eng, "connect")
        def _sqlite_pragma(dbapi_conn, _record):  # noqa: ANN001
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.execute("PRAGMA busy_timeout=5000")
            cur.close()
        return eng
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """建表（幂等），并对旧库做轻量"加列"迁移（不删数据）。"""
    # noqa: F401 确保模型注册到 Base.metadata
    from . import documents, tasks, study  # noqa: F401

    Base.metadata.create_all(engine)
    _migrate_add_columns()


# 演进记录：表新增列（老库 ALTER TABLE ADD COLUMN，新库 create_all 已包含）
_TABLE_ADDITIONS: dict[str, dict[str, str]] = {
    "weaknesses": {
        "due_at": "DATETIME",
        "reps": "INTEGER DEFAULT 0",
        "interval_days": "INTEGER DEFAULT 0",
        "ease": "FLOAT DEFAULT 2.5",
        "lapses": "INTEGER DEFAULT 0",
        # FSRS 卡片 + 章节聚合（2026-08-27 FSRS-lite -> 官方 py-fsrs）
        "chapter_index": "INTEGER DEFAULT -1",
        "chapter_title": "VARCHAR(200) DEFAULT ''",
        "fsrs_state": "INTEGER DEFAULT 1",
        "fsrs_step": "INTEGER",
        "stability": "FLOAT",
        "difficulty": "FLOAT",
        "last_review": "DATETIME",
    },
    "turns": {"usage": "JSON"},
    # 书籍自定义命名（2026-09-01：title 展示名，空串回退 filename）
    "documents": {"title": "VARCHAR(255) DEFAULT ''"},
    # 脚手架阶梯（2026-08-29：hint_level 进状态机，fading 可续学）
    "teaching_sessions": {"hint_level": "INTEGER DEFAULT 0",
                          "exam_questions": "JSON",
                          "exam_idx": "INTEGER DEFAULT 0",
                          "exam_scores": "JSON",
                          # 鉴权落档（2026-09-02 部署前置）：user_id=openid。NULL=老数据/游客
                          "user_id": "VARCHAR(64)"},
    "turns": {"usage": "JSON",
              "user_id": "VARCHAR(64)"},
    # 书籍自定义命名（2026-09-01：title 展示名，空串回退 filename）
    # 鉴权落档（2026-09-02）：upload 时写入 user_id
    # 共享书库去重（2026-09-03）：文件 sha256
    "documents": {"title": "VARCHAR(255) DEFAULT ''",
                  "user_id": "VARCHAR(64)",
                  "content_hash": "VARCHAR(64)"},
    "judgements": {"user_id": "VARCHAR(64)"},
    "weaknesses": {"user_id": "VARCHAR(64)"},
    "strategy_logs": {"user_id": "VARCHAR(64)"},
    # 网页版邮箱密码登录（2026-09-03 网页版 MVP）：auth_type/email/password_hash
    "user_profiles": {
        "auth_type": "VARCHAR(16) DEFAULT 'wx'",
        "email": "VARCHAR(128)",
        "password_hash": "VARCHAR(255)",
    },
}


def _existing_columns(table: str) -> set[str]:
    dialect = engine.dialect.name
    with engine.connect() as conn:
        if dialect == "sqlite":
            rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            return {r[1] for r in rows}
        if dialect == "postgresql":
            rows = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = :t"), {"t": table}).fetchall()
            return {r[0] for r in rows}
    return set()


def _migrate_add_columns() -> None:
    dialect = engine.dialect.name
    with engine.begin() as conn:
        existing_cache: dict[str, set[str]] = {}
        for table, cols in _TABLE_ADDITIONS.items():
            existing = existing_cache.get(table)
            if existing is None:
                existing = _existing_columns(table)
                existing_cache[table] = existing
            for col, ddl in cols.items():
                if col in existing:
                    continue
                try:
                    conn.execute(text(
                        f"ALTER TABLE {table} ADD COLUMN {col} {ddl}"))
                    print(f"[db] 迁移：{table}.{col} 新增列")
                except Exception as exc:  # noqa: BLE001 单列失败不阻塞启动
                    print(f"[db] 迁移失败（忽略）：{table}.{col}: {exc}")


def get_db():
    """FastAPI 依赖：请求级 session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["Base", "engine", "SessionLocal", "init_db", "get_db", "DateTime", "_tznow", "JSONType", "BigIntPK"]