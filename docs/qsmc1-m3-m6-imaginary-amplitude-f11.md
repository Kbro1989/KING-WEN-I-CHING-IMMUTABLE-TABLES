# F-11 Mathematical Validation — M6 Imaginary Amplitude

## 1. Investigation charter

**Question:** Why does M6 (the sampled complex amplitude) remain purely real (imaginary amplitude 0.0), and is this a consequence of M3's zero-valued Hamiltonian or an independent computation?

**Authorization:** User-authorized, 2026-11-02. No source-code modifications. No formula changes. No normalization, rescaling, or clamp changes. No alteration of the 1,536-state baseline or frozen provenance artifacts. No changes to frozen M3 research artifacts. No implementation consolidation or deletion. No commits.

**Dependency:** F-11 inherits from M3's zero-energy condition. The investigation must establish whether:
1. M6's imaginary component is independently computed and happens to be zero.
2. M6's imaginary component is derived from M3's Hamiltonian value and therefore inherits its zero.
3. M6's imaginary component is never actually computed because of a structural omission.

**Additional requirement:** A zero observed across tested inputs does not prove that nonzero values are impossible. Establish whether the implementation permits nonzero imaginary amplitudes analytically, and separately report what the available tests demonstrate.

**Deliverable:** This document (`docs/qsmc1-m3-m6-imaginary-amplitude-f11.md`). Analytical investigation only.

**Gate 2 remains OPEN.** F-11 investigation is authorized; remediation is not.

---

## 2. Source location and implementation

### 2.1 Function definition

Location: `emotional_engine.py`, lines 471–570.

```python
def _quantum_avatar_modulation(
    hexagram_id: int,
    phase_bits: int,
    resolved_vector: List[float],
    expanded_vector: List[float],
    request_text: str = "",
    emotional_input: int = 50,
) -> Dict[str, Any]:
```

### 2.2 Imaginary amplitude computation

Lines 512–528:

```python
# Wavefunction: |psi> = a|canonical> + b|phase> + c|intent>
# Real/imaginary components for each vector axis
wavefunction: Dict[str, Dict[str, Any]] = {}
for i, key in enumerate(VEC_KEYS):
    rv = float(resolved_vector[i]) if i < len(resolved_vector) else 0.0
    ev = float(expanded_vector[i]) if i < len(expanded_vector) else 0.0

    # Phase drives the imaginary component (temporal dynamics)
    phase_complexity = (phase_bits % 3) + 1  # 1..3
    real_part = rv * temporal_gaussian
    imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)

    wavefunction[key] = {
        "real": round(real_part, 6),
        "imag": round(imag_part, 6),
        "amplitude": round(math.sqrt(real_part**2 + imag_part**2), 6),
    }
```

### 2.3 Hamiltonian call site

Line 499:

```python
hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})
hamiltonian_normalized = float(hamiltonian)  # 0..1
```

**Critical observation:** The third argument to `_hamiltonian_energy` is `{}` (empty dict), not the actual `line_balance`. This means the lagrangian is computed from zero counts (yin=0, yang=0, yao=0, changing=0), giving:
- dy = 0 - 0 = 0
- yao_dy = 0 - 3.0 = -3.0
- changing_dy = 0 - (6.0 - 0) = -6.0
- lagrangian = 0*0.5 + 3.0*0.3 + 6.0*0.2 = 0 + 0.9 + 1.2 = 2.1

Even with correct line_balance data, the lagrangian would be ≥ 0.7 (minimum), which still exceeds |pq_dot| max 0.15. So the outcome (H=0) is the same regardless of whether the empty dict is passed or the correct line_balance.

### 2.4 Call site in the engine

Line 934 (in `expand_hexagram`):

```python
"quantum_avatar_state": _quantum_avatar_modulation(
    hexagram_id, phase_bits, sampled, expanded_vec, request_text, resolved_emotional_input
),
```

