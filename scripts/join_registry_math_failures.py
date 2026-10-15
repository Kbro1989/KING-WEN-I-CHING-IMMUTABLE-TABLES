#!/usr/bin/env python3
"""
Join the paper↔repo relationship registry with math failure/recovery datasets.

PURPOSE
=======
The registry maps papers to repositories. The math failure/recovery datasets
record extraction problems per paper. Joining them creates a evidence chain:
  paper → repository → extraction failures → recovery attempts

This answers: "Which repositories are associated with papers that have
known extraction problems, and what are those problems?"

DATA SOURCES
============
- paper_repo_relationship_registry.json  (259 records, 125 papers)
- math_recovery/*.json                   (14 papers with recovery data)
- math_failure_corpus.jsonl              (33 records, 1 paper)

OUTPUT
======
DATASETS/paper_repo_math_failure_join.json
  - one record per (paper, repo) pair, augmented with:
    - math_failure_count: number of failed equations for this paper
    - math_recovery_count: number of recovery attempts
    - math_failure_states: breakdown by failure state
    - math_recovery_stats: recoverable/solvable counts
    - has_math_issues: bool (any extraction problems detected)
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SRC = ROOT / "DATASETS" / "paper_repo_relationship_registry.json"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery"
FAILURE_SRC = ROOT / "DATASETS" / "math_failure_corpus.jsonl"
OUT_JSON = ROOT / "DATASETS" / "paper_repo_math_failure_join.json"


def load_math_recovery() -> dict[str, dict]:
    """Load math recovery data keyed by arxiv_id."""
    out = {}
    for f in RECOVERY_DIR.glob("*_recovery.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        stats = d.get("stats", {})
        arxiv_id = stats.get("arxiv_id", "")
        if not arxiv_id:
            # try to infer from filename
            arxiv_id = f.stem.replace("_recovery", "")
        results = d.get("results", [])
        out[arxiv_id] = {
            "total_equations": stats.get("total_equations", len(results)),
            "recoverable": stats.get("recoverable", 0),
            "solvable": stats.get("solvable", 0),
            "status": stats.get("status", ""),
            "results_count": len(results),
        }
    return out


def load_math_failures() -> dict[str, dict]:
    """Load math failure corpus keyed by paper."""
    out = {}
    for l in FAILURE_SRC.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        paper = r.get("paper", "")
        if paper not in out:
            out[paper] = {"count": 0, "states": Counter(), "unknown_commands": set()}
        out[paper]["count"] += 1
        out[paper]["states"][r.get("state", "UNKNOWN")] += 1
        if r.get("unknown"):
            for u in r["unknown"]:
                out[paper]["unknown_commands"].add(u)
    # convert sets to lists for JSON
    for v in out.values():
        v["unknown_commands"] = sorted(v["unknown_commands"])
        v["states"] = dict(v["states"])
    return out


def main() -> int:
    registry = json.loads(REGISTRY_SRC.read_text(encoding="utf-8"))
    math_recovery = load_math_recovery()
    math_failures = load_math_failures()

    records = []
    for r in registry["records"]:
        pid = r["paper_id"]
        recovery = math_recovery.get(pid, {})
        failure = math_failures.get(pid, {})

        records.append({
            **r,
            "math_failure_count": failure.get("count", 0),
            "math_failure_states": failure.get("states", {}),
            "math_unknown_commands": failure.get("unknown_commands", []),
            "math_recovery_total": recovery.get("total_equations", 0),
            "math_recovery_recoverable": recovery.get("recoverable", 0),
            "math_recovery_solvable": recovery.get("solvable", 0),
            "has_math_issues": bool(failure.get("count", 0) > 0 or recovery.get("total_equations", 0) > 0),
        })

    # summary
    papers_with_issues = set()
    papers_with_recovery = set()
    for r in records:
        if r["math_failure_count"] > 0:
            papers_with_issues.add(r["paper_id"])
        if r["math_recovery_total"] > 0:
            papers_with_recovery.add(r["paper_id"])

    summary = {
        "total_records": len(records),
        "papers_with_math_failures": len(papers_with_issues),
        "papers_with_math_recovery": len(papers_with_recovery),
        "papers_with_issues": sorted(papers_with_issues | papers_with_recovery),
        "math_recovery_available_for": sorted(math_recovery.keys()),
        "math_failure_available_for": sorted(math_failures.keys()),
    }

    out = {"summary": summary, "records": records}
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"total records: {len(records)}")
    print(f"papers with math failures: {len(papers_with_issues)}")
    print(f"papers with math recovery: {len(papers_with_recovery)}")
    print(f"\nmath recovery available for: {sorted(math_recovery.keys())}")
    print(f"math failure available for: {sorted(math_failures.keys())}")
    print(f"\nwrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())