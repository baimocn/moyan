"""墨衍 · 复习会话服务（engram 失败回收最小闭环，自评制，不烧 LLM）

流程（对齐设计文档第八节 engram 经验）：
- start：取"到期 ∩ 薄弱"队列快照（FSRS 优先级排序），附每个概念的教材微点片段；
- answer：学生自评 again/hard/good/easy → FSRS 重排落库；
  - rating=again → **失败回收**：立即展示该概念教材片段（重讲），该项留在队列
    要求本会话内再答一次（防止'忘了就当没看见'）；同一概念本会话连忘 2 次仍放行
    （FSRS 已把它推回重学步，10 分钟后自然到期）。
  - rating≠again → 出队，计入本次完成。
- 会话内存态（单用户阶段与 TutorService 一致）；服务重启后重新 start 即可。

自评口径（保持"判定最稳"）：复习不重考（不调判定模型），全凭学生诚实自评；
后续若做"复习即考"，可复用 judge/quiz（cheap 模型）替换自评入口。
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from ... import storage
from ...models import repo


def _snippet_for(doc_id: str, chapter_index: int, keyword: str) -> str:
    """从章节 md 里取包含关键词的片段（微点注入，无嵌入的简化检索）。"""
    try:
        md = (storage.get_chapter(doc_id, chapter_index) or {}).get("markdown", "")
    except Exception:
        md = ""
    if not md or not keyword:
        return ""
    pos = md.find(keyword)
    if pos < 0 and len(keyword) >= 4:
        pos = md.find(keyword[:4])
    if pos >= 0:
        start = max(0, pos - 80)
        return md[start:start + 300].replace("\n", " ")
    return ""


@dataclass
class ReviewItem:
    skill_id: str
    name: str
    chapter_index: int = -1
    chapter_title: str = ""
    retention: float = 0.0
    priority: float = 0.0
    reason: str = ""
    snippet: str = ""
    seen: bool = False            # 是否在本会话被要求重答（again 回收后）
    recovery_count: int = 0       # 本会话内连续 again 次数

    def to_event(self, with_snippet: bool = False) -> dict:
        d = {
            "skill_id": self.skill_id, "name": self.name,
            "chapter_index": self.chapter_index, "chapter_title": self.chapter_title,
            "retention": self.retention, "priority": self.priority,
            "reason": self.reason,
        }
        if with_snippet:
            d["snippet"] = self.snippet
        return d


@dataclass
class ReviewSession:
    session_id: str
    doc_id: str
    queue: list[ReviewItem] = field(default_factory=list)
    done: list[str] = field(default_factory=list)      # 已完成 skill_id
    answered: dict[str, str] = field(default_factory=dict)  # skill_id -> 最后评分
    tally: dict[str, int] = field(default_factory=dict)     # 累计评分次数（again/hard/good/easy）
    created_at: float = field(default_factory=time.time)

    @property
    def finished(self) -> bool:
        return not self.queue


class ReviewService:
    """复习会话注册表（内存，单用户阶段）。"""

    MAX_SESSIONS = 50

    def __init__(self):
        self.sessions: dict[str, ReviewSession] = {}

    def _evict_if_full(self) -> None:
        if len(self.sessions) >= self.MAX_SESSIONS:
            oldest = min(self.sessions, key=lambda k: self.sessions[k].created_at)
            self.sessions.pop(oldest, None)

    def start(self, doc_id: str, limit: int = 20) -> ReviewSession:
        self._evict_if_full()
        due = repo.due_reviews(doc_id, limit=limit)
        queue = [
            ReviewItem(
                skill_id=d["skill_id"], name=d["name"],
                chapter_index=d.get("chapter_index", -1),
                chapter_title=d.get("chapter_title", ""),
                retention=d.get("retention", 0.0), priority=d.get("priority", 0.0),
                reason=d.get("reason", ""),
                snippet=_snippet_for(doc_id, d.get("chapter_index", -1), d["name"]),
            )
            for d in due
        ]
        ses = ReviewSession(session_id="rv_" + uuid.uuid4().hex[:10], doc_id=doc_id,
                            queue=queue)
        self.sessions[ses.session_id] = ses
        return ses

    def get(self, session_id: str) -> ReviewSession | None:
        return self.sessions.get(session_id)

    def answer(self, session_id: str, skill_id: str, rating: str) -> dict:
        """评分一项；again → 失败回收（展示片段、留队再答）；非 again → 出队。"""
        ses = self.get(session_id)
        if ses is None:
            raise KeyError("复习会话不存在（服务重启后需重新 start）")
        item = next((i for i in ses.queue if i.skill_id == skill_id), None)
        if item is None:
            raise KeyError(f"「{skill_id}」不在当前复习队列")
        rec = repo.record_review(ses.doc_id, skill_id, rating)
        if rec is None:
            raise KeyError(f"薄弱点不存在：{skill_id}")
        ses.answered[skill_id] = rating
        ses.tally[rating] = ses.tally.get(rating, 0) + 1

        recovery = None
        if rating == "again":
            item.recovery_count += 1
            recovery = {
                "retry_required": item.recovery_count < 2,   # 连忘 2 次仍放行（防死循环）
                "snippet": item.snippet,
                "message": ("记住这个词是薄弱点：先读一遍教材片段，再试一次。"
                            if item.snippet else "重新回想这个概念，再答一次。"),
            }
            if not recovery["retry_required"]:
                ses.queue.remove(item)
                ses.done.append(skill_id)
            else:
                item.seen = True
        else:
            ses.queue.remove(item)
            ses.done.append(skill_id)

        nxt = ses.queue[0] if ses.queue else None
        return {
            "ok": True,
            "recorded": rec,
            "recovery": recovery,
            "progress": {"done": len(ses.done), "remaining": len(ses.queue)},
            "next": nxt.to_event(with_snippet=True) if nxt else None,
            "finished": ses.finished,
        }

    def summary(self, session_id: str) -> dict:
        ses = self.get(session_id)
        if ses is None:
            raise KeyError("复习会话不存在")
        ratings = ses.tally
        return {
            "session_id": ses.session_id,
            "doc_id": ses.doc_id,
            "answered": sum(ratings.values()),
            "finished": ses.finished,
            "by_rating": {r: ratings.get(r, 0) for r in repo.REVIEW_RATINGS},
        }