The function receives `sampled` (resolved vector) and `expanded_vec` (expanded vector) but NOT the line_balance. The line_balance is computed earlier in `expand_hexagram` and is available in the local scope, but it is not passed to `_quantum_avatar_modulation`.

---

## 3. Dependency chain

### 3.1 M6 → M3 dependency

```
M6 (imag_part) 
  → hamiltonian_normalized (line 500)
    → hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {}) (line 499)
      → pq_dot = Σ resolved[i] × (resolved[i] - expanded[i]) (lines 422-424)
      → lagrangian = |dy|*0.5 + |yao_dy|*0.3 + |changing_dy|*0.2 (lines 436-444)
      → return _clamp(pq_dot - lagrangian) (line 445)
  → _clamp() → max(0, min(1, negative)) → 0.0 (always, because lagrangian >> |pq_dot|)
```

### 3.2 Dependency classification

The imaginary component is **derived from M3's Hamiltonian value** (dependency type 2). It is not independently computed (type 1) and it is not a structural omission (type 3) — the code explicitly computes `imag_part` using `hamiltonian_normalized` as a factor.

The formula is:
```
imag_part = (rv - ev) × (hamiltonian_normalized × phase_complexity × 0.1)
```

Since `hamiltonian_normalized = 0.0` for all states (due to the clamp), `imag_part = (rv - ev) × 0.0 = 0.0` for all states.

### 3.3 The dependency is multiplicative, not additive

The imaginary component is a **product** of three factors:
1. `(rv - ev)` — the difference between resolved and expanded vectors (nonzero for most states)
2. `hamiltonian_normalized` — the Hamiltonian energy (always 0.0)
3. `phase_complexity × 0.1` — a phase-dependent scaling factor (1..3, always nonzero)

Since one factor is always zero, the product is always zero. This is a **multiplicative dependency** — the imaginary component cannot be nonzero unless ALL three factors are nonzero.

---

## 4. Analytical capability assessment

### 4.1 Can the implementation produce nonzero imaginary amplitudes?

**YES, analytically.** If `hamiltonian_normalized` were nonzero (i.e., if H were positive), then:

- `imag_part = (rv - ev) × (H_norm × phase_complexity × 0.1)`
- For any state where `rv ≠ ev` (which is most states, since resolved is phase-shifted from expanded)
- And `phase_complexity > 0` (always true: 1, 2, or 3)
- And `H_norm > 0` (which would require H > 0, which would require pq_dot > lagrangian)

Then `imag_part` would be nonzero.

**The implementation is structurally capable of producing nonzero imaginary amplitudes.** The zero is entirely due to M3's zero-energy condition, not a structural omission or a hardcoded zero.

### 4.2 What would be required for nonzero imaginary amplitudes?

1. **H > 0** (requires pq_dot > lagrangian, which requires normalization or formula change)
2. **rv ≠ ev** (true for most states — resolved is phase-shifted from expanded)
3. **phase_complexity > 0** (always true: 1, 2, or 3)

The only blocking condition is (1). If M3's Hamiltonian were nonzero, M6's imaginary component would be populated (assuming the other factors are nonzero).

### 4.3 Necessary vs sufficient

A nonzero Hamiltonian is **necessary** but not **sufficient** for a nonzero imaginary component:
- Necessary: If H = 0, then imag = 0 (always)
- Not sufficient: If H > 0, imag may still be 0 if rv = ev or phase_complexity = 0 (but phase_complexity is never 0)

In practice, H > 0 would be sufficient for most states (since rv ≠ ev for most states and phase_complexity ∈ {1,2,3}).

---

## 5. What the available tests demonstrate

### 5.1 Verified observations

