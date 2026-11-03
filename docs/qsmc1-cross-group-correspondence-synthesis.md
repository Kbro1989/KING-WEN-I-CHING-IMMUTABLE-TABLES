# QSMC-1 Cross-Group Correspondence Synthesis

**Research Gate:** QSMC-1
**Document Type:** Cross-group synthesis and evidence audit
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02
**Predecessor documents:** M1-Gaussian, M2-Expectation, M3-Hamiltonian, M4-Phase, M5-Angular-momentum/vortex, M6-Interference/coherence, M7-Evolution/propagation

---

## 1. Purpose and scope

This document synthesizes the evidence from the M1–M7 investigation cycle. It does not upgrade any individual disposition. Each mathematical object retains its own evidence record and disposition. M7's direct implementation reuse does not upgrade M3's Hamiltonian disposition or M6's coherence disposition.

**Gate 2 status:** OPEN — Producer unrecovered, No canonical authority assigned. M1–M7 completion does not alter Gate 2.

---

## 2. Master QSMC-1 ledger

| Group | Subject | Disposition | Established finding | Evidence level |
|---|---|---|---|---|
| M1 | Gaussian functions | `partial` | Shared kernel form exp(-(x-μ)²/(2σ²)) | E2 (conceptual) |
| M2 | Expectation / aggregation | `partial` conceptual | Shared weighted-summation kernel; different weight meaning | E2 (conceptual) |
| M3 | Hamiltonian / energy | `undetermined` | Three distinct entities sharing name "Hamiltonian" | E2 (conceptual) |
| M4 | Phase representations | `undetermined` | 8 discrete phases vs continuous complex phase | E2 (conceptual) |
| M5 | Angular momentum / vortex | `undetermined` | Operator vs scalar; shared difference-operation structure | E2 (conceptual) |
| M6 | Interference / coherence | `undetermined` | Wavefunction vs static construction; shared complex construction | E2 (conceptual) |
| M7 | Evolution / propagation | `undetermined` | Shared split-step Fourier method; different application | E2 (conceptual) + E3 (method-level) |

**All seven investigations are complete. Their mathematical correspondence dispositions remain unchanged.**

---

## 3. Evidence classification framework

Three kinds of findings emerged from the M1–M7 cycle:

### 3.1 Direct implementation reuse

| Group | Finding | Evidence |
|---|---|---|
| M7 | King Wen directly uses Quantum-Sim's split-step Fourier method (Strang splitting) | Source code: `psi = ifft(fft(psi * U_V) * U_T) * U_V` in both repos; identical mathematical structure |

### 3.2 Shared mathematical structures without established equivalence

| Group | Shared structure | King Wen | Quantum-Sim | Equivalence established? |
|---|---|---|---|---|
| M1 | Gaussian kernel form | `exp(-(x-μ)²/(2σ²))` | Same | No — domain, normalization, phase, dimensionality differ |
| M2 | Weighted-summation kernel | `sum(w_i*f_i)/sum(w_i)` | Same | No — weight meaning differs (Gaussian-tau vs Born-rule) |
| M6 | Complex amplitude construction | `sqrt(real²+imag²)` | Same | No — static construction vs evolved wavefunction |

### 3.3 Shared terminology or conceptual territory requiring further correspondence

| Group | Shared terminology | King Wen meaning | Quantum-Sim meaning | Correspondence established? |
|---|---|---|---|---|
| M3 | "Hamiltonian" | Scalar scoring function from paired differentials | Linear operator / nonlinear action (Schrödinger) | No — three distinct entities |
| M4 | "Phase" | 8 discrete categorical labels (past/present/future/...) | Continuous complex argument arg(ψ) mod 2π | No — discrete vs continuous |
| M5 | "Angular momentum"/"vortex" | Character-code arithmetic + index product + chaos composite | Physical L_z operator + topological charge | No — operator vs scalar |
| M6 | "Interference"/"coherence" | Static harmonic construction + emotional vector axis | Wavefunction superposition + state overlap | No — static vs physical |

---

## 4. All identified variables and formulas

### 4.1 King Wen variables (by group)

**M1 Gaussian:**
- `FWHM` (2.35482, 2.354820045)
- `sigma = FWHM / 2.35482`
- `mu` (center)
- `x` (input, discrete 0-7 or continuous)
- `temporal_gaussian` (scalar)

