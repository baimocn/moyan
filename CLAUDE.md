<!-- GSD:project-start source:PROJECT.md -->

## Project

**墨衍 · 项目上下文（PROJECT.md）**

墨衍——AI 辅导应用（"AI 同桌"人设）：用户上传教材 PDF/文档，系统解析成章节，AI 按"先思路后对答案"的方式一章一章带着学，带判定、出题、弱点记录与 FSRS 复习。

**双前端 · 一后端 · 数据共享**的多生态架构：

- **微信小程序**（uni-app 单工程双编译出小程序+H5）——已上线（体验版 0.2.1，2026-09-04 审核中），AppID `wx9ca2b10b07573b3d`（个人主体）
- **网页版**（Vue3 独立工程 frontend-web/）——已上线 https://moyan.baimo7715.top，免登录 + 共享书库（任何人可用，同书 sha256 去重秒回）
- **硬性约束**：两个前端代码零共享、独立可用，"一个坏了不影响另一个"；后端与数据层唯一

**Core Value:** 用户能上传一本教材 → 选章节 → 与 AI 同桌进行"讲思路→判定→出题→汇报"的真实学习循环，且学习进度跨设备可续。
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## 后端（backend/，Python）

| 项 | 值 | 来源 |
|---|---|---|
| 语言/运行时 | Python 3.12（生产 venv）/ 3.11+ | `deploy/run-prod.sh` |
| Web 框架 | FastAPI >=0.115 + uvicorn[standard]（生产 1 worker，`--timeout-keep-alive 75`） | `requirements.txt`, systemd unit |
| ORM/DB | SQLAlchemy >=2.0（DeclarativeBase），开发 SQLite `data/moyan_dev.db`，生产 PostgreSQL16 | `backend/models/db.py` |
| DB 驱动 | psycopg2-binary >=2.9 | `requirements.txt` |
| 鉴权 | PyJWT >=2.8（HS256，sub=openid，7d）；小程序侧 jscode2session；网页版 scrypt 密码 | `backend/auth/jwt.py`, `backend/auth/wx.py`, `backend/auth/passwords.py` |
| 限流 | slowapi >=0.1.9（真实 openid 按 user:，匿名 web_* 回落 ip:） | `backend/rate_limit.py` |
| 迁移 | alembic >=1.13（schema 变更唯一通道，0001-0003） | `migrations/` |
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
- 关键 env：`MOYAN_DB_URL`、`MOYAN_AI_*`、`MOYAN_AUTH_DISABLED`、`MOYAN_ADMIN_OPENIDS`、`MOYAN_GEN_MAX_TOKENS`、`MOYAN_DAILY_TOKEN_BUDGET/HARD`、`MOYAN_MODERATION_FAIL_OPEN`、`MOYAN_UPLOAD_DEFAULT_SHARED`
- 生产 env 在服务器 `/opt/moyan/.env`（CRLF 行尾，勿 bash source）

## 运行方式

- 开发：`uvicorn backend.main:app --port 5001` + 前端各自 dev server
- 生产：systemd `moyan.service` + nginx 443→5001；Caddy 已弃用；`moyan-smoke.timer` 冒烟探针（scripts/smoke_probe.py）

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## 语言与注释

- 代码注释与文档**全中文**；docstring 风格 `"""墨衍 · 主题（补充说明）"""`
- 提交信息中文，格式 `feat|fix|chore(scope): 摘要` + 空行 + 正文要点（见 git log）

## 后端（FastAPI）

- 路由函数：`@router.<method>("路径")` + Pydantic schema 入参出参（`backend/engine/schemas.py`、`backend/auth/schemas.py`）
- **slowapi 铁律**：限流装饰器修饰的函数第一个参数必须是 `request: Request`（slowapi 内部读 self），否则运行时炸
- 身份获取：一律通过 `Depends(get_requester)`（`backend/auth/deps.py`），返回 `CurrentUser(openid, role)`；**不要**在路由里自己解析 token
- 配置读取：从 `backend/settings.py` 的 `app_settings` 取；新 env 键用 `MOYAN_` 前缀 + `setdefault`（注意跨模块 setdefault 顺序坑，测试里必须 monkeypatch 显式控制）
- DB 访问：`backend/models/repo.py` 集中数据访问；**schema 变更一律走 alembic**（幂等迁移，生产 stamp/upgrade）
- **会话端点红线**：接受 session_id 的新端点必须做归属校验（`repo.session_owned_by`），非 owner 404；并发走 `try_begin_turn` 409
- **上传审核 fail-closed**：moderation 异常拒收 503；测试必须 `--basetemp=out/_pytest_tmp`，改模型后删 test_dev.db 重建
- 错误处理：HTTPException 带中文 detail；SSE 错误以 `event: error` 下发而非 HTTP 错误码
- 子进程（docling）：必须经 `docling_adapter._run_worker` 启动（剥代理 env + 离线 HF 变量），不要直接 subprocess

