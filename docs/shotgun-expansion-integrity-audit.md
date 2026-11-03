# Shotgun Expansion Integrity Audit

**Date:** 2026-11-02  
**Status:** READ-ONLY AUDIT — no source modifications authorized  
**Purpose:** Detect architectural regression against the original distributed expansion design  
**Correction:** Supersedes the "reinvention" framing from `shotgun-reinvention-audit.md` — the system is a distributed expansion, not a conventional producer-consumer pipeline

---

## Architectural Model (Corrected)

The system is NOT a conventional producer-consumer pipeline where `shotgun_expand()` is the canonical authority and all other files are "reinventions" to be consolidated.

The intended architecture is a **distributed expansion system** with these properties:

| Property | Description |
|----------|-------------|
| Archetype identity | Hexagram archetype establishes structural identity and initial conditions |
| Persona agency | Persona establishes interpretive agency, not a single assigned value |
| Variable retention | Positional, ternary, and domain-specific information is retained |
| Pooling | Contributions pooled WITHOUT destructive collapse |
| Cross-examination | Independent representations compared while preserving differences |
| Domain locking | Domain boundaries survive downstream transformations |
| Expansion continuation | Each identity continues from its own variables, not from a reduced common representation |

**Key distinction:** Pooling ≠ Collapse. Collapse reduces to one value. Pooling combines while retaining source identity.

---

## Audit Dimensions

### 1. Archetype Identity — No Unintended Single-Value Assignment

**Question:** Does any downstream consumer reduce the 64 hexagram archetypes to a single representative value?

**Evidence:**
- `shotgun_expand()` returns ALL 64 expanded + 512 resolved states (no single-hex collapse)
- `personality_consensus` aggregates across all 64 (dominant_agent_type, dominant_domain) but does NOT replace the full expansion
- `emotional_engine.py` `_quantum_avatar_modulation()` uses `_hamiltonian_energy()` but does not collapse to single hex
- `generate_sovereign_world.py` uses JKD scalar (separate formula) but does not collapse

**Finding:** ✅ No unintended single-value assignment found in the seven audited consumers. The `personality_consensus` field is an aggregation, not a collapse — the full 64/512 expansion remains available in the same output.

**Important:** `personality_consensus` is NOT equivalent to `consensus_hexagram_id`. The former aggregates; the latter would collapse. Only the former exists in the current output.

---

### 2. Persona Agency — Independent Persona-Specific Variables Retained

**Question:** Does each persona retain its own variables, or do personas share a single value?

**Evidence:**
- `expanded[]` has 37 keys per hexagram including `table_personality`, `domain_vector`, `training_notes`, `intent`
- `resolved[]` has 26 keys per state including `table_personality`, `domain_vector`, `intent`
- `personality_map` is a separate top-level field (64 entries, one per hexagram)
- `personality_subsets` is populated for all 64 expanded (18 items each) but None for all 512 resolved
- `personality_subsets_total`: 1152 (64 × 18)

**Finding:** ✅ Persona agency is retained at the expanded layer. Each hexagram has its own `table_personality`, `domain_vector`, and `training_notes`. The resolved layer does not carry `personality_subsets` (design choice, not regression).

**Note:** The resolved layer losing `personality_subsets` means consumers reading only `resolved[]` cannot access persona-specific subsets. This is a data-flow gap, not a collapse.

---

### 3. Pooling — Contributions Pooled Without Destructive Collapse

**Question:** When contributions are pooled, is the source identity preserved?

**Evidence:**
- `personality_consensus` uses `dominant_agent_type` and `dominant_domain` — these are aggregation labels, not replacements
- `consensus_vector` in `personality_consensus` is a 5-axis vector (chaos, whimsy, darkTone, coherence, voiceWeight) — this is a mean, not a replacement
- The full `expanded[]` and `resolved[]` arrays remain in the output alongside the consensus

**Finding:** ✅ Pooling does not destructively collapse. The consensus is computed alongside the full expansion, not instead of it. Consumers can access both the pooled consensus and the individual hexagram states.

**Key test:** If a consumer reads only `personality_consensus`, it gets the pooled view. If it reads `expanded[]`, it gets all 64. Both are available. No consumer is forced to use the pooled view.

---

### 4. Positional Identity — Original Positional Information Survives

**Question:** Do downstream consumers preserve the positional encoding of each hexagram state?

**Evidence:**
- `expanded[0]` has `ternary_slots` (6 items), `line_states` (6 items), `line_balance` (6 items), `phase_bits`, `phase_temporal`
- `resolved[0]` has `line_states`, `line_balance`, `phase_bits`, `phase_temporal`
- `kingwen_ternary_tables_complete.py` encodes 9-bit (6 base ternary + 3 phase bits) for 512 states
- `kingwen_quantum_expand.py` has `marginalize_to_46656()` for 729 hexagram × 8 phase = 46,656 states
- `ternary_full_expansion.json` has 27 trigrams, 729 hexagrams, 5,832 resolved states