**M2 Expectation:**
- `512 states` (64 hexagrams × 8 phases)
- `w_i` (Gaussian-tau weights, renormalized)
- `f_i` (per-state values)
- `temporal_mode` (categorical)
- `porosity_mean`, `porosity_mode`
- `consensus_vector` (5 axes)
- `pool_weights` (0.7, 0.18, 0.12)
- `dominant_hexagram` (argmax selection)

**M3 Hamiltonian:**
- `resolved_vector` (5 axes)
- `expanded_vector` (5 axes)
- `line_balance` (6 line states)
- `momentum = [max(0.0, v) for v in resolved_vector]`
- `q_dot = [rv - ev for rv, ev in zip(resolved, expanded)]`
- `pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))`
- `dy = yang_r - yin_r` (signed)
- `yao_dy = yao - 3.0`
- `changing_dy = changing - (6 - changing)`
- `lagrangian = abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2`
- `H = _clamp(pq_dot - lagrangian)` → 0.0 for all states (scale mismatch)

**M4 Phase:**
- `phase_bits` (0-7, 3-bit)
- `PHASE_LINE_MAP` (phase → changing line indices)
- `PHASE_INFO` (phase → temporal label, polarity, description)
- `phase_temporal` (past/present/future/transition/resolution/dissolution/crystallization/void)
- `phase_bits × π/4` (rotation modulation)

**M5 Angular momentum / vortex:**
- `vortex_tension_1 = abs(char_code_sum_upper - char_code_sum_lower) / 360 × porosity × emotional`
- `vortex_tension_2 = (u_idx * l_idx) / 49.0`
- `vortex_tension_3 = 0.20 + 0.55 * chaos + 0.25 * darkTone`
- `rotation_modulation = hamiltonian * 0.35 * sin(phase_bits * π/4)`

**M6 Interference / coherence:**
- `yao_harmonics = sum(0.15 * cos((line_idx+1)*(X-x_center) + line_idx*T*0.5) for line_idx in range(6))`
- `envelope = exp(-((X-x_center)²)/(2*sig_t²))`
- `Z = envelope * (1.0 + 0.25 * sin(E*T*2.0) + yao_harmonics)`, clipped to [0,∞)
- `real_part = rv * temporal_gaussian`
- `imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)`
- `amplitude = sqrt(real_part² + imag_part²)`
- `coherence = clamp(yang_r * 0.3 - yao_dy * 0.3 - abs(old_dy) * 0.1)`

**M7 Evolution / propagation:**
- `U_V = exp(-1j * V * DT / (2*HBAR))`
- `U_T = exp(-1j * T_k * DT / HBAR)`
- `psi = ifft(fft(psi * U_V) * U_T) * U_V` (Strang splitting)
- `T_k = HBAR² * k² / (2*MASS)`
- `V = sum(sin(p*x/pi)/p for p in [97,89,83,79,73])`
- `momentum = (avg_chaos + avg_whimsy) / 2`
- `new_chaos = min(1.0, intent.emotional[0] + momentum * 0.1)`
- `future_weight = 0.3501` (Gaussian future projection)
- `mag = 4.689, theta = -1.429` (Mobius transformation)

### 4.2 Quantum-Sim variables (by group)

**M1 Gaussian:**
- `WaveFunction1D.gaussian()` (L2-normalized complex phase)
- `GaussianBarrier` (height-normalized potential)
- `sigma = FWHM / 2.35482`

**M2 Expectation:**
- `psi` (complex wavefunction)
- `O` (operator)
- `<O> = ∫ ψ* O ψ dx` (Born-rule expectation)
- `P = |ψ|²` (probability density)

**M3 Hamiltonian:**
- `Hψ = F⁻¹(T_k F(ψ)) + Vψ + g|ψ|²ψ`
- `T_k = ℏ²k²/(2m)` (kinetic energy)
- `V` (potential)
- `g` (nonlinear interaction coefficient)
- `ℏ` (reduced Planck constant)
- `m` (mass)

**M4 Phase:**
- `arg(ψ)` (continuous complex phase)
- `phase mod 2π`
- `phase winding` (topological charge, q ∈ ℤ)
- `phase separation` (BEC miscibility)

**M5 Angular momentum / vortex:**
- `L_z = -iℏ(x ∂_y - y ∂_x)` (angular momentum operator)
- `q = (1/2π) ∮ ∇φ · dl` (vortex topological charge)
- `H' = H - Ω L_z` (rotating frame)