## 前端（uni-app 小程序）

- 条件编译三语法：template `<!-- #ifdef H5 -->`、style `/* #ifdef H5 */`、JS `// #ifdef MP-WEIXIN`
- 所有请求走 `frontend/src/utils/api.js`（Bearer 注入 + 401 静默重试；SSE 双通道：H5 fetch/ReadableStream，MP wx.request+enableChunked，同一 onEvent 回调）
- 本地存储仅限 `moyan:` 前缀键（moyan:last / moyan:token / moyan:user_id / moyan:openid）
- UI 设计语言：墨绿 #163628 + 米纸 #f6f2e8 + 暖米 #fffdf8；字号 rpx；中文文案口语化（"同桌"人设）

## 前端（frontend-web）

- pinia store（`stores/auth.js`）+ 纯函数 API 模块（`src/api/*.js`），client.js 统一注入 `X-Device-Id`（localStorage 持久化）
- 视图组件放 `views/`，路由无强制登录守卫（免登录产品语义）

## Git

- 主干开发（无分支流程），push 用 `git -c http.proxy= -c https.proxy= push`（沙箱代理会 502）
- 提交前跑 `git diff --name-only | grep -E "^backend/|^frontend-web/"` 之类校验改动范围（双前端独立性验收）

## 安全约定

- 任何密钥/AppID Secret/生产连接串**不入库**（.gitignore 已强化：*.key/*.pem/api_keys/.env）
- out/ 目录不进 git（历史遗留含生产密钥副本文件，待用户处置）

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## 总体模式：单后端 + 双前端（同源 API，前端独立部署）

```

```

- 两前端**零代码共享**（各自独立工程），仅共享后端 API 与数据；一方坏了不影响另一方（用户硬性要求）
- 后端无会话粘性：所有教学状态在 DB（teaching_sessions/turns），前端可刷新续学

## 后端分层（backend/）

| 层 | 位置 | 职责 |
|---|---|---|
| 入口 | `backend/main.py` | FastAPI app + lifespan（init_db）+ 挂 6 个 router（auth/upload/documents/tasks/tutor/study） |
| 路由 | `backend/routers/` | HTTP 协议层：参数校验、限流（slowapi）、身份注入 |
| 身份 | `backend/auth/deps.py` | `get_requester` 三态依赖：Bearer JWT → 真实用户；`X-Device-Id` → `web_<did>`；兜底 `web_anon`。**写端点不强鉴权**（免登录设计） |
| 服务 | `backend/services/` | 解析域：docling_adapter（子进程管理）、chapter_splitter、ocr_engine、pdf_parser、lines_pipeline |
| 引擎 | `backend/engine/` | 教学域：tutor/（actions.py 状态机 + session.py + service.py）、judge/quiz/persona/reviewer、review/service.py（FSRS）、prompts.py（全部提示词）、providers.py（AI 客户端） |
| 任务 | `backend/tasks.py` | 异步解析管线：上传 → docling → 章节 → proofread → cleanup_original → status=done |
| 模型 | `backend/models/` | SQLAlchemy 2.0：Document / Task / TeachingSession / Turn / Judgement / Weakness / StrategyLog / UserProfile；`repo.py` 数据访问 |
| 存储 | `backend/storage.py` | 文件系统布局 + 章节清单读写 + 学习计划（plan）缓存 |

## 核心数据流

### 1. 文档上架流（POST /api/upload）

```

```

### 2. 教学对话流（POST /api/tutor/turn，SSE）

```

```

### 3. 复习流（review/）

## 关键抽象

- **doc_id**：`YYYYMMDD-HHMMSS-6位hex`，贯穿 DB 行、文件目录、任务
- **plan 缓存**：`storage.py save_learning_plan` —— LLM 章节知识点计划落 JSON（~80s 生成成本，只该算一次）
- **限流键**：`backend/rate_limit.py` 优先 `request.state.user.openid`，匿名按设备头隔离

## 入口点

- 后端：`backend.main:app`（uvicorn）
- 小程序：`frontend/src/pages/index/index.vue`（书架）→ `pages/tutor/`（教学）
- 网页版：`frontend-web/src/main.js` → router.js → HomeView / TutorView / LoginView

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
