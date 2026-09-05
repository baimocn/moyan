"""墨衍 alembic 环境（SCHEMA-06）：URL 与 metadata 全部来自 backend，单一事实源。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alembic import context  # noqa: E402

from backend.models.db import Base  # noqa: E402
from backend.settings import db_settings  # noqa: E402
import backend.models  # noqa: F401,E402  确保全部模型注册进 metadata

config = context.config

# 日志配置可选（ini 无 logging 段时跳过）
if config.config_file_name is not None:
    try:
        import logging
        import logging.config
        logging.config.fileConfig(config.config_file_name, disable_existing_loggers=False)
    except Exception:  # noqa: BLE001
        pass

# URL 注入（% 需转义供 configparser）
config.set_main_option("sqlalchemy.url", db_settings.db_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import engine_from_config, pool

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