**M6 Interference / coherence:**
- `ψ = real + i·imag` (complex wavefunction)
- `P = |ψ|²` (Born rule)
- `C(t) = ⟨ψ₀|ψₜ⟩` (autocorrelation, complex inner product)
- `phi_y = FFT(psi_T)` (momentum distribution)
- `fringe_pattern = |phi_y|²` (interference fringes)

**M7 Evolution / propagation:**
- `psi(t+dt) = exp(-i H dt / ℏ) psi(t)` (unitary propagator)
- `psi = ifft(fft(psi * U_V) * U_T) * U_V` (Strang splitting)
- `T_k = ℏ²k²/(2m)` (kinetic energy)
- `U_V = exp(-1j * V * dt / (2*ℏ))`
- `U_T = exp(-1j * T_k * dt / ℏ)`

---

## 5. Source-file references

### King Wen

| File | Key functions/variables | Lines |
|---|---|---|
| `emotional_engine.py` | `_hamiltonian_energy`, `_gaussian_kernel`, `_quantum_avatar_modulation`, `_compute_consensus_from_resolved`, `coherence` computation | 395-432, 458-470, 471-570, 741, 1083+ |
| `kingwen_ternary_tables_complete.py` | `HEXAGRAM_INJECTION_SITE`, `VOICEBOX_VOICE_POOL`, `YAO_VOCABULARY`, `PHASE_LINE_MAP`, `PHASE_INFO` | 79, 1013, 458+ |
| `scripts/full_hexagram_shotgun.py` | `shotgun_expand`, `expand_hexagram`, `_hamiltonian_energy` calls | 75, 141+ |
| `scripts/schauberger_parsing_layers.py` | `_vortex_tension` (3 formulas) | 96-124 |
| `scripts/bridge_desktop_3d_engines.py` | `vortex_tension` formula | 42 |
| `scripts/generate_sovereign_world.py` | `vortex_tension` formula, Godhead interference | 245-246, 1820-1885 |
| `scripts/prewarm_quantum_wavepackets.py` | Split-step Fourier (1D/2D/3D) | 1-200 |
| `scripts/bridge_quantumlab_visualization.py` | Harmonic interference pattern | 100-130 |
| `scripts/kingwen_mobius_sphere.py` | Mobius transformation, `_gaussian_bias_weight` | 827 |
| `scripts/kingwen_quantum_expand.py` | `_gaussian_kernel` | 33 |
| `scripts/kingwen_state_transition.py` | `_gaussian_kernel` | 195 |
| `src/core/pog3_hexagram_runtime_substrate.py` | Temporal momentum, save-string pellets | 318-325, 436-591 |
| `scripts/decision_matrix.py` | Coherence threshold | 340-360 |
| `scripts/generate_avatar_meshes.py` | Coherence in mesh deformation | 139, 181 |

### Quantum-Sim

| File | Key functions/variables | Lines |
|---|---|---|
| `quantumlab/solvers/split_operator.py` | `apply_hamiltonian`, Strang splitting | — |
| `quantumlab/observables/expectation.py` | `<O> = ∫ ψ* O ψ dx` | — |
| `quantumlab/observables/current.py` | `autocorrelation`, `vortex_positions` | 35-90 |
| `quantumlab/core/wavefunction.py` | `WaveFunction1D.gaussian()` | — |
| `quantumlab/potentials/barriers.py` | `GaussianBarrier` | — |
| `quantumlab/stationary.py` | Imaginary time evolution | — |
| `quantumlab/strongfield.py` | Strong-field evolution (SFA) | — |
| `examples/07_3d_double_slit.py` | Interference pattern, fringe analysis | 29-131 |

---

## 6. Mathematical object classifications

| Group | King Wen object | Quantum-Sim object | Classification |
|---|---|---|---|
| M1 | Gaussian kernel (scalar, FWHM parameterized) | Gaussian wavefunction/potential (L2/potential-height normalized) | Same functional form, different normalization/domain |
| M2 | 5-stage consensus pipeline (Gaussian-tau weights, argmax selection) | Born-rule expectation (probability-weighted observable) | Shared aggregation kernel, different weight semantics |
| M3 | Scalar energy scoring function from paired differentials | Hamiltonian operator (linear + nonlinear) | Different mathematical types (function vs operator) |
| M4 | 8 discrete categorical phase labels | Continuous complex phase (mod 2π, winding, separation) | Different (discrete vs continuous) |
| M5 | Character-code arithmetic + index product + chaos composite (scalar) | Physical L_z operator + topological charge (operator) | Different (scalar vs operator) |
| M6 | Static harmonic construction + emotional vector axis | Wavefunction superposition + state overlap | Different (static vs physical) |
| M7 | Split-step Fourier (pre-warming) + rule-based transitions | Schrödinger equation (unitary evolution) | Shared method (split-step), different application |

