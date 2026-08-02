# King Wen Ternary Math Correction Spec
## Paired Differentials + Quantitative Ternary States

Date: 2026-08-02
Status: spec only — no code changes yet

---

## Core Correction

**Current bug:** yin/yang/yao are flattened into boolean-ish ratios (`yin_ratio`, `yang_ratio`) with yao added as an absolute term. This loses the ternary structure.

**Correct model:** ternary states are quantitative. Boolean only appears at final gating decisions, never in the math layers.

---

## Ternary State Definitions

Each line position carries a **quantitative ternary state**, not a boolean:

| State | Value | Meaning |
|-------|-------|---------|
| stable_yin | 0 | settled yin |
| yang | 1 | settled yang |
| old_yin | 2 | yin becoming yang |
| old_yang | 3 | yang becoming yin |
| yao | 4 | active changing line (phase-gated) |

Note: yao is NOT a third binary pole. Yao is a **temporal differential** within yin/yang: it marks which lines are changing in the current phase. The true ternary opposition is:

```
yin_count + yang_count + yao_count = 6  (always)
```

Any ratio computation must respect this tricomponential constraint.

---

## Paired Differentials (Required)

All state comparisons must use **paired differentials**, not absolute ratios:

### 1. Primary ternary differentials
```
dy = yang_count - yin_count              # signed, not abs
dy_abs = |dy|                            # magnitude only for distance
yao_dy = yao_count - (yin_count + yang_count) / 2.0   # yao vs midpoint of binary pair
```

### 2. Temporal differentials (old vs stable within each base state)
```
old_yin_dy = old_yin_count - stable_yin_count
old_yang_dy = old_yang_count - stable_yang_count
old_yao_dy = old_yao_count - stable_yao_count
changing_dy = changing_count - non_changing_count  # within phase-gated subset
```

### 3. Phase-rate differentials (q̇^i)
```
q_dot[i] = resolved_vector[i] - expanded_vector[i]   # per-axis phase derivative
```
NOT `sum(momentum) * 1.0`. That is vector magnitude, not phase rate.

### 4. Neighbor differentials
```
prev_dy = hex_prev.vector - hex_current.vector
next_dy = hex_next.vector - hex_current.vector
```
Not absolute neighbor magnitudes compared to current.

---

## Corrected Hamiltonian

```
ℋ(p,q,t) = Σ p_i · q̇^i - ℒ
```

Where:
- `p_i` = resolved_vector[i] (momentum per axis)
- `q̇^i` = resolved_vector[i] - expanded_vector[i] (phase-rate per axis)
- `ℒ` = Lagrangian from paired ternary differentials:

```
ℒ = |yin_count - yang_count| * 0.5
    + yao_count * 0.3
    + changing_count * 0.2
```

**Wait — that's still wrong.** The Lagrangian must use **paired differentials**, not absolute counts:

```
ℒ = |dy| * 0.5
    + |yao_dy| * 0.3
    + |changing_dy| * 0.2
```

Where:
```
dy = yang_count - yin_count
yao_dy = yao_count - 3.0  # 3 is neutral midpoint (half of 6)
changing_dy = changing_count - (6 - changing_count)  # changing vs stable
```

---

## Corrected 5-Axis Vector

Current code (emotional_engine.py:547-553):
```python
return [
    _clamp(yao_r * 0.5 + old_ratio * 0.3 + abs(yang_r - yin_r) * 0.2),  # chaos
    _clamp(yin_r * 0.4 + yao_r * 0.3 + old_ratio * 0.1),                # whimsy
    _clamp(old_yang * 0.15 + old_yao * 0.2 + yang_r * 0.1),             # darkTone
    ...
]
```

**Problems:**
1. `abs(yang_r - yin_r)` appears only in chaos axis — missing from whimsy, darkTone, coherence, voiceWeight
2. `old_ratio` is absolute count, not differential between old_yang vs old_yin
3. yao is added as absolute term, not as ternary opposition to yin+yang midpoint

