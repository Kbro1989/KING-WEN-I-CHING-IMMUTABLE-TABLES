# M7 Evolution and Propagation Correspondence Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M7-EVOLUTION-PROPAGATION
**Mathematical Object:** Evolution and propagation
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02

---

## 1. King Wen Implementation

### 1.1 Split-step Fourier pre-warming (quantum wave packet evolution)

**Source:** `scripts/prewarm_quantum_wavepackets.py:1-200`

```python
HBAR, MASS, DT, WARMUP_STEPS = 1.0, 1.0, 0.02, 3
N1 = 64
N2X, N2Y = 8, 8
N3X, N3Y, N3Z = 9, 9, 9

def prewarm_1d():
    dx = (2*PI) / N1
    x = np.linspace(-PI, PI, N1, endpoint=False)
    k = 2 * np.pi * np.fft.fftfreq(N1, dx)
    V = _kw_pot_1d(x)
    T_k = HBAR**2 * k**2 / (2.0 * MASS)
    U_V = np.exp(-1j * V * DT / (2.0 * HBAR))
    U_T = np.exp(-1j * T_k * DT / HBAR)
    psi = np.exp(-(x**2) / (4.0*0.5**2)) * np.exp(1j * 1.0 * x)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)
    for _ in range(WARMUP_STEPS):
        psi = ifft(fft(psi * U_V) * U_T) * U_V
```

**Operation:** Split-step Fourier evolution of a Gaussian wave packet on King Wen's potential surface.
**Mathematical type:** Time evolution via split-step Fourier method (Strang splitting).
**Input:** Grid (N points), potential V(x), time step DT=0.02, 3 warmup steps
**Output:** Evolved wavefunction psi (complex array)
**Potential:** `_kw_pot_1d(x) = sum(sin(p * x / pi) / p for p in [97,89,83,79,73])`
**Evolution:** `psi → ifft(fft(psi * U_V) * U_T) * U_V` (Strang splitting: half-potential, full-kinetic, half-potential)
**Relationship to Quantum-Sim:** This is a DIRECT USE of Quantum-Sim's split-step Fourier method, but with King Wen's own potential surface (coprime-frequency sum). The evolution machinery is borrowed; the potential is King Wen's.

### 1.2 State transition (temporal propagation)

**Source:** `src/core/pog3_hexagram_runtime_substrate.py:318-325`

```python
# Look at last 3 captures for temporal momentum
momentum = (avg_chaos + avg_whimsy) / 2
new_chaos = min(1.0, intent.emotional[0] + momentum * 0.1)
```

**Operation:** Temporal momentum from recent state history; adjusts chaos weight.
**Mathematical type:** Exponential moving average / momentum-based update.
**Input:** Last 3 captured states (avg_chaos, avg_whimsy)
**Output:** new_chaos (adjusted chaos weight)
**Relationship to evolution:** This is a state-transition rule, not a wavefunction evolution. No Schrödinger equation, no unitary operator.

### 1.3 Mobius transformation (conformal propagation)

**Source:** `kingwen_mobius_sphere.py` (Sovereign Riemann Sphere Backend)

```python
# t1 mobius mag=4.689 theta=-1.429
# t2 future bias future_weight=0.3501
# North=60, South=0, Void=4
# path 1→48 in 6 steps
```

**Operation:** Conformal mapping on Riemann sphere (Mobius transformation).
**Mathematical type:** Complex analysis (Mobius transformation z → (az+b)/(cz+d)).
**Input:** Hexagram state on Riemann sphere
**Output:** Transformed state (mag, theta)
**Relationship to evolution:** Conformal map preserves angles but is not time evolution. It maps states between representations.

### 1.4 Gaussian future projection

**Source:** `emotional_engine.py` (_project_gaussian_future, referenced in prior sessions)

```python
# future phase weight from Gaussian kernel
# centered on phase 2 (future)
# FWHM=2.5
```

**Operation:** Gaussian-weighted projection of present state onto future phase.
**Mathematical type:** Gaussian kernel convolution / projection.
**Input:** Present state, future phase center
**Output:** Future-weighted state
**Relationship to evolution:** This is a projection (not evolution). It weights future phases by Gaussian distance from present.

### 1.5 State capture and propagation (shotgun_expand)

**Source:** `full_hexagram_shotgun.py` (shotgun_expand)

```python
# Full 64-hexagram × 8-phase expansion
# 729 ternary configurations per hexagram
# 46,656 total ternary line permutations
# 35,000 domained routes
```

