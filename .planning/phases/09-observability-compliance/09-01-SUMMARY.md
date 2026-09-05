# 09-01-SUMMARY — Phase 9 执行记录

*Date: 2026-09-05 · 状态：✅ 已交付并部署生产*

## 交付对照（must_haves → 实证）

| must_have | 实证 |
|---|---|
| 冒烟探针 | moyan-smoke.timer active（5min）；手动一轮 `SMOKE_OK {health:200, ai_turn:200, ai_ok:true, ms:40311}`；jsonl 落盘；/api/admin/smoke 上线（未授权 403 实测） |
| 书库审核 fail-closed | moderation 异常 → 503 拒收 + 残壳清理（test_moderation_error_fail_closed）；MOYAN_MODERATION_FAIL_OPEN=1 回退（legacy 测试） |
| shared 列 + 可见性 + 一键下架 | 迁移 0003 落库；书架过滤 shared/owner；POST /api/admin/documents/{id}/share；管理台按钮（下架/恢复上架）；实测匿名见 11 本共享书 |
| 隐私策略 | GET /api/privacy 实弹返回；/privacy 页面上线；docs/数据保留与隐私策略.md |
| 文档 | docs/运维-部署与回滚清单.md + 交接文档 v5.1（git 状态/Python 3.12/nginx 实况/新坑 13-16/API 速查扩充） |
| pytest 全绿、小程序零改动 | **185/185**；frontend/ 冻结未碰 |

## Deviations

- 探针 AI 全链从"每 5 分钟"调整为 **health 5min + AI turn 60min 限频**（成本核算：
  24 次真实 turn/天，SEC-04 预算熔断兜底）——"故障五分钟可见"对进程/DB 级成立，
  教学链路级 ≤60min
- shared 列默认 true（维持现网获客行为），"默认私有"通过 MOYAN_UPLOAD_DEFAULT_SHARED
  开关预留，产品决策时一键切换
- 文档级 `/api/study/{doc_id}/*` 读端点仍未鉴权（Phase 7 遗留项，随 M5 个人页一起收口）
- 旧测试 test_moderation_error_fails_open 更名改断言为 fail-closed 新契约

## 新增运维资产

- scripts/smoke_probe.py + deploy/moyan-smoke.{service,timer}
- migrations/versions/0003_documents_shared.py
- frontend-web：/privacy 页 + 管理台下架按钮 + dist 全量更新
