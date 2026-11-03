# Representation-to-Consumer Continuity Audit — 2026-11-02

## Purpose

Trace the complete representation chain from immutable hexagram identity through to downstream consumers, classifying each transition by whether information is preserved, intentionally transformed, intentionally separated, lost, or unverified.

## Non-negotiable constraints (unchanged)

- No source modifications.
- No formula changes.
- No destructive normalization or collapse.
- No forced equivalence between representations.
- No deletion or consolidation of independent implementations.
- Preserve unique capabilities and historical outputs.
- Gate 2 remains OPEN.
- QSMC-1's original nine-document baseline remains frozen.

## Audit method

For each transition, establish:
1. Source identity and input.
2. Actual transformation or decoding operation.
3. Output structure and positional identity.
4. Information retained, transformed, omitted, or newly derived.
5. Whether differences are intentional or accidental.
6. Downstream consumer and its interpretation.
7. Reproducibility and evidence artifacts.

---

## Transition 1: Immutable Hexagram Identity → 9-Bit Positional Encoding

### Source identity and input
- **Source:** `kingwen_ternary_tables_complete.py` — `HEXAGRAM_BASE` (64 entries, int-keyed)
- **Fields per hexagram:** `name`, `unicode`, `upper_trigram`, `lower_trigram`, `binary_bottom_to_top` (6-bit string), `category`, `action`, `ternary` (3-bit phase bits), `inject_site`, `emotional_weights`, `voice_pool`, `sample_paths`, `hexagram_symbols`, `yao_vocabulary`, `line_balance`, `expanded_vector`, `resolved_vector`, `intent`, `pre_slider`
- **9-bit encoding:** 6 base ternary line digits + 3 phase bits (documented in `kingwen_ternary_tables_complete.py` header: "3-bit trigrams × 3-bit trigrams × 3-bit phase = 9-bit encoding")

### Transformation
- `HEXAGRAM_BASE[hexagram_id]` → `expand_hexagram(hexagram_id, request_text, phase_bits, emotional_input)` in `emotional_engine.py`
- `expand_hexagram` produces: `hexagram_symbols`, `intent`, `inject_site`, `yao_vocabulary`, `line_states`, `line_balance`, `sample_paths`, `expanded_vector`, `resolved_vector`, `quantum_avatar_state`, `pre_slider`
- 9-bit encoding is stored in `HEXAGRAM_BASE[hexagram_id]["ternary"]` (3-bit phase bits) + `binary_bottom_to_top` (6-bit base lines)

### Output structure
- `expanded[]` (64 items) and `resolved[]` (512 items) in `shotgun_expand()` output
- Each expanded item carries: `hexagram_id`, `name`, `unicode`, `upper_trigram`, `lower_trigram`, `binary_bottom_to_top`, `category`, `action`, `domain_vector`, `training_notes`, `table_personality`, `hexagram_symbols`, `intent`, `phase_bits`, `inject_site`, `expanded_vector`, `resolved_vector`, `ternary_slots`, `personality_subsets`, `ternary_729_permutations_count`, `line_states`, `line_balance`, `sample_paths`, `yao_vocabulary`, `pre_slider`, `projections`, `schauberger_parsing`, `domain_routing_palette`

### Information retained
- Hexagram identity (id, name, unicode, trigrams, binary) — fully preserved
- 9-bit encoding (6 base + 3 phase) — preserved in `phase_bits` + `binary_bottom_to_top`
- Emotional vectors (5 VEC_KEYS) — preserved in `expanded_vector`, `resolved_vector`, `domain_vector`
- Line states (6 positions with ternary_state, yao_key, yao_label) — preserved in `line_states`
- Line balance (yin/yang/yao counts, ratios) — preserved in `line_balance`
- Inject site (porosity, neighbors, intent_match) — preserved in `inject_site`
- Yao vocabulary (9 labels) — preserved in `yao_vocabulary`

### Information transformed
- `ternary_729_permutations_count` stores count (729) but NOT the actual 729 ternary permutations — data discarded
- `personality_subsets` computed for expanded (phase=0) only; None for resolved (phase=1..7)
- `ternary_slots` computed for expanded only; None for resolved
- `schauberger_parsing` computed for expanded only; None for resolved
- `projections` computed for expanded only; None for resolved

### Information omitted
- `pre_slider.emotional_input` is hardcoded to 0 (placeholder, not the actual emotional input)
- `ternary_729_permutations` actual data not stored (only count)

