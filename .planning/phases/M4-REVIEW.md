# M4-REVIEW — 里程碑代码审查

*Date: 2026-09-05 · Scope: 715d10e..50024d8（Phase 7/8/9 全部代码变更，33 文件 +1321/-64）*
*Depth: standard（逐文件 + 定向取证）· 审查者：主代理 inline（GSD 子代理未安装）*

## 总评

**质量整体扎实，无 Critical 发现。** 安全设计（SEC-01..04）经对抗性自审未发现绕过路径；
schema 变更经 from-zero + 幂等双验证；fail-closed 语义经新旧测试双向锁定。发现 2 个 Warning
（均为探针引入的副作用，修复成本低）与 4 个 Info（2 个为已知遗留项的确认）。

## ✅ 正确性确认清单（对抗性自审通过项）

| 审查点 | 结论 |
|---|---|
| SEC-01 归属校验绕过 | 未发现：4 端点全走 `session_owned_by`；NULL-owner 仅 web_anon/admin；404 不暴露存在性 |
| SEC-03 锁竞态 | 单事件循环内 check-and-add 无 await 间隙；gen() finally 断连必释放；预算/归属检查先于抢锁（早期失败不占锁） |
| SEC-04 预算熔断 | hard 在端点层 429（start/turn 都拦）；soft 仅优先 cheap 不禁主引擎（符合设计）；台账写路径不熔断 |
| fail-closed | async/sync 双路径经 `asyncio.run` 委托一致；worker 异常 → task failed；`MOYAN_MODERATION_FAIL_OPEN` 回退有测试 |
| 迁移幂等 | 0002/0003 全 IF NOT EXISTS / DO 块 / 可重入 ALTER；from-zero 临时库 12 表验证 |
| CHECK 域 | 预检 SELECT DISTINCT 后落约束；`rejected` 由测试抓出补齐 |
| 可见性 | shared 过滤 list/detail/chapters 三处一致；下架后 owner/admin 仍可见；403/404 语义正确 |

## 🟠 Warning

### W1. 探针污染生产统计数字
- **位置**：`scripts/smoke_probe.py`（24 次 AI turn/天）+ `backend/routers/admin.py:146-147`
- **场景**：`platform_stats` 全量 `count(TeachingSession/Turn)`，探针每天新增 ~24 会话 + ~48 轮，
  全部挂 `web_smokeprobe0001` 身份——管理台"教学轮次/会话数"一个月灌水 ~720，运营数字失真
- **建议**：stats 查询排除 `user_id LIKE 'web_smokeprobe%'`；或探针身份改专用标记列。修复约 3 行

### W2. tutor.sessions 无淘汰，探针加速堆积
- **位置**：`backend/engine/tutor/service.py:36`（`sessions: dict` 无任何 pop/MAX 逻辑，grep 证实）
- **场景**：ReviewService 有 MAX_SESSIONS=50 淘汰，TutorService 没有。M4 前"游客会话"增速有限；
  探针上线后 +24/天确定增长。单对象 KB 级，年积 ~9k 条 ≈ 数十 MB，且 `try_begin_turn` 的
  `_inflight` 同样只增不减（end_turn discard，但泄漏的 session_id 键保留）
- **建议**：TutorService 加与 ReviewService 同款 MAX+LRU 淘汰（~5 行）

## 🟡 Info

| # | 发现 | 说明 |
|---|---|---|
| I1 | web_anon 认领 NULL-owner 会话并落库 | `handle_turn` 归属补挂会把老 NULL 会话的 user_id 写成 `web_anon`（save_session 持久化）。语义可接受（web_anon 即兜底身份），仅数据口径瑕疵 |
| I2 | `tokens_today()` 同步查询在事件循环 | 60s 缓存摊薄为每分钟 1 次阻塞查询，当前规模可接受；并发上来后换 `run_in_executor` 或后台刷新 |
| I3 | admin share 下架无审计日志 | 谁在何时下架了哪本书没有留痕（ai_usage 只记 AI 调用）；管理台单人阶段可接受 |
| I4 | `/api/study/{doc_id}/*` 文档级读端点仍无身份依赖 | 已知遗留（Phase 7 记录），doc 范围学习数据可匿名读；随 M5 个人页收口 |

## 覆盖确认

- 测试：185/185（M4 新增 26 例：限流 1 + SEC 12 + SCHEMA 6 + OBS/CMP 5 + 既有更新）
- 文档审查：CLAUDE.md/codebase 五件/API 契约/REQUIREMENTS 已由文档洁癖同步（50024d8），无相对时间遗留
- 前端：frontend/（小程序）冻结未碰 ✅；frontend-web 改动经 build+部署验证

## 建议后续

1. W1+W2 一次小修复（合计 ~10 行 + 2 个测试），可挂 Phase 8.1 或随 M5 首任务
2. I4 随 M5 收口；I1-I3 记录在案即可
