"""墨衍 · FastAPI 入口（服务器模式）

启动：uvicorn backend.main:app --host 127.0.0.1 --port 5001
静态调试台（backend/static）由 FastAPI 托管，后续被 uni-app H5 取代。
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config, tasks
from .models import init_db
from .routers import documents, study, tasks as tasks_router, tutor, upload
from .settings import app_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    config.ensure_dirs()
    init_db()                     # 建表（幂等）
    tasks.start_worker()          # 拉起后台 OCR 单 worker
    from . import settings
    from .container import services
    print(f"墨衍 API 已启动（数据库：{settings.db_settings.db_url.split('://')[0]}；"
          f"AI 引擎：{'READY' if settings.ai_settings.engine_ready else '未配置'}"
          f"{'（mock 演示）' if services.mock else ''}）")
    yield


app = FastAPI(title="墨衍 · AI 导师 API", version="0.3.0", lifespan=lifespan)

app.include_router(upload.router)
app.include_router(documents.router)
app.include_router(tasks_router.router)
app.include_router(tutor.router)
app.include_router(study.router)

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