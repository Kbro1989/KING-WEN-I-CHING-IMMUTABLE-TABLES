# Field-Availability and Derivation Matrix

## Purpose

This matrix documents, for each measurement dimension in the proposed X=(A,R,D,E,B,L) vector, the source function, existing JSONL field, derivation formula, required additional data, and whether reconstruction is possible without rerunning the pipeline.

## Authority

- Source JSONL: `DATASETS/vision_comparison/representative_page_evaluation.jsonl`
- 988 page records + 2 coverage summaries = 990 lines
- Schema version: current (no versioned measurement schema yet)

---

## Dimension A — Region Area

| Field | Source Function | Existing JSONL Field | Derivation Formula | Required Additional Data | Reconstruction Possible? |
|---|---|---|---|---|---|
| A.region_count | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.region_count` | Direct read | None | Yes |
| A.area_px.min | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.regions[].area_px` | `min(regions[].area_px)` | None | Yes |
| A.area_px.max | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.regions[].area_px` | `max(regions[].area_px)` | None | Yes |
| A.area_px.mean | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.regions[].area_px` | `mean(regions[].area_px)` | None | Yes |
| A.area_px.median | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.regions[].area_px` | `median(regions[].area_px)` | None | Yes |
| A.area_px.per_region | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.regions[].area_px` | Direct read | None | Yes |
| A.is_complex_count | `detect_math_regions_on_page()` | `functions.detect_math_regions_on_page.regions[].is_complex` | `sum(is_complex)` | None | Yes |

**Status: Fully reconstructable from existing JSONL. No rerun required.**

---

## Dimension R — Content Ratio

| Field | Source Function | Existing JSONL Field | Derivation Formula | Required Additional Data | Reconstruction Possible? |
|---|---|---|---|---|---|
| R.per_region | `expand_crop_context()` | **Not captured** | `np.mean(gray < 250)` on expanded crop | Original PDF, page number, expanded bbox, zoom level, crop pixels | **No** — not stored in JSONL |
| R.threshold | `expand_crop_context()` | Hardcoded `min_content_ratio=0.01` in function signature | Direct read from source code | None (constant) | Yes (from source) |
| R.render_scale | `run_representative_page_evaluation.py` | `zoom` (top-level, value=4) | Direct read | None | Yes |

**Status: NOT reconstructable from existing JSONL. Requires rerunning `expand_crop_context()` or processing source crops.**

**Critical finding:** `detect_border_contamination()` does NOT compute or return content ratio. Its return contract is:
- `contaminated`: boolean
- `borders`: dict of per-border stroke counts
- `edge_pixel_counts`: per-border pixel counts
- `border_density`: per-border density
- `overall_density`: overall edge density
- `bracket_contacts`, `vertical_border_strokes`, `horizontal_border_strokes`, `unmatched_brackets_at_border`, `stretched_symbols_at_border`, `has_left_vertical`, `has_right_vertical`

None of these is the content ratio (non-white pixels / total pixels). Content ratio is computed inside `expand_crop_context()` as `np.mean(gray < 250)` but is not stored in the output dict.

**Derivation path:** To populate R, either:
1. Rerun `expand_crop_context()` with an added field storing the content ratio, or
2. Process the original PDF crops (page number + original bbox + zoom) through a standalone content-ratio computation.

Option 2 is preferred because it does not require rerunning the full evaluation pipeline. The original bbox is stored in `expand_crop_context.original_bbox` for pass records and `original_bbox` for skip records. The page number and paper_id are top-level fields. The zoom (4) is stored top-level.

---

## Dimension D — Boundary Density

| Field | Source Function | Existing JSONL Field | Derivation Formula | Required Additional Data | Reconstruction Possible? |
|---|---|---|---|---|---|
| D.page_boundary_count | `extract_text_boundaries()` | `functions.extract_text_boundaries.total_boundaries` | Direct read | None | Yes |
| D.page_area | `detect_math_regions_on_page()` | `page_dimensions` (top-level: [width, height]) | `width × height` (document space, not rendered) | None | Yes (document-space area; rendered area = width × height × zoom²) |
| D.page_density | Derived | `total_boundaries / page_area` | `total_boundaries / (width × height)` | None | Yes |
| D.region_density | Derived | `regions[].bbox` + `boundaries[].bbox` | Count boundaries whose bbox intersects each region bbox / region area | None | Yes (bbox data exists in JSONL) |

**Status: Fully reconstructable from existing JSONL. No rerun required.**

**Important qualification:** Page-level density and region-level density are different measurements. Page density = boundaries / page area. Region density = boundaries intersecting a region / region area. The JSONL stores bbox for both regions and boundaries, so region-level density can be computed without rerunning.

---

## Dimension E — Eligibility

| Field | Source Function | Existing JSONL Field | Derivation Formula | Required Additional Data | Reconstruction Possible? |
|---|---|---|---|---|---|
| E.eligible | `expand_crop_context()` | `functions.expand_crop_context.status` | `status == 'pass'` | None | Yes |
| E.skip_reason | `expand_crop_context()` | `functions.expand_crop_context.reason` | Direct read (null if pass) | None | Yes |
| E.threshold | `expand_crop_context()` | Hardcoded in source | `0.01` (from `min_content_ratio=0.01`) | None (constant in source) | Yes (from source code) |
| E.expansion_ratio | `expand_crop_context()` | `functions.expand_crop_context.expansion_ratio` (pass records only) | Direct read (null if skip) | None | Yes |
| E.expansion_params | `run_representative_page_evaluation.py` | Not explicitly stored | `expand_factor=1.5, zoom=4, min_content_ratio=0.01` | Source code | Yes (from source code) |

**Status: Fully reconstructable from existing JSONL. No rerun required.**

