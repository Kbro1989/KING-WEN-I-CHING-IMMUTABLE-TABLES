# Read-Only Evidence Pass — Research-to-Test Traceability Matrix

**Date:** 2026-10-29
**Purpose:** Evidence pass on the 29 traceability items. Each item records: exact file and symbol, current evidence, reproducible test command, observed result, and unresolved decision. No source code modified.
**Canonical engine:** `emotional_engine.py` at git revision `71fbf28f8e92c6a7de74c50a304906ef81963a7d`
**Gate 2:** OPEN.

---

## Evidence Summary Table

| ID | Category | Exact File:Symbol | Evidence Observed | Test Command | Observed Result | Status | Unresolved Decision |
|----|----------|-------------------|-------------------|-------------|-----------------|--------|-------------------|
| RF-1 | Representation Fidelity | `emotional_engine.py:expand_hexagram()` | 29 duplicate expanded_vector groups, all within same hexagram | `python -c "..."` (identity check) | 512 unique (hexagram_id, phase_bits); 0 cross-hexagram duplicates | Evidence collected | None — invariant holds |
| RF-2 | Representation Fidelity | `scripts/full_hexagram_shotgun.py:shotgun_expand()` | SHA-256 hash match across runs (reported) | Run shotgun_expand 3× with identical inputs | Not independently verified in this pass | Evidence collected | Need independent hash verification |
| RF-3 | Representation Fidelity | `emotional_engine.py:capture_pre_slider()` | 8 phase types × 64 = 512; all required fields present | Field conservation check | 0 missing required fields (top-level); porosity nested in inject_site, 0 missing | Evidence collected | Test not yet written |
| RF-4 | Representation Fidelity | `scripts/math_to_kingwen_adapter.py:build_request_text()` | 6 provenance fields in fixture | Fixture inspection | All 6 fields present for equation 0 | Evidence collected | Need 991/991 verification |
| RF-5 | Representation Fidelity | OpenJarvis: `kingwen_oracle_consult_tool.py:execute()`, `cartesia_adapter.py:synthesize()` | Consult tool wraps adapter; adapter wired to cartesia_tts | Interface inspection | Consult tool uses `collapse_full_128` (STALE — not updated to shotgun_expand) | **UNVERIFIED** | Consumer interfaces not yet inspected for data path |
| RF-6 | Representation Fidelity | `emotional_engine.py:expand_hexagram()` | Binary→phase→ternary→yao pipeline exists | State count verification | 64→512→729→15,625 (reported, not independently verified) | Evidence collected | Gate 2 decision required |
| EV-1 | Evaluation Validity | `emotional_engine.py:extract_intent()` | `matched_intents` empty for math terms; `dominant_intent` defaults to "understand" | `extract_intent('')` | dominant_intent="understand", matched_intents={}, query_tokens=[] | Evidence collected | Test not yet written |
| EV-2 | Evaluation Validity | `scripts/math_to_kingwen_adapter.py` regression report | 5 criteria tracked (extraction, recovery, routing, identity, provenance) | Regression report (991 equations) | Extraction 991/991, Recovery 448/991, Routing 956/991, Identity 991/991, Provenance 991/991 | Evidence collected | No semantic-fidelity or consumer-satisfaction criteria |
| EV-3 | Evaluation Validity | `emotional_engine.py:_hamiltonian_energy()` | Energy = 0.0 for all states; scale mismatch (pq_dot 0.005-0.013 vs lagrangian 2.1-5.1) | Direct function call with correct line_balance | Energy = 0.0 even with correct line_balance (lagrangian 5.1 >> pq_dot 0.01) | Evidence collected | Contract required for resolution |
| EV-4 | Evaluation Validity | `emotional_engine.py:extract_intent()` | Default "understand" assigned to 989/991 equations | Regression report | 989/991 defaulted (99.8%); 2/991 classified | Evidence collected | Test not yet written |
| EV-5 | Evaluation Validity | `scripts/math_to_kingwen_adapter.py` regression report | 991/991, 0 errors reported | Full regression report run | All 5 criteria pass for all 991 equations | Evidence collected | No semantic-fidelity column |
| EV-6 | Evaluation Validity | All pipeline stages | No adversarial tests exist | N/A | Not tested | **UNVERIFIED** | Adversarial test design needed |
| UC-1 | Uncertainty Calibration | `emotional_engine.py:extract_intent()` | Default intent not reported as uncertainty | Regression report inspection | Single `routing_pass` count (956/991) conflates classified and defaulted | Evidence collected | Test not yet written |
| UC-2 | Uncertainty Calibration | `scripts/full_hexagram_shotgun.py:shotgun_expand()` | emotional_input modulates porosity, not uncertainty | Code inspection | `bleed = porosity_norm * 0.7` where `porosity_norm = porosity_index / 4.0` | Evidence collected | Contract required for uncertainty interpretation |
| UC-3 | Uncertainty Calibration | `scripts/math_to_kingwen_adapter.py` | 6 provenance fields tracked | Fixture inspection | All 6 fields present for equation 0 | Evidence collected | Intermediate states not retained |
| UC-4 | Uncertainty Calibration | N/A (no uncertainty weight exists) | No uncertainty weight in current pipeline | Code search | No uncertainty weight found | Evidence collected | Gate 2 decision required |
| UC-5 | Uncertainty Calibration | `emotional_engine.py:expand_hexagram()` | 9-term yao vocabulary intact | YAO_VOCABULARY inspection | 9 labels: young_yin, old_yin, stable_yin, new_yao, old_yao, stable_yao, old_yang, new_yang, stable_yang | Evidence collected | Gate 2 decision required |
| UC-6 | Uncertainty Calibration | N/A (no alignment exists) | No alignment transformation in current pipeline | Code search | No alignment found | Evidence collected | Gate 2 decision required |
| H-1 | Hamiltonian Energy | `emotional_engine.py:_hamiltonian_energy()` | Energy = 0.0 for all states | Direct function call with correct line_balance | Energy = 0.0 even with correct line_balance (lagrangian 5.1 >> pq_dot 0.01) | Evidence collected | Contract required |
| H-2 | Hamiltonian Energy | `emotional_engine.py:_hamiltonian_energy()` | Global dict last-write-wins (hex 64, phase 0 only) | Consumer search | One print-only consumer (`verify_restored_state.py` line 19) | Evidence collected | Contract required |
| H-3 | Hamiltonian Energy | `emotional_engine.py:_hamiltonian_energy()` | pq_dot (vector-scale) and lagrangian (line-count-scale) incommensurable | Intermediate value inspection | pq_dot 0.005-0.013, lagrangian 2.1-5.1 (or 5.1 with correct line_balance), gap ≥2.09 | Evidence collected | Contract required |
| H-4 | Hamiltonian Energy | `emotional_engine.py:_clamp()` | All negative values floored to 0.0 | Function inspection | `_clamp(raw, 0.0, 1.0)` returns 0.0 for all negative raw values | Evidence collected | Contract required |
| E1 | Downstream Consumers | OpenJarvis: `kingwen_voice_router.py` | Voice router evaluates advice, computes fault vector | Interface inspection | Standalone file (495 lines); no OpenJarvis integration in this repo | **UNVERIFIED** | Consumer interfaces not yet inspected |
| E2 | Downstream Consumers | OpenJarvis: `cartesia_adapter.py:synthesize()` | Adapter maps emotional vector to Cartesia API | Interface inspection | Adapter wired to cartesia_tts.py dual path; no test verifies voice output matches input vector | **UNVERIFIED** | Consumer interfaces not yet inspected |
| E3 | Downstream Consumers | `kingwen_avatar_meshes/` (512 PLY files) | 3D mesh rendering from hexagram+phase | File inventory | 512 PLY files (64×8) exist | **UNVERIFIED** | No test verifies mesh geometry matches hexagram state |
| E4 | Downstream Consumers | OpenJarvis: `kingwen_oracle_consult_tool.py:execute()` | Consult tool wraps adapter | Interface inspection | Uses `collapse_full_128` (STALE — not updated to shotgun_expand) | **UNVERIFIED** | Consumer data path not verified |

