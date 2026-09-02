"""教学服务编排：会话生命周期 + turn 分发（状态机入口）+ 学习档案落库

依赖注入：TutorService 由容器装配；持久化走 models.repo（会话/判定/薄弱点）。
"""
from __future__ import annotations

import uuid
from typing import AsyncIterator

from ... import storage
from ...models import repo
from ...models.db import _tznow
from ..providers import EV_FINISH, EV_START, EV_TEXT
from ..quiz import QuizService
from ..schemas import KnowledgePlan, KnowledgePoint, TutorState
from .actions import TutorActions
from .session import TutorSession


class TutorService:
    """会话注册表（内存缓存）+ 状态分发 + 档案落库。"""

    def __init__(self, container=None):
        if container is None:
            from ..judge import JudgeService
            from ..quiz import QuizService as QS
            from ..router import Router
            container = _MinContainer(Router(), JudgeService(), QS())
        self._deps = container
        self.actions = TutorActions(container.router, container.judge, container.quiz,
                                    container=container)
        self._quiz: QuizService = container.quiz
        self.sessions: dict[str, TutorSession] = {}

    # ---------- 启动 / 恢复 ----------

    async def start_chapter(self, doc_id: str, chapter_index: int,
                            session_id: str = "", user_id: str = "") -> TutorSession:
        manifest = storage.get_chapter_manifest(doc_id)
        if not manifest:
            raise ValueError(f"文档不存在或尚未解析：{doc_id}")
        chapter = next((c for c in manifest if c["index"] == chapter_index), None)
        if chapter is None:
            raise ValueError(f"章节不存在：第 {chapter_index} 章（共 {len(manifest)} 章）")
        if not session_id:
            session_id = "s_" + uuid.uuid4().hex[:10]
        chapter_title = chapter.get("title", f"第{chapter_index}章")
        toc_titles = "|".join(t["title"] for t in chapter.get("toc", [])[:12])
        preview = (storage.get_chapter(doc_id, chapter_index) or {}).get("markdown", "")[:600]

        # 章计划缓存（真实引擎一次生成 ~80s；只该每章一次，之后复用）
        cached = storage.load_learning_plan(doc_id, chapter_index)
        if cached:
            plan = KnowledgePlan(
                chapter_id=f"ch{chapter_index}", chapter_title=chapter_title,
                kps=[KnowledgePoint(id=k["id"], name=k["name"],
                                    summary=k.get("summary", ""),
                                    skill_id=k.get("skill_id", k["id"]))
                     for k in cached],
            )
        else:
            plan = await self._quiz.plan_knowledge(
                f"ch{chapter_index}", chapter_title, toc_titles, preview,
            )
            storage.save_learning_plan(
                doc_id, chapter_index,
                [{"id": k.id, "name": k.name, "summary": k.summary,
                  "skill_id": k.skill_id} for k in plan.kps],
            )
        ses = TutorSession(session_id=session_id, doc_id=doc_id,
                           chapter_index=chapter_index, chapter_title=chapter_title,
                           plan=plan)
        # 人物化开场白（D11）：回访接旧线 + 到期复习 + 连续天数（模板拼接，0 token）
        try:
            from ..persona import compose_greeting
            due = repo.due_reviews(doc_id, limit=1)
            due_first = None
            if due:
                due_first = due[0].get("name") or due[0].get("skill_id")
            ses.greeting = compose_greeting(
                title=chapter_title, kp_count=len(plan.kps),
                next_kp=plan.kps[0].name if plan.kps else None,
                due_first=due_first,
                streak_days=repo.study_streak(),
            )
        except Exception:  # noqa: BLE001 开场白失败不影响教学
            ses.greeting = ""
        repo.save_session(
            session_id, doc_id, chapter_index, chapter_title,
            ses.state.value, ses.kp_idx,
            [{"id": k.id, "name": k.name, "summary": k.summary, "skill_id": k.skill_id}
             for k in plan.kps],
            dict(ses.weak), hint_level=ses.hint_level,
            user_id=user_id or None,
        )
        self.sessions[session_id] = ses
        return ses

    def resume_session(self, session_id: str) -> TutorSession | None:
        """从档案恢复会话（服务重启后续学，含当前题目）。"""
        rec = repo.load_session(session_id)
        if not rec:
            return None
        plan = KnowledgePlan(
            chapter_id=f"ch{rec['chapter_index']}",
            chapter_title=rec["chapter_title"],
            kps=[KnowledgePoint(id=k["id"], name=k["name"], summary=k.get("summary", ""),
                                skill_id=k.get("skill_id", k["id"]))
                 for k in rec.get("plan", [])],
        )
        ses = TutorSession(
            session_id=session_id, doc_id=rec["doc_id"],
            chapter_index=rec["chapter_index"], chapter_title=rec["chapter_title"],
            plan=plan,
            state=TutorState(rec["state"]),
            kp_idx=rec["kp_idx"],
            weak=dict(rec.get("weak", {})),
            hint_level=int(rec.get("hint_level") or 0),
        )
        q = rec.get("current_question")
        if q:
            from ..schemas import QuestionSpec
            try:
                ses.current_question = QuestionSpec.model_validate(q)
            except Exception:
                ses.current_question = None
        # 章末考中间态恢复（2026-08-29 修复：重启不再丢考题/进度/得分）
        from ..schemas import QuestionSpec as _QS
        for eq in rec.get("exam_questions") or []:
            try:
                ses.exam_questions.append(_QS.model_validate(eq))
            except Exception:
                pass
        ses.exam_idx = int(rec.get("exam_idx") or 0)
        ses.exam_scores = dict(rec.get("exam_scores") or {})
        self.sessions[session_id] = ses
        return ses

    # ---------- 主轮 ----------

    async def handle_turn(self, session_id: str, user_text: str) -> AsyncIterator[dict]:
        ses = self.sessions.get(session_id)
        if ses is None and repo.load_session(session_id):
            ses = self.resume_session(session_id)   # 服务重启后按档案自动恢复
        if ses is None:
            yield {"type": "error", "error": "会话不存在"}
            return
        yield {"type": EV_START, "session_id": session_id,
               "chapter": ses.chapter_title, "state": ses.state.value,
               "ts": _tznow().timestamp()}

        gen = None
        if ses.state == TutorState.explain:
            gen = self.actions.explain(ses, user_text)
        elif ses.state in (TutorState.question, TutorState.await_answer):
            gen = self.actions.evaluate(ses, user_text)
        elif ses.state == TutorState.chapter_exam:
            gen = self.actions.exam_turn(ses, user_text)
        elif ses.state == TutorState.done:
            yield {"type": EV_TEXT, "delta": "本章学习完毕。可以返回选择下一章，或做章节复习。"}
            yield {"type": EV_FINISH, "finish_reason": "end"}
            return

        # skill_id -> 知识点中文名（薄弱点档案展示用；查不到时回退 skill_id）
        skill_names = {k.skill_id: k.name for k in (ses.plan.kps if ses.plan else [])}

        # 流式转发 + 判定/薄弱点落库
        async for ev in gen or ():
            if ev["type"] == "judge":
                j = ev["judgement"]
                repo.add_judgement(ses.session_id, {**j, "question_id":
                                                    (ses.current_question.question_id
                                                     if ses.current_question else "")},
                                   user_id=ses.user_id or None)
                for wp in j.get("weak_points", []):
                    sid = wp.get("skill_id", "")
                    if not sid:
                        continue
                    repo.upsert_weakness(
                        ses.doc_id, sid, skill_names.get(sid, sid),
                        wp.get("mastery", "low"),
                        chapter_index=ses.chapter_index,
                        chapter_title=ses.chapter_title,
                        user_id=ses.user_id or None,
                    )
            yield ev

        # 每轮结束：增量落 turn + 会话状态快照
        self._flush_turns(ses)
        repo.save_session(
            ses.session_id, ses.doc_id, ses.chapter_index, ses.chapter_title,
            ses.state.value, ses.kp_idx,
            [{"id": k.id, "name": k.name, "summary": k.summary, "skill_id": k.skill_id}
             for k in (ses.plan.kps if ses.plan else [])],
            dict(ses.weak),
            current_question=ses.current_question.model_dump() if ses.current_question else None,
            hint_level=ses.hint_level,
            exam_questions=[q.model_dump() for q in ses.exam_questions],
            exam_idx=ses.exam_idx,
            exam_scores=dict(ses.exam_scores),
            user_id=ses.user_id or None,
        )

    def _flush_turns(self, ses: TutorSession) -> None:
        """增量落库 turn_history（含 token 用量，AI 成本核算用）。"""
        while ses._saved_turns < len(ses.turn_history):
            t = ses.turn_history[ses._saved_turns]
            repo.add_turn(ses.session_id, t["role"], t.get("kind", ""), t["content"],
                          usage=t.get("usage"), user_id=ses.user_id or None)
            ses._saved_turns += 1


class _MinContainer:
    """测试兜底容器（避免循环导入）。"""
    def __init__(self, router, judge, quiz):
        self.router = router
        self.judge = judge
        self.quiz = quiz