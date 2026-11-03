**Cross-reference to current run (2026-11-02):** F-05 (4 of 7 consumers still reference nonexistent `shotgun_expand_output.json`), F-06 (`build_full_shotgun_jsonl.py` import path broken), and F-07 (no `scripts/__init__.py`) are now VALIDATED as separate findings. The `or 0.35` fix was verified (13/13 PASS) but F-01 (`or 0.0875` remaining) and F-02 (None handling) are new findings not identified in this report. See `docs/remediation-verification-matrix.md` Entries 1–2 and `docs/cross-reference-audit-2026-11-02.md`.

# Shotgun Authority Lineage Audit

**Date:** 2026-11-02  
**Status:** READ-ONLY AUDIT — no source modifications authorized  
**Purpose:** Establish authority and provenance of each shotgun-related output without changing implementation

---

## 1. Canonical Producer Trace

### Function Signature
```python
shotgun_expand(request_text: str = "", emotional_input: float = 50.0) -> dict
```
**Location:** `scripts/full_hexagram_shotgun.py` (no `__init__.py` in `scripts/`)

### Invocation Methods
| Method | Command | Works? |
|--------|---------|--------|
| Flat import via sys.path | `sys.path.insert(0, 'scripts'); from full_hexagram_shotgun import shotgun_expand` | ✅ Yes |
| Package import | `from scripts.full_hexagram_shotgun import shotgun_expand` | ❌ No (missing `scripts/__init__.py`) |
| Module execution | `python -m scripts.full_hexagram_shotgun` | ❌ No (missing `__init__.py`) |
| Direct execution | `python scripts/full_hexagram_shotgun.py` | ✅ Yes (if `__main__` guard exists) |

### Source Inputs
- `kingwen_ternary_tables_complete.py` (HEXAGRAM_BASE, 64 hexagrams)
- `emotional_engine.py` (emotional weights, collapse logic)
- `kingwen_quantum_process.py` (Hamiltonian, Gaussian kernel)
- `config` or default emotional_input=50

### Complete Output Schema (verified runtime, emotional_input=50)

**Top-level keys (19):**
```
source, request_text, emotional_input, total_expanded, total_resolved,
total_encodings, ternary_line_permutations_per_hex, total_ternary_line_permutations,
total_domained_routes, capture_point, expanded, resolved, personality_map,
personality_consensus, personality_subsets_total, avg_hamiltonian_energy,
min_hamiltonian_energy, max_hamiltonian_energy, table_sources
```

**expanded[] (64 items, 37 keys):**
```
hexagram_id, name, unicode, upper_trigram, lower_trigram, binary_bottom_to_top,
coder_specialty, rs3_actionable, category, action, domain_vector, training_notes,
table_personality, hexagram_symbols, intent, phase_bits, request_text,
avalokiteshvara_arm, jkd_pedagogy_anchor, quantum_superposition, hermes_layer,
schauberger_metrics, phase_temporal, inject_site, expanded_vector, resolved_vector,
ternary_slots, personality_subsets, ternary_729_permutations_count, line_states,
line_balance, sample_paths, yao_vocabulary, pre_slider, projections,
schauberger_parsing, domain_routing_palette
```

**resolved[] (512 items, 26 keys):**
```
hexagram_id, category, action, coder_specialty, rs3_actionable, training_notes,
trainingNotes, hexagram_symbols, intent, table_personality, domain_vector, phase_bits,
phase_temporal, inject_site, expanded_vector, resolved_vector, line_states,
line_balance, quantum_avatar_state, sample_paths, yao_vocabulary, pre_slider,
personality_subsets, ternary_slots, ternary_729_permutations_count, schauberger_parsing
```

**personality_consensus (8 keys):**
```
dominant_agent_type, agent_distribution, dominant_domain, domain_distribution,
slot_distribution, source, consensus_vector, dominant_intent
```

### Verified Null Patterns (emotional_input=50)
| Field | expanded (64) | resolved (512) |
|-------|---------------|----------------|
| personality_subsets | 0 null | 512 null (ALL) |
| ternary_slots | 0 null | 512 null (ALL) |
| schauberger_parsing | 0 null | 512 null (ALL) |
| projections | 0 null | 512 null (ALL) |

**Design observation:** Expanded layer computes these fields; resolved layer does not carry them. This is a design choice, not a bug, but it means consumers reading only `resolved[]` lose ternary_slots, personality_subsets, schauberger_parsing, and projections.

### Verified Values
- Hamiltonian energy: 0.0 for all 512 resolved states (scale mismatch, documented)
- personality_subsets_total: 1152
- emotional_input returned: 25 (derived from request, not 50 as passed — derived internally)
- total_encodings: 512
- ternary_729_permutations_count: 729 (per hexagram)

---

## 2. Consumer Trace: Seven Identified Files

### Authority Status Classification

