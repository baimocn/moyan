"""墨衍 · 教材校对服务（D8：AI 对照知识库纠错，成本控制 + 原件清理）

设计：
- 定点校对：只校"可疑句"（OCR score<0.85 的行文本），不全文重写 → token 省一个量级；
- 批量修正：可疑句去重成清单 → 一次 instructor 调用返回 {原句: 修正句} → 在 MD 里替换；
- 原则：教材可信度最高，只改确信的 OCR 错误，不润色不改意（不重建内容）；
- 文本层 PDF（无 OCR score）跳过校对；
- 校对完成后清理原件（uploads 下原始 PDF），MD 为唯一依据。
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from .. import config
from . import load_engines
from .prompts import PROOFREAD_INSTRUCTION


class CorrectionPair(BaseModel):
    original: str
    corrected: str


class ProofreadResult(BaseModel):
    corrections: list[CorrectionPair] = []


class ProofreadService:
    def __init__(self, container=None, mock: bool = False):
        self._sync = None
        self._model = ""
        self.mock = bool(mock)
        if container is None or self.mock:
            return
        try:
            base, key, model = container.engine_factory.require_engine(cheap=True)
            self._sync = container.engine_factory.build_openai_client(base, key)
            self._model = model
        except Exception:
            self.mock = True

    def proofread_markdown(self, md: str, work_dir: Optional[Path] = None) -> tuple[str, int]:
        """校对一份 MD，返回（修正后 MD，修正条数）。同步入口（后台线程可用）。"""
        if self.mock or self._sync is None:
            return md, 0   # mock/未配置：跳过校对（配 MOYAN_AI_MAIN_* 后生效）
        suspicious = self._collect_suspicious(work_dir)
        if not suspicious:
            return md, 0
        pairs = self._correct_batch(suspicious)
        if not pairs:
            return md, 0
        corrected_md = md
        n = 0
        for p in pairs:
            if p.original and p.corrected and p.original != p.corrected:
                # 按句替换（原句唯一化：一次替换一处）
                if p.original in corrected_md and corrected_md.count(p.original) <= 3:
                    corrected_md = corrected_md.replace(p.original, p.corrected, 1)
                    n += 1
        return corrected_md, n

    def _collect_suspicious(self, work_dir: Optional[Path]) -> list[str]:
        """从 OCR 行流拿低置信行（score<0.85）作为可疑句。"""
        if not work_dir:
            return []
        json_path = work_dir / "ocr_lines.json"
        if not json_path.exists():
            return []
        try:
            rows = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return []
        seen: list[str] = []
        for r in rows:
            score = r.get("score", 1.0)
            text = (r.get("text") or "").strip()
            if score < 0.85 and 3 <= len(text) <= 80 and text not in seen:
                seen.append(text)
        return seen[:200]

    def _correct_batch(self, sentences: list[str]) -> list[CorrectionPair]:
        """批量校对（每批 30 句），返回修正对。"""
        result: list[CorrectionPair] = []
        batch = 30
        for i in range(0, len(sentences), batch):
            chunk = sentences[i:i + batch]
            try:
                resp, _usage = chat_json_sync(
                    self._sync, self._model,
                    messages=[{
                        "role": "user",
                        "content": (
                            "以下是待校对句子清单（JSON 数组）。请逐句判断并输出修正结果。\n"
                            + json.dumps(chunk, ensure_ascii=False)
                        ),
                    }],
                    response_model=ProofreadResult,
                    max_retries=1,
                    temperature=0,
                )
                result.extend(resp.corrections or [])
            except Exception:
                continue
        return result


def cleanup_original(doc_id: str) -> int:
    """删除上传原件（PDF 等非 md 文件），MD 为唯一依据。返回删除文件数。"""
    upload_dir = config.UPLOAD_DIR / doc_id
    removed = 0
    if upload_dir.exists():
        for f in upload_dir.iterdir():
            if f.is_file() and f.suffix.lower() not in (".md",):
                try:
                    f.unlink()
                    removed += 1
                except OSError:
                    pass
    return removed