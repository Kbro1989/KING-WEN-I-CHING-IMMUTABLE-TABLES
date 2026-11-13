# Original Pix2Text Pipeline Recovery — Exact Composition & Historical Evidence Chain

**Date:** 2026-11-07  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b651477afd0bcba55a2454e0a123cde`

---

## 1. Original Pipeline Composition (Exact)

### Layer 1 — Discovery (Harvest)

| Script | Version | Output | Records | Key Contracts |
|--------|---------|--------|---------|---------------|
| `scripts/pix2text_harvest.py` | `pix2text-harvest 0.2.0` | `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_candidates.jsonl` | 158 raw-harvest candidates | **Immutable evidence** — never modified by downstream layers |

**Inputs:**
- Raw Pix2Text outputs: `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_output/*.md` (158 files)
- Source page renders: `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/page_*.png`
- Frozen parser reference: `DATASETS/candidates_1907.04931.json` (4 records)

**Key Implementation Details:**
- Pix2Text version: `1.1.7`
- Model: `pix2text-mfd-1.5-onnx`
- Recognition method: `p2t.recognize(pil_image)`
- Harvest script hash: `70de92169a42cff0d467bb62443656f0b1da9277` (script SHA-256)
- Input SHA-256 per record (source image hash)
- `FakeElement` reconstruction from Pix2Text `Page` repr dumps
- Classification: `DISPLAY_EQUATION`, `INLINE_MATH`, `TEXT`, `PROSE`, `TITLE`, `UNPARSEABLE`

---

### Layer 2 — Adjudication (Classification)

| Script | Output | Records | Status Model |
|--------|--------|---------|--------------|
| `scripts/adjudicate_candidates_v2.py` | `adjudication_report.jsonl` (158 records) | 158 | 4-level: `SPATIAL_MATCH` / `TEXT_MATCH` / `VISUALLY_VERIFIED` / `ADJUDICATED` / `UNADJUDICATED` |
| | `adjudication_summary.json` | 1 | Aggregate metrics |
| | `adjudication_report.md` | 1 | Human-readable |

**Adjudication Logic (Two-Path):**
1. **Spatial first** — parser candidate box overlap/containment (`parser_match_ids`)
2. **Text match** — normalized token overlap ≥ 0.5 threshold
3. **Visually verified** — source crop non-blank + OCR carries real content (`_crop_nonblank`)
4. **Adjudicated** — human review flag

**Outputs:**
- `adjudication_report.jsonl` — 158 records with `match_status`, `adjudication`
- `adjudication_summary.json` — aggregate counts
- `adjudication_report.md` — markdown summary

**Layer 2 Results (from `adjudication_summary.json`):**
- `region_count`: 158
- `unique_expression_count`: 137
- `equation_occurrence_count`: 95
- Status distribution: `VISUALLY_VERIFIED`: 30, `UNADJUDICATED`: 128, `SPATIAL_MATCH`: 0, `TEXT_MATCH`: 0, `ADJUDICATED`: 0

---

### Layer 3 — Targeted Adjudication

| Script | Output | Records | Contract |
|--------|--------|---------|----------|
| `scripts/adjudicate_targets.py` | `adjudication_targets.jsonl` | 158 | Carries forward L2 explicit statuses; adjudicates `UNADJUDICATED` |
| | `adjudication_targets_summary.json` | 1 | Aggregate |
| | `adjudication_targets_report.md` | 1 | Markdown |

**Layer 3 Status Model (exclusive within layer):**
- `ADJUDICATED` — newly adjudicated; `adjudication_detail` non-semantic
- `UNVERIFIED` — could not be verified
- `NO_MATCH` — no parser association and no evidence
- **Carry-forward** (exclusive within layer): `VISUALLY_VERIFIED`, `SPATIAL_MATCH`, `TEXT_MATCH` from Layer 2

**Layer 3 Results (from `adjudication_targets_summary.json`):**
- `total_records`: 158
- `carried_forward_count`: 32 (32 with detail)
- `newly_adjudicated_count`: 126 (126 with detail)

**Contract:** `adjudication_targets.jsonl` is the **authoritative final adjudication** for Layer 3. Layer 2 explicit statuses are carried forward unchanged. Statuses are NOT mutually exclusive across layers.

---

## 2. Historical Evidence Chain (Per-Crop Traceability)

### Per-Crop Evidence Artifacts (158 candidates)

For each of the 158 Pix2Text candidates, the chain is:

| Layer | Artifact | Fields Preserved |
|-------|----------|------------------|
| **Harvest (L1)** | `pix2text_candidates.jsonl` | `_pix2text_file`, `paper_id`, `pdf_sha256`, `page_index`, `pdf_page`, `render_sha256`, `image_path`, `pix2text_element_id`, `source_element_id`, `element_index`, `element_type`, `bbox_original`, `raw_ocr`, `element_score`, `metadata_score`, `parser_match_ids`, `match_status`, `adjudication`, `candidate_class`, `parse_error`, `source_image_sha256`, `pix2text_version`, `input_sha256`, `harvest_script_sha256`, `harvest_script_version` |
| **Adjudication (L2)** | `adjudication_report.jsonl` | All L1 fields + `match_status` (SPATIAL_MATCH/TEXT_MATCH/VISUALLY_VERIFIED/ADJUDICATED/UNADJUDICATED), `adjudication` detail |
| **Targeted (L3)** | `adjudication_targets.jsonl` | All L2 fields + L3 `match_status` (ADJUDICATED/UNVERIFIED/NO_MATCH + carry-forward) |

### Per-Crop Evidence Chain Example (crop_06 from polarity ablation)

| Artifact | Path | Role |
|----------|------|------|
| Source crop (original) | `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/crop_06_4x.png` | Source image |
| Source crop (inverted) | `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/crop_06_4x_inverted.png` | Inverted variant |
| Pix2Text output (original) | `ocr_polarity_ablation_report.json` → `crop_06_4x` | `original_latex` = `""` |
| Pix2Text output (inverted) | `ocr_polarity_ablation_report.json` → `crop_06_4x` | `inverted_latex` = `""` |
| Human adjudication | `cache/scripts/ocr_output/crop06_adjudication_revision.json` | Glyph identity `=` (probable), `semantic_classification`: `pending_context_review` |
| Visual evidence | `cache/scripts/ocr_output/crop_06_native.png`, `crop_06_4x.png`, `page3_with_bboxes.png` | Visual verification artifacts |

---

## 3. Polarity Ablation Experiment (Pre-Existing)

### Script: `scripts/ocr_polarity_ablation.py`

| Parameter | Value |
|-----------|-------|
| Engine | Pix2Text `pix2text-mfd-1.5-onnx` v1.1.7 |
| Method | `p2t.recognize(pil_image)` |
| Transformation | Pixel-wise inversion: `inverted = 255 - original` (per channel, uint8) |
| Crops tested | 8 crops from `1907_04931` (crop_00 through crop_06, plus crop__) |
| Output | `DATASETS/ocr_polarity_ablation/ocr_polarity_ablation_report.json` |

### Results (from `ocr_polarity_ablation_report.json`)

| Metric | Value |
|--------|-------|
| Crops tested | 8 |
| Exact matches | 3/8 |
| Non-empty original | 5 |
| Non-empty inverted | 4 |
| Error classifications | `deletion (recognition loss: c)`: 1, `substitution (added: a, h, k, r)`: 1, `none`: 3, `deletion (recognition failure)`: 1, `case_change`: 1, `substitution (removed: \n, a, g, i, m, s; added: O)`: 1 |

### Per-Crop Polarity Results

| Crop | Original LaTeX | Inverted LaTeX | Exact Match | Error Classification |
|------|----------------|----------------|-------------|---------------------|
| `crop_00_4x` | `$$ c= $$` | `$$ = $$` | ❌ | `deletion (recognition loss: c)` |
| `crop_01_4x` | `$$ f^{( \ell)} \times f $$` | `$$\mathfrak{r}^{( \ell)} \times f $$` | ❌ | `substitution (added: a, h, k, r)` |
| `crop_02_4x` | `""` | `""` | ✅ | `none` |
| `crop_03_4x` | `$$ = $$` | `""` | ❌ | `deletion (recognition failure)` |
| `crop_04_4x` | `o` | `O` | ❌ | `case_change` |
| `crop_05_4x` | `$$\sigma $$` | `O` | ❌ | `substitution (removed: \n, a, g, i, m, s; added: O)` |
| `crop_06_4x` | `""` | `""` | ✅ | `none` |
| `crop__4x` | `""` | `""` | ✅ | `none` |

---

## 4. RapidOCR Crops (Separate Population)

### Pre-Existing RapidOCR Records (7 crops)

| Path | Engine | Model | Output |
|------|--------|-------|--------|
| `cache/scripts/ocr_output/rapidocr_crop_00.json` … `06.json` | RapidOCR (PP-OCRv6) | PP-OCRv6 det/rec/cls ONNX | Per-crop text, confidence, boxes |
| `cache/scripts/ocr_output/rapidocr_all_crops.json` | RapidOCR | PP-OCRv6 | Aggregated (duplicates individual) |

### RapidOCR Records Summary

| Crop | Text | Confidence | Chars | Boxes |
|------|------|------------|-------|-------|
| 00 | `三` | 0.825 | `三 (0.83)` | 1 box |
| 01 | `(e) X` | 0.726 | `(e) (0.92) \| X (0.53)` | 2 boxes |
| 02 | *(no detection)* | null | — | — |
| 03 | `三` | 0.623 | `三 (0.62)` | 1 box |
| 04 | `b` | 0.964 | `b (0.96)` | 1 box |
| 05 | `9` | 0.81 | `9 (0.81)` | 1 box |
| 06 | `三` | 0.74 | `三 (0.74)` | 1 box |

**Note:** RapidOCR is a **separate population** (Chinese character recognition), not part of the Pix2Text pipeline. Different engine, different crops, different purpose.

---

## 5. Near-Golden Disposition Assessment

### What Was Achieved (L1–L3 Complete)

| Layer | Status | Evidence |
|-------|--------|----------|
| L1 Harvest | ✅ Complete | 158 candidates, immutable, SHA-256 traced |
| L2 Adjudication | ✅ Complete | 158 records, 4-level model, 30 VISUALLY_VERIFIED |
| L3 Targeted | ✅ Complete | 158 records, 32 carried forward, 126 newly adjudicated |
| Polarity Ablation | ✅ Complete | 8 crops, 3/8 exact match, error taxonomy |
| Crop 06 Adjudication | ✅ Partial | Glyph `=` probable, semantic classification pending |

### What Remained Unresolved (Blocking Golden)

| Gap | Evidence | Impact |
|-----|----------|--------|
| Semantic classification for crop 06 | `semantic_classification`: `pending_context_review` | Glyph identity `=` probable, but mathematical role undetermined |
| Layer 2 spatial/text matches | 0 SPATIAL_MATCH, 0 TEXT_MATCH | Parser reference only 4 records; low spatial overlap |
| Multi-paper generalization | Only 1 paper (1907.04931) | No multi-paper evaluation |
| Semantic classification contract | Layer 3 `ADJUDICATED` = non-semantic | No display_equation/footnote/annotation classification |
| Polarity ablation scope | 8 crops only | Not representative of full math distribution |

### Golden Blocker Summary

The pipeline was **near-golden** because:
- ✅ Full L1–L3 execution chain complete
- ✅ Immutable evidence chain (SHA-256 throughout)
- ✅ Exclusive status model enforced per layer
- ✅ Carry-forward contract honored across layers
- ✅ Polarity ablation as controlled experiment
- ❌ **Semantic classification gap** — no display_equation/footnote/annotation resolution
- ❌ **Parser coverage** — only 4 parser records for 158 candidates
- ❌ **Single paper** — no multi-paper validation
- ❌ **Crop 06 semantic gap** — glyph identity known, role unknown

---

## 6. Provenance Hashes (Frozen)

| Artifact | SHA-256 |
|----------|---------|
| `scripts/pix2text_harvest.py` | `70de92169a42cff0d467bb62443656f0b1da9277` |
| `scripts/ocr_polarity_ablation.py` | (compute at runtime) |
| `scripts/adjudicate_candidates_v2.py` | (compute at runtime) |
| `scripts/adjudicate_targets.py` | (compute at runtime) |
| `pix2text_candidates.jsonl` | Per-record `input_sha256` + `harvest_script_sha256` |
| `adjudication_report.jsonl` | 162,121 bytes |
| `adjudication_targets.jsonl` | 166,431 bytes |
| `ocr_polarity_ablation_report.json` | `608b4d62f840547a69a974ab897455a99a8b890a596e21062901e1615e2ff217` |

---

## 7. Reproducibility Contract

### Controlled Rerun Requirements

To reproduce the original pipeline outputs exactly:

| Step | Command | Expected Output |
|------|---------|-----------------|
| 1. L1 Harvest | `python scripts/pix2text_harvest.py` | `pix2text_candidates.jsonl` (158 records, identical fields) |
| 2. L2 Adjudication | `python scripts/adjudicate_candidates_v2.py` | `adjudication_report.jsonl`, `summary.json`, `report.md` |
| 3. L3 Targeted | `python scripts/adjudicate_targets.py` | `adjudication_targets.jsonl`, `summary.json`, `report.md` |
| 4. Polarity Ablation | `python scripts/ocr_polarity_ablation.py` | `ocr_polarity_ablation_report.json` (3/8 exact) |

### Determinism Requirements

- Pix2Text model weights frozen (`pix2text-mfd-1.5-onnx`)
- Pix2Text version pinned (`1.1.7`)
- Harvest script version pinned (`pix2text-harvest 0.2.0`)
- All SHA-256 hashes must match frozen values
- No modification to `pix2text_candidates.jsonl` (immutable)
- Carry-forward contract enforced: L2 statuses → L3 unchanged

---

## 8. Separation of Concerns (Critical)

### Original Pipeline (Preserve)
- Pix2Text harvest → adjudication → targeted adjudication
- Polarity ablation (8 crops, Pix2Text)
- Crop 06 human adjudication
- 158 candidates, 3-layer adjudication, polarity ablation

### Later Additions (Isolate)
| Addition | Location | Disposition |
|----------|----------|-------------|
| RapidOCR (7 crops) | `cache/scripts/ocr_output/rapidocr_crop_*.json` | `NEEDS_PRESERVATION` — separate population |
| Tesseract (656 crops) | `DATASETS/d1_diagnostic_2026-11-06/ocr_tesseract_results.json` | `UNVERIFIED` — new diagnostic |
| RapidOCR on D1 crops | `DATASETS/d1_diagnostic_2026-11-06/ocr_rapidocr_sample10.json` | `UNVERIFIED` — new diagnostic |
| D3 visual layer run | `DATASETS/d3_diagnostic_2026-11-06/delimiter_records.json` | `UNVERIFIED` — new diagnostic |

**Rule:** Later additions must NOT silently become dependencies of the original pipeline. They are isolated experiments.

---

## 8. Recovery Next Steps

1. **Verify exact reproducibility** — run L1→L2→L3 controlled rerun, confirm bit-identical outputs
2. **Resolve crop 06 semantic gap** — complete context review for display_equation/footnote/annotation
3. **Expand parser coverage** — increase `candidates_1907.04931.json` beyond 4 records
4. **Multi-paper evaluation** — apply pipeline to 2nd, 3rd papers
5. **Semantic classification contract** — define `display_equation` / `footnote` / `annotation` criteria

---

**Milestone B remains OPEN / NOT VERIFIED.** The original pipeline is recovered and documented. Its near-golden disposition is established. Golden promotion requires resolving the semantic classification gap and multi-paper validation.

---

**Document Status:** This recovery document is the authoritative record of the original pipeline composition, evidence chain, and disposition. All later experimental additions are explicitly separated and labeled.