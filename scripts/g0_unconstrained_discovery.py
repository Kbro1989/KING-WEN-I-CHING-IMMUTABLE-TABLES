"""PIAA-010 Unconstrained G0 Candidate Discovery.

Runs full-page math region discovery on PIAA paper Page 4 (page_idx=3)
WITHOUT reading oracle coordinates from the fixture manifest.

Policy invariants (from PIAA-010 fixture):
  - oracle_coordinates_allowed: false
  - fixture_annotations_read: false (candidate generation phase)

Workflow:
  1. Open PDF, extract all glyphs from full Page 4 (no bbox_clip).
  2. Keep only glyphs in math fonts (CMEX, CMSY, CMMI, CMBX, CMMIB, MSBM).
  3. Cluster glyphs into spatial math regions using baseline proximity.
  4. Score each candidate region by: math glyph density, relational operators,
     vector rule (fraction/radical) intersection.
  5. Output sorted candidates to DATASETS/structural_preservation/piaa_010_g0_candidates.json
  6. Post-hoc adjudication against PIAA-001..PIAA-005 sealed bboxes (IoU >= 0.5).

Critical: NO reference to piaa_fixture_manifest.json target_tiers bboxes
          during the candidate generation phase (steps 1-5).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pymupdf

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
DATASETS_DIR = REPO_ROOT / "DATASETS" / "structural_preservation"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from font_aware_math_classifier import is_math_font

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PDF_PATH = Path(
    "C:/Users/krist/Desktop/zotero/learning-corpus/"
    "efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)
MANIFEST_PATH = DATASETS_DIR / "piaa_fixture_manifest.json"
OUTPUT_PATH = DATASETS_DIR / "piaa_010_g0_candidates.json"

# PIAA Page 4 (0-based index 3)
TARGET_PAGE_IDX = 3

# Clustering parameters
BASELINE_MERGE_PT = 4.0    # glyphs within this y-distance share a baseline row
ROW_MERGE_PT = 20.0        # adjacent baseline rows within this gap form one region
MIN_MATH_GLYPHS = 2        # minimum math glyphs to propose a region
IOU_MATCH_THRESHOLD = 0.5  # IoU to count a fixture match

# Scoring weights
W_DENSITY = 0.5
W_RELATION = 0.3
W_VECTOR = 0.2

# Relation characters that boost score
RELATION_CHARS = set("=<>≤≥≠≈∝∈∉∼")

# Math font substrings (must match font_aware_math_classifier logic)
MATH_FONT_TOKENS = ("cmex", "cmsy", "cmmi", "cmbx", "cmmib", "msbm")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_math_font_name(font: str) -> bool:
    fl = font.lower()
    return any(tok in fl for tok in MATH_FONT_TOKENS)


def _iou(a: list[float], b: list[float]) -> float:
    """Compute Intersection over Union for two [x0,y0,x1,y1] boxes."""
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _bbox_union(bboxes: list[list[float]]) -> list[float]:
    return [
        min(b[0] for b in bboxes),
        min(b[1] for b in bboxes),
        max(b[2] for b in bboxes),
        max(b[3] for b in bboxes),
    ]


# ---------------------------------------------------------------------------
# Step 1: Extract all glyphs from full page (NO oracle clip)
# ---------------------------------------------------------------------------

def extract_full_page_glyphs(page: pymupdf.Page) -> list[dict]:
    """Extract character-level glyph stream from entire page — no bbox restriction."""
    glyphs = []
    blocks = page.get_text("rawdict", flags=pymupdf.TEXT_PRESERVE_LIGATURES)["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font = span.get("font", "")
                size = span.get("size", 0.0)
                for ch in span.get("chars", []):
                    cb = ch.get("bbox", [])
                    if len(cb) < 4:
                        continue
                    char_c = ch.get("c", "")
                    if not char_c:
                        continue
                    glyphs.append({
                        "char": char_c,
                        "font": font,
                        "size_pt": size,
                        "bbox": [round(x, 3) for x in cb],
                        "is_math_font": _is_math_font_name(font),
                        "is_relation": char_c in RELATION_CHARS,
                    })
    return glyphs


# ---------------------------------------------------------------------------
# Step 2: Keep only math-font glyphs
# ---------------------------------------------------------------------------

def filter_math_glyphs(glyphs: list[dict]) -> list[dict]:
    return [g for g in glyphs if g["is_math_font"]]


# ---------------------------------------------------------------------------
# Step 3: Cluster into spatial regions
# ---------------------------------------------------------------------------

def cluster_into_regions(math_glyphs: list[dict]) -> list[list[dict]]:
    """Group glyphs into spatial math regions using baseline proximity.

    Two-pass:
      Pass 1 — assign each glyph to a baseline row (y-center within BASELINE_MERGE_PT).
      Pass 2 — merge adjacent rows whose y-gap is within ROW_MERGE_PT into regions.
    """
    if not math_glyphs:
        return []

    # Pass 1: assign rows by y-center
    rows: list[list[dict]] = []
    for g in sorted(math_glyphs, key=lambda g: (g["bbox"][1] + g["bbox"][3]) / 2.0):
        g_cy = (g["bbox"][1] + g["bbox"][3]) / 2.0
        placed = False
        for row in rows:
            row_cy = sum((r["bbox"][1] + r["bbox"][3]) / 2.0 for r in row) / len(row)
            if abs(g_cy - row_cy) <= BASELINE_MERGE_PT:
                row.append(g)
                placed = True
                break
        if not placed:
            rows.append([g])

    # Sort rows by y position
    rows.sort(key=lambda row: min(g["bbox"][1] for g in row))

    # Pass 2: merge rows into contiguous regions
    regions: list[list[dict]] = []
    current_region: list[dict] = list(rows[0])
    for row in rows[1:]:
        prev_y_max = max(g["bbox"][3] for g in current_region)
        this_y_min = min(g["bbox"][1] for g in row)
        gap = this_y_min - prev_y_max
        if gap <= ROW_MERGE_PT:
            current_region.extend(row)
        else:
            regions.append(current_region)
            current_region = list(row)
    regions.append(current_region)

    # Filter regions with too few glyphs
    return [r for r in regions if len(r) >= MIN_MATH_GLYPHS]


# ---------------------------------------------------------------------------
# Step 4: Score each candidate region
# ---------------------------------------------------------------------------

def extract_vector_rules(page: pymupdf.Page) -> list[dict]:
    """Extract horizontal line segments (fraction bars, vinculum) from vector paths."""
    rules = []
    for path in page.get_drawings():
        rect = path.get("rect")
        if rect is None:
            continue
        x0, y0, x1, y1 = rect.x0, rect.y0, rect.x1, rect.y1
        width = x1 - x0
        height = y1 - y0
        # Horizontal rule: wide relative to height, thin
        if width > 4.0 and height < 2.5 and width > height * 4:
            rules.append({"rect": [x0, y0, x1, y1], "width_pt": round(width, 2)})
    return rules


def score_region(region: list[dict], vector_rules: list[dict]) -> dict:
    """Compute a composite candidate score for a region."""
    bbox = _bbox_union([g["bbox"] for g in region])
    total_glyphs = len(region)
    math_count = sum(1 for g in region if g["is_math_font"])
    relation_count = sum(1 for g in region if g["is_relation"])

    # Density: fraction of glyphs that are math-font
    density_score = math_count / total_glyphs if total_glyphs > 0 else 0.0

    # Relation score: at least one relational operator present → 1.0
    relation_score = min(1.0, relation_count / 1.0) if relation_count > 0 else 0.0

    # Vector rule score: fraction bar or radical intersects region bbox
    vector_score = 0.0
    for rule in vector_rules:
        rx0, ry0, rx1, ry1 = rule["rect"]
        if (bbox[0] - 2.0 <= rx0 and rx1 <= bbox[2] + 2.0 and
                bbox[1] <= ry0 <= bbox[3]):
            vector_score = 1.0
            break

    composite = (
        W_DENSITY * density_score
        + W_RELATION * relation_score
        + W_VECTOR * vector_score
    )

    return {
        "bbox": [round(x, 3) for x in bbox],
        "glyph_count": total_glyphs,
        "math_glyph_count": math_count,
        "relation_glyph_count": relation_count,
        "has_vector_rule": vector_score > 0.0,
        "density_score": round(density_score, 4),
        "relation_score": round(relation_score, 4),
        "vector_score": round(vector_score, 4),
        "composite_score": round(composite, 4),
    }


# ---------------------------------------------------------------------------
# Step 5: Collect sealed reference bboxes for post-hoc adjudication
#         (read AFTER candidate generation is complete)
# ---------------------------------------------------------------------------

SEALED_FIXTURE_IDS = ["PIAA-001", "PIAA-002", "PIAA-003", "PIAA-004", "PIAA-005"]


def load_sealed_bboxes() -> dict[str, list[float]]:
    """Read sealed reference bboxes from manifest for post-hoc IoU adjudication.

    This function is called AFTER candidate generation is complete.
    It MUST NOT be called during candidate generation (steps 1-4).
    """
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    sealed: dict[str, list[float]] = {}
    for fixture in manifest["fixtures"]:
        fid = fixture["fixture_id"]
        if fid not in SEALED_FIXTURE_IDS:
            continue
        tiers = fixture.get("target_tiers", {})
        # Use display_block bbox (primary tier) or inline_block_1
        for tier_key in ("display_block", "inline_block_1"):
            if tier_key in tiers and "bbox" in tiers[tier_key]:
                sealed[fid] = tiers[tier_key]["bbox"]
                break

    return sealed


def adjudicate_candidates(
    candidates: list[dict],
    sealed_bboxes: dict[str, list[float]],
) -> dict:
    """Post-hoc IoU matching of candidates against sealed reference bboxes."""
    matched_fixtures: set[str] = set()
    per_fixture_best: dict[str, dict] = {}

    for fid, ref_bbox in sealed_bboxes.items():
        best_iou = 0.0
        best_cand = None
        for cand in candidates:
            iou = _iou(cand["bbox"], ref_bbox)
            if iou > best_iou:
                best_iou = iou
                best_cand = cand
        per_fixture_best[fid] = {
            "best_iou": round(best_iou, 4),
            "matched": best_iou >= IOU_MATCH_THRESHOLD,
            "best_candidate_bbox": best_cand["bbox"] if best_cand else None,
        }
        if best_iou >= IOU_MATCH_THRESHOLD:
            matched_fixtures.add(fid)

    return {
        "per_fixture": per_fixture_best,
        "matched_fixture_ids": sorted(matched_fixtures),
        "total_matched": len(matched_fixtures),
        "total_sealed": len(sealed_bboxes),
    }


# ---------------------------------------------------------------------------
# Main discovery runner
# ---------------------------------------------------------------------------

def run_g0_discovery() -> dict:
    """Execute PIAA-010 G0 unconstrained full-page discovery.

    Returns the full output dict (also written to OUTPUT_PATH).
    """
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    # --- CANDIDATE GENERATION PHASE (no oracle reads) ---
    doc = pymupdf.open(str(PDF_PATH))
    page = doc[TARGET_PAGE_IDX]
    page_rect = page.rect

    all_glyphs = extract_full_page_glyphs(page)
    math_glyphs = filter_math_glyphs(all_glyphs)
    regions = cluster_into_regions(math_glyphs)
    vector_rules = extract_vector_rules(page)

    candidates_raw = []
    for region in regions:
        scored = score_region(region, vector_rules)
        candidates_raw.append(scored)

    # Sort descending by composite score
    candidates_sorted = sorted(
        candidates_raw, key=lambda c: c["composite_score"], reverse=True
    )

    # Assign candidate IDs
    candidates: list[dict] = []
    for rank, cand in enumerate(candidates_sorted, start=1):
        candidates.append({
            "candidate_id": f"G0-{rank:03d}",
            "rank": rank,
            **cand,
        })

    doc.close()

    # --- POST-HOC ADJUDICATION PHASE (oracle read permitted here) ---
    sealed_bboxes = load_sealed_bboxes()
    adjudication = adjudicate_candidates(candidates, sealed_bboxes)

    output = {
        "discovery_id": "PIAA-010-G0-UNCONSTRAINED",
        "source_document": {
            "arxiv_id": "2605.25821",
            "pdf_path": str(PDF_PATH),
            "page_idx_0based": TARGET_PAGE_IDX,
            "page_dimensions_pt": [page_rect.width, page_rect.height],
        },
        "policy": {
            "oracle_coordinates_allowed": False,
            "fixture_annotations_read_during_generation": False,
            "iou_match_threshold": IOU_MATCH_THRESHOLD,
        },
        "extraction_summary": {
            "total_glyphs_on_page": len(all_glyphs),
            "math_font_glyphs": len(math_glyphs),
            "raw_regions_before_filter": len(
                [r for r in regions]  # already filtered
            ) + sum(1 for c in candidates_raw if c["glyph_count"] < MIN_MATH_GLYPHS),
            "candidate_regions_proposed": len(candidates),
        },
        "candidates": candidates,
        "post_hoc_adjudication": adjudication,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_g0_discovery()
    summary = result["extraction_summary"]
    adj = result["post_hoc_adjudication"]

    print(f"G0 Discovery complete.")
    print(f"  Total glyphs on page:     {summary['total_glyphs_on_page']}")
    print(f"  Math-font glyphs:         {summary['math_font_glyphs']}")
    print(f"  Candidate regions:        {summary['candidate_regions_proposed']}")
    print()
    print(f"Post-hoc adjudication (IoU >= {result['policy']['iou_match_threshold']}):")
    for fid, info in adj["per_fixture"].items():
        mark = "✓" if info["matched"] else "✗"
        print(f"  {mark} {fid}  IoU={info['best_iou']:.4f}")
    print(f"\n  Matched: {adj['total_matched']}/{adj['total_sealed']} fixtures")
    print(f"\nOutput: {OUTPUT_PATH}")
