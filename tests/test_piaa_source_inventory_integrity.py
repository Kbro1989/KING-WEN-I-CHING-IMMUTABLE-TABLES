"""Unit Tests: PIAA Source Mathematical Inventory Verification.

Ensures that DATASETS/structural_preservation/piaa_source_mathematical_inventory.json
meets all binding integrity, completeness, and non-leakage criteria.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest
from scripts.audit_piaa_source_inventory import audit_source_inventory, check_delimiter_balance

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "piaa_source_mathematical_inventory.json"


def test_source_inventory_file_exists():
    assert INVENTORY_PATH.exists(), f"Source inventory file missing: {INVENTORY_PATH}"


def test_source_inventory_audit_all_passed():
    report = audit_source_inventory()
    assert report["all_checks_passed"] is True, f"Audit failed: {report['audit_findings']}"
    assert report["audit_disposition"] == "VERIFIED_CORRECT"


def test_zero_coordinate_leakage():
    report = audit_source_inventory()
    assert report["metrics"]["coordinate_leakage_count"] == 0


def test_display_equations_contiguity_and_count():
    report = audit_source_inventory()
    assert report["metrics"]["display_equations_count"] == 13
    assert report["metrics"]["all_delimiters_balanced"] is True


def test_initial_status_is_strictly_not_verified():
    report = audit_source_inventory()
    assert report["metrics"]["all_initial_statuses_not_verified"] is True


def test_s3_e6_tier_bifurcation_tracked():
    report = audit_source_inventory()
    assert report["metrics"]["tier_bifurcation_tracked"] is True


def test_population_partitions_mutually_exclusive():
    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        inv = json.load(f)
    part = inv["population_partition_summary"]
    dev = set(part["development_specimens"])
    test = set(part["independent_test_specimens"])
    held = set(part["held_out_candidates_pending"])
    
    assert len(dev & test) == 0
    assert len(dev & held) == 0
    assert len(test & held) == 0
    assert len(dev | test | held) == 13

