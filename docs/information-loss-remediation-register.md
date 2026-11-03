# Information-Loss Remediation Register — 2026-11-02

## Purpose

Prioritized register of all demonstrated information-loss findings from the representation-to-consumer continuity audit (8 transitions) and the M3 Hamiltonian scale-mismatch diagnosis. Each entry carries a source location, reproduction evidence, affected consumers, severity, and a proposed correction boundary.

The correction boundary field is mandatory: a correction must not accidentally reintroduce collapse, erase persona agency, or replace ternary positional identity with a superficially equivalent state count.

## Non-negotiable constraints (unchanged)

- No source modifications are authorized by this register.
- No formula changes.
- No destructive normalization or collapse.
- No forced equivalence between representations.
- No deletion or consolidation of independent implementations.
- Preserve unique capabilities and historical outputs.
- Gate 2 remains OPEN.
- QSMC-1's original nine-document baseline remains frozen.

## Severity scale

| Severity | Definition |
|----------|-----------|
| CRITICAL | Blocks downstream consumers from running or produces demonstrably wrong output |
| HIGH | Causes information loss that propagates to multiple consumers |
| MEDIUM | Causes information loss visible only under specific conditions |
| LOW | Cosmetic or documentation-level issue with no functional impact |

## Category 1: Execution Blockers

### R-01 — Missing `scripts/__init__.py`

- **Source location:** `scripts/` directory (no `__init__.py` file exists)
- **Reproduction evidence:** `from scripts.full_hexagram_shotgun import shotgun_expand` fails with `ModuleNotFoundError` from repo root. Verified 2026-11-02.
- **Affected consumers:** `build_full_shotgun_jsonl.py`, `build_per_hex_training_data.py`, `hexagram_shotgun_matcher.py`, `kingwen_quantum_expand.py`, `build_512_widget.py`, `kingwen_mobius_sphere.py`, `kingwen_state_transition.py` (7 files)
- **Severity:** CRITICAL
- **Proposed correction boundary:** Add `scripts/__init__.py` (empty or minimal). Does not modify any formula, representation, or consumer logic. Must not be accompanied by import rewrites that assume package structure beyond what PEP 420 already provides. Verify with `PYTHONPATH=. python -c "from scripts.full_hexagram_shotgun import shotgun_expand"` after.

### R-02 — Nonexistent `shotgun_expand_output.json` reference

- **Source location:** `hexagram_shotgun_matcher.py:28`, `build_per_hex_training_data.py:29` (both reference `ROOT / "shotgun_expand_output.json"`)
- **Reproduction evidence:** File does not exist on disk. Only `full_shotgun_expansion_all.jsonl` exists. Verified 2026-11-02 by full-tree search.
- **Affected consumers:** `build_per_hex_training_data.py` (64 per-hex JSONL files + manifest), `hexagram_shotgun_matcher.py` (paper-to-hex routing)
- **Severity:** CRITICAL
- **Proposed correction boundary:** Update file path references to `full_shotgun_expansion_all.jsonl` or call `shotgun_expand()` directly. Must not create a new intermediate file that duplicates the canonical producer's output. Must preserve the distinction between the canonical producer and any cached serialization.

---

## Category 2: Data Omissions

### R-03 — Empty `text` and `request_text` in all 1,536 JSONL records

- **Source location:** `kingwen_train_data/full_shotgun_expansion_all.jsonl` (all records)
- **Reproduction evidence:** Verified 2026-11-02 — every record has `"text": ""` and `"request_text": ""`. No request context was provided during batch generation.
- **Affected consumers:** All training-data consumers, Megatron training pipeline, any consumer that expects request text for intent classification
- **Severity:** HIGH
- **Proposed correction boundary:** Provide request text during generation or add a provenance field indicating the text was intentionally omitted. Must not fabricate request text. Must not treat empty text as equivalent to "no request" without documenting the distinction.

### R-04 — `intent.dominant_intent` is "understand" for 989/991 records

- **Source location:** `kingwen_train_data/full_shotgun_expansion_all.jsonl` (all records)
- **Reproduction evidence:** Verified 2026-11-02 — 99.8% of records have `dominant_intent: "understand"` (default, not derived from request text).
- **Affected consumers:** Intent classification consumers, training data, any consumer that expects differentiated intent per record
- **Severity:** HIGH
- **Proposed correction boundary:** Derive intent from actual request text or document the default as a documented simplification. Must not silently assign a default without provenance. Must not collapse the 5-axis emotional vector into a single intent label without evidence.

