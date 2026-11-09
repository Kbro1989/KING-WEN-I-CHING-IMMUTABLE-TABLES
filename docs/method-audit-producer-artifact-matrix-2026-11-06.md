# Producer-to-Artifact Provenance Matrix

**Date:** 2026-11-06  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b`  
**License:** Read-only audit — no code changes, no test execution

---

## 1. Scope

The matrix covers the 12 functions across the three modules identified in the audit:

| Module | File | Functions |
|--------|------|-----------|
| `scripts/targeted_math_detector.py` | 4 | extract_raw_observations, geometry_candidates, script_position_candidates, render_visual_candidates |
| `scripts/pdf_visual_analysis_layer.py` | 5 | detect_delimiters_on_page, run_page_pipeline, run_corpus, corpus_aggregate, main |
| `scripts/pdf_visual_corpus_integrator.py` | 3 | load_batch_output, build_integrated_report, main |

**Total: 12 functions.** (Plus the 6 covered functions and `is_math_font()` = 19 total in the corrected inventory.)

---

## 2. Provenance Matrix

Each row maps a function to its output artifacts, the output type (in-memory vs. file-based), and whether a producer-artifact trace is possible from source code alone.

| # | Function | Module | Output Type | File Artifact(s) | Output Path(s) in Code | Can Trace? | Status |
|---|----------|--------|-------------|------------------|--------------------------|------------|--------|
| 1 | `extract_raw_observations()` | `targeted_math_detector.py` | In-memory only | None | Returns `(spans, chars)` dicts | ✅ Yes | Producer confirmed, no file artifact |
| 2 | `geometry_candidates()` | `targeted_math_detector.py` | In-memory only | None | Returns `[dict]` (candidate list) | ✅ Yes | Producer confirmed, no file artifact |
| 3 | `script_position_candidates()` | `targeted_math_detector.py` | In-memory only | None | Returns `[dict]` (candidate list) | ✅ Yes | Producer confirmed, no file artifact |
| 4 | `render_visual_candidates()` | `targeted_math_detector.py` | Mixed (in-memory + file writes) | `page_render.png`, `page_threshold.png`, `component_*.png` | `out_dir / f"page_{page_index+1:04d}"` | ✅ Yes | Producer confirmed, artifacts in `arena_math_audit/` |
| 5 | `detect_delimiters_on_page()` | `pdf_visual_analysis_layer.py` | In-memory only | None | Returns per-page record dict | ✅ Yes | Producer confirmed, no file artifact |
| 6 | `run_page_pipeline()` | `pdf_visual_analysis_layer.py` | In-memory only | None | Returns record from detect_delimiters_on_page | ✅ Yes | Producer confirmed, no file artifact |
| 7 | `run_corpus()` | `pdf_visual_analysis_layer.py` | In-memory only | None | Returns `list[dict]` of page records | ✅ Yes | Producer confirmed, no file artifact |
| 8 | `corpus_aggregate()` | `pdf_visual_analysis_layer.py` | In-memory only | None | Returns summary dict | ✅ Yes | Producer confirmed, no file artifact |
| 9 | `main()` | `pdf_visual_analysis_layer.py` | File write | `delimiter_records.json` | `out_dir / "delimiter_records.json"` | ✅ Yes | Producer confirmed, writes `delimiter_records.json` |
| 10 | `load_batch_output()` | `pdf_visual_corpus_integrator.py` | In-memory only | None (reads file) | Loads `batch_records` JSONL | ✅ Yes | Consumer of batch JSONL; no own artifact |
| 11 | `build_integrated_report()` | `pdf_visual_corpus_integrator.py` | In-memory only | None | Returns integrated report dict | ✅ Yes | Producer confirmed, no file artifact |
| 12 | `main()` | `pdf_visual_corpus_integrator.py` | File write | `integrated_report.json` | `args.out / "integrated_report.json"` | ✅ Yes | Producer confirmed, writes `integrated_report.json` |

---

## 3. Artifact-to-Function Mapping (Verified)

### 3.1 Targeted Math Detector Artifacts

| Artifact Directory/File | Function | Confirmed? | Notes |
|-------------------------|----------|------------|-------|
| `DATASETS/arena_math_audit/page_NNNN/page_render.png` | `render_visual_candidates()` | ✅ | Confirmed by source code (line 225-227) |
| `DATASETS/arena_math_audit/page_NNNN/page_threshold.png` | `render_visual_candidates()` | ✅ | Confirmed by source code (line 226-228) |
| `DATASETS/arena_math_audit/page_NNNN/component_NNNN.png` | `render_visual_candidates()` | ✅ | Confirmed by source code (line 247-248) |
| `DATASETS/arena_math_audit/targeted_math_detection.json` | `main()` (and downstream) | ❌ Not verified | 0-byte file; writer invoked, but no data recorded |

**Producer attribution:** All artifacts in `arena_math_audit/` map to `render_visual_candidates()` and `main()` from `targeted_math_detector.py`. The 0-byte JSON does not independently prove the full pipeline ran.

---

### 3.2 Visual Analysis Layer Artifacts

| Artifact Directory/File | Function | Confirmed? | Notes |
|-------------------------|----------|------------|-------|
| `cache/scripts/ocr_output/delimiter_records.json` (if exists) | `main()` (visual analysis layer) | ⚠️ Uncertain | Search for this file yielded `crop06_adjudication_revision.json` in `ocr_output/`, not `delimiter_records.json` |
| `cache/scripts/ocr_output/crop06_adjudication_revision.json` | Unattributable | ❌ Not established | File exists but producer is not confirmed via source-code trace |
| `cache/scripts/ocr_output/rapidocr_crop_00.json` … `rapidocr_crop_06.json` | Unattributable | ❌ Not established | These belong to `render_visual_candidates()` variant, not the visual analysis layer |
| `cache/scripts/ocr_output/rapidocr_all_crops.json` | Unattributable | ❌ Not established | Aggregate of rapidocr crops; no producer function identified |

**Producer attribution:** The visual analysis layer functions (`detect_delimiters_on_page()`, `run_page_pipeline()`, `run_corpus()`, `corpus_aggregate()`) write no output files. Their artifacts are in-memory structures. The `main()` of `pdf_visual_analysis_layer.py` writes `delimiter_records.json` to the `--out` directory, which was not observed in the working tree.

---

### 3.3 Corpus Integrator Artifacts

| Artifact Directory/File | Function | Confirmed? | Notes |
|-------------------------|----------|------------|-------|
| `integrated_report.json` | `main()` (corpus integrator) | ⚠️ Uncertain | Not observed in working tree; function writes to `args.out` |
| `batch_pipeline_output.jsonl` | `load_batch_output()` (consumes this) | ✅ Yes | This file is an input to the corpus integrator, not an output |
| `cross_reference/cross_reference_records.jsonl` | Unattributable | ❌ Not established | Existing output; producer not established |
| `cross_reference/cross_refs_*.json` | Unattributable | ❌ Not established | Existing output; producer not established |

**Producer attribution:** The corpus integrator functions that write files (`main()`) have not been observed writing any artifact in the working tree. The functions that produce in-memory structures (`load_batch_output()`, `build_integrated_report()`) have no file artifacts.

---

## 4. Negative Findings (No Producer Attribution)

| Artifact | Function | Status | Reason |
|----------|----------|--------|--------|
| `crop06_adjudication_revision.json` | All functions | ❌ | File exists; no producer function identified via source-code trace |
| `rapidocr_crop_*.json` (6 files) | All functions | ❌ | File exists; belongs to rapidocr variants, no producer identified |
| `rapidocr_all_crops.json` | All functions | ❌ | File exists; no producer function identified |
| `crop_00.txt` (0 bytes) | All functions | ❌ | 0-byte; producer not established |
| `crop_06_4x.png`, `crop_06_native.png` | All functions | ❌ | File exists; producer function not confirmed |
| `page3_with_bboxes.png` | All functions | ❌ | File exists; producer function not confirmed |

---

## 5. Summary of Evidence Gaps

| Category | Count | Summary |
|----------|-------|---------|
| Functions with confirmed in-memory outputs | 8 | `extract_raw_observations`, `geometry_candidates`, `script_position_candidates`, `render_visual_candidates` (rendered PNGs), `detect_delimiters_on_page`, `run_page_pipeline`, `run_corpus`, `corpus_aggregate` |
| Functions with confirmed file outputs | 3 | `render_visual_candidates` (PNGs), `main()` (visual analysis layer), `main()` (corpus integrator) |
| Functions with producer confirmed but artifact not observed | 2 | `main()` (visual analysis layer) — `delimiter_records.json` not found; `main()` (corpus integrator) — `integrated_report.json` not found |
| Artifacts with no producer attribution | 6 | crop06_adjudication_revision.json, rapidocr_crop_*.json (×6), rapidocr_all_crops.json, crop_00.txt |

---

## 6. Controls Applied

1. ✅ No code execution — all findings from source-code reading and file inventory
2. ✅ No tests executed
3. ✅ Producer attribution requires source-code evidence (file paths in code)
4. ✅ File existence alone is not sufficient for producer attribution
5. ✅ 0-byte files do not independently prove writer invocation
6. ✅ Each attribute requires traceable source-path evidence

---

## 7. Gate Status

| Item | Status |
|------|--------|
| Read-only provenance audit | ✅ Complete |
| Producer-to-artifact matrix | ✅ Complete |
| Fixture verification | ✅ Done (read-only) |
| Test execution | None |
| Production wiring | Not attempted |
| Corpus execution | Not attempted |
| Certification | Blocked |

---

*End of provenance matrix.*
