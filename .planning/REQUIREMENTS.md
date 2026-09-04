# REQUIREMENTS — 下一阶段（M2 管理底座 / M3 向量知识库）

*Created: 2026-09-04 · 来源：out/下一阶段方向设计_M2管理底座_M3向量库.md + 用户决策（2026-09-04）*

约束背景：小程序 0.2.1 审核中（代码冻结期），M2 全部为后端 + frontend-web 改动，不碰 `frontend/`。

## v1 Requirements

### ADMIN — 权限分层

- [x] **ADMIN-01**: `get_requester` 返回值携带 role（admin/user/anon），管理员由 env `MOYAN_ADMIN_OPENIDS` 清单（逗号分隔 openid）判定（2026-09-04 生产已配置）
- [x] **ADMIN-02**: 破坏性写操作（文档 DELETE 等）要求 role=admin，非 admin 返回 403（中文 detail）
- [x] **ADMIN-03**: 生产安全硬校验：AUTH_DISABLED=1 或 dev-login 在生产配置（AUTH_DISABLED=0 且配了真实域）时自动禁用并打日志，防误开

### DOC — 文档删除

- [x] **DOC-01**: `DELETE /api/documents/{doc_id}`（admin only）联级清理：documents 行、tasks 关联行、`data/markdown/{doc_id}.md`、`data/chapters/{doc_id}/` 整目录、`data/uploads/{doc_id}/` 残留（Phase 5 起含 document_chunks）
- [x] **DOC-02**: 删除不存在的 doc_id 返回 404；幂等重删返回 404（不做软删除，v2 再议）
- [x] **DOC-03**: ~~网页版书架对 admin 显示删除入口~~ **（REN-01 决策推翻：删除收敛到管理台，用户层书架不再显示删除按钮，管理员也统一去 /admin 删）**

### REN — 重命名 AI 审核（2026-09-04 新增，本地已上线）

- [x] **REN-01**: 用户层重命名保留，但非 admin 改名需先过「新名称-内容相符」AI 审核（头部2500字+章节清单→cheap 引擎 json_mode；相符标准宽泛：主题/别名/课程名/简称都算，只拒明显风马牛不相及）；不符 422 并给理由；admin 绕过；审核异常 fail-open；mock/未配引擎/MOYAN_RENAME_REVIEW=0 跳过；审核消耗入 ai_usage（scope=title_check）

### MOD — 上传内容安全审核（2026-09-04 新增，已上线）

- [x] **MOD-01**: 文本产出后、付费 AI 步骤（校对）与上架前，用粗活引擎 json_mode 一次判定；黄赌毒等违禁 → 同步路径 422 / 异步任务 status=rejected+task failed，产物不落盘；fail-open（审核异常放行+warnings 留痕）；mock/未配引擎/MOYAN_MODERATION=0 跳过；通过则 stats.moderation 留痕（verdict/category/reason/engine）

### COST — 成本可见

- [x] **COST-01**: `ai_usage` 统一台账（providers/structured 出口自动记账，ai_scope 标注 endpoint，重试/failover 各记一行）；`GET /api/admin/usage` 按天×endpoint×模型聚合（2026-09-04 上线，只记 tokens 不估金额——用户用套餐）

### STATS — 浏览量统计（双前端共用，有人点进来就算）

- [x] **STATS-01**: `POST /api/metrics/pv`（免鉴权、fire-and-forget）：body `{source: web|mp, page, device_id}`，写入 `page_views(id, ts, source, page, device_id)`
- [x] **STATS-02**: 网页端 router.afterEach sendBeacon 上报已上线；小程序侧代码已备好（docs/待合入-小程序埋点.md），0.2.1 审核通过后合入
- [x] **STATS-03**: 统计接口 `GET /api/admin/stats`（admin only）：今日/累计 PV、UV、来源分布、教学轮次数、文档数、token 消耗（金额估算按用户决策不做）

### ADMINUI — 管理后台页

- [x] **ADMINUI-01**: frontend-web 新增 `/admin` 路由 + 口令门：`POST /api/admin/login` 用 `MOYAN_ADMIN_WEB_PASSWORD` 换 30 天管理员 JWT（secrets.compare_digest + 10/min 限流；非用户登录层，网页免登录原则不变）；已持有效 token 刷新直接进看板（2026-09-04 上线本地）
- [x] **ADMINUI-02**: 文档管理视图：列表（标题/状态/doc_id）+ 删除按钮（确认弹层，含学习记录提示）；改名沿用书架普通用户功能（Phase 2 决策不改挂载点）
- [x] **ADMINUI-03**: 统计面板：8 张数字卡（PV/UV 今日+累计、tokens 今日+累计、教学轮次、上架教材）+ 来源分布行 + AI 用量台账表（近 30 天按天×endpoint×模型），纯数字卡无图表库（2026-09-04 上线本地，生产未部署）

### VEC — 向量知识库（场景：学生提问超出当前章时检索全书相关段落补上下文）

- [x] **VEC-01**: `document_chunks` 表（doc_id, chapter_index, chunk_index, chunk_text, embedding JSON, embedded 布尔）+ 章节切片嵌入管线（~500字/块段界切分+80字重叠）。**MVP 决策：向量 JSON 列 + Python 余弦（SQLite/PG 通用），pgvector 待语料上量再迁**；embedding 服务未配置时优雅降级（只落切片，检索返空）（2026-09-04）
- [x] **VEC-02**: 成本护栏：建索引仅管理员显式触发（`POST /api/admin/vec/index/{doc_id}`，上传不自动嵌入）；单本 token 估算超 `MOYAN_VEC_MAX_EMBED_TOKENS`（默认30万）拒绝执行；embedding 消耗入 ai_usage 台账（endpoint=embedding）
- [x] **VEC-03**: 检索（内部函数 `vec.search` + 管理调试端点 `GET /api/admin/vec/search`）：余弦 top-k、可排除当前章、零分块过滤
- [x] **VEC-04**: 教学注入：evaluate 中学生回答疑似提问（？/疑问词启发式）时跨章检索拼入 judge context；`MOYAN_VEC_INJECT` 开关**默认关**（2026-09-04 本地已实现未开启）
- [x] **VEC-05**: 删除文档联级清 `document_chunks`（已挂 DOC-01 清理链，deleted.chunks 计数返回）

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
| ADMIN-01..03 | Phase 1 权限分层与生产安全硬校验 | done（2026-09-04，管理员 openid 已配置生产） |
| DOC-01..03 + VEC-05（清理链挂点） | Phase 2 文档删除与联级清理 | done（2026-09-04 生产已上线；DOC-03 被 REN-01 推翻） |
| MOD-01 + REN-01 | 内容安全 + 重命名 AI 审核 | done（2026-09-04；MOD 生产已上线，REN 本地） |
| COST-01, STATS-01..03 | Phase 3 用量观测 | done（2026-09-04 生产已上线） |
| ADMINUI-01..03 | Phase 4 管理后台页 | done（2026-09-04 本地，09-05 生产已部署） |
| VEC-01..03 | Phase 5 向量知识库底座 | done（2026-09-04 本地，09-05 生产已部署） |
| VEC-04 | Phase 6 检索注入教学引擎 | done（2026-09-04 本地，09-05 生产已部署·默认关） |
