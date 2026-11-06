# Standalone Context-Preservation Test Plan

**Date:** 2026-11-04
**Status:** Read-only test specification — no implementation authorized
**Authority:** Context-preservation spec (330 lines), Context Preservation Gate Verification Matrix (324 lines)
**Scope:** Four uncovered functions in `scripts/vision_comparison_pipeline.py` + cross-function lineage contract

---

## 1. Purpose

Establish independent behavioral evidence for four functions that currently have **zero test coverage** and **zero runtime integration**:

1. `detect_math_regions_on_page()` — connected-component region proposal
2. `expand_crop_context()` — zoom-out context expansion
3. `extract_text_boundaries()` — PyMuPDF word-level text boundaries
4. `detect_partial_formulas()` — inline/partial math detection in prose

This plan is a **test specification**, not a test implementation. No source code changes, no pipeline wiring, no gate claims.

---

## 2. Three Milestones (must be tracked separately)

| Milestone | Definition | Gate Relevance |
|---|---|---|
| **Tested** | Function behaves per its defined contract on controlled (synthetic + real frozen) cases | G2–G6 entry criteria |
| **Evaluated** | Function performs adequately on representative real document pages | G2–G6 acceptance conditions |
| **Accepted** | Function satisfies the documented gate criteria | Context Preservation Gate review |

A function can be Tested but not Evaluated. A function can be Evaluated but not Accepted. These must never be conflated in status reports.

---

## 3. Test Categories

### 3.1 Synthetic geometry tests (predictable behavior)

Use artificially constructed image arrays or PyMuPDF page objects with known geometry. These establish the function's contract independent of document-specific noise.

### 3.2 Real frozen-page tests (document-specific failures)

Use the 127 pages from the 6-paper candidate corpus (4,730 candidates). These expose failures that synthetic cases cannot predict.

### 3.3 Cross-function lineage tests (contract integration)

Test the four functions together as a pipeline: `page → region → candidate → expanded representation`. This is a contract test, not pipeline integration.

---

## 4. Function 1: `detect_math_regions_on_page()`

### 4.1 Function contract (as currently implemented)

- **Input:** `image_array` (numpy array, page raster at zoom=4), `min_region_size=50`, `max_region_size=50000`
- **Output:** List of dicts, each with `bbox` (x, y, w, h), `region_type` (tall_symbol / fraction_bar / multi_line / single_line), `member_candidates` (list of candidate indices), `confidence` (float 0–1)
- **Algorithm:** `cv2.findContours()` with `RETR_EXTERNAL`, followed by min/max size filtering and aspect-ratio-based classification

### 4.2 Synthetic test cases

| Test ID | Input | Expected Output | What It Validates |
|---|---|---|---|
| DR-01 | Single isolated glyph (20×20 px) | 1 region, type `single_line`, confidence ≥ 0.5 | Basic detection |
| DR-02 | Two disconnected glyphs (20×20 each, 50px apart) | 2 regions, each `single_line` | Disconnected component separation |
| DR-03 | Two adjacent glyphs (20×20 each, 2px apart) | 1 region (merged) or 2 regions depending on gap threshold | Over-merging boundary |
| DR-04 | Tall symbol (20×60 px, aspect ratio 0.33) | 1 region, type `tall_symbol` | Tall-symbol classification |
| DR-05 | Wide fraction bar (100×5 px, aspect ratio 20.0) | 1 region, type `fraction_bar` | Fraction-bar classification |
| DR-06 | Multi-line block (3 glyphs stacked vertically, 10px gaps) | 1 region, type `multi_line` | Multi-line grouping |
| DR-07 | Empty image (no dark pixels) | Empty list | No false positives on blank |
| DR-08 | Noise (random salt-and-pepper, 1% density) | Empty list or minimal regions | Noise rejection |
| DR-09 | 43-candidate cluster (stress case from 2104.01277 page 64) | Region count ≤ 43, no single region containing > 20 candidates | Under-merging prevention |
| DR-10 | Region touching image edge | Region bbox clamped to image bounds; no negative coordinates | Edge handling |

### 4.3 Real frozen-page test cases

| Test ID | Source | What It Validates |
|---|---|---|
| DR-R1 | 2104.01277 page 64 (43-candidate cluster) | Region count, over-merging rate, under-merging rate |
| DR-R2 | 1907.04931 candidate 0 (ζ with subscript) | Single tall symbol detected as one region |
| DR-R3 | 2605.22902 cand3 (fraction with numerator/denominator) | Fraction bar detected as `fraction_bar` type |
| DR-R4 | 2605.27315 cand0 (parameter set with right-edge clipping) | Region not over-merged with adjacent content |

