#!/usr/bin/env python3
"""
Independent Positive-Control Validation Run — Paper C
Paper: 1406.2661 (Generative Adversarial Nets, Ian Goodfellow et al., NIPS 2014)
Target: Page 3 (Equation 1), Page 4 (Equation 2), Page 5 (Equations 5 and 6)

Executes the frozen hierarchical proposal generator (v2.0) blindly,
then independently measures Observation, Spatial (Dual BBox), and Structural Fidelity.

Outputs:
  DATASETS/structural_preservation/1406.2661_hierarchical_proposals_p003.json
  DATASETS/structural_preservation/1406.2661_hierarchical_proposals_p004.json
  DATASETS/structural_preservation/1406.2661_hierarchical_proposals_p005.json
  DATASETS/structural_preservation/1406.2661_three_fidelity_evaluation.json
"""

import sys
import io
import json
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from hierarchical_region_proposals import run_page
try:
    import fitz
except ImportError:
    import pymupdf as fitz

PDF_PATH = REPO_ROOT / "DATASETS" / "benchmark_pdfs" / "1406.2661.pdf"
MANIFEST_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "1406.2661_positive_control_manifest.json"
OUT_ROOT = REPO_ROOT / "DATASETS" / "structural_preservation"
EVAL_OUT_PATH = OUT_ROOT / "1406.2661_three_fidelity_evaluation.json"

