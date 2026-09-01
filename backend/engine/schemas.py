"""墨衍 · 教学引擎数据结构（Pydantic v2）

设计依据：《教学引擎设计文档》第四节，字段与调研定稿 Schema 一致。
知识点标签（skill_id / knowledge_points）全库统一，支撑"薄弱点→出题→复习"闭环。
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# ---------- 判定 ----------

class Correctness(str, Enum):
    correct = "correct"
    partial_correct = "partial_correct"
    incorrect = "incorrect"
    off_topic = "off_topic"
    unanswered = "unanswered"

    @property
    def label(self) -> str:
        return {
            "correct": "答对", "partial_correct": "部分对", "incorrect": "答错",
            "off_topic": "答非所问", "unanswered": "未作答",
        }[self.value]


class Decision(str, Enum):
    reteach = "reteach"
    alternative_explanation = "alternative_explanation"
    practice_question = "practice_question"
    skip = "skip"

    @property
    def label(self) -> str:
        return {
            "reteach": "同讲法再讲", "alternative_explanation": "换一种讲法",
            "practice_question": "出巩固题", "skip": "已掌握，进入下一知识点",
        }[self.value]


class Misconception(BaseModel):
    concept: str = Field(..., description="误区对应的知识点名（对齐 skill_id）")
    description: str = Field(..., description="学生错在哪、怎么理解的")
    evidence: str = Field("", description="学生原话片段，便于复核")


class WeakPoint(BaseModel):
    skill_id: str = Field(..., description="知识点/技能标签 ID，如 process/state")
    mastery: str = Field("low", pattern="^(low|mid|high)$")
    evidence: str = Field("", description="判定依据简述")


class Feedback(BaseModel):
    """展示给学生的话术（苏格拉底：给方向不给答案）。"""
    positive: str = Field(..., description="先肯定，1-2 句")
    correction: str = Field("", description="指出误区，不给完整答案")
    hint: str = Field("", description="引导性问题 / 下一步思考方向")


class AnswerJudgement(BaseModel):
    question_id: str = ""                  # 模型常漏；落库时由调用方以题目 id 覆盖
    correctness_level: Correctness
    score: float = Field(default=0.5, ge=0, le=1)
    misconceptions: list[Misconception] = []
    decision: Decision
    weak_points: list[WeakPoint] = []
    feedback: Feedback = Field(default_factory=lambda: Feedback(positive=""))
    confidence: float = Field(default=0.8, ge=0, le=1)
    # 运行时注入的 token 用量（exclude：不进序列化/LLM 校验；成本审计用）
    usage: dict = Field(default_factory=dict, exclude=True)


# ---------- 出题 ----------

class QuestionType(str, Enum):
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    fill_blank = "fill_blank"
    short_answer = "short_answer"

    @property
    def label(self) -> str:
        return {"single_choice": "单选", "multiple_choice": "多选", "true_false": "判断题",
                "fill_blank": "填空", "short_answer": "简答"}[self.value]


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Option(BaseModel):
    key: str = Field(..., pattern="^[A-F]$")
    text: str


class QuestionSpec(BaseModel):
    question_id: str = Field("", description="知识点ID+序号，如 process/状态转换/01")
    subject: str = ""
    topic: str = ""
    question_type: QuestionType
    stem: str
    options: list[Option] = []
    correct_answer: list[str] = Field(default_factory=list,
                                      description="选择题=[选项key]；填空/简答=要点列表")
    correct_answer_text: str = Field("", description="正确选项的文字（键-文一致性校对用）")

    @field_validator("correct_answer", mode="before")
    @classmethod
    def _coerce_correct_answer(cls, v):
        """模型偶发把 correct_answer 写成字符串（实测 "D"）——宽容归一成列表。"""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            parts = [p.strip(" .。、，,;；") for p in re.split(r"[、,，;；\s]+", v) if p.strip()]
            return parts or [v]
        return v
    knowledge_points: list[str] = Field(default_factory=list,
                                        description="与 weak_points.skill_id 同一标签体系")
    difficulty: Difficulty = Difficulty.medium
    difficulty_score: int = Field(default=3, ge=1, le=5)
    explanation: str = ""
    hint: str = ""
    estimated_time_s: int = Field(default=30, ge=5)
    # 运行时注入的出题 token 用量与耗时（exclude：不进序列化/LLM 校验；成本与性能审计用）
    usage: dict = Field(default_factory=dict, exclude=True)
    latency_ms: int = Field(default=0, exclude=True)


# ---------- 章内知识点序列 ----------

class KnowledgePoint(BaseModel):
    """章内知识点（D6：LLM 生成，学生可跳）。"""
    id: str = Field(..., description="知识点 ID，如 chapter-1/kp-02")
    name: str = Field(..., description="知识点名，如'进程的状态与转换'")
    summary: str = Field("", description="一句话说明，用于目录展示")
    skill_id: str = Field(..., description="标签体系 ID（判定/出题共用）")


class KnowledgePlan(BaseModel):
    """一章的知识点教学序列。"""
    chapter_id: str = ""                   # 模型常漏；调用方（plan_knowledge）回填
    chapter_title: str = ""                # 同上
    kps: list[KnowledgePoint] = Field(default_factory=list, description="按教学顺序排列")


# ---------- 章末考 ----------

class ExamQuestion(BaseModel):
    question: QuestionSpec
    difficulty: Difficulty


class ChapterExam(BaseModel):
    """章末考：小题组 + 掌握度报告（D10）。"""
    chapter_id: str
    chapter_title: str
    questions: list[ExamQuestion] = Field(default_factory=list)
    summary: str = ""   # 考后由判定汇总生成掌握度报告


class MasteryReport(BaseModel):
    """考后掌握度报告：各知识点掌握情况。"""
    chapter_id: str
    scores: dict[str, float] = Field(default_factory=dict)   # skill_id -> 0~1
    weak: list[str] = Field(default_factory=list)            # 薄弱 skill_id 列表
    weak_zh: list[str] = Field(default_factory=list)         # 薄弱点中文描述
    summary: str = ""


# ---------- 会话 ----------

class TutorState(str, Enum):
    init = "init"
    explain = "explain"          # 讲解当前知识点
    question = "question"        # 提问检查理解
    await_answer = "await_answer"
    evaluate = "evaluate"        # 判定
    chapter_exam = "chapter_exam"
    done = "done"


class Turn(BaseModel):
    role: str = ""               # user / assistant
    content: str = ""
    kind: str = ""               # explain / question / answer / judge…