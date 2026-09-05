# 墨衍 · AI 同桌式自考辅导平台

> **当前状态（2026-09-05）**：双前端（微信小程序 0.2.x 审核中 + 网页版已上线）+ 单后端，M4「加固与升级」已交付。接手/协作请先读 `墨衍-交接文档-v5-20260905.md`（现行交接文档）；下文为项目早期骨架说明，结构仍准确，功能以交接文档为准。

> 品牌名**墨衍**：从"白墨"衍生——深、静、有生机、藏锋于内。
> 规划文档：`墨衍-项目规划.md`（开新对话时把本文件路径发给 AI 即可无缝继续）。

## 技术栈（已定案）

| 层 | 选型 | 说明 |
|---|---|---|
| 前端 | **uni-app（Vue3）** | H5 端先做网页调试，同一套代码编译微信小程序/安卓 |
| 后端 | **FastAPI**（uvicorn） | 异步原生，自动接口文档 |
| 数据库 | **PostgreSQL** | 本地已配置（moyan/moyan_dev_2026@5432），
  与生产一致；无 PG 环境时可用 `MOYAN_DB_URL` 指向 SQLite 降级 |
| 解析 | **Docling**（全类型→MD：PDF/DOCX/PPTX/XLSX/HTML/EPUB/图片；版面/表格/公式/扫描OCR）
  + RapidOCR 快检兜底 | 独立 `.docling-venv`（py3.13）；PPT 表格无损实测 |
| AI（规划） | Provider 抽象层（OpenAI 兼容协议） | 主/备引擎可切，评测后定 |
| 部署 | systemd + uvicorn + nginx（不 Docker） | 适配 2G/2核 云服务器 |

## 架构（工业级分层，v0.3）

```
backend/
├── main.py            # API 入口（组装 + lifespan + /api/health）
├── settings.py        # 集中配置（pydantic-settings：App/Db/AI 分节，支持 .env）
├── container.py       # 服务容器（DI：EngineFactory 唯一 client 工厂 + 服务装配 + mock 显式治理）
├── models/            # 数据访问层（db 基座 + Document/Task；session 落库待加）
├── engine/            # AI 能力层
│   ├── schemas.py     #   领域模型（判定/出题/知识点）
│   ├── prompts.py     #   提示词体系（教师角色/判定/出题/校对）
│   ├── providers.py   #   LLM Provider 抽象（OpenAI 兼容，流式）
│   ├── router.py      #   主备降级路由（熔断）
│   ├── judge/quiz/proofread  # 判定/出题/教材校对（client 由容器注入）
│   └── tutor/         #   教学状态机（session 数据 / actions 行为 / service 编排，依赖注入）
├── services/          # 资料解析层（pdf/ocr/切章/版式）
├── routers/           # API 路由层（auth/upload/documents/tasks/tutor/study/admin/metrics）
├── tasks.py           # 后台解析 worker（线程队列）
├── migrations/        # alembic schema 迁移（M4）
└── storage.py         # 文件存储
```

纪律：依赖单向（routers→engine→models→storage）；一文件一职责；无僵尸代码；单测覆盖（pytest）。

## 真实引擎配置（OpenGo 网关）

在项目根 `.env`（已 gitignore）或环境变量配置：

```
MOYAN_AI_MAIN_BASE_URL=https://opencode.ai/zen/go/v1   # OpenGo OpenAI 兼容端点
MOYAN_AI_MAIN_KEY=sk-xxxx                                # OpenGo 套餐密钥
MOYAN_AI_MAIN_MODEL=deepseek-v4-flash                    # 教学对话（可换 deepseek-v4-pro 等）
MOYAN_AI_CHEAP_BASE_URL=...                              # 出题/总结粗活（同网关省钱）
MOYAN_AI_CHEAP_KEY=...
MOYAN_AI_CHEAP_MODEL=deepseek-v4-flash
```

OpenGo 网关模型全家桶（/models）：deepseek-v4-pro/flash、glm-5.3、qwen3.8、kimi-k3、
minimax-m3、gpt-5.6-luna、grok-4.6 等 31 个；OpenAI 兼容协议，穷要浏览器 UA 过 Cloudflare。

## 真实教学体验实录（2026-08-27 验证）

以《操作系统复习资料》第一课：知识点序列为教研级 8 点（概念→功能总览→进程/内存/文件/设备→用户接口→分类）；讲解苏格拉底式（一次一点"我先只讲这一个点"、教材依据"首次扩充"、类比"硬件的大管家"、以问题收尾并停嘴）；判定实测 correct→skip 推进、incorrect→reteach + 薄弱点 `os/functions:low` 入账；meta 事件带 provider/latencyMs 可观测。

