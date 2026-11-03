# Yao-Line Semantic Audit — Read-Only Evidence Matrix

**Date:** 2026-10-29
**Status:** READ-ONLY AUDIT — no source modifications authorized
**Scope:** `DATASETS/kingwen_oracle_yao_lines.csv` vs `DATASETS/kingwen_oracle_yao_lines (1).csv`

---

## 1. File Inventory

| Property | Base (`kingwen_oracle_yao_lines.csv`) | Enriched (`kingwen_oracle_yao_lines (1).csv`) |
|---|---|---|
| Rows | 384 (64 hexagrams × 6 lines) | 384 (64 hexagrams × 6 lines) |
| Columns | 9 | 12 |
| Size | 22K | 29K |
| Date | Jul 6, 2026 | Jul 6, 2026 |
| Generator | **NOT FOUND in repo** | **NOT FOUND in repo** |
| Consumers | None found (no script references base version) | `score_truth_tables.py`, `build_avalokiteshvara_registry.py` |

**Provenance gap:** No generator script exists in the repository for either file. Both were likely created by an external tool or a script that has since been removed. This is a critical gap — the generation lineage cannot be traced.

---

## 2. Schema Comparison

| Column | Base | Enriched | Notes |
|---|---|---|---|
| `hexagram_id` | ✅ | ✅ | Stable key |
| `hexagram_name` | ✅ | ✅ | Stable key |
| `line_number` | ✅ | ✅ | Stable key (1-6, bottom to top) |
| `position` | ✅ | ✅ | upper/lower |
| `trigram` | ✅ | ✅ | Trigram name |
| `base_state` | ✅ | ✅ | Stable binary: yin/yang |
| `ternary_state` | ✅ | ✅ | **DIFFERENT SEMANTICS** (see below) |
| `category` | ✅ | ✅ | Hexagram category |
| `hexagram_binary` | ✅ | ✅ | 6-bit binary string |
| `direction` | ❌ | ✅ | NEW: rising/falling/stable |
| `is_stressed` | ❌ | ✅ | NEW: boolean |
| `is_activated` | ❌ | ✅ | NEW: boolean |

---

## 3. Field Semantics Analysis

### 3.1 `base_state` — STABLE across both files

- Base: yang=192, yin=192 (perfectly balanced)
- Enriched: yang=192, yin=192 (identical)
- **Conclusion:** `base_state` is the stable binary identity of each line. Both files agree. This is the canonical binary representation.

### 3.2 `ternary_state` — DIFFERENT SEMANTICS

| Metric | Base | Enriched |
|---|---|---|
| `yin` count | 176 | 118 |
| `yang` count | 181 | 110 |
| `yao` count | 27 | 156 |
| Total | 384 | 384 |

**Base `ternary_state`:**
- For 357/384 lines (93%), `ternary_state == base_state` (stable binary value)
- For 27/384 lines (7%), `ternary_state = yao` (changing-line marker)
- These 27 lines span 13 hexagrams: 3, 5, 9, 16, 18, 23, 28, 36, 38, 39, 47, 56, 59
- Position distribution: upper=17, lower=10 (no bottom/middle/top)

**Enriched `ternary_state`:**
- `yao` = 156 lines (40.6%) — ALL have `is_stressed=True` and `is_activated=True`
- `yin` = 118 lines (30.7%) — ALL have `is_stressed=False`, `is_activated=False`
- `yang` = 110 lines (28.6%) — ALL have `is_stressed=False`, `is_activated=False`
- Direction: yao+rising=74, yao+falling=82, yao+stable=0; yin+stable=118, yang+stable=110

**Key insight:** In the enriched version, `ternary_state` is a **derived classification**:
- `yao` = stressed/activated changing line (with rising/falling direction)
- `yin`/`yang` = stable non-changing line

In the base version, `ternary_state` **conflates** stable binary with changing classification:
- For 357 lines: `ternary_state = base_state` (stable binary)
- For 27 lines: `ternary_state = yao` (changing marker)

### 3.3 Overlap Analysis

| Metric | Count |
|---|---|
| Base yao lines | 27 |
| Enriched yao lines | 156 |
| Intersection (yao in both) | 10 |
| Enriched-only yao | 146 |
| Base-only yao | 17 |

