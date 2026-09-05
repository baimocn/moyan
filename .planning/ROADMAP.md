# ROADMAP — 墨衍执行路线（M2/M3 → M4）

*Created: 2026-09-04 · M4 立项 2026-09-05 · 标准粒度 · PROJECT_MODE=mvp（每阶段交付端到端用户能力）*

约束：小程序代码冻结期（0.2.x 审核中），M2/M3 Phase 1-4 不碰 `frontend/`；
M4 三阶段（7-9）全部为 backend/ops/docs，双前端零改动。执行顺序即依赖顺序。

### Phase 1: 权限分层与生产安全硬校验
**Goal:** 系统有 admin/user/anon 三态角色，破坏性操作有闸门，生产误开风险关闭
**Mode:** mvp
**Success Criteria**:
1. env 配置 ADMIN_OPENIDS 后，/me 或登录响应返回 role=admin，匿名设备为 anon
2. 无权限调用破坏性接口返回 403（自动化测试覆盖）
3. 生产配置下 AUTH_DISABLED/dev-login 被强制禁用并有日志（测试覆盖）
4. pytest 全绿，`frontend/` 与 `frontend-web/` 零改动

### Phase 2: 文档删除与联级清理
**Goal:** admin 能通过 API 彻底删除一份文档，磁盘与 DB 无残留
**Mode:** mvp
**Success Criteria**:
1. DELETE /api/documents/{doc_id} 联级清除 DB 行 + markdown + chapters 目录 + uploads 残留（测试覆盖）
2. 非 admin 删除返回 403；重复删除返回 404
3. 生产实测：删除探针文档后 psql 无行、目录无残留
4. existing 共享书库去重不受影响（同书可重新上传）

### Phase 3: 用量观测——token 成本 + 浏览量埋点
**Goal:** 每一分 AI 花费和每一次访问都可量化
**Mode:** mvp
**Success Criteria**:
1. 一轮真实教学对话后 ai_usage 表出现带 token 数的记录；按天聚合接口可算出估算金额（¥）
2. 双端各访问一次后 page_views 出现 web 与 mp 两行；PV/UV/来源分布可查
3. 埋点失败不影响前端主流程（上报接口 5xx 时前端静默）
4. pytest 全绿

### Phase 4: 管理后台页 /admin
**Goal:** 所有管理操作和统计数字在网页上点点就能完成，告别 psql
**Mode:** mvp
**Success Criteria**:
1. 非 admin 访问 /admin 显示无权限；admin（env 配置的 openid）可进入
2. 文档管理视图可改名、可删除（带确认），与后端状态实时一致
3. 统计面板展示 PV/UV/来源分布/教学轮次/文档数/token 估算金额
4. 生产部署验证通过（nginx 静态 + API）

### Phase 5: 向量知识库底座（pgvector + 嵌入管线）
**Goal:** 书的每一章可被语义检索，成本先算后花
**Mode:** mvp
**Success Criteria**:
1. pgvector 扩展 + document_chunks 表就绪，存量书籍嵌入完成且成本日志可查
2. 嵌入前成本估算护栏生效（超阈值需 env 显式放行）
3. 内部检索接口：给定查询文本返回 top-k 相关切片（准确性抽样人工验收）
4. 删除文档联级清 chunks（挂在 Phase 2 清理链）

### Phase 6: 检索注入教学引擎
**Goal:** 学生提问超出当前章时，AI 能引用全书相关段落，回答不再"只看得到一章"
**Mode:** mvp
**Success Criteria**:
1. 超章提问触发检索并注入参考上下文（开关可控，默认开）
2. 教学主流程回归全绿（test_d11_fixes/test_tutor_fsm 不受影响）
3. 检索未命中时行为与现状完全一致
4. 真机/模拟器抽样对话人工验收

## Requirement → Phase 映射

| Requirements | Phase |
|---|---|
| ADMIN-01..03 | 1 |
| DOC-01..03, VEC-05 | 2（VEC-05 底座在 5，清理链先挂空位） |
| COST-01, STATS-01..03 | 3 |
| ADMINUI-01..03 | 4 |
| VEC-01..03 | 5 |
| VEC-04 | 6 |

覆盖率：23/23 v1 需求全覆盖 ✓

---

# 里程碑 M4：加固与升级（2026-09-05 立项）

*来源：魔鬼代言人审查 v2 + Schema 审计 + 产品定位确认（不收费、搜集用户-AI 对话数据）。*
*调研：`.planning/phases/07-hardening/RESEARCH.md`。*
*前置：Phase 1-6 已全量交付（docs/REQUIREMENTS）；挂起的限流改动需先 commit 收口基线。*

### Phase 7: 教学链路安全与成本边界（SEC-01..04）
**Goal:** 会话只能被主人驱动，AI 消耗有上限有熔断，状态机无双跑
**Mode:** mvp
**Success Criteria**:
1. 非 owner 携他人 session_id 调 turn/resume/review-* 一律 404（测试覆盖 4 个端点）
2. 所有真实 AI 调用带 max_tokens（env 可调，mock 断言 + 生产日志可见）
3. 同会话并发第二个 turn 返 409，不产生双 AI 调用（测试覆盖）
4. 日 token 预算超限自动降级 cheap，超硬限返 429（测试覆盖，默认关闭不影响现网）
5. pytest 全绿（--basetemp）；frontend/ 与 frontend-web/ 零改动

### Phase 8: Schema 健康化 + alembic 基线（SCHEMA-01..06）
**Goal:** 模型声明与生产 schema 一致，迁移有工具，台账表寿命解除
**Mode:** mvp
**Success Criteria**:
1. pg_indexes 与模型声明一致（补 content_hash 索引、email 唯一约束）
2. ai_usage/page_views/document_chunks 主键 bigint；关键 JSON 列统一 jsonb
3. 核心状态字段带 CHECK，weaknesses 业务唯一键就位
4. 引入 alembic：`upgrade head` 可从零重建生产等价 schema，模型层 JSONB variant 公共化
5. 生产执行并复核 pg_indexes，pytest 全绿

### Phase 9: 可观测与合规（OBS-01/02，CMP-01/02，DOC-01）
**Goal:** 故障五分钟内可见，合规底线落纸，文档与现实一致
**Mode:** mvp
**Success Criteria**:
1. SSE 冒烟探针每 5 分钟一轮，失败留痕且管理台可见（探针消耗计入 ai_usage）
2. 公开书库内容审核 fail-closed + 上传默认私有/显式分享 + 管理台一键下架（测试覆盖）
3. 双端隐私告知 + 数据保留策略上线（CMP-01）
4. 交接文档 v5.1：git 状态行、Python 3.12 实况、Caddy 弃用声明、后端归属规则、内容池风险声明
5. pytest 全绿；frontend/ 零改动（告知页如需前端展示，延至 M5）

## M5（后置立项，暂缓规划）

双端功能升级：错题本深化（重练流）、学习报告、个人页、聊天气泡 markdown 渲染、
上传进度流、管理台图表、向量检索 UI。——摘自交接文档 5A/5B，待 M4 收口后走 gsd-new-milestone。
