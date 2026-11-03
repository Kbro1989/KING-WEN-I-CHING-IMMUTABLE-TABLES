# M7 Source Provenance Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M7-PROVENANCE
**Document Type:** Source provenance audit (second-pass verification, Priority 1)
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02
**Baseline:** `docs/qsmc1-cross-group-correspondence-synthesis.md` (frozen)
**Individual evidence record:** `docs/qsmc1-m7-evolution-propagation-correspondence.md`

---

## 1. Purpose

This document traces the exact source lineage of the shared split-step Fourier implementation between King Wen and Quantum-Sim. It is a **second-pass verification** artifact that supplements (does not modify) the original M7 evidence record.

**Baseline rule:** The original M7 disposition (`undetermined`) and its evidence record are frozen. This document records new provenance evidence alongside, not as a replacement.

---

## 2. Provenance timeline

### 2.1 Quantum-Sim (source)

| Property | Value |
|---|---|
| Repository | `rasidi3112/quantum-simulation` (forked to `Kbro1989/quantum-simulation`) |
| File | `quantumlab/solvers/split_step_1d.py` |
| Author | rasidi3112 (`macbook@Rasidi-MacBook-Pro.local`) |
| Commit | `c17817f` ("feat: Modularize framework (Phase 11, 1, 4, 5)") |
| Date | 2026-06-14 12:05:01 +0700 |
| License | MIT |
| Co-author | Kbro1989 (accepted contributions, listed in CITATION.cff) |

**Implementation (class-based, reusable):**
```python
class SplitStep1DSolver(Solver):
    def update_operators(self):
        self.U_V = np.exp(-1j * self.V * self.dt / (2.0 * self.hbar))
        self.U_T = np.exp(-1j * self.T_k * self.dt / self.hbar)
    def step(self, wavefunction):
        psi = wavefunction.psi.copy()
        psi *= self.U_V
        psi_k = fft(psi)
        psi_k *= self.U_T
        psi = ifft(psi_k)
        psi *= self.U_V
        return WaveFunction1D(self.grid, psi)
```

### 2.2 King Wen (consumer)

| Property | Value |
|---|---|
| Repository | `Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES` |
| File | `scripts/prewarm_quantum_wavepackets.py` |
| Author | Kbro (`kristain33rs@gmail.com`) |
| Commit | `2548ba170d` ("feat(quantum): add 1D->2D->3D wave packet pre-warming, DA-V2 depth relief, 512-avatar meshes, and updated docs") |
| Date | 2026-08-29 11:56:31 -0500 |
| Docstring | `"King Wen x QuantumLab -- Wave Packet Pre-Warming Engine"` |

**Implementation (inline, functional):**
```python
# 1D
U_V = np.exp(-1j * V * DT / (2.0 * HBAR))
U_T = np.exp(-1j * T_k * DT / HBAR)
psi = np.exp(-(x**2) / (4.0*0.5**2)) * np.exp(1j * 1.0 * x)
psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)
for _ in range(WARMUP_STEPS):
    psi = ifft(fft(psi * U_V) * U_T) * U_V

# 2D
psi = ifft2(fft2(psi * U_V) * U_T) * U_V

# 3D
psi = ifftn(fftn(psi * U_V) * U_T) * U_V
```

### 2.3 Temporal ordering

| Event | Date | Actor |
|---|---|---|
| Quantum-Sim split-step solver created | 2026-06-14 | rasidi3112 |
| King Wen pre-warming script added | 2026-08-29 | Kbro |
| King Wen bridge script created | 2026-08-29 (same commit) | Kbro |

**Temporal ordering confirmed:** Quantum-Sim implementation (June 14) precedes King Wen implementation (August 29) by 76 days. The King Wen implementation could not have been created before the Quantum-Sim implementation existed.

---

## 3. Explicit provenance evidence

### 3.1 Docstring reference

`scripts/prewarm_quantum_wavepackets.py:2`:
```python
"King Wen x QuantumLab -- Wave Packet Pre-Warming Engine"
```

