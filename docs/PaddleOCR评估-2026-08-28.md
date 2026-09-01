# 墨衍 · PaddleOCR（PP-StructureV3）评估记录（2026-08-28）

> 目标：评测能否用 PaddleOCR 补齐 RapidOCR 缺失的"表格结构 + 公式 + 版面"，
> 为"正文 RapidOCR 主跑 + 表格/公式页定向精修"决策提供实测证据。

## 一、环境与样本

- 独立 Python 3.13 venv（`.ocr-venv`，uv 创建）：paddlepaddle 3.3.1 + paddleocr 3.7.0 + paddlex[ocr]
- 样本：《普通生物学（第3版）》原书 PDF（110MB，data/uploads/qlsb-verified/），
  取 3 张真实表格页（134/343/377，其中 343=染色体数表、377=遗传病表），150dpi 渲染
- 对照：RapidOCR（现生产引擎）同页

## 二、平台坑（重要，别人会再踩）

1. **paddlepaddle 无 Python 3.14 轮子**（当前系统是 3.14）→ 需要 py3.13 独立 venv
2. **paddle 3.3.1 Windows CPU 默认 oneDNN 崩溃**：
   `ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute]`
   → 解法：`PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=False`（纯 paddle 算子路径）
   （`FLAGS_use_mkldnn=0` / `FLAGS_enable_pir_api=0` 均无效）
3. paddleocr 3.7 结构化管道类名：**`PPStructureV3`**（顶层导出，非 PPStructure）

## 三、实测结果

| 项 | RapidOCR（生产） | PaddleOCR PP-StructureV3 |
|---|---|---|
| 单页耗时（CPU，150dpi） | 2.7~4.1s | **88~183s**（server 模型 + 纯 paddle） |
| 正文文本 | ✅ 80~102 行 | ✅ 91~111 行（PP-OCRv5/v6，精度相当/略优） |
| **表格结构** | ❌ 只能读成一行行文字 | ✅ **还原 HTML**（9行×3列，染色体数 38/14/24… 全部正确） |
| **公式（内联数学）** | ❌ 无 | ✅ LaTeX（`2n=46,n=23`、`0.2\sim3.0\mu m` 等） |
| **版面分区** | ❌ 无 | ✅ 标题/正文/页眉/页码/图/图题/表格/公式 分区（置信 0.85~0.99） |

## 四、结论与建议

- **能力真实，价值明确**：表格/公式正是扫描教材当前最脏的部分，PP-Structure 能直接产出
  MD 友好结构（表格 HTML / 公式 LaTeX / 版面序）。
- **代价不可忽略**：本地 CPU **约 3 分钟/页**（server 模型 + 被迫关 mkldnn），
  **2G/2核 服务器做整本不可接受**。
- **推荐方案：定向精修，不换主引擎**：
  RapidOCR 继续主跑正文；仅在检测到"表格/公式特征"的页（短数字行密集/行内数学符号）
  定向调 PP-Structure 精修，把 HTML 表格、LaTeX 公式并入章节 MD。
  适合场景：本地离线精修 / 章节级按需 / 用户点选页。
- 加速路径（后续可选）：换一台无 oneDNN bug 的 paddle 版本看能否开 mkldnn；
  或换 mobile/轻量模型组合；或 PaddleOCR 的 C++/部署模型。

## 五、可复用资产

- `.ocr-venv`：python 3.13 + paddle 全套（约几百 MB，工具目录）
- `data/work/ppocr_probe/`：3 页 PNG（150/200dpi）+ 结果 JSON/HTML/md 证据
- 平台坑记录见上文第二节（交接文档已同步）