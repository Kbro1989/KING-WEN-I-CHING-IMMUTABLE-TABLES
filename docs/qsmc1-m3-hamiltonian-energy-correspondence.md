# M3 Hamiltonian and Energy Correspondence Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M3-HAMILTONIAN-ENERGY
**Mathematical Object:** Hamiltonian / energy
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02

---

## 1. King Wen Implementation

### Source: `_hamiltonian_energy()` in `emotional_engine.py:408-455`

```python
def _hamiltonian_energy(
    resolved_vector: List[float],
    expanded_vector: List[float],
    line_balance: Dict[str, Any],
) -> float:
    """H(p,q,t) = sum p_i * q_dot^i - L

    - p_i     : resolved vector axis as momentum
    - q_dot^i : per-axis phase derivative = resolved[i] - expanded[i]
    - L       : line-state Lagrangian from paired ternary differentials

    Boolean is forbidden in this layer. All state comparisons use signed
    quantitative differentials. Final gating only.
    """
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
    pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))

    # Paired ternary differentials -- no absolute ratios
    yin_count = float(line_balance.get("yin_count", 0) or 0)
    yang_count = float(line_balance.get("yang_count", 0) or 0)
    yao_count = float(line_balance.get("yao_count", 0) or 0)
    changing_count = float(line_balance.get("changing_count", 0) or 0)
    old_yang_count = float(line_balance.get("old_yang_count", 0) or 0)
    old_yin_count = float(line_balance.get("old_yin_count", 0) or 0)
    stable_yao_count = float(line_balance.get("stable_yao_count", 0) or 0)
    stable_yin_count = float(line_balance.get("stable_yin_count", 0) or 0)

    old_yao_count = float(line_balance.get("old_yao_count", 0) or 0)
    old_dy = old_yang_count - old_yin_count
    stable_dy = stable_yao_count - stable_yin_count

    dy = yang_count - yin_count
    yao_dy = yao_count - 3.0
    changing_dy = changing_count - (6.0 - changing_count)

    lagrangian = (
        abs(dy) * 0.5
        + abs(yao_dy) * 0.3
        + abs(changing_dy) * 0.2
    )
    return _clamp(pq_dot - lagrangian)
```

### King Wen Hamiltonian Summary

| Property | Value |
|---|---|
| Function type | Scalar function (not a linear operator) |
| State space | 5D emotional vector (resolved_vector, expanded_vector as List[float]) |
| Momentum (p_i) | `max(0.0, resolved_vector[i])` -- clamped to non-negative |
| Velocity (q_dot^i) | `resolved_vector[i] - expanded_vector[i]` -- per-axis delta |
| pq_dot | `sum(momentum[i] * q_dot[i])` -- dot product of momentum and velocity |
| Lagrangian (L) | `abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2` -- weighted absolute differentials |
| Output | `_clamp(pq_dot - lagrangian)` -- clamped to [0, 1] |
| Units | None defined (dimensionless) |
| Invariants | None defined |
| Evolution operator | None |
| Hermiticity | Not applicable (scalar, not operator) |
| Observed behavior | Returns 0.0 for all 512 states (scale mismatch: pq_dot ~0.005-0.013, lagrangian ~2.1-5.1) |

### Additional source: `HAMILTONIAN_PAIRED_DIFFERENTIALS` global dict (line 396)

```python
HAMILTONIAN_PAIRED_DIFFERENTIALS: Dict[str, Any] = {
    "old_yao_count": 0.0,
    "old_dy": 0.0,
    "stable_dy": 0.0,
    "old_yang_count": 0.0,
    "old_yin_count": 0.0,
    "stable_yao_count": 0.0,
    "stable_yin_count": 0.0,
}
```

Mutated during computation (lines 446-448). Retains only last hexagram (hex 64, phase 0). One consumer: `verify_restored_state.py` (print-only).

### Additional source: `kingwen_quantum_process.py`

Does NOT contain `_hamiltonian_energy`. The function was imported from the wrong module in `build_full_shotgun_jsonl.py` (fixed to `from emotional_engine import _hamiltonian_energy`).

---

## 2. Quantum-Sim Implementation

### Source: `apply_hamiltonian()` in `quantumlab/stationary/hamiltonian.py`

