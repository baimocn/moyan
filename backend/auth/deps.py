"""墨衍 · 当前用户解析（FastAPI Depends）。

优先级：
1. MOYAN_AUTH_DISABLED=1 时直接返回 mock 用户（开发期免登录/微信开发者工具游客模式）
2. 否则从 Authorization: Bearer <jwt> 取，verify 后取 sub=openid

被路由用：
    @router.post("/xxx")
    async def xxx(user: CurrentUser = Depends(get_current_user)):
        ...
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..settings import app_settings
from .jwt import verify_token

_bearer = HTTPBearer(auto_error=False, description="Bearer JWT (Authorization: Bearer <token>)")


@dataclass(frozen=True)
class CurrentUser:
    """鉴权后注入到请求的当前用户。"""
    openid: str
    user_id: str
    is_mock: bool = False

    def __str__(self) -> str:  # noqa: Dunder
        return self.openid


def _mock_user() -> CurrentUser:
    return CurrentUser(openid="dev_user", user_id="dev_user", is_mock=True)


def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    # 0. 开发模式免鉴权
    if app_settings.auth_disabled:
        u = _mock_user()
        request.state.user = u
        return u

    # 1. 缺 header
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录：缺少 Authorization: Bearer <token>",
            headers={"WWW-Authenticate": 'Bearer realm="moyan"'},
        )

    # 2. 校验 token
    try:
        payload = verify_token(creds.credentials)
    except Exception as exc:  # noqa: BLE001 PyJWT 抛的子类统一兜住
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"token 无效：{exc}",
            headers={"WWW-Authenticate": 'Bearer realm="moyan", error="invalid_token"'},
        ) from exc

    openid = str(payload.get("sub") or "")
    if not openid:
        raise HTTPException(401, detail="token 缺少 sub(openid)")
    u = CurrentUser(openid=openid, user_id=openid, is_mock=False)
    request.state.user = u
    return u


def get_current_user_optional(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser | None:
    """鉴权可选（匿名可读，写入则需鉴权）。"""
    if app_settings.auth_disabled:
        u = _mock_user()
        request.state.user = u
        return u
    if creds is None or not creds.credentials:
        return None
    try:
        payload = verify_token(creds.credentials)
    except Exception:  # noqa: BLE001
        return None
    openid = str(payload.get("sub") or "")
    if not openid:
        return None
    u = CurrentUser(openid=openid, user_id=openid, is_mock=False)
    request.state.user = u
    return u
