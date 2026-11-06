#!/usr/bin/env python3
"""Independent Generalization Evaluator for Rahmani (arXiv:1212.0957, Page 8).

Evaluates the UNCHANGED Delimiter-Aware Structural Recovery Engine against the
registered Rahmani generalization target without modifying any frozen pipeline code.

Validates Criteria 1-7 and Negative Controls NEG_001 - NEG_004.
Outputs:
  DATASETS/structural_preservation/rahmani_1212.0957_generalization_evaluation.json
"""
import sys
import io
import json
import hashlib
from pathlib import Path
import pymupdf

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
TARGET_JSON = REPO_ROOT / "DATASETS" / "structural_preservation" / "rahmani_1212.0957_generalization_target.json"
TARGETED_OCR_JSON = REPO_ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "targeted_ocr" / "targeted_ocr_results.json"
OUT_REPORT = REPO_ROOT / "DATASETS" / "structural_preservation" / "rahmani_1212.0957_generalization_evaluation.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from delimiter_aware_structural_recovery import (
    verify_d1_glyph_extent,
    classify_delimiter_glyph_font_aware,
    associate_delimiter_pairs,
    reconstruct_2d_matrix_grid,
    build_enclosure_completeness,
    verify_d5_translation_fidelity,
    build_d6_provenance,
    sha256_file,
)


