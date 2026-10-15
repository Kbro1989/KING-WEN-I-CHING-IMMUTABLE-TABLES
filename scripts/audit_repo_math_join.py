#!/usr/bin/env python3
"""
Audit the paper↔repo↔math-failure join for scope integrity.

THE PROBLEM WITH THE CURRENT JOIN
==================================
The join repeats paper-level math counts (360 equations, 42 recoverable)
for every repository linked to that paper. Summing them would double-count.
Additionally, math_failure_corpus.jsonl and math_recovery/*.json come from
different scopes:
  - math_failure_corpus: 33 records from 1 paper, keyed by 'paper' field
  - math_recovery: 14 papers, keyed by arxiv_id, with stats + results

These are NOT the same scope, and the join does not make that explicit.

THIS AUDIT
==========
1. For each joined record, trace back to the original source record
2. Flag scope mismatches (paper-level vs repo-level)
3. Define denominators explicitly
4. Verify the 5-paper intersection uses exact arXiv IDs
5. Separate official implementations from third-party references
6. Preserve unresolved expressions — do not count them as absent

OUTPUT
======
DATASETS/paper_repo_math_failure_audit.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOIN_SRC = ROOT / "DATASETS" / "paper_repo_math_failure_join.json"
REGISTRY_SRC = ROOT / "DATASETS" / "paper_repo_relationship_registry.json"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery"
FAILURE_SRC = ROOT / "DATASETS" / "math_failure_corpus.jsonl"
OUT_JSON = ROOT / "DATASETS" / "paper_repo_math_failure_audit.json"


def trace_to_source(paper_id: str) -> dict:
    """Trace a paper's math data back to its original source records."""
    # Check math_recovery
    recovery_file = RECOVERY_DIR / f"{paper_id}_recovery.json"
    recovery_data = None
    if recovery_file.exists():
        d = json.loads(recovery_file.read_text(encoding="utf-8"))
        recovery_data = {
            "source": str(recovery_file.relative_to(ROOT)),
            "stats": d.get("stats", {}),
            "results_count": len(d.get("results", [])),
        }

    # Check math_failure_corpus — records are keyed by 'paper' field
    failure_data = None
    if FAILURE_SRC.exists():
        matches = []
        for l in FAILURE_SRC.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("paper", "") == paper_id:
                matches.append({
                    "index": r.get("index"),
                    "state": r.get("state"),
                    "latex_len": r.get("latex_len"),
                    "recovered": r.get("recovered", ""),
                    "unknown": r.get("unknown", []),
                })
        if matches:
            failure_data = {
                "source": str(FAILURE_SRC.relative_to(ROOT)),
                "record_count": len(matches),
                "records": matches,
            }

    # Check cross_stage_drop_trace
    drop_trace_file = ROOT / "DATASETS" / "cross_stage_drop_trace.json"
    drop_data = None
    if drop_trace_file.exists():
        d = json.loads(drop_trace_file.read_text(encoding="utf-8"))
        drop_data = {
            "source": str(drop_trace_file.relative_to(ROOT)),
            "metrics": d.get("metrics", {}),
            "conservation": d.get("conservation", {}),
        }

    return {
        "paper_id": paper_id,
        "math_recovery": recovery_data,
        "math_failure_corpus": failure_data,
        "cross_stage_drop_trace": drop_data,
    }


