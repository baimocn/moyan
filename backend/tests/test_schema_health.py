"""SCHEMA-01..06 回归锁（2026-09-05，Phase 08-01）

- PG 方言编译断言：bigint 主键 / JSONB / CHECK / 部分唯一索引
- CHECK 在 SQLite 侧真实生效（插坏值必须 IntegrityError）
- upsert_weakness 隔离：None 路径不跨用户抓行（SCHEMA-05 修复）
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import exc as sa_exc
from sqlalchemy.schema import CreateIndex, CreateTable
from sqlalchemy.dialects import postgresql

from backend.models import db as models_db
from backend.models import repo
from backend.models.usage import AiUsage, PageView
from backend.models.vec import DocumentChunk


def _ddl(table: str) -> str:
    return str(CreateTable(models_db.Base.metadata.tables[table]).compile(
        dialect=postgresql.dialect()))


def test_pg_dialect_bigint_ledger_pks():
    for t in ["ai_usage", "page_views", "document_chunks"]:
        ddl = _ddl(t)
        assert ("BIGSERIAL" in ddl) or ("BIGINT" in ddl), f"{t} 主键应为 bigint"


def test_pg_dialect_jsonb_columns():
    for t in ["documents", "teaching_sessions", "turns", "judgements"]:
        assert "JSONB" in _ddl(t), f"{t} 应含 JSONB 列"


def test_pg_dialect_check_constraints():
    ddl_sess = _ddl("teaching_sessions")
    assert "ck_sessions_state" in ddl_sess
    assert "ck_turns_role" in _ddl("turns")
    ddl_weak = _ddl("weaknesses")
    assert "ck_weaknesses_mastery" in ddl_weak
    assert "ck_weaknesses_fsrs_state" in ddl_weak
    assert "ck_user_profiles_auth_type" in _ddl("user_profiles")
    assert "ck_documents_status" in _ddl("documents")


def test_pg_dialect_weakness_unique_partial_index():
    tbl = models_db.Base.metadata.tables["weaknesses"]
    rendered = [str(CreateIndex(i).compile(dialect=postgresql.dialect()))
                for i in tbl.indexes]
    uq = [r for r in rendered if "uq_weaknesses_user_doc_skill" in r]
    assert uq and "WHERE user_id IS NOT NULL" in uq[0]


def test_sqlite_check_enforced(test_sessionlocal=None):
    """CHECK 约束在 SQLite 也要真实生效（测试库与开发库共用建表路径）。"""
    from backend.models.db import SessionLocal
    from backend.models.study import Weakness
    import uuid
    with SessionLocal() as db:
        db.add(Weakness(id=f"w_{uuid.uuid4().hex[:10]}", doc_id="doc-ck",
                        skill_id="s1", mastery="bad"))
        with pytest.raises(sa_exc.IntegrityError):
            db.commit()


def test_upsert_weakness_null_user_isolation():
    """SCHEMA-05：None 路径不得抓走实名用户的行。"""
    doc, skill = "doc-upsert-ck", "sk1"
    repo.upsert_weakness(doc, skill, "知识点", "low", user_id="web_userA")
    with_a = repo.list_weaknesses(doc)
    assert len([w for w in with_a if w["user_id"] == "web_userA"
                or w.get("user_id") == "web_userA"]) >= 1
    before = [w for w in with_a if w.get("skill_id") == skill]
    times_before = before[0]["times_low"] if before else None

    repo.upsert_weakness(doc, skill, "知识点", "mid", user_id=None)     # None 路径
    repo.upsert_weakness(doc, skill, "知识点", "low", user_id="web_userB")

    rows = [w for w in repo.list_weaknesses(doc) if w.get("skill_id") == skill]
    owners = sorted((r.get("user_id") or "NULL") for r in rows)
    assert owners == ["NULL", "web_userA", "web_userB"], owners
    a_row = next(r for r in rows if r.get("user_id") == "web_userA")
    assert a_row["times_low"] == times_before            # A 行未被 None/B 路径污染
