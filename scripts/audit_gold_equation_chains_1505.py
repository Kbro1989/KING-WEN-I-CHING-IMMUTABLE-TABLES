#!/usr/bin/env python3
"""
Independent End-to-End Audit: Five Gold Equation Chains for 1505.05770.

Consumes frozen artifacts only. Does NOT modify any detector, candidate manifest,
or gold reference. Verifies the full chain for each gold equation:
  Source transcript -> Text/raster evidence -> Component identity ->
  Reconstructed expression -> Four-dimensional verdict.

Outputs:
    DATASETS/structural_preservation/1505.05770_end_to_end_audit.json

Adversarial operator disambiguation cases included in Section 4.
"""
from __future__ import annotations

import hashlib
import json
import sys
import datetime
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
SP = REPO_ROOT / "DATASETS" / "structural_preservation"

ADVERSARIAL_OPERATOR_CASES = [
    {
        "case_id": "ADV-001",
        "description": "Gradient identity: biconditional vs equality",
        "source_equation": "GS-002",
        "source_operator": "⇔",
        "source_unicode": "U+21D4",
        "source_font": "CMSY10",
        "confusable_operator": "=",
        "confusable_unicode": "U+003D",
        "mathematical_significance": "Replacing ⇔ with = changes the claim from an equivalence (iff) to an equation; they have different logical status even though the mathematical content is the same statement.",
        "extraction_risk": "MuPDF may map CMSY10 math symbols to different unicode code points; must verify extracted character against source font glyph.",
    },
    {
        "case_id": "ADV-002",
        "description": "Similarity vs approximate equality",
        "source_equation": "GS-001",
        "source_operator": "∼",
        "source_unicode": "U+223C",
        "confusable_operator": "≈",
        "confusable_unicode": "U+2248",
        "mathematical_significance": "In GS-001, ∼ means 'is distributed as' (z ~ N(...)). ≈ means approximately equal. These are distinct mathematical claims.",
        "extraction_risk": "Both operators are single unicode characters in CMSY10; a font encoding bug could transpose them.",
    },
    {
        "case_id": "ADV-003",
        "description": "Biconditional vs implication in GS-001",
        "source_equation": "GS-001",
        "source_operator": "⇔",
        "source_unicode": "U+21D4",
        "confusable_operator": "⇒",
        "confusable_unicode": "U+21D2",
        "mathematical_significance": "GS-001 asserts a reparameterization equivalence (⇔). Replacing with ⇒ weakens it to one-directional implication.",
        "extraction_risk": "Adjacent unicode code points; a 2-bit error or misread would produce the wrong symbol.",
    },
    {
        "case_id": "ADV-004",
        "description": "Conditional bar vs parallel/norm in GS-005",
        "source_equation": "GS-005",
        "source_operator": "‖",
        "source_unicode": "U+2016",
        "confusable_operator": "|",
        "confusable_unicode": "U+007C",
        "mathematical_significance": "In GS-005, ‖ separates the KL divergence arguments q_phi || p. Using | would read as conditioning, changing the equation's meaning.",
        "extraction_risk": "Single vertical bar | is common in many contexts; double-bar ‖ for divergence may be output as || (two singles) or as one character.",
    },
]


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iou_boxes(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0, ix1, iy1 = max(ax0, bx0), max(ay0, by0), min(ax1, bx1), min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    i = (ix1 - ix0) * (iy1 - iy0)
    return i / ((ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - i)


def find_visual_region_candidates(gold_bbox, cands):
    gx0, gy0, gx1, gy1 = gold_bbox
    hits = []
    for idx, c in enumerate(cands):
        cx0, cy0, cx1, cy1 = c["bbox_pdf_pt_approx"]
        if cx1 > gx0 and cx0 < gx1 and cy1 > gy0 and cy0 < gy1:
            iou = iou_boxes(gold_bbox, c["bbox_pdf_pt_approx"])
            hits.append({
                "page_candidate_index": idx,
                "opencv_component_id": c["component_id"],
                "crop_filename": Path(c["crop_path"]).name,
                "bbox_pdf_pt_approx": c["bbox_pdf_pt_approx"],
                "bbox_render_px": c["bbox_render_px"],
                "width_px": c["width_px"],
                "height_px": c["height_px"],
                "aspect_ratio": c["height_width_ratio"],
                "area_px": c["area_px"],
                "candidate_reasons": c["candidate_reasons"],
                "iou_with_gold_bbox": round(iou, 6),
            })
    hits.sort(key=lambda x: x["iou_with_gold_bbox"], reverse=True)
    return hits


def classify_dimension_verdicts(gid, v3):
    fc = v3["features_checked"]
    fails = [k for k, v in fc.items() if not v]
    return {
        "geometric_localization": {
            "metric": "math_expression_iou",
            "value": v3["math_expression_iou"],
            "verdict": "HIGH" if v3["math_expression_iou"] > 0.9 else ("MODERATE" if v3["math_expression_iou"] > 0.5 else "LOW"),
        },
        "glyph_completeness": {
            "features_passed": v3["features_passed"],
            "features_total": v3["features_total"],
            "failed_features": fails,
            "verdict": "COMPLETE" if not fails else "INCOMPLETE",
        },
        "structural_fidelity": {
            "structural_verdict": v3["structural_verdict"],
            "structural_ratio": v3["structural_ratio"],
            "verdict": v3["structural_verdict"],
        },
        "semantic_validity": {
            "note": "Semantic validity is not independently computed; it is inferred from glyph completeness + structural fidelity.",
            "verdict": "INFERRED_PRESERVED" if not fails else "INFERRED_PARTIAL",
        },
    }


def run_audit():
    # --- Load frozen artifacts ---
    with open(SP / "1505.05770_positive_control_manifest.json", "r", encoding="utf-8") as f:
        gold_manifest = json.load(f)
    with open(SP / "v2_v3_comparison_evaluation.json", "r", encoding="utf-8") as f:
        v2v3 = json.load(f)
    with open(SP / "1505.05770_blind_detection_p002.json", "r", encoding="utf-8") as f:
        dp2 = json.load(f)
    with open(SP / "1505.05770_blind_detection_p003.json", "r", encoding="utf-8") as f:
        dp3 = json.load(f)
    with open(SP / "1505.05770_blind_renders_freeze_manifest.json", "r", encoding="utf-8") as f:
        freeze = json.load(f)

    evals = {e["gold_id"]: e for e in v2v3["per_equation_comparison"] if e["document_id"] == "1505.05770"}
    cands_p2 = dp2["visual_component_analysis"]["visual_candidates"]
    cands_p3 = dp3["visual_component_analysis"]["visual_candidates"]

    input_artifact_hashes = {
        "1505.05770_positive_control_manifest.json": sha256_path(SP / "1505.05770_positive_control_manifest.json"),
        "v2_v3_comparison_evaluation.json": sha256_path(SP / "v2_v3_comparison_evaluation.json"),
        "1505.05770_blind_detection_p002.json": sha256_path(SP / "1505.05770_blind_detection_p002.json"),
        "1505.05770_blind_detection_p003.json": sha256_path(SP / "1505.05770_blind_detection_p003.json"),
        "1505.05770_blind_renders_freeze_manifest.json": sha256_path(SP / "1505.05770_blind_renders_freeze_manifest.json"),
    }

    equation_chains = []
    for eq in gold_manifest["gold_equations"]:
        gid = eq["gold_id"]
        pdf_loc = eq["pdf_localization"]
        page = pdf_loc["page_number_one_based"]
        gold_bbox = pdf_loc["gold_pdf_bbox"]
        pdf_text = pdf_loc["pdf_text_extracted"]
        latex = eq["selection_identity"]["html_latex_verbatim"]
        ev = evals[gid]
        v3 = ev["candidate_v3"]
        v2 = ev["baseline_v2"]

        cands = cands_p2 if page == 2 else cands_p3
        visual_hits = find_visual_region_candidates(gold_bbox, cands)

        # Cross-channel recovery check: identify glyphs in text stream vs visual only
        text_channel = {
            "source": "mupdf_character_stream",
            "extracted_text": v3["extracted_text"],
            "total_glyphs": v3["total_glyphs"],
            "math_glyph_ratio": v3["math_glyph_ratio"],
        }

        # Visual-only glyph recovery (documented cases)
        visual_only_recoveries = []
        if gid == "GS-004":
            # integral (#4241 / component_1568.png) is in visual region but absent from text stream
            int_cands = [c for c in visual_hits if c["opencv_component_id"] == 4241]
            if int_cands:
                visual_only_recoveries.append({
                    "glyph": "integral_operator",
                    "latex_symbol": r"\int",
                    "opencv_component_id": 4241,
                    "page_candidate_index": int_cands[0]["page_candidate_index"],
                    "crop_filename": int_cands[0]["crop_filename"],
                    "bbox_pdf_pt_approx": int_cands[0]["bbox_pdf_pt_approx"],
                    "aspect_ratio": int_cands[0]["aspect_ratio"],
                    "recovery_status": "DETECTED_IN_VISUAL_CHANNEL",
                    "downstream_unification_status": "PENDING — not yet unified into reconstructed expression",
                    "feature_check_result": "has_integral_operator: false (text channel only)",
                    "note": "Visual detector independently found stretched tall ∫ glyph. Text stream omits it. Evaluator correctly withholds PRESERVED verdict until cross-channel unification.",
                })

        dim_verdicts = classify_dimension_verdicts(gid, v3)

        chain_record = {
            "gold_id": gid,
            "page": page,
            "chain_link_1_source_transcript": {
                "gold_pdf_bbox": gold_bbox,
                "pdf_text_extracted": pdf_text,
                "latex_verbatim": latex,
                "extraction_channel": "mupdf_rawdict",
                "verification_status": pdf_loc.get("verification_status", "UNKNOWN"),
                "geometry_correction": pdf_loc.get("geometry_correction_provenance"),
            },
            "chain_link_2_text_raster_evidence": {
                "text_channel": text_channel,
                "visual_candidates_in_gold_region": len(visual_hits),
                "top_visual_candidates": visual_hits[:5],
                "visual_only_recoveries": visual_only_recoveries,
            },
            "chain_link_3_component_identity": {
                "namespace_note": "page_candidate_index: 0-based local index in filtered candidate list (crop filename). opencv_component_id: 1-based global label from cv2.connectedComponentsWithStats on binarized page raster.",
                "matched_proposal_id": v3["matched_proposal_id"],
                "hierarchy_level": v3["hierarchy_level"],
                "proposal_bbox": v3["proposal_bbox"],
                "math_expression_bbox": v3["math_expression_bbox"],
                "provenance": v3.get("provenance_summary", {}),
            },
            "chain_link_4_reconstructed_expression": {
                "extracted_text": v3["extracted_text"],
                "features_checked": v3["features_checked"],
                "structural_verdict": v3["structural_verdict"],
                "structural_ratio": v3["structural_ratio"],
                "features_passed": v3["features_passed"],
                "features_total": v3["features_total"],
            },
            "chain_link_5_four_dimensional_verdict": dim_verdicts,
            "v2_vs_v3": {
                "v2_verdict": v2["structural_verdict"],
                "v2_iou": v2["math_expression_iou"],
                "v3_verdict": v3["structural_verdict"],
                "v3_iou": v3["math_expression_iou"],
                "comparison_status": ev["comparison_verdict"],
            },
        }

        equation_chains.append(chain_record)

        verdict_sym = "PASS" if v3["structural_verdict"] == "PRESERVED" else "PARTIAL"
        print(f"[{gid}] P{page} | {verdict_sym} {v3['features_passed']}/{v3['features_total']} IoU={v3['math_expression_iou']:.4f}"
              f" | visual_in_region={len(visual_hits)}"
              + (f" | visual_only_recoveries={len(visual_only_recoveries)}" if visual_only_recoveries else ""))

    summary = {
        "total_gold_equations": len(equation_chains),
        "preserved": sum(1 for c in equation_chains if c["chain_link_4_reconstructed_expression"]["structural_verdict"] == "PRESERVED"),
        "partial": sum(1 for c in equation_chains if c["chain_link_4_reconstructed_expression"]["structural_verdict"] == "PARTIAL"),
        "missing": sum(1 for c in equation_chains if c["chain_link_4_reconstructed_expression"]["structural_verdict"] == "MISSING"),
        "cross_channel_recovery_cases": sum(1 for c in equation_chains if c["chain_link_2_text_raster_evidence"]["visual_only_recoveries"]),
        "pending_cross_channel_unification": ["GS-004 (integral operator)"],
    }

    output = {
        "schema_version": "1.0",
        "audit_name": "1505.05770 Independent End-to-End Gold Equation Chain Audit",
        "audit_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "audit_scope": {
            "population": "1505.05770 (Variational Inference with Normalizing Flows)",
            "gold_equations": ["GS-001", "GS-002", "GS-003", "GS-004", "GS-005"],
            "pages_audited": [2, 3],
            "benchmark_boundary": "These five equations provide targeted reconciliation evidence. This audit does NOT establish generalization across document classes, typographic conventions, or PDF producers.",
        },
        "consumed_frozen_artifacts": input_artifact_hashes,
        "modifications_to_frozen_artifacts": "NONE — audit is read-only.",
        "equation_chains": equation_chains,
        "adversarial_operator_cases": ADVERSARIAL_OPERATOR_CASES,
        "summary": summary,
    }

    out_path = SP / "1505.05770_end_to_end_audit.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nAudit written -> {out_path}")

    print("\n=== SUMMARY ===")
    print(f"Total gold equations:     {summary['total_gold_equations']}")
    print(f"Preserved:                {summary['preserved']}")
    print(f"Partial:                  {summary['partial']}")
    print(f"Missing:                  {summary['missing']}")
    print(f"Cross-channel recoveries: {summary['cross_channel_recovery_cases']}")
    print(f"Pending unification:      {summary['pending_cross_channel_unification']}")
    print(f"Adversarial operator cases documented: {len(ADVERSARIAL_OPERATOR_CASES)}")

    return output


if __name__ == "__main__":
    run_audit()