### 4.4 Pass criteria for G2

- All synthetic tests (DR-01 through DR-10) pass
- Region proposal precision ≥ 0.80 on real frozen pages (measured against adjudicated region boundaries)
- Region proposal recall ≥ 0.90 on real frozen pages
- Over-merging rate ≤ 0.10 (no unrelated expressions grouped)
- Under-merging rate ≤ 0.15 (no single expression split across regions)
- 43-candidate stress case: region count ≤ 43, no region contains > 20 candidates

---

## 5. Function 2: `expand_crop_context()`

### 5.1 Function contract (as currently implemented)

- **Input:** `pdf_page` (PyMuPDF page object), `bbox` (dict with x0, y0, x1, y1), `expand_factor=1.5`, `zoom=4`, `min_content_ratio=0.01`
- **Output:** `np.ndarray` (expanded crop image) or `None` (if expansion fails or content ratio below threshold)
- **Algorithm:** Expands bbox by `expand_factor`, renders at `zoom`, checks content ratio

### 5.2 Synthetic test cases

| Test ID | Input | Expected Output | What It Validates |
|---|---|---|---|
| EC-01 | Center bbox, expand_factor=1.5, no page edges | Expanded crop larger than original; content ratio ≥ min_content_ratio | Basic expansion |
| EC-02 | Bbox at page top edge, expand_factor=1.5 | Expanded crop clamped to page boundary; no negative coordinates | Top-edge clipping |
| EC-03 | Bbox at page bottom edge, expand_factor=1.5 | Expanded crop clamped to page bottom; no overflow | Bottom-edge clipping |
| EC-04 | Bbox at page left edge, expand_factor=1.5 | Expanded crop clamped to page left; no negative coordinates | Left-edge clipping |
| EC-05 | Bbox at page right edge, expand_factor=1.5 | Expanded crop clamped to page right; no overflow | Right-edge clipping |
| EC-06 | Bbox covering entire page, expand_factor=1.5 | Returns original (no expansion possible) or None | Full-page bbox |
| EC-07 | Bbox with expand_factor=2.0 | Expanded crop 2× larger (clamped to page) | Factor scaling |
| EC-08 | Bbox with expand_factor=1.0 | Returns original crop (no expansion) | Identity factor |
| EC-09 | Bbox with content ratio below min_content_ratio | Returns None | Content ratio gate |
| EC-10 | Bbox with expand_factor=1.5 on multi-line region | Expanded crop contains all lines of the region | Multi-line preservation |

### 5.3 Real frozen-page test cases

| Test ID | Source | What It Validates |
|---|---|---|
| EC-R1 | 1907.04931 cand0 (ζ with subscript) | Expanded crop contains subscript and surrounding context |
| EC-R2 | 2104.01277 cand8 (big union, 43-candidate cluster) | Expanded crop contains full multi-line expression without clipping |
| EC-R3 | 2605.27315 cand0 (parameter set, right-edge clipping) | Expanded crop does not clip content further; page boundary respected |

### 5.4 Pass criteria for G3 (context expansion)

- All synthetic tests (EC-01 through EC-10) pass
- Expanded crop contains original candidate bbox (provable coordinate containment)
- Page boundaries are never violated (no negative coords, no overflow)
- Content ratio gate works (returns None when below threshold)
- Original candidate identity is preserved (bbox coordinates recoverable from expanded crop metadata)

---

## 6. Function 3: `extract_text_boundaries()`

### 6.1 Function contract (as currently implemented)

- **Input:** `pdf_page` (PyMuPDF page object)
- **Output:** List of dicts, each with `text`, `bbox` (x0, y0, x1, y1), `is_math` (bool), `font_size` (float)
- **Algorithm:** PyMuPDF word-level extraction with math detection heuristic

### 6.2 Synthetic test cases

