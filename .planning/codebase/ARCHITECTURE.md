# ARCHITECTURE — 架构模式与数据流

*Last updated: 2026-09-04*

## 总体模式：单后端 + 双前端（同源 API，前端独立部署）

```
微信小程序（uni-app 编译）──┐
                            ├──► FastAPI @127.0.0.1:5001 ──► PostgreSQL16
网页版 SPA（Vue3，nginx）──┘         │
                                    ├──► DeepSeek（OpenAI 兼容，流式/结构化）
                                    └──► docling 子进程（.docling-venv，解析 PDF→md）
```

- 两前端**零代码共享**（各自独立工程），仅共享后端 API 与数据；一方坏了不影响另一方（用户硬性要求）
- 后端无会话粘性：所有教学状态在 DB（teaching_sessions/turns），前端可刷新续学

## 后端分层（backend/）

| 层 | 位置 | 职责 |
|---|---|---|
| 入口 | `backend/main.py` | FastAPI app + lifespan（init_db）+ 挂 7 个 router（auth/upload/documents/tasks/tutor/study/admin/metrics）+ `/api/privacy` |
| 路由 | `backend/routers/` | HTTP 协议层：参数校验、限流（slowapi）、身份注入 |
| 身份 | `backend/auth/deps.py` | `get_requester` 三态依赖：Bearer JWT → 真实用户；`X-Device-Id` → `web_<did>`；兜底 `web_anon`。**写端点不强鉴权**（免登录设计） |
| 服务 | `backend/services/` | 解析域：docling_adapter（子进程管理）、chapter_splitter、ocr_engine、pdf_parser、lines_pipeline |
| 引擎 | `backend/engine/` | 教学域：tutor/（actions.py 状态机 + session.py + service.py）、judge/quiz/persona/reviewer、review/service.py（FSRS）、prompts.py（全部提示词）、providers.py（AI 客户端） |
| 任务 | `backend/tasks.py` | 异步解析管线：上传 → docling → 章节 → proofread → cleanup_original → status=done |
| 模型 | `backend/models/` | SQLAlchemy 2.0：Document(+shared) / Task / TeachingSession / Turn / Judgement / Weakness / StrategyLog / UserProfile / AiUsage / PageView / DocumentChunk；`repo.py` 数据访问；schema 变更走 alembic（migrations/，2026-09-05 起） |
| 存储 | `backend/storage.py` | 文件系统布局 + 章节清单读写 + 学习计划（plan）缓存 |

## 核心数据流

### 1. 文档上架流（POST /api/upload）
```
multipart 上传 → sha256 流式计算 → content_hash 命中已 done 文档?
  ├─ 是 → 返回 reused:true（不落盘，共享书库去重）
  └─ 否 → save_upload → Task(status=processing) → docling 子进程转 md
          → chapter_splitter 切章 → save_chapters → proofread → cleanup_original（删原件）
          → status=done；前端 pollTask 轮询
```

### 2. 教学对话流（POST /api/tutor/turn，SSE）
```
turn 请求（session_id + 用户输入）→ tutor/actions.py 状态机（讲知识点→判定→出题→汇报）
  → providers.py 流式调 DeepSeek → yield SSE 事件（text-delta/reasoning-delta/judge/question/report…）
  → 每轮落 Turn/Judgement/Weakness/StrategyLog
前端：H5 fetch+ReadableStream；小程序 wx.request+enableChunked；api.js 同一 onEvent 回调分发
```

### 3. 复习流（review/）
FSRS 间隔重复调度弱点知识点，`review/service.py` 生成复习计划。

## 关键抽象

- **doc_id**：`YYYYMMDD-HHMMSS-6位hex`，贯穿 DB 行、文件目录、任务
- **plan 缓存**：`storage.py save_learning_plan` —— LLM 章节知识点计划落 JSON（~80s 生成成本，只该算一次）
- **限流键**：`backend/rate_limit.py` 真实用户按 openid，匿名 web_* 一律回落 IP（自报设备头可旋转，2026-09-05）；SEC-04 日预算熔断（soft 降 cheap / hard 429）

## 入口点

- 后端：`backend.main:app`（uvicorn）
- 小程序：`frontend/src/pages/index/index.vue`（书架）→ `pages/tutor/`（教学）
- 网页版：`frontend-web/src/main.js` → router.js → HomeView / TutorView / LoginView / AdminView / PrivacyView
- 运维：systemd `moyan-smoke.timer` → `scripts/smoke_probe.py`（探针记录 `/api/admin/smoke`）
