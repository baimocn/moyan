# 08-01-SUMMARY — Phase 8 执行记录

*Date: 2026-09-05 · 状态：✅ 已交付并部署生产*

## 交付对照（must_haves → 实证）

| must_have | 实证 |
|---|---|
| 索引/唯一补齐 | pg_indexes 复核：ix_documents_content_hash、user_profiles_email_key、uq_weaknesses_user_doc_skill 三索引在列 |
| 台账主键 bigint | information_schema：ai_usage/page_views/document_chunks.id 全部 bigint |
| jsonb 统一 | 模型层 JSONType 公共化（PG=JSONB/SQLite=JSON），主库 10 列已 ALTER jsonb |
| CHECK 就位 | pg_constraint 6 个 ck_*（status/state/role/mastery/fsrs_state/auth_type） |
| upsert NULL 路径修复 | test_upsert_weakness_null_user_isolation（None 不再跨用户抓行） |
| alembic 从零重建 | 临时库 moyan_p8_zero_test：upgrade head → 12 表 / 6 CHECK / 3 bigint，rc=0 |
| pytest 全绿、前端零改动 | **180/180**（+6 schema 回归锁）；git diff 无 frontend/ |

## 生产执行序列

1. 取值域预检（status/mastery/role/state/auth_type/fsrs_state 全在约束域内）
2. venv `pip install alembic`
3. 主库：`alembic stamp 0001` → `alembic upgrade head`（0002 全幂等）
4. from-zero：临时库（**createdb -O moyan**，PG15+ public schema 无公共 CREATE 权限）验证通过
5. restart + health=200

## Deviations / 教训

- **documents.status 实际取值域比计划多一个 `rejected`**（moderation 拒收路径写入）——
  CHECK 上线前 SELECT DISTINCT 全域核实救了一命；约束按 4 值落地
- **SQLite 的 BIGINT PRIMARY KEY 无 rowid 自增别名**：BigIntPK = BigInteger.with_variant(Integer,"sqlite")
  （单测先行暴露：ledger 记账 NOT NULL id 失败）
- 测试库 test_dev.db 是陈旧 schema 的载体：改模型后必须删除重建（已两次踩中）
- alembic.ini 只能 ASCII（Windows configparser 按 GBK 解码）
- 本地开发库如需对齐新 schema：删除 data/moyan_dev.db 重启即重建（dev 走 create_all 路径）
