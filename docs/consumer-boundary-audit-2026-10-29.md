# Consumer-Boundary Audit — OpenJarvis King Wen Integration

**Date:** 2026-10-29
**Purpose:** Trace data from the canonical producer (`shotgun_expand` in `KING-WEN-I-CHING-IMMUTABLE-TABLES`) through every OpenJarvis consumer boundary. Identify stale references, information loss, and interface mismatches. No source code modified.
**Canonical producer:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\scripts\full_hexagram_shotgun.py:shotgun_expand()`
**Canonical engine:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\emotional_engine.py`
**OpenJarvis root:** `C:\Users\krist\Desktop\OpenJarvis`

---

## Audit Finding: Stale Function Reference (CRITICAL)

### OpenJarvis adapter fails to import

**File:** `OpenJarvis/src/openjarvis/emotion/kingwen_engine_adapter.py`
**Line:** 67
**Code:**
```python
collapse_full_128 = _EngineModule.collapse_full_128
```

**Problem:** `collapse_full_128` no longer exists in `emotional_engine.py`. It was removed in the 2026-09-01 cleanup (replaced by `shotgun_expand`). The adapter references it without a try/except fallback. When loaded, it raises:
```
AttributeError: module 'kingwen_emotional_engine' has no attribute 'collapse_full_128'
```

**Verified:** `PYTHONPATH=src python -c "from openjarvis.emotion.kingwen_engine_adapter import consult"` → `AttributeError: module 'kingwen_emotional_engine' has no attribute 'collapse_full_128'`

**Impact:** The OpenJarvis emotion adapter CANNOT LOAD. Any OpenJarvis code path that imports `kingwen_engine_adapter` will fail.

---

## Consumer Inventory

### 1. King Wen Engine Adapter (`kingwen_engine_adapter.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/emotion/kingwen_engine_adapter.py` |
| **Function** | `consult()` (line 184) |
| **Producer called** | `collapse_full_128(emotional_input=...)` (STALE — function removed) |
| **Canonical producer** | `shotgun_expand(request_text=..., emotional_input=...)` |
| **Status** | **BROKEN** — adapter cannot load |
| **Fields consumed** | `consensus`, `expanded`, `resolved` from collapse output |
| **Fields expected by adapter** | `consensus_hexagram_id`, `consensus_hexagram_name`, `consensus_temporal`, `consensus_porosity_mean`, `consensus_vector`, `consensus_intent`, `consensus_explanation`, `consensus_yao`, `temporal_distribution` |
| **Canonical producer output** | `expanded` (64), `resolved` (512), `personality_consensus` (not `consensus`) |
| **Mismatch** | Adapter expects `consensus` dict; shotgun_expand returns `personality_consensus`. Adapter expects `consensus_hexagram_id`; shotgun returns `dominant_agent_type`, `agent_distribution`, `dominant_domain`, `domain_distribution` |

