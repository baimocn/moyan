"""墨衍 · 鉴权 Pydantic 模型。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class WxLoginReq(BaseModel):
    """小程序 wx.login 兑换 token。"""
    code: str = Field(min_length=1, max_length=128)
    # 可选：客户端拿到的昵称/头像，便于首登时落档
    nick_name: str = Field(default="", max_length=64)
    avatar_url: str = Field(default="", max_length=512)


class DevLoginReq(BaseModel):
    """开发模式免鉴权（仅 MOYAN_AUTH_DISABLED=1 时接受）。

    用于本地调试 / 微信开发者工具「游客模式」绕过登录：直接传 dev_openid 拿到 token。
    """
    dev_openid: str = Field(default="dev_user", min_length=1, max_length=64)


class LoginResp(BaseModel):
    token: str
    token_type: str = "Bearer"
    expires_in: int = 7 * 24 * 3600
    user_id: str            # openid（前端持久化键）
    openid: str
    is_new: bool = False    # 是否首次登录（落库新增行）


class MeResp(BaseModel):
    user_id: str
    openid: str
    created_at: str         # ISO8601
    sessions: int = 0
    last_active: str | None = None
