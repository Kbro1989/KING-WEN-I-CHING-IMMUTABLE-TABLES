"""
Focused regression test for math_contract StructuralStatus validation (P0 fix).

Verifies that validate_record() accepts every declared StructuralStatus value
and rejects unknown ones. This is the canonical contract check that prevents
the type/validator disagreement from regressing.

Run:  PYTHONPATH=. python -m pytest tests/test_math_contract_status.py -v
"""

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is on the path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from math_contract import (
    RecoveryRecord,
    SourceOccurrence,
    StructuralStatus,
    validate_record,
)
from typing import get_args


def make_record(status: str) -> RecoveryRecord:
    """Build a minimally valid RecoveryRecord with the given structural_status."""
    source = SourceOccurrence(
        paper_id="test-paper",
        paper_version="v1",
        source_locator="math[0]",
        occurrence_index=0,
        source_hash="test-hash",
    )
    return RecoveryRecord(
        source=source,
        parse_status="complete",
        structural_status=status,  # type: ignore[arg-type]
    )


class TestStructuralStatusValidation:
    """Every declared StructuralStatus value must be accepted by validate_record()."""

    def test_all_declared_structural_statuses_are_accepted(self):
        """The canonical set from get_args(StructuralStatus) must all pass."""
        declared = get_args(StructuralStatus)
        assert "partial" in declared, "partial must be a declared status"
        for status in declared:
            violations = validate_record(make_record(status))
            structural_violations = [
                v for v in violations if "Invalid structural_status" in v
            ]
            assert not structural_violations, (
                f"status '{status}' should be accepted but got: {structural_violations}"
            )

    def test_partial_status_is_accepted(self):
        """The previously-rejected 'partial' status must now be accepted."""
        violations = validate_record(make_record("partial"))
        assert not any(
            "Invalid structural_status" in v for v in violations
        ), f"partial should be accepted: {violations}"

    def test_unknown_structural_status_is_rejected(self):
        """An invented status string must be rejected."""
        violations = validate_record(make_record("invented-status"))
        assert any(
            "Invalid structural_status" in v for v in violations
        ), "unknown status should be rejected"

    def test_validator_matches_canonical_type_definition(self):
        """validate_record's accepted set must equal get_args(StructuralStatus)."""
        declared = get_args(StructuralStatus)
        assert "partial" in declared
        assert len(declared) == 6