### R-05 — `pre_slider.emotional_input` is 0 (placeholder)

- **Source location:** `scripts/full_hexagram_shotgun.py` — `expand_hexagram()` sets `pre_slider["emotional_input"] = 0` (hardcoded placeholder)
- **Reproduction evidence:** Verified 2026-11-02 — all expanded records have `pre_slider.emotional_input = 0` regardless of the `emotional_input` parameter passed to `shotgun_expand()`.
- **Affected consumers:** Any consumer that reads `pre_slider` expecting the actual emotional input value
- **Severity:** MEDIUM
- **Proposed correction boundary:** Set `pre_slider["emotional_input"]` to the actual `emotional_input` parameter value. Must not change the slider propagation formula. Must not alter the canonical engine.

### R-06 — `personality_subsets` is None for all 512 resolved states

- **Source location:** `scripts/full_hexagram_shotgun.py` — `resolved[]` items set `personality_subsets=None`
- **Reproduction evidence:** Verified 2026-11-02 — 512/512 resolved records have `personality_subsets: null`. Computed only for `expanded[]` (64 records, phase=0).
- **Affected consumers:** Any consumer that expects personality subsets per resolved state
- **Severity:** MEDIUM
- **Proposed correction boundary:** Document that `personality_subsets` is computed for `expanded[]` (phase=0) only by design. The authoritative representation exists in `expanded[hexagram_id-1]`. If consumer needs per-phase personality, it must reference the expanded representation, not expect duplication in resolved[]. Must not duplicate the field across 8 phases without evidence that the computation is phase-dependent.

### R-07 — `ternary_slots` is None for all 512 resolved states

- **Source location:** `scripts/full_hexagram_shotgun.py` — `resolved[]` items set `ternary_slots=None`
- **Reproduction evidence:** Verified 2026-11-02 — 512/512 resolved records have `ternary_slots: null`. Computed only for `expanded[]` (64 records, phase=0).
- **Affected consumers:** Any consumer that expects ternary slot data per resolved state
- **Severity:** MEDIUM
- **Proposed correction boundary:** Document that `ternary_slots` is computed for `expanded[]` (phase=0) only by design. The authoritative representation exists in `expanded[hexagram_id-1]`. Must not duplicate across phases without evidence of phase-dependency.

### R-08 — `schauberger_parsing` is None for all 512 resolved states

- **Source location:** `scripts/full_hexagram_shotgun.py` — `resolved[]` items set `schauberger_parsing=None`
- **Reproduction evidence:** Verified 2026-11-02 — 512/512 resolved records have `schauberger_parsing: null`. Computed only for `expanded[]` (64 records, phase=0).
- **Affected consumers:** Any consumer that expects Schauberger metrics per resolved state
- **Severity:** MEDIUM
- **Proposed correction boundary:** Document that `schauberger_parsing` is computed for `expanded[]` (phase=0) only by design. The authoritative representation exists in `expanded[hexagram_id-1]`. Must not duplicate across phases without evidence of phase-dependency.

### R-09 — `projections` absent from resolved[] items

- **Source location:** `scripts/full_hexagram_shotgun.py` — `resolved[]` item dict does not include `projections` key
- **Reproduction evidence:** Verified 2026-11-02 — `projections` key is present in `expanded[]` items but absent from `resolved[]` items.
- **Affected consumers:** Any consumer that expects J-space projections per resolved state
- **Severity:** MEDIUM
- **Proposed correction boundary:** Document that `projections` is computed for `expanded[]` (phase=0) only by design. The authoritative representation exists in `expanded[hexagram_id-1]`. Must not duplicate across phases without evidence of phase-dependency.

### R-10 — `domain_routing_palette` absent from resolved[] items

