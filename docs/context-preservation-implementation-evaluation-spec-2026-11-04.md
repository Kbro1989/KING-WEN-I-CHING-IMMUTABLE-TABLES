# Context-Preservation Implementation and Evaluation Specification

**Date:** 2026-11-04
**Document:** `docs/context-preservation-implementation-evaluation-spec-2026-11-04.md`
**Status:** Read-only specification. No implementation authority. No source changes authorized.
**Depends on:** `docs/glyph-catalog-template-matching-p1-spec-2026-11-03.md` (P1 recognition spec, read-only)
**Governs:** Context preservation as a prerequisite to catalog-backed recognition

---

## 1. Purpose and Authorization

This specification defines a **context-preservation workstream** that is independent from, and prerequisite to, the P1 glyph-catalog recognition workstream. It establishes that mathematical context must be preserved before any recognition work begins.

### Authorization boundary

- **Read-only specification.** No source changes, no baseline changes, no acceptance claims.
- **Implementation requires separate explicit authorization.** The P1 spec authorization does not extend to this workstream.
- **No frozen baseline may be modified.** Original crops, corrected clips, and `baseline_frozen_padding15.jsonl` remain immutable.
- **No implementation may be authorized by this document alone.**

### Relationship to P1

The P1 specification assumes context-inclusive recognition (§6.1 point 3). This document exposes a dependency that P1 does not explicitly address: the preservation of multi-line context before recognition. This is an **additive specification update**, not a retroactive claim that P1 already satisfies it.

```
Context Preservation (this spec)  -->  P1 Recognition (glyph-catalog-template-matching-p1-spec)
        prerequisite                              dependent
```

---

## 2. Current-State Evidence

### 2.1 Candidate Population

| Metric | Value |
|---|---|
| Total candidates | 4,730 |
| Papers | 6 (1907.04931, 2104.01277, 2205.01395, 2206.00364, 2605.22902, 2605.27315) |
| Pages with candidates | 127 |
| Classifications | true_equation: 1,808 / inline_math: 2,366 / isolated_symbol: 556 |

### 2.2 Spatial Layout Evidence

| Metric | Value |
|---|---|
| Pages with multi-line clusters (gap < 5pt) | 118 / 127 (92.9%) |
| Total multi-line clusters | 1,000 |
| Max cluster size | 43 candidates |
| Isolated candidates (no neighbor within 5pt) | 348 (7.4%) |
| Clustered candidates | 4,382 (92.6%) |
| Overlapping bbox pairs (gap < 0) | 2,882 (60.9%) |
| Largest vertical span | 141.8pt (25 candidates, page 64 of 2104.01277) |
| Tall bboxes (>20pt height) | 84 (1.8%) |
| Very small bboxes (<10pt in either dimension) | 2,182 (46.1%) |
| Wide bboxes (>100pt width) | 51 (1.1%) |

### 2.3 Crop Pipeline Evidence

| Parameter | Current value | Assessment |
|---|---|---|
| Crop padding | (3, 2) points | Insufficient for multi-line context |
| Multi-line grouping in main loop | Not implemented | `detect_math_regions_on_page()` exists but not called |
| Context expansion in main loop | Not implemented | `expand_crop_context()` exists but not called |
| Multi-scale recognition in main loop | Not implemented | `recognize_formula_multiscale()` exists but not called |
| Catalog image comparison | Not implemented | 3,304 glyphs loaded, 0 comparisons |

### 2.4 Important Distinction

**92.6% of candidates belong to multi-line clusters.** This establishes **exposure to context fragmentation**, not proof of information loss. Actual information loss requires comparison against the original page and mathematical relationships. This distinction must remain explicit in all evaluations.

---

## 3. Three Independent Limitations

These limitations are related but are **not the same defect**. They must be tracked separately.

### 3.1 Coverage Limitation

The crop pipeline does not preserve enough surrounding mathematical context. Current crops capture only the exact bounding box with minimal padding (3, 2 points). Multi-line expressions, stretched symbols, and surrounding prose are excluded.

**Evidence:** 92.6% multi-line cluster membership; 60.9% overlapping bbox pairs; 141.8pt maximum vertical span.

### 3.2 Recognition Limitation

The glyph catalog (3,304 images, 1,595 unique hashes) is loaded but not connected to image-based recognition. The `glyph_catalog` naive substring match (`source_text in glyph['name']`) almost never matches full LaTeX expressions. No image-to-glyph comparison exists.

**Evidence:** P0 catalog audit (3,301 valid images, 21 cross-name hash groups); P1 spec written but implementation not authorized.

### 3.3 Structural Limitation

Spatial and mathematical relationships are not carried through the recognition path. There is no bracket pairing, no multi-line grouping, no fraction structure detection, and no superscript/subscript relationship tracking in the crop pipeline.

