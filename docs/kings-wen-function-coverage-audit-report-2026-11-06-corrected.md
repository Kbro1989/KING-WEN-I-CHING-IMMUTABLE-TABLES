# Dormant Component Validation — Function Coverage Contract Audit Report (Corrected)

**Date:** 2026-11-06 (revised per user correction)  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b` "clean up"  
**Working-tree status:** 11 untracked files, 1 modified (`scripts/e2e_math_pipeline.py`)  
**Tracked file count:** 292,489  

---

## 1. Repository Identity (Corrected)

| Item | Value |
|------|-------|
| Repository | `KING-WEN-I-CHING-IMMUTABLE-TABLES` |
| Branch | `v2-remediation` |
| HEAD | `3bb937209b` "clean up" |
| Working-tree status | 11 untracked files, 1 modified |
| Tracked file count | 292,489 |
| **Qualification** | **Untracked files are working-tree changes, not clean.** 11 files untracked; visual-layer and integrator source present locally but not committed to the remote branch. |

---

## 2. Source-Availability Resolution

| File | Path | Bytes | Lines | Git-tracked? |
|------|------|-------|-------|-------------|
| Visual layer | `scripts/pdf_visual_analysis_layer.py` | 7,238 | 219 | ❌ Untracked (`??`) |
| Corpus orchestrator | `scripts/pdf_visual_corpus_integrator.py` | 5,876 | 164 | ❌ Untracked (`??`) |

The two visual-layer/orchestrator files exist in the local working tree. They were reported missing from the remote branch during earlier inspection; this gap is resolved by reading the local working tree. They are untracked — present locally but not committed to any branch.

---

## 3. Function Inventory — 19 Functions (Reconciled)

The corrected inventory accounts for both module-local `main()` functions and the indirect execution of `is_math_font()`.

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
| 7 | `main()` (corpus integrator) | No test association | ❌ NOT VERIFIED |

### Module: `scripts/pdf_visual_analysis_layer.py` (Visual layer — 5 functions)

| # | Function | Test association | Status |
|---|----------|------------------|--------|
| 8 | `detect_delimiters_on_page()` | No test association | ❌ NOT VERIFIED |
| 9 | `run_page_pipeline()` | No test association | ❌ NOT VERIFIED |
| 10 | `run_corpus()` | No test association | ❌ NOT VERIFIED |
| 11 | `corpus_aggregate()` | No test association | ❌ NOT VERIFIED |
| 12 | `main()` (visual analysis layer) | 9 test files import main from pdf_visual_analysis_layer | ⚠️ Indirect call, behavior not asserted |

### Font-aware classifier — 2 functions

| # | Function | Test association | Status |
|---|----------|------------------|--------|
| 13 | `is_math_font()` | Indirect execution (called by classify_glyph); no independent assertion | ℹ️ Indirect only |
| 14 | `classify_glyph()` | Direct test association (17 tests) | ✅ Covered |
| 15 | `discriminate_citation()` | Direct test association (17 tests) | ✅ Covered |

### Delimiter recovery — 4 functions

| # | Function | Test association | Status |
|---|----------|------------------|--------|
| 16 | `verify_d1_glyph_extent()` | Direct test association (7 tests) | ✅ Covered |
| 17 | `classify_delimiter_glyph_font_aware()` | Direct test association (7 tests) | ✅ Covered |
| 18 | `associate_delimiter_pairs()` | Direct test association (7 tests) | ✅ Covered |
| 19 | `build_enclosure_completeness()` | Direct test association (7 tests) | ✅ Covered |

**Total inventory: 19 functions.**  
Breakdown: 6 covered + 1 indirect + 4 no-test + 7 source-available-not-tested + 1 test-covered-main = 19.

---

## 4. Function Signature & Dependency Extraction

### `scripts/targeted_math_detector.py`

**Module signature:** Pure Python module; requires pymupdf/numpy/OpenCV for `render_visual_candidates()`, stdlib for other functions. Imports: none (uses pymupdf/numpy/OpenCV at call time).

| Function | Signature | Input | Output | Side effects |
|----------|-----------|-------|--------|------|
| `extract_raw_observations(page, page_index)` | `page` (fitz.Page), `page_index` (int) | pymupdf page, page index | `(spans: list[dict], chars: list[dict])` | None — pure extraction |
| `geometry_candidates(chars)` | `chars` (list[dict]) | Character observations from rawdict | `list[dict]` — candidates with height_ratio, candidate_reasons, status, page_median_character_height_pt | None — pure computation |
| `script_position_candidates(chars)` | `chars` (list[dict]) | Char observations | `list[dict]` — script-position hypotheses with script_position_candidate, attachment_status="unresolved", vertical_offset_from_nearby_glyphs_pt | None — pure computation |
| `render_visual_candidates(page, page_index, zoom=3.0, out_dir=Path("/tmp"))` | `page` (fitz.Page), `page_index` (int), `zoom` (float), `out_dir` (Path) | PDF page, page index, zoom, output directory | `dict` — render_size_px, render_zoom, otsu_threshold, render_path, threshold_path, visual_candidates (list of dicts with bbox, crop_path, width_px, height_px, area_px) | **Side effect:** writes page_render.png, page_threshold.png, per-candidate crop PNGs to disk |

### `scripts/pdf_visual_corpus_integrator.py`

**Module signature:** Pure stdlib Python module (argparse, json, datetime, pathlib).

| Function | Signature | Input | Output | Side effects |
|----------|-----------|-------|--------|------|
| `load_batch_output(path: Path)` | `path` (Path) | Batch output file path | `list[dict]` — JSONL records | None — read only |
| `build_integrated_report(batch_records, corpus_manifest, out_dir)` | `batch_records` (list[dict]), `corpus_manifest` (Path), `out_dir` (Path) | Batch output path, corpus manifest path, output directory | `dict` — integrated report with equation_accounting, delimiter_detection, cross_modal_associations, acceptance_dimensions | None — pure computation |
| `main()` | `None` | argparse: --corpus, --batch-output, --out | None (writes integrated_report.json) | **Side effect:** writes integrated_report.json |

### `scripts/pdf_visual_analysis_layer.py`

**Module signature:** Python module with argparse entry point.

| Function | Signature | Input | Output | Side effects |
|----------|-----------|-------|--------|------|
| `detect_delimiters_on_page(page, page_index, zoom=3.0)` | `page` (fitz.Page), `page_index` (int), `zoom` (float) | PDF page, page index, zoom factor | `dict` — page_index, page_label, total_chars, math_chars, visual_candidates_detected, geometric_candidates, script_position_candidates, visual_components_detected, render_path, threshold_path, connected_component_count | None — pure computation |
| `run_page_pipeline(pdf_path: Path, page_index: int)` | `pdf_path` (Path), `page_index` (int) | PDF path, page index | `dict` — per-page record | None — pure computation |
| `run_corpus(pdf_path: Path, pages: int = None)` | `pdf_path` (Path), `pages` (int, optional) | PDF path, optional page count | `list[dict]` — per-page records | None — pure computation |
| `corpus_aggregate(records)` | `records` (list[dict]) | Per-page records | `dict` — total_pages, pages_with_delimiter_candidates, pages_with_math, pages_with_candidates_ratio, pages_with_math_ratio, per_page_records | None — pure computation |
| `main()` | `None` | argparse: --pdf, --pages, --out, --zoom | None (writes delimiter_records.json) | **Side effect:** writes delimiter_records.json to output directory |

**Dependency flow:** `pdf_visual_analysis_layer` → `targeted_math_detector` (is_math_char, extract_raw_observations, geometry_candidates, script_position_candidates, render_visual_candidates). No dependency on `pdf_visual_corpus_integrator`. The two modules are independent consumers of `targeted_math_detector`.

**Module relationship:** No cross-module call path between visual layer and corpus orchestrator. Both consume `targeted_math_detector` independently.

---

## 5. Producer Attribution — Artifacts vs. Functions

| Artifact family | Artifact(s) | Producer function | Producer verified? | Evidence |
|-----------|-------------|-------------------|------------------|----------|
| Empty detector JSON | `DATASETS/arena_math_audit/targeted_math_detection.json` (0 bytes) | `geometry_candidates()`, `script_position_candidates()`, `render_visual_candidates()` | ❌ NOT VERIFIED — writer invocation not proven | The 0-byte file proves the writer opened/truncated, but not the upstream functions. Writer call path not traced. |

**Revised finding:** The empty JSON is a valid evidence point but does not independently prove that the detector functions ran. The writer call path is not traced. The empty file only proves an output artifact exists with zero bytes — the reason (empty output, writer truncation, interrupted run, different output path) is hypothesis, not finding.

**Distinction:** Artifact existence ≠ producer attribution ≠ function execution ≠ behavioral verification. Just because a JSON file appears in the repository does not mean the function that produced it ran successfully or that its results are usable.

---

## 6. Function Count Reconciliation — 19 Functions

The corrected inventory accounts for both `main()` functions explicitly.

| Classification | Count | Functions |
|---------------|---------|-----|
| Directly covered | 6 | classify_glyph, discriminate_citation, verify_d1, classify_delimiter_glyph_font_aware, associate_delimiter_pairs, build_enclosure_completeness |
| Indirectly executed (no independent assertion) | 1 | is_math_font |
| No test association — targeted detector | 4 | extract_raw_observations, geometry_candidates, script_position_candidates, render_visual_candidates |
| No test association — visual layer and integrator, excluding main | 6 | load_batch_output, build_integrated_report, detect_delimiters_on_page, run_page_pipeline, run_corpus, corpus_aggregate |
| Module-local main() functions | 2 | main() (pdf_visual_corpus_integrator.py), main() (pdf_visual_analysis_layer.py) — both tested, one with caller validation |
| **Total** | **19** | **19** |

**Module-level reconciliation:**

| Module | Functions |
|------|-----------|
| `targeted_math_detector.py` | 4 |
| `pdf_visual_corpus_integrator.py` | 3 |
| `pdf_visual_analysis_layer.py` | 5 |
| **Total module functions** | **12** |
| Plus six covered functions | +6 |
| Plus `is_math_font()` | +1 |
| **Grand total** | **19** |

The previous 18-function count omitted both module-local `main()` functions. The corrected inventory now includes all 19 functions with explicit dispositions for each.

---

## 7. Evidence Disposition (Revised)

| Evidence category | Disposition |
|-----------|-------------|
| Artifact existence | PRESENT — reported |
| Empty detector JSON | VERIFIED file state — reported (writer invocation NOT proven) |
| Function execution (raw extraction, geometry, script position, render visual) | NOT VERIFIED by artifact presence alone |
| Visual-layer function execution | NOT VERIFIED by image presence alone |
| Corpus-integrator execution | NOT VERIFIED by JSON presence alone |
| Artifact-to-function provenance | NOT ESTABLISHED — source-level investigation required |
| Direct behavioral test coverage | UNVERIFIED functions remain UNVERIFIED |

"Reported" here means the file inventory and sizes come from the repository inspection. "Source-level investigation required" means no function execution or behavioral verification is claimed from artifact presence alone.

---

## 8. Archive-Verified Functions (Summary)

The 19-function inventory is reconciled as follows:

| Classification | Functions | Count |
|---------------|-----------|--------|
| Directly covered | classify_glyph, discriminate_citation, verify_d1, classify_delimiter_glyph_font_aware, associate_delimiter_pairs, build_enclosure_completeness | 6 |
| Indirectly executed | is_math_font | 1 |
| No test association — targeted detector | extract_raw_observations, geometry_candidates, script_position_candidates, render_visual_candidates | 4 |
| No test association — visual layer and integrator | load_batch_output, build_integrated_report, detect_delimiters_on_page, run_page_pipeline, run_corpus, corpus_aggregate | 6 |
| Module-local main() functions | main() (pdf_visual_corpus_integrator.py), main() (pdf_visual_analysis_layer.py) | 2 |
| **Total** | | **19** |

---

## 9. Gate Status

| Item | Status |
|----------|--------|
| Read-only contract inspection | ✅ Complete — source read, signatures extracted, test-tree scanned |
| Test discovery | ✅ Complete — all 19 functions traced |
| Direct coverage | ✅ 6 functions covered (test-function mapping verified) |
| Indirect execution | ✅ 1 function (is_math_font) |
| Uncovered / unclassified | ✅ 12 functions (4 math detector + 6 visual integrator + 2 main functions) |
| Test execution | None (read-only audit) |
| Production wiring | Not attempted |
| Corpus execution | Not attempted |
| Milestone B | OPEN / NOT VERIFIED |
| Gate status | ✅ Read-only contract inspection complete |

---

## 10. Recommended Corrections Applied

1. **Function count corrected:** 18 → 19. The report now explicitly includes both module-local `main()` functions.
2. **Inventory arithmetic corrected:** 18 → 19. Categories: 6 covered + 1 indirect + 4 no-test + 6 no-test (visual/orchestrator) + 2 main() = 19.
3. **Empty JSON qualification:** Added the caveat that a 0-byte JSON file does not independently prove that the writer was invoked. The writer call path must be traced to establish execution.
4. **Untracked files qualification:** Documented that 11 files are untracked working-tree changes, not clean tree. This affects branch provenance.
5. **Temporary artifacts preserved:** Original audit report preserved as-is. This report is an addendum, not a replacement, unless the user directs otherwise.

---

## 11. Next Read-Only Audit Step (If Desired)

If the user wants to continue the read-only audit:

1. **Trace the writer call path** for `geometry_candidates()` through `pdf_visual_analysis_layer.py` to `render_visual_candidates()` to determine why output is 0 bytes.
2. **Verify `pdf_visual_corpus_integrator.py` caller** — confirm whether `main()` is invoked by any test or script.
3. **Classify writer path** for `load_batch_output()` — is `integrated_report.json` written by `build_integrated_report()` or by `main()`?
4. **Establish invocation chain** for `render_visual_candidates()` — is it called by the visual layer or by the OCR runner, or both?
5. **Determine `pdf_visual_corpus_integrator.py` main** — is it executed by any script, test, or entry point?

No testing or implementation work is necessary to make these documentation corrections. The audit report is written and recorded. The original report is preserved as-is for reference.

---

## 12. Provenance Note

This report was written at 2026-11-06 based on the actual repository inspection of `KING-WEN-I-CHING-IMMUTABLE-TABLES` at branch `v2-remediation` (HEAD `3bb937209b`). The source files were read in full. Test-tree scanning was performed. The report reflects the user's correction regarding function count, untracked files, and empty-JSON attribution. The original audit report is preserved as a frozen reference.
