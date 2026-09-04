# 01-01 SUMMARY — Phase 1 权限分层与生产安全硬校验

*Completed: 2026-09-04*

## Delivered

- `backend/settings.py`：`env`（MOYAN_ENV）/ `admin_openids` 配置 + `admin_set` / `is_production` property + `apply_production_safety()` 纯函数（可单测）
- `backend/auth/deps.py`：CurrentUser.role（admin/user/anon）；`get_requester`/`get_current_user`/`get_current_user_optional` 三路径贯通；`require_admin` 依赖（403）
- `backend/main.py`：lifespan 调 `apply_production_safety()`，启动日志带环境与管理员数
- `backend/auth/router.py`：dev-login 生产 403 双保险；/me 两分支返回 role
- `backend/auth/schemas.py`：MeResp.role
- `backend/tests/test_admin_roles.py`：11 例全过

## Verification（对照成功标准）

| 标准采信 | 结果 |
|---|---|
| 1. env 配 ADMIN_OPENIDS → /me 返 role=admin；匿名 anon | ✓ test_me_returns_role / test_role_anon_device_rejected |
| 2. 无权限调破坏性接口 403（自动化测试） | ✓ require_admin API 级 4 例（admin 200 / user 403 / 设备 403 / 裸 403）；真实端点挂载在 Phase 2 DELETE 落地 |
| 3. 生产配置下 AUTH_DISABLED/dev-login 强制禁用 | ✓ test_production_forces_auth_disabled_off / test_dev_login_blocked_in_production |
| 4. pytest 全绿 + 前端零改动 | ✓ 104/104（93 基线+11 新增）；git diff 确认仅 backend/ 5 文件 + 1 测试 |

## Deviations

- rename 未收权（研究定论：普通用户日常功能），ADMIN-02 实际应用点移至 Phase 2 DELETE——已在 PLAN deviations 记录。
- 测试临时目录坑：pytest 默认 basetemp 在本机沙箱被拒 → 用 `--basetemp=./pytest-tmp`（已 gitignore 类目录）。

## Commits

- a46ceae docs: phase 1 research + plan
- 本提交 feat(auth): Phase 1 权限分层（6 文件，+204/-8）

## Next

Phase 2 文档删除与联级清理（DELETE + require_admin 首个真实挂载点）。
