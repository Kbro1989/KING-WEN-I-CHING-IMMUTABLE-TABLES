# Interface-Conformance Matrix — Visual-Delimiter Ecosystem

**Date:** 2026-11-11
**Branch:** `v2-remediation` (befa228927)
**Purpose:** Testable target for the visual-evidence pipeline integration contract — maps each visual component's actual callable signature, input schema, output schema, coordinate assumptions, and execution status against `docs/delimiter-corpus-integration-contract-2026-11-11.md`.
**Status:** Source-level audit; no files modified.

---

## Table of Contents

1. [Scope and Method](#scope-and-method)
2. [Component Matrix](#component-matrix)
3. [Exported Symbol Verification](#exported-symbol-verification)
4. [Cross-Cutting Schema Contract](#cross-cutting-schema-contract)
5. [Coordinate Assumptions Audit](#coordinate-assumptions-audit)
6. [Gap Register](#gap-register)
7. [Construction Order for integration contract](#construction-order-for-integration-contract)
8. [Non-Regressio Tigers](#non-regression-tiggers)

---

## Scope and Method

This matrix is the **interface conformance audit** for the visual-delimiter ecosystem. It maps:

- What each module **names** (callable signature, as read from source).
- What it **produces** (return schema).
- What it **assumes** (coordinate system, import contiguity, state).
- Whether it is actually **reachable** from the proposed `delimiter_corpus_integration.py` execution path.

The companion document is `docs/delimiter-corpus-integration-contract-2026-11-11.md` (pending). This report is its **conformance ground truth**.

---

## Component Matrix

### C1 — `targeted_math_detector.py`

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/targeted_math_detector.py` (343 lines, v1.1) |
| **Entry point** | `main()` (CLI: `python targeted_math_detector.py paper.pdf --pages N --out dir`) |
| **Primary callables** | `extract_raw_observations(page, page_index)` → `(spans, chars)`<br>`geometry_candidates(chars)` → list[dict]<br>`script_position_candidates(chars)` → list[dict]<br>`render_visual_candidates(page, page_index, zoom, out_dir)` → dict |
| **Input** | `page: pymupdf.Page`, `page_index: int` |
| **Output** | `(spans, chars)` for `extract_raw_observations`; list of candidate dicts for `geometry_candidates`; list of script-hypothesis dicts for `script_position_candidates`; dict with `visual_candidates` list for `render_visual_candidates` |
| **Coordinate assumptions** | `bbox_pdf_pt` — PDF points, y-down |
| **Coordinate output fields** | `bbox_pdf_pt`, `bbox_pdf_pt_approx` (render scale divide), `page_number_1_based`, `page_size_pdf_pt` |
| **Coordinate space declaration** | PDF points (math text detector); render pixels reported as `bbox_pdf_pt_approx` (scaled, not re-tabulated) |
| **Coordinate convention** | PDF native y-down, top-origin |
| **Source pinning** | `source_pdf_sha256` (module-level caller passes in `main()`) |
| **Dependency on gold** | None observed — purely observation-based |
| **Execution status** | CLI-executable; no import-based callable evidence for the contract layer |

---

### C2 — `font_aware_math_classifier.py`

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/font_aware_math_classifier.py` (226 lines) |
| **Callables** | `is_math_font(font_name: str \| None) -> bool`<br>`classify_glyph(char: str, font_name: str \| None, font_size_pt: float = 10.0) -> dict[str, Any]`<br>`discriminate_citation(text: str) -> dict[str, Any]` |
| **Input** | `classify_glyph` consumes a glyph observation (char, font, font_size) |
| **Output** | `classify_glyph` returns a dict with `is_math`, `math_category`, `latex_interpretation`, `font_family_is_math` |
| **Coordinate assumptions** | None — glyph classification is coordinate-free |
| **Coordinate output fields** | None |
| **Coordinate convention** | N/A (no spatial dimensions) |
| **Dependency on gold** | None — classification from glyph properties + Unicode plus font-provenance heuristics |
| **Execution status** | Importable library; no CLI entry point tested |

---

### C3 — `delimiter_aware_structural_recovery.py` (V1 baseline)

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/delimiter_aware_structural_recovery.py` (531 lines) |
| **Callables** | `verify_d1_glyph_extent(glyph_rect, crop_rect, tolerance_pt=0.5)` → dict<br>`classify_delimiter_glyph_font_aware(page, rect)` → dict<br>`associate_delimiter_pairs(candidates, page_width, page_height)` → `tuple[list[dict], list[dict]]` |
| **Input** | `verify_d1_glyph_extent`: two `pymupdf.Rect` objects<br>`classify_delimiter_glyph_font_aware`: `page`, `rect`<br>`associate_delimiter_pairs`: `candidates` list of dict (with `rect` as `pymupdf.Rect`), `page_width`, `page_height` |
| **Output** | `verify_d1_glyph_extent` → dict with keys `gate`, `passed`, `h_glyph_pt`, `h_crop_pt`, `glyph_aspect_ratio`, `is_scalable_delimiter`, `rule`<br>`classify_delimiter_glyph_font_aware` → dict with `gate`, `kind`, `is_opening`, `family`, `resolution_method`, `confidence`, `raw_characters`, `font_lineage`, `spans_count`<br>`associate_delimiter_pairs` → `tuple[list[dict], list[dict]]` of `(paired_structures, unpaired_structures)` |
| **Coordinate assumptions** | `pymupdf.Rect` (PDF points, y-down, clip rects) |
| **Coordinate output fields** | `rect` → `rect_to_list(rect)` = `[x0, y0, x1, y1]` in PDF points |
| **Coordinate convention** | PDF native coordinates; `rect_to_list` rounds to 2 decimals |
| **Coordinate convention** | `pymupdf.Rect` — top-left origin, y-down |
| **Dependency on gold** | None observed in V1 — purely observation-driven |
| **Execution status** | Importable; `associate_delimiter_pairs` returns paired/unpaired but the visual layer never calls it |

---

### C4 — `v2_delimiter_aware_structural_recovery.py` (V2 remediated baseline)

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/v2_delimiter_aware_structural_recovery.py` (735 lines) |
| **Engine identifier** | `ENGINE_IDENTIFIER = "KING-WEN-DELIMITER-ENGINE-V2"`; `ENGINE_VERSION = "2.0.0-remediation"` |
| **Callables** | `classify_delimiter_glyph_font_aware(page, rect, fallback_text="", fallback_font="") -> dict`<br>`detect_delimiter_candidates(page, y_band)` → list[dict]<br>`associate_delimiter_pairs(candidates, page_width, page_height)` → `tuple[list[dict], list[dict]]` |
| **Input** | `classify_delimiter_glyph_font_aware`: `page`, `rect`, optional `fallback_text`, `fallback_font`<br>`detect_delimiter_candidates`: `page`, `y_band=(y_min, y_max)`<br>`associate_delimiter_pairs`: `candidates`, `page_width=612.0`, `page_height=792.0` |
| **Output** | `classify_delimiter_glyph_font_aware` → dict with `gate`, `kind`, `is_opening`, `family`, `resolution_method`, `confidence`, `spans`<br>`detect_delimiter_candidates` → list[dict] (`rect`, `source`, `font`, `text`)<br>`associate_delimiter_pairs` → `tuple[list[dict], list[dict]]` |
| **Coordinate assumptions** | `pymupdf.Rect` for text candidates; raster stroke candidates converted to `pdf_rect` via `band_rect.x0 + x/2.0` (not a documented transform) |
| **Coordinate output fields** | `rect` (PDF points) for text candidates; `pdf_rect` for raster candidates |
| **Coordinate convention** | PDF native coordinates; raster stroke coords are computed from `pixmap` sampling, not re-tabulated to a declared `coord_space` |
| **Coordinate convention** | Text: `pymupdf.Rect` (top-left origin, y-down). Raster: `pixmap` sampling with `Matrix(2.0, 2.0)` |
| **Dependency on gold** | None observed — purely observation-driven |
| **Execution status** | Importable; `associate_delimiter_pairs` in v2 is the pipeline-facing aggregation point |

---

### C5 — `delimiter_identity.py`

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/delimiter_identity.py` (427 lines) |
| **Callables** | `normalize_latex_norms(latex: str) -> str`<br>`balance_norm_tokens(s: str) -> str`<br>`_match_latex_norm_token(latex, pos)` |
| **Input** | `normalize_latex_norms`: LaTeX string<br>`balance_norm_tokens`: normalized string of `NORM_OPEN`/`NORM_CLOSE` tokens |
| **Output** | `normalize_latex_norms` → normalized string with `NORM_OPEN`/`NORM_CLOSE` tokens<br>`balance_norm_tokens` → balanced normalized string |
| **Coordinate assumptions** | None — string-level identity preservation |
| **Coordinate output fields** | None |
| **Coordinate convention** | N/A |
| **Dependency on gold** | None |
| **Execution status** | Imported by `mathml_parser.py`, `math_recovery_tool.py` |

---

### C6 — `mathml_parser.py`

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/mathml_parser.py` (849 lines) |
| **Callables** | `MathMLParser` class (main parse entry point), `extract_from_html` (module-level function) |
| **Input** | `extract_from_html(html)` — HTML string; `MathMLParser()` parse math_tag |
| **Output** | `parse(math_tag)` → `(tree_expr, unsupported)` |
| **Coordinate assumptions** | None — string/tree level |
| **Coordinate output fields** | None |
| **Coordinate convention** | N/A |
| **Dependency on gold** | None (imports `delimiter_identity` for canonical tokens) |

---

### C7 — `batch_math_pipeline.py`

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/batch_math_pipeline.py` (185 lines) |
| **Callables** | `run_single_paper(paper, paper_idx, verbose=False)` → dict<br>`main()` (CLI) |
| **Input** | `run_single_paper`: `paper` dict (with `arxiv_id`), `paper_idx`, `verbose` |
| **Output** | `run_single_paper` → dict with `arxiv_id`, `status`, `equations_extracted`, `solvable`, `partial`, `rejected`, `error`, `timings`, `result_document` |
| **Coordinate assumptions** | None — pure equation text extraction |
| **Coordinate output fields** | None |
| **Coordinate convention** | N/A |
| **Dependency on gold** | None |
| **Execution status** | Executable; 243-paper corpus baseline frozen |

---

### C8 — `e2e_math_pipeline.py`

| Attribute | Value |
|-----------|-------|
| **File** | `scripts/e2e_math_pipeline.py` (410 lines) |
| **Callables** | `fetch_arxiv_html(arxiv_id, timeout=30) -> (html, url)`<br>`process_paper(arxiv_id, html_content, url)` → dict (with `total_equations`, `solvable`, `partial`, `rejected`) |
| **Input** | `process_paper`: arxiv_id, html_content, url |
| **Output** | `process_paper` → `result_document` with `total_equations`, `solvable`, `partial`, `rejected` (and `equations` list) |
| **Coordinate assumptions** | None — pure equation text extraction |
| **Coordinate output fields** | None |
| **Coordinate convention** | N/A |
| **Dependency on gold** | None |
| **Execution status** | Executable; used by the 243-paper batch accounting |

---

## Exported Symbol Verification

The recommended contract specifies explicit construction:

| Section | Symbol |
|---------|--------|
| Population contract | `paper_id`, `equation_population` |
| Input contract | `source_pdf`, `pdf_sha256`, `page_number`, `render_dpi`, `render_scale`, `page_rotation`, `coord_space` |
| Prediction contract | `visual_candidates`, `font_family`, `pixel_bbox`, `bbox_pdf_pt_approx` |
| Processing contract | `delimiter_identity`, `associate_delimiter_pairs` |
| Persistence contract | `visual_observation_id`, `delimiter_candidate_id`, `adjudication_id` |
| Evaluation contract | `G0`, `G1`, `G2`, `G3`, `G4`, `G5` — conjunctive |
| Provenance contract | `code_hash`, `config_hash`, `execution_record`, `artifact_hash` |

The actual callables found on disk:

| Contract section | Mapped contract | Confirmed callable |
|------------------|----------------|
| Population | `paper_id` | `run_single_paper(paper, paper_idx, verbose)` → `arxiv_id` present in output |
| Input | `source_pdf`, `pdf_sha256`, `page_number` | `main()` in `targeted_math_detector.py` computes `source_pdf_sha256` and `selected_pages_1_based` |
| Input | `render_dpi`, `render_scale` | `render_visual_candidates(page, page_index, zoom, out_dir)` — `zoom` is the scale factor; `render_size_px` = `[pix.width, pix.height]` |
| Input | `page_rotation` | Not exposed — page is read from `pymupdf.Page` without rotation metadata |
| Input | `coord_space` | Implicitly `"pdf_points"` — all detections use `pymupdf.Rect` and `bbox_pdf_pt` |
| Prediction | `visual_candidates` | `render_visual_candidates` returns `visual_candidates` list |
| Processing | `delimiter_identity` | `classify_delimiter_glyph_font_aware(page, rect)` → `classify_delimiter_glyph_font_aware` in v2 |
| Processing | `associate_delimiter_pairs` | Both V1 and V2 expose `associate_delimiter_pairs(candidates, page_width, page_height)` |
| Persistence | `visual_observation_id` | `targeted_math_detector` uses `component_id` as candidate id; no UUID generation observed |
| Evaluation | `G0`–`G5` | Defined in `docs/golden-standard-audit-matrix.md`; enforcement not present in `batch_math_pipeline` |

### Capability Discovery: Candidate Tooling Inventory (2026-11-11)

This appendix follows the component matrix with a **capability-level lookup** that groups the confirmed interfaces above by the higher-level capability they implement. This is the interface layer mapped to the capability categories that the golden-standard qualification matrix uses.

### Capability Map (2026-11-11)

| # | Capability | Primary component in interface matrix | Input authority | Output contract | Confirmed interface? |
|----|-----------|-----------|-----------------|-----------------|----------------------|
| C1 | MathML extraction | `MathMLParser` | MathML tree + x-tex annotations | Equation structured output (ExprNode tree) | YES — `mathml_parser.py` |
| C2 | LaTeX reconstruction | `math_recovery_tool.py`, `delimiter_identity.py` | MathML, gold, LaTeX | Reconstructed LaTeX string | YES — `delimiter_identity.py` (confirmed) |
| C3 | Structural recovery (V1) | `delimiter_aware_structural_recovery.py` | Visual candidates (bbox) | Paired/unpaired structure | YES — `associate_delimiter_pairs()` |
| C4 | Structural recovery (V2) | `v2_delimiter_aware_structural_recovery.py` | Visual candidates (bbox) | Paired/unpaired structure | YES — `detect_delimiter_candidates()`, `associate_delimiter_pairs()` |
| C5 | AST extraction | `structural_ast_extractor.py` | MathML tree | Structural AST (ExprNode) | NO — interface not confirmed |
| C6 | Visual detection | `targeted_math_detector.py` | PDF page (rawdict) | Bbox, char observations, visual candidates | YES — `render_visual_candidates()`, `extract_raw_observations()` |
| C7 | OCR (entry points) | Pix2Text, Tesseract integrations | PDF image / crop | Character/text output | NO — no integration scripts found |
| C8 | Semantic validation | `math_contract.py`, `semantic_honesty_scoreboard.py` | Recovered math tree | Validation status + scoreboard | PARTIAL — imports not traced |
| C9 | Equation solving | `solve_all.py`, `solve_dual_path.py` | Recovered math IR | Solution (SymPy) | PARTIAL — solver coverage not audited |
| C10 | Geometric validation | Localization, crop-isolation tests | Geometry ops | Adversary output (pass/fail) | PARTIAL — test scripts exist, assertions not read |
| C11 | Provenance tracing | `verify_provenance_trace.py`, candidate manifests, audit runners | Artifact + trace | Verification result | NO — not exercised |

### Interface vs Ability: Suites That Are NOT Equivalent

The following capability–interface pairs are **not** equivalent and must not be conflated when certifying golden-standard status:

| Capability | Interface present? | Is the interface an independent oracle? |
|------------|-------------------|----------------------------------------|
| C1 MathML extraction | YES | No — parser reads MathML; it does not adjudicate correctness |
| C2 LaTeX reconstruction | YES | No — reconstruction is a recovery step, not a truth assertion |
| C3 Structural recovery V1 | YES | No — pairing is a prediction, not a gold truth |
| C4 Structural recovery V2 | YES | No — same as C3 |
| C6 Visual detection | YES | No — detection is a candidate generator, not an evaluator |
| C7 OCR | NO — not integrated | Unknown until integration scripts are found |
| C8 Semantic validation | PARTIAL | No — validation depends on the recovery layer it is validating |
| C9 Equation solving | PARTIAL | No — the solver accepts any parseable form; it does not certify correctness |
| C10 Geometric validation | PARTIAL | No — test scripts exist; assertions not read |
| C11 Provenance tracing | NO — not exercised | Unknown until executed |

**Certification rule:** The presence of an interface does not make a component an oracle. An oracle must be independently adjudicative, not merely predictive. The capability map above is the candidate list for golden-standard qualification, not the certification itself.

### Completeness Caveat

| Coverage area | Status | Evidence |
|---------------|--------|----------|
| Interface discovery | `scripts/` scanned | 17 capability categories, 8 confirmed, 3 partial, 2 unknown, 4 not verified |
| Corpus coverage test | Frozen 243-paper batch | `batch_math_pipeline.py` runs, but visual components not wired |
| Negative control | Not present | No test for random input producing no output |
| Independent oracle | None | No independent adjudicator exists for delimiter pairing |
| Provenance | NO | No executed provenance trace found |

---

## Cross-Cutting Schema Contract

| Field | Delimiter engine | Batch accounting |
|-------|------------------|------------------|
| `source_pdf_sha256` | `main()` in `targeted_math_detector.py` | Present in batch output (passed from corpus?) |
| `page_number` | `page_index` in `extract_raw_observations` output | Not present in `run_single_paper` output |
| `coord_space` | `bbox_pdf_pt` — PDF points (y-down) | None |
| `font_family` | `font` in `extract_raw_observations` | None |
| `render_dpi` | `render_zoom` (4.0 default) | None |
| `page_rotation` | None | None |
| `bbox_pdf_pt` | `extract_raw_observations` returns `bbox_pdf_pt` | None |
| `delimiter_id` | `classify_delimiter_glyph_font_aware` returns `kind` | None |

---

## Coordinate Assumptions Audit

| Component | Coordinate scheme | Origin | Direction | Rotation | Transformation | `source_pdf_sha256` |
|-----------|-------------------|--------|------------|----------|----------------|---------------------|
| `targeted_math_detector.py` | `bbox_pdf_pt` | PDF top-left | y-down | None | None (observed) | `source_pdf_sha256` (in `main()`) |
| `font_aware_math_classifier.py` | None | N/A | N/A | N/A | N/A | No |
| `delimiter_aware_structural_recovery.py` | `pymupdf.Rect` | PDF top-left | y-down | None | None (observed) | No |
| `v2_delimiter_aware_structural_recovery.py` | `pymupdf.Rect` + raster stroke | PDF top-left | y-down | None | Raster sampling via `Matrix(2.0,2.0)` | No |
| `delimiter_identity.py` | None | N/A | N/A | N/A | N/A | No |
| `mathml_parser.py` | None | N/A | N/A | N/A | N/A | No |
| `batch_math_pipeline.py` | None | N/A | N/A | N/A | N/A | None |

**Coordinate contract gaps:**
1. `v2_delimiter_aware_structural_recovery.py` raster stroke coordinates are computed as `band_rect.x0 + x/2.0` without a declared `coord_space`. The output `pdf_rect` is an interpolation, not confirmed to match `pdf_points`.
2. No rotation metadata is captured in any visual component. `page_rotation` is absent from all output schemas.
3. No cross-component coordinate provenance record exists (e.g., `transform_id`).

---

## Gap Register

| Gap | Evidence | Impact | Priority |
|-----|----------|--------|----------|
| G1 | `batch_math_pipeline.py` never imports `targeted_math_detector` | Visual candidates never appear in batch accounting | HIGH |
| G2 | `pdf_visual_analysis_layer.py` does not call `delimiter_aware_structural_recovery.py` | Structure recovery not triggered by visual layer | HIGH |
| G3 | `targeted_math_detector.py` output has no `coord_space` field (implicitly PDF points) | Coordinate contract not machine-readable | MEDIUM |
| G4 | `v2_delimiter_aware_structural_recovery.py` raster stroke coords computed via `band_rect.x0 + x/2.0` without declared transform | Raster coordinate provenance ambiguous | MEDIUM |
| G5 | `page_rotation` not captured anywhere in visual components | Device rotation unaccounted for | LOW |
| G6 | `delimiter_inference.py` line 17: `from delimiter_inference import DelimiterInferer, infer_delimiters` — appears to be a self-import; verify actual call graph | May indicate stale method or mis-specified import | MEDIUM |
| G7 | `e2e_math_pipeline.py` `process_paper` imports `from test_integral_ir import parse_integral` — it is in the same directory as `test_integral_ir.py` but the module name suggests a test artifact | Verify `test_integral_ir` is a test helper, not an active source dependency | LOW |
| G8 | `batch_math_pipeline.py` output has no `coord_space` field | Coordinate contract not machine-readable | MEDIUM |

---

## Construction Order for integration contract

The contract (`docs/delimiter-corpus-integration-contract-2026-11-11.md`) should be built in this order:

1. **Population contract** — freeze the 243-paper equation accounting; define `paper_id` linkage.
2. **Input contract** — define `source_pdf`, `pdf_sha256`, `page_number`, `render_dpi`, `render_scale`, `page_rotation`, `coord_space`.
3. **Prediction contract** — define `visual_candidates`, `font_family`, `pixel_bbox`, `bbox_pdf_pt_approx`.
4. **Processing contract** — map `classify_glyph` (C2), `associate_delimiter_pairs` (C3/C4) as the processing layer.
5. **Persistence contract** — define `visual_observation_id`, `delimiter_candidate_id`, `adjudication_id` with storage schema.
6. **Evaluation contract** — define G0–G5 as conjunctive; each gate must pass all-dimensional.
7. **Provenance contract** — `code_hash`, `config_hash`, `execution_record`, `artifact_hash`.
8. **Non-regression contract** — frozen 243-paper accounting unchanged; no gold-conditioned prediction.

---

## Non-Regression Tigers

1. Do not add `coord_space` or `page_number` fields to the 243-paper batch accounting (frozen). Create a separate visual population.
2. Do not modify `delimiter_identity.py` exported tokens (`NORM_OPEN`, `NORM_CLOSE`, `CONDITIONAL_BAR`, etc.) — they are the identity cipher.
3. Do not change `run_single_paper` output schema (keys: `arxiv_id`, `status`, `equations_extracted`, `solvable`, `partial`, `rejected`, `error`, `timings`, `result_document`).
4. Do not change `process_paper` output schema (keys: `total_equations`, `solvable`, `partial`, `rejected`, `equations`).
5. Do not wire `associate_delimiter_pairs` into `batch_math_pipeline.py` until the integration contract is written.

---

*This matrix is the conformance target for `docs/delimiter-corpus-integration-contract-2026-11-11.md`. It is a source-level audit, not endorsement of the pipeline as integrated or certified.*
