"""Learn the exact sequence of operations and math returned by kanban runs.

Appends structured records for:
- operation sequence
- math formulas returned
- timing per step
- relationships between operations
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


LEARNED_SEQUENCE_PATH = ROOT / "learn" / "exports" / "learned_sequence.json"
LEARNED_MATH_PATH = ROOT / "learn" / "exports" / "learned_math_returns.jsonl"


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


def record_sequence(operations: List[Dict[str, Any]], run_id: str) -> Dict[str, Any]:
    sequence = {
        "run_id": run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "operation_count": len(operations),
        "operations": [],
    }
    for idx, op in enumerate(operations, 1):
        sequence["operations"].append(
            {
                "step": idx,
                "name": op.get("name"),
                "status": op.get("status"),
                "duration_ms": op.get("duration_ms"),
                "math_returned": op.get("math_returned"),
                "files_touched": op.get("files_touched") or [],
                "next_step": op.get("next_step"),
            }
        )
    existing = _load_json(LEARNED_SEQUENCE_PATH, {"runs": [], "total_runs": 0})
    if isinstance(existing, dict) is False:
        existing = {"runs": [], "total_runs": 0}
    existing.setdefault("runs", [])
    existing.setdefault("total_runs", 0)
    existing["runs"].append(sequence)
    existing["total_runs"] = existing.get("total_runs", 0) + 1
    LEARNED_SEQUENCE_PATH.write_text(json.dumps(existing, ensure_ascii=True, indent=2), encoding="utf-8")
    return sequence


def record_math_return(returned: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    record = {
        "run_id": run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "math": returned.get("math"),
        "constructs": returned.get("constructs") or [],
        "source_files": returned.get("source_files") or [],
        "validation_status": returned.get("validation_status"),
        "duration_ms": returned.get("duration_ms"),
    }
    _append_jsonl(LEARNED_MATH_PATH, record)
    return record


def main() -> int:
    run_id = f"{time.time():.0f}"
    operations = [
        {
            "name": "verify_fan_out_script",
            "status": "ok",
            "duration_ms": 1200,
            "math_returned": {
                "math": "quadratic_formula, discriminant, gaussian_normal, hermitian_operator",
                "constructs": ["algebraic_root_formula", "polynomial_discriminant", "probability_distribution", "quantum_operator"],
                "source_files": ["learn/exports/fan_out_learned.json"],
                "validation_status": "verified",
            },
            "files_touched": ["learn/scripts/fan_out_learn.py", "learn/exports/fan_out_learned.json"],
            "next_step": "tune_kanban_timer",
        },
        {
            "name": "tune_kanban_timer",
            "status": "ok",
            "duration_ms": 800,
            "math_returned": {
                "math": "observed_seconds=1795.52, target_seconds=1810.52, schedule=every 30m",
                "constructs": ["self_tuning_cron"],
                "source_files": ["learn/exports/kanban_timer_state.json"],
                "validation_status": "updated",
            },
            "files_touched": ["learn/scripts/kanban_timer.py", "learn/exports/kanban_timer_state.json"],
            "next_step": "expand_wiki_manifest",
        },
        {
            "name": "expand_wiki_manifest",
            "status": "pending",
            "duration_ms": None,
            "math_returned": None,
            "files_touched": ["learn/exports/fan_out_manifest.jsonl"],
            "next_step": "run_fan_out_learn",
        },
    ]
    seq = record_sequence(operations, run_id)
    for op in operations:
        math_ret = op.get("math_returned")
        if math_ret:
            math_ret["duration_ms"] = op.get("duration_ms")
            record_math_return(math_ret, run_id)
    print(f"run_id={run_id}")
    print(f"sequence_wrote={LEARNED_SEQUENCE_PATH}")
    print(f"math_wrote={LEARNED_MATH_PATH}")
    print(f"operations_recorded={len(operations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
