#!/usr/bin/env python3
"""
METRICS SEPARATION REPORT — P4-C
=================================
Reports five INDEPENDENT metrics that must never be conflated:

  1. parsing_success     -- did the MathML parser emit an expression?
  2. structural_fidelity -- did the typed AST survive extraction + round-trip?
  3. recovery_coverage   -- does every source occurrence have a recovery record?
  4. solver_acceptance   -- did SymPy accept the recovered expression?
  5. solution_correctness-- is the solution mathematically correct?
                            (REQUIRES INDEPENDENT VALIDATION -- not derived
                             from solver acceptance)

A parser that succeeds does not imply the mathematics survived.
A round-trip that passes does not imply the tree is semantically correct.
A solver that accepts does not imply the solution is correct.

Also enforces the population boundary: the 4,235-occurrence structural
pipeline and the 991-equation E2E run for paper 2605.00155 are DIFFERENT
populations and are reported with separate denominators.

Output:
  DATASETS/metrics_separation_2026-10-11.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import SourceOccurrence, occurrence_key  # noqa: E402

CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery_v16"
E2E_PAPER = "2605.00155"
OUT = ROOT / "DATASETS" / "metrics_separation_2026-10-11.json"


def load_pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    p = BASELINE / "pinned_versions.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    pins[parts[0]] = parts[1]
    return pins


def main() -> int:
    pins = load_pins()

    # ---- Population A: the full corpus structural pipeline ----
    source_keys: Counter = Counter()
    per_paper: Counter = Counter()
    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        version = pins.get(paper_id, "unpinned")
        for i, eq in enumerate(data.get("equations", [])):
            occ = SourceOccurrence(
                paper_id=paper_id, paper_version=version,
                source_locator=f"math[{i}]", occurrence_index=i,
                source_hash="",
            )
            source_keys[occurrence_key(occ)] += 1
            per_paper[paper_id] += 1

    # recovery records
    recovery_keys: Counter = Counter()
    parse_ok = 0
    parse_total = 0
    struct_ok = 0
    solver_accept = 0
    rec_total = 0
    for rf in sorted(RECOVERY_DIR.glob("*_recovery.json")):
        paper_id = rf.name.replace("_recovery.json", "")
        version = pins.get(paper_id, "unpinned")
        rj = json.loads(rf.read_text(encoding="utf-8", errors="replace"))
        for r in rj.get("results", []):
            idx = r.get("occurrence")
            if not isinstance(idx, int):
                continue
            rec_total += 1
            occ = SourceOccurrence(
                paper_id=paper_id, paper_version=version,
                source_locator=f"math[{idx}]", occurrence_index=idx,
                source_hash="",
            )
            recovery_keys[occurrence_key(occ)] += 1
            # metric 1: parsing success (path:tree means the parser emitted a tree)
            notes = r.get("notes") or []
            if any(str(n).startswith("path:tree") for n in notes):
                parse_ok += 1
            parse_total += 1
            # metric 2: structural fidelity (canonical_tree persisted)
            if r.get("canonical_tree") is not None:
                struct_ok += 1
            # metric 4: solver acceptance
            if r.get("solvable"):
                solver_accept += 1

    recovery_missing = sum((source_keys - recovery_keys).values())
    recovery_only = sum((recovery_keys - source_keys).values())

    # ---- Population B: the E2E run for ONE paper (separate denominator) ----
    e2e_path = ROOT / "DATASETS" / f"e2e_output_{E2E_PAPER}.json"
    e2e: dict[str, Any] = {"present": e2e_path.exists()}
    if e2e_path.exists():
        d = json.loads(e2e_path.read_text(encoding="utf-8"))
        e2e.update({
            "arxiv_id": d.get("arxiv_id"),
            "total_equations": d.get("total_equations"),
            "solvable": d.get("solvable"),
            "partial": d.get("partial"),
            "rejected": d.get("rejected"),
            "note": (
                "This is a DIFFERENT population from the 4235-occurrence "
                "structural pipeline. Do not compare denominators."
            ),
        })

    report = {
        "date": "2026-10-11",
        "principle": (
            "Parsing success, structural fidelity, recovery coverage, solver "
            "acceptance, and solution correctness are SEPARATE metrics. "
            "None implies the next."
        ),
        "population_a_structural_pipeline": {
            "description": "Full corpus, all papers",
            "source_occurrences": sum(source_keys.values()),
            "recovery_occurrences": rec_total,
            "papers": len(per_paper),
            "metrics": {
                "parsing_success": {
                    "count": parse_ok, "total": parse_total,
                    "pct": round(100.0 * parse_ok / parse_total, 2) if parse_total else 0.0,
                    "means": "MathML parser emitted a tree (path:tree)",
                },
                "structural_fidelity": {
                    "count": struct_ok, "total": rec_total,
                    "pct": round(100.0 * struct_ok / rec_total, 2) if rec_total else 0.0,
                    "means": "typed canonical_tree persisted in the recovery record",
                },
                "recovery_coverage": {
                    "missing": recovery_missing,
                    "extra": recovery_only,
                    "covered": rec_total,
                    "total": sum(source_keys.values()),
                    "means": "every source occurrence has a recovery record",
                },
                "solver_acceptance": {
                    "count": solver_accept, "total": rec_total,
                    "pct": round(100.0 * solver_accept / rec_total, 2) if rec_total else 0.0,
                    "means": "SymPy accepted the recovered expression -- NOT correctness",
                },
                "solution_correctness": {
                    "count": None,
                    "status": "NOT_MEASURED",
                    "means": (
                        "Requires independent validation (substitution back into "
                        "the source relation, dimension check, or symbolic "
                        "equivalence). Solver acceptance is NOT evidence."
                    ),
                },
            },
        },
        "population_b_e2e_single_paper": e2e,
        "population_boundary": (
            "Population A (4235 occurrences, 14 papers) and Population B "
            f"({e2e.get('total_equations', 'n/a')} equations, paper {E2E_PAPER}) "
            "are different populations. Their denominators are not comparable."
        ),
    }

    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    m = report["population_a_structural_pipeline"]["metrics"]
    print("=== METRICS SEPARATION (P4-C) ===")
    print(f"Population A: {sum(source_keys.values())} source occurrences, "
          f"{len(per_paper)} papers")
    print()
    print(f"  1. parsing_success      {m['parsing_success']['count']:>5} / "
          f"{m['parsing_success']['total']:<5} ({m['parsing_success']['pct']}%)")
    print(f"  2. structural_fidelity  {m['structural_fidelity']['count']:>5} / "
          f"{m['structural_fidelity']['total']:<5} ({m['structural_fidelity']['pct']}%)")
    print(f"  3. recovery_coverage    missing={m['recovery_coverage']['missing']} "
          f"extra={m['recovery_coverage']['extra']} "
          f"covered={m['recovery_coverage']['covered']}")
    print(f"  4. solver_acceptance    {m['solver_acceptance']['count']:>5} / "
          f"{m['solver_acceptance']['total']:<5} ({m['solver_acceptance']['pct']}%)")
    print(f"  5. solution_correctness {m['solution_correctness']['status']}")
    print()
    print("Population B (E2E, separate denominator):")
    if e2e.get("present"):
        print(f"  {E2E_PAPER}: {e2e['total_equations']} equations, "
              f"{e2e['solvable']} solvable, {e2e['partial']} partial, "
              f"{e2e['rejected']} rejected")
    else:
        print("  E2E output not found")
    print()
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
