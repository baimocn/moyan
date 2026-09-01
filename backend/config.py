"""墨衍 · 全局路径与常量（运行时配置统一入口在 settings.py）

本文件只保留：
- 数据目录布局（本地文件存储，已 gitignore）；
- 从 settings 复读的常量（唯一事实源 = settings.py / .env / 环境变量）。
"""
from pathlib import Path

from .settings import app_settings

# 项目根目录 = 本文件上两级的目录（backend/config.py -> 项目根）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 数据目录（运行时生成，已 gitignore）
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"      # 原始上传文件
MARKDOWN_DIR = DATA_DIR / "markdown"   # 转换后的 Markdown
CHAPTERS_DIR = DATA_DIR / "chapters"   # 按章节切割的产物
WORK_DIR = DATA_DIR / "work"           # OCR 中间产物（png / 行流 json）

# 静态资源（调试网页）
STATIC_DIR = PROJECT_ROOT / "backend" / "static"

# ---- 以下常量唯一事实源在 settings.py（MOYAN_* 环境变量 / .env 覆盖） ----
HOST = app_settings.host
PORT = app_settings.port
MAX_UPLOAD_MB = app_settings.max_upload_mb

# 扫描件处理：自动用本地 OCR 兜底（免费，不烧 token）
OCR_AUTO = True          # 检测到扫描件时自动 OCR 重跑
OCR_DPI = app_settings.ocr_dpi
OCR_ENGINE = app_settings.ocr_engine   # rapid=RapidOCR(PP-OCR, 准) | win=Windows OCR(备)
OCR_WORKERS = app_settings.ocr_workers
OCR_INTRA_THREADS = app_settings.ocr_intra_threads

# 解析引擎：docling（主）/ legacy（RapidOCR + 文本层快路径）
PARSER_ENGINE = app_settings.parser_engine
DOCLING_VENV_PY = PROJECT_ROOT / ".docling-venv" / "Scripts" / "python.exe"
DOCLING_WORKER = PROJECT_ROOT / "tools" / "docling_worker.py"
# Docling 直读的"快速办公格式"同步上限（超过走异步任务）
OFFICE_SYNC_MAX_MB = 8

# 架构原则：所有格式先转 Markdown，再分章节。
# Docling 主引擎覆盖：pdf / docx / pptx / xlsx / html / epub / 图片 / md / txt
# 扩展名 -> 后端服务名（与 services 中的解析函数一一对应）
SUPPORTED_FORMATS = {
    ".pdf": "docling",
    ".docx": "docling",
    ".pptx": "docling",
    ".xlsx": "docling",
    ".html": "docling",
    ".epub": "docling",
    ".png": "docling",
    ".jpg": "docling",
    ".jpeg": "docling",
    ".tiff": "docling",
    ".md": "md",
    ".txt": "md",
}

# 章节切割：无一级标题时，把"最低级别标题"当作顶层章节
MIN_TOP_LEVEL = 1
MAX_HEADING_LEVEL = 6


def ensure_dirs() -> None:
    """确保所有数据目录存在。"""
    for d in (DATA_DIR, UPLOAD_DIR, MARKDOWN_DIR, CHAPTERS_DIR, WORK_DIR):
        d.mkdir(parents=True, exist_ok=True)