# Remediation Verification Matrix — 2026-11-02

## Purpose

Read-only matrix connecting each post-change remediation to its applicable R-register entries, original failure evidence, specific verification tests, seven invariants, and historical regression targets. This matrix implements the "implemented ≠ tested ≠ accepted" distinction.

## Non-negotiable constraints (unchanged)

- No source modifications authorized by this document.
- No formula changes.
- No destructive normalization or collapse.
- No forced equivalence between representations.
- No deletion or consolidation of independent implementations.
- Preserve unique capabilities and historical outputs.
- Gate 2 remains OPEN.
- QSMC-1's original nine-document baseline remains frozen.

## Matrix

### Entry 1: Zero-preservation fixes (explicit 0.0)

| Field | Value |
|-------|-------|
| **Changed files** | `decision_matrix.py`, `emotional_engine.py`, `multi_layer_expand.py`, `schauberger_parsing_layers.py` |
| **Applicable R-entries** | R-11 (viewer zero masking), R-14 (Hamiltonian zero output) |
| **Original failure evidence** | `or 0.35` / `or 0.0875` fallbacks silently replaced explicit `0.0` with `0.35`/`0.0875` due to Python falsy evaluation. Verified 2026-11-02: `float(inject.get("porosity", 0.35) or 0.35)` returns 0.35 when porosity is 0.0. |
| **Change applied** | Removed `or 0.35` / `or 0.0875` from 7 locations across 4 files. Replaced with explicit `None` checks preserving 0.0. |
| **Verification tests** | Test inputs: 0.0, None, missing key, 0.35, 1.0. Expected: 0.0 preserved, None→default, missing→default, 0.35→0.35, 1.0→1.0. |
| **Seven invariants** | INV-01 through INV-07: N/A (no representation structure changed) |
| **Historical regression target** | 2026-09-18: expansion-first, no early collapse. Zero values must remain distinguishable from missing values. |
| **Disposition** | `INCONCLUSIVE` — implemented, not yet tested against all four input classes (0.0, None, missing, nonzero) |

### Entry 2: Import path fixes

| Field | Value |
|-------|-------|
| **Changed files** | `kingwen_train_data/build_full_shotgun_jsonl.py`, `scripts/full_hexagram_shotgun.py` |
| **Applicable R-entries** | R-01 (missing `scripts/__init__.py`), R-02 (nonexistent `shotgun_expand_output.json`) |
| **Original failure evidence** | `from kingwen_train_data.kingwen_quantum_process import _hamiltonian_energy` failed (module not found). `from schauberger_parsing_layers import ...` failed from repo root (no `scripts/__init__.py`). Verified 2026-11-02. |
| **Change applied** | `build_full_shotgun_jsonl.py`: import changed from `kingwen_quantum_process` to `emotional_engine`. `full_hexagram_shotgun.py`: import wrapped in try/except (`from scripts.schauberger_parsing_layers` → `from schauberger_parsing_layers`). |
| **Verification tests** | Execute all 7 affected consumers: `build_full_shotgun_jsonl.py`, `build_per_hex_training_data.py`, `hexagram_shotgun_matcher.py`, `kingwen_quantum_expand.py`, `build_512_widget.py`, `kingwen_mobius_sphere.py`, `kingwen_state_transition.py`. Each must run without import error AND produce correct output. |
| **Seven invariants** | INV-01 through INV-07: N/A (no representation structure changed) |
| **Historical regression target** | 2026-10-27: loader repair passed basic checks but did not verify downstream consumption. This remediation must not repeat that gap. |
| **Disposition** | `INCONCLUSIVE` — import fixes applied, but 7 affected consumers not yet executed |

### Entry 3: Hamiltonian argument correction

