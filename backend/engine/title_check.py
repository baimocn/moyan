"""墨衍 · 重命名 AI 审核（REN-01，2026-09-04）

权限策略（用户拍板）：删除收敛到管理台（用户层不显示删除）；重命名保留给用户层，
但非 admin 改名需先过「新名称是否与文档内容相符」AI 审核，不符 422 拒绝。

- 抽样 markdown 头部 ~2500 字 + 章节标题清单，粗活引擎 json_mode 一次判定（每次改名几百 token）；
- 相符标准宽泛：主题一致/同义概括/课程名/别名/简称都算相符，只有明显风马牛不相及才拒；
- fail-open：审核服务异常放行（改名不是安全事件，引擎挂了不能把重命名功能堵死）；
- mock 模式 / 未配置引擎 / MOYAN_RENAME_REVIEW=0 → 跳过（skipped 标记）。

用法（async 端点内）：
    check = await check_title_async(new_title, markdown, chapter_titles)
    if not check["match"]: raise HTTPException(422, ...)
"""
from __future__ import annotations

import json
import logging

from . import EngineConfig
from .providers import Provider
from ..container import services
from ..settings import app_settings

log = logging.getLogger("moyan.title_check")

_SAMPLE_HEAD = 2500   # 书名反映主题，开头足够；再叠加章节标题清单

_SYSTEM_PROMPT = (
    "你是教材共享平台的命名审核员。判断给教材起的新名称是否与文档内容主题相符。"
    "相符的标准宽泛：主题一致、同义概括、课程名/别名/简称/副标题都算相符；"
    "只有明显风马牛不相及（如内容是高等数学却改名《畜禽养殖大全》）才算不符。"
    "只输出 JSON，不要输出任何其他文字。"
)


def _build_messages(title: str, sample: str, chapters: str) -> list[dict]:
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"拟改的新名称：《{title}》\n"
            f"章节标题清单：{chapters or '（无）'}\n"
            "文档开头内容：\n---\n"
            f"{sample}\n---\n\n"
            '请输出 JSON：{"match":true或false,"reason":"一句话中文理由，match 时写：名称与内容相符"}'
        )},
    ]


def _parse(content: str) -> dict:
    """容错解析模型输出（剥 ``` 围栏 / 截取首个花括号块）。"""
    text = (content or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"输出非 JSON：{text[:120]}")
    data = json.loads(text[start:end + 1])
    return {
        "match": bool(data.get("match")),
        "reason": str(data.get("reason", ""))[:200],
    }


async def check_title_async(title: str, markdown: str, chapter_titles: list[str]) -> dict:
    """返回 {match, reason, engine, skipped}；异常一律 fail-open（match=True, skipped=error）。"""
    skip = {"match": True, "reason": "", "engine": "", "skipped": ""}
    if not app_settings.rename_review:
        skip["skipped"] = "disabled"
        return skip
    if services.mock:                      # mock 演示引擎无审核能力，绝不假审
        skip["skipped"] = "mock"
        return skip
    sample = (markdown or "").strip()[:_SAMPLE_HEAD]
    if not sample:                         # 无内容可比（解析中/空文档）→ 放行
        skip["skipped"] = "empty"
        return skip
    try:
        base, key, model = services.engine_factory.require_engine(cheap=True)
        provider = Provider(EngineConfig(
            name="title_check", base_url=base, api_key=key, model=model))
        from ..ledger import ai_scope
        with ai_scope("title_check"):
            resp = await provider.chat(
                _build_messages(title[:200], sample,
                                "、".join(t for t in chapter_titles if t)[:600]),
                temperature=0.0, max_tokens=150, json_mode=True,
            )
        out = _parse(resp.get("content", ""))
        out["engine"] = resp.get("engine", "")
        out["skipped"] = ""
        return out
    except Exception as exc:  # noqa: BLE001 ProviderError/EngineNotReady/解析失败统一放行
        log.warning("重命名审核服务异常，fail-open 放行：%s", exc)
        return {**skip, "skipped": "error",
                "reason": f"审核服务异常已放行：{exc}"[:200]}