| Observation | Source | States |
|---|---|---|
| imag = 0.0 for all states | qsmc1-m3-m6-reproduction.md | 512/512 |
| amplitude = \|real\| for all states | qsmc1-m3-m6-reproduction.md | 512/512 |
| H = 0.0 for all states | qsmc1-m3-floor-ceiling research | 1,536/1,536 |
| coherence varies (136 states > 0.7) | qsmc1-m3-m6-reproduction.md | 512 |
| All 64 hexagrams present | qsmc1-m3-m6-reproduction.md | 512 |
| No interference cross-term | qsmc1-m3-m6-reproduction.md | 512 |

### 5.2 What the tests do NOT demonstrate

The tests demonstrate that imag = 0 for all tested inputs under current conditions. They do NOT demonstrate that:
- imag could never be nonzero (the formula permits nonzero values)
- The code is structurally incapable of producing imaginary amplitudes
- A nonzero Hamiltonian would not populate the imaginary component

The tests are **conditional** — they test the current implementation where H = 0.0. They do not test the hypothetical case where H ≠ 0.0.

### 5.3 Test limitation

No test exists that:
- Injects a nonzero Hamiltonian value and verifies imag ≠ 0
- Tests the imag_part formula in isolation with controlled inputs
- Verifies the amplitude computation with nonzero imag

This is a gap in test coverage, not a finding about the implementation's capability.

---

## 6. Secondary finding: empty line_balance

### 6.1 Observation

The call site at line 499 passes `{}` as the line_balance:

```python
hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})
```

This means the lagrangian is computed from zero counts, not from the actual line balance. The `_hamiltonian_energy` function's `line_balance` parameter is designed to receive the line counts, but the caller does not provide them.

### 6.2 Impact

With empty line_balance:
- dy = 0 - 0 = 0
- yao_dy = 0 - 3.0 = -3.0
- changing_dy = 0 - 6.0 = -6.0
- lagrangian = 0*0.5 + 3.0*0.3 + 6.0*0.2 = 0 + 0.9 + 1.2 = 2.1

With correct line_balance (e.g., hex 1, phase 0):
- dy = yang_count - yin_count (actual values)
- lagrangian would be ≥ 0.7 (minimum observed in 1,536-state dataset)

In both cases, lagrangian >> |pq_dot|, so H = 0.0. The empty dict does not change the outcome.

### 6.3 Significance

This is a **consumer integration defect** (related to F-08: porosity consumer dependency unverified). The function is designed to receive line_balance but the caller does not provide it. This is independent of the scale mismatch (F-10) but compounds the issue.

Even if the correct line_balance were passed, H would still be 0.0 (due to scale mismatch). So this defect does not change the F-11 finding, but it is a separate issue that should be tracked.

---

## 7. Classification

### 7.1 Three possible explanations

| Explanation | Description | Evidence | Verdict |
|---|---|---|---|
| 1. Independently computed, happens to be zero | M6 computes imag independently; zero is coincidental | Formula uses hamiltonian_normalized as a factor — NOT independent | **Rejected** |
| 2. Derived from M3's Hamiltonian value | M6's imag is a product that includes H as a factor; H=0 → imag=0 | Code: `imag_part = (rv - ev) * (hamiltonian_normalized * ...)` | **Confirmed** |
| 3. Never computed (structural omission) | The imag component is hardcoded to 0 or not computed | Code explicitly computes imag_part; not hardcoded | **Rejected** |

### 7.2 Verdict

**Dependency type 2 confirmed.** M6's imaginary amplitude is derived from M3's Hamiltonian value through a multiplicative dependency. The imaginary component is never independently computed — it is a product that includes `hamiltonian_normalized` as a factor. Since M3's Hamiltonian is always 0.0 (due to the clamp), M6's imaginary component is always 0.0.

The implementation is analytically capable of producing nonzero imaginary amplitudes (if H were positive), but under current conditions, it cannot.

---

## 8. Downstream impact

### 8.1 Amplitude computation

```python
"amplitude": round(math.sqrt(real_part**2 + imag_part**2), 6)
```

Since imag_part = 0.0 for all states:
- amplitude = |real_part| = |rv × temporal_gaussian|