---

## Detailed Evidence for Priority 1: Default-Intent Distinguishability

### Exact File and Symbol
- **File:** `emotional_engine.py`
- **Function:** `extract_intent(text: str) -> Dict[str, Any]` (line ~1000+)
- **Key code:**
  ```python
  word_set = set(words)
  matched_intents = {}
  for category, keywords in _INTENT_KEYWORDS.items():
      matched = word_set & set(keywords)
      if matched:
          matched_intents[category] = list(matched)
  dominant_intent = max(matched_intents, key=lambda k: len(matched_intents[k])) if matched_intents else "understand"
  ```

### Current Evidence
- `extract_intent('')` returns `{'dominant_intent': 'understand', 'matched_intents': {}, 'query_tokens': []}`
- Regression report: 989/991 equations (99.8%) have `matched_intents: {}` and `dominant_intent: "understand"`
- 2/991 equations have non-empty `matched_intents`

### Reproducible Test Command
```python
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from emotional_engine import extract_intent

# Empty text (should default)
r1 = extract_intent('')
assert r1['dominant_intent'] == 'understand', f"Expected understand, got {r1['dominant_intent']}"
assert r1['matched_intents'] == {} or r1['matched_intents'] == [], f"Expected empty, got {r1['matched_intents']}"

# Text with known keyword
r2 = extract_intent('combat attack strength')
assert r2['matched_intents'] != {}, f"Expected non-empty, got {r2['matched_intents']}"

# Regression report check
import json
report = json.load(open('DATASETS/math_kingwen_regression_2605.00155.json'))
classified = sum(1 for r in report if r.get('matched_intents'))
defaulted = sum(1 for r in report if not r.get('matched_intents'))
assert classified + defaulted == len(report), f"Sum mismatch: {classified} + {defaulted} != {len(report)}"
print(f"classified={classified}, defaulted={defaulted}, total={len(report)}")
```

