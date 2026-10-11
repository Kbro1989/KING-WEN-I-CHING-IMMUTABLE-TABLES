#!/usr/bin/env python3
"""
AST DUNGEON LEVEL 0 — occurrence-keyed witness identity.

MIGRATED (P3): no longer uses LaTeX as a dictionary key. The witness
identity is (paper_id, source_locator, occurrence_index) — not latex
alone. Uses math_occurrence_accounting for reconciliation.

DEFECT (found by external audit, verified here):
    by_latex[L] = r
keys on `latex` alone, so duplicate occurrences COLLAPSE. For 2605.00155:
    991 source equations but only 651 unique LaTeX -> 340 occurrences lost.

Consequence: "651 matched" does NOT mean 651 of 991 occurrences were matched.
It means 651 unique strings were represented.

FIX: the witness needs a LOCATION dimension.
    (paper, source_locator, occurrence_index) -> recovery

This script verifies the collapse, then re-runs the match with occurrence
identity preserved, and measures how much the collapse was hiding.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import SourceOccurrence, occurrence_key  # noqa: E402
from math_occurrence_accounting import OccurrenceLedger, build_accounting_report  # noqa: E402

PAPER = "2605.00155"

GENS = [
    ("original",   "math_recovery"),
    ("after_fix",  "math_recovery_after_fix"),
    ("nested_fix", "math_recovery_nested_fix"),
    ("v3_bigop",   "math_recovery_v3"),
    ("v4_escapes", "math_recovery_v4"),
    ("v5_logfix",  "math_recovery_v5"),
    ("v6_funcjoin", "math_recovery_v6"),
]


def load_source_occurrences() -> list[SourceOccurrence]:
    """Load source occurrences from the pinned corpus."""
    src_path = ROOT / "DATASETS" / "arxiv_html_corpus" / f"{PAPER}.json"
    src = json.loads(src_path.read_text(encoding="utf-8", errors="replace"))
    src_eqs = src.get("equations", [])

    occurrences = []
    for idx, eq in enumerate(src_eqs):
        latex = eq.get("latex")
        if not latex:
            continue
        occurrences.append(SourceOccurrence(
            paper_id=PAPER,
            paper_version="latest",
            source_locator=eq.get("id") or f"math[{idx}]",
            occurrence_index=idx,
            source_hash="",  # not needed for accounting
            latex=latex,
            mathml=eq.get("mathml"),
        ))
    return occurrences


def load_recovery_ledger(dataset_subdir: str, stage: str) -> OccurrenceLedger:
    """Load recovery results into an OccurrenceLedger keyed by occurrence identity."""
    source_occurrences = []
    records = []

    d = ROOT / "DATASETS" / dataset_subdir
    if not d.exists():
        return OccurrenceLedger(
            paper_id=PAPER, paper_version="latest", stage=stage,
            source_keys=(), record_keys=(),
        )

    for f in sorted(d.glob("*_recovery.json")):
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
            source_occurrences.append(source)

            from math_contract import RecoveryRecord
            records.append(RecoveryRecord(
                source=source,
                parse_status=r.get("parse_status", "complete"),
                structural_status=r.get("structural_status", "unverified"),
                backend_status=r.get("backend_status", "not_attempted"),
                solution_status=r.get("solution_status", "not_attempted"),
            ))

    return OccurrenceLedger.from_records(
        paper_id=PAPER,
        paper_version="latest",
        stage=stage,
        source_occurrences=source_occurrences,
        records=records,
    )


def main():
    # ---------------------------------------------------------------- 1. the defect
    src_occurrences = load_source_occurrences()
    src_latex = [s.latex for s in src_occurrences if s.latex]

    print("=" * 80)
    print("LEVEL 0 — VERIFY THE DUPLICATE-WITNESS COLLAPSE")
    print("=" * 80)
    print()
    print(f"  source equations        : {len(src_occurrences)}")
    print(f"  with latex              : {len(src_latex)}")
    print(f"  UNIQUE latex            : {len(set(src_latex))}")
    print(f"  COLLAPSED occurrences   : {len(src_latex) - len(set(src_latex))}")
    print()

    dupes = Counter(src_latex)
    print("  most-repeated witnesses:")
    for L, n in dupes.most_common(6):
        print(f"    x{n:<3d} {L[:96]}")
    print()

    # ---------------------------------------------------------------- 2. the fix
    print("=" * 80)
    print("LEVEL 0 — MATCH WITH OCCURRENCE IDENTITY PRESERVED")
    print("=" * 80)
    print()
    print("  key: occurrence_key(source) — not latex alone")
    print()

    per_gen = {}
    for label, sub in GENS:
        ledger = load_recovery_ledger(sub, label)
        per_gen[label] = ledger

    print(f"  {'generation':13s} {'records':>9s} {'unique_latex':>13s} {'occurrences':>12s}")
    print("-" * 80)
    for label, _ in GENS:
        if label not in per_gen:
            continue
        ledger = per_gen[label]
        report = build_accounting_report(ledger)
        uniq_latex = len({r.source.latex for r in ledger.record_keys})  # not meaningful, but kept for comparison
        print(f"  {label:13s} {report['record_occurrences']:>9d} {uniq_latex:>13d} {report['unique_record_keys']:>12d}")

    print()
    print("  source-side occurrence count vs recovery-side occurrence count:")
    for label, _ in GENS:
        if label not in per_gen:
            continue
        report = build_accounting_report(per_gen[label])
        print(f"    {label:13s} recovery occurrences = {report['record_occurrences']:>12d}   "
              f"(source = {len(src_occurrences)})")

    # ---------------------------------------------------------------- 3. what it hid
    print()
    print("=" * 80)
    print("LEVEL 0 — WHAT THE COLLAPSE WAS HIDING")
    print("=" * 80)
    print()
    print("  For each generation, count solvable by OCCURRENCE vs by UNIQUE LATEX.")
    print()
    print(f"  {'generation':13s} {'solvable_occ':>13s} {'solvable_uniq':>14s} {'delta':>8s}")
    print("-" * 80)
    for label, sub in GENS:
        if label not in per_gen:
            continue
        ledger = per_gen[label]

        # Count by occurrence key (correct)
        solvable_keys = _load_solvable_keys(sub)
        sol_occ = len(solvable_keys)

        # Count by unique LaTeX (what the old script did)
        latex_map = _load_latex_by_key(sub)
        sol_uniq = len({latex_map[k] for k in solvable_keys if k in latex_map})

        print(f"  {label:13s} {sol_occ:>13d} {sol_uniq:>14d} {sol_occ - sol_uniq:>+8d}")

    print()
    print("  => If delta != 0, the old 'matched/solvable' figures under-counted")
    print("     because duplicate occurrences were silently dropped.")
    print()


def _load_latex_by_key(dataset_subdir: str) -> dict[str, str]:
    """Load occurrence_key -> latex map for a given dataset."""
    latex_map: dict[str, str] = {}
    d = ROOT / "DATASETS" / dataset_subdir
    if not d.exists():
        return latex_map

    for f in sorted(d.glob("*_recovery.json")):
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
            latex_map[key] = latex

    return latex_map


def _load_solvable_keys(dataset_subdir: str) -> set[str]:
    """Load the set of occurrence keys that are solvable in a given dataset."""
    solvable = set()
    d = ROOT / "DATASETS" / dataset_subdir
    if not d.exists():
        return solvable

    for f in sorted(d.glob("*_recovery.json")):
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
                solvable.add(key)

    return solvable


if __name__ == "__main__":
    main()
