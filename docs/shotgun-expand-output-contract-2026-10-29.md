# shotgun_expand Output Contract

## Status

Phase 1 contract-test preparation. No implementation authorized.
This document defines the intended output contract for `shotgun_expand()` as the canonical
producer of King Wen expansion data. It is the reference against which the OpenJarvis
adapter must be tested before any adapter repair is attempted.

## Canonical Producer

- **Function:** `shotgun_expand(request_text, emotional_input)` in `scripts/full_hexagram_shotgun.py`
- **Source-of-truth:** `KING-WEN-I-CHING-IMMUTABLE-TABLES` (read-only canonical tables)
- **Revision under test:** `71fbf28f8e92c6a7de74c50a304906ef81963a7d`

## Top-Level Output Fields

| Field | Type | Cardinality | Notes |
|-------|------|-------------|-------|
| `source` | str | 1 | Always `"kingwen-shotgun-expand"` |
| `request_text` | str | 1 | Input text passed through |
| `emotional_input` | int | 1 | Input emotional_input (0-100) |
| `total_expanded` | int | 1 | Always 64 |
| `total_resolved` | int | 1 | Always 512 |
| `total_encodings` | int | 1 | Always 512 |
| `total_ternary_line_permutations` | int | 1 | Always 46656 (64 × 729) |
| `ternary_line_permutations_per_hex` | int | 1 | Always 729 (3⁶) |
| `total_domained_routes` | int | 1 | Always 35000 |
| `personality_subsets_total` | int | 1 | Always 1152 |
| `capture_point` | str | 1 | Always `"first-parse"` |
| `expanded` | list[dict] | 64 | One per hexagram (1-64) |
| `resolved` | list[dict] | 512 | One per (hexagram, phase) pair (64 × 8) |
| `personality_consensus` | dict | 1 | Full 512-state wave consensus (NOT single-hex) |
| `personality_map` | dict | 64 | Hexagram ID → personality metadata |
| `avg_hamiltonian_energy` | float | 1 | Average Hamiltonian energy (currently 0.0 by construction) |
| `min_hamiltonian_energy` | float | 1 | Minimum Hamiltonian energy (currently 0.0) |
| `max_hamiltonian_energy` | float | 1 | Maximum Hamiltonian energy (currently 0.0) |
| `table_sources` | dict | 7 | Source table provenance |

## personality_consensus Sub-Fields

| Field | Type | Semantics |
|-------|------|-----------|
| `dominant_agent_type` | str | Agent type with highest weighted count across all 512 resolved states (e.g., "integrator", "navigator", "guardian", "architect") |
| `agent_distribution` | dict[str, float] | Weighted counts per agent type (sum ≈ 512) |
| `dominant_domain` | str | Domain with highest weighted count (e.g., "reception", "adaptation") |
| `domain_distribution` | dict[str, float] | Weighted counts per domain |
| `slot_distribution` | dict[str, dict] | Per-slot (1-6) bit distribution and trigram distribution |
| `consensus_vector` | dict[str, float] | 5-axis mean vector: chaos, whimsy, darkTone, coherence, voiceWeight |
| `dominant_intent` | str | Default `"understand"` for 989/991 equations; only 2/991 explicitly classified |
| `source` | str | Always `"immutable_table_tags"` |

## Expanded Record Fields (64 entries)

Each expanded record contains:
- `hexagram_id`: int (1-64)
- `name`: str (hexagram name)
- `unicode`: str (hexagram symbol)
- `upper_trigram`, `lower_trigram`: str (trigram names)
- `binary_bottom_to_top`: str (6-bit binary)
- `coder_specialty`: str
- `rs3_actionable`: bool
- `category`: str
- `action`: str
- `domain_vector`: dict
- `training_notes`: str
- `table_personality`: dict
- `hexagram_symbols`: dict (name, unicode, category, action, chinese, pinyin)
- `intent`: dict (tokenized intent with dominant_intent, query_tokens, etc.)
- `phase_bits`: int (0-7)
- `request_text`: str
- `avalokiteshvara_arm`: str
- `jkd_pedagogy_anchor`: str
- `quantum_superposition`: dict
- `hermes_layer`: dict
- `schauberger_metrics`: dict (vortex, temperature_gradient, etc.)
- `phase_temporal`: str (past/present/future/etc.)
- `inject_site`: dict (porosity is nested here as int 0-4)
- `expanded_vector`: dict (5 axes: chaos, whimsy, darkTone, coherence, voiceWeight)
- `resolved_vector`: dict (5 axes, same keys)
- `ternary_slots`: list or None (only populated for phase 0 in current output)
- `personality_subsets`: list or None (only populated for phase 0 in current output)
- `ternary_729_permutations_count`: int (729)
- `line_states`: list[dict] (6 lines, each with yao vocabulary)
- `line_balance`: dict (yin_ratio, yang_ratio, yao_ratio, changing_ratio)
- `sample_paths`: list[dict] (pool references)
- `yao_vocabulary`: dict (9-term yao vocabulary)
- `pre_slider`: dict
- `projections`: dict or None
- `schauberger_parsing`: dict or None
- `domain_routing_palette`: dict or None