**Finding:** The adapter was written for `collapse_full_128`'s output schema, which has been replaced by `shotgun_expand`'s different schema. The adapter needs:
1. Replace `collapse_full_128` import with `shotgun_expand` (or add try/except fallback)
2. Bridge `personality_consensus` → `consensus` shape (as done in `expand_server.py`)
3. Update field names (`consensus_hexagram_id` → first expanded hexagram's id, etc.)

### 2. King Wen Completion Injection (`kingwen_completion_injection.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/emotion/kingwen_completion_injection.py` |
| **Lines** | 82-88 |
| **Code** | `from openjarvis.emotion.kingwen_engine_adapter import collapse_full_128` then `expansion = collapse_full_128(emotional_input=emotional_input)` |
| **Status** | **BROKEN** — depends on broken adapter |
| **Fallback** | Line 93: `from emotional_engine import expand_hexagram, sample_resolve` (also may fail due to import path) |
| **Fields consumed** | `expanded`, `resolved` from collapse output |
| **Fields expected** | `expanded_count`, `resolved_count`, `expanded_vector`, `resolved_vector` |

**Finding:** Same stale reference as adapter. Fallback path also uses `emotional_engine` directly without `sys.path` setup.

### 3. King Wen Prompt Builder (`kingwen.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/emotion/kingwen.py` |
| **Lines** | 100, 109, 143, 450, 831, 1215 |
| **Reference** | Reads `collapse_full_128_output.json` from disk |
| **Status** | **STALE** — file may exist but is a frozen snapshot (timestamp/emotional_input may be null) |
| **Fields consumed** | `expanded`, `resolved`, `consensus` from JSON file |
| **Fields expected** | Same as adapter (consensus schema) |

**Finding:** Reads a frozen JSON snapshot instead of calling the live producer. The snapshot may be stale (null timestamp/emotional_input). This is a "frozen snapshot" consumer pattern.

### 4. Chat Command (`chat_cmd.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/cli/chat_cmd.py` |
| **Lines** | 909, 915, 1468, 1520 |
| **Reference** | Reads `collapse_full_128_output.json` from disk; also references `emotional_engine.py` at line 1074 |
| **Status** | **STALE** — same frozen snapshot pattern |
| **Fields consumed** | JSON file existence check, path resolution |
| **Fields expected** | File existence for `/blueprint` command |

**Finding:** Multiple references to the stale JSON file. The `/blueprint` command appears to depend on this file existing.

### 5. Blueprint Executor (`blueprints/executor.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/blueprints/executor.py` |
| **Line** | 109 |
| **Reference** | Reads `collapse_full_128_output.json` from disk |
| **Status** | **STALE** — same frozen snapshot pattern |

### 6. Blueprint Registry (`blueprints/registry.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/blueprints/registry.py` |
| **Line** | 204 |
| **Reference** | String reference: "2) Call collapse_full_128() to get all 512 resolved states." |
| **Status** | **DOCUMENTATION ONLY** — string in docstring, not executable |

### 7. Oracle Speak (`_oracle_speak.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/cli/_oracle_speak.py` |
| **Line** | 591 |
| **Reference** | `from openjarvis.emotion.kingwen_engine_adapter import consult as local_consult` |
| **Status** | **BROKEN** — depends on broken adapter |

### 8. Voice Router (`kingwen_voice_router.py`)

| Field | Value |
|-------|-------|
| **File** | `KING-WEN-I-CHING-IMMUTABLE-TABLES/kingwen_voice_router.py` |
| **Lines** | 495 |
| **Status** | **STANDALONE** — no OpenJarvis integration in this repo |
| **Fields consumed** | Hexagram ID → voice mode mapping |
| **Fields expected** | `hexagram_id` only (no emotional vector, no phase) |

**Finding:** The voice router is a standalone file that maps hexagram_id to voice mode. It does not consume emotional vectors, phase_bits, or porosity. It is not wired into OpenJarvis.

### 9. Cartesia Adapter (`cartesia_adapter.py`)

| Field | Value |
|-------|-------|
| **File** | `OpenJarvis/src/openjarvis/speech/cartesia_adapter.py` |
| **Class** | `CartesiaAdapter` |
| **Data source** | `emotional-weights.json` (static 64-entry file) |
| **Status** | **STATIC** — uses static weights, not dynamic shotgun_expand output |
| **Fields consumed** | `hexagram_id` → 5D vector from static file |
| **Fields expected** | 5D emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight) |

**Finding:** The adapter reads from a static JSON file (`emotional-weights.json`) with 64 entries. It does not call `shotgun_expand` or use dynamic expansion. The 5D vectors are fixed per hexagram, not per (hexagram, phase). This is a "static weights" consumer, not a "dynamic expansion" consumer.

### 10. 3D Avatar Meshes (`kingwen_avatar_meshes/`)

| Field | Value |
|-------|-------|
| **Path** | `KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/kingwen_avatar_meshes/` |
| **Count** | 512 PLY files (64×8) |
| **Manifest** | `kingwen_avatar_mesh_manifest.json` (512 entries) |
| **Status** | **UNVERIFIED** — no test verifies mesh geometry matches hexagram state |
| **Fields expected** | Hexagram ID + phase → PLY mesh with wavefunction amplitudes |

**Finding:** 512 PLY files exist with manifest entries. No test verifies that mesh geometry corresponds to the correct (hexagram_id, phase_bits) state. The manifest has wavefunction amplitudes per phase, but these are not cross-checked against `shotgun_expand` output.

---

## Consumer-Boundary Findings Summary

### Finding CB-1: OpenJarvis Adapter Cannot Load (CRITICAL)

**Root cause:** `kingwen_engine_adapter.py` line 67 references `_EngineModule.collapse_full_128` which no longer exists in `emotional_engine.py`.

**Impact:** Any OpenJarvis code path that imports `kingwen_engine_adapter` fails. This includes:
- `kingwen_oracle_consult_tool.py:execute()` (line 97)
- `_oracle_speak.py` (line 591)
- `kingwen_completion_injection.py` (line 82)

**Consumer data path:** BROKEN — cannot reach canonical producer.

### Finding CB-2: Schema Mismatch Between Adapter and Producer

**Problem:** The adapter expects `collapse_full_128`'s output schema (`consensus`, `consensus_hexagram_id`, `consensus_hexagram_name`, etc.). The canonical producer `shotgun_expand` returns a different schema (`personality_consensus`, `dominant_agent_type`, `agent_distribution`, `dominant_domain`, `domain_distribution`).