**Evidence:** 84 tall bboxes (>20pt) with no dedicated handling; 51 wide bboxes (>100pt) with no multi-line grouping; no open/close bracket correspondence tracking.

---

## 4. Full-Region Geometry

### 4.1 Requirements

Every candidate must retain its original page coordinates. Region detection must produce full-region boundaries. Candidate-to-region membership must be recorded. No candidate may be silently reduced to an independent glyph.

### 4.2 Region Detection

Connected-component grouping (`detect_math_regions_on_page()`) identifies likely regions. Region detection is a **proposal mechanism**, not mathematical parsing. It proposes that certain components belong together spatially. It does not establish that they form a fraction, that a symbol is a superscript, or that consecutive lines belong to the same equation.

### 4.3 Page Coordinate Preservation

All region boundaries and candidate memberships must be expressed in original page coordinates (PDF points). No transformation to crop-local coordinates may discard the page-level spatial relationship.

---

## 5. Context-Preserving Crops

### 5.1 Multiple Representations Required

For every candidate, three representations must be retained together:

| Representation | Source | Purpose |
|---|---|---|
| Original crop | `crop_pdf_region()` with (3, 2) padding | Existing baseline; immutable |
| Expanded crop | `expand_crop_context()` with adaptive factor | Context-inclusive view |
| Full-region crop | `detect_math_regions_on_page()` region bbox | Multi-line context |

### 5.2 Provenance Linkage

Every expanded or full-region crop must retain a link to its original crop. The original crop is never overwritten or replaced. Transformations are additive.

### 5.3 Adaptive Context Expansion

Padding must not be a universal constant. Expansion factor must be based on region geometry:

- Small isolated symbols: minimal expansion (1.2×)
- Inline math: moderate expansion (1.5×)
- Display equations: larger expansion (2.0×)
- Multi-line clusters: full region span (all candidates in cluster)

---

## 6. Structural Evidence

### 6.1 Tall Symbols (Stretched Delimiters and Operators)

Symbols spanning > 15pt height (2-3 lines of normal text) require dedicated evaluation. These include:
- Stretched brackets: `\left(`, `\right)`, `\left[`, `\right]`, `\left\{`, `\right\}`
- Large operators: `\sum`, `\int`, `\prod`, `\bigcup`, `\bigcap`
- Fraction bars extending beyond numerator/denominator

**Current handling:** `detect_border_contamination()` with `vertical_border_strokes` and `stretched_symbols_at_border` detects tall symbols at crop borders but does not capture their full extent.

### 6.2 Delimiter Pairing Hypotheses

A left delimiter and right delimiter can be separated by substantial vertical distance. Their pairing must:
- Retain candidate identities and coordinates
- Record intervening expression membership
- Be treated as a **hypothesis**, not a confirmed mathematical relationship
- Require independent verification before being treated as structural fact

### 6.3 Multi-Line Relationships

Consecutive lines with gap < 5pt are candidates for multi-line grouping. This is a **spatial hypothesis**, not a mathematical fact. Lines may be:
- Consecutive parts of the same equation
- Separate equations in close proximity
- A display equation and its continuation

---

## 7. Five-Path Evaluation Protocol

### 7.1 Evaluation Paths

| Path | Description | What it tests |
|---|---|---|
| Original crops | Existing `(3, 2)` padding crops | Current baseline |
| Expanded crops | Adaptive context expansion | Effect of increased padding |
| Adaptive crops | Region-aware boundaries based on geometry | Effect of geometry-aware context |
| Full-region recognition | All candidates in a region processed together | Effect of retaining multi-line context |
| Full-region + catalog | Full-region with catalog-backed retrieval | Incremental visual reference contribution |

**Path 5 is a later dependent experiment.** It must not obscure whether context preservation alone (paths 2-4) improved results.

### 7.2 Three Independent Outcome Measurements

| Outcome | Definition | Measurement |
|---|---|---|
| **Recognition** | Was the symbol identified correctly? | Match against adjudicated reference |
| **Structural reconstruction** | Were relationships between symbols and lines preserved? | Multi-line grouping accuracy, bracket pairing correctness |
| **Source fidelity** | Is the reconstruction supported by the original page? | Comparison against original PDF rendering |

These three outcomes are **independent**. An improvement in recognition does not imply an improvement in structural reconstruction. A structural hypothesis may be correct without being source-faithful.

### 7.3 Evaluation Rules

- Do not overwrite original crops or frozen baseline.
- Preserve all representations (original, expanded, adaptive, full-region) for comparison.
- Report results per-path, per-outcome, per-candidate.
- Do not merge outcomes into a single score.

---

## 8. Context Preservation Gate

### 8.1 Entry Criteria

Before any context-preservation implementation may begin, all of the following must be established:

