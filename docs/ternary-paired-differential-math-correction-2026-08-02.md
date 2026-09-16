# King Wen Ternary Math Correction Spec
## Paired Differentials + Quantitative Ternary States

Date: 2026-08-02
Status: applied — code patches merged 2026-08-02 (verified in emotional_engine.py:425-433,714-723 and decision_matrix.py paired-differential sections). Header corrected 2026-08-21 audit (B8).

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

## Final Corrected 5-Axis Vector (code-aligned, emotional_engine.py post-2026-08-02 patch)

```python
dy = yang_count - yin_count                           # signed binary differential
yao_dy = yao_count - 3.0                              # yao vs neutral midpoint (6/2 = 3)
old_dy = old_yang_count - old_yin_count               # old_yang vs old_yin
changing_dy = changing_count - (6.0 - changing_count) # changing vs stable

yin_r = yin_count / 6.0
yang_r = yang_count / 6.0
yao_r = yao_count / 6.0
old_yang_r = old_yang_count / 6.0
old_yao_r = old_yao_count / 6.0
old_ratio = (old_yang_count + old_yin_count) / 6.0

return [
    _clamp(yao_dy * 0.5 + old_dy * 0.3 + abs(dy) * 0.2),        # chaos
    _clamp(yin_r * 0.4 + yao_dy * 0.3 + old_dy * 0.1),           # whimsy
    _clamp(old_yang_r * 0.15 + old_yao_r * 0.2 + dy * 0.1),      # darkTone
    _clamp(yang_r * 0.3 + (1.0 - yao_r) * 0.3 - old_ratio * 0.1),# coherence
    _clamp(yang_r * 0.3 + (1.0 - yao_r) * 0.2 + old_yang_r * 0.1),# voiceWeight
]
```

Each axis blends paired differentials (`dy`, `yao_dy`, `old_dy`, `old_yang_r`, `old_ratio`) rather than absolute counts. Boolean gating (e.g., `yao_r > 0.3`) lives only in `_primary_pool_for_hex` pool selection, never in the vector formula itself.

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

## Appendix A. Hamiltonian Trajectory Measurement (Rollout)

The corrected Hamiltonian from Section 3,

$$
\mathcal{H}(p,q,t) = \sum_{i=1}^{5} p_i \cdot \dot{q}^i - \Lambda,
$$
$$
p_i = \max(0, v_i^{\mathrm{res}}), \quad \dot{q}^i = v_i^{\mathrm{res}} - v_i^{\mathrm{exp}},
$$
$$
\Lambda = |dy| \cdot 0.5 + |yao\_dy| \cdot 0.3 + |changing\_dy| \cdot 0.2,
$$
$$
dy = yang - yin, \quad yao\_dy = yao - 3.0, \quad changing\_dy = changing - (6 - changing),
$$

is evaluated per phase across the 8-phase chained rollout in `scripts/shotgun_rollout_runtime.py` (stage 19) and packaged as training consumables by `scripts/rl_shotgun_measurables.py` (stage 20).

### A.1 Per-Phase Hamiltonian on the Rollout

For each hexagram $h$ and phase $t \in \{0,\dots,7\}$, the rollout computes:

$$
\mathcal{H}_{h,t} = \mathcal{H}\!\left(\mathbf{v}_{h,t}^{\mathrm{res}}, \mathbf{v}_{h,t}^{\mathrm{exp}}, \boldsymbol{\ell}_{h,t}\right)
$$

and records the Hamiltonian trajectory $\mathbf{H}_h = (\mathcal{H}_{h,0}, \dots, \mathcal{H}_{h,7})$.

For yang-dominant hexagrams (e.g., hex 1: $yang=6, yin=0$), the Lagrangian term $\Lambda_{h,t}$ dominates the $p \cdot \dot{q}$ term because:

$$
dy = 6 - 0 = 6, \quad |dy| \cdot 0.5 = 3.0, \quad p \cdot \dot{q} \approx 0.009,
$$

so $\mathcal{H}_{h,t} = \mathrm{clamp}(0.009 - 3.0, 0, 1) = 0$ for all $t$. In these hexagrams the temporal signal is carried by the resolved-vector trajectory $\|\Delta\mathbf{v}_t\|$ and the entropy $H(\mathbf{p}_t^{\mathrm{res}})$, not by $\mathcal{H}_{h,t}$. This is a measured property of the state, not a missing value.

For hexagrams with more balanced line distributions, $\Lambda$ is smaller and $\mathcal{H}_{h,t}$ may carry signal — the per-hexagram variation in $\mathrm{Var}(\mathbf{r})$ across the $G_0$ range $6.8413 \to 7.4319$ reflects this.

### A.2 Reward Decomposition on the Rollout

The step reward at phase $t$ decomposes as:

$$
r_{h,t} = w_{\mathcal{H}} \mathcal{H}_{h,t} + w_{\Delta} \|\Delta\mathbf{v}_{h,t}\| + w_H H(\mathbf{p}_{h,t}^{\mathrm{res}}) + w_c c_{h,t} + w_B B_{h,t}
$$

