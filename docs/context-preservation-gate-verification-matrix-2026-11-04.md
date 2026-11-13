# Context Preservation Gate Verification Matrix

**Date:** 2026-11-04
**Document:** `docs/context-preservation-gate-verification-matrix-2026-11-04.md`
**Status:** Read-only verification specification. No implementation authority.
**References:** `docs/context-preservation-implementation-evaluation-spec-2026-11-04.md` (330-line spec)
**Purpose:** Convert the 6 gate-entry criteria and 5 acceptance conditions into independently measurable pass/fail conditions, each with a defined measurement population, reproducible procedure, source of ground truth, and failure recording.

---

## 1. Scope

This matrix does not duplicate the 330-line context-preservation specification. It references it. It adds only what is needed for objective evaluation: measurable conditions, populations, procedures, and failure recording.

### What this matrix does NOT do

- Does not authorize implementation.
- Does not modify the frozen baseline.
- Does not change the 330-line spec.
- Does not set acceptance thresholds (those require review of §8.1 and §8.2 wording).

---

## 2. Gate-Entry Criteria Verification Matrix

Each of the 6 entry criteria from spec §8.1 must be independently measurable.

### G1: Page geometry retained

| Field | Definition |
|---|---|
| Observable pass/fail | Every candidate record contains `page_id` (paper_id + page number) and `original_bbox` (x0, y0, x1, y1 in PDF points) |
| Measurement population | All 4,730 candidates across 6 papers and 127 pages |
| Reproducible procedure | Load candidate JSON files; assert `page_id` and `original_bbox` present and non-null for every record; verify bbox coordinates match source PDF page dimensions |
| Source of ground truth | Original PDF files in `DATASETS/benchmark_pdfs/` (page dimensions) and candidate JSON files |
| Failure recording | Record candidate ID, missing field name, and paper/page for every failure; write to `gate_verification_failures.jsonl` |

**Current status:** PASS (all 4,730 candidates have page_id and bbox from PyMuPDF extraction).

### G2: Region detection precision and recall

| Field | Definition |
|---|---|
| Observable pass/fail | Region proposals contain relevant mathematical material at measurable precision and recall; over-merging and under-merging rates are reported |
| Measurement population | All 127 pages with candidates; 43-candidate cluster (page 64, paper 2104.01277) as stress case; 5 representative pages per paper for detailed adjudication |
| Reproducible procedure | Run `detect_math_regions_on_page()` on each page; compare proposed regions against adjudicated region boundaries (manual or semi-automated); compute precision = TP/(TP+FP), recall = TP/(TP+FN), over-merging = regions containing >1 distinct expression, under-merging = expressions split across >1 region |
| Source of ground truth | Adjudicated region boundaries (to be established — currently not available; requires manual or semi-automated labeling) |
| Failure recording | Record page_id, region_id, failure type (over-merge/under-merge/missed), and affected candidate IDs; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. `detect_math_regions_on_page()` exists but has not been run on any page. Adjudicated region boundaries do not yet exist. This is the primary blocker for gate evaluation.

### G3: Candidate lineage coverage

| Field | Definition |
|---|---|
| Observable pass/fail | Every original candidate is traceable to a region or explicitly recorded as unassigned; no candidate silently reduced to an independent glyph |
| Measurement population | All 4,730 candidates |
| Reproducible procedure | For each candidate, verify `candidate_id` and `original_bbox` are present; verify `region_id` is either assigned or explicitly null with `unassigned_reason`; verify no candidate has been dropped or merged without lineage record |
| Source of ground truth | Candidate JSON files (original extraction) + region detection output (when available) |
| Failure recording | Record candidate ID, paper, page, and reason for unassigned; write to `gate_verification_failures.jsonl` |

**Current status:** PARTIAL. Candidate IDs and bboxes exist. Region assignment not yet performed (depends on G2).

### G4: Context expansion linkage

| Field | Definition |
|---|---|
| Observable pass/fail | Original and transformed representations are linked; every expanded crop retains a reference to its original candidate and source-page coordinates |
| Measurement population | All 4,730 candidates (when expanded crops are generated) |
| Reproducible procedure | For each candidate, verify `expanded_crop_id` links to a file that exists on disk; verify the expanded crop's bbox contains the original bbox; verify both reference the same `page_id` |
| Source of ground truth | Original candidate JSON + expanded crop files on disk |
| Failure recording | Record candidate ID, missing/invalid link, and file path; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. No expanded crops have been generated yet. `expand_crop_context()` exists but has not been called in the main pipeline.