**Critical finding:** The two files use **different criteria** for what constitutes a "changing" (yao) line. Only 10 of 156 enriched-yao lines overlap with the 27 base-yao lines. The base-only 17 lines are NOT classified as yao in the enriched version.

### 3.4 `direction`, `is_stressed`, `is_activated` — NEW in enriched

These three fields exist only in the enriched version. They encode:
- `direction`: rising (74), falling (82), stable (228) — temporal trajectory of the line
- `is_stressed`: True for 156 lines (all yao), False for 228 (all stable)
- `is_activated`: True for 156 lines (all yao), False for 228 (all stable)

These are **derived fields** not present in the base version. They add temporal/differential information that the base version lacks.

---

## 4. Classification per Assessment Framework

| Finding Category | Evidence | Classification |
|---|---|---|
| `base_state` identical across both files | 384/384 match | **Equivalent representation** — same stable binary identity |
| `ternary_state` has different meanings | 163 diffs, different criteria | **Semantic incompatibility** — different definitions of "changing" |
| `direction`/`is_stressed`/`is_activated` only in enriched | 3 new columns | **Derived-stage difference** — enriched adds temporal/differential layer |
| 27 base-yao vs 156 enriched-yao | Only 10 overlap | **Semantic incompatibility** — different thresholds/criteria for "changing" |

### Most Important Finding

The base file's `ternary_state` field **conflates** two concepts:
1. Stable binary identity (yin/yang) for non-changing lines
2. Changing-line marker (yao) for 27 "stressed" lines

The enriched file **separates** these:
1. `base_state` = stable binary for ALL lines
2. `ternary_state` = changing classification (yao for 156, stable for 228)
3. `direction` = temporal trajectory
4. `is_stressed`/`is_activated` = derived boolean flags

This is **not** merely a stage difference. The enriched version introduces a different **definition** of what constitutes a "changing" line (156 vs 27). The 17 base-only yao lines that are NOT yao in the enriched version demonstrate that the criteria are fundamentally different, not just more sensitive.

---

## 5. Three Possible Findings — Disposition

| Finding | Evidence | Disposition |
|---|---|---|
| **Equivalent representations** | `base_state` identical (384/384) | ✅ `base_state` is equivalent across both files |
| **Different stages of one transformation** | Enriched adds `direction`, `is_stressed`, `is_activated` | ✅ These are derived-stage additions |
| **Semantic incompatibility** | `ternary_state` has different criteria (27 vs 156 yao, only 10 overlap) | ⚠️ **REQUIRES INVESTIGATION** — different "changing" thresholds |

The third finding is the critical one. The two files disagree on **which lines are changing** (yao), not just how to represent them. This cannot be resolved by renaming or normalizing.

---

## 6. Read-Only Evidence Matrix (Differing Records)

| Stable Key | Base ternary_state | Enriched ternary_state | Enriched base_state | Enriched direction | Enriched is_stressed | Disposition |
|---|---|---|---|---|---|---|
| hex 3, line 5 | yang | yao | yang | falling | True | **Semantic incompatibility** — base says stable, enriched says changing |
| hex 3, line 4 | yin | yao | yin | rising | True | **Semantic incompatibility** |
| hex 3, line 3 | yin | yao | yin | rising | True | **Semantic incompatibility** |
| hex 3, line 2 | yao | yin | yin | stable | False | **Semantic incompatibility** — base says changing, enriched says stable |
| hex 5, line 6 | yao | yin | yin | stable | False | **Semantic incompatibility** |
| hex 5, line 5 | yang | yao | yang | falling | True | **Semantic incompatibility** |
| ... (163 total) | | | | | | |

Full matrix: 163 differing records out of 384. Only 221 records have identical `ternary_state` values (base `ternary_state` == enriched `ternary_state`).

---

## 7. What This Audit Does NOT Establish

1. **Which criterion is correct** — 27 yao (base) vs 156 yao (enriched) cannot be resolved without examining the generator logic, which is not in the repo.
2. **Whether the enriched `direction` values are meaningful** — rising/falling/stable are derived from an unknown algorithm.
3. **Whether `is_stressed`/`is_activated` are independent signals** — they are perfectly correlated (both True for all 156 yao, both False for all 228 stable), suggesting they may be the same signal with two names.
4. **Generator provenance** — no script in the repo generates either CSV file. The generation lineage is unknown.
5. **Whether the base or enriched version is "canonical"** — this requires understanding the intended semantics of `ternary_state` in each generation.

