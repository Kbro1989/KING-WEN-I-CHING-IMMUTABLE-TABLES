# Context-Preservation Measurement-Enrichment Schema Specification

## Version: context-preservation-v1
## Status: Specification only — no implementation authorized
## Date: 2026-11-04

---

## 1. Purpose

This specification defines a versioned, additive measurement-enrichment schema for the 988-page representative-page evaluation. It describes how derived measurements are layered on top of existing execution evidence without modifying the original records.

## 2. Governing Rules

1. **The original JSONL is immutable.** `DATASETS/vision_comparison/representative_page_evaluation.jsonl` (988 page records + 2 coverage summaries = 990 lines) must not be modified, rewritten, or appended to.
2. **Missing measurements are null, not zero.** A field that was not captured during execution must be `null` or `"unavailable"`, never `0` or `false`.
3. **Original observations are preserved.** Recomputed values occupy separate fields with documented derivation. The original value (even if suspect) is never replaced.
4. **Enrichment ≠ acceptance.** Creating an enrichment record does not establish G2–G6 gate satisfaction.
5. **Enrichment ≠ pipeline integration.** No enrichment record authorizes wiring functions into `process_candidates()`.

## 3. Source Evidence

| Field | Value |
|---|---|
| Source file | `DATASETS/vision_comparison/representative_page_evaluation.jsonl` |
| Page records | 988 |
| Coverage summaries | 2 |
| Total lines | 990 |
| Papers | 16 |
| Execution IDs | Per-record `execution_id` (UUID, stable) |
| Population scope | `population_scope` field per record |
| Timestamp | `run_timestamp` per record |

## 4. Stable Linkage

Every enrichment record links to exactly one source page record via:

| Linkage Field | Source Field | Type | Description |
|---|---|---|---|
| `source_execution_id` | `execution_id` | string (UUID) | Stable identifier from original record |
| `source_paper_id` | `paper_id` | string | Paper identifier (e.g., "2605.00155") |
| `source_page_number` | `page_number` | integer | 1-indexed page within paper |
| `source_run_timestamp` | `run_timestamp` | string (ISO 8601) | When the original evaluation was executed |
| `source_population_scope` | `population_scope` | string | Population identifier (e.g., "benchmark-16-paper") |
| `source_jsonl_path` | — | string (path) | Path to the source JSONL file |

## 5. Measurement Origin Tags

Every measurement value carries an origin tag:

| Tag | Meaning |
|---|---|
| `observed_original` | Captured during the original 988-page execution; present in source JSONL |
| `derived_existing_data` | Computed from data already present in the source JSONL; no additional execution required |
| `recomputed_source_crop` | Computed from source PDF crops; requires accessing original page geometry and rendering |
| `unavailable` | Not captured, not derivable from existing data, and not yet computed |

## 6. Schema Definition

### 6.1 Top-Level Enrichment Record

```json
{
  "measurement_schema": "context-preservation-v1",
  "enrichment_version": "1.0.0",
  "enrichment_timestamp": "<ISO 8601>",
  "source_linkage": {
    "source_execution_id": "<UUID>",
    "source_paper_id": "<string>",
    "source_page_number": "<integer>",
    "source_run_timestamp": "<ISO 8601>",
    "source_population_scope": "<string>",
    "source_jsonl_path": "DATASETS/vision_comparison/representative_page_evaluation.jsonl"
  },
  "execution_status_preserved": "<pass|partial|fail>",
  "measurements": {
    "A": { ... },
    "R": { ... },
    "D": { ... },
    "E": { ... },
    "B": { ... },
    "L": { ... }
  },
  "derivation_versions": { ... },
  "provenance_notes": [ ... ]
}
```

### 6.2 Dimension A — Region Area

```json
"A": {
  "measurement_origin": "observed_original",
  "region_count": "<integer>",
  "area_px": {
    "min": "<number>",
    "max": "<number>",
    "mean": "<number>",
    "median": "<number>",
    "per_region": [ "<number>", ... ]
  },
  "is_complex_count": "<integer>",
  "is_complex_ratio": "<number>"
}
```

