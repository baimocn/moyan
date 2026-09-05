"""documents.shared 列（CMP-02 一键下架，M4 Phase 9）

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-05
"""
from __future__ import annotations

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return   # SQLite 走 create_all / _migrate_add_columns
    op.execute("ALTER TABLE documents "
               "ADD COLUMN IF NOT EXISTS shared BOOLEAN NOT NULL DEFAULT TRUE")


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS shared")
