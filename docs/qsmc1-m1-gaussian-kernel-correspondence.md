# M1 Gaussian Kernel Correspondence Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M1-GAUSSIAN-KERNEL
**Mathematical Object:** Gaussian kernel / Gaussian function
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02

---

## 1. King Wen Implementation

### Source 1: emotional_engine.py (canonical engine)

```python
# emotional_engine.py:458
def _gaussian_kernel(value: float, center: float, fwhm: float) -> float:
    """f(x) = a * exp(-(x - b)^2 / (2c^2))

    a=1 normalized. c = FWHM / (2*sqrt(2*ln 2)) ≈ FWHM/2.35482.
    Source: Gaussian function wiki parse.
    """
    if fwhm <= 1e-9:
        return 1.0 if value == center else 0.0
    c = fwhm / 2.3548200
    exponent = -((value - center) ** 2) / (2.0 * c * c)
    return math.exp(exponent)
```

**Usage (emotional_engine.py:505):**
```python
temporal_gaussian = _gaussian_kernel(float(phase_bits), phase_center, 2.5)
```
- `value` = phase_bits (0-7, integer as float)
- `center` = 1.0 (present phase)
- `fwhm` = 2.5 (hardcoded)

### Source 2: kingwen_quantum_expand.py

```python
# scripts/kingwen_quantum_expand.py:33
def _gaussian_kernel(value: float, center: float, fwhm: float) -> float:
    sigma = fwhm / 2.354820045
    diff = value - center
    return np.exp(-(diff * diff) / (2.0 * sigma * sigma))
```

### Source 3: kingwen_state_transition.py

```python
# scripts/kingwen_state_transition.py:195
def gaussian_kernel(value: float, center: float, fwhm: float) -> float:
    """Gaussian bell used for future-phase bias."""
    sigma = fwhm / 2.354820045
    diff = value - center
    return math.exp(-(diff * diff) / (2.0 * sigma * sigma))
```

### Source 4: kingwen_mobius_sphere.py

```python
# scripts/kingwen_mobius_sphere.py:827
def _gaussian_bias_weight(phase: int, fwhm: float) -> float:
    # (not shown in detail; called from _gaussian_future_transition)
    bias = [_gaussian_bias_weight(p, fwhm) for p in phases]
```

### King Wen Gaussian Summary

| Property | Value |
|---|---|
| Formula | `exp(-((x - b)^2) / (2 * c^2))` where `c = FWHM / 2.35482` |
| Amplitude | 1.0 (unnormalized, peak = 1.0) |
| Normalization | None (peak-normalized, not area-normalized) |
| Input domain | `value` = phase_bits (0-7, integer), `center` = 1.0 (present phase), `fwhm` = 2.5 |
| FWHM-to-sigma | `sigma = FWHM / 2.354820045` (where 2.35482 = 2*sqrt(2*ln(2))) |
| Edge case | `fwhm <= 1e-9`: returns 1.0 if value==center else 0.0 |
| Usage context | Temporal phase bias: phases ~2 away from present get ~50% modulation |
| Purpose | Phase-weighted modulation of quantum avatar wavefunction |

---

## 2. Quantum-Sim Implementation

### Source 1: Gaussian wave packet (wavefunction.py)

```python
# quantumlab/core/wavefunction.py:35
@classmethod
def gaussian(cls, grid: Grid1D, x0: float, k0: float, sigma: float) -> 'WaveFunction1D':
    psi = np.exp(-(grid.x - x0) ** 2 / (4.0 * sigma ** 2)) * np.exp(1j * k0 * grid.x)
    wf = cls(grid, psi)
    wf.normalize()
    return wf
```

**Formula:** `psi(x) = exp(-(x - x0)^2 / (4 * sigma^2)) * exp(i * k0 * x)`

**Note:** The exponent uses `4 * sigma^2` (not `2 * sigma^2`), which corresponds to `sigma_psi = sigma * sqrt(2)` in the probability density `|psi|^2 = exp(-(x-x0)^2 / (2*sigma^2))`. This is the standard quantum mechanical convention where `sigma` is the standard deviation of the probability density, not the wavefunction.

**Normalization:** `wf.normalize()` divides by `sqrt(norm)` where `norm = sum(|psi|^2) * dx`. This makes the wavefunction L2-normalized (unit total probability).

### Source 2: Gaussian barrier (barriers.py)

```python
# quantumlab/potentials/barriers.py:5
class GaussianBarrier(Potential):
    def __init__(self, V0: float, width: float, position: float=0.0):
        self.V0 = V0
        self.width = width
        self.position = position

    def evaluate(self, grid) -> np.ndarray:
        return self.V0 * np.exp(-((grid.x - self.position) / self.width) ** 2)
```

