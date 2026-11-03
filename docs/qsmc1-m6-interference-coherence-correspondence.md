# M6 Interference and Coherence Correspondence Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M6-INTERFERENCE-COHERENCE
**Mathematical Object:** Interference and coherence
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02

---

## 1. King Wen Implementation

### 1.1 Harmonic interference pattern (synthetic visualization)

**Source:** `scripts/bridge_quantumlab_visualization.py:100-130`

```python
yao_harmonics = sum(
    0.15 * np.cos((line_idx + 1) * (X - x_center) + line_idx * T * 0.5)
    for line_idx in range(6)
)
envelope = np.exp(-((X - x_center) ** 2) / (2.0 * sig_t ** 2))
Z = envelope * (1.0 + 0.25 * np.sin(E * T * 2.0) + yao_harmonics)
Z = np.clip(Z, 0.0, None)
```

**Operation:** Six real cosine harmonics (one per Yao line) superposed with a Gaussian envelope and energy-dependent sinusoidal modulation. Clipped to nonnegative.

**Mathematical type:** Real-valued scalar field construction (visualization).
**Input:** X (position grid), T (time grid), x_center, sig_t, E (Hamiltonian energy), line_idx (0-5)
**Output:** Z (scalar field, nonnegative)
**Components:**
- 6 cosine terms: `0.15 * cos((line_idx+1)*(X-x_center) + line_idx*T*0.5)`
- Gaussian envelope: `exp(-((X-x_center)^2)/(2*sig_t^2))`
- Energy modulation: `1.0 + 0.25 * sin(E*T*2.0)`
**Physical interpretation:** Synthetic visualization — no wavefunction, no complex amplitudes, no Born rule. Six real harmonics superposed as scalar field.

### 1.2 Quantum wavefunction construction (complex amplitude)

**Source:** `emotional_engine.py:488-570` (_quantum_avatar_modulation)

```python
wavefunction: Dict[str, Dict[str, Any]] = {}
for i, key in enumerate(VEC_KEYS):
    rv = float(resolved_vector[i])
    ev = float(expanded_vector[i])
    phase_complexity = (phase_bits % 3) + 1  # 1..3
    real_part = rv * temporal_gaussian
    imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)
    wavefunction[key] = {
        "real": round(real_part, 6),
        "imag": round(imag_part, 6),
        "amplitude": round(math.sqrt(real_part**2 + imag_part**2), 6),
    }
```

**Operation:** Constructs a complex amplitude (real, imag) per vector axis from resolved/expanded vectors, Gaussian kernel, and Hamiltonian energy.
**Mathematical type:** Complex number construction (z = a + ib).
**Input:** resolved_vector (5 axes), expanded_vector (5 axes), phase_bits (0-7), hamiltonian (0-1), temporal_gaussian (scalar)
**Output:** wavefunction dict with real, imag, amplitude per axis
**Relationship to interference:** This is the closest King Wen gets to complex amplitude construction. The real/imag components are derived from vector differences and energy, not from physical wavefunctions. No superposition of multiple wavefunctions is computed.

### 1.3 Coherence as 5-axis vector component

**Source:** `emotional_engine.py:741` (coherence computation)

```python
_clamp(yang_r * 0.3 - yao_dy * 0.3 - abs(old_dy) * 0.1)  # coherence
```

**Operation:** Coherence computed as clamped combination of yang ratio, yao differential, and old differential.
**Mathematical type:** Scalar scoring function (dimensionless [0,1]).
**Relationship to interference:** "Coherence" is a named axis in the 5-axis emotional vector. It is not computed from wavefunction overlap, autocorrelation, or any interference-related operation. It is a derived score from paired differentials.

### 1.4 Coherence in decision matrix

**Source:** `decision_matrix.py:340-360`

```python
coherence = float(vector.get("coherence", 0.0) or 0.0)
if coherence > 0.7:
    parts.append("focused")
```

**Operation:** Threshold comparison for decision-making.
**Mathematical type:** Boolean classification (coherence > 0.7 → "focused").
**Relationship to interference:** None. Coherence used as a threshold for behavioral classification.

### 1.5 Coherence in avatar mesh generation

**Source:** `generate_avatar_meshes.py:139, 181` (from prior search)

```python
vortex_tension: float = 0.5,
delta_r = (d_norm - 0.5) * 0.40 * (1.0 + vortex_tension) * phase_mod
```

**Operation:** Coherence amplitude mapped to latitudinal compression in 3D mesh deformation.
**Mathematical type:** Geometric deformation (mesh vertex displacement).
**Relationship to interference:** Coherence used as a modulation parameter for 3D geometry, not as wavefunction overlap.

