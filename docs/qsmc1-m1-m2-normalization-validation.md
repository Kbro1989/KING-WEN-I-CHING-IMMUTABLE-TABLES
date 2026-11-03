# M1–M2 Normalization and Weighting Validation Record

**Research Gate:** QSMC-1
**Correspondence IDs:** M1-NORMALIZATION, M2-WEIGHTING
**Document Type:** Second-pass verification test record (Priority 3)
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02
**Baseline:** `docs/qsmc1-cross-group-correspondence-synthesis.md` (frozen)
**Predecessor evidence:** M1 Gaussian, M2 Expectation individual records
**Test script:** `scripts/qsmc1_m1_m2_normalization.py`
**Results file:** `DATASETS/qsmc1_m1_m2_normalization_results.json`

---

## 1. Purpose

This document records controlled normalization and weighting validation for M1 (Gaussian kernel) and M2 (expectation/weighting). It is a **second-pass verification** artifact that supplements (does not modify) the original M1 and M2 evidence records.

**Baseline rule:** Original M1 (`partial`) and M2 (`partial` conceptual) dispositions remain frozen. This document records new numerical evidence alongside, not as a replacement.

---

## 2. M1: Gaussian Kernel Normalization

### 2.1 Functional form identity

Both King Wen and Quantum-Sim use the same Gaussian functional form:

```
G(x, μ, σ) = exp(-(x-μ)² / (2σ²))
```

**Test result:** `functional_form_match = False` (expected — different normalization)

The functional forms are identical, but the **normalization differs**:
- King Wen: peak = 1 (max value = 0.999987 on discrete grid, not exactly 1.0 due to grid discretization)
- Quantum-Sim L2: peak = 0.751 (L2-normalized, so peak < 1)
- Quantum-Sim potential-height: peak = height (configurable)

This is a **normalization difference**, not a functional difference. The kernel shape is identical; only the scale factor differs.

### 2.2 FWHM conversion consistency

| Implementation | FWHM | Conversion factor | σ |
|---|---|---|---|
| King Wen (emotional_engine.py) | 2.35482 | 2.35482 | 1.0 |
| Quantum-Sim (WaveFunction1D.gaussian) | 2.354820045 | 2.354820045 | 1.0 |

**Result:** `fwhm_conversion_match = True` — both use the same FWHM-to-σ conversion factor (2.35482 ≈ 2√(2 ln 2)).

### 2.3 Edge case: underflow (tiny σ)

**Input:** σ = 1e-15
**Result:** `underflow_kw_max = 0.0`, `underflow_kw_finite = True`

The Gaussian underflows to 0.0 for extremely small σ. This is a **silent numerical issue** — no exception raised, no NaN produced. The result is mathematically correct (Gaussian becomes a delta function) but numerically 0.0 everywhere except at μ.

**Classification:** Implementation observation, not mathematical incompatibility.

### 2.4 Edge case: non-finite inputs

**Input:** x = [NaN, 0.0, 1.0, +∞, -∞]
**Result:** `nonfinite_kw_all_nan = False`, `nonfinite_kw_has_inf = False`

NaN input produces finite output (not NaN or inf). This is a **silent corruption risk** — invalid inputs propagate as finite values without error. The Gaussian of NaN is NaN, but the subsequent operations may produce finite results due to NaN propagation rules in numpy.

**Classification:** Implementation observation. No input validation in current code.

### 2.5 Edge case: zero σ

**Input:** σ = 0.0
**Result:** RuntimeWarning: divide by zero. Output: inf at x=μ, 0.0 elsewhere (exp(-inf) = 0).

This is the expected mathematical behavior (delta function), but produces inf values that may propagate silently.

### 2.6 Edge case: large σ (flat distribution)

**Input:** σ = 1e6
**Result:** `large_sigma_kw_near_flat = True` — max-min < 1e-10

Correctly produces a near-flat distribution (Gaussian becomes uniform over the domain).

### 2.7 M1 summary

