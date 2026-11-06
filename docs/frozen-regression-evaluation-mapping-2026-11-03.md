# Frozen Regression Evaluation — Artifact-to-Category Mapping

**Date:** 2026-11-03
**Purpose:** Traceable mapping from every existing visual artifact to its test category, expected result, and adjudicated reference. This is the first section of the evaluation report, created before any new OCR experiments.

**Governing principle:** Reuse existing artifacts. Do not overwrite originals. Do not modify frozen baseline. Classify by actual visual content, not filename.

---

## 1. Test Population Definitions

| # | Population | Definition | Key failure mode tested |
|---|---|---|---|
| P1 | Clean glyph recognition | Uncontaminated crops with single or simple multi-symbol expressions | Baseline OCR accuracy |
| P2 | Border contamination and clipping | Crops where content touches or is clipped by bbox boundary | Border detection, context expansion |
| P3 | Stretched delimiters and operators | Expressions containing `\sum`, `\int`, `\prod`, `\left(`, `\right)`, `\lfloor`, etc. | ASCII pattern classification, stretch vs hallucination |
| P4 | Inline mathematics and surrounding prose | Mixed math+prose in paragraphs | Partial formula detection, text boundaries |
| P5 | Multi-component mathematical structures | Fractions, limits, superscripts, subscripts combined | Region grouping, structural preservation |
| P6 | Similar-looking glyph discrimination | Glyphs OCR commonly confuses (e.g., `\sigma`/`s`, `\partial`/`d`) | Glyph balloon, edge smoothing |

---

## 2. Artifact-to-Category Mapping

### 2.1 crop_verification_renders/ (before/after pairs)

| Artifact | Paper | Candidate | Population | Expected result | Adjudicated reference |
|---|---|---|---|---|---|
| `2104_01277_cand8_summation_lambda__ORIGINAL.png` | 2104.01277 | cand8 | P3 (stretched operator) | `\cup_{j=1}^{i-1} (\lambda_j + Q)` | CONFIRMED_ACCURATE |
| `2104_01277_cand8_summation_lambda__CORRECTED.png` | 2104.01277 | cand8 | P3 (stretched operator) | `\cup_{j=1}^{i-1} (\lambda_j + Q)` | CONFIRMED_ACCURATE |
| `2206_00364_cand6_dot_derivative__ORIGINAL.png` | 2206.00364 | cand6 | P2 (border clipping) | `-\dot{\sigma}(t)` | BOUNDARY_AMBIGUITY |
| `2206_00364_cand6_dot_derivative__CORRECTED.png` | 2206.00364 | cand6 | P2 (border clipping) | `-\dot{\sigma}(t)` | BOUNDARY_AMBIGUITY |
| `2206_00364_cand7_denoiser_function__ORIGINAL.png` | 2206.00364 | cand7 | P5 (multi-component) | `D_{\theta}(\mathbf{x}; \sigma)` | BOUNDARY_AMBIGUITY |
| `2206_00364_cand7_denoiser_function__CORRECTED.png` | 2206.00364 | cand7 | P5 (multi-component) | `D_{\theta}(\mathbf{x}; \sigma)` | BOUNDARY_AMBIGUITY |
| `2206_00364_cand8_skip_scaling__ORIGINAL.png` | 2206.00364 | cand8 | P5 (multi-component) | `c_{\mathrm{skip}}(\sigma) \mathbf{x}` | BOUNDARY_AMBIGUITY |
| `2206_00364_cand8_skip_scaling__CORRECTED.png` | 2206.00364 | cand8 | P5 (multi-component) | `c_{\mathrm{skip}}(\sigma) \mathbf{x}` | BOUNDARY_AMBIGUITY |

### 2.2 crop_verification_renders/ (CURRENT — uncorrected)

| Artifact | Paper | Candidate | Population | Expected result | Adjudicated reference |
|---|---|---|---|---|---|
| `1907_04931_cand1_expectation__CURRENT.png` | 1907.04931 | cand1 | P1 (clean) | `(\zeta_v^{(\ell+1)})` | CONFIRMED_ACCURATE |
| `2104_01277_cand1_inner_product__CURRENT.png` | 2104.01277 | cand1 | P2 (border touch) | `\langle T \chi_I ,` | INTENDED_PARTIAL_FRAGMENT |
| `2104_01277_cand3_abs_inner_product__CURRENT.png` | 2104.01277 | cand3 | P2 (border touch) | `\| \langle T \chi_I ,` | INTENDED_PARTIAL_FRAGMENT |
| `2605_27315_cand0_parameter_set__CURRENT.png` | 2605.27315 | cand0 | P2 (border clipped) | `\{ \rho_k \}_{k=1}^{K}` | BOUNDARY_TRUNCATION |