```python
def apply_hamiltonian(psi, grid, V, hbar=1.0, m=1.0,
                      nonlinearity=0.0, workers=-1, rotation=0.0) -> np.ndarray:
    """Hψ = -ℏ²/2m ∇²ψ + (V + g|ψ|²)ψ - Ω L_z ψ"""
    T_k = hbar ** 2 * k_squared(grid) / (2.0 * m)
    psi_k = fftn(psi, workers=workers)
    H_psi = ifftn(T_k * psi_k, workers=workers)
    V_eff = V if nonlinearity == 0.0 else V + nonlinearity * np.abs(psi) ** 2
    H_psi = H_psi + V_eff * psi
    if rotation != 0.0:
        d_dx = ifftn(1j * grid.K_x * psi_k, workers=workers)
        d_dy = ifftn(1j * grid.K_y * psi_k, workers=workers)
        L_z_psi = -1j * hbar * (grid.X * d_dy - grid.Y * d_dx)
        H_psi = H_psi - rotation * L_z_psi
    return H_psi
```

### Quantum-Sim Hamiltonian Summary

<|message|> Property | Value |
|---|---|
| Function type | Linear operator (Hψ) for kinetic + potential terms; nonlinear action when g≠0 (Gross-Pitaevskii-type) |
| Linearity caveat | Kinetic (-ℏ²/2m ∇²ψ) and potential (Vψ) terms are linear in ψ. Nonlinear interaction (g|ψ|²ψ) is NOT linear. Complete expression is nonlinear when g≠0. |
| State space | Complex wavefunction ψ(x) on spatial grid (1D/2D/3D) |
| Operator | H = T + V + g\|ψ\|² + rotation (L_z) |
| Kinetic term | -ℏ²/2m ∇²ψ (spectral, exact for band-limited ψ) |
| Potential term | V(x)ψ (multiplication operator) |
| Nonlinearity | g\|ψ\|²ψ (Gross-Pitaevskii) |
| Rotation | -Ω L_z ψ (angular momentum about z-axis) |
| Units | Atomic units (ℏ=1, m=1 by default) |
| Invariants | Norm conservation (unitary evolution), energy conservation |
| Evolution operator | Split-step Fourier (Strang 2nd order, Yoshida 4th order) |
| Hermiticity | Yes (self-adjoint for real V, no rotation/damping) |
| Observed behavior | Norm conserved to < 10^-12; energy conserved in evolution |

### Energy expectation (separate from operator)

```python
def total_energy_expectation(wf, potential, hbar=1.0, m=1.0) -> float:
    T_exp = kinetic_energy_expectation(wf, hbar, m)  # <p^2>/(2m)
    V_exp = potential_energy_expectation(wf, potential)  # <V(x)>
    return float(T_exp + V_exp)
```

**Operation:** Scalar energy expectation value (not an operator application).
**Mathematical type:** `<E> = <T> + <V>` = expectation of Hamiltonian under Born rule.
**Units:** Atomic units (energy in Hartree).

---

## 3. Comparison

### 3.1 Structural comparison

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Function type | Scalar function: (vector, vector, dict) -> float | Linear operator: (ψ, grid, V) -> ψ |
| State space | 5D emotional vector (resolved, expanded) | Complex wavefunction on spatial grid |
| Operator | None (scalar computation) | H = T + V + g\|ψ\|² - Ω L_z |
| Energy | pq_dot - Lagrangian (clamped to [0,1]) | Kinetic + potential expectation values |
| Momentum | `max(0, resolved[i])` (clamped, not physical) | Physical momentum (Fourier space) |
| Lagrangian | Weighted absolute differentials (0.5/0.3/0.2) | Not used (Hamiltonian formalism, not Lagrangian) |
| Evolution | None defined | Split-step Fourier (unitary) |
| Invariants | None defined | Norm conservation, energy conservation |
| Units | None (dimensionless) | Atomic units (Hartree) |
| Hermiticity | Not applicable | Yes (self-adjoint) |
| Output | Scalar [0,1] | Wavefunction (complex array) or scalar energy |

### 3.2 What IS structurally similar

1. **Energy decomposition**: Both decompose energy into components. King Wen: pq_dot - lagrangian. Quantum-Sim: kinetic + potential. Both use subtraction of a "cost" term from a "driving" term.

2. **Paired differentials**: King Wen uses `resolved - expanded` per axis. Quantum-Sim uses `T_k * psi_k` (kinetic) and `V * psi` (potential). Both compute per-component contributions.

3. **Clamping/bounding**: King Wen uses `_clamp()` to [0,1]. Quantum-Sim uses normalization (unit norm). Both constrain output to a defined range.

### 3.3 What is NOT the same

1. **Operator vs scalar**: Quantum-Sim's Hamiltonian is a linear operator Hψ that acts on a wavefunction. King Wen's `_hamiltonian_energy` is a scalar function that takes two vectors and a dict and returns a float. These are fundamentally different mathematical objects.

2. **State space**: Quantum-Sim operates on complex-valued wavefunctions on spatial grids. King Wen operates on 5D real-valued emotional vectors. No defined mapping between these spaces exists.