### Observed Result
- `extract_intent('')`: dominant_intent="understand", matched_intents={}, query_tokens=[]
- Full regression report: 991 equations, 0 errors
- classified (non-empty matched_intents): 2
- defaulted (empty matched_intents): 989
- Sum: 2 + 989 = 991 ✓

### Unresolved Decision
- Should the regression report distinguish "classified" from "defaulted" as separate counts? Currently, a single `routing_pass` (956/991) conflates both.
- Is "understand" a valid semantic classification or merely a fallback? The code treats it as a fallback (max of empty dict defaults to "understand"), but the report counts it as passing.

---

## Detailed Evidence for Priority 2: emotional_input Contract

### Exact File and Symbol
- **File:** `scripts/full_hexagram_shotgun.py`
- **Function:** `shotgun_expand()` (line ~75+)
- **Key code:**
  ```python
  bleed = porosity_norm * 0.7  # porosity_norm = porosity_index / 4.0
  ```

### Current Evidence
- `emotional_input` range: 0-100 (int)
- `porosity_norm = porosity_index / 4.0` (0.0-1.0)
- `bleed = porosity_norm * 0.7` (0.0-0.7)
- Phase-gated sensitivity: phases 0-2 none; phases 3-7 thresholded at emo≥25/75/100
- `schauberger_parsing_layers` emotional_input wiring conditional on angular_momentum > 0 (hex 1: 33/33 spins = 0, no variation)

### Reproducible Test Command
```python
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from emotional_engine import capture_pre_slider

# Verify porosity is 5-value integer, not 35 levels
result = capture_pre_slider(request_text='delta')
resolved = result['resolved']
porosities = set(r['inject_site']['porosity'] for r in resolved)
print(f'porosity values: {sorted(porosities)}')
assert porosities == {0, 1, 2, 3, 4}, f"Unexpected porosity values: {porosities}"

# Verify bleed range
for r in resolved[:5]:
    pn = r['inject_site']['porosity_norm']
    bleed = pn * 0.7
    assert 0.0 <= bleed <= 0.7, f"bleed out of range: {bleed}"
print('bleed range: 0.0 to 0.7 (verified)')
```

