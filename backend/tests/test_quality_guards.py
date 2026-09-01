"""质量护栏单测：选项洗牌 + 反馈防答案泄漏（真实引擎验收发现的两个问题）

运行：pytest backend/tests/test_quality_guards.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from backend.engine.quiz import shuffle_options
from backend.engine.schemas import Option, QuestionSpec, QuestionType


def _choice(**kw) -> QuestionSpec:
    base = dict(
        question_id="q1", topic="t", question_type=QuestionType.single_choice,
        stem="题目", correct_answer=["A"],
        options=[Option(key="A", text="管理硬件、服务程序的软件"),
                 Option(key="B", text="一种硬件设备"),
                 Option(key="C", text="一个普通应用")],
    )
    base.update(kw)
    return QuestionSpec(**base)


def test_shuffle_preserves_options_and_remaps_correct():
    q = shuffle_options(_choice())
    keys = [o.key for o in q.options]
    assert sorted(keys) == ["A", "B", "C"]                # 键保持完整
    # 选项文字集合不丢（顺序可变）
    assert sorted(o.text for o in q.options) == sorted(["管理硬件、服务程序的软件",
                                                        "一种硬件设备", "一个普通应用"])
    assert len(q.correct_answer) == 1 and q.correct_answer[0] in keys
    # 正确项文字与 new key 对齐（映射一致）
    idx = next(i for i, o in enumerate(q.options)
               if o.key == q.correct_answer[0])
    assert q.options[idx].text == "管理硬件、服务程序的软件"


def test_shuffle_randomizes_position():
    """跑多次，正确项位置应出现过多个不同 key（随机有效）。"""
    positions = set()
    for _ in range(60):
        q = shuffle_options(_choice())
        positions.add(q.correct_answer[0])
    assert len(positions) >= 2


def test_shuffle_single_option_noop():
    from backend.engine.schemas import QuestionType as QT
    q = QuestionSpec(question_id="q", question_type=QT.true_false,
                     stem="s", correct_answer=["对"])
    out = shuffle_options(q)
    assert out.correct_answer == ["对"]


def test_sanitize_feedback_strips_answer_leak():
    from backend.engine.tutor.actions import _sanitize_feedback
    q = _choice()
    leaked = ("你选对了答案 A，管理硬件、服务程序的软件 正是其定位。"
              "再想想 B 为什么不对，结合教材。")
    out = _sanitize_feedback(leaked, q)
    assert "A" not in out and "B" not in out and "C" not in out
    assert "管理硬件、服务程序的软件" not in out
    assert "再想想" in out                                 # 引导保留
    assert "正是其定位" in out                              # 正文不受损


def test_sanitize_keeps_non_option_letters():
    from backend.engine.tutor.actions import _sanitize_feedback
    q = _choice()
    out = _sanitize_feedback("API 调用是正路，G 是干扰字母", q)
    assert "API" in out                                    # 多字母词不被误删
    assert "G" in out                                      # 非选项字母保留


def test_structured_aliases_normalize_self_named_fields():
    """模型把 stem 自拟成 question → alias 归一化（真实引擎验收发现的落 mock 根因）。"""
    from backend.engine.structured import _apply_aliases
    data = {"question_type": "single_choice", "question": "操作系统本质是什么？",
            "options": [{"key": "A", "text": "软件"}]}
    out = _apply_aliases(data, {"stem": ["question", "text"]})
    assert out["stem"] == "操作系统本质是什么？" and "question" not in out
    # 已有 stem 不被覆盖
    keep = _apply_aliases({"stem": "已存在"}, {"stem": ["question"]})
    assert keep["stem"] == "已存在"