**Operation:** Full state space expansion (all 64 hexagrams × 8 phases × 729 ternary configs).
**Mathematical type:** Cartesian product / combinatorial expansion.
**Input:** request_text, emotional_input
**Output:** 64 expanded + 512 resolved states + 729 ternary configs per hexagram
**Relationship to evolution:** This is a static expansion (all states computed simultaneously), not a time evolution. No time step, no differential equation.

### King Wen Evolution/Propagation Summary

| Property | Value |
|---|---|
| Split-step Fourier | Direct use of Quantum-Sim method with King Wen potential (coprime frequencies) |
| State transition | Momentum-based update from recent history (not wavefunction evolution) |
| Mobius transformation | Conformal map on Riemann sphere (not time evolution) |
| Gaussian future projection | Weighted projection (not differential equation) |
| State expansion | Static combinatorial expansion (not time evolution) |
| Schrödinger equation | Absent (no differential equation for state evolution) |
| Unitary evolution | Absent (no unitary operator) |
| Time parameter | Present in split-step pre-warming (DT=0.02) but not in state expansion |
| Conservation | None defined for state transitions |

---

## 2. Quantum-Sim Implementation

### 2.1 Split-step Fourier evolution

**Source:** `quantumlab/solvers/split_operator.py`

```python
def apply_hamiltonian(psi, grid, V, hbar=1.0, m=1.0, g=0.0, rotation=0.0, ...):
    T_k = hbar**2 * k**2 / (2 * m)
    H_psi = ifftn(T_k * fftn(psi)) + V * psi + g * np.abs(psi)**2 * psi
    if rotation != 0.0:
        L_z_psi = -1j * hbar * (grid.X * d_dy - grid.Y * d_dx)
        H_psi = H_psi - rotation * L_z_psi
    return H_psi
```

**Operation:** Hamiltonian application (kinetic + potential + nonlinear + rotation).
**Mathematical type:** Linear operator (kinetic+potential) + nonlinear action (when g≠0).
**Evolution:** `psi(t+dt) = exp(-i H dt / hbar) psi(t)` via Strang splitting.

### 2.2 Time evolution loop

```python
for step in range(num_steps):
    psi = ifft(fft(psi * U_V) * U_T) * U_V  # Strang splitting
```

**Operation:** Iterative time evolution of wavefunction.
**Mathematical type:** Discrete time evolution (unitary propagator).
**Conservation:** Norm conserved (unitary); energy depends on scheme/time dependence/numerical error.

### 2.3 Stationary state evolution

**Source:** `quantumlab/stationary.py`

```python
# Imaginary time evolution for ground state
psi = psi * np.exp(-V * dt / (2*hbar))
psi = ifft(fft(psi) * np.exp(-T_k * dt / hbar))
psi = psi * np.exp(-V * dt / (2*hbar))
psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)  # renormalize
```

**Operation:** Imaginary time evolution for ground state finding.
**Mathematical type:** Wick rotation (t → -iτ) for eigenstate computation.
**Relationship to King Wen:** No direct equivalent. King Wen has no ground state computation.

### 2.4 Strong-field evolution

**Source:** `quantumlab/strongfield.py`

```python
# Classical trajectory phase in strong-field ionization
phase = np.interp(target, ke[b][order], returns[b][order])
classical_t += [(phase + np.pi / 2 + n * np.pi) / omega for n in range(10, 30)]
```

**Operation:** Classical trajectory phase in strong-field ionization (SFA).
**Mathematical type:** Phase accumulation in classical action.
**Relationship to King Wen:** No direct equivalent.

### Quantum-Sim Evolution Summary

| Property | Value |
|---|---|
| Evolution equation | Schrödinger equation (iℏ ∂ψ/∂t = Hψ) |
| Evolution method | Split-step Fourier (Strang splitting) |
| Propagator | Unitary (norm conserved) |
| Time parameter | Continuous (dt = 0.02 typical) |
| State space | Complex wavefunction on spatial grid |
| Conservation | Norm (unitary); energy (depends on scheme) |
| Stationary states | Imaginary time evolution (ground state finding) |
| Strong-field | Classical trajectory phase (SFA) |

---

## 3. Implementation-Level Comparison

