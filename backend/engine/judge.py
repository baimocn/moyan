"""墨衍 · 判定服务（学生回答 → AnswerJudgement）

真实现：结构化输出助手（json_object + pydantic 校验重试，D1 修订，usage 可审计）。
Mock 模式：无 key 空跑演示（规则判定）。
引擎：cheap 优先（判定是粗活，省钱），缺省回落 main。
"""
from __future__ import annotations

import logging

from .prompts import JUDGE_INSTRUCTION
from .schemas import (AnswerJudgement, Correctness, Decision, Feedback,
                      Misconception, QuestionSpec, WeakPoint)
from .structured import chat_json

logger = logging.getLogger(__name__)


class JudgeService:
    """学生回答判定。client 由容器注入（EngineFactory）；mock 由容器显式决定。"""

    def __init__(self, container=None, mock: bool = False):
        self._client = None
        self._model = ""
        self.mock = bool(mock)
        if container is None or self.mock:
            return  # mock：由 _mock_judge 承接；container=None：测试兜底
        try:
            base, key, model = container.engine_factory.require_engine(cheap=True)
            self._client = container.engine_factory.build_async_client(base, key)
            self._model = model
        except Exception:
            self.mock = True   # 未就绪 → 兜底 mock（路由器层已 503 保护）

    async def judge(
        self,
        question: QuestionSpec,
        student_answer: str,
        context: str = "",
        solicit_count: int = 0,
        hint_level: int = 0,
    ) -> AnswerJudgement:
        """判定一次学生回答。solicit_count=学生已连续索要答案的次数（宽松策略入参）。

        hint_level=脚手架阶梯（0 诊断/1 指向/2 思路第一步/3 先思路后结论），
        judge 按 Level 生成 feedback.hint，不越级泄答案。
        返回 AnswerJudgement；usage 以属性挂在对象上（j.usage，成本审计用）。
        """
        if self.mock or self._client is None:
            return self._mock_judge(question, student_answer)
        options_text = "\n".join(f"{o.key}. {o.text}" for o in question.options) \
            or "（非选择题）"
        messages = [
            {"role": "system", "content": JUDGE_INSTRUCTION.format(
                context=context or "（无教材上下文）",
                question_stem=question.stem,
                options_text=options_text,
                knowledge_tags="、".join(question.knowledge_points) or "（无标签）",
                hint_level=max(0, min(int(hint_level), 3)),
                correct_answer="；".join(question.correct_answer),
                student_answer=student_answer or "（无回答）")},
            {"role": "user", "content": f"学生累计索要答案次数：{solicit_count}；请按 schema 判定。"},
        ]
        try:
            j, usage = await chat_json(
                self._client, self._model, messages,
                AnswerJudgement,
                temperature=0, max_retries=1,
                schema_hint="correctness_level/decision 取枚举值；feedback 苏格拉底式且不得透露选项字母",
                aliases={"question_id": ["id", "question"]},
            )
            _harmonize(j, question)
            setattr(j, "usage", usage)
            return j
        except Exception as exc:  # noqa: BLE001 重试耗尽/上游失败：保守兜底，绝不乱判
            logger.warning("判定结构化输出失败，退回保守兜底：%s", exc)
            j = self._mock_judge(question, student_answer)
            setattr(j, "usage", {})
            return j


    # ---------- mock（无 key 演示） ----------

    def _mock_judge(self, question: QuestionSpec, answer: str) -> AnswerJudgement:
        ans = (answer or "").strip()
        if not ans:
            kps = [WeakPoint(skill_id=k, mastery="low", evidence="未作答") for k in question.knowledge_points]
            return AnswerJudgement(
                question_id=question.question_id or "q",
                correctness_level=Correctness.unanswered,
                decision=Decision.practice_question,
                feedback=Feedback(positive="没关系，我们再看一遍", hint="试着回答一下"),
                weak_points=kps,
                confidence=0.6,
            )
        correct = set(k.strip().lower() for k in question.correct_answer)
        low = ans.lower()
        hits = sum(1 for c in correct if c and c.lower() in low)
        kps = [WeakPoint(skill_id=k, mastery="high", evidence="mock") for k in question.knowledge_points[:1]]
        if hits >= len(correct) * 0.8 and correct:
            return AnswerJudgement(
                question_id=question.question_id or "q",
                correctness_level=Correctness.correct, score=1.0,
                decision=Decision.skip,
                feedback=Feedback(positive="答得很好！"),
                weak_points=[], confidence=0.9,
            )
        if hits >= 1 or (correct and any(len(c) > 2 and c in low for c in correct)):
            return AnswerJudgement(
                question_id=question.question_id or "q",
                correctness_level=Correctness.partial_correct, score=0.5,
                decision=Decision.practice_question,
                misconceptions=[Misconception(concept="", description="接近但不完整（mock 判定）", evidence=ans[:50])],
                feedback=Feedback(positive="方向对了", correction="还差一点点",
                                  hint=f"想想跟关键词 {'、'.join(correct)} 的关系"),
                weak_points=kps, confidence=0.7,
            )
        return AnswerJudgement(
            question_id=question.question_id or "q",
            correctness_level=Correctness.incorrect, score=0.0,
            decision=Decision.alternative_explanation,
            misconceptions=[Misconception(concept="", description="答错了（mock 判定）", evidence=ans[:50])],
            feedback=Feedback(positive="别急", correction="这个理解需要调整",
                              hint="回到教材里那句话，再想想——正确答案涉及：" + "、".join(correct)),
            weak_points=kps, confidence=0.7,
        )

def _harmonize(j: AnswerJudgement, question: QuestionSpec) -> None:
    """判定模型常见偷懒的程序级兜底：score 与分档对齐、weak_points 缺失时补齐。

    2026-08-29 真机实测：模型常把 score 留默认 0.5、weak_points 恒空 —— 后者会
    掐断薄弱点/FSRS/章节聚合整条记忆链，这里必须在最靠近判定的位置兜住。
    """
    cl = j.correctness_level
    if cl == Correctness.correct and j.score < 0.75:
        j.score = 0.9
    elif cl == Correctness.incorrect and j.score > 0.4:
        j.score = 0.2
    elif cl == Correctness.off_topic and j.score > 0.1:
        j.score = 0.0
    if cl in (Correctness.incorrect, Correctness.partial_correct) and not j.weak_points:
        tag = question.knowledge_points[0] if question.knowledge_points else \
            (question.topic.rsplit("/", 1)[-1] if question.topic else "unknown")
        j.weak_points = [WeakPoint(skill_id=tag,
                                   mastery="low" if cl == Correctness.incorrect else "mid",
                                   evidence="判定模型未给出，系统按答错兜底")]

