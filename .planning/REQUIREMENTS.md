# REQUIREMENTS — 下一阶段（M2 管理底座 / M3 向量知识库）

*Created: 2026-09-04 · 来源：out/下一阶段方向设计_M2管理底座_M3向量库.md + 用户决策（2026-09-04）*

约束背景：小程序 0.2.1 审核中（代码冻结期），M2 全部为后端 + frontend-web 改动，不碰 `frontend/`。

## v1 Requirements

### ADMIN — 权限分层

- [ ] **ADMIN-01**: `get_requester` 返回值携带 role（admin/user/anon），管理员由 env `ADMIN_OPENIDS` 清单（逗号分隔 openid）判定，用户可在文档中写明配置方法
- [ ] **ADMIN-02**: 破坏性写操作（文档 DELETE 等）要求 role=admin，非 admin 返回 403（中文 detail）
- [ ] **ADMIN-03**: 生产安全硬校验：AUTH_DISABLED=1 或 dev-login 在生产配置（AUTH_DISABLED=0 且配了真实域）时自动禁用并打日志，防误开

### DOC — 文档删除

- [ ] **DOC-01**: `DELETE /api/documents/{doc_id}`（admin only）联级清理：documents 行、tasks 关联行、`data/markdown/{doc_id}.md`、`data/chapters/{doc_id}/` 整目录、`data/uploads/{doc_id}/` 残留
- [ ] **DOC-02**: 删除不存在的 doc_id 返回 404；幂等重删返回 404（不做软删除，v2 再议）
- [ ] **DOC-03**: 网页版书架对 admin 显示删除入口（确认弹层），删除后列表即时刷新

### MOD — 上传内容安全审核（2026-09-04 新增，已上线）

- [x] **MOD-01**: 文本产出后、付费 AI 步骤（校对）与上架前，用粗活引擎 json_mode 一次判定；黄赌毒等违禁 → 同步路径 422 / 异步任务 status=rejected+task failed，产物不落盘；fail-open（审核异常放行+warnings 留痕）；mock/未配引擎/MOYAN_MODERATION=0 跳过；通过则 stats.moderation 留痕（verdict/category/reason/engine）

### COST — 成本可见

- [x] **COST-01**: `ai_usage` 统一台账（providers/structured 出口自动记账，ai_scope 标注 endpoint，重试/failover 各记一行）；`GET /api/admin/usage` 按天×endpoint×模型聚合（2026-09-04 上线，只记 tokens 不估金额——用户用套餐）

### STATS — 浏览量统计（双前端共用，有人点进来就算）

- [x] **STATS-01**: `POST /api/metrics/pv`（免鉴权、fire-and-forget）：body `{source: web|mp, page, device_id}`，写入 `page_views(id, ts, source, page, device_id)`
- [x] **STATS-02**: 网页端 router.afterEach sendBeacon 上报已上线；小程序侧代码已备好（docs/待合入-小程序埋点.md），0.2.1 审核通过后合入
- [x] **STATS-03**: 统计接口 `GET /api/admin/stats`（admin only）：今日/累计 PV、UV、来源分布、教学轮次数、文档数、token 消耗（金额估算按用户决策不做）

### ADMINUI — 管理后台页

- [ ] **ADMINUI-01**: frontend-web 新增 `/admin` 路由：非 admin 访问显示"无权限"（判定依据：登录后 openid ∈ ADMIN_OPENIDS，由 /me 或专用接口返回 role）
- [ ] **ADMINUI-02**: 文档管理视图：列表（标题/状态/大小/上传时间）+ 删除按钮（确认弹层）+ 改名
- [ ] **ADMINUI-03**: 统计面板：数字卡展示 STATS-03 全部指标（简单数字卡，不引图表库）

### VEC — 向量知识库（场景：学生提问超出当前章时检索全书相关段落补上下文）

- [ ] **VEC-01**: pgvector 扩展启用 + `document_chunks` 表（doc_id, chapter_index, chunk_text, embedding vector）+ 章节切片嵌入管线（云端 embedding API，批次处理）
- [ ] **VEC-02**: 嵌入成本护栏：全库嵌入前估算成本并打日志；单价与模型写 env
- [ ] **VEC-03**: 检索接口（内部）：按当前文档 + 查询文本取 top-k 相关切片
- [ ] **VEC-04**: 教学引擎注入：turn 处理中当学生提问疑似超章时检索并作为参考上下文注入 prompt（受开关控制，默认可关）
- [ ] **VEC-05**: 删除文档时联级清 `document_chunks`（挂在 DOC-01 的清理链上）

## v2 Requirements（deferred）

- 软下架（对用户隐藏但保留数据）
- PV 按天聚合归档表（明细大后）
- 上传者删除自己上传的书（需引入"上传者"语义）
- 管理页图表可视化

## Out of Scope

- users.role 表级 RBAC——env 清单已满足单管理员现实
- 本地 embedding 模型——2C2G 内存不允许
- 对象存储/CDN——无必要
- 小程序端管理界面——管理后台只做网页版（管理员场景在桌面）

## Traceability

*(filled by roadmap, 2026-09-04)*

| Requirement | Phase | Status |
|---|---|---|
| ADMIN-01..03 | Phase 1 权限分层与生产安全硬校验 | pending |
| DOC-01..03 + VEC-05（清理链挂点） | Phase 2 文档删除与联级清理 | pending |
| COST-01, STATS-01..03 | Phase 3 用量观测 | pending |
| ADMINUI-01..03 | Phase 4 管理后台页 | pending |
| VEC-01..03 | Phase 5 向量知识库底座 | pending |
| VEC-04 | Phase 6 检索注入教学引擎 | pending |