| # | File | Producer/Consumer | Authority | Status |
|---|------|-------------------|-----------|--------|
| 1 | `emotional_engine.py` | Internal consumer (calls `_hamiltonian_energy`) | Canonical consumer | Both paths H=0.0 |
| 2 | `build_full_shotgun_jsonl.py` | Intended direct consumer | **Import blocked** | `from scripts.full_hexagram_shotgun` fails (no `__init__.py`) |
| 3 | `generate_sovereign_world.py` | Separate JKD scalar | Independent | Different formula (coherence − chaos − ...) |
| 4 | `update_3d_kits_with_quantum_wavepackets.py` | Independent bypass | Independent | Does not consume M3 H |
| 5 | `shotgun_rollout_runtime.py` | Direct consumer | Canonical consumer | Inherits H=0 |
| 6 | `rl_shotgun_measurables.py` | Indirect consumer | Canonical consumer | h_signal=0.0 |
| 7 | `generate_avatar_meshes.py` | Direct consumer | Canonical consumer | Inherits H=0 |

### Transformation Analysis

| Consumer | Modifies shotgun data? | How |
|----------|----------------------|-----|
| emotional_engine.py | No (internal) | Calls `_hamiltonian_energy` with empty `line_balance` |
| build_full_shotgun_jsonl.py | Yes (serializes) | Rounds H to 6 decimals, stores as `hamiltonian_energy` |
| generate_sovereign_world.py | Yes (parallel) | Computes JKD scalar independently, stores as `hamiltonian_energy` |
| update_3d_kits | No (bypass) | Does not read M3 H at all |
| shotgun_rollout_runtime | No (propagates) | Reads H=0, propagates downstream |
| rl_shotgun_measurables | No (propagates) | h_signal=0.0 from H=0 |
| generate_avatar_meshes | No (propagates) | Inherits H=0 |

---

## 3. Reinvention Groups: Behavioral Comparison

### Group A: Godot 729 Generation (5 versions)

| File | Key Difference |
|------|---------------|
| `generate_godot_729.py` | Base version, 9 funcs |
| `generate_godot_729_v2.py` | Refactored, 8 funcs |
| `generate_godot_729_v3.py` | Further refactored, 8 funcs |
| `generate_godot_729_v4.py` | Further refactored, 8 funcs |
| `generate_godot_729_sovereign.py` | Uses manifest validation, 14 funcs, `validate_value_against_manifest()` |

**Unique behavior in sovereign version:** `validate_value_against_manifest()` — checks values against canonical manifest before generation. This validation logic is NOT present in v1-v4.

### Group B: Training Data Generation (4 implementations)

| File | Key Difference |
|------|---------------|
| `build_full_shotgun_jsonl.py` | Intended direct consumer (import blocked) |
| `regenerate_training_data.py` | `regenerate_full_shotgun_jsonl()`, `regenerate_kingwen_pretrain_jsonl()` |
| `recover_training_data.py` | Quarantine + recovery pipeline (gates A/B/C) |
| `build_per_hex_training_data.py` | References nonexistent `shotgun_expand_output.json` |

**Unique behavior in recover_training_data:** Gate A/B/C verification pipeline with quarantine logic. This is a quality-control layer not present in other implementations.

### Group C: Hamiltonian (2 formulas, same field name)

| Producer | Formula | Meaning |
|----------|---------|---------|
| M3 (`_hamiltonian_energy`) | `pq_dot - lagrangian`, clamped | M3 energy-like scalar |
| JKD ingestion | `coherence - chaos - 0.5*darkTone + 0.3*voiceWeight - 0.2*whimsy` | JKD-derived scalar |

**Classification:** Semantic schema collision. Shared field name does not establish shared provenance or mathematical meaning.

### Group D: Ternary Expansion (3 implementations)

| File | Key Difference |
|------|---------------|
| `full_hexagram_shotgun.py` | Canonical (binary 512 + ternary 729 count) |
| `kingwen_quantum_expand.py` | 12 funcs, PQC v2.0, 12 qubits, marginalize_to_46656 |
| `generate_729_resolved_full.py` | `compute_ternary_emotional_vector()`, 3 funcs |

**Unique behavior in kingwen_quantum_expand:** PQC v2.0 quantum circuit with 12 qubits, mask-conditioned gates. This is a quantum-computing layer not present in the canonical shotgun.

---

## 4. Training-Data Provenance Map

### Existing JSONL Files

| File | Size | Records | Source |
|------|------|---------|--------|
| `kingwen_train_data/full_shotgun_expansion_all.jsonl` | 32MB | 1536 (64×8×3) | `full_hexagram_shotgun.py` |
| `kingwen_train_data/full_shotgun_expansion_corpus_enriched.jsonl` | 31MB | ? | Enriched version |
| `kingwen_train_data/full_shotgun_expansion_lexical_gate.jsonl` | 33MB | ? | Lexical-gated version |
| `kingwen_train_data/kingwen_pretrain.jsonl` | 275KB | ? | Pretrain subset |
| `kingwen_train_data/megatron_multi_domain.jsonl` | 97KB | ? | Multi-domain |
| `output/per_hex_training/*.jsonl` | 64 files | Per-hex | `build_per_hex_training_data.py` (broken ref) |

