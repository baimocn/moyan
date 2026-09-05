# CONVENTIONS — 编码约定

*Last updated: 2026-09-04*

## 语言与注释

- 代码注释与文档**全中文**；docstring 风格 `"""墨衍 · 主题（补充说明）"""`
- 提交信息中文，格式 `feat|fix|chore(scope): 摘要` + 空行 + 正文要点（见 git log）

## 后端（FastAPI）

- 路由函数：`@router.<method>("路径")` + Pydantic schema 入参出参（`backend/engine/schemas.py`、`backend/auth/schemas.py`）
- **slowapi 铁律**：限流装饰器修饰的函数第一个参数必须是 `request: Request`（slowapi 内部读 self），否则运行时炸
- 身份获取：一律通过 `Depends(get_requester)`（`backend/auth/deps.py`），返回 `CurrentUser(openid, role)`；**不要**在路由里自己解析 token
- 配置读取：从 `backend/settings.py` 的 `app_settings` 取；新 env 键用 `MOYAN_` 前缀 + `setdefault`（注意跨模块 setdefault 顺序坑，测试里必须 monkeypatch 显式控制）
- DB 访问：`backend/models/repo.py` 集中数据访问；**schema 变更一律走 alembic**（`migrations/versions/`，必须幂等，生产 `stamp`+`upgrade`；SQLite 开发库走 create_all+stamp）——`_TABLE_ADDITIONS` 仅剩老开发库补列兼容语义
- 错误处理：HTTPException 带中文 detail；SSE 错误以 `event: error` 下发而非 HTTP 错误码
- **会话端点红线（SEC-01）**：凡接受 session_id 的新端点必须做归属校验（`repo.session_owned_by`），非 owner 一律 404；同会话并发走 `try_begin_turn` 409
- **上传审核 fail-closed（CMP-02）**：moderation 异常拒收（503），`MOYAN_MODERATION_FAIL_OPEN=1` 才回退放行
- 测试必须 `--basetemp`（系统 Temp 拒绝访问）：`python -m pytest backend/tests/ -q --basetemp=out/_pytest_tmp`；改模型后必须删除 `backend/tests/test_dev.db` 重建（陈旧 schema 会假绿/假红）
- 子进程（docling）：必须经 `docling_adapter._run_worker` 启动（剥代理 env + 离线 HF 变量），不要直接 subprocess

## 前端（uni-app 小程序）

- 条件编译三语法：template `<!-- #ifdef H5 -->`、style `/* #ifdef H5 */`、JS `// #ifdef MP-WEIXIN`
- 所有请求走 `frontend/src/utils/api.js`（Bearer 注入 + 401 静默重试；SSE 双通道：H5 fetch/ReadableStream，MP wx.request+enableChunked，同一 onEvent 回调）
- 本地存储仅限 `moyan:` 前缀键（moyan:last / moyan:token / moyan:user_id / moyan:openid）
- UI 设计语言：墨绿 #163628 + 米纸 #f6f2e8 + 暖米 #fffdf8；字号 rpx；中文文案口语化（"同桌"人设）

## 前端（frontend-web）

- pinia store（`stores/auth.js`）+ 纯函数 API 模块（`src/api/*.js`），client.js 统一注入 `X-Device-Id`（localStorage 持久化）
- 视图组件放 `views/`，路由无强制登录守卫（免登录产品语义）

## Git

- 主干开发（无分支流程），push 用 `git -c http.proxy= -c https.proxy= push`（沙箱代理会 502）
- 提交前跑 `git diff --name-only | grep -E "^backend/|^frontend-web/"` 之类校验改动范围（双前端独立性验收）

## 安全约定

- 任何密钥/AppID Secret/生产连接串**不入库**（.gitignore 已强化：*.key/*.pem/api_keys/.env）
- out/ 目录不进 git（历史遗留含生产密钥副本文件，待用户处置）
