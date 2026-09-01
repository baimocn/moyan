"""Docling 解析适配层单测：分诊 + 格式表（不依赖真实 docling 环境）"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from backend import config
from backend.services import docling_adapter as da


@pytest.fixture(autouse=True)
def _mark_available(monkeypatch):
    da.set_docling_available(True)
    yield
    da.set_docling_available(None)


def _make_file(tmp_path, name, size_kb=1):
    p = tmp_path / name
    p.write_bytes(b"\x00" * (size_kb * 1024))
    return p


def test_supported_formats_extended():
    for e in (".pdf", ".docx", ".pptx", ".xlsx", ".html", ".epub",
              ".png", ".md", ".txt"):
        assert e in config.SUPPORTED_FORMATS


def test_preflight_md_txt_sync(tmp_path):
    a = da.preflight(_make_file(tmp_path, "a.md"), ".md")
    b = da.preflight(_make_file(tmp_path, "a.txt"), ".txt")
    assert a["kind"] == "md" and a["sync"] is True
    assert b["kind"] == "md" and b["sync"] is True


def test_preflight_office_small_sync_big_async(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OFFICE_SYNC_MAX_MB", 1)
    small = da.preflight(_make_file(tmp_path, "a.pptx", size_kb=100), ".pptx")
    big = da.preflight(_make_file(tmp_path, "b.pptx", size_kb=2048), ".pptx")
    assert small["kind"] == "office" and small["sync"] is True
    assert big["kind"] == "office" and big["sync"] is False


def test_preflight_pdf_text_vs_scanned(tmp_path):
    import pymupdf as fitz
    text_pdf = tmp_path / "text.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "操作系统教程正文内容足够长了，用于判定非扫描件。" * 10)
    doc.save(str(text_pdf)); doc.close()
    scanned_pdf = tmp_path / "scan.pdf"
    doc = fitz.open()
    doc.new_page()   # 无文本
    doc.save(str(scanned_pdf)); doc.close()
    assert da.preflight(text_pdf, ".pdf")["kind"] == "pdf-text"
    assert da.preflight(scanned_pdf, ".pdf")["kind"] == "pdf-scanned"
    assert da.preflight(scanned_pdf, ".pdf")["sync"] is False


def test_docling_available_detects_venv_python_path():
    assert str(da.docling_venv_python()).endswith("python.exe")
    assert da.docling_available() in (True, False)   # 跟随真实环境