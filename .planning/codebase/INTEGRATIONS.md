# INTEGRATIONS — 外部集成

*Last updated: 2026-09-04*

## AI 引擎（DeepSeek，OpenAI 兼容协议）

- 客户端封装：`backend/engine/providers.py` —— 单例 provider，环境变量 `MOYAN_AI_*` 配置 base_url/api_key/model
- 调用形态两类：
  1. **SSE 流式**（教学对话）：`backend/routers/tutor.py` → `backend/engine/tutor/actions.py`，事件 type：reasoning-delta / text-delta / meta / judge / question / question-batch / report / error
  2. **结构化输出**（判定/出题/校对/复习计划）：instructor 约束 pydantic schema（`backend/engine/structured.py`）
- **坑**：沙箱/WorkBuddy 环境注入 http_proxy 会致 docling 子进程 ProxyError——`docling_adapter._run_worker` 剥代理 env；后端 AI 调用需保留代理
- **缺口**：AI 响应的 usage（prompt/completion tokens）未记录——成本不可见（M2 待补 `ai_usage` 表）

## 微信生态

| 集成 | 位置 | 说明 |
|---|---|---|
| jscode2session | `backend/auth/wx.py`（httpx 调 api.weixin.qq.com） | AppID `wx9ca2b10b07573b3d`（个人主体），Secret 在生产 `/opt/moyan/.env` 不入库 |
| 上传域名白名单 | 微信后台配置 | request/uploadFile 均需 `https://moyan.baimo7715.top`（2026-09-04 已配，真机验证通过） |
| 提审/发布 | 无 API | 个人小程序无提审 API，只能后台手动 |

## 数据库

- 开发：SQLite `data/moyan_dev.db`；生产：PostgreSQL 16（`moyan` 库，连接串 `MOYAN_DB_URL`）
- 迁移策略：`backend/models/db.py` 的 `_TABLE_ADDITIONS` 在 `init_db()`（uvicorn lifespan 触发）时自动 ALTER TABLE 加列——仅支持加列，不支持改型/删列
- 注意：`backend/db.py` 是 Flask 时代死代码（读 `config.DATABASE_URL` 会炸），生产查库用 `sudo -u postgres psql moyan`

## HTTP 服务链

- 生产：nginx（443, TLS certbot + 阿里云双 CA 软链切换）→ 127.0.0.1:5001（uvicorn，HTTP/1.1）
- 关键 nginx 配置：`location /api/` 反代 + `proxy_buffering off`（SSE 必需）；`location /` 静态 frontend-web（index.html `no-cache`，assets `immutable 30d`）
- wx.request 强制 HTTP/2 → nginx keepalive 必须配 uvicorn `--timeout-keep-alive 75` ≥ proxy_read_timeout，否则随机 network error

## 文件存储（本地磁盘，无对象存储）

```
data/uploads/{doc_id}/{原文件}      原件（解析完成后 cleanup_original 删除）
data/markdown/{doc_id}.md           docling 转换产物
data/chapters/{doc_id}/chapter_XXX.md + chapters.json + plan_{n}.json 缓存
data/work/                          OCR 中间产物
```

## 无外部集成的部分

- 无对象存储/OSS、无消息队列、无 CDN、无统计 SDK（M2 计划自建 `page_views` 表埋点）、无邮件/短信服务