| Field | Value |
|-------|-------|
| **Changed files** | `scripts/full_hexagram_shotgun.py` |
| **Applicable R-entries** | R-14 (M3 Hamiltonian zero output), R-15 (M3→M6 degenerate amplitude) |
| **Original failure evidence** | `hamiltonian_energy(vec, vec, ...)` passed the same vector for both resolved and expanded, making q̇ identically 0. Verified 2026-11-02: 1,536/1,536 states had H=0.0. |
| **Change applied** | Changed to `hamiltonian_energy(resolved_vec, expanded_vec, ...)` — passes distinct vectors. |
| **Verification tests** | Reproduce M3 across original test population (1,536 states). Compare H values before/after. Verify: (1) q̇ is no longer identically 0, (2) pq_dot and lagrangian scales still differ (dimensional incompatibility may persist), (3) M6 imaginary amplitude responds to any nonzero H, (4) no new zero-output states introduced. |
| **Seven invariants** | INV-01 through INV-07: N/A (no representation structure changed, but INV-02/INV-03/INV-04/INV-05 remain phase=0 only) |
| **Historical regression target** | 2026-10-27: M3 zero was visible in serialized data. 2026-11-02: runtime evidence established scale mismatch. The argument fix addresses q̇ degeneracy but does NOT resolve dimensional incompatibility. |
| **Disposition** | `INCONCLUSIVE` — argument fix applied, but dimensional mismatch (pq_dot ~0.01 vs lagrangian ~1–5) may still produce H=0 for all states. Requires reproduction across full test population. |

### Entry 4: Deterministic token ordering

| Field | Value |
|-------|-------|
| **Changed files** | `emotional_engine.py` |
| **Applicable R-entries** | R-03 (empty text), R-04 (default intent) — indirectly, via determinism |
| **Original failure evidence** | `query_tokens`: `list(word_set)` — Python set iteration order is `PYTHONHASHSEED`-dependent. Verified 2026-11-02: different hash seeds produced different token orderings. |
| **Change applied** | `sorted(word_set)` — deterministic lexicographic ordering. |
| **Verification tests** | Run `extract_intent()` with `PYTHONHASHSEED=0`, `PYTHONHASHSEED=12345`, `PYTHONHASHSEED=99999`. Verify identical `query_tokens` output across all three seeds. |
| **Seven invariants** | INV-01 through INV-07: N/A (no representation structure changed) |
| **Historical regression target** | 2026-10-27: deterministic token ordering was a known concern. The fix must not alter the set membership (only ordering). |
| **Disposition** | `INCONCLUSIVE` — fix applied, not yet verified across multiple hash seeds |

### Entry 5: Pre-slider consensus removal

| Field | Value |
|-------|-------|
| **Changed files** | `emotional_engine.py` (`capture_pre_slider`) |
| **Applicable R-entries** | R-27 (personality consensus aggregation) |
| **Original failure evidence** | `capture_pre_slider` called `_compute_consensus_from_resolved()` and stored `consensus` hexagram ID/temporal in output. This produced a single-hex consensus from a pre-slider (phase=0) capture. |
| **Change applied** | Removed consensus computation. Returns `consensus: None`. Consensus computation moved to `personality_consensus` in `shotgun_expand()` which aggregates across all 64 hexagrams. |
| **Verification tests** | Verify no downstream consumer reads `capture_pre_slider().consensus` or `capture_pre_slider().consensus_hexagram_id`. Verify `shotgun_expand().personality_consensus` still produces aggregation (not single-hex collapse). |
| **Seven invariants** | INV-07: Verify `personality_consensus` is still aggregation, not collapse |
| **Historical regression target** | 2026-09-18: expansion-first, no early collapse. Pre-slider capture must not produce consensus. |
| **Disposition** | `INCONCLUSIVE` — consensus removed from pre-slider, but downstream consumer dependency not yet verified |

### Entry 6: Porosity None resolution (kingwen_mobius_sphere.py, kingwen_state_transition.py)