| Test ID | Input | Expected Output | What It Validates |
|---|---|---|---|
| TB-01 | Page with single word "hello" | 1 boundary, is_math=False | Basic text extraction |
| TB-02 | Page with single Greek letter "ζ" | 1 boundary, is_math=True | Greek symbol detection |
| TB-03 | Page with mixed text and math: "where ζ is the variable" | 2+ boundaries, math boundary has is_math=True | Mixed content |
| TB-04 | Page with inline math: "f(x) = x²" | Math boundaries detected, is_math=True for x, ² | Inline math detection |
| TB-05 | Page with superscript: "x²" | Superscript detected as separate boundary or flagged | Superscript handling |
| TB-06 | Page with subscript: "x₁" | Subscript detected as separate boundary or flagged | Subscript handling |
| TB-07 | Empty page | Empty list | No false positives |
| TB-08 | Page with only numbers "123" | Boundary detected, is_math=False (numbers alone are not math) | Number handling |
| TB-09 | Page with LaTeX-like text "\frac{a}{b}" | Boundary detected, is_math=True (contains math operators) | LaTeX detection |
| TB-10 | Page with multi-word math expression "sin(x) + cos(y)" | Multiple boundaries, all is_math=True | Multi-word math |

### 6.3 Real frozen-page test cases

| Test ID | Source | What It Validates |
|---|---|---|
| TB-R1 | 1907.04931 page with ζ subscript | Text boundary for ζ detected with correct bbox |
| TB-R2 | 2605.22902 page with fraction | Text boundaries for numerator and denominator detected |
| TB-R3 | 2605.27315 page with parameter set | Text boundaries for all parameters detected |

### 6.4 Pass criteria for G5 (structural hypotheses)

- All synthetic tests (TB-01 through TB-10) pass
- Math detection heuristic correctly identifies Greek symbols, operators, and LaTeX
- Non-math text is correctly classified as is_math=False
- Bounding boxes are accurate (within 2pt of PyMuPDF word extraction)
- Superscript/subscript handling is documented (even if imperfect)

---

## 7. Function 4: `detect_partial_formulas()`

### 7.1 Function contract (as currently implemented)

- **Input:** `pdf_page` (PyMuPDF page object), `text_boundaries` (list from `extract_text_boundaries()`)
- **Output:** List of dicts, each with `text`, `bbox`, `partial_type` (inline / display / isolated), `confidence`
- **Algorithm:** Detects math patterns within text boundaries; classifies as inline (embedded in prose), display (standalone), or isolated (no surrounding text)

### 7.2 Synthetic test cases

| Test ID | Input | Expected Output | What It Validates |
|---|---|---|---|
| PF-01 | Page with inline math: "The value of x is 5" | 1 partial formula, type `inline` | Inline detection |
| PF-02 | Page with display math: standalone "E = mc²" | 1 partial formula, type `display` | Display detection |
| PF-03 | Page with isolated symbol: standalone "ζ" | 1 partial formula, type `isolated` | Isolated detection |
| PF-04 | Page with no math: "The quick brown fox" | Empty list | No false positives |
| PF-05 | Page with partial math in prose: "where α is the learning rate" | 1 partial formula, type `inline` | Partial formula in prose |
| PF-06 | Page with incomplete boundary: math at page edge | Partial formula detected with confidence < 1.0 | Incomplete boundary handling |
| PF-07 | Page with false detection: "the sum of" (no math symbols) | Empty list or low-confidence result | False detection prevention |
| PF-08 | Page with multiple partial formulas in one paragraph | Multiple partial formulas detected | Multi-formula paragraph |
| PF-09 | Page with math at line boundary (spans two lines) | Partial formula detected with type `display` or `inline` | Line-boundary spanning |
| PF-10 | Page with nested math: "f(g(x)) where f is..." | Partial formula detected for inner and outer | Nested math |

### 7.3 Real frozen-page test cases

| Test ID | Source | What It Validates |
|---|---|---|
| PF-R1 | 1907.04931 page with ζ in prose | Inline partial formula detected |
| PF-R2 | 2605.22902 page with fraction in display | Display partial formula detected |
| PF-R3 | 2605.27315 page with parameter set | Multiple partial formulas detected |

### 7.4 Pass criteria for G4 (structural evidence)

- All synthetic tests (PF-01 through PF-10) pass
- Inline math correctly classified as `inline`
- Display math correctly classified as `display`
- Isolated symbols correctly classified as `isolated`
- False positive rate ≤ 0.10 on real frozen pages (no non-math text classified as formula)
- Incomplete boundaries recorded with confidence < 1.0 (not silently discarded)

---

## 8. Cross-Function Lineage Test (G5/G6)

### 8.1 Test ID: CL-01 through CL-06

Test the four functions together as a contract pipeline without main-loop integration.

