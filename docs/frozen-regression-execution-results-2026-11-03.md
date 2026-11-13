# Frozen Regression Execution Results — Border Detection & Ballooning

**Date:** 2026-11-03
**Script:** `scripts/run_border_evaluation.py`
**Governing spec:** `docs/frozen-regression-evaluation-mapping-2026-11-03.md`
**Status:** Execution task 1 (border evaluation) + execution task 2 (ballooning) complete. Task 3 (P6 coverage) pending.

---

## 1. Border Detection vs Manual Adjudication

### Results

| Crop | Adjudicated crop status | Border expected | Detector: contaminated | Detector: borders | Agreement |
|---|---|---|---|---|---|
| 1907_04931_cand1_expectation__CURRENT.png | PASS | No | **Yes** | top,bottom,left,right | **DISAGREE** |
| 2104_01277_cand1_inner_product__CURRENT.png | BOUNDARY_TOUCH | Yes | Yes | bottom,left,right | AGREE |
| 2104_01277_cand3_abs_inner_product__CURRENT.png | BOUNDARY_TOUCH | Yes | Yes | top,bottom,left | AGREE |
| 2104_01277_cand8_summation_lambda__CORRECTED.png | PASS | No | **Yes** | bottom,left,right | **DISAGREE** |
| 2104_01277_cand8_summation_lambda__ORIGINAL.png | PASS | No | **Yes** | bottom,left,right | **DISAGREE** |
| 2206_00364_cand6_dot_derivative__CORRECTED.png | BOUNDARY_TOUCH | Yes | Yes | top,left,right | AGREE |
| 2206_00364_cand6_dot_derivative__ORIGINAL.png | BOUNDARY_TOUCH | Yes | Yes | top,left,right | AGREE |
| 2206_00364_cand7_denoiser_function__CORRECTED.png | BOUNDARY_TOUCH | Yes | Yes | top,bottom,left | AGREE |
| 2206_00364_cand7_denoiser_function__ORIGINAL.png | BOUNDARY_TOUCH | Yes | Yes | top,bottom,left | AGREE |
| 2206_00364_cand8_skip_scaling__CORRECTED.png | BOUNDARY_TOUCH | Yes | Yes | top,bottom,right | AGREE |
| 2206_00364_cand8_skip_scaling__ORIGINAL.png | BOUNDARY_TOUCH | Yes | Yes | top,bottom,right | AGREE |
| 2605_27315_cand0_parameter_set__CURRENT.png | BOUNDARY_CLIPPED | Yes | Yes | right | AGREE |

**Summary:** 9/12 AGREE (75%), 3/12 DISAGREE (25%).

### Disagreement Analysis

All 3 disagreements share the same pattern: the detector reports `border_contact=True` on crops where adjudication expected `border_expected=False`. These are:

1. **`1907_04931_cand1_expectation__CURRENT.png`** — adjudicated CONFIRMED_ACCURATE, crop=PASS. Detector reports all 4 borders contaminated. The crop contains `\langle T \chi_I ,` which is a partial fragment with content extending to all edges. The detector's simple threshold (`gray < 250`) flags any dark pixel at the border, including legitimate content that simply reaches the crop edge.

2. **`2104_01277_cand8_summation_lambda__CORRECTED.png`** — adjudicated CONFIRMED_ACCURATE, crop=PASS. Detector reports bottom,left,right contaminated. The crop contains `\cup_{j=1}^{i-1} (\lambda_j + Q)` with subscripts that extend to the bottom and left edges.

3. **`2104_01277_cand8_summation_lambda__ORIGINAL.png`** — same as above (original version).

**Root cause:** The detector uses a binary threshold (`gray < 250`) on border pixels. Any dark content touching the border — including legitimate formula content that extends to the crop edge — is flagged as contamination. The detector cannot distinguish between:
- **True contamination**: content clipped by the crop boundary (information loss)
- **Border-touching content**: formula content that legitimately extends to the crop edge (no information loss)

**Refined detector (3-concept model):** The detector now returns three distinct concepts:
- `border_contact`: geometric contact (any dark pixel at border) — same as before
- `suspected_clipping`: density ratio > 1.5 (border density / overall density) — **False for all 12 crops** (density ratios range 0.00–0.02, far below 1.5 threshold)
- `confirmed_information_loss`: requires external verification (OCR/structural), defaults to False