---

## 8. Recommended Next Steps (Read-Only)

1. **Trace generator provenance** — search all repos (KING-WEN, POG2, OpenJarvis, Megatron) for any script that writes `kingwen_oracle_yao_lines.csv`. The generator may be in a different repository or may have been deleted.
2. **Examine `PHASE_LINE_MAP` in `emotional_engine.py`** — this defines which lines change per phase (0-7). Compare against the 27 base-yao and 156 enriched-yao lines to determine which criterion aligns with the canonical phase model.
3. **Check `kingwen_ternary_tables_complete.py`** — the canonical ternary table may define which lines are "changing" for each hexagram. Compare against both CSV versions.
4. **Document the intended semantics** of `ternary_state` in each generation before attempting reconciliation.
5. **Do NOT normalize** the two versions into one representation. The 163 differences are evidence to preserve, not noise to clean up.

---

## 9. Provenance Finding: Git History

| File Family | First Commit | Date | Commit Message |
|---|---|---|---|
| `(1)` variants (all 8) | `ea89a9cf2d` | 2026-07-06 16:13 | "Add emotional engine and temporal emotional engine with expand/collapse functionality" |
| Base variants (all 8, no `(1)`) | `62061bddb1` | 2026-07-21 14:42 | "docs: fix repo name typo in missed integrations tracking" |

**Key finding:** The `(1)` files are the **original** generation (Jul 6), added alongside the emotional engine. The base files (without `(1)`) were added **15 days later** (Jul 21) in a commit whose message is about fixing a repo name typo — suggesting the base files were added as a side effect, possibly as "cleaned up" or "simplified" versions.

This means:
- The `(1)` files are the **original** enriched versions
- The base files are **later derivatives** — possibly simplified (fewer columns, different values)
- The direction of derivation is `(1)` → base, not base → `(1)` as the filenames might suggest

The commit message for the base files ("docs: fix repo name typo") is misleading — it added 8 CSV files + 1 JSON file alongside a 2-line docs fix. This suggests the base files were generated by an external process and committed opportunistically.

**No generator script exists in either commit's diff.** The CSV files were added as static artifacts without their generating code. This is a critical provenance gap.

## 10. Additional Finding: Base Yao Lines Share a Common Property

All 13 base-yao hexagrams share three properties:
- `category = dissipator` (100%)
- `action = ADAPT` or `WAIT` (100%)
- `porosity = 4` (maximum porosity, 100%)

This means the base version's `yao` classification is **not** a general "changing line" detector. It is a **category-specific filter** that only flags lines in dissipator-category, high-porosity hexagrams. The 27 base-yao lines are a deliberate subset, not a comprehensive inventory.

In contrast, the enriched version's 156 yao lines span 42 hexagrams across all categories, with `is_stressed=True` and `is_activated=True` as the criterion.

**This confirms semantic incompatibility:** the two files are asking different questions about different subsets of hexagrams. The base asks "which lines change in dissipator hexagrams?" while the enriched asks "which lines are stressed across all hexagrams?"

This cannot be resolved by normalizing or renaming. The criteria are fundamentally different.

---

## 11. Provenance Finding: Master JSON Metadata

The `kingwen_oracle_master.json` files reveal the generation source:

| Property | Base (`kingwen_oracle_master.json`) | Enriched (`kingwen_oracle_master (1).json`) |
|---|---|---|
| `source` | `shotgun_expand(emotional_input=50)` | `kingwen-oracle-worker` |
| `session_id` | None | `ws-openjarvis` |
| `emotional_input` | None (embedded in source string) | 88 |
| `schema_version` | None | 2.0 |
| `total_hexagrams` | 64 | 64 |

**Critical finding:** The `(1)` files were generated by the **Cloudflare Worker** (`kingwen-oracle-worker`) during a session with `emotional_input=88` and `session_id=ws-openjarvis`. The base files were generated by the **local Python engine** (`shotgun_expand(emotional_input=50)`).

This explains the value differences:
- Different emotional_input (88 vs 50) → different quantum avatar modulation → different emotional vectors
- Different code paths (worker TS vs local Python) → potentially different computation
- The worker may use `collapse_full_128` (now deprecated) while the local engine uses `shotgun_expand`

