"""schema_health：索引/唯一补齐 + bigint + jsonb + CHECK（SCHEMA-01..05，全部幂等）

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-05

生产路径：alembic stamp 0001（schema 已存在）→ alembic upgrade head（本迁移）。
本迁移仅面向 PostgreSQL；SQLite 开发库由 create_all 直达目标形态（stamp 0002 即可）。
"""
from __future__ import annotations

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

_STEPS = [
    # ---- SCHEMA-01 索引/唯一补齐（迁移路径曾丢索引）----
    "CREATE INDEX IF NOT EXISTS ix_documents_content_hash ON documents (content_hash)",
    "CREATE UNIQUE INDEX IF NOT EXISTS user_profiles_email_key ON user_profiles (email)",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_weaknesses_user_doc_skill "
    "ON weaknesses (user_id, doc_id, skill_id) WHERE user_id IS NOT NULL",
    # ---- SCHEMA-02 台账主键 bigint ----
    "ALTER SEQUENCE ai_usage_id_seq AS bigint",
    "ALTER TABLE ai_usage ALTER COLUMN id TYPE bigint",
    "ALTER SEQUENCE page_views_id_seq AS bigint",
    "ALTER TABLE page_views ALTER COLUMN id TYPE bigint",
    "ALTER SEQUENCE document_chunks_id_seq AS bigint",
    "ALTER TABLE document_chunks ALTER COLUMN id TYPE bigint",
    # ---- SCHEMA-03 json -> jsonb（可重入）----
    "ALTER TABLE documents ALTER COLUMN headings TYPE jsonb USING headings::jsonb",
    "ALTER TABLE documents ALTER COLUMN warnings TYPE jsonb USING warnings::jsonb",
    "ALTER TABLE documents ALTER COLUMN stats TYPE jsonb USING stats::jsonb",
    "ALTER TABLE documents ALTER COLUMN manifest TYPE jsonb USING manifest::jsonb",
    "ALTER TABLE turns ALTER COLUMN usage TYPE jsonb USING usage::jsonb",
    "ALTER TABLE judgements ALTER COLUMN payload TYPE jsonb USING payload::jsonb",
    "ALTER TABLE teaching_sessions ALTER COLUMN plan TYPE jsonb USING plan::jsonb",
    "ALTER TABLE teaching_sessions ALTER COLUMN weak TYPE jsonb USING weak::jsonb",
    "ALTER TABLE teaching_sessions ALTER COLUMN current_question TYPE jsonb USING current_question::jsonb",
    "ALTER TABLE teaching_sessions ALTER COLUMN exam_questions TYPE jsonb USING exam_questions::jsonb",
    "ALTER TABLE teaching_sessions ALTER COLUMN exam_scores TYPE jsonb USING exam_scores::jsonb",
]

_CHECKS = [
    ("documents", "ck_documents_status",
     "status IN ('done','processing','failed','rejected')"),
    ("teaching_sessions", "ck_sessions_state",
     "state IN ('init','explain','question','await_answer','evaluate','chapter_exam','done')"),
    ("turns", "ck_turns_role", "role IN ('user','assistant')"),
    ("weaknesses", "ck_weaknesses_mastery", "mastery IN ('low','mid','high')"),
    ("weaknesses", "ck_weaknesses_fsrs_state", "fsrs_state BETWEEN 1 AND 3"),
    ("user_profiles", "ck_user_profiles_auth_type", "auth_type IN ('wx','web')"),
]


def _add_check_sql(table: str, name: str, cond: str) -> str:
    return (
        "DO $$ BEGIN\n"
        f"  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{name}') THEN\n"
        f"    ALTER TABLE {table} ADD CONSTRAINT {name} CHECK ({cond});\n"
        "  END IF;\n"
        "END $$;"
    )


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return   # SQLite 开发库由 create_all 直达目标形态，走 stamp 不跑本迁移
    for stmt in _STEPS:
        op.execute(stmt)
    for table, name, cond in _CHECKS:
        op.execute(_add_check_sql(table, name, cond))


def downgrade() -> None:
    for table, name, _cond in reversed(_CHECKS):
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}")
