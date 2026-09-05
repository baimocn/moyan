# STATE — 项目记忆

*Last updated: 2026-09-05*

## Current Position

- **Project**: 墨衍（双前端 · 一后端 · 共享书库）
- **Milestone**: M2/M3 六阶段全量交付（docs/REQUIREMENTS Phase1-6 全 done）→ **M4 加固与升级（2026-09-05 立项）**
- **Phase**: Phase 7 已规划（07-01-PLAN 就绪），待 T0 收口基线后执行
- **Mode**: mvp（每阶段端到端交付）
- **Blocked**: 无（M4 三阶段全为 backend/ops/docs，与小程序冻结无冲突）

## LOG

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