**Note:** The user previously directed that the `kingwen-oracle-worker` should be treated as a "previous agent's slick minimal attempt" and ignored. However, the metadata reveals that the `(1)` CSVs (which have MORE columns and different values) were generated by that worker. This does not validate the worker's approach — it only explains the provenance of the `(1)` files.

The base files (without `(1)`) were generated by `shotgun_expand(emotional_input=50)` — the canonical local engine. Their values are derived from the immutable tables, not from the worker.

**Implication for the audit:** The value differences between base and `(1)` files are partly explained by different emotional_input values (50 vs 88) and different code paths (local Python vs Cloudflare Worker TS). This does not resolve which is "correct" — it only explains why they differ.

## 12. Track A Finding: PHASE_LINE_MAP Comparison

The canonical phase model (`PHASE_LINE_MAP` in `kingwen_ternary_tables_complete.py`) defines changing lines per phase:

| Phase | Temporal | Changing Lines (1-indexed) | Count |
|---|---|---|---|
| 0 (0b000) | past | [] | 0 |
| 1 (0b001) | present | [1, 4] | 2 |
| 2 (0b010) | future | [2, 5] | 2 |
| 3 (0b011) | transition | [1, 2, 4, 5] | 4 |
| 4 (0b100) | resolution | [3, 6] | 2 |
| 5 (0b101) | dissolution | [1, 3, 4, 6] | 4 |
| 6 (0b110) | crystallization | [2, 3, 5, 6] | 4 |
| 7 (0b111) | void | [1, 2, 3, 4, 5, 6] | 6 |

### Comparison Result

| Metric | Base (27 yao) | Enriched (156 yao) |
|---|---|---|
| Hexagrams with yao | 13 | 42 |
| Matching a phase's changing-line set | **0 of 13** | **0 of 42** |
| Line-count distribution | 1-3 lines per hexagram | 2 (8), 4 (30), 5 (4) hexagrams |

**Critical finding:** Neither CSV version's yao classification matches ANY phase in the canonical PHASE_LINE_MAP. The changing-line sets in the CSVs (e.g., [2,6], [4,6], [3], [1,5,6]) do not correspond to any phase's defined changing positions.

### Implication

The `yao_lines` CSVs are **NOT encoding phase-derived changing lines**. They represent something else — possibly:
1. Inherent "stress points" of each hexagram (static property, not phase-dependent)
2. Emotional activation thresholds
3. Category-specific behavior markers
4. Some other semantic not tied to the 8-phase model

This means the CSVs and the PHASE_LINE_MAP are **different classification systems** operating on different dimensions. The CSVs do not represent phase transitions at all.

This is a significant finding for the audit: the `ternary_state` field in the yao_lines CSVs is **not** the same concept as the phase-derived changing lines in the canonical engine. They are different properties of the same hexagram, recorded in different representations.

### Updated Gate 2 Status

| Question | Previous Status | Updated Status |
|---|---|---|
| Are the two Yao criteria equivalent? | No — incompatible | **No — incompatible** (unchanged) |
| Is either definition authoritative? | Unresolved | **Unresolved** (unchanged) |
| Is `ternary_state` safe as shared cross-generation field? | No | **No** (unchanged) |
| Are `is_stressed`/`is_activated` independent? | Unresolved | **Unresolved** (unchanged) |
| Is enriched `direction` semantically validated? | Unresolved | **Unresolved** (unchanged) |
| Can the files be reconciled without losing meaning? | Not established | **Not established** (unchanged) |
| Do the CSVs encode phase-derived changing lines? | Not investigated | **No** — neither version matches any PHASE_LINE_MAP phase |
| Define canonical runtime changing-line semantics | Pending | **Pending** — PHASE_LINE_MAP is the canonical phase model, but CSVs encode a different property |

**Gate 2 remains OPEN.**

## 13. Phase Terminology and Cross-System Semantic Separation

### 13.1 Finding

The repository uses phase-related terminology across multiple systems with different mathematical representations and operational purposes. Four distinct concepts have been identified:

