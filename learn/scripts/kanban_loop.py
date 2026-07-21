"""Self-updating kanban loop.

Reads kanban_board.json, advances cards when outputs are present,
records operation sequence and math returns, and persists state.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.core.pog3_hexagram_runtime_substrate import POG3Runtime, IntentVector

BOARD_PATH = ROOT / "learn" / "exports" / "kanban_board.json"
STATE_PATH = ROOT / "learn" / "exports" / "kanban_loop_state.json"
SEQUENCE_PATH = ROOT / "learn" / "exports" / "learned_sequence.json"
MATH_RETURNS_PATH = ROOT / "learn" / "exports" / "learned_math_returns.jsonl"
CARD_LIMIT = 50


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


def _outputs_present(outputs: List[str]) -> bool:
    return all((ROOT / out).exists() for out in outputs)


def _advance_column(column: str) -> Optional[str]:
    order = ["ready", "parse", "classify", "learn_math", "tune_timer", "done"]
    try:
        idx = order.index(column)
        return order[idx + 1] if idx + 1 < len(order) else None
    except ValueError:
        return None


def _load_state() -> Dict[str, Any]:
    state = _load_json(STATE_PATH, {
        "run_id": None,
        "loop_count": 0,
        "processed_cards": [],
        "retry_counts": {},
        "last_run_ts": None,
    })
    state.setdefault("processed_cards", [])
    state.setdefault("retry_counts", {})
    state.setdefault("loop_count", 0)
    state.setdefault("last_run_ts", None)
    return state


def _save_state(state: Dict[str, Any]) -> None:
    _write_json(STATE_PATH, state)


def _record_sequence(run_id: str, steps: List[Dict[str, Any]]) -> None:
    data = _load_json(SEQUENCE_PATH, {"runs": [], "total_runs": 0})
    if not isinstance(data, dict):
        data = {"runs": [], "total_runs": 0}
    data.setdefault("runs", [])
    data.setdefault("total_runs", 0)
    data["runs"].append({
        "run_id": run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "operation_count": len(steps),
        "operations": steps,
    })
    data["total_runs"] = data.get("total_runs", 0) + 1
    _write_json(SEQUENCE_PATH, data)


def _record_math(run_id: str, step: Dict[str, Any]) -> None:
    math_return = step.get("math_returned")
    if not math_return:
        return
    _append_jsonl(MATH_RETURNS_PATH, {
        "run_id": run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": step.get("step"),
        "name": step.get("name"),
        "math": math_return.get("math"),
        "constructs": math_return.get("constructs") or [],
        "source_files": math_return.get("source_files") or [],
        "validation_status": math_return.get("validation_status"),
        "duration_ms": math_return.get("duration_ms"),
    })


def run_once() -> Dict[str, Any]:
    board = _load_json(BOARD_PATH, {"cards": [], "loop_policy": {}})
    cards: List[Dict[str, Any]] = board.get("cards", [])[:CARD_LIMIT]
    state = _load_state()
    loop_count = state.get("loop_count", 0) + 1
    state["loop_count"] = loop_count
    run_id = f"{time.time():.0f}"
    state["run_id"] = run_id
    steps: List[Dict[str, Any]] = []
    advanced = 0
    requeued = 0

    runtime = POG3Runtime.for_session(run_id)

    for card in cards:
        card_id = card.get("id")
        column = card.get("column")
        title = card.get("title", "")
        outputs = card.get("outputs") or []
        math_returned = card.get("auto_math_return")
        duration_ms = card.get("auto_duration_ms")

        # Deterministically derive emotional weights from the card's title
        title_hash = hashlib.md5(title.encode("utf-8")).digest()
        chaos = (title_hash[0] % 100) / 100.0
        whimsy = (title_hash[1] % 100) / 100.0
        dark_tone = (title_hash[2] % 100) / 100.0

        # Construct intent vector
        intent = IntentVector(
            temporal=(1 if loop_count % 3 == 0 else 0, 1 if loop_count % 3 == 1 else 0, 1 if loop_count % 3 == 2 else 0),
            emotional=(chaos, whimsy, dark_tone),
            action=(1 if column in ["ready", "parse"] else 0, 1 if column in ["classify", "learn_math"] else 0, 1 if column in ["tune_timer", "done"] else 0)
        )

        # Consult oracle central nervous system
        state_obj, capture = runtime.engine.consult(intent, context={"card_id": card_id, "title": title})
        telemetry = capture.to_telemetry()

        # Update card with oracle volition telemetry
        card["oracle_volition"] = telemetry

        step = {
            "step": len(steps) + 1,
            "name": title,
            "status": "ok" if _outputs_present(outputs) else "pending",
            "duration_ms": duration_ms,
            "math_returned": math_returned,
            "files_touched": card.get("inputs", []) + outputs,
            "next_step": None,
            "oracle": telemetry,
        }

        if _outputs_present(outputs):
            oracle_action = state_obj.provenance["king_wen_action"]
            if oracle_action in ["ASSERT", "ADAPT"]:
                new_column = _advance_column(column)
                if new_column:
                    card["column"] = new_column
                    step["next_step"] = new_column
                    advanced += 1
            else:
                step["status"] = "deferred"
                step["deferral_reason"] = f"Oracle action {oracle_action} (YIELD/WAIT) requested temporal holding."
                requeued += 1

        _record_math(run_id, step)
        steps.append(step)
    _record_sequence(run_id, steps)
    state["last_run_ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save_state(state)
    _write_json(BOARD_PATH, board)
    return {
        "run_id": run_id,
        "loop_count": state.get("loop_count"),
        "advanced": advanced,
        "deferred": requeued,
        "cards": len(cards),
    }


def main() -> int:
    result = run_once()
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