## Resolved Record Fields (512 entries)

Each resolved record contains:
- All expanded fields except `quantum_superposition`, `hermes_layer`, `schauberger_metrics`, `phase_temporal`, `domain_routing_palette`
- `phase_temporal`: str (8 phase temporals: past, present, future, transition, resolution, dissolution, crystallization, void)
- `quantum_avatar_state`: dict
- `trainingNotes`: str (alias for training_notes)
- `ternary_slots`, `personality_subsets`, `ternary_729_permutations_count`, `schauberger_parsing` (same as expanded, may be None)

## Identity Invariant

The canonical identity of a state is `(hexagram_id, phase_bits)`, not vector uniqueness.
- 64 unique hexagram_ids in expanded (1-64)
- 512 unique (hexagram_id, phase_bits) pairs in resolved (64 × 8)
- Expanded vectors may have 29 duplicate groups within the same hexagram (phase-modulation artifacts)
- No cross-hexagram vector duplicates

## Consumer Adaptation Semantics

The old `collapse_full_128()` returned a `consensus` dict with fields that no longer
exist in the producer output. The new `personality_consensus` returns a different
set of fields. The adapter must be investigated to determine which fields it
actually needs and how it should consume the expanded output. The following
documents the old schema for reference only — it is NOT a target to reproduce.

Old `collapse_full_128()` returned a `consensus` dict with:
- `consensus_hexagram_id`: int (single hexagram ID)
- `consensus_hexagram_name`: str
- `consensus_temporal`: str
- `consensus_yao`: str
- `consensus_porosity_mean`: float
- `consensus_porosity_mode`: str or None
- `consensus_vector`: dict (5 axes)
- `consensus_intent`: str
- `consensus_explanation`: str
- `temporal_distribution`: dict
- `consensus_explanation`: str

The new `personality_consensus` returns:
- `dominant_agent_type`: str (highest-weight agent type across ALL 512 states)
- `agent_distribution`: dict (weighted counts per agent type)
- `dominant_domain`: str (highest-weight domain)
- `domain_distribution`: dict (weighted counts per domain)
- `slot_distribution`: dict (per-slot bit/trigram distributions)
- `consensus_vector`: dict (5-axis mean across all expanded states)
- `dominant_intent`: str (default "understand")
- `source`: str

**CRITICAL:** The new consensus is NOT a single-hexagram selection. It is a weighted
aggregation across all 512 resolved states. The `dominant_agent_type` is the agent type
with the highest total weight, not "the chosen hexagram."

**Note:** The adapter must consume expanded fields directly. It must not map expanded
fields to legacy collapse field names without evidence that the legacy semantics
are required. The appropriate investigation is to trace the adapter's actual needs
and determine how it should consume the expanded output.

The old `consensus_hexagram_id` was a single hexagram ID selected via hash-based
ranking. The new `dominant_agent_type` is a categorical label for the dominant
agent-type weight across the full wave.

**Semantic equivalence between old and new consensus fields is NOT established.**
Any mapping between them requires explicit evidence and is the subject of Phase 1
contract testing.

## Emotional Input Effect (Observation, Not Contract)

OBSERVATION (2026-10-29): `shotgun_expand` calls `derive_dynamic_emotional_input(request_text, emotional_input)` which:
- Returns input as-is if `emotional_input != 50` and `0 <= emotional_input <= 100`
- Derives from text sentiment if `emotional_input == 50` (flat default)
- Returns 52 if request_text is empty

The derived emotional_input affects `quantum_avatar_state` but does NOT affect:
- `expanded_vector` (identical across emotional_input values)
- `resolved_vector` (identical across emotional_input values)
- `consensus_vector` (computed from expanded, phase 0)
- `porosity` (nested in inject_site, identical)
- `phase_temporal` (identical)

This is an observation, not a permanent contract. Consumers should not assume
emotional_input modulates core vectors until a contract explicitly defines the relationship.

## Porosity Access Path

Porosity is NOT a top-level key in resolved records. It is nested:
```
record["inject_site"]["porosity"]  # int 0-4
```

Consumers must know to look there. The `primary_pool` is also nested:
```
record["inject_site"]["primary_pool"]  # str
```

## Hamiltonian Energy

- All 512 resolved states currently produce `0.0` energy (scale mismatch + empty line_balance)
- `avg_hamiltonian_energy`, `min_hamiltonian_energy`, `max_hamiltonian_energy` are all `0.0`
- This is an observed result, NOT a permanent system requirement
- Tests must verify observability of intermediate terms, not assert zero as permanent expectation

## Consumer Acceptance Criteria (beyond import success)