The amplitude is purely real. The "complex" amplitude construction is degenerate — it reduces to a real-valued amplitude.

### 8.2 Consequences

1. **No temporal dynamics in imaginary component:** The phase_complexity factor (1..3) has no effect because it multiplies a zero.
2. **No interference:** There is no imaginary component to interfere with the real component. The "interference" concept is inactive.
3. **Amplitude = |real|:** The amplitude is simply the absolute value of the real part, with no contribution from the imaginary part.
4. **Delegate vector degeneracy:** `delegate_vector = {k: round(v["amplitude"], 6)}` inherits the purely real amplitude.

### 8.3 What is NOT affected

- `real_part` is computed independently of H (uses rv × temporal_gaussian)
- `temporal_gaussian` is computed independently of H
- `rotation_modulation` uses hamiltonian_normalized (also zero, so rotation_x and rotation_y are also zero)
- `scale_factor` uses hamiltonian_normalized (scale = 1.0 + (0.0 - 0.5) * 0.5 = 0.75 for all states)
- `animation_phase` uses hamiltonian_normalized (animation_phase = phase/8 + 0.0)

So H=0 also zeros out rotation_x, rotation_y, and modifies scale_factor and animation_phase. But these are separate from M6's imaginary amplitude.

---

## 9. Summary of findings

### 9.1 Dependency classification

**Type 2 (derived from M3's Hamiltonian value).** M6's imaginary amplitude is a multiplicative product that includes `hamiltonian_normalized` as a factor. Since M3's Hamiltonian is always 0.0, M6's imaginary amplitude is always 0.0.

### 9.2 Analytical capability

**The implementation IS capable of producing nonzero imaginary amplitudes.** If H were positive (requiring pq_dot > lagrangian), then:
- imag_part = (rv - ev) × (H_norm × phase_complexity × 0.1)
- For states where rv ≠ ev (most states) and phase_complexity > 0 (always), imag_part would be nonzero.

The zero is a consequence of M3's zero-energy condition, not a structural limitation.

### 9.3 What tests demonstrate

The available tests demonstrate that imag = 0.0 for all 512/512 states under current conditions (H = 0.0). They do NOT demonstrate that nonzero values are impossible. No test exists that injects a nonzero Hamiltonian and verifies imag ≠ 0.

### 9.4 Secondary finding

The `_hamiltonian_energy` function is called with `{}` as line_balance (line 499), meaning the lagrangian is computed from zero counts, not actual line balance. This does not change the outcome (H = 0.0 either way) but is a separate consumer integration defect (related to F-08).

### 9.5 Relationship to F-10

F-11 is a **direct consequence** of F-10. The scale incompatibility (F-10) causes H = 0.0, which causes imag = 0.0 (F-11). F-11 is not an independent finding — it is a downstream effect of F-10's zero-energy condition.

If F-10's scale incompatibility were resolved (e.g., through normalization), F-11's imaginary amplitude would be populated (assuming the other factors are nonzero).

---

## 10. Safeguard

This investigation **does not** change the original M3 classification or close F-11. It establishes that:

1. M6's imaginary amplitude is **derived from M3's Hamiltonian value** (dependency type 2), not independently computed or structurally omitted.
2. The implementation **is analytically capable** of producing nonzero imaginary amplitudes (if H were positive).
3. The available tests demonstrate imag = 0 for all tested inputs but do **not** prove nonzero values are impossible.
4. F-11 is a **direct consequence** of F-10's zero-energy condition, not an independent finding.
5. A secondary consumer integration defect exists: `_hamiltonian_energy` is called with empty line_balance `{}`.

**F-11 Status:** VALIDATED (dependency type 2 confirmed; analytical capability established; test coverage gap identified).

**F-10 remains VALIDATED and unchanged.**

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline. Mathematical validation is authorized; remediation is not.

---

*End of F-11 mathematical validation.*