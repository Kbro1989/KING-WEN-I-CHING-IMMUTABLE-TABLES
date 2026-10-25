# Visual Review Audit Log — 21 Candidates

**Date:** 2026-10-24  
**Reviewer:** Antigravity Autonomous Math Reviewer (Machine-Checked Visual Inspection)  
**Audit Basis:** Rendered 288 DPI PDF Crops vs. Declared Mathematical References  
**Status:** Provisional Benchmark Ground-Truth Audit  

---

## 1. Audit Summary Across Independent Axes

| Evaluation Axis | Pass Count | Non-Pass Count | Pass Rate (%) | Criteria |
| :--- | :---: | :---: | :---: | :--- |
| **Visual Glyph Fidelity** | 19/21 | 2 | 90.5% | Visible symbols, accents, and font glyphs correspond to reference |
| **Mathematical Structure** | 19/21 | 2 | 90.5% | Subscripts, superscripts, bounds, grouping, and operator scope |
| **Crop Boundary Fidelity** | 10/21 | 11 | 47.6% | Matches declared complete or partial/open boundary specification |

---

## 2. Per-Candidate Visual Audit Matrix

| Candidate ID | Declared Reference | Scope / Boundary | Glyph Fidelity | Math Structure | Boundary Fidelity | Overall Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `1907_04931_cand0_zeta` | `\zeta_v^{(\ell+1)}` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `1907_04931_cand1_expectation` | `(\zeta_v^{(\ell+1)})` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `1907_04931_cand2_sqrt` | `(\sqrt{p_e})` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `1907_04931_cand3_proportional` | `\propto \sqrt{p_e}` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `1212_0957_eq1.1_forward_summation` | `b_n = \sum_{k=0}^{n} S(n,k) a_k` | complete (closed) | DISCREPANCY_NOTED | PASS | PASS | `NOTATION_AMBIGUITY` |
| `1212_0957_eq1.2_inverse_summation` | `a_n = \sum_{k=0}^{n} s(n,k) b_k` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `2104_01277_cand0_set_membership` | `(\chi_Q)_{Q \in \mathcal{Q}}` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `2104_01277_cand1_inner_product` | `\langle T \chi_I ,` | partial (closed) | PASS | PASS | BOUNDARY_TOUCH | `INTENDED_PARTIAL_FRAGMENT` |
| `2104_01277_cand3_abs_inner_product` | `\| \langle T \chi_I ,` | partial (closed) | PASS | PASS | BOUNDARY_TOUCH | `INTENDED_PARTIAL_FRAGMENT` |
| `2104_01277_cand5_norm_inequality` | `\leq \Vert  T \Vert  \mu(I)^{\frac{1}{2}}` | partial (closed_at_rel) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `2104_01277_cand8_summation_lambda` | `\cup_{j=1}^{i-1} (\lambda_j + Q)` | partial (closed_at_op) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `2206_00364_cand2_sigma_data` | `\sigma_{\mathrm{data}}` | complete (closed) | PASS | PASS | PASS | `CONFIRMED_ACCURATE` |
| `2206_00364_cand4_much_greater_than` | `\gg \sigma_{\mathrm{data}}` | partial (closed_at_rel) | PASS | PASS | LEAKAGE_NOTED | `INTENDED_PARTIAL_FRAGMENT` |
| `2206_00364_cand6_dot_derivative` | `-\dot{\sigma}(t)` | complete (closed) | PASS | PASS | BOUNDARY_TOUCH | `BOUNDARY_AMBIGUITY` |
| `2206_00364_cand7_denoiser_function` | `D_{\theta}(\mathbf{x} ; \sigma)` | complete (closed) | PASS | PASS | BOUNDARY_TOUCH | `BOUNDARY_AMBIGUITY` |
| `2206_00364_cand8_skip_scaling` | `c_{\mathrm{skip}}(\sigma) \mathbf{x}` | complete (closed) | PASS | PASS | BOUNDARY_TOUCH | `BOUNDARY_AMBIGUITY` |
| `2605_22902_cand0_l1_norm` | `\lambda \Vert  f(x) \Vert _1` | complete (closed) | PASS | PASS | BOUNDARY_TOUCH | `CONFIRMED_ACCURATE` |
| `2605_22902_cand1_gradient` | `\nabla_{h^{(l)}} y` | complete (closed) | PASS | PASS | BOUNDARY_TOUCH | `CONFIRMED_ACCURATE` |
| `2605_22902_cand3_partial` | `\partial h^{(l)}` | complete (closed) | PASS | PARTIAL_CONTEXT | BOUNDARY_TOUCH | `INTENDED_PARTIAL_FRAGMENT` |
| `2605_27315_cand0_parameter_set` | `\{ \rho_k \}_{k=1}^{K}` | complete (closed) | TRUNCATION_NOTED | PASS | BOUNDARY_CLIPPED | `BOUNDARY_TRUNCATION` |
| `2605_27315_cand2_partial_derivative` | `\partial e_{t,k}` | complete (closed) | PASS | PARTIAL_CONTEXT | BOUNDARY_TOUCH | `CONFIRMED_ACCURATE` |

---

## 3. Key Forensic Visual Observations

1. **`2104_01277_cand8_summation_lambda` Operator Identity:** Visually confirmed to be a big union $\bigcup_{j=1}^{i-1} (\lambda_j + \mathbb{Q})$, NOT a summation $\sum$. The legacy candidate ID is misnamed, but the declared reference LaTeX is mathematically correct.
2. **`1212_0957_eq1.1_forward_summation` Stirling Notation:** Source paper visually prints 2D vertical curly braces $\left\{ \begin{matrix} n \\ k \end{matrix} \right\}$ rather than horizontal $S(n,k)$. The PDF text layer uses non-Unicode glyphs (`\x1a`/`\x1b`), explaining why automated text extraction is partial. Explicitly annotated with `literal_notation_match: false` and `mathematical_equivalence: true` to distinguish typographic transcription from mathematical equivalence.
3. **`1212_0957_eq1.2_inverse_summation` Display Limits:** Source paper visually prints display limits $\sum_{k=0}^n$ with lowercase Stirling cycle notation $s(n,k)$.
4. **`2605_27315_cand0_parameter_set` Right BBox Truncation:** Physical crop cuts off the subscript bound digit `1`, leaving only $k=$. The OCR model faithfully read what was in the crop.
5. **Fraction Denominators (`2605_22902_cand3`, `2605_27315_cand2`):** Crops contain the horizontal fraction bar touching the top border, causing OCR overline/fraction hallucinations.