- **Source location:** `scripts/full_hexagram_shotgun.py` — `resolved[]` item dict does not include `domain_routing_palette` key
- **Reproduction evidence:** Verified 2026-11-02 — `domain_routing_palette` is present in `expanded[]` items but absent from `resolved[]` items.
- **Affected consumers:** Any consumer that expects domain routing palette per resolved state
- **Severity:** MEDIUM
- **Proposed correction boundary:** Document that `domain_routing_palette` is computed for `expanded[]` (phase=0) only by design. The authoritative representation exists in `expanded[hexagram_id-1]`. Must not duplicate across phases without evidence of phase-dependency.

---

## Category 3: Semantic Substitutions

### R-11 — Viewer zero masking (`|| 0.75` fallback)

- **Source location:** `scripts/generate_sovereign_world.py:1033` — `const hamiltonian = passage.energy || 0.75;`
- **Reproduction evidence:** Verified 2026-11-02 — JavaScript `||` operator treats `0` as falsy, so `energy: 0` becomes `0.75`. Confirmed via reproduction script.
- **Affected consumers:** Sovereign world viewer, any downstream visualization that reads `passage.energy`
- **Severity:** HIGH
- **Proposed correction boundary:** Replace `|| 0.75` with `?? 0.75` (nullish coalescing) or explicit `passage.energy !== null ? passage.energy : 0.75`. Must not change the computed energy value. Must not mask zero with a nonzero fallback. Must preserve the distinction between "energy is zero" and "energy is absent."

### R-12 — Field-name collision: `hamiltonian_energy`

- **Source location:** `emotional_engine.py` (M3 `_hamiltonian_energy()` — pq_dot − lagrangian, clamped) vs `scripts/ingest_jkd_megatron_wavepackets.py` (JKD ingestion scalar — coherence − chaos − 0.5*darkTone + 0.3*voiceWeight − 0.2*whimsy)
- **Reproduction evidence:** Verified 2026-11-02 — both produce a field named `hamiltonian_energy` with different formulas and meanings. Consumers cannot distinguish which formula produced the value.
- **Affected consumers:** Any consumer that reads `hamiltonian_energy` from JSONL or kit files
- **Severity:** HIGH
- **Proposed correction boundary:** Rename one or both fields to reflect their actual formula (e.g., `hamiltonian_energy_m3` and `hamiltonian_energy_jkd`). Must not change either formula. Must not create a third field that conflates them. Must preserve both as separate semantic entities.

### R-13 — Default intent "understand" assigned to 989/991 equations

- **Source location:** `scripts/math_to_kingwen_adapter.py` — default intent assignment in adapter pipeline
- **Reproduction evidence:** Verified 2026-11-02 — 99.8% of equations receive `dominant_intent: "understand"` (default, not derived from request text or equation content).
- **Affected consumers:** Intent classification consumers, training data, any consumer that expects differentiated intent
- **Severity:** HIGH
- **Proposed correction boundary:** Derive intent from equation content or request text. Must not silently assign a default without provenance. Must not collapse the 5-axis emotional vector into a single intent label without evidence. If default is retained, document it as a documented simplification with explicit provenance.

---

## Category 4: Computational Findings

**Cross-reference to current run (2026-11-02):** R-14 is now superseded by F-10 (semantic/scale incompatibility VALIDATED) and F-12 (one-sided clamp information loss VALIDATED). F-10 establishes the scale mismatch (pq_dot 0-1 vs L 0-6) as root cause; F-12 establishes the clamp as sole information-loss mechanism (727→1 distinct values, 100% loss). R-14's "Verified" status is now "VALIDATED" with more detailed mathematical evidence. See `docs/qsmc1-m3-mathematical-validation-f10.md` and `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

### R-14 — M3 Hamiltonian energy = 0.0 for all states (scale mismatch)

- **Source location:** `emotional_engine.py:395-432` — `_hamiltonian_energy(resolved_vector, expanded_vector, line_balance)`
- **Reproduction evidence:** Verified 2026-11-02 — 1,536/1,536 states have `hamiltonian_energy = 0.0`. Root cause: `pq_dot (~0.01) − lagrangian (~1–5) < 0 → _clamp(lo=0.0) = 0.0`. Dimensional incompatibility: pq_dot operates on emotional-weight product scale; lagrangian operates on line-count scale. 6-phase diagnosis documented in `docs/M3_SCALE_MISMATCH_DIAGNOSIS.md`.
- **Affected consumers:** `emotional_engine.py` (internal), `build_full_shotgun_jsonl.py` (intended direct consumer), `shotgun_rollout_runtime.py`, `rl_shotgun_measurables.py`, `generate_avatar_meshes.py`, M6 imaginary amplitude (degenerate: imag=0 → amplitude=|real|)
- **Severity:** HIGH
- **Proposed correction boundary:** Document the dimensional incompatibility. Do NOT rescale the formula, silently replace zero, or alter the canonical engine. The scale mismatch is a mathematical contract issue, not a bug to patch. Any correction must explicitly define: (1) what pq_dot and lagrangian each measure, (2) whether they are commensurable, (3) what the intended range of H is, (4) what clamping behavior is correct. Must not force nonzero values. Must not change `_clamp()` bounds without semantic justification.

