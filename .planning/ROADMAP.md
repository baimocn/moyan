# ROADMAP — 墨衍 M2/M3 执行路线

*Created: 2026-09-04 · 标准粒度 · PROJECT_MODE=mvp（每阶段交付端到端用户能力）*

约束：小程序代码冻结期（审核中），Phase 1-4 不碰 `frontend/`。执行顺序即依赖顺序。

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