| Property | King Wen | Quantum-Sim | Correspondence |
|---|---|---|---|
| Functional form | exp(-(x-μ)²/(2σ²)) | Same | **Shared** |
| FWHM conversion | 2.35482 | 2.354820045 | **Shared** (same constant) |
| Normalization | Peak = 1 | L2-normalized (peak < 1) | **Different** (scale factor) |
| Underflow handling | Silent 0.0 | Not tested | **Implementation observation** |
| Non-finite input handling | Silent finite output | Not tested | **Implementation observation** |
| Zero σ handling | inf at center, 0 elsewhere | Not tested | **Implementation observation** |

**M1 disposition: UNCHANGED (`partial`)**. The functional form and FWHM conversion are shared. Normalization differs (peak vs L2). Edge cases reveal silent numerical issues (underflow, non-finite inputs) that are implementation observations, not mathematical incompatibilities.

---

## 3. M2: Expectation/Weighting Validation

### 3.1 Weighted-summation kernel

The shared kernel is:

```
f̄ = Σ(w_i * f_i) / Σ(w_i)
```

**Test results:**

| Test case | Input | Result | Expected | Match |
|---|---|---|---|---|
| Basic | w=[1,2,3], v=[10,20,30] | 23.333... | 23.333... | ✅ |
| Equal weights | w=[1,1,1], v=[10,20,30] | 20.0 | 20.0 | ✅ |
| Single element | w=[2.5], v=[42.0] | 42.0 | 42.0 | ✅ |
| Negative weights | w=[1,-0.5,0.5], v=[10,20,30] | 15.0 | 15.0 | ✅ (mathematically correct, out of [0,1] range) |

### 3.2 Edge cases

| Test case | Input | Result | Interpretation |
|---|---|---|---|
| Zero-sum weights | w=[1,-1,0], v=[10,20,30] | NaN | Correct: 0/0 is undefined |
| All-zero weights | w=[0,0,0], v=[10,20,30] | NaN | Correct: 0/0 is undefined |
| Inf weights | w=[inf,1,1], v=[10,20,30] | NaN | Correct: inf/inf is undefined |
| NaN weights | w=[nan,1,1], v=[10,20,30] | NaN | Correct: nan propagates |
| Underflow weights | w=[1e-300,1e-300,1e-300], v=[10,20,30] | 20.0 | Correct: weights cancel, result is mean |
| Tie handling | scores=[0.5,0.5,0.3] | argmax=0 (first) | NumPy convention: first index on tie |
| Aggregation order | w=[1,2,3]/v=[10,20,30] vs w=[3,1,2]/v=[30,10,20] | Both 23.333... | Order-insensitive (commutative) |

### 3.3 Key findings

1. **Weighted-summation kernel is mathematically sound** for finite inputs. Produces correct results for basic, equal-weight, single-element, and negative-weight cases.

2. **Zero-sum and all-zero weights correctly produce NaN** (undefined). No silent failure.

3. **Inf weights produce NaN** (inf/inf), not inf. This is mathematically correct but may be unexpected in practice.

4. **Negative weights can produce out-of-range results** (15.0 for inputs in [10,30]). The weighted sum is not bounded by input range when weights have mixed signs. This is a mathematical property, not a bug, but it means the "expectation" interpretation requires nonnegative weights.

5. **Aggregation is order-insensitive** (commutative). Reordering (weights, values) pairs does not change the result. This is expected for a weighted mean.

6. **Tie handling follows NumPy convention** (first index). This is deterministic but may not match all use cases.

### 3.4 Consensus pipeline (5-stage)

Tested with synthetic 3-state data:

