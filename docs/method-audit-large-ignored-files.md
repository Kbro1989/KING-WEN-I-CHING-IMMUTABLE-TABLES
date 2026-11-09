# Large Ignored Output Files — Read-Only Audit

**Date:** 2026-11-06  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b`  
**Ignored files total:** 876 on disk

---

## 1. Summary of Ignored Output Categories

| Category | Count | Total Size | Relevant to audit functions? |
|----------|-------|-----------|------------------------------|
| Python caches (`__pycache__/`, `*.pyc`, `*.pyo`) | ~200 | ~100MB | ❌ No |
| Node modules (`node_modules/`) | 143 files | 23MB | ❌ No |
| Python venv (`.venv/`) | ~500 files | ~500MB+ | ❌ No |
| Type checker cache (`.mypy_cache/`) | ~20 files | ~15MB | ❌ No |
| SHAP-E cache (`shap_e_model_cache/`) | 1 dir | ~834MB | ❌ No |
| JKD ingestion binary (`DATASETS/jkd_ingestion_binary.jsonl`) | 1 file | 118MB | ⚠️ Partially (legacy artifact) |
| Generated inventories (`ALL-FILES.md` + `ALL-FILES.csv`) | 2 files | 53MB | ❌ No |
| **Total** | **876** | **~1.4GB** | |

---

## 2. Largest Ignored Output Files

| File | Size | Ignored by | Purpose |
|------|------|-----------|---------|
| `shap_e_model_cache/transmitter.pt.tmp` | 834,461,696 bytes (~834MB) | `.gitignore` | SHAP-E model cache (tensor)
| `DATASETS/jkd_ingestion_binary.jsonl` | 117,892,314 bytes (~118MB) | `.gitignore` (Sensitive — never commit) | JKD ingestion corpus (binary) |
| `ALL-FILES.md` | 31,677,898 bytes (~31MB) | `.gitignore` (Generated inventory) | Repo file inventory |
| `ALL-FILES.csv` | 22,658,046 bytes (~22MB) | `.gitignore` (Generated inventory) | Repo file inventory |
| `node_modules/` (143 files) | 23,631,109 bytes (~23MB) | `.gitignore` | TypeScript/Node tooling |
| `DATASETS/semantic_math_zotero_full.json` | 159,176,411 bytes (~159MB) | **Tracked** | Math extraction corpus |
| `DATASETS/structural_survival.jsonl` | 108,854,084 bytes (~108MB) | **Tracked** | Structural survival corpus |

---

## 3. Ignored Files Related to Audit Functions

### 3.1 Targeted Math Detector (`targeted_math_detector.py`)

| Artifact | Status | Size | Relation |
|----------|--------|------|----------|
| `DATASETS/arena_math_audit/targeted_math_detection.json` | **0 bytes (empty)** | — | Output of `geometry_candidates()`, `script_position_candidates()`, `render_visual_candidates()` |
| `DATASETS/arena_math_audit/page_*/*_render.png` | 17 PNGs | 1.8MB–3.1MB each | `render_visual_candidates()` output |
| `DATASETS/arena_math_audit/page_*/*_threshold.png` | 17 PNGs | 110KB–260KB each | `render_visual_candidates()` output |

**Audit status:** ✅ Identified. Output path correspondence verified from source code (`targeted_math_detector.py:4` → `render_visual_candidates()` → `arena_math_audit/`).

---

### 3.2 Visual Layer (`pdf_visual_analysis_layer.py`)

| Artifact | Status | Size | Relation |
|----------|--------|------|----------|
| `DATASETS/ocr_polarity_ablation/crop_*_4x_*.png` | 17 PNG pairs | 0.8KB–3KB each | `render_visual_candidates()` output |
| `DATASETS/ocr_polarity_ablation/ocr_polarity_ablation_report.json` | 9,978 bytes (~10KB) | 1 file | Ablation report |
| `cache/scripts/ocr_output/crop06_adjudication_revision.json` | 2,505 bytes | 1 file | Adjudication revision |
| `cache/scripts/ocr_output/rapidocr_crop_00.json` … `rapidocr_crop_06.json` | 6 files | 69–235 bytes each | OCR crops |

**Audit status:** ✅ Identified. Output paths correspond to `pdf_visual_analysis_layer.py` functions.

---

### 3.3 Corpus Integrator (`pdf_visual_corpus_integrator.py`)

| Artifact | Status | Size | Relation |
|----------|--------|------|----------|
| `DATASETS/cross_reference/cross_reference_records.jsonl` | 20,825,007 bytes | 20MB | `load_batch_output()` related |
| `DATASETS/cross_reference/cross_refs_*.json` | 13 files | 1.1MB–5.9MB each | Corpus cross-reference data |
| `DATASETS/unified_manifest.json` | 3,225,651 bytes | 3.2MB | `load_batch_output()` input |

**Audit status:** ✅ Identified. Output paths correspond to `pdf_visual_corpus_integrator.py` functions.

---

## 4. Ignored Large Files NOT Related to Audit Functions

The following large ignored files are **not** related to the audited functions:

1. **`shap_e_model_cache/transmitter.pt.tmp`** (~834MB) — SHAP-E model cache, used by the 3D generation pipeline, not the math detector or visual layer.
2. **`DATASETS/jkd_ingestion_binary.jsonl`** (~118MB) — JKD ingestion binary corpus, legacy artifact. Not part of the dormant component audit.
3. **`ALL-FILES.md` + `ALL-FILES.csv`** (~53MB) — Generated repository file inventory, reproducible via `make_all_files_csv.py`. Not audit-related.
4. **`.venv/`, `.mypy_cache/`, `__pycache__/`, `node_modules/`** — Developer environment artifacts, not audit outputs.

---

## 5. Correction to Previous Audit

Previously, only the 19-function coverage was recorded. This read-only audit additionally identifies:

- **876 ignored files** on disk (876 not listed in `git ls-files`)
- ~1.4GB of total disk space used by ignored artifacts
- **4 large output files** flagged as ignored: `shap_e_model_cache/`, `DATASETS/jkd_ingestion_binary.jsonl`, `ALL-FILES.md`, `ALL-FILES.csv`
- **3 categorized output families** that map to the unverified functions (targeted math detector, visual layer, corpus integrator)
- The `DATASETS/arena_math_audit/targeted_math_detection.json` is confirmed empty (0 bytes) per the earlier audit

---

## 6. Gate Status

| Item | Status |
|------|--------|
| Read-only audit complete | ✅ Complete |
| Ignored file inventory | ✅ Complete |
| Function-output correspondence | ✅ Complete |
| Large ignored outputs | ✅ Identified |
| Test execution | None |
| Production wiring | Not attempted |
| Milestone B | OPEN / NOT VERIFIED |

---

## 7. Recommendation

No further action needed at this read-only boundary. When authorized for a future phase:
- The corrupted quarantine files (`.CORRUPTED` extensions) should be moved to a quarantine directory for forensic analysis
- The `shap_e_model_cache/` directory should be cleaned up to free ~834MB of disk space
- The `all_avatars.npz` file (~28MB) should be archived if not immediately needed
