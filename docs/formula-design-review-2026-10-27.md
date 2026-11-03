# Formula-Level Design Review: Emotional Vector Axes

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Commit under audit:** `71fbf28f8e`
**Source file:** `emotional_engine.py`, lines 720-742
**Spec file:** `docs/ternary-paired-differential-math-correction-2026-08-02.md`
**Status:** Design review — NO code changes made. Formulas unchanged.

---

## Governing Specification

The ternary paired differential correction specifies:

> "5-axis vector uses signed ternary differentials: dy, yao_dy, old_dy, stable_dy in all 5 axes"

The paired differentials are defined as:

| Differential | Formula | Range | Meaning |
|-------------|---------|-------|---------|
| `dy` | `yang_r - yin_r` | [-1, 1] | Signed binary yang/yin balance |
| `yao_dy` | `yao_r - 0.5` | [-0.5, 0.5] | Signed yao deviation from neutral midpoint |
| `old_dy` | `(old_yang / 6.0) - (old_yin / 6.0)` | [-1, 1] | Signed old_yang vs old_yin balance |
| `stable_dy` | `(stable_yao / 6.0) - (stable_yin / 6.0)` | [-1, 1] | Signed stable ternary opposition |

The spec's governing rule: **boolean only at final decision gates; forbidden in math/scoring/phase-rate layers.**

The spec does not explicitly state whether `abs()` is permitted or prohibited. It says "signed ternary differentials" which implies sign preservation, but does not define the mathematical contract for each axis.

---

