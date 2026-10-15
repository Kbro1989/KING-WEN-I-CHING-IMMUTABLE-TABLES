#!/usr/bin/env python3
"""
Build the equation-level comparison table for Marker vs. King Wen.

PURPOSE
=======
Each reference equation gets one record with:
  - equation_id: stable ID ({paper_id}:eq{index:04d})
  - paper_id: arXiv ID
  - kingwen_result: the King Wen extraction result (from recovery file)
  - marker_result: (to be filled when Marker is run)
  - marker_status: "pending" until Marker output is available

THREE EVALUATION DIMENSIONS (measured separately)
==================================================
1. Extraction completeness: Was the equation detected and captured?
   - Detected: yes/no
   - Duplicated: yes/no
   - Boundary errors: yes/no

2. Structural fidelity: Were operators, grouping, bounds, fractions,
   superscripts, subscripts, and symbol order preserved?
   - AST match: yes/no/partial
   - Structure checks: individual flags for sub/superscripts, fractions,
     matrices, nesting, operator bounds, symbol order

3. Mathematical solvability: Can the recovered representation be parsed
   and processed by the downstream symbolic system?
   - Parseable: yes/no
   - Normalizable: yes/no
   - Solvable: yes/no
   - Failure reason: (if not parseable)

OUTPUT
======
DATASETS/equation_level_comparison.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery"
MANIFEST = ROOT / "DATASETS" / "benchmark_manifest.json"
OUT_JSONL = ROOT / "DATASETS" / "equation_level_comparison.jsonl"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    records = []
    for paper in manifest["papers"]:
        pid = paper["paper_id"]
        recovery_path = RECOVERY_DIR / f"{pid}_recovery.json"

        if not recovery_path.exists():
            continue

        recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
        results = recovery.get("results", [])

        for i, r in enumerate(results, 1):
            eq_id = f"{pid}:eq{i:04d}"

            record = {
                "equation_id": eq_id,
                "paper_id": pid,
                "kingwen_result": {
                    "latex": r.get("latex", ""),
                    "recovered": r.get("recovered", ""),
                    "solvable": r.get("solvable", False),
                    "solution": r.get("solution"),
                    "notes": r.get("notes", []),
                },
                "marker_result": None,
                "marker_status": "pending",
                "evaluation": {
                    "extraction_completeness": {
                        "detected": None,  # to be filled
                        "duplicated": None,
                        "boundary_errors": None,
                    },
                    "structural_fidelity": {
                        "ast_match": None,
                        "subscripts_preserved": None,
                        "superscripts_preserved": None,
                        "fractions_preserved": None,
                        "matrices_preserved": None,
                        "nesting_preserved": None,
                        "operator_bounds_preserved": None,
                        "symbol_order_preserved": None,
                    },
                    "mathematical_solvability": {
                        "parseable": None,
                        "normalizable": None,
                        "solvable": None,
                        "failure_reason": None,
                    },
                },
            }
            records.append(record)

    # Write JSONL
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"total equation records: {len(records)}")
    print(f"papers covered: {len(manifest['papers'])}")
    print(f"wrote {OUT_JSONL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())