"""墨衍 · 上传内容安全审核（MOD-01，2026-09-04）

在文档文本已产出、任何付费 AI 步骤（校对）与上架之前执行：
- 抽样（头/中/尾，最多约 8000 字）送粗活引擎 json_mode 一次判定（每次上传几百 token）；
- verdict=reject → 拒绝入库：同步路径 422，异步任务 status=rejected + task failed；
- fail-open：审核服务异常时放行并记 warnings（审核挂掉不能把正常教材全堵死；
  极小概率错放的违规内容可由管理员 DELETE 兜底清理）；
- mock 模式 / 未配置引擎 / MOYAN_MODERATION=0 → 跳过（skipped 标记，绝不假审）。

用法：
    异步端点内     mod = await moderate_markdown_async(markdown)
    worker 线程内  mod = moderate_markdown_sync(markdown)
"""
from __future__ import annotations

import asyncio
import json
import logging

from . import EngineConfig
from .providers import Provider
from ..container import services
from ..settings import app_settings

log = logging.getLogger("moyan.moderation")

_SAMPLE_HEAD = 4000   # 文档头部（标题/导语，最可能暴露意图）
_SAMPLE_MID = 2500    # 中段（防夹带）
_SAMPLE_TAIL = 1500   # 尾部（引流/联系方式常藏尾）

_SYSTEM_PROMPT = (
    "你是教材共享平台的内容安全审核员。判断文本是否属于以下违规内容："
    "色情淫秽、赌博、毒品（含制作/贩卖/教唆），或其他明显违法有害内容。"
    "医学、法学、禁毒教育、文学研究等学术与教学语境的正常提及不算违规。"
    "只输出 JSON，不要输出任何其他文字。"
)


def sample_text(markdown: str) -> str:
    """长文档抽样：头/中/尾三段拼接（控制 token，短文全量送审）。"""
    md = (markdown or "").strip()
    budget = _SAMPLE_HEAD + _SAMPLE_MID + _SAMPLE_TAIL
    if len(md) <= budget:
        return md
    head = md[:_SAMPLE_HEAD]
    mid_start = (len(md) - _SAMPLE_MID) // 2
    mid = md[mid_start:mid_start + _SAMPLE_MID]
    tail = md[-_SAMPLE_TAIL:]
    return f"{head}\n…（中略）…\n{mid}\n…（中略）…\n{tail}"


def _build_messages(sample: str) -> list[dict]:
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": (
            "待审核文本（截取自用户上传的文档）：\n---\n"
            f"{sample}\n---\n\n"
            '请输出 JSON：{"verdict":"pass或reject",'
            '"category":"none|porn|gambling|drug|other",'
            '"reason":"一句话中文理由，pass 时写：无违规"}'
        )},
    ]


def _parse_verdict(content: str) -> dict:
    """容错解析模型输出（剥 ``` 围栏 / 截取首个花括号块）。"""
    text = (content or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"审核输出非 JSON：{text[:120]}")
    data = json.loads(text[start:end + 1])
    verdict = str(data.get("verdict", "")).strip().lower()
    if verdict not in ("pass", "reject"):
        raise ValueError(f"审核 verdict 非法：{verdict!r}")
    return {
        "verdict": verdict,
        "category": str(data.get("category", "none"))[:20],
        "reason": str(data.get("reason", ""))[:200],
    }


async def _moderate_via_engine(sample: str) -> dict:
    """真实引擎调用（json_mode，粗活引擎优先省钱，缺省回落主引擎）；调用入 moderation 台账。"""
    base, key, model = services.engine_factory.require_engine(cheap=True)
    provider = Provider(EngineConfig(
        name="moderation", base_url=base, api_key=key, model=model))
    from ..ledger import ai_scope
    with ai_scope("moderation"):
        resp = await provider.chat(
            _build_messages(sample),
            temperature=0.0, max_tokens=200, json_mode=True,
        )
    out = _parse_verdict(resp.get("content", ""))
    out["engine"] = resp.get("engine", "")
    return out


class ModerationUnavailable(RuntimeError):
    """CMP-02 fail-closed：审核服务不可用（端点层映射 503，拒收新内容）。"""


async def moderate_markdown_async(markdown: str) -> dict:
    """事件循环内可用。返回 {verdict, category, reason, ...}；异常一律 fail-open。"""
    skip = {"verdict": "pass", "category": "none", "reason": "", "skipped": ""}
    if not app_settings.moderation:
        skip["skipped"] = "disabled"
        return skip
    if services.mock:                      # mock 演示引擎无审核能力，绝不假审
        skip["skipped"] = "mock"
        return skip
    if not (markdown or "").strip():
        skip["skipped"] = "empty"
        return skip
    try:
        return await _moderate_via_engine(sample_text(markdown))
    except Exception as exc:
        # CMP-02（2026-09-05）：默认 fail-closed——审核挂掉就拒收，不让未审内容进公开书库
        if app_settings.moderation_fail_open:
            log.warning("内容审核服务异常，fail-open 放行：%s", exc)
            return {**skip, "skipped": "error",
                    "reason": f"审核服务异常已放行：{exc}"[:200]}
        raise ModerationUnavailable("审核服务暂不可用，请稍后重试") from exc


def moderate_markdown_sync(markdown: str) -> dict:
    """worker 线程用（无运行中的事件循环）。"""
    return asyncio.run(moderate_markdown_async(markdown))


def stats_entry(mod: dict) -> dict:
    """写入 documents.stats["moderation"] 的裁剪版（去抽样无关字段）。"""
    return {k: mod.get(k) for k in ("verdict", "category", "reason", "engine", "skipped")
            if mod.get(k) not in (None, "")}