| Type | Representation | Operational Purpose |
|---|---|---|
| Canonical temporal phase | 3-bit integer, 0–7 | Determines temporal classification and changing-line positions |
| Visualization oscillation phase | Continuous angular quantity | Drives Godhead interference and 3D animation |
| Wave-packet evolution time | Continuous numerical time steps | Advances split-step Fourier simulation |
| Acoustic signal parameters | Frequency (Hz), duration, encoded state | Controls acoustic signal generation and transmission |

### 13.2 Canonical Temporal Phase

`PHASE_LINE_MAP` and `PHASE_INFO` in `kingwen_ternary_tables_complete.py` define eight discrete temporal configurations. Each phase maps to a predetermined set of changing-line positions. This is the canonical source for phase-derived changing-line classification.

### 13.3 Visualization Oscillation Phase

The Godhead interference calculation in `generate_sovereign_world.py` (lines 1831-1846) uses:

```
phase = presentTime * (qwpFundHz / 108.0) * 1.5 + sIdx * 0.098
godheadInterference += Math.sin(phase) * sp.tension * sp.suction
```

This produces a continuous oscillator phase used in visualization calculations. It is distinct from the canonical 3-bit temporal phase. No demonstrated mapping establishes equivalence between them.

### 13.4 Wave-Packet Evolution

The wave-packet prewarming system (`prewarm_quantum_wavepackets.py`) uses continuous numerical time evolution through split-step Fourier calculations (dt=0.02, 3 warmup steps, 1D/2D/3D grids). Its time-step parameter and simulation state are not equivalent to the canonical temporal phase.

### 13.5 Acoustic Signal Parameters

The acoustic protocol (`KING_WEN_LINK_ACOUSTIC_PROTOCOL.md`, `functions/api/kingwen-link.js`) uses frequencies (80-8000 Hz), frame durations (120ms), and encoded state information. Frequency is not itself phase. Although an acoustic waveform has an oscillatory phase, the protocol's frequency parameters do not establish equivalence with the canonical temporal phase.

### 13.6 Relationship to Yao-Line Classification

Neither CSV generation's Yao classifications match the canonical `PHASE_LINE_MAP` changing-line sets. The visualization, wave-packet, and acoustic systems provide no additional evidence that the CSV classifications are phase-derived.

The Yao-line CSVs therefore remain a separate behavioral classification dimension pending recovery of their original semantic contracts.

### 13.7 Governing Principle

**Shared terminology does not establish shared mathematical meaning.**

Canonical temporal phase, visualization oscillator phase, numerical simulation time, and acoustic signal parameters must retain distinct definitions and provenance unless an explicit, validated transformation establishes a relationship.

No normalization, conversion, or canonical-authority decision follows from this finding.

### 13.8 Cross-Cutting Audit Requirement

The following terms in King Wen have at least two distinct meanings and must be treated as semantic-boundary risks:

| Term | Meaning A | Meaning B |
|---|---|---|
| `ternary_state` | Stable binary identity (base CSV) | Changing-line classification (enriched CSV) |
| `yao` | Changing-line marker in base CSV (27 lines) | Stress/activation classification in enriched CSV (156 lines) |
| `phase` | 3-bit temporal state (0-7, canonical) | Continuous oscillator angle (visualization) |
| `pellet` | 6-Yao acoustic frequency element (80-8000 Hz) | 64-hexagram save-string token (24 fields) |
| `direction` | (not present in base CSV) | rising/falling/stable (enriched CSV) |

No subsystem should assume another subsystem's vocabulary has identical meaning without explicit semantic contract verification.

### 13.9 Gate 2 Status

**Gate 2 remains OPEN.** This finding clarifies the boundaries between systems; it does not select a canonical representation or authorize implementation changes.

## 14. Final Disposition

| Item | Previous Disposition | Updated Disposition |
| `base_state` equivalence | Equivalent | **Equivalent** (unchanged) |
| `ternary_state` semantics | Semantic incompatibility | **Confirmed semantic incompatibility** — base filters by category+porosity, enriched filters by stress/activation |
| `direction`/`is_stressed`/`is_activated` | Derived-stage addition | **Derived-stage addition** (unchanged) |
| Generator provenance | Unknown | **Unknown** (unchanged) |
| Canonical authority | Unresolved | **Unresolved** — requires semantic definition of "changing" per generation |

**Gate 2 remains OPEN.**