```bash
pip install -r requirements.txt
# 真实 AI：设置环境变量 MOYAN_AI_MAIN_BASE_URL/API_KEY/MODEL（可加 MOYAN_AI_FALLBACK_* 作兜底）
# 本地演示（无 key）：MOYAN_AI_MOCK=1
python run.py                      # http://127.0.0.1:5001  (/docs 接口文档, /api/health 状态)
python -m pytest backend/tests     # 单测（含教学状态机 5 项）
```

注意（生产保护）：未配置 AI key 且未开 MOYAN_AI_MOCK 时，教学接口返回 503，
不会用规则 mock 冒充真判定——防止"假老师"。

## 怎么跑

```bash
pip install -r requirements.txt
python run.py                      # 启动 http://127.0.0.1:5001（生产模式，无 reload）
```bash
# 解析引擎（Docling）独立环境（后端是 py3.14，docling 依赖无 3.14 轮子）：
uv venv --python 3.13 .docling-venv
uv pip install --python .docling-venv\Scripts\python.exe docling
# 国内模型下载慢时：$env:HF_ENDPOINT="https://hf-mirror.com"
```

```

浏览器打开 http://127.0.0.1:5001：拖入 PDF → 自动解析 → 左侧章节目录，右侧预览/原文。

## 学习档案（P0 落库，2026-08-27）

```
teaching_sessions / turns / judgements / weaknesses  四张表（SQLite 本地 / PostgreSQL 生产）
```

- **会话持久化**：章节、状态、知识点序列、当前题目、薄弱点全部落库；
  **服务重启不丢，/api/study/resume 直接续学**（恢复后可直接答上一轮题目，实测正确）；
  /api/tutor/turn 也支持按档案自动恢复（无需先 resume）
- **判定/薄弱点审计**：每次判定的 JSON 全量入库；薄弱点按 skill_id 聚合（times_low 计数），
  中文名由知识点标签映射（不再把英文 skill_id 当名字）
- **复习调度（官方 FSRS，2026-08-27 升级）**：
  `fsrs`（py-fsrs 官方库，现行模型，目标保持率 90%）替换 FSRS-lite：
  卡片四态（Learning/Review/Relearning）与稳定性/难度/可提取率全量落库；
  到期队列按"预计挽回记忆/分钟"代理指标排序（遗忘风险 × 薄弱权重 × 遗忘次数加成）；
  概念级→章节级聚合（`/chapters`）：每章到期数/掌握度画像
- **复习会话（engram 失败回收）**：自评制（again/hard/good/easy）；
  答错 → 立即给教材片段（重讲）→ 留队再答一次；连忘 2 次放行（FSRS 推回重学步）
- **AI 用量落库**：turns 记录每次讲解流的 token（prompt/completion/估算），
  `/stats` 汇总 tokens（成本核算第一步；判定/出题结构化调用暂未暴露 usage，属已知限制）
- **档案 API**
  | GET /api/study/{doc_id}/sessions | 历史会话 |
  | GET /api/study/{doc_id}/weaknesses | 薄弱点档案（含 FSRS 卡片字段） |
  | GET /api/study/{doc_id}/stats | 掌握度统计（弱/中/强 + 判定数 + 到期数 + token 用量） |
  | GET /api/study/{doc_id}/reviews | 到期待复习薄弱点（FSRS 优先级 + 理由） |
  | GET /api/study/{doc_id}/chapters | 概念→章节聚合（到期/掌握度画像） |
  | POST /api/study/review | 记录复习结果（again/hard/good/easy；FSRS 重排） |
  | POST /api/study/review-session/start | 开始复习会话（队列 + 教材微点） |
  | POST /api/study/review-session/{sid}/answer | 评分一项（again 触发失败回收） |
  | GET /api/study/review-session/{sid} | 会话进度/评分分布 |
  | POST /api/study/resume | 服务重启后续学 |
- 数据库入口统一（settings），测试库与开发库隔离（conftest）；
  旧库自动"加列"迁移（init_db 幂等，不删数据）

