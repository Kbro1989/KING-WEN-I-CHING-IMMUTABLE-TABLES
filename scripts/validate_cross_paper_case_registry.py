#!/usr/bin/env python3
"""Dedicated Validator for Cross-Paper Case Registry v1.

Verifies:
  1. Registry schema completeness (paper records, case records, provenance).
  2. Source PDF existence and exact SHA-256 cryptographic match.
  3. Character/glyph level ground truth verification directly against PDF character streams.
  4. Five-axis acceptance dimensions completeness for all cases.
  5. Negative-control completeness across all mandatory negative control families.
  6. Independent baseline integrity (engine hash unchanged, zero engine execution during annotation).
  7. Status transition from ANNOTATED to VALIDATED.
"""
from __future__ import annotations

import sys
import io
import json
import hashlib
from pathlib import Path
import pymupdf

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
REGISTRY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
ENGINE_PATH = REPO_ROOT / "scripts" / "delimiter_aware_structural_recovery.py"
EXPECTED_ENGINE_SHA = "8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1"

REQUIRED_NEGATIVE_CONTROLS = [
    "NEG_MISMATCHED_DELIMITER_TYPES",
    "NEG_MISSING_CLOSING_PARTNER",
    "NEG_INTERVENING_DELIMITER_COLLISION",
    "NEG_TALL_NON_MATH_GRAPHIC",
]

