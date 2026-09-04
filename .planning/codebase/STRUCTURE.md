# STRUCTURE — 目录布局与关键位置

*Last updated: 2026-09-04*

```
D:\Desktop\墨衍-项目\
├── backend/                     # FastAPI 后端（唯一后端）
│   ├── main.py                  # 入口：app + lifespan(init_db) + 6 routers
│   ├── settings.py              # pydantic-settings，MOYAN_* env 唯一事实源
│   ├── config.py                # 路径常量 + SUPPORTED_FORMATS + OCR 参数
│   ├── rate_limit.py            # slowapi 5 档限流器
│   ├── container.py / db.py     # db.py 是 Flask 时代死代码（勿用）
│   ├── storage.py               # 文件布局 + 章节清单 + plan 缓存
│   ├── tasks.py                 # 异步解析管线（docling→切章→proofread→清原件）
│   ├── auth/                    # jwt.py / wx.py / passwords.py(scrypt) / deps.py(get_requester) / router.py / schemas.py
│   ├── routers/                 # upload.py / documents.py / tasks.py / tutor.py / study.py
│   ├── services/                # docling_adapter.py / chapter_splitter.py / ocr_engine.py / pdf_parser.py / lines_pipeline.py
│   ├── engine/
│   │   ├── providers.py         # DeepSeek 客户端（EV_TEXT 等事件常量也在这）
│   │   ├── tutor/               # actions.py（教学状态机+SSE 产出）/ session.py / service.py
│   │   ├── review/              # FSRS 复习 service.py
│   │   ├── prompts.py           # 全部提示词（含 D11 修复：禁追问/净化器/桥句）
│   │   ├── judge.py / quiz.py / persona.py / reviewer.py / structured.py / proofread.py
│   ├── models/                  # db.py(Base+_TABLE_ADDITIONS迁移) / documents.py / study.py / tasks.py / repo.py
│   ├── static/                  # 调试网页
│   └── tests/                   # pytest（17 文件 ~1900 行）
├── frontend/                    # uni-app：微信小程序 + H5 双编译
│   ├── src/
│   │   ├── pages/index/index.vue   # 共享书架+搜索+上传（v2 核心，~600 行）
│   │   ├── pages/tutor/            # 教学对话页
│   │   ├── pages/index/guide_text.js # 内置示例教材文本（审核修复）
│   │   ├── utils/api.js            # 请求封装：Bearer+401 重试、SSE 双通道（fetch/enableChunked）
│   │   ├── utils/auth.js           # silentLogin/ensureLogin
│   │   └── manifest.json           # AppID wx9ca2b10b07573b3d
│   └── dist/build/mp-weixin      # 编译产物（微信开发者工具导入此目录）
├── frontend-web/                # Vue3 网页版（独立工程）
│   ├── src/views/               # HomeView(书架) / TutorView(SSE) / LoginView
│   ├── src/api/                 # client.js(X-Device-Id 注入) / documents.js / tutor.js / upload.js / auth.js
│   ├── src/stores/auth.js       # pinia
│   └── src/router.js            # 免登录，无强制守卫
├── deploy/                      # Caddy 备选部署（未启用；生产实际用 nginx+systemd）
├── tools/docling_worker.py      # docling 子进程 worker
├── out/                         # 会话产物（诊断脚本/spec/截图，部分含敏感副本待清理）
├── data/                        # 运行时数据（gitignore）：uploads/markdown/chapters/work
└── .planning/                   # GSD 规划（本次初始化）
```

## 命名约定

- doc_id：`YYYYMMDD-HHMMSS-6hex`（`storage.new_doc_id()`）
- 章节：`chapter_{index:03d}.md`、plan 缓存 `plan_{index}.json`
- 测试：`test_<域>.py`；env 键：`MOYAN_<域>_<键>`
- 前端事件/常量：EV_TEXT = "text-delta"（在 `backend/engine/providers.py:20`，断言别写 "text"）

## 关键已知位置（高频修改点）

| 改什么 | 去哪 |
|---|---|
| 教学流程/话术 | `backend/engine/tutor/actions.py` + `backend/engine/prompts.py` |
| 接口/鉴权语义 | `backend/routers/*.py` + `backend/auth/deps.py` |
| 解析/OCR | `backend/services/` + `backend/tasks.py` |
| 小程序 UI | `frontend/src/pages/index/index.vue` |
| 网页版 UI | `frontend-web/src/views/HomeView.vue` |
| 数据库加列 | `backend/models/db.py` 的 `_TABLE_ADDITIONS` |