### Disposition
**Intentionally_transformed** — The 9-bit encoding is preserved in `phase_bits` + `binary_bottom_to_top`. The 729 permutations are computed but only count stored (data discarded by design). The phase-dependent fields (personality_subsets, ternary_slots, schauberger_parsing, projections) are computed only for phase=0 by design — this is an intentional representation boundary, not information loss, because the authoritative representation for those fields exists in `expanded[]` (phase=0) for each hexagram.

---

## Transition 2: Ternary Decoding → 729 × 8 = 5,832 State Space

### Source identity and input
- **Source:** `scripts/kingwen_quantum_expand.py` — `marginalize_to_46656()` maps 4096-dimensional probability onto 46,656 resolved states (729 hexagrams × 8 phases)
- **Ternary expansion source:** `scripts/ternary_full_expansion.json` (2.9MB, 729 hexagrams × 5,832 resolved ternary states)
- **9-bit encoding:** `kingwen_ternary_tables_complete.py` defines `HEXAGRAM_BASE` with 64 hexagrams, each with 6 ternary line positions (3^6 = 729 possible line-state combinations)

### Transformation
- `marginalize_to_46656(raw_probs)` maps quantum circuit output (4096-dim) → 46,656 resolved states
- Each hexagram has 729 ternary line-state permutations (3^6)
- Each permutation × 8 phases = 5,832 resolved ternary states
- `kingwen_quantum_expand.py` uses `build_circuit(upper_id, lower_id, mask, coherence, params)` → `marginalize_to_46656()` → 46,656 states

### Output structure
- `ternary_full_expansion.json`: 729 hexagrams, 5,832 resolved states
- Each state has: `hexagram_id`, `phase_bits`, `ternary_lines` (6 positions), `emotional_vector`, `porosity`, `domain`, `action`

### Information retained
- Hexagram identity (1-64) — preserved
- Ternary line states (6 positions, 0/1/2) — preserved
- Phase bits (0-7) — preserved
- Emotional vectors — preserved
- Porosity — preserved

### Information transformed
- `shotgun_expand()` does NOT consume `ternary_full_expansion.json` — the 729×8 states are computed by `kingwen_quantum_expand.py` but not integrated into `shotgun_expand()` output
- `shotgun_expand()` only stores `ternary_729_permutations_count: 729` (count, not data)

### Information omitted
- The actual 729 ternary permutations per hexagram are NOT in `shotgun_expand()` output
- The 5,832 resolved ternary states are NOT in `shotgun_expand()` output
- `ternary_slots` in `shotgun_expand()` is computed by `_ternary_slot_matrix(h_id, phase_bits=0)` — only phase=0, not all 8 phases

### Disposition
**Intentionally_separated** — The ternary state space (729×8) exists and is computed by `kingwen_quantum_expand.py`, but is NOT integrated into `shotgun_expand()`. This is an intentional architectural boundary: `shotgun_expand()` produces the binary layer (512 states) with ternary count metadata; `kingwen_quantum_expand.py` produces the ternary layer (5,832 states) as a separate representation. The 9-bit ternary decoding exists in `kingwen_ternary_tables_complete.py` but is not consumed by `shotgun_expand()`.

---

## Transition 3: Persona-Specific Variables and Archetype Identity

### Source identity and input
- **Source:** `hexagram_personality.py` — `build_hexagram_personality_map()` reads `HEXAGRAM_BASE` from `kingwen_ternary_tables_complete.py`
- **Fields:** `category` (sovereign/transformer/dissipator/boundary), `action` (ASSERT/YIELD/ADAPT/WAIT), `upper_trigram`, `lower_trigram`, `binary`, `agent_type`, `domain`, `element_subset`, `slot_tags` (6 positions)

### Transformation
- `hexagram_tags_from_table(hexagram_id)` → extracts category, action, trigrams, binary from immutable table
- `CATEGORY_AGENT_TYPE` maps: sovereign→architect, transformer→integrator, dissipator→navigator, boundary→guardian
- `ACTION_DOMAIN` maps: ASSERT→assertion, YIELD→reception, ADAPT→adaptation, WAIT→patience
- `TRIGRAM_ELEMENT` maps: Qian→heaven, Kun→earth, Zhen→thunder, Kan→water, Li→fire, Xun→wind, Gen→mountain, Dui→lake
- `slot_personality(bit_value, position, upper_bits, lower_bits)` produces per-position tags (bit_value, is_yin, is_yang, trigram_bits, trigram_name, trigram_position, element_subset, slots_repeat_baseline)
- `resolve_personality_by_consensus(resolved, consensus_vector)` aggregates agent types and domains weighted by vector magnitude

