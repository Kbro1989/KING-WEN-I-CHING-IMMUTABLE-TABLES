# Pipeline Output Measurement Report — Gap Analysis

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Pipeline:** `scripts/full_hexagram_shotgun.py` → `shotgun_expand(request_text, emotional_input)`

---

## User Observation: "I'm seeing 64, 512.. but not 729+ in these outputs."

**Confirmed.** The pipeline output does NOT contain 729 or 5,832 state data. Here's exactly what's present vs. what's missing.

---

## What IS in the output

| State Space | Count | Where | Status |
|-------------|-------|-------|--------|
| Binary expanded | 64 | `result['expanded']` array | ✅ Present, full data |
| Binary resolved | 512 | `result['resolved']` array | ✅ Present, full data |
| Ternary slots | 6 per hex | `expanded[i]['ternary_slots']` | ✅ Present (6 line positions × 3 states) |
| Ternary permutations count | 729 | `expanded[i]['ternary_729_permutations_count']` | ⚠️ Count only, no data |
| Ternary permutations data | 729 per hex | NOT stored | ❌ Computed then discarded |
| 729 ternary hexagrams | — | NOT in output | ❌ Separate file |
| 5,832 resolved ternary | — | NOT in output | ❌ Separate file |

---

## What IS NOT in the output (and where it lives)

### 1. The 729 ternary permutations per hexagram

**Computed but discarded.** In `full_hexagram_shotgun.py` line 568:
```python
ternary_729_permutations = _expand_729_ternary_line_permutations(h_id, inject)
```

This generates all 729 line-state permutations (3^6) for each hexagram. But only the count is stored:
```python
"ternary_729_permutations_count": len(ternary_729_permutations),  # = 729
```

The actual `ternary_729_permutations` list (729 dicts with permutation_id, hexagram_id, line_states, yin/yang/yao counts, route_key) is **never included in the output dict**. It's computed, counted, and thrown away.

### 2. The 729 ternary hexagrams

**Lives in a separate file:** `scripts/ternary_full_expansion.json` (2.9MB)

```json
{
  "total_trigrams": 27,
  "total_hexagrams": 729,
  "total_resolved": 5832,
  "canonical_count": 64,
  "ternary_count": 665,
  "trigrams": { ... 27 entries ... },
  "hexagrams": { ... 729 entries ... },
  "resolved": { ... 5832 entries ... }
}
```

This file is loaded by `kingwen_quantum_expand.py` but is NOT loaded by `shotgun_expand()`. The shotgun pipeline only produces binary states (64/512).

### 3. The 5,832 resolved ternary states

**Also in `ternary_full_expansion.json`** under the `resolved` key. These are 729 hexagrams × 8 phases. Never produced by `shotgun_expand()`.

### 4. Ternary slots, schauberger parsing, personality subsets, projections for resolved states

**None for 448/512 resolved states.** These fields are only computed for expanded (phase-0) states:
```python
"personality_subsets": None,  # computed only for expanded (phase=0)
"ternary_slots": None,  # computed only for expanded (phase=0)
"ternary_729_permutations_count": 0,  # computed only for expanded (phase=0)
"schauberger_parsing": None,  # computed only for expanded (phase=0)
```

Only 64 of 512 resolved states (phase 0) have these fields populated. The other 448 (phases 1-7) have None.

---

## Summary: What the pipeline actually produces vs. what it claims

| Claimed | Actually Stored | Gap |
|---------|----------------|-----|
| 64 expanded | 64 expanded with full data | ✅ Complete |
| 512 resolved | 512 resolved, but 448 lack ternary/schauberger/personality data | ⚠️ Partial |
| 729 permutations/hex | Count only (729) | ❌ Data discarded |
| 46,656 total ternary permutations | Count only (46,656) | ❌ Data discarded |
| 729 ternary hexagrams | In separate file, not loaded | ❌ Not in pipeline output |
| 5,832 resolved ternary | In separate file, not loaded | ❌ Not in pipeline output |
| ternary_slots (6 per hex) | 6 for expanded, None for resolved | ⚠️ Partial |
| schauberger_parsing | For expanded only | ⚠️ Partial |
| personality_subsets (18 per hex) | For expanded only | ⚠️ Partial |
| projections | None for all | ❌ Never computed |
| quantum_avatar_state | For all 512 resolved | ✅ Complete |
| sample_paths | For all 512 resolved | ✅ Complete |
| yao_vocabulary | For all 512 resolved | ✅ Complete |
| pre_slider | For all 512 resolved | ✅ Complete |
| inject_site | For all 512 resolved | ✅ Complete |

---

## Root Cause

The `shotgun_expand()` function is designed as a **binary-layer** pipeline:
- 64 hexagrams × 8 phases = 512 binary states
- It computes ternary data (729 permutations) but only stores the count
- The ternary expansion (729 hexagrams × 8 phases = 5,832) lives in a separate file (`ternary_full_expansion.json`) loaded by a different script (`kingwen_quantum_expand.py`)

The two layers (binary 64/512 and ternary 729/5832) are **not integrated** into a single pipeline output. The shotgun_expand function reports ternary counts as metadata but doesn't include the actual ternary data.

---

## What Would Need to Change

To make the 729+ data appear in the pipeline output:

1. **Store the 729 permutations** — include `ternary_729_permutations` (the list of 729 dicts) in the expanded output, not just the count
2. **Load ternary_full_expansion.json** — integrate the 729 ternary hexagrams and 5,832 resolved states into the shotgun output
3. **Compute ternary_slots, schauberger, personality_subsets for all 512 resolved** — not just phase 0
4. **Compute projections** — currently None for all states
5. **Reconcile porosity** — the 3 independent computations need a single authority

None of these are being done currently. The pipeline produces 64/512 binary states with metadata about 729/5832 but doesn't actually include that data.