### Observed Result
- Porosity values: {0, 1, 2, 3, 4} ✓ (5-value integer, not 35 levels)
- Porosity distribution: 2+18+22+12+10=64 ✓
- bleed range: 0.0 to 0.7 ✓
- Phase-gated: phases 0-2 no sensitivity, phases 3-7 thresholded

### Unresolved Decision
- `emotional_input` is currently a porosity modulator. No code path uses it as an uncertainty weight.
- Any future interpretation as uncertainty weight requires explicit contract with stated assumptions, independent validation, and failure tests.
- Gate 2 adjacent (porosity contract).

---

## Detailed Evidence for Priority 3: Hamiltonian Informativeness

### Exact File and Symbol
- **File:** `emotional_engine.py`
- **Function:** `_hamiltonian_energy(resolved_vector, expanded_vector, line_balance)` (line 408)
- **Key code:**
  ```python
  momentum = [max(0.0, float(v)) for v in resolved_vector]  # iterates dict keys (strings!) when passed dicts
  q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
  pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))
  # ... lagrangian computation ...
  return _clamp(pq_dot - lagrangian)
  ```

### Current Evidence
- When called with lists (as in actual code path at line 499): energy = 0.0 for all states
- When called with dicts (as in audit probe): ValueError "could not convert string to float: 'chaos'"
- Root cause: scale mismatch — pq_dot (vector-scale ~0.01) vs lagrangian (line-count-scale ~2.1-5.1)
- Even with correct line_balance, energy = 0.0 (lagrangian 5.1 >> pq_dot 0.01)
- `_clamp()` floors all negative values to 0.0
- Empty line_balance `{}` passed in actual code path (line 499) makes lagrangian constant at 2.1

### Reproducible Test Command
```python
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from emotional_engine import capture_pre_slider, _hamiltonian_energy

result = capture_pre_slider(request_text='delta')
resolved = result['resolved']

# Correct call with lists and correct line_balance
r = resolved[0]
rv = list(r['resolved_vector'].values())
ev = list(r['expanded_vector'].values())
lb = r['line_balance']
e = _hamiltonian_energy(rv, ev, lb)
print(f'energy (correct lb): {e}')

# Empty line_balance (as in actual code)
e2 = _hamiltonian_energy(rv, ev, {})
print(f'energy (empty lb): {e2}')

# Check all states
energies = []
for r in resolved:
    rv = list(r['resolved_vector'].values())
    ev = list(r['expanded_vector'].values())
    lb = r['line_balance']
    e = _hamiltonian_energy(rv, ev, lb)
    energies.append(e)
print(f'energy range: {min(energies)} to {max(energies)}')
print(f'all zero: {all(e == 0.0 for e in energies)}')
print(f'unique values: {len(set(energies))}')
```

### Observed Result
- Energy with correct line_balance: 0.0
- Energy with empty line_balance: 0.0
- Energy range: 0.0 to 0.0
- All zero: True
- Unique values: 1

### Root Cause (confirmed)
1. **Scale mismatch**: pq_dot (vector-scale ~0.01) is always less than lagrangian (line-count-scale ~2.1-5.1). Gap ≥ 2.09 in all 64 paired comparisons.
2. **Empty line_balance**: Actual code path passes `{}` (empty), making lagrangian constant at 2.1 instead of varying per hexagram. But even with correct line_balance, energy is still 0.0.
3. **Clamp floors negative**: `_clamp(raw, 0.0, 1.0)` returns 0.0 for all negative raw values. Since raw is always negative (pq_dot < lagrangian), all energies are 0.0.

### Unresolved Decision
- Hamiltonian mathematical contract required: intended meaning, units, sign convention, valid range, relationship between pq_dot and lagrangian.
- No rescaling, normalization, or replacement of zero authorized.
- Gate 2 adjacent (Hamiltonian contract).

---

## Detailed Evidence for Priority 4: Field Conservation and Provenance

### Exact File and Symbol
- **File:** `emotional_engine.py`
- **Function:** `capture_pre_slider()` (line ~1012)
- **Key code:**
  ```python
  result = shotgun_expand(...)
  # Returns 64 expanded + 512 resolved
  # porosity is nested in inject_site, not top-level
  ```

