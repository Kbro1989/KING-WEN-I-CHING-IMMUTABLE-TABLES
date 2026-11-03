# M4 Phase Representations Correspondence Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M4-PHASE-REPRESENTATIONS
**Mathematical Object:** Phase
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02

---

## 1. King Wen Implementation

### Source: `kingwen_ternary_tables_complete.py:53-72` (PHASE_LINE_MAP and PHASE_INFO)

```python
PHASE_LINE_MAP: Final[Dict[int, List[int]]] = {
    0b000: [],
    0b001: [0, 1],
    0b010: [2, 3],
    0b011: [0, 1, 2, 3],
    0b100: [4, 5],
    0b101: [0, 1, 4, 5],
    0b110: [2, 3, 4, 5],
    0b111: [0, 1, 2, 3, 4, 5],
}

PHASE_INFO: Final[Dict[int, Dict[str, Any]]] = {
    0b000: {"temporal": "past",            "polarity": "yin",        "description": "completed, resolved, memory"},
    0b001: {"temporal": "present",         "polarity": "yang",       "description": "active, manifest, now"},
    0b010: {"temporal": "future",          "polarity": "yao",        "description": "potential, emerging, becoming"},
    0b011: {"temporal": "transition",      "polarity": "yin-yang",   "description": "changing, flux, threshold"},
    0b100: {"temporal": "resolution",      "polarity": "yang-yin",   "description": "settling, clarity, convergence"},
    0b101: {"temporal": "dissolution",     "polarity": "yin-yao",    "description": "breaking, releasing, dispersal"},
    0b110: {"temporal": "crystallization", "polarity": "yang-yao",   "description": "forming, condensing, structure"},
    0b111: {"temporal": "void",            "polarity": "yao-yao",    "description": "null, reset, origin"},
}
```

### King Wen Phase Summary

| Property | Value |
|---|---|
| Phase encoding | 3-bit integer (0-7), binary |
| Phase count | 8 |
| Phase temporal | Categorical label: past, present, future, transition, resolution, dissolution, crystallization, void |
| Phase polarity | Categorical label: yin, yang, yao, yin-yang, yang-yin, yin-yao, yang-yao, yao-yao |
| Phase description | Human-readable semantic label |
| Changing lines | PHASE_LINE_MAP maps phase_bits to list of line indices (0-5) that change |
| Phase bits encoding | 3 bits represent which of 6 lines are in "changing" state |
| Continuous phase | Absent -- no angular variable, no modulo 2π |
| Phase as function | Phase is a classification label, not a continuous coordinate |
| Phase in evolution | Not used as evolution parameter -- phase is a state index |
| Phase in Gaussian | `_gaussian_kernel(float(phase_bits), phase_center, 2.5)` -- phase_bits treated as discrete numeric input to Gaussian |
| Phase in rotation | `rotation_x = hamiltonian * 0.35 * sin(phase_bits * pi/4)` -- phase_bits treated as discrete angle (pi/4 steps) |

### Additional phase concepts in King Wen (from prior audit)

Four distinct "phase" concepts were identified in the earlier audit:

1. **Canonical temporal phase** (3-bit, 0-7, discrete): PHASE_INFO temporal labels (past/present/future/etc.)
2. **Visualization oscillator phase** (continuous angular): Godhead interference formula `phase = presentTime * (qwpFundHz / 108.0) * 1.5 + sIdx * 0.098`
3. **Wave-packet simulation phase** (continuous time): split-step Fourier dt=0.02, coprime frequencies
4. **Acoustic signal phase** (frequency Hz): audio pellet carrier frequency [80, 8000] Hz (MAP-002)

No demonstrated semantic link between any pair.

---

## 2. Quantum-Sim Implementation

### Source: `quantumlab/observables/current.py` and examples

Quantum-Sim uses phase in multiple distinct ways:

### 2.1 Wavefunction phase (arg ψ)