**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) and F-12 (one-sided clamp information loss) are now VALIDATED. The scale mismatch identified here (pq_dot 0-1 vs L 0-6) is the root cause (F-10), and the clamp is the sole information-loss mechanism (F-12). The abs() sign-discarding question (coherence/voiceWeight/chaos) is a SEPARATE design question from F-10/F-12 and remains OPEN. See `docs/qsmc1-m3-mathematical-validation-f10.md` and `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

## Axis 1: chaos

### Formula (current implementation)

```
chaos = _clamp(yao_dy * 0.5 + old_dy * 0.3 + abs(dy) * 0.2)
```

### Input quantities and units

| Term | Source | Unit | Range |
|------|--------|------|-------|
| `yao_dy` | `yao_r - 0.5` | dimensionless | [-0.5, 0.5] |
| `old_dy` | `(old_yang - old_yin) / 6.0` | dimensionless | [-1, 1] |
| `dy` | `yang_r - yin_r` | dimensionless | [-1, 1] |
| `abs(dy)` | magnitude of dy | dimensionless | [0, 1] |

### Semantic definition (inferred from formula structure)

Chaos measures the degree of disorder or unpredictability in the hexagram's line distribution. It combines:
- Yao deviation from neutral (yao_dy): how much the changing lines deviate from the midpoint
- Old differential (old_dy): the signed balance between old yang and old yin
- Absolute binary differential (abs(dy)): the magnitude of yang/yin imbalance, regardless of direction

### Test vectors (empirically verified)

| State | yang_r | yin_r | yao_r | old_dy | abs(dy) | chaos (current) | chaos (signed dy) |
|-------|--------|-------|-------|--------|---------|-----------------|-------------------|
| All yang (phase 0) | 1.000 | 0.000 | 0.000 | +1.000 | 1.000 | 0.2500 | 0.2500 |
| All yin (phase 0) | 0.000 | 1.000 | 0.000 | -1.000 | 1.000 | 0.0000 | 0.0000 |
| Alternating (phase 0) | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.0000 | 0.0000 |
| Mixed 3/3 (phase 0) | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.0000 | 0.0000 |
| All yang (phase 1) | 0.667 | 0.000 | 0.333 | 0.000 | 0.667 | 0.0500 | 0.0500 |
| All yin (phase 1) | 0.000 | 0.667 | 0.333 | 0.000 | 0.667 | 0.0500 | 0.0000 |

### Sign sensitivity question

**Does `abs(dy)` discard meaningful sign information?**

- For all-yang vs all-yin at phase 0: both have `abs(dy)` = 1.0, so the `abs(dy)` term contributes equally. The difference in chaos (0.25 vs 0.0) comes from `yao_dy` (-0.5 in both) and `old_dy` (+1.0 vs -1.0), not from `abs(dy)`.
- For phase 1 states: all-yang and all-yin both have `abs(dy)` = 0.667, but chaos differs (0.05 vs 0.05) only because `yao_dy` and `old_dy` differ.

**Assessment:** The `abs(dy)` term measures the **magnitude** of yang/yin imbalance, not its direction. This is likely intentional — chaos should be high regardless of whether yang or yin dominates, because both represent disorder relative to balance. The sign of `dy` is already captured by `old_dy` (which is signed) and `yao_dy` (which is signed).

**Design question:** Is chaos meant to be symmetric under yang↔yin inversion? If yes, `abs(dy)` is correct. If no, `dy` should be used instead.

**Recommendation:** `abs(dy)` appears intentional. The sign of `dy` is already represented by `old_dy` in the same formula. No change recommended unless the semantic definition explicitly requires directional chaos.

---

## Axis 2: coherence

### Formula (current implementation)

```
coherence = _clamp(yang_r * 0.3 - yao_dy * 0.3 - abs(old_dy) * 0.1)
```

### Input quantities and units

| Term | Source | Unit | Range |
|------|--------|------|-------|
| `yang_r` | `balance["yang_ratio"]` | dimensionless | [0, 1] |
| `yao_dy` | `yao_r - 0.5` | dimensionless | [-0.5, 0.5] |
| `old_dy` | `(old_yang - old_yin) / 6.0` | dimensionless | [-1, 1] |
| `abs(old_dy)` | magnitude of old_dy | dimensionless | [0, 1] |

### Semantic definition (inferred from formula structure)

Coherence measures the degree of structural alignment or consistency in the hexagram. It combines:
- Yang ratio (yang_r): proportion of yang lines (higher = more yang)
- Yao deviation (yao_dy): how much changing lines deviate from neutral
- Absolute old differential (abs(old_dy)): magnitude of old yang/yin imbalance, regardless of direction

### Test vectors (empirically verified)

| State | yang_r | yao_dy | old_dy | abs(old_dy) | coherence (abs) | coherence (signed) |
|-------|--------|--------|--------|-------------|----------------|-------------------|
| All yang (phase 0) | 1.000 | -0.500 | +1.000 | 1.000 | 0.3500 | 0.3500 |
| All yin (phase 0) | 0.000 | -0.500 | -1.000 | 1.000 | 0.0500 | 0.2500 |
| Alternating (phase 0) | 0.500 | -0.500 | 0.000 | 0.000 | 0.3000 | 0.3000 |
| Mixed 3/3 (phase 0) | 0.500 | -0.500 | 0.000 | 0.000 | 0.3000 | 0.3000 |
| All yang (phase 1) | 0.667 | -0.167 | 0.000 | 0.000 | 0.2500 | 0.2500 |
| All yin (phase 1) | 0.000 | -0.167 | 0.000 | 0.000 | 0.0500 | 0.0500 |

### Sign sensitivity question

**Does `abs(old_dy)` discard meaningful sign information?**

- For all-yang (phase 0): old_dy = +1.0, abs = +1.0 → no difference (positive case)
- For all-yin (phase 0): old_dy = -1.0, abs = +1.0 → **difference**: coherence changes from 0.05 to 0.25
- For alternating/mixed: old_dy = 0.0 → no difference
- For phase 1 states: old_dy = 0.0 → no difference

**The sign of old_dy only matters when old_yang ≠ old_yin.** This occurs in hexagrams with asymmetric old yin/yang distributions (e.g., all yang has old_dy = +1.0, all yin has old_dy = -1.0).

**Assessment:** Using `abs(old_dy)` means coherence cannot distinguish between a state with excess old yang vs excess old yin. Both get the same coherence penalty. Using signed `old_dy` would give all-yin a higher coherence (0.25 vs 0.05) because the negative old_dy reduces the penalty.

**Design question:** Is coherence meant to measure "structural alignment regardless of which force dominates" (magnitude)? Or "signed balance where yang dominance increases coherence and yin dominance decreases it" (direction)?

**Recommendation:** This is a **genuine design decision**. The spec says "signed ternary differentials" but does not define the semantic contract for coherence. Neither formula is obviously correct without a formal definition. The decision should be documented explicitly before changing the code.

**Test vectors needed:**
- All-yang: coherence = 0.35 (both formulas agree)
- All-yin: coherence = 0.05 (abs) vs 0.25 (signed) — **discriminating case**
- Balanced: coherence = 0.30 (both formulas agree)
- Mixed: coherence = 0.30 (both formulas agree)

---

## Axis 3: voiceWeight

### Formula (current implementation)

```
voiceWeight = _clamp(yang_r * 0.3 - yao_dy * 0.2 + (old_yang / 6.0) * 0.1)
```

### Input quantities and units

| Term | Source | Unit | Range |
|------|--------|------|-------|
| `yang_r` | `balance["yang_ratio"]` | dimensionless | [0, 1] |
| `yao_dy` | `yao_r - 0.5` | dimensionless | [-0.5, 0.5] |
| `old_yang` | `balance["old_yang_count"]` | count | [0, 6] |
| `old_yang / 6.0` | normalized old yang count | dimensionless | [0, 1] |

### Semantic definition (inferred from formula structure)

VoiceWeight measures the authority or prominence of the hexagram's voice. It combines:
- Yang ratio (yang_r): proportion of yang lines (higher = more yang)
- Yao deviation (yao_dy): how much changing lines deviate from neutral (subtracted — more deviation = less voice weight)
- Normalized old yang count (old_yang/6.0): proportion of old yang lines (higher = more voice weight)

### Test vectors (empirically verified)

| State | yang_r | yao_dy | old_yang | voiceWeight (current) | voiceWeight (signed old_dy) |
|-------|--------|--------|----------|----------------------|---------------------------|
| All yang (phase 0) | 1.000 | -0.500 | 6 | 0.5000 | 0.5000 |
| All yin (phase 0) | 0.000 | -0.500 | 0 | 0.1000 | 0.0000 |
| Alternating (phase 0) | 0.500 | -0.500 | 0 | 0.3000 | 0.2500 |
| Mixed 3/3 (phase 0) | 0.500 | -0.500 | 0 | 0.3000 | 0.2500 |
| All yang (phase 1) | 0.667 | -0.167 | 0 | 0.2333 | 0.2333 |
| All yin (phase 1) | 0.000 | -0.167 | 0 | 0.0333 | 0.0333 |

### Sign sensitivity question

**Does voiceWeight's use of absolute `old_yang` (instead of signed `old_dy`) discard meaningful information?**

- The formula uses `old_yang / 6.0` (absolute count of old yang) rather than `old_dy` (signed differential of old yang vs old yin).
- This means voiceWeight increases with more old yang lines, regardless of old yin.
- Using signed `old_dy` instead would make voiceWeight decrease when old yin exceeds old yang.

**Assessment:** The current formula treats old yang as a positive contributor to voice authority. This is semantically different from treating it as a signed differential. The spec says "signed ternary differentials" but the formula uses an absolute count.

**Design question:** Is voiceWeight meant to measure "yang authority" (where only yang contributes positively)? Or "yang/yin balance authority" (where yang and yin contribute oppositely)?

**Recommendation:** This is a **genuine design decision**. The current formula treats old yang as inherently authoritative (more old yang = more voice weight). The signed alternative would treat old yin as anti-authoritative (more old yin = less voice weight). Neither is obviously correct without a formal definition.

**Test vectors needed:**
- All-yang: voiceWeight = 0.50 (both formulas agree, since old_dy = +1.0)
- All-yin: voiceWeight = 0.10 (abs) vs 0.00 (signed) — **discriminating case**
- Alternating: voiceWeight = 0.30 (abs) vs 0.25 (signed) — **discriminating case**

---

## Summary of Design Questions

| Axis | Current Formula Uses | Spec Says | Question to Resolve |
|------|---------------------|-----------|---------------------|
| chaos | `abs(dy)` | signed differential | Is chaos symmetric under yang↔yin inversion? |
| coherence | `abs(old_dy)` | signed differential | Is coherence a magnitude or a signed balance? |
| voiceWeight | `old_yang` (absolute count) | signed differential | Is voiceWeight "yang authority" or "yang/yin balance authority"? |

## Key Corrections to Earlier Audit

The earlier audit report claimed:

> "Hexagram 2 would get coherence = +0.6" under signed `old_dy`

This was **incorrect**. The actual value is **+0.25**, not +0.6. The recalculation from the complete formula shows:

```
coherence (signed) = yang_r * 0.3 - yao_dy * 0.3 - old_dy * 0.1
                   = 0.0 * 0.3 - (-0.5) * 0.3 - (-1.0) * 0.1
                   = 0.0 + 0.15 + 0.1
                   = 0.25
```

The difference between abs (0.05) and signed (0.25) is 0.20, not 0.60. The earlier value of 0.6 was a calculation error.

## Governing Principle

Neither formula should be selected solely because its output appears more intuitive. The correct approach:

1. Establish the formal semantic definition for each axis.
2. Write the governing equation in the ternary differential specification.
3. Define expected outputs for all-yang, all-yin, balanced, and mixed states.
4. Determine whether sign symmetry or sign sensitivity is an explicit requirement.
5. Only then change the code.

**No production formula should change until its intended semantics and expected outputs are established.**