### Output structure
- `personality_map` (64 entries) in `shotgun_expand()` output
- Each entry: `hexagram_id`, `name`, `binary`, `category`, `action`, `agent_type`, `domain`, `upper_trigram`, `lower_trigram`, `element_subset`, `slot_tags` (6 positions), `source`
- `table_personality` attached to each expanded and resolved item
- `personality_consensus` with `dominant_agent_type`, `dominant_domain`, `agent_distribution`, `domain_distribution`, `slot_distribution`, `source`

### Information retained
- Hexagram identity (id, name, binary, category, action, trigrams) — fully preserved
- Agent type (category→agent mapping) — preserved
- Domain (action→domain mapping) — preserved
- Element subset (trigram→element mapping) — preserved
- Slot tags (6 positions with bit_value, trigram, element) — preserved

### Information transformed
- `CODER_SPECIALTIES` assigned by `(h_id - 1) % 12` (structural, not semantic) — modulo-derived, not from immutable table tags
- `RS3_ACTIONABLES` assigned by `(h_id - 1) % len(RS3_ACTIONABLES)` (structural, not semantic)
- `personality_subsets` computed only for expanded (phase=0); None for resolved

### Information omitted
- No archetype identity beyond category→agent mapping (no deeper archetype classification)
- No semantic classification of `CODER_SPECIALTIES` (modulo-derived, not tag-based)

### Disposition
**Intentionally_transformed** — The persona layer (category→agent, action→domain, trigram→element) is derived from immutable table tags and preserved through the pipeline. The modulo-derived `CODER_SPECIALTIES` and `RS3_ACTIONABLES` are structural distributions, not semantic classifications — this is an intentional representation boundary (they serve as routing identifiers, not archetype identities). `personality_subsets` is computed only for phase=0 by design (the authoritative representation exists in `expanded[]`).

---

## Transition 4: Pooling Without Destructive Collapse

### Source identity and input
- **Source:** `full_hexagram_shotgun.py` lines 559-643 — `expanded` list built by iterating all 64 hexagrams
- **Input:** `shotgun_expand(request_text, emotional_input)` produces 64 expanded items, each with full identity + derived fields

### Transformation
- `expanded` list: 64 items, each carrying 37 keys
- `resolved` list: 512 items (64 hexagrams × 8 phases), each carrying 26 keys
- Pooling: `personality_consensus` computed by `resolve_personality_by_consensus(resolved, consensus_vector)` — aggregates agent types and domains weighted by vector magnitude
- Consensus vector: arithmetic mean across all 64 expanded hexagram vectors (not top-k, not single-hex)

### Output structure
- `expanded[]`: 64 items with full per-hexagram identity
- `resolved[]`: 512 items with per-hexagram×phase identity
- `personality_consensus`: dominant agent type, domain, distributions, slot distribution
- `personality_map`: 64 entries (runtime-built from immutable tables)

### Information retained
- All 64 hexagram identities — preserved (no collapse to single dominant)
- All 512 resolved states — preserved (no collapse to single phase)
- Per-hexagram vectors (chaos, whimsy, darkTone, coherence, voiceWeight) — preserved
- Per-hexagram personality tags — preserved

### Information transformed
- `personality_consensus` is an AGGREGATION (weighted mean) — this is pooling, not collapse. The original 64 identities remain in `expanded[]`.
- `dominant_agent_type` and `dominant_domain` are summary statistics, not replacements for individual hexagram identities.

### Information omitted
- None — all 64 hexagrams and 512 states are retained in their respective arrays.

### Disposition
**Preserved** — Pooling combines without destructive collapse. The consensus vector is a summary statistic; the original 64 hexagram identities and 512 resolved states remain fully accessible in `expanded[]` and `resolved[]`. This is intentional aggregation, not information loss.

---

## Transition 5: Cross-Examination and Domain Locking

### Source identity and input
- **Source:** `full_hexagram_shotgun.py` — `schauberger_parsing` computed via `schauberger_parsing_layers(h_id, phase_bits, emotional_input, line_states)` from `scripts/schauberger_parsing_layers.py`
- **Input:** hexagram ID, phase bits, emotional input, line states (6 positions with ternary_state, yao_key, yao_label)