| Field | Value |
|-------|-------|
| **Changed files** | `scripts/kingwen_mobius_sphere.py`, `scripts/kingwen_state_transition.py` |
| **Applicable R-entries** | R-01 (import path), R-02 (nonexistent file), R-16 (mesh provenance) |
| **Original failure evidence** | Both files referenced `shotgun_expand_output.json` (never existed). Loaded from nonexistent file. `porosity` defaulted to `0.5` (could mask explicit 0.0). |
| **Change applied** | Load from live `shotgun_expand()` instead of nonexistent file. `porosity` default changed to `None` with resolution from `_INJECT_SITES` (inject_site porosity). |
| **Verification tests** | Execute both scripts. Verify: (1) no import error, (2) `_INJECT_SITES` populated from live `shotgun_expand()`, (3) porosity resolves from inject_site when not explicitly provided, (4) explicit `porosity=0.0` is preserved (not replaced by inject_site value), (5) mesh coordinates change when porosity changes. |
| **Seven invariants** | INV-01 through INV-07: N/A (no representation structure changed, but porosity resolution must not collapse to default) |
| **Historical regression target** | 2026-09-27: 3D positional representations existed. Mesh provenance must be traceable to canonical producer. |
| **Disposition** | `INCONCLUSIVE` — scripts modified, not yet executed or verified |

### Entry 7: README count updates

| Field | Value |
|-------|-------|
| **Changed files** | `README.md` |
| **Applicable R-entries** | R-19 (output differentiation) — documentation only |
| **Original failure evidence** | README stated 470 binary / 18 ternary JKD ingestion records; actual counts are 540 / 21. Path reference `DATASETS/full_shotgun_expansion_all.jsonl` corrected to `kingwen_train_data/full_shotgun_expansion_all.jsonl`. |
| **Change applied** | Count updates: 470→540, 18→21. Path fix. |
| **Verification tests** | Reconcile counts against actual dataset files. Verify `jkd_ingestion_binary.jsonl` has 540 records and `jkd_ingestion_ternary.jsonl` has 21 records. Verify file path exists. |
| **Seven invariants** | INV-01 through INV-07: N/A (documentation only) |
| **Historical regression target** | 2026-09-27: large/small outputs serve distinct purposes. README must accurately describe both. |
| **Disposition** | `INCONCLUSIVE` — counts updated, not yet reconciled against actual files |

### Entry 8: Schauberger parsing emotional_input propagation