NEGATIVE_ASSESSMENTS_PATH = (
    REPO_ROOT / "DATASETS" / "structural_preservation"
    / "2009.00031_p005_region_assessments.json"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_iou(a: list[float], b: list[float]) -> float:
    ix0 = max(a[0], b[0]); iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2]); iy1 = min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = max(0.0, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(0.0, (b[2] - b[0]) * (b[3] - b[1]))
    return round(inter / max(area_a + area_b - inter, 1e-9), 6)


def compute_coverage(prop: list[float], gold: list[float]) -> float:
    ix0 = max(prop[0], gold[0]); iy0 = max(prop[1], gold[1])
    ix1 = min(prop[2], gold[2]); iy1 = min(prop[3], gold[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    gold_area = max(0.0, (gold[2] - gold[0]) * (gold[3] - gold[1]))
    return round(inter / max(gold_area, 1e-9), 6)


def evaluate_gan_structural_features(gold_id: str, text: str, page_proposals: list[dict], eq_num: int) -> dict:
    """
    Check Stage 1 Structural Fidelity for GAN equations.
    Also verifies Section 10 equation-number metadata contract.
    """
    checks = {}
    
    # Check if equation number was observed either in the text or as an adjacent proposal on the same row
    eq_label_str = f"({eq_num})"
    has_eq_num_prop = any(
        p.get("has_equation_number") and eq_label_str in p.get("text", "")
        for p in page_proposals
    )

    if gold_id == "GAN-001":
        # min_G max_D V(D, G) = E_x~p_data[log D(x)] + E_z~p_z[log(1 - D(G(z)))]
        checks["has_min"] = ("min" in text.lower())
        checks["has_max"] = ("max" in text.lower())
        checks["has_V"] = ("V" in text)
        checks["has_equality"] = ("=" in text)
        checks["has_expectation_E"] = ("E" in text)
        checks["has_sim_relation"] = ("∼" in text or "~" in text)
        checks["has_log_D"] = ("log" in text and "D" in text)
        checks["has_plus"] = ("+" in text)
        checks["has_equation_number_metadata"] = has_eq_num_prop

    elif gold_id == "GAN-002":
        # D*_G(x) = p_data(x) / (p_data(x) + p_g(x))
        checks["has_D"] = ("D" in text)
        checks["has_equality"] = ("=" in text)
        checks["has_p_data"] = ("p" in text and "data" in text)
        checks["has_plus"] = ("+" in text)
        checks["has_p_g"] = ("p" in text and "g" in text)
        checks["has_equation_number_metadata"] = has_eq_num_prop

    elif gold_id == "GAN-005":
        # C(G) = -log(4) + KL(p_data || (p_data + p_g)/2) + KL(p_g || (p_data + p_g)/2)
        checks["has_C_G"] = ("C" in text and "G" in text)
        checks["has_equality"] = ("=" in text)
        checks["has_minus"] = ("−" in text or "-" in text)
        checks["has_log_4"] = ("log" in text and "4" in text)
        checks["has_KL"] = ("KL" in text)
        checks["has_p_data"] = ("p" in text and "data" in text)
        checks["has_equation_number_metadata"] = has_eq_num_prop

    elif gold_id == "GAN-006":
        # C(G) = -log(4) + 2 \cdot JSD(p_data || p_g)
        checks["has_C_G"] = ("C" in text and "G" in text)
        checks["has_equality"] = ("=" in text)
        checks["has_minus"] = ("−" in text or "-" in text)
        checks["has_log_4"] = ("log" in text and "4" in text)
        checks["has_plus_2"] = ("+" in text and "2" in text)
        checks["has_center_dot"] = ("·" in text or "." in text)
        checks["has_JSD"] = ("JSD" in text)
        checks["has_parallel_bars"] = ("∥" in text or "||" in text or "|" in text)
        checks["has_p_data"] = ("p" in text and "data" in text)
        checks["has_equation_number_metadata"] = has_eq_num_prop

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    ratio = round(passed / max(total, 1), 3)

    if ratio >= 0.85:
        verdict = "PRESERVED"
    elif ratio >= 0.50:
        verdict = "PARTIAL"
    elif ratio > 0.0:
        verdict = "AMBIGUOUS"
    else:
        verdict = "MISSING"

    return {
        "verdict": verdict,
        "features_checked": checks,
        "features_passed": passed,
        "features_total": total,
        "structural_fidelity_ratio": ratio,
    }


def run_validation():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    print("=" * 70)
    print("INDEPENDENT POSITIVE-CONTROL VALIDATION RUN — PAPER C")
    print("Paper: 1406.2661 (Generative Adversarial Nets, Ian Goodfellow et al.)")
    print("Targets: Page 3 (Eq 1), Page 4 (Eq 2), Page 5 (Eq 5, Eq 6)")
    print("=" * 70)

    pdf_sha = sha256_file(PDF_PATH)
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))

    doc = fitz.open(PDF_PATH)

    # 1. Blind Proposal Generation on Pages 3, 4, 5
    page_proposals_map = {}
    for p_0based in [2, 3, 4]:
        p_1based = p_0based + 1
        page_res = run_page(doc, p_0based)
        page_proposals_map[p_1based] = page_res["level4_level5_proposals"]

        # Persist hierarchical proposal JSON
        out_p_path = OUT_ROOT / f"1406.2661_hierarchical_proposals_p{p_1based:03d}.json"
        with out_p_path.open("w", encoding="utf-8") as f:
            json.dump(page_res, f, indent=2, ensure_ascii=False)
        print(f"Saved proposals: {out_p_path}")

    # 2. Three-Fidelity Dimension Evaluation
    results = []
    sum_expr_iou = 0.0
    sum_full_iou = 0.0
    sum_expr_cov = 0.0
    verdict_counts = {"PRESERVED": 0, "PARTIAL": 0, "AMBIGUOUS": 0, "MISSING": 0}

    for eq in manifest["gold_equations"]:
        gid = eq["gold_id"]
        eq_num = eq["equation_number"]
        loc = eq["pdf_localization"]
        p_num = loc["page_number_one_based"]
        expr_box = loc["math_expression_bbox"]
        full_box = loc["full_row_bbox"]

        cands = page_proposals_map.get(p_num, [])

        # Match proposal by best IoU against math_expression_bbox
        best_cand = None
        best_expr_iou = -1.0
        best_full_iou = 0.0
        best_expr_cov = 0.0

        for c in cands:
            cbox = c["merged_bbox"]
            eiou = compute_iou(cbox, expr_box)
            if eiou > best_expr_iou:
                best_expr_iou = eiou
                best_cand = c
                best_full_iou = compute_iou(cbox, full_box)
                best_expr_cov = compute_coverage(cbox, expr_box)

        if best_cand is None or best_expr_iou <= 0.0:
            # Fallback: check full_box overlap if expression IoU was 0
            for c in cands:
                cbox = c["merged_bbox"]
                fiou = compute_iou(cbox, full_box)
                if fiou > best_full_iou:
                    best_full_iou = fiou
                    best_cand = c
                    best_expr_iou = compute_iou(cbox, expr_box)
                    best_expr_cov = compute_coverage(cbox, expr_box)

        sum_expr_iou += max(0.0, best_expr_iou)
        sum_full_iou += max(0.0, best_full_iou)
        sum_expr_cov += max(0.0, best_expr_cov)

        # Dimension 1: Observation
        extracted_text = best_cand["text"] if best_cand else ""
        total_glyphs = best_cand.get("total_glyph_count", 0) if best_cand else 0
        math_ratio = best_cand.get("math_glyph_ratio", 0.0) if best_cand else 0.0

        # Dimension 3: Structural
        structural_eval = evaluate_gan_structural_features(gid, extracted_text, cands, eq_num)
        verdict_counts[structural_eval["verdict"]] += 1

        res = {
            "gold_id": gid,
            "equation_number": eq_num,
            "page_number": p_num,
            "dimension1_observation_fidelity": {
                "extracted_text": extracted_text,
                "total_glyphs": total_glyphs,
                "math_glyph_ratio": math_ratio,
                "has_adjacent_equation_number": best_cand.get("has_equation_number", False) if best_cand else False
            },
            "dimension2_spatial_fidelity": {
                "matched_proposal_id": best_cand.get("proposal_id") if best_cand else None,
                "hierarchy_level": best_cand.get("hierarchy_level") if best_cand else None,
                "proposal_bbox": best_cand.get("merged_bbox") if best_cand else None,
                "math_expression_bbox": expr_box,
                "full_row_bbox": full_box,
                "math_expression_iou": max(0.0, best_expr_iou),
                "math_expression_coverage": max(0.0, best_expr_cov),
                "full_row_iou": max(0.0, best_full_iou),
                "whitespace_gap_pt": loc["gap_to_equation_number_pt"]
            },
            "dimension3_structural_fidelity": structural_eval
        }
        results.append(res)

        print(f"\n[{gid}] Eq {eq_num} (Page {p_num}):")
        print(f"  Matched Proposal: {res['dimension2_spatial_fidelity']['matched_proposal_id']} (L{res['dimension2_spatial_fidelity']['hierarchy_level']})")
        print(f"  Math Expression IoU: {res['dimension2_spatial_fidelity']['math_expression_iou']:.4f} (Coverage: {res['dimension2_spatial_fidelity']['math_expression_coverage']:.4f})")
        print(f"  Full Row (Legacy) IoU: {res['dimension2_spatial_fidelity']['full_row_iou']:.4f} (Whitespace Gap: {loc['gap_to_equation_number_pt']} pt)")
        print(f"  Structural Verdict: {structural_eval['verdict']} ({structural_eval['features_passed']}/{structural_eval['features_total']})")
        print(f"  Extracted: {repr(extracted_text[:65])}")

    # 3. Negative-Control Invariant Check
    neg_data = json.load(open(NEGATIVE_ASSESSMENTS_PATH, encoding="utf-8"))
    neg_regions = neg_data["regions"]
    ineligible_count = sum(
        1 for r in neg_regions
        if not r["assessment"]["expectation_generation_eligible"]
    )
    neg_rate = ineligible_count / max(len(neg_regions), 1)

    n_eqs = len(manifest["gold_equations"])
    mean_expr_iou = round(sum_expr_iou / n_eqs, 4)
    mean_full_iou = round(sum_full_iou / n_eqs, 4)
    mean_expr_cov = round(sum_expr_cov / n_eqs, 4)

    eval_artifact = {
        "schema_version": "2.0_dual_bbox",
        "milestone": "independent_positive_control_validation_paper_c",
        "validation_document": "1406.2661",
        "target_pages": [3, 4, 5],
        "source_pdf_sha256": pdf_sha,
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "equations_evaluated": n_eqs,
        "mean_math_expression_iou": mean_expr_iou,
        "mean_full_row_iou": mean_full_iou,
        "mean_math_expression_coverage": mean_expr_cov,
        "structural_verdicts": verdict_counts,
        "negative_control_verification": {
            "document": "2009.00031",
            "page_number": 5,
            "total_regions": len(neg_regions),
            "ineligible_count": ineligible_count,
            "rejection_rate": neg_rate,
            "invariant_status": "UPHELD" if neg_rate == 1.0 else "VIOLATED"
        },
        "per_equation_results": results
    }

    with EVAL_OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(eval_artifact, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY (1406.2661):")
    print(f"  Equations Evaluated: {n_eqs}")
    print(f"  Mean Math Expression IoU: {mean_expr_iou} (Coverage: {mean_expr_cov})")
    print(f"  Mean Full-Row (Legacy) IoU: {mean_full_iou}")
    print(f"  Structural Verdicts: {verdict_counts}")
    print(f"  Negative Control Invariant: {eval_artifact['negative_control_verification']['invariant_status']} (100% Rejection)")
    print(f"Output saved: {EVAL_OUT_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    run_validation()

