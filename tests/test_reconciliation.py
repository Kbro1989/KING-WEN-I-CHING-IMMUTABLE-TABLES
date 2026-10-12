"""
RECONCILIATION REGRESSION TESTS — P4-B/P4-C

Guards the occurrence reconciliation contract:
  - identity is occurrence_key, never LaTeX
  - version resolution uses pinned versions (not 'unpinned')
  - categories are reported separately, never conflated
  - the frozen baseline is never modified
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import SourceOccurrence, occurrence_key


BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"
RECON = ROOT / "DATASETS" / "reconciliation_2026-10-11.json"


def test_baseline_is_immutable():
    """The frozen baseline ledger must still exist and be unmodified."""
    ledger = BASELINE / "occurrences.jsonl"
    assert ledger.exists(), "Frozen baseline ledger must exist"
    lines = [l for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 3409, (
        f"Frozen baseline must still hold 3409 occurrences, found {len(lines)}. "
        "The baseline must NOT be modified to make a gate pass."
    )


def test_occurrence_key_ignores_latex():
    """Occurrence identity must not depend on LaTeX text."""
    a = SourceOccurrence(
        paper_id="x", paper_version="v1", source_locator="math[0]",
        occurrence_index=0, source_hash="", latex="a=b",
    )
    b = SourceOccurrence(
        paper_id="x", paper_version="v1", source_locator="math[0]",
        occurrence_index=0, source_hash="", latex="totally different text",
    )
    assert occurrence_key(a) == occurrence_key(b), (
        "Same (paper, version, locator, index) must yield the same key "
        "regardless of LaTeX content"
    )


def test_occurrence_key_depends_on_version():
    """Version is part of occurrence identity."""
    a = SourceOccurrence(
        paper_id="x", paper_version="v1", source_locator="math[0]",
        occurrence_index=0, source_hash="",
    )
    b = SourceOccurrence(
        paper_id="x", paper_version="v2", source_locator="math[0]",
        occurrence_index=0, source_hash="",
    )
    assert occurrence_key(a) != occurrence_key(b), (
        "Different paper versions must yield different occurrence keys"
    )


def test_reconciliation_report_exists():
    """The reconciliation report must be generated."""
    assert RECON.exists(), (
        "Run scripts/reconcile_occurrences.py to generate the report"
    )


def test_reconciliation_categories_are_separate():
    """source_only and recovery_missing must be distinct fields."""
    if not RECON.exists():
        return
    report = json.loads(RECON.read_text(encoding="utf-8"))
    cats = report["categories"]
    required = [
        "source_only", "baseline_only", "recovery_missing", "recovery_only",
        "content_changed",
    ]
    for field in required:
        assert field in cats, f"Reconciliation must report {field} separately"


def test_reconciliation_explains_every_difference():
    """No unexplained omissions or duplicate identities."""
    if not RECON.exists():
        return
    report = json.loads(RECON.read_text(encoding="utf-8"))
    assert report["unexplained_total"] == 0, (
        f"Unexplained differences: {report['unexplained_total']}"
    )
    assert report["explained"] is True


def test_recovery_covers_source_exactly():
    """recovery_missing and recovery_only must both be zero."""
    if not RECON.exists():
        return
    report = json.loads(RECON.read_text(encoding="utf-8"))
    cats = report["categories"]
    assert cats["recovery_missing"] == 0, (
        f"Recovery must cover every source occurrence, "
        f"{cats['recovery_missing']} missing"
    )
    assert cats["recovery_only"] == 0, (
        f"Recovery must not contain extras, {cats['recovery_only']} found"
    )


def test_no_duplicate_occurrence_keys():
    """No ledger may contain duplicate occurrence identities."""
    if not RECON.exists():
        return
    report = json.loads(RECON.read_text(encoding="utf-8"))
    cats = report["categories"]
    assert cats["duplicate_source_keys"] == 0
    assert cats["duplicate_baseline_keys"] == 0
    assert cats["duplicate_recovery_keys"] == 0


def test_source_only_is_attributable_to_a_paper():
    """Every source_only difference must be attributable to a named paper."""
    if not RECON.exists():
        return
    report = json.loads(RECON.read_text(encoding="utf-8"))
    total = report["categories"]["source_only"]
    if total == 0:
        return
    attributable = sum(
        p["source_minus_baseline"]
        for p in report["per_paper"]
        if p["source_minus_baseline"] > 0
    )
    assert attributable == total, (
        f"source_only={total} but per-paper breakdown sums to {attributable}"
    )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