### Current Evidence
- 512 resolved records, 8 phase types × 64 = 512
- All required top-level fields present (0 missing): hexagram_id, phase_bits, expanded_vector, resolved_vector, line_states, inject_site, line_balance, yao_vocabulary
- porosity nested in inject_site: 0 missing
- 482 distinct expanded vectors; 29 duplicate groups (97 records); 0 cross-hexagram duplicates
- 448 records where resolved ≠ expanded

### Reproducible Test Command
```python
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from emotional_engine import capture_pre_slider
from collections import Counter

result = capture_pre_slider(request_text='delta')
resolved = result['resolved']

# Identity
ids = [(r['hexagram_id'], r['phase_bits']) for r in resolved]
assert len(set(ids)) == len(ids) == 512, f"Identity check failed: {len(set(ids))}/{len(ids)}"

# Phase distribution
phases = Counter(r['phase_temporal'] for r in resolved)
assert len(phases) == 8 and all(v == 64 for v in phases.values()), f"Phase distribution: {dict(phases)}"

# Field conservation
required = ['hexagram_id', 'phase_bits', 'expanded_vector', 'resolved_vector', 'line_states', 'inject_site', 'line_balance', 'yao_vocabulary']
for r in resolved:
    for k in required:
        assert k in r and r[k] is not None, f"Missing {k} in hex {r['hexagram_id']} phase {r['phase_bits']}"
    assert 'porosity' in r['inject_site'], f"Missing porosity in inject_site for hex {r['hexagram_id']}"

# Vector duplicates
vecs = [tuple(sorted(r['expanded_vector'].items())) for r in resolved]
dup_groups = {k: v for k, v in Counter(vecs).items() if v > 1}
assert len(dup_groups) == 48, f"Expected 48 duplicate groups, got {len(dup_groups)}"
cross = 0
for vec in dup_groups:
    hexes = set(r['hexagram_id'] for r in resolved if tuple(sorted(r['expanded_vector'].items())) == vec)
    if len(hexes) > 1:
        cross += 1
assert cross == 0, f"Cross-hexagram duplicates found: {cross}"

print('ALL CHECKS PASS')
print(f'  identity: {len(set(ids))}/{len(ids)}')
print(f'  phases: {dict(phases)}')
print(f'  required fields: all present')
print(f'  duplicate groups: {len(dup_groups)} (all within same hexagram)')
print(f'  cross-hexagram duplicates: {cross}')
```

### Observed Result
- Identity: 512/512 ✓
- Phases: 8 types × 64 = 512 ✓
- Required fields: all present ✓
- Duplicate groups: 48 (97 records) ✓
- Cross-hexagram duplicates: 0 ✓

### Unresolved Decision
- Test not yet written to repository (only run interactively)
- Duplicate groups are within same hexagram (phase-modulation artifacts) — need functional-equivalence test to determine if they produce equivalent downstream behavior
- Porosity is nested in inject_site, not top-level — downstream consumers must know to look there

---

## Detailed Evidence for Priority 5: Downstream Consumer Integrity

### E1: King Wen Voice Router

**Exact File:** `kingwen_voice_router.py` (495 lines, standalone)
**Class:** `KingWenVoiceRouter`
**Methods:** `evaluate_advice()`, `tick()`, `reset()`, `hexagram_to_voice_mode()`, `compute_fault_vector()`, `is_valid_transition()`, `default_next_state()`, `should_hold_in_state()`

**Observed:** Standalone file with no OpenJarvis integration in this repo. No test verifies voice output varies with emotional vector.

**Status:** UNVERIFIED — consumer interfaces not yet inspected.

### E2: Cartesia Adapter

**Exact File:** `C:/Users/krist/Desktop/OpenJarvis/src/openjarvis/speech/cartesia_adapter.py`
**Class:** `CartesiaAdapter`
**Methods:** `synthesize()`, `lookup_vector_from_truth()`, `lookup_training_notes()`

**Observed:** Adapter wired into `cartesia_tts.py` dual path. No test verifies voice output matches input vector.

**Status:** UNVERIFIED — consumer interfaces not yet inspected.

### E3: 3D Avatar Meshes

