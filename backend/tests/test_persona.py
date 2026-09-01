"""人物卡（D11 同桌）单测：世界书命中 / 开场白 / 人格注入提示词"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.engine.persona import (CHARACTER_BOOK, PERSONA_SECTION,
                                    compose_greeting, persona_book_hits)


def test_card_is_deskmate():
    assert "同桌" in PERSONA_SECTION
    assert "2027" in PERSONA_SECTION          # 有自己的考试（不是服务者）
    assert "错题本" in PERSONA_SECTION        # 有自己的筹码
    assert "绝不嘲身份与努力本身" in PERSONA_SECTION  # 嘲讽红线
    assert len(CHARACTER_BOOK) >= 4           # 世界书条目


def test_book_hits_by_keyword():
    hits = persona_book_hits("这节讲 E-R 图和实体联系")
    assert any("E-R" in h for h in hits)
    hits2 = persona_book_hits("范式与函数依赖判定")
    assert any("范式" in h for h in hits2)
    assert persona_book_hits("") == []
    assert persona_book_hits("毫不相关的内容") == []


def test_book_hits_limit():
    text = "物理独立性 SQL 触发器 范式"
    assert len(persona_book_hits(text, limit=2)) == 2


def test_greeting_variants():
    due = compose_greeting(title="t", kp_count=5, next_kp="自然连接",
                           due_first="物理独立性")
    assert "互相批改" in due and "物理独立性" in due and "自然连接" in due
    resume = compose_greeting(title="t", kp_count=5, next_kp="自然连接")
    assert "从这儿接着走" in resume
    new = compose_greeting(title="数据库", kp_count=5)
    assert "同一本" in new and "5" in new


def test_greeting_streak_in_deskmate_voice():
    g = compose_greeting(title="t", kp_count=5, next_kp="x", streak_days=3)
    assert "连着第 3 天" in g
    g1 = compose_greeting(title="t", kp_count=5, next_kp="x", streak_days=1)
    assert "连着" not in g1


def test_persona_injected_into_teacher_prompt():
    from backend.engine.prompts import TEACHER_SYSTEM_PROMPT
    assert "人物设定" in TEACHER_SYSTEM_PROMPT
    assert "同桌" in TEACHER_SYSTEM_PROMPT
    assert "绝不直接给答案" in TEACHER_SYSTEM_PROMPT
    assert "只依据《教材》" in TEACHER_SYSTEM_PROMPT
