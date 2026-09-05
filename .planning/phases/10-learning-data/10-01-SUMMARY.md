# 10-01-SUMMARY — Phase 10 执行记录

*Date: 2026-09-05 · 状态：✅ 已交付并部署生产*

- AUTH-04：7 个 doc 级读端点全部加身份+可见性（repo.doc_visible 纯函数，
  documents._doc_visible 委托——单一事实源）
- PRAC-01：list_weaknesses owner 过滤 + due 优先排序；admin 全量口径
- RPT-01：repo.user_report（turns/sessions/逐日均分趋势/薄弱分布/连续天数，
  Python 聚合避方言）；GET /api/study/report 双入口之一
- ME-01：GET /api/auth/me/stats（get_current_user，无 web_anon 兜底——个人口径）
- UP-01：契约 7.5 补 tasks 进度语义
- 全量 193/193；生产实弹（report 结构/me-stats 401）
- 教训：测试清理 fixture 的 LIKE 模式必须覆盖全部播种键（跨运行 UNIQUE 残留）
