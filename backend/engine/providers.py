"""墨衍 · LLM Provider 抽象（OpenAI 兼容协议）

- 统一 chat / chat_stream 接口；
- 流式走 OpenAI 兼容 stream=True（delta 增量），DeepSeek/中转站均兼容；
- 结构化输出：response_format={"type": "json_object"} + prompt 显式要求（兼容 DeepSeek 文档要求）；
- 无 key 时提供 MockProvider（本地演示/测试，不回显死板文本而是模拟教学节奏）。
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncIterator, Optional

from . import EngineConfig

# 事件类型常量（与前端约定，Vercel Stream Protocol 风格裁剪）
EV_START = "start"
EV_REASONING = "reasoning-delta"
EV_TEXT = "text-delta"
EV_JUDGE = "judge"
EV_META = "meta"
EV_ERROR = "error"
EV_FINISH = "finish"
EV_ABORT = "abort"
DONE_MARKER = "[DONE]"


class ProviderError(Exception):
    """上游调用失败（可重试/可降级）。"""
    def __init__(self, message: str, *,
                 retriable: bool = True,
                 status_code: Optional[int] = None,
                 engine: str = ""):
        super().__init__(message)
        self.retriable = retriable
        self.status_code = status_code
        self.engine = engine


class Provider:
    """单个引擎的客户端封装。"""

    def __init__(self, cfg: EngineConfig):
        self.cfg = cfg
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=self.cfg.base_url,
                api_key=self.cfg.api_key,
                timeout=600.0,
                max_retries=2,  # openai SDK 内置：退避 0.5s→8s 抖动
            )
        return self._client

    async def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> dict:
        """非流式调用，返回 {content, usage, model}。"""
        client = self._get_client()
        kwargs: dict = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            resp = await client.chat.completions.create(**kwargs)
        except Exception as exc:  # 统一包装成 ProviderError
            raise ProviderError(
                str(exc), retriable=True,
                status_code=getattr(exc, "status_code", None),
                engine=self.cfg.name,
            ) from exc
        return {
            "content": (resp.choices[0].message.content or ""),
            "usage": _usage_dict(resp.usage),
            "model": resp.model or self.cfg.model,
            "engine": self.cfg.name,
            "finish_reason": resp.choices[0].finish_reason,
        }

    async def chat_stream(self, messages: list[dict], *, temperature: float = 0.7) -> AsyncIterator[dict]:
        """流式调用：yield 事件 dict（type=start/text-delta/meta/finish）。"""
        client = self._get_client()
        yield {"type": EV_START, "model": self.cfg.model, "engine": self.cfg.name,
               "ts": time.time()}
        text_parts: list[str] = []
        reason_parts: list[str] = []
        finish_reason = None
        usage = {}
        try:
            stream = await client.chat.completions.create(
                model=self.cfg.model,
                messages=messages,
                temperature=temperature,
                stream=True,
                stream_options={"include_usage": True},  # 中断时可能丢失，见兜底
            )
            async for chunk in stream:
                if not chunk.choices and chunk.usage:
                    usage = _usage_dict(chunk.usage)
                    continue
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta is None:
                    continue
                reasoning = getattr(delta, "reasoning_content", None)  # DeepSeek 思考模型
                if reasoning:
                    reason_parts.append(reasoning)
                    yield {"type": EV_REASONING, "delta": reasoning}
                if delta.content:
                    text_parts.append(delta.content)
                    yield {"type": EV_TEXT, "delta": delta.content}
                fr = chunk.choices[0].finish_reason
                if fr:
                    finish_reason = fr
            await stream.response.aclose() if hasattr(stream, "response") else None
        except asyncio.CancelledError:
            # 客户端断连：关闭上游流停止计费后向上抛
            raise
        except Exception as exc:
            yield {"type": EV_ERROR, "error": str(exc),
                   "retriable": True, "engine": self.cfg.name}
            return
        yield {"type": EV_FINISH,
               "finish_reason": finish_reason,
               "usage": usage or {"estimated_tokens": _estimate_tokens(text_parts, reason_parts)},
               "engine": self.cfg.name}


class MockProvider(Provider):
    """无 API key 时的本地演示引擎：模拟教学节奏的流式输出（方便跑通管线）。"""

    def __init__(self, cfg: EngineConfig | None = None):
        super().__init__(cfg or EngineConfig(name="mock", model="mock", enabled=True))

    async def chat_stream(self, messages, *, temperature=0.7):
        last = (messages or [{}])[-1].get("content", "")
        text = f"[模拟老师] 我收到了你的问题：「{last[:40]}」。等配置好 MOYAN_AI_MAIN_* 环境变量后，我会在这里真正讲课。"
        yield {"type": EV_START, "model": "mock", "engine": "mock", "ts": time.time()}
        for ch in text:
            yield {"type": EV_TEXT, "delta": ch}
            await asyncio.sleep(0.02)
        yield {"type": EV_FINISH, "finish_reason": "stop", "usage": {"estimated_tokens": 42}}


def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
        "total_tokens": getattr(usage, "total_tokens", 0) or 0,
    }


def _estimate_tokens(text_parts: list[str], reason_parts: list[str]) -> int:
    """中断兜底：按字符估算 token（中文约 1 字符≈0.6 token）。"""
    total = sum(len(t) for t in text_parts) + sum(len(t) for t in reason_parts)
    return max(1, int(total * 0.6))