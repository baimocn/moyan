# STACK — 技术栈与依赖

*Last updated: 2026-09-04*

## 后端（backend/，Python）

| 项 | 值 | 来源 |
|---|---|---|
| 语言/运行时 | Python 3.12（生产 venv）/ 3.11+ | `deploy/run-prod.sh` |
| Web 框架 | FastAPI >=0.115 + uvicorn[standard]（生产 1 worker，`--timeout-keep-alive 75`） | `requirements.txt`, systemd unit |
| ORM/DB | SQLAlchemy >=2.0（DeclarativeBase），开发 SQLite `data/moyan_dev.db`，生产 PostgreSQL16 | `backend/models/db.py` |
| DB 驱动 | psycopg2-binary >=2.9 | `requirements.txt` |
| 鉴权 | PyJWT >=2.8（HS256，sub=openid，7d）；小程序侧 jscode2session；网页版 scrypt 密码 | `backend/auth/jwt.py`, `backend/auth/wx.py`, `backend/auth/passwords.py` |
| 限流 | slowapi >=0.1.9（key_func 按 openid/设备维度，5 档） | `backend/rate_limit.py` |
| AI 引擎 | openai >=2.0 SDK（OpenAI 兼容协议，DeepSeek）+ instructor >=1.15 结构化输出 + pydantic >=2.10 | `backend/engine/providers.py` |
| 记忆调度 | fsrs >=6.3（间隔重复） | `backend/engine/review/service.py` |
| 解析 | docling（主引擎，独立 venv `.docling-venv/` + `tools/docling_worker.py` 子进程）；pymupdf、rapidocr_onnxruntime、onnxruntime、pillow | `backend/services/docling_adapter.py`, `backend/config.py` |

## 前端 A：微信小程序 + H5（frontend/，uni-app）

- uni-app 3.0.0-alpha（`@dcloudio/uni-app` 等 5 包同版本）+ Vue 3.4.21，vite 构建
- 单工程双编译：`npm run build:mp-weixin` → `dist/build/mp-weixin`（微信开发者工具导入）；H5 走 5173 dev server
- 富文本渲染 mp-html；条件编译三处语法：template `<!-- #ifdef H5 -->`、style `/* #ifdef H5 */`、JS `// #ifdef MP-WEIXIN`
- 用户侧存储：`uni.setStorageSync` 仅存 `moyan:last`（进度记忆）+ token/user_id（`frontend/src/utils/auth.js`）

## 前端 B：网页版（frontend-web/，Vue3 + Vite）

- Vue ^3.5.13 + vue-router ^4.5.0 + pinia ^2.2.6 + vite ^5.4.11
- 三个视图：`frontend-web/src/views/HomeView.vue`（共享书架+搜索）、`TutorView.vue`（SSE 教学）、`LoginView.vue`
- dev 端口 5174，vite 代理 `/api` → 127.0.0.1:5001

## 配置体系

- 唯一事实源：`backend/settings.py` 的 `app_settings`（pydantic-settings），`MOYAN_*` 环境变量 / `.env` 覆盖
- `backend/config.py` 只保留路径常量与从 settings 复读的值（UPLOAD/MARKDOWN/CHAPTERS/WORK 目录、OCR 参数、SUPPORTED_FORMATS）
- 关键 env：`MOYAN_DB_URL`、`MOYAN_AI_*`（模型/key/并发）、`AUTH_DISABLED`、`ADMIN_*`（M2 计划新增）
- 生产 env 在服务器 `/opt/moyan/.env`（CRLF 行尾，勿 bash source）

## 运行方式

- 开发：`uvicorn backend.main:app --port 5001` + 前端各自 dev server
- 生产：systemd `moyan.service`（uvicorn @127.0.0.1:5001）+ nginx 443→5001（`/etc/nginx/sites-enabled/moyan`）；`deploy/` 是 Caddy 备选方案（未启用）