### 3.1 Split-step Fourier (shared implementation)

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Method | Strang splitting (half-potential, full-kinetic, half-potential) | Same |
| Potential | King Wen's coprime-frequency sum | Physical potential V(x) |
| Grid | 1D=64, 2D=8×8, 3D=9×9×9 | Variable (128×96×96 typical) |
| Time step | DT=0.02 | Variable |
| Warmup steps | 3 | Variable |
| Normalization | Yes (sqrt(sum\|ψ\|²)·dx) | Yes |
| Evolution loop | 3 warmup steps only | Variable number of steps |
| Physical meaning | Pre-warming for avatar animation | Physical quantum evolution |

### 3.2 State transition (King Wen only)

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Method | Momentum from recent history | N/A (no state transition rule) |
| Input | Last 3 captured states | N/A |
| Output | Adjusted chaos weight | N/A |
| Evolution equation | None (rule-based) | Schrödinger equation |
| Conservation | None | Norm conserved |

### 3.3 Mobius transformation (King Wen only)

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Method | Conformal map on Riemann sphere | N/A |
| Input | Hexagram state on sphere | N/A |
| Output | Transformed state (mag, theta) | N/A |
| Evolution | No (static map) | N/A |
| Physical meaning | State transformation | N/A |

### 3.4 Gaussian future projection (King Wen only)

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Method | Gaussian-weighted projection | N/A |
| Input | Present state, future phase center | N/A |
| Output | Future-weighted state | N/A |
| Evolution | No (projection, not differential equation) | N/A |

### 3.5 State expansion (King Wen only)

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Method | Cartesian product / combinatorial expansion | N/A |
| Input | request_text, emotional_input | N/A |
| Output | 64 expanded + 512 resolved + 729 ternary | N/A |
| Evolution | No (static expansion) | N/A |
| Time parameter | None | N/A |

### 3.6 Shared mathematical structures

1. **Split-step Fourier method**: Both use Strang splitting (half-potential, full-kinetic, half-potential). King Wen borrows this directly from Quantum-Sim.

2. **Normalization**: Both normalize wavefunction to unit norm. King Wen: `psi /= sqrt(sum(|psi|²) * dx)`. Quantum-Sim: same pattern.

3. **Complex exponentials**: Both use `exp(-1j * ...)` for phase factors. King Wen: `U_V = exp(-1j * V * DT / (2*HBAR))`. Quantum-Sim: same form.

4. **FFT/IFFT**: Both use fast Fourier transform for kinetic energy computation. King Wen: `fft`, `ifft`. Quantum-Sim: `fftn`, `ifftn`.

### 3.7 Genuine differences

1. **No Schrödinger equation in King Wen**: King Wen has no differential equation governing state evolution. The split-step Fourier is used for pre-warming only.

2. **No unitary evolution in King Wen**: King Wen's state transitions are rule-based (momentum from history), not unitary.

3. **No time parameter in state expansion**: King Wen's shotgun_expand is static (all states computed simultaneously). No time evolution.

4. **No conservation in King Wen**: Quantum-Sim conserves norm (unitary). King Wen has no conservation law for state transitions.

5. **Different potential surfaces**: King Wen uses coprime-frequency sum. Quantum-Sim uses physical potentials.

6. **Different grid sizes**: King Wen uses small grids (64, 8×8, 9×9×9). Quantum-Sim uses larger grids (128×96×96).

---

## 4. Mathematical Correspondence Assessment

### 4.1 Kernel-level

Both systems use split-step Fourier evolution with Strang splitting. King Wen directly borrows Quantum-Sim's method. The mathematical structure (half-potential, full-kinetic, half-potential) is identical.

**Status: Shared at the method level (split-step Fourier).**

### 4.2 Implementation-level

The evolution machinery is shared (split-step Fourier), but the application differs:
- Quantum-Sim: Physical quantum evolution (Schrödinger equation, unitary, norm-conserving)
- King Wen: Pre-warming for avatar animation (3 warmup steps, no physical evolution)

The state transition rules (momentum from history) are King Wen-specific with no Quantum-Sim equivalent.

**Status: Shared method, different application.**

### 4.3 Application-level

King Wen's evolution quantities modulate avatar animation, audio, and 3D mesh. Quantum-Sim's evolution is physical quantum dynamics. Different mathematical roles.

**Status: Partial conceptual relationship.**

### 4.4 Disposition

**M7-EVOLUTION-PROPAGATION: `undetermined`**

The split-step Fourier method is directly shared (King Wen borrows from Quantum-Sim). However, the application differs: Quantum-Sim uses it for physical quantum evolution; King Wen uses it for pre-warming avatar animation. The state transition rules, Mobius transformation, Gaussian projection, and combinatorial expansion are King Wen-specific with no Quantum-Sim equivalent.

