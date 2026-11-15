# V2.3 Legacy Tool Integration Matrix & Multi-Stage Evidence Specification

**Document Path:** `docs/v2_3_legacy_tool_integration_matrix.md`  
**Companion Machine-Readable Artifact:** [`DATASETS/structural_preservation/v2_3_evidence_channel_registry.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/v2_3_evidence_channel_registry.json) (`f34424b2...`)  
**Governing Standard:** Ratified Reconstructed Operating Contract (Reuse Before Replacement; No Fabrication; Evidence Independence)

---

## 1. Architectural Vision: Multi-Stage Evidence Pipeline

Rather than treating the recovery pipeline as a monolithic OCR transcription sequence, the standalone V2.3 mathematical recovery architecture is organized into **six discrete evidence layers**. Downstream stages must never manufacture evidence that should have been independently observed upstream.

```
       +-----------------------------------------------------------+
  L0   | Source Acquisition (PDF streams, font dicts, vectors, HTML)|
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
  L1   | Physical Candidate Discovery (Unconditioned proposals)    |
       |  - targeted_math_detector.py   - G0 unconstrained detector |
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
  L2   | Visual Evidence Acquisition (Adaptive crops, overlays)   |
       |  - vision_comparison_pipeline  - cross_reference_pipeline  |
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
  L3   | Independent Physical Cross-Verification (Multi-substrate)  |
       |  - chroma_visual_reader        - physical_symbol_matcher   |
       |  - audit_rendered_png_producers - experiments_crop_isolation|
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
  L4   | Structural Reconstruction (Spatial grammar, typed AST)     |
       |  - spatial_grammar_engine      - mathml_parser.py          |
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
  L5   | Evidence Adjudication & Gate D4 (Clearance & Abstention)  |
       |  - glyph_evidence_adjudicator  - Gate D4 clearance check   |
       |  - explicit abstention on UNRESOLVED_CONFLICT             |
       +-----------------------------------------------------------+
```

---

## 2. Ranked Legacy Tool Reuse & Compatibility Matrix

| Rank | Tool / Script | Assigned Layer | Recommended Role | Integration Disposition | Independent Evidence Provided | Correlated Failure Modes / Hazards | Validating Test Suite |
| :---: | :--- | :---: | :--- | :---: | :--- | :--- | :--- |
| **1** | `targeted_math_detector.py` | **L1** | Observation-only physical candidate proposal | **ADAPTER EXECUTED** (`scripts/targeted_math_detector_adapter.py`) | Unconditioned detection of math punctuation, aspect ratios, and font anomalies without keyword priors | Shares PyMuPDF text layer; label termination heuristic prevents prose bleeding | `tests/test_targeted_math_detector_adapter.py` (3 passed) |
| **2** | `chroma_visual_reader.py` | **L3** | 2D physical geometry extraction (vinculums, braces, cases) | **ADAPTER EXECUTED** (`scripts/chroma_geometry_adapter.py`) | K-means color clustering + 2D connected components extract division bars and braces without OCR | Raster thresholding can merge touching strokes; thin bar threshold relaxed | `tests/test_chroma_geometry_adapter.py` (2 passed) |
| **3** | `targeted_depth_ocr.py` | **L1 / L2** | High-zoom ($8\times$) detection of tall/wide structures | **ADAPTER REQUIRED** | Connected-component projection profiling isolates stretched delimiters | Assumes fixed $4\times$ detection scale; hardcoded Windows paths | `test_crop_isolation_regression.py` |
| **4** | `vision_comparison_pipeline.py` | **L2** | Adaptive cropping and content-ratio validation | **ADAPTER EXECUTED** (`scripts/safe_adaptive_cropping_adapter.py`) | Pure image-level crop extraction with RGB colorspace, neighbor-aware padding, and blank rejection | Requires prior bounding box; cannot propose candidates independently | `tests/test_safe_adaptive_cropping_adapter.py` (2 passed) |
| **5** | `cross_reference_pipeline.py` | **L2 / L5** | Full-page visual targeting overlays & annotation | **DIRECT REUSE** | PyMuPDF vector overlay drawing (`page.draw_rect`) color-coding 6 region categories | Requires prior region proposals and text boundaries | `test_structural_evidence_graph.py` (21 passed) |
| **6** | `pix2text_harvest.py` | **L3** | Independent OCR candidate channel | **DIRECT REUSE (Provenance Bound)** | Visual neural recognition from cropped raster patches | Susceptible to font hallucinations; shares crop boundary defects | `test_pix2text_harvest.py` |
| **7** | `audit_rendered_png_producers.py` | **L3 / L5** | Crop boundary verification & 1px/2px ink contact audit | **INTEGRATED** (`scripts/chroma_geometry_adapter.py`) | Exact pixel perimeter touch check: guarantees crops do not clip symbol ink | Measures pixels, not PDF points; scale factor `min_margin_px / zoom` used for Gate D4 | `tests/test_chroma_geometry_adapter.py` |
| **8** | `adjudicate_targets.py` / `adjudicate_candidates_v2.py` | **L5** | Multi-layer candidate classification | **DEFECT RESOLVED** (`scripts/adjudicate_candidates_v2.py`) | Association tracking between visual candidates and parser IDs | Defect in `_text_match()` (empty token sets matching) surgically resolved | `tests/test_adjudicate_candidates_v2.py` (2 passed) |
| **9** | `experiments_crop_isolation.py` | **L2 / L3** | Crop padding calibration ($15\text{ pt}$ vs. $2\text{ pt}$) & prose filter | **EXPERIMENTAL / HARNESS** | Mathematical whitelist filter (`sin, cos, lim, log, det, var, cov`) rejects prose | Preselected candidate boxes; not a discovery tool | `test_crop_isolation_regression.py` (16 passed) |
| **10**| `render_fullpage_depth.py` | **L2** | 2.5D visual depth estimation via Depth Anything V2 | **OPTIONAL DIAGNOSTIC** | Monocular depth maps providing visual layer separation | Depth does not establish symbolic identity or syntax | Depth manifest inspection |

---

## 3. Evidence Independence vs. Correlated Substrates

A critical failure mode identified in historical runs is the **illusion of independent confirmation**—counting two tools as separate evidence when they share the same underlying substrate.

| Evidence Channels | What They Actually Share | Genuine Independence Status | Correct Pipeline Treatment |
| :--- | :--- | :---: | :--- |
| **PyMuPDF text extraction vs. rawdict extraction** | Identical PDF `/Contents` and font stream parsing engine | **CORRELATED** (Single Substrate) | Treat as single text/font evidence channel (`L0`) |
| **Two OCR engines on the same crop** | Identical crop boundary, resolution, and raster degradation | **PARTIALLY CORRELATED** | Track shared crop dependency; do not count as independent localization |
| **Chroma geometry vs. OpenCV connected components** | Same raster pixmap and thresholding | **PARTIALLY CORRELATED** | Check for shared binarization artifacts before fusing |
| **Font metadata vs. Physical Raster Matching** | Different substrates (TrueType/Type1 tables vs. visual ink) | **GENUINELY INDEPENDENT** | Fuse in `L3`; trigger `UNRESOLVED_CONFLICT` on mismatch |
| **HTML/MathML source vs. PDF Physical Recovery** | Completely different generation pathways | **GENUINELY INDEPENDENT REFERENCE** | Source establishes semantic target; PDF establishes physical reality |
| **AST generated from OCR vs. the OCR string** | AST is a direct derivative of the OCR string | **NOT INDEPENDENT** | AST validates syntactic well-formedness, NOT character correctness |

---

## 4. Standardized Evidence Provenance Sidecar Schema

To eliminate unstructured string passing, every intermediate producer emits a standardized record:

```json
{
  "evidence_id": "OBS-PIAA-004-CHROMA-001",
  "producer": "scripts/chroma_visual_reader.py:ChromaVisualReader.detect_math_structures",
  "producer_version": "git:9015929c38",
  "layer": "L3_independent_physical_cross_verification",
  "input_sha256": "e7ac011ddbe6ac53e2593cdf1d0ffdd92333bfc6ca646c0e7c82d11282f3444a",
  "page_id": {
    "page_0based": 4,
    "page_1based": 5
  },
  "bbox_pdf_pt": [90.73, 247.42, 278.0, 270.96],
  "crop_sha256": "3a4f89b...",
  "observation": {
    "structure_type": "fraction",
    "vinculum_bbox": [180.2, 259.46, 195.4, 259.96],
    "numerator_region": [180.2, 250.0, 195.4, 258.5],
    "denominator_region": [180.2, 261.0, 195.4, 270.0]
  },
  "confidence": 0.94,
  "dependencies": ["OBS-PIAA-004-DISCOVERY-001"],
  "status": "OBSERVED"
}
```

---

## 5. Execution Slice: Prioritized Integration Sequence

We will not integrate all 10 tools simultaneously. The initial execution slice connects the four highest-confidence, highest-independence tools:

1. **Step 1 — Discovery Adapter (`targeted_math_detector.py`):**
   - Wrap `extract_raw_observations()` into an unconditioned proposal generator emitting candidate `bbox_pdf_pt` sidecars without reading `TARGET_LATEX_NAMES`.
2. **Step 2 — Safe Adaptive Cropping (`vision_comparison_pipeline.py`):**
   - Call `crop_pdf_region` with explicit RGB colorspace and `min_content_ratio` validation, outputting immutable crop PNGs to `DATASETS/structural_preservation/crops/`.
3. **Step 3 — Multi-Substrate L3 Cross-Verification:**
   - Execute `chroma_visual_reader.py` (for physical 2D fraction bars and braces) in parallel with `physical_symbol_matcher.py` (for Bilinear NCC raster template matching).
   - If font metadata says `+` but Chroma detects a vinculum bar, emit `UNRESOLVED_CONFLICT`.
4. **Step 4 — Physical Perimeter Contact & Prose QA (`audit_rendered_png_producers.py` + `experiments_crop_isolation.py`):**
   - Run `analyze_crop_image()`: assert `border_touch_1px == 0`.
   - Run `evaluate_isolation()`: assert `prose_contamination == False`.
5. **Step 5 — Diagnostic Overlays (`cross_reference_pipeline.py`):**
   - Call `generate_annotated_page()` to render visual targeting verification overlays.

---

## 6. Non-Negotiable Boundaries

1. **Frozen V1 Baselines:** `delimiter_aware_structural_recovery.py` and `cross_paper_delimiter_generalization_spec_v1.json` remain byte-for-byte locked.
2. **Sealed PIAA Fixtures:** `PIAA-001` through `PIAA-010` remain untouched.
3. **Zero Gold Leakage:** Source inventory coordinates must never enter L1 discovery tools.
4. **Standalone Isolation:** Standalone mathematical recovery remains decoupled from King Wen game, ternary, or quantum execution runtimes.