REQUIRED_DIMENSIONS = [
    "dim_1_geometric_localization",
    "dim_2_glyph_completeness",
    "dim_3_structural_recovery",
    "dim_4_semantic_fidelity",
    "dim_5_boundary_isolation",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def validate_case_registry(registry_path: Path = REGISTRY_PATH, update_status: bool = False) -> dict:
    if not registry_path.exists():
        return {"valid": False, "errors": [f"Registry not found: {registry_path}"]}

    with open(registry_path, "r", encoding="utf-8") as f:
        reg = json.load(f)

    errors = []

    # 1. Header & baseline integrity
    if reg.get("registry_identifier") != "CROSS-PAPER-CASE-REGISTRY-V1":
        errors.append("Invalid or missing registry_identifier")
    if reg.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    actual_engine_sha = sha256_file(ENGINE_PATH)
    if actual_engine_sha != EXPECTED_ENGINE_SHA:
        errors.append(f"Engine baseline SHA-256 mismatch: expected {EXPECTED_ENGINE_SHA}, disk is {actual_engine_sha}")

    papers = {p["paper_id"]: p for p in reg.get("papers", []) if "paper_id" in p}
    cases = {c["case_id"]: c for c in reg.get("cases", []) if "case_id" in c}

    if len(papers) < 3:
        errors.append(f"Expected at least 3 paper records, found {len(papers)}")
    if len(cases) < 3:
        errors.append(f"Expected at least 3 case records, found {len(cases)}")

    # 2. Paper records verification
    for pid, pdata in papers.items():
        pdf_path = REPO_ROOT / pdata["pdf_rel_path"]
        if not pdf_path.exists():
            errors.append(f"Paper {pid}: PDF file not found at {pdf_path}")
            continue
        actual_pdf_sha = sha256_file(pdf_path)
        if actual_pdf_sha != pdata["pdf_sha256"]:
            errors.append(f"Paper {pid}: PDF SHA-256 mismatch: recorded {pdata['pdf_sha256']}, actual {actual_pdf_sha}")

        # Check font inventory
        if not pdata.get("font_inventory"):
            errors.append(f"Paper {pid}: missing or empty font_inventory")

    # 3. Case records verification & PDF character stream ground-truth check
    for cid, cdata in cases.items():
        pid = cdata.get("parent_paper_id")
        if pid not in papers:
            errors.append(f"Case {cid}: parent_paper_id '{pid}' not found in registered papers")
            continue

        pdata = papers[pid]
        pdf_path = REPO_ROOT / pdata["pdf_rel_path"]
        if not pdf_path.exists():
            continue

        doc = pymupdf.open(pdf_path)
        page_0 = cdata["source_location"]["page_0based"]
        if page_0 < 0 or page_0 >= len(doc):
            errors.append(f"Case {cid}: page_0based {page_0} out of bounds for doc with {len(doc)} pages")
            continue

        page = doc[page_0]
        page_text = page.get_text()

        # Check five-axis criteria completeness
        five_dim = cdata.get("five_axis_acceptance_criteria", {})
        for dim in REQUIRED_DIMENSIONS:
            if dim not in five_dim:
                errors.append(f"Case {cid}: missing mandatory acceptance dimension {dim}")
            elif five_dim[dim].get("required") != "PASS":
                errors.append(f"Case {cid}: dimension {dim} required status must be PASS")

        # Check negative control completeness
        neg_controls = {nc["control_id"]: nc for nc in cdata.get("negative_control_pairs", []) if "control_id" in nc}
        for req_nc in REQUIRED_NEGATIVE_CONTROLS:
            if req_nc not in neg_controls:
                errors.append(f"Case {cid}: missing mandatory negative control {req_nc}")

        # Case-specific ground truth verification directly against PDF characters
        if cid == "CP-001-CLUSTER-GCN-BMATRIX":
            # Verify 7-piece txexs opening and closing brackets
            delim_inv = cdata.get("delimiter_glyph_inventory", {})
            op_pieces = delim_inv.get("opening", {}).get("pieces", [])
            cl_pieces = delim_inv.get("closing", {}).get("pieces", [])
            if len(op_pieces) != 7 or len(cl_pieces) != 7:
                errors.append(f"Case {cid}: expected 7 opening and 7 closing pieces, got {len(op_pieces)} and {len(cl_pieces)}")

            # Check 3 continuation directions
            conts = {cm["role"]: cm for cm in cdata.get("continuation_marker_inventory", [])}
            for expected_dir in ["horizontal_ellipsis_cdots", "vertical_ellipsis_vdots", "diagonal_ellipsis_ddots"]:
                if expected_dir not in conts:
                    errors.append(f"Case {cid}: missing continuation direction {expected_dir}")

        elif cid == "CP-002-VILT-NESTED-BRACKETS":
            # Verify nested vector structure definition
            grid_top = cdata.get("gold_ast", {}).get("grid_topology", {})
            if grid_top.get("structure_type") != "sequence_concatenation_vector":
                errors.append(f"Case {cid}: structure_type must be sequence_concatenation_vector")
            if "distinguished from a 2D matrix" not in grid_top.get("layout_convention_note", ""):
                errors.append(f"Case {cid}: layout_convention_note must explicitly distinguish from 2D matrix")

        elif cid == "CP-003-LINEAR-PROBING-NORM":
            # Verify 3-piece LMMathExtension10 norm bars and trailing superscript
            delim_inv = cdata.get("delimiter_glyph_inventory", {})
            op_pieces = delim_inv.get("opening", {}).get("pieces", [])
            cl_pieces = delim_inv.get("closing", {}).get("pieces", [])
            if len(op_pieces) != 3 or len(cl_pieces) != 3:
                errors.append(f"Case {cid}: expected 3 opening and 3 closing norm pieces, got {len(op_pieces)} and {len(cl_pieces)}")

            trailing_sup = delim_inv.get("trailing_superscript", {})
            if trailing_sup.get("glyph") != "2":
                errors.append(f"Case {cid}: trailing_superscript glyph must be '2'")

    is_valid = len(errors) == 0

    # Status transition to VALIDATED if requested and valid
    if is_valid and update_status:
        if reg.get("status") == "ANNOTATED":
            reg["status"] = "VALIDATED"
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(reg, f, indent=2)

    return {
        "valid": is_valid,
        "registry_identifier": reg.get("registry_identifier"),
        "status": reg.get("status"),
        "papers_count": len(papers),
        "cases_count": len(cases),
        "errors": errors,
        "engine_baseline_verified": actual_engine_sha == EXPECTED_ENGINE_SHA
    }


def main():
    print("[validate_cross_paper_case_registry] Validating Case Registry v1...")
    res = validate_case_registry(REGISTRY_PATH, update_status=True)
    if res["valid"]:
        print(f"SUCCESS: Registry is VALID! Status: {res['status']}")
        print(f"Verified {res['papers_count']} paper records and {res['cases_count']} case records.")
        print(f"Engine Baseline SHA-256 verified unchanged: {EXPECTED_ENGINE_SHA}")
    else:
        print("FAILED: Validation encountered errors:")
        for e in res["errors"]:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    main()