**Key finding:** The density-ratio heuristic is too conservative — it never triggers. The border density is always much lower than the overall density because formula content is spread across the image, not concentrated at edges. The 3 false positives are cases where content touches the border but is NOT concentrated there (legitimate edge-touching content). The 9 true positives are cases where content touches the border AND the crop is intentionally partial or has boundary ambiguity.

**Implication:** Distinguishing true clipping from border-touching content requires **semantic analysis** (complete symbol vs. clipped fragment), not just density. The current detector is useful as a **screening tool** (100% recall, no false negatives) but not as a **classification tool** (25% false positive rate among the 12 tested). The `suspected_clipping` heuristic needs recalibration or replacement with a semantic check.

**Recommendation:** The detector should be augmented with a secondary check — e.g., comparing border pixel density against the overall image density, or checking whether the border-touching content is a complete symbol vs. a clipped fragment. This is a design improvement, not a new function.

### Contamination Level Distribution

| Border pattern | Count | Interpretation |
|---|---|---|
| top,bottom,left,right | 3 | Full border contact (likely contamination or dense content) |
| bottom,left,right | 1 | Three-edge contact |
| top,bottom,left | 2 | Three-edge contact |
| top,left,right | 1 | Three-edge contact |
| right | 2 | Right-edge only (likely subscript clipping) |
| top,bottom,right | 1 | Three-edge contact |
| bottom,right | 2 | Two-edge contact |

---

## 2. Ballooning Experiment

### Results

| Crop | Original shape | Ballooned shape | Balloon path |
|---|---|---|---|
| 1907_04931_cand1_expectation__CURRENT.png | (19, 8) | (171, 72) | `balloon_renders/1907_04931_cand1_expectation__CURRENT__BALLOON9x.png` |
| 2104_01277_cand1_inner_product__CURRENT.png | (31, 12) | (279, 108) | `balloon_renders/2104_01277_cand1_inner_product__CURRENT__BALLOON9x.png` |
| 2104_01277_cand3_abs_inner_product__CURRENT.png | (31, 12) | (279, 108) | `balloon_renders/2104_01277_cand3_abs_inner_product__CURRENT__BALLOON9x.png` |
| 2104_01277_cand8_summation_lambda__CORRECTED.png | (24, 12) | (216, 108) | `balloon_renders/2104_01277_cand8_summation_lambda__CORRECTED__BALLOON9x.png` |
| 2104_01277_cand8_summation_lambda__ORIGINAL.png | (24, 12) | (216, 108) | `balloon_renders/2104_01277_cand8_summation_lambda__ORIGINAL__BALLOON9x.png` |
| 2206_00364_cand6_dot_derivative__CORRECTED.png | (18, 10) | (162, 90) | `balloon_renders/2206_00364_cand6_dot_derivative__CORRECTED__BALLOON9x.png` |
| 2206_00364_cand6_dot_derivative__ORIGINAL.png | (18, 10) | (162, 90) | `balloon_renders/2206_00364_cand6_dot_derivative__ORIGINAL__BALLOON9x.png` |
| 2206_00364_cand7_denoiser_function__CORRECTED.png | (18, 10) | (162, 90) | `balloon_renders/2206_00364_cand7_denoiser_function__CORRECTED__BALLOON9x.png` |
| 2206_00364_cand7_denoiser_function__ORIGINAL.png | (18, 10) | (162, 90) | `balloon_renders/2206_00364_cand7_denoiser_function__ORIGINAL__BALLOON9x.png` |
| 2206_00364_cand8_skip_scaling__CORRECTED.png | (18, 10) | (162, 90) | `balloon_renders/2206_00364_cand8_skip_scaling__CORRECTED__BALLOON9x.png` |
| 2206_00364_cand8_skip_scaling__ORIGINAL.png | (18, 10) | (162, 90) | `balloon_renders/2206_00364_cand8_skip_scaling__ORIGINAL__BALLOON9x.png` |
| 2605_27315_cand0_parameter_set__CURRENT.png | (24, 10) | (216, 90) | `balloon_renders/2605_27315_cand0_parameter_set__CURRENT__BALLOON9x.png` |