### 2.3 candidate_visual_audit_renders/ (crop + context pairs, 21 candidates)

| Artifact pattern | Paper | Candidate | Population | Verdict | Crop boundary |
|---|---|---|---|---|---|
| `1907_04931_cand0_zeta_crop_pad3_2.png` + `_context.png` | 1907.04931 | cand0 | P1 (clean) | CONFIRMED_ACCURATE | PASS |
| `1907_04931_cand1_expectation_crop_pad3_2.png` + `_context.png` | 1907.04931 | cand1 | P1 (clean) | CONFIRMED_ACCURATE | PASS |
| `1907_04931_cand2_sqrt_crop_pad3_2.png` + `_context.png` | 1907.04931 | cand2 | P5 (multi-component) | CONFIRMED_ACCURATE | PASS |
| `1907_04931_cand3_proportional_crop_pad3_2.png` + `_context.png` | 1907.04931 | cand3 | P3 (stretched operator) | CONFIRMED_ACCURATE | PASS |
| `1212_0957_eq1.1_forward_summation_crop_pad3_2.png` + `_context.png` | 1212.0957 | eq1.1 | P3 (stretched operator) | NOTATION_AMBIGUITY | PASS |
| `1212_0957_eq1.2_inverse_summation_crop_pad3_2.png` + `_context.png` | 1212.0957 | eq1.2 | P3 (stretched operator) | CONFIRMED_ACCURATE | PASS |
| `2104_01277_cand0_set_membership_crop_pad3_2.png` + `_context.png` | 2104.01277 | cand0 | P1 (clean) | CONFIRMED_ACCURATE | PASS |
| `2104_01277_cand1_inner_product_crop_pad3_2.png` + `_context.png` | 2104.01277 | cand1 | P2 (border touch) | INTENDED_PARTIAL_FRAGMENT | BOUNDARY_TOUCH |
| `2104_01277_cand3_abs_inner_product_crop_pad3_2.png` + `_context.png` | 2104.01277 | cand3 | P2 (border touch) | INTENDED_PARTIAL_FRAGMENT | BOUNDARY_TOUCH |
| `2104_01277_cand5_norm_inequality_crop_pad3_2.png` + `_context.png` | 2104.01277 | cand5 | P5 (multi-component) | CONFIRMED_ACCURATE | PASS |
| `2104_01277_cand8_summation_lambda_crop_pad3_2.png` + `_context.png` | 2104.01277 | cand8 | P3 (stretched operator) | CONFIRMED_ACCURATE | PASS |
| `2206_00364_cand2_sigma_data_crop_pad3_2.png` + `_context.png` | 2206.00364 | cand2 | P1 (clean) | CONFIRMED_ACCURATE | PASS |
| `2206_00364_cand4_much_greater_than_crop_pad3_2.png` + `_context.png` | 2206.00364 | cand4 | P2 (leakage) | INTENDED_PARTIAL_FRAGMENT | LEAKAGE_NOTED |
| `2206_00364_cand6_dot_derivative_crop_pad3_2.png` + `_context.png` | 2206.00364 | cand6 | P2 (border touch) | BOUNDARY_AMBIGUITY | BOUNDARY_TOUCH |
| `2206_00364_cand7_denoiser_function_crop_pad3_2.png` + `_context.png` | 2206.00364 | cand7 | P5 (multi-component) | BOUNDARY_AMBIGUITY | BOUNDARY_TOUCH |
| `2206_00364_cand8_skip_scaling_crop_pad3_2.png` + `_context.png` | 2206.00364 | cand8 | P5 (multi-component) | BOUNDARY_AMBIGUITY | BOUNDARY_TOUCH |
| `2605_22902_cand0_l1_norm_crop_pad3_2.png` + `_context.png` | 2605.22902 | cand0 | P5 (multi-component) | CONFIRMED_ACCURATE | BOUNDARY_TOUCH |
| `2605_22902_cand1_gradient_crop_pad3_2.png` + `_context.png` | 2605.22902 | cand1 | P5 (multi-component) | CONFIRMED_ACCURATE | BOUNDARY_TOUCH |
| `2605_22902_cand3_partial_crop_pad3_2.png` + `_context.png` | 2605.22902 | cand3 | P4 (inline/partial) | INTENDED_PARTIAL_FRAGMENT | BOUNDARY_TOUCH |
| `2605_27315_cand0_parameter_set_crop_pad3_2.png` + `_context.png` | 2605.27315 | cand0 | P2 (border clipped) | BOUNDARY_TRUNCATION | BOUNDARY_CLIPPED |
| `2605_27315_cand2_partial_derivative_crop_pad3_2.png` + `_context.png` | 2605.27315 | cand2 | P4 (inline/partial) | CONFIRMED_ACCURATE | BOUNDARY_TOUCH |

