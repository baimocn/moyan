"""Phase 2 文档删除联级清理单测（DOC-01/02，2026-09-04）

覆盖：
1) admin 删除 → 200 + DB 全链无残留 + 文件产物清空 + 级联计数正确
2) 非 admin Bearer → 403；设备匿名 → 403
3) 重复删除 → 404；不存在 doc → 404
4) 删除后同 content_hash 可重建（去重不受污染）
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-please-do-not-use-in-prod")

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.auth.deps import require_admin
from backend.auth.jwt import sign_token
from backend.config import CHAPTERS_DIR, MARKDOWN_DIR, UPLOAD_DIR
from backend.models import Document, SessionLocal
from backend.models.study import Judgement, StrategyLog, TeachingSession, Turn, Weakness
from backend.models.tasks import Task
from backend.routers.documents import router as documents_router


@pytest.fixture()
def client(monkeypatch, tmp_path):
    # 文件产物重定向到临时目录，避免污染开发库 data/
    monkeypatch.setattr("backend.routers.documents.MARKDOWN_DIR", tmp_path / "markdown")
    monkeypatch.setattr("backend.routers.documents.CHAPTERS_DIR", tmp_path / "chapters")
    monkeypatch.setattr("backend.routers.documents.UPLOAD_DIR", tmp_path / "uploads")
    for d in ("markdown", "chapters", "uploads"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)

    app = FastAPI()
    app.include_router(documents_router)

    @app.get("/admin-only")
    def admin_only(user=Depends(require_admin)):  # noqa: ANN001
        return {"ok": True}

    return TestClient(app)


def _mk_doc(doc_id: str, tmp_files: dict[str, str] | None = None) -> None:
    with SessionLocal() as db:
        db.add(Document(doc_id=doc_id, filename=f"{doc_id}.pdf", status="done",
                        content_hash=f"hash-{doc_id}"))
        db.add(Task(id=f"task_{doc_id}", doc_id=doc_id, status="done"))
        sess = TeachingSession(id=f"s_{doc_id}", doc_id=doc_id, user_id="tester")
        db.add(sess)
        db.flush()
        db.add(Turn(id=f"t1_{doc_id}", session_id=sess.id, role="assistant", content="x"))
        db.add(Judgement(id=f"j1_{doc_id}", session_id=sess.id, score=0.5))
        db.add(Weakness(id=f"w1_{doc_id}", doc_id=doc_id, skill_id="sk1"))
        db.add(StrategyLog(id=f"sl1_{doc_id}", doc_id=doc_id, skill_id="sk1"))
        db.commit()


def _mk_files(doc_id: str, tmp_path: Path) -> None:
    md = tmp_path / "markdown" / f"{doc_id}.md"
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("# t", encoding="utf-8")
    ch = tmp_path / "chapters" / doc_id
    ch.mkdir(parents=True, exist_ok=True)
    (ch / "chapters.json").write_text("[]", encoding="utf-8")
    up = tmp_path / "uploads" / doc_id
    up.mkdir(parents=True, exist_ok=True)
    (up / "orig.pdf").write_bytes(b"%PDF-1.4")


def _residue(doc_id: str) -> dict:
    with SessionLocal() as db:
        return {
            "doc": db.get(Document, doc_id) is not None,
            "task": db.query(Task).filter_by(doc_id=doc_id).count(),
            "session": db.query(TeachingSession).filter_by(doc_id=doc_id).count(),
            "turn": db.query(Turn).filter_by(session_id=f"s_{doc_id}").count(),
            "judgement": db.query(Judgement).filter_by(session_id=f"s_{doc_id}").count(),
            "weakness": db.query(Weakness).filter_by(doc_id=doc_id).count(),
            "strategy": db.query(StrategyLog).filter_by(doc_id=doc_id).count(),
        }


# ---- admin 删除全链 ----

def test_admin_delete_cascades_all(client, monkeypatch, tmp_path):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin")
    doc_id = f"d{uuid.uuid4().hex[:10]}"
    _mk_doc(doc_id)
    _mk_files(doc_id, tmp_path)

    r = client.delete(f"/api/documents/{doc_id}",
                      headers={"Authorization": f"Bearer {sign_token('oX-admin')}"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["deleted"] == {"sessions": 1, "turns": 1, "judgements": 1,
                               "weaknesses": 1, "strategy_logs": 1, "tasks": 1}
    residue = _residue(doc_id)
    assert not any(residue.values()), f"DB 残留: {residue}"
    assert not (tmp_path / "markdown" / f"{doc_id}.md").exists()
    assert not (tmp_path / "chapters" / doc_id).exists()
    assert not (tmp_path / "uploads" / doc_id).exists()


# ---- 权限闸门 ----

def test_non_admin_bearer_403(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-someone-else")
    doc_id = f"d{uuid.uuid4().hex[:10]}"
    _mk_doc(doc_id)
    r = client.delete(f"/api/documents/{doc_id}",
                      headers={"Authorization": f"Bearer {sign_token('oX-normal')}"})
    assert r.status_code == 403
    assert _residue(doc_id)["doc"] is True  # 未被删


def test_anon_device_403(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin")
    doc_id = f"d{uuid.uuid4().hex[:10]}"
    _mk_doc(doc_id)
    r = client.delete(f"/api/documents/{doc_id}", headers={"X-Device-Id": "abcd1234wxyz"})
    assert r.status_code == 403


# ---- 404 语义 ----

def test_repeat_delete_404(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin")
    doc_id = f"d{uuid.uuid4().hex[:10]}"
    _mk_doc(doc_id)
    h = {"Authorization": f"Bearer {sign_token('oX-admin')}"}
    assert client.delete(f"/api/documents/{doc_id}", headers=h).status_code == 200
    assert client.delete(f"/api/documents/{doc_id}", headers=h).status_code == 404


def test_missing_doc_404(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin")
    r = client.delete("/api/documents/no-such-doc",
                      headers={"Authorization": f"Bearer {sign_token('oX-admin')}"})
    assert r.status_code == 404


# ---- 去重不受污染 ----

def test_recreate_same_hash_after_delete(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.admin_openids", "oX-admin")
    doc_id = f"d{uuid.uuid4().hex[:10]}"
    _mk_doc(doc_id)
    h = {"Authorization": f"Bearer {sign_token('oX-admin')}"}
    client.delete(f"/api/documents/{doc_id}", headers=h)
    with SessionLocal() as db:
        db.add(Document(doc_id=f"d{uuid.uuid4().hex[:10]}", filename="again.pdf",
                        status="done", content_hash=f"hash-{doc_id}"))
        db.commit()
        dup = db.query(Document).filter_by(content_hash=f"hash-{doc_id}").count()
    assert dup == 1