```python
phase = np.angle(wf.psi)  # continuous, modulo 2π
```

**Operation:** Element-wise complex argument of the wavefunction.
**Mathematical type:** Continuous function φ(x) = arg(ψ(x)), defined modulo 2π.
**Range:** [-π, π] (or [0, 2π)).
**Physical meaning:** Quantum mechanical phase of the wavefunction.

### 2.2 Phase winding (vortices)

```python
circulation = wrapped(phase[:-1, :-1], phase[1:, :-1]) + ...
charge = np.rint(circulation / (2.0 * np.pi)).astype(int)
```

**Operation:** Discrete topological charge from phase winding around plaquettes.
**Mathematical type:** Integer (winding number q ∈ ℤ).
**Physical meaning:** Quantized vortex charge (topological invariant).

### 2.3 Phase in evolution

In split-step Fourier evolution, phase accumulates as:
- Kinetic phase: exp(-i T_k Δt / ℏ)
- Potential phase: exp(-i V Δt / ℏ)

**Operation:** Continuous phase accumulation in time evolution.
**Mathematical type:** Complex exponential phase factor.
**Physical meaning:** Time evolution of quantum state.

### 2.4 Phase separation (BEC)

```python
# Two-component BEC: phase separation when g_12/g > 1
ax.set_title(f'g_12/g = {r} ({"miscible" if r < 1 else "phase separated"})')
```

**Operation:** Binary classification based on interaction strength ratio.
**Mathematical type:** Threshold comparison (r < 1 vs r ≥ 1).
**Physical meaning:** Miscible vs phase-separated condensate.

### Quantum-Sim Phase Summary

| Property | Value |
|---|---|
| Phase encoding | Continuous complex argument arg(ψ) |
| Phase range | [-π, π) (modulo 2π) |
| Phase type | Continuous function of spatial coordinates |
| Phase winding | Quantized topological charge (integer) |
| Phase in evolution | Continuous time-dependent phase accumulation |
| Phase separation | Binary threshold (miscible/phase-separated) |
| Discrete phase | Absent -- no discrete phase classification |
| Phase as function | Phase is a continuous coordinate, not a state index |

---

## 3. Comparison

### 3.1 Structural comparison

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Phase encoding | 3-bit integer (0-7) | Continuous arg(ψ) ∈ [-π, π) |
| Phase count | 8 discrete values | Uncountably infinite (continuous) |
| Phase type | Categorical label (past/present/future/etc.) | Continuous function of space |
| Phase meaning | Temporal classification of state | Quantum mechanical phase of wavefunction |
| Phase in Gaussian | Discrete numeric (phase_bits as float) | Continuous (phase as function argument) |
| Phase in rotation | Discrete angle (phase_bits × π/4) | Continuous rotation (Ω L_z) |
| Phase winding | Absent | Quantized topological charge |
| Phase evolution | Absent (phase is state index, not evolution parameter) | Continuous time-dependent accumulation |
| Modulo 2π | Absent | Present (phase is periodic) |
| Information preservation | Not defined | Phase winding is topological invariant |

### 3.2 What IS structurally similar

1. **Phase as a state property**: Both systems associate a phase with each state. King Wen: phase_bits 0-7. Quantum-Sim: arg(ψ(x)).

2. **Phase in Gaussian kernel**: King Wen uses `phase_bits` as a numeric input to `_gaussian_kernel(float(phase_bits), phase_center, 2.5)`. Quantum-Sim uses phase in wavefunction construction. Both use phase as a parameter in a Gaussian-related computation.

3. **Phase in rotation**: King Wen uses `phase_bits * pi/4` as a discrete rotation angle. Quantum-Sim uses continuous rotation operator. Both use phase to modulate rotation.

### 3.3 What is NOT the same

1. **Discrete vs continuous**: King Wen has 8 discrete phases. Quantum-Sim has continuous phase modulo 2π. These are fundamentally different mathematical objects.

