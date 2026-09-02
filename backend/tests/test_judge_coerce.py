# -*- coding: utf-8 -*-
"""AnswerJudgement 宽容归一测试：LLM 歪格式不应炸校验、不应中断判定流。

背景（2026-09-01 真机实测）：判定 LLM 偶发把 misconceptions 写成字符串，
Pydantic 校验失败 → chat_json 重试耗尽 → SSE 判定流中断、徽章出不来。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.engine.schemas import AnswerJudgement


BASE = {
    "correctness_level": "partial_correct",
    "decision": "practice_question",
}


def test_misconceptions_string():
    """实测场景：misconceptions 是纯字符串。"""
    j = AnswerJudgement.model_validate({
        **BASE,
        "misconceptions": "学生混淆了页和页框；认为页表存放在页内",
    })
    texts = [m.description for m in j.misconceptions]
    assert "学生混淆了页和页框" in " ".join(texts), texts
    assert len(j.misconceptions) == 2, texts


def test_misconceptions_single_dict():
    j = AnswerJudgement.model_validate({
        **BASE,
        "misconceptions": {"concept": "paging", "description": "概念混淆", "evidence": "原话"},
    })
    assert len(j.misconceptions) == 1
    assert j.misconceptions[0].concept == "paging"


def test_misconceptions_mixed_list():
    j = AnswerJudgement.model_validate({
        **BASE,
        "misconceptions": [
            {"concept": "a", "description": "正经条目"},
            "被写成字符串的条目",
        ],
    })
    assert len(j.misconceptions) == 2
    assert j.misconceptions[1].description == "被写成字符串的条目"


def test_weak_points_string():
    j = AnswerJudgement.model_validate({
        **BASE,
        "weak_points": "分页地址转换不熟",
    })
    assert len(j.weak_points) == 1
    assert "分页地址转换" in j.weak_points[0].evidence


def test_feedback_string():
    j = AnswerJudgement.model_validate({
        **BASE,
        "feedback": "方向对了，再想想页表的作用。",
    })
    assert j.feedback.positive == "方向对了，再想想页表的作用。"
    assert j.feedback.correction == ""


def test_normal_shape_untouched():
    """正常格式不受宽容逻辑影响。"""
    j = AnswerJudgement.model_validate({
        **BASE,
        "misconceptions": [{"concept": "c", "description": "d", "evidence": "e"}],
        "feedback": {"positive": "好", "correction": "差一点", "hint": "再想"},
        "weak_points": [{"skill_id": "s", "mastery": "low", "evidence": "x"}],
    })
    assert j.misconceptions[0].concept == "c"
    assert j.feedback.hint == "再想"
    assert j.weak_points[0].skill_id == "s"
