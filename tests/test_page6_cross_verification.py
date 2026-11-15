"""Unit tests for Page 6 Independent Cross-Verification (Step H).

Verifies:
  1. Equations 11, 12, 13 on Page 6 are discovered blindly by L1 with IoU >= 0.50.
  2. All three equations pass L5 Gate D4 physical perimeter clearance (border_touch_1px == 0, clearance >= 2.0 pt).
  3. L3 Chroma 2D geometry confirms fraction vinculum on Eq 11.
  4. Cross-verification report is generated with verdict DEMONSTRATED.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from run_page6_cross_verification import run_page6_cross_verification, REPORT_PATH


@pytest.fixture(scope="module")
def page6_report():
    return run_page6_cross_verification()


def test_page6_report_file_and_verdict(page6_report):
    assert REPORT_PATH.exists()
    assert page6_report["verdict"] == "DEMONSTRATED"
    assert page6_report["summary"]["overall_status"] == "PASSED_DEMONSTRATION"
    assert page6_report["summary"]["total_specimens"] == 3


def test_page6_specimens_l1_discovery(page6_report):
    for spec in page6_report["specimens"]:
        l1 = spec["l1_discovery"]
        assert l1["detected"] is True
        assert l1["best_iou"] >= 0.50
        assert l1["candidate_confidence"] >= 0.70


def test_page6_specimens_gate_d4(page6_report):
    for spec in page6_report["specimens"]:
        g4 = spec["l5_gate_d4_perimeter_audit"]
        assert g4["gate_d4_passed"] is True
        assert g4["border_touch_1px"] == 0
        assert g4["clearance_pt"] >= 2.0


def test_page6_eq11_chroma_vinculum(page6_report):
    eq11 = [s for s in page6_report["specimens"] if s["equation_number"] == 11][0]
    chroma = eq11["l3_chroma_geometry"]
    assert chroma["has_vector_match"] is True
    assert chroma["vinculums_detected"] > 0
