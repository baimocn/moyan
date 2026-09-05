"""墨衍 · 限流（slowapi）

key_func：优先 user_id（鉴权后从 request.state.user 拿），否则客户端 IP。
挂载：main.py 注册 Limiter，给路由用 @limiter.limit("30/minute") 等装饰器。

约定：
- 装饰器要求被装饰的函数第一参数为 request: Request（slowapi 内部读 self）
- headers_enabled=True 时，被装饰端点【必须】声明 response: Response 参数，
  否则 slowapi 注入 X-RateLimit-* 头时抛 500（业务已执行但响应失败，教训 2026-09-03）
- 自定义 429 响应：返 JSON {detail, retry_after}
- mock 模式 / AUTH_DISABLED 时仍走限流（防 dev 误打）
"""
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .settings import app_settings

# 全局 Limiter（app.state.limiter 会在 main.py 启动时挂上）
limiter = Limiter(
    key_func=None,  # 在 _key_func 里动态选
    headers_enabled=True,
    strategy="fixed-window",  # 固定窗口；够用且 0 内存
    default_limits=[],         # 默认不限，按需装饰
)


def _key_func(request: Request) -> str:
    """user_id 优先（鉴权时已注入 request.state.user），否则 IP。

    匿名 web_* 身份来自客户端自报的 X-Device-Id，可任意伪造/旋转：
    一旦作为限流 key，换 header 即新额度（R11 刷账单同类风险）。
    故匿名一律回落 IP 维度（nginx 已传真实 IP，uvicorn --proxy-headers 已开）；
    仅真实登录用户（openid 非 web_ 前缀）按 user: 记账。
    """
    u = getattr(request.state, "user", None)
    if u is not None:
        openid = getattr(u, "openid", "")
        if openid and not openid.startswith("web_"):
            return f"user:{openid}"
    return f"ip:{get_remote_address(request)}"


limiter._key_func = _key_func   # 覆盖默认


# ---- 常用限流档（5/min 最严，上传 5/hour，教学 30/min） ----
L_TUTOR = "30/minute"            # 教学 SSE / start
L_UPLOAD = "5/hour"              # 上传教材
L_HEAVY = "10/minute"            # 解析/重切/出题等重活
L_GENERAL = "120/minute"         # 通用接口兜底
L_HEALTH = "600/minute"          # 健康检查


# ---- 429 响应（JSON 友好） ----

def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry = getattr(exc, "retry_after", None) or 60
    return JSONResponse(
        status_code=429,
        content={
            "ok": False,
            "detail": f"请求过快：{exc.detail}",
            "retry_after": int(retry),
        },
        headers={"Retry-After": str(int(retry))},
    )


__all__ = ["limiter", "_rate_limit_handler", "L_TUTOR", "L_UPLOAD", "L_HEAVY", "L_GENERAL", "L_HEALTH"]