### Provenance Gaps

1. **No single canonical serialization contract** — three JSONL files with different enrichment levels, no versioned schema
2. **`build_full_shotgun_jsonl.py` cannot run** — import blocked by missing `__init__.py`
3. **`build_per_hex_training_data.py` references nonexistent file** — `shotgun_expand_output.json`
4. **`regenerate_training_data.py` exists** — suggests prior regeneration was needed

---

## 5. Package/Import Failure: Reproducible Conditions

### Condition A: Flat import (works)
```python
import sys
sys.path.insert(0, 'scripts')
from full_hexagram_shotgun import shotgun_expand  # ✅ Works
```

### Condition B: Package import (fails)
```python
from scripts.full_hexagram_shotgun import shotgun_expand  # ❌ ModuleNotFoundError
```
**Root cause:** `scripts/` has no `__init__.py`. Python 3.3+ namespace packages can work without `__init__.py` under certain conditions (PEP 420), but the observed failure occurs when:
- Working directory is repo root
- `scripts/` is not on `sys.path`
- No `__init__.py` exists

### Condition C: kingwen_train_data import (fails)
```python
import kingwen_train_data.build_full_shotgun_jsonl  # ❌ ImportError
```
**Root cause:** `kingwen_train_data/` also has no `__init__.py`, AND the module internally imports `from scripts.full_hexagram_shotgun` which fails.

### Namespace Package Qualification

Per PEP 420, Python 3.3+ CAN import from directories without `__init__.py` IF:
- The directory is on `sys.path`
- No conflicting module with the same name exists

The failure here is NOT that namespace packages are impossible — it's that the import statement `from scripts.full_hexagram_shotgun` requires `scripts` to be importable as a package, which requires it to be on `sys.path` as a parent. When running from repo root with `scripts/` NOT on `sys.path`, the import fails.

**Adding `scripts/__init__.py` would fix this**, but the audit should not assume it's the only fix — `sys.path` insertion or `PYTHONPATH=scripts` would also work.

---

## 6. Authority Matrix: Producer/Consumer/Authority Status

| Producer | Output | Authority Status | Consumers |
|----------|--------|------------------|-----------|
| `shotgun_expand()` | 64 expanded + 512 resolved | **Canonical** | 7 direct consumers |
| `generate_full_shotgun_30gb.py` | 30GB output | **Duplicate** (reimplements) | None identified |
| `generate_729_resolved_full.py` | 729 resolved | **Duplicate** (reimplements) | None identified |
| `kingwen_quantum_expand.py` | 5,832 ternary states | **Independent** (quantum layer) | `scripts/ternary_full_expansion.json` |
| `build_full_shotgun_jsonl.py` | JSONL serialization | **Blocked** (import failure) | Training pipeline |
| `build_per_hex_training_data.py` | Per-hex JSONL | **Blocked** (missing file) | None identified |
| `hexagram_shotgun_matcher.py` | Matcher results | **Blocked** (missing file) | None identified |

---

## 7. Recommended Execution Order (Not Yet Authorized)

1. **Trace `shotgun_expand()` runtime** — ✅ COMPLETE (this audit)
2. **Establish output schema contract** — ✅ COMPLETE (Section 1)
3. **Trace 7 consumers against contract** — ✅ COMPLETE (Section 2)
4. **Compare 4 reinvention groups** — ✅ COMPLETE (Section 3)
5. **Map training-data provenance** — ✅ COMPLETE (Section 4)
6. **Document package/import failure** — ✅ COMPLETE (Section 5)

### Next Steps (Awaiting Authorization)

| Step | Action | Risk |
|------|--------|------|
| A | Create `scripts/__init__.py` | Low — fixes imports |
| B | Consolidate 5 Godot generators | Medium — may lose unique validation in sovereign version |
| C | Fix 4 files referencing nonexistent JSON | Low — switch to `shotgun_expand()` call |
| D | Unify training-data serialization | Medium — 3 JSONL files with different enrichment |
| E | Document Hamiltonian field-name collision | Low — documentation only |

---

## 8. Research Constraints Honored

- ✅ No source modifications
- ✅ No formula changes
- ✅ No Gate 2 closure
- ✅ All findings recorded as supplementary evidence
- ✅ Observed behavior distinguished from proposed corrections
- ✅ No deletion or consolidation of competing implementations
- ✅ No canonical authority assigned without evidence
- ✅ External audit claims verified against runtime evidence before acceptance