The shared method (split-step Fourier) is a genuine mathematical correspondence at the algorithm level. Whether this constitutes a meaningful mathematical relationship depends on whether the application context matters.

### 4.5 Three-Level Distinction

| Level | King Wen | Quantum-Sim | Status |
|---|---|---|---|
| Kernel-level | Split-step Fourier (Strang splitting) | Split-step Fourier (Strang splitting) | SHARED -- identical algorithm |
| Implementation-level | Pre-warming for avatar (3 steps, small grids) | Physical evolution (variable steps, large grids) | SHARED METHOD, DIFFERENT APPLICATION |
| Application-level | Avatar animation, audio, mesh modulation | Physical quantum dynamics | PARTIAL CONCEPTUAL -- same method, different purpose |

### 4.6 Audit dimensions

| Audit dimension | Question | King Wen | Quantum-Sim |
|---|---|---|---|
| Evolution equation | Is there a differential equation? | No (rule-based + pre-warming) | Yes (Schrödinger equation) |
| Propagator | Is evolution unitary? | No (pre-warming only) | Yes (unitary split-step) |
| Time parameter | Is there a time variable? | Yes (DT=0.02, 3 steps) | Yes (continuous) |
| State space | What evolves? | Wavefunction on small grid | Wavefunction on large grid |
| Conservation | What is conserved? | None | Norm (unitary) |
| Stationary states | Are ground states computed? | No | Yes (imaginary time) |
| Strong-field | Is there strong-field evolution? | No | Yes (SFA) |
| State transition | Is there a state update rule? | Yes (momentum from history) | No (differential equation) |
| Conformal map | Is there a Mobius transformation? | Yes (Riemann sphere) | No |
| Projection | Is there a Gaussian projection? | Yes (future phase weighting) | No |
| Expansion | Is there combinatorial expansion? | Yes (64×8×729) | No |

### 4.7 What would be needed to upgrade to `defined`

1. A formal definition of evolution in King Wen (if one exists beyond pre-warming).
2. A demonstration that the state transition rule (momentum from history) corresponds to a differential equation.
3. A specification of the relationship between the Mobius transformation and quantum evolution.
4. Reproducible numerical validation comparing King Wen evolution against Quantum-Sim evolution.

### 4.8 What would make it `incompatible`

1. If King Wen's split-step Fourier were found to be purely for visualization with no mathematical evolution.
2. If the state transition rule were found to be unrelated to differential equations.
3. If the Mobius transformation were found to have no relationship to quantum evolution.

---

## 5. Known Limitations

1. King Wen's split-step Fourier is used for pre-warming only (3 steps), not physical evolution.
2. The state transition rule (momentum from history) is rule-based, not derived from a differential equation.
3. The Mobius transformation is a conformal map, not a time evolution.
4. The Gaussian future projection is a weighted projection, not a differential equation.
5. The combinatorial expansion is static, not a time evolution.
6. No Schrödinger equation, no unitary operator, no conservation law in King Wen's state machinery.

---

## 6. Unresolved Questions

1. Is the split-step Fourier pre-warming intended as a physical evolution or a visualization technique?
2. What is the relationship between the state transition rule and differential equations?
3. Could the Mobius transformation be interpreted as a time evolution operator?
4. Is the Gaussian future projection related to imaginary time evolution?
5. What is the physical interpretation of the combinatorial expansion?

---

## 7. Evidence Provenance

- King Wen sources:
  - `scripts/prewarm_quantum_wavepackets.py:1-200` (split-step Fourier pre-warming, 1D/2D/3D)
  - `src/core/pog3_hexagram_runtime_substrate.py:318-325` (temporal momentum from history)
  - `kingwen_mobius_sphere.py` (Mobius transformation, Riemann sphere)
  - `emotional_engine.py` (_project_gaussian_future, Gaussian future projection)
  - `full_hexagram_shotgun.py` (shotgun_expand, combinatorial expansion)
- Quantum-Sim sources:
  - `quantumlab/solvers/split_operator.py` (apply_hamiltonian, Strang splitting)
  - `quantumlab/stationary.py` (imaginary time evolution)
  - `quantumlab/strongfield.py` (strong-field evolution, SFA)
- Audit date: 2026-11-02
- Evidence level: E1 (lexical overlap) for "evolution"/"propagation" terminology; E2 (conceptual) for split-step Fourier method; E3 (mathematical) NOT YET DEMONSTRATED
- Mathematical correspondence (E3): NOT YET DEMONSTRATED (shared method, different application)
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