**Finding:** ✅ Positional identity is preserved in the expanded layer. The resolved layer carries `line_states` and `line_balance` but not `ternary_slots` or `projections`.

**Gap:** Resolved states do not carry `ternary_slots` (6 items) or `projections` (dict). Consumers needing these must read from `expanded[]` instead.

---

### 5. Ternary Decoding — 9-Bit Ternary-to-Binary Decoding Preserved

**Question:** Is the 9-bit ternary decoding capability (6 base ternary + 3 phase bits) preserved across all representations?

**Evidence:**
- `kingwen_ternary_tables_complete.py`: 64 hexagrams × 8 phases = 512 states, each with 9-bit encoding (6 base + 3 phase)
- `kingwen_quantum_expand.py`: `marginalize_to_46656()` converts 729 hexagrams × 8 phases = 46,656 states
- `scripts/ternary_full_expansion.json`: 27 trigrams, 729 hexagrams, 5,832 resolved (729 × 8)
- `full_hexagram_shotgun.py`: `ternary_729_permutations_count: 729` stored per hexagram (count only, not the actual permutations)

**Finding:** ⚠️ PARTIAL. The 9-bit encoding is defined in `kingwen_ternary_tables_complete.py` and the ternary expansion (729) is computed in `kingwen_quantum_expand.py` and stored in `ternary_full_expansion.json`. However:

1. `shotgun_expand()` stores only the **count** (729) in `ternary_729_permutations_count`, not the actual 729 ternary permutations
2. The actual 729 ternary hexagrams and 5,832 resolved ternary states live in `scripts/ternary_full_expansion.json` (2.9MB) — NOT in `shotgun_expand()` output
3. `kingwen_quantum_expand.py` loads `ternary_full_expansion.json` but `shotgun_expand()` does not

**This is the critical finding:** The 9-bit ternary decoding capability EXISTS in the system (in `ternary_full_expansion.json` and `kingwen_quantum_expand.py`), but it is NOT integrated into `shotgun_expand()`'s output. A consumer reading only `shotgun_expand()` output cannot access the 729 ternary permutations or the 5,832 resolved ternary states.

**This is NOT a regression** — it is an architectural gap between the binary layer (512 states in `shotgun_expand()`) and the ternary layer (5,832 states in `ternary_full_expansion.json`). The two layers are not integrated.

---

### 6. Cross-Examination — Independent Representations Remain Comparable

**Question:** Can independent expansions be compared without losing their distinct identities?

**Evidence:**
- Two shotgun output scales exist: 50-line JSON (compact) and 30MB single-shot (full)
- Both are present in the system; neither is obsolete
- `personality_consensus` provides a comparison point across all 64 hexagrams
- `domain_routing_palette` provides per-hexagram routing information

**Finding:** ✅ Independent representations remain comparable. The 50-line and 30MB outputs serve different purposes (compact vs full) and neither is a replacement for the other. Cross-examination is possible via `personality_consensus` and `domain_routing_palette`.

**Important:** A smaller output is not inherently better. A larger output is not inherently more complete. The question is whether each representation retains the information required by its intended consumers.

---

### 7. Domain Locking — Domain Boundaries Survive Downstream

**Question:** Do domain boundaries survive downstream transformations?

**Evidence:**
- `expanded[0]` has `domain_vector` (5-axis), `domain_routing_palette` (dict)
- `resolved[0]` has `domain_vector` (5-axis)
- `personality_consensus` has `dominant_domain` and `domain_distribution`
- `table_sources` identifies 7 source tables (hexagram_base, phase_line_map, yao_vocabulary, inject_site, emotional_weights, pool, personality)

**Finding:** ✅ Domain locking is present. Each hexagram carries its own `domain_vector` and `domain_routing_palette`. The consensus provides a pooled view but does not overwrite individual domain assignments.

**Gap:** `generate_sovereign_world.py` uses a JKD scalar (different formula) stored under the same `hamiltonian_energy` field name. This is a semantic schema collision — the JKD scalar does not share provenance with the M3 Hamiltonian, but they share a field name.

---

### 8. 3D Provenance — Meshes and Scenes Retain Generating Positional Identity

**Question:** Do 3D meshes and scenes retain their generating positional identity?

**Evidence:**
- `update_3d_kits_with_quantum_wavepackets.py` — independent bypass, does not consume M3 H
- `generate_avatar_meshes.py` — direct consumer, inherits H=0
- `DATASETS/kingwen_avatar_meshes/` — 512 PLY files (64 hex × 8 phases)
- `DATASETS/kingwen_model_sets/kit_*.json` — canonical hexagram state packets
- `enrich_kit_models.py` — enriches kit models from shotgun_expand

