#!/usr/bin/env python3
"""
Step 4 — Positive Control Comparison: Gold vs Blind Detection Candidates
for 1505.05770 (Variational Inference with Normalizing Flows)

Matching strategy:
    Visual candidates have bbox_pdf_pt_approx = [x0, y0, x1, y1] in MuPDF page points.
    Gold equations have gold_pdf_bbox = [x0, y0, x1, y1] in the same coordinate space.

    For each gold equation, every visual candidate on the same page is compared.
    IoU is computed between candidate bbox and gold bbox.
    Matching is one-to-one (greedy by descending IoU).
    Gold containment (is gold bbox fully inside candidate?) is recorded separately.

    We also cluster overlapping candidates into region proposals (by overlap)
    so the comparison is not purely individual-component.

Outputs:
    DATASETS/structural_preservation/1505.05770_detection_comparison.json

Invariants:
    - Gold coordinates are loaded from the frozen manifest AFTER detection data is loaded.
    - Missed gold equations and unmatched candidates remain in results, never filtered.
    - No structural expectations generated.
    - All file writes use encoding="utf-8".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = REPO_ROOT / "DATASETS" / "structural_preservation"

MANIFEST_PATH = OUT_ROOT / "1505.05770_positive_control_manifest.json"
DETECTION_P002_PATH = OUT_ROOT / "1505.05770_blind_detection_p002.json"
DETECTION_P003_PATH = OUT_ROOT / "1505.05770_blind_detection_p003.json"

# IoU threshold for a candidate to "match" a gold equation
IOU_MATCH_THRESHOLD = 0.05  # deliberately low; recall detection is the goal

# A candidate is considered to spatially cover a gold equation if
# the gold bbox centre falls inside the candidate bbox.
# (Used in addition to IoU for loose coverage reporting.)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def iou(a, b):
    """Intersection-over-union between two [x0,y0,x1,y1] boxes."""
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    intersection = (ix1 - ix0) * (iy1 - iy0)
    area_a = max(0.0, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(0.0, (b[2] - b[0]) * (b[3] - b[1]))
    union = area_a + area_b - intersection
    if union <= 0:
        return 0.0
    return round(intersection / union, 6)


def gold_centre_in_candidate(gold_bbox, cand_bbox):
    """Return True if the gold bbox centroid falls inside cand_bbox."""
    cx = (gold_bbox[0] + gold_bbox[2]) / 2
    cy = (gold_bbox[1] + gold_bbox[3]) / 2
    return cand_bbox[0] <= cx <= cand_bbox[2] and cand_bbox[1] <= cy <= cand_bbox[3]


def gold_contained_in_candidate(gold_bbox, cand_bbox):
    """Return True if the gold bbox is fully enclosed by cand_bbox."""
    return (
        cand_bbox[0] <= gold_bbox[0]
        and cand_bbox[1] <= gold_bbox[1]
        and cand_bbox[2] >= gold_bbox[2]
        and cand_bbox[3] >= gold_bbox[3]
    )


def boxes_overlap(a, b):
    """Return True if two boxes have any overlap."""
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def merge_box(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


# ---------------------------------------------------------------------------
# Cluster overlapping visual candidates into region proposals
# ---------------------------------------------------------------------------

def cluster_candidates(candidates):
    """
    Union-find clustering: merge visual candidates whose bboxes overlap.
    Returns list of cluster dicts with merged_bbox and member component_ids.
    """
    boxes = [c["bbox_pdf_pt_approx"] for c in candidates]
    n = len(boxes)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if boxes_overlap(boxes[i], boxes[j]):
                union(i, j)

    clusters = {}
    for i in range(n):
        root = find(i)
        if root not in clusters:
            clusters[root] = {"merged_bbox": list(boxes[i]), "members": []}
        clusters[root]["members"].append(candidates[i]["component_id"])
        clusters[root]["merged_bbox"] = merge_box(clusters[root]["merged_bbox"], boxes[i])

    result = sorted(clusters.values(), key=lambda c: c["merged_bbox"][1])
    for idx, cl in enumerate(result):
        cl["cluster_id"] = idx
        cl["member_count"] = len(cl["members"])
    return result


# ---------------------------------------------------------------------------
# Match gold equations against candidates on a page
# ---------------------------------------------------------------------------

def match_page(gold_equations, visual_candidates):
    """
    One-to-one greedy matching by descending IoU between gold_pdf_bbox
    and each candidate bbox_pdf_pt_approx.

    Also compute cluster-level matches for region proposals.

    Returns:
        matched_pairs: list of dicts (one per matched gold)
        missed_gold_ids: gold_ids with no match above threshold
        unmatched_candidate_ids: component_ids not matched to any gold
    """
    # Build all pairwise IoU scores
    pairs = []
    for geq in gold_equations:
        gold_bbox = geq["pdf_localization"]["gold_pdf_bbox"]
        for cand in visual_candidates:
            cand_bbox = cand["bbox_pdf_pt_approx"]
            score = iou(gold_bbox, cand_bbox)
            covered = gold_centre_in_candidate(gold_bbox, cand_bbox)
            contained = gold_contained_in_candidate(gold_bbox, cand_bbox)
            pairs.append({
                "gold_id": geq["gold_id"],
                "component_id": cand["component_id"],
                "iou": score,
                "gold_centre_in_candidate": covered,
                "gold_contained_in_candidate": contained,
                "gold_bbox": gold_bbox,
                "cand_bbox": cand_bbox,
                "candidate_reasons": cand["candidate_reasons"],
            })

    # Sort by IoU descending for greedy matching
    pairs.sort(key=lambda p: p["iou"], reverse=True)

    matched_gold = set()
    matched_cands = set()
    matched_pairs = []

    for p in pairs:
        if p["gold_id"] in matched_gold:
            continue
        if p["component_id"] in matched_cands:
            continue
        if p["iou"] >= IOU_MATCH_THRESHOLD:
            matched_gold.add(p["gold_id"])
            matched_cands.add(p["component_id"])
            matched_pairs.append({
                "gold_id": p["gold_id"],
                "matched_component_id": p["component_id"],
                "iou": p["iou"],
                "gold_centre_in_candidate": p["gold_centre_in_candidate"],
                "gold_contained_in_candidate": p["gold_contained_in_candidate"],
                "gold_bbox": p["gold_bbox"],
                "matched_cand_bbox": p["cand_bbox"],
                "candidate_reasons": p["candidate_reasons"],
            })

    all_gold_ids = {geq["gold_id"] for geq in gold_equations}
    all_cand_ids = {c["component_id"] for c in visual_candidates}

    missed_gold_ids = sorted(all_gold_ids - matched_gold)
    unmatched_cand_ids = sorted(all_cand_ids - matched_cands)

    # For missed golds: find best IoU and best centre-coverage even if below threshold
    best_per_missed = {}
    for p in pairs:
        if p["gold_id"] not in missed_gold_ids:
            continue
        gid = p["gold_id"]
        if gid not in best_per_missed or p["iou"] > best_per_missed[gid]["iou"]:
            best_per_missed[gid] = p

    missed_gold_details = []
    for gid in missed_gold_ids:
        detail = {"gold_id": gid}
        if gid in best_per_missed:
            bp = best_per_missed[gid]
            detail["best_iou_found"] = bp["iou"]
            detail["best_matching_component_id"] = bp["component_id"]
            detail["gold_centre_in_best_candidate"] = bp["gold_centre_in_candidate"]
            detail["gold_contained_in_best_candidate"] = bp["gold_contained_in_candidate"]
            detail["note"] = "No candidate reached IoU threshold; best candidate recorded."
        else:
            detail["best_iou_found"] = 0.0
            detail["note"] = "No overlapping candidate found."
        missed_gold_details.append(detail)

    # Duplicate detection: multiple candidates mapping to same gold
    gold_to_all_candidates = {}
    for p in pairs:
        if p["iou"] >= IOU_MATCH_THRESHOLD:
            gold_to_all_candidates.setdefault(p["gold_id"], []).append(p)
    duplicate_detections = {
        gid: [{"component_id": p["component_id"], "iou": p["iou"]}
               for p in sorted(cands, key=lambda x: x["iou"], reverse=True)]
        for gid, cands in gold_to_all_candidates.items()
        if len(cands) > 1
    }

    return matched_pairs, missed_gold_details, unmatched_cand_ids, duplicate_detections


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_comparison():
    # Load frozen manifest
    if not MANIFEST_PATH.is_file():
        sys.exit(f"[ERROR] Manifest not found: {MANIFEST_PATH}")
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        manifest = json.load(f)

    gold_equations = manifest["gold_equations"]

    # Load blind detection outputs
    for path in [DETECTION_P002_PATH, DETECTION_P003_PATH]:
        if not path.is_file():
            sys.exit(f"[ERROR] Detection output not found: {path}\nRun scripts/blind_detection_run_1505.py first.")

    with DETECTION_P002_PATH.open(encoding="utf-8") as f:
        det_p002 = json.load(f)
    with DETECTION_P003_PATH.open(encoding="utf-8") as f:
        det_p003 = json.load(f)

    # Verify provenance: detection SHA must match manifest PDF SHA
    manifest_pdf_sha = manifest["document_identity"]["pdf_sha256"]
    for det, label in [(det_p002, "p002"), (det_p003, "p003")]:
        if det["source_pdf_sha256"] != manifest_pdf_sha:
            sys.exit(
                f"[ERROR] SHA-256 mismatch in {label}.\n"
                f"  manifest: {manifest_pdf_sha}\n"
                f"  detection: {det['source_pdf_sha256']}"
            )
    print("[comparison] Source PDF SHA-256 verified for both detection outputs.", flush=True)

    # Organise gold by page (0-based index)
    gold_by_page = {}
    for geq in gold_equations:
        pidx = geq["pdf_localization"]["page_index_zero_based"]
        gold_by_page.setdefault(pidx, []).append(geq)

    # Page 2 → doc index 1; Page 3 → doc index 2
    detection_by_page = {
        1: det_p002,
        2: det_p003,
    }

    page_results = []
    total_matched = 0
    total_missed = 0
    total_unmatched_cands = 0
    total_visual_cands = 0

    for page_0based, det in detection_by_page.items():
        page_1based = page_0based + 1
        gold_on_page = gold_by_page.get(page_0based, [])
        visual_cands = det["visual_component_analysis"]["visual_candidates"]
        total_visual_cands += len(visual_cands)

        print(
            f"\n[comparison] Page {page_1based}: "
            f"{len(gold_on_page)} gold equations, "
            f"{len(visual_cands)} visual candidates",
            flush=True,
        )

        # Build clusters from candidates
        clusters = cluster_candidates(visual_cands) if visual_cands else []
        print(f"  Clustered into {len(clusters)} region proposals.", flush=True)

        # Cluster-level matching against gold
        cluster_match_details = []
        for geq in gold_on_page:
            gold_bbox = geq["pdf_localization"]["gold_pdf_bbox"]
            best_cl_iou = 0.0
            best_cl = None
            for cl in clusters:
                cl_iou = iou(gold_bbox, cl["merged_bbox"])
                if cl_iou > best_cl_iou:
                    best_cl_iou = cl_iou
                    best_cl = cl
            cluster_match_details.append({
                "gold_id": geq["gold_id"],
                "gold_bbox": gold_bbox,
                "best_cluster_iou": round(best_cl_iou, 6),
                "best_cluster": best_cl,
                "gold_centre_in_best_cluster": gold_centre_in_candidate(
                    gold_bbox, best_cl["merged_bbox"]
                ) if best_cl else False,
                "gold_contained_in_best_cluster": gold_contained_in_candidate(
                    gold_bbox, best_cl["merged_bbox"]
                ) if best_cl else False,
            })

        # Individual-component matching
        matched_pairs, missed_gold_details, unmatched_cand_ids, duplicates = match_page(
            gold_on_page, visual_cands
        )

        total_matched += len(matched_pairs)
        total_missed += len(missed_gold_details)
        total_unmatched_cands += len(unmatched_cand_ids)

        for mp in matched_pairs:
            print(
                f"  MATCHED: {mp['gold_id']} ↔ component {mp['matched_component_id']} "
                f"(IoU={mp['iou']:.4f}, contained={mp['gold_contained_in_candidate']})",
                flush=True,
            )
        for md in missed_gold_details:
            print(
                f"  MISSED:  {md['gold_id']} "
                f"(best IoU={md.get('best_iou_found', 0):.4f})",
                flush=True,
            )

        page_results.append({
            "page_number_1_based": page_1based,
            "page_index_0_based": page_0based,
            "gold_equation_count": len(gold_on_page),
            "visual_candidate_count": len(visual_cands),
            "cluster_count": len(clusters),
            "matched_pair_count": len(matched_pairs),
            "missed_gold_count": len(missed_gold_details),
            "unmatched_candidate_count": len(unmatched_cand_ids),
            "duplicate_detection_gold_ids": list(duplicates.keys()),
            "matched_pairs": matched_pairs,
            "missed_gold_equations": missed_gold_details,
            "cluster_match_details": cluster_match_details,
            "unmatched_candidate_component_ids": unmatched_cand_ids,
            "duplicate_detections": duplicate_detections if (duplicate_detections := duplicates) else {},
        })

    # Overall summary
    total_gold = len(gold_equations)
    summary = {
        "gold_recall": {
            "matched_gold_count": total_matched,
            "missed_gold_count": total_missed,
            "total_gold_count": total_gold,
            "recall_at_iou_threshold": round(total_matched / total_gold, 6) if total_gold else 0.0,
            "iou_threshold_used": IOU_MATCH_THRESHOLD,
        },
        "candidate_precision": {
            "total_visual_candidates": total_visual_cands,
            "matched_to_gold": total_matched,
            "unmatched_to_gold": total_unmatched_cands,
            "precision_at_iou_threshold": round(
                total_matched / total_visual_cands, 6
            ) if total_visual_cands else 0.0,
        },
        "notes": [
            "Matching is one-to-one greedy by descending IoU.",
            "IoU is computed between individual connected components (bbox_pdf_pt_approx) and gold_pdf_bbox.",
            "Cluster-level match details use union-find merging of overlapping candidates.",
            "No structural expectations generated; this is a detection dataset only.",
            "Visual connected components represent ink marks, not equation boundaries.",
            "Gold equations span multiple components; individual-component IoU is expected to be low.",
            "bbox_pdf_pt_approx accuracy is limited by pixel quantization at zoom=4 (~0.25pt error).",
        ],
    }

    output = {
        "schema_version": "1.0",
        "step": "step4_gold_candidate_comparison",
        "document_id": "1505.05770",
        "source_pdf_sha256": manifest_pdf_sha,
        "manifest_path": str(MANIFEST_PATH),
        "detection_sources": {
            "p002": str(DETECTION_P002_PATH),
            "p002_detector_sha256": det_p002["detector_script_sha256"],
            "p003": str(DETECTION_P003_PATH),
            "p003_detector_sha256": det_p003["detector_script_sha256"],
        },
        "gold_coordinates_supplied_to_detector": False,
        "structural_expectations_generated": False,
        "iou_match_threshold": IOU_MATCH_THRESHOLD,
        "summary": summary,
        "page_results": page_results,
    }

    out_path = OUT_ROOT / "1505.05770_detection_comparison.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[comparison] Saved → {out_path}", flush=True)

    # Print summary table
    print("\n=== Detection Comparison Summary ===", flush=True)
    print(f"Gold equations:        {total_gold}", flush=True)
    print(f"Gold matched (IoU≥{IOU_MATCH_THRESHOLD}): {total_matched}", flush=True)
    print(f"Gold missed:           {total_missed}", flush=True)
    print(f"Recall:                {summary['gold_recall']['recall_at_iou_threshold']:.4f}", flush=True)
    print(f"Total visual cands:    {total_visual_cands}", flush=True)
    print(f"Precision:             {summary['candidate_precision']['precision_at_iou_threshold']:.6f}", flush=True)
    print("[comparison] Step 4 complete.", flush=True)


if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    run_comparison()