**Corrected:**
```python
dy = yang_r - yin_r                          # signed ternary differential
yao_dy = yao_r - 0.5                         # yao vs neutral midpoint
old_dy = old_yang_count/6.0 - old_yin_count/6.0  # old_yang vs old_yin differential
stable_dy = stable_yao_count/6.0 - stable_yin_count/6.0  # stable ternary opposition

return [
    _clamp(yao_dy * 0.5 + old_dy * 0.3 + abs(dy) * 0.2),    # chaos = yao opposition + old tension + binary tension
    _clamp(yin_r * 0.4 + yao_dy * 0.3 + old_dy * 0.1),      # whimsy = yin base + yao opposition + old tension
    _clamp(old_yang_r * 0.15 + old_yao_r * 0.2 + dy * 0.1), # darkTone = old_yang + old_yao + signed binary differential
    _clamp(yang_r * 0.3 + (1.0 - yao_r) * 0.3 - old_ratio * 0.1),  # coherence — needs differential rewrite
    _clamp(yang_r * 0.3 + (1.0 - yao_r) * 0.2 + old_yang * 0.1),   # voiceWeight — needs differential rewrite
]
```

Note: coherence and voiceWeight formulas need separate review — they still use absolute terms.

---

## Decision Matrix Corrections

**decision_matrix.py:135-146** `_hamiltonian_alignment_score()`:

Current:
```python
pq_dot = sum(momentum) * 1.0  # phase shift rate proxy
```

Correct:
```python
# Per-axis phase derivative from resolved vs expanded
expanded_vec = resolved_item.get("expanded_vector") or {}
q_dot = [
    float(rv.get(k, 0.0) or 0.0) - float(expanded_vec.get(k, 0.0) or 0.0)
    for k in VEC_KEYS
]
pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))  # p·q̇, not ||p||
```

**decision_matrix.py:112-129** `_neighbor_continuity_score()`:

Current:
```python
current_mag = _safe_mean([...])
prev_mag = _safe_mean([...])
next_mag = _safe_mean([...])
return _clamp(1.0 - abs(current_mag - avg_neighbor))
```

Correct:
```python
# Paired differential: current vs prev, current vs next
prev_dy = [current_vec[k] - prev_vec[k] for k in VEC_KEYS]
next_dy = [current_vec[k] - next_vec[k] for k in VEC_KEYS]
prev_dist = sum(d*d for d in prev_dy) ** 0.5
next_dist = sum(d*d for d in next_dy) ** 0.5
avg_dist = (prev_dist + next_dist) / 2.0
return _clamp(1.0 - avg_dist)  # lower distance = higher continuity
```

---

## Boolean Gating Rule

Boolean (`true`/`false`, `0`/`1`) is allowed **only** at:

1. Final decision gates: `should_execute`, `is_blocked`, `has_authority`
2. Binary artifact selection: `use_fallback`, `is_canonical`
3. Trigram bit representation: `0`/`1` is structural encoding, not a value judgment

Boolean is **forbidden** in:
- Ratio computations (use signed floats)
- Vector math (use differentials)
- Scoring surfaces (use paired deltas)
- Phase-rate calculations (use `q̇`, not magnitude)

---

## Verification Checklist

- [ ] All `yin_ratio`/`yang_ratio` usages reviewed for paired-differential replacement
- [ ] `old_ratio` replaced with `old_yang - old_yin` differential
- [ ] `changing_ratio` replaced with `changing - stable` differential
- [ ] `q̇^i` computed as per-axis `resolved - expanded`, not `sum(momentum)`
- [ ] Neighbor continuity uses vector deltas, not magnitude deltas
- [ ] No boolean comparisons in math layers (`== 0`, `== 1`, `is True/False` in scoring)
- [ ] All 512 resolved states carry `expanded_vector` so `q̇` is computable downstream

---

## Files Requiring Patches

1. `emotional_engine.py:376` `_hamiltonian_energy()` — Lagrangian paired differentials
2. `emotional_engine.py:526-553` `_line_state_vector()` — ternary vector rebuild
3. `emotional_engine.py:560+` `expand_hexagram()` — ensure `expanded_vector` retained in all returned dicts
4. `decision_matrix.py:135-146` `_hamiltonian_alignment_score()` — `q̇` replacement
5. `decision_matrix.py:112-129` `_neighbor_continuity_score()` — vector delta replacement
6. `hexagram_personality.py` — review for boolean flattening of ternary states
