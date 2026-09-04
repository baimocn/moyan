# Phase 1 Research — 权限分层与生产安全硬校验（inline，2026-09-04）

> 本运行时无 GSD 子代理，研究由主上下文直接完成。结论基于对 `backend/auth/deps.py`、`backend/auth/router.py`、`backend/settings.py`、`backend/routers/documents.py` 的逐行阅读。

## 现状事实

1. **身份三态已有**：`get_requester`（deps.py:102）产出 Bearer 用户 / 设备用户 `web_<did>` / 兜底 `web_anon`，无 role 概念。
2. **两处身份路径**：`get_current_user`（强鉴权，/me 用）与 `get_requester`（免登录，业务端点用）——role 必须两处一致。
3. **rename 是普通用户功能**：双端书架人人可点"重命名"（frontend-web HomeView.vue:252、frontend index.vue:45）。**不能**作为 ADMIN-02 的保护对象，否则破坏体验 + 违反小程序冻结。→ ADMIN-02 的 403 应用点在 Phase 2 的 DELETE。
4. **生产误开面**：`AUTH_DISABLED=1` 时全免鉴权 + mock dev_user + wx-login 退化 + dev-login 开放；`auth_disabled=True` 时 JWT secret 有内置兜底（jwt.py）→ 伪造 token 可行。当前没有"这是生产"的概念（无 MOYAN_ENV）。
5. **MeResp** 无 role 字段；前端 admin 判定（Phase 4）需要它。

## 方案模式（业界惯例对照）

- **env 管理员清单**（静态配置 role）是单管理员/小团队产品的标准轻量做法（对比：数据库 RBAC 表在单管理员场景是过度设计）。逗号分隔 + set 匹配，O(1)。
- **生产环境指纹**：`MOYAN_ENV=production` 显式声明（12-factor 惯例），启动时做安全断言（fail-safe 覆盖而非 fail-open）。
- **require_admin 为独立依赖**（FastAPI Depends 链式），未来任何破坏性端点一行挂载——与 slowapi 装饰器共存无冲突（一个管身份一个管限流）。

## 风险与对策

| 风险 | 对策 |
|---|---|
| pydantic v2 BaseSettings 实例属性赋值兼容性 | 生产覆盖写成纯函数 `apply_production_safety()`，内部用 `object.__setattr__` 兜底，可单测 |
| role 判定放 deps 会拖慢每请求 | set成员判定 O(1)，无 IO |
| mock dev_user role | dev 模式给 admin（开发/测试方便），is_mock=True 已可识别 |
| web 注册用户 openid 也是 `web_` 前缀 | role 不看前缀看"是否持有效 token"：Bearer→user/admin，设备→anon，与登录态语义一致 |

## 决策

- D1（env 清单）用户已拍板；D2 删除语义 Phase 2 再议；本阶段 rename 权限保持现状（全开放）。
