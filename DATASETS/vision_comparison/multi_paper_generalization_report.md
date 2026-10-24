# Multi-Paper Vision Generalization Report — Dual Semantic Metrics & Integrity Audit

**Date:** 2026-10-23  
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES  
**Evaluated Geometry:** `padding=(3, 2)` (pad_x=3 pt, pad_y=2 pt)  
**Paired Baseline:** `padding=(15, 15)` evaluated on identical candidate coordinates and definitions  

---

## 1. 4-Tier Separated Architecture & Dual Semantic Fidelity

To prevent conflating crop execution, coordinate localization, prose contamination, extra recognized tokens, and semantic fidelity, metrics are reported under four distinct verification tiers with dual semantic metrics:

| Tier / Metric | Numerator / Denominator | Rate (%) | Exact Meaning & Verification Criteria |
|:---|:---:|:---:|:---|
| **Tier 1: Crop Execution** | 21/21 | **100.0%** | PDF rendering and image decoding generated valid pixel regions (content ratio $\ge 0.01$). |
| **Tier 2: Target Localization** | 17/21 | **81.0%** | Bounding box coordinates genuinely locate the intended formula (not an offset prose paragraph). |
| **Tier 3A: Formula Isolation (All Attempted)** | 17/21 | **81.0%** | Crop is free of adjacent prose text/arrays across the full candidate sample. |
| **Tier 3B: Formula Isolation (Correctly Localized)** | 17/17 | **100.0%** | Given correct localization, asymmetric padding eliminated prose leakage in all 17 cases. |
| **Tier 4A: Target-Span Strict Agreement (Localized)** | 13/17 | **76.5%** | Target mathematical expression recognized with 100% token accuracy; surrounding tokens classified. |
| **Tier 4B: Fragment-Scoped Agreement (Localized)** | 14/17 | **82.4%** | Target-span match against designated crop fragment targets (including expectation operator fragment). |
| **Tier 4C: Full-Crop Exact Match (Localized)** | 7/17 | **41.2%** | Full crop strictly matches ground truth with zero extra mathematical tokens, wrappers, or repetitions. |
| **Tier 4D: Structural Agreement (Localized)** | 17/17 | **100.0%** | Core mathematical operator/structure preserved with documented boundary or print font variations. |
| **Tier 4E: Target-Span Strict Agreement (All Attempted)** | 13/21 | **61.9%** | Target-span exact match rate across the full 21-candidate matrix including localization failures. |
| **Tier 4F: Structural Agreement (All Attempted)** | 17/21 | **81.0%** | Structural match rate across the full 21-candidate matrix including localization failures. |

---

## 2. Separated Quality Counters (Glyph Geometry vs Content Boundaries)

To avoid conflating geometric boundary safety with formula boundary truncation or coordinate misalignment, quality issues are partitioned into four independent counters:

| Quality Counter | Count / Total | Rate (%) | Description & Diagnosis |
|:---|:---:|:---:|:---|
| **Glyph Clipping** | 0/21 | **0.0%** | Zero lost tall delimiters, radical bars, summation limits, or ascenders/descenders from crop geometry. |
| **Formula-Boundary Truncation** | 2/21 | **9.5%** | Formula split across column/line break; candidate bbox cut off right delimiter at comma (`2104_cand1`, `cand3`). |
| **Boundary Omission** | 1/21 | **4.8%** | Target component situated outside candidate bbox; outer expectation operator $\mathbb{E}$ omitted (`1907_cand1`). |
| **Target Localization Failure** | 4/21 | **19.0%** | Coordinate bbox or page index enclosed prose text/table headers rather than target formula. |

---

## 3. Paired Baseline Classification Ledger (`padding=15` vs `padding=(3, 2)`)

Both conditions were evaluated across identical candidate IDs, bounding boxes, and pages using the same classification rules:

- **Baseline `padding=(15, 15)` Isolation:** 2/21 (9.5%) — 19 out of 21 crops suffered multi-line prose contamination.
  *(Note: baseline isolation is 2/21 (9.5%) rather than legacy 1/21 (4.8%) because `1212_0957_eq1.1` is correctly recognized as a legitimate `matrix_environment` with zero prose words).*
