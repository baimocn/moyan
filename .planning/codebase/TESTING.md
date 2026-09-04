# TESTING — 测试结构

*Last updated: 2026-09-04*

## 后端：pytest（唯一正式测试层）

- 位置：`backend/tests/`，17 个文件 ~1900 行，pytest 套件全绿（2026-09-04 基线 93/93）
- 运行：项目根 `python -m pytest backend/tests/`（本地用受管 Python 3.13 venv；CI 无）
- `conftest.py`：共享 fixture（测试 app、临时 DB）；测试 DB 用 `test_dev.db`

## 文件地图

| 文件 | 覆盖 |
|---|---|
| `test_auth.py` | JWT 签发/校验、wx-login（mock jscode2session）、dev-login 启停、/me 401→200、首登 is_new |
| `test_web_auth.py` | 网页版 register/login（scrypt） |
| `test_web_share.py` | 免登录共享书库：get_requester 三态、X-Device-Id 映射、?q= 搜索、content_hash 去重 reused |
| `test_rate_limit.py` | key_func、30/m 触发、用户隔离（须带合法 JWT，否则依赖层 401 不计数） |
| `test_d11_fixes.py` | 4 引擎缺陷回归：两题叠一/净化器/skip 桥句/讲解态收束 |
| `test_tutor_fsm.py` | 教学状态机流转 |
| `test_judge_coerce.py` / `test_quality_guards.py` | 结构化输出兜底与质量守卫 |
| `test_pipeline.py` / `test_docling_adapter.py` / `test_chapter_splitter.py` | 解析管线（docling mock、切章） |
| `test_review.py` / `test_reviewer.py` / `test_persona.py` | FSRS 复习、复习引擎、人设 |
| `test_cors.py` | 跨域配置 |

## Mock 约定（重要坑）

- **绝不用模块级 `os.environ.setdefault` 控制测试行为**——`backend.tests.*` 共享 `app_settings` 单例，import 顺序会互相覆盖。一律 `monkeypatch.setattr("backend.X.app_settings.Y", value)` 显式设置
- SSE 事件断言：`e["type"] == "text-delta"` + `e["delta"]`（EV_TEXT 实际值在 `backend/engine/providers.py:20`，不是 "text"）
- AI 调用全部 mock（不烧 token）；docling 用假 worker/跳过真实解析

## 前端：无单测框架

- 小程序/网页版均未配测试框架。验证手段：
  1. 微信开发者工具模拟器 + `wechatide` CLI 自动化（automation_evaluate 直调 `$vm` 方法、automation_element_action 点击/输入、截图）
  2. Playwright 驱动 http://localhost:5173（网页版 E2E，脚本在 `out/` 目录，非仓库资产）
  3. 生产验证：SSH 探针（curl 链路）+ nginx access log 区分 devtools/真机来源（UA 含 `wechatdevtools/`）

## 手工回归清单（发版前）

- 小程序：书架加载→搜索→上传 reused 秒回→正常上传→选书教学→刷新续学
- 网页版：免登录直达→搜索→上传→同书秒回→匿名 SSE→刷新续学
- 双端独立性：`git diff frontend-web/ backend/`（改小程序时）或 `git diff frontend/ backend/`（改网页时）必须为空
