"""Tests for the Independent Glyph-Source Boundary Audit.

Verifies:
  1. The audit report exists and is valid JSON.
  2. All 4 benchmark targets are evaluated against their source PDF vector glyphs.
  3. CP-002 right-side shaving is verified as whitespace removal (not glyph loss).
  4. Vector glyph envelope to zero-margin crop clearance metrics are captured.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
AUDIT_JSON = ROOT / "DATASETS" / "structural_preservation" / "glyph_source_boundary_audit_results.json"


@pytest.fixture(scope="module")
def audit_data():
    assert AUDIT_JSON.exists(), f"Audit file missing: {AUDIT_JSON}"
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_audit_structure(audit_data):
    assert audit_data["audit_identifier"] == "GLYPH-SOURCE-BOUNDARY-AUDIT-V1"
    assert audit_data["total_targets"] == 4
    assert len(audit_data["targets"]) == 4


def test_cp002_whitespace_reduction_distinction(audit_data):
    cp002 = next((t for t in audit_data["targets"] if t["target_id"] == "CP-002-VILT-NESTED-BRACKETS"), None)
    assert cp002 is not None
    # CP-002 shaved ~89 px at 2x (~44.5 pt) of empty right whitespace
    ws_analysis = cp002["whitespace_reduction_analysis"]
    assert ws_analysis["right_shaved_px"] == 89
    assert ws_analysis["right_shaved_pt_equivalent"] == 44.5
    # The rightmost glyph (closing bracket ']') ends well before the candidate edge
    assert ws_analysis["distance_from_rightmost_glyph_to_candidate_edge_pt"] > 40.0


def test_vector_glyph_envelopes_present(audit_data):
    for t in audit_data["targets"]:
        assert t["glyph_count"] > 0
        envelope = t["source_vector_envelope_pt"]
        assert len(envelope) == 4
        assert envelope[0] < envelope[2]  # x0 < x1
        assert envelope[1] < envelope[3]  # y0 < y1
        assert "clearances_to_vector_envelope_pt" in t

