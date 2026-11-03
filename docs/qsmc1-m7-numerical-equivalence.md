# M7 Controlled Numerical-Equivalence Test Record

**Research Gate:** QSMC-1
**Correspondence ID:** M7-NUMERICAL-EQUIVALENCE
**Document Type:** Second-pass verification test record (Priority 2)
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02
**Baseline:** `docs/qsmc1-cross-group-correspondence-synthesis.md` (frozen)
**Predecessor evidence:** `docs/qsmc1-m7-evolution-propagation-correspondence.md`, `docs/qsmc1-m7-source-provenance.md`
**Test script:** `scripts/qsmc1_m7_numerical_equivalence.py`
**Results file:** `DATASETS/qsmc1_m7_numerical_equivalence_results.json`

---

## 1. Purpose

This document records the controlled numerical-equivalence test between King Wen's inline split-step Fourier implementation and Quantum-Sim's class-based implementation. It is a **second-pass verification** artifact that supplements (does not modify) the original M7 evidence record.

**Baseline rule:** The original M7 disposition (`undetermined`) and its evidence record are frozen. This document records new numerical evidence alongside, not as a replacement.

---

## 2. Test design

### 2.1 Isolation principle

The test isolates the **numerical method** from **application-specific differences**. Both implementations receive identical inputs. No post-processing is applied. Outputs are raw complex arrays.

### 2.2 Controlled inputs

| Parameter | Value | Source |
|---|---|---|
| Grid size (N) | 64 | King Wen's N1 |
| Grid domain | x ∈ [-π, π), periodic | King Wen's linspace |
| Grid spacing (dx) | 2π/64 | Derived |
| Potential (V) | Coprime-frequency sum: `sum(sin(p*x/pi)/p for p in [97,89,83,79,73])` | King Wen's `_kw_pot_1d` |
| Initial wavefunction | `exp(-(x²)/(4*0.5²)) * exp(1j * 1.0 * x)`, normalized | King Wen's psi_init |
| HBAR | 1.0 | King Wen's HBAR |
| MASS | 1.0 | King Wen's MASS |
| DT | 0.02 | King Wen's DT |
| WARMUP_STEPS | 3 | King Wen's WARMUP_STEPS |
| Operators | U_V = exp(-1j*V*DT/(2*HBAR)), U_T = exp(-1j*T_k*DT/HBAR) | Computed identically for both |

### 2.3 Implementations compared

**King Wen (inline, functional):**
```python
psi = psi_init.copy()
for _ in range(steps):
    psi = ifft(fft(psi * U_V) * U_T) * U_V
```

**Quantum-Sim (class-based):**
```python
def step(self, psi):
    psi = psi.copy()
    psi *= self.U_V
    psi_k = fft(psi)
    psi_k *= self.U_T
    psi = ifft(psi_k)
    psi *= self.U_V
    return psi
```

### 2.4 Metrics

| Metric | Formula | Purpose |
|---|---|---|
| Maximum absolute complex-field error | `max(|ψ_KW - ψ_QS|)` | Pointwise worst-case deviation |
| Relative L2 error | `‖ψ_KW - ψ_QS‖₂ / ‖ψ_QS‖₂` | Overall field deviation |
| Norm before propagation | `‖ψ_init‖₂` | Initial state verification |
| Norm after propagation (KW) | `‖ψ_KW‖₂` | Norm preservation (KW) |
| Norm after propagation (QS) | `‖ψ_QS‖₂` | Norm preservation (QS) |
| Norm preservation (KW) | `\|‖ψ_KW‖₂² - ‖ψ_init‖₂²\|` | Unitarity check (KW) |
| Norm preservation (QS) | `\|‖ψ_QS‖₂² - ‖ψ_init‖₂²\|` | Unitarity check (QS) |
| Maximum probability-density difference | `max(|\|ψ_KW\|² - \|ψ_QS\|²\|)` | Born-rule equivalence |
| Relative probability-density difference | `‖P_KW - P_QS‖₂ / ‖P_QS‖₂` | Overall probability deviation |
| Maximum phase difference | `max(|arg(ψ_KW) - arg(ψ_QS)|)` (wrapped) | Phase fidelity |
| Mean phase difference | `mean(|arg(ψ_KW) - arg(ψ_QS)|)` (wrapped) | Average phase fidelity |

### 2.5 Per-step comparison

Metrics computed after **every** step, not just the final step. This detects divergence accumulation.

---

## 3. Results

### 3.1 Per-step metrics

| Step | max_abs_err | rel_l2_err | norm_kw | norm_qs | delta_N_kw | delta_N_qs | max_prob_diff | max_phase_diff |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.00e+00 | 0.00e+00 | 1.0000000000 | 1.0000000000 | 0.00e+00 | 0.00e+00 | 0.00e+00 | 0.00e+00 |
| 1 | 1.39e-16 | 1.50e-16 | 1.0000000000 | 1.0000000000 | 2.22e-16 | 2.22e-16 | 2.22e-16 | 4.28e-13 |
| 2 | 2.78e-16 | 3.36e-16 | 1.0000000000 | 1.0000000000 | 4.44e-16 | 0.00e+00 | 3.33e-16 | 1.48e-12 |
| 3 | 4.48e-16 | 5.59e-16 | 1.0000000000 | 1.0000000000 | 2.22e-16 | 0.00e+00 | 5.55e-16 | 2.79e-12 |

