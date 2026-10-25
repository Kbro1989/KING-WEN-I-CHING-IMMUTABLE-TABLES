# Multi-Paper Vision Generalization Report — Padding (3, 2)

**Date:** 2026-10-24  
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES  
**Evaluator Version:** `v2.0-strict-reference-comparison`  
**Geometry Evaluated:** `padding=(3, 2)` (pad_x=3 pt, pad_y=2 pt)  
**Baseline Comparison:** Prior frozen baseline `padding=(15, 15)`  

---

## 1. Executive Summary & Aggregate Metrics

Across **21 candidates** sampled across **6 distinct arXiv papers** and **10 mathematical structures**:

| Metric | Padding (15, 15) Baseline | Padding (3, 2) Experiment | Delta / Impact |
| :--- | :---: | :---: | :--- |
| **Candidates Attempted** | 21 | 21 | Paired 21-candidate benchmark corpus |
| **Successfully Cropped** | 21/21 (100.0%) | 21/21 (100.0%) | Valid image pixel region extracted |
| **Non-Empty OCR Outputs** | 21/21 (100.0%) | 21/21 (100.0%) | Recognizer returned non-whitespace LaTeX |
| **Formula-Isolation Rate** | 2/21 (9.5%) | 20/21 (95.2%) | +85.7% elimination of prose arrays |
| **Clipping / Truncation Rate** | 6/21 (28.6%) | 7/21 (33.3%) | Tighter crop boundary sensitivity |
| **Semantic Agreement Rate** | 0/21 (0.0%) | 6/21 (28.6%) | +28.6% verified against audited references |

---

## 2. Results Grouped by Paper

| arXiv ID | Domain / Paper Title | Candidates | Cropped | Isolated | Agreement | Key Findings |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `1212.0957` | Generalized Stirling Transform (Combinatorics Benchmark) | 2 | 2/2 | 1/2 (50%) | 0/2 (0%) | Full isolation without prose leakage |
| `1907.04931` | GraphSAINT (Graph Neural Networks) | 4 | 4/4 | 4/4 (100%) | 4/4 (100%) | Full isolation without prose leakage |
| `2104.01277` | Beyond Low-Pass Filters (Adaptive Feature Propagation) | 5 | 5/5 | 5/5 (100%) | 2/5 (40%) | Full isolation without prose leakage |
| `2206.00364` | Diffusion-Based Generative Models (Stochastic Differential) | 5 | 5/5 | 5/5 (100%) | 0/5 (0%) | Full isolation without prose leakage |
| `2605.22902` | Transcoders Trace Visual Grounding (Vision-Language) | 3 | 3/3 | 3/3 (100%) | 0/3 (0%) | Full isolation without prose leakage |
| `2605.27315` | VLM Concreteness Evaluation (Multimodal) | 2 | 2/2 | 2/2 (100%) | 0/2 (0%) | Full isolation without prose leakage |

---

## 3. Results Grouped by Mathematical Structure

