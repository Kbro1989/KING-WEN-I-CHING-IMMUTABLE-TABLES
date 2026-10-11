#!/usr/bin/env python3
"""
REGRESSION HUNT — occurrence-keyed comparison between two recovery runs.

MIGRATED (P3): no longer uses LaTeX as a dictionary key. Identical
expressions at different source locations are compared as independent
occurrences. Uses math_occurrence_accounting.OccurrenceLedger for
reconciliation.

Compares the per-occurrence outcome between two recovery runs.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import occurrence_key, SourceOccurrence  # noqa: E402
from math_occurrence_accounting import OccurrenceLedger, compare_regressions  # noqa: E402

A = ROOT / "DATASETS" / "math_recovery_after_fix"
B = ROOT / "DATASETS" / "math_recovery_nested_fix"


def load_ledger(dataset_dir: Path, stage: str) -> OccurrenceLedger:
    """
    Load recovery results into an OccurrenceLedger.

    Each record is keyed by occurrence identity (paper_id + version +
    source_locator + occurrence_index), NOT by LaTeX. Identical expressions
    at different locations remain independent entries.
    """
    source_occurrences = []
    records = []

    for f in sorted(dataset_dir.glob("*_recovery.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

        paper_id = j.get("paper_id") or f.stem.replace("_recovery", "")
        paper_version = j.get("paper_version") or "latest"

        for idx, r in enumerate(j.get("results", [])):
            latex = r.get("latex")
            if not latex:
                continue

            # Build a SourceOccurrence with proper identity
            source = SourceOccurrence(
                paper_id=paper_id,
                paper_version=paper_version,
                source_locator=r.get("source_locator") or f"math[{idx}]",
                occurrence_index=r.get("occurrence_index", idx),
                source_hash=r.get("source_hash") or "",
                latex=latex,
                mathml=r.get("mathml"),
            )
            source_occurrences.append(source)

            # Build a minimal RecoveryRecord for accounting
            from math_contract import RecoveryRecord
            records.append(RecoveryRecord(
                source=source,
                parse_status=r.get("parse_status", "complete"),
                structural_status=r.get("structural_status", "unverified"),
                backend_status=r.get("backend_status", "not_attempted"),
                solution_status=r.get("solution_status", "not_attempted"),
            ))

    return OccurrenceLedger.from_records(
        paper_id="*",
        paper_version="*",
        stage=stage,
        source_occurrences=source_occurrences,
        records=records,
    )


def load_outcomes(dataset_dir: Path) -> dict[str, str]:
    """
    Load occurrence_key -> outcome map for regression comparison.

    outcome is one of: "solvable", "failed", "error", "unknown".
    """
    outcomes: dict[str, str] = {}
    for f in sorted(dataset_dir.glob("*_recovery.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

        paper_id = j.get("paper_id") or f.stem.replace("_recovery", "")
        paper_version = j.get("paper_version") or "latest"

        for idx, r in enumerate(j.get("results", [])):
            latex = r.get("latex")
            if not latex:
                continue

            source = SourceOccurrence(
                paper_id=paper_id,
                paper_version=paper_version,
                source_locator=r.get("source_locator") or f"math[{idx}]",
                occurrence_index=r.get("occurrence_index", idx),
                source_hash=r.get("source_hash") or "",
                latex=latex,
                mathml=r.get("mathml"),
            )
            key = occurrence_key(source)

            if r.get("solvable"):
                outcomes[key] = "solvable"
            elif r.get("error"):
                outcomes[key] = "error"
            elif r.get("recovered") or r.get("recovered_latex"):
                outcomes[key] = "failed"
            else:
                outcomes[key] = "unknown"

    return outcomes


def main():
    print("=" * 78)
    print("REGRESSION HUNT — occurrence-keyed (P3)")
    print("=" * 78)
    print()

    ledger_a = load_ledger(A, "after_fix")
    ledger_b = load_ledger(B, "nested_fix")

    report_a = ledger_a.reconcile()
    report_b = ledger_b.reconcile()

    print(f"  Stage A ({A.name}):")
    print(f"    source occurrences      : {report_a['source_occurrences']}")
    print(f"    unique source keys      : {report_a['unique_source_keys']}")
    print(f"    record occurrences      : {report_a['record_occurrences']}")
    print(f"    matched                 : {report_a['matched']}")
    print(f"    missing                 : {report_a['missing']}")
    print(f"    unexpected              : {report_a['unexpected']}")
    print()
    print(f"  Stage B ({B.name}):")
    print(f"    source occurrences      : {report_b['source_occurrences']}")
    print(f"    unique source keys      : {report_b['unique_source_keys']}")
    print(f"    record occurrences      : {report_b['record_occurrences']}")
    print(f"    matched                 : {report_b['matched']}")
    print(f"    missing                 : {report_b['missing']}")
    print(f"    unexpected              : {report_b['unexpected']}")
    print()

    # Compare outcomes keyed by occurrence identity
    outcomes_a = load_outcomes(A)
    outcomes_b = load_outcomes(B)

    common = set(outcomes_a) & set(outcomes_b)
    newly_missing = set(outcomes_a) - set(outcomes_b)
    newly_added = set(outcomes_b) - set(outcomes_a)

    lost = []      # solvable in A, not in B
    gained = []    # not solvable in A, solvable in B
    status_changed = []

    for k in sorted(common):
        oa = outcomes_a[k]
        ob = outcomes_b[k]
        if oa != ob:
            status_changed.append((k[:16], oa, ob))
            if oa == "solvable" and ob != "solvable":
                lost.append((k[:16], oa, ob))
            elif oa != "solvable" and ob == "solvable":
                gained.append((k[:16], oa, ob))

    print("=" * 78)
    print("OCCURRENCE-KEYED COMPARISON")
    print("=" * 78)
    print()
    print(f"  Common occurrences       : {len(common)}")
    print(f"  Newly missing in B       : {len(newly_missing)}")
    print(f"  Newly added in B          : {len(newly_added)}")
    print(f"  Status changed            : {len(status_changed)}")
    print(f"  LOST solvable (A->B)      : {len(lost)}")
    print(f"  GAINED solvable (A->B)    : {len(gained)}")
    print()

    if lost:
        print("=" * 78)
        print("LOST — was solvable, now is not")
        print("=" * 78)
        print()
        for key_prefix, oa, ob in lost[:20]:
            print(f"  [{key_prefix}]  {oa} -> {ob}")
        print()

    if gained:
        print("=" * 78)
        print("GAINED — now solvable")
        print("=" * 78)
        print()
        for key_prefix, oa, ob in gained[:10]:
            print(f"  [{key_prefix}]  {oa} -> {ob}")
        print()

    # Bucket the B-side outcomes for lost equations
    if lost:
        c = Counter(ob for _, _, ob in lost)
        print("B-side outcome classes for the LOST set:")
        for k, v in c.most_common():
            print(f"  {v:>4}  {k}")
        print()

    # Ambiguity check
    if ledger_a.duplicate_occurrence_keys > 0 or ledger_b.duplicate_occurrence_keys > 0:
        print("WARNING: duplicate occurrence keys detected — comparison may be ambiguous")
        print(f"  A duplicates: {ledger_a.duplicate_occurrence_keys}")
        print(f"  B duplicates: {ledger_b.duplicate_occurrence_keys}")
        print()


if __name__ == "__main__":
    main()