---

## 7. Numerical validation results

### M1 Gaussian
- King Wen: `exp(-(x-μ)²/(2σ²))` with FWHM=2.35482
- Quantum-Sim: Same form, L2-normalized or potential-height-normalized
- FWHM conversion (2.35482) is parameter conversion, not proof of equivalence
- Domain: King Wen (discrete 0-7) vs Quantum-Sim (continuous spatial)

### M2 Expectation
- King Wen: 5-stage pipeline, Gaussian-tau weights renormalized
- Quantum-Sim: Born-rule expectation ⟨O⟩ = ∫ ψ* O ψ dx
- Normalized weights can define a discrete probability measure, but that alone does not make it a Born-rule measure
- Shared weighted-summation kernel: `sum(w_i*f_i)/sum(w_i)`

### M3 Hamiltonian
- King Wen: H = clamp(pq_dot - lagrangian) → 0.0 for all 512 states (scale mismatch: pq_dot 0.005-0.013, lagrangian 2.1-5.1)
- Quantum-Sim: Hψ = F⁻¹(T_k F(ψ)) + Vψ + g|ψ|²ψ
- Three entities sharing name "Hamiltonian": function, scalar, operator
- Quantum-Sim nonlinear term: complete expression is nonlinear when g≠0 (Gross-Pitaevskii-type)

### M4 Phase
- King Wen: 8 discrete values (0-7) with categorical labels
- Quantum-Sim: continuous arg(ψ) mod 2π, phase winding (topological charge q ∈ ℤ), phase separation
- No defined mapping between discrete labels and continuous phase

### M5 Angular momentum / vortex
- King Wen: 3 vortex_tension formulas (char-code arithmetic, index product, chaos/darkTone composite)
- Quantum-Sim: L_z expectation, vortex topological charge, rotating frame
- Shared: difference operation, normalization by scale, trigonometric rotation, composite scoring, clamping

### M6 Interference / coherence
- King Wen: 6 real cosine harmonics + Gaussian envelope + energy modulation; static complex amplitude construction
- Quantum-Sim: FFT of complex wavefunction → momentum distribution → fringes; Born rule; autocorrelation; topological invariant
- Shared: complex amplitude construction, trigonometric superposition, phase as parameter, energy modulation

### M7 Evolution / propagation
- King Wen: Split-step Fourier (pre-warming, 3 steps); rule-based state transition; Mobius transformation; Gaussian projection; combinatorial expansion
- Quantum-Sim: Schrödinger equation (unitary, norm-conserving); split-step Fourier; imaginary time; strong-field
- Shared: split-step Fourier algorithm (Strang splitting), normalization, complex exponentials, FFT/IFFT

---

## 8. Unresolved correspondence questions (by group)

### M1
1. Are the 4 King Wen Gaussian implementations related to each other or independently derived?
2. What is the relationship between King Wen's FWHM=2.35482 and Quantum-Sim's FWHM conventions?

### M2
1. Are all weights finite and nonnegative?
2. Are the 512 records statistically independent or deterministically related?
3. Does changing aggregation order change the outcome?
4. Is the argmax selection (stage 5) a form of expectation or a different operation?

### M3
1. Is the Hamiltonian zero an implementation defect or a design choice?
2. What is the relationship between paired differentials and kinetic/potential/nonlinear terms?
3. Can the scalar be reformulated as an operator without changing the canonical engine?
4. What are the units of the King Wen Hamiltonian?

### M4
1. Is there a defined mapping between 8 discrete phases and continuous phase?
2. What is the relationship between phase_bits × π/4 and quantum phase rotation?
3. Are the 8 phases 8 samples of a continuous phase?

### M5
1. What is the relationship between the 3 vortex_tension formulas?
2. Can the character-code arithmetic be related to physical angular momentum?
3. Is the vortex_tension a physical quantity or a visualization parameter?

### M6
1. Is the complex amplitude construction intended as a wavefunction or animation parameter?
2. What is the relationship between the 6 cosine harmonics and the 6 Yao lines?
3. Could the harmonic superposition be interpreted as a discrete Fourier series?