### 1.6 Superposition / expansion records

**Source:** `full_hexagram_shotgun.py` (shotgun_expand output)

The shotgun expansion produces 64 expanded + 512 resolved states. Each state has:
- expanded_vector (5 axes)
- resolved_vector (5 axes)
- consensus_vector (5 axes)
- phase_temporal, phase_polarity, phase_description

**Operation:** State expansion (not wavefunction superposition). All 64 hexagrams expanded simultaneously; no collapse to single dominant.
**Relationship to interference:** "Superposition" in King Wen means all states exist simultaneously (quantum metaphor). No complex amplitude superposition (ψ₁ + ψ₂) is computed.

### King Wen Interference/Coherence Summary

| Property | Value |
|---|---|
| Interference pattern | 6 real cosine harmonics + Gaussian envelope + energy modulation (visualization) |
| Complex amplitude | Constructed per vector axis (real, imag) from vector differences |
| Coherence | 5-axis vector component computed from paired differentials |
| Superposition | All 64 hexagrams expanded simultaneously (state expansion, not wavefunction) |
| Physical units | None (dimensionless) |
| Wavefunction | Constructed but not evolved (no Schrödinger equation) |
| Born rule | Absent |
| Autocorrelation | Absent |
| Cross-term | Absent (no ψ₁*ψ₂ computation) |

---

## 2. Quantum-Sim Implementation

### 2.1 Double-slit interference (physical)

**Source:** `examples/07_3d_double_slit.py:29-131`

```python
def fringe_analysis(psi, grid, x_cut, pad=8):
    psi_T = psi * (grid.X > x_cut)
    n_y = grid.N_y * pad
    phi_y = np.fft.fft(psi_T, n=n_y, axis=1)
    P = np.fft.fftshift(np.sum(np.abs(phi_y) ** 2, axis=(0, 2)))
    k_y = np.fft.fftshift(2 * np.pi * np.fft.fftfreq(n_y, grid.dy))
    return k_y, P / P.max()
```

**Operation:** FFT of transmitted wavefunction → momentum distribution → fringe pattern.
**Mathematical type:** Fourier transform of complex wavefunction → probability density in momentum space.
**Physical interpretation:** Two-source interference pattern from complex wavefunction propagation through two pinholes.

### 2.2 State overlap (autocorrelation)

**Source:** `quantumlab/observables/current.py:35-40`

```python
def autocorrelation(psi0, psi_t, grid) -> complex:
    """C(t) = <psi(0)|psi(t)>."""
    return complex(np.sum(np.conj(psi0) * psi_t) * volume_element(grid))
```

**Operation:** Complex inner product ⟨ψ₀|ψₜ⟩ = ∫ ψ₀* ψₜ dV.
**Mathematical type:** State overlap (complex scalar).
**Physical interpretation:** Measures similarity between initial and evolved wavefunction; Fourier transform peaks at eigenenergies.

### 2.3 Vortex detection (phase winding)

**Source:** `quantumlab/observables/current.py:52-90`

```python
phase = np.angle(wf.psi)
circulation = (wrapped(phase[:-1, :-1], phase[1:, :-1]) + ...)
charge = np.rint(circulation / (2.0 * np.pi)).astype(int)
```

**Operation:** Phase winding around grid plaquettes → quantized topological charge.
**Mathematical type:** Topological invariant (winding number).
**Physical interpretation:** Vortex detection from phase singularities.

### Quantum-Sim Interference/Coherence Summary

| Property | Value |
|---|---|
| Interference pattern | FFT of complex wavefunction → momentum distribution → fringes |
| Complex amplitude | Wavefunction ψ(x) = real + i·imag (evolved via split-step Fourier) |
| State overlap | Autocorrelation C(t) = ⟨ψ₀\|ψₜ⟩ (complex inner product) |
| Phase winding | Topological charge from phase gradient (quantized) |
| Born rule | Present (P = \|ψ\|²) |
| Cross-term | Present (ψ₁*ψ₂ in interference) |
| Physical units | ℏ, spatial coordinates |
| Evolution | Split-step Fourier (unitary) |

---

## 3. Implementation-Level Comparison

### 3.1 Interference pattern construction

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Components | 6 real cosine harmonics | Complex wavefunction ψ(x) |
| Combination | Direct scalar sum | Wavefunction superposition through evolution |
| Probability | Absent (scalar field) | Born rule P = \|ψ\|² |
| Cross-term | Absent | Present (2 Re(ψ₁*ψ₂)) |
| Phase interaction | Phase offsets in cosine arguments | Relative complex phase |
| Validation | Visualization only | Measured fringes vs Fraunhofer prediction |
| Physical meaning | Synthetic visualization | Physical interference pattern |

