# Vortex / Hamiltonian / Jacobian / Gaussian Diagnostic Report

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Commit under audit:** `71fbf28f8e`

---

**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) and F-12 (one-sided clamp) are now VALIDATED. The scale mismatch (pq_dot 0.009543 vs L 2.500000 for Hex 1) is the root cause (F-10); the clamp is the sole information-loss mechanism (F-12). F-11 (M6 imaginary amplitude) is also VALIDATED — imag=0 is a type 2 dependency on M3's zero H, not an independent defect. The proposed fix (normalize L to /4.0) remains unimplemented. The or 0.35 bug affected Hex 7 and Hex 52 (not Hex 15/20 as originally stated); fix verified 13/13 PASS. See `docs/qsmc1-m3-mathematical-validation-f10.md`, `docs/qsmc1-m3-m6-imaginary-amplitude-f11.md`, `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

## 1. Hamiltonian: Root Cause Confirmed

### Observed failure

`_hamiltonian_energy()` returns **0.0** for all 64 expanded and 512 resolved states.

### Root cause: scale mismatch

| Term | Scale | Value (Hex 1) |
|------|-------|---------------|
| `pq_dot` (momentum × velocity) | 0-1 | 0.009543 |
| `L` (Lagrangian from paired differentials) | 0-6 | 2.500000 |
| `raw = pq_dot - L` | mixed | -2.490457 |
| `clamped (0..1)` | 0-1 | 0.000000 |

The Lagrangian is computed as `abs(dy) + abs(yao_dy) + abs(old_dy) + abs(stable_dy)` where each differential is on a 0-1 normalized scale but summed to 0-6. The momentum product `pq_dot` is on a 0-1 scale. Subtracting a 0-6 value from a 0-1 value always produces a negative result, which `_clamp(value, lo=0.0, hi=1.0)` floors to 0.0.

### Downstream impact

All Hamiltonian-dependent avatar animations are zeroed:
- Wavefunction imaginary part: `imag_part = (rv - ev) * (0.0 * phase_complexity * 0.1)` = **0.0**
- Rotation: `rotation_x = 0.0 * 0.35 * sin(...)` = **0.0**
- Scale factor: `scale_factor = 1.0 + (0.0 - 0.5) * 0.5` = **0.75** (constant, no variation)
- Animation phase: `animation_phase = (phase/8 + 0.0 * 0.125) % 1.0` = **phase/8** (Hamiltonian contributes nothing)

### Required diagnostic outputs (per review recommendation)

For each of 64 hexagrams × 8 phases = 512 states:
- `p_q` (momentum vector, 5 axes)
- `q̇` (velocity vector = resolved - expanded, 5 axes)
- `L` (Lagrangian from paired differentials)
- Raw `p_q · q̇ - L` before clamping
- Final clamped energy
- Hexagram identity and phase
- Expanded vs resolved flag

### Proposed fix (NOT applied — requires design approval)

The ternary paired differential correction spec (`docs/ternary-paired-differential-math-correction-2026-08-02.md`) specifies:
- `q̇^i = q_resolved^i - q_expanded^i` (per-axis, not scalar)
- Lagrangian should use paired differentials on compatible scale

The fix would normalize the Lagrangian to vector scale: `L = (abs(dy) + abs(yao_dy) + abs(old_dy) + abs(stable_dy)) / 4.0` (average of 4 differentials, each 0-1). This would make L range 0-1, compatible with pq_dot's 0-1 scale.

**No code change applied.** Design decision required.

---

## 2. Vortex: Porosity Scale Mismatch + `or` Bug

### Observed issue

`_vortex_tension()` in `scripts/schauberger_parsing_layers.py` line 19:

```python
porosity = float(inject.get("porosity", 0.35) or 0.35)
```

Injection site porosity is **always an integer 0-4** (verified: all 64 records, 5 unique values [0,1,2,3,4]).

### Concrete bug: `0 or 0.35`

Python's `or` operator treats 0 as falsy. When porosity=0 (2 of 64 hexagrams), `float(0) or 0.35` evaluates to `0.35` instead of `0.0`.

| Hexagram | Injection porosity | Code result | Correct result |
|----------|-------------------|-------------|----------------|
| Hex 7 | 0 | 0.35 | 0.0 |
| Hex 52 | 0 | 0.35 | 0.0 |

### Scale mismatch

The vortex function treats porosity as a float 0-1 (default 0.35), but the source is an integer 0-4. The vortex strength formula:

```python
vortex_strength = _clamp(angular_momentum * (0.5 + porosity * 0.5) * (0.5 + emotional_input / 200.0))
```

With porosity=0: `0.5 + 0*0.5 = 0.5` (correct if 0 means "no porosity")
With porosity=4: `0.5 + 4*0.5 = 2.5` → clamped to 1.0 (porosity=4 always maxes out)

