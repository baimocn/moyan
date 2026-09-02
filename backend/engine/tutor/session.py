"""教学会话状态（数据 + 状态枚举，不含行为逻辑）"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..schemas import Decision, KnowledgePlan, QuestionSpec, TutorState


@dataclass
class TutorSession:
    """一次教学会话的可持久化状态。"""
    session_id: str
    doc_id: str
    chapter_index: int
    chapter_title: str = ""
    plan: KnowledgePlan | None = None
    kp_idx: int = 0
    state: TutorState = TutorState.explain
    current_question: QuestionSpec | None = None
    solicit_count: int = 0            # 学生累计索要答案次数（宽松策略）
    hint_level: int = 0               # 脚手架阶梯 0-3（0 诊断/1 指向/2 思路第一步/3 先思路后结论）
    wrong_streak: int = 0
    reteach_count: int = 0
    last_decision: Decision | None = None
    weak: dict[str, str] = field(default_factory=dict)   # skill_id -> mastery
    turn_history: list[dict] = field(default_factory=list)
    last_context: str = ""            # 当前 kp 的教材微点（缓存）
    last_explain: str = ""
    exam_questions: list[QuestionSpec] = field(default_factory=list)
    exam_idx: int = 0
    exam_scores: dict[str, float] = field(default_factory=dict)
    greeting: str = ""                # 人物化开场白（D11，start 时合成，不持久化）
    user_id: str = ""                 # 鉴权落档（2026-09-02 部署前置），空 = 游客/未鉴权
    _saved_turns: int = 0             # 落库游标（增量写 turn）

    def to_snapshot(self) -> dict:
        """落库/快照用（不含大文本）。"""
        return {
            "session_id": self.session_id,
            "doc_id": self.doc_id,
            "chapter_index": self.chapter_index,
            "chapter_title": self.chapter_title,
            "state": self.state.value,
            "kp_idx": self.kp_idx,
            "weak": dict(self.weak),
            "solicit_count": self.solicit_count,
            "wrong_streak": self.wrong_streak,
            "reteach_count": self.reteach_count,
            "kp_names": [k.name for k in (self.plan.kps if self.plan else [])],
        }