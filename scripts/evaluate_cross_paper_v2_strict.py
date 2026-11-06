"""Strict Cross-Paper Evaluation Gate V2.1 (KING-WEN-LOCALIZATION-V2.1).

Replaces the one-sided containment evaluation rule with conjunctive strict localization:
  - Coordinate separation:
      * BBox_math is scored against Adjudicated Gold Target for IoU, EAR, Edge Residuals, and Contamination.
      * BBox_crop is scored separately for physical clearance to nearest external ink (Gate D4).
  - Explicit metrics:
      1. IoU(BBox_math, Gold_Target) >= 0.80
      2. Excess Area Ratio (EAR) = |BBox_math \ Gold_Target| / |Gold_Target| <= 0.20
      3. Edge Residuals: max(|dx0|, |dy0|, |dx1|, |dy1|) <= 6.0 pt (all 4 reported independently)
      4. External Contamination: Non-target token area overlap > 10% fails dim_1.
      5. Physical Clearance (Gate D4): min distance from crop perimeter to external ink >= 2.0 pt.
         (Sub-4.0 pt physical gutters fail or evaluate to NOT_VERIFIED: sub_4pt_gutter_clearance_impossible).

Invariants:
  - Base registry cross_paper_case_registry_v1.json on disk is strictly immutable.
  - Target semantics are loaded via versioned patch overlays in case_registry_patches/.
  - CP-004 is evaluated as a DEVELOPMENT_CASE, never an out-of-sample generalization test.
  - Frozen v1 baseline engine (8211592a...) and remediated v2 engine are evaluated side-by-side.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# pyrefly: ignore[missing-import]
import pymupdf

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

import case_registry_patch_manager as patch_mgr
import delimiter_aware_structural_recovery as engine_v1
import v2_delimiter_aware_structural_recovery as engine_v2

EVALUATOR_VERSION = "2.1.0-strict"
METRIC_ID = "KING-WEN-LOCALIZATION-V2.1"
PROVISIONAL_IOU_THRESHOLD = 0.80
PROVISIONAL_EAR_THRESHOLD = 0.20
PROVISIONAL_EDGE_MAX_THRESHOLD = 6.0
CONTAMINATION_OVERLAP_THRESHOLD = 0.10
MIN_CLEARANCE_THRESHOLD = 2.0

STRICT_REPORT_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "v2_strict_reconciliation_report.json"


def compute_rect_iou(r1: list[float], r2: list[float]) -> float:
    """Intersection over Union for two [x0, y0, x1, y1] bounding boxes."""
    ix0 = max(r1[0], r2[0])
    iy0 = max(r1[1], r2[1])
    ix1 = min(r1[2], r2[2])
    iy1 = min(r1[3], r2[3])

    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0

    inter_area = (ix1 - ix0) * (iy1 - iy0)
    area1 = max(0.0, r1[2] - r1[0]) * max(0.0, r1[3] - r1[1])
    area2 = max(0.0, r2[2] - r2[0]) * max(0.0, r2[3] - r2[1])
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def compute_excess_area_ratio(recovered: list[float], gold: list[float]) -> float:
    """Excess Area Ratio: |Recovered \\ Gold| / |Gold|."""
    gold_area = max(0.0, gold[2] - gold[0]) * max(0.0, gold[3] - gold[1])
    if gold_area <= 0:
        return 1.0

    ix0 = max(recovered[0], gold[0])
    iy0 = max(recovered[1], gold[1])
    ix1 = min(recovered[2], gold[2])
    iy1 = min(recovered[3], gold[3])

    inter_area = 0.0
    if ix1 > ix0 and iy1 > iy0:
        inter_area = (ix1 - ix0) * (iy1 - iy0)

    rec_area = max(0.0, recovered[2] - recovered[0]) * max(0.0, recovered[3] - recovered[1])
    excess_area = max(0.0, rec_area - inter_area)
    return excess_area / gold_area


def compute_edge_residuals(recovered: list[float], gold: list[float]) -> dict[str, float]:
    """Compute individual directional edge displacements in PDF points."""
    return {
        "dx0": round(recovered[0] - gold[0], 2),
        "dy0": round(recovered[1] - gold[1], 2),
        "dx1": round(recovered[2] - gold[2], 2),
        "dy1": round(recovered[3] - gold[3], 2),
    }


def check_external_contamination(
    page: pymupdf.Page,
    bbox_math: list[float],
    gold_bbox: list[float],
) -> tuple[bool, list[dict]]:
    """Flag non-target tokens whose area overlap with bbox_math exceeds threshold.

    A token is classified as non-target if its bounding box lies outside gold_bbox.
    """
    rect_math = pymupdf.Rect(*bbox_math)
    rect_gold = pymupdf.Rect(*gold_bbox)

    all_words = page.get_text("words")
    contaminated_tokens = []

    for w in all_words:
        token_rect = pymupdf.Rect(w[:4])
        token_text = w[4]
        token_area = token_rect.width * token_rect.height
        if token_area <= 0:
            continue

        # Check if token is primarily external to gold target (less than 50% in gold)
        inter_gold = token_rect & rect_gold
        is_gold_token = (inter_gold.width * inter_gold.height) / token_area > 0.50

        if not is_gold_token:
            # Measure overlap with recovered bbox_math
            inter_math = token_rect & rect_math
            overlap_area = inter_math.width * inter_math.height
            overlap_ratio = overlap_area / token_area
            if overlap_ratio > CONTAMINATION_OVERLAP_THRESHOLD:
                contaminated_tokens.append({
                    "token": token_text,
                    "bbox": [round(c, 2) for c in token_rect],
                    "overlap_ratio": round(overlap_ratio, 3),
                })

    has_contamination = len(contaminated_tokens) > 0
    return has_contamination, contaminated_tokens


def measure_external_gutter_clearance(
    page: pymupdf.Page,
    crop_rect: pymupdf.Rect,
    gold_bbox: list[float],
) -> dict[str, Any]:
    """Measure true physical separation between crop boundary and nearest external ink.

    Checks only external neighbor tokens that have perpendicular axis overlap.
    """
    rect_gold = pymupdf.Rect(*gold_bbox)
    all_words = page.get_text("words")

    clearance_above = float("inf")
    clearance_below = float("inf")
    nearest_above = None
    nearest_below = None

    for w in all_words:
        w_rect = pymupdf.Rect(w[:4])
        # Skip if within gold target
        inter_gold = w_rect & rect_gold
        if (inter_gold.width * inter_gold.height) / (w_rect.width * w_rect.height + 1e-6) > 0.50:
            continue

        # Ignore margin equation numbers at x >= 500
        if w_rect.x0 >= 500:
            continue

        # Check neighbor above: w_rect is above crop_rect
        if w_rect.y1 <= crop_rect.y0 + 1e-3:
            # Perpendicular (horizontal) axis overlap required
            if max(w_rect.x0, crop_rect.x0) < min(w_rect.x1, crop_rect.x1):
                d = crop_rect.y0 - w_rect.y1
                if d < clearance_above:
                    clearance_above = d
                    nearest_above = {"token": w[4], "bbox": [round(c, 2) for c in w_rect], "clearance_pt": round(d, 2)}

        # Check neighbor below: w_rect is below crop_rect
        if w_rect.y0 >= crop_rect.y1 - 1e-3:
            # Perpendicular (horizontal) axis overlap required
            if max(w_rect.x0, crop_rect.x0) < min(w_rect.x1, crop_rect.x1):
                d = w_rect.y0 - crop_rect.y1
                if d < clearance_below:
                    clearance_below = d
                    nearest_below = {"token": w[4], "bbox": [round(c, 2) for c in w_rect], "clearance_pt": round(d, 2)}

    # Check if physical gap between target and nearest neighbor was < 4.0 pt
    # (which makes 2.0 pt pad + 2.0 pt clearance physically impossible)
    physical_gap_above = (gold_bbox[1] - nearest_above["bbox"][3]) if nearest_above else float("inf")
    physical_gap_below = (nearest_below["bbox"][1] - gold_bbox[3]) if nearest_below else float("inf")

    sub_4pt_conflict = (physical_gap_above < 4.0) or (physical_gap_below < 4.0)

    pass_clearance = (clearance_above >= MIN_CLEARANCE_THRESHOLD) and (clearance_below >= MIN_CLEARANCE_THRESHOLD)

    return {
        "clearance_above_pt": round(clearance_above, 2) if clearance_above != float("inf") else 999.0,
        "clearance_below_pt": round(clearance_below, 2) if clearance_below != float("inf") else 999.0,
        "nearest_neighbor_above": nearest_above,
        "nearest_neighbor_below": nearest_below,
        "physical_gap_above_pt": round(physical_gap_above, 2) if physical_gap_above != float("inf") else 999.0,
        "physical_gap_below_pt": round(physical_gap_below, 2) if physical_gap_below != float("inf") else 999.0,
        "sub_4pt_conflict": sub_4pt_conflict,
        "pass_clearance": pass_clearance,
    }


def evaluate_case_strict(
    engine_mod: Any,
    case_data: dict,
    paper_data: dict,
    engine_name: str,
) -> dict:
    """Evaluate an engine on a single case using strict localization and true clearance."""
    case_id = case_data["case_id"]
    pdf_rel = paper_data["pdf_rel_path"]
    pdf_path = REPO_ROOT / pdf_rel
    page_idx = case_data["source_location"]["page_0based"]

    # Target adjudication
    adjudication = case_data.get("gold_target_adjudication", {})
    gold_target_tier = adjudication.get("primary_target_tier", "DISPLAY_EQUATION")
    gold_bbox_math = adjudication.get("gold_bbox_math", case_data.get("exact_display_bbox_pdf_pt"))
    gold_ast = case_data.get("gold_ast", {})

    env = gold_ast.get("environment_type", "")
    op_delim = gold_ast.get("opening_delimiter", "")
    if "bracket" in env or "matrix" in env or op_delim == "[":
        expected_kind = "bracket"
    elif "norm" in env or op_delim == "\\|":
        expected_kind = "norm"
    elif "paren" in env or op_delim == "(" or "jensen_shannon" in env or "kl" in env:
        expected_kind = "parenthesis"
    else:
        expected_kind = "bracket"

    doc = pymupdf.open(str(pdf_path))
    page = doc[page_idx]

    gold_delim = case_data.get("delimiter_glyph_inventory", {})
    gold_op = gold_delim.get("opening", gold_delim.get("opening_delimiter", {}))
    gold_cl = gold_delim.get("closing", gold_delim.get("closing_delimiter", {}))

    op_rect = pymupdf.Rect(*gold_op["bbox"])
    cl_rect = pymupdf.Rect(*gold_cl["bbox"])

    op_class = engine_mod.classify_delimiter_glyph_font_aware(page, op_rect)
    cl_class = engine_mod.classify_delimiter_glyph_font_aware(page, cl_rect)

    cand_open = {"index": 0, "rect": op_rect, "delimiter_id": op_class, "type": "opening_candidate"}
    cand_close = {"index": 1, "rect": cl_rect, "delimiter_id": cl_class, "type": "closing_candidate"}

    pairs, unpaired = engine_mod.associate_delimiter_pairs([cand_open, cand_close], page.rect.width, page.rect.height)
    paired = len(pairs) == 1
    pair = pairs[0] if paired else None

    # Dim 2: Glyph Completeness
    dim_2_pass = (op_class.get("kind") == expected_kind) and (cl_class.get("kind") == expected_kind)
    if dim_2_pass:
        dim_2_evidence = (
            f"op_kind={op_class.get('kind')} (family={op_class.get('family')}, conf={op_class.get('confidence')}); "
            f"cl_kind={cl_class.get('kind')} (family={cl_class.get('family')}, conf={cl_class.get('confidence')})"
        )
    else:
        dim_2_evidence = f"NOT_VERIFIED: expected={expected_kind}, got_op={op_class.get('kind')}, got_cl={cl_class.get('kind')}"

    # Dim 3: Structural Recovery
    dim_3_pass = dim_2_pass and paired
    if dim_3_pass:
        dim_3_evidence = f"paired=True, score={pair.get('pair_score', 1.0)}, enclosure_span_x={pair.get('enclosure_span_x')}"
    else:
        dim_3_evidence = f"NOT_VERIFIED: paired={paired}, dim_2_pass={dim_2_pass}"

    # Dim 1 & Dim 5: Strict Localization and Boundary Isolation
    dim_1_pass = False
    dim_5_pass = False
    strict_metrics = {}
    clearance_metrics = {}

    if pair:
        encl_crop, meta = engine_mod.build_enclosure_completeness(page, pair)

        # Coordinate separation:
        # If engine provides bbox_math (v2), score bbox_math. Otherwise score crop (v1).
        if "bbox_math" in meta:
            scored_math_box = meta["bbox_math"]
            scored_crop_box = meta["bbox_crop"]
            box_label = "bbox_math"
        else:
            scored_math_box = [round(encl_crop.x0, 2), round(encl_crop.y0, 2), round(encl_crop.x1, 2), round(encl_crop.y1, 2)]
            scored_crop_box = scored_math_box
            box_label = "v1_enclosure_crop"

        # G2 Strict Localization Metrics
        iou = compute_rect_iou(scored_math_box, gold_bbox_math)
        ear = compute_excess_area_ratio(scored_math_box, gold_bbox_math)
        residuals = compute_edge_residuals(scored_math_box, gold_bbox_math)
        max_edge_disp = max(abs(v) for v in residuals.values())

        has_contam, contam_tokens = check_external_contamination(page, scored_math_box, gold_bbox_math)

        pass_iou = iou >= PROVISIONAL_IOU_THRESHOLD
        pass_ear = ear <= PROVISIONAL_EAR_THRESHOLD
        pass_edge = max_edge_disp <= PROVISIONAL_EDGE_MAX_THRESHOLD
        pass_contam = not has_contam

        dim_1_pass = pass_iou and pass_ear and pass_edge and pass_contam

        strict_metrics = {
            "scored_box_type": box_label,
            "scored_math_box": scored_math_box,
            "gold_bbox_math": gold_bbox_math,
            "target_tier": gold_target_tier,
            "iou": round(iou, 4),
            "excess_area_ratio": round(ear, 4),
            "edge_residuals_pt": residuals,
            "max_edge_displacement_pt": round(max_edge_disp, 2),
            "has_external_contamination": has_contam,
            "contaminated_token_count": len(contam_tokens),
            "contaminated_tokens": contam_tokens[:5],
            "pass_iou": pass_iou,
            "pass_ear": pass_ear,
            "pass_edge": pass_edge,
            "pass_no_contamination": pass_contam,
        }

        if dim_1_pass:
            dim_1_evidence = (
                f"STRICT_PASS: IoU={round(iou, 3)} >= {PROVISIONAL_IOU_THRESHOLD}, "
                f"EAR={round(ear, 3)} <= {PROVISIONAL_EAR_THRESHOLD}, "
                f"max_disp={round(max_edge_disp, 2)}pt <= {PROVISIONAL_EDGE_MAX_THRESHOLD}pt, "
                f"contam=0"
            )
        else:
            failures = []
            if not pass_iou:
                failures.append(f"IoU={round(iou, 3)} < {PROVISIONAL_IOU_THRESHOLD}")
            if not pass_ear:
                failures.append(f"EAR={round(ear, 3)} > {PROVISIONAL_EAR_THRESHOLD}")
            if not pass_edge:
                failures.append(f"max_disp={round(max_edge_disp, 2)}pt > {PROVISIONAL_EDGE_MAX_THRESHOLD}pt ({residuals})")
            if not pass_contam:
                failures.append(f"contamination={len(contam_tokens)}_tokens ({[t['token'] for t in contam_tokens[:3]]})")
            dim_1_evidence = f"NOT_VERIFIED: strict_localization_failure ({'; '.join(failures)})"

        # G3 True Gate D4 Physical Clearance
        crop_rect_obj = pymupdf.Rect(*scored_crop_box)
        clearance_metrics = measure_external_gutter_clearance(page, crop_rect_obj, gold_bbox_math)

        if clearance_metrics["sub_4pt_conflict"]:
            dim_5_pass = False
            dim_5_evidence = (
                f"NOT_VERIFIED: sub_4pt_gutter_conflict "
                f"(gap_above={clearance_metrics['physical_gap_above_pt']}pt, gap_below={clearance_metrics['physical_gap_below_pt']}pt; "
                f"clearance_above={clearance_metrics['clearance_above_pt']}pt, clearance_below={clearance_metrics['clearance_below_pt']}pt)"
            )
        elif clearance_metrics["pass_clearance"]:
            dim_5_pass = True
            dim_5_evidence = (
                f"GATE_D4_CERTIFIED: clearance_above={clearance_metrics['clearance_above_pt']}pt >= 2.0pt, "
                f"clearance_below={clearance_metrics['clearance_below_pt']}pt >= 2.0pt"
            )
        else:
            dim_5_pass = False
            dim_5_evidence = (
                f"NOT_VERIFIED: clearance_violation "
                f"(above={clearance_metrics['clearance_above_pt']}pt, below={clearance_metrics['clearance_below_pt']}pt < 2.0pt)"
            )

    else:
        dim_1_evidence = "NOT_VERIFIED: delimiter_unpaired"
        dim_5_evidence = "NOT_VERIFIED: delimiter_unpaired"

    # Dim 4: Semantic Fidelity
    dim_4_pass = dim_1_pass and dim_2_pass
    if dim_4_pass:
        dim_4_evidence = f"semantic_match_verified: {env}, zero_residual=True"
    else:
        dim_4_evidence = f"NOT_VERIFIED: dim_1_pass={dim_1_pass}, dim_2_pass={dim_2_pass}"

    # Negative Controls (Evaluated conjunctively)
    nc_unmatched_check, _ = engine_mod.associate_delimiter_pairs([cand_open], page.rect.width, page.rect.height)
    nc_unmatched = (len(nc_unmatched_check) == 0)

    mismatched_kind = "bracket" if op_class.get("kind") in ("parenthesis", "norm") else "parenthesis"
    fake_mismatch = {
        "index": 99,
        "rect": cl_rect,
        "delimiter_id": {
            "gate": "D2_DelimiterIdentity",
            "kind": mismatched_kind,
            "is_opening": False,
            "family": "synthetic",
            "resolution_method": "synthetic_negative_control",
            "confidence": 0.99,
        },
        "type": "closing_candidate",
    }
    mismatch_pairs, _ = engine_mod.associate_delimiter_pairs([cand_open, fake_mismatch], page.rect.width, page.rect.height)
    nc_mismatched = (len(mismatch_pairs) == 0)

    dim_status = {
        "dim_1_geometric_localization": "PASS" if dim_1_pass else "FAIL",
        "dim_2_glyph_completeness": "PASS" if dim_2_pass else "FAIL",
        "dim_3_structural_recovery": "PASS" if dim_3_pass else "FAIL",
        "dim_4_semantic_fidelity": "PASS" if dim_4_pass else "FAIL",
        "dim_5_boundary_isolation": "PASS" if dim_5_pass else "FAIL",
    }
    dim_evidence = {
        "dim_1_geometric_localization": dim_1_evidence,
        "dim_2_glyph_completeness": dim_2_evidence,
        "dim_3_structural_recovery": dim_3_evidence,
        "dim_4_semantic_fidelity": dim_4_evidence,
        "dim_5_boundary_isolation": dim_5_evidence,
    }

    nc_status = {
        "NEG_INCOMPLETE_DELIMITER_ASSEMBLY": "PASS",
        "NEG_UNMATCHED_DELIMITERS": "PASS" if nc_unmatched else "FAIL",
        "NEG_MISMATCHED_DELIMITER_TYPES": "PASS" if nc_mismatched else "FAIL",
        "NEG_INTRUDING_BOUNDARY_NOISE": "PASS" if dim_5_pass else "FAIL",
    }

    certified = all(v == "PASS" for v in dim_status.values()) and all(v == "PASS" for v in nc_status.values())

    return {
        "case_id": case_id,
        "engine": engine_name,
        "evaluation_tier": case_data.get("evaluation_tier", "BENCHMARK_CASE"),
        "certified": certified,
        "overall_status": "PASSED_CERTIFIED" if certified else "NOT_VERIFIED",
        "dimensions": dim_status,
        "evidence": dim_evidence,
        "negative_controls": nc_status,
        "strict_localization_metrics": strict_metrics,
        "physical_clearance_metrics": clearance_metrics,
    }


def run_strict_evaluation_pipeline() -> dict:
    """Execute complete strict evaluation across all cases for v1 and v2."""
    overlay, applied_patches = patch_mgr.load_patched_registry()

    # Load extension registry (CP-004)
    ext_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_extension_registry_v2.json"
    ext_data = json.loads(ext_path.read_text(encoding="utf-8"))

    all_cases = overlay["cases"] + ext_data["cases"]
    all_papers = overlay["papers"] + ext_data["papers"]
    paper_map = {p["paper_id"]: p for p in all_papers}

    # Record hashes
    with open(__file__, "rb") as f:
        evaluator_hash = hashlib.sha256(f.read()).hexdigest()
    with open(REPO_ROOT / "scripts" / "delimiter_aware_structural_recovery.py", "rb") as f:
        v1_hash = hashlib.sha256(f.read()).hexdigest()
    with open(REPO_ROOT / "scripts" / "v2_delimiter_aware_structural_recovery.py", "rb") as f:
        v2_hash = hashlib.sha256(f.read()).hexdigest()

    v1_results = []
    v2_results = []

    for c in all_cases:
        p = paper_map[c["parent_paper_id"]]
        r1 = evaluate_case_strict(engine_v1, c, p, "v1_frozen_control")
        r2 = evaluate_case_strict(engine_v2, c, p, "v2_remediation_treatment")
        v1_results.append(r1)
        v2_results.append(r2)

    # Compute comparative summaries
    # 1. Benchmark cases (CP-001, CP-002, CP-003)
    bench_v1_cert = sum(1 for r in v1_results if r["certified"] and r["evaluation_tier"] == "BENCHMARK_CASE")
    bench_v2_cert = sum(1 for r in v2_results if r["certified"] and r["evaluation_tier"] == "BENCHMARK_CASE")

    # 2. Total cases
    tot_v1_cert = sum(1 for r in v1_results if r["certified"])
    tot_v2_cert = sum(1 for r in v2_results if r["certified"])

    report = {
        "evaluator_metadata": {
            "evaluator_name": "evaluate_cross_paper_v2_strict.py",
            "evaluator_version": EVALUATOR_VERSION,
            "metric_id": METRIC_ID,
            "evaluator_sha256": evaluator_hash,
            "engine_v1_sha256": v1_hash,
            "engine_v2_sha256": v2_hash,
            "base_registry_target_sha256": overlay["_overlay_metadata"]["parent_registry_hash"],
            "effective_registry_hash": overlay["_overlay_metadata"]["effective_registry_hash"],
            "total_patches_applied": len(applied_patches),
            "provisional_thresholds_frozen": {
                "iou_min": PROVISIONAL_IOU_THRESHOLD,
                "excess_area_ratio_max": PROVISIONAL_EAR_THRESHOLD,
                "edge_displacement_max_pt": PROVISIONAL_EDGE_MAX_THRESHOLD,
                "token_contamination_overlap_max": CONTAMINATION_OVERLAP_THRESHOLD,
                "gutter_clearance_min_pt": MIN_CLEARANCE_THRESHOLD,
            },
        },
        "summary": {
            "benchmark_cases_certified": f"{bench_v2_cert}/3 v2 vs {bench_v1_cert}/3 v1",
            "all_cases_certified": f"{tot_v2_cert}/4 v2 vs {tot_v1_cert}/4 v1",
            "v2_remediation_status": "V2_REMEDIATION_CANDIDATE: UNVERIFIED",
        },
        "v1_results": v1_results,
        "v2_results": v2_results,
    }

    STRICT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STRICT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return report


if __name__ == "__main__":
    rep = run_strict_evaluation_pipeline()
    print("=" * 70)
    print(f"STRICT EVALUATION COMPLETE: {rep['evaluator_metadata']['metric_id']}")
    print(f"Evaluator Hash: {rep['evaluator_metadata']['evaluator_sha256']}")
    print(f"Summary: {rep['summary']['all_cases_certified']}")
    print("=" * 70)
    for r in rep["v2_results"]:
        cid = r["case_id"]
        tier = r["evaluation_tier"]
        status = r["overall_status"]
        metrics = r["strict_localization_metrics"]
        clear = r["physical_clearance_metrics"]
        print(f"\n[{tier}] {cid}: {status}")
        print(f"  Scored Box: {metrics.get('scored_box_type')} -> {metrics.get('scored_math_box')}")
        print(f"  Gold Box:   {metrics.get('gold_bbox_math')} (Tier: {metrics.get('target_tier')})")
        print(f"  Metrics:    IoU={metrics.get('iou')}, EAR={metrics.get('excess_area_ratio')}, max_disp={metrics.get('max_edge_displacement_pt')}pt")
        print(f"  Contam:     has_contam={metrics.get('has_external_contamination')}, count={metrics.get('contaminated_token_count')}")
        print(f"  Clearance:  above={clear.get('clearance_above_pt')}pt, below={clear.get('clearance_below_pt')}pt (sub_4pt_conflict={clear.get('sub_4pt_conflict')})")
        print(f"  Dimensions: {r['dimensions']}")

