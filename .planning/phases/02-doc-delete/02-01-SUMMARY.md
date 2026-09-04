# 02-01 SUMMARY — Phase 2 文档删除与联级清理

*Completed: 2026-09-04（部署与生产实测部分见下）*

## Delivered

- `backend/routers/documents.py`：DELETE /api/documents/{doc_id}——require_admin 闸门 + 单事务 FK 安全级联（turns/judgements→weaknesses/strategy_logs→sessions→tasks→documents）+ 事务后文件清理（markdown/chapters/uploads，缺失容错）+ 幂等 404
- `frontend-web`：api/documents.js deleteDocument；HomeView isAdmin 判定（登录态拉 /me）+ 书架卡「删除」按钮 + 确认弹层 + 删除后刷新
- `backend/tests/test_doc_delete.py`：6 例（级联全清/计数/403×2/404×2/去重不受污染）

## Verification（对照成功标准）

| 标准采信 | 结果 |
|---|---|
| 1. DELETE 联级清除 | ✓ pytest test_admin_delete_cascades_all（DB 7 表 0 残留 + 3 类文件 0 残留 + 计数正确） |
| 2. 403/404 | ✓ 非 admin 403 / 设备 403 / 重复删 404 / 不存在 404 |
| 3. 生产实测 | 部分完成：代码已部署（9 文件 md5 校验），MOYAN_ENV=production 已配置，公网实测 **anon DELETE 403** ✓；admin 全链删除实测待 ADMIN_OPENIDS 配置后补（等用户账号 ID） |
| 4. 去重不受影响 | ✓ test_recreate_same_hash_after_delete |

## Deviations

- 全量回归首跑遇 1 例 basetemp OSError（WorkBuddy 沙箱 shim 短路径解析偶发）→ 换 basetemp 重跑 110/110 绿，确认非代码问题。
- 部署脚本首验 502 为 2C2G 冷启动 ~36s 窗口内 curl 打早，直连与公网复验均正常。

## Pending（用户动作后闭环）

1. 用户在 https://moyan.baimo7715.top 注册网页账号 → 告知邮箱 → 查 user_profiles 取 user_id → 写入 ADMIN_OPENIDS → 重启 → admin token 实测删除全链
2. 或者：用户确认本人 wx openid（候选 o7PVH3dMXVtBqHP3zwOxbCY43JKg，今天 16:11 仍活跃）
