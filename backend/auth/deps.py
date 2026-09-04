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

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..settings import app_settings
from .jwt import verify_token

_bearer = HTTPBearer(auto_error=False, description="Bearer JWT (Authorization: Bearer <token>)")


@dataclass(frozen=True)
class CurrentUser:
    """鉴权后注入到请求的当前用户。role: admin | user | anon（Phase 1 权限分层）。"""
    openid: str
    user_id: str
    is_mock: bool = False
    role: str = "anon"

    def __str__(self) -> str:  # noqa: Dunder
        return self.openid


def _mock_user() -> CurrentUser:
    # dev 免鉴权模式给 admin：本地开发/测试可直接验证管理端行为
    return CurrentUser(openid="dev_user", user_id="dev_user", is_mock=True, role="admin")


def _role_for(openid: str) -> str:
    """真实登录用户的角色：管理员清单命中 → admin，否则 user（ADMIN-01）。"""
    return "admin" if openid in app_settings.admin_set else "user"


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
    u = CurrentUser(openid=openid, user_id=openid, is_mock=False, role=_role_for(openid))
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
    u = CurrentUser(openid=openid, user_id=openid, is_mock=False, role=_role_for(openid))
    request.state.user = u
    return u


_DEVICE_ID_RE = __import__("re").compile(r"^[A-Za-z0-9_-]{8,64}$")


def get_requester(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    device_id: str = Header(default="", alias="X-Device-Id"),
) -> CurrentUser:
    """可登录可匿名的请求者解析（网页版免登录核心，2026-09-03）。

    优先级：
    1. AUTH_DISABLED=1 → mock dev_user（本地开发）
    2. Bearer 有效    → 真实用户（小程序 / 已登录网页用户，行为不变）
    3. X-Device-Id    → 匿名设备用户 web_<did>（网页免登录，进度按浏览器隔离）
    4. 都没有         → web_anon 兜底

    总是设置 request.state.user —— 限流 key_func 以此为维度。
    """
    # 1. 开发模式免鉴权
    if app_settings.auth_disabled:
        u = _mock_user()
        request.state.user = u
        return u

    # 2. Bearer 有效 → 真实用户
    if creds is not None and creds.credentials:
        try:
            payload = verify_token(creds.credentials)
            openid = str(payload.get("sub") or "")
            if openid:
                u = CurrentUser(openid=openid, user_id=openid, is_mock=False, role=_role_for(openid))
                request.state.user = u
                return u
        except Exception:  # noqa: BLE001 token 无效不拒客，落入匿名分支
            pass

    # 3/4. 匿名：X-Device-Id（白名单清洗）或 web_anon 兜底
    did = (device_id or "").strip()
    if not _DEVICE_ID_RE.match(did):
        did = "anon"
    u = CurrentUser(openid=f"web_{did}", user_id=f"web_{did}", is_mock=False, role="anon")
    request.state.user = u
    return u


def require_admin(user: CurrentUser = Depends(get_requester)) -> CurrentUser:
    """破坏性/管理端点的闸门（ADMIN-02）：非 admin 一律 403。

    用法（Phase 2 DELETE 起逐个挂载）：
        @router.delete("/documents/{doc_id}")
        def delete_doc(doc_id: str, user: CurrentUser = Depends(require_admin)): ...
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user