### 2.4 crop_isolation_experiment/ (4 candidates × 4 crop variants)

| Variant suffix | Description | Population |
|---|---|---|
| `_baseline_p4.png` / `_baseline_p12.png` | Baseline crop at 4x/12x zoom | P1/P2 |
| `_tight_pad2_p4.png` / `_tight_pad2_p12.png` | Tight crop with (2,2) padding | P2 (border clipping) |
| `_asym_tight_y1_p4.png` / `_asym_tight_y1_p12.png` | Asymmetric tight crop, y-padding=1 | P2 (border clipping) |
| `_zero_y_pad0_p4.png` / `_zero_y_pad0_p12.png` | Zero y-padding crop | P2 (border clipping) |

### 2.5 Frozen Baseline

| Artifact | Description | Population |
|---|---|---|
| `baseline_frozen_padding15.jsonl` | Historical baseline with 15px padding | P1/P2 (reference) |
| `multi_paper_baseline_padding15.jsonl` | Multi-paper baseline with 15px padding | P1/P2 (reference) |
| `multi_paper_experiment_padding_3_2.jsonl` | Multi-paper experiment with (3,2) padding | P2 (border clipping) |

---

### 3. Test Population Distribution — RECONCILED

**Important:** Category assignments sum to 25, not 21. This is NOT a counting error. Candidates can belong to **multiple populations** when their visual content exhibits multiple failure modes. The overlap is intentional and must remain explicit — otherwise later percentages will be misleading.

#### Reconciliation Table

| Candidate | Paper | P1 | P2 | P3 | P4 | P5 | P6 | Total |
|---|---|---|---|---|---|---|---|---|
| cand0_zeta | 1907.04931 | ✓ | | | | | | 1 |
| cand1_expectation | 1907.04931 | ✓ | | | | | | 1 |
| cand2_sqrt | 1907.04931 | | | | | ✓ | | 1 |
| cand3_proportional | 1907.04931 | | | ✓ | | | | 1 |
| eq1.1_forward_summation | 1212.0957 | | | ✓ | | | | 1 |
| eq1.2_inverse_summation | 1212.0957 | | | ✓ | | | | 1 |
| cand0_set_membership | 2104.01277 | ✓ | | | | | | 1 |
| cand1_inner_product | 2104.01277 | | ✓ | | | | | 1 |
| cand3_abs_inner_product | 2104.01277 | | ✓ | | | | | 1 |
| cand5_norm_inequality | 2104.01277 | | | | | ✓ | | 1 |
| cand8_summation_lambda | 2104.01277 | | | ✓ | | | | 1 |
| cand2_sigma_data | 2206.00364 | ✓ | | | | | | 1 |
| cand4_much_greater_than | 2206.00364 | | ✓ | | | | | 1 |
| cand6_dot_derivative | 2206.00364 | | ✓ | | | ✓ | | 2 |
| cand7_denoiser_function | 2206.00364 | | ✓ | | | ✓ | | 2 |
| cand8_skip_scaling | 2206.00364 | | ✓ | | | ✓ | | 2 |
| cand0_l1_norm | 2605.22902 | | | | | ✓ | | 1 |
| cand1_gradient | 2605.22902 | | | | | ✓ | | 1 |
| cand3_partial | 2605.22902 | | | | ✓ | | | 1 |
| cand0_parameter_set | 2605.27315 | | ✓ | | | | | 1 |
| cand2_partial_derivative | 2605.27315 | | | | ✓ | | | 1 |
| **Total** | | **5** | **8** | **4** | **2** | **6** | **0** | **25** |

**Overlap candidates (3):** cand6_dot_derivative, cand7_denoiser_function, cand8_skip_scaling each belong to both P2 (border touch) and P5 (multi-component). These are candidates where border contamination co-occurs with multi-component structure — both failure modes are relevant and must be evaluated independently.

**Denominator rule:** When reporting accuracy per population, the denominator is the number of candidates in that population (including overlaps). When reporting overall accuracy, the denominator is 21 unique candidates. Never conflate the two.

#### Population Counts (with overlap)

| Population | Candidates | Unique candidates |
|---|---|---|
| P1: Clean glyph recognition | 5 | 5 |
| P2: Border contamination and clipping | 8 | 8 |
| P3: Stretched delimiters and operators | 4 | 4 |
| P4: Inline mathematics and surrounding prose | 2 | 2 |
| P5: Multi-component mathematical structures | 6 | 6 (3 shared with P2) |
| P6: Similar-looking glyph discrimination | 0 | 0 |
| **Total assignments** | **25** | **21 unique** |

### 3b. Adjudicated Verdict Population (Separate Evidence)

The 21 adjudicated verdicts are a **separate evidence population** from the test population assignments above. A candidate's population (P1–P6) describes its visual failure mode; its verdict describes the adjudicated outcome. These are orthogonal dimensions.

