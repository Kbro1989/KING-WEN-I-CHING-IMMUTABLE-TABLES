# Delimiter-Blind-Coordinate Semantics Audit

**Date:** 2026-11-11
**Branch:** `v2-remediation` (befa228927)
**Purpose:** Freeze operational definitions and semantic boundaries for blind execution, detection/recovery/verification operations, and coordinate-space distinctions in the King Wen delimiter ecosystem.
**Status:** Source-level audit; no files modified.

---

## Table of Contents

1. [Scope and Method](#scope-and-method)
2. [Operational Definition: Blind Execution](#operational-definition-blind-execution)
3. [Four-Vocabulary Distinction: Observation / Detection / Recovery / Verification](#four-vocabulary-distinction-observation--detection--recovery--verification)
4. [Coordinate-Space Distinctions](#coordinate-space-distinctions)
5. [y_band Provenance and G0 Implications](#y_band-provenance-and-g0-implications)
6. [Blind Execution Evidence Chain](#blind-execution-evidence-chain)
7. [The Three King Wen Domains](#the-three-king-wen-domains)
8. [Terminology Cheat-Sheet](#terminology-cheat-sheet)

---

## Scope and Method

This document freezes the vocabulary and evidence boundaries established in the preceding three artifacts:

- `docs/cross-reference-audit-2026-11-11.md` — architectural domains and population boundaries
- `docs/interface-conformance-matrix-2026-11-11.md` — callable interfaces and coordinate assumptions
- `docs/delimiter-usage-evidence-audit-2026-11-11.md` — actual imports and execution paths

This document adds the semantic layer: what the operations mean, what the coordinate spaces are, and what "blind" means in this repository.

All claims are verified against source on disk as of commit `befa228927`.

---

## Operational Definition: Blind Execution

**Blind execution** is defined as:

> The resolver runs without reference data. No gold manifests, no gold bounding boxes, no equation identifiers, and no gold-derived glyph inventory are loaded or exposed to the prediction path.

### Verified Evidence

| File | Evidence |
|------|----------|
| `scripts/blind_detection_run_1505.py` | Runs paper 1505.05770 without gold; candidate records `1505.05770_blind_detection_p002.json` and `p003.json` stored separately |
| `scripts/targeted_math_detector.py` | `main()` reads PDF, extracts observations, renders candidates — no gold manifest reference in the execution path |
| `scripts/freeze_1505_blind_renders_manifest.py` | Produces SHA-256 freeze manifest from frozen source PDF and detector without gold input |
| `docs/POST_C40286_DEVELOPMENT_RECONCILIATION_2026-11-05.md` | Line 332: "Machine-checked verification confirming `blind_detection_run_1505.py` and `targeted_math_detector.py` contain zero imports, references, or knowledge of gold manifests, gold bounding boxes, or equation identifiers (GS-001 through GS-005)" |

**KGS-001 through GS-005** (to be treated as frozen evidence items once linked): the five checks that establish zero-gold in the blind execution path.

### What "Blind" Does NOT Mean

- Not a machine-learning holdout or training split. No model is being trained or validated here; the resolver is a deterministic pipeline.
- Not a veto of later gold comparison. A blind run can be evaluated afterward against gold — the comparison stage is separate.
- Not a claim that the current visual pipeline has no gold-dependent inputs. The evaluation layer (G0–G5, `gold_comparison`, `independent_validation`) is a separate stage from the prediction stage, but the two are not yet connected into a certified pipeline (separate integration issue, per `batch-delimiter-integration-audit-2026-11-06.md`).

---

## Four-Vocabulary Distinction

### Operation Definitions

| Operation | Representative function | Evidence produced |
|-----------|------------------------|-------------------|
| **Observation** | `extract_raw_observations(page, page_index)` in `targeted_math_detector.py` | Raw PDF character geometry and font properties (per-character `bbox_pdf_pt`, `font`, `font_size_pt`, `is_math_char`) |
| **Detection** | `render_visual_candidates(page, page_index, zoom, out_dir)` in `targeted_math_detector.py`; `detect_delimiter_candidates(page, y_band)` in `v2_delimiter_aware_structural_recovery.py` | Visual candidate hypotheses (tall glyph, wide operator, raster stroke) |
| **Recovery** | `run_v2_recovery_on_page(page, y_band)` in `v2_delimiter_aware_structural_recovery.py` | Structural relationships and delimiter pairing (associated pairs, unpaired structures) |
| **Verification** | `blind_detection_run_1505.py` + `audit_gold_equation_chains_1505.py`; G0–G5 evaluator gates | Evidence supporting or rejecting correctness — comparison with gold, independent validation |

### Explicit Non-Equivalences

1. **Raw character extraction does not prove delimiter detection.** `extract_raw_observations()` returns every character with a bbox, but this is character-level geometry, not a delimiter-opinion. A `(` and `a` both return a bbox; delimiter status comes from `classify_delimiter_glyph_font_aware` and `associate_delimiter_pairs`.

2. **Structural pairing does not prove identity correctness.** `associate_delimiter_pairs()` in both `delimiter_aware_structural_recovery.py` and `v2_delimiter_aware_structural_recovery.py` produces pair/unpaired structure, but the final identity judgment is made by `classify_delimiter_glyph_font_aware()` and the G0–G5 evaluator gates.

3. **Verification is a separate stage from prediction.** The blind run (prediction) is not the same as the gold comparison (verification). Both can be executed, but the second consumes the first's outputs, not the other way around.

---

## Coordinate-Space Distinctions

### Three Explicit Coordinate Spaces

| Coordinate space | Meaning | Where it appears |
|------------------|---------|------------------|
| `pdf_points` | Native page geometry, top-left origin, y-down | `bbox_pdf_pt` in `targeted_math_detector.py`; `pymupdf.Rect` in `v2_delimiter_aware_structural_recovery.py`; `y_band` bounds in `prediction_adapter.py` |
| `rendered_pixels` | Raster observations from rendered page image | `render_visual_candidates()` in `targeted_math_detector.py` (`bbox_render_px`, `pixel offsets`); raster stroke candidate extraction via `cv2` morphology |
| `normalized_page_coordinates` | Derived coordinates, if actually implemented | **NOT confirmed** — source evidence shows `bbox_pdf_pt_approx = bbox_render_px / zoom` in `targeted_math_detector.py`, which is a scale conversion, not a third coordinate space. Do not add `normalized_page_coordinates` to the implementation contract until source confirms it |

### Coordinate-Conversion Evidence

**Confirmed conversion paths:**

- `targeted_math_detector.py` lines 103–104: `"bbox_pdf_pt": rect4(span.get("bbox", ...))` — native PDF points
- Lines 253–254: `"bbox_pdf_pt_approx": [round(v / zoom, 3) for v in (x, y, x + w, y + h)]` — raster-to-PDF conversion by `zoom` factor

**No confirmed conversion paths for:**

- `page.rect` rotation (no `page_rotation` metadata captured anywhere)
- Scale transformation (only `zoom` factor in one direction: render → PDF)
- Coordinate-origin translation (PDF points are top-left; raster is pixel, but the two are treated as separate, not normalized)

### Three-Space Model (PoC: Confirmed, Ad Hoc)

| Space | Source | Provenance |
|-------|--------|------------|
| `pdf_points` | `page.get_text("rawdict")` or `pymupdf.Rect` | Native page geometry |
| `rendered_pixels` | `page.get_pixmap(matrix=Matrix(zoom, zoom))` | Raster observations |
| `normalized_page_coordinates` | `bbox_render_px / zoom` → `bbox_pdf_pt_approx` in `targeted_math_detector.py` | Scale conversion only; **not a third space** |

**Reconciliation:** The earlier audit's proposal of `normalized_page_coordinates` as a third space is not supported by source evidence. The actual conversion is a simple scale (render → PDF, both in the same origin system). Add `normalized_page_coordinates` to the implementation contract only if source code confirms an independently normalized third space (e.g., a transform that changes origin or units).

---

## y_band Provenance and G0 Implications

### Source of y_band

`evaluation/prediction_adapter.py:88`:
```python
y_band = (0.0, float(page.rect.height))
```

`evaluation/prediction_adapter.py:97`:
```python
raw_detector_output = detect_delimiter_candidates(page, y_band)
```

### What This Establishes

| Check | Result |
|-------|--------|
| `y_band` is full page height (0 to page height) | Confirmed |
| `y_band` is not a gold-derived region | Confirmed — a rectangle defined by `page.rect`, not by gold data |
| `predictor` obtains `page` independently of gold | `page.rect` is a PDF page property; no gold manifest is opened in the adapter path |
| `predictor` uses any gold-derived glyph inventory | No gold data flows into `predictor` — the adapter receives `page` and computes `y_band` from page geometry |
| `predictor` uses any gold-derived labels/identities | No gold data in the adapter path |

### Remaining G0 Checks (Not Yet Demonstrated)

| Check | Status |
|-------|--------|
| Does the detector use any gold-derived glyph inventory, coordinates, labels, or target identities? | Not yet proven — the detector reads page geometry, but the full pipeline must be traced from `targeted_math_detector.py` through `v2_delimiter_aware_structural_recovery.py` to confirm all downstream grooming is gold-free |
| Does any downstream filtering or pairing use gold-derived information? | Not yet proven — `associate_delimiter_pairs()` receives candidates; no gold data is visible in the V1/V2 engine at this snapshot, but the final `evaluation` stage is where gold enters the picture |
| Is the corpus-level G0 certification complete? | **No.** The full pipeline must be executed with the same `y_band` across all 243 papers, with G0–G5 assessed per paper, and the results recorded. This is a separate integration issue from `prediction_adapter.py` |

### Conclusion on y_band

The full-page `y_band` is a potentially important G0 improvement. It narrows the concern from "caller-supplied region" to "complete prediction-path independence." That is a precise investigation, but it is not yet a corpus-level G0 certification.

---

## The Three King Wen Domains

| Domain | Contents | Evidence |
|--------|----------|----------|
| **Mathematical engine** | King Wen state machine (64 hexagrams × 8 phases = 512 binary states, ternary layer 729/5832/46656) | `king_wen_ternary_tables_complete.py`, `emotional_engine.py`, `king_wen_core/` — the engine, not the deliverable |
| **Mathematical extraction** | arXiv HTML / MathML → MathML tree → `parse_mathml_tree()` → equation recovery and solver | `mathml_parser.py`, `math_recovery_tool.py`, `math_contract.py`, `semantic_math_extractor.py` |
| **PDF visual analysis** | PDF pages → character observation → delimiter detection → pairing → identity adjudication | `targeted_math_detector.py`, `font_aware_math_classifier.py`, `delimiter_aware_structural_recovery.py`, `v2_delimiter_aware_structural_recovery.py`, `delimiter_identity.py` |

**Boundary rule:** King Wen's core mathematical engine is authoritative for the 512-state state machine and emotional-vector space. Mathematical extraction is for recovering and verifying mathematical expressions from papers (not King Wen definitions). PDF visual analysis is for generating visual evidence from pages. The three domains exchange data but must not inherit each other's validation authority.

---

## Terminology Cheat-Sheet

| Term | Definition |
|------|------------|
| `blind_execution` | Resolver runs without reference data (gold manifests, bounding boxes, equation identifiers, gold glyph inventory) |
| `gold_comparison` | Separate process that compares blind output with gold; separate stage from prediction |
| `independent_validation` | Validation run using a separate reference or execution path |
| `blind_render_manifest` | Frozen rendered outputs produced under a blind execution protocol |
| `observation` | Raw PDF character geometry and font properties (`extract_raw_observations()`) |
| `detection` | Visual candidate hypotheses (`render_visual_candidates()`, `detect_delimiter_candidates()`) |
| `recovery` | Structural relationships and delimiter pairing (`run_v2_recovery_on_page()`) |
| `verification` | Independent validation and gold comparison harnesses |
| `pdf_points` | Native page geometry (top-left origin, y-down) |
| `rendered_pixels` | Raster observations from rendered page image |
| `normalized_page_coordinates` | Derived coordinates — NOT confirmed in source; do not add to implementation contract yet |
| `full_page_search_region` | Complete prediction-path independent search interval |
| `gold_conditioned_search_region` | Search region derived from gold data |

---

## Files Referenced in This Audit

| File | Role |
|------|--------|
| `evaluation/prediction_adapter.py` | `y_band` provenance (line 88); `detect_delimiter_candidates()` call (line 97) |
| `v2_delimiter_aware_structural_recovery.py` | `detect_delimiter_candidates()` (line 213); `run_v2_recovery_on_page()` (line 723) |
| `targeted_math_detector.py` | `extract_raw_observations()` (line 79); `render_visual_candidates()` |
| `scripts/blind_detection_run_1505.py` | Blind execution harness |
| `scripts/freeze_1505_blind_renders_manifest.py` | Blind render freeze manifest |
| `scripts/audit_gold_equation_chains_1505.py` | Gold comparison of blind detection results |
| `docs/POST_C40286_DEVELOPMENT_RECONCILIATION_2026-11-05.md` | GS-001 through GS-005 zero-gold evidence for blind pipeline |

---

## Open Items

1. Verify that all 243 papers in the batch corpus can be processed through the blind path and G0–G5 gates with `y_band` as defined.
2. Trace the full prediction path from `blind_detection_run_1505.py` through `targeted_math_detector.py` → `v2_delimiter_aware_structural_recovery.py` → `delimiter_identity.py` and confirm zero gold references throughout.
3. Confirm whether `normalized_page_coordinates` (third coordinate space) is actually implemented anywhere.
3. Confirm the G0–G5 gate evaluation runs per paper and records results in a format suitable for corpus-level certification.

---

## Capability Discovery: Candidate Tooling Inventory (2026-11-11)

This section records the full production surface across all math-pipeline tooling, mapped by capability. It supplements the earlier capability map in `delimiter-usage-evidence-audit-2026-11-11.md` with the semantic boundaries of each transformation layer.

### Capability Map (2026-11-11)

| # | Capability | Declared source path(s) | Input authority | Output contract | Current status |
|----|-----------|-----------------|-----------------|-----------------|----------------|
| C1 | MathML extraction | `scripts/mathml_parser.py`, `scripts/arxiv_html_parser.py` | MathML tree + x-tex annotations | Equation structured output (ExprNode tree) | Candidate — needs corpus coverage test |
| C2 | LaTeX reconstruction | `scripts/math_recovery_tool.py`, `scripts/delimiter_identity.py` | MathML, gold, LaTeX | Reconstructed LaTeX string | Supporting — needs corpus benchmark |
| C3 | Structural recovery (V1) | `scripts/delimiter_aware_structural_recovery.py` | Visual candidates (bbox) | Paired/unpaired structure | Candidate — needs sender linkage |
| C4 | Structural recovery (V2) | `scripts/v2_delimiter_aware_structural_recovery.py` | Visual candidates (bbox) | Paired/unpaired structure | Candidate — no caller confirmed |
| C5 | AST extraction | `scripts/structural_ast_extractor.py` | MathML tree | Structural AST (ExprNode) | Candidate — may reuse delimiter tokens |
| C6 | Visual detection | `scripts/targeted_math_detector.py`, `scripts/vision_math_extractor.py` | PDF page (rawdict) | Bbox, char observations, visual candidates | Candidate — executable |
| C7 | OCR (entry points) | Pix2Text, Tesseract integrations | PDF image / crop | Character/text output | Not tested — no integration scripts found |
| C8 | Semantic validation | `scripts/math_contract.py`, `scripts/semantic_honesty_scoreboard.py` | Recovered math tree | Validation status + scoreboard | Candidate — needs assertion inspection |
| C9 | Equation solving | `scripts/solve_all.py`, `scripts/solve_dual_path.py` | Recovered math IR | Solution (SymPy) | Candidate — needs negative controls |
| C10 | Geometric validation | Localization, crop-isolation tests | Geometry ops | Adversary output (pass/fail) | Candidate — needs assertion inspection |
| C11 | Provenance tracing | `scripts/verify_provenance_trace.py`, candidate manifests, audit runners | Artifact + trace | Verification result | Candidate — needs execution |

### Capability→Operation Mapping (Verification Layer)

| Capability | Representative function | Operation defined in semantics audit |
|------------|------------------------|-------------------------------------|
| C1 (MathML extraction) | `mathml_parser.py`, `arxiv_html_parser.py` | Observation layer — parses MathML into structured expression tree |
| C2 (LaTeX reconstruction) | `math_recovery_tool.py`, `delimiter_identity.py` | Recovery layer — reconstructs LaTeX from structured representation |
| C3 (Structural recovery V1) | `delimiter_aware_structural_recovery.py` | Recovery layer — delimiter pairing (V1 engine) |
| C4 (Structural recovery V2) | `v2_delimiter_aware_structural_recovery.py` | Recovery layer — delimiter pairing (V2 engine) |
| C6 (Visual detection) | `targeted_math_detector.py` | Detection layer — bbox and character observation |
| C7 (OCR) | Pix2Text, Tesseract | Detection layer — raster character recognition |
| C8 (Semantic validation) | `math_contract.py`, `semantic_honesty_scoreboard.py` | Verification layer — semantic status and scoreboard |
| C9 (Equation solving) | `solve_all.py`, `solve_dual_path.py` | Equation solving — SymPy-based solution |
| C10 (Geometric validation) | Localization, crop-isolation tests | Verification layer — geometric pass/fail |
| C11 (Provenance tracing) | `verify_provenance_trace.py` | Verification layer — provenance result |

### Continuity with Blind Execution Semantics

| Semantic concept | Capability mapping | Connection |
|-------------------|---------------------|------------|
| `observation` | C1, C6 | `extract_raw_observations()` and MathML parsing are the observation layer |
| `detection` | C6, C7, C10 | `render_visual_candidates()`, OCR, and geometric detection combine into detection |
| `recovery` | C3, C4, C5 | V1/V2 delimiter recovery and AST extraction form the structural recovery layer |
| `verification` | C8, C9, C11 | Semantic validation, equation solving, and provenance tracing form the verification layer |

**Note:** `blind_execution` is a temporal property (no reference data loaded) that must hold at every layer: the blind run must be independent of gold at the observation, detection, recovery, and verification layers simultaneously. This is verified per paper, not globally.

---

## Three King Wen Domains

| Domain | Contents | Evidence |
|--------|----------|----------|
| **Mathematical engine** | King Wen state machine (64 hexagrams × 8 phases = 512 binary states, ternary layer 729/5832/46656) | `king_wen_ternary_tables_complete.py`, `emotional_engine.py`, `king_wen_core/` — the engine, not the deliverable |
| **Mathematical extraction** | arXiv HTML / MathML → MathML tree → `parse_mathml_tree()` → equation recovery and solver | `mathml_parser.py`, `math_recovery_tool.py`, `math_contract.py`, `semantic_math_extractor.py` |
| **PDF visual analysis** | PDF pages → character observation → delimiter detection → pairing → identity adjudication | `targeted_math_detector.py`, `font_aware_math_classifier.py`, `delimiter_aware_structural_recovery.py`, `v2_delimiter_aware_structural_recovery.py`, `delimiter_identity.py` |

**Boundary rule:** King Wen's core mathematical engine is authoritative for the 512-state state machine and emotional-vector space. Mathematical extraction is for recovering and verifying mathematical expressions from papers (not King Wen definitions). PDF visual analysis is for generating visual evidence from pages. The three domains exchange data but must not inherit each other's validation authority.

---

## Terminology Cheat-Sheet

| Term | Definition |
|------|------------|
| `blind_execution` | Resolver runs without reference data (gold manifests, bounding boxes, equation identifiers, gold glyph inventory) |
| `gold_comparison` | Separate process that compares blind output with gold; separate stage from prediction |
| `independent_validation` | Validation run using a separate reference or execution path |
| `blind_render_manifest` | Frozen rendered outputs produced under a blind execution protocol |
| `observation` | Raw PDF character geometry and font properties (`extract_raw_observations()`) |
| `detection` | Visual candidate hypotheses (`render_visual_candidates()`, `detect_delimiter_candidates()`) |
| `recovery` | Structural relationships and delimiter pairing (`run_v2_recovery_on_page()`) |
| `verification` | Independent validation and gold comparison harnesses |
| `pdf_points` | Native page geometry (top-left origin, y-down) |
| `rendered_pixels` | Raster observations from rendered page image |
| `normalized_page_coordinates` | Derived coordinates — NOT confirmed in source; do not add to implementation contract yet |
| `full_page_search_region` | Complete prediction-path independent search interval |
| `gold_conditioned_search_region` | Search region derived from gold data |

---

## Files Referenced in This Audit

| File | Role |
|------|--------|
| `evaluation/prediction_adapter.py` | `y_band` provenance (line 88); `detect_delimiter_candidates()` call (line 97) |
| `v2_delimiter_aware_structural_recovery.py` | `detect_delimiter_candidates()` (line 213); `run_v2_recovery_on_page()` (line 723) |
| `targeted_math_detector.py` | `extract_raw_observations()` (line 79); `render_visual_candidates()` |
| `scripts/blind_detection_run_1505.py` | Blind execution harness |
| `scripts/freeze_1505_blind_renders_manifest.py` | Blind render freeze manifest |
| `scripts/audit_gold_equation_chains_1505.py` | Gold comparison of blind detection results |
| `docs/POST_C40286_DEVELOPMENT_RECONCILIATION_2026-11-05.md` | GS-001 through GS-005 zero-gold evidence for blind pipeline |

---

## Open Items

1. Verify that all 243 papers in the batch corpus can be processed through the blind path and G0–G5 gates with `y_band` as defined.
2. Trace the full prediction path from `blind_detection_run_1505.py` through `targeted_math_detector.py` → `v2_delimiter_aware_structural_recovery.py` → `delimiter_identity.py` and confirm zero gold references throughout.
3. Confirm whether `normalized_page_coordinates` (third coordinate space) is actually implemented anywhere.
4. Confirm the G0–G5 gate evaluation runs per paper and records results in a format suitable for corpus-level certification.
5. Confirm the capability inventory above against live source (C7 OCR integration, C8 semantic validation assertions, C9 solver coverage, C10 geometric validation cases).

---

*This document is a semantic supplement to `cross-reference-audit-2026-11-11.md`, `interface-conformance-matrix-2026-11-11.md`, and `delimiter-usage-evidence-audit-2026-11-11.md`. It does not create new code or alter existing artifacts.*