2. **Categorical vs functional**: King Wen's phase is a categorical label (past/present/future/etc.). Quantum-Sim's phase is a continuous function of spatial coordinates.

3. **No modulo 2π in King Wen**: King Wen's phase_bits is an integer 0-7, not a periodic angle. There is no wraparound or periodicity.

4. **No phase winding in King Wen**: Quantum-Sim has quantized topological charge from phase winding (vortices). King Wen has no analogous topological invariant.

5. **No phase evolution in King Wen**: Quantum-Sim's phase evolves continuously in time via split-step Fourier. King Wen's phase is a static state index.

6. **Phase as state index vs phase as coordinate**: In King Wen, phase_bits is part of the state identity (hexagram_id, phase_bits). In Quantum-Sim, phase is a property of the wavefunction at each spatial point.

7. **No defined mapping**: No source code defines a mapping from King Wen's 8 phases to Quantum-Sim's continuous phase. The 8 phases are not 8 samples of a 2π range.

---

## 4. Mathematical Correspondence Assessment

### 4.1 Three King Wen phase concepts (from prior audit)

The earlier audit identified four distinct "phase" concepts in King Wen:

1. **Canonical temporal phase** (3-bit, 0-7, discrete): PHASE_INFO temporal labels
2. **Visualization oscillator phase** (continuous angular): Godhead interference formula
3. **Wave-packet simulation phase** (continuous time): split-step Fourier dt=0.02
4. **Acoustic signal phase** (frequency Hz): audio pellet carrier frequency [80, 8000] Hz

No demonstrated semantic link between any pair. The canonical temporal phase (concept 1) is the one used in the 512-state expansion and is the subject of this M4 investigation.

### 4.2 Five Quantum-Sim phase concepts

1. **Wavefunction phase** (arg ψ): continuous, modulo 2π, function of space
2. **Phase winding** (vortices): quantized topological charge (integer)
3. **Evolution phase**: continuous time-dependent phase accumulation
4. **Phase separation** (BEC): binary threshold (miscible/phase-separated)
5. **Relative phase** (soliton collision): Δφ = 0 vs π

### 4.3 Kernel-level

Both systems use phase as a parameter in computations. King Wen: `phase_bits` as numeric input to Gaussian and rotation. Quantum-Sim: `arg(ψ)` as phase in wavefunction construction. Both use phase as a mathematical quantity in formulas.

**Status: Shared at the parameter level.**

### 4.4 Implementation-level

The phase representations are fundamentally different:
- Quantum-Sim: continuous function φ(x) = arg(ψ(x)) on spatial domain, modulo 2π
- King Wen: 3-bit integer 0-7, categorical label, state index

No defined mapping between 8 discrete phases and continuous phase modulo 2π.

**Status: NOT ESTABLISHED.**

### 4.5 Application-level

King Wen's phase classifies temporal state (past/present/future/etc.). Quantum-Sim's phase describes quantum mechanical wavefunction phase. Different mathematical roles.

**Status: Partial conceptual relationship.**

### 4.6 Disposition

**M4-PHASE-REPRESENTATIONS: `undetermined`**

The King Wen phase is a discrete 3-bit classification (8 values) with categorical labels. The Quantum-Sim phase is a continuous function modulo 2π. They share the word "phase" but represent different mathematical objects. No mapping from 8 discrete phases to continuous phase has been defined or demonstrated.

The eight King Wen phase values must not be treated as eight samples of quantum phase unless the source code defines such a mapping.

### 4.7 Three-Level Distinction

| Level | King Wen | Quantum-Sim | Status |
|---|---|---|---|
| Kernel-level | Phase as parameter in Gaussian/rotation formulas | Phase as parameter in wavefunction construction | SHARED -- both use phase as mathematical quantity |
| Implementation-level | 3-bit integer 0-7, categorical, state index | Continuous arg(ψ) ∈ [-π,π), function of space | NOT ESTABLISHED -- discrete vs continuous |
| Application-level | Temporal state classification (past/present/future) | Quantum mechanical wavefunction phase | PARTIAL CONCEPTUAL -- both describe "phase" |

