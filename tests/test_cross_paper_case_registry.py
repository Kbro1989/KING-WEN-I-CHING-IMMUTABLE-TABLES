#!/usr/bin/env python3
"""Test suite for Cross-Paper Case Registry v1 validation and integrity."""
import pytest
from pathlib import Path
import json
import hashlib

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
ENGINE_PATH = REPO_ROOT / "scripts" / "delimiter_aware_structural_recovery.py"
EXPECTED_ENGINE_SHA = "8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1"

import sys
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_cross_paper_case_registry import validate_case_registry, sha256_file


def test_registry_file_exists_and_valid():
    assert REGISTRY_PATH.exists(), f"Registry file missing: {REGISTRY_PATH}"
    res = validate_case_registry(REGISTRY_PATH, update_status=False)
    assert res["valid"] is True, f"Registry validation failed: {res['errors']}"
    assert res["papers_count"] == 3
    assert res["cases_count"] == 3
    assert res["status"] in ["VALIDATED", "FROZEN"]


def test_engine_baseline_immutability():
    actual_engine_sha = sha256_file(ENGINE_PATH)
    assert actual_engine_sha == EXPECTED_ENGINE_SHA, "Delimiter recovery engine hash has drifted!"


def test_paper_records_cryptographic_integrity():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)

    for p in reg["papers"]:
        pdf_path = REPO_ROOT / p["pdf_rel_path"]
        assert pdf_path.exists(), f"PDF missing: {pdf_path}"
        actual_sha = sha256_file(pdf_path)
        assert actual_sha == p["pdf_sha256"], f"PDF hash mismatch for {p['paper_id']}"


def test_cluster_gcn_case_safeguards():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)

    c1 = next(c for c in reg["cases"] if c["case_id"] == "CP-001-CLUSTER-GCN-BMATRIX")
    # Verify 7-piece opening and closing
    assert len(c1["delimiter_glyph_inventory"]["opening"]["pieces"]) == 7
    assert len(c1["delimiter_glyph_inventory"]["closing"]["pieces"]) == 7
    # Verify 3 continuation directions
    conts = {cm["role"] for cm in c1["continuation_marker_inventory"]}
    assert "horizontal_ellipsis_cdots" in conts
    assert "vertical_ellipsis_vdots" in conts
    assert "diagonal_ellipsis_ddots" in conts


def test_vilt_case_safeguards():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)

    c2 = next(c for c in reg["cases"] if c["case_id"] == "CP-002-VILT-NESTED-BRACKETS")
    assert c2["gold_ast"]["grid_topology"]["structure_type"] == "sequence_concatenation_vector"
    assert "distinguished from a 2D matrix" in c2["gold_ast"]["grid_topology"]["layout_convention_note"]


def test_linear_probing_case_safeguards():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)

    c3 = next(c for c in reg["cases"] if c["case_id"] == "CP-003-LINEAR-PROBING-NORM")
    assert len(c3["delimiter_glyph_inventory"]["opening"]["pieces"]) == 3
    assert len(c3["delimiter_glyph_inventory"]["closing"]["pieces"]) == 3
    assert c3["delimiter_glyph_inventory"]["trailing_superscript"]["glyph"] == "2"