Explicitly names "QuantumLab" (Quantum-Sim's framework name) as the co-authoring system.

### 3.2 Bridge script path reference

`scripts/bridge_quantumlab_visualization.py:23`:
```python
QUANTUMLAB_DIR = (Path.home() / "Desktop" / "quantum-simulation-main/quantum-simulation-main")
```

The bridge script directly references the Quantum-Sim repository path on disk. It imports `quantumlab` (confirmed at line 331-332 in the manifest output).

### 3.3 Structural correspondence

| Element | Quantum-Sim (`SplitStep1DSolver`) | King Wen (`prewarm_quantum_wavepackets.py`) | Match |
|---|---|---|---|
| Potential operator | `U_V = exp(-1j * V * dt / (2*hbar))` | `U_V = np.exp(-1j * V * DT / (2.0 * HBAR))` | Identical form |
| Kinetic operator | `U_T = exp(-1j * T_k * dt / hbar)` | `U_T = np.exp(-1j * T_k * DT / HBAR)` | Identical form |
| Strang splitting | `psi *= U_V; psi_k = fft(psi); psi_k *= U_T; psi = ifft(psi_k); psi *= U_V` | `psi = ifft(fft(psi * U_V) * U_T) * U_V` | Identical (composed) |
| Normalization | `psi /= sqrt(sum(|psi|²) * dx)` | `psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)` | Identical |
| Time step | `dt` (configurable) | `DT = 0.02` (hardcoded) | Same concept, different value |
| Grid | `grid.k` (configurable) | `k = 2*pi*fftfreq(N1, dx)` | Same computation |
| Potential | Physical V(x) | Coprime-frequency sum `_kw_pot_1d` | Different potential |
| Grid size | Configurable (128×96×96) | Fixed (64, 8×8, 9×9×9) | Different scale |

### 3.4 Key differences (not shared)

| Element | Quantum-Sim | King Wen |
|---|---|---|
| Potential function | Physical (harmonic, Gaussian barrier, etc.) | Coprime-frequency sum `sin(p*x/pi)/p` |
| Grid size | Large (128×96×96) | Small (64, 8×8, 9×9×9) |
| Time steps | Variable (user-configurable) | Fixed 3 warmup steps |
| Architecture | Class-based (`SplitStep1DSolver`) | Inline functional |
| Physical constants | Configurable (ℏ, m) | Hardcoded (HBAR=1.0, MASS=1.0) |
| Boundary conditions | Configurable | Periodic (implicit FFT) |
| Evolution loop | Variable number of steps | Fixed 3 steps |
| Purpose | Physical quantum evolution | Pre-warming for avatar animation |

---

## 4. Provenance conclusion

### 4.1 Source lineage: ESTABLISHED

The shared split-step Fourier implementation is **directly derived** from Quantum-Sim:

1. **Temporal ordering**: Quantum-Sim implementation (June 14, 2026) predates King Wen implementation (August 29, 2026) by 76 days
2. **Explicit reference**: King Wen docstring names "QuantumLab" and bridge script references Quantum-Sim repository path
3. **Structural identity**: Identical Strang splitting formula, identical normalization, identical complex exponential phase factors
4. **Author overlap**: Kbro (King Wen author) is co-author of Quantum-Sim (accepted contributions, listed in CITATION.cff)

### 4.2 What provenance establishes

- The split-step Fourier algorithm in King Wen is **not independently derived**
- The mathematical method (Strang splitting) is **directly reused** from Quantum-Sim
- The potential function, grid size, and time parameters are **King Wen-specific adaptations**
- The application context (pre-warming for avatar animation vs physical quantum evolution) is **different**

### 4.3 What provenance does NOT establish

- Physical equivalence between King Wen's pre-warming and Quantum-Sim's evolution
- That the coprime-frequency potential has the same mathematical properties as physical potentials
- That the fixed 3-step warmup produces the same numerical results as variable-step evolution
- That the small grids (64, 8×8, 9×9×9) produce the same accuracy as large grids (128×96×96)

### 4.4 M7 disposition impact

**No change to M7 disposition.** The original M7 evidence record remains `undetermined` with the finding "Shared numerical method, different application." This provenance document adds:

- **Algorithm provenance: ESTABLISHED** (direct reuse from Quantum-Sim, not independently derived)
- **Implementation-level correspondence: STRENGTHENED** (identical formula, not just similar)
- **Application-level correspondence: UNCHANGED** (pre-warming vs physical evolution)

The provenance upgrade applies to the **algorithm-level** evidence only. It does not upgrade the M7 disposition to `defined` because:
1. The application context differs (pre-warming vs physical evolution)
2. The potential functions differ (coprime-frequency vs physical)
3. The grid sizes differ (small vs large)
4. No numerical equivalence has been demonstrated

### 4.5 Next step: M7 numerical equivalence testing

The five M7 validation questions from the external assessment remain open:

1. **Algorithm provenance**: ✅ ESTABLISHED (this document)
2. **Numerical equivalence**: ❓ NOT YET TESTED — requires controlled matched-condition test
3. **Normalization**: ❓ NOT YET TESTED — once, periodically, or after every step?
4. **Unitarity**: ❓ NOT YET TESTED — does pre-warming preserve norm without corrective renormalization?
5. **Potential construction**: ❓ NOT YET TESTED — mathematical properties of coprime-frequency potential vs physical potentials

---

## 5. Evidence provenance

- Quantum-Sim source: `quantumlab/solvers/split_step_1d.py` (commit c17817f, 2026-06-14, rasidi3112)
- King Wen source: `scripts/prewarm_quantum_wavepackets.py` (commit 2548ba170d, 2026-08-29, Kbro)
- Bridge source: `scripts/bridge_quantumlab_visualization.py:23` (QUANTUMLAB_DIR reference)
- Audit date: 2026-11-02
- Evidence level: E3 (mathematical correspondence at method level) — upgraded from E2
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
- Baseline rule: Original M7 disposition (`undetermined`) preserved. This document is supplementary evidence, not a modification.