| Mathematical Structure | Sample Count | Isolation Rate | Semantic Agreement | Sample Extracted LaTeX |
| :--- | :---: | :---: | :---: | :--- |
| Absolute Value & Inner Product | 1 | 1/1 (100%) | 0/1 (0%) | `\| \langle T \chi_{I} , \|` |
| Composite Functional Operator | 1 | 1/1 (100%) | 0/1 (0%) | `\overline{{D_{\theta} ( \boldsymbol{x} ; \sig` |
| Composite Functional Scaling | 1 | 1/1 (100%) | 0/1 (0%) | `\stackrel{\iota\mathbf{j} , \ \ \alpha=0} {\m` |
| Delimited Parameter Set | 1 | 1/1 (100%) | 0/1 (0%) | `\{\rho_{k} \}_{k=}^{K^{\cdot}}` |
| Differential Dot Operator | 1 | 1/1 (100%) | 0/1 (0%) | `\mathbf{\partial}=-\dot{\sigma} ( t ) \, \mat` |
| Gradient Operator | 1 | 1/1 (100%) | 0/1 (0%) | `\nabla_{h^{( l )}} y \big)` |
| Greek Subscript & Superscript | 1 | 1/1 (100%) | 1/1 (100%) | `\zeta_{v}^{( \ell+1 )}` |
| Greek Subscript Parameter | 1 | 1/1 (100%) | 0/1 (0%) | `\mathbf{\sigma}_{\mathrm{d a t a}} , \mathbf{` |
| Indexed Summation Parameter | 1 | 1/1 (100%) | 0/1 (0%) | `\cup_{j=1}^{i-1} ( \underset{\mathrm{c}} {\la` |
| Inner Product | 1 | 1/1 (100%) | 0/1 (0%) | `\langle T \chi_{I} , \|` |
| Norm & Inequality | 1 | 1/1 (100%) | 1/1 (100%) | `\leq\| T \| \mu( I )^{\frac{1} {2}}` |
| Parenthesized Expectation | 1 | 1/1 (100%) | 1/1 (100%) | `\left( \zeta_{v}^{( \ell+1 )} \right)` |
| Partial Derivative with Dual Subscript | 1 | 1/1 (100%) | 0/1 (0%) | `\overline{{\partial e_{t , k}}}` |
| Partial Differential Operator | 1 | 1/1 (100%) | 0/1 (0%) | `\frac{\partial} {\partial h^{( l )}}` |
| Radical / Square Root | 1 | 1/1 (100%) | 1/1 (100%) | `( \sqrt{p_{e}} )` |
| Relation & Asymptotics | 1 | 1/1 (100%) | 0/1 (0%) | `\gg\sigma_{\mathrm{d a t a}} , \break\cdot\cd` |
| Relation & Proportionality | 1 | 1/1 (100%) | 1/1 (100%) | `\propto\sqrt{p_{e}} .` |
| Subscript & Set Membership | 1 | 1/1 (100%) | 1/1 (100%) | `( \chi_{Q} )_{Q \in{\cal Q}}` |
| Summation with Matrix Braces | 1 | 0/1 (0%) | 0/1 (0%) | `b_{n}=\sum_{k=0}^{n} \biggl\{\begin{matrix} {` |
| Summation with Signed Coefficient | 1 | 1/1 (100%) | 0/1 (0%) | `a_{n}=\overset{n} {\underset{k=0} {\sum}} s \` |
| Tall Norm & Regularization | 1 | 1/1 (100%) | 0/1 (0%) | `\lambda\| f ( x ) \|_{1} , 1` |

---

## 4. Detailed Candidate Records

| Candidate ID | Paper | Page | Source Text | Recognized LaTeX | Shape | Isolated | Agreement | Reference Match |
| :--- | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| `1907_04931_cand0_zeta` | `1907.04931` | 4 | `ζ(ℓ+1)` | `\zeta_{v}^{( \ell+1 )}` | 68x124 | YES | YES | `exact_match` |
| `1907_04931_cand1_expectation` | `1907.04931` | 4 | `ζ(ℓ+1)` | `\left( \zeta_{v}^{( \ell+1 )} \right)` | 68x124 | YES | YES | `exact_match` |
| `1907_04931_cand2_sqrt` | `1907.04931` | 12 | `√pe` | `( \sqrt{p_{e}} )` | 86x94 | YES | YES | `exact_match` |
| `1907_04931_cand3_proportional` | `1907.04931` | 12 | `∝√pe.` | `\propto\sqrt{p_{e}} .` | 85x147 | YES | YES | `exact_match` |
| `1212_0957_eq1.1_forward_summation` | `1212.0957` | 1 | `bn = ∑ S(n,k) ak` | `b_{n}=\sum_{k=0}^{n} \biggl\{\begin{matrix} {n} \\ {k} \\ \end{matrix} \biggr\} a_{k} ,` | 180x356 | NO | NO | `mismatch` |
| `1212_0957_eq1.2_inverse_summation` | `1212.0957` | 1 | `an = ∑ s(n,k) bk` | `a_{n}=\overset{n} {\underset{k=0} {\sum}} s \left( n , k \right) b_{k} .` | 168x376 | YES | NO | `mismatch` |
| `2104_01277_cand0_set_membership` | `2104.01277` | 1 | `(χQ)Q∈Q` | `( \chi_{Q} )_{Q \in{\cal Q}}` | 68x197 | YES | YES | `exact_match` |
| `2104_01277_cand1_inner_product` | `2104.01277` | 2 | `⟨TχI,` | `\langle T \chi_{I} , \|` | 69x139 | YES | NO | `boundary_violation` |
| `2104_01277_cand3_abs_inner_product` | `2104.01277` | 2 | `\|⟨TχI,` | `\| \langle T \chi_{I} , \|` | 69x152 | YES | NO | `boundary_violation` |
| `2104_01277_cand5_norm_inequality` | `2104.01277` | 2 | `≤∥T∥µ(I)` | `\leq\| T \| \mu( I )^{\frac{1} {2}}` | 66x253 | YES | YES | `exact_match` |
| `2104_01277_cand8_summation_lambda` | `2104.01277` | 3 | `j=1(λj+Q)).` | `\cup_{j=1}^{i-1} ( \underset{\mathrm{c}} {\lambda_{j}+\mathbb{Q}} ) ) .` | 92x304 | YES | NO | `mismatch` |
| `2206_00364_cand2_sigma_data` | `2206.00364` | 2 | `σdata,` | `\mathbf{\sigma}_{\mathrm{d a t a}} , \mathbf{\sigma}_{\mathrm{d a t a}}` | 60x106 | YES | NO | `duplicated` |
| `2206_00364_cand4_much_greater_than` | `2206.00364` | 2 | `≫σdata,` | `\gg\sigma_{\mathrm{d a t a}} , \break\cdot\cdot\cdot\cdot` | 62x157 | YES | NO | `extraneous_content` |
| `2206_00364_cand6_dot_derivative` | `2206.00364` | 2 | `−˙σ(t)` | `\mathbf{\partial}=-\dot{\sigma} ( t ) \, \mathbf{\partial}` | 72x144 | YES | NO | `mismatch` |
| `2206_00364_cand7_denoiser_function` | `2206.00364` | 3 | `Dθ(x; σ)` | `\overline{{D_{\theta} ( \boldsymbol{x} ; \sigma)}}=` | 72x196 | YES | NO | `boundary_violation` |
| `2206_00364_cand8_skip_scaling` | `2206.00364` | 3 | `cskip(σ)x` | `\stackrel{\iota\mathbf{j} , \ \ \alpha=0} {\mathbf{\psi}_{\mathrm{s k i p}} ( \sigma) \mathbf{x}}` | 72x188 | YES | NO | `mismatch` |
| `2605_22902_cand0_l1_norm` | `2605.22902` | 2 | `λ∥f(x)∥1,` | `\lambda\| f ( x ) \|_{1} , 1` | 61x193 | YES | NO | `extraneous_content` |
| `2605_22902_cand1_gradient` | `2605.22902` | 3 | `∇h(l)y` | `\nabla_{h^{( l )}} y \big)` | 64x131 | YES | NO | `extraneous_content` |
| `2605_22902_cand3_partial` | `2605.22902` | 3 | `∂h(l)` | `\frac{\partial} {\partial h^{( l )}}` | 47x94 | YES | NO | `mismatch` |
| `2605_27315_cand0_parameter_set` | `2605.27315` | 13 | `{ρk}K` | `\{\rho_{k} \}_{k=}^{K^{\cdot}}` | 72x140 | YES | NO | `mismatch` |
| `2605_27315_cand2_partial_derivative` | `2605.27315` | 14 | `∂et,k` | `\overline{{\partial e_{t , k}}}` | 65x111 | YES | NO | `mismatch` |

---

## 5. Artifact Provenance & Traceability

- **Evaluator Version:** `v2.0-strict-reference-comparison` (enforces mathematical reference equivalence, rejects duplicated tokens and extraneous trailing expressions)
- **Reference Audit Status:** All 21 reference expressions audited against source-paper PDF clips with exact text, boundaries, and provenance (`scripts/evaluate_output_reference.py`)
- **Raw Experiment OCR Inputs (Padding 3, 2, Immutable):** [`DATASETS/vision_comparison/raw_multi_paper_experiment_padding_3_2.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/raw_multi_paper_experiment_padding_3_2.jsonl) (SHA-256: `5c3baac8ca652b8b6f4e9d210c1f6a145dced7a056b81f73375273ee387eb192`)
- **Raw Baseline OCR Inputs (Padding 15, 15, Immutable):** [`DATASETS/vision_comparison/raw_multi_paper_baseline_padding15.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/raw_multi_paper_baseline_padding15.jsonl) (SHA-256: `76eea32ea1729fda6b57a4a21fba5d45e2daa5d107ec2b6f4cd1c992035883b3`)
- **Evaluated Experiment JSONL (Padding 3, 2):** [`DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl) (SHA-256: `f019c67ae50558a5f8456ae228652e0150e603588d1bb08d7204a7bb9259ab5d`)
- **Evaluated Paired Baseline JSONL (Padding 15, 15, 21 candidates):** [`DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl) (SHA-256: `5a72e811f21cbea588b7a9ed672fe5c8892becaea8b5c071c43bb1353ad58944`)
- **Candidate Audit Manifest:** [`DATASETS/vision_comparison/candidate_audit_manifest.json`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/candidate_audit_manifest.json) (SHA-256: `c48802e2883088cf60baed8cbe8a4ce649e39ea8142b4ce49c86ecda890e17f3`)
- **Reference Ground Truth:** [`scripts/evaluate_output_reference.py`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/evaluate_output_reference.py) (SHA-256: `4014ce1fc60f70769ecb61f67375b27f2ed73ad506b089861772c9f7aaf26a7d`)
- **Legacy Frozen Baseline (4 candidates):** [`DATASETS/vision_comparison/baseline_frozen_padding15.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/vision_comparison/baseline_frozen_padding15.jsonl) (SHA-256: `fc3ecdbea30c9abddc2add3e759d9eaab09b5587e6b8f9ac21889fab3ce1ff35`)
- **Provenance Resolution:** `multi_paper_baseline_padding15.jsonl` provides the complete 21-candidate paired baseline run at padding (15, 15), while `baseline_frozen_padding15.jsonl` is the original 4-candidate preliminary run from 1907.04931 preserved for historical audit.
- **Runner Script:** [`scripts/experiments_multi_paper_generalization.py`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/experiments_multi_paper_generalization.py)
