"""OBS-01 墨衍冒烟探针（服务器 systemd timer 每 5 分钟触发一次本脚本）。

- health 每轮必查（进程 + DB 活性，0 token）
- AI 全链 turn（start → turn SSE 断言 text-delta）按 60 分钟限频，消耗计入 ai_usage
  （SEC-04 日预算熔断兜底，探针失控也会被掐）
- 结果追加 data/smoke_probe.jsonl（留 2000 行），GET /api/admin/smoke 可查

退出码：健康 0 / 异常 1（journald 可告警）。
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "http://127.0.0.1:5001"
DATA = Path("/opt/moyan/data")
PROBE_DID = "smokeprobe0001"      # 固定探针身份（web_smokeprobe0001）
AI_INTERVAL = 3600                # AI 全链探针限频（秒）
KEEP = 2000


def _req(path, method="GET", body=None, headers=None, timeout=30):
    req = urllib.request.Request(
        BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def main() -> int:
    now = time.time()
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "health": None,
           "ai_turn": None, "ai_ok": None, "ms": None}

    try:
        code, _ = _req("/api/health", timeout=10)
        rec["health"] = code
    except Exception as exc:  # noqa: BLE001
        rec["health"] = f"error:{str(exc)[:100]}"

    last = DATA / ".smoke_last_ai"
    try:
        due = now - float(last.read_text().strip()) >= AI_INTERVAL
    except Exception:  # noqa: BLE001
        due = True

    if rec["health"] == 200 and due:
        t0 = time.time()
        try:
            _, body = _req("/api/documents", headers={"X-Device-Id": PROBE_DID})
            docs = json.loads(body).get("documents", [])
            doc_id = next((d["doc_id"] for d in docs if d.get("status") == "done"), None)
            if not doc_id:
                raise RuntimeError("书库无 done 文档可探")
            _, body = _req("/api/tutor/start", method="POST",
                           body={"doc_id": doc_id, "chapter_index": 0},
                           headers={"X-Device-Id": PROBE_DID})
            sid = json.loads(body).get("session_id")
            if not sid:
                raise RuntimeError("start 无 session_id")
            code, body = _req("/api/tutor/turn", method="POST",
                              body={"session_id": sid, "user_text": "探针：请简单回应一句"},
                              headers={"X-Device-Id": PROBE_DID}, timeout=300)
            rec["ai_turn"] = code
            rec["ai_ok"] = (code == 200 and "text-delta" in body)
            rec["ms"] = int((time.time() - t0) * 1000)
            last.write_text(str(now))
        except Exception as exc:  # noqa: BLE001
            rec["ai_turn"] = "error"
            rec["ai_ok"] = False
            rec["detail"] = str(exc)[:200]

    f = DATA / "smoke_probe.jsonl"
    lines = f.read_text(encoding="utf-8").splitlines()[-(KEEP - 1):] if f.exists() else []
    lines.append(json.dumps(rec, ensure_ascii=False))
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok = rec["health"] == 200 and rec.get("ai_ok") is not False
    print(("SMOKE_OK" if ok else "SMOKE_FAIL"),
          json.dumps(rec, ensure_ascii=False)[:300])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