- **Evaluated `padding=(3, 2)` Isolation:** 17/21 (81.0%) — an increase of **+15 candidates (+71.4 percentage points)**.
- **On Correctly Localized Formulas:** `padding=(3, 2)` achieved **17/17 (100.0%)** isolation.

| Candidate ID | Paper | Page | Target Expression | Baseline (pad=15) Output | Baseline Class | Tight (pad=3,2) Output | Tight Class | Isolation Delta |
|:---|:---:|:---:|:---|:---|:---:|:---|:---:|:---:|
| `1907_04931_cand0_zeta` | `1907.04931` | 4 | `ζ(ℓ+1)` | `\begin{array} {l} {\mathrm{a g ~ s ...` | `prose_array` | `\zeta_{v}^{( \ell+1 )}...` | `isolated_formula` | +1 (PROMOTED) |
| `1907_04931_cand1_expectation` | `1907.04931` | 4 | `ζ(ℓ+1)` | `\stackrel{s \ a n \ u n b i a s e d...` | `prose_array` | `\left( \zeta_{v}^{( \ell+1 )} \righ...` | `isolated_formula` | +1 (PROMOTED) |
| `1907_04931_cand2_sqrt` | `1907.04931` | 12 | `√pe` | `\begin{aligned} {} & {{} \mathrm{e ...` | `prose_array` | `( \sqrt{p_{e}} )...` | `isolated_formula` | +1 (PROMOTED) |
| `1907_04931_cand3_proportional` | `1907.04931` | 12 | `∝√pe.` | `\begin{array} {l} {{\sf\zeta}_{e} \...` | `prose_array` | `\propto\sqrt{p_{e}} ....` | `isolated_formula` | +1 (PROMOTED) |
| `1212_0957_eq1.1_forward_summation` | `1212.0957` | 1 | `bn = ∑ S(n,k) ak` | `b_{n}=\underset{k=0} {\overset{n} {...` | `matrix_environment` | `b_{n}=\sum_{k=0}^{n} \biggl\{\begin...` | `matrix_environment` | PARITY |
| `1212_0957_eq1.2_inverse_summation` | `1212.0957` | 1 | `an = ∑ s(n,k) bk` | `\begin{aligned} {} & {{} \mathrm{i ...` | `prose_array` | `a_{n}=\overset{n} {\underset{k=0} {...` | `isolated_formula` | +1 (PROMOTED) |
| `2104_01277_cand0_set_membership` | `2104.01277` | 1 | `(χQ)Q∈Q` | `\begin{array} {l} {\mathrm{i z a t ...` | `prose_array` | `( \chi_{Q} )_{Q \in{\cal Q}}...` | `isolated_formula` | +1 (PROMOTED) |
| `2104_01277_cand1_inner_product` | `2104.01277` | 2 | `⟨TχI,` | `{\begin{array} {l} {\mathrm{~ i t h...` | `prose_array` | `\langle T \chi_{I} , \|...` | `isolated_formula` | +1 (PROMOTED) |
| `2104_01277_cand3_abs_inner_product` | `2104.01277` | 2 | `|⟨TχI,` | `{\begin{matrix} {\mathrm{z a t i o ...` | `prose_text` | `\| \langle T \chi_{I} , \|...` | `isolated_formula` | +1 (PROMOTED) |
| `2104_01277_cand5_norm_inequality` | `2104.01277` | 2 | `≤∥T∥µ(I)` | `\begin{array} {l} {\mathrm{p l i e ...` | `prose_array` | `\leq\\| T \\| \mu( I )^{\frac{1} {2}}...` | `isolated_formula` | +1 (PROMOTED) |
| `2104_01277_cand8_summation_lambda` | `2104.01277` | 3 | `j=1(λj+Q)).` | `\begin{array} {l} {\mathrm{~ J l ~ ...` | `prose_array` | `\begin{array} {l} {\mathrm{~ J l ~ ...` | `prose_array` | PARITY |
| `2206_00364_cand2_sigma_data` | `2206.00364` | 2 | `σdata,` | `\begin{array} {l} {\mathrm{i o n ~ ...` | `prose_array` | `\mathbf{\sigma}_{\mathrm{d a t a}} ...` | `isolated_formula` | +1 (PROMOTED) |
| `2206_00364_cand4_much_greater_than` | `2206.00364` | 2 | `≫σdata,` | `\begin{array} {l} {\mathrm{s t r i ...` | `prose_array` | `\gg\sigma_{\mathrm{d a t a}} , \bre...` | `isolated_formula` | +1 (PROMOTED) |
| `2206_00364_cand6_dot_derivative` | `2206.00364` | 2 | `−˙σ(t)` | `\begin{aligned} {} & {{} \texttt{o ...` | `prose_array` | `\smile_{\mathrm{d e s i r e d ~ d i...` | `prose_text` | PARITY |
| `2206_00364_cand7_denoiser_function` | `2206.00364` | 3 | `Dθ(x;` | `\begin{aligned} {} & {{}} & {} & {}...` | `prose_array` | `\mathrm{\ n e d u l e} \qquad\qquad...` | `prose_text` | PARITY |
| `2206_00364_cand8_skip_scaling` | `2206.00364` | 3 | `cskip(σ)x` | `\begin{aligned} {} & {{} \mathrm{s ...` | `prose_array` | `\frac{\mathrm{S c a n i n g}} {\mat...` | `prose_text` | PARITY |
| `2605_22902_cand0_l1_norm` | `2605.22902` | 2 | `λ∥f(x)∥1,` | `\begin{array} {r} {\mathrm{T h e ~ ...` | `prose_array` | `\lambda\\| f ( x ) \\|_{1} , 1...` | `isolated_formula` | +1 (PROMOTED) |
| `2605_22902_cand1_gradient` | `2605.22902` | 3 | `∇h(l)y` | `\begin{array} {l} {\mathrm{i n o n ...` | `prose_array` | `\nabla_{h^{( l )}} y \big)...` | `isolated_formula` | +1 (PROMOTED) |
| `2605_22902_cand3_partial` | `2605.22902` | 3 | `∂h(l)` | `\begin{array} {l} {\mathrm{a y e r ...` | `prose_array` | `\frac{\partial} {\partial h^{( l )}...` | `isolated_formula` | +1 (PROMOTED) |
| `2605_27315_cand0_parameter_set` | `2605.27315` | 13 | `{ρk}K` | `\begin{array} {l} {\mathrm{o r o c ...` | `prose_array` | `\{\rho_{k} \}_{k=}^{K^{\cdot}}...` | `isolated_formula` | +1 (PROMOTED) |
| `2605_27315_cand2_partial_derivative` | `2605.27315` | 14 | `∂et,k` | `\frac{\mathbf{x}^{\prime}+\alpha( \...` | `isolated_formula` | `\overline{{\partial e_{t , k}}}...` | `isolated_formula` | PARITY |

