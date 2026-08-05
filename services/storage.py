"""Local JSON read/write under data/ - committed to the repo by the workflow's
commit-data action, and read back by the dashboard via the GitHub Contents API."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DHAKA = ZoneInfo("Asia/Dhaka")

LOG_HISTORY_LIMIT = 200


def today_str() -> str:
    return datetime.now(DHAKA).strftime("%Y-%m-%d")


def read_json(relative_path: str, default: Any = None) -> Any:
    path = DATA_DIR / relative_path
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(relative_path: str, data: Any) -> None:
    path = DATA_DIR / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_config() -> dict[str, Any]:
    return read_json("config.json", default={"sources": []})


def append_history(digest: dict[str, Any]) -> None:
    """Keep a lightweight per-day index (history.json) separate from the full
    digest payloads in daily/ - cheap to read for dashboard charts, and
    idempotent so a resend/rerun on the same day doesn't duplicate an entry."""
    history = read_json("history.json", default=[])
    entry = {
        "date": digest["date"],
        "top_ai_count": len(digest.get("top_ai_news", [])),
        "top_tech_count": len(digest.get("top_tech_news", [])),
    }
    history = [h for h in history if h["date"] != entry["date"]]
    history.append(entry)
    history.sort(key=lambda h: h["date"])
    write_json("history.json", history)


def append_log(entry: dict[str, Any]) -> None:
    logs = read_json("logs.json", default=[])
    logs.append(entry)
    logs = logs[-LOG_HISTORY_LIMIT:]
    write_json("logs.json", logs)
    _update_analytics(logs)


def _update_analytics(logs: list[dict[str, Any]]) -> None:
    ok_runs = [entry for entry in logs if entry.get("status") == "ok"]
    total = len(logs)
    write_json(
        "analytics.json",
        {
            "total_runs_logged": total,
            "successful_runs": len(ok_runs),
            "success_rate": round(len(ok_runs) / total, 3) if total else None,
            "last_run": logs[-1] if logs else None,
            "updated_at": datetime.now(UTC).isoformat(),
        },
    )