### 3.2 Complex amplitude construction

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Real part | `rv * temporal_gaussian` | Re(ψ(x)) from wavefunction |
| Imag part | `(rv - ev) * (hamiltonian * phase_complexity * 0.1)` | Im(ψ(x)) from wavefunction |
| Amplitude | `sqrt(real² + imag²)` | \|ψ(x)\| |
| Source | Vector differences + energy | Schrödinger equation solution |
| Evolution | None (static construction) | Split-step Fourier (time evolution) |
| Physical meaning | Avatar animation parameter | Quantum mechanical wavefunction |

### 3.3 Coherence

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Definition | Clamped combination of paired differentials | State overlap ⟨ψ₀\|ψₜ⟩ (complex inner product) |
| Input | Emotional vector differentials | Wavefunctions at two times |
| Output | Scalar [0,1] | Complex number |
| Physical meaning | "Focused" threshold (>0.7) | Quantum coherence (phase relationship) |
| Measurement | Behavioral classification | Fourier transform peaks at eigenenergies |

### 3.4 Shared mathematical structures

1. **Complex number construction**: Both construct (real, imag) pairs. King Wen: from vector differences. Quantum-Sim: from wavefunction. Both use `sqrt(real² + imag²)` for amplitude.

2. **Sum of components**: King Wen sums 6 cosine harmonics. Quantum-Sim sums wavefunction contributions. Both use superposition of multiple components.

3. **Phase as parameter**: King Wen uses phase_bits in cosine arguments and Gaussian. Quantum-Sim uses phase in wavefunction construction and evolution. Both use phase as a mathematical quantity.

4. **Modulation by energy**: King Wen modulates by Hamiltonian energy. Quantum-Sim modulates by potential energy. Both use energy to modulate wave behavior.

### 3.5 Genuine differences

1. **No Born rule in King Wen**: Quantum-Sim computes P = |ψ|². King Wen has no probability density computation.

2. **No cross-term in King Wen**: Quantum-Sim has ψ₁*ψ₂ interference cross-terms. King Wen sums real cosines (no complex cross-terms).

3. **No state overlap in King Wen**: Quantum-Sim has autocorrelation C(t) = ⟨ψ₀|ψₜ⟩. King Wen has no state comparison.

4. **No wavefunction evolution in King Wen**: Quantum-Sim evolves ψ via split-step Fourier. King Wen constructs static amplitudes.

5. **Coherence is different**: Quantum-Sim's coherence is wavefunction phase relationship. King Wen's coherence is an emotional vector axis.

6. **No topological invariant in King Wen**: Quantum-Sim has quantized vortex charge. King Wen has no topological structure.

---

## 4. Mathematical Correspondence Assessment

### 4.1 Kernel-level

Both systems construct complex amplitudes (real, imag) and compute amplitudes via `sqrt(real² + imag²)`. Both use phase as a parameter in trigonometric functions. Both superpose multiple components.

**Status: Shared at the formula level (complex construction, trigonometric superposition).**

### 4.2 Implementation-level

The mathematical objects are fundamentally different:
- Quantum-Sim: Complex wavefunction evolved via Schrödinger equation, with Born rule, autocorrelation, topological invariants
- King Wen: Static complex amplitude construction from vector differences, no evolution, no Born rule, no state overlap

No defined mapping between King Wen's vector-derived amplitudes and Quantum-Sim's wavefunction.

**Status: NOT ESTABLISHED.**

### 4.3 Application-level

King Wen's interference/coherence quantities modulate avatar animation, audio, and 3D mesh. Quantum-Sim's interference/coherence are physical observables. Different mathematical roles.

**Status: Partial conceptual relationship.**

### 4.4 Disposition

**M6-INTERFERENCE-COHERENCE: `undetermined`**

The name "interference" and "coherence" are shared, but the mathematical objects are different. King Wen constructs static complex amplitudes and superposes real cosine harmonics for visualization. Quantum-Sim evolves complex wavefunctions, computes probability densities, state overlaps, and topological invariants. No defined mapping between the implementations.

However, the shared mathematical structures (complex amplitude construction, trigonometric superposition, phase as parameter, energy modulation) suggest that King Wen's implementation may have been designed with quantum interference concepts as inspiration, even if the mathematical correspondence is not established.

### 4.5 Three-Level Distinction

