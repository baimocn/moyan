"""墨衍 · 集中配置（pydantic-settings）

分层：App（服务）/ Db（数据库）/ AI（引擎）
来源：环境变量 + 本地 .env（可选），类型校验。
兼容：config.py 保留旧名字代理 settings（避免全项目大改）。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"   # 绝对路径：启动目录无关，避免"以为配了 key 实际没配"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MOYAN_", env_file=str(ENV_FILE), extra="ignore")

    host: str = "127.0.0.1"
    port: int = 5001
    max_upload_mb: int = 200
    ocr_dpi: int = 150
    ocr_engine: str = "rapid"          # rapid | win（备用）
    ocr_workers: int = 4
    ocr_intra_threads: int = 2
    parser_engine: str = "docling"     # docling（主引擎，需 .docling-venv）| legacy（RapidOCR/文本层快路径）
    teaching_reviewer: str = "sample"  # 输出后裁判：off | sample（默认） | on
    # ---- 上传内容安全审核（MOD-01，2026-09-04）----
    # 上架前 AI 审核（黄赌毒等违禁内容拒绝入库）；0 可关闭（本地自用环境）
    moderation: bool = True
    ai_mock: bool = False              # 显式开启 mock 演示（无 key 且未开时拒绝 AI 服务）
    cors_origins: str = ""             # 跨源白名单（逗号分隔，如 https://moyan.example）；空=仅同源
    debug: bool = False
    # ---- 运行环境（Phase 1 权限分层：2026-09-04）----
    # dev（默认，本地开发）/ production（生产；启动时强制关闭免鉴权与 dev-login）
    env: str = "dev"
    # ---- 管理员清单（权限分层 ADMIN-01）----
    # 逗号分隔的 openid 列表，命中的用户 role=admin。例：ADMIN_OPENIDS=oX123,oX456
    admin_openids: str = ""
    # ---- 鉴权（部署前置：2026-09-02）----
    # 微信小程序登录 AppID / AppSecret（从 mp.weixin.qq.com 后台拿）
    wx_appid: str = ""
    wx_appsecret: str = ""
    # JWT 签发密钥（HS256）。生产必须 ≥32 字节随机串。空串时若开启鉴权会启动失败
    jwt_secret: str = ""
    # 鉴权总开关：1=完全免登录（dev / 微信开发者工具游客模式），0=强制 Bearer token
    # 留 str 而非 bool 是为了容忍 "1"/"true"/"yes" 多种写法
    auth_disabled: bool = False

    @property
    def admin_set(self) -> frozenset:
        """管理员 openid 集合（逗号/空白分隔，去空）。O(1) 成员判定。"""
        raw = (self.admin_openids or "").replace("，", ",")
        return frozenset(s.strip() for s in raw.replace(" ", ",").split(",") if s.strip())

    @property
    def is_production(self) -> bool:
        return (self.env or "").strip().lower() == "production"


def apply_production_safety() -> list[str]:
    """生产环境安全硬校验（ADMIN-03）：MOYAN_ENV=production 时强制关闭免鉴权。

    返回触发的动作列表（供启动日志与测试断言）。FAIL-SAFE：宁可生产要配 jwt_secret，
    也绝不让人误开 AUTH_DISABLED 裸奔上线。
    """
    actions: list[str] = []
    if app_settings.is_production and app_settings.auth_disabled:
        object.__setattr__(app_settings, "auth_disabled", False)
        actions.append("auth_disabled 已从 True 强制改为 False（生产环境禁止免鉴权）")
    for a in actions:
        logging.getLogger("moyan.security").warning("生产安全硬校验：%s", a)
    return actions


class DbSettings(BaseSettings):
    """数据库；部署时用 MOYAN_DB_URL 指 PostgreSQL。"""
    model_config = SettingsConfigDict(env_prefix="MOYAN_", env_file=str(ENV_FILE), extra="ignore")

    db_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'moyan_dev.db').as_posix()}"


class AiSettings(BaseSettings):
    """AI 引擎（OpenAI 兼容协议）。

    main=教学对话（顶级模型）；fallback=兜底（DeepSeek 等）；浮动=总结/出题等粗活。
    """
    model_config = SettingsConfigDict(env_prefix="MOYAN_AI_", env_file=str(ENV_FILE), extra="ignore")

    main_base_url: str = ""
    main_key: str = ""
    main_model: str = ""
    fallback_base_url: str = ""
    fallback_key: str = ""
    fallback_model: str = ""
    cheap_base_url: str = ""           # 缺省回退到 fallback
    cheap_key: str = ""
    cheap_model: str = ""

    @property
    def has_main(self) -> bool:
        return bool(self.main_base_url and self.main_key and self.main_model)

    @property
    def engine_ready(self) -> bool:
        return self.has_main

    def engines(self):
        """返回 [(name, base_url, key, model), ...] 按优先级。"""
        out = []
        if self.has_main:
            out.append(("main", self.main_base_url, self.main_key, self.main_model))
        fb = self.fallback_base_url or self.cheap_base_url
        fk = self.fallback_key or self.cheap_key
        fm = self.fallback_model or self.cheap_model
        if fb and fk and fm:
            out.append(("fallback", fb, fk, fm))
        return out

    def cheap(self):
        """粗活引擎（出题/总结），优先 cheap，缺省 fallback。"""
        b = self.cheap_base_url or self.fallback_base_url
        k = self.cheap_key or self.fallback_key
        m = self.cheap_model or self.fallback_model
        return (b, k, m) if (b and k and m) else None


app_settings = AppSettings()
db_settings = DbSettings()
ai_settings = AiSettings()