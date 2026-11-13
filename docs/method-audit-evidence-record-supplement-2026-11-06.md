# Audit Evidence Record — Supplement 1: Ignored Output Artifact Inventory

**Date:** 2026-11-06  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b`  
**Working-tree status:** 11 untracked files + 1 modified (`scripts/e2e_math_pipeline.py`)

---

## 1. Evidence Structure — Three Distinct Layers

The evidence record operates across three independent layers. These layers are **not interchangeable**; each has a distinct evidentiary role.

### Layer 1: Tracked Source and Tests

| Category | Content | Evidentiary Role |
|----------|---------|------------------|
| Tracked source files | `scripts/targeted_math_detector.py`, `scripts/pdf_visual_analysis_layer.py`, `scripts/pdf_visual_corpus_integrator.py`, etc. | Implementation contracts |
| Tracked test files | `tests/test_structural_preservation.py`, `tests/test_delimiter_structural_recovery.py` | Direct behavioral assertions |
| Frozen docs | `docs/kings-wen-function-coverage-audit-report-2026-11-06.md` | Original frozen scope |

**Role:** Establish contracts, test associations, and frozen scope. This layer is the primary audit surface.

---

### Layer 2: Untracked Working-Tree Source

| Category | Content | Evidentiary Role |
|----------|---------|------------------|
| `scripts/pdf_visual_analysis_layer.py` | 219 lines, 7,238 bytes | Local implementation; not committed |
| `scripts/pdf_visual_corpus_integrator.py` | 164 lines, 5,876 bytes | Local implementation; not committed |
| `scripts/check_contracts.py` | (deleted after use) | Ad-hoc verification script |
| `scripts/inspect_raw_observation_retention.py` | (deleted after use) | Ad-hoc verification script |
| `scripts/batch_math_pipeline.py` | (current) | Pipeline runner |

**Role:** Document local implementations present in the working tree but not yet committed to any branch. These are implementation artifacts, not behavioral evidence.

---

### Layer 3: Ignored Output Artifacts

| Category | Count | Total Size | Evidentiary Status |
|----------|-------|-----------|-------------------|
| Python caches (`__pycache__/`, `*.pyc`) | ~200 | ~100MB | ❌ Not evidence |
| Node modules (`node_modules/`) | 143 | 23MB | ❌ Not evidence |
| Python venv (`.venv/`) | ~500 | ~500MB+ | ❌ Not evidence |
| Type checker cache (`.mypy_cache/`) | ~20 | ~15MB | ❌ Not evidence |
| SHAP-E cache (`shap_e_model_cache/`) | 1 dir | ~834MB | ❌ Not evidence |
| JKD ingestion binary | 1 file | 118MB | ⚠️ Sensitive; not audit evidence |
| Generated inventories | 2 files | 53MB | ❌ Not behavioral evidence |
| **Total** | **876** | **~1.4GB** | **Provenance not established** |

**Role:** Document on-disk experimental outputs and caches. **Provenance for these artifacts is not established** — they are not automatically attributable to the audited functions.

---

## 2. Evidence Disposition Table

| Finding | Correct Interpretation |
|---------|------------------------|
| 876 ignored files, ~1.4 GB | Reported on-disk inventory; **not necessarily all related to this audit** |
| 834 MB model-cache temporary file | Large ignored cache artifact; **not evidence of detector execution** |
| 118 MB `jkd_ingestion_binary.jsonl` | Sensitive ignored data; **do not expose or redistribute its contents** |
| 31 MB / 22 MB generated inventories | Generated repository inventories; **not behavioral evidence** |
| Arena math audit PNGs | Visual output artifacts; **producer attribution requires source-path evidence** |
| OCR polarity ablation artifacts | Separate experimental output population; **do not automatically attribute to the visual analysis layer** |
| Cross-reference JSONL | Existing cross-reference output; **not proof that the corpus integrator generated it** |
| Empty detector JSON (0 bytes) | Zero-byte artifact; **function execution remains NOT VERIFIED** |

**Key principle:** File size or artifact count does not establish successful processing, valid provenance, completeness, or correctness.

---

## 3. Gate Status (Unchanged)

| Item | Status |
|------|--------|
| Read-only contract inspection | ✅ Complete |
| Test discovery | ✅ Complete |
| Direct coverage | ✅ 6 functions |
| Indirect execution | ✅ 1 function |
| Uncovered / unclassified | ✅ 12 functions |
| Test execution | None |
| Production wiring | Not attempted |
| Corpus execution | Not attempted |
| Milestone B | OPEN / NOT VERIFIED |
| Frozen benchmark/certification | Not affected; ignored artifacts excluded |

---

## 4. Supplemental Document Policy

Per the user's instruction, this report is a **separate supplemental inventory**, not a replacement for the frozen audit.

| Document | Role |
|----------|------|
| `docs/kings-wen-function-coverage-audit-report-2026-11-06.md` | ✅ Frozen authoritative record (original scope) |
| `docs/kings-wen-function-coverage-audit-report-2026-11-06-corrected.md` | ✅ Supplemental — 19-function correction |
| `docs/method-audit-large-ignored-files.md` | ✅ Supplemental — ignored output inventory |

These documents are **linked supplemental records**. None is silently folded into or substituted for the frozen report.

---

## 5. Controls Applied

1. ✅ Ignored artifacts excluded from frozen benchmark and certification denominators
2. ✅ File size and artifact count not treated as evidence of successful processing
3. ✅ Producer attribution requires source-path evidence for each artifact
4. ✅ Audit report and supplemental records remain separate, linked documents

---

*End of Supplement 1.*
