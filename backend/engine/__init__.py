"""墨衍 · AI 引擎包

教学引擎四层：
1. providers.py   —— LLM Provider 抽象（OpenAI 兼容协议，主/备引擎可配，流式/非流式）
2. router.py      —— 主备降级 Router（重试→failover→熔断）
3. judge/quiz/proofread —— 判定 / 出题 / 校对（instructor 结构化输出，依赖容器注入 client）
4. tutor/         —— 教学状态机（session 数据 / actions 行为 / service 编排）

事件协议（流式，Vercel AI SDK Stream Protocol 风格裁剪）：
    每条 SSE：data: {json}
    type = start | reasoning-delta | text-delta | judge | meta | error | finish | abort
    流尾：data: [DONE]
"""
from __future__ import annotations

from dataclasses import dataclass

from ..settings import ai_settings, app_settings


@dataclass
class EngineConfig:
    """一个 LLM 引擎（OpenAI 兼容协议）的配置。"""
    name: str = ""
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    enabled: bool = True


def load_engines() -> list[EngineConfig]:
    """从 settings 加载引擎列表（顺序即优先级）。"""
    engines: list[EngineConfig] = []
    for name, base, key, model in ai_settings.engines():
        engines.append(EngineConfig(name=name, base_url=base, api_key=key, model=model))
    if not engines and app_settings.ai_mock:
        engines.append(EngineConfig(name="mock", enabled=False))
    elif not engines:
        engines.append(EngineConfig(name="unconfigured", enabled=False))
    return engines