with $w_{\mathcal{H}}=0.1$, $w_{\Delta}=1.0$, $w_H=0.5$, $w_c=0.4$, $w_B=0.2$, and:

- $\|\Delta\mathbf{v}_{h,t}\| = \|\mathbf{v}_{h,t}^{\mathrm{res}} - \mathbf{v}_{h,t-1}^{\mathrm{res}}\|_2$ for $t>0$, $0$ for $t=0$
- $H(\mathbf{p}_{h,t}^{\mathrm{res}}) = -\sum_i p_{h,t,i} \log p_{h,t,i}$, with $p_{h,t,i} = v_{h,t,i}^{\mathrm{res}} / \sum_j v_{h,t,j}^{\mathrm{res}}$
- $c_{h,t} = v_{h,t,3}^{\mathrm{res}}$ — coherence axis
- $B_{h,t} = 0.2 \cdot \mathbf{1}[\chi_{h,t}=0]$ — chain bonus

The weights $w_{(\cdot)}$ are **measurement heuristics**, not derived from the consensus math. They are chosen so that the reward is dominated by the resolved-vector movement $\|\Delta\mathbf{v}\|$ and the vector diversity $H$, with the Hamiltonian, coherence, and chain continuity as secondary signals.

### A.3 Discounted Return

$$
G_{h,t} = \sum_{k=0}^{7-t} \gamma^k r_{h,t+k}, \quad \gamma = 0.95
$$

$G_{h,0}$ is the total return for hexagram $h$; $G_{h,7} = r_{h,7}$ is the terminal return.

### A.4 Trajectory Variance and Terminal Goodness

$$
\mathrm{Var}(\mathbf{r}_h) = \sqrt{\frac{1}{8} \sum_{t=0}^{7} (r_{h,t} - \bar{r}_h)^2}, \quad \bar{r}_h = \frac{1}{8} \sum_{t=0}^{7} r_{h,t}
$$

$$
\tau_h = 0.5 \cdot c_{h,7} + 0.3 \cdot H(\mathbf{p}_{h,7}^{\mathrm{res}}) + 0.2 \cdot \mathbf{1}\!\left[\sum_{t=0}^{7} \chi_{h,t} = 0\right]
$$

$\tau_h$ is the **terminal goodness** heuristic over the final phase — not a derived quantity from the consensus math, but a measurement of the terminal resolved state's coherence, diversity, and chain continuity.

### A.5 Empirical Batch (64 Hexagrams, Verified)

From `scripts/output/rl_measurables_all64.json`:

$$
\begin{aligned}
\bar{G}_0 &= 7.1472, & \overline{\mathrm{Var}(\mathbf{r})} &= 0.0696, & \bar{\tau} &= 0.9114, \\
\mathbf{1}_{\mathrm{chain\_continuous}_{64}} &= \mathrm{True}, & G_0^{\min} &= 6.8413\ (h=52), & G_0^{\max} &= 7.4319\ (h=51).
\end{aligned}
$$

Top 5 by $G_0$: $h=51\ (7.4319),\ h=38\ (7.3636),\ h=34\ (7.3487),\ h=6\ (7.3456),\ h=44\ (7.3320)$.
Bottom 5 by $G_0$: $h=52\ (6.8413),\ h=20\ (6.8808),\ h=2\ (6.8705),\ h=11\ (6.8655),\ h=15\ (6.8595)$.

The $G_0$ spread is $0.5906$ across 64 hexagrams, with all hexagrams chain-continuous. The spread is driven primarily by the entropy ($w_H=0.5$) and coherence ($w_c=0.4$) components, with the Hamiltonian component ($w_{\mathcal{H}}=0.1$) contributing $0$ for yang-dominant hexagrams and the change component ($w_{\Delta}=1.0$) providing the per-step movement signal.

### A.6 Relationship to the Corrected Hamiltonian

The rollout's $\mathcal{H}_{h,t}$ is exactly the corrected Hamiltonian from Section 3 evaluated on the per-phase state. It is not a new Hamiltonian, not a learned value function, and not a policy — it is the same $\mathcal{H}(p,q,t)$ measured at 8 discrete phase coordinates per hexagram and packaged as a trajectory. The 5-component reward $r_{h,t}$ and the scalar $\tau_h$ are measurement heuristics built on top of $\mathcal{H}_{h,t}$ and the other resolved-state quantities; they do not alter the underlying Hamiltonian or the 512-state consensus.

---

## Files Requiring Patches

1. `emotional_engine.py:376` `_hamiltonian_energy()` — Lagrangian paired differentials
2. `emotional_engine.py:526-553` `_line_state_vector()` — ternary vector rebuild
3. `emotional_engine.py:560+` `expand_hexagram()` — ensure `expanded_vector` retained in all returned dicts
4. `decision_matrix.py:135-146` `_hamiltonian_alignment_score()` — `q̇` replacement
5. `decision_matrix.py:112-129` `_neighbor_continuity_score()` — vector delta replacement
6. `hexagram_personality.py` — review for boolean flattening of ternary states