**Source:** `functions.detect_math_regions_on_page.region_count` and `regions[].area_px`, `regions[].is_complex`
**Derivation:** Direct read from existing JSONL. No computation required.
**Origin tag:** `observed_original`

### 6.3 Dimension R — Content Ratio

```json
"R": {
  "measurement_origin": "unavailable",
  "per_region": [],
  "threshold": 0.01,
  "render_scale": 4,
  "grayscale_threshold": 250,
  "pixel_ratio_formula": "np.mean(gray < 250)",
  "crop_source": null,
  "derivation_notes": "Content ratio not captured in original execution. Requires source-crop processing or rerunning expand_crop_context(). detect_border_contamination() does not return content ratio."
}
```

**Source:** Not available in existing JSONL. `expand_crop_context()` computes `np.mean(gray < 250)` internally but does not store it.
**Derivation path:** Process original PDF crops (page number + original bbox + zoom) through standalone content-ratio computation, or rerun `expand_crop_context()` with an added field.
**Origin tag:** `unavailable` (until computed)
**When populated:** `recomputed_source_crop`

**Required provenance fields when populated:**
- `crop_source`: path to source PDF
- `render_scale`: zoom level used (4)
- `grayscale_threshold`: pixel value threshold (250)
- `pixel_ratio_formula`: formula used ("np.mean(gray < 250)")
- `crop_identity`: page number + original bbox + region index

### 6.4 Dimension D — Boundary Density

```json
"D": {
  "measurement_origin": "derived_existing_data",
  "page_boundary_count": "<integer>",
  "page_area_px": "<integer>",
  "page_density": "<number>",
  "math_boundary_count": "<integer>",
  "text_boundary_count": "<integer>",
  "region_density": [
    {
      "region_index": "<integer>",
      "region_area_px": "<number>",
      "intersecting_boundaries": "<integer>",
      "region_density": "<number>"
    }
  ]
}
```

**Source:** `functions.extract_text_boundaries.total_boundaries`, `math_boundaries`, `text_boundaries`; `functions.detect_math_regions_on_page.regions[].bbox`; `boundaries[].bbox`; `page_dimensions`
**Derivation:**
- `page_area_px` = `page_dimensions[0] × page_dimensions[1] × zoom²` (rendered pixels)
- `page_density` = `page_boundary_count / page_area_px`
- `region_density` = for each region, count boundaries whose bbox intersects region bbox, divided by region area

**Origin tag:** `derived_existing_data`

### 6.5 Dimension E — Eligibility

```json
"E": {
  "measurement_origin": "observed_original",
  "eligible": "<boolean>",
  "skip_reason": "<string|null>",
  "threshold": 0.01,
  "expansion_ratio": "<number|null>",
  "expansion_params": {
    "expand_factor": 1.5,
    "zoom": 4,
    "min_content_ratio": 0.01
  },
  "original_bbox": [ "<number>", "<number>", "<number>", "<number>" ]
}
```

**Source:** `functions.expand_crop_context.status`, `reason`, `original_bbox`, `expansion_ratio`; threshold from source code
**Derivation:** Direct read. `eligible = (status == 'pass')`.
**Origin tag:** `observed_original`

**Important qualification:** Eligibility is not preservation quality. A passing page does not demonstrate context preservation. A skipped page does not demonstrate information loss.

### 6.6 Dimension B — Boundary Correspondence

```json
"B": {
  "region_boundary_overlaps_original": 0,
  "region_boundary_overlaps_recomputed": "<integer|null>",
  "matched_boundaries": "<integer|null>",
  "unmatched_boundaries": "<integer|null>",
  "overlap_ratio": "<number|null>",
  "per_region": [
    {
      "region_index": "<integer>",
      "intersecting_boundary_count": "<integer>",
      "region_boundary_overlap_ratio": "<number>"
    }
  ],
  "derivation_notes": "Original value 0 preserved as observed. Recomputed value derived from bbox intersection. If recomputed differs from original, the original computation is flagged as defective."
}
```

