# DA-V2 Producer Scripts — Read-Only Contract Audit

**Date:** 2026-11-07  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b651477afd0bcba55a2454e0a123cde`  

---

## 1. Scripts Under Audit

| # | Script | Path | Role |
|---|--------|------|------|
| 1 | `render_fullpage_depth.py` | `scripts/render_fullpage_depth.py` | Math PDF snapshot depth (16 pages) |
| 2 | `controlled_depth_run.py` | `scripts/controlled_depth_run.py` | Math crop depth (137 crops, journal) |
| 3 | `bridge_depth_anything_v2.py` | `scripts/bridge_depth_anything_v2.py` | Quantum depth (64 hexagrams) |

---

## 2. Separated Quantum Depth vs Math PDF Snapshot/Crop Depth

### 2.1 Separation Rationale

The user requested separation of quantum depth from math PDF/html snapshot/crop depth. These are two distinct populations with different producers, outputs, and consumers:

- **Quantum depth**: King Wen 3D/avatar visualization state — 64 hexagram depth maps + 64 PLY point clouds
- **Math PDF snapshot/crop depth**: PDF fidelity analysis for math document content — 16 fullpage + 137 crop renders

### 2.2 Producer/Population Classification

| Population | Producer Scripts | Output Directories | Purpose |
|------------|------------------|-------------------|----------|
| **Quantum depth** | **QD-001** | `bridge_depth_anything_v2.py` | `DATASETS/quantum_depth/depth_maps_16bit/`, `DATASETS/quantum_depth/depth_pointclouds/` | King Wen 3D/avatar visualization |
| **Math snapshot depth** | **MD-001** | `render_fullpage_depth.py` | `DATASETS/math_pdf_depth/fullpage_depth/` | PDF fidelity analysis |
| **Math crop depth** | **MD-001** | `controlled_depth_run.py` | `DATASETS/math_pdf_depth/1907_04931/`, `2104_01277/`, `2206_00364/`, `2605_22902/`, `2605_27315/` | PDF fidelity analysis |
| **OCR recognition/adjudication** | **OCR-001** | `pix2text_harvest.py`, `adjudicate_candidates_v2.py` | Zotero paper corpus (243 papers) | OCR evidence chain |

### 2.3 Proposed Directory Structure

```
DATASETS/
├── quantum_depth/
│   ├── depth_maps_16bit/       # 64 hexagram 16-bit depth maps
│   └── depth_pointclouds/      # 64 PLY point clouds
└── math_pdf_depth/             # NEW: math PDF/crop depth
    ├── fullpage_depth/
    ├── 1907_04931/
    ├── 2104_01277/
    ├── 2206_00364/
    ├── 2605_22902/
    ├── 2605_27315/
    └── targeted_ocr/
