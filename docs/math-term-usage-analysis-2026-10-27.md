# Math Term Usage Analysis for King Wen Engine

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Purpose:** Study how Hamiltonian, Lagrangian, porosity, Jacobian, and Gaussian are used in standard mathematical practice (from Zotero corpus + arxiv HTML corpus), to determine the best path forward for each failed/mismatched term. Math layers and expansion layers are studied independently.

---

**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) is now VALIDATED. The diagnosis in this document (scale mismatch 0-6 vs 0-1, terms in different units, no mass matrix) is confirmed as the root cause. The clamp (F-12) is the sole information-loss mechanism. See `docs/qsmc1-m3-mathematical-validation-f10.md` and `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

## 1. Hamiltonian

### Standard usage (from arxiv corpus)

**Paper 1505.05770 — "Variational Inference with Normalizing Flows"**

The Hamiltonian is defined as:

```
ℋ(z, ω) = -ℒ(z) - ½ ωᵀ M ω
```

Where:
- `ℒ(z)` = log-likelihood (negative potential energy, since -ℒ is the potential)
- `ω` = momentum (conjugate variable to position z)
- `M` = mass matrix (positive definite, defines kinetic energy metric)
- `ℋ` = Hamiltonian = potential energy + kinetic energy (standard form H = T + V, but here written as -ℒ - ½ωᵀMω because ℒ is log-likelihood, so -ℒ is the negative log-likelihood = "potential")

**Key structural properties:**
1. **Dimensions must match:** ℒ(z) is a scalar (log-likelihood), ½ωᵀMω is a scalar (kinetic energy). Both are in the same units (nats or log-probability).
2. **The kinetic term** ½ωᵀMω is **quadratic in momentum** — it scales as O(||ω||²), not O(||ω||).
3. **The mass matrix M** is positive definite and typically diagonal or block-diagonal. It defines the metric on momentum space.
4. **Hamilton's equations:** ż = ∂ℋ/∂ω = Mω, ω̇ = -∂ℋ/∂z = ∇ℒ(z). The velocity ż is the momentum transformed by the mass matrix.

### Comparison to King Wen's current implementation

| Property | Standard Hamiltonian | King Wen current |
|----------|---------------------|------------------|
| Potential term | -ℒ(z) (scalar, log-likelihood) | L = abs(dy)+abs(yao_dy)+abs(old_dy)+abs(stable_dy) (0-6 scale) |
| Kinetic term | ½ωᵀMω (quadratic, 0-1 scale if ω normalized) | pq_dot = Σ(p_i × q̇_i) (bilinear, 0-1 scale) |
| Dimensions | Both terms in same units (nats) | Terms in different units (0-6 vs 0-1) |
| Mass matrix | M defines metric on momentum | No mass matrix; pq_dot is dot product |
| Clamp | None (Hamiltonian can be any real) | _clamp(raw, 0, 1) floors negatives to 0 |

### Diagnosis

The King Wen "Hamiltonian" is NOT a Hamiltonian in the standard sense. It is:

```
H = pq_dot - L
```

Where:
- `pq_dot` = Σ(p_i × q̇_i) — a bilinear form (inner product of momentum and velocity)
- `L` = sum of 4 absolute differentials — a total variation / L1 norm

This is actually closer to a **Lagrangian** (L = T - V) than a Hamiltonian (H = T + V), and even then the terms are in incompatible units.

### Best path forward

**Option A: Fix the scale mismatch (normalize L to 0-1)**
- Divide L by 4.0 (average of 4 differentials, each 0-1)
- This makes L range 0-1, compatible with pq_dot's 0-1 scale
- But this is a rescaling, not a mathematical justification
- The review correctly notes: "that factor must be justified by the intended equation"

**Option B: Redefine as a proper Lagrangian**
- L = T - V where T = ½ωᵀMω (kinetic) and V = -ℒ(z) (potential)
- Requires defining a mass matrix M and a potential ℒ(z)
- More mathematically sound but requires more design work

**Option C: Use the ternary paired differential spec as-is**
- The spec (`docs/ternary-paired-differential-math-correction-2026-08-02.md`) defines signed differentials: dy, yao_dy, old_dy, stable_dy
- The Lagrangian should use these signed differentials, not their absolute values
- The issue is that `abs()` is used, which discards sign information
- But even with signed values, the scale mismatch remains (0-6 vs 0-1)

**Recommendation:** Option C + scale normalization. The ternary paired differential spec is the governing document. The Lagrangian should use signed differentials (not abs), and the scale should be normalized to be compatible with pq_dot. But this requires:
1. Establishing that the differentials are signed (not magnitude)
2. Establishing that the Lagrangian is the sum (not average) of signed differentials
3. Establishing that pq_dot is the correct kinetic term
4. Testing all 64 hexagrams × 8 phases

**No code change applied.** Design decision required.

---

## 2. Porosity

### Standard usage

"Porosity" does not appear in any of the 245 Zotero corpus papers or the arxiv HTML corpus. It is a domain-specific term in the King Wen system.

In the King Wen system, porosity appears in three contexts:
1. **Injection site porosity** (0-4 integer): semantic topology property of each hexagram's inject site
2. **Kit QWP porosity** (0.15-0.71 float): spatial structure derived from trigram indices
3. **Emotional engine porosity** (0-1 float): line-state balance measure

### Best path forward

The review recommendation is correct: keep the three porosity measurements separate unless the domain specification establishes that they represent the same quantity. Each measures a different aspect:
- Injection site: semantic topology
- Kit QWP: spatial structure
- Emotional engine: line-state balance

If the vortex formula needs normalized porosity, define a named conversion at its interface and retain the original source value.

**No code change applied.** Field contract definitions needed.

---

## 3. Jacobian

### Standard usage (from arxiv corpus)

**Paper 2212.00774 — "Score Jacobian Chaining: Lifting Pretrained 2D Diffusion Models for 3D Generation"**

The Jacobian is used as:

```
J = ∂g/∂x  (partial derivative of a function g with respect to input x)
```

Specifically:
- `J_{g_{j←i}}` = partial Jacobian of function g from modality i to modality j
- Shape: ℝ^(d_x^j × d_c^i) — output dimension × input dimension
- Used for: chaining gradients through multiple modalities, propagating information from one coordinate space to another

**Paper 2605.21059 — "Multimodal LLMs under Pairwise Modalities"**

The Jacobian is used for:
- `G = ∂g_c/∂(z_e^c)^T` — Jacobian of a function g with respect to its input
- Used for: reparameterization, coordinate transformation, gradient flow

### Comparison to King Wen's J-lens

| Property | Standard Jacobian | King Wen J-lens |
|----------|-------------------|-----------------|
| Definition | ∂f/∂x (partial derivatives) | J(a; v) = E[dY/dA] * dA (perturbation vector) |
| Input | Function f and point x | Activation a and perturbation v |
| Output | Matrix of partial derivatives | Vector (perturbation response) |
| Consumer | Gradient-based optimization, coordinate transform | None (verification only) |
| Numerical check | Finite differences | Not implemented |

### Best path forward

The King Wen J-lens is NOT a standard Jacobian. It is a **perturbation response vector** — a measure of how much the state changes when the activation is perturbed. This is closer to a **sensitivity analysis** or **gradient** than a Jacobian matrix.

The review recommendation is correct: define the interface before integration. The J-lens needs:
1. Input activation definition
2. Output state representation
3. Derivative convention (finite differences or analytical)
4. Perturbation vector shape
5. Production consumer

**No code change applied.** Interface specification required.

---

## 4. Gaussian

### Standard usage (from arxiv corpus)

**Paper 1907.05600 — "Generative Modeling by Estimating Gradients of the Data Distribution"**

Gaussian kernels appear in score-based generative modeling:
- The score function ∇_x log p(x) is estimated using Gaussian noise perturbation
- The Gaussian kernel K(x, y) = exp(-||x-y||² / 2σ²) is used for kernel density estimation
- Normalization: ∫ K(x, y) dy = 1 (over the full space)

**Paper 2106.01357 — "Diffusion Schrödinger Bridge"**

Gaussian appears in:
- The transition kernel of diffusion processes: p(x_t | x_0) = N(x_0, tI)
- The Schrödinger bridge problem uses Gaussian reference measures

**Paper 2210.02747 — "Flow Matching for Generative Modeling"**

Gaussian appears in:
- The conditional probability path: p_t(x | x_1) = N(tx_1, (1-t)²σ²)
- The velocity field is derived from the Gaussian conditional

### Comparison to King Wen's Gaussian

| Property | Standard Gaussian | King Wen |
|----------|-------------------|----------|
| Kernel form | K(v1, v2) = exp(-||v1-v2||² / 2σ²) | `_gaussian_kernel(v1, v2)` in emotional_engine.py |
| Normalization | ∫ K = 1 over full space | Not verified (needs test) |
| FWHM | 2σ√(2ln2) ≈ 2.355σ | FWHM=2.5 (parameter, not derived from σ) |
| Used for | Density estimation, smoothing, diffusion | Phase bias weighting, future projection, avatar transitions |
| Identity preservation | Kernel doesn't change identity (weights only) | Not verified (needs test) |

### Best path forward

The King Wen Gaussian is used as a **weighting function** (phase bias), not a probability density. This is a valid use case — Gaussian kernels are commonly used for smoothing and weighting in signal processing.

The review recommendation is correct: validate without changing behavior. Tests needed:
1. Kernel normalization (does it sum to 1 over all pairs?)
2. FWHM interpretation (is 2.5 the right value?)
3. Boundary behavior (phase 0 and phase 7)
4. Identity preservation (does weighting merge hexagram identities?)

**No code change applied.** Validation tests needed.

---

## Summary: Best Path Forward

| Term | Standard Usage | King Wen Status | Recommended Action |
|------|---------------|-----------------|-------------------|
| Hamiltonian | H = T + V, same units, mass matrix | Scale mismatch (0-6 vs 0-1), no mass matrix, abs() discards sign | Redefine using ternary paired differential spec; normalize scale; test all 64×8 |
| Porosity | Domain-specific (not in standard math) | 3 independent computations, no reconciliation | Keep separate; define field contracts; document conversion if needed |
| Jacobian | ∂f/∂x matrix for gradient flow | Perturbation vector, no production consumer | Specify interface before integration; test against finite differences |
| Gaussian | Kernel for density/smoothing/weighting | Functional in 4 locations, unvalidated | Add regression tests; preserve behavior |

### Priority Order (confirmed by review)

1. **Hamiltonian equation review** — establish mathematical contract, compare candidate formulations, define expected outputs
2. **Vortex porosity contract** — zero handling, units, range, saturation (bug fixed, scale decision needed)
3. **Jacobian interface specification** — inputs, outputs, derivative convention, consumer
4. **Gaussian regression suite** — normalization, FWHM, boundaries, identity preservation
5. **Traceability corrections** — T10, test-to-invariant mapping, scope annotations
6. **Cross-pipeline porosity reconciliation** — field contracts, formal relationship or explicit distinct measurement

**No production formula changes applied** (beyond the `or 0.35` fallback fix). All other changes are diagnostic documentation. Design decisions required before any further engine behavior changes.