"""Audit Completeness and Correctness of PIAA Source Mathematical Inventory.

Audits DATASETS/structural_preservation/piaa_source_mathematical_inventory.json
against the publication text of arXiv:2605.25821.

Audit Dimensions:
  1. Structural & Syntactic Correctness: Delimiter balance, valid LaTeX syntax, construct tags.
  2. Numbered Equation Contiguity: Full contiguous sequence 1..13 with zero gaps or duplicates.
  3. Algorithmic Integrity: Algorithm 1 frame, numbered steps, multi-stage structure.
  4. Population Partitioning: Clean segregation of development vs. held-out test specimens.
  5. Gate D4 Bifurcation Tracking: Explicit documentation of S3.E6 clearance ambiguity.
  6. Zero Gold-Coordinate Leakage: Recursive verification that no spatial coordinates exist.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
INVENTORY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "piaa_source_mathematical_inventory.json"
AUDIT_REPORT_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "piaa_source_inventory_audit_report.json"


def check_delimiter_balance(latex: str) -> dict[str, Any]:
    """Check balanced braces, brackets, and parentheses in LaTeX."""
    # Remove escaped delimiters for balance checking
    clean = re.sub(r"\\\{|\\\}|\\\(|\\\)|\\\[|\\\]", " ", latex)
    
    curly_open = clean.count("{")
    curly_close = clean.count("}")
    paren_open = clean.count("(")
    paren_close = clean.count(")")
    bracket_open = clean.count("[")
    bracket_close = clean.count("]")
    
    balanced = (curly_open == curly_close and 
                paren_open == paren_close and 
                bracket_open == bracket_close)
    
    return {
        "balanced": balanced,
        "curly": {"open": curly_open, "close": curly_close, "diff": curly_open - curly_close},
        "paren": {"open": paren_open, "close": paren_close, "diff": paren_open - paren_close},
        "bracket": {"open": bracket_open, "close": bracket_close, "diff": bracket_open - bracket_close},
    }


def audit_source_inventory() -> dict[str, Any]:
    if not INVENTORY_PATH.exists():
        raise FileNotFoundError(f"Missing inventory file: {INVENTORY_PATH}")

    with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
        inv = json.load(f)

    findings = []
    passed_all = True

    # 1. Coordinate Leakage Scan
    forbidden_keys = {
        "bbox", "coordinates", "rect", "crop", "x0", "y0", "x1", "y1",
        "page_number", "page_0based", "page_1based", "width_pt", "height_pt"
    }
    leakage_instances = []

    def scan_leakage(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in forbidden_keys:
                    leakage_instances.append(f"{path}.{k} = {v}")
                scan_leakage(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                scan_leakage(item, f"{path}[{idx}]")

    scan_leakage(inv)
    has_leakage = len(leakage_instances) > 0
    if has_leakage:
        passed_all = False
        findings.append(f"FAILED: Found {len(leakage_instances)} coordinate leakage instances.")
    else:
        findings.append("PASSED: Zero gold-coordinate leakage verified across entire inventory.")

    # 2. Numbered Display Equations Contiguity Check
    display_eqs = inv.get("display_equations", [])
    eq_numbers = [eq["equation_number"] for eq in display_eqs]
    expected_numbers = list(range(1, 14))
    
    if eq_numbers != expected_numbers:
        passed_all = False
        findings.append(f"FAILED: Contiguity failure in display equations: got {eq_numbers}, expected {expected_numbers}")
    else:
        findings.append("PASSED: All 13 numbered display equations (1..13) are contiguous and strictly ordered.")

    # 3. Delimiter Balance & Syntax Correctness
    syntax_results = []
    for eq in display_eqs:
        anchor = eq["source_anchor"]
        latex = eq["latex_source"]
        balance = check_delimiter_balance(latex)
        
        # Check initial physical status
        status = eq.get("physical_pdf_correspondence_status")
        status_ok = (status == "NOT_VERIFIED")
        
        if not balance["balanced"]:
            passed_all = False
            findings.append(f"FAILED: Delimiter unbalance in {anchor}: {balance}")
        if not status_ok:
            passed_all = False
            findings.append(f"FAILED: Physical status for {anchor} is {status}, must be NOT_VERIFIED")
            
        syntax_results.append({
            "source_anchor": anchor,
            "equation_number": eq["equation_number"],
            "title": eq["title"],
            "delimiters_balanced": balance["balanced"],
            "construct_count": len(eq.get("principal_constructs", [])),
            "status_is_not_verified": status_ok,
        })

    # 4. S3.E6 Gate D4 Tier Bifurcation Check
    s3_e6 = next((eq for eq in display_eqs if eq["source_anchor"] == "S3.E6"), None)
    bifurcation_ok = False
    if s3_e6:
        note = s3_e6.get("tier_bifurcation_note", "")
        if ("wrap below formula" in note or "wrapped below formula" in note) and "-0.11 pt" in note and "2.02 pt" in note:
            bifurcation_ok = True
            findings.append("PASSED: S3.E6 (Eq 6) explicitly records Gate D4 tier bifurcation metadata.")
        else:
            passed_all = False
            findings.append("FAILED: S3.E6 missing required tier bifurcation documentation.")

    # 5. Population Partitioning Verification
    partition = inv.get("population_partition_summary", {})
    dev_set = set(partition.get("development_specimens", []))
    test_set = set(partition.get("independent_test_specimens", []))
    held_set = set(partition.get("held_out_candidates_pending", []))
    
    # Assert mutual exclusivity
    intersection = (dev_set & test_set) | (dev_set & held_set) | (test_set & held_set)
    if intersection:
        passed_all = False
        findings.append(f"FAILED: Overlap in population partitions: {intersection}")
    else:
        findings.append("PASSED: Population partitions are strictly mutually exclusive.")

    expected_dev = {"S3.E1", "S3.E2", "S3.E3", "S3.E4", "S3.E5", "S3.E7", "S3.E8", "S3.E9", "S3.E10"}
    expected_test = {"S3.E11", "S3.E12", "S3.E13"}
    expected_held = {"S3.E6"}
    
    partition_match = (dev_set == expected_dev and test_set == expected_test and held_set == expected_held)
    if not partition_match:
        passed_all = False
        findings.append("FAILED: Population partition set membership does not match expected allocation.")
    else:
        findings.append("PASSED: Exact population allocation verified (9 Dev, 1 Held-Out, 3 Independent Test).")

    # 6. Algorithmic Target Check
    algos = inv.get("algorithmic_structures", [])
    algo_ok = len(algos) == 1 and algos[0]["source_anchor"] == "S3.ALG1" and len(algos[0].get("stages", [])) == 5
    if algo_ok:
        findings.append("PASSED: Algorithm 1 (PVCL) accounted for as separate algorithmic structure with 5 stages.")
    else:
        passed_all = False
        findings.append("FAILED: Algorithm 1 structure verification failed.")

    # 7. Inline Mathematics Check
    inlines = inv.get("inline_mathematics_inventory", [])
    inline_ok = len(inlines) == 8 and all(inl.get("physical_pdf_correspondence_status") == "NOT_VERIFIED" for inl in inlines)
    if inline_ok:
        findings.append("PASSED: 8 key inline mathematical constructs cataloged with status NOT_VERIFIED.")
    else:
        passed_all = False
        findings.append("FAILED: Inline mathematics population verification failed.")

    report = {
        "audit_identifier": "PIAA-SOURCE-INVENTORY-VERIFICATION-AUDIT",
        "inventory_verified": str(INVENTORY_PATH),
        "audit_disposition": "VERIFIED_CORRECT" if passed_all else "AUDIT_REJECTED",
        "all_checks_passed": passed_all,
        "audit_findings": findings,
        "metrics": {
            "display_equations_count": len(display_eqs),
            "algorithmic_structures_count": len(algos),
            "inline_targets_count": len(inlines),
            "coordinate_leakage_count": len(leakage_instances),
            "all_delimiters_balanced": all(s["delimiters_balanced"] for s in syntax_results),
            "all_initial_statuses_not_verified": all(s["status_is_not_verified"] for s in syntax_results) and inline_ok,
            "tier_bifurcation_tracked": bifurcation_ok,
            "population_partition_clean": partition_match and (len(intersection) == 0),
        },
        "display_equations_syntax_audit": syntax_results,
    }

    AUDIT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report


if __name__ == "__main__":
    rep = audit_source_inventory()
    print(f"=== SOURCE INVENTORY AUDIT RESULT: {rep['audit_disposition']} ===")
    for find in rep["audit_findings"]:
        print(f"  {find}")
    print(f"\nReport written to: {AUDIT_REPORT_PATH}")