**Cross-reference to current run (2026-11-02):** R-15 is now superseded by F-11 (M6 imaginary amplitude VALIDATED). F-11 establishes type 2 dependency (derived from M3 Hamiltonian via multiplicative path), not independent computation or structural omission. F-11's more detailed dependency analysis replaces R-15's "consequence of R-14" framing. See `docs/qsmc1-m3-m6-imaginary-amplitude-f11.md`.

### R-15 — M3→M6 dependency: degenerate complex-amplitude representation

- **Source location:** `emotional_engine.py` — `imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)` produces 0 when H=0
- **Reproduction evidence:** Verified 2026-11-02 — 512/512 resolved states have `imag = 0`, so `amplitude = sqrt(real² + 0²) = |real|`. M6 coherence varies (136 states > 0.7) but complex amplitude is purely real.
- **Affected consumers:** M6 interference/coherence analysis, any consumer that expects complex-valued wavefunction
- **Severity:** MEDIUM
- **Proposed correction boundary:** Document that M6 complex amplitude is degenerate (purely real) due to M3 H=0. The degeneracy is a consequence of R-14, not an independent finding. Any correction must address R-14 first. Must not fabricate imaginary components. Must not describe the result as "1-dimensional wavefunction" (potentially misleading; evidence establishes purely real-valued sampled amplitude, not necessarily reduced dimensionality of underlying state space).

---

## Category 5: Provenance Gaps

### R-16 — 3D PLY mesh provenance unverified

- **Source location:** `scripts/generate_avatar_meshes.py` — generates 512 PLY files from `expand_hexagram()` output
- **Reproduction evidence:** Verified 2026-11-02 — 512 PLY files exist in `DATASETS/kingwen_avatar_meshes/` (114KB-293KB each). No evidence that mesh vertices are derived from canonical identity (hexagram_id, phase_bits, line_states) rather than procedurally generated from `quantum_avatar_state` alone.
- **Affected consumers:** Any consumer that treats PLY meshes as positional-provenance artifacts
- **Severity:** HIGH
- **Proposed correction boundary:** Trace the source-to-mesh lineage: verify that (1) mesh vertices are derived from `quantum_avatar_state` (which is derived from `expand_hexagram()`), (2) each mesh's scale/rotation/color correspond to specific hexagram×phase identity, (3) no procedural randomization is used. Must not assume provenance from file existence alone. Must not treat meshes as fully traceable until lineage is verified.

### R-17 — Ternary source lineage untraced

- **Source location:** `scripts/kingwen_quantum_expand.py` (729×8 ternary states), `scripts/ternary_full_expansion.json` (2.9MB)
- **Reproduction evidence:** Verified 2026-11-02 — 729 hexagrams × 5,832 resolved ternary states exist in `ternary_full_expansion.json`. No canonical-source lineage traced from this file back to `shotgun_expand()` or `HEXAGRAM_BASE`.
- **Affected consumers:** Any consumer that uses ternary states and expects provenance from the canonical producer
- **Severity:** MEDIUM
- **Proposed correction boundary:** Trace the generation path: verify that `ternary_full_expansion.json` is produced by `kingwen_quantum_expand.py` consuming `HEXAGRAM_BASE` from `kingwen_ternary_tables_complete.py`. Must not assume canonical lineage from file existence alone. Must not treat the ternary layer as equivalent to the binary layer without evidence.

### R-18 — Corpus evidence cardinality unvalidated

