# Fullpage Depth & Crop Depth — Producer/Consumer Trace

**Date:** 2026-11-07  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b651477afd0bcba55a2454e0a123cde`

---

## 1. Depth Map Producers

### Producer 1: Fullpage Depth Renders (`render_fullpage_depth.py`)

| Aspect | Detail |
|--------|--------|
| **Script** | `scripts/render_fullpage_depth.py` |
| **Input** | 16 benchmark PDFs + page selections from cross-reference pipeline |
| **Dependencies** | PyMuPDF, DA-V2 (`depth_anything_v2.dpt.DepthAnythingV2`), matplotlib, safetensors, torch |
| **DA-V2 Config** | Encoder: `vits`, Input size: 518, Zoom: 2 |
| **DA-V2 Path** | `C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2` (sys.path injection + os.chdir) |
| **Output Directory** | `DATASETS/PDF_FIDELITY_RENDERINGS/fullpage_depth/` |
| **Outputs per Page** | 1. `{paper_id}_p{page}_fullpage_z2.png` (original render) |
| | 2. `{stem}_depth_grayscale.png` (normalized depth × 255, grayscale) |
| | 3. `{stem}_depth.png` (Spectral_r colormap, BGR for OpenCV) |
| | 4. `{stem}_combined.png` (original | 50px splitter | depth_color) |
| **Manifest** | `fullpage_depth_manifest.json` (16 entries, depth statistics, file paths) |
| **SHA-256** | Not recorded in manifest (only depth stats) |

**Selected Pages (from cross-reference pipeline):**
```python
SELECTED_PAGES = {
    "0806.2366": 3, "1212.0957": 8, "2009.00031": 5, "2102.03334": 6,
    "2605.00155": 27, "2605.00224": 1, "2605.06070": 12, "2605.18130": 4,
    "2605.22715": 19, "2605.23244": 4, "2605.24807": 9, "2605.24856": 17,
    "2605.25036": 3, "2605.25334": 6, "2605.28615": 15, "2605.28896": 16,
}
```

---

### Producer 2: Crop Depth Renders (`controlled_depth_run.py` → DA-V2 `run_image-depth_8bit.py`)

| Aspect | Detail |
|--------|--------|
| **Orchestrator** | `scripts/controlled_depth_run.py` |
| **DA-V2 Module** | `Upgraded-Depth-Anything-V2/run_image-depth_8bit.py` (imported via importlib) |
| **DA-V2 Function** | `process_image(img_path, output_path, input_size, encoder, pred_only, grayscale)` |
| **DA-V2 Config** | Encoder: `vitl` (default), Input size: 518, Device: CPU (no CUDA on this host) |
| **Input** | 152 baseline crops from `pdf_depth_lineage_audit.json` (15 original + 137 unprocessed) |
| **Output (Global)** | `C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2/depth_output/` (shared) |
| **Output (Per-Run)** | `C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2/depth_output/run_{run_id}/` (isolated) |
| **Local Copy** | `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/depth_output/` (for paper 1907_04931) |
| **Journal** | `DATASETS/pdf_depth_runs/pdf_depth_journal_{run_id}.jsonl` (fsync per crop) |
| **Execution Record** | `DATASETS/pdf_depth_runs/pdf_depth_execution_{run_id}.json` |

**Outputs per Crop (3 variants required for "completed"):**
1. `{crop}_depth_grayscale.png` — normalized depth × 255, 3-channel grayscale
2. `{crop}_depth.png` — Spectral_r colormap (color depth map)
3. `{crop}_combined.png` — original | 50px white splitter | depth_color

**Validation (all 3 must exist for "completed"):**
```python
EXPECTED_VARIANTS = ["_depth_grayscale.png", "_depth.png", "_combined.png"]
```

**Accounting (152 baseline crops):**
- 15 original completed (paper 1907_04931) — hashes verified BEFORE and AFTER
- 137 unprocessed eligible crops
- Per-run isolated output directory (`run_{run_id}/`)
- Journal fsync per crop; final JSON via temp-file + os.replace()

---

### Producer 3: King Wen × DA-V2 Bridge (`bridge_depth_anything_v2.py`)

| Aspect | Detail |
|--------|--------|
| **Script** | `scripts/bridge_depth_anything_v2.py` |
| **Input** | 64 QuantumLab surface plot PNGs (`DATASETS/quantumlab_plots/quantum_3d_hex_{01..64}.png`) |
| **DA-V2 Config** | Encoder: `vits` (default), Input size: 518, 16-bit output |
| **Output (16-bit Depth)** | `DATASETS/depth_maps_16bit/depth_hex_{01..64}_16bit.png` (uint16, 0–65025) |
| **Output (Point Cloud)** | `DATASETS/depth_pointclouds/depth_cloud_hex_{01..64}.ply` (ASCII, stride=4 downsample) |
| **Projection** | Pinhole camera model: fx=fy=w*0.6, z_metric = depth × 20.0m |
| **Manifest** | Emitted linking hexagram ID → depth assets |

**King Wen Integration:**
- Input plots: `DATASETS/quantumlab_plots/quantum_3d_hex_{01..64}.png` (from `generate_sovereign_world.py`)
- Output depth maps consumed by King Wen avatar/3D visualization
- PLY point clouds for 3D rendering pipeline

---

### Producer 4: Crop Depth (Polarity Ablation) — Separate Pipeline

| Script | `scripts/ocr_polarity_ablation.py` |
|--------|-----------------------------------|
| **Input** | 8 crops from `1907_04931` (crop_00 through crop_06, plus crop__) |
| **Engine** | Pix2Text (`pix2text-mfd-1.5-onnx` v1.1.7) — **NOT DA-V2** |
| **Purpose** | OCR polarity ablation (Pix2Text LaTeX on original vs inverted) |
| **Depth Artifacts** | `DATASETS/ocr_polarity_ablation/crop_*_4x_depth.png` (from DA-V2 run, not Pix2Text) |
| **Note** | Depth maps here are DA-V2 outputs on the same crops, not Pix2Text outputs |

---

## 2. Depth Map Consumers

### Consumer 1: Fullpage Depth Manifest (Human/Visual Inspection)

| Consumer | `fullpage_depth_manifest.json` |
|----------|-------------------------------|
| **Type** | Human-readable audit artifact |
| **Consumes** | 16 fullpage depth renders + manifest |
| **Purpose** | Visual verification of depth quality on formula pages |
| **No Automated Consumer** | No script reads this manifest as input |

---

### Consumer 2: Crop Depth Outputs (DA-V2 Pipeline)

| Consumer | `controlled_depth_run.py` (journal + execution record) |
|----------|--------------------------------------------------------|
| **Reads** | Global `depth_output/` + per-run `run_{run_id}/` |
| **Validates** | 3 variants per crop (`_depth_grayscale.png`, `_depth.png`, `_combined.png`) |
| **Accounts** | 152 baseline crops → 15 original + 137 new |

| Consumer | `bridge_depth_anything_v2.py` (King Wen) |
|----------|------------------------------------------|
| **Reads** | 64 QuantumLab PNGs |
| **Produces** | 16-bit depth maps + PLY point clouds for 64 hexagrams |
| **Consumes By** | King Wen 3D avatar / visualization pipeline |

---

### Consumer 3: King Wen × DA-V2 Bridge (Hexagram Depth Maps)

| Consumer | King Wen 3D / Avatar / Visualization |
|----------|--------------------------------------|
| **Input** | `DATASETS/depth_maps_16bit/depth_hex_{01..64}_16bit.png` |
| **Input** | `DATASETS/depth_pointclouds/depth_cloud_hex_{01..64}.ply` |
| **Purpose** | Depth-displacement for hexagram 3D visualization / avatar meshes |
| **Link** | Manifest emitted by `bridge_depth_anything_v2.py` links hex_id → depth assets |

---

### Consumer 4: Crop Depth in Polarity Ablation (Separate)

| Consumer | `ocr_polarity_ablation_report.json` |
|----------|-------------------------------------|
| **Input** | `crop_*_4x_depth.png` (DA-V2 depth on polarity ablation crops) |
| **Purpose** | Visual correlation: depth map vs OCR LaTeX output |
| **Note** | These are DA-V2 depth maps on the SAME crops as Pix2Text polarity test |

---

## 3. Producer → Consumer Traceability Matrix

| Artifact | Producer Script | Consumer(s) | Traceability |
|----------|----------------|-------------|--------------|
| `fullpage_depth_manifest.json` + 4 PNGs/page | `render_fullpage_depth.py` | Human audit only | Manifest has SHA-256? **No** (only stats) |
| `fullpage_depth/` 4 PNGs × 16 pages | `render_fullpage_depth.py` | None (audit only) | No automated consumer |
| `controlled_depth_run.py` journal | `controlled_depth_run.py` | Self (resume), audit | Journal fsync per crop |
| `run_{run_id}/` 3 PNGs/crop | `controlled_depth_run.py` → DA-V2 `process_image()` | Self (validation), audit | 3-variant check |
| `depth_output/` (global) | DA-V2 `process_image()` | `controlled_depth_run.py` (validation), audit | Duplicate of per-run |
| `depth_maps_16bit/depth_hex_{01..64}_16bit.png` | `bridge_depth_anything_v2.py` | King Wen 3D / avatar | Bridge manifest |
| `depth_pointclouds/depth_cloud_hex_{01..64}.ply` | `bridge_depth_anything_v2.py` | King Wen 3D rendering | Bridge manifest |
| `depth_output/crop_*_depth*.png` (1907_04931) | `controlled_depth_run.py` | Local copy for paper | Duplicate of global |

---

## 4. Critical Traceability Gaps

| Gap | Impact |
|-----|--------|
| **No SHA-256 in fullpage manifest** | Cannot verify integrity of 64 fullpage PNGs |
| **No SHA-256 in crop depth journal** | Cannot verify crop depth outputs against baseline |
| **Global + local depth_output duplication** | Confusion about canonical location |
| **No consumer for fullpage depth** | 16 pages rendered but no automated downstream use |
| **DA-V2 model version not pinned in manifests** | `vits`/`vitl` encoder + checkpoint path only |
| **King Wen bridge manifest not tracked** | 64 hexagram depth assets not in git/manifest |

---

## 5. Recommended Traceability Improvements

1. **Add SHA-256 to all manifests** — every output file in `fullpage_depth_manifest.json` and crop depth journal
2. **Unify depth_output location** — choose one canonical path; symlink or copy for local access
3. **Record DA-V2 model hash** — checkpoint SHA-256 in every manifest
4. **Declare consumers explicitly** — add `consumers: []` field to each manifest
5. **Link fullpage depth to cross-reference pipeline** — record which `SELECTED_PAGES` version was used
6. **Record King Wen bridge manifest in git** — track 64 hexagram depth assets

---

## 6. Summary: Producer → Consumer Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  SOURCE DATA                                                         │
├─────────────────────────────────────────────────────────────────────┤
│  16 benchmark PDFs (selected pages)  ──▶ render_fullpage_depth.py  │
│  152 baseline crops (pdf_depth_lineage) ──▶ controlled_depth_run.py │
│  64 QuantumLab PNGs ──▶ bridge_depth_anything_v2.py                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PRODUCERS (DA-V2 INFERENCE)                                         │
├─────────────────────────────────────────────────────────────────────┤
│  render_fullpage_depth.py ──▶ 16 fullpage depth renders (4×16)     │
│  controlled_depth_run.py ──▶ 152 crop depth renders (3×152)        │
│  bridge_depth_anything_v2.py ──▶ 64 depth maps + 64 PLY clouds      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OUTPUTS & MANIFESTS                                                 │
├─────────────────────────────────────────────────────────────────────┤
│  fullpage_depth/ + fullpage_depth_manifest.json (16 pages)         │
│  depth_output/ (global) + run_{run_id}/ (isolated) + journal       │
│  depth_maps_16bit/ + depth_pointclouds/ + bridge manifest          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CONSUMERS                                                           │
├─────────────────────────────────────────────────────────────────────┤
│  Human audit: fullpage_depth_manifest.json, execution records      │
│  Self-validation: controlled_depth_run.py (3-variant check)        │
│  King Wen 3D/avatar: depth_maps_16bit/, depth_pointclouds/         │
│  No automated consumer for fullpage_depth (audit only)             │
└─────────────────────────────────────────────────────────────────────┘
```

---

**End of trace.**

---

*Document generated 2026-11-07. All scripts and paths verified against `v2-remediation` HEAD `3bb937209b`.*