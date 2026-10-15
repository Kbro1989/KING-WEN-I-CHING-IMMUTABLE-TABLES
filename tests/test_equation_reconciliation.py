#!/usr/bin/env python3
"""
Regression test for equation count reconciliation invariants.

TWO INVARIANTS
==============
1. Paper count: exactly 14 papers in the baseline
2. Equation counts: recovered + unresolved == total for every paper

RUN
===
    python tests/test_equation_reconciliation.py

EXIT CODE
=========
0 = all checks pass
1 = at least one check failed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECON = ROOT / "DATASETS" / "equation_count_reconciliation.json"

EXPECTED_PAPERS = {
    "2009.00031", "2102.03334", "2605.00155", "2605.00224",
    "2605.06070", "2605.18130", "2605.22715", "2605.23244",
    "2605.24807", "2605.24856", "2605.25036", "2605.25334",
    "2605.28615", "2605.28896",
}


def main() -> int:
    if not RECON.exists():
        print(f"FAIL: {RECON.relative_to(ROOT)} not found")
        return 1

    d = json.loads(RECON.read_text(encoding="utf-8"))
    errors = []

    # Check 1: paper count == 14
    papers = d["papers"]
    paper_ids = set(papers.keys())
    if len(paper_ids) != 14:
        errors.append(f"paper count: expected 14, got {len(paper_ids)}")
    if paper_ids != EXPECTED_PAPERS:
        missing = EXPECTED_PAPERS - paper_ids
        extra = paper_ids - EXPECTED_PAPERS
        if missing:
            errors.append(f"missing papers: {sorted(missing)}")
        if extra:
            errors.append(f"unexpected papers: {sorted(extra)}")

    # Check 2: excluded list contains 1406.2661
    excluded = d.get("excluded_from_baseline", [])
    excluded_ids = {x["arxiv_id"] for x in excluded}
    if "1406.2661" not in excluded_ids:
        errors.append("1406.2661 should be in excluded_from_baseline")

    # Check 3: per-paper invariant: recovered + unresolved == total
    for pid, p in papers.items():
        total = p["total"]
        recovered = p["recovered"]
        unresolved = p["unresolved"]
        if recovered + unresolved != total:
            errors.append(
                f"{pid}: {recovered} + {unresolved} != {total}"
            )
        # solvable must be subset of recovered
        if p["solvable"] > recovered:
            errors.append(
                f"{pid}: solvable ({p['solvable']}) > recovered ({recovered})"
            )

    # Check 4: grand total invariant
    gt = d["grand_totals"]
    if gt["recovered"] + gt["unresolved"] != gt["total"]:
        errors.append(
            f"grand total: {gt['recovered']} + {gt['unresolved']} != {gt['total']}"
        )
    if not gt["check_pass"]:
        errors.append("grand total check_pass is False")

    # Report
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: 14 papers, {gt['total']} equations")
    print(f"  recovered: {gt['recovered']} ({100*gt['recovered']/gt['total']:.1f}%)")
    print(f"  solvable:  {gt['solvable']} ({100*gt['solvable']/gt['total']:.1f}%)")
    print(f"  unresolved: {gt['unresolved']} ({100*gt['unresolved']/gt['total']:.1f}%)")
    print(f"  excluded: {sorted(excluded_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())