### G5: Structural hypothesis distinguishability

| Field | Definition |
|---|---|
| Observable pass/fail | Structural relationships are recorded as hypotheses (`hypothesized`) or verified facts (`verified`), never assumed; `unclassified` is the default |
| Measurement population | All candidates with potential structural relationships (tall symbols, multi-line clusters, delimiter pairs) |
| Reproducible procedure | For each candidate in a multi-line cluster, verify `structural_status` is one of `unclassified`/`hypothesized`/`verified`; verify no candidate has `structural_status=verified` without an independent verification record; verify `membership_evidence` is non-empty for any `hypothesized` or `verified` status |
| Source of ground truth | Lineage records (when generated) + independent verification records |
| Failure recording | Record candidate ID, invalid status, and reason; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. No lineage records have been generated yet. Structural status defaults to `unclassified` by spec definition.

### G6: Evaluation integrity

| Field | Definition |
|---|---|
| Observable pass/fail | All five evaluation paths use identical source-page inputs, consistent adjudication criteria, and the same frozen baseline; no path uses modified or different source material |
| Measurement population | All 5 evaluation paths × 3 outcomes × 12-crop frozen regression set |
| Reproducible procedure | For each evaluation path, verify: (a) source page IDs match across paths, (b) adjudication criteria document is identical, (c) frozen baseline file (`baseline_frozen_padding15.jsonl`) is unmodified (hash check), (d) no candidate appears in one path but not another |
| Source of ground truth | Frozen baseline file hash + evaluation path configuration files |
| Failure recording | Record path name, discrepancy type, and affected candidates; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. No evaluation paths have been run yet. The 5-path protocol is defined in spec §7 but not executed.

---

## 3. Acceptance Conditions Verification Matrix

Each of the 5 acceptance conditions from spec §8.2 must have an observable pass/fail, measurement population, reproducible procedure, source of ground truth, and failure recording.

### A1: Region detection produces measurable, reproducible region boundaries

| Field | Definition |
|---|---|
| Observable pass/fail | Region detection runs on all 127 pages; produces region boundaries that are consistent across runs (same input → same output); boundaries are expressible in page coordinates |
| Measurement population | All 127 pages with candidates |
| Reproducible procedure | Run `detect_math_regions_on_page()` twice on each page; compare region bboxes (must be identical); verify all boundaries are in PDF point coordinates; record region count per page |
| Source of ground truth | Deterministic function output (reproducibility = identical output on identical input) |
| Failure recording | Record page_id, run number, and boundary discrepancy; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. Function exists but has not been run on any page.

### A2: Candidate-to-region membership recorded for every candidate

| Field | Definition |
|---|---|
| Observable pass/fail | Every one of the 4,730 candidates has a `region_id` (assigned) or `unassigned_reason` (explicit); no candidate is silently dropped or left without a record |
| Measurement population | All 4,730 candidates |
| Reproducible procedure | Count candidates with `region_id` assigned + candidates with `unassigned_reason` set; verify sum = 4,730; verify no candidate has both null |
| Source of ground truth | Candidate JSON files + lineage records (when generated) |
| Failure recording | Record candidate ID, paper, page, and missing field; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. Depends on A1 (region detection must run first).

### A3: At least one evaluation path demonstrates measurable improvement

| Field | Definition |
|---|---|
| Observable pass/fail | At least one of the 4 non-baseline paths (expanded, adaptive, full-region, full-region+catalog) shows improvement in at least one of 3 outcomes (recognition, structural reconstruction, source fidelity) compared to the original-crop baseline |
| Measurement population | 12-crop frozen regression set × 5 paths × 3 outcomes = 180 measurements |
| Reproducible procedure | Run all 5 paths on the 12-crop set; compute per-outcome scores for each path; compare non-baseline paths against baseline; record any path/outcome with score > baseline score |
| Source of ground truth | Adjudicated reference verdicts (12 CONFIRMED_ACCURATE, 3 INTENDED_PARTIAL_FRAGMENT, 3 BOUNDARY_AMBIGUITY, 1 NOTATION_AMBIGUITY, 1 BOUNDARY_TRUNCATION) from `frozen-regression-evaluation-mapping-2026-11-03.md` |
| Failure recording | Record path, outcome, candidate ID, baseline score, path score, and delta; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. No evaluation paths have been run. Adjudicated verdicts exist for 21 candidates but the 5-path comparison has not been executed.