### M7
1. Is the split-step Fourier pre-warming intended as physical evolution or visualization?
2. What is the relationship between the state transition rule and differential equations?
3. Could the Mobius transformation be interpreted as a time evolution operator?
4. Is the Gaussian future projection related to imaginary time evolution?
5. What is the physical interpretation of the combinatorial expansion?

---

## 9. M7 additional validation questions (from external assessment)

1. **Algorithm provenance:** Can the shared Strang-splitting implementation be traced to a specific Quantum-Sim source revision?
2. **Numerical equivalence:** Do both implementations produce equivalent outputs under identical grids, potentials, initial conditions, and time steps?
3. **Normalization:** Is normalization performed once, periodically, or after every propagation step?
4. **Unitarity:** Does the King Wen pre-warming implementation preserve norm without relying on corrective renormalization?
5. **Potential construction:** What are the mathematical properties of the coprime-frequency potential compared with Quantum-Sim's physical potentials?

---

## 10. Gate 2 restrictions

**Gate 2: OPEN**

| Requirement | Status |
|---|---|
| Producer recovered | No |
| Canonical authority | Unassigned |
| Authority lineage | Unresolved |
| M1–M7 completion | Complete |

**Gate 2 restrictions (carried forward):**
- No normalization between hexagrams
- No inferred uncertainty weighting
- No silent replacement of Hamiltonian zeros
- No Gate 2 closure by implication
- No formula, scale, sign, or clamping changes to force nonzero Hamiltonian values
- No cross-hexagram normalization
- Tests must not encode observations as permanent design decisions
- Identity test must invoke canonical producer directly, not read from previously generated dataset
- Consumer acceptance criteria must be explicit beyond import success

**M1–M7 completion does not alter Gate 2.**

---

## 11. What the combined evidence establishes

### 11.1 Direct implementation reuse (strongest finding)

M7 split-step Fourier: King Wen directly uses Quantum-Sim's numerical method (Strang splitting) with identical mathematical structure. This is an implementation-level relationship, not just terminology.

### 11.2 Shared mathematical structures (moderate finding)

M1 Gaussian kernel form: Same functional form `exp(-(x-μ)²/(2σ²))`. M2 weighted-summation kernel: Same aggregation structure. M6 complex amplitude construction: Same `sqrt(real²+imag²)`. These are shared at the formula level.

### 11.3 Shared terminology/conceptual territory (weakest finding)

M3 "Hamiltonian", M4 "Phase", M5 "Angular momentum/vortex", M6 "Interference/coherence": Shared names but different mathematical objects. These require further correspondence investigation.

### 11.4 What the evidence does NOT establish

1. Physical equivalence between any King Wen and Quantum-Sim quantity
2. That shared terminology implies shared mathematical meaning
3. That shared algorithm implies identical numerical behavior
4. That any disposition should be upgraded based on another group's finding
5. That Gate 2 should be closed

---

## 12. Next steps

1. **Do not create M8.** The M1–M7 cycle is complete.
2. **Conduct second-pass audits** using the corrected methodology for groups where evidence is thin (M3, M4, M5, M6).
3. **Address the five M7 validation questions** (algorithm provenance, numerical equivalence, normalization, unitarity, potential construction).
4. **Resolve the three Gate 2 decisions** (canonical representation, Path A vs B, invalid-input semantics) — these are independent of QSMC-1.
5. **Preserve all seven individual evidence records** as independent documents.

---

## 13. Evidence provenance

- Individual evidence records:
  - `docs/qsmc1-m1-gaussian-kernel-correspondence.md` (352 lines)
  - `docs/qsmc1-m2-expectation-consensus-correspondence.md` (352 lines)
  - `docs/qsmc1-m3-hamiltonian-energy-correspondence.md` (400+ lines)
  - `docs/qsmc1-m4-phase-representations-correspondence.md` (293 lines)
  - `docs/qsmc1-m5-angular-momentum-vortex-correspondence.md` (371 lines)
  - `docs/qsmc1-m6-interference-coherence-correspondence.md` (361 lines)
  - `docs/qsmc1-m7-evolution-propagation-correspondence.md` (361 lines)
- Framework document: `docs/qsmc1-quantum-sim-mathematical-correspondence-audit.md` (352 lines)
- Audit date: 2026-11-02
- Evidence level: E1 (lexical), E2 (conceptual), E3 (mathematical — NOT YET DEMONSTRATED for any group)
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