- **Source location:** `kingwen_train_data/full_shotgun_expansion_all.jsonl` — 20 corpus evidence items per record
- **Reproduction evidence:** Verified 2026-11-02 — 1,536 records each have 20 corpus evidence items. No validation that these items establish independent confirmation vs. consistent cardinality.
- **Affected consumers:** Any consumer that treats corpus evidence as independent confirmation
- **Severity:** LOW
- **Proposed correction boundary:** Validate whether the 20 corpus evidence items per record are independently sourced or derived from the same source. Must not treat consistent cardinality as evidence of independent confirmation. Must not upgrade unverified evidence to verified status based on count alone.

### R-19 — Output differentiation unverified (50-line vs 30MB)

- **Source location:** `scripts/generate_full_shotgun_30gb.py` (30MB output) vs `scripts/full_hexagram_shotgun.py` (50-line output)
- **Reproduction evidence:** Verified 2026-11-02 — both outputs exist. User states both serve distinct purposes. No formal comparison of information content between the two exists.
- **Affected consumers:** Any consumer that needs to know which output to use for which purpose
- **Severity:** LOW
- **Proposed correction boundary:** Document the distinct purpose of each output. Must not treat one as obsolete or redundant. Must not consolidate outputs without verifying that properties are preserved. Must not assume larger output is more complete or smaller output is sufficient.

### R-20 — Personality-subset intent unverified

- **Source location:** `scripts/full_hexagram_shotgun.py` — `personality_subsets` computed for expanded (phase=0) only
- **Reproduction evidence:** Verified 2026-11-02 — `personality_subsets` is a list for expanded items (64 records) and None for resolved items (512 records). No explicit documentation in code of whether this is intentional.
- **Affected consumers:** Any consumer that expects personality subsets per resolved state
- **Severity:** LOW
- **Proposed correction boundary:** Document whether `personality_subsets=None` on resolved states is intentional. If intentional, document the rationale (phase-dependent computation). If unintentional, compute for all phases. Must not assume intent from absence alone. Must not duplicate field across phases without evidence of phase-dependency.

---

## Category 6: Intentional Boundaries

These are NOT information-loss findings. They are documented intentional representation boundaries that must be preserved during any future remediation.

### R-21 — 729 ternary permutations: count stored, data in separate file

- **Source location:** `scripts/full_hexagram_shotgun.py` (stores `ternary_729_permutations_count: 729`), `scripts/ternary_full_expansion.json` (2.9MB, 729 hexagrams × 5,832 resolved states)
- **Disposition:** Intentionally_separated
- **Correction boundary:** Must not integrate ternary data into `shotgun_expand()` output without verifying that the integration preserves the 9-bit positional identity and does not collapse the ternary layer into the binary layer. The 9-bit ternary decoding is a distinct capability that must be preserved.

### R-22 — Schauberger parsing: phase=0 only

- **Source location:** `scripts/full_hexagram_shotgun.py` — `schauberger_parsing` computed via `schauberger_parsing_layers()` for expanded only
- **Disposition:** Intentionally_separated
- **Correction boundary:** Must not duplicate Schauberger parsing across 8 phases without evidence that the computation is phase-dependent. The authoritative representation exists in `expanded[]` for each hexagram. Consumers needing phase-specific Schauberger metrics must reference the expanded representation.

### R-23 — Domain routing palette: phase=0 only

- **Source location:** `scripts/full_hexagram_shotgun.py` — `domain_routing_palette` computed for expanded only
- **Disposition:** Intentionally_separated
- **Correction boundary:** Must not duplicate domain routing palette across 8 phases without evidence of phase-dependency. The authoritative representation exists in `expanded[]` for each hexagram.

### R-24 — Projections: phase=0 only

- **Source location:** `scripts/full_hexagram_shotgun.py` — `projections` computed for expanded only
- **Disposition:** Intentionally_separated
- **Correction boundary:** Must not duplicate projections across 8 phases without evidence of phase-dependency. The authoritative representation exists in `expanded[]` for each hexagram.

### R-25 — Pre-slider capture: phase=0 only

- **Source location:** `scripts/full_hexagram_shotgun.py` — `pre_slider` computed for expanded only
- **Disposition:** Intentionally_separated
- **Correction boundary:** Must not duplicate pre-slider capture across 8 phases. The authoritative representation exists in `expanded[]` for each hexagram.

### R-26 — 9-bit ternary decoding not integrated into shotgun_expand()