1. **Consumer adaptation:** adapter must consume `personality_consensus`/`dominant_agent_type` from the expanded output with documented semantics, or explicitly define how the adapter reads expanded output and update all consumers. The adapter must not map expanded fields to legacy collapse field names without evidence that the legacy semantics are required.
2. **Live producer output:** adapter must call `shotgun_expand()` not read frozen JSON
3. **Identity preservation:** (hexagram_id, phase_bits) pairs must be preserved through
   the adapter boundary
4. **Provenance preservation:** `source`, `request_text`, `emotional_input` must survive
5. **Vector fidelity:** `consensus_vector` 5 axes must be preserved

## Known Failures (to reproduce in contract tests)

### KF-1: Missing Symbol
- **Location:** `kingwen_engine_adapter.py:67` — `collapse_full_128 = _EngineModule.collapse_full_128`
- **Failure:** `AttributeError: module 'kingwen_emotional_engine' has no attribute 'collapse_full_128'`
- **Root cause:** `collapse_full_128()` was removed from `emotional_engine.py` on 2026-09-01; adapter not updated
- **Expected behavior:** Import fails with clear error; adapter cannot load
- **Fix (NOT authorized yet):** Replace with `shotgun_expand` import or add fallback

### KF-2: Schema Mismatch
- **Location:** `kingwen_engine_adapter.py:213-235` — adapter reads `consensus.get("consensus_hexagram_id")`, `consensus.get("consensus_hexagram_name")`, etc.
- **Failure:** `consensus` dict is empty (shotgun_expand returns `personality_consensus`, not `consensus`); all fields default to None/empty
- **Root cause:** Adapter expects old `collapse` output schema; producer returns new `shotgun_expand` schema
- **Expected behavior:** Fields are None/empty; no crash but no useful data
- **Fix (NOT authorized yet):** Trace adapter's actual field needs against expanded output; consume expanded fields directly or define adapter-specific consumption with documented semantics

### KF-3: Stale JSON Readers
- **Location:** 6 files in OpenJarvis read `collapse_full_128_output.json` instead of calling live producer
- **Failure:** Files read frozen snapshot with null timestamp/emotional_input
- **Root cause:** Role of frozen snapshot not classified (historical/cache/obsolete)
- **Expected behavior:** Consumers use stale data; no crash
- **Fix (NOT authorized yet):** Classify each reader's source-of-truth role

### KF-4: Cartesia Static Weights
- **Location:** `cartesia_adapter.py` reads `emotional-weights.json`
- **Failure:** Voice output does not vary with phase_bits or emotional_input
- **Root cause:** Adapter uses static weights, not dynamic expansion
- **Expected behavior:** Voice output is deterministic for same (hexagram_id, phase_bits, emotional_input)
- **Fix (NOT authorized yet):** Wire dynamic expansion into voice path

### KF-5: 3D Avatar Provenance
- **Location:** 512 PLY files in `DATASETS/kingwen_avatar_meshes/`
- **Failure:** No manifest mapping file to (hexagram_id, phase_bits)
- **Root cause:** File count (512) ≠ provenance
- **Expected behavior:** Cannot verify which PLY corresponds to which state
- **Fix (NOT authorized yet):** Create manifest with identity + phase lineage

## Explicit Failure Conditions

1. **Import failure:** `from openjarvis.emotion.kingwen_engine_adapter import collapse_full_128` raises `AttributeError`
2. **Schema mismatch:** `consult()` returns `hexagram_id=None`, `hexagram_name=""`, `emotional_deltas={}` when called with live producer
3. **Identity loss:** If adapter maps `dominant_agent_type` to `consensus_hexagram_id` without evidence, identity is corrupted
4. **Provenance loss:** If adapter drops `source`, `request_text`, or `emotional_input`, provenance is lost
5. **Vector fidelity loss:** If `consensus_vector` axes are renamed or dropped, downstream voice/3D consumers break
6. **Hamiltonian false expectation:** If tests assert `energy == 0.0` as permanent contract, future formula fixes will fail tests
7. **Frozen snapshot staleness:** If consumers read `collapse_full_128_output.json` without checking timestamp, they use stale data

## Test Design Principles

1. **Observation vs. permanent expectation:** Tests must distinguish "current behavior is X" from "system must always produce X"
2. **Identity vs. vector equality:** Tests must validate (hexagram_id, phase_bits) identity separately from vector value equality
3. **Canonical producer invocation:** Tests must call `shotgun_expand()` directly, not read from frozen datasets
4. **Revision recording:** Tests must record git revision and input conditions
5. **Explicit failure conditions:** Each test must define what constitutes failure, not just success
6. **Consumer adaptation semantics:** Tests must verify field consumption according to documented semantics, not assumed equivalence

## Phase 1 Implementation Gate

Phase 1 may begin ONLY when:
1. This contract is reviewed and accepted
2. Consumer adaptation semantics are explicitly documented (Section: Consumer Adaptation Semantics)
3. Contract tests are written and FAIL on current code (red phase)
4. Expected behavior and failure conditions are recorded

Phase 1 is NOT authorized by this document. This document is preparation only.