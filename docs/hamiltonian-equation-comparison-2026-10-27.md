**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) and F-12 (one-sided clamp) are now VALIDATED. The scale mismatch (pq_dot 0-1 vs L 0-6) is the root cause (F-10); the clamp is the sole information-loss mechanism (F-12). Candidate C remains unimplemented and unvalidated. The abs() sign-discarding question is a SEPARATE design question from F-10/F-12. See `docs/qsmc1-m3-mathematical-validation-f10.md` and `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

# Hamiltonian Equation Comparison Document

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Purpose:** Compare the current Hamiltonian-like expression against candidate formulations derived from the ternary paired differential specification. No production code changes. Establish mathematical contract before any fix.

---

## 1. Current Expression

**Source:** `emotional_engine.py`, function `_hamiltonian_energy()`

```python
def _hamiltonian_energy(resolved_vector, expanded_vector, line_balance):
    pq = [float(v) for v in resolved_vector]          # momentum (5-axis, 0-1)
    qdot = [resolved_vector[i] - expanded_vector[i]   # velocity (5-axis, 0-1)
            for i in range(5)]
    pq_dot = sum(pq[i] * qdot[i] for i in range(5))  # bilinear form (0-1 scale)

    lb = line_balance
    yin = lb.get('yin_count', 0)
    yang = lb.get('yang_count', 0)
    yao = lb.get('yao_count', 0)
    changing = lb.get('changing_count', 0)
    old_yang = lb.get('old_yang_count', 0)
    old_yin = lb.get('old_yin_count', 0)
    old_yao = lb.get('old_yao_count', 0)
    stable_yao = lb.get('stable_yao_count', 0)
    stable_yin = lb.get('stable_yin_count', 0)

    dy = (yang - yin) / 6.0          # 0-1 scale (yang-yin over 6 lines)
    yao_dy = yao / 6.0 - 0.5          # 0-1 scale (yao over 6 lines, centered)
    old_dy = (old_yang - old_yin) / 6.0  # 0-1 scale
    stable_dy = (stable_yao - stable_yin) / 6.0  # 0-1 scale

    # Current: uses abs() — discards sign
    L = abs(dy) + abs(yao_dy) + abs(old_dy) + abs(stable_dy)  # 0-4 scale (sum of 4 abs)

    raw = pq_dot - L                    # 0-1 minus 0-4 → always negative
    return _clamp(raw, 0.0, 1.0)        # floors to 0.0 for all states