**Source:** `lineage.region_boundary_overlaps` (original, value 0 in all records); `functions.detect_math_regions_on_page.regions[].bbox`; `functions.extract_text_boundaries.boundaries[].bbox`
**Derivation:**
- `region_boundary_overlaps_recomputed` = count of region-boundary pairs whose bboxes intersect
- `matched_boundaries` = count of unique boundaries that intersect at least one region
- `unmatched_boundaries` = `total_boundaries - matched_boundaries`
- `overlap_ratio` = `matched_boundaries / total_boundaries`
- `per_region` = for each region, count intersecting boundaries and compute ratio

**Origin tag:** `derived_existing_data` (for recomputed values); `observed_original` (for original 0)

**Critical finding:** The original `region_boundary_overlaps` is 0 in all 988 records. This appears to be a computation bug (bbox data exists for both regions and boundaries). The recomputed value is stored separately. If the recomputed value differs from 0, the original computation is documented as defective, not overwritten.

### 6.7 Dimension L — Lineage

```json
"L": {
  "measurement_origin": "unavailable",
  "region_count": "<integer>",
  "boundary_count": "<integer>",
  "partial_count": "<integer>",
  "candidate_count": null,
  "traced_count": null,
  "unresolved_count": null,
  "failed_count": null,
  "completeness_ratio": null,
  "all_candidates_traced": false,
  "lineage_entries": [],
  "derivation_notes": "Summary counts (region, boundary, partial) are observed_original. Per-candidate lineage entries were not captured during execution (lineage_entries is empty in all 988 records). Candidate-level tracing requires runner modification and rerun."
}
```

**Source:** `lineage.region_count`, `lineage.boundary_count`, `lineage.partial_count`, `lineage.all_candidates_traced`, `lineage.lineage_entries`
**Derivation:** Summary counts are direct reads. Per-candidate trace data is not available.
**Origin tag:** `observed_original` (for summary counts); `unavailable` (for candidate-level traces)

**Important qualification:** `all_candidates_traced: false` in all 988 records means the runner did not attempt per-candidate tracing. This is not a failure of tracing; it is an absence of tracing. The distinction between "not attempted" and "attempted and failed" must be preserved.

---

## 7. Derivation Versions

```json
"derivation_versions": {
  "A": "1.0.0",
  "R": null,
  "D": "1.0.0",
  "E": "1.0.0",
  "B": "1.0.0",
  "L": null
}
```

Each derived dimension records the version of the derivation algorithm used. If the algorithm changes, the version increments and prior enrichment records remain valid under their recorded version.

---

## 8. Provenance Requirements

Every enrichment record must include:

1. **Measurement origin** — tagged per dimension (observed_original, derived_existing_data, recomputed_source_crop, unavailable)
2. **Derivation version** — algorithm version for each derived dimension
3. **Source linkage** — execution_id, paper_id, page_number, run_timestamp, population_scope, source JSONL path

These three requirements prevent a later enrichment from appearing as something the original execution actually measured.

---

## 9. Governance Constraints

This specification is **documentation only**. The following are explicitly prohibited until authorized:

1. Modifying the original 988-page JSONL
2. Treating missing measurements (R, L candidate-level) as zero
3. Replacing original observations (B's 0) with recomputed values
4. Treating successful enrichment as G2–G6 acceptance
5. Wiring `process_candidates()` into the pipeline
6. Claiming the 12-crop border detector pilot (25% false positive) as a validated production estimate

---

## 10. Recommended Next Step

Create a **read-only field-availability and derivation matrix** — already completed at `docs/field-availability-and-derivation-matrix-2026-11-04.md`.

The next artifact after this specification is a **measurement-enrichment implementation plan** that:
- Defines the enrichment script (read-only, additive output)
- Specifies the enrichment JSONL file path and format
- Documents which dimensions can be populated from existing data vs. require rerun
- Establishes the governance gate for authorizing enrichment execution

No enrichment execution, no pipeline changes, and no gate claims are authorized by this specification.