The formula assumes porosity is 0-1, but the source is 0-4. This means porosity values 2, 3, 4 all produce vortex_strength at or near maximum, losing differentiation.

### Required diagnostic (per review recommendation)

Before changing:
1. Confirm injection site porosity is integer in every record ✅ (verified: all 64, values [0,1,2,3,4])
2. Determine whether vortex expects raw or normalized porosity → **Needs decision**
3. Check if normalization already occurs elsewhere → **No normalization found**
4. Identify downstream thresholds/attenuation functions that depend on porosity → **generate_sovereign_world.py uses porosity for spatial cutoffs and attenuation**

**No code change applied.** Design decision required: normalize porosity at a documented boundary, or change the vortex formula to accept 0-4 scale.

---

## 3. Jacobian: Verification Only, No Production Consumer

### Current state

- **Spec:** `docs/j-space-jacobian-lens-math-2026-07-11.md` documents J(a; v) = E[dY/dA] * dA
- **Diagnostic:** `scripts/verify_math_jacobian_hamiltonian.py` computes perturbation vector
- **Production:** No consumer identified in emotional_engine.py or state-transition paths

### Required before integration

1. Define input activation (what state triggers Jacobian computation)
2. Define output state representation (what the perturbation vector feeds into)
3. Define derivative convention (finite differences? analytical?)
4. Define perturbation vector shape (5-axis? per-hexagram?)
5. Define the production decision that consumes the vector

**No code change applied.** Interface specification required before integration.

---

## 4. Gaussian: Functional, Needs Validation

### Current state

- `_gaussian_kernel()` in emotional_engine.py: functional, used for temporal phase modulation (FWHM=2.5)
- `gaussian_kernel()` in kingwen_state_transition.py: functional, used for future-phase bias
- `_project_gaussian_future()`: functional, weights future phase through Gaussian
- `_gaussian_future_transition()` in kingwen_mobius_sphere.py: functional, avatar coordinate transition

### Required validation (per review recommendation)

- Kernel normalization: does K(v1, v2) sum to 1 over all pairs?
- FWHM interpretation: is 2.5 the correct FWHM for "phases ~2 away get ~50% modulation"?
- Boundary behavior: what happens at phase 0 and phase 7 (edges)?
- Downstream identity preservation: does Gaussian blending preserve hexagram identity?

**No code change applied.** Validation tests needed.

---

## 5. Porosity: Three Independent Sources, No Reconciliation

| Source | Scale | Range | Computation | Used by |
|--------|-------|-------|-------------|---------|
| Injection site | 0-4 (integer) | 0,1,2,3,4 | `HEXAGRAM_INJECTION_SITE[h_id]['porosity']` | vortex tension, emotional engine |
| Kit QWP | 0.15-0.71 (float) | 0.15, 0.20, ..., 0.71 | `0.15 + u_idx*0.05 + l_idx*0.03` | 3D kits, sovereign world |
| Emotional engine | 0-1 (float) | varies | `_line_state_balance` + phase adjustment | emotional vectors |

**No reconciliation exists.** The three sources measure different things (semantic topology, spatial structure, line-state balance) but share the field name "porosity."

### Required actions

1. Define explicit field names: `structural_porosity`, `injection_site_porosity`, `line_balance_porosity`
2. Preserve original values — no silent conversion
3. If a shared interface needs a single value, introduce an explicit documented adapter
4. Validate prewarm artifacts independently (manifest path resolution, cache existence, count agreement)

---

## 6. Traceability Matrix Corrections (from review)

| Finding | Required Action |
|---------|----------------|
| 19 PROVEN entries establish presence, not identity | Add scope annotations: "PROVEN (count only)" vs "PROVEN (identity)" vs "PROVEN (behavior)" |
| 3 CLI checks establish only `--help` | Add input-to-output tests |
| T10 missing from build order | Add explicit no-cross-hexagram-normalization test |
| Test-to-invariant mapping incomplete | Map T1-T10 to specific invariants, symbols, assertions, evidence |
| Section 9 duplicates Section 3 | Retain as concise expected-vs-observed index with links |
| coherence/voiceWeight/chaos design questions | Add design review row with formal semantic definition question |
| YAO_VOCABULARY expected column | Should say "1 key (0) with 9 sub-keys" not "9-item yao vocabulary" |

---

## 7. Priority Order (from review)

1. **P1: Hamiltonian diagnosis** — raw terms, units, clamp, intended energy range → then decide fix
2. **P2: Vortex porosity contract** — trace complete porosity path, establish units and valid range
3. **P3: Jacobian production interface** — define consumer contract before integration
4. **Monitor: Gaussian** — preserve and validate, no unnecessary changes
5. **Traceability corrections** — scope annotations, T10, test mapping
6. **Porosity reconciliation** — define field contracts, don't force conversion

**No production code changes applied.** All findings are diagnostic. Design decisions required before any fix.