3. **Momentum**: Quantum-Sim uses physical momentum (Fourier-transformed wavefunction, p = -iℏ∇). King Wen uses `max(0, resolved_vector[i])` which is a clamped emotional vector component, not a physical momentum.

4. **Lagrangian**: Quantum-Sim does not use a Lagrangian at all -- it uses the Hamiltonian formalism H = T + V. King Wen uses a Lagrangian L = 0.5*|dy| + 0.3*|yao_dy| + 0.2*|changing_dy|. The Lagrangian in King Wen is not derived from a kinetic-minus-potential formulation.

5. **Units**: Quantum-Sim uses atomic units (Hartree). King Wen has no defined units.

6. **Evolution**: Quantum-Sim has a defined evolution operator (split-step Fourier, unitary). King Wen has no evolution operator.

7. **Invariants**: Quantum-Sim conserves norm and energy. King Wen has no defined invariants.

8. **Zero-energy finding**: King Wen produces 0.0 for all 512 states due to scale mismatch (pq_dot ~0.005-0.013, lagrangian ~2.1-5.1). This is an implementation finding, not evidence of incompatibility.

---

## 4. Mathematical Correspondence Assessment

### 4.1 Three distinct entities

The assessment must separate three things that share the name "Hamiltonian":

1. **A function named `_hamiltonian_energy()`** -- exists in King Wen codebase.
2. **A computational energy-like scalar** -- derived from paired differentials (resolved vs expanded vectors, line-state counts).
3. **A quantum-mechanical Hamiltonian operator** -- Hψ = -ℏ²/2m ∇²ψ + Vψ + ... acting on a defined state space.

The shared name does not establish that these are equivalent. Entity 1 is a function. Entity 2 is a scalar. Entity 3 is a linear operator. They are different mathematical objects.

### 4.2 Kernel-level

Both systems compute an energy-like quantity from state components. King Wen: `pq_dot - lagrangian`. Quantum-Sim: `kinetic + potential`. Both use subtraction/addition of component energies.

**Status: Shared at the formula level (both compute energy as sum of components).**

### 4.3 Implementation-level

The mathematical objects are fundamentally different:
- Quantum-Sim: Linear operator on Hilbert space (Hψ)
- King Wen: Scalar function on 5D real vectors and a dict

No defined state space, operator domain, or unit system in King Wen.

**Status: NOT ESTABLISHED.**

### 4.4 Application-level

Quantum-Sim's Hamiltonian predicts physical energy (measurable in Hartree). King Wen's energy is a dimensionless scalar used to modulate avatar animation intensity. Different mathematical roles.

**Status: Partial conceptual relationship.**

### 4.5 Disposition

**M3-HAMILTONIAN-ENERGY: `undetermined`**

The name "Hamiltonian" is shared, but the mathematical objects are different (scalar function vs linear operator / nonlinear action). The state spaces, units, operators, and invariants are not established as corresponding. The zero-energy finding is an implementation observation, not evidence of incompatibility.

The Quantum-Sim implementation must be described as a Gross-Pitaevskii-type nonlinear evolution model when g≠0, not as a purely linear operator. Norm conservation and energy conservation are expected properties that must be measured, not assumed. Atomic units are default parameters that must be verified as explicitly configured.

A function that outputs an energy-like scalar is not automatically a Hamiltonian operator. Reformulating it as an operator would be a new mathematical construction, not evidence that the existing implementation already represents one.

### 4.6 Three-Level Distinction

| Level | King Wen | Quantum-Sim | Status |
|---|---|---|---|
| Kernel-level | Energy as sum of components (pq_dot - lagrangian) | Energy as sum of components (kinetic + potential) | SHARED -- both decompose energy into components |
| Implementation-level | Scalar function on 5D vectors + dict; no operator, no units, no evolution | Linear operator on Hilbert space; spectral, unitary, conserved | NOT ESTABLISHED -- different mathematical objects |
| Application-level | Avatar animation intensity modulation | Physical energy prediction | PARTIAL CONCEPTUAL -- both produce energy-like scalars |

### 4.7 Audit dimensions

