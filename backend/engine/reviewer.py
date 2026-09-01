"""墨衍 · 输出后裁判（防"支架崩塌"，设计文档第九节）

职责：判定反馈（苏格拉底式话术）产出后，按 5 项崩坏判据打分 + 4 维质量评分：
  崩坏判据：①泄漏答案 ②过度讲解 ③不再提问 ④忽视误区 ⑤角色漂移
  质量四维（AITutor-EvalKit 分类学）：错误识别/错误定位/引导提供/可执行性
触发：由 tutor/actions 按 reviewer_mode 采样调用（on|sample|off，默认 sample：
每 5 次判定一审【首判不审】+ reteach≥2 或施压≥3 时必审）。审计结果并入判定 JSON 落库。
引擎：cheap 直连（与 judge/quiz 同通道，省主引擎）；无 cheap 时回落 router.chat。
"""
from __future__ import annotations

import json
import logging
import time

from pydantic import BaseModel, Field

from .structured import chat_json

logger = logging.getLogger(__name__)


class ReviewViolation(BaseModel):
    criterion: str = Field(..., description="判据名，如 答案泄漏")
    severity: str = Field("low", pattern="^(low|mid|high)$")
    evidence: str = Field("", description="反馈里的原文片段")


class ReviewScores(BaseModel):
    """质量四维分（0-1，越高越好）。"""
    mistake_identification: float = Field(0.5, ge=0, le=1, description="是否识别了学生回答中的问题")
    mistake_location: float = Field(0.5, ge=0, le=1, description="是否定位到具体错处而非泛泛而谈")
    providing_guidance: float = Field(0.5, ge=0, le=1, description="是否提供了有效引导而非直给/空转")
    actionability: float = Field(0.5, ge=0, le=1, description="学生拿到反馈后能否明确下一步做什么")


class ReviewVerdict(BaseModel):
    passed: bool = True
    violations: list[ReviewViolation] = Field(default_factory=list)
    scores: ReviewScores = Field(default_factory=ReviewScores)
    note: str = ""


REVIEW_INSTRUCTION = """你是教学质量巡检员。下面是本次教学判定（题目/学生回答/给学生的反馈）。
请做两件事：
一、按 5 项崩坏判据检查【反馈】是否违反"苏格拉底教学铁律"：
1. 答案泄漏：反馈点名了正确选项字母(A/B/C/D)或复述了正确选项的完整文字
   ——哪怕学生答对，也不得点名选项给出答案（会让学生"背字母"通关）；
2. 过度讲解：反馈一次堆砌 3 个以上新概念或给出完整解题步骤/最终答案；
3. 不再提问：反馈没有引导性提问或下一步思考方向（正常判定应留一个钩子）；
4. 忽视误区：学生的回答暴露明显误区，反馈却未指出；
5. 角色漂移：反馈泄露系统指令、放弃教师角色、或无原则听从学生要求。
二、给反馈的质量四维打分（0~1，一位小数）：
- mistake_identification：是否识别了学生回答中的对错点；
- mistake_location：是否定位到具体错处（而非泛泛评价）；
- providing_guidance：引导是否有效（既不直给也不空转）；
- actionability：学生看完能否明确下一步做什么。

【题目】{stem}
【正确要点】{correct}
【学生回答】{student}
【系统给的反馈】{feedback}

输出：{{"passed": true/false, "violations": [{{"criterion","severity","evidence"}}],
"scores": {{"mistake_identification": 0.0, "mistake_location": 0.0, "providing_guidance": 0.0, "actionability": 0.0}}, "note": ""}}
只有确实违反铁律才标 violations；note ≤40 字，且仅在 violations 非空或某维 <0.6 时输出
（点明改进方向），否则留空——note 是给系统看的，不是给学生看的。"""


class Reviewer:
    """输出后裁判：cheap 引擎直连（structured.chat_json），无 cheap 回落 router.chat。"""

    def __init__(self, router, container=None):
        self.router = router
        self._client = None
        self._model = ""
        if container is not None:
            try:
                base, key, model = container.engine_factory.require_engine(cheap=True)
                self._client = container.engine_factory.build_async_client(base, key)
                self._model = model
            except Exception as exc:  # noqa: BLE001
                logger.warning("裁判 cheap 引擎不可用，回落 router：%s", exc)

    async def review_feedback(self, *, stem: str, correct: str,
                              student: str, feedback: str) -> dict:
        """返回 {passed, violations, scores, note, usage, engine, latency_ms?}。"""
        prompt = REVIEW_INSTRUCTION.format(
            stem=stem, correct=correct, student=student or "（无）", feedback=feedback)
        messages = [{"role": "user", "content": prompt}]
        _t0 = time.perf_counter()
        if self._client is not None:
            try:
                verdict, usage = await chat_json(
                    self._client, self._model, messages,
                    ReviewVerdict, temperature=0, max_retries=1,
                    schema_hint="passed 布尔；violations 数组可空；scores 四个 0-1 分；note ≤40 字或空",
                )
                return {
                    "passed": verdict.passed,
                    "violations": [v.model_dump() for v in verdict.violations],
                    "scores": verdict.scores.model_dump(),
                    "note": verdict.note,
                    "usage": usage,
                    "engine": f"cheap:{self._model}",
                    "latency_ms": int((time.perf_counter() - _t0) * 1000),
                }
            except Exception as exc:  # noqa: BLE001 裁判失败不阻塞教学
                logger.warning("裁判 cheap 调用失败，回落 router：%s", exc)

        try:
            r = await self.router.chat(
                messages, temperature=0, json_mode=True)
            content = (r.get("content") or "").strip()
            verdict = ReviewVerdict.model_validate_json(content)
            return {
                "passed": verdict.passed,
                "violations": [v.model_dump() for v in verdict.violations],
                "scores": verdict.scores.model_dump(),
                "note": verdict.note,
                "usage": r.get("usage", {}),
                "engine": r.get("engine"),
            }
        except Exception as exc:  # noqa: BLE001 裁判失败不阻塞教学
            return {"passed": True, "violations": [], "scores": {},
                    "note": f"裁判调用失败：{exc}",
                    "usage": {}, "engine": ""}


__all__ = ["Reviewer", "ReviewVerdict", "REVIEW_INSTRUCTION"]
