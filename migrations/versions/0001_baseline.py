"""baseline：从零按当前模型重建等价 schema（棕地基线，生产 stamp 用）

Revision ID: 0001
Revises:
Create Date: 2026-09-05
"""
from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from backend.models.db import Base
    import backend.models  # noqa: F401 注册全部模型

    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    from backend.models.db import Base
    import backend.models  # noqa: F401

    Base.metadata.drop_all(bind=op.get_bind())