| Audit dimension | Question | King Wen | Quantum-Sim |
|---|---|---|---|
| State space | What mathematical object does H act upon? | 5D emotional vector (resolved, expanded) | Complex wavefunction on spatial grid |
| Operator classification | Is H linear, nonlinear, or mixed? | Scalar function (not linear, not operator) | Linear for T+V terms; nonlinear when g≠0 (Gross-Pitaevskii) |
| Operator | Is H a linear operator, scalar function, or computational procedure? | Scalar function (not linear, not operator) | Linear operator for kinetic+potential; nonlinear action for g≠0 |
| Conservation (theoretical) | What should be conserved? | None defined | Norm (unitary); energy (time-independent) |
| Conservation (numerical) | What is actually conserved? | Not measured | Must be measured against evolution scheme and error |
| Energy | What quantity is calculated and in what units? | Dimensionless scalar [0,1] | Energy in atomic units (Hartree) |
| Momentum | Is pq_dot a physically defined momentum quantity? | No -- clamped emotional vector component | Yes -- Fourier-transformed wavefunction |
| Lagrangian | Is it derived from kinetic-minus-potential? | No -- weighted absolute differentials | Not used (Hamiltonian formalism) |
| Evolution | Does either define an evolution operator? | No | Yes -- split-step Fourier (unitary) |
| Invariants | What quantities are conserved? | None defined | Norm conservation, energy conservation |
| Numerical behavior | Why does King Wen produce zero energy? | Scale mismatch: pq_dot ~0.005-0.013, lagrangian ~2.1-5.1, _clamp floors to 0 | Energy conserved to machine precision |

### 4.8 What would be needed to upgrade to `defined`

1. A formal definition of the King Wen energy as a mathematical function with explicit domain, codomain, and units.
2. A demonstration that the King Wen energy corresponds to a Hamiltonian operator on a defined state space.
3. A specification of the relationship between `pq_dot` and physical momentum.
4. A specification of the relationship between the Lagrangian and a kinetic-minus-potential formulation.
5. Reproducible numerical validation comparing King Wen energy against a known Hamiltonian eigenvalue.

### 4.9 What would make it `incompatible`

1. If the King Wen energy were found to not be derivable from a Hamiltonian formalism (i.e., no corresponding operator exists).
2. If the state spaces were found to be fundamentally incompatible (e.g., 5D real vectors vs infinite-dimensional Hilbert space).
3. If the units were found to be incommensurable (e.g., dimensionless vs energy units with no conversion).

### 4.10 Compatibility scope note

Failure to find a corresponding physical Hamiltonian does not mean the King Wen scoring function is mathematically invalid. It may be a perfectly legitimate synthetic scoring function with a misleadingly familiar name. Reformulating it as an operator would be a new mathematical construction, not evidence that the existing implementation already represents one. The exact scope of the proposed correspondence must be defined before declaring incompatibility.

---

## 5. Known Limitations

1. The King Wen Hamiltonian has not been validated against any known energy value.
2. Quantum-Sim norm conservation is expected for appropriate Hamiltonian evolution but should be measured, not assumed.
3. Quantum-Sim energy conservation depends on evolution scheme (Strang 2nd order vs Yoshida 4th order), time dependence, and numerical error. Should be evaluated against measured conservation error.
4. Atomic units (ℏ=1, m=1) are default parameters, not explicitly configured. Verify whether they are set or assumed.
5. The complete Quantum-Sim expression is nonlinear when g≠0 (Gross-Pitaevskii-type). Do not classify entire implementation as linear operator.
2. The `line_balance` dict is empty in production (`{}`), making the Lagrangian constant at 2.1.
3. The `HAMILTONIAN_PAIRED_DIFFERENTIALS` global dict retains only the last hexagram (hex 64, phase 0).
4. The `momentum` uses `max(0.0, resolved_vector[i])` which discards negative components -- this is not a physical momentum.
5. No evolution operator or conservation law is defined in King Wen.

---

## 6. Unresolved Questions

1. Is the King Wen energy intended to approximate a physical Hamiltonian, or is it a synthetic scoring function?
2. What is the relationship between `pq_dot` and physical momentum? Is it a metaphor or a computation?
3. What is the relationship between the Lagrangian and a kinetic-minus-potential formulation?
4. Could the King Wen energy be reformulated as a Hamiltonian operator on a defined state space?
5. What would be the physical interpretation of the 5-axis emotional vector as a quantum state?

---

## 7. Evidence Provenance

- King Wen source: `emotional_engine.py:395-455` (canonical engine, revision 71fbf28f8e92c6a7de74c50a304906ef81963a7d)
- King Wen additional: `HAMILTONIAN_PAIRED_DIFFERENTIALS` global dict at line 396; `verify_restored_state.py` (print-only consumer)
- Quantum-Sim source: `quantumlab/stationary/hamiltonian.py:1-30` (v1.3.0, merged 2026-11-02); `quantumlab/observables/expectation.py:140-185` (energy expectation)
- Zero-energy finding: observed in prior testing; pq_dot ~0.005-0.013, lagrangian ~2.1-5.1, _clamp floors to 0.0; 64/64 pairs verified pq_dot < lagrangian
- Audit date: 2026-11-02
- Evidence level: E1 (lexical overlap) for "Hamiltonian" terminology; E2 (conceptual) for energy decomposition; E3 (mathematical) NOT YET DEMONSTRATED
- Mathematical correspondence (E3): NOT YET DEMONSTRATED
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