**Finding:** ✅ 3D provenance is present. 512 PLY meshes (64 × 8 phases) exist with wavefunction amplitudes per phase. Kit JSONs carry Riemann coordinates, rotation, and big_value.

**Gap:** `generate_avatar_meshes.py` inherits H=0 (from M3 scale mismatch). The avatar meshes are modulated by |real| amplitude, not by Hamiltonian energy. The Hamiltonian field in the output is always 0.0.

---

### 9. Output Fidelity — Small and Large Outputs Retain Distinct Information

**Question:** Do the 50-line and 30MB outputs serve different purposes, or is one obsolete?

**Evidence:**
- 50-line JSON: compact summary, suitable for quick inspection
- 30MB single-shot: full expansion with all fields, suitable for training data
- Both exist in the system; neither is a replacement for the other
- `full_shotgun_expansion_all.jsonl` (32MB, 1536 records) is the canonical training-data serialization

**Finding:** ✅ Both outputs serve distinct purposes. The 50-line JSON is a summary; the 30MB output is a full serialization. Neither is obsolete. The question is whether each retains the information required by its intended consumers.

**Gap:** `build_full_shotgun_jsonl.py` (the intended serializer) is blocked by import failure. The 32MB JSONL exists but was produced by an unknown generator (not the canonical builder).

---

### 10. Consumer Integrity — Reinventions Do Not Silently Discard Capabilities

**Question:** Do downstream consumers preserve all capabilities of the canonical producer, or do they silently discard some?

**Evidence:**
- `emotional_engine.py`: uses H=0 (from scale mismatch), but does not discard other fields
- `build_full_shotgun_jsonl.py`: blocked (cannot run), but intended to serialize full output
- `generate_sovereign_world.py`: uses JKD scalar (different formula) — semantic collision, not capability loss
- `update_3d_kits`: bypasses M3 H entirely — does not use H, but does not discard other fields
- `shotgun_rollout_runtime.py`: inherits H=0 — propagates zero
- `rl_shotgun_measurables.py`: h_signal=0.0 — propagates zero
- `generate_avatar_meshes.py`: inherits H=0 — propagates zero

**Finding:** ⚠️ PARTIAL. No consumer silently discards capabilities EXCEPT:
1. `resolved[]` does not carry `ternary_slots`, `personality_subsets`, `schauberger_parsing`, `projections` (design choice, not regression)
2. H=0 propagates through all consumers that read it (scale mismatch, not capability loss)
3. `build_full_shotgun_jsonl.py` cannot run (import blocked) — the intended serializer is non-functional

---

## Summary of Audit Findings

### Verified (No Regression)
- ✅ Archetype identity: 64 hexagrams, all present, no single-value collapse
- ✅ Persona agency: per-hexagram variables retained
- ✅ Pooling: consensus alongside expansion, not instead of
- ✅ Positional identity: line_states, line_balance, phase_bits preserved
- ✅ Cross-examination: 50-line and 30MB outputs serve different purposes
- ✅ Domain locking: domain_vector and domain_routing_palette per hexagram
- ✅ 3D provenance: 512 PLY meshes with wavefunction amplitudes

### Partial (Gap, Not Regression)
- ⚠️ Ternary decoding: 9-bit exists but not integrated into shotgun_expand() output (lives in ternary_full_expansion.json separately)
- ⚠️ Consumer integrity: resolved[] loses ternary_slots/personality_subsets/projections/schauberger_parsing
- ⚠️ Consumer integrity: build_full_shotgun_jsonl.py cannot run (import blocked)
- ⚠️ H=0 propagates through all consumers (scale mismatch, not capability loss)

### Not Verified (Requires Deeper Investigation)
- ❓ Whether `generate_full_shotgun_30gb.py`'s `_calculate_permutation_emotional_vector()` produces the same values as `shotgun_expand()`'s `expanded_vector`
- ❓ Whether `generate_729_resolved_full.py`'s `compute_ternary_emotional_vector()` produces the same values as the ternary layer
- ❓ Whether the 5 Godot generators produce equivalent worlds or different ones
- ❓ Whether `recover_training_data.py`'s Gate A/B/C verification catches real quality issues
- ❓ Whether `kingwen_quantum_expand.py`'s PQC v2.0 produces different results than the canonical ternary expansion

---

## Research Constraints Honored

- ✅ No source modifications
- ✅ No formula changes
- ✅ No Gate 2 closure
- ✅ No consolidation authorized
- ✅ All findings recorded as supplementary evidence
- ✅ Observed behavior distinguished from proposed corrections
- ✅ Independent representations preserved, not flagged as defects
- ✅ 9-bit ternary decoding identified as critical capability requiring integration verification
- ✅ Distinction between pooling and collapse maintained throughout