### 4.8 Audit dimensions

| Audit dimension | Question | King Wen | Quantum-Sim |
|---|---|---|---|
| Representation | Discrete or continuous? | Discrete (3-bit, 0-7) | Continuous (arg ψ, modulo 2π) |
| Domain | What is the input space? | State index (hexagram, phase) | Spatial coordinates x |
| Codomain | What is the output? | Categorical label + polarity | Real number in [-π, π) |
| Periodicity | Is phase periodic? | No (0-7, no wraparound) | Yes (modulo 2π) |
| Topological invariant | Is there a winding number? | No | Yes (vortex charge q ∈ ℤ) |
| Evolution | Does phase evolve in time? | No (static state index) | Yes (continuous accumulation) |
| Information preservation | Is phase reversible? | Not defined | Phase winding is topological invariant |
| Mapping | Is there a defined mapping between representations? | No | N/A (different system) |

### 4.9 What would be needed to upgrade to `defined`

1. A formal definition of the mapping from King Wen's 8 phases to Quantum-Sim's continuous phase (if one exists).
2. A demonstration that the 8 phases correspond to 8 samples of a 2π range (or another defined subset).
3. A specification of the relationship between PHASE_LINE_MAP (which lines change) and phase winding (topological charge).
4. Reproducible numerical validation showing that phase-dependent computations produce corresponding results.

### 4.10 What would make it `incompatible`

1. If the 8 phases were found to be purely categorical with no continuous interpretation.
2. If the phase encoding were found to be structurally incompatible with modulo 2π (e.g., non-periodic, non-ordered).
3. If the phase information were found to be lossy or non-invertible.

---

## 5. Known Limitations

1. King Wen has four distinct "phase" concepts with no demonstrated semantic link. This M4 investigation addresses only the canonical temporal phase (concept 1).
2. The Godhead interference formula uses a continuous phase that may or may not relate to the canonical temporal phase.
3. The wave-packet simulation uses continuous time, which may or may not relate to the discrete phase.
4. The acoustic signal phase uses frequency Hz, which may or may not relate to either.
5. Quantum-Sim's phase is defined on spatial grids, not on abstract state indices. No bridge between spatial coordinates and hexagram/phase indices exists.

---

## 6. Unresolved Questions

1. Is the King Wen phase purely categorical, or does it encode a continuous quantity?
2. Does the 3-bit phase encoding have a natural interpretation as 3 binary flags (past/present/future)?
3. What is the relationship between PHASE_LINE_MAP (which lines change) and phase winding (topological charge)?
4. Could the 8 phases be mapped to 8 points on a circle (e.g., octants of 2π)?
5. Is there a continuous interpolation between King Wen phases?

---

## 7. Evidence Provenance

- King Wen source: `kingwen_ternary_tables_complete.py:53-72` (PHASE_LINE_MAP, PHASE_INFO, canonical, revision 71fbf28f8e92c6a7de74c50a304906ef81963a7d)
- King Wen additional: `emotional_engine.py:207-220` (_line_state_balance, phase_bits usage); `emotional_engine.py:490-570` (_quantum_avatar_modulation, phase in Gaussian and rotation)
- Quantum-Sim source: `quantumlab/observables/current.py:1-120` (vortices, phase winding, arg ψ); examples 08, 09, 11, 13 (phase visualization, soliton collision, BEC phase separation)
- Prior audit: `docs/yao-line-semantic-audit-2026-10-29.md` Section on phase terminology (4 concepts identified)
- Audit date: 2026-11-02
- Evidence level: E1 (lexical overlap) for "phase" terminology; E2 (conceptual) for phase as parameter; E3 (mathematical) NOT YET DEMONSTRATED
- Mathematical correspondence (E3): NOT YET DEMONSTRATED
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