- **Source location:** `kingwen_ternary_tables_complete.py` (9-bit encoding: 6 base + 3 phase), `scripts/kingwen_quantum_expand.py` (`marginalize_to_46656()`)
- **Disposition:** Intentionally_separated
- **Correction boundary:** This is an integration boundary, not a missing implementation. The ternary capability exists independently. Any integration must preserve the binary/ternary distinction and must not collapse the ternary layer into the binary layer. Must not treat the integration gap as a bug to fix without evidence that the separation is accidental.

### R-27 — Personality consensus is aggregation, not collapse

- **Source location:** `scripts/full_hexagram_shotgun.py` — `personality_consensus` computed by `resolve_personality_by_consensus(resolved, consensus_vector)`
- **Disposition:** Preserved
- **Correction boundary:** Must not treat `personality_consensus` as equivalent to `consensus_hexagram_id` without evidence. The consensus is a weighted aggregation across all 64 hexagrams; it does not replace individual hexagram identities. Must not collapse the consensus into a single-hex resolve.

---

## Register Summary

| ID | Category | Severity | Status | Correction Boundary Defined |
|----|----------|----------|--------|---------------------------|
| R-01 | Execution blocker | CRITICAL | Verified | Yes |
| R-02 | Execution blocker | CRITICAL | Verified | Yes |
| R-03 | Data omission | HIGH | Verified | Yes |
| R-04 | Data omission | HIGH | Verified | Yes |
| R-05 | Data omission | MEDIUM | Verified | Yes |
| R-06 | Data omission | MEDIUM | Verified | Yes |
| R-07 | Data omission | MEDIUM | Verified | Yes |
| R-08 | Data omission | MEDIUM | Verified | Yes |
| R-09 | Data omission | MEDIUM | Verified | Yes |
| R-10 | Data omission | MEDIUM | Verified | Yes |
| R-11 | Semantic substitution | HIGH | Verified | Yes |
| R-12 | Semantic substitution | HIGH | Verified | Yes |
| R-13 | Semantic substitution | HIGH | Verified | Yes |
| R-14 | Computational finding | HIGH | Verified | Yes |
| R-15 | Computational finding | MEDIUM | Verified | Yes |
| R-16 | Provenance gap | HIGH | Verified | Yes |
| R-17 | Provenance gap | MEDIUM | Verified | Yes |
| R-18 | Provenance gap | LOW | Verified | Yes |
| R-19 | Provenance gap | LOW | Verified | Yes |
| R-20 | Provenance gap | LOW | Verified | Yes |
| R-21 | Intentional boundary | — | Verified | Yes |
| R-22 | Intentional boundary | — | Verified | Yes |
| R-23 | Intentional boundary | — | Verified | Yes |
| R-24 | Intentional boundary | — | Verified | Yes |
| R-25 | Intentional boundary | — | Verified | Yes |
| R-26 | Intentional boundary | — | Verified | Yes |
| R-27 | Intentional boundary | — | Verified | Yes |

### Severity distribution
- CRITICAL: 2 (R-01, R-02)
- HIGH: 7 (R-03, R-04, R-11, R-12, R-13, R-14, R-16)
- MEDIUM: 8 (R-05, R-06, R-07, R-08, R-09, R-10, R-15, R-17)
- LOW: 3 (R-18, R-19, R-20)
- Intentional boundary (no severity): 7 (R-21 through R-27)

### Remediation priority order (recommended)
1. **CRITICAL (R-01, R-02):** Execution blockers — unblock training-data consumers
2. **HIGH (R-03, R-04, R-11, R-12, R-13, R-14, R-16):** Data omissions, semantic substitutions, computational findings, provenance gaps
3. **MEDIUM (R-05–R-10, R-15, R-17):** Data omissions, computational findings, provenance gaps
4. **LOW (R-18–R-20):** Provenance gaps with minimal functional impact
5. **Intentional boundaries (R-21–R-27):** Must be preserved during all remediation

### Constraints maintained
- No source modifications authorized by this register
- No formula changes
- No destructive normalization or collapse
- No forced equivalence between representations
- No deletion or consolidation of independent implementations
- Preserve unique capabilities and historical outputs
- Gate 2 remains OPEN
- QSMC-1's original nine-document baseline remains frozen