```

### Variables

| Variable | Symbol | Domain | Range | Units | Source |
|----------|--------|--------|-------|-------|--------|
| `resolved_vector` | p (momentum) | 5-axis emotional vector | [0,1] per axis | dimensionless | resolved state from shotgun_expand |
| `expanded_vector` | q (position) | 5-axis emotional vector | [0,1] per axis | dimensionless | expanded state from shotgun_expand |
| `q̇` | q̇ (velocity) | resolved - expanded | [-1,1] per axis | dimensionless | computed |
| `pq_dot` | p·q̇ | scalar | [-1,1] (but observed [0, 0.04]) | dimensionless | computed |
| `dy` | yang - yin | signed differential | [-1,1] | dimensionless | line_balance |
| `yao_dy` | yao - 3 | signed differential | [-0.5, 0.5] | dimensionless | line_balance |
| `old_dy` | old_yang - old_yin | signed differential | [-1,1] | dimensionless | line_balance |
| `stable_dy` | stable_yao - stable_yin | signed differential | [-1,1] | dimensionless | line_balance |
| `L` | Lagrangian (current) | sum of abs differentials | [0,4] | dimensionless | computed |
| `raw` | p·q̇ - L | scalar | [-4, 1] (observed [-2.49, -0.49]) | dimensionless | computed |
| `clamped` | energy | scalar | [0,1] | dimensionless | _clamp(raw, 0, 1) |

### Observed behavior

- **All 64 hexagrams (phase 0):** raw ranges [-2.494478, -0.490560], all clamped to 0.0
- **All 8 phases of Hex 1:** raw ranges [-2.490457, -0.000000], all clamped to 0.0
- **Total:** 512/512 states produce energy = 0.0

### Key issues

1. **Scale mismatch:** pq_dot is 0-1 scale, L is 0-4 scale. Subtraction always negative.
2. **abs() discards sign:** The ternary paired differential spec requires signed differentials. Current code uses `abs()` on all four.
3. **Clamp floors to zero:** `_clamp(raw, 0.0, 1.0)` makes all negative values 0.0. Since all raw values are negative, energy is always 0.0.
4. **No mass matrix:** Standard Hamiltonian uses M (mass matrix) in kinetic term. Current code uses simple dot product.
5. **Naming ambiguity:** The form `p·q̇ - L` is the canonical Hamiltonian construction (Legendre transform), but it may not be a valid Hamiltonian if the variables are not canonical coordinates/momenta.

---

## 2. Governing Specification

**Source:** `docs/ternary-paired-differential-math-correction-2026-08-02.md`

### Ternary paired differentials (signed)

| Differential | Definition | Sign meaning |
|-------------|-----------|-------------|
| `dy` | yang - yin | + = more yang (IS NOT), - = more yin (IS) |
| `yao_dy` | yao - 3.0 | + = more yao (MAYBE), - = less yao |
| `old_dy` | old_yang - old_yin | + = more old yang, - = more old yin |
| `stable_dy` | stable_yao - stable_yin | + = more stable yao, - = more stable yin |
| `changing_dy` | changing - (6 - changing) | + = more changing, - = less changing |

### Hamiltonian specification from spec

The spec defines:
- `q̇^i = q_resolved^i - q_expanded^i` (per-axis velocity, NOT scalar sum)
- Lagrangian from paired differentials (signed, not absolute)
- Neighbor continuity uses vector deltas (not magnitude deltas)

### Boolean gating rule

"Boolean only at final decision gates, forbidden in math/scoring/phase-rate layers."

The current code uses `abs()` which is a form of magnitude gating — it removes sign information from the differential layer. This violates the spec's requirement that differentials remain signed.

---

## 3. Candidate Equations

### Candidate A: Current (as-is)

```
H = clamp(pq_dot - (|dy| + |yao_dy| + |old_dy| + |stable_dy|), 0, 1)
```

- **Scale:** pq_dot ∈ [0,0.04], L ∈ [0,4] → raw ∈ [-4, 0.04]
- **Result:** Always 0.0 (all raw negative)
- **Sign:** abs() discards sign
- **Status:** Broken (universal clamping)

### Candidate B: Signed differentials, same scale (remove abs)

```
H = clamp(pq_dot - (dy + yao_dy + old_dy + stable_dy), 0, 1)
```

- **Scale:** pq_dot ∈ [0,0.04], L ∈ [-2, 2] (signed sum) → raw ∈ [-2, 2.04]
- **Result:** May produce positive values when differentials are negative
- **Sign:** Preserves sign information
- **Concern:** L can be negative (when more yin than yang), which means H = pq_dot - (negative) = pq_dot + |L|, potentially inflating energy
- **Status:** Needs testing

### Candidate C: Signed differentials, normalized scale

```
H = clamp(pq_dot - (dy + yao_dy + old_dy + stable_dy) / 4.0, 0, 1)
```

- **Scale:** pq_dot ∈ [0,0.04], L ∈ [-0.5, 0.5] (normalized) → raw ∈ [-0.5, 1.04]
- **Result:** More likely to produce positive values
- **Sign:** Preserves sign information
- **Concern:** The /4.0 factor is a rescaling, not mathematically justified by the spec
- **Status:** Needs testing

### Candidate D: Signed differentials, average (mean) instead of sum

```
H = clamp(pq_dot - (dy + yao_dy + old_dy + stable_dy) / 4.0, 0, 1)
```

- Same as Candidate C (average of 4 differentials)
- **Status:** Same as C

### Candidate E: Per-axis velocity (from spec), signed L

```
H = clamp(Σ(p_i × q̇_i) - (dy + yao_dy + old_dy + stable_dy) / 4.0, 0, 1)
```

- **Scale:** pq_dot ∈ [0,0.04], L ∈ [-0.5, 0.5]
- **Sign:** Preserves sign information
- **Velocity:** Per-axis (as spec requires), not scalar
- **Concern:** Same as C but with explicit per-axis velocity notation
- **Status:** Needs testing

### Candidate F: Hamiltonian as energy (T + V, not T - V)

```
H = clamp(pq_dot + (|dy| + |yao_dy| + |old_dy| + |stable_dy|) / 4.0, 0, 1)
```

- **Scale:** pq_dot ∈ [0,0.04], L ∈ [0,1] → raw ∈ [0, 1.04]
- **Result:** Always positive (sum of two positive terms)
- **Sign:** abs() on differentials (magnitude only)
- **Concern:** This is H = T + V (Hamiltonian), not L = T - V (Lagrangian). But it uses abs() which discards sign.
- **Status:** Needs testing

---

## 4. Worked Reference Cases

### Case 1: All yang (Hex 1, phase 0)

Line balance: yin=0, yang=6, yao=0, changing=0, old_yang=6, old_yin=0, old_yao=0, stable_yao=0, stable_yin=0

| Differential | Value | abs() |
|-------------|-------|-------|
| dy | (6-0)/6 = 1.0 | 1.0 |
| yao_dy | 0/6 - 0.5 = -0.5 | 0.5 |
| old_dy | (6-0)/6 = 1.0 | 1.0 |
| stable_dy | (0-0)/6 = 0.0 | 0.0 |

- L (abs sum) = 1.0 + 0.5 + 1.0 + 0.0 = 2.5
- L (signed sum) = 1.0 + (-0.5) + 1.0 + 0.0 = 1.5
- L (signed avg) = 1.5 / 4 = 0.375
- pq_dot = 0.009543

| Candidate | Raw | Clamped |
|-----------|-----|---------|
| A (current) | 0.009543 - 2.5 = -2.490457 | 0.0 |
| B (signed sum) | 0.009543 - 1.5 = -1.490457 | 0.0 |
| C (signed avg) | 0.009543 - 0.375 = -0.365457 | 0.0 |
| F (T+V) | 0.009543 + 0.625 = 0.634543 | 0.634543 |

### Case 2: All yin (Hex 2, phase 0)

Line balance: yin=6, yang=0, yao=0, changing=0, old_yang=0, old_yin=6, old_yao=0, stable_yao=0, stable_yin=6

| Differential | Value | abs() |
|-------------|-------|-------|
| dy | (0-6)/6 = -1.0 | 1.0 |
| yao_dy | 0/6 - 0.5 = -0.5 | 0.5 |
| old_dy | (0-6)/6 = -1.0 | 1.0 |
| stable_dy | (0-6)/6 = -1.0 | 1.0 |

- L (abs sum) = 1.0 + 0.5 + 1.0 + 1.0 = 3.5
- L (signed sum) = -1.0 + (-0.5) + (-1.0) + (-1.0) = -3.5
- L (signed avg) = -3.5 / 4 = -0.875
- pq_dot = 0.005522

| Candidate | Raw | Clamped |
|-----------|-----|---------|
| A (current) | 0.005522 - 3.5 = -3.494478 | 0.0 |
| B (signed sum) | 0.005522 - (-3.5) = 3.505522 | 1.0 |
| C (signed avg) | 0.005522 - (-0.875) = 0.880522 | 0.880522 |
| F (T+V) | 0.005522 + 0.875 = 0.880522 | 0.880522 |

**Key observation:** Candidate B produces 1.0 (saturated) for all-yin. Candidate C produces 0.88 (meaningful). Candidate F produces same as C.

### Case 3: Balanced (Hex 3, phase 0)

Line balance: yin=4, yang=2, yao=0, changing=0, old_yang=2, old_yin=4, old_yao=0, stable_yao=0, stable_yin=4

| Differential | Value | abs() |
|-------------|-------|-------|
| dy | (2-4)/6 = -0.333 | 0.333 |
| yao_dy | 0/6 - 0.5 = -0.5 | 0.5 |
| old_dy | (2-4)/6 = -0.333 | 0.333 |
| stable_dy | (0-4)/6 = -0.667 | 0.667 |

- L (abs sum) = 0.333 + 0.5 + 0.333 + 0.667 = 1.833
- L (signed sum) = -0.333 + (-0.5) + (-0.333) + (-0.667) = -1.833
- L (signed avg) = -1.833 / 4 = -0.458
- pq_dot = 0.007332

| Candidate | Raw | Clamped |
|-----------|-----|---------|
| A (current) | 0.007332 - 1.833 = -1.826 | 0.0 |
| B (signed sum) | 0.007332 - (-1.833) = 1.840 | 1.0 |
| C (signed avg) | 0.007332 - (-0.458) = 0.465 | 0.465 |
| F (T+V) | 0.007332 + 0.458 = 0.465 | 0.465 |

### Case 4: Mixed (Hex 5, phase 0)

Line balance: yin=2, yang=4, yao=0, changing=0, old_yang=4, old_yin=2, old_yao=0, stable_yao=0, stable_yin=2

| Differential | Value | abs() |
|-------------|-------|-------|
| dy | (4-2)/6 = 0.333 | 0.333 |
| yao_dy | 0/6 - 0.5 = -0.5 | 0.5 |
| old_dy | (4-2)/6 = 0.333 | 0.333 |
| stable_dy | (0-2)/6 = -0.333 | 0.333 |

- L (abs sum) = 0.333 + 0.5 + 0.333 + 0.333 = 1.5
- L (signed sum) = 0.333 + (-0.5) + 0.333 + (-0.333) = -0.167
- L (signed avg) = -0.167 / 4 = -0.042
- pq_dot = 0.010009

| Candidate | Raw | Clamped |
|-----------|-----|---------|
| A (current) | 0.010009 - 1.5 = -1.490 | 0.0 |
| B (signed sum) | 0.010009 - (-0.167) = 0.177 | 0.177 |
| C (signed avg) | 0.010009 - (-0.042) = 0.052 | 0.052 |
| F (T+V) | 0.010009 + 0.042 = 0.052 | 0.052 |

---

## 5. Analysis

### Sign sensitivity

| Candidate | All-yang (Hex 1) | All-yin (Hex 2) | Balanced (Hex 3) | Mixed (Hex 5) |
|-----------|-----------------|-----------------|------------------|---------------|
| A (abs, sum) | 0.0 | 0.0 | 0.0 | 0.0 |
| B (signed, sum) | 0.0 | 1.0 | 1.0 | 0.177 |
| C (signed, avg) | 0.0 | 0.881 | 0.465 | 0.052 |
| F (T+V, abs) | 0.635 | 0.881 | 0.465 | 0.052 |

### Key observations

1. **Candidate A** (current) produces 0.0 for all states — no variation, no information.

2. **Candidate B** (signed sum) saturates at 1.0 for all-yin and balanced — loses differentiation between those states.

3. **Candidate C** (signed average) produces meaningful variation across all four cases: 0.0, 0.881, 0.465, 0.052. No saturation.

4. **Candidate F** (T+V with abs) produces the same as C for all-yin and balanced, but different for all-yang (0.635 vs 0.0). This is because T+V always adds, while T-L can be negative.

5. **Candidate C and F agree** for all-yin, balanced, and mixed, but disagree for all-yang. The difference is whether all-yang (pure yang, no yin) should have high or low energy.

### Sign symmetry question

The ternary paired differential spec says:
- `dy = yang - yin` (signed)
- `old_dy = old_yang - old_yin` (signed)
- `stable_dy = stable_yao - stable_yin` (signed)

For all-yang: dy=+1.0, old_dy=+1.0, stable_dy=0.0 → signed sum = +1.5 → L = +1.5 → raw = pq_dot - 1.5 = negative → clamped to 0.0

For all-yin: dy=-1.0, old_dy=-1.0, stable_dy=-1.0 → signed sum = -3.0 → L = -3.0 → raw = pq_dot - (-3.0) = pq_dot + 3.0 → clamped to 1.0

This means:
- All-yang → 0.0 energy (low)
- All-yin → 1.0 energy (high, saturated)

This is **asymmetric**: all-yang and all-yin produce very different energies. Whether this is intended depends on the semantic definition of the Hamiltonian.

### Semantic question

Is the Hamiltonian supposed to be:
- **Symmetric** (all-yang and all-yin should produce the same energy)?
- **Asymmetric** (all-yin should have higher energy than all-yang)?

The ternary model (Yin=IS, Yang=IS NOT, Yao=MAYBE) suggests:
- All-yang = all IS NOT = maximum negation = high "not-ness"
- All-yin = all IS = maximum affirmation = high "is-ness"

Whether "is-ness" should have higher energy than "not-ness" is a domain question, not a mathematical one.

---

## 6. Acceptance Criteria (from review)

| Gate | Required Evidence | Status |
|------|-------------------|--------|
| Mathematical contract | Explicit definitions of every variable, sign convention, domain, scale | ⚠️ Partial — variables defined, sign convention needs domain decision |
| Signed differential fidelity | Tests demonstrating positive/negative/zero differentials retain distinctions | ❌ Not yet — candidate equations need testing |
| Numerical validity | No unexplained scale mismatch, saturation, or universal clamping | ❌ Candidate B saturates; C does not |
| Identity preservation | Results traceable to each of 64 canonical hexagrams | ❌ Not yet tested |
| Phase coverage | All 8 phases tested for each hexagram (512 cases) | ❌ Not yet tested |
| Independent verification | Hand-calculated reference cases and independent implementation | ⚠️ Partial — 4 hand-calculated cases above |
| Downstream effect | Wavefunction/rotation/scale vary when they should | ❌ Not yet tested |
| Reproducibility | Deterministic results with recorded inputs, formula version, expected outputs | ❌ Not yet recorded |

---

---

## 8. Read-Only Audit Findings (2026-10-29)

### 8.1 Audit Scope

Read-only audit of the Hamiltonian energy subsystem. No source code was modified. All findings are based on evidence supplied during the audit session.

### 8.2 Confirmed Root Cause: Scale Mismatch

The Hamiltonian energy is zero-by-construction for all 512 resolved states. The root cause is a scale mismatch between two terms in the formula, not a calculation error.

**Exact intermediate values (Hexagram 1, phase 0, all-yang, emotional_input=86):**

| Term | Value | Scale |
|------|-------|-------|
| `resolved_vec` | [0.1712, 0.1167, 0.2021, 0.5831, 0.6402] | Vector (0-1 per axis) |
| `expanded_vec` | [0.1712, 0.1167, 0.1521, 0.5731, 0.6502] | Vector (0-1 per axis) |
| `q_dot` | [0.0, 0.0, 0.05, 0.01, -0.01] | Vector difference (0-1) |
| `momentum` | [0.1712, 0.1167, 0.2021, 0.5831, 0.6402] | max(0, resolved) |
| `pq_dot` | 0.00953 | Vector-scale (0-1) |
| `dy` (yang - yin) | 6.0 | Line-count (0-6) |
| `yao_dy` (yao - 3.0) | -3.0 | Line-count (0-6) |
| `changing_dy` (changing - (6-changing)) | -6.0 | Line-count (0-6) |
| `lagrangian` | 5.1 | Line-count-scale (0-6 × 0.5/0.3/0.2) |
| `pq_dot - lagrangian` | -5.09047 | Incommensurable |
| `_clamp(-5.09047)` | 0.0 | Floors negative to 0.0 |

**Across all 64 expanded hexagrams:**

| Metric | Range |
|--------|-------|
| `pq_dot` | 0.0053 – 0.0126 |
| `lagrangian` | 2.1 – 5.1 |
| Gap (min_lag - max_pq) | 2.087 |
| Paired comparisons where pq_dot < lagrangian | 64/64 |
| Result | 0.0 for all 512 states |

**Root cause**: `pq_dot` operates on vector-scale (~0.01), `lagrangian` operates on line-count-scale (~2-5). These terms are incommensurable. The gap is ≥ 2.09 in every case, so `pq_dot - lagrangian` is always negative, and `_clamp(value, 0.0, 1.0)` floors it to 0.0.

This is **zero-by-construction**, not a calculation error. The formula's two terms cannot be meaningfully subtracted without a normalization or bridge term.

### 8.3 Diagnostic Retention Issue

`HAMILTONIAN_PAIRED_DIFFERENTIALS` is a module-level global dictionary:

```python
HAMILTONIAN_PAIRED_DIFFERENTIALS: Dict[str, Any] = {
    "old_yao_count": 0.0, "old_dy": 0.0, "stable_dy": 0.0,
    "old_yang_count": 0.0, "old_yin_count": 0.0,
    "stable_yao_count": 0.0, "stable_yin_count": 0.0,
}
```

Mutated during `_hamiltonian_energy()` computation (lines 446-448). Overwritten on each of the 64 calls during `shotgun_expand()`. Retains only the **last hexagram processed** (hex 64, phase 0).

**Consumers:**

| File | Line | Usage | Risk |
|------|------|-------|------|
| `emotional_engine.py` | 396 | Definition | — |
| `emotional_engine.py` | 446-448 | Mutated during computation | Side effect |
| `scripts/verify_restored_state.py` | 19 | `print("audit dict:", ...)` | Read-only, print only |

**Assessment**: Only one external consumer, print-only. No production code reads this global. The stale-state risk is informational, not functional. Retaining only the last record loses earlier diagnostic values but does not explain why each individual energy is zero.

### 8.4 Three Properties to Preserve (Audit Disposition)

1. **Numerical output**: All-zero over the audited input set (512 resolved states, emotional_input=86, request_text="delta").
2. **Numerical explanation**: Incompatible scales (pq_dot ~0.01 vs lagrangian ~2-5) followed by lower-bound clamping. Confirmed, not hypothesized.
3. **Diagnostic retention**: Module-level dictionary overwritten across calls; one print-only consumer; no production code reads it.

### 8.5 What This Audit Does NOT Establish

- The intended formula, units, or valid range of the Hamiltonian energy
- Whether pq_dot and lagrangian are meant to share a common scale
- Whether the sign asymmetry (all-yang=0.0, all-yin=1.0) is intended
- Whether the clamp is a physical constraint, normalization, or safety bound
- Whether zero is a valid energy, a floor, or an error

These are **model-definition questions**, not implementation questions. They must be answered before any formula change.

### 8.6 Disposition

| Area | Status |
|------|--------|
| Math-to-King-Wen adapter | Integration-tested (reported): 991 equations, 5 criteria, 0 errors |
| Vector identity & phase coverage | Passing (reported): 512 unique identities, within-hexagram duplicates only |
| Hamiltonian energy | Numerically unresolved: scale mismatch diagnosed, formula/units/range unspecified |
| Hamiltonian global dictionary | Retention limitation documented: last-write-wins, print-only consumer |
| Gate 2 | OPEN: no representation choice, Path A/B, or invalid-input policy authorized |

**No source code was modified during this audit.** The Hamiltonian formula remains unresolved. Gate 2 remains open. The next step is to establish the mathematical contract (units, scale, sign convention, valid range, intended meaning) before any implementation change.

**Do not change the production formula yet.** The candidate equations show that:

1. Removing `abs()` (Candidate B) eliminates universal clamping but introduces saturation
2. Normalizing scale (Candidate C) eliminates both clamping and saturation
3. The sign asymmetry (all-yang=0.0, all-yin=1.0) is a **domain question**, not a math question

The next step is to:
1. Establish the semantic definition of the Hamiltonian (what should "energy" mean?)
2. Determine if sign symmetry is required
3. Test all 64×8 states for each candidate
4. Verify downstream effects (wavefunction, rotation, scale)
5. Compare with an independently computed implementation

Only after these gates are passed should the production formula change.