### A4: No information loss during region grouping

| Field | Definition |
|---|---|
| Observable pass/fail | No candidate disappears during region grouping; candidate count before grouping = candidate count after grouping |
| Measurement population | All 4,730 candidates |
| Reproducible procedure | Count candidates before region grouping; count candidates after region grouping; verify counts are equal; verify no candidate has been dropped, merged, or overwritten without a lineage record |
| Source of ground truth | Candidate JSON files (pre-grouping count) + lineage records (post-grouping count) |
| Failure recording | Record number of candidates lost, their IDs, and the grouping operation that caused the loss; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. Depends on A1 and A2.

### A5: Original crops and frozen baseline remain unmodified

| Field | Definition |
|---|---|
| Observable pass/fail | Frozen baseline file hash matches pre-work hash; original crop files are unmodified; no file in immutable artifact set has been changed |
| Measurement population | 4 immutable artifact sets (baseline_frozen_padding15.jsonl, crop_verification_renders/, candidate_visual_audit_renders/, crop_isolation_experiment/) |
| Reproducible procedure | Compute SHA-256 of each immutable artifact; compare against recorded pre-work hashes; verify no modification timestamps have changed |
| Source of ground truth | Pre-work SHA-256 hashes (to be recorded before any implementation begins) |
| Failure recording | Record file path, expected hash, actual hash, and modification timestamp; write to `gate_verification_failures.jsonl` |

**Current status:** NOT EVALUATED. Pre-work hashes have not been recorded. This must be done before any implementation begins.

---

## 4. Dependency Graph

```
A5 (baseline unmodified) ──┐
                            ├──► A4 (no info loss) ──┐
G1 (page geometry) ────────┤                        ├──► A3 (improvement demonstrated)
G2 (region detection) ─────┤                        │
G3 (lineage coverage) ─────┤                        │
G4 (context expansion) ────┘                        │
G5 (structural hypotheses) ─────────────────────────┘

G1 ──► G2 ──► G3 ──► G4 ──► G5 ──► A1 ──► A2 ──► A4 ──► A3
```

**Critical path:** G1 → G2 → G3 → G4 → A1 → A2 → A4 → A3

**Independent:** A5 (can be verified at any time, must be verified before implementation)

---

## 5. Failure Recording Format

All gate and acceptance failures are recorded in a single JSONL file:

**File:** `DATASETS/vision_comparison/gate_verification_failures.jsonl`

**Schema:**
```json
{
  "timestamp": "ISO-8601",
  "gate_id": "G1-G6 or A1-A5",
  "paper_id": "1907.04931",
  "page": 4,
  "candidate_id": "cand0_parameter_set",
  "failure_type": "missing_field | over_merge | under_merge | info_loss | hash_mismatch | unassigned",
  "details": "Human-readable description",
  "expected": "Expected value or condition",
  "observed": "Actual value or condition"
}
```

**Rules:**
- Failed/partial results remain useful. Do not discard them.
- Every failure must be recorded, not just the first.
- The file is append-only during evaluation.
- The file is never deleted or truncated.

---

## 6. Current Status Summary

| Gate | Name | Status | Blocker |
|---|---|---|---|
| G1 | Page geometry retained | **PASS** | None |
| G2 | Region detection precision/recall | **NOT EVALUATED** | No adjudicated region boundaries exist |
| G3 | Candidate lineage coverage | **PARTIAL** | Depends on G2 |
| G4 | Context expansion linkage | **NOT EVALUATED** | No expanded crops generated |
| G5 | Structural hypothesis distinguishability | **NOT EVALUATED** | No lineage records generated |
| G6 | Evaluation integrity | **NOT EVALUATED** | No evaluation paths run |

