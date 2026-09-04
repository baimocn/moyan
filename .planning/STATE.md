# STATE — 项目记忆

*Last updated: 2026-09-04*

## Current Position

- **Project**: 墨衍（双前端 · 一后端 · 共享书库）
- **Milestone**: M2 管理底座 → M3 向量知识库（路线图 6 阶段）
- **Phase**: Phase 1 完成（01-01-SUMMARY），下一 Phase 2（文档删除与联级清理）
- **Mode**: mvp（每阶段端到端交付）
- **Blocked**: 无（小程序审核与 Phase 1-4 无代码交集）

## LOG

- 2026-09-04: GSD 初始化完成。棕地映射 7 文档（.planning/codebase/，342 行）。PROJECT/REQUIREMENTS/ROADMAP 就绪。方向设计来源：out/下一阶段方向设计_M2管理底座_M3向量库.md
- 2026-09-04: Phase 1 完成并提交——role 三态贯通（CurrentUser.role / me.role / require_admin 403 依赖）+ MOYAN_ENV=production 安全硬校验（AUTH_DISABLED 强制关 + dev-login 403）+ 11 新测试（全量 104/104）。ADMIN-02 真实挂载点移至 Phase 2 DELETE（rename 是普通用户功能不可收权）。注意：pytest 需 --basetemp=./pytest-tmp（系统 Temp 被沙箱拒）

## Key Context for Next Session

- 工作流偏好：YOLO + 标准粒度 + 门禁全开（research/plan_check/verifier）+ planning 文档入库
- GSD 子代理未安装于本运行时——研究/规划/验证由主代理 inline 执行（等同 sequential 模式）
- 小程序 0.2.1 审核中：**Phase 1-4 严禁改动 frontend/**（冻结期）
- 用户最关心：AI 成本可见（COST-01 优先级最高）、双前端独立性（每阶段 diff 校验）
- 沙箱坑速查：git push 用 `git -c http.proxy= -c https.proxy= push`；docling 子进程须走 docling_adapter（剥代理）；测试控制 env 用 monkeypatch 不用 setdefault
