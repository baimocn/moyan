"""墨衍 · 网页版密码哈希（scrypt）。

选型说明：设计文档建议 bcrypt/argon2，但为避免给生产服务器（2C2G）加
pip 依赖，改用 Python 标准库 hashlib.scrypt —— 内存困难型 KDF，安全强度
与 bcrypt/argon2 同级（OWASP 认可）。存储格式（5 段，$ 分隔）：

    scrypt$16384$8$1$<salt_hex>$<hash_hex>

verify 用 hmac.compare_digest 防时序攻击。参数取 RFC 7914 推荐值：
n=2^14, r=8, p=1（内存 ~16MB/次，登录路径可接受）。
"""
from __future__ import annotations

import hashlib
import hmac
import os

_N = 2 ** 14
_R = 8
_P = 1
_DKLEN = 32


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_N, r=_R, p=_P, dklen=_DKLEN
    )
    return f"scrypt${_N}${_R}${_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码。格式不符 / 字段缺失一律 False（不抛异常）。"""
    try:
        scheme, n_s, r_s, p_s, salt_hex, hash_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        salt = bytes.fromhex(salt_hex)
        expect = bytes.fromhex(hash_hex)
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=salt,
            n=int(n_s), r=int(r_s), p=int(p_s), dklen=len(expect),
        )
        return hmac.compare_digest(actual, expect)
    except Exception:  # noqa: BLE001 格式坏/长度短/非十六进制 → 校验失败
        return False
