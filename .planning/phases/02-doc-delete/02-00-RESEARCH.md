# Phase 2 Research — 文档删除与联级清理（inline，2026-09-04）

## 现状事实

1. `DELETE /api/documents/{doc_id}` 不存在；`PATCH`（rename）是普通用户功能不动（Phase 1 定论）。
2. **外键链（PG 生产强制约束）**：`teaching_sessions.doc_id → documents.doc_id`（FK）、`turns.session_id → sessions.id`（FK）、`judgements.session_id → sessions.id`（FK）；`tasks.doc_id → documents.doc_id`（FK）。`weaknesses.doc_id`、`strategy_logs.doc_id` 仅索引无 FK。
3. 文件产物：`data/markdown/{doc_id}.md`、`data/chapters/{doc_id}/`（章节+plan 缓存）、`data/uploads/{doc_id}/`（空壳或未清理原件）。
4. 生产是 PostgreSQL → **必须按 FK 顺序删**：turns/judgements → sessions → tasks → documents。SQLite 开发库默认不强制 FK，但代码必须按能过 PG 的写法。

## 方案

- **级联删除**（而非拒绝删除）：管理员删书=明确意图，连带该书的学习记录（会话/轮次/判定/弱点/策略日志）。UI 确认弹层写明"连同学习记录一起删除"。
- 删除顺序（单事务）：`turns`、`judgements`（按 session_id ∈ 该书 sessions）→ `weaknesses`/`strategy_logs`（按 doc_id）→ `teaching_sessions`（按 doc_id）→ `tasks`（按 doc_id）→ `documents` 行。
- 文件清理放 DB 事务提交**之后**（尽力删，文件缺失不回滚——幂等）。
- 404 语义：doc 不存在 → 404「文档不存在」；重复删除天然 404（幂等）。
- content_hash 行随文档删除 → 同书之后可重新完整上传（去重不受污染）。
- 前端（frontend-web，小程序冻结不碰）：登录用户拉 `/api/auth/me` 得 role；admin 在书架卡片上显示「删除」按钮 + 确认弹层；删除后 refresh。

## 决策

- 不做软下架（v2 deferred，用户未选）；不做"上传者删除"（无上传者语义）。
- require_admin 首个真实挂载点 = 本端点（Phase 1 机制就位）。
