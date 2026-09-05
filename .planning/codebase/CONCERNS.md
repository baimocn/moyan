# CONCERNS — 技术债与风险

*Last updated: 2026-09-05（M4 收口复核）*

## 安全

| 项 | 位置 | 风险 | 建议 |
|---|---|---|---|
| `AUTH_DISABLED` 开关 | `backend/auth/deps.py` | 生产误开=完全免鉴权（mock user openid=dev_user） | M2 权限分层时加"生产禁用"硬校验（auth_disabled 且非 DEBUG 时启动告警/拒绝） |
| dev-login 端点 | `backend/auth/router.py` | 邮箱密码换 token 的开发后门仍在生产路由 | 加 env 开关，生产关闭 |
| JWT secret 兜底 | `backend/auth/jwt.py` | auth_disabled=True 时用内置固定密钥——生产若误开此模式，token 可被任何人伪造 | 同上，硬校验 |
| 生产密钥副本 | `out/_env_prod.txt`、`out/_pg_pass.txt`（本地磁盘，不入 git） | 泄露面 | 用户确认后删除 |
| 管理能力真空 | — | 目前删数据/查统计只能 SSH psql，误操作风险高 | M2 admin 后台正是解法 |

## 可靠性 / 数据

| 项 | 位置 | 症状/风险 | 建议 |
|---|---|---|---|
| 迁移只支持加列 | `backend/models/db.py` `_TABLE_ADDITIONS` | 改列型/删列/加索引无路径，schema 演进会卡 | M2 若需复杂迁移，引入一次性 SQL 迁移脚本约定 |
| tasks 表垃圾行 | tasks 表 | failed 行永留 DB（UI 不显示但污染数据） | DELETE 联级清理时顺带；或定期任务 |
| 老数据 NULL | documents/5 表 user_id、content_hash 列 | 匿名/迁移旧行 NULL，查询条件须兼容 `IS NULL` | 保持现有兼容写法 |
| plan 缓存无失效 | `backend/storage.py` plan_{n}.json | prompts 改版后旧缓存仍被用，教学行为不更新 | 加版本号或清除机制 |
| 单 worker + 2C2G | 生产 systemd | docling 解析 PDF 内存峰值 + SSE 长连接并发，内存 1.2G/1.6G 紧张 | 加 swap 兜底；观察真实用户量后升配 |


## 已解决（M4，2026-09-05，留档防复发）

| 原风险 | 解决方式 |
|---|---|
| AUTH_DISABLED 生产误开 | Phase 1：MOYAN_ENV=production 硬校验 + dev-login 403 |
| dev-login 生产后门 | 同上，生产 403 |
| JWT secret 兜底可伪造 | 同上（auth_disabled 生产强制关） |
| 生产密钥副本 out/*.txt | 已删除（2026-09-05）；root 密码仍在 out/_ssh_run2.py（用户决定不轮换） |
| 迁移只支持加列 | Phase 8：alembic 全量接管（0001-0003） |
| 匿名限流可旋转（刷账单根因） | Phase 7 前置：限流 key 匿名回落 IP |
| 未审内容入公开书库 | Phase 9：审核 fail-closed + shared 下架 |
| 故障发现靠用户 | Phase 9：moyan-smoke.timer 探针 |

## 死代码 / 债

| 项 | 位置 | 说明 |
|---|---|---|
| `backend/db.py` | Flask 时代遗留 | 读 `config.DATABASE_URL` 会炸，生产查库用 psql。可删除 |
| `storage.py` 废弃函数 | `add_document/list_documents/get_document` | JSON 清单时代遗物，标了已废弃可删 |
| `deploy/` Caddy 方案 | 未启用（生产用 nginx） | 保留但 README 需注明非现役，防误用 |
| 教学状态机巨型文件 | `backend/engine/tutor/actions.py` | 状态流转+话术+SSE 产出耦合，改动回归成本高（test_d11/test_tutor_fsm 护航）。重构建议：业务流先行小步拆 |

## 脆弱流程

- **解析管线**（`backend/tasks.py`）：docling 子进程失败→状态 failed 无自动重试；用户视角"卡住"。上传域名白名单/限流桶等客户端因素也会表现成"上传失败"（本次审核拒绝即此类）
- **SSE 链路**：nginx↔uvicorn keepalive 配置敏感（--timeout-keep-alive 75），换环境部署必查
- **沙箱环境坑**：代理注入致 docling 需剥 env；Git Bash 下 `$vm` 会被展开；automation callMethod 对 uni-app Vue3 无效（用 evaluate `$vm` 直调）
- **微信平台**：个人主体类目受限；无提审 API；服务器域名随 AppID 走（换号须重配）

## 性能

- 搜索 `?q=` 用 `lower() like %kw%` 全表扫——书万级前可接受，之后转 pg trigram/全文
- token 用量无记录（成本不可见）→ M2 `ai_usage` 表最高优先
- 页面浏览无统计（用户已要求 M2 自建 `page_views` 埋点）
