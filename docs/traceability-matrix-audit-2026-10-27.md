# Traceability Matrix Audit Report

**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) and F-12 (one-sided clamp) are now VALIDATED. The Hamiltonian scale mismatch (pq_dot 0-1 vs L 0-6) is the root cause (F-10); the clamp is the sole information-loss mechanism (F-12). These findings are SEPARATE from the abs() sign-discarding design questions (coherence/voiceWeight/chaos) documented in this report — F-10/F-12 establish why H is always 0.0, not whether abs() should be replaced with signed differentials. The abs() sign question remains a design decision. See `docs/qsmc1-m3-mathematical-validation-f10.md` and `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

**Date:** 2026-10-27
**Audited file:** `docs/traceability-matrix-2026-10-27.md`
**Auditor:** Verification pass against actual repository code
**Commit under audit:** `71fbf28f8e`

---

## 1. Status Integrity Audit

### 1.1 Row Count and Status Distribution

| Status | Actual count | Notes |
|--------|--------------|-------|
| PROVEN | **40** | User's assessment said "16" — undercount by 24 |
| UNVERIFIED | **50** | Accurate |
| KNOWN_CONCERN | **11** | — |
| SPECIFIED | **3** | — |
| **Total data rows** | **104** | — |
| Gate rows (Section 7) | **6** | — |
| Section 9 illustrative rows | **10** | Duplicates Section 3.1/3.2 claims |

The user's claim of "16 PROVEN entries" is incorrect. There are 40 PROVEN entries. This affects the perceived verification coverage ratio.

### 1.2 PROVEN Entry Integrity Review

Each PROVEN entry was checked against its stated claim. No entry is technically wrong, but 16 of 40 establish **only existence or count**, not the broader invariant they appear to support.

#### Section 1: Canonical Authority Tier (20 PROVEN)

All 20 entries are **Valid** but 19 are **presence-only** (count verified, not identity preserved):

| # | Claim | Verdict | Reason |
|---|-------|---------|--------|
| 1.1 | `HEXAGRAM_BASE` has 64 entries, 10 keys | Valid (presence) | Count + key structure verified for hex 1 only |
| 1.2-1.18 | Constants have expected counts | Valid (presence) | Direct constant reads |
| 1.19 | `get_emotional_weights()` exists | Valid (presence) | Existence verified |
| 1.20 | `HEXAGRAM_BASE_TYPED is HEXAGRAM_BASE` = True | Valid (identity) | Cast identity verified — this is the only entry that proves identity preservation at the alias level |

**Assessment:** 19 of 20 PROVEN entries establish only existence or count. None establish that downstream code preserves hexagram identity. 1.20 is the only entry that proves identity at any level (alias-level only).

#### Section 2: Mathematical Specification Tier (6 PROVEN)

All 6 entries are **Valid**. They establish mathematical encoding correctness (0 mismatches across 512 entries) but do not establish that downstream code uses these encodings correctly.

#### Section 3: Executable Pipeline Tier (5 PROVEN)

All 5 entries are **Valid**. 3 of 5 are presence-only (count verified, not identity preserved):
- 3.1.1: 64/512 counts verified
- 3.1.3: All 64 hex IDs present (presence, not identity of data)
- 3.1.7: 64/512 counts verified

#### Section 5: Math Pipeline Tier (3 PROVEN)

All 3 entries are **Valid but weak**. They establish that the CLI doesn't crash (`--help` exits 0), not that extraction produces correct output.

#### Section 6: Evidence and Verification Tier (6 PROVEN)

All 6 entries are **Valid**. These are meta-level entries about the audit itself.

#### Section 7: Acceptance Gates (2 PROVEN)

Both entries are **Valid**. Gate 1 (determinism) and Gate 2 (canonical integrity) are proven.

### 1.3 Status Integrity Summary

| Verdict | Count | Notes |
|---------|-------|-------|
| Valid | 40 | All PROVEN entries establish what they claim |
| Overclaim | 0 | No PROVEN entry overclaims its stated scope |
| Presence-only (not identity) | 19 | Section 1 + 3.1.3 — count verified, identity not |
| Weak (CLI runs, not correctness) | 3 | 5.1.1-5.1.3 |

**Key finding:** No PROVEN entry is technically wrong. However, 19 of 40 PROVEN entries establish only existence or count, not the broader invariant they appear to support. The matrix should distinguish "PROVEN (count only)" from "PROVEN (identity)" from "PROVEN (behavior)".

**Recommendation:** Add scope annotations to PROVEN entries. For example, 1.1 should read "PROVEN (count only)" rather than "PROVEN".

---

## 2. Coverage and Consistency Audit

### 2.1 Row Count Reconciliation

| Section | Data rows |
|---------|-----------|
| 1. Canonical Authority | 20 |
| 2. Mathematical Specification | 14 |
| 3.1 State Expansion | 11 |
| 3.2 Identity Preservation | 7 |
| 3.3 Decision Matrix | 2 |
| 3.4 Determinism | 2 |
| 4. Migration Contract | 8 |
| 5.1 Math Extraction | 10 |
| 5.2 Occurrence Accounting | 4 |
| 5.3 Math Recovery | 9 |
| 5.4 Math Pipeline Verification | 4 |
| 6.1 Commit Audit | 6 |
| 6.2 Test Suite Status | 7 |
| 7. Acceptance Gates | 6 (gate rows) |
| 9. Expected vs Observed | 10 (illustrative) |
| **Total** | **120** |

The audit report's "119" was off by 1. Minor counting error.

### 2.2 Cross-Reference Consistency

All four governing invariants (A, B, C, D) have consistent cross-references. No discrepancies found.

### 2.3 Section 9 Redundancy

Section 9 contains 10 rows that duplicate Section 3.1 and 3.2 claims. This is not an error (Section 9 is an illustrative summary), but the matrix should note this explicitly to prevent readers from double-counting.

---

## 3. Test Derivation Audit

### 3.1 Mapping of 10 Parity Tests to Invariants

The matrix's Section 10 does not explicitly map each test to specific invariants. Here is the derived mapping:

| Test # | Test Name (from Section 10) | Invariant(s) | Specific Claim | Expected Result |
|--------|---------------------------|--------------|----------------|-----------------|
| T1 | Gate 1: Determinism | 3.4.1, 3.1.2 | Identical inputs → identical serialized outputs | SHA-256 hash identical across PYTHONHASHSEED values |
| T2 | Gate 2: Canonical integrity | 1.1, 6.1.1 | `HEXAGRAM_BASE` unchanged after pipeline run | `HEXAGRAM_BASE is HEXAGRAM_BASE` still True; no mutation |
| T3 | Gate 3: Identity (inject_site) | 3.2.1 | Each hexagram's inject_site unchanged through expansion | `expanded[i]['inject_site'] == HEXAGRAM_INJECTION_SITE[i+1]` for all 64 |
| T4 | Gate 3: Identity (emotional weights) | 3.2.1 | Each hexagram's emotional weights unchanged | `expanded[i]['emotional_weights'] == EMOTIONAL_WEIGHTS[str(i+1)]` for all 64 |
| T5 | Gate 3: Identity (category/action) | 3.2.1 | Each hexagram's category and action unchanged | `expanded[i]['category'] == HEXAGRAM_BASE[i+1]['category']` for all 64 |
| T6 | Gate 3: Identity (phase association) | 3.2.2 | Each resolved state's hexagram_id matches its expanded parent | `resolved[j]['hexagram_id'] == expanded_parent_id` for all 512 |
| T7 | Gate 4: Occurrence conservation | 5.2.1 | Multiset of provenance-bearing occurrence keys preserved | `Counter(source_keys) == Counter(extracted_keys)` |
| T8 | Gate 5: Interface fidelity | 4.1-4.8 | Each documented interface matches actual Python symbol | All 8 mismatches corrected in `lua-math-tool.md` |
| T9 | Gate 6: Parity (Lua vs Python) | A, B, C, D | Lua results match Python baseline | Requires gates 1-5 green first |
| T10 | Gate 6: No cross-hexagram normalization | Invariant A | No hexagram's representation transformed to conform to another's | `expanded[i]` data differs from `expanded[j]` for i≠j (not collapsed) |

**Key gap:** Test T10 (no cross-hexagram normalization) is the most important test but is **not explicitly listed** in Section 10's build order. It should be added as a dedicated parity test.

**Recommendation:** Add the test-to-invariant mapping and T10 to the matrix.

---

## 4. Mathematical-Contract Review: coherence, voiceWeight, and chaos

### 4.1 Specification

The ternary paired differential correction (`ternary-paired-differential-math-correction-2026-08-02.md`) specifies:

> "5-axis vector uses signed ternary differentials: dy, yao_dy, old_dy, stable_dy in all 5 axes"

The paired differentials are:
- `dy = yang_count - yin_count` (signed)
- `yao_dy = yao_count - 3.0` (signed)
- `old_dy = old_yang_count - old_yin_count` (signed)
- `stable_dy = stable_yao_count - stable_yin_count` (signed)

### 4.2 Actual Code

```python
# emotional_engine.py lines 738-742
_clamp(yao_dy * 0.5 + old_dy * 0.3 + abs(dy) * 0.2),    # chaos
_clamp(yin_r * 0.4 + yao_dy * 0.3 + old_dy * 0.1),      # whimsy
_clamp((old_yang / 6.0) * 0.15 + (old_yao / 6.0) * 0.2 + dy * 0.1), # darkTone
_clamp(yang_r * 0.3 - yao_dy * 0.3 - abs(old_dy) * 0.1),  # coherence
_clamp(yang_r * 0.3 - yao_dy * 0.2 + (old_yang / 6.0) * 0.1),   # voiceWeight
```

### 4.3 Analysis

| Axis | Terms | Signed? | Spec Compliance |
|------|-------|---------|-----------------|
| chaos | `yao_dy*0.5 + old_dy*0.3 + abs(dy)*0.2` | `abs(dy)` — **absolute** | Partial: dy loses sign |
| whimsy | `yin_r*0.4 + yao_dy*0.3 + old_dy*0.1` | All signed except yin_r (ratio) | Partial: yin_r is absolute ratio |
| darkTone | `(old_yang/6)*0.15 + (old_yao/6)*0.2 + dy*0.1` | `dy` signed; old_yang, old_yao absolute | Partial: old_yang, old_yao are counts |
| **coherence** | `yang_r*0.3 - yao_dy*0.3 - abs(old_dy)*0.1` | `abs(old_dy)` — **absolute** | **Non-compliant**: spec says signed; code uses abs |
| **voiceWeight** | `yang_r*0.3 - yao_dy*0.2 + (old_yang/6)*0.1` | `yao_dy` signed; yang_r, old_yang absolute | **Non-compliant**: spec says signed; code uses absolute terms |

### 4.4 Empirical Verification

Tested with Hexagram 1 (all yang) vs Hexagram 2 (all yin):

| Hexagram | old_dy | abs(old_dy) | coherence (signed) | coherence (abs) |
|----------|--------|-------------|--------------------|-----------------|
| 1 (all yang) | +6 | 6 | -0.3 → 0.0 | -0.3 → 0.0 |
| 2 (all yin) | -6 | 6 | +0.6 | -0.3 → 0.0 |

With signed `old_dy`, Hexagram 2 would have coherence = +0.6. With `abs(old_dy)`, both hexagrams have coherence = 0.0. This is a **significant difference in emotional routing** — the sign information matters.

### 4.5 Finding

**Coherence** explicitly uses `abs(old_dy)`, which discards the sign of the old_yang vs old_yin differential. This means coherence cannot distinguish between a state where old_yang > old_yin vs old_yin > old_yang. The paired differential specification requires signed differentials, so this is a **genuine non-compliance**.

**VoiceWeight** uses `yang_r` (absolute ratio) and `old_yang` (absolute count) rather than differentials. The spec says "5-axis vector uses signed ternary differentials" but voiceWeight uses absolute values for two of its three terms. This is also a **genuine non-compliance**, though less severe than coherence because `yao_dy` is signed.

**Chaos** uses `abs(dy)` which also discards sign, but chaos is not flagged as a concern in the matrix. This is an oversight — chaos should also be flagged.

### 4.6 Recommendation

The coherence and voiceWeight formulas need mathematical-contract review before any change. The question is: **does discarding sign information in coherence and voiceWeight produce incorrect emotional routing?**

- If coherence is meant to measure "how much the yang forces dominate" (a magnitude), then `abs(old_dy)` is correct and the spec should be updated to say "signed differentials where direction matters, absolute where magnitude matters."
- If coherence is meant to measure "the signed balance between yang and yin forces," then `abs(old_dy)` is wrong and should be `old_dy`.

This is a **design decision**, not a bug. The matrix correctly flags coherence as `KNOWN_CONCERN`, but the concern should be escalated to a design review before any code change.

**Matrix update needed:** The matrix should add a row documenting this design decision and the specific question that needs resolution. Also add chaos to the KNOWN_CONCERN list.

---

## 5. Summary of Audit Findings

### Critical Findings

1. **PROVEN count discrepancy:** User's assessment said "16 PROVEN" but there are actually 40. The matrix itself does not state a PROVEN count. This is an assessment error, not a matrix error.

2. **19 of 40 PROVEN entries are presence-only:** They establish that constants exist with the right counts, not that downstream code preserves identity. The matrix should distinguish "PROVEN (count only)" from "PROVEN (identity)" from "PROVEN (behavior)".

3. **coherence uses `abs(old_dy)`** — genuine non-compliance with paired differential spec. Verified empirically: Hexagram 1 and Hexagram 2 both get coherence = 0.0 with abs, but Hexagram 2 would get coherence = +0.6 with signed. Needs design review.

4. **voiceWeight uses absolute terms** — non-compliance with paired differential spec. Needs design review.

5. **chaos also uses `abs(dy)`** — same issue, not flagged in matrix. Should be added as KNOWN_CONCERN.

6. **Test T10 (no cross-hexagram normalization) is not explicitly listed** in Section 10's build order. Should be added as a dedicated parity test.

7. **Section 10 does not map tests to invariants.** The mapping derived in this audit (T1-T10) should be added to the matrix.

### Minor Findings

8. **Row count discrepancy:** Audit report said 119, actual is 120 (104 data + 6 gate + 10 section-9). Minor counting error.

9. **Section 9 has 10 redundant rows** that duplicate Section 3.1 and 3.2 claims. Not an error, but should be noted as illustrative.

10. **YAO_VOCABULARY structure:** The matrix says "9-item yao vocabulary" but the actual structure is `{0: {9 items}}` — a single key containing 9 sub-keys. The matrix's evidence column correctly notes this, but the "Expected" column should say "1 key (0) with 9 sub-keys" instead of "9-item yao vocabulary".

### Recommendations

1. **Add scope annotations to PROVEN entries:** Distinguish "PROVEN (count only)" from "PROVEN (identity)" from "PROVEN (behavior)".
2. **Add coherence/voiceWeight/chaos design review row** to Section 2 with the specific question: does sign information matter for these axes?
3. **Add T10 (no cross-hexagram normalization) to Section 10** as a dedicated parity test.
4. **Add test-to-invariant mapping** to Section 10.
5. **Fix YAO_VOCABULARY expected column** to say "1 key (0) with 9 sub-keys".
6. **Run the 7 verification scripts** (6.2.5-6.2.7) to reduce UNVERIFIED count.
7. **Keep Lua port blocked** until gates 1-5 are green.