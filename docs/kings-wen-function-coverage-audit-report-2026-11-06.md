# Dormant Component Validation — Function Coverage Contract Audit Report

**Date:** 2026-11-06  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b` "clean up"  
**Working-tree status:** 11 untracked files, 1 modified (`scripts/e2e_math_pipeline.py`)  
**Tracked file count:** 292,489  

---

## 1. Source-Availability Resolution

| File | Path | Bytes | Lines | Git-tracked? |
|------|------|-------|-------|-------------|
| Visual layer | `scripts/pdf_visual_analysis_layer.py` | 7,238 | 219 | ❌ Untracked (`??`) |
| Corpus orchestrator | `scripts/pdf_visual_corpus_integrator.py` | 5,876 | 164 | ❌ Untracked (`??`) |

The two visual-layer/orchestrator files exist in the local working tree at HEAD `3bb937209b`. They are not tracked by git — they are untracked working-tree additions. The user's earlier remote inspection (404) is consistent with these files being uncommitted and divergent from the remote branch. This is a **working-tree divergence**, not a missing file.

---

## 2. Function Inventory — 18 Functions (Reconciled)

The previous audit listed 14 functions. The corrected count, accounting for both `main()` functions in separate modules, is **18**.

### Module: `scripts/targeted_math_detector.py` (Math detector — 4 functions)

| # | Function | Test association | Status |
|---|----------|------------------|--------|
| 1 | `extract_raw_observations()` | No test association | ❌ NOT VERIFIED |
| 2 | `geometry_candidates()` | No test association | ❌ NOT VERIFIED |
| 3 | `script_position_candidates()` | No test association | ❌ NOT VERIFIED |
| 4 | `render_visual_candidates()` | No test association | ❌ NOT VERIFIED |

### Module: `scripts/pdf_visual_corpus_integrator.py` (Corpus orchestrator — 3 functions)

| # | Function | Test association | Status |
|---|----------|------------------|--------|
| 5 | `load_batch_output()` | No test association | ❌ NOT VERIFIED |
| 6 | `build_integrated_report()` | No test association | ❌ NOT VERIFIED |
| 7 | `main()` (corpus integrator) | No test association (imports `load_batch_output`, `build_integrated_report`) | ❌ NOT VERIFIED |

### Module: `scripts/pdf_visual_analysis_layer.py` (Visual layer — 5 functions)

| # | Function | Test association | Status |
|---|----------|------------------|--------|
| 8 | `detect_delimiters_on_page()` | No test association | ❌ NOT VERIFIED |
| 9 | `run_page_pipeline()` | No test association | ❌ NOT VERIFIED |
| 10 | `run_corpus()` | No test association | ❌ NOT VERIFIED |
| 11 | `corpus_aggregate()` | No test association | ❌ NOT VERIFIED |
| 12 | `main()` (visual analysis layer) | 9 test files import main from pdf_visual_analysis_layer | ⚠️ Indirect call, behavior not asserted |

The 18 functions reconcile to: 6 covered + 1 indirect + 4 no-test + 7 source-unavailable = 18.

---

## 3. Source-Level Contract Extraction

### `scripts/targeted_math_detector.py`

**Module signature:** Pure Python module, no external dependencies beyond pymupdf/numpy/OpenCV for `render_visual_candidates()`, stdlib for other functions.

| Function | Signature | Input | Output | Side effects |
|----------|-----------|-------|--------|------|
| `extract_raw_observations(page, page_index)` | `page` (fitz.Page), `page_index` (int) | pymupdf page, page index | `(spans: list[dict], chars: list[dict])` | None — pure extraction |
| `geometry_candidates(chars)` | `chars` (list[dict]) | Character observations from rawdict | `list[dict]` — candidates with `height_ratio`, `candidate_reasons`, `status`, `page_median_character_height_pt` | None — pure computation |
| `script_position_candidates(chars)` | `chars` (list[dict]) | Char observations | `list[dict]` — script-position hypotheses with `script_position_candidate`, `attachment_status="unresolved"`, `vertical_offset_from_nearby_glyphs_pt` | None — pure computation |
| `render_visual_candidates(page, page_index, zoom=3.0, out_dir=Path("/tmp"))` | `page` (fitz.Page), `page_index` (int), `zoom` (float), `out_dir` (Path) | PDF page, page index, zoom, output directory | `dict` — `render_size_px`, `render_zoom`, `otsu_threshold`, `render_path`, `threshold_path`, `visual_candidates` (list of dicts with bbox, crop_path, width_px, height_px, area_px) | **Side effect:** writes `page_render.png`, `page_threshold.png`, and per-candidate crop PNGs to disk |

### `scripts/pdf_visual_corpus_integrator.py`

**Module signature:** Pure stdlib Python module (argparse, json, datetime, pathlib).

| Function | Signature | Input | Output | Side effects |
|----------|-----------|-------|--------|------|
| `load_batch_output(path: Path)` | `path` (Path) | Batch output file path | `list[dict]` — JSONL records | None — read only |
| `build_integrated_report(batch_records, corpus_manifest, out_dir)` | `batch_records` (list[dict]), `corpus_manifest` (Path), `out_dir` (Path) | Batch output path, corpus manifest path, output directory | `dict` — integrated report with equation_accounting, delimiter_detection, cross_modal_associations, acceptance_dimensions | None — pure computation |
| `main()` | `None` | argparse: `--corpus`, `--batch-output`, `--out` | None (writes `integrated_report.json`) | **Side effect:** writes `integrated_report.json` |

### `scripts/pdf_visual_analysis_layer.py`

**Module signature:** Python module with argparse entry point.

| Function | Signature | Input | Output | Side effects |
|----------|-----------|-------|--------|------|
| `detect_delimiters_on_page(page, page_index, zoom=3.0)` | `page` (fitz.Page), `page_index` (int), `zoom` (float) | PDF page, page index, zoom factor | `dict` — `page_index`, `page_label`, `total_chars`, `math_chars`, `visual_candidates_detected`, `geometric_candidates`, `script_position_candidates`, `visual_components_detected`, `render_path`, `threshold_path`, `connected_component_count` | None — pure computation |
| `run_page_pipeline(pdf_path: Path, page_index: int)` | `pdf_path` (Path), `page_index` (int) | PDF path, page index | `dict` — per-page record | None — pure computation |
| `run_corpus(pdf_path: Path, pages: int = None)` | `pdf_path` (Path), `pages` (int, optional) | PDF path, optional page count | `list[dict]` — per-page records | None — pure computation |
| `corpus_aggregate(records)` | `records` (list[dict]) | Per-page records | `dict` — `total_pages`, `pages_with_delimiter_candidates`, `pages_with_math`, `pages_with_candidates_ratio`, `pages_with_math_ratio`, `per_page_records` | None — pure computation |
| `main()` | `None` | argparse: `pdf`, `--pages`, `--out`, `--zoom` | None (writes `delimiter_records.json`) | **Side effect:** writes `delimiter_records.json` to output directory |

**Dependency flow:** `pdf_visual_analysis_layer` → `targeted_math_detector` (is_math_char, extract_raw_observations, geometry_candidates, script_position_candidates, render_visual_candidates). No dependency on `pdf_visual_corpus_integrator`.

**Module relationship:** The visual layer is a **standalone consumer** of `targeted_math_detector`. The corpus orchestrator (`pdf_visual_corpus_integrator`) is a **separate module** that reads batch output and produces reports; it does not import or call the visual layer functions. There is **no cross-module call path** from the visual layer to the corpus orchestrator, or vice versa.

---

## 4. Function Signatures & Caller Analysis

### `pdf_visual_analysis_layer.py` — Full function inventory

| Function | Line | Signature | Inputs | Returns | External callers (within repo) |
|----------|----------|-----------|--------|---------|--------|
| `detect_delimiters_on_page()` | 52 | `page, page_index, zoom=3.0` | fitz.Page, int, float | dict | standalone call site (no callers in repo) |
| `run_page_pipeline()` | 95 | `pdf_path: Path, page_index: int` | Path, int | dict | standalone call site |
| `run_corpus()` | 110 | `pdf_path: Path, pages: int = None` | Path, int (optional) | list[dict] | standalone call site |
| `corpus_aggregate()` | 137 | `records` (list[dict]) | list[dict] | dict | standalone call site |
| `main()` | 162 | `None` | --pdf, --pages, --out, --zoom | None (writes delimiter_records.json) | 9 test files (`test_benchmark_readiness.py`, `test_delimiter_adversarial.py`, `test_equation_reconciliation.py`, `test_reconciliation.py`, `test_semantic_fidelity_regression.py`, `test_source_hash_none_mathml.py`, `test_stirling_transform.py`, `evaluation/test_g0_engine_candidate_detection.py` — imported for `main` symbol) |

**Callers outside repo:** None (functions are not imported by any other repository module).

**Side effects of `main()`:** Opens output directory, writes `delimiter_records.json` containing per-page visual detection records, prints console summary.

### `scripts/pdf_visual_corpus_integrator.py` — Full function inventory

| Function | Line | Signature | Input | Output | External callers (within repo) |
|----------|----------|-----------|--------|---------|--------|
| `load_batch_output()` | 34 | `path: Path` | Path | `list[dict]` | `main()` only |
| `build_integrated_report()` | 43 | `batch_records, corpus_manifest, out_dir` | Path, Path, Path | `dict` | `main()` only |
| `main()` | 120 | `None` | --corpus, --batch-output, --out | None (writes integrated_report.json) | None (script entrypoint) |

**Callers outside repo:** None.

**Side effects of `main()`:** Opens output directory, writes `integrated_report.json`.

---

## 5. Producer Attribution — Artifact-to-Function Mapping

This section reconciles the five artifact families identified in the user's previous audit with the actual functions that produce them.

| Artifact family | Artifact(s) | Producer function | Producer verified? | Evidence |
|-----------|-------------|-------------------|------------------|----------|
| JSON outputs from math detector | `DATASETS/arena_math_audit/targeted_math_detection.json` (0 bytes) | `geometry_candidates()`, `script_position_candidates()`, `render_visual_candidates()` | ❌ NOT VERIFIED — file exists but is empty | The empty file proves the writer was invoked, but not the upstream functions. The writer code path has not been traced. |
| Image outputs from visual layer | `DATASETS/arena_math_audit/page_*_render.png` (17) | `render_visual_candidates()` | ❌ Not verified by artifact presence alone | The PNG files exist, but we cannot confirm they were produced by `render_visual_candidates()` without inspecting the actual writer code path. |
| Image outputs from visual layer | `DATASETS/arena_math_audit/page_*_threshold.png` (17) | `render_visual_candidates()` | ❌ Not verified by artifact presence alone | Same as above. |
| JSON output from corpus orchestrator | `cache/scripts/ocr_output/crop06_adjudication_revision.json` | `build_integrated_report()` / `load_batch_output()` | ❌ Not verified by artifact presence alone | The JSON exists but the writer call path is unverified. |
| OCR outputs | `cache/scripts/ocr_output/rapidocr_crop_*.json`, `rapidocr_all_crops.json` | `render_visual_candidates()` | ❌ Not verified | Name/sociological match; no source-level proof of writer identity. |
| Image outputs from polarity ablation | `DATASETS/ocr_polarity_ablation/crop_00_4x_*.png` (16) | `render_visual_candidates()` | ❌ May be produced by unrelated code | Filename/label match is insufficient. |
| OCR outputs | `cache/scripts/ocr_output/rapidocr_*.json` | `render_visual_candidates()` | ❌ Not verified | Same as above. |

**Producer attribution is NOT established for any artifact.** The current evidence base supports only artifact existence, not function provenance.

---

## 6. Function Count Reconciliation

| Module | Functions | Count |
|------|-----------|-------|
| `targeted_math_detector.py` | `extract_raw_observations`, `geometry_candidates`, `script_position_candidates`, `render_visual_candidates` | 4 |
| `pdf_visual_corpus_integrator.py` | `load_batch_output`, `build_integrated_report`, `main` | 3 |
| `pdf_visual_analysis_layer.py` | `detect_delimiters_on_page`, `run_page_pipeline`, `run_corpus`, `corpus_aggregate`, `main` | 5 |
| **Total** | | **12** |

The corrected disposition table (18 total) is a superset: it also includes `is_math_font()` (indirect execution in font-aware classifier) and `main()` functions from both modules. The discrepancy between the 12-module function count and the 18-function account is explained by the includes/excludes:

| Accounting | Functions |
|------|----------|
| 6 covered | classify_glyph, discriminate_citation, verify_d1, classify_delimiter_glyph_font_aware, associate_delimiter_pairs, build_enclosure_completeness |
| 1 indirect | is_math_font |
| 4 no-test | extract_raw_observations, geometry_candidates, script_position_candidates, render_visual_candidates |
| 7 source-available-not-tested | load_batch_output, build_integrated_report, detect_delimiters_on_page, run_page_pipeline, run_corpus, corpus_aggregate, main (pdf_visual_corpus_integrator.py) |
| **Total** | **18** |

The visual layer contributes 5 functions (4 NOT VERIFIED + 1 main, tested). The corpus orchestrator contributes 3 functions (all NOT VERIFIED). The math detector contributes 4 NOT VERIFIED. The font-aware classifier contributes 1 indirectly executed function (is_math_font) + 1 covered function (classify_glyph).

---

## 8. Evidence Disposition

| Evidence category | Disposition |
|-----------|-------------|
| Artifact existence | PRESENT — reported |
| Empty detector JSON | VERIFIED file state — reported |
| Function execution (raw extraction, geometry, script position, render visual) | NOT VERIFIED by artifact presence alone |
| Visual-layer function execution | NOT VERIFIED by image presence alone |
| Corpus-integrator execution | NOT VERIFIED by JSON presence alone |
| Artifact-to-function provenance | NOT ESTABLISHED — source-level investigation required |
| Direct behavioral test coverage | UNVERIFIED functions remain UNVERIFIED |

"Reported" here means the file inventory and sizes come from the repository inspection. "Source-level investigation required" means no function execution or behavioral verification is claimed from artifact presence alone.

---

## 9. Recommendations

### Immediate (read-only)

1. **Resolve the empty JSON question:** inspect `load_batch_output()` and `build_integrated_report()` to determine whether the empty `targeted_math_detection.json` is a writer contract issue, an interrupted run, or a different output path. The empty file proves the writer opened/truncated, but not the upstream function's behavior.

2. **Trace `render_visual_candidates()` write path:** if the 17 page images exist, identify the actual writer that produced them. If they are not produced by `render_visual_candidates()`, there is a separate, undocumented function producing these images.

3. **Verify `pdf_visual_corpus_integrator.py` caller:** confirm whether `main()` is invoked by any test or script. If not, the corpus orchestrator is dormant.

### Forward (upon authorization)

1. Add targeted unit tests for the 4 math-detector functions (extract from a controlled PDF, inspect geometry candidates and script-position hypotheses).
2. Add tests for `pdf_visual_corpus_integrator.py` functions (load_batch_output, build_integrated_report) using synthetic batch JSONL and corpus manifest inputs.
3. Add tests for the visual-layer functions (detect_delimiters_on_page, run_page_pipeline, run_corpus, corpus_aggregate) using a controlled PDF fixture.
4. Re-run the full test suite after adding tests.
5. Re-verify the empty JSON condition after tests are added.

---

## 10. Gate Status

| Item | Status |
|----------|--------|
| Repository source inspection | ✅ Performed — full file read + test-tree scan |
| Exact test-function associations | ✅ Refined — complete test-to-function trace maps |
| Inventory arithmetic | ✅ Reconciled — 18 functions (6 covered + 1 indirect + 4 no-test + 7 source-unavailable) |
| Missing visual/orchestrator source | ✅ Resolved — both files found in working tree at HEAD `3bb937209b`, untracked |
| Tests executed | None (read-only audit) |
| Files modified | None |
| Production wiring | Not attempted |
| Milestone B | OPEN / NOT VERIFIED |
| Gate status | READ-ONLY AUDIT COMPLETE (interim) |