| Test ID | Transition | What It Validates |
|---|---|---|
| CL-01 | Page → Region | `detect_math_regions_on_page()` output contains page identity (page number, page dimensions) in every region record |
| CL-02 | Region → Candidate | Every candidate from the frozen set is assigned to exactly one region; region membership is explicit (not implicit) |
| CL-03 | Candidate → Expanded | `expand_crop_context()` output contains original candidate bbox coordinates; expanded crop can be traced back to original |
| CL-04 | Page boundaries | No expanded crop violates page boundaries (no negative coords, no overflow) |
| CL-05 | Uncertain membership | Candidates with ambiguous region membership are recorded as `uncertain`, not silently assigned to nearest region |
| CL-06 | Failed detection | Failed region detections are recorded with failure reason, not silently discarded |

### 8.2 Lineage record schema

Each transition must produce a record with these fields:

```json
{
  "page_id": "paper_id:page_number",
  "region_id": "page_id:region_index",
  "candidate_id": "page_id:candidate_index",
  "original_bbox": [x0, y0, x1, y1],
  "region_bbox": [rx, ry, rw, rh],
  "expanded_bbox": [ex0, ey0, ex1, ey1],
  "membership_status": "assigned|uncertain|unassigned",
  "expansion_status": "expanded|clamped|failed",
  "failure_reason": null
}
```

### 8.3 Pass criteria for G5 (representation continuity)

- All 6 lineage tests (CL-01 through CL-06) pass
- Every candidate has a traceable path: page → region → candidate → expanded
- No candidate identity is lost during expansion (bbox recoverable)
- Uncertain membership is explicitly recorded, not silently resolved
- Failed detections are recorded with reason, not discarded

### 8.4 Pass criteria for G6 (evaluation integrity)

- All test results are reproducible on frozen inputs (same input → same output)
- Test results are recorded in append-only JSONL (no truncation)
- Failed tests are recorded, not silently skipped
- No test modifies frozen baseline artifacts

---

## 9. Test Implementation Rules

1. **Synthetic tests first** — establish predictable behavior before real-page tests
2. **Real frozen-page tests second** — expose document-specific failures
3. **Cross-function lineage tests third** — verify contract integration
4. **No pipeline integration** — tests are standalone, not wired into `process_candidates()`
5. **No baseline modification** — frozen artifacts remain immutable
6. **Append-only results** — test results recorded in JSONL, never overwritten
7. **Failed tests recorded** — failures are useful evidence, not discarded
8. **Three milestones tracked separately** — Tested ≠ Evaluated ≠ Accepted

---

## 10. Gate Mapping (recommended evidence relationship)

| Gate | Required Evidence | Test IDs | Status |
|---|---|---|---|
| G2 — Region geometry | Region detection tests pass against adjudicated cases | DR-01–DR-10, DR-R1–DR-R4 | NOT EVALUATED |
| G3 — Context expansion | Expansion preserves coordinates and source lineage | EC-01–EC-10, EC-R1–EC-R3 | NOT EVALUATED |
| G4 — Structural evidence | Structural hypotheses retain their uncertainty | PF-01–PF-10, PF-R1–PF-R3, TB-01–TB-10, TB-R1–TB-R3 | NOT EVALUATED |
| G5 — Representation continuity | Original and expanded crops remain independently accessible | CL-01–CL-06 | NOT EVALUATED |
| G6 — Evaluation integrity | Reproducible results against frozen inputs | All test IDs (reproducibility) | NOT EVALUATED |

**Note:** This is the recommended evidence relationship. The exact mapping follows the existing matrix definitions. No gate has passed. No implementation is authorized.

---

## 11. Recommended Sequence

```
Current position: Gate not evaluated
                    ↓
Next: Standalone behavioral tests (4 functions, independent contracts, frozen inputs)
                    ↓
Then: Cross-function lineage tests (page → region → candidate → expanded)
                    ↓
Then: Representative-page evaluation (real frozen pages, 6 papers)
                    ↓
Then: Context Preservation Gate review (verify G2–G6 independently measurable)
                    ↓
Finally: Separate authorization for pipeline integration
```

---

## 12. Governance

- This document is a read-only test specification.
- No source code changes are authorized by this document.
- No pipeline integration is authorized by this document.
- No gate claims are authorized by this document.
- Test implementation requires separate explicit authorization.
- Frozen baseline artifacts must not be modified.
- All test results must be recorded in append-only JSONL.
- Failed tests are useful evidence and must not be silently discarded.
- Three milestones (Tested, Evaluated, Accepted) must be tracked separately in all status reports.

---

*End of standalone test plan.*