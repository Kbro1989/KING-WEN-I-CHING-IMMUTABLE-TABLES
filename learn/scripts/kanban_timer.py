"""Self-tuning kanban timer.

Monitors actual run duration and updates the cron cadence to match:
  observed duration + polite buffer -> new schedule.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from hermes_tools import terminal  # type: ignore
except Exception:  # pragma: no cover
    terminal = None


JOB_ID = "39780391e3ad"
STATE_PATH = ROOT / "learn" / "exports" / "kanban_timer_state.json"
MIN_SECONDS = 60
MAX_SECONDS = 3600
DEFAULT_SECONDS = 240


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_duration_seconds": None, "last_schedule": "every 4m", "history": []}


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")


def _cron_to_seconds(schedule: str) -> Optional[int]:
    if not schedule:
        return None
    m = re.fullmatch(r"every\s+(\d+)\s*m", schedule.strip(), re.IGNORECASE)
    if m:
        return max(MIN_SECONDS, int(m.group(1)) * 60)
    m = re.fullmatch(r"every\s+(\d+)\s*h", schedule.strip(), re.IGNORECASE)
    if m:
        return max(MIN_SECONDS, int(m.group(1)) * 3600)
    return None


def _seconds_to_cron(seconds: int) -> str:
    seconds = max(MIN_SECONDS, min(MAX_SECONDS, seconds))
    if seconds % 3600 == 0:
        return f"every {seconds // 3600}h"
    minutes = max(1, round(seconds / 60))
    return f"every {minutes}m"


def _get_last_run_duration_seconds() -> Optional[float]:
    # Best-effort local inference from cached web content metadata when available.
    cache_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / "hermes" / "cache" / "web"
    if not cache_dir.exists():
        return None
    try:
        mtimes = [p.stat().st_mtime for p in cache_dir.glob("*.md")]
        if not mtimes:
            return None
        newest = max(mtimes)
        age = time.time() - newest
        return max(0.0, age)
    except Exception:
        return None


def _update_cron(schedule: str) -> None:
    if terminal is None:
        return
    try:
        terminal(
            "cronjob",
            json.dumps({"action": "update", "job_id": JOB_ID, "schedule": schedule}),
        )
    except Exception:
        pass


def tune_once() -> dict:
    state = _load_state()
    observed = _get_last_run_duration_seconds()
    buffer_seconds = 15
    if observed is None:
        observed = state.get("last_duration_seconds") or (_cron_to_seconds(state.get("last_schedule")) or DEFAULT_SECONDS)
    target_seconds = max(MIN_SECONDS, observed + buffer_seconds)
    new_schedule = _seconds_to_cron(target_seconds)
    old_schedule = state.get("last_schedule") or "every 4m"
    if new_schedule != old_schedule:
        _update_cron(new_schedule)
    history = state.get("history") or []
    history.append(
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "observed_seconds": observed,
            "target_seconds": target_seconds,
            "old_schedule": old_schedule,
            "new_schedule": new_schedule,
        }
    )
    if len(history) > 50:
        history = history[-50:]
    state.update(
        {
            "last_duration_seconds": observed,
            "last_schedule": new_schedule,
            "history": history,
        }
    )
    _save_state(state)
    return {
        "observed_seconds": observed,
        "target_seconds": target_seconds,
        "schedule": new_schedule,
        "updated": new_schedule != old_schedule,
    }


def main() -> int:
    result = tune_once()
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
