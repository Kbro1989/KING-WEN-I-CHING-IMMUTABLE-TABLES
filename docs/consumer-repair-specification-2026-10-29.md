# Consumer Repair Specification and Contract-Test Plan

**Date:** 2026-10-29
**Purpose:** Repair specification and contract-test plan for all OpenJarvis King Wen consumers. No implementation patches. No source code modified. Canonical engine protected. Gate 2 remains open.
**Canonical producer:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\scripts\full_hexagram_shotgun.py:shotgun_expand()`
**OpenJarvis root:** `C:\Users\krist\Desktop\OpenJarvis`
**Input:** `docs/read-only-evidence-pass-2026-10-29.md`, `docs/consumer-boundary-audit-2026-10-29.md`

---

## 1. Repair Order

### Phase 1: Restore OpenJarvis Adapter Boundary (Blocking)

**Problem:** `OpenJarvis/src/openjarvis/emotion/kingwen_engine_adapter.py:67` references `_EngineModule.collapse_full_128` which no longer exists in `emotional_engine.py`. Adapter cannot load. Three downstream consumers depend on this adapter.

**Required actions (specification only — no implementation):**

1.1. **Define `personality_consensus` semantics.** The canonical producer returns:
   - `dominant_agent_type`: string (e.g., "creative", "receptive")
   - `agent_distribution`: dict mapping agent type → count
   - `dominant_domain`: string (e.g., "social", "combat")
   - `domain_distribution`: dict mapping domain → count
   - `dominant_porosity`: float

   The legacy consumer expects:
   - `consensus_hexagram_id`: int
   - `consensus_hexagram_name`: string
   - `consensus_temporal`: string
   - `consensus_porosity_mean`: float
   - `consensus_porosity_mode`: int
   - `consensus_vector`: 5D dict
   - `consensus_intent`: string
   - `consensus_explanation`: string
   - `consensus_yao`: string
   - `temporal_distribution`: dict

   **Decision required:** Is `personality_consensus` semantically equivalent to `consensus`? If not, what mapping is valid? This is a Gate 2-adjacent decision (representation semantics).

1.2. **Trace adapter's actual needs against expanded output.** The adapter was written for `collapse_full_128`'s output schema, which no longer exists. The investigation must determine what the adapter actually consumes and how it should consume `shotgun_expand`'s output. Any replacement must preserve the producer's semantics rather than recreate collapse under a different name. The `expand_server.py` already exposes `personality_consensus` → `consensus` shape as a reference for how a consumer can read expanded output, but this is a consumer-side adaptation, not a bridge to restore collapse.

1.3. **Update import.** Replace `collapse_full_128 = _EngineModule.collapse_full_128` with either:
   - `shotgun_expand = _EngineModule.shotgun_expand` (if available in `emotional_engine.py` — it is NOT; it's in `scripts/full_hexagram_shotgun.py`)
   - Or: add a sys.path entry for `scripts/` and import `shotgun_expand` from `full_hexagram_shotgun`
   - Or: use the `expand_server.py` HTTP endpoint as the producer interface

   **Decision required:** Which producer interface should the adapter use? Direct import, HTTP, or file-based?

1.4. **Update `_compute_consensus_from_resolved` call.** The adapter calls `consensus_from_resolved = _EngineModule._compute_consensus_from_resolved`. Verify this function still exists in `emotional_engine.py`.

### Phase 2: Classify Frozen-JSON Readers

**Problem:** Six OpenJarvis files read `collapse_full_128_output.json` from disk. The file may be a frozen snapshot with null timestamp/emotional_input.

**Required actions (specification only):**

For each reader, classify the snapshot's intended role:

| Reader | File | Lines | Role Classification | Action Required |
|--------|------|-------|---------------------|-----------------|
| Prompt builder | `kingwen.py` | 100, 109, 143, 450, 831, 1215 | TBD | Inspect: is this intentionally historical? |
| Chat command | `chat_cmd.py` | 915, 1468, 1520 | TBD | Inspect: is this a cache? |
| Blueprint executor | `blueprints/executor.py` | 109 | TBD | Inspect: is this an obsolete substitute? |
| Blueprint registry | `blueprints/registry.py` | 204 | Documentation only | No action needed |
| Oracle speak | `_oracle_speak.py` | 591 | TBD | Inspect: does it need live data? |
| Completion injection | `kingwen_completion_injection.py` | 82-88 | TBD | Inspect: does it need live data? |

**Classification criteria:**
- **Intentionally historical:** The snapshot is used as a reference/audit artifact. No live integration needed.
- **Cache:** The snapshot is a performance cache. Live integration needed only if cache staleness causes incorrect behavior.
- **Obsolete substitute:** The snapshot is used as a substitute for live producer output. Live integration required.

**For each reader, record:**
1. What fields does it read from the snapshot?
2. Does it require live or historical data?
3. What breaks if the snapshot is stale?
4. What breaks if the snapshot is missing?

### Phase 3: Trace Cartesia Voice Path

**Problem:** The Cartesia adapter reads from static `emotional-weights.json` (64 entries, 5D vectors). It does not use dynamic expansion output. Voice output does not vary with `phase_bits` or `emotional_input`.

**Required actions (specification only):**

3.1. **Define intended voice behavior.** Is `hexagram_id` + `phase_bits` + `emotional_input` intended to influence:
   - Voice selection (which voice ID)?
   - Voice parameters (speed, pitch, etc.)?
   - Both?

3.2. **Trace the data path.** From canonical producer → adapter → Cartesia API:
   - Does `hexagram_id` reach the adapter? (Yes — via `vector_for_hexagram(hexagram_id)`)
   - Does `phase_bits` reach the adapter? (No — adapter only takes `hexagram_id`)
   - Does `emotional_input` reach the adapter? (No — adapter has no emotional_input parameter)

3.3. **Define test requirements:**
   - Controlled input: vary `hexagram_id` → verify voice output changes
   - Controlled input: vary `phase_bits` → verify voice output changes (if intended)
   - Controlled input: vary `emotional_input` → verify voice output changes (if intended)
   - Static configuration may be valid for defaults; dynamic behavior must be tested separately

### Phase 4: Verify 3D Avatar Provenance

**Problem:** 512 PLY files exist with manifest entries, but no test verifies mesh geometry matches (hexagram_id, phase_bits).

**Required actions (specification only):**

4.1. **Manifest inspection.** Read `DATASETS/kingwen_avatar_mesh_manifest.json` and verify:
   - 512 entries (64×8)
   - Each entry has `hexagram_id` (1-64), `phase_bits` (0-7)
   - Each entry has `file_path` pointing to existing PLY file
   - No duplicate (hexagram_id, phase_bits) pairs

4.2. **File integrity.** For each PLY file:
   - File exists and is non-empty
   - PLY header is valid (contains `end_header`)
   - Vertex count matches manifest claim
   - File size is within expected range (114KB-293KB per prior audit)

4.3. **Geometry correspondence.** For each (hexagram_id, phase_bits):
   - PLY mesh has wavefunction amplitudes
   - Amplitudes correspond to the hexagram's resolved vector from `shotgun_expand`
   - **Decision required:** What constitutes "correspondence"? Exact match? Within tolerance? Which fields?

### Phase 5: Producer-Side Math Defects (Separate Track)

**Problem:** Hamiltonian energy = 0.0 for all states. Two independent defects:
1. Scale mismatch: pq_dot (vector-scale ~0.01) vs lagrangian (line-count-scale ~2.1-5.1)
2. Empty line_balance: production passes `{}` instead of actual line balance

**Required actions (specification only):**

5.1. **Document Hamiltonian contract.** Define:
   - Intended meaning of Hamiltonian energy in this context
   - Units of pq_dot and lagrangian
   - Valid range of output
   - Sign convention (positive = ? negative = ?)
   - Whether pq_dot and lagrangian share a common scale
   - Whether zero is a valid output or indicates failure

5.2. **Distinguish classified intent from default.** 
   - Current: `dominant_intent = max(matched_intents, ...) if matched_intents else "understand"`
   - Test: `extract_intent('')` → `dominant_intent: "understand"`, `matched_intents: {}`
   - Required: separate reporting of "classified" vs "defaulted" vs "failed"

5.3. **Document porosity schema.**
   - Current: `inject_site['porosity']` (0-4 int), `inject_site['porosity_norm']` (0.0-1.0)
   - Consumers that expect top-level `porosity` will fail
   - Required: document access path for all consumers

---

## 2. Contract-Test Requirements

### Minimum Test Assertions by Boundary

| Boundary | Required Assertion | Test File (to create) | Status |
|----------|-------------------|----------------------|--------|
| Adapter import | Imports successfully without relying on removed symbols | `tests/test_adapter_import.py` | Not written |
| Consumer adaptation | Every consumed field has documented, tested semantics | `tests/test_consumer_adaptation.py` | Not written |
| Identity | All 512 `(hexagram_id, phase_bits)` pairs remain traceable | `tests/test_identity_preservation.py` | Not written |
| Snapshot/live data | Each consumer's data source matches its declared role | `tests/test_consumer_data_source.py` | Not written |
| Voice | Intended phase and emotional inputs reach the voice path | `tests/test_voice_boundary.py` | Not written |
| Avatar | Every mesh has verifiable identity and phase provenance | `tests/test_avatar_provenance.py` | Not written |
| Intent | Defaults are distinguishable from semantic classifications | `tests/test_intent_classification.py` | Not written |
| Hamiltonian | Inputs, intermediate terms, and zero-valued outputs are observable and reproducible | `tests/test_hamiltonian_observability.py` | Not written |

### Test Design Principles

1. **Read-only:** Tests must not modify source code or canonical data.
2. **Reproducible:** Tests must produce identical results on repeated runs.
3. **Independent:** Tests must not depend on external services or network access.
4. **Observable:** Tests must record intermediate values, not just pass/fail.
5. **Separate statuses:** Each test must distinguish:
   - Evidence collected (source/code/output inspected)
   - Test executed (condition actually tested)
   - Disposition reached (result accepted or left unresolved)

### Test Specification: Adapter Import

```python
# tests/test_adapter_import.py
import sys
sys.path.insert(0, 'C:/Users/krist/Desktop/OpenJarvis/src')
sys.path.insert(0, 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

def test_adapter_imports_without_collapse_full_128():
    """Adapter must not reference collapse_full_128 (removed function)."""
    import ast, pathlib
    adapter_path = pathlib.Path('C:/Users/krist/Desktop/OpenJarvis/src/openjarvis/emotion/kingwen_engine_adapter.py')
    source = adapter_path.read_text()
    assert 'collapse_full_128' not in source, "Adapter still references removed function"

def test_shotgun_expand_available():
    """shotgun_expand must be importable from the canonical producer."""
    from scripts.full_hexagram_shotgun import shotgun_expand
    result = shotgun_expand(request_text='test', emotional_input=50)
    assert 'expanded' in result and len(result['expanded']) == 64
    assert 'resolved' in result and len(result['resolved']) == 512

def test_adapter_consult_returns_512_states():
    """Adapter consult must return 512 resolved states from canonical producer."""
    # This test will FAIL until adapter is repaired
    # Documented as expected failure
    pass
```

### Test Specification: Identity Preservation

```python
# tests/test_identity_preservation.py
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from emotional_engine import capture_pre_slider

def test_512_unique_identities():
    result = capture_pre_slider(request_text='delta')
    resolved = result['resolved']
    ids = [(r['hexagram_id'], r['phase_bits']) for r in resolved]
    assert len(set(ids)) == len(ids) == 512

def test_phase_distribution():
    from collections import Counter
    result = capture_pre_slider(request_text='delta')
    phases = Counter(r['phase_temporal'] for r in result['resolved'])
    assert len(phases) == 8
    assert all(v == 64 for v in phases.values())

def test_no_cross_hexagram_vector_duplicates():
    from collections import Counter
    result = capture_pre_slider(request_text='delta')
    vecs = [tuple(sorted(r['expanded_vector'].items())) for r in result['resolved']]
    dup_groups = {k: v for k, v in Counter(vecs).items() if v > 1}
    for vec in dup_groups:
        hexes = set(r['hexagram_id'] for r in result['resolved'] if tuple(sorted(r['expanded_vector'].items())) == vec)
        assert len(hexes) == 1, f"Cross-hexagram duplicate: {hexes}"
```

### Test Specification: Intent Classification

```python
# tests/test_intent_classification.py
import sys
sys.path.insert(0, '.')
from emotional_engine import extract_intent

def test_empty_text_defaults():
    r = extract_intent('')
    assert r['dominant_intent'] == 'understand'
    assert r['matched_intents'] == {} or r['matched_intents'] == []

def test_classified_text_has_matched_intents():
    r = extract_intent('combat attack strength')
    assert r['matched_intents'] != {}, f"Expected non-empty, got {r['matched_intents']}"

def test_default_distinguishable_from_classified():
    r_default = extract_intent('')
    r_classified = extract_intent('combat attack strength')
    # Default should have empty matched_intents
    assert r_default['matched_intents'] == {} or r_default['matched_intents'] == []
    # Classified should have non-empty matched_intents
    assert r_classified['matched_intents'] != {}
    # Both may have same dominant_intent, but matched_intents differs
```

### Test Specification: Hamiltonian Observability

```python
# tests/test_hamiltonian_observability.py
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from emotional_engine import capture_pre_slider, _hamiltonian_energy

def test_energy_zero_for_all_states():
    result = capture_pre_slider(request_text='delta')
    resolved = result['resolved']
    energies = []
    for r in resolved:
        rv = list(r['resolved_vector'].values())
        ev = list(r['expanded_vector'].values())
        lb = r['line_balance']
        e = _hamiltonian_energy(rv, ev, lb)
        energies.append(e)
    assert all(e == 0.0 for e in energies), f"Non-zero energy found: {set(energies)}"
    assert len(set(energies)) == 1, f"Multiple energy values: {set(energies)}"

def test_energy_intermediates_observable():
    result = capture_pre_slider(request_text='delta')
    r = result['resolved'][0]
    rv = list(r['resolved_vector'].values())
    ev = list(r['expanded_vector'].values())
    lb = r['line_balance']
    # Record intermediates
    pq_dot = sum(float(rv[i]) * (float(rv[i]) - float(ev[i])) for i in range(len(rv)))
    print(f'pq_dot={pq_dot}, line_balance={lb}')
    # Lagrangian with correct line_balance
    # (documented, not asserted — contract not yet defined)
```

---

## 3. What Must Not Change Implicitly

1. **No canonical expansion or identity model changes** as a side effect of adapter repair.
2. **No treating `personality_consensus` as equivalent to `consensus_hexagram_id`** without evidence. Matching field names is not proof of semantic equivalence.
3. **No replacing historical snapshots** before their intended role is established. Only snapshots classified as "obsolete substitute" require live integration.
4. **No formula, scale, sign, or clamping changes** to force nonzero Hamiltonian values. The mathematical contract must be defined first.
5. **No interpreting the 48 within-hexagram duplicate-vector groups** as identity collisions. The audit distinguishes those from the 512 unique identity pairs.
6. **No Gate 2 closure** by implication. The three outstanding decisions (canonical representation, Path A vs B, invalid-input semantics) remain unresolved.
7. **No cross-hexagram normalization** of vectors, porosity, or energy.
8. **No inferred uncertainty weighting** from `emotional_input` without explicit contract and independent validation.

---

## 4. Disposition

| Workstream | Disposition |
|-----------|-------------|
| OpenJarvis adapter | Repair specification defined; implementation deferred until semantic equivalence of `personality_consensus` is established |
| Frozen-JSON readers | Classification criteria defined; per-reader role determination required before any integration |
| Cartesia voice path | Intended behavior undefined; trace specification defined; dynamic behavior not yet tested |
| 3D avatar provenance | Manifest inspection and file integrity tests specified; geometry correspondence requires contract |
| Hamiltonian energy | Contract specification defined; implementation deferred until contract agreed |
| Intent classification | Separation of classified vs defaulted specified; test design provided |
| Porosity schema | Access path documented; consumer verification required |
| Vector type contract | Accepted representation must be specified; valid and invalid inputs tested separately |

**Decision:** Finish contract and tests first, then repair consumers in isolated changes with before-and-after evidence. The reported audits provide a strong basis for that work. No source edits are implied or authorized by this specification.

**Gate 2:** OPEN. Three decisions unresolved. No closure by implication.

---

## 5. Refinements from External Review (2026-10-29)

### 5.1 Hamiltonian Test Must Not Encode Zero as Permanent Expectation

The `test_hamiltonian_observability.py` tests verify current energy is zero and intermediates are observable. They must NOT assert that zero is the permanent expected result. A separate regression test (`test_hamiltonian_current_behavior_regression`) preserves current behavior until the mathematical contract authorizes a change.

**Pattern:**
- `test_energy_zero_current_behavior`: verifies current output is zero (observation)
- `test_hamiltonian_current_behavior_regression`: preserves current behavior as regression baseline
- Neither test asserts that zero is the correct or intended value
- When contract is agreed, both tests will be updated

### 5.2 Identity Test Must Invoke Canonical Producer

The identity test must invoke `capture_pre_slider()` directly, not read from a previously generated dataset. It must also:
- Record the revision and input conditions (request_text, emotional_input)
- Test identity separately from vector equality
- Verify that vector duplicates do not constitute identity collisions

### 5.3 Consumer Acceptance Criteria Beyond Import

A successful adapter import is necessary but insufficient. The adapter must also demonstrate:
1. It consumes the intended live producer output (not a frozen snapshot)
2. It maps fields according to documented semantics (not just field names)
3. It preserves identity and provenance (512 pairs traceable end-to-end)
4. Controlled input changes produce expected differences in output

Similarly, a valid PLY file does not prove geometry correspondence. The avatar test must verify identity-to-mesh lineage, not just file existence.

### 5.4 Phase 1 Only — Separately Reviewable Unit

Phase 1 (adapter boundary repair) must be completed as a separately reviewable unit:
- No bundling of snapshot readers, voice path, avatar pipeline, or Hamiltonian changes
- Before-and-after evidence captured for each change
- Canonical producer output verified identical before and after
- Gate 2 decisions verified unchanged
- No other consumer modified

### 5.5 Test Design Principle: Observation vs. Permanent Expectation

Tests must distinguish between:
- **Observation tests:** Document current behavior without asserting it is correct
- **Regression tests:** Preserve current behavior until authorized change
- **Contract tests:** Assert behavior defined by an agreed contract

A test that observes zero energy is not the same as a test that asserts zero is the correct value. The former is a documentation; the latter is a design decision.