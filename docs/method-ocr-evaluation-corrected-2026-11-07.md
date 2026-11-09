# OCR Tools — Corrected Dispositions & Paired Evaluation

**Date:** 2026-11-07  
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`  
**Branch:** `v2-remediation`  
**HEAD:** `3bb937209b651477afd0bcba55a2454e0a123cde`

---

## 1. Corrected Dispositions

| Component | Previous Disposition | **Corrected Disposition** | Reason |
|-----------|---------------------|---------------------------|--------|
| D1 targeted detector | Execution reported | **UNVERIFIED** | Execution confirmed; output inspection complete (see below) |
| D3 visual analysis layer | Execution reported | **UNVERIFIED** | Execution confirmed; only geometric candidates, no delimiter classification |
| Tesseract (psm 7) | NEEDS_PRESERVATION | **NEEDS_PRESERVATION** | Complete run preserved; no accuracy claim |
| RapidOCR (PP-OCRv6) | GOLDEN_CANDIDATE | **NEEDS_PRESERVATION** | Sample only (10/656); superiority UNVERIFIED |
| RapidOCR comparative superiority | GOLDEN_CANDIDATE | **UNVERIFIED** | Unequal populations; no accuracy measurement |

**Key correction:** RapidOCR is **not** a golden candidate. The comparison was methodologically flawed (see Section 2).

---

## 2. Why RapidOCR is Not a Golden Candidate

| Problem | Evidence |
|---------|----------|
| **A. Unequal populations** | Tesseract: 656 crops. RapidOCR: 10 crops. Not comparable. |
| **B. Different task configurations** | Tesseract: PSM 7 (single line). RapidOCR: detection+recognition pipeline. Engine differences confounded with task differences. |
| **C. Confidence ≠ correctness** | RapidOCR confidence 0.66–1.00 is model confidence, not verified accuracy. E.g., "Eud2" at 0.72 confidence is likely wrong. |
| **D. Unsupported speed extrapolation** | 10 crops in ~30s ≠ 656 crops in 30 min. Initialization, batching, hardware affect throughput non-linearly. |

**What the first 10 crops actually show:** RapidOCR produces different, sometimes more coherent text fragments on ordinary document text. The crops are fragments of ordinary typography (author names, affiliations), not isolated mathematical expressions. Visual candidate generation ≠ mathematical-region localization.

---

## 3. Paired OCR Evaluation (First 10 Crops)

| Crop | Tesseract (PSM 7) | RapidOCR (PP-OCRv6) | Notes |
|------|-------------------|---------------------|-------|
| `0000` | `g In` (2 tok) | `In` (0.999), `F` (0.663) | RapidOCR drops "g", adds "F" |
| `0001` | *(empty)* | `of T` (0.974), `nive` (0.973) | RapidOCR detects; Tesseract misses |
| `0002` | `ied A` | `ied A` (0.922) | **Agreement** |
| `0003` | `AI` | `AI` (0.999) | **Agreement** |
| `0004` | `astit` | `nstit` (0.998), `op` (0.764) | RapidOCR more complete |
| `0005` | *(empty)* | `titu` (0.999), `uop` (0.770) | RapidOCR detects; Tesseract misses |
| `0006` | `ute` | `tute` (1.000), `n` (0.984) | RapidOCR more complete |
| `0007` | `istw` | `ustw` (0.989), `ity` (0.907) | Different fragment |
| `0008` | `orth;` | `orthy` (0.992) | RapidOCR more complete |
| `0009` | `nsti` | `nsti` (1.000), `Eud2` (0.720) | **Agreement** on `nsti`; `Eud2` likely noise |

### Summary (10 crops)

| Metric | Tesseract | RapidOCR |
|--------|-----------|----------|
| Crops with any text | 7/10 | 10/10 |
| Total tokens | 9 | 17 |
| Exact agreement on content | 3/10 (0002, 0003, 0009) | — |
| RapidOCR detects where Tesseract misses | — | 0001, 0005 |
| RapidOCR more complete text | — | 0004, 0006, 0008 |

**Conclusion:** RapidOCR produces more detections on these text fragments, but **no accuracy measurement** (CER/WER against ground truth) was performed. "Confidence" values are not verified correctness.

---

## 4. Crop Content Classification (All 656 Crops)

Based on Tesseract output + candidate reasons from `targeted_math_detection.json`:

| Category | Count | % | Notes |
|----------|-------|---|-------|
| **Empty OCR** | 423 | 64.5% | No text detected by Tesseract |
| **Ordinary text fragments** | 230 | 35.1% | Author names, affiliations, words (`In`, `of T`, `ied A`, `nstit`, `orth`, etc.) |
| **Single chars / punctuation** | 3 | 0.5% | `=`, `,` (3 crops with `math_hits=1`, all `=` sign) |
| **Math symbols** | 0 | 0% | No integrals, sums, greek, roots, etc. detected |
| **Total** | **656** | **100%** | |

### Visual Candidate Reasons

| Reason | Count | % |
|--------|-------|---|
| `tall_narrow_component` | 649 | 98.9% |
| `wide_horizontal_component` | 7 | 1.1% |

**Critical finding:** The visual detector's heuristics (`tall_narrow` = stretched delimiter candidate; `wide_horizontal` = fraction bar candidate) are **overwhelmingly capturing ordinary typography** (tall letters in author names, column separators), not mathematical delimiters. Only 3 crops contained an `=` sign; **zero** contained integrals, sums, greek letters, roots, or other math notation.

---

## 5. D3 Visual Analysis Layer — What It Actually Contains

`delimiter_records.json` (203 KB) contains:

| Field | Value | Assessment |
|-------|-------|------------|
| `geometric_candidates` | 114 entries | **Per-character** tall-glyph hypotheses (same as `geometry_candidates` from D1) |
| `script_position_candidates` | 0 | None |
| `visual_components_detected` | 2,729 | Connected components (same as D1's `connected_component_count`) |
| **Delimiter classification** | **NONE** | No pairing, nesting, enclosure, or delimiter identity |
| **Font-aware classification** | **NONE** | Does not call `font_aware_math_classifier.py` or `delimiter_aware_structural_recovery.py` |

**The D3 layer is a pass-through** of D1's geometric candidates with no additional delimiter detection or structural recovery. The name "delimiter_records" is misleading — it contains **unverified geometric candidates**, not classified delimiters.

---

## 6. Evidence Inventory

| File | Size | Status |
|------|------|--------|
| `ocr_tesseract_results.json` | 145 KB | ✅ Complete (656/656) |
| `ocr_rapidocr_sample10.json` | 6.5 KB | ✅ Sample (10/656) |
| `targeted_math_detection.json` | 1.9 MB | ✅ Complete |
| `delimiter_records.json` | 203 KB | ✅ Complete |
| 658 image files | ~30 MB | ✅ Preserved |

---

## 7. Corrected Gate Status

| Item | Status |
|------|--------|
| D1 execution | ✅ Complete (exit 0) |
| D3 execution | ✅ Complete (exit 0) |
| Tesseract OCR | ✅ Complete (656/656) |
| RapidOCR OCR | Sample only (10/656) |
| Paired OCR evaluation | ✅ Complete (10 crops) |
| Crop classification | ✅ Complete (656 crops) |
| **Milestone B** | **OPEN / NOT VERIFIED** |
| Certification | **Blocked** |

---

## 8. Recommended Next Steps

1. **Paired, adjudicated OCR comparison** — same crops, both engines, CER/WER against ground truth.
2. **Stratified crop sampling** — separate ordinary text, math regions, punctuation, noise before evaluation.
3. **Mathematical-region localization** — the current visual detector does not isolate math; it fragments ordinary text.
4. **Do not run full 656-crop RapidOCR** until paired evaluation design is complete.
5. **Inspect the 3 `=`-sign crops** (`component_0184`, `0310`, `0366`) — verify if they are actual math or noise.

---

**Milestone B remains OPEN / NOT VERIFIED.** No tests executed; no production wiring; no corpus execution.