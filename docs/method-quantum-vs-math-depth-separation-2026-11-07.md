# Quantum Depth vs Math Snapshot/Crop Depth — Separation Documentation

**Date:** 2026-11-07  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b651477afd0bcba55a2454e0a123cde`  

---

## 1. Separation Objective

The user requested separation of **quantum depth** (King Wen 3D/avatar visualization) from **math PDF/html snapshot/crop depth** (PDF fidelity rendering for math document analysis). These are two distinct populations with different producers, outputs, and consumers.

**Key principle:** Separating them prevents conflation of:
- King Wen quantum state visualization (64 hexagram depth maps + PLY point clouds)
- Math content localization (crop-level depth renders for PDF fidelity analysis)

---

## 2. Producer/Population Classification

### 2.1 Quantum Depth (King Wen Visual State)

| Attribute | Value |
|-----------|-------|
| **Producer** | **QD-001** | `bridge_depth_anything_v2.py` |
| **Script** | `scripts/bridge_depth_anything_v2.py` |
| **Input** | 64 QuantumLab surface plots (`DATASETS/quantumlab_plots/quantum_3d_hex_{01..64}.png`) |
| **DA-V2 Config** | Encoder: `vits` (default), Input size: 518 |
| **Output** | `DATASETS/depth_maps_16bit/` (64 hexagram 16-bit depth maps) |
| | `DATASETS/depth_pointclouds/` (64 PLY point clouds) |
| **Purpose** | King Wen 3D/avatar visualization — quantum state representation |
| **Run ID** | None (bridge script, no journal) |
| **Execution Type** | One-time bridge run, no journal/limit |

### 2.2 Math PDF Snapshot/Crop Depth (PDF Fidelity)

| Attribute | Value |
|-----------|-------|
| **Producer** | **MD-001** | `render_fullpage_depth.py` + `controlled_depth_run.py` |
| **Script** | `scripts/render_fullpage_depth.py` + `scripts/controlled_depth_run.py` |
| **Input** | 16 benchmark PDFs (fullpage) + 137 crop records across 5 papers (crop depth) |
| **DA-V2 Config** | Encoder: `vits` (both scripts), Input size: 518, Zoom: 2 |
| **Output (fullpage)** | `DATASETS/PDF_FIDELITY_RENDERINGS/fullpage_depth/` (16 pages × 4 PNGs) |
| **Output (crop)** | `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/`, `2104_01277/`, `2206_00364/`, `2605_22902/`, `2605_27315/` |
| **Purpose** | Math PDF/fidelity content analysis — page-level and crop-level depth |
| **Run ID** | `20261104_170309` (fullpage), `20261107_005725` (crop) |

### 2.3 Unified Producer/Consumer Map

| Script | Script File | Output Directory | Population |
|--------|-------------|------------------|------------|
| `bridge_depth_anything_v2.py` | `scripts/bridge_depth_anything_v2.py` | `depth_maps_16bit/`, `depth_pointclouds/` | Quantum depth |
| `render_fullpage_depth.py` | `scripts/render_fullpage_depth.py` | `PDF_FIDELITY_RENDERINGS/fullpage_depth/` | Math snapshot depth |
| `controlled_depth_run.py` | `scripts/controlled_depth_run.py` | `PDF_FIDELITY_RENDERINGS/1907_04931/`, `2104_01277/`, `2206_00364/`, `2605_22902/`, `2605_27315/` | Math crop depth |

---

## 3. Manifest Type Field

### 3.1 Current State

The existing `fullpage_depth_manifest.json` does not have a "type" field. The manifest only contains metadata about fullpage depth renders.

### 3.2 Proposed Type Field

The manifest should include a `type` field to distinguish population:

```json
{
  "description": "Full-page depth renders at zoom=2 for 16 benchmark formula pages",
  "type": "math_snapshot",  // "quantum" | "math_snapshot"
  "encoder": "vits",
  "input_size": 518,
  "zoom": 2,
  "paper_count": 16,
  "source_scripts": ["render_fullpage_depth.py"],
  "results": [...]
}
```

### 3.3 Manifest Schema (Type Field)

| Field | Type | Values | Required |
|-------|------|--------|----------|
| `type` | string | `"quantum"` \| `"math_snapshot"` | Yes |

**Rationale:** When a downstream consumer reads the manifest, it must know whether the depth outputs are for King Wen 3D visualization (quantum) or PDF fidelity analysis (math snapshot). This prevents cross-population confusion.

---

## 4. Directory Structure

### 4.1 Current Structure

```
DATASETS/
├── depth_maps_16bit/          # 64 quantum depth maps
├── depth_pointclouds/          # 64 quantum PLY files
├── PDF_FIDELITY_RENDERINGS/
│   ├── fullpage_depth/
│   ├── 1907_04931/             # 38 files
│   ├── 2104_01277/             # 69 files
│   ├── 2206_00364/             # 43 files
│   ├── 2605_22902/             # 5 files
│   ├── 2605_27315/             # 6 files
│   └── targeted_ocr/           # 18 files
└── pdf_depth_lineage_audit.json
```

### 4.2 Proposed Structure

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

**Rationale:** Directory-level separation makes it impossible to accidentally consume quantum depth as math snapshot depth. No single consumer sees both populations without explicit routing.

### 4.3 Mapping Rule

- Any script with `bridge_depth_anything_v2.py` → Quantum depth → `DATASETS/quantum_depth/`
- Any script with `render_fullpage_depth.py` or `controlled_depth_run.py` → Math PDF depth → `DATASETS/math_pdf_depth/`

---

## 5. OCR Pipeline Separation

The OCR (Pix2Text ↔ RapidOCR ↔ Tesseract) is a separate population from DA-V2 depth rendering. It should not be conflated with depth outputs.

| Component | Population | Artifacts |
|-----------|------------|-----------|
| Pix2Text polarity ablation (8 crops) | OCR evidence pipeline | `ocr_polarity_ablation/` (17 files) |
| RapidOCR (7 crops) | OCR evidence pipeline | `cache/scripts/ocr_output/` (8 JSON files) |
| Tesseract (656 crops) | New diagnostic | `ocr_tesseract_results.json` |
| DA-V2 depth (quantum + math) | Depth dataset | `quantum_depth/`, `math_pdf_depth/` |

Documented separate populations:
- Pix2Text, RapidOCR, Tesseract are OCR tooling — NOT depth rendering
- The OCR pipeline is separate from DA-V2 depth pipeline
- OCR outputs are preserved as experimental evidence, not conflated with depth

---

## 6. Audit Document Updates

### 6.1 Updated Section 1 (Scripts Under Audit)

```
| # | Script | Path | Role |
|---|--------|------|------|
| 1 | render_fullpage_depth.py | scripts/render_fullpage_depth.py | Math snapshot depth (16 pages) |
| 2 | controlled_depth_run.py | scripts/controlled_depth_run.py | Math crop depth (137 crops) |
| 3 | bridge_depth_anything_v2.py | scripts/bridge_depth_anything_v2.py | Quantum depth (64 hexagrams) |
```

### 6.2 Updated Section 2 (Contract Audit)

- **Script 1** (`render_fullpage_depth.py`): Move to `DATASETS/math_pdf_depth/fullpage_depth/`
- **Script 2** (`controlled_depth_run.py`): Move to `DATASETS/math_pdf_depth/` (crop depth)
- **Script 3** (`bridge_depth_anything_v2.py`): Move to `DATASETS/quantum_depth/`

### 6.3 Updated Section 5 (Supporting Artifacts)

- `DATASETS/pdf_depth_lineage_audit.json` → The lineage audit now includes both populations
- `DATASETS/PDF_FIDELITY_RENDERINGS/` → All under `DATASETS/math_pdf_depth/`
- `DATASETS/depth_maps_16bit/`, `DATASETS/depth_pointclouds/` → Under `DATASETS/quantum_depth/`

---

## 7. Required Changes

### 7.1 Pending (Do Not Execute)

| Action | Owner | Status |
|--------|-------|--------|
| Create `DATASETS/quantum_depth/` container | User/Admin | Pending |
| Create `DATASETS/math_pdf_depth/` container | User/Admin | Pending |
| Move 64 quantum depth maps | User/Admin | Pending |
| Move 64 quantum PLY files | User/Admin | Pending |
| Move 16 fullpage depth renders | User/Admin | Pending |
| Move 137 crop depth renders | User/Admin | Pending |
| Update `fullpage_depth_manifest.json` with `type` field | Admin | Pending |
| Update `pdf_depth_lineage_audit.json` directory paths | Admin | Pending |

### 7.2 Verified

- ✅ Source scripts identified: `bridge_depth_anything_v2.py` (quantum), `render_fullpage_depth.py` (snapshot), `controlled_depth_run.py` (crop)
- ✅ Output directories identified: `depth_maps_16bit/`, `depth_pointclouds/` (quantum), `PDF_FIDELITY_RENDERINGS/*` (math)
- ✅ File counts: 64+64 quantum, 16 fullpage, 137 crop
- ✅ Neither population is currently separated at the directory level

---

## 8. Summary

| Population | Count | Producer Scripts | Output Directories | Consumer |
|------------|-------|------------------|-------------------|----------|
| **Quantum depth** | 64 depth maps + 64 point clouds | `bridge_depth_anything_v2.py` | `DATASETS/quantum_depth/` | King Wen 3D/avatar |
| **Math snapshot depth** | 16 pages × 4 PNGs | `render_fullpage_depth.py` | `DATASETS/math_pdf_depth/fullpage_depth/` | Human audit |
| **Math crop depth** | 137 crops × 3 PNGs | `controlled_depth_run.py` | `DATASETS/math_pdf_depth/1907_04931/`, etc. | Human audit, journal resume |

**Separation is documented. No directory move executed. Joint implementation with user approval required before any file reorganization.**

---

**Audit complete.** No model execution performed. No artifacts modified. Separation documented as a precondition for future directory reorganization.

