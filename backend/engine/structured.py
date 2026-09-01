"""墨衍 · 结构化输出助手（替代 instructor，D1 修订）

动机（真实引擎验收）：
- instructor reask 重试叠加 → 判定 65s 延迟；
- instructor 不暴露 usage → 判定/出题的 token 成本不可审计。

方案：OpenAI response_format=json_object + prompt 显式要求 schema + Pydantic model_validate_json
校验重试（≤max_retries），返回 (对象, usage)。网关（opencode.ai）实测 json_object 兼容。
"""
from __future__ import annotations

import json
import re
from typing import TypeVar, Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

_SCHEMA_HINT = """输出要求：
- 返回**纯 JSON**（不要 markdown 代码块、不要前后缀文字）；
- JSON 必须能按结构解析：{hint}"""


async def chat_json(
    client,
    model: str,
    messages: list[dict],
    response_model: Type[T],
    *,
    temperature: float = 0.0,
    max_retries: int = 2,
    schema_hint: str = "",
    aliases: dict[str, list[str]] | None = None,
    list_renames: dict[str, dict[str, str]] | None = None,
) -> tuple[T, dict]:
    """调用 chat.completions.create(json_object) → pydantic 校验重试。

    返回 (response_model 实例, usage)。校验失败重试（第 2 次去掉 response_format，
    纯文本提示仍要求 JSON）；耗尽后抛 ValueError。

    aliases：顶层字段名归一化（如 {"stem": ["question"]}）；
    list_renames：列表元素内键改名（如 options 的 label→key）并解析 "A. 文本"。
    """
    hint = _SCHEMA_HINT.format(hint=schema_hint or "按 schema 输出")
    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=messages + [{"role": "user", "content": hint}],
                temperature=temperature,
                response_format={"type": "json_object"} if attempt == 0 else None,
            )
            content = _strip_fences((resp.choices[0].message.content or "").strip())
            usage = _usage_dict(resp.usage)
            if not content:
                raise ValueError("空响应")
            data = json.loads(content)
            data = _apply_aliases(data, aliases or {}, list_renames)
            return response_model.model_validate(data), usage
        except Exception as exc:  # noqa: BLE001 重试覆盖解析/校验/网络抖动
            last_err = exc
    raise ValueError(f"结构化输出重试耗尽：{last_err}") from last_err


def _apply_aliases(data: dict, aliases: dict[str, list[str]],
                   list_renames: dict[str, dict[str, str]] | None = None) -> dict:
    """把模型自拟字段名归一化到 schema 字段名（缺失才补，不覆盖已有值）。

    aliases：顶层字段；list_renames：列表元素内部的键改名（如 options 的 label→key），
    并支持把 "A. 文本" 形式的字符串选项解析成 {"key","text"}。
    """
    out = dict(data)
    for field, cands in aliases.items():
        if out.get(field) not in (None, ""):
            continue
        for cand in cands:
            if isinstance(out.get(cand), (dict, list, str, int, float, bool)):
                out[field] = out.pop(cand)
                break
    if list_renames:
        for field, mapping in list_renames.items():
            items = out.get(field)
            if not isinstance(items, list):
                continue
            fixed = []
            for item in items:
                if isinstance(item, dict):
                    fixed.append({mapping.get(k, k): v for k, v in item.items()})
                elif isinstance(item, str):
                    m = _OPTION_STRING_RE.match(item.strip())
                    if m:
                        fixed.append({"key": m.group(1), "text": m.group(2)})
                        continue
                    fixed.append(item)
                else:
                    fixed.append(item)
            out[field] = fixed
    return out


_OPTION_STRING_RE = re.compile(r"^([A-F])[.、．]\s*(.+)$")


def _strip_fences(text: str) -> str:
    """剥掉模型可能包的 ```json ... ``` / ``` ... ``` 围栏。"""
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].rstrip() in ("```", "```json", "```JSON"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def chat_json_sync(
    client,
    model: str,
    messages: list[dict],
    response_model: Type[T],
    *,
    temperature: float = 0.0,
    max_retries: int = 2,
    schema_hint: str = "",
) -> tuple[T, dict]:
    """同步版（校对等后台线程场景）。"""
    import asyncio
    return asyncio.run(chat_json(client, model, messages, response_model,
                                 temperature=temperature, max_retries=max_retries,
                                 schema_hint=schema_hint))


def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
        "total_tokens": getattr(usage, "total_tokens", 0) or 0,
    }


__all__ = ["chat_json", "_SCHEMA_HINT"]