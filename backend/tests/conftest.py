"""pytest 公共夹具：测试库独立 SQLite + 建表（不污染开发库）"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# 在 import backend 前指定测试库（独立文件）
os.environ.setdefault(
    "MOYAN_DB_URL",
    f"sqlite:///{(Path(__file__).resolve().parent / 'test_dev.db').as_posix()}",
)

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _db_ready():
    from backend.models import init_db
    init_db()
    yield