---

## 4. Localization Failures (The 4 Discrepancies Reconciled)

The 4 unisolated / disagreeing records failed target localization because candidate manifest coordinates had in-page bounding box offsets into prose text, not because of crop geometry failure:

| Candidate ID | Paper | Listed Page | Actual Formula Location | Crop Contents Transcribed by OCR | Root Cause Diagnosis |
|:---|:---:|:---:|:---:|:---|:---|
| `2104_01277_cand8_summation_lambda` | 2104.01277 | 3 | Page 3, (418, 404, 488, 423) | `\begin{array} {l} {\mathrm{~ J l ~ \tau~ l o c u s e s ~ o n}} ...` | BBox offset on Page 3: candidate bbox (200, 180, 275, 195) captured prose text ('focuses on Haar wavelets'); actual formula is at y=406..421. |
| `2206_00364_cand6_dot_derivative` | 2206.00364 | 2 | Page 2, (250, 629, 280, 643) | `\smile_{\mathrm{d e s i r e d ~ d i s t r i}}` | BBox offset on Page 2: primary formula is in Eq (1) line (y=630..642); candidate bbox (430, 430, 475, 445) captured body prose ('desired distri'). Also appears in derivation on p33. |
| `2206_00364_cand7_denoiser_function` | 2206.00364 | 3 | Page 3, (107, 121, 150, 135) | `\mathrm{\ n e d u l e} \qquad\qquad\sigma` | BBox offset on Page 3: primary formula is in Table 1 caption (y=122..134); candidate bbox (120, 200, 165, 213) captured Table 1 header ('schedule'). Also appears on p38 Eq (227). |
| `2206_00364_cand8_skip_scaling` | 2206.00364 | 3 | Page 3, (157, 121, 198, 135) | `\frac{\mathrm{S c a n i n g}} {\mathrm{N e t w o r k ...}}` | BBox offset on Page 3: primary formula is in Table 1 caption (y=122..134); candidate bbox (100, 225, 160, 238) captured Table 1 header ('Scaning Network'). Also appears on p38. |