**Important qualification:** Eligibility is not preservation quality. A page that passes expansion (eligible=true) does not demonstrate that context was preserved. A page that skips (eligible=false) does not demonstrate information loss. These are separate measurements.

---

## Dimension B — Boundary Correspondence

| Field | Source Function | Existing JSONL Field | Derivation Formula | Required Additional Data | Reconstruction Possible? |
|---|---|---|---|---|---|
| B.overlap_count | `run_representative_page_evaluation.py` (lineage) | `lineage.region_boundary_overlaps` | Direct read | None | Yes (but value is 0 in all 988 records — see note) |
| B.matched_boundaries | Derived | Not directly stored | Count of boundaries whose bbox intersects at least one region bbox | None (bbox data exists) | Yes (compute from bbox intersection) |
| B.unmatched_boundaries | Derived | Not directly stored | `total_boundaries - matched_boundaries` | None | Yes |
| B.per_region | Derived | Not directly stored | For each region: count boundaries whose bbox intersects region bbox | None | Yes (compute from bbox data) |
| B.overlap_ratio | Derived | Not directly stored | `matched_boundaries / total_boundaries` | None | Yes |

**Status: Fully reconstructable from existing JSONL. No rerun required.**

**Critical finding:** `lineage.region_boundary_overlaps` is **0 in all 988 records**. This appears to be either:
1. A bug in the runner (the overlap computation returned 0), or
2. The overlap was computed using exact bbox equality (no intersection), or
3. The field was populated but not correctly computed

The region and boundary bbox data IS stored in the JSONL, so B can be recomputed independently. This is a derived measurement, not an observed one. The original 0 value should be preserved (as observed) while the recomputed value is stored separately (as derived).

**Important qualification:** Overlap count alone does not demonstrate boundary preservation. A region can overlap many text boundaries while still having incorrect geometry. Normalized correspondence (per-region overlap ratios) is more informative than a global count.

---

## Dimension L — Lineage

| Field | Source Function | Existing JSONL Field | Derivation Formula | Required Additional Data | Reconstruction Possible? |
|---|---|---|---|---|---|
| L.candidate_count | `run_representative_page_evaluation.py` | Not directly stored | Total candidates processed on the page | Source data (not in JSONL) | **No** — not stored in JSONL |
| L.region_count | `detect_math_regions_on_page()` | `lineage.region_count` | Direct read | None | Yes |
| L.boundary_count | `extract_text_boundaries()` | `lineage.boundary_count` | Direct read | None | Yes |
| L.partial_count | `detect_partial_formulas()` | `lineage.partial_count` | Direct read | None | Yes |
| L.traced_count | Derived | Not stored (lineage_entries is empty in all records) | Count of candidates traced through page→region→candidate→expanded | Source data | **No** — lineage_entries is empty |
| L.unresolved_count | Derived | Not stored | Count of candidates not traced | Source data | **No** |
| L.failed_count | Derived | Not stored | Count of candidates that failed tracing | Source data | **No** |
| L.completeness_ratio | Derived | Not stored | `traced_count / candidate_count` | Source data | **No** |
| L.all_candidates_traced | `run_representative_page_evaluation.py` | `lineage.all_candidates_traced` | Direct read (false in all 988 records) | None | Yes |

**Status: Partially reconstructable.** Region, boundary, and partial counts are available. Candidate count, traced count, unresolved count, and failed count are NOT stored — `lineage_entries` is an empty array in all 988 records, and no candidate-level data was captured in the runner.

**Critical finding:** The lineage was not actually populated during the representative-page evaluation. `lineage_entries` is `[]` and `all_candidates_traced` is `false` in all 988 records. The lineage counts (region_count, boundary_count, partial_count) are summary statistics, not per-candidate traces.

To populate L fully, the runner would need to:
1. Track each candidate through detection → region membership → expansion → boundary correspondence
2. Record per-candidate trace status (traced / unresolved / failed)
3. Store the trace in `lineage_entries`

This requires modifying the runner, not just deriving from existing data.

---

## Summary: Reconstruction Feasibility

| Dimension | Reconstructable? | Requires Rerun? | Notes |
|---|---|---|---|
| A (Area) | Yes — fully | No | All data in JSONL |
| R (Content ratio) | No | Yes | Content ratio not stored; must compute from source crops |
| D (Boundary density) | Yes — fully | No | All data in JSONL |
| E (Eligibility) | Yes — fully | No | All data in JSONL |
| B (Boundary correspondence) | Yes — recomputable | No (but original 0 values are suspect) | Bbox data exists; overlap_count=0 in all records appears to be a computation bug |
| L (Lineage) | Partially | Yes (runner modification) | Summary counts available; per-candidate traces not captured |

## Recommended Next Step

Create a **measurement-enrichment record** (versioned `context-preservation-v1`) that:

1. Preserves the original 988-page JSONL unchanged.
2. Links each enriched record to its original page record via `execution_id` (stable identifier).
3. Stores derived measurements (A, D, E, B) computed from existing JSONL data.
4. Stores R (content ratio) as null until source-crop processing is authorized.
5. Stores L (lineage) as null until runner modification is authorized.
6. Records which fields are observed vs. derived vs. unavailable.

This follows the external assessment's governance rule: **do not rewrite historical records to add measurements that were not captured at execution time.** Create a separate, versioned enrichment record linked by stable identifiers.

## Governance Status

| Workstream | Status |
|---|---|
| Original execution evidence | Preserve (unchanged) |
| Field-availability matrix | Complete |
| Measurement-vector design | Ready for specification |
| Measurement enrichment | Not yet established |
| G2–G6 formal review | Pending |
| Pipeline integration | Not authorized |