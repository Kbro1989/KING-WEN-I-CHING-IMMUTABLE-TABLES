#!/usr/bin/env python3
"""
Inspect passed/matched page component images and proposals for 1505.05770.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent

# 1. Load blind detection p002 & p003
with open(REPO_ROOT / "DATASETS/structural_preservation/1505.05770_blind_detection_p002.json", "r", encoding="utf-8") as f:
    d_p2 = json.load(f)

with open(REPO_ROOT / "DATASETS/structural_preservation/1505.05770_blind_detection_p003.json", "r", encoding="utf-8") as f:
    d_p3 = json.load(f)

# 2. Load positive control manifest
with open(REPO_ROOT / "DATASETS/structural_preservation/1505.05770_positive_control_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

gold_eqs = {}
for eq in manifest["gold_equations"]:
    gold_eqs[eq["gold_id"]] = {
        "page": eq["pdf_localization"]["page_number_one_based"],
        "bbox": eq["pdf_localization"]["gold_pdf_bbox"],
        "latex": eq["selection_identity"]["html_latex_verbatim"],
        "pdf_text": eq["pdf_localization"]["pdf_text_extracted"],
    }

# 3. Load v2/v3 comparison
with open(REPO_ROOT / "DATASETS/structural_preservation/v2_v3_comparison_evaluation.json", "r", encoding="utf-8") as f:
    v2v3 = json.load(f)

v3_evals = {e["gold_id"]: e for e in v2v3["per_equation_comparison"] if e["document_id"] == "1505.05770"}

def find_overlapping_cands(gold_bbox, cands):
    gx0, gy0, gx1, gy1 = gold_bbox
    overlaps = []
    for c in cands:
        cx0, cy0, cx1, cy1 = c["bbox_pdf_pt_approx"]
        ix0 = max(gx0, cx0)
        iy0 = max(gy0, cy0)
        ix1 = min(gx1, cx1)
        iy1 = min(gy1, cy1)
        if ix1 > ix0 and iy1 > iy0:
            i_area = (ix1 - ix0) * (iy1 - iy0)
            c_area = (cx1 - cx0) * (cy1 - cy0)
            g_area = (gx1 - gx0) * (gy1 - gy0)
            iou = i_area / (c_area + g_area - i_area)
            overlaps.append((iou, c))
    overlaps.sort(key=lambda x: x[0], reverse=True)
    return overlaps

print("=" * 80)
print("1505.05770: DETAILED AUDIT OF PASSED / MATCHED COMPONENTS & CROPS")
print("=" * 80)

order = ["GS-004", "GS-005", "GS-001", "GS-002", "GS-003"]
for gid in order:
    info = gold_eqs[gid]
    comp_eval = v3_evals[gid]
    c_v3 = comp_eval["candidate_v3"]
    b_v2 = comp_eval["baseline_v2"]
    page_num = info["page"]
    cands = d_p2["visual_component_analysis"]["visual_candidates"] if page_num == 2 else d_p3["visual_component_analysis"]["visual_candidates"]

    print(f"\n================================================================================")
    print(f"[{gid}] Page {page_num} | Gold BBox: {info['bbox']}")
    print(f"LaTeX: {info['latex']}")
    print(f"Extracted Text: {c_v3['extracted_text']}")
    print(f"Verdict: {c_v3['structural_verdict']} ({c_v3['features_passed']}/{c_v3['features_total']} features, IoU: {c_v3['math_expression_iou']:.4f})")
    print(f"Matched Proposal: {c_v3['matched_proposal_id']} Level {c_v3['hierarchy_level']} BBox: {c_v3['proposal_bbox']}")
    print(f"Features Checked: {json.dumps(c_v3['features_checked'])}")

    overlaps = find_overlapping_cands(info["bbox"], cands)
    print(f"\nTop Intersecting Visual Component Crops ({len(overlaps)} components inside/touching gold bbox):")
    for iou, c in overlaps[:6]:
        cpath = Path(c["crop_path"]).name
        print(f"  * Crop: page_000{page_num}/{cpath} (Component #{c['component_id']})")
        print(f"    - Render bbox: {c['bbox_render_px']} px | PDF pt approx: {c['bbox_pdf_pt_approx']}")
        print(f"    - Dimensions: {c['width_px']}x{c['height_px']} px | Aspect Ratio: {c['height_width_ratio']} | Area: {c['area_px']} px")
        print(f"    - IoU with full equation: {iou:.4f}")
        print(f"    - Candidate detection reasons: {c['candidate_reasons']}")