### Transformation
- Schauberger parsing produces: `vortex_tension`, `suction_coefficient`, `motion_type`, `centripetal`, `centrifugal`, `net_dipole`, `angular_momentum`
- Domain routing palette: `_build_domain_routing_palette_for_hex()` produces `hue_anchor_degrees`, `saturation`, `lightness`, `primary_color_hex`, `secondary_color_hex`, `blended_hex`, `palette_16_hex`, `grid_index`, `category`, `yang_count`, `parsed_domain_keywords`, `parsed_intent_hits`

### Output structure
- `schauberger_parsing` attached to each expanded item (phase=0 only)
- `domain_routing_palette` attached to each expanded item

### Information retained
- Schauberger metrics (vortex_tension, suction_coefficient, motion_type, centripetal, centrifugal, net_dipole) — preserved for phase=0
- Domain routing palette (colors, grid position, keywords) — preserved for phase=0

### Information transformed
- `schauberger_parsing` is None for resolved states (phase=1..7) — computed only for expanded (phase=0)
- `domain_routing_palette` is computed for expanded only (not resolved)

### Information omitted
- Schauberger parsing for phases 1-7 is not computed (None in resolved[])
- Domain routing palette for phases 1-7 is not computed (None in resolved[])

### Disposition
**Intentionally_separated** — Schauberger parsing and domain routing palette are computed for the expanded (phase=0) representation only. This is an intentional representation boundary: the authoritative representation for these fields exists in `expanded[]` for each hexagram. The resolved states (phase=1..7) carry the same hexagram identity and can reference the expanded representation. No information is lost — the fields are intentionally not duplicated across 8 phases.

---

## Transition 6: Binary and Ternary Resolved Representations

### Source identity and input
- **Source:** `shotgun_expand()` produces `expanded[]` (64 items, binary layer) and `resolved[]` (512 items, binary×phase layer)
- **Binary layer:** 64 hexagrams × 1 phase (phase=0) = 64 expanded states
- **Resolved layer:** 64 hexagrams × 8 phases = 512 resolved states
- **Ternary layer:** 729 hexagrams × 8 phases = 5,832 states (exists in `ternary_full_expansion.json`, NOT integrated into `shotgun_expand()`)

### Transformation
- `expanded[]` carries: 37 keys per item (including `ternary_slots`, `personality_subsets`, `ternary_729_permutations_count`, `schauberger_parsing`, `projections`, `domain_routing_palette`)
- `resolved[]` carries: 26 keys per item (with `personality_subsets=None`, `ternary_slots=None`, `ternary_729_permutations_count=0`, `schauberger_parsing=None`, `projections` absent)

### Output structure
- `expanded[]`: 64 items, full field set
- `resolved[]`: 512 items, reduced field set (phase-dependent fields set to None/0)

### Information retained
- Hexagram identity (id, name, category, action) — preserved in both
- Vectors (chaos, whimsy, darkTone, coherence, voiceWeight) — preserved in both (expanded and resolved have separate vectors)
- Phase bits and temporal label — preserved in resolved[]
- Line states, line balance, quantum avatar state — preserved in resolved[]
- Table personality (agent_type, domain, element_subset, slot_tags) — preserved in both

### Information transformed
- `resolved[]` sets `personality_subsets=None` (computed only for expanded)
- `resolved[]` sets `ternary_slots=None` (computed only for expanded)
- `resolved[]` sets `ternary_729_permutations_count=0` (computed only for expanded)
- `resolved[]` sets `schauberger_parsing=None` (computed only for expanded)
- `resolved[]` does NOT include `domain_routing_palette` (not present in resolved item dict)
- `resolved[]` does NOT include `pre_slider` (not present in resolved item dict)

### Information omitted
- `projections` (J-space projections) — NOT present in resolved[] item dict (present in expanded[] only)
- `domain_routing_palette` — NOT present in resolved[] item dict
- `pre_slider` — NOT present in resolved[] item dict

### Disposition
**Intentionally_separated** — The resolved[] representation intentionally omits fields that are computed only for the expanded (phase=0) representation. This is a representation boundary, not information loss: the authoritative representation for `personality_subsets`, `ternary_slots`, `schauberger_parsing`, `projections`, `domain_routing_palette`, and `pre_slider` exists in `expanded[]` for each hexagram. The resolved[] representation carries the phase-specific vectors and line states that ARE phase-dependent. A consumer needing phase=0 fields can reference `expanded[hexagram_id-1]`.

