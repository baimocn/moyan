# 墨衍 · 项目上下文（PROJECT.md）

*Last updated: 2026-09-05（M5 立项）*

## What This Is

墨衍——AI 辅导应用（"AI 同桌"人设）：用户上传教材 PDF/文档，系统解析成章节，AI 按"先思路后对答案"的方式一章一章带着学，带判定、出题、弱点记录与 FSRS 复习。

**双前端 · 一后端 · 数据共享**的多生态架构：

- **微信小程序**（uni-app 单工程双编译出小程序+H5）——已上线（体验版 0.2.1，2026-09-04 审核中），AppID `wx9ca2b10b07573b3d`（个人主体）
- **网页版**（Vue3 独立工程 frontend-web/）——已上线 https://moyan.baimo7715.top，免登录 + 共享书库（任何人可用，同书 sha256 去重秒回）
- **硬性约束**：两个前端代码零共享、独立可用，"一个坏了不影响另一个"；后端与数据层唯一

## Core Value

用户能上传一本教材 → 选章节 → 与 AI 同桌进行"讲思路→判定→出题→汇报"的真实学习循环，且学习进度跨设备可续。

## Context（现状与约束）

- 生产：ECS 2C2G（内存紧张 1.2G/1.6G）+ PostgreSQL16 + nginx + systemd uvicorn（1 worker）；域名 moyan.baimo7715.top
- 用户（项目所有者）**对 AI 调用成本敏感**——成本可见性是 M2 最高优先级
- 个人主体小程序：类目受限（已过"教育信息展示"），无提审 API，域名白名单随 AppID 走
- 技术栈详情见 `.planning/codebase/STACK.md`；已知风险见 `CONCERNS.md`

## Requirements

### Validated（已上线能力，棕地推断）

- ✓ 教材上传 → docling 解析 → 章节切分 → 教学就绪（小程序/网页双端）
- ✓ 教学对话：SSE 流式（讲/判定/出题/汇报），状态全在 DB，刷新续学
- ✓ 免登录身份（get_requester 三态）+ 共享书库（content_hash 去重）+ 书架搜索
- ✓ 注册/登录（网页 scrypt；小程序 wx.login→JWT）+ slowapi 限流
- ✓ 弱点记录 + FSRS 复习调度；内置示例教材（审核合规）

### Validated 补记（M2/M3/M4 全部交付，2026-09-05）

- ✓ M2+M3：权限分层/文档删除/用量观测/管理台/向量库（ADMIN/DOC/COST/STATS/ADMINUI/VEC）
- ✓ M4 加固与升级：会话归属 404、并发锁 409、生成上限、日预算熔断、限流 IP 兜底、
  Schema 健康化 + alembic、冒烟探针、书库 fail-closed + shared 下架、隐私策略（SEC/SCHEMA/OBS/CMP/DOC）

### Active（M5 功能升级，2026-09-05 立项）

- [ ] 学习数据底座：doc 级读端点鉴权收口、错题重练口径、学习报告/个人页聚合 API、上传进度契约（AUTH-04/PRAC-01/RPT-01/ME-01/UP-01）
- [ ] 网页端体验：markdown 渲染、错题本页、学习报告页、管理台图表、向量管理 UI（MD-01/PRAC-02/RPT-02/CHART-01/VECUI-01）
- [ ] 小程序升级：隐私告知展示、错题重练页、个人页、上传进度（PP-01/PRAC-03/ME-02/UP-02）——**门禁：frontend/ 冻结解除**

### Out of Scope

- 对象存储/CDN——磁盘 27G 空闲，本地文件够用
- 用户角色后台管理系统（users.role 表级 RBAC）——个人项目，env 清单足够
- 跨文档知识图谱、笔记/评论等社交功能——无场景
- 本地 embedding 模型——2C2G 内存不允许

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 免登录 + 设备身份（web_anon） | 降低使用门槛，审核要求可完整体验 | ✓ 已实施 |
| 转 md 后删原件（cleanup_original） | 省空间；原件非必需 | ✓ 已实施 |
| 转向网页版优先（2026-09-03 用户决策） | 小程序审核流程重、迭代慢 | ✓ 已交付 v2 |
| 权限模型用 env 管理员清单 | 单管理员现实，YAGNI | Pending（M2） |
| 向量库选 pgvector + 云端 embedding | 零新组件、成本可忽略、2C2G 不跑本地模型 | Pending（M3） |
| GSD 门禁全开 + 标准粒度 | 用户 2026-09-04 选定 | ✓ config.json |
| M5 顺序：后端底座→网页→小程序 | 小程序冻结未解；沿用 2026-09-03「网页优先」决策 | Pending（M5） |
| 产品定位：不收费，搜集用户-AI 对话数据 | 用户 2026-09-05 确认；限流=成本+数据质量双防线 | ✓ M4 交付 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state