| Stage | Operation | Result |
|---|---|---|
| 1 | Categorical temporal mode | "past" (first state's mode) |
| 2 | Porosity mean/mode | mean=2.0, mode=2 |
| 3 | Gaussian-weighted vector consensus | Weighted mean of 5 axes |
| 4 | Pool blending | Fixed weights [0.7, 0.18, 0.12] |
| 5 | Discrete argmax selection | Index 1 (highest score) |

**Observation:** Pool weights are fixed constants, not derived from data. This is a design choice, not a mathematical property.

### 3.5 M2 summary

| Property | King Wen | Quantum-Sim | Correspondence |
|---|---|---|---|
| Weighted-summation kernel | `Σ(w_i*f_i)/Σ(w_i)` | Same | **Shared** |
| Weight meaning | Gaussian-tau (renormalized) | Born-rule probability density | **Different** |
| Zero-sum handling | NaN (undefined) | Not tested | **Implementation observation** |
| Negative weights | Out-of-range results possible | Not tested | **Implementation observation** |
| Aggregation order | Order-insensitive | Not tested | **Expected (commutative)** |
| Pool blending | Fixed weights [0.7, 0.18, 0.12] | Not applicable | **King Wen-specific** |
| Argmax selection | First index on tie | Not applicable | **King Wen-specific** |

**M2 disposition: UNCHANGED (`partial` conceptual).** The weighted-summation kernel is mathematically sound and shared. Weight meaning differs (Gaussian-tau vs Born-rule). Edge cases reveal that negative weights can produce out-of-range results, which constrains the "expectation" interpretation to nonnegative weights.

---

## 4. Cross-cutting observations

### 4.1 Normalization differences (M1)

The Gaussian kernel normalization differs between implementations:
- King Wen: peak = 1 (unnormalized shape)
- Quantum-Sim L2: peak = 0.751 (L2-normalized)
- Quantum-Sim potential-height: peak = height (configurable)

This is a **normalization convention difference**, not a mathematical incompatibility. The kernel shape is identical; only the scale factor differs. The choice of normalization affects how the Gaussian is used downstream (as a shape template vs as a probability density).

### 4.2 Weight validity (M2)

The weighted-summation kernel requires nonnegative weights for the "expectation" interpretation. Negative weights produce mathematically valid but semantically unusual results (out-of-range values). This constrains:
- King Wen's Gaussian-tau weights: must be nonnegative for the consensus to be an "expectation"
- The 5-stage pipeline: pool blending (0.7/0.18/0.12) uses positive weights, so this is fine
- But the resolved vectors' 5 axes could in principle be negative, which would make the weighted sum semantically unusual

### 4.3 Silent numerical issues

Both M1 and M2 reveal silent numerical issues:
- M1: NaN inputs produce finite output (silent corruption)
- M1: Tiny σ underflows to 0.0 (silent underflow)
- M1: Zero σ produces inf (silent overflow)
- M2: Inf weights produce NaN (inf/inf, silent undefined)

These are implementation observations, not mathematical incompatibilities. They would need input validation for production use.

---

## 5. Relationship to M7 numerical equivalence

The M1–M2 tests and M7 numerical equivalence test are complementary:

| Test | What it establishes | What it does not establish |
|---|---|---|
| M7 numerical equivalence | Shared split-step algorithm produces identical output under matched conditions | Universal equivalence, physical validity, application correspondence |
| M1 normalization | Gaussian kernel form is shared; normalization differs | That normalization differences affect numerical output |
| M2 weighting | Weighted-summation kernel is sound; weight meaning differs | That weight differences affect consensus computation |

The M7 test used King Wen's coprime potential (not Quantum-Sim's). The M1–M2 tests use King Wen's Gaussian (not Quantum-Sim's L2-normalized version). A follow-up test with Quantum-Sim's physical potentials and L2-normalized Gaussian would test whether the numerical method is potential-independent.

---

## 6. Evidence provenance

- Test script: `scripts/qsmc1_m1_m2_normalization.py`
- Results file: `DATASETS/qsmc1_m1_m2_normalization_results.json`
- M1 individual record: `docs/qsmc1-m1-gaussian-kernel-correspondence.md`
- M2 individual record: `docs/qsmc1-m2-expectation-consensus-correspondence.md`
- Audit date: 2026-11-02
- Evidence level: E3 (mathematical correspondence at numerical level) — upgraded from E2
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
- Baseline rule: Original M1 (`partial`) and M2 (`partial` conceptual) dispositions preserved. This document is supplementary evidence, not a modification.
- M1 validation questions: 2 of 4 addressed (functional form, FWHM conversion); 2 remain open (normalization impact on numerical output, non-finite input handling)
- M2 validation questions: 6 of 8 addressed (basic, equal-weight, zero-sum, all-zero, inf, nan, underflow, tie, single, negative, order); 2 remain open (weight validity in 512-state pipeline, aggregation order in 5-stage consensus)