---

## 5. Candidate-by-Candidate Semantic Audit & Extra-Token Classification

Audit of all 21 candidates comparing target-span strict match, fragment-scoped match, crop-exact match, and structural agreement with explicit extra-token accounting:

| Candidate ID | Ground-Truth Target | Fragment Target | OCR Output (pad=3,2) | Localized | Strict (Span) | Fragment | Crop Exact | Structural | Extra Tokens | Analysis & Notes |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `1907_04931_cand0_zeta` | `\zeta_{v}^{(\ell+1)}` | `\zeta_{v}^{(\ell+1)}` | `\zeta_{v}^{( \ell+1 )}` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Exact visual match to PDF print glyphs including subscript v. Zero prose. |
| `1907_04931_cand1_expectation` | `\mathbb{E}\left(\zeta_{v}^{(\ell+1)}\right)` | `\left(\zeta_{v}^{(\ell+1)}\right)` | `\left( \zeta_{v}^{( \ell+1 )} \right)` | YES | **FAIL** | PASS | FAIL | **PASS** | `extra_parens` | Crop contains parenthesized variable \left(\zeta_v^{(\ell+1)}\right); outer expectation operator E was outside candidate bbox. |
| `1907_04931_cand2_sqrt` | `\sqrt{p_e}` | `\sqrt{p_e}` | `( \sqrt{p_{e}} )` | YES | **PASS** | PASS | FAIL | **PASS** | `extra_parens` | Square root radical with subscript pe intact; outer parentheses captured from PDF formula (\sqrt{p_e})^2. |
| `1907_04931_cand3_proportional` | `\propto \sqrt{p_e}` | `\propto \sqrt{p_e}` | `\propto\sqrt{p_{e}} .` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Proportionality relation and radical preserved without clipping. Trailing sentence period. |
| `1212_0957_eq1.1_forward_summation` | `b_n = \sum_{k=0}^n \left\{ \begin{matrix} n \\ k \end{matrix} \right\} a_k` | `b_n = \sum_{k=0}^n \left\{ \begin{matrix} n \\ k \end{matrix} \right\} a_k` | `b_{n}=\sum_{k=0}^{n} \biggl\{\begin{matrix} {n} \\ {k} \\ \end{matrix} \biggr\} a_{k} ,` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Legitimate 2x1 mathematical matrix inside curly braces representing Stirling number of second kind {n atop k}. Trailing sentence comma. |
| `1212_0957_eq1.2_inverse_summation` | `a_n = \sum_{k=0}^n s(n,k) b_k` | `a_n = \sum_{k=0}^n s(n,k) b_k` | `a_{n}=\overset{n} {\underset{k=0} {\sum}} s \left( n , k \right) b_{k} .` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Exact inverse Stirling sum a_n = sum_{k=0}^n s(n,k) b_k. Trailing sentence period. |
| `2104_01277_cand0_set_membership` | `(\chi_Q)_{Q \in \mathcal{Q}}` | `(\chi_Q)_{Q \in \mathcal{Q}}` | `( \chi_{Q} )_{Q \in{\cal Q}}` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Characteristic function set membership (\chi_Q)_{Q \in \mathcal{Q}} exact. Zero prose. |
| `2104_01277_cand1_inner_product` | `\langle T\chi_I, \chi_J \rangle` | `\langle T\chi_I, \chi_J \rangle` | `\langle T \chi_{I} , \|` | YES | **FAIL** | FAIL | FAIL | **PASS** | `boundary_truncated_tokens` | Candidate line was split after comma in PDF column; recognized as \langle T\chi_I, |. Core operator preserved, but right bracket truncated at crop edge. |
| `2104_01277_cand3_abs_inner_product` | `\|\langle T\chi_I, \chi_J \rangle\|` | `\|\langle T\chi_I, \chi_J \rangle\|` | `\| \langle T \chi_{I} , \|` | YES | **FAIL** | FAIL | FAIL | **PASS** | `boundary_truncated_tokens` | Candidate line split after comma; recognized as | \langle T \chi_I , |. Right side truncated at crop edge. |
| `2104_01277_cand5_norm_inequality` | `\leq \\|T\\| \mu(I)^{1/2}` | `\leq \\|T\\| \mu(I)^{1/2}` | `\leq\\| T \\| \mu( I )^{\frac{1} {2}}` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Inequality, tall double-bar norm ||T||, and fraction exponent intact. |
| `2104_01277_cand8_summation_lambda` | `\sum_{j=1}^n (\lambda_j + Q)` | `\sum_{j=1}^n (\lambda_j + Q)` | `\begin{array} {l} {\mathrm{~ J l ~ \tau~ l o c u s e s ~ o n}} \\ {\mathrm{~ H a a r ~ w a v e l e t s . ~ I ~}} \\ \end{array}` | NO | **FAIL** | FAIL | FAIL | **FAIL** | `localization_failure_prose` | Localization failure: BBox captured adjacent prose text ("focuses on Haar wavelets"). Target formula was not in crop. |
| `2206_00364_cand2_sigma_data` | `\sigma_{\mathrm{data}}` | `\sigma_{\mathrm{data}}` | `\mathbf{\sigma}_{\mathrm{d a t a}} , \mathbf{\sigma}_{\mathrm{d a t a}}` | YES | **PASS** | PASS | FAIL | **PASS** | `doubled_token` | Noise schedule parameter sigma_data recognized; OCR doubled the expression from subpixel font repetition. |
| `2206_00364_cand4_much_greater_than` | `\gg \sigma_{\mathrm{data}}` | `\gg \sigma_{\mathrm{data}}` | `\gg\sigma_{\mathrm{d a t a}} , \break\cdot\cdot\cdot\cdot` | YES | **PASS** | PASS | FAIL | **PASS** | `trailing_math_dots` | Asymptotic relation >> sigma_data recognized; trailing punctuation and math dots captured from sentence. |
| `2206_00364_cand6_dot_derivative` | `-\dot{\sigma}(t)` | `-\dot{\sigma}(t)` | `\smile_{\mathrm{d e s i r e d ~ d i s t r i}}` | NO | **FAIL** | FAIL | FAIL | **FAIL** | `localization_failure_prose` | Localization failure: In-page vertical BBox offset on Page 2: candidate bbox (430, 430, 475, 445) captured body prose ("desired distri"); primary formula -\dot{\sigma}(t) is at y=630..642. (Formula also recurs in derivation on p33). |
| `2206_00364_cand7_denoiser_function` | `D_\theta(x; \sigma)` | `D_\theta(x; \sigma)` | `\mathrm{\ n e d u l e} \qquad\qquad\sigma` | NO | **FAIL** | FAIL | FAIL | **FAIL** | `localization_failure_prose` | Localization failure: In-page vertical BBox offset on Page 3: candidate bbox (120, 200, 165, 213) captured Table 1 header text ("schedule"); primary formula D_\theta(x; \sigma) is in Table 1 caption at y=122..134. (Formula also recurs on p38 Eq 227). |
| `2206_00364_cand8_skip_scaling` | `c_{\mathrm{skip}}(\sigma) x` | `c_{\mathrm{skip}}(\sigma) x` | `\frac{\mathrm{S c a n i n g}} {\mathrm{N e t w o r k ~ a n d ~ p r e}}` | NO | **FAIL** | FAIL | FAIL | **FAIL** | `localization_failure_prose` | Localization failure: In-page vertical BBox offset on Page 3: candidate bbox (100, 225, 160, 238) captured Table 1 header text ("Scaning Network"); primary formula c_{\mathrm{skip}}(\sigma)x is in Table 1 caption at y=122..134. (Formula also recurs on p38). |
| `2605_22902_cand0_l1_norm` | `\lambda \\|f(x)\\|_1` | `\lambda \\|f(x)\\|_1` | `\lambda\\| f ( x ) \\|_{1} , 1` | YES | **PASS** | PASS | FAIL | **PASS** | `none` | L1 regularization lambda ||f(x)||_1 recognized; trailing comma and character fragment captured as ", 1". |
| `2605_22902_cand1_gradient` | `\nabla_{h^{(l)}} y` | `\nabla_{h^{(l)}} y` | `\nabla_{h^{( l )}} y \big)` | YES | **PASS** | PASS | FAIL | **PASS** | `trailing_closing_delimiter` | Gradient nabla_{h^(l)} y recognized; closing parenthesis from enclosing expression captured as \big). |
| `2605_22902_cand3_partial` | `\frac{\partial}{\partial h^{(l)}}` | `\frac{\partial}{\partial h^{(l)}}` | `\frac{\partial} {\partial h^{( l )}}` | YES | **PASS** | PASS | PASS | **PASS** | `none` | Differential fraction \frac{\partial}{\partial h^{(l)}} exact. |
| `2605_27315_cand0_parameter_set` | `\{\rho_k\}_{k=1}^K` | `\{\rho_k\}_{k=1}^K` | `\{\rho_{k} \}_{k=}^{K^{\cdot}}` | YES | **FAIL** | FAIL | FAIL | **PASS** | `trailing_math_dots` | Lower index lower limit incomplete (k=) and print font dot near K transcribed as K^\cdot. Delimiters and indexed element preserved. |
| `2605_27315_cand2_partial_derivative` | `\partial e_{t,k}` | `\partial e_{t,k}` | `\overline{{\partial e_{t , k}}}` | YES | **PASS** | PASS | FAIL | **PASS** | `overline_wrapper` | Partial derivative \partial e_{t,k} recognized; overlying fraction bar from integrand rendered as \overline{...}. |

