# STATE — 项目记忆

*Last updated: 2026-09-05（M5 收口）*

## Current Position

- **Project**: 墨衍（双前端 · 一后端 · 共享书库）
- **Milestone**: M2/M3/M4 全部交付 → **M5 功能升级（2026-09-05 立项）**
- **Phase**: **M5 三阶段全部交付**（10 学习数据底座 / 11 网页端升级 / 12 小程序升级，各见 0X-01-SUMMARY）。下一步候选：M6 或按用户反馈迭代
- **Mode**: mvp（每阶段端到端交付）
- **Blocked**: 无（M4 三阶段全为 backend/ops/docs，与小程序冻结无冲突）

## LOG

- 2026-09-05: **M5 收口**——Phase 10 部署实弹（report 结构/me-stats 401）；Phase 11 三页上线（发现 MD-01 md.js 已存在未重做；补 review-session current 恢复现场端点）；Phase 12 小程序 4 页 build:mp-weixin 通过（提审包 0.2.3=埋点+本阶段，待用户操作）。全量 193/193。教训：改测试清理 fixture 的 LIKE 模式要覆盖全部播种键；HomeView 多行根标签被单行正则截断
- 2026-09-05: **M5 立项**——PROJECT Active 区重写（M2/M3/M4 归档已交付）；REQUIREMENTS M5 增补 13 项需求（AUTH-04/PRAC-01..03/RPT-01..02/ME-01..02/MD-01/CHART-01/VECUI-01/UP-01..02/PP-01）；ROADMAP M5 三阶段（10 后端底座+遗留收口 / 11 网页端升级 / 12 小程序升级·门禁=冻结解除）；M6 候选挂起（知识图谱/邮箱绑定/多管理员）
- 2026-09-05: **M4 收口**——Phase 7 部署实弹（B 访问 A 会话 404/A 本人 200，生产冒烟抓到 start/resume 未挂 owner 缺口已修）；Phase 8 生产 stamp/upgrade （3 索引+3 bigint+10 jsonb+6 CHECK，from-zero 临时库 12表/6CHECK/3bigint 验证；createdb 须 -O moyan）；Phase 9 探针 SMOKE_OK + fail-closed + shared 下架 + /api/privacy + v5.1 文档。全量 185/185。教训：改模型后必须删 test_dev.db 重建；CHECK 取值域先 SELECT DISTINCT（漏了 rejected）；alembic.ini 只能 ASCII
- 2026-09-05: **会话级修复（已上线/已落盘）**——限流 key 匿名回落 IP（rate_limit.py + 回归锁，已部署生产并实弹验证 35×429；**代码未 commit，= Phase 7 T0**）；生产 requirements.txt 补 slowapi/PyJWT（md5 验证）；git 基线推送（远端=本地=生产 4f72eea）；删除本地明文凭据 _env_prod.txt/_pg_pass.txt（**AI key/root 密码轮换待用户控制台操作**；out/_ssh_run2.py 仍硬编码 root 密码）
- 2026-09-05: **审计沉淀**——魔鬼代言人审查 v2（docs 未存档，结论见会话）：schema 审计发现迁移路径丢索引实锤（content_hash 索引缺失、email unique 缺失）、Integer 台账到期炸弹、json/jsonb 混用；边界缺口实证（turn 无归属校验/max_tokens 无上限/同会话无锁/无预算熔断）；服务器实况（Python 3.12、nginx 反代、caddy failed）
- 2026-09-05: **M4 立项并规划**——ROADMAP 追加 Phase 7/8/9（安全与成本边界 / Schema 健康化+alembic / 可观测与合规）+ M5 功能升级后置立项；07-hardening/RESEARCH.md + 07-01-PLAN.md 就绪，plan-check 通过
- 2026-09-04: GSD 初始化完成。棕地映射 7 文档（.planning/codebase/，342 行）。PROJECT/REQUIREMENTS/ROADMAP 就绪
- 2026-09-04: Phase 1 完成并提交——role 三态贯通 + MOYAN_ENV=production 安全硬校验 + 11 新测试（104/104）

## Key Context for Next Session

- 工作流偏好：YOLO + 标准粒度 + 门禁全开（research/plan_check/verifier）+ planning 文档入库
- GSD 子代理未安装于本运行时——研究/规划/验证由主代理 inline 执行（等同 sequential 模式）
- 小程序 0.2.x 审核中：**M4 全阶段严禁改动 frontend/（冻结延续）**
- 产品定位（2026-09-05 用户确认）：**不收费，搜集用户-AI 对话数据**——限流=成本+数据质量双防线；PIPL 合规进 Phase 9
- 生产实况：Python 3.12（venv）、nginx 反代（caddy 已废）、uvicorn --proxy-headers 已开、PG16 行数个位数（schema 改造窗口期）
- 沙箱坑速查：pytest 需 `--basetemp=out/_pytest_tmp`（系统 Temp 拒绝访问）；docling 子进程走 docling_adapter（剥代理）；测试控制 env 用 monkeypatch 不用 setdefault；restart moyan 后 sleep ≥15s 再 health 检查（冷启动 >4s）
- 凭据纪律：生产凭据仅存服务器 /opt/moyan/.env 一份；out/ 下严禁再落明文副本