**Formula:** `V(x) = V0 * exp(-((x - position) / width)^2)`

**Note:** This uses `width` as a scale parameter, not FWHM or sigma. The exponent is `-(x-position)^2 / width^2`, which corresponds to `sigma = width / sqrt(2)` in standard Gaussian form `exp(-(x-mu)^2 / (2*sigma^2))`.

**Normalization:** None (amplitude = V0, not normalized to unit area).

### Quantum-Sim Gaussian Summary

| Property | Wave Packet | Barrier |
|---|---|---|
| Formula | `exp(-(x-x0)^2/(4*sigma^2)) * exp(i*k0*x)` | `V0 * exp(-((x-pos)/width)^2)` |
| Amplitude | 1.0 (before normalization) | V0 (height) |
| Normalization | L2-normalized (unit probability) | None (height-scaled) |
| Input domain | Continuous x on spatial grid | Continuous x on spatial grid |
| Parameters | x0 (center), k0 (wavenumber), sigma (std dev of probability density) | V0 (height), width (scale), position (center) |
| FWHM relation | sigma_psi = sigma*sqrt(2); FWHM = 2*sqrt(2*ln2)*sigma_psi ≈ 2.355*sigma*sqrt(2) | width = sigma*sqrt(2); FWHM = 2.355*width/sqrt(2) ≈ 1.665*width |
| Purpose | Initial quantum state preparation | Potential energy barrier |

---

## 3. Comparison

### 3.1 Formula structure

Both implementations use the standard Gaussian form:

```
exp(-(x - center)^2 / (2 * scale^2))
```

where `scale` is a width parameter. The mathematical identity of the Gaussian kernel is present in both.

### 3.2 Parameter conventions

| Parameter | King Wen | Quantum-Sim Wave Packet | Quantum-Sim Barrier |
|---|---|---|---|
| Center | `center` (phase_bits, 0-7) | `x0` (spatial position) | `position` (spatial position) |
| Width | `fwhm` (2.5) | `sigma` (std dev of probability density) | `width` (scale parameter) |
| Amplitude | 1.0 (unnormalized) | 1.0 (then L2-normalized) | `V0` (height) |
| Complex phase | None | `exp(i*k0*x)` (momentum boost) | None |
| Normalization | None (peak = 1.0) | L2 unit probability | None (height = V0) |

### 3.3 FWHM convention

King Wen uses FWHM explicitly: `sigma = FWHM / 2.35482` where `2.35482 = 2*sqrt(2*ln(2))`.

This is the standard FWHM-to-sigma conversion for a Gaussian where `FWHM = 2*sqrt(2*ln(2))*sigma`.

Quantum-Sim does NOT use FWHM. It uses `sigma` directly (standard deviation of probability density) or `width` (scale parameter). Neither is FWHM.

**Conversion:**
- King Wen: `sigma = FWHM / 2.35482` (FWHM → sigma)
- Quantum-Sim wave packet: `sigma` is std dev of probability density; wavefunction std dev = `sigma * sqrt(2)`
- Quantum-Sim barrier: `width = sigma * sqrt(2)` where sigma is std dev of the Gaussian

### 3.4 Input domain

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Input type | Discrete integer (phase_bits 0-7) | Continuous spatial coordinate (x) |
| Input range | 0-7 (8 discrete values) | Continuous real line (or bounded grid) |
| Output | Scalar weight (0-1) | Array (wavefunction values or potential values) |
| Dimensionality | 1D (scalar phase) | 1D/2D/3D (spatial) |

### 3.5 Purpose

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Purpose | Temporal phase bias modulation | Initial state preparation / potential barrier |
| Role | Weights phase contributions to avatar wavefunction | Defines physical quantum state or potential |
| Usage | `temporal_gaussian = _gaussian_kernel(phase_bits, 1.0, 2.5)` | `psi = gaussian(grid, x0, k0, sigma)` |

---

## 4. Mathematical Correspondence Assessment

### 4.1 What IS mathematically identical

The core Gaussian kernel form:

```
exp(-(x - center)^2 / (2 * scale^2))
```

Both implementations use this form. The mathematical identity of the Gaussian function is present in both.

### 4.2 What is NOT the same

1. **Input domain**: King Wen uses discrete integer phases (0-7); Quantum-Sim uses continuous spatial coordinates. These are fundamentally different input spaces.

2. **Parameter conventions**: King Wen uses FWHM; Quantum-Sim uses sigma (std dev) or width (scale). While convertible, the conventions differ.

3. **Normalization**: King Wen is peak-normalized (amplitude = 1.0, no area normalization); Quantum-Sim wave packet is L2-normalized (unit probability). Quantum-Sim barrier is height-normalized (V0).

4. **Complex phase**: Quantum-Sim wave packet includes `exp(i*k0*x)` momentum boost; King Wen Gaussian has no complex phase component.

