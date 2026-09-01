"""生成一份模拟"操作系统复习资料"的测试 PDF。

刻意包含真实课本的特征：
- 每页顶部页眉（书名，反复出现）→ 用于验证页眉/页脚过滤
- 每页底部页码（反复出现）→ 同上
- 多级标题（章 18pt / 节 14pt / 正文 10.5pt）→ 用于验证字号标题识别
- 中文内容（用 PyMuPDF 内置中文字体 china-s）
"""
from __future__ import annotations

from pathlib import Path

import pymupdf as fitz

HEADER = "操作系统 · 期末复习资料"
TITLE = "第一章 操作系统概述"
BODY = (
    "操作系统（Operating System，OS）是管理计算机硬件与软件资源的系统软件，"
    "同时也是计算机系统的内核与基石。操作系统需要处理如管理与配置内存、"
    "决定系统资源供需的优先次序、控制输入设备与输出设备、操作网络与管理文件系统等基本事务。"
)
BODY2 = (
    "操作系统的功能包括进程管理、内存管理、文件系统管理、设备管理与用户接口五个方面。"
    "其中进程管理负责进程的创建、调度与撤销；内存管理负责地址空间分配与回收；"
    "文件系统管理负责文件的组织、存储与访问控制。"
)
SUBS = [
    ("1.1 操作系统的定义", "操作系统是配置在计算机硬件上的第一层软件，是对硬件系统的首次扩充。"),
    ("1.2 操作系统的功能", BODY2),
    ("1.3 操作系统的分类", "按用户界面与使用环境，操作系统可分为批处理系统、分时系统与实时系统三大类。"),
]
CHAPTERS = [
    ("第二章 进程管理", "进程是程序在一个数据集合上运行的过程，是系统进行资源分配和调度的基本单位。"),
    ("第三章 内存管理", "内存管理的核心目标是提高内存利用率并为用户提供足够的地址空间。"),
]

OUT = Path(__file__).resolve().parent.parent.parent / "data" / "test"


def build(path: Path = OUT / "操作系统_复习资料.pdf") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page_w, page_h, margin = 595, 842, 50

    def new_page_with_frame():
        p = doc.new_page(width=page_w, height=page_h)
        # 页眉（放大测试重复行过滤的鲁棒性：大字号标题可能撞到页眉规则）
        p.insert_text((margin, 30), HEADER, fontsize=9, fontname="china-s")
        # 页脚页码
        p.insert_text((page_w / 2 - 5, page_h - 20), f"第 {p.number + 1} 页", fontsize=9, fontname="china-s")
        return p

    # 第 1 页：章标题 + 小节（章标题字号与其他章一致 16pt）
    p = new_page_with_frame()
    p.insert_text((margin, 90), TITLE, fontsize=16, fontname="china-s")
    p.insert_text((margin, 120), BODY, fontsize=10.5, fontname="china-s")
    y = 160
    for sub, text in SUBS:
        p.insert_text((margin, y), sub, fontsize=14, fontname="china-s")
        y += 30
        p.insert_text((margin, y), text, fontsize=10.5, fontname="china-s")
        y += 40

    # 第 2 页起：后续章节（各自新页，带上一样的页眉页脚）
    y = 90
    for ch, text in CHAPTERS:
        p = new_page_with_frame()
        p.insert_text((margin, y), ch, fontsize=16, fontname="china-s")
        p.insert_text((margin, y + 30), text, fontsize=10.5, fontname="china-s")
        p.insert_text((margin, y + 70), BODY2, fontsize=10.5, fontname="china-s")

    doc.save(path)
    doc.close()
    print(f"测试 PDF 已生成：{path}")
    return path


if __name__ == "__main__":
    build()