def evaluate_generalization():
    print("=== RAHMANI (1212.0957 p8) GENERALIZATION EVALUATION ===")
    with open(TARGET_JSON, "r", encoding="utf-8") as f:
        target = json.load(f)

    pdf_rel = target["source_document"]["pdf_path"]
    pdf_path = REPO_ROOT / pdf_rel
    assert pdf_path.exists(), f"PDF not found: {pdf_path}"

    # Verify PDF hash matches registered target
    actual_pdf_sha = sha256_file(pdf_path)
    expected_pdf_sha = target["source_document"]["pdf_sha256"]
    assert actual_pdf_sha == expected_pdf_sha, f"PDF SHA mismatch: {actual_pdf_sha} vs {expected_pdf_sha}"

    doc = pymupdf.open(str(pdf_path))
    page = doc[target["source_document"]["page_0based"]]

    # Load visual candidates from targeted_ocr
    with open(TARGETED_OCR_JSON, "r", encoding="utf-8") as f:
        tdata = json.load(f)

    p8_regions = tdata["results"]["1212.0957_p8"]["regions"]
    scale = 0.25  # 4x render to 1x PDF pt
    candidates = []

    for idx, r in enumerate(p8_regions):
        bbox = r["bbox"]
        core_rect = pymupdf.Rect(
            bbox[0] * scale,
            bbox[1] * scale,
            (bbox[0] + bbox[2]) * scale,
            (bbox[1] + bbox[3]) * scale,
        )
        delim_id = classify_delimiter_glyph_font_aware(page, core_rect)
        candidates.append({
            "index": idx,
            "region_id": r["region_index"],
            "rect": core_rect,
            "aspect_ratio": r["aspect_ratio"],
            "type": r["type"],
            "delimiter_id": delim_id,
        })

    # --- Criterion 1: Independent Detection ---
    c1_passed = (len(candidates) >= 2) and all(
        c["delimiter_id"]["kind"] == "parenthesis" for c in candidates
    )
    open_cand = next((c for c in candidates if c["delimiter_id"]["is_opening"] is True), None)
    close_cand = next((c for c in candidates if c["delimiter_id"]["is_opening"] is False), None)
    c1_passed = c1_passed and (open_cand is not None) and (close_cand is not None)

    # --- Criterion 2: Correct Pairing ---
    pairs, unpaired = associate_delimiter_pairs(candidates, page.rect.width, page.rect.height)
    c2_passed = (len(pairs) == 1) and (pairs[0]["pair_score"] >= 0.90)
    c2_score = pairs[0]["pair_score"] if pairs else 0.0

    pair = pairs[0] if pairs else None
    encl_rect, meta = build_enclosure_completeness(page, pair) if pair else (None, {})
    grid = meta.get("grid", {})
    rows = grid.get("rows", [])

    # --- Criterion 3: Column and Row Ordering ---
    ref_rows = target["matrix_structural_specification"]["row_definitions"]
    c3_details = []
    c3_passed = True
    if len(rows) >= 6:
        for r_idx in range(6):
            expected_entries = ref_rows[r_idx]["entries"]
            actual_row = rows[r_idx]
            # normalize minus signs: U+2212 -> '-'
            norm_actual = [tok.replace("\u2212", "-") for tok in actual_row]
            norm_expected = [tok.replace("\u2212", "-") for tok in expected_entries]
            # check that all expected entries appear in order
            matched = True
            pos = 0
            for exp in norm_expected:
                try:
                    next_pos = norm_actual.index(exp, pos)
                    pos = next_pos + 1
                except ValueError:
                    matched = False
                    break
            c3_details.append({"row": r_idx, "matched": matched, "actual": norm_actual, "expected": norm_expected})
            if not matched:
                c3_passed = False
    else:
        c3_passed = False

    # --- Criterion 4: Ellipsis Preservation ---
    # Horizontal ellipsis in Row 0
    row0_tokens = rows[0] if len(rows) > 0 else []
    h_dots_present = any("·" in tok or "..." in tok for tok in row0_tokens)

    # Vertical continuation in Row 6
    row6_tokens = rows[6] if len(rows) > 6 else []
    v_dots_present = any("." in tok or "·" in tok or "⋮" in tok for tok in row6_tokens)
    c4_passed = h_dots_present and v_dots_present

    # --- Criterion 5: Boundary Isolation ---
    # Ensure '= e^z / (1+z)' is strictly outside the enclosure
    encl_y1 = encl_rect.y1 if encl_rect else 999.0
    trailing_y0 = target["trailing_external_expression"]["closest_inline_math_bbox"][1]
    # Enclosure must not extend to or past the trailing equation line
    absorbed_trailing = any("ez" in tok or "1+z" in tok for tok in grid.get("raw_tokens", []))
    c5_passed = (encl_y1 <= trailing_y0 + 2.0) and not absorbed_trailing

    # --- Criterion 6: AST Preservation ---
    d5_check = verify_d5_translation_fidelity(
        grid,
        pair["opening_candidate"]["delimiter_id"] if pair else {},
        expected_rows=7,
    ) if pair else {"passed": False, "target_latex_environment": "unknown"}
    c6_passed = d5_check["passed"] and (d5_check["target_latex_environment"] == "pmatrix") and (grid.get("row_count") == 7)

    # --- Criterion 7: Mathematical Fidelity ---
    c7_passed = c3_passed and c4_passed and (grid.get("row_count") == 7)

    # --- Negative Controls ---
    # NEG_001: Mismatched Delimiters (paren + bracket)
    c_bracket = {
        "index": 99,
        "rect": pymupdf.Rect(400, 382, 406, 480),
        "delimiter_id": {"kind": "bracket", "is_opening": False},
    }
    pairs_neg1, _ = associate_delimiter_pairs([open_cand, c_bracket], page.rect.width, page.rect.height)
    neg_001_passed = len(pairs_neg1) == 0  # must be rejected

    # NEG_002: Missing Closing Delimiter (lone opening)
    pairs_neg2, unp_neg2 = associate_delimiter_pairs([open_cand], page.rect.width, page.rect.height)
    neg_002_passed = (len(pairs_neg2) == 0) and (len(unp_neg2) == 1)

    # NEG_003: Adjacent Matrix Cross-Association
    m1_open = {"index": 0, "rect": pymupdf.Rect(100, 100, 105, 200), "delimiter_id": {"kind": "parenthesis", "is_opening": True}}
    m1_close = {"index": 1, "rect": pymupdf.Rect(200, 100, 205, 200), "delimiter_id": {"kind": "parenthesis", "is_opening": False}}
    m2_open = {"index": 2, "rect": pymupdf.Rect(300, 100, 305, 200), "delimiter_id": {"kind": "parenthesis", "is_opening": True}}
    m2_close = {"index": 3, "rect": pymupdf.Rect(400, 100, 405, 200), "delimiter_id": {"kind": "parenthesis", "is_opening": False}}
    pairs_neg3, _ = associate_delimiter_pairs([m1_open, m1_close, m2_open, m2_close], 600, 800)
    neg_003_passed = (len(pairs_neg3) == 2) and (pairs_neg3[0]["closing_candidate"]["index"] == 1)

    # NEG_004: Tall Non-Math Graphic (generic vertical line without CMEX / math font)
    fake_rule = pymupdf.Rect(50, 100, 52, 220)
    delim_rule = classify_delimiter_glyph_font_aware(page, fake_rule)
    neg_004_passed = delim_rule["kind"] == "unknown" or delim_rule["confidence"] < 0.5

    criteria_summary = {
        "Criterion_1_IndependentDetection": {
            "status": "PASS" if c1_passed else "FAIL",
            "candidates_found": len(candidates),
            "opening_detected": open_cand is not None,
            "closing_detected": close_cand is not None,
        },
        "Criterion_2_CorrectPairing": {
            "status": "PASS" if c2_passed else "FAIL",
            "pairs_formed": len(pairs),
            "pair_score": c2_score,
        },
        "Criterion_3_ColumnRowOrdering": {
            "status": "PASS" if c3_passed else "FAIL",
            "rows_extracted": len(rows),
            "row_evaluations": c3_details,
        },
        "Criterion_4_EllipsisPreservation": {
            "status": "PASS" if c4_passed else "FAIL",
            "horizontal_ellipsis_row0": h_dots_present,
            "vertical_continuation_row6": v_dots_present,
        },
        "Criterion_5_BoundaryIsolation": {
            "status": "PASS" if c5_passed else "FAIL",
            "enclosure_bottom_y": round(encl_y1, 2) if encl_rect else None,
            "trailing_expression_y0": trailing_y0,
            "absorbed_trailing_tokens": absorbed_trailing,
        },
        "Criterion_6_ASTPreservation": {
            "status": "PASS" if c6_passed else "FAIL",
            "target_latex_environment": d5_check["target_latex_environment"],
            "effective_row_count": grid.get("row_count"),
            "effective_col_count": 6,
        },
        "Criterion_7_MathematicalFidelity": {
            "status": "PASS" if c7_passed else "FAIL",
            "overall_fidelity": "PASS" if c7_passed else "FAIL",
        },
    }

    negative_controls_summary = {
        "NEG_001_MismatchedDelimiters": {"status": "PASS" if neg_001_passed else "FAIL", "rejected": neg_001_passed},
        "NEG_002_MissingClosingDelimiter": {"status": "PASS" if neg_002_passed else "FAIL", "rejected": neg_002_passed},
        "NEG_003_AdjacentMatrixCrossAssociation": {"status": "PASS" if neg_003_passed else "FAIL", "rejected_cross_pairing": neg_003_passed},
        "NEG_004_TallNonMathGraphic": {"status": "PASS" if neg_004_passed else "FAIL", "rejected_non_math": neg_004_passed},
    }

    all_criteria_pass = all(v["status"] == "PASS" for v in criteria_summary.values())
    all_neg_pass = all(v["status"] == "PASS" for v in negative_controls_summary.values())
    overall_generalization_verdict = "PASSED_UNMODIFIED" if (all_criteria_pass and all_neg_pass) else "GENERALIZATION_FAILED"

    evaluation_report = {
        "report_title": "Independent Generalization Evaluation: Rahmani (arXiv:1212.0957 Page 8)",
        "target_identifier": target["target_identifier"],
        "pipeline_state": "UNMODIFIED_BASELINE",
        "overall_generalization_verdict": overall_generalization_verdict,
        "criteria_evaluations": criteria_summary,
        "negative_controls": negative_controls_summary,
        "recovered_matrix": {
            "prefix": meta.get("prefix_text"),
            "enclosure_bbox_pt": meta.get("enclosure_rect"),
            "row_count": grid.get("row_count"),
            "token_count": grid.get("token_count"),
            "rows": rows,
        },
        "provenance": {
            "pdf_sha256": actual_pdf_sha,
            "page_1based": 8,
            "engine_file": "scripts/delimiter_aware_structural_recovery.py",
        },
    }

    OUT_REPORT.write_text(json.dumps(evaluation_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Evaluation report written -> {OUT_REPORT}")
    print(f"Overall Generalization Verdict: {overall_generalization_verdict}")
    for k, v in criteria_summary.items():
        print(f"  [{v['status']}] {k}")
    print("Negative Controls:")
    for k, v in negative_controls_summary.items():
        print(f"  [{v['status']}] {k}")

    doc.close()
    return evaluation_report


if __name__ == "__main__":
    evaluate_generalization()