| Field | Value |
|-------|-------|
| **Changed files** | `scripts/full_hexagram_shotgun.py` |
| **Applicable R-entries** | R-08 (schauberger parsing phase=0 only) |
| **Original failure evidence** | `schauberger_parsing_layers(h_id, phase_bits=0, emotional_input=0, ...)` — emotional_input hardcoded to 0, ignoring the actual emotional_input parameter passed to `shotgun_expand()`. |
| **Change applied** | `emotional_input=0` → `emotional_input=emotional_input` (passes through the actual value). |
| **Verification tests** | Run `shotgun_expand(request_text="", emotional_input=50)` and `shotgun_expand(request_text="", emotional_input=75)`. Compare `expanded[0]["schauberger_parsing"]` between the two. Verify vortex_tension, suction_coefficient, or other Schauberger metrics differ when emotional_input differs. |
| **Seven invariants** | INV-02: Schauberger parsing remains phase=0 only (check that it's still None for resolved states) |
| **Historical regression target** | 2026-09-18: deterministic generation, no pseudo-random substitution. Emotional input must propagate, not be hardcoded. |
| **Disposition** | `INCONCLUSIVE` — fix applied, not yet verified that emotional_input actually affects Schauberger output |

---

## Entry 1 Verification Results (2026-11-02)

### Test execution
- Script: `cache/scripts/test_zero_preservation.py`
- Environment: Python 3.11, Windows, repo root CWD
- Result: 13/13 PASS, 0 FAIL (after correcting test key name from `porosity_mean` to `consensus_porosity_mean`)

### Findings (not source changes)

| # | Finding | Location | Severity | Description |
|---|---------|----------|----------|-------------|
| F-01 | Remaining `or 0.0875` fallback | `multi_layer_expand.py:235` | **High** | `porosity_norms.append(float(item.get("inject_site", {}).get("porosity_norm", 0.0875) or 0.0875))` — explicit 0.0 porosity_norm is still masked to 0.0875. This line was NOT included in the original fix. |
| F-02 | None value not handled | `decision_matrix.py:195`, `emotional_engine.py:1046`, `multi_layer_expand.py:231` | **Medium** | When `inject_site` contains `"porosity": None`, `.get("porosity", 0.35)` returns `None` (not the default 0.35), and `float(None)` raises TypeError. The default only applies when the key is absent, not when it exists with None. |
| F-03 | Redundant `or 0.0` (harmless) | `emotional_engine.py:1223` | **Low** | `inject_site.get("porosity", 0.0) or 0.0` — redundant but not harmful since 0.0 or 0.0 = 0.0. |
| F-04 | `or 0.0` in vector extraction (separate concern) | `emotional_engine.py:1046,1127,1152,1221,1232,1235,1366-1370` | **Low** | These `or 0.0` patterns are on vector/expression keys, not porosity. They mask 0.0 expression values but are not part of the porosity zero-preservation scope. |

### Disposition
- **Entry 1 status:** `INCONCLUSIVE` (not `PASSED`)
- The 13 passing tests verify that the FIXED code paths preserve 0.0. They do NOT verify that ALL porosity code paths are fixed (F-01, F-02 remain).
- F-01 is a genuine remaining bug in the same function (`open_pool_consensus`) that was partially fixed.
- F-02 is a genuine edge case (None value) not covered by the original fix scope.
- No source changes authorized by this document. Findings reported for future remediation.

| Entry | Changed Files | R-Entries | Priority | Current Disposition |
|-------|--------------|-----------|----------|---------------------|
| 1 | decision_matrix.py, emotional_engine.py, multi_layer_expand.py, schauberger_parsing_layers.py | R-11, R-14 | 1 (zero preservation) | INCONCLUSIVE |
| 2 | build_full_shotgun_jsonl.py, full_hexagram_shotgun.py | R-01, R-02 | 2 (import/consumer execution) | INCONCLUSIVE |
| 3 | full_hexagram_shotgun.py | R-14, R-15 | 4 (M3/M6 numerical reproduction) | INCONCLUSIVE |
| 4 | emotional_engine.py | R-03, R-04 | 3 (determinism) | INCONCLUSIVE |
| 5 | emotional_engine.py | R-27 | 3 (determinism) | INCONCLUSIVE |
| 6 | kingwen_mobius_sphere.py, kingwen_state_transition.py | R-01, R-02, R-16 | 2 (import/consumer execution) | INCONCLUSIVE |
| 7 | README.md | R-19 | 5 (documentation) | INCONCLUSIVE |
| 8 | full_hexagram_shotgun.py | R-08 | 2 (import/consumer execution) | INCONCLUSIVE |

## Entry 2 Verification Results (2026-11-02)

### Import execution test

| Consumer | Import Status | Runtime Status | shotgun_expand_output.json Reference | Notes |
|----------|--------------|----------------|-------------------------------------|-------|
| kingwen_mobius_sphere.py | OK | FUNCTIONAL (tested: hex 1, 15, 52) | Removed (loads from live shotgun_expand) | Porosity resolves from _INJECT_SITES |
| kingwen_state_transition.py | OK | FUNCTIONAL (tested: _INJECT_SITES populated, 64 entries) | Removed (loads from live shotgun_expand) | _INJECT_SITES populated from live shotgun_expand() |
| hexagram_shotgun_matcher.py | OK | NOT TESTED (references nonexistent file) | STILL PRESENT (line 28) | Imports OK but crashes at runtime when file is read |
| build_per_hex_training_data.py | OK | NOT TESTED (references nonexistent file) | STILL PRESENT (line 30) | Imports OK but crashes at runtime when file is read |
| kingwen_quantum_expand.py | FAIL (crashes on import) | NOT RUNNABLE | STILL PRESENT (line 46) | FileNotFoundError on import |
| build_512_widget.py | FAIL (crashes on import) | NOT RUNNABLE | STILL PRESENT (line 6) | FileNotFoundError on import |
| build_full_shotgun_jsonl.py | FAIL (crashes on import) | NOT RUNNABLE | NOT PRESENT (uses from scripts.full_hexagram_shotgun) | ModuleNotFoundError — scripts is not a package (no __init__.py) |

### Findings (not source changes)

| # | Finding | Location | Severity | Description |
|---|---------|----------|----------|-------------|
| F-05 | 4 of 7 consumers still reference nonexistent file | hexagram_shotgun_matcher.py:28, build_per_hex_training_data.py:30, kingwen_quantum_expand.py:46, build_512_widget.py:6 | High | shotgun_expand_output.json never existed. Only 3 of 7 consumers were fixed. |
| F-06 | build_full_shotgun_jsonl.py import path broken | kingwen_train_data/build_full_shotgun_jsonl.py:34 | High | from scripts.full_hexagram_shotgun fails because scripts/__init__.py does not exist. The kingwen_quantum_process → emotional_engine fix was applied but the scripts. prefix issue was not addressed. |
| F-07 | No scripts/__init__.py | scripts/ directory | Medium | The from scripts.xxx import pattern requires scripts to be a package. Either add __init__.py or change all imports to flat from xxx import. |
| F-08 | Porosity consumer dependency | All 7 consumers | Medium | 3 fixed consumers now load porosity from live shotgun_expand(). 4 unfixed consumers still reference nonexistent file and cannot verify porosity consumption. |
| F-05b | Additional broken consumer (additive discovery) | `build_unified_bin.py:23` | High | References `"shotgun_expand_output.json"` — same nonexistent file as F-05's four consumers. Not included in the original 7-consumer classification. Discovered during producer-to-consumer lineage inventory (2026-11-02). Provisional F-05b; separate verification status required. |

### Expanded consumer population (additive, 2026-11-02)

| Classification | Consumers | Count |
|---|---|---|
| Original matrix population (Entry 2) | 4 broken + 3 other tracked consumers | 7 |
| Additional discovery | `build_unified_bin.py:23` | 1 |
| Expanded known population | Original 7 + additional consumer | 8 |

### Disposition
- Entry 2 status: INCONCLUSIVE (not PASSED)
- 3 of 7 consumers are functional (mobius_sphere, state_transition, and module-level imports of hexagram_shotgun_matcher and build_per_hex_training_data).
- 4 of 7 consumers are not runnable (build_512_widget, kingwen_quantum_expand, build_full_shotgun_jsonl, and the runtime paths of hexagram_shotgun_matcher and build_per_hex_training_data).
- The original fix scope (7 consumers) was only partially addressed.
- No source changes authorized by this document. Findings reported for future remediation.

## Entry 3 Verification Results (2026-11-02)

### M3 Hamiltonian numerical reproduction

#### Test execution
- Population: 1,536 states (64 hexagrams × 8 phases × 3 inputs: 0, 50, 100)
- Environment: Python 3.11, Windows, repo root CWD
- Function: `_hamiltonian_energy(resolved_vector, expanded_vector, line_balance)` in `emotional_engine.py:408-450`
- Caller: `full_hexagram_shotgun.py:678-683` (changed from `hamiltonian_energy(vec, vec, ...)` to `hamiltonian_energy(resolved_vec, expanded_vec, ...)`)

#### Results

| Metric | Value | Assessment |
|--------|-------|------------|
| Total states tested | 1,536 | Full population |
| States with H == 0.0 | 1,536 (100%) | UNCHANGED from pre-fix |
| States with H != 0.0 | 0 (0%) | No improvement |
| avg_hamiltonian_energy | 0.0 | Still zero |
| min_hamiltonian_energy | 0.0 | Still zero |
| max_hamiltonian_energy | 0.0 | Still zero |

#### Dimensional analysis (first state, hex 1, phase 0)

| Component | Value | Scale |
|-----------|-------|-------|
| pq_dot (Σ momentum × q̇) | 0.00947 | ~0.01 (vector axes 0-1, differences ~0.01-0.05) |
| lagrangian (abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2) | 5.1 | ~1-5 (line counts 0-6) |
| raw H (no clamp) | -5.0905 | Negative |
| clamped H | 0.0 | Floors to 0.0 |

#### Findings (not source changes)

| # | Finding | Location | Severity | Description |
|---|---------|----------|----------|-------------|
| F-09 | q̇ degeneracy fixed | full_hexagram_shotgun.py:678-683 | Low (resolved) | The argument change from `hamiltonian_energy(vec, vec, ...)` to `hamiltonian_energy(resolved_vec, expanded_vec, ...)` successfully produces nonzero q_dot values. q_dot is no longer identically 0. |
| F-10 | Semantic and scale incompatibility persists (dimensional compatibility established; semantic compatibility not established) | emotional_engine.py:408-450 | **High** | pq_dot operates on ~0.01 scale (vector axes 0-1). Lagrangian operates on ~1-5 scale (line counts 0-6). The subtraction `pq_dot - lagrangian` is always negative. `_clamp()` floors to 0.0. This is the root cause of M3 zero output, NOT the degenerate argument. Both terms are dimensionless but semantically heterogeneous: pq_dot is a continuous vector-space quantity; lagrangian is a discrete line-count quantity. No common mathematical basis for subtraction has been established. Coefficients (0.5, 0.3, 0.2) are dimensionless, undocumented, with no theoretical basis found. |
| F-11 | M6 imaginary amplitude remains zero | downstream consumers | **High** | M6 (quantum avatar modulation) inherits H=0.0. Imaginary amplitude = 0.0 for all states. Complex amplitude is purely real. This is a consequence of F-10, not an independent bug. |
| F-12 | _clamp is one-sided | emotional_engine.py:450 | Medium | `return _clamp(pq_dot - lagrangian)` uses `_clamp` with default bounds 0.0-1.0. Negative values are floored to 0.0. Even if scales were compatible, negative H would still be lost. |

#### Disposition
- **Entry 3 status:** `INCONCLUSIVE` (not `PASSED`)
- The argument fix (F-09) addressed q̇ degeneracy but did NOT resolve the dimensional mismatch (F-10).
- H remains 0.0 for all 1,536 states — same as pre-fix.
- M6 imaginary amplitude remains 0.0 — same as pre-fix.
- The root cause is dimensional incompatibility between pq_dot (~0.01) and lagrangian (~1-5), compounded by one-sided clamping.
- No source changes authorized by this document. Findings reported for future remediation.

1. **Zero preservation (Entry 1):** Test 0.0, None, missing, nonzero across all 4 files. Verify explicit zeros are preserved.
2. **Import/consumer execution (Entries 2, 6, 8):** Execute all 7 affected consumers. Verify each runs and produces correct output.
3. **Determinism (Entry 4):** Compare across multiple PYTHONHASHSEED values.
4. **M3/M6 numerical reproduction (Entry 3):** Reproduce across full test population. Verify q̇ no longer identically 0. Verify dimensional mismatch still present.
5. **Pre-slider consensus removal (Entry 5):** Verify no downstream consumer requires removed consensus.
6. **Documentation (Entry 7):** Reconcile counts against actual files.

## Entry 3 Raw Value Distribution (2026-11-02)

### Hypothesis test: do raw H values vary or are they identical?

**Result: Raw H values VARY significantly.** The clamp is the sole information-loss mechanism.

#### Raw H distribution (1,536 states, no clamp)

| Metric | Value |
|--------|-------|
| Total states | 1,536 |
| Distinct raw H values | 727 |
| Min raw H | -5.094550 |
| Max raw H | -0.560876 |
| Mean raw H | -1.656209 |
| All raw H < 0 | True (100%) |
| All raw H == 0 | False (0%) |
| Distinct raw H → observed (clamped) | 727 → 1 (0.0) |
| Information lost | 726 distinct values destroyed |

#### pq_dot distribution

| Metric | Value |
|--------|-------|
| Distinct pq_dot values | 727 |
| Min | -0.150831 |
| Max | 0.147103 |
| Mean | -0.020272 |

#### lagrangian distribution

| Metric | Value |
|--------|-------|
| Distinct lagrangian values | 7 |
| Min | 0.700000 |
| Max | 5.100000 |
| Mean | 1.635937 |

#### By emotional_input

| emotional_input | Min | Max | Mean | Distinct |
|----------------|-----|-----|------|----------|
| 0 | -5.094550 | -0.666441 | -1.671437 | 511 |
| 50 | -5.094550 | -0.666441 | -1.663117 | 511 |
| 100 | -5.094550 | -0.560876 | -1.634074 | 511 |

#### By phase

| Phase | Min | Max | Mean | Distinct |
|-------|-----|-----|------|----------|
| 0 | -5.094550 | -2.090632 | -3.029632 | 63 |
| 1 | -2.783471 | -0.690422 | -1.474828 | 64 |
| 2 | -2.772611 | -0.676311 | -1.463411 | 64 |
| 3 | -1.843782 | -0.718023 | -1.263419 | 64 |
| 4 | -2.761035 | -0.560876 | -1.434322 | 118 |
| 5 | -1.843929 | -0.634101 | -1.242629 | 118 |
| 6 | -1.831311 | -0.572550 | -1.220400 | 118 |
| 7 | -2.250831 | -2.014591 | -2.121035 | 118 |

### Hypothesis test results

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| H1: Raw H values are identical (clamp is not the issue) | REJECTED | 727 distinct raw H values across 1,536 states |
| H2: Raw H values vary (clamp is the sole information-loss mechanism) | CONFIRMED | 727 distinct values → 1 observed value (0.0). All raw H negative. |
| H3: Dimensional mismatch causes all-negative H | CONFIRMED | pq_dot (~0.01) << lagrangian (~1-5). raw H always negative. |
| H4: emotional_input has significant effect on H | REJECTED | Min/max nearly identical across 0/50/100. Mean varies by ~0.04. |
| H5: Phase has significant effect on H | CONFIRMED | Phase 0 mean=-3.03, phase 7 mean=-2.12. Significant variation. |

### Conclusions

1. Category A (artificial floor) is confirmed as the primary information-loss mechanism. The one-sided _clamp() destroys 727 distinct H values into a single 0.0.
2. Category C (unattainable supremum) is NOT the issue. Raw H values vary significantly.
3. The dimensional mismatch (F-10) is a secondary issue. Even without the clamp, all H values would be negative. The variation would be preserved, but the sign would be uniformly negative.
4. The lagrangian dominates pq_dot by 2-3 orders of magnitude. The lagrangian has only 7 distinct values (determined by line counts), while pq_dot has 727 distinct values.
5. emotional_input has minimal effect on H. The min/max are nearly identical across 0/50/100.

### Disposition
- Entry 3 status: INCONCLUSIVE (not PASSED)
- Category A (artificial floor) confirmed as primary cause of information loss.
- F-10 (dimensional mismatch) remains unresolved.
- F-12 (one-sided clamp) remains unresolved.
- Raw value distribution diagnostic has been RUN. Results saved to DATASETS/raw_h_distribution_2026-11-02.json.
- No source changes authorized by this document. Findings reported for future remediation.

## Critical Principle

Implemented ≠ Tested ≠ Accepted.

A successful patch (implemented) is not a passing isolated test (tested) and neither is end-to-end restoration (accepted). Each entry must complete all 8 verification protocol steps before receiving a final disposition.

## Constraints maintained

- No source modifications authorized by this document.
- No formula changes.
- No destructive normalization or collapse.
- No forced equivalence between representations.
- No deletion or consolidation of independent implementations.
- Preserve unique capabilities and historical outputs.
- Gate 2 remains OPEN.
- QSMC-1's original nine-document baseline remains frozen.