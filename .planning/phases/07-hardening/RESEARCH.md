# RESEARCH — M4 加固与升级 · 规划前置调研

*Date: 2026-09-05 · 来源：魔鬼代言人审查 v2 + 数据库 Schema 审计 + 生产实测（全部本会话代码/生产验证，非推测）*

## R1 产品定位变更（规划的根本输入）

用户确认（2026-09-05）：**产品不收费，核心目的是搜集用户与 AI 的对话数据。**
推论：AI 账单是纯运营成本；限流同时是**数据质量防线**（脚本刷入的垃圾对话污染语料）；
搜集行为触发 PIPL 合规义务。原"商业/类目待办"降权，但小程序 AIGC 审核风险仍在。

## R2 已修（本会话交付，勿重复规划）

| 项 | 证据 |
|---|---|
| 限流 key 匿名回落 IP | `backend/rate_limit.py::_key_func` 已改并**部署验证**（旋转 X-Device-Id 35×429）；回归锁 test_key_func_anon_device_falls_back_to_ip；改动文档 docs/改动记录-20260905-限流IP兜底.md。**代码未 commit** |
| 生产 requirements.txt 补 slowapi/PyJWT | 已 SFTP + md5 验证 |
| git 基线推送 | 远端=本地=生产=4f72eea |
| 本地明文凭据删除 | out/_env_prod.txt、_pg_pass.txt 已删；**AI key/root 密码轮换待用户控制台操作**；out/_ssh_run2.py 仍硬编码 root 密码 |

## R3 安全边界缺口（代码实证）

1. **会话归属未校验**：`backend/routers/tutor.py:67-68` 只查会话存在，不比 owner；
   `backend/routers/study.py` 的 resume / review-session/{id} / answer 同样裸奔（session_id 直取）。
   session_id 熵仅 40bit（`backend/engine/tutor/service.py:49` `uuid4().hex[:10]`）。
   影响：持他人 session_id 可注入对话、读取会话、污染搜集数据。
2. **生成无 max_tokens 上限**：`backend/engine/providers.py:64-75` 支持参数但全链未传。
3. **同会话无并发锁**：service/session 无任何锁；双开/重试风暴 → 状态机竞态 + 双倍 AI 调用。
4. **无全局预算熔断**：`backend/ledger.py` 已有 ai_scope/record 与 ai_usage 台账（含 total_tokens 列），
   缺"按日累计→降级/拒绝"的消费闸门。IPv6 可旋转，IP 限流非终点。

## R4 Schema 缺口（生产 PG16 实测，129 列/32 索引/行数个位数）

1. **迁移路径丢索引实锤**：模型声明 `documents.content_hash index=True`、
   `user_profiles.email unique=True`，但 pg_indexes 无对应索引
   （`db.py::_TABLE_ADDITIONS` 的 ALTER ADD COLUMN 不带索引）。
2. **Integer 自增到期炸弹**：ai_usage / page_views / document_chunks 的 id。
3. **json/jsonb 混用**：仅 document_chunks.embedding 用 JSONB（vec.py with_variant 先例），
   其余 10 个 JSON 列 PG 上全是裸 json，审计统计场景加不了 GIN。
4. 时间戳全可空无 DB 默认；状态字段（status/mastery/role/auth_type/fsrs_state）无 CHECK；
   weaknesses 缺 (user_id, doc_id, skill_id) 业务唯一键；主键 40bit 熵。
5. `create_all` 不加列不加索引（坑4）→ 无迁移工具，建议 alembic。

## R5 可观测与运维

- chat_stream 坏一天才被发现（P0 事故）→ 无探针。建议 cron 冒烟（5min 一轮 mock/cheap 教学流）。
- 单 worker、PG 池 5+5；部署重启切断活跃 SSE（本会话实测冷启动 >4s，restart 脚本需 sleep≥15s）。
- 服务器 venv 为 **Python 3.12**（文档写 3.13；本地启动指令写 3.14）——文档三处硬伤待 v5.1。
- 反代实为 **nginx**（/etc/nginx/sites-available/moyan），caddy 服务 failed——文档未声明。

## R6 合规与内容风险

- 共库共书池：网页 fail-open 审核的内容直接出现在小程序书库 → **小程序过审率被网页 UGC 绑架**。
- PIPL：对话数据可关联设备/个人，需隐私告知 + 保留期限。
- 间接提示词注入：教材文本是一等输入，共享书库一本被投毒的书污染所有学它的人。

## R7 约束

- `frontend/` 冻结（0.2.x 审核中）——M4 三阶段全部 backend/ops/docs，天然合规。
- pytest 需 `--basetemp`（系统 Temp 拒绝访问，本会话实测 `out/_pytest_tmp` 可用）。
- 沙箱 git push 曾被代理阻断；本会话实测直推成功，若复发用 STATE.md 记录的 proxy 参数。
- GSD 子代理未安装，主代理 inline 执行；工作流 YOLO + 标准粒度 + 门禁全开。