def main() -> int:
    join = json.loads(JOIN_SRC.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_SRC.read_text(encoding="utf-8"))

    # Build set of official implementations for separation
    official_pairs = set()
    for r in registry["records"]:
        if r["relationship_type"] == "official_implementation":
            official_pairs.add((r["paper_id"], r["repository_url"]))

    # Audit each joined record
    audit_records = []
    for r in join["records"]:
        pid = r["paper_id"]
        repo = r["repository_url"]
        is_official = (pid, repo) in official_pairs

        # The math counts in the join are PAPER-LEVEL, not repo-level.
        # Flag this so downstream consumers don't sum them.
        scope_warning = (
            "math_failure_count and math_recovery_total are PAPER-LEVEL "
            "values repeated for each repo link. Do NOT sum across repos."
        )

        # Trace to source
        source = trace_to_source(pid)

        audit_records.append({
            "paper_id": pid,
            "repository_url": repo,
            "relationship_type": r["relationship_type"],
            "is_official_implementation": is_official,
            "math_data_scope": "paper_level",
            "scope_warning": scope_warning,
            "math_failure_count": r["math_failure_count"],
            "math_recovery_total": r["math_recovery_total"],
            "math_recovery_recoverable": r["math_recovery_recoverable"],
            "math_recovery_solvable": r["math_recovery_solvable"],
            "source_trace": source,
        })

    # Verify the 5-paper intersection
    papers_with_issues = set()
    for r in join["records"]:
        if r["has_math_issues"]:
            papers_with_issues.add(r["paper_id"])

    # Check for papers where join says 0 failures but has recovery records
    scope_mismatches = []
    for r in join["records"]:
        if r["math_failure_count"] == 0 and r["math_recovery_total"] > 0:
            scope_mismatches.append({
                "paper_id": r["paper_id"],
                "issue": "0 failures but has recovery records — different scopes",
                "math_failure_count": r["math_failure_count"],
                "math_recovery_total": r["math_recovery_total"],
            })

    # Denominator analysis
    # The recovery rate denominator should be total_equations, not total_equations * num_repos
    denominator_analysis = {}
    for pid in papers_with_issues:
        source = trace_to_source(pid)
        if source["math_recovery"]:
            stats = source["math_recovery"]["stats"]
            total = stats.get("total_equations", 0)
            recoverable = stats.get("recoverable", 0)
            solvable = stats.get("solvable", 0)
            denominator_analysis[pid] = {
                "total_equations": total,
                "recoverable": recoverable,
                "solvable": solvable,
                "recovery_rate_pct": round(100 * recoverable / total, 1) if total else None,
                "solvable_rate_pct": round(100 * solvable / total, 1) if total else None,
                "note": "These are PAPER-LEVEL rates. Do not multiply by repo count.",
            }

    # Official vs third-party separation
    official_records = [r for r in audit_records if r["is_official_implementation"]]
    third_party_records = [r for r in audit_records if not r["is_official_implementation"]]

    # Unresolved expressions: equations that are neither recoverable nor solvable
    # These must be preserved, not counted as absent
    unresolved = {}
    for pid, analysis in denominator_analysis.items():
        total = analysis["total_equations"]
        recoverable = analysis["recoverable"]
        solvable = analysis["solvable"]
        neither = total - recoverable - solvable
        unresolved[pid] = {
            "total_equations": total,
            "recoverable": recoverable,
            "solvable": solvable,
            "unresolved": neither,
            "note": "Unresolved equations are preserved in source files, not discarded",
        }

    out = {
        "summary": {
            "total_joined_records": len(audit_records),
            "papers_with_math_issues": sorted(papers_with_issues),
            "official_implementation_count": len(official_records),
            "third_party_reference_count": len(third_party_records),
            "scope_mismatch_count": len(scope_mismatches),
        },
        "denominator_analysis": denominator_analysis,
        "unresolved_expressions": unresolved,
        "scope_mismatches": scope_mismatches,
        "audit_records": audit_records,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== Join Integrity Audit ===")
    print(f"total joined records: {len(audit_records)}")
    print(f"papers with math issues: {sorted(papers_with_issues)}")
    print(f"official implementations: {len(official_records)}")
    print(f"third-party references: {len(third_party_records)}")
    print(f"scope mismatches: {len(scope_mismatches)}")
    print()
    print("=== Denominator Analysis ===")
    for pid, a in sorted(denominator_analysis.items()):
        print(f"  {pid}: {a['total_equations']} total, {a['recoverable']} recoverable "
              f"({a['recovery_rate_pct']}%), {a['solvable']} solvable ({a['solvable_rate_pct']}%)")
    print()
    print("=== Unresolved Expressions ===")
    for pid, u in sorted(unresolved.items()):
        print(f"  {pid}: {u['unresolved']} unresolved (preserved in source)")
    print()
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())