**Impact:** Even if the import is fixed, the adapter would fail to extract fields from the shotgun_expand output.

**Bridge needed:** Map `personality_consensus` → `consensus` shape (as done in `expand_server.py`).

### Finding CB-3: OpenJarvis Uses Frozen Snapshot (`collapse_full_128_output.json`)

**Problem:** Multiple OpenJarvis files read `collapse_full_128_output.json` from disk instead of calling the live producer. This file may be a frozen snapshot with null timestamp/emotional_input.

**Affected files:**
- `kingwen.py` (lines 100, 109, 143, 450, 831, 1215)
- `chat_cmd.py` (lines 915, 1468, 1520)
- `blueprints/executor.py` (line 109)

**Impact:** Consumers may be using stale data instead of live expansion.

### Finding CB-4: Cartesia Adapter Uses Static Weights

**Problem:** The adapter reads from `emotional-weights.json` (static 64-entry file) instead of calling `shotgun_expand`. The 5D vectors are fixed per hexagram, not per (hexagram, phase).

**Impact:** Voice output does not vary with phase_bits or emotional_input. This is a "static weights" consumer, not a "dynamic expansion" consumer.

### Finding CB-5: Voice Router Is Standalone

**Problem:** `kingwen_voice_router.py` is a standalone file with no OpenJarvis integration. It maps hexagram_id → voice mode but does not consume emotional vectors, phase_bits, or porosity.

**Impact:** The voice router is not wired into the OpenJarvis pipeline. It is a standalone utility, not a consumer of the canonical producer.

### Finding CB-6: 3D Avatar Meshes Unverified

**Problem:** 512 PLY files exist with manifest entries, but no test verifies mesh geometry matches (hexagram_id, phase_bits). The manifest has wavefunction amplitudes per phase, but these are not cross-checked against `shotgun_expand` output.

**Impact:** Mesh geometry may not correspond to the canonical state. This is an unverified consumer.

---

## Consumer-Boundary Audit Disposition

| Consumer | Producer Path | Status | Information Loss Risk |
|----------|--------------|--------|----------------------|
| OpenJarvis consult tool | `collapse_full_128` (BROKEN) | **BROKEN** | Cannot reach producer |
| King Wen completion injection | `collapse_full_128` (BROKEN) | **BROKEN** | Cannot reach producer |
| King Wen prompt builder | `collapse_full_128_output.json` (STALE) | **STALE** | May use frozen snapshot |
| Chat command | `collapse_full_128_output.json` (STALE) | **STALE** | May use frozen snapshot |
| Blueprint executor | `collapse_full_128_output.json` (STALE) | **STALE** | May use frozen snapshot |
| Oracle speak | `kingwen_engine_adapter` (BROKEN) | **BROKEN** | Cannot reach producer |
| Voice router | Standalone (no integration) | **UNWIRED** | Not a consumer |
| Cartesia adapter | Static weights (not dynamic) | **STATIC** | Does not use phase or emotional_input |
| 3D avatar meshes | File-based (unverified) | **UNVERIFIED** | Geometry not cross-checked |
| King Wen link address | `/decode` route (worker) | **UNVERIFIED** | Worker may use stale data |

---

## Recommended Next Steps (in priority order)

1. **Fix OpenJarvis adapter import** — replace `collapse_full_128` with `shotgun_expand` or trace the adapter's actual needs and determine how it should consume the expanded output. This is the highest-priority consumer fix because it unblocks 3 downstream consumers.

2. **Consumer adaptation for personality_consensus → consensus** — trace adapter's actual field needs against expanded output; do not recreate collapse schema under a different name.

3. **Update stale JSON file references** — replace `collapse_full_128_output.json` reads with live `shotgun_expand()` calls in `kingwen.py`, `chat_cmd.py`, `blueprints/executor.py`.

4. **Wire cartesia adapter to dynamic expansion** — replace static `emotional-weights.json` lookup with `shotgun_expand` output per (hexagram_id, phase_bits).

5. **Verify 3D avatar mesh geometry** — cross-check PLY mesh manifest against `shotgun_expand` output for (hexagram_id, phase_bits) correspondence.

6. **Write consumer-boundary tests** — for each consumer, verify that output identity, phase, vector, yao, porosity, and provenance match the canonical producer output.

---

## Boundaries Preserved

- No normalization between hexagrams
- No inferred uncertainty weighting
- No silent replacement of Hamiltonian zeros
- No Gate 2 closure by implication
- No source code modified (OpenJarvis or immutable tables)
- Canonical engine protected
- Geometric alignment remains separate experimental layer