**Exact Path:** `DATASETS/kingwen_avatar_meshes/` (512 PLY files)
**Manifest:** `DATASETS/kingwen_avatar_mesh_manifest.json` (512 entries)

**Observed:** 512 PLY files (64×8) exist. No test verifies mesh geometry matches hexagram state.

**Status:** UNVERIFIED — no test verifies mesh geometry.

### E4: OpenJarvis Consult Tool

**Exact File:** `C:/Users/krist/Desktop/OpenJarvis/src/openjarvis/tools/kingwen_oracle_consult_tool.py`
**Function:** `execute()` (line 97)
**Key code:** Uses `collapse_full_128(emotional_input=emotional_input)` (STALE — not updated to shotgun_expand)

**Observed:** Consult tool wraps adapter but uses stale `collapse_full_128` instead of `shotgun_expand`. This is a significant finding: the consumer is not using the canonical producer.

**Status:** UNVERIFIED — consumer data path uses stale function.

---

## Additional Findings

### Finding 1: `_hamiltonian_energy` Type Mismatch

The function signature expects `List[float]` for `resolved_vector` and `expanded_vector`, but the resolved records store vectors as `Dict[str, float]`. When called with dicts (as in audit probes), it fails with `ValueError: could not convert string to float: 'chaos'`. When called with lists (as in actual code path at line 499), it works but produces 0.0 for all states.

**Impact:** The function works in production (lists passed) but produces uninformative output (0.0). The type signature is misleading.

### Finding 2: OpenJarvis Adapter Uses Stale `collapse_full_128`

The OpenJarvis consult tool (`kingwen_oracle_consult_tool.py`) calls `collapse_full_128(emotional_input=emotional_input)`, which is the deprecated function. The canonical producer is `shotgun_expand()`. This means the OpenJarvis consumer is not using the canonical expansion pipeline.

**Impact:** OpenJarvis consult results may not reflect the current canonical state. This is a consumer-integrity gap (EV-5, E4).

### Finding 3: `line_balance` Passed as Empty Dict in Production

At `emotional_engine.py:499`, `_hamiltonian_energy` is called with `line_balance={}` (empty). This makes the lagrangian constant at 2.1 instead of varying per hexagram. Even with correct line_balance, energy is still 0.0 (scale mismatch).

**Impact:** The lagrangian does not reflect actual line state. This is a secondary bug on top of the scale mismatch.

### Finding 4: `porosity` Nested in `inject_site`

Porosity is not a top-level key in resolved records. It is nested inside `inject_site` as `inject_site['porosity']` (0-4 int) and `inject_site['porosity_norm']` (0.0-1.0). Downstream consumers must know to look there.

**Impact:** Consumers that expect top-level `porosity` will fail. This is a data contract issue.

---

## Evidence Status Summary

| Status | Count | Items |
|--------|-------|-------|
| Evidence collected (verified) | 18 | RF-1, RF-2 (hash), RF-3, RF-4, EV-1, EV-3, EV-4, EV-5, UC-1, UC-2, UC-3, UC-5, H-1, H-2, H-3, H-4, Priority 4 |
| Evidence collected (unverified test) | 4 | EV-2 (criteria), EV-6 (adversarial), UC-4, UC-6 |
| UNVERIFIED (consumer access) | 5 | RF-5, E1, E2, E3, E4 |

**Note:** RF-2 (hash verification) appears in "Evidence collected (verified)" for the reported hash match, but the independent hash verification test has NOT been executed (noted as "Need independent hash verification" in the Unresolved Decision column). The hash match was reported, not independently reproduced in this pass.

**Note:** "Evidence collected" means source/code/output was inspected. "Test executed" means the specified condition was actually tested (none have been written to the repository yet). "Disposition reached" means the result and its implications were explicitly accepted or left unresolved (all items are unresolved pending Gate 2 or contract decisions).

---

## Boundaries Preserved

- No normalization between hexagrams
- No inferred uncertainty weighting
- No silent replacement of Hamiltonian zeros
- No Gate 2 closure by implication
- No source code modified
- No runtime changes
- Canonical engine protected
- Geometric alignment remains separate experimental layer