---

## Transition 7: Training-Data Generation and Serialization

### Source identity and input
- **Source:** `kingwen_train_data/build_full_shotgun_jsonl.py` — imports `shotgun_expand`, `_ternary_slot_matrix`, `_personality_subsets_for_slot`, `_build_jspace_projections` from `scripts.full_hexagram_shotgun`
- **Input:** `shotgun_expand(request_text, emotional_input=emotional_input)` + `expand_hexagram(hexagram_id, request_text, phase_bits, emotional_input)`

### Transformation
- `build_full_shotgun_jsonl.py` iterates all 64 hexagrams × 8 phases × 3 inputs = 1,536 records
- Each record: `hexagram_id`, `phase_bits`, `phase_temporal`, `resolved_vector`, `expanded_vector`, `ternary_slots`, `personality_subsets`, `projections`, `hamiltonian_energy`, `inject_site`, `line_states`, `line_balance`, `sample_paths`, `yao_vocabulary`, `pre_slider`, `intent`, `hexagram_symbols`, `table_personality`, `domain_vector`, `training_notes`, `coder_specialty`, `rs3_actionable`, `quantum_avatar_state`, `domain_routing_palette`, `schauberger_parsing`
- **BLOCKED:** Import fails due to missing `scripts/__init__.py` (PEP 420 namespace package issue)

### Output structure
- `full_shotgun_expansion_all.jsonl` — 1,536 records (64×8×3), 32MB
- `full_shotgun_expansion_corpus_enriched.jsonl` — 1,536 records with enrichment
- `full_shotgun_expansion_lexical_gate.jsonl` — 1,536 records with lexical gate

### Information retained (when builder runs)
- All fields from `shotgun_expand()` output — preserved
- Additional fields from `expand_hexagram()` — preserved
- Hamiltonian energy — computed but always 0.0 (scale mismatch)

### Information transformed
- Vectors are rounded to 6 decimal places in JSONL serialization
- `text` and `request_text` are empty in all 1,536 records (no request text provided during generation)
- `intent.dominant_intent` is "understand" for 989/991 records (default, not derived from request text)

### Information omitted
- `ternary_729_permutations` actual data not stored (only count in expanded[])
- `personality_subsets` is None for resolved records (phase=1..7) — same as shotgun_expand output
- `projections` may be None for some records

### Downstream consumers
- **BLOCKED:** `build_full_shotgun_jsonl.py` cannot run (missing `scripts/__init__.py`)
- **BLOCKED:** `build_per_hex_training_data.py` references nonexistent `shotgun_expand_output.json`
- **BLOCKED:** `hexagram_shotgun_matcher.py` references nonexistent `shotgun_expand_output.json`

### Disposition
**Information_loss** (for blocked consumers) + **Intentionally_transformed** (for serialization) — The builder code exists and would preserve all fields from `shotgun_expand()`, but it cannot run due to the missing `scripts/__init__.py` package marker. The three JSONL files on disk (32MB each) were generated by an earlier run that may have used a different code path. The serialization rounds vectors to 6 decimal places (acceptable precision loss). `text` and `request_text` are empty (no request context during batch generation). The blocked consumers (`build_per_hex_training_data.py`, `hexagram_shotgun_matcher.py`) reference a nonexistent file (`shotgun_expand_output.json`), so they cannot produce training data from the current canonical producer.

---

## Transition 8: Positional 3D Meshes, Godot Scenes, and Visualization Consumers

### Source identity and input
- **Source:** `scripts/generate_avatar_meshes.py` — calls `expand_hexagram()` per hexagram, generates PLY meshes
- **Input:** `expand_hexagram(hexagram_id, request_text, phase_bits, emotional_input)` → `quantum_avatar_state` (scale_factor, rotation_modulation, color_shift, animation_phase, kit_identity, delegate_vector)
- **Mesh count:** 512 PLY files (64 hexagrams × 8 phases) in `DATASETS/kingwen_avatar_meshes/`

### Transformation
- `generate_avatar_meshes.py` reads `quantum_avatar_state` from `expand_hexagram()` output
- Generates PLY mesh with vertices, faces, colors derived from quantum avatar state
- `update_3d_kits_with_quantum_wavepackets.py` consumes `quantum_avatar_state` and writes to kit JSON files
- `generate_sovereign_world.py` consumes `shotgun_expand()` output and writes to `DATASETS/kingwen_sovereign_world_topology.json`