5. **Purpose**: King Wen weights temporal phases for avatar modulation; Quantum-Sim prepares quantum states or defines potentials. Same kernel, different application.

6. **Dimensionality**: King Wen is 1D scalar; Quantum-Sim supports 1D/2D/3D.

### 4.3 Disposition

**M1-GAUSSIAN-KERNEL: `partial`**

The mathematical kernel form is identical (standard Gaussian), but the input domain, parameter conventions, normalization, and purpose are different. A mathematical correspondence exists at the level of the kernel formula, but not at the level of the complete mathematical object (which includes domain, normalization, and application context).

### 4.4 Three-Level Correspondence Distinction

The `partial` disposition must not be misread as proof that the two complete implementations are mathematically equivalent. Three distinct levels must be kept separate:

| Level | King Wen | Quantum-Sim | Status |
|---|---|---|---|
| Kernel-level | Gaussian functional form exp(-(x-mu)^2/(2*sigma^2)) | Same Gaussian functional form | SHARED -- the kernel formula is mathematically identical |
| Implementation-level | Peak-normalized, FWHM-parameterized, discrete phase input, no complex phase, 1D | L2-normalized or height-scaled, sigma/width-parameterized, continuous spatial input, complex phase present, 1D/2D/3D | NOT ESTABLISHED -- parameter conventions, normalization, dimensionality, and complex structure differ |
| Application-level | Temporal phase weighting for avatar wavefunction modulation | Wavefunction preparation or potential barrier definition | PARTIAL CONCEPTUAL RELATIONSHIP -- same kernel, different mathematical roles |

Key distinction: The FWHM conversion (sigma = FWHM / 2.35482) is a parameter conversion, not proof that the complete functions are equivalent. Two functions can use the same kernel form while representing different mathematical objects.

The `partial` disposition reflects only the kernel-level shared form. It does not imply implementation-level or application-level correspondence.

### 4.5 What would be needed to upgrade to `defined`

1. A formal definition of the King Wen Gaussian as a mathematical function with explicit domain, codomain, and normalization.
2. A demonstration that the King Wen Gaussian, when applied to continuous phase values, produces the same output as the Quantum-Sim Gaussian with equivalent parameters.
3. Unit/dimensional consistency verification.
4. Invariant preservation (e.g., normalization, peak value, symmetry).

### 4.6 What would make it `incompatible`

1. If the King Wen Gaussian were found to use a different exponent structure (e.g., `-(x-c)^2/c^2` without the factor of 2).
2. If the input domain were found to be fundamentally non-continuous (e.g., categorical rather than ordinal).
3. If the normalization convention were found to be mathematically incompatible (e.g., peak-normalized vs area-normalized in a context where area normalization is required).

---

## 5. Known Limitations

1. The King Wen Gaussian has not been tested with continuous input values (only discrete phase_bits 0-7).
2. The FWHM=2.5 value is hardcoded; no evidence of parameter sensitivity analysis.
3. The Quantum-Sim Gaussian wave packet includes a complex phase component (`exp(i*k0*x)`) that has no King Wen equivalent.
4. The King Wen Gaussian is used as a weight (0-1) in a modulation context; the Quantum-Sim Gaussian is used as a state preparation or potential definition. The mathematical roles differ.

---

## 6. Unresolved Questions

1. Is the King Wen Gaussian intended to approximate a continuous Gaussian kernel, or is it inherently discrete?
2. Does the FWHM=2.5 value have a physical or semantic justification, or is it empirically chosen?
3. Could the King Wen Gaussian be extended to continuous phase values without changing its mathematical properties?
4. Is there a meaningful relationship between the King Wen Gaussian (phase bias) and the Quantum-Sim Gaussian (wave packet preparation)?

---

## 7. Evidence Provenance

- King Wen source: `emotional_engine.py:458-470` (canonical engine, revision 71fbf28f8e92c6a7de74c50a304906ef81963a7d)
- King Wen additional sources: `scripts/kingwen_quantum_expand.py:33-37`, `scripts/kingwen_state_transition.py:195-200`, `scripts/kingwen_mobius_sphere.py:827`
- Quantum-Sim source: `quantumlab/core/wavefunction.py:35-40` (WaveFunction1D.gaussian), `quantumlab/potentials/barriers.py:5-15` (GaussianBarrier)
- Quantum-Sim repository: `Kbro1989/quantum-simulation` fork of `rasidi3112/quantum-simulation`, v1.3.0, merged 2026-11-02
- Audit date: 2026-11-02
- Evidence level: E2 (conceptual correspondence) for kernel form; E1 (lexical overlap) for terminology
- Mathematical correspondence (E3): NOT YET DEMONSTRATED