- [ ] Every candidate retains its original page coordinates.
- [ ] Candidate-to-region membership is recorded.
- [ ] Expanded crops retain links to their original crops.
- [ ] Multi-line regions are not silently reduced to independent glyphs.
- [ ] Structural relationships remain hypotheses until independently evaluated.
- [ ] Original and expanded representations remain available together.

### 8.2 Acceptance Conditions

Context preservation is accepted only when:

1. Region detection produces measurable, reproducible region boundaries.
2. Candidate-to-region membership is recorded for every candidate.
3. At least one evaluation path (expanded, adaptive, or full-region) demonstrates measurable improvement in at least one of the three outcomes (recognition, structural reconstruction, source fidelity) compared to the original-crop baseline.
4. No information loss is introduced (no candidate disappears during region grouping).
5. Original crops and frozen baseline remain unmodified.

---

## 9. Baseline and Provenance Protections

### 9.1 Immutable Artifacts

The following must never be modified during context-preservation work:

- `DATASETS/vision_comparison/baseline_frozen_padding15.jsonl`
- All files in `DATASETS/vision_comparison/crop_verification_renders/`
- All files in `DATASETS/vision_comparison/candidate_visual_audit_renders/`
- All files in `DATASETS/vision_comparison/crop_isolation_experiment/`

### 9.2 Traceable Transformations

Every transformation (crop expansion, region grouping, context extraction) must produce:
- Input reference (original crop path or candidate ID)
- Transformation type and parameters
- Output reference (new crop path or region ID)
- Timestamp

### 9.3 No Silent Replacement

Original crops are never overwritten. Expanded crops are new files. Full-region crops are new files. The original remains the baseline for all comparisons.

---

## 10. Dependencies and Authorization Boundary

### 10.1 Dependency Chain

```
Context Preservation (this spec)
    |
    v
P1 Recognition (glyph-catalog-template-matching-p1-spec-2026-11-03.md)
    |
    v
P1 Implementation (requires separate authorization)
```

Context preservation is a **prerequisite** to P1 recognition. P1 recognition assumes context-inclusive crops (§6.1 point 3). Without context preservation, P1 recognition operates on fragments.

### 10.2 Authorization

- This specification is **read-only**. No implementation authority.
- Implementation requires **separate explicit authorization**.
- The P1 spec authorization does not extend to this workstream.
- No source changes, no baseline changes, no acceptance claims.

---

## 11. Region-to-Candidate Lineage Record

Every candidate must be linked to its region through a lineage record. Region membership and mathematical relationships are **different facts**. A candidate can belong to a region without being mathematically connected to every other candidate in it.

### 11.1 Lineage Schema

| Field | Type | Purpose |
|---|---|---|
| `page_id` | string | Original page identity (paper_id + page number) |
| `candidate_id` | string | Existing crop identity (candidate index or UUID) |
| `region_id` | string | Proposed full-region identity (region index or UUID) |
| `original_bbox` | object | Original crop coordinates (x0, y0, x1, y1 in PDF points) |
| `region_bbox` | object | Full-region coordinates (x0, y0, x1, y1 in PDF points) |
| `membership_evidence` | string | Why the candidate belongs to the region (spatial proximity, connected component, vertical adjacency, etc.) |
| `expanded_crop_id` | string | Link to additional representation (expanded crop file path or ID) |
| `structural_status` | enum | `unclassified` / `hypothesized` / `verified` |

### 11.2 Structural Status Semantics

| Status | Meaning |
|---|---|
| `unclassified` | No structural hypothesis has been formed |
| `hypothesized` | A spatial or mathematical relationship has been proposed but not verified |
| `verified` | The relationship has been independently confirmed against source evidence |

### 11.3 Lineage Rules

1. `region_id` must be unique per page.
2. `candidate_id` must be unique per page.
3. A candidate may belong to exactly one region.
4. A region may contain one or more candidates.
5. `membership_evidence` must be non-empty and describe the spatial basis for membership.
6. `structural_status` defaults to `unclassified`. It may only advance to `hypothesized` or `verified` through explicit evaluation, never by assumption.
7. `original_bbox` is immutable once recorded.
8. `region_bbox` is computed from the union of all member candidate bboxes plus padding, not from a separate detection.

---

## 12. Summary

This specification establishes context preservation as a **prerequisite** to recognition. It does not implement anything. It defines:

1. What must be preserved (page coordinates, region boundaries, candidate membership, multiple representations).
2. How it must be preserved (provenance linkage, no silent replacement, traceable transformations).
3. How it must be evaluated (5 paths, 3 outcomes, no overwriting).
4. What gates must be passed (Context Preservation Gate with 6 entry criteria and 5 acceptance conditions).
5. What lineage must be recorded (region-to-candidate linkage with structural status).

**The three limitations (coverage, recognition, structural) remain separately tracked.**

**The frozen baseline remains protected.**

**Implementation remains unauthorized.**