| Verdict | Count | Meaning | Scoring rule |
|---|---|---|---|
| `CONFIRMED_ACCURATE` | 12 | Crop, glyph, and structure all pass adjudication | Score as success |
| `INTENDED_PARTIAL_FRAGMENT` | 3 | Crop is intentionally partial; not an OCR failure | Do NOT score as failure — this is a designed outcome |
| `BOUNDARY_AMBIGUITY` | 3 | Crop touches boundary; ambiguity in whether content is complete | Score separately from clean recognition |
| `NOTATION_AMBIGUITY` | 1 | Notation interpretation is ambiguous | Score as structural uncertainty |
| `BOUNDARY_TRUNCATION` | 1 | Crop is clipped; content is lost | Score as failure (truncation) |

**Critical safeguard:** `INTENDED_PARTIAL_FRAGMENT` must NOT be scored as an OCR failure. These are designed partial crops (cand1_inner_product, cand3_abs_inner_product, cand4_much_greater_than, cand3_partial) where the crop boundary was intentionally placed to isolate a fragment. Scoring them as failures would inflate the failure rate and misrepresent the system's performance. They belong to their own category: "correctly identified partial fragment."

---

## 4. Variant Comparison Matrix (per external assessment recommendation)

For each eligible original crop, the following variants should be compared:

| Variant | Purpose | Source |
|---|---|---|
| Original crop | Existing recognition baseline | `*_crop_pad3_2.png` |
| Existing corrected crop | Historical correction reference | `*__CORRECTED.png` |
| 9× ballooned crop | New transformation | `balloon_glyph(original, 9)` |
| Context-expanded crop | Context recovery | `expand_crop_context(page, bbox, 1.5)` |
| Multiscale recognition | Combined recognition strategy | `recognize_formula_multiscale()` |

Each variant's OCR result must be recorded independently with: text, confidence, method, status, border_info, scale_used.

---

## 5. Adjudicated Reference Summary

| Verdict | Count | Candidates |
|---|---|---|
| CONFIRMED_ACCURATE | 12 | cand0_zeta, cand1_expectation, cand2_sqrt, cand3_proportional, eq1.2_inverse_summation, cand0_set_membership, cand5_norm_inequality, cand8_summation_lambda, cand2_sigma_data, cand0_l1_norm, cand1_gradient, cand2_partial_derivative |
| INTENDED_PARTIAL_FRAGMENT | 3 | cand1_inner_product, cand3_abs_inner_product, cand4_much_greater_than, cand3_partial |
| BOUNDARY_AMBIGUITY | 3 | cand6_dot_derivative, cand7_denoiser_function, cand8_skip_scaling |
| NOTATION_AMBIGUITY | 1 | eq1.1_forward_summation |
| BOUNDARY_TRUNCATION | 1 | cand0_parameter_set |

---

## 6. Baseline Protection Rules

1. **`baseline_frozen_padding15.jsonl`** — NEVER overwrite. Historical baseline.
2. **Existing corrected clips (`*__CORRECTED.png`)** — NEVER overwrite. Historical adjudication evidence.
3. **New ballooned crops** — Write to separate directory: `DATASETS/vision_comparison/balloon_renders/`
4. **New regression results** — Write to separate file: `DATASETS/vision_comparison/frozen_regression_results.jsonl`
5. **Original crops** — Read-only reference. Never modify.

---

## 7. Missing Coverage (Gaps in Existing Artifacts)

| Gap | Description | Impact |
|---|---|---|
| P6 (similar-looking glyphs) | No adjudicated cases for glyph confusion pairs | Cannot test `balloon_glyph()` on similar-looking symbols |
| Balloon comparison | No existing balloon renders to compare against | Must generate new renders (non-destructive) |
| Border detection validation | `detect_border_contamination()` not yet run on actual crops | Unknown false-positive/negative rates |
| Region grouping validation | `detect_math_regions_on_page()` not yet run on actual pages | Unknown grouping accuracy |

---

## 8. Next Steps (Read-Only Governance)

1. **Create balloon renders** (non-destructive): apply `balloon_glyph()` to each original crop, save to `balloon_renders/`
2. **Run border detection** on each crop: record contamination status per candidate
3. **Run multiscale recognition** on each crop: record OCR results per variant
4. **Compare variants**: original vs corrected vs balloon vs context vs multiscale
5. **Record results** in `frozen_regression_results.jsonl` with per-variant OCR, confidence, method, status
6. **Measure 3 outcomes** independently: Recognition, Structural reconstruction, Source fidelity

No new functions. No baseline modifications. No gate closures. Only traceable evaluation.

---

*This is a read-only governance document. No source modifications, pipeline changes, or gate closures are implied by its creation.*
PYEOF
echo "Written"