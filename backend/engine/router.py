"""墨衍 · 主备降级 Router（轻量手写版，~150 行，不引 litellm）

策略（调研结论：litellm Router + free-llm-gateway + 9router 业界做法的裁剪）：
- 按配置顺序尝试引擎；失败 → 下一引擎（failover），用户无感；
- 同端点重试交给 openai SDK（max_retries=2，抖动退避）；跨引擎总尝试 ≤ 3-4；
- 连续失败触发冷却（cooldown 60s），冷却中的引擎跳过（熔断）；
- 每次请求记录 Meta 事件：provider / fallbackUsed / latencyMs。
"""
from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator

from . import EngineConfig, load_engines
from .providers import (EV_ERROR, EV_META, EV_START, Provider, ProviderError,
                        MockProvider)

COOLDOWN_SECONDS = 60
MAX_STOPPED_FAILURES = 4  # 连续失败 N 次开始冷却
MAX_TOTAL_ATTEMPTS = 4


class Router:
    """引擎路由：主→备 failover + 熔断。

    mock=True（容器在 MOYAN_AI_MOCK=1 且无真实 key 时传入）：直接走 MockProvider，
    绝不真调配置里残留的引擎（防 mock 演示还烧钱）。
    """

    def __init__(self, engines: list[EngineConfig] | None = None, mock: bool = False):
        self._engines: list[Provider] = []
        self._fail_since: dict[str, float] = {}   # engine -> 冷却开始时间
        self._consec_fails: dict[str, int] = {}
        self._mock_mode = mock
        if mock:
            return
        for cfg in engines or load_engines():
            if not cfg.enabled:
                continue
            self._engines.append(Provider(cfg))

    @property
    def configured(self) -> bool:
        return bool(self._engines)

    @property
    def engine_names(self) -> list[str]:
        return [p.cfg.name for p in self._engines]

    def _cooled_providers(self, now: float) -> list[Provider]:
        return [p for p in self._engines
                if now - self._fail_since.get(p.cfg.name, 0) > COOLDOWN_SECONDS]

    def _record_fail(self, name: str, now: float) -> None:
        self._consec_fails[name] = self._consec_fails.get(name, 0) + 1
        if self._consec_fails[name] >= MAX_STOPPED_FAILURES:
            self._fail_since[name] = now
            self._consec_fails[name] = 0

    def _record_ok(self, name: str) -> None:
        self._consec_fails[name] = 0
        self._fail_since.pop(name, None)

    def _mock(self) -> MockProvider:
        return MockProvider()

    async def chat(self, messages: list[dict], **kwargs) -> dict:
        """非流式：主→备→mock。返回最终结果（含 engine 字段）。"""
        if self._mock_mode or not self.configured:
            r = await self._mock().chat(messages, **kwargs)
            r["fallbackUsed"] = True
            return r
        now = time.time()
        last_err: ProviderError | None = None
        for provider in self._cooled_providers(now):
            try:
                t0 = time.time()
                r = await provider.chat(messages, **kwargs)
                self._record_ok(provider.cfg.name)
                r["latencyMs"] = int((time.time() - t0) * 1000)
                r["fallbackUsed"] = False
                return r
            except ProviderError as exc:
                last_err = exc
                self._record_fail(provider.cfg.name, time.time())
                continue
        # 全部失败：放行冷却中的引擎再试一次（最后努力），仍失败 → mock 或抛错
        for provider in self._engines:
            try:
                t0 = time.time()
                r = await provider.chat(messages, **kwargs)
                self._record_ok(provider.cfg.name)
                r["latencyMs"] = int((time.time() - t0) * 1000)
                r["fallbackUsed"] = True
                return r
            except ProviderError:
                continue
        if last_err:
            raise last_err
        r = await self._mock().chat(messages, **kwargs)
        r["fallbackUsed"] = True
        return r

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[dict]:
        """流式：主→备 failover。上游中途失败时，切到备胎**重发整段**并追加 meta 提示。"""
        if self._mock_mode or not self.configured:
            async for ev in self._mock().chat_stream(messages, **kwargs):
                yield ev
            return
        now = time.time()
        total_attempts = 0
        last_err: ProviderError | None = None
        started = False
        for provider in self._cooled_providers(now) + self._engines:
            if total_attempts >= MAX_TOTAL_ATTEMPTS:
                break
            total_attempts += 1
            try:
                t0 = time.time()
                first = True
                async for ev in provider.chat_stream(messages, **kwargs):
                    if first:
                        started = True
                        first = False
                    if ev["type"] == EV_ERROR:
                        # 上游流中途失败：交给外层 failover 循环
                        last_err = ProviderError(ev.get("error", "stream error"), retriable=True,
                                                 engine=ev.get("engine", provider.cfg.name))
                        break
                    yield ev
                else:
                    self._record_ok(provider.cfg.name)
                    yield {
                        "type": EV_META,
                        "provider": provider.cfg.name,
                        "fallbackUsed": total_attempts > 1,
                        "latencyMs": int((time.time() - t0) * 1000),
                    }
                    return
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # 连接级失败
                last_err = ProviderError(str(exc), retriable=True, engine=provider.cfg.name)
            self._record_fail(provider.cfg.name, time.time())
            if started:
                yield {"type": EV_META,
                       "provider": provider.cfg.name,
                       "fallbackUsed": True,
                       "note": "上游引擎失败，已切换备胎重新生成"}
        # 全失败
        if last_err:
            yield {"type": EV_ERROR, "error": str(last_err), "retriable": True,
                   "engine": last_err.engine}
        else:
            async for ev in self._mock().chat_stream(messages, **kwargs):
                yield ev