---

## 6. Machine-Checkable Acceptance Criteria Verification

The audit script (`scripts/audit_multi_paper_experiment.py`) programmatically enforces and passes six machine-checkable acceptance criteria:

1. **Identical Candidate Manifest & Provenance:** Baseline and experiment contain the exact same 21 candidate IDs with identical bounding box coordinates, pages, and source paper SHA-256 bindings. *(VERIFIED: 21/21)*
2. **Uniform Evaluation Parity:** Both ledgers use identical programmatic classification rules (`classify_latex`) and the same evaluator version. *(VERIFIED: 21/21)*
3. **Independent Metric Computation:** Strict, structural, crop-exact, and fragment-scoped metrics are computed independently from raw data, without inference shortcuts. *(VERIFIED: 21/21)*
4. **Explicit Extra-Token Accounting:** Every strict PASS candidate is audited for missing target tokens and unaccounted-for mathematical additions via `extra_tokens_detected`. *(VERIFIED: 13 localized strict matches audited)*
5. **Separated Quality Counters:** Glyph clipping (0/21), formula-boundary truncation (2/21), boundary omission (1/21), and localization failure (4/21) are tracked as independent counters. *(VERIFIED: Counters reconcile)*
6. **Direct Traceability & Metric Reconciliation:** All summary figures derive directly from candidate records without rounding drift or manual footnote adjustments. *(VERIFIED: 100% arithmetic reconciliation)*

---

## 7. Artifact Traceability

- **Audited Experiment Dataset:** [`DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl)
- **Classified Baseline Ledger:** [`DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl)
- **Audit Script:** [`scripts/audit_multi_paper_experiment.py`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_multi_paper_experiment.py)