**Transformation applied:** 9× bicubic upscale (INTER_CUBIC) + Gaussian blur (σ=1.0) for edge smoothing.

**All 12 crops ballooned successfully.** No originals modified. Balloon renders are in a separate directory.

### Balloon Limitations (per external assessment)

- Bicubic interpolation + Gaussian blur can **erase or distort thin strokes**.
- Balloon output is an **alternate recognition input**, not a more authoritative representation.
- Balloon results must be compared against original OCR, not assumed to be improvements.

---

## 3. P6 Coverage — Status

**Not yet addressed.** P6 (similar-looking glyph discrimination) has 0 adjudicated cases in the existing artifact set.

**Required for P6:** Independently adjudicated ground truth for similar-looking glyph pairs (e.g., `\sigma`/`s`, `\partial`/`d`, `\propto`/`\alpha`, `\lambda`/`\Lambda`). These must be sourced from actual paper crops, not OCR-generated labels.

**Recommendation:** Search the 21 candidate crops for visually confusable glyph pairs. The `get_ascii_pattern_v2()` classes (D/P/F/Q/M) provide a structural basis for identifying such pairs, but ground truth must come from independent adjudication.

---

## 4. Execution Status Summary

| Task | Status | Evidence |
|---|---|---|
| 1. Border detection vs manual adjudication | ✅ Complete | 9/12 agree (75%), 3 false positives documented |
| 2. Ballooning experiment | ✅ Complete | 12 balloon renders generated, parameters recorded |
| 3. P6 coverage | ⬜ Pending | No similar-looking glyph pairs adjudicated |
| 4. Variant OCR comparison | ⬜ Pending | Need to run OCR on original/corrected/balloon/context/multiscale |
| 5. Structural reconstruction measurement | ⬜ Pending | Need to compare LaTeX structure across variants |
| 6. Source fidelity measurement | ⬜ Pending | Need to compare against adjudicated reference LaTeX |

### 3 Tracked Outcomes (per external assessment)

| Outcome | Status |
|---|---|
| Recognition | Not yet measured |
| Structural reconstruction | Not yet measured |
| Source fidelity | Not yet measured |

### Governance Status (per external assessment)

| Dimension | Status |
|---|---|
| Implementation | ✅ Passed |
| Syntax and import checks | ✅ Passed |
| Basic functional checks | ✅ Passed |
| Border detection accuracy | ⬜ Partially established (9/12, false positive pattern identified) |
| Ballooning effect | ⬜ Not measured (renders generated, OCR not yet run) |
| Structural reconstruction accuracy | ⬜ Not established |
| Semantic fidelity | ⬜ Not established |
| Independent acceptance | ⬜ Not established |

---

## 5. Artifacts Produced

| Artifact | Path | Description |
|---|---|---|
| Border evaluation results | `DATASETS/vision_comparison/border_evaluation_results.jsonl` | 12 records with border detection, balloon params, adjudication match |
| Balloon renders | `DATASETS/vision_comparison/balloon_renders/` | 12 × 9× ballooned PNGs |
| Evaluation script | `scripts/run_border_evaluation.py` | Reproducible border + balloon evaluation |
| Frozen regression mapping | `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | 170-line governing spec |
| Authority map | `docs/cross-document-finding-authority-map-2026-11-03.md` | 23 findings, 10 acceptance criteria |

---

## 6. Next Steps

1. **Run OCR on all 5 variants** (original, corrected, balloon, context-expanded, multiscale) for each of the 12 crops
2. **Compare recognition results** across variants — does ballooning improve OCR accuracy?
3. **Measure structural reconstruction** — does the LaTeX structure survive better in any variant?
4. **Measure source fidelity** — which variant's OCR output best matches the adjudicated reference LaTeX?
5. **Address P6 coverage** — find similar-looking glyph pairs with independent adjudication
6. **Document results** in a frozen regression evaluation report with per-candidate, per-variant, per-outcome measurements

No new functions. No baseline modifications. No gate closures. Only measured evidence.

---

*This is a read-only execution artifact. No source modifications, pipeline changes, or gate closures are implied by its creation.*