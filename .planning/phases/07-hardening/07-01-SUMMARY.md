# 07-01-SUMMARY — Phase 7 执行记录

*Date: 2026-09-05 · 状态：✅ 已交付并部署生产（commit d68db97 + 本次修复）*

## 交付对照（must_haves → 实证）

| must_have | 实证 |
|---|---|
| 4 个 session_id 端点归属校验，非 owner 404 | 单测 6 例 + 生产实弹：B turn A 会话=404，B review answer=404 |
| 真实 AI 调用带 max_tokens | test_provider_chat_injects_max_tokens（kwargs 断言）+ cheap 1500 封顶 |
| 同会话并发 409，异常释放 | test_turn_lock_semantics_and_release + API 级 409 |
| 日预算熔断默认关、软顶降 cheap/硬顶 429 | budget_state 三态 + Router hard 抛 BudgetExceeded + soft 优先 cheap |
| pytest 全绿、双前端零改动 | **174/174**（163 存量基线 + 11 新增，git diff 无 frontend/） |

## 生产验证

- 9 文件 SFTP + md5 抽检一致；restart（sleep 15）后 active + health 200
- 实弹：start(SmokeA) → B turn=404 / **A turn=200**；review B=404 / A=200
- 预算参数未开启（默认 0），现网行为零变化

## 执行中抓到并修复的缺口

1. **生产冒烟抓到单测盲区**：start_chapter 把 user_id 落库但未挂内存会话、
   resume_session 恢复时同样丢失 → owner 本人在 start 后/restart 后会被自己的
   归属校验 404 误杀。已修（`ses.user_id = ...`）+ 回归锁
   test_start_and_resume_carry_owner。
2. Router 软顶降级路径 `self._cheap_provider()` 调用不存在的实例方法——
   单测先行暴露，改为模块函数调用。

## Deviations（与 PLAN 的偏差）

- 归属校验端点 4 个（start 创建会话不校验，PLAN 已修正口径）
- 并发锁用 in-flight set 替代 asyncio.Lock（单事件循环下语义等价，注释已标注
  多 worker 需换 PG advisory lock）
- **遗留**：`/api/study/{doc_id}/*` 文档级读端点（sessions/weaknesses/stats/reviews）
  仍无身份依赖——doc 范围学习数据可匿名读，建议纳入 Phase 8 一起收口
- Bearer 无效静默落 web_anon 的旧行为未动（归 Phase 9 / 审查 C3 边界条件）
- 预先生成的 _MinContainer 缺 engine_factory 导致 reviewer 回落告警（存量，与本阶段无关）
