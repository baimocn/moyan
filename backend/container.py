"""墨衍 · 服务容器（依赖注入）

职责：
- 单一 EngineFactory：为全部 AI 能力（判定/出题/校对/对话）提供 client 工厂
  （避免各服务自造连接参数）；
- 装配单例服务（由容器管理，取代模块级散落单例）；
- mock 显式治理：**仅当  MOYAN_AI_MOCK=1 且未配置真实 key** 时启用 mock 演示；
  一旦配了真实 key，即使 MOCK=1 也走真实引擎（绝不静默假判定）。

用法：FastAPI 路由里 Depends(get_services)；后台线程用 services 容器实例。
"""
from __future__ import annotations

from dataclasses import dataclass

from openai import AsyncOpenAI, OpenAI

from .settings import ai_settings, app_settings

MOCK_ON = app_settings.ai_mock          # 用户显式开关（一次赋值，不再被改写）


class EngineNotReadyError(RuntimeError):
    """未配置 AI 引擎且 mock 未开启（生产保护）。"""


@dataclass
class EngineFactory:
    """AI client 工厂（instructor / openai SDK）。"""

    def build_openai_client(self, base_url: str, api_key: str) -> OpenAI:
        return OpenAI(base_url=base_url, api_key=api_key, timeout=600.0, max_retries=2)

    def build_async_client(self, base_url: str, api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=600.0, max_retries=2)

    def require_engine(self, cheap: bool = False) -> tuple[str, str, str]:
        """返回 (base_url, key, model)；未就绪抛 EngineNotReadyError。

        cheap=True 时优先粗活引擎（出题/判定/校对省钱），缺省回落主引擎。
        """
        if cheap:
            c = ai_settings.cheap()
            if c and c[0] and c[1] and c[2]:
                return c
        engines = ai_settings.engines()
        if not engines:
            raise EngineNotReadyError(
                "未配置 AI 引擎（MOYAN_AI_MAIN_BASE_URL/KEY/MODEL）。"
                "本地演示请设置 MOYAN_AI_MOCK=1。"
            )
        _name, base, key, model = engines[0]
        return base, key, model


def mock_effective() -> bool:
    """mock 生效条件：显式开启 **且** 没有可用真实引擎（key 优先，防假老师）。"""
    return MOCK_ON and not ai_settings.engine_ready


class Services:
    """装配后的服务容器。"""

    def __init__(self):
        self.mock = mock_effective()
        self.engine_factory = EngineFactory()

        from .engine.judge import JudgeService
        from .engine.proofread import ProofreadService
        from .engine.quiz import QuizService
        from .engine.router import Router
        from .engine.tutor.service import TutorService

        self.judge = JudgeService(self, mock=self.mock)
        self.quiz = QuizService(self, mock=self.mock)
        self.proofread = ProofreadService(self, mock=self.mock)
        # mock 模式下 Router 只走 MockProvider，绝不用配置里的引擎真调（省钱/防假）
        self.router = Router(mock=self.mock)
        self.tutor = TutorService(self)

        from .engine.review import ReviewService
        self.review = ReviewService()   # 复习会话（FSRS + engram 失败回收）

    def require_real(self):
        """生产保护：无 key 且 mock 未开 -> 拒绝（防止静默假老师）。"""
        if self.mock or ai_settings.engine_ready:
            return
        raise EngineNotReadyError(
            "AI 引擎未配置（MOYAN_AI_MAIN_*）。本地演示请 MOYAN_AI_MOCK=1。"
        )


services = Services()


def get_services() -> Services:
    return services