## 接口一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/upload | 上传资料：文本层秒级返回；扫描件返回 task_id 进后台队列（超上限 413） |
| GET  | /api/documents | 文档清单（PostgreSQL/SQLite） |
| GET  | /api/documents/&lt;doc_id&gt; | 文档详情（含章节清单） |
| GET  | /api/documents/&lt;doc_id&gt;/chapters/&lt;index&gt; | 章节 Markdown 原文 |
| GET  | /api/tasks/&lt;task_id&gt; | 后台任务进度（ocr 异步必备） |
| POST | /api/tutor/start | 开一章的教学会话（doc/章节不存在 → 404） |
| POST | /api/tutor/turn | 教学轮（SSE；服务重启后按档案自动恢复） |
| GET  | /api/study/&lt;doc_id&gt;/reviews | 到期复习队列（FSRS 排序 + 理由） |
| GET  | /api/study/&lt;doc_id&gt;/chapters | 概念→章节聚合 |
| POST | /api/study/review | 复习结果入账（FSRS 重排） |
| POST | /api/study/review-session/start | 复习会话（again 失败回收：片段重讲+再答） |
| POST | /api/study/review-session/&lt;sid&gt;/answer | 评分一项 |
| GET  | /docs | FastAPI 自动接口文档（Swagger） |

## 大文件/扫描件 CLI（也可先跑通再决定是否走网页）

```bash
python tools/ocr_convert.py "D:\Desktop\电子书\普通生物学.pdf" [doc_id] [--work 已有OCR产物目录] [--no-proofread]
python tools/import_legacy_docs.py   # 把旧 CLI 产物登记进 DB（幂等）
```

## 自测

```bash
python -m backend.tests.test_pipeline   # 文本层 PDF：端到端验证
```

## 真实验收：《普通生物学（第3版）》105MB / 466 页扫描件

- 该书是 Pdg2Pic 扫描件（**零文本层**），自动切本地 OCR：
  **RapidOCR（PP-OCR + ONNX Runtime，免费离线）**，150dpi + 8 进程并行，
  全本 466 页 → **约 2 分钟**（断点续跑可只补缺页）；
- 文字质量：抽样同页对比 Windows 自带 OCR，错字从每 8 行 4+ 处降到 0
  （"纟目织、器官和系统"→"组织、器官和系统"、"瞢羹果"→"菁葵果"、
  "生物苜养与代谢"→"生物营养与代谢"）；
- 切章结果：41 段，九大章全部正确识别——
  前言 / 第一章细胞（112k 字）/ 第二章组织、器官和系统（71k 字整段）/
  第三章生物的营养与代谢 / 第四章生物的繁殖与发育 / 第五章生物的类群 /
  第六章生物与环境 / 第七章遗传与变异 / 第八章生物的起源与进化 /
  第九章生命科学研究的热点领域；
- 已知限制（已记录）：Windows OCR 已弃用为主引擎（错字太多）；RapidOCR 下
  偶见**一章被章内小节标题切成多段**（内容完整、归位正确）。确定性解法是
  【目录页对齐切章】（第 6-9 页目录给出权威章节清单+页码 → 页级切分，
  一章一刀），已列入下一步。

## 数据落盘（data/ 已 gitignore）

```
data/uploads/{doc_id}/原始文件
data/markdown/{doc_id}.md              转换结果（原原本本）
data/chapters/{doc_id}/chapter_XXX.md  章节切片
data/chapters/{doc_id}/chapters.json   章节清单（含 toc）
data/work/ocr_{doc_id}/                OCR 中间产物（ocr_lines.json 保留；pngs 任务完成后自动清理）
```

- 文档清单在 **DB documents 表**（旧 data/documents.json 已废弃，仅历史留档）
- 历史 CLI 产物（《普通生物学》两版）已通过 `tools/import_legacy_docs.py` 导入 DB
- 存储最小化（D8）：文本层/OCR 完成后删除原件与 OCR 页图（保留 ocr_lines.json 供校对复用）

## 自测

```bash
python -m backend.tests.test_pipeline
```

生成一份模拟"操作系统复习资料"PDF（含页眉/页码/多级标题），端到端验证"PDF→MD→分章节"。

## 已知局限（第 1 阶段接受，记录留档）

- 多栏排版阅读顺序、真实表格结构、公式暂不处理（图片先提示，OCR 阶段以文本为主）；
- Windows OCR 对汉字有错字，OCR 源切章会出现一章多段（见上方验收记录）；
- 标题识别是启发式：PDF 文本层按字号，扫描件按"标题模式+行高"；
- 后续阶段按规划接入：Word/PPT/TXT/MD 解析、AI 总结/教学、学习档案、微信小程序。