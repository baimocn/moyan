"""墨衍 · JWT 签发与校验（HS256）。

约定：
- sub: openid（用户唯一标识）
- exp: 7 天
- iat: 签发时间
- iss: moyan

密钥来源：app_settings.jwt_secret。生产必须 ≥32 字节随机串。
"""
from __future__ import annotations

import time
from typing import Any

import jwt

from ..settings import app_settings

ALG = "HS256"
ISS = "moyan"
EXP_SECONDS = 7 * 24 * 3600


def _secret() -> str:
    """取 JWT 密钥。空串或太短 → 抛 RuntimeError（开发期早暴露）。"""
    s = (app_settings.jwt_secret or "").strip()
    if not s:
        raise RuntimeError(
            "MOYAN_JWT_SECRET 未配置。在 .env 加 MOYAN_JWT_SECRET=<随机32字节以上>。"
        )
    if len(s) < 16:
        raise RuntimeError(
            f"MOYAN_JWT_SECRET 太短（{len(s)} < 16 字符），请用更长的随机串。"
        )
    return s


def sign_token(openid: str, extra: dict[str, Any] | None = None) -> str:
    """签发 token。"""
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": openid,
        "iat": now,
        "exp": now + EXP_SECONDS,
        "iss": ISS,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, _secret(), algorithm=ALG)


def verify_token(token: str) -> dict[str, Any]:
    """校验 token，返回 payload。失败抛 jwt.PyJWTError。"""
    return jwt.decode(token, _secret(), algorithms=[ALG], issuer=ISS, options={"require": ["exp", "sub", "iat"]})


def decode_unsafe(token: str) -> dict[str, Any] | None:
    """不带签名校验的解析（仅供诊断日志使用）。"""
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception:  # noqa: BLE001
        return None
