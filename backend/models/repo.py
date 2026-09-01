"""学习档案仓储：会话/判定/薄弱点的持久化与查询"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fsrs import Card, Rating, Scheduler, State

from .db import SessionLocal
from .study import (Judgement, StrategyLog, TeachingSession, Turn, Weakness)

ZERO = datetime.fromtimestamp(0, tz=timezone.utc)

# ---- FSRS（官方 py-fsrs；D4 修订：FSRS-lite -> FSRS 现行模型） ----
FSRS_SCHEDULER = Scheduler()   # 默认参数 + 90% 目标保持率 + 学习/重学短步长
RATING_MAP = {"again": Rating.Again, "hard": Rating.Hard,
              "good": Rating.Good, "easy": Rating.Easy}
_RATING_MASTERY = {"again": "low", "hard": "mid", "good": "mid", "easy": "high"}
_MASTERY_WEIGHT = {"low": 2.0, "mid": 1.4, "high": 1.0}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _utc(dt: datetime | None) -> datetime:
    """SQLite 读回的 DateTime 是 naive（UTC 无后缀），统一补成 tz-aware 再比较。"""
    if dt is None:
        return _now()
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _card_from_row(r) -> Card:
    """DB 行 -> fsrs Card（card_id 无关紧要，仅用于调度；缺失字段按新卡片兜底）。"""
    state = State(r.fsrs_state) if r.fsrs_state in (1, 2, 3) else State.Learning
    return Card(
        card_id=0,
        state=state,
        step=r.fsrs_step if r.fsrs_step is not None else (0 if state != State.Review else None),
        stability=float(r.stability) if r.stability is not None else None,
        difficulty=float(r.difficulty) if r.difficulty is not None else None,
        due=_utc(r.due_at) if r.due_at else _now(),
        last_review=_utc(r.last_review) if r.last_review else None,
    )


def _apply_card(r, card: Card, now: datetime) -> None:
    """fsrs Card -> DB 行（due/last_review 必须 aware）。"""
    r.due_at = card.due
    r.last_review = card.last_review
    r.fsrs_state = card.state.value
    r.fsrs_step = card.step
    r.stability = card.stability
    r.difficulty = card.difficulty
    if card.last_review is not None:
        days = max(0, (card.due - card.last_review).days)
    else:
        days = 0
    r.interval_days = days


# ---------- 会话 ----------

def save_session(session_id: str, doc_id: str, chapter_index: int, chapter_title: str,
                 state: str, kp_idx: int, plan: list, weak: dict,
                 current_question: dict | None = None, hint_level: int = 0,
                 exam_questions: list | None = None, exam_idx: int = 0,
                 exam_scores: dict | None = None) -> None:
    with SessionLocal() as db:
        row = db.get(TeachingSession, session_id)
        if row is None:
            db.add(TeachingSession(id=session_id, doc_id=doc_id, chapter_index=chapter_index,
                                   chapter_title=chapter_title, state=state, kp_idx=kp_idx,
                                   plan=plan, weak=weak, current_question=current_question or {},
                                   hint_level=hint_level,
                                   exam_questions=exam_questions or [],
                                   exam_idx=exam_idx, exam_scores=exam_scores or {}))
        else:
            row.state = state
            row.kp_idx = kp_idx
            row.weak = weak
            row.hint_level = hint_level
            row.current_question = current_question or {}
            row.exam_questions = exam_questions or []
            row.exam_idx = exam_idx
            row.exam_scores = exam_scores or {}
        db.commit()


def load_session(session_id: str) -> dict | None:
    with SessionLocal() as db:
        row = db.get(TeachingSession, session_id)
        if row is None:
            return None
        return {
            "id": row.id, "doc_id": row.doc_id, "chapter_index": row.chapter_index,
            "chapter_title": row.chapter_title, "state": row.state, "kp_idx": row.kp_idx,
            "plan": row.plan or [], "weak": row.weak or {},
            "current_question": row.current_question or {},
            "hint_level": row.hint_level or 0,
            "exam_questions": row.exam_questions or [],
            "exam_idx": row.exam_idx or 0,
            "exam_scores": row.exam_scores or {},
        }


def streak_from_dates(dates: set, today) -> int:
    """连续学习天数：从 today（或其前一天）往回数连续日期数。纯函数。"""
    from datetime import timedelta
    if not dates:
        return 0
    day = today
    if day not in dates:
        if day - timedelta(days=1) not in dates:
            return 0
        day = day - timedelta(days=1)
    n = 0
    while day in dates:
        n += 1
        day -= timedelta(days=1)
    return n


def study_streak() -> int:
    """连续学习天数（按 teaching_sessions 创建日期，本地时区）——人物开场白用。"""
    from datetime import datetime, timezone
    with SessionLocal() as db:
        rows = db.query(TeachingSession.created_at).all()
    days = set()
    for (dt,) in rows:
        if dt is None:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        days.add(dt.astimezone().date())
    today = datetime.now().astimezone().date()
    return streak_from_dates(days, today)


def list_sessions(doc_id: str, limit: int = 20) -> list[dict]:
    with SessionLocal() as db:
        rows = (db.query(TeachingSession)
                .filter(TeachingSession.doc_id == doc_id)
                .order_by(TeachingSession.updated_at.desc()).limit(limit).all())
    return [
        {"id": r.id, "chapter_title": r.chapter_title, "chapter_index": r.chapter_index,
         "state": r.state, "kp_idx": r.kp_idx, "weak": r.weak or {},
         "updated_at": r.updated_at.isoformat() if r.updated_at else None}
        for r in rows
    ]


def add_turn(session_id: str, role: str, kind: str, content: str, usage: dict | None = None) -> None:
    with SessionLocal() as db:
        db.add(Turn(id=f"t_{uuid.uuid4().hex[:10]}", session_id=session_id,
                    role=role, kind=kind, content=content[:5000],
                    usage=usage or {}))
        db.commit()


def add_judgement(session_id: str, j: dict) -> None:
    with SessionLocal() as db:
        db.add(Judgement(
            id=f"j_{uuid.uuid4().hex[:10]}",
            session_id=session_id,
            question_id=j.get("question_id", ""),
            correctness=j.get("correctness_level") or j.get("correctness", ""),
            score=j.get("score", 0.0),
            decision=j.get("decision", ""),
            confidence=j.get("confidence", 0.0),
            payload=j,
        ))
        db.commit()


def upsert_weakness(doc_id: str, skill_id: str, name: str, mastery: str,
                    chapter_index: int = -1, chapter_title: str = "") -> None:
    """薄弱点入账：新卡片立即到期（尽快首学/复习）；已有卡片不打断其 FSRS 排程。

    chapter_index/chapter_title 供"概念→章节"聚合（复习任务 = due ∩ 章节）。
    """
    with SessionLocal() as db:
        row = db.query(Weakness).filter(
            Weakness.doc_id == doc_id, Weakness.skill_id == skill_id).first()
        now = _now()
        if row is None:
            db.add(Weakness(
                id=f"w_{uuid.uuid4().hex[:10]}", doc_id=doc_id, skill_id=skill_id,
                name=name, mastery=mastery, times_low=1,
                chapter_index=chapter_index, chapter_title=chapter_title,
                due_at=now, fsrs_state=State.Learning.value, fsrs_step=0,
                last_seen_at=now))
        else:
            if name and row.name != name:
                row.name = name
            if mastery == "low":
                row.times_low = (row.times_low or 0) + 1
            row.mastery = mastery
            if chapter_index >= 0 and row.chapter_index != chapter_index:
                row.chapter_index = chapter_index
                row.chapter_title = chapter_title or row.chapter_title
            row.last_seen_at = now
            row.updated_at = now
        db.commit()


# ---------- 复习调度（官方 py-fsrs，D4） ----------

REVIEW_RATINGS = tuple(RATING_MAP)


def _retention(scheduler: Scheduler, r, now: datetime) -> float:
    try:
        r_val = scheduler.get_card_retrievability(_card_from_row(r), now)
    except Exception:  # noqa: BLE001 卡片字段异常时视为极高遗忘风险
        r_val = 0.0
    return max(0.0, min(1.0, r_val or 0.0))


def review_priority(r, retention: float) -> float:
    """'预计挽回记忆/分钟'的工程近似：遗忘风险 × 薄弱偏向 × 遗忘次数加成。

    精确值需 FSRS 模拟器全量重放，这里用可解释的代理指标做排序（记录于文档）：
    - forgetting_risk = 1 - R(now)：当前越可能忘，越该先复习；
    - mastery 越弱权重越高（low 2.0 / mid 1.4 / high 1.0）；
    - 曾遗忘（lapses）再加权，防止'屡错屡忘'被长间隔掩盖。
    """
    forgetting_risk = 1.0 - retention
    return forgetting_risk * _MASTERY_WEIGHT.get(r.mastery, 1.0) * (1 + (r.lapses or 0))


def due_reviews(doc_id: str, limit: int = 30, scheduler: Scheduler | None = None) -> list[dict]:
    """到期待复习的薄弱点，按'预计挽回记忆/分钟'（代理指标）降序。

    概念级队列；章节级聚合见 chapter_overview()。
    """
    now = _now()
    sched = scheduler or FSRS_SCHEDULER
    with SessionLocal() as db:
        rows = db.query(Weakness).filter(Weakness.doc_id == doc_id).all()
    due = [r for r in rows if _utc(r.due_at) <= now]
    items = []
    for r in due:
        retention = _retention(sched, r, now)
        items.append({
            "skill_id": r.skill_id,
            "name": r.name or r.skill_id,
            "mastery": r.mastery,
            "chapter_index": r.chapter_index,
            "chapter_title": r.chapter_title or "",
            "state": r.fsrs_state,
            "times_low": r.times_low,
            "reps": r.reps,
            "lapses": r.lapses,
            "retention": round(retention, 3),
            "priority": round(review_priority(r, retention), 4),
            "reason": _priority_reason(r, retention),
            "due_at": _utc(r.due_at).isoformat(),
        })
    items.sort(key=lambda it: it["priority"], reverse=True)
    return items[:limit]


def _priority_reason(r, retention: float) -> str:
    parts = [f"遗忘风险 {1 - retention:.0%}"]
    if r.mastery == "low":
        parts.append("掌控度弱")
    if (r.lapses or 0) > 0:
        parts.append(f"遗忘过 {r.lapses} 次")
    return "，".join(parts)


def record_review(doc_id: str, skill_id: str, rating: str,
                  scheduler: Scheduler | None = None,
                  review_datetime: datetime | None = None) -> dict | None:
    """记录一次复习评分，按 FSRS 重排卡片（state/stability/difficulty/due）。"""
    if rating not in REVIEW_RATINGS:
        raise ValueError(f"rating 必须是 {REVIEW_RATINGS}")
    sched = scheduler or FSRS_SCHEDULER
    now = _utc(review_datetime) if review_datetime else _now()
    with SessionLocal() as db:
        row = db.query(Weakness).filter(
            Weakness.doc_id == doc_id, Weakness.skill_id == skill_id).first()
        if row is None:
            return None
        card = _card_from_row(row)
        card, _log = sched.review_card(card, RATING_MAP[rating], review_datetime=now)
        _apply_card(row, card, now)
        row.mastery = _RATING_MASTERY[rating]
        if rating == "again":
            row.lapses = (row.lapses or 0) + 1
        row.reps = (row.reps or 0) + 1
        row.last_seen_at = now
        row.updated_at = now
        db.commit()
        return {
            "skill_id": row.skill_id,
            "name": row.name or row.skill_id,
            "mastery": row.mastery,
            "state": row.fsrs_state,
            "reps": row.reps,
            "interval_days": row.interval_days,
            "lapses": row.lapses,
            "stability": round(row.stability, 3) if row.stability is not None else None,
            "difficulty": round(row.difficulty, 3) if row.difficulty is not None else None,
            "due_at": _utc(row.due_at).isoformat() if row.due_at else None,
        }


def chapter_overview(doc_id: str, scheduler: Scheduler | None = None) -> dict:
    """概念级 -> 章节级聚合：每章到期/掌握度画像，按到期数优先、最弱优先排序。"""
    now = _now()
    sched = scheduler or FSRS_SCHEDULER
    with SessionLocal() as db:
        rows = db.query(Weakness).filter(Weakness.doc_id == doc_id).all()
    groups: dict[tuple, dict] = {}
    for r in rows:
        key = (r.chapter_index if r.chapter_index is not None else -1,
               r.chapter_title or "")
        g = groups.setdefault(key, {
            "chapter_index": key[0], "chapter_title": key[1] or "未标明章节",
            "total": 0, "due": 0, "by_mastery": {"low": 0, "mid": 0, "high": 0},
            "concepts": [],
        })
        g["total"] += 1
        g["due"] += 1 if _utc(r.due_at) <= now else 0
        g["by_mastery"][r.mastery if r.mastery in g["by_mastery"] else "low"] += 1
        g["concepts"].append({"skill_id": r.skill_id, "name": r.name or r.skill_id,
                              "mastery": r.mastery,
                              "retention": round(_retention(sched, r, now), 3)})
    chapters = list(groups.values())
    for c in chapters:
        c["by_mastery"] = {k: c["by_mastery"].get(k, 0) for k in ("low", "mid", "high")}
    chapters.sort(key=lambda c: (-c["due"], -c["by_mastery"]["low"]))
    return {
        "doc_id": doc_id,
        "chapters": chapters,
        "summary": {
            "total_weakness": len(rows),
            "due_total": sum(c["due"] for c in chapters),
            "chapters_with_due": sum(1 for c in chapters if c["due"] > 0),
        },
    }


# ---------- 查询 ----------

def list_weaknesses(doc_id: str) -> list[dict]:
    with SessionLocal() as db:
        rows = (db.query(Weakness)
                .filter(Weakness.doc_id == doc_id)
                .order_by(Weakness.mastery, Weakness.times_low.desc()).all())
    return [
        {"skill_id": r.skill_id, "name": r.name, "mastery": r.mastery,
         "times_low": r.times_low, "reps": r.reps, "interval_days": r.interval_days,
         "lapses": r.lapses,
         "chapter_index": r.chapter_index, "chapter_title": r.chapter_title or "",
         "state": r.fsrs_state,
         "stability": round(r.stability, 3) if r.stability is not None else None,
         "difficulty": round(r.difficulty, 3) if r.difficulty is not None else None,
         "due_at": r.due_at.isoformat() if r.due_at else None,
         "updated_at": r.updated_at.isoformat() if r.updated_at else None}
        for r in rows
    ]


def study_stats(doc_id: str) -> dict:
    """掌握度统计：弱/中/强 知识点数 + 累计判定数 + 复习队列 + token 用量。"""
    with SessionLocal() as db:
        rows = db.query(Weakness).filter(Weakness.doc_id == doc_id).all()
        judgements = db.query(Judgement).join(TeachingSession).filter(
            TeachingSession.doc_id == doc_id).count()
        turns = db.query(Turn).join(TeachingSession).filter(
            TeachingSession.doc_id == doc_id).all()
    by = {"low": 0, "mid": 0, "high": 0}
    for r in rows:
        by[r.mastery] = by.get(r.mastery, 0) + 1
    now = _now()
    due = sum(1 for r in rows if _utc(r.due_at) <= now)
    prompt = sum((t.usage or {}).get("prompt_tokens", 0) for t in turns)
    completion = sum((t.usage or {}).get("completion_tokens", 0) for t in turns)
    estimated = sum((t.usage or {}).get("estimated_tokens", 0) for t in turns)
    return {
        "weak_points": by, "total_judgements": judgements, "skills": len(rows),
        "review_due": due, "turns": len(turns),
        "tokens": {"prompt": prompt, "completion": completion,
                   "estimated": estimated, "total": prompt + completion + estimated},
    }


# ---------- 教学策略反馈（借鉴 synapse Groove/Tracer：哪个讲法对哪个知识点有效） ----------

def save_strategy_feedback(doc_id: str, skill_id: str, strategy: str,
                           effect: float, review_passed: bool,
                           session_id: str = "") -> None:
    """每轮判定后落一条策略反馈（短程效果=判定分数；裁判是否通过=质量信号）。"""
    with SessionLocal() as db:
        db.add(StrategyLog(
            id=f"sl_{uuid.uuid4().hex[:10]}", doc_id=doc_id,
            skill_id=skill_id or "", strategy=strategy or "",
            effect=float(effect or 0.0), review_passed=bool(review_passed),
            session_id=session_id,
        ))
        db.commit()


def strategy_stats(doc_id: str, skill_id: str = "") -> list[dict]:
    """聚合：skill × strategy → 样本数/平均效果/裁判通过率，据此选"下次讲法"。"""
    with SessionLocal() as db:
        q = db.query(StrategyLog).filter(StrategyLog.doc_id == doc_id)
        if skill_id:
            q = q.filter(StrategyLog.skill_id == skill_id)
        rows = q.all()
    groups: dict[tuple, list] = {}
    for r in rows:
        key = (r.skill_id, r.strategy)
        groups.setdefault(key, []).append(r)
    out = []
    for (sid, strategy), logs in groups.items():
        n = len(logs)
        avg = sum(l.effect for l in logs) / n
        pass_rate = sum(1 for l in logs if l.review_passed) / n
        out.append({
            "skill_id": sid, "strategy": strategy,
            "samples": n, "avg_effect": round(avg, 3),
            "pass_rate": round(pass_rate, 3),
        })
    # 每个 skill 的"效果最好的策略"排前（数据→讲解方式路由）
    out.sort(key=lambda x: (-x["avg_effect"], -x["pass_rate"], -x["samples"]))
    return out


def best_strategy(doc_id: str, skill_id: str, min_samples: int = 3,
                  prefer: str = "alternative_explanation") -> str | None:
    """数据驱动的讲解方式选择：若该 skill 历史统计更偏好某策略则返回它。

    prefer：在效果相近时优先的默认策略名；样本不足/无差异返回 None（走原逻辑）。
    """
    stats = strategy_stats(doc_id, skill_id)
    cands = [s for s in stats if s["samples"] >= min_samples
             and s["strategy"] in ("reteach", "alternative_explanation")]
    if not cands:
        return None
    best = cands[0]
    alt = next((s for s in cands if s["strategy"] == prefer), None)
    # 若 best 与 prefer 效果差距 < 5%，用 prefer（换讲法通常更省轮次）
    if alt and best["strategy"] != prefer and \
            (best["avg_effect"] - alt["avg_effect"]) < 0.05:
        return prefer
    return best["strategy"] if best["strategy"] != "reteach" else None


def traces(doc_id: str, skill_id: str, limit: int = 30) -> dict:
    """Tracer：某知识点的完整学习轨迹（讲解/判定/掌握度/策略反馈时间线）。"""
    with SessionLocal() as db:
        sess_ids = [r.id for r in db.query(TeachingSession)
                    .filter(TeachingSession.doc_id == doc_id).all()]
        jrows = (db.query(Judgement)
                 .filter(Judgement.session_id.in_(sess_ids))
                 .order_by(Judgement.created_at.asc()).all() if sess_ids else [])
        wrows = (db.query(Weakness)
                 .filter(Weakness.doc_id == doc_id, Weakness.skill_id == skill_id)
                 .order_by(Weakness.updated_at.asc()).all())
        slogs = (db.query(StrategyLog)
                 .filter(StrategyLog.doc_id == doc_id,
                         StrategyLog.skill_id == skill_id)
                 .order_by(StrategyLog.created_at.asc()).all())
    judgements = [
        {"at": r.created_at.isoformat() if r.created_at else None,
         "correctness": r.correctness, "score": r.score, "decision": r.decision,
         "review_passed": (r.payload or {}).get("review", {}).get("passed")}
        for r in jrows
    ]
    mastery = [{"at": _utc(r.updated_at).isoformat(), "mastery": r.mastery,
                "reps": r.reps, "stability": round(r.stability, 2) if r.stability else None}
               for r in wrows]
    strategies = [{"at": _utc(r.created_at).isoformat(), "strategy": r.strategy,
                   "effect": r.effect, "review_passed": r.review_passed}
                  for r in slogs]
    return {
        "doc_id": doc_id, "skill_id": skill_id,
        "judgements": judgements[-limit:],
        "mastery": mastery[-limit:],
        "strategies": strategies[-limit:],
    }