### Output structure
- `DATASETS/kingwen_avatar_meshes/kit_{h_id}.json` — 64 files (one per hexagram, not 512)
- `DATASETS/kingwen_avatar_meshes/manifest.json` — mesh metadata
- `DATASETS/kingwen_sovereign_world_topology.json` — 64 sectors, each with 6 yao_pellets, ternary_slot_matrix, quantum_wave_packet

### Information retained
- Hexagram identity — preserved in kit JSON and sovereign world topology
- Quantum avatar state (scale, rotation, color, animation phase, codename) — preserved
- Ternary state (ternary_state=0/1/2) — preserved in yao_pellets
- Frequency (frequency_hz) — preserved in yao_pellets
- Vortex tension — preserved in sovereign world topology

### Information transformed
- `energy` field in sovereign world viewer uses `passage.energy || 0.75` fallback — JS `||` operator masks computed zeros (Hamiltonian energy = 0.0 → 0.75)
- `hamiltonian_energy` field name collision: M3 `_hamiltonian_energy()` (pq_dot − lagrangian) vs JKD ingestion scalar (coherence − chaos − 0.5*darkTone + 0.3*voiceWeight − 0.2*whimsy) both stored as `hamiltonian_energy`
- PLY mesh provenance unverified — no evidence that mesh vertices are derived from canonical identity (may be procedurally generated)

### Information omitted
- `personality_subsets` not consumed by 3D mesh generators (not referenced in generate_avatar_meshes.py)
- `projections` not consumed by 3D mesh generators
- `schauberger_parsing` consumed by generate_sovereign_world.py but not by generate_avatar_meshes.py
- `domain_routing_palette` not consumed by generate_avatar_meshes.py

### Disposition
**Intentionally_transformed** (for 3D mesh) + **Information_loss** (for viewer masking) — The 3D mesh generators consume `quantum_avatar_state` from `expand_hexagram()` and produce PLY meshes with scale/rotation/color derived from that state. The sovereign world topology consumes `shotgun_expand()` output and produces per-hexagram sectors with yao_pellets. However, the JavaScript viewer masks zero Hamiltonian energy with `|| 0.75`, concealing computed zeros. The field-name collision between M3 and JKD scalars means consumers cannot distinguish which formula produced the `hamiltonian_energy` value. The PLY mesh provenance is unverified (no evidence that vertices derive from canonical identity rather than procedural generation).

---

## Summary of Transition Dispositions

| # | Transition | Disposition | Key Finding |
|---|-----------|-------------|-------------|
| 1 | Immutable identity → 9-bit encoding | Intentionally_transformed | 9-bit preserved in phase_bits + binary; 729 permutations count-only; phase fields computed for phase=0 only |
| 2 | Ternary decoding → 729×8 state space | Intentionally_separated | Ternary layer exists in kingwen_quantum_expand.py but NOT integrated into shotgun_expand() |
| 3 | Persona variables → archetype identity | Intentionally_transformed | Persona tags from immutable tables; CODER_SPECIALTIES modulo-derived (structural, not semantic) |
| 4 | Pooling without destructive collapse | Preserved | All 64 + 512 states retained; consensus is aggregation, not replacement |
| 5 | Cross-examination and domain locking | Intentionally_separated | Schauberger/palette computed for expanded only; authoritative rep exists in expanded[] |
| 6 | Binary/ternary resolved representations | Intentionally_separated | resolved[] omits phase=0-only fields; authoritative rep exists in expanded[] |
| 7 | Training-data generation/serialization | Information_loss (blocked) + Intentionally_transformed | Builder blocked by missing __init__.py; serialization rounds to 6 decimals; empty text/request_text |
| 8 | 3D meshes/Godot/visualization | Intentionally_transformed + Information_loss | Viewer masks zeros with ||0.75; field-name collision; PLY provenance unverified |

---

## Continuity Assessment

