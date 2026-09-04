"""墨衍 · FastAPI 入口（服务器模式）

启动：uvicorn backend.main:app --host 127.0.0.1 --port 5001
静态调试台（backend/static）由 FastAPI 托管，后续被 uni-app H5 取代。
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from . import config, tasks
from .auth.router import router as auth_router
from .models import init_db
from .rate_limit import _rate_limit_handler, limiter
from .routers import admin, documents, metrics, study, tasks as tasks_router, tutor, upload
from .settings import app_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    config.ensure_dirs()
    init_db()                     # 建表（幂等）
    tasks.start_worker()          # 拉起后台 OCR 单 worker
    from . import settings
    from .container import services
    from .settings import apply_production_safety
    apply_production_safety()     # ADMIN-03：生产环境强制关闭免鉴权（fail-safe）
    print(f"墨衍 API 已启动（环境：{app_settings.env}；数据库：{settings.db_settings.db_url.split('://')[0]}；"
          f"AI 引擎：{'READY' if settings.ai_settings.engine_ready else '未配置'}"
          f"{'（mock 演示）' if services.mock else ''}；"
          f"鉴权：{'关闭' if app_settings.auth_disabled else '开启'}；"
          f"管理员：{len(app_settings.admin_set)} 人；"
          f"限流：user_id 主 / IP 兑底）")
    yield


app = FastAPI(title="墨衍 · AI 导师 API", version="0.4.0", lifespan=lifespan)

# 限流（slowapi）：挂全局异常处理 + Limiter 实例
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# 鉴权优先挂载（其他业务路由可 Depends(get_current_user））
app.include_router(auth_router)
app.include_router(upload.router)
app.include_router(documents.router)
app.include_router(tasks_router.router)
app.include_router(tutor.router)
app.include_router(study.router)
app.include_router(metrics.router)
app.include_router(admin.router)

# 双前端地基（2026-08-29）：跨源白名单（MOYAN_CORS_ORIGINS，逗号分隔）。
# 默认空 = 行为与从前完全一致（仅同源）；小程序 wx.request 不走浏览器 CORS，不受此影响。
_origins = [o.strip() for o in (app_settings.cors_origins or "").split(",") if o.strip()]
if _origins:
    app.add_middleware(CORSMiddleware, allow_origins=_origins,
                       allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    from . import settings
    from .container import services
    return {
        "status": "ok",
        "db": settings.db_settings.db_url.split("://")[0],
        "engine_ready": settings.ai_settings.engine_ready,
        "engines": [e[0] for e in settings.ai_settings.engines()] or [],
        "mock": services.mock,
        "workers": "ocr-enabled",
    }

# 调试静态页（先挂根；后续 uni-app 独立前端工程会替换）
app.mount("/", StaticFiles(directory=str(config.STATIC_DIR), html=True), name="static")