"""D11 4 引擎缺陷修复锁单测（2026-09-02）

源自 docs/人物设计-D11-墨衍人物卡-2026-08-29.md 第六节"实测抓出的引擎缺陷（4 个，均已定位待修）"。
代码层面 4 个都已实装（8-29 后迭代过），这里写单测防回归：

1. P1 两题叠一：教师提示词"教学流程"段明令"讲解正文不以提问结尾、不另出追问"
2. P1 防泄漏净化器：_sanitize_feedback 只遮正确项文字,干扰项文字与字母都保留
3. P2 skip 无桥句：actions.evaluate 的 skip 分支 yield 桥句 text + meta next_kp
4. P3 讲解态输入无回执：actions.explain 收到非空 user_text 先 yield 收束句
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from backend.engine.schemas import Option, QuestionSpec, QuestionType
from backend.engine.tutor.session import TutorState


@pytest.fixture(autouse=True)
def _fake_storage(monkeypatch):
    """start_chapter 需 storage 提供假清单（与 test_tutor_fsm 同款 autouse）。"""
    from backend.engine.tutor import service as svc
    manifest = [{"index": 0, "title": "第一章", "toc": []}]
    monkeypatch.setattr(svc.storage, "get_chapter_manifest", lambda doc_id: manifest)
    monkeypatch.setattr(svc.storage, "get_chapter",
                        lambda doc_id, idx: {"markdown": "第一章 内容片段。"})


# === 缺陷 1: P1 两题叠一 — 提示词明令不追问 ===

def test_teacher_prompt_prohibits_two_questions_one():
    """教师提示词必须明令'讲解正文不以提问结尾、不另出追问',防两题叠一误判。"""
    from backend.engine.prompts import TEACHER_SYSTEM_PROMPT
    # 必须同时含"不以提问结尾"+"不另出追问",缺一即为回归
    assert "不以提问结尾" in TEACHER_SYSTEM_PROMPT, "回归:讲解可被允许以提问结尾"
    assert "不另出追问" in TEACHER_SYSTEM_PROMPT, "回归:讲解可被允许另出追问"
    # 注释里点明根因,便于后人维护
    assert "两题叠一" in TEACHER_SYSTEM_PROMPT, "回归:两题叠一根因注释丢失"


# === 缺陷 2: P1 防泄漏净化器 — 只遮正确项 ===

def _make_choice_q(correct=("A",)) -> QuestionSpec:
    return QuestionSpec(
        question_id="q1", topic="t", question_type=QuestionType.single_choice,
        stem="题目",
        correct_answer=list(correct),
        options=[
            Option(key="A", text="管理硬件、服务程序的软件"),
            Option(key="B", text="一种硬件设备"),
            Option(key="C", text="一个普通应用"),
        ],
    )


def test_sanitize_only_masks_correct_option_text_keeps_distractors():
    """P1 净化器:正确项文字打码,干扰项文字保留(指向性提示仍可读)。"""
    from backend.engine.tutor.actions import _sanitize_feedback
    q = _make_choice_q(correct=("A",))
    # 含正确项文字 + 干扰项文字
    txt = "正解是管理硬件、服务程序的软件,不是一种硬件设备,也不是一个普通应用"
    out = _sanitize_feedback(txt, q)
    # 正确项文字被 □ 替代(已并入"管理硬件..."这个完整词)
    assert "管理硬件、服务程序的软件" not in out, "回归:正确项文字未打码"
    # 干扰项文字必须保留(否则学生看到的"是□、□还是□"指向性丢失)
    assert "一种硬件设备" in out, "回归:干扰项被打码,指向性丢失"
    assert "一个普通应用" in out, "回归:干扰项被打码,指向性丢失"


def test_sanitize_masks_all_option_letters_but_keeps_others():
    """防选X答案泄漏:全部选项字母 A-F 都被打码(防"选A"/"别选B"等指认),非选项字母保留。"""
    from backend.engine.tutor.actions import _sanitize_feedback
    q = _make_choice_q(correct=("A",))
    out = _sanitize_feedback("选 A 就对了,别选 B,也不能选 C。但 G 是干扰字母", q)
    # 全部选项字母 A/B/C 应被 □ 替代(无论正确/干扰,字母指认都是泄漏)
    assert "A" not in out, "回归:正确字母 A 未打码"
    assert "B" not in out, "回归:干扰字母 B 未打码(防'别选B'指认)"
    assert "C" not in out, "回归:干扰字母 C 未打码"
    # 非选项字母 G 保留(否则"API"、"G"等无意义被误杀)
    assert "G" in out, "回归:非选项字母被错杀"


# === 缺陷 3: P2 skip 无桥句 — skip 分支 yield 桥句 + next meta ===

@pytest.mark.asyncio
async def test_skip_emits_bridge_text_and_next_meta():
    """P2 skip 报站:答对触发 skip 时,必须先 yield 一段'下一站'桥句 text,再 yield meta next=kp 名。"""
    # 复用 test_tutor_fsm 的 make_service / grade / collect 套路
    from backend.engine.schemas import AnswerJudgement, Correctness, Decision, Feedback
    from backend.tests.test_tutor_fsm import make_service, collect

    def grade_correct_skip() -> AnswerJudgement:
        return AnswerJudgement(
            question_id="q1",
            correctness_level=Correctness.correct,
            score=1.0, decision=Decision.skip,
            feedback=Feedback(positive="好", correction="", hint=""),
            confidence=0.9,
        )

    svc = make_service([grade_correct_skip()])
    ses = await svc.start_chapter("doc-x", 0)
    await collect(svc.handle_turn(ses.session_id, "开始"))     # kp1 explain
    events = await collect(svc.handle_turn(ses.session_id, "A"))  # kp1 答对 → skip → kp2

    # 必须有"这题过了"桥句（事件 type = "text-delta" 见 backend/engine/providers.py EV_TEXT）
    text_events = [e for e in events if e.get("type") == "text-delta" and e.get("delta")]
    assert any("这题过了" in e["delta"] for e in text_events), \
        "回归:skip 无桥句 text-delta (用户换 KP 迷路)"
    assert any("下一站" in e["delta"] for e in text_events), \
        "回归:skip 桥句未提'下一站'"

    # 必须有 meta branch=next + next=知识点二
    next_metas = [e for e in events if e.get("type") == "meta" and e.get("branch") == "next"]
    assert next_metas, "回归:skip 后无 meta branch=next"
    assert next_metas[0]["next"] == "知识点二"


# === 缺陷 4: P3 讲解态输入无回执 — 2026-09-05 演进为"插话进 prompt 由模型接住" ===

@pytest.mark.asyncio
async def test_lecture_state_user_input_enters_prompt():
    """P3 演进：讲解态收到非空 user_text 时，插话必须进入讲解上下文（不再静默吞输入），
    固定收束句已退役——由模型用同桌口吻接住。"""
    from backend.tests.test_tutor_fsm import make_service

    svc = make_service([])  # 不需要 judge 结果,只验 explain 自身
    ses = await svc.start_chapter("doc-x", 0)
    assert ses.state == TutorState.explain

    # 直接调 actions.explain,模拟"讲解态收到学生插话"
    events = []
    async for ev in svc.actions.explain(ses, user_text="等等,这个词啥意思?"):
        events.append(ev)
        if len(events) >= 2:
            break  # 收够前两条即可

    prompt = svc._router_for_test.last_content
    assert "等等,这个词啥意思?" in prompt, \
        f"回归:插话未进讲解上下文(静默吞输入): {prompt[:120]!r}"
    assert "学生插话" in prompt, "回归:插话段丢失"
    # 固定收束句退役：流里不应再出现"记下了"复读
    assert all("记下了" not in (e.get("delta") or "") for e in events), \
        "回归:固定桥句复辟"


@pytest.mark.asyncio
async def test_lecture_state_empty_input_no_note():
    """P3 边界:user_text 为空时(初次讲解),prompt 不含【学生插话】段,直接进入讲解流。"""
    from backend.tests.test_tutor_fsm import make_service

    svc = make_service([])
    ses = await svc.start_chapter("doc-x", 0)
    events = []
    async for ev in svc.actions.explain(ses, user_text=""):  # 空 → 无插话段
        events.append(ev)
        if len(events) >= 1:
            break
    assert "学生插话" not in svc._router_for_test.last_content, \
        "回归:空 user_text 仍注入了插话段"