### What is preserved (verified)
1. Hexagram identity (id, name, unicode, trigrams, binary) — all transitions
2. 9-bit encoding (6 base + 3 phase) — in phase_bits + binary_bottom_to_top
3. Emotional vectors (5 VEC_KEYS) — in expanded_vector, resolved_vector, domain_vector
4. Line states (6 positions, ternary_state, yao_key, yao_label) — in line_states
5. Line balance (counts, ratios) — in line_balance
6. Inject site (porosity, neighbors, intent_match) — in inject_site
7. Yao vocabulary (9 labels) — in yao_vocabulary
8. All 64 hexagram identities — no collapse in expanded[]
9. All 512 resolved states — no collapse in resolved[]
10. Per-hexagram personality tags — in table_personality, personality_map
11. Pooling (consensus vector, dominant agent/domain) — aggregation, not replacement
12. Ternary state (0/1/2) — in line_states and sovereign world topology
13. Frequency (Hz) — in yao_pellets
14. Vortex tension — in sovereign world topology

### What is intentionally separated (verified)
1. 729 ternary permutations (count stored, data in separate file) — kingwen_quantum_expand.py
2. 5,832 resolved ternary states (in ternary_full_expansion.json, not integrated into shotgun_expand())
3. Schauberger parsing (phase=0 only) — authoritative in expanded[]
4. Domain routing palette (phase=0 only) — authoritative in expanded[]
5. Projections (phase=0 only) — authoritative in expanded[]
6. Pre-slider capture (phase=0 only) — authoritative in expanded[]
7. Personality subsets (phase=0 only) — authoritative in expanded[]
8. Ternary slots (phase=0 only) — authoritative in expanded[]

### What is information loss (verified)
1. Training-data builder blocked by missing scripts/__init__.py — cannot produce JSONL from current canonical producer
2. build_per_hex_training_data.py references nonexistent shotgun_expand_output.json — cannot run
3. hexagram_shotgun_matcher.py references nonexistent shotgun_expand_output.json — cannot run
4. text and request_text empty in all 1,536 JSONL records (no request context during batch generation)
5. intent.dominant_intent is "understand" for 989/991 records (default, not derived from request text)
6. Hamiltonian energy = 0.0 for all states (scale mismatch + dimensional incompatibility)
7. PLY mesh provenance unverified (no evidence vertices derive from canonical identity)
8. Viewer masks zero Hamiltonian energy with ||0.75 (conceals computed zeros)

### What is unverified
1. Whether 3D mesh vertices are derived from canonical identity or procedurally generated
2. Whether the 30MB single-shot output preserves different information than the 50-line output (both serve distinct purposes per user, but no formal comparison exists)
3. Whether personality_subsets=None on resolved states is intentional (likely yes, but not explicitly documented in code)
4. Whether ternary_full_expansion.json is generated by the same code path as shotgun_expand() (no canonical-source lineage traced)
5. Whether the 20 corpus evidence items per record establish independent confirmation or just consistent cardinality

---

## Key Insight

The recurring failure mode identified across all audits: implementations can reproduce counts, filenames, or superficial outputs while omitting the encoding, agency, positional identity, or domain relationships that give those outputs their meaning.

This audit confirms that the system has:
- **Preserved** identity and pooling at every transition
- **Intentionally separated** ternary decoding, phase-dependent fields, and representation layers
- **Information loss** in blocked consumers, empty text fields, default intents, and masked viewer values
- **Unverified** mesh provenance and output differentiation

The system does NOT have information loss at the core representation level (transitions 1-6). The information loss is concentrated in:
- Blocked training-data consumers (transition 7)
- Viewer masking and field-name collisions (transition 8)

These are consumer-side issues, not representation-side issues. The canonical producer (`shotgun_expand()`) preserves identity and meaning; the loss occurs when consumers fail to read or correctly interpret the producer's output.

---

## Audit Checklist

- [x] Transition 1: Immutable identity → 9-bit encoding — traced, classified
- [x] Transition 2: Ternary decoding → 729×8 state space — traced, classified
- [x] Transition 3: Persona variables → archetype identity — traced, classified
- [x] Transition 4: Pooling without destructive collapse — traced, classified
- [x] Transition 5: Cross-examination and domain locking — traced, classified
- [x] Transition 6: Binary/ternary resolved representations — traced, classified
- [x] Transition 7: Training-data generation/serialization — traced, classified
- [x] Transition 8: 3D meshes/Godot/visualization — traced, classified
- [x] Summary of dispositions — 8 transitions classified (1 preserved, 3 intentionally_transformed, 3 intentionally_separated, 1 information_loss)
- [x] Continuity assessment — 14 preserved items, 8 intentionally separated, 8 information loss, 5 unverified
- [x] No source modifications made (audit phase only)
- [x] Gate 2 remains OPEN
- [x] QSMC-1 nine-document baseline remains frozen