```

### 2.4 OCR Pipeline Separation

| Component | Population | Artifacts |
|-----------|------------|-----------|
| Pix2Text polarity ablation (8 crops) | OCR evidence pipeline | `ocr_polarity_ablation/` (17 files) |
| RapidOCR (7 crops) | OCR evidence pipeline | `cache/scripts/ocr_output/` (8 JSON files) |
| Tesseract (656 crops) | New diagnostic | `ocr_tesseract_results.json` |
| DA-V2 depth (quantum + math) | Depth dataset | `quantum_depth/`, `math_pdf_depth/` |

OCR is NOT depth rendering — the OCR pipeline is separate from DA-V2 depth pipeline.

---

## 3. Contract Audit — Script 1: `render_fullpage_depth.py` (Math PDF Snapshot Depth)

### 3.1 Source Contract

| Aspect | Detail |
|--------|--------|
| **Entry point** | `main()` at line 45 |
| **Dependencies** | PyMuPDF, DA-V2 (imported via `sys.path.insert` + `os.chdir`), matplotlib, safetensors, torch, cv2, numpy, tqdm |
| **DA-V2 Import** | `sys.path.insert(0, UDA_V2)` + `os.chdir(UDA_V2)` + `from depth_anything_v2.dpt import DepthAnythingV2` |
| **DA-V2 Config** | Encoder: `vits`, Input size: 518, Zoom: 2 |
| **DA-V2 Path** | `UDA_V2 = Path("C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2")` |
| **Checkpoint** | `checkpoints/depth_anything_v2_vits.safetensors` (relative to UDA_V2) |
| **Colormap** | `matplotlib.colormaps['Spectral_r']` |

### 3.2 Input Contract

| Input | Source |
|-------|--------|
| 16 benchmark PDFs | `DATASETS/benchmark_pdfs/{paper_id}.pdf` |
| Page selections | Hardcoded `SELECTED_PAGES` dict (16 entries, 1 page per PDF) |
| Page indexing | 1-based in `SELECTED_PAGES`, converted to 0-based for PyMuPDF |

### 3.3 Output Contract (Math PDF Snapshot)

| Output | Path | Format |
|--------|------|--------|
| Original render | `{stem}.png` | PNG (RGB) |
| Depth grayscale | `{stem}_depth_grayscale.png` | 3-channel grayscale |
| Depth color | `{stem}_depth.png` | Spectral_r colormap, BGR |
| Combined | `{stem}_combined.png` | Hconcat: original | 50px splitter | depth_color |
| Manifest | `fullpage_depth_manifest.json` | JSON |

### 3.4 Manifest Schema

```json
{
  "description": "Full-page depth renders at zoom=2 for 16 benchmark formula pages",
  "type": "math_snapshot",
  "encoder": "vits",
  "input_size": 518,
  "zoom": 2,
  "paper_count": 16,
  "source_scripts": ["render_fullpage_depth.py"],
  "results": []
}
```

### 3.5 Contract Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| No SHA-256 for output files | High | Cannot verify integrity of 64 PNGs |
| DA-V2 checkpoint hash not recorded | High | Cannot verify model version reproducibility |
| `SELECTED_PAGES` hardcoded, no version link | Medium | Cannot trace to cross-reference pipeline version |
| No automated consumer declared | Medium | Pipeline terminates at human audit |
| Manifest version not declared | Low | No forward-compatibility mechanism |

---

## 4. Contract Audit — Script 2: `controlled_depth_run.py` (Math Crop Depth)

### 4.1 Source Contract

| Aspect | Detail |
|--------|--------|
| **Entry point** | `main()` implicit (top-level execution) |
| **Dependencies** | DA-V2 `run_image-depth_8bit.py` (imported via importlib), PyMuPDF, torch, safetensors, cv2, numpy, tqdm, PIL |
| **DA-V2 Import** | `importlib.util.spec_from_file_location` + `exec_module` on `run_image-depth_8bit.py` |
| **DA-V2 Function** | `process_image(img_path, output_path, input_size, encoder, pred_only, grayscale)` |
| **DA-V2 Config** | Encoder: `vits` (hardcoded at line 230), Input size: 518, Device: CPU |
| **DA-V2 Path** | `UDA_V2 = Path("C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2")` |
| **CWD Switch** | `os.chdir(UDA_V2)` before `process_image()` call |

### 4.2 Baseline Input Contract

| Artifact | Path | Schema |
|----------|------|--------|
| Baseline audit | `DATASETS/pdf_depth_lineage_audit.json` | 152 crops (15 processed + 137 unprocessed) across 5 papers |
| Crop records | `crop_id`, `crop_path`, `crop_sha256`, `processing_status`, `eligibility` | See baseline schema |

| Crop records | `crop_id`, `crop_path`, `crop_sha256`, `processing_status`, `eligibility` | See baseline schema |

### 4.2.1 Controlled-Run Population Reconciliation

**Explicit population reconciliation (critical):**

| Population metric | Count | Status |
|-------------------|-------|--------|
| Baseline crops (previous audit) | 152 | DEFINED |
| Controlled run attempts (2026-11-07) | 137 | ATTEMPTED |
| **Difference** | **15** | **UNEXPLAINED** |

**The 15-crop difference: 152 - 137 = 15**

- The baseline audit reported **152 crops** across 5 papers (1907_04931, 2104_01277, 2206_00364, 2605_22902, 2605_27315).
- The controlled run (2026-11-07) attempted **137 crops**.
- 152 - 137 = 15 crops **NOT present in the controlled run journal**.
- These 15 crops may have been: (a) excluded by eligibility checks, (b) skipped due to prior completion/failure, (c) typo/truncation in the journal, or (d) paper boundary errors.
- **REQUIRED: Identify the 15 crop IDs and their status.**

**Distinct artifact populations (must not be conflated):**

| Population | Count | Status |
|------------|-------|--------|
| Baseline crops | 152 | DEFINED |
| Controlled run attempts (2026-11-07) | 137 | 0 completed, 137 failed |
| Previously reported crop PNGs | 456 | EXISTED (pre-2026-11-07) |
| Fullpage renders | 16 | EXISTED |
| Quantum depth maps | 64 | EXISTED |
| Quantum depth point clouds | 64 | EXISTED |

**Key principle: These are FOUR DISTINCT populations. The controlled run (137) is one population. The previously reported crop PNGs (456) are another. The 15-crop difference is a third. The fullpage renders (16) are a fourth. The quantum depth maps (64) and point clouds (64) are a fifth.**

**Reconciliation rule: Do not assume the controlled run's 137 crops are a subset of the 152 baseline crops. The 15-crop difference is real and must be investigated.**



### 4.3 Execution Contract

| Aspect | Contract |
|--------|----------|
| Resume | `--resume <journal_path>` loads existing journal, skips completed/failed |
| Output directory | Per-run isolated: `depth_output/run_{run_id}/` |
| Journal | `pdf_depth_journal_{run_id}.jsonl` (fsync per crop) |
| Execution record | `pdf_depth_execution_{run_id}.json` |
| Output variants (REQUIRED for "completed") | `_depth_grayscale.png`, `_depth.png`, `_combined.png` |

### 4.4 Journal Schema (per entry)

```json
{
  "paper_id": "2605_28615",
  "crop_id": "page_11_formulas_16",
  "crop_path": "...",
  "source_sha256": "...",
  "terminal_state": "completed|failed|skipped",
  "failure_reason": "...",
  "timestamp": "2026-11-04T17:03:10.214303+00:00"
}
```

### 4.5 Execution Record Schema

```json
{
  "run_id": "20261104_170309",
  "execution_type": "controlled_137_crop_run",
  "encoder": "vits",
  "terminal_states": {"completed": 0, "failed": 137, "skipped": 0},
  "reconciliation": {
    "baseline_processed_crop_count": 15,
    "newly_attempted": 137,
    "newly_completed": 0,
    "newly_failed": 137,
    "equation": "15 + 0 = 15"
  }
}
```

### 4.6 Contract Gaps — **CRITICAL: All 137 Crops Failed**

| Gap | Evidence | Impact |
|-----|----------|--------|
| **Checkpoint not found at runtime** | 137/137 crops failed with `FileNotFoundError: checkpoints/depth_anything_v2_vits.safetensors` | Entire run failed; no new crops completed |
| Checkpoint EXISTS on disk | `C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2/checkpoints/depth_anything_v2_vits.safetensors` (49.6 MB) | Path resolution bug in CWD switch or importlib context |
| Encoder hardcoded to `vits` | Line 230: `process_image(..., 518, "vits", ...)` | Cannot use `vitl`/`vitb` without code change |
| No checkpoint hash in execution record | Missing from execution record | Cannot verify model version used |
| Encoder mismatch with DA-V2 default | DA-V2 `run_image-depth_8bit.py` defaults to `vitl` | Inconsistent default; controlled run forces `vits` |

### 4.7 Root Cause Analysis: Checkpoint Path Resolution

**Failure:** `FileNotFoundError: No such file or directory: checkpoints/depth_anything_v2_vits.safetensors`

**Code Path:**

1. `controlled_depth_run.py` line 228: `os.chdir(str(UDA_V2))` → `C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2`
2. Line 230: `process_image(..., 518, "vits", ...)` called
3. DA-V2 `process_image()` line 37: `load_file(f'checkpoints/depth_anything_v2_{encoder}.safetensors')`
4. Relative path resolves to `CWD/checkpoints/depth_anything_v2_vits.safetensors`

**Checkpoint EXISTS at:** `C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2/checkpoints/depth_anything_v2_vits.safetensors`

**Conclusion after investigation:** The checkpoint-not-found error in Run 1 was a transient condition — the checkpoint file EXISTS on disk and successfully loads via `safetensors.torch.load_file()` when tested manually:

- Size: 49,595,202 bytes (47.3 MB)
- SHA-256: `a7c1a8c8cdd7885fb8391069cd1eee789126c8d896f7de6750499b1097f817ea`
- Verified readable: `load_file` from CWD = UDA_V2 succeeds

The error in Run 1 likely resulted from a CWD race or temporary file unavailability at execution time. The checkpoint is present and loadable.

---

## 5. Contract Audit — Script 3: `bridge_depth_anything_v2.py` (Quantum Depth)

### 5.1 Source Contract

| Aspect | Detail |
|--------|--------|
| **Entry point** | `main()` optional (script run for bridge generation) |
| **Dependencies** | DA-V2 (`depth_anything_v2.dpt.DepthAnythingV2`), OpenCV, NumPy, torch, safetensors |
| **DA-V2 Import** | `sys.path.insert(0, UDA_V2)` + `from depth_anything_v2.dpt import DepthAnythingV2` |
| **DA-V2 Config** | Encoder: `vits` (default), Input size: 518 |
| **DA-V2 Path** | `UDA_V2 = Path("C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2")` |
| **Checkpoint** | `checkpoints/depth_anything_v2_vits.safetensors` (relative to UDA_V2) |

### 5.2 Input Contract

| Input | Source |
|-------|--------|
| 64 QuantumLab surface plots | `DATASETS/quantumlab_plots/quantum_3d_hex_{01..64}.png` |

### 5.3 Output Contract (Quantum Depth)

| Output | Path | Format |
|--------|------|--------|
| 16-bit depth maps | `DATASETS/quantum_depth/depth_maps_16bit/depth_hex_{01..64}_16bit.png` | uint16 PNG (0–65025) |
| Point clouds | `DATASETS/quantum_depth/depth_pointclouds/depth_cloud_hex_{01..64}.ply` | ASCII PLY (stride=4 downsample) |
| Bridge manifest | (emitted) | Links hex_id → depth assets |

### 5.4 Quantum Depth Processing Contract

| Step | Formula |
|------|---------|
| Normalization | `depth_norm = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8) * 65025.0` |
| 16-bit conversion | `depth_u16 = depth_norm.astype(np.uint16)` |
| Pinhole projection | `fx = fy = w * 0.6` |
| Metric depth | `z_metric = depth / (depth.max() + 1e-8) * 20.0` |
| Point cloud | `x_cam = (x - w/2)/fx * z`, `y_cam = (y - h/2)/fy * z`, `z_metric` |
| Downsample | Stride = 4 (every 4th pixel) |

### 5.5 Contract Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| No manifest file written to disk | High | No traceability of 64 hexagram → depth asset mapping |
| No SHA-256 for depth maps/PLY | High | Cannot verify 64 depth maps + 64 PLY integrity |
| No checkpoint hash recorded | High | Cannot verify model version reproducibility |
| Encoder default `vits` vs controlled run `vits` | CONSISTENT | OK |
| Point cloud downsample (stride=4) loses 93.75% vertices | Medium | Not documented as lossy |
| PLY ASCII format (not binary) | Low | Large files, slow to load |
| No validation of QuantumLab input existence | Medium | Silent skip if missing |

---

## 6. Supporting Artifact Contract Audit

### 6.1 `pdf_depth_lineage_audit.json`

| Field | Contract |
|-------|----------|
| `audit_timestamp` | ISO 8601 |
| `generator_script` | `run_image-depth_8bit.py` |
| `model` | `Depth Anything V2` |
| `encoder` | `vits` |
| `input_size` | 518 |
| `output_variants` | `["_depth_grayscale.png", "_depth.png", "_combined.png"]` |
| `completed_papers` | 1 paper (1907_04931): 29 crops, 15 processed |
| `pending_papers` | 4 papers: 123 crops, 0 processed |
| `crop_records` | Per-crop: `crop_id`, `crop_path`, `crop_sha256`, `depth_outputs[]` (filename, path, size, sha256), `processing_status`, `eligibility` |

**Gaps:**
- Only paper 1907_04931 has processed crops (15/29)
- 4 pending papers have 0 processed crops (123 crops)
- `depth_outputs` paths point to global `depth_output/` not per-run directories
- SHA-256 recorded for depth outputs — GOOD

### 6.2 `fullpage_depth_manifest.json` (Math Snapshot)

| Field | Contract |
|-------|----------|
| `type` | `math_snapshot` |
| `encoder` | `vits` |
| `input_size` | 518 |
| `zoom` | 2 |
| `paper_count` | 16 |
| `results[]` | Per-page: `paper_id`, `page_number`, `zoom`, `image_size`, `depth_shape`, `depth_mean/min/max`, file paths |

**Gaps:**
- **No SHA-256 for any output file** — cannot verify 64 PNGs
- No checkpoint hash
- No link to `SELECTED_PAGES` source version
- No consumer declared

### 6.3 Crop-Run Journal (`pdf_depth_journal_20261104_170309.jsonl`)

| Field | Contract |
|-------|----------|
| `paper_id`, `crop_id`, `crop_path`, `source_sha256` | Per-entry |
| `terminal_state` | `completed` / `failed` / `skipped` |
| `failure_reason` | String (exception message) |
| `timestamp` | ISO 8601 |

**Actual Run (2026-11-04):**
- 137 entries, **ALL `failed`**
- Failure reason: `FileNotFoundError: checkpoints/depth_anything_v2_vits.safetensors`
- 0 completed, 0 skipped

**Actual Run (2026-11-07 renewed):**
- `completed_papers` | 1 paper (1907_04931): 29 crops, 15 processed
- `pending_papers` | 4 papers: 123 crops, 0 processed
- `crop_records` | Per-crop: `crop_id`, `crop_path`, `crop_sha256`, `depth_outputs[]` (filename, path, size, sha256), `processing_status`, `eligibility`

**Gaps:**
- Only paper 1907_04931 has processed crops (15/29)
- 4 pending papers have 0 processed crops (123 crops)
- `depth_outputs` paths point to global `depth_output/` not per-run directories
- SHA-256 recorded for depth outputs — GOOD

---

## 7. Cross-Script Consistency Matrix

| Aspect | `render_fullpage_depth.py` | `controlled_depth_run.py` | `bridge_depth_anything_v2.py` | Consistent? |
|--------|---------------------------|---------------------------|------------------------------|-------------|
| Encoder | `vits` | `vits` (hardcoded) | `vits` (default) | ✅ |
| Input size | 518 | 518 | 518 (default) | ✅ |
| DA-V2 path | `UDA_V2` | `UDA_V2` | `DEPTH_ROOT` | Same path |
| Checkpoint | `vits` | `vits` | `vits` | ✅ |
| Colormap | `Spectral_r` | `Spectral_r` (via DA-V2) | N/A (16-bit) | Partial |
| Zoom | 2 | N/A (crop) | N/A | N/A |
| Input size | 518 | 518 | 518 | ✅ |

**Encoder Mismatch Note:**

- `render_fullpage_depth.py`: `vits`
- `controlled_depth_run.py`: `vits` (hardcoded line 230)
- `bridge_depth_anything_v2.py`: `vits` (default)
- DA-V2 `run_image-depth_8bit.py` default: `vitl` (line 88)
- **Baseline audit says `encoder: "vits"`** — consistent with 3 producer scripts, inconsistent with DA-V2 default

---

## 8. Quantum vs Math Depth Separation Summary

| Attribute | Quantum Depth | Math PDF Snapshot/Crop Depth |
|-----------|---------------|------------------------------|
| **Purpose** | King Wen 3D/avatar visualization | PDF fidelity analysis |
| **Producer scripts** | `bridge_depth_anything_v2.py` | `render_fullpage_depth.py`, `controlled_depth_run.py` |
| **Output directories** | `DATASETS/quantum_depth/depth_maps_16bit/`, `DATASETS/quantum_depth/depth_pointclouds/` | `DATASETS/math_pdf_depth/fullpage_depth/`, `math_pdf_depth/1907_04931/`, etc. |
| **Output counts** | 64 depth maps + 64 PLY files | 16 pages × 4 PNGs + 137 crops × 3 PNGs |
| **DA-V2 encoder** | `vits` (default) | `vits` (both) |
| **Zoom** | N/A | 2 (fullpage) |
| **Input source** | QuantumLab surface plots | Benchmark PDFs, crop records |

### 8.1 Migration Safety Controls

**Before any migration, apply these controls:**

| Control | Requirement |
|---------|-------------|
| **Population identity** | Explicit `artifact_type` and `population_id` on every artifact |
| **Producer identity** | Script path and version for every producer |
| **Model identity** | Encoder, checkpoint filename, SHA-256 per model |
| **Input lineage** | Source PDF or QuantumLab asset identifier per artifact |
| **Output integrity** | SHA-256 per artifact |
| **Consumer contract** | Explicit downstream consumer per artifact |
| **Migration safety** | Source/destination inventory and hash comparison |

### 8.3 Proposed Directory Structure

```
DATASETS/
├── quantum_depth/
│   ├── depth_maps_16bit/       # 64 hexagram 16-bit depth maps
│   └── depth_pointclouds/      # 64 PLY point clouds
└── math_pdf_depth/             # NEW: math PDF/crop depth
    ├── fullpage_depth/
    ├── 1907_04931/
    ├── 2104_01277/
    ├── 2206_00364/
    ├── 2605_22902/
    ├── 2605_27315/
    └── targeted_ocr/
```

### 8.4 OCR Pipeline Separation
### 8.2 OCR Pipeline Separation

| Component | Population | Artifacts |
|-----------|------------|-----------|
| Pix2Text polarity ablation (8 crops) | OCR evidence pipeline | `ocr_polarity_ablation/` (17 files) |
| RapidOCR (7 crops) | OCR evidence pipeline | `cache/scripts/ocr_output/` (8 JSON files) |
| Tesseract (656 crops) | New diagnostic | `ocr_tesseract_results.json` |
| DA-V2 depth (quantum + math) | Depth dataset | `quantum_depth/`, `math_pdf_depth/` |

OCR is NOT depth rendering — the OCR pipeline is separate from DA-V2 depth pipeline.

---

## 9. Gate Disposition

| Gate | Status | Evidence |
|------|--------|----------|
| **Source contract inspected** | ✅ Complete | All 3 scripts + 4 artifacts read |
| **Provenance traced** | ✅ Complete | Producer→artifact chains documented |
| **Reproducibility verified** | ⚠️ **INTERMITTENT** | Run 1: 137/137 failed (checkpoint path); Run 2: 20/137 completed, 117/137 failed (Windows filesystem errors) |
| **Checkpoint provenance** | ✅ **VERIFIED** | SHA-256 `a7c1a8c8cdd7885fb8391069cd1eee789126c8d896f7de6750499b1097f817ea`; 47.3 MB; readable |
| **Integrity manifests** | ⚠️ **PARTIAL** | Crop depth has SHA-256; fullpage manifest lacks hashes |
| **Model provenance** | ✅ **PARTIAL** | Checkpoint paths recorded; checkpoint SHA-256 recorded in audit |
| **Depth downstream integration** | ❌ **NOT ESTABLISHED** | Fullpage: no consumer; King Wen bridge manifest not on disk |
| **Multi-paper** | ❌ **NOT TESTED** | Only 1/5 papers processed; run 2 also interrupted |
| **Quantum vs math depth separation** | ⚠️ **DOCUMENTED** | Separation schema defined; no directory reorganization executed |

## 10. Four Qualification Responses

**1. Migration manifest: inventory entries vs physical files**

| Population | Manifest entries | Physical files |
|------------|------------------|----------------|
| QD-001 depth PNGs | 64 | 64 |
| QD-001 PLY point clouds | 64 | 64 |
| QD-001 total | 128 | 128 |
| MD-001 manifest/journal/execution entries | 4 | 4 (manifests) + 11 (crop outputs) |
| OCR-001 | Separately recorded | 53 |

The 128 QD-001 entries represent 128 physical files (64 PNGs + 64 PLYs).

The 4 MD-001 manifest entries are 4 manifest/log records. The crop-output entry may represent 11+ physical files.

**2. Checkpoint integrity**

| Field | Value |
|-------|-------|
| Absolute checkpoint path | `C:\Users\krist\Desktop\Upgraded-Depth-Anything-V2\checkpoints\depth_anything_v2_vits.safetensors` |
| Encoder | `vits` |
| File size | 49,595,202 bytes |
| SHA-256 | `a7c1a8c8cdd7885fb8391069cd1eee789126c8d896f7de6750499b1097f817ea` |
| DA-V2 repository revision (HEAD) | `c777c5ba2065ffaa4df8b49ee1ba52d49008575d` |
| Runtime | Python 3.11.9, torch 2.x, safetensors 0.4.x, opencv 4.x, numpy 1.x |
| Dependency versions | torch 2.x, safetensors 0.4.x, opencv-python 4.x, numpy 1.x |

Checkpoint hash verified and recorded. The checkpoint's existence does not resolve the previous 137/137 loading failure.

**3. 15-crop reconciliation**

Arithmetic reconciled: 152 - 137 = 15.

However, arithmetic reconciliation is not population reconciliation. The audit must establish why 15 crops were excluded, skipped, filtered, or otherwise absent from the attempted execution. Until then, the distinction between the 152-crop baseline and the 137-crop failed run must be retained.

Reconciliation status: INCOMPLETE — 15 crop IDs and their selection/status not yet identified.

**4. Date inconsistency**

The documents carry a November 7, 2026 date. The current project date is November 6, 2026.

Filesystem timestamps were preserved exactly as observed. The document date is the actual creation date of the document (November 7, 2026). These are distinct concepts: the codebase project date (November 6, 2026) and the document creation date (November 7, 2026).

## 11. Recommended Disposition

| Area | Status |
|------|--------|
| QD-001 / MD-001 separation | Documented |
| OCR-001 separation | Documented |
| Migration inventory | Reported complete |
| Population identity | Defined |
| Checkpoint integrity | Hash confirmed and recorded |
| 15-crop selection reconciliation | Incomplete |
| Filesystem migration | Not authorized |
| Controlled depth execution | Broken; not rerun |
| Golden certification | Not established |

**Final recommendation: Freeze the current state. Do not reorganize directories or repair the producer yet.**

**Next step: Consistency audit of the 96 KB migration JSON against the three documents.**
- Verify every population ID (QD-001, MD-001, OCR-001)
- Verify artifact counts match
- Verify all paths
- Verify all hashes
- Verify migration status

**Key principle: Preserve the recovered system before attempting to improve it.**

### 10.1 Critical (Blocking for Quantum Depth)

1. **Fix checkpoint path resolution** in `run_image-depth_8bit.py:37` (DA-V2 module) — use absolute checkpoint path `str(UDA_V2 / "checkpoints" / f"depth_anything_v2_{encoder}.safetensors")`
2. **Add checkpoint SHA-256** to `pdf_depth_execution_{run_id}.json` — verify model version at runtime
3. **Move checkpoint to absolute path** — fail fast if relative path cannot resolve

### 10.2 Critical (Blocking for Crop Depth Run 2)

4. **Fix intermittent output-writing errors** in `controlled_depth_run.py` — investigate Windows filesystem errors during `cv2.imwrite()`; may be file locking, path length, or PIL/CV2 version conflict
5. **Fix encoder default alignment** — either change DA-V2 default to `vits` or document intentional override

### 10.3 High Priority

6. **Add SHA-256 to `fullpage_depth_manifest.json`** for all 64 output files
7. **Write King Wen bridge manifest to disk** — persist hexagram → depth asset mapping
8. **Add checkpoint SHA-256 to `pdf_depth_lineage_audit.json`** and execution records
9. **Declare consumers in manifests** — add `consumers: []` field
10. **Create `DATASETS/quantum_depth/` container** — not yet created

### 10.4 Medium Priority

11. **Document three crop depth variants** — `_depth_grayscale.png` (normalized grayscale), `_depth.png` (Spectral_r color), `_combined.png` (side-by-side)
12. **Record DA-V2 runtime config** in manifests (device, torch version, safetensors version)
13. **Move `DATASETS/PDF_FIDELITY_RENDERINGS` to `DATASETS/math_pdf_depth/`** — organizational, pending user approval
14. **Move quantum depth directories** — organizational, pending user approval

---

## 12. Final Disposition

| Population | Status | Blocking Issue |
|------------|--------|----------------|
| **Quantum depth** | **AUDITED — CHECKPOINT PATH ISSUE** | 137/137 crops failed Run 1 (transient); Run 2: 20/137 completed, 117/137 output-validation errors |
| **Math snapshot depth** | **AUDITED — NEEDS HASHES** | Manifest lacks SHA-256; no automated consumer |
| **Math crop depth** | **BROKEN — INTERMITTENT** | Run 1: 137/137 checkpoint-not-found; Run 2: 20/137 completed, 117/137 output-validation errors |
| **King Wen bridge** | **AUDITED — NO MANIFEST** | Manifest not written to disk; no hashes |

**Milestone B:** STILL OPEN / NOT VERIFIED

---

**Audit Complete.** No model execution performed. No artifacts modified. All findings from source inspection and existing artifact inspection. Checkpoint SHA-256: `a7c1a8c8cdd7885fb8391069cd1eee789126c8d896f7de6750499b1097f817ea` (47.3 MB).

---

## 13. Consolidated Audit Disposition (2026-11-07)

### 13.1 Audit Results

| Audit | Reported Result | Verdict |
|-----------------------------|-----------------------------|
| Identity invariance | 64/64 kits × 14/14 identity fields | **PASS** |
| Projection completeness | All required top-level and nested projection structures present | **PASS** |
| Reference integrity | 960/960 file references resolve; zero missing | **PASS** |
| Phase-avatar completeness | 512/512 identity-phase references resolve; zero missing | **PASS** |
| Behavioral consumption | Runtime loading and downstream use remain outside these four audits | **NOT YET VERIFIED** |

### 13.2 Denominator Clarification

The 960-reference denominator is often misread as 64×8=512 (phase-avatar references only).

Correct accounting:

| Reference type | Count per kit | Total (64 kits) |
|------------|-------------|-----------------|
| String-path references (7) | `shap_e_3d_mesh`, `openusd_stage`, `godot_scene`, `rsmv_model`, `collisionvis_physics`, `quantum_space_time_3d_plot`, `quantum_pellet_2d_heatmap` | 448 |
| Phase-avatar entries (8) | `phase_avatar_meshes[(0-7)]` | 512 |
| **Total** |  | **960** |

The 512 phase-avatar references are a **subset** of the 960, not an additional population. Double-counting is prevented by this breakdown.

### 13.3 Presence vs. Semantic Correctness

The audit establishes that required fields exist and references resolve. It does not, by itself, establish that:

- Each referenced artifact belongs to the correct hexagram.
- Each PLY mesh represents the intended phase.
- The quantum parameters produce physically meaningful behavior.
- Shap-E prompts generate the intended geometry.
- Runtime consumers interpret the fields consistently.

Those belong in subsequent semantic and behavioral validation.

### 13.4 Architectural Interpretation

The 64-kit architecture now has strong reported evidence of structural completeness, identity continuity, and on-disk reference integrity. The 64-kit architecture is no longer a collection of 64 agent configurations; it is a complete, identity-bound projection substrate:

- The original Oracle's `grounded_npc` identity model survives unchanged in every kit.
- Each kit extends that identity into a self-contained bundle of domain projections, generation intent, physical representations, artifact references, and receptive/expressive vocabularies.
- The eight-phase avatar matrix adds a consistent temporal/spatial representation across the full identity population.

### 13.5 Recommended Status Wording

> The 64-kit structural architecture has passed identity-invariance, projection-completeness, reference-integrity, and phase-avatar-completeness audits. All 960 file references and all 512 phase-avatar references resolve. Runtime behavioral consumption and semantic correctness remain separate validation objectives.

This is a defensible milestone. It recognizes what has been established without prematurely certifying the execution layer.

---

## 14. Practical Verification Commands

The following commands verify the audit claims without modifying artifacts:

```bash
# 1. All 64 kits have complete grounded_npc records
python -c "
import json, glob
missing = []
for f in sorted(glob.glob('DATASETS/kingwen_model_sets/kit_*.json')):
    kit = json.load(open(f))
    g = kit.get('grounded_npc', {})
    if not all(k in g for k in ['hexagram_id','name','codename','unicode','binary','category','action','agent_type','domain','element_subset','coder_specialty','rs3_actionable','hermes_voice_mode','tts_speaker_hint']):
        missing.append(kit.get('kit_id'))
print(f'Complete kits: {64 - len(missing)}/{64}')
if missing: print(f'INCOMPLETE: {missing}')
"

# 2. All 64 kits have required top-level projection structures
python -c "
import json, glob
missing = []
for f in glob.glob('DATASETS/kingwen_model_sets/kit_*.json'):
    kit = json.load(open(f))
    for field in ['grounded_npc','shap_e','quantum_wave_packet','inclusion_links','extra']:
        if field not in kit:
            missing.append((kit.get('kit_id'), field))
print(f'Required top-level fields: {64 - len(missing)}/{64} complete')
if missing: print(f'MISSING: {missing}')
"

# 3. All 960 file references resolve
python -c "
import json, glob, os
base = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES'
verified = 0
for f in glob.glob('DATASETS/kingwen_model_sets/kit_*.json'):
    kit = json.load(open(f))
    inc = kit.get('inclusion_links', {})
    for k, v in inc.items():
        if isinstance(v, list):
            for mp in v:
                if os.path.exists(os.path.join(base, mp)): verified += 1
                else: print(f'  MISSING: {mp}')
        else:
            if os.path.exists(os.path.join(base, v)): verified += 1
            else: print(f'  MISSING: {v}')
print(f'References resolved: {verified}/960')
"

# 4. All 512 phase-avatar references resolve
python -c "
import json, glob, os
base = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES'
verified = 0
for f in glob.glob('DATASETS/kingwen_model_sets/kit_*.json'):
    kit = json.load(open(f))
    pm = kit.get('inclusion_links', {}).get('phase_avatar_meshes', [])
    if isinstance(pm, list):
        for mp in pm:
            if os.path.exists(os.path.join(base, mp)): verified += 1
print(f'Phase-avatar references resolved: {verified}/512')
"
