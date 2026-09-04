"""墨衍 · /api/auth/* 路由。

端点：
- POST /api/auth/wx-login   : 小程序 wx.login 兑换 token
- POST /api/auth/dev-login  : 开发模式免鉴权（仅 MOYAN_AUTH_DISABLED=1）
- POST /api/auth/register   : 网页版邮箱密码注册（2026-09-03）
- POST /api/auth/login      : 网页版邮箱密码登录
- GET  /api/auth/me         : 取当前用户（需鉴权）

首登落档：user_profiles 表（user_id=openid, nick_name/avatar_url/last_active），
         由 init_db 后续建表。首登返 is_new=True 让前端弹一次"完善资料"。
网页用户：user_id = web_<10位hex>，auth_type='web'，email/password_hash 落档。
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.db import SessionLocal
from .deps import CurrentUser, get_current_user
from .jwt import sign_token
from .passwords import hash_password, verify_password
from .schemas import DevLoginReq, LoginReq, LoginResp, MeResp, RegisterReq, WxLoginReq
from .wx import WxConfigError, WxLoginError, exchange_openid
from ..settings import app_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 防用户枚举：邮箱不存在时也跑一次 scrypt 校验，拉平响应时间
_DUMMY_HASH = hash_password("dummy-password-for-timing")


def _upsert_profile(db: Session, openid: str, nick: str, avatar: str) -> bool:
    """首登落档；返回是否新行。"""
    row = db.execute(
        text("SELECT user_id, last_active FROM user_profiles WHERE user_id=:u"),
        {"u": openid},
    ).first()
    if row is None:
        db.execute(
            text("""INSERT INTO user_profiles
                    (user_id, nick_name, avatar_url, created_at, last_active)
                    VALUES (:u, :n, :a, :t, :t)"""),
            {"u": openid, "n": nick or "", "a": avatar or "", "t": datetime.now(timezone.utc)},
        )
        db.commit()
        return True
    # 老用户：仅在提供新昵称/头像时更新
    if nick or avatar:
        db.execute(
            text("""UPDATE user_profiles
                    SET nick_name = CASE WHEN :n='' THEN nick_name ELSE :n END,
                        avatar_url = CASE WHEN :a='' THEN avatar_url ELSE :a END,
                        last_active = :t
                    WHERE user_id=:u"""),
            {"u": openid, "n": nick or "", "a": avatar or "", "t": datetime.now(timezone.utc)},
        )
    else:
        db.execute(
            text("UPDATE user_profiles SET last_active=:t WHERE user_id=:u"),
            {"u": openid, "t": datetime.now(timezone.utc)},
        )
    db.commit()
    return False


@router.post("/wx-login", response_model=LoginResp)
async def wx_login(req: WxLoginReq):
    if app_settings.auth_disabled:
        # 鉴权关闭：wx-login 退化为 dev-login 行为（避免游客模式卡死）
        token = sign_token(req.code or "wx_dev_user")
        return LoginResp(token=token, user_id="wx_dev_user", openid="wx_dev_user", is_new=False)

    try:
        data = await exchange_openid(req.code)
    except WxConfigError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    except WxLoginError as exc:
        raise HTTPException(400, detail=str(exc)) from exc

    openid = str(data.get("openid", ""))
    db = SessionLocal()
    try:
        is_new = _upsert_profile(db, openid, req.nick_name, req.avatar_url)
    finally:
        db.close()
    token = sign_token(openid)
    return LoginResp(token=token, user_id=openid, openid=openid, is_new=is_new)


@router.post("/dev-login", response_model=LoginResp)
def dev_login(req: DevLoginReq):
    """开发模式免鉴权直登：仅当 MOYAN_AUTH_DISABLED=1 且非生产环境接受（ADMIN-03 双保险）。"""
    if app_settings.is_production:
        raise HTTPException(403, detail="dev-login 在生产环境不可用")
    if not app_settings.auth_disabled:
        raise HTTPException(403, detail="dev-login 仅在 MOYAN_AUTH_DISABLED=1 时可用")

    openid = f"dev_{req.dev_openid}"
    db = SessionLocal()
    try:
        is_new = _upsert_profile(db, openid, "", "")
    finally:
        db.close()
    token = sign_token(openid)
    return LoginResp(token=token, user_id=openid, openid=openid, is_new=is_new)


@router.post("/register", response_model=LoginResp)
def register(req: RegisterReq):
    """网页版邮箱密码注册：落档 user_profiles（auth_type='web'），直接签 token。"""
    db = SessionLocal()
    try:
        exists = db.execute(
            text("SELECT user_id FROM user_profiles WHERE email=:e"),
            {"e": req.email},
        ).first()
        if exists is not None:
            raise HTTPException(409, detail="该邮箱已注册")

        user_id = f"web_{uuid.uuid4().hex[:10]}"
        try:
            db.execute(
                text("""INSERT INTO user_profiles
                        (user_id, auth_type, email, password_hash, nick_name, avatar_url,
                         created_at, last_active)
                        VALUES (:u, 'web', :e, :p, :n, '', :t, :t)"""),
                {"u": user_id, "e": req.email, "p": hash_password(req.password),
                 "n": req.nick_name or req.email.split("@")[0],
                 "t": datetime.now(timezone.utc)},
            )
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, detail="该邮箱已注册")
    finally:
        db.close()
    token = sign_token(user_id)
    return LoginResp(token=token, user_id=user_id, openid=user_id, is_new=True)


@router.post("/login", response_model=LoginResp)
def login(req: LoginReq):
    """网页版邮箱密码登录。401 不区分"邮箱不存在"与"密码错误"（防枚举）。"""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT user_id, password_hash FROM user_profiles WHERE email=:e"),
            {"e": req.email},
        ).first()
        stored = row[1] if row else _DUMMY_HASH
        # 无论"邮箱不存在"还是"密码错误"都跑一次 scrypt 校验，响应时间一致
        if row is None or not verify_password(req.password, stored):
            raise HTTPException(401, detail="邮箱或密码错误")
        user_id = row[0]
        db.execute(
            text("UPDATE user_profiles SET last_active=:t WHERE user_id=:u"),
            {"u": user_id, "t": datetime.now(timezone.utc)},
        )
        db.commit()
    finally:
        db.close()
    token = sign_token(user_id)
    return LoginResp(token=token, user_id=user_id, openid=user_id, is_new=False)


@router.get("/me", response_model=MeResp)
def me(user: CurrentUser = Depends(get_current_user)):
    db = SessionLocal()
    try:
        row = db.execute(
            text("""SELECT user_id, created_at, last_active,
                          (SELECT COUNT(*) FROM teaching_sessions WHERE user_id=:u) AS sessions
                   FROM user_profiles WHERE user_id=:u"""),
            {"u": user.openid},
        ).first()
    finally:
        db.close()
    if row is None:
        # 真没在 profiles 但 token 合法：兜底（罕见）
        return MeResp(
            user_id=user.openid,
            openid=user.openid,
            created_at=datetime.now(timezone.utc).isoformat(),
            sessions=0,
            last_active=None,
            role=user.role,
        )

    def _iso(v) -> str | None:  # noqa: ANN001
        """SQLite 存 TEXT 返 str，PG 返 datetime —— 统一 ISO 字符串。"""
        if v is None:
            return None
        return v.isoformat() if hasattr(v, "isoformat") else str(v)

    return MeResp(
        user_id=row[0],
        openid=row[0],
        created_at=_iso(row[1]) or "",
        sessions=int(row[3] or 0),
        last_active=_iso(row[2]),
        role=user.role,
    )
