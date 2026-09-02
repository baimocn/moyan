"""墨衍 · 微信 jscode2session 客户端。

AppID/AppSecret 来源：app_settings.wx_appid / wx_appsecret。
无配置时调 exchange_openid 会抛 ConfigurationError（让上层 503/500 暴露）。
"""
from __future__ import annotations

from typing import Any

import httpx

from ..settings import app_settings

WX_SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class WxLoginError(RuntimeError):
    """微信侧返回非 0 错误码。"""


class WxConfigError(RuntimeError):
    """本地没配 AppID/AppSecret。"""


def _creds() -> tuple[str, str]:
    appid = (app_settings.wx_appid or "").strip()
    secret = (app_settings.wx_appsecret or "").strip()
    if not appid or not secret:
        raise WxConfigError(
            "MOYAN_WX_APPID / MOYAN_WX_APPSECRET 未配置。"
            "开发期可设 MOYAN_AUTH_DISABLED=1 走 dev-login。"
        )
    return appid, secret


async def exchange_openid(code: str) -> dict[str, Any]:
    """拿 code 换 openid + session_key。

    返回字段至少含 openid；errcode!=0 → WxLoginError。
    """
    appid, secret = _creds()
    params = {
        "appid": appid,
        "secret": secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10.0) as cli:
        r = await cli.get(WX_SESSION_URL, params=params)
        data = r.json()
    if not isinstance(data, dict):
        raise WxLoginError(f"微信接口返回非 JSON：{r.text[:200]}")
    errcode = data.get("errcode", 0)
    if errcode and errcode != 0:
        errmsg = data.get("errmsg", "未知错误")
        raise WxLoginError(f"微信登录失败 errcode={errcode} errmsg={errmsg}")
    openid = data.get("openid", "")
    if not openid:
        raise WxLoginError(f"微信接口未返回 openid：{data}")
    return data