### 3.2 Final verdict

| Metric | Value | Interpretation |
|---|---|---|
| max_abs_complex_err | 4.48e-16 | Machine precision (double-precision floating point) |
| rel_l2_err | 5.59e-16 | Machine precision |
| norm_kw | 1.0000000000 | Norm preserved |
| norm_qs | 1.0000000000 | Norm preserved |
| delta_N_kw | 2.22e-16 | Machine-precision norm preservation |
| delta_N_qs | 0.00e+00 | Machine-precision norm preservation |
| max_prob_diff | 5.55e-16 | Machine precision |
| max_phase_diff | 2.79e-12 | Machine precision (phase wrapping) |

**RESULT: NUMERICALLY IDENTICAL (machine precision)**

Both implementations produce bit-identical output (within floating-point roundoff, ~4.5e-16). Both preserve norm to machine precision. Agreement holds at every step, not just the final step.

### 3.3 Norm preservation analysis

Both implementations preserve norm to machine precision (ΔN ≈ 2.22e-16 for KW, 0.00e+00 for QS). This confirms:

1. The Strang splitting is unitary (as expected mathematically)
2. No corrective renormalization is needed in either implementation
3. The normalization is performed once (before the evolution loop), not after every step

### 3.4 Error accumulation

The error grows linearly with step count (1.39e-16 → 2.78e-16 → 4.48e-16), consistent with floating-point roundoff accumulation. No super-linear growth (which would indicate algorithmic divergence).

---

## 4. Interpretation

### 4.1 What the test establishes

1. **Algorithmic equivalence under tested conditions**: The shared split-step Fourier method produces numerically identical output when given identical inputs, parameters, and grid. The implementation identity is confirmed at the numerical level.

2. **Unitarity**: Both implementations preserve norm to machine precision without corrective renormalization. The Strang splitting is unitary under these conditions.

3. **No divergence accumulation**: Error grows linearly (roundoff only), not super-linearly (algorithmic divergence).

### 4.2 What the test does NOT establish

1. **Universal equivalence**: Only tested with N=64, DT=0.02, HBAR=1.0, MASS=1.0, coprime potential, 3 steps. Different grids, potentials, or parameters may produce different results.

2. **Physical validity**: The test uses King Wen's coprime-frequency potential, not a physical potential. The numerical equivalence of the algorithm does not validate the physical meaningfulness of the potential.

3. **Application-level correspondence**: The test isolates the numerical method. It does not address whether King Wen's pre-warming (3 steps, small grids, avatar animation) and Quantum-Sim's physical evolution (variable steps, large grids, quantum dynamics) represent the same physical process.

4. **M7 disposition upgrade**: The original M7 disposition (`undetermined`) remains unchanged. This numerical evidence strengthens the implementation-level correspondence but does not establish application-level correspondence or physical equivalence.

### 4.3 Relationship to M7 disposition

| Evidence layer | Status | This test's contribution |
|---|---|---|
| Algorithm provenance | ESTABLISHED (source provenance) | Confirmed (identical formula) |
| Formula identity | CONFIRMED (source code comparison) | Confirmed (numerical output) |
| Implementation correspondence | STRENGTHENED (source provenance) | **STRENGTHENED** (numerical identity) |
| Numerical equivalence | NOT YET TESTED | **ESTABLISHED** (machine precision, tested conditions) |
| Physical equivalence | UNDETERMINED | Not addressed (out of scope) |
| Application-level correspondence | PARTIAL CONCEPTUAL | Not addressed (out of scope) |

**M7 disposition remains `undetermined`.** The numerical equivalence test establishes that the shared method behaves identically under tested conditions. It does not establish that the two systems represent the same physical process.

---

## 5. Critical experimental control

The test used **identical inputs** (King Wen's coprime-frequency potential) for both implementations. This isolates the numerical method from potential-construction differences.

**Follow-up test (not yet performed):** Test with Quantum-Sim's physical potentials (harmonic, Gaussian barrier) to determine whether the shared algorithm produces equivalent output under different potential surfaces. This would test whether the numerical method is potential-independent.

---

## 6. Evidence provenance

- Test script: `scripts/qsmc1_m7_numerical_equivalence.py`
- Results file: `DATASETS/qsmc1_m7_numerical_equivalence_results.json`
- Quantum-Sim source: `quantumlab/solvers/split_step_1d.py` (commit c17817f, 2026-06-14)
- King Wen source: `scripts/prewarm_quantum_wavepackets.py` (commit 2548ba170d, 2026-08-29)
- Provenance record: `docs/qsmc1-m7-source-provenance.md`
- Audit date: 2026-11-02
- Evidence level: E3 (mathematical correspondence at numerical level) — upgraded from E2
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
- Baseline rule: Original M7 disposition (`undetermined`) preserved. This document is supplementary evidence, not a modification.
- M7 validation questions: 2 of 5 addressed (provenance + numerical equivalence); 3 remain open (normalization, unitarity, potential construction)