| Acceptance | Name | Status | Blocker |
|---|---|---|---|
| A1 | Region detection reproducible | **NOT EVALUATED** | Depends on G2 |
| A2 | Candidate-to-region membership complete | **NOT EVALUATED** | Depends on A1 |
| A3 | Measurable improvement demonstrated | **NOT EVALUATED** | Depends on A1-A4 |
| A4 | No information loss | **NOT EVALUATED** | Depends on A1, A2 |
| A5 | Frozen baseline unmodified | **NOT EVALUATED** | Pre-work hashes not recorded |

### Critical path

```
G2 (region detection) → A1 (reproducibility) → A2 (membership) → A4 (no loss) → A3 (improvement)
```

**First blocker:** G2 — no adjudicated region boundaries exist. This is the primary work item before any implementation can be authorized.

---

## 7. Recommended Next Step

Per your recommendation: the next artifact should be a **compact Context Preservation Gate Verification Matrix** referencing the existing 330-line spec rather than duplicating it.

This matrix serves that purpose. It converts each gate-entry criterion and acceptance condition into independently measurable pass/fail conditions with defined populations, procedures, ground truth, and failure recording.

**No source changes are warranted at this stage.** The six entry criteria and five acceptance conditions must be reviewed against this matrix before implementation authorization.

---

## 8. Governance

- **Read-only.** No implementation authority.
- **No frozen baseline modification.**
- **No source changes.**
- **No acceptance claims.**
- **Failed/partial results remain useful.** Do not discard them.
- **A specification being complete does not mean its acceptance conditions have been satisfied.**

---

## 9. Existing Test Scripts and Usages Covering These Patterns

### 9.1 Test scripts that exist

| Test File | What It Tests | Coverage of Context-Preservation Patterns |
|---|---|---|
| `tests/test_chroma_visual_reader.py` | `detect_2d_structures()` (fraction vinculum, cases brace), `VisualMathTranslator` (fraction/cases AST), `DiscrepancyReport` (skipped division, collapsed cases) | Tests 2D structure detection from `chroma_visual_reader.py` — a **different module** from `vision_comparison_pipeline.py`. Does NOT test `detect_math_regions_on_page()`, `expand_crop_context()`, `detect_partial_formulas()`, or `extract_text_boundaries()` from the vision pipeline. |
| `tests/test_crop_isolation_regression.py` | Crop isolation experiment artifacts (4 candidates × 4 configs = 16 records) | Tests crop geometry and OCR isolation but NOT region detection or context expansion. |
| `tests/test_visual_review_and_atomic_recompute.py` | Visual review audit log (21 candidates, 3-axis judgments, render artifacts, atomic recomputation) | Tests visual review but NOT region detection or context expansion. |
| `tests/test_candidate_audit_manifest.py` | Candidate audit manifest | Tests manifest but NOT region detection. |
| `tests/test_candidate_localization_verification.py` | Candidate localization | Tests localization but NOT region detection. |

### 9.2 Scripts that use these patterns

| Script | What It Does | Uses New Functions? |
|---|---|---|
| `scripts/vision_comparison_pipeline.py` | Main pipeline; defines all new functions (CF-023) | Defines them but does NOT call them in `process_candidates()` |
| `scripts/chroma_visual_reader.py` | 2D visual analysis: `find_visual_regions()`, `detect_2d_structures()`, `analyze_pdf_page()` | Separate module; does NOT use vision pipeline functions |
| `scripts/math_symbol_vision_hooks.py` | K-Means + connected components + Tesseract OCR; ~40 hardcoded shape profiles | Separate module; does NOT use vision pipeline functions |
| `scripts/chroma_usage_finder.py` | Uses `analyze_pdf_page()` from chroma_visual_reader; structural subtree matching against 1D MathML ASTs | Does NOT use vision pipeline functions |
| `scripts/run_border_evaluation.py` | **Only script that directly imports `vision_comparison_pipeline`**; calls `detect_border_contamination()` and `balloon_glyph()` on 12 crops | Yes (partial — only 2 of 10 new functions) |
| `scripts/experiments_crop_isolation.py` | 4 crop configurations (baseline, tight_pad2, asym_tight_y1, zero_y_pad0) with Pix2Text | Does NOT use region detection or context expansion |
| `scripts/run_one_candidate_diagnostic.py` | Single candidate diagnostic with padding=15 | Does NOT use new functions |
| `scripts/run_provenance_integration.py` | Uses `crop_pdf_region()` from vision pipeline | Does NOT use `detect_math_regions_on_page()` or `expand_crop_context()` |
| `scripts/audit_candidate_crops.py` | Candidate audit manifest | Does NOT use new functions |
| `scripts/recompute_vision_evaluations.py` | Atomic recomputation with failure injection | Does NOT use new functions |

