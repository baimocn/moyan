"""MOD-01 上传内容 AI 审核单测（2026-09-04）

覆盖：
1) 同步 md 路径：审核 reject → 422 + 不落 done 文档 + 上传残壳清理
2) 审核通过 → 正常上架 + stats.moderation 留痕
3) MOYAN_MODERATION=0 → 跳过审核（引擎不被调用）
4) 审核服务异常 → fail-open 放行 + warnings 留痕
5) docling 异步任务：reject → 文档 status=rejected + task failed + 产物不落盘
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("MOYAN_AUTH_DISABLED", "0")
os.environ.setdefault("MOYAN_JWT_SECRET", "test-secret-moderation")

import pytest
from fastapi.testclient import TestClient

from backend import tasks as tasks_mod
from backend.main import app as real_app
from backend.models import Document, SessionLocal
from backend.models.tasks import Task
from backend.rate_limit import limiter


def _fake_moderate(verdict: str = "pass", category: str = "none", reason: str = "无违规"):
    async def _inner(sample: str) -> dict:
        return {"verdict": verdict, "category": category, "reason": reason,
                "engine": "fake"}
    return _inner


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.auth_disabled", True)
    monkeypatch.setattr("backend.settings.app_settings.moderation", True)
    try:
        limiter.reset()  # 上传 5/hour 限流，逐测试清零
    except Exception:  # noqa: BLE001
        pass
    return TestClient(real_app)


def _upload_md(client: TestClient, title: str, body: str):
    return client.post(
        "/api/upload",
        files={"file": (f"{title}.md", body.encode("utf-8"), "text/markdown")},
        data={"display_name": title},
    )


def _doc_by_title(title: str) -> Document | None:
    with SessionLocal() as db:
        return db.query(Document).filter_by(title=title).order_by(
            Document.created_at.desc()).first()


# ---- 1) 拒绝：422 + 无 done 文档 ----

def test_upload_md_rejected(client, monkeypatch):
    monkeypatch.setattr("backend.engine.moderation._moderate_via_engine",
                        _fake_moderate("reject", "porn", "涉黄内容"))
    marker = uuid.uuid4().hex[:8]
    title = f"违规书{marker}"
    r = _upload_md(client, title, f"# {title}\n\n" + "正文。" * 100)
    assert r.status_code == 422, r.text
    assert "内容审核未通过" in r.json()["detail"]
    doc = _doc_by_title(title)
    assert doc is None or doc.status != "done"


# ---- 2) 通过：正常上架 + 审核留痕 ----

def test_upload_md_pass(client, monkeypatch):
    monkeypatch.setattr("backend.engine.moderation._moderate_via_engine",
                        _fake_moderate("pass", "none", "无违规"))
    marker = uuid.uuid4().hex[:8]
    title = f"合规书{marker}"
    r = _upload_md(client, title, f"# {title}\n\n" + "正文。" * 100)
    assert r.status_code == 200, r.text
    doc = _doc_by_title(title)
    assert doc is not None and doc.status == "done"
    assert doc.stats.get("moderation", {}).get("verdict") == "pass"


# ---- 3) 关闭开关：引擎不被调用 ----

def test_moderation_disabled_skips(client, monkeypatch):
    monkeypatch.setattr("backend.settings.app_settings.moderation", False)

    async def _boom(sample: str) -> dict:
        raise AssertionError("开关关闭时不应调用审核引擎")

    monkeypatch.setattr("backend.engine.moderation._moderate_via_engine", _boom)
    marker = uuid.uuid4().hex[:8]
    title = f"关审书{marker}"
    r = _upload_md(client, title, f"# {title}\n\n" + "正文。" * 100)
    assert r.status_code == 200, r.text
    doc = _doc_by_title(title)
    assert doc is not None and doc.status == "done"
    assert doc.stats.get("moderation", {}).get("skipped") == "disabled"


# ---- 4) 审核异常 fail-open ----

def test_moderation_error_fails_open(client, monkeypatch):
    async def _boom(sample: str) -> dict:
        raise RuntimeError("engine down")

    monkeypatch.setattr("backend.engine.moderation._moderate_via_engine", _boom)
    marker = uuid.uuid4().hex[:8]
    title = f"审挂书{marker}"
    r = _upload_md(client, title, f"# {title}\n\n" + "正文。" * 100)
    assert r.status_code == 200, r.text  # 放行
    doc = _doc_by_title(title)
    assert doc is not None and doc.status == "done"
    assert any("审核" in w for w in (doc.warnings or []))


# ---- 5) docling 异步任务拒绝 ----

def test_docling_task_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.settings.app_settings.moderation", True)
    for attr in ("UPLOAD_DIR", "MARKDOWN_DIR", "CHAPTERS_DIR", "WORK_DIR"):
        (tmp_path / attr.lower()).mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(f"backend.config.{attr}", tmp_path / attr.lower())

    doc_id = f"m{uuid.uuid4().hex[:10]}"
    task_id = f"t_{uuid.uuid4().hex[:10]}"
    upload_dir = tmp_path / "upload_dir" / doc_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / "book.pdf").write_bytes(b"%PDF-1.4 fake")

    with SessionLocal() as db:
        db.add(Document(doc_id=doc_id, filename="book.pdf", status="processing"))
        db.add(Task(id=task_id, doc_id=doc_id, kind="docling", status="queued"))
        db.commit()

    def _fake_convert(upload_path, work):  # noqa: ANN001
        return {"markdown": "# 违规教材\n\n涉黄内容", "page_count": 1,
                "seconds": 0.1, "ok": True, "chars": 10}

    monkeypatch.setattr("backend.services.docling_adapter.convert_sync", _fake_convert)
    monkeypatch.setattr("backend.tasks.moderate_markdown_sync",
                        lambda md: {"verdict": "reject", "category": "porn",
                                    "reason": "涉黄内容", "engine": "fake"})

    tasks_mod._run_docling_task(task_id)

    with SessionLocal() as db:
        doc = db.get(Document, doc_id)
        task = db.get(Task, task_id)
    assert doc.status == "rejected"
    assert doc.stats.get("moderation", {}).get("category") == "porn"
    assert task.status == "failed"
    assert "内容审核未通过" in (task.message or "")
    # 产物不落盘
    assert not (tmp_path / "markdown_dir" / f"{doc_id}.md").exists()
    assert not (tmp_path / "chapters_dir" / doc_id).exists()