| Level | King Wen | Quantum-Sim | Status |
|---|---|---|---|
| Kernel-level | Complex amplitude construction (real, imag, amplitude); cosine superposition | Complex wavefunction construction; wavefunction superposition | SHARED -- complex construction, trigonometric superposition |
| Implementation-level | Static amplitudes from vector differences; no evolution; no Born rule | Evolved wavefunctions; Born rule; autocorrelation; topological invariants | NOT ESTABLISHED -- different mathematical objects |
| Application-level | Avatar animation, audio, 3D mesh modulation | Physical observable prediction (fringes, coherence, vortices) | PARTIAL CONCEPTUAL -- both produce "interference" quantities |

### 4.6 Audit dimensions

| Audit dimension | Question | King Wen | Quantum-Sim |
|---|---|---|---|
| State space | What mathematical object? | 5-axis emotional vector (discrete) | Complex wavefunction on spatial grid |
| Superposition | How are components combined? | Scalar sum of real cosines | Complex wavefunction addition (ψ₁ + ψ₂) |
| Probability | Is Born rule present? | No | Yes (P = \|ψ\|²) |
| Cross-term | Is there ψ₁*ψ₂? | No | Yes (interference cross-term) |
| State overlap | Is autocorrelation computed? | No | Yes (C(t) = ⟨ψ₀\|ψₜ⟩) |
| Topological invariant | Is there phase winding? | No | Yes (vortex charge q ∈ ℤ) |
| Evolution | Is the state evolved? | No (static construction) | Yes (split-step Fourier) |
| Coherence | What does "coherence" mean? | Emotional vector axis (scored from differentials) | Wavefunction phase relationship (state overlap) |
| Physical meaning | What is predicted? | Avatar animation, audio, mesh | Physical interference pattern, coherence, vortices |

### 4.7 What would be needed to upgrade to `defined`

1. A formal definition of "interference" in King Wen as a mathematical operation on a defined state space.
2. A demonstration that the 6 cosine harmonics correspond to wavefunction components.
3. A specification of the relationship between King Wen's coherence and quantum coherence (state overlap).
4. Reproducible numerical validation comparing King Wen interference quantities against Quantum-Sim interference patterns.

### 4.8 What would make it `incompatible`

1. If King Wen's interference were found to be purely visualization with no mathematical operation.
2. If the complex amplitude construction were found to have no relationship to wavefunction superposition.
3. If the coherence were found to be a behavioral threshold with no relationship to wavefunction phase.

---

## 5. Known Limitations

1. King Wen's harmonic interference is a synthetic visualization (6 real cosines + Gaussian envelope), not a physical interference pattern.
2. The complex amplitude construction in `_quantum_avatar_modulation` is static (no evolution, no Schrödinger equation).
3. "Coherence" in King Wen is an emotional vector axis, not a wavefunction phase relationship.
4. No Born rule, no state overlap, no topological invariant in King Wen.
5. The bridge inserts a QuantumLab path but calculates its own fields (provenance issue).

---

## 6. Unresolved Questions

1. Is the complex amplitude construction in `_quantum_avatar_modulation` intended as a wavefunction or as an animation parameter?
2. What is the relationship between the 6 cosine harmonics and the 6 Yao lines?
3. Could the harmonic superposition be interpreted as a discrete Fourier series?
4. Is there a relationship between King Wen's coherence and quantum coherence (state overlap)?
5. What is the physical interpretation of the real/imag components in the wavefunction?

---

## 7. Evidence Provenance

- King Wen sources:
  - `scripts/bridge_quantumlab_visualization.py:100-130` (harmonic interference pattern)
  - `emotional_engine.py:471-570` (_quantum_avatar_modulation, complex amplitude construction)
  - `emotional_engine.py:741` (coherence computation from paired differentials)
  - `decision_matrix.py:340-360` (coherence threshold classification)
  - `generate_avatar_meshes.py:139, 181` (coherence in mesh deformation)
  - `full_hexagram_shotgun.py` (shotgun expansion, superposition of states)
- Quantum-Sim sources:
  - `examples/07_3d_double_slit.py:29-131` (physical interference pattern, fringe analysis)
  - `quantumlab/observables/current.py:35-40` (autocorrelation, state overlap)
  - `quantumlab/observables/current.py:52-90` (vortex positions, phase winding)
- Audit date: 2026-11-02
- Evidence level: E1 (lexical overlap) for "interference"/"coherence" terminology; E2 (conceptual) for complex amplitude construction and harmonic superposition; E3 (mathematical) NOT YET DEMONSTRATED
- Mathematical correspondence (E3): NOT YET DEMONSTRATED
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