### 9.3 Coverage gap summary

| New Function (CF-023) | Defined In | Called In Main Pipeline? | Called In Any Script? | Directly Tested? |
|---|---|---|---|---|
| `detect_math_regions_on_page()` | `vision_comparison_pipeline.py:941` | **No** | No | **No** |
| `expand_crop_context()` | `vision_comparison_pipeline.py:918` | **No** | No | **No** |
| `detect_partial_formulas()` | `vision_comparison_pipeline.py` | **No** | No | **No** |
| `extract_text_boundaries()` | `vision_comparison_pipeline.py` | **No** | No | **No** |
| `detect_border_contamination()` | `vision_comparison_pipeline.py:743` | Yes (screening only) | Yes (`run_border_evaluation.py`) | Yes (12-crop pilot, 75% agreement) |
| `balloon_glyph()` | `vision_comparison_pipeline.py:707` | No | Yes (`run_border_evaluation.py`) | Yes (12 crops generated) |
| `recognize_formula_multiscale()` | `vision_comparison_pipeline.py` | Yes (fallback in `recognize_formula()`) | No | No |
| `get_ascii_pattern_v2()` | `vision_comparison_pipeline.py` | No | No | No |
| `classify_alignment()` | `vision_comparison_pipeline.py:201` | Yes (in main loop) | No | No (stretch_recognized vs stretch_suspect distinction not tested) |
| `balloon_glyph_to_match()` | `vision_comparison_pipeline.py` | No | No | No |

### 9.4 What this means for the Context Preservation Gate

- **G2 (region detection):** The new `detect_math_regions_on_page()` has **zero** test coverage. The existing `test_chroma_visual_reader.py` tests `detect_2d_structures()` from a **different module** (`chroma_visual_reader.py`), not the vision pipeline's region detector. G2 cannot be evaluated until either (a) the function is wired into the pipeline, or (b) a standalone test is written against it.
- **G4 (context expansion):** `expand_crop_context()` has **zero** test coverage and is not called anywhere. The only related test is `test_crop_isolation_regression.py`, which tests crop geometry but not context expansion.
- **G5 (structural hypotheses):** `detect_partial_formulas()` and `extract_text_boundaries()` have **zero** test coverage and are not called anywhere.
- **G6 (evaluation integrity):** No test script verifies the 5-path evaluation protocol or the 3 tracked outcomes. The closest existing test is `test_visual_review_and_atomic_recompute.py`, which tests visual review audit log but not the context-preservation evaluation protocol.

### 9.5 Related but separate implementations

| Module | Region Detection Approach | Relationship to Context-Preservation Gate |
|---|---|---|
| `chroma_visual_reader.py` (`find_visual_regions`) | K-Means + `ndimage.label()` connected components | Separate module; same algorithm family as `detect_math_regions_on_page()` but different thresholds and classification. Could serve as reference implementation for G2. |
| `math_symbol_vision_hooks.py` (`detect_math_symbols`) | K-Means + `ndimage.label()` + Tesseract OCR | Separate module; uses ~40 hardcoded shape profiles. Not wired to catalog. |
| `vision_comparison_pipeline.py` (`detect_math_regions_on_page`) | `cv2.findContours()` + `cv2.RETR_EXTERNAL` + min/max size filtering | New implementation; different algorithm from `find_visual_regions()`. Needs independent validation. |

**Conclusion:** The Context Preservation Gate (G2–G6) has **no existing test coverage** for the new functions. The existing tests cover `chroma_visual_reader.py` (a different module) and crop geometry (a different concern). Before the gate can be evaluated, either the new functions must be wired into the pipeline with test coverage, or standalone tests must be written against them. The user's request to "check for previous test scripts and other usages" is satisfied: no previous test scripts cover these specific patterns.
