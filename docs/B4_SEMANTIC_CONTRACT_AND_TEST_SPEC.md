# B4 Semantic Contract and Exhaustive Test Specification

**Status**: OPEN — Gate 2 not closed
**Date**: 2026-10-28
**Auditor**: Kirby (Hermes agent)
**Attribution**: Evidence matrix results reported by auditor; not independently reproduced in this turn

---

## 1. Canonical State Model

### Current State (Unresolved)

| Representation | Space | Cardinality | Implementation Status |
|----------------|-------|-------------|----------------------|
| Binary identity | `{0,1}⁶` | 64 | **CANONICAL** — `HEXAGRAM_BASE[hex_id]["binary_bottom_to_top"]` |
| Phase-expanded | `64 × 8` | 512 | **IMPLEMENTED** — `expand_hexagram()` produces 8 phases per hexagram |
| Ternary lines | `{0,1,2}⁶` | 729 | **PARTIAL** — runtime produces ternary_state ∈ {0,1,2} per line, but only 512 of 729 configurations reachable |
| Five-valued differential | `{0,1,2,3,4}⁶` | 15,625 | **DOCUMENTED ONLY** — described in `ternary-paired-differential-math-correction-2026-08-02.md`; no runtime implementation |

### Design Decision Required

**The canonical representation must be explicitly designated.** Current candidates:

- **Option 1 (Binary-first)**: Binary identity is canonical; phase-expanded is derived; ternary is an intermediate computation; five-valued is aspirational
- **Option 2 (Ternary-first)**: Ternary state space is canonical; binary is a projection; five-valued is an enrichment
- **Option 3 (Dual-track)**: Binary and ternary coexist as separate representations with explicit conversion

**No decision recorded.** Gate 2 cannot close until this is resolved and documented here.

---

## 2. Transformation Contracts

### 2.1 Binary Identity → Phase-Expanded

**Producer**: `expand_hexagram(hexagram_id, request_text, phase_bits, emotional_input)`  
**Location**: `emotional_engine.py:785-900`

**Inputs**:
- `hexagram_id: int` — 1..64
- `phase_bits: int` — 0..7 (selects one of 8 phase patterns)
- `request_text: str` — intent extraction input
- `emotional_input: int | None` — 0..100 slider

**Output**: Dictionary containing:
```python
{
    "hexagram_id": int,
    "phase_bits": int,              # 0..7
    "phase_temporal": str,          # from PHASE_INFO[phase_bits]["temporal"]
    "hexagram_symbols": {...},      # includes binary_bottom_to_top, binary_top_to_bottom
    "line_states": [                # 6 entries, position 1..6 (bottom to top)
        {
            "position": int,        # 1=bottom, 6=top
            "ternary_state": int,   # 0, 1, or 2
            "yao_key": str,         # one of 9 labels
            "yao_label": str        # human-readable
        }
    ],
    "inject_site": {...},           # porosity, pool names, etc.
    "expanded_vec": [float]*5,      # 5-axis emotional vector
    ...
}
```

**Phase Semantics** (from `PHASE_LINE_MAP` and `PHASE_INFO`):

| phase_bits | changing_positions | temporal | polarity | description |
|------------|-------------------|----------|----------|-------------|
| 0 | [] | past | yin | completed, resolved, memory |
| 1 | [1,4] | present | yang | active, manifest, now |
| 2 | [2,5] | future | yao | potential, emerging, becoming |
| 3 | [1,2,4,5] | transition | yin-yang | changing, flux, threshold |
| 4 | [3,6] | resolution | yang-yin | settling, clarity, convergence |
| 5 | [1,3,4,6] | dissolution | yin-yao | breaking, releasing, dispersal |
| 6 | [2,3,5,6] | crystallization | yang-yao | forming, condensing, structure |
| 7 | [1,2,3,4,5,6] | void | yao-yao | null, reset, origin |

**Line Orientation**: `position 1 = bottom line (initial)`, `position 6 = top line (governing)` — confirmed by `binary_bottom_to_top` ordering and iteration order in `expand_hexagram()`.

**Contract**: All 64 hexagrams × 8 phases = 512 unique states. No collisions. Binary identity preserved in `hexagram_symbols.binary_bottom_to_top`.

---

### 2.2 Binary → Ternary Line State

**Producer**: `expand_hexagram()` lines 836-864

**Transformation**:
```python
changing_positions = PHASE_LINE_MAP[phase_bits]  # list of 1-indexed line positions
base_ternary = HEXAGRAM_BASE[hexagram_id]["binary_bottom_to_top"]  # string "010101"

for idx, bit in enumerate(base_ternary):
    line_pos = idx + 1
    ternary_state = 2 if line_pos in changing_positions else int(bit)
    yao_key = _line_yao_key(ternary_state, temporal)
```

**Contract**:
- Unchanged lines: `ternary_state = int(binary_bit)` → 0 (yin) or 1 (yang)
- Changing lines: `ternary_state = 2` (yao) — **regardless of original binary value**
- `changing_positions` comes exclusively from `PHASE_LINE_MAP[phase_bits]`
- No other source of ternary_state = 2 exists in current runtime

**Reversibility**: **Lossy**. When `ternary_state = 2`, the original binary polarity (0 or 1) is discarded. The `yao_key` encodes temporal frame but not original polarity.

**Verified Loss Example** (Hexagram 3 vs 4, Phase 1):
- Hex 3 (binary `010001`): line 1 was yang(1) → ternary=2, yao=stable_yao; line 4 was yin(0) → ternary=2, yao=stable_yao
- Hex 4 (binary `100010`): line 1 was yin(0) → ternary=2, yao=stable_yao; line 4 was yang(1) → ternary=2, yao=stable_yao
- **Both produce identical `ternary_state=2, yao_key=stable_yao` for the changing lines** — original yin/yang polarity is not preserved anywhere in output.

**Exact Fields Lost**: The `binary_bit` value (0 or 1) for positions in `changing_positions`. Input field: `base_ternary[idx]` (the original binary character). Output: constant `ternary_state=2`. No field in `line_states` preserves the original bit.

---

### 2.3 Ternary + Temporal → Yao Label

**Producer**: `_line_yao_key(ternary_state: int, temporal: str) → str`  
**Location**: `emotional_engine.py:79-94`

**Input Contract**:
- `ternary_state ∈ {0, 1, 2}`
- `temporal ∈ {"past", "present", "future", "transition", "resolution", "dissolution", "crystallization", "void"}`

**Output**: One of 9 labels from `YAO_VOCABULARY`:

| ternary_state | temporal | yao_key |
|---------------|----------|---------|
| 0 (yin) | past | old_yin |
| 0 | present | stable_yin |
| 0 | future/transition/resolution/dissolution/crystallization/void | young_yin |
| 1 (yang) | past | old_yang |
| 1 | present | stable_yang |
| 1 | future/transition/resolution/dissolution/crystallization/void | new_yang |
| 2 (yao) | past | old_yao |
| 2 | present | stable_yao |
| 2 | future/transition | new_yao |
| 2 | resolution/dissolution/void | old_yao |
| 2 | crystallization | stable_yao |

**Exhaustive Coverage**: 3 ternary states × 8 temporal frames = 24 combinations. All produce valid labels. **No invalid-input branch raises** — invalid ternary_state and invalid temporal silently fall through to default branches.

**Actual Runtime Behavior** (tested):
- `_line_yao_key(3, "past")` → `"stable_yang"` (falls through to final `return "stable_yang"`)
- `_line_yao_key(0, "invalid_temporal")` → `"young_yin"` (falls through to `return "young_yin"`)

**Contract vs Implementation Gap**: The function **does not reject invalid inputs**. It uses fall-through logic that produces a valid-looking label for any input. This violates the "no silent defaults" requirement.

**Temporal Collapse Verified**:
- yin (0): 8 temporals → 3 labels (old_yin, stable_yin, young_yin)
- yang (1): 8 temporals → 3 labels (old_yang, stable_yang, new_yang)
- yao (2): 8 temporals → 3 labels (old_yao, stable_yao, new_yao)

**Exact Fields Lost**: Fine-grained temporal distinction. Input: 8 distinct temporal frames. Output: 3 label categories per ternary state. The `phase_temporal` field in the parent record preserves the original temporal, but the per-line `yao_key` does not.

---

### 2.4 Ternary → Five-Valued Differential

**Status**: **NO RUNTIME IMPLEMENTATION**

**Documented Model** (from `ternary-paired-differential-math-correction-2026-08-02.md`):
- Values: 0=stable_yin, 1=yang, 2=old_yin, 3=old_yang, 4=active_changing/yao
- Space: 5⁶ = 15,625 configurations
- Signed differentials: dy, yao_dy, changing_dy, old_dy, stable_dy

**Conversion Contract**: **Undefined**. No function in source tree maps:
- `(ternary_state, temporal, binary_polarity) → five-valued`
- Or any equivalent transformation

**Required if Path A chosen**: Explicit function with defined semantics for all 3×8×2 = 48 input combinations, proving which information is preserved/lost.

---

## 3. Information-Preservation Analysis

| Transformation | Reversible? | Information Lost | Exact Fields Lost |
|----------------|-------------|------------------|-------------------|
| Binary → Phase-expanded | Yes (by hexagram_id) | None | Phase is additive metadata |
| Binary → Ternary | **No** | Original polarity of changing lines | `binary_bit` value when `line_pos ∈ changing_positions` — the 0/1 is replaced by constant 2 |
| Ternary → Yao Label | **No** | Fine-grained temporal distinctions | 8 temporals collapsed to 3 label categories per ternary state (e.g., future/transition/resolution/dissolution/crystallization/void → young_yin) |
| Ternary → Five-valued | N/A | N/A | Not implemented |
| Yao Label → Binary | **No** | Original binary, phase, temporal | Many-to-one mapping; no reverse lookup possible |

**Intentional Loss Points** (require explicit documentation):
1. **Changing-line original polarity** → lost at binary→ternary boundary. Input field: `binary_bit` (0 or 1) for positions in `changing_positions`. Output: constant `ternary_state=2`. No field in `line_states` preserves the original bit.
2. **Fine-grained temporal distinctions** → collapsed at ternary→yao boundary. Input: 8 distinct temporal frames. Output: 3 label categories per ternary state. The `phase_temporal` field in the parent record preserves the original temporal, but the per-line `yao_key` does not.
3. **Five-valued differential model** → entirely absent from runtime.

---

## 4. Exhaustive Verification Specification

### 4.1 Test: Binary → Phase-Expanded (512 States)

**Test Function**: `test_binary_phase_expanded_exhaustive()`

**Expected Result**: All assertions pass. 512 states, unique (hex_id, phase_bits), 8 per hexagram, binary preserved.

**Failure Condition**: Any assertion fails (wrong count, collision, missing phase, binary mismatch).

```python
def test_binary_phase_expanded_exhaustive():
    states = []
    for hex_id in range(1, 65):
        for phase in range(8):
            r = expand_hexagram(hex_id, "", phase_bits=phase)
            states.append(r)
    
    assert len(states) == 512
    keys = [(s['hexagram_id'], s['phase_bits']) for s in states]
    assert len(set(keys)) == 512
    
    from collections import Counter
    counts = Counter(s['hexagram_id'] for s in states)
    assert all(c == 8 for c in counts.values())
    
    for s in states:
        hid = s['hexagram_id']
        binary = s['hexagram_symbols']['binary_bottom_to_top']
        expected = HEXAGRAM_BASE[hid]['binary_bottom_to_top']
        assert binary == expected, f"hex {hid}: {binary} != {expected}"
```

---

### 4.2 Test: Binary → Ternary Line States

**Test Function**: `test_binary_ternary_mapping_exhaustive()`

**Expected Result**: No mismatches across all 512 × 6 = 3,072 line positions. Changing lines → ternary=2; unchanged lines → int(binary_bit).

**Failure Condition**: Any line position violates the mapping rule.

```python
def test_binary_ternary_mapping_exhaustive():
    for hex_id in range(1, 65):
        for phase in range(8):
            r = expand_hexagram(hex_id, "", phase_bits=phase)
            binary = r['hexagram_symbols']['binary_bottom_to_top']
            changing = PHASE_LINE_MAP[phase]
            
            for ls in r['line_states']:
                pos = ls['position']
                ternary = ls['ternary_state']
                
                if pos in changing:
                    assert ternary == 2, f"hex {hex_id} ph {phase} pos {pos}: changing but ternary={ternary}"
                else:
                    expected = int(binary[pos-1])
                    assert ternary == expected, f"hex {hex_id} ph {phase} pos {pos}: {ternary} != {expected}"
```

**Verified Loss Check**: This test does NOT assert preservation of original polarity for changing lines — that loss is intentional and documented.

---

### 4.3 Test: Ternary + Temporal → Yao Label

**Test Function**: `test_yao_label_exhaustive()`

**Expected Result**: All 24 valid combinations match the contract table. **Invalid inputs do NOT raise** — they produce fall-through labels (current implementation behavior).

**Failure Condition**: Valid combination produces wrong label.

```python
def test_yao_label_exhaustive():
    expected = {
        (0, "past"): "old_yin", (0, "present"): "stable_yin",
        (0, "future"): "young_yin", (0, "transition"): "young_yin",
        (0, "resolution"): "young_yin", (0, "dissolution"): "young_yin",
        (0, "crystallization"): "young_yin", (0, "void"): "young_yin",
        (1, "past"): "old_yang", (1, "present"): "stable_yang",
        (1, "future"): "new_yang", (1, "transition"): "new_yang",
        (1, "resolution"): "new_yang", (1, "dissolution"): "new_yang",
        (1, "crystallization"): "new_yang", (1, "void"): "new_yang",
        (2, "past"): "old_yao", (2, "present"): "stable_yao",
        (2, "future"): "new_yao", (2, "transition"): "new_yao",
        (2, "resolution"): "old_yao", (2, "dissolution"): "old_yao",
        (2, "crystallization"): "stable_yao", (2, "void"): "old_yao",
    }
    
    for (ts, temp), expected_key in expected.items():
        actual = _line_yao_key(ts, temp)
        assert actual == expected_key, f"({ts}, {temp}): {actual} != {expected_key}"
    
    # Invalid inputs currently produce fall-through labels (not raises)
    # Documenting current behavior — DECISION NEEDED on whether this is acceptable:
    assert _line_yao_key(3, "past") == "stable_yang"  # fall-through
    assert _line_yao_key(0, "invalid") == "young_yin"  # fall-through
```

**Contract Decision Needed**: Should invalid inputs raise, or is fall-through behavior accepted? Current implementation = fall-through.

---

### 4.4 Test: Determinism

**Test Function**: `test_determinism()`

**Expected Result**: Identical inputs produce identical outputs for all sampled states.

**Failure Condition**: Any non-deterministic output.

```python
def test_determinism():
    for hex_id in [1, 2, 30, 64]:
        for phase in [0, 1, 3, 7]:
            r1 = expand_hexagram(hex_id, "test query", phase_bits=phase, emotional_input=50)
            r2 = expand_hexagram(hex_id, "test query", phase_bits=phase, emotional_input=50)
            assert r1 == r2, f"Non-deterministic: hex {hex_id} phase {phase}"
```

---

### 4.5 Test: Identity Preservation (No Cross-Hexagram Normalization)

**Test Function**: `test_no_cross_hexagram_normalization()`

**Expected Result**: Emotional vectors show meaningful per-hexagram variation (variance > 0.001 on all 5 axes).

**Failure Condition**: Vectors collapsed to same values across hexagrams.

```python
def test_no_cross_hexagram_normalization():
    vectors = {}
    for hex_id in range(1, 65):
        r = expand_hexagram(hex_id, "", phase_bits=0, emotional_input=50)
        vectors[hex_id] = r['expanded_vec']
    
    import numpy as np
    vec_array = np.array(list(vectors.values()))
    variances = np.var(vec_array, axis=0)
    assert all(v > 0.001 for v in variances), "Vectors collapsed to same values across hexagrams"
```

---

### 4.6 Test: Fallback Context Analysis

**Test Function**: `test_fallback_context()`

**Purpose**: Distinguish canonical-path fallbacks (non-contract-compliant) from optional-path fallbacks.

**Expected Result**: Fallbacks in `_tau_for_resolved()` and `_compute_consensus_from_resolved()` are flagged as consumer-side; `porosity_window = 0.35` is a local constant, not a data fallback.

**Failure Condition**: Canonical path uses `.get(key, default)` for required fields.

```python
def test_fallback_context():
    # Line 1046: _tau_for_resolved() - CONSENSUS CALCULATION, not canonical path
    # This is a downstream consumer that tolerates missing data for robustness
    # FLAGGED: should use direct access in canonical path, fallback only in consumers
    
    # Line 1108-1111: _compute_consensus_from_resolved() - CONSENSUS CALCULATION
    # FLAGGED: same rationale
    
    # Line 1177: porosity_window = 0.35 - LOCAL CONSTANT, not a fallback
    # This is a filter threshold constant, not a data substitution
    # ACCEPTABLE: constant default for algorithm parameter
    
    # Canonical path checks (expand_hexagram output):
    for hex_id in range(1, 65):
        r = expand_hexagram(hex_id, "", phase_bits=0, emotional_input=50)
        inj = r['inject_site']
        # These MUST be present (direct access in canonical producer)
        assert 'porosity' in inj
        assert 'primary_pool' in inj
        assert 'secondary_pool' in inj
```

**Call-Site Context Summary**:

| Location | Function | Purpose | Contract Compliance |
|----------|----------|---------|---------------------|
| 1046 | `_tau_for_resolved()` | Consensus tau calculation | **Non-canonical** — consumer fallback, acceptable if documented |
| 1108-1111 | `_compute_consensus_from_resolved()` | Consensus statistics | **Non-canonical** — consumer fallback, acceptable if documented |
| 1177 | `porosity_window = 0.35` | Filter threshold constant | **Acceptable** — algorithm parameter, not data fallback |
| expand_hexagram output | Canonical producer | Must have all required fields | **Must use direct access** — no `.get(key, default)` |

---

## 5. Failure Semantics

| Failure Mode | Current Behavior | Required Behavior |
|--------------|------------------|-------------------|
| `hexagram_id` not in 1..64 | `KeyError` from `HEXAGRAM_BASE` | Raise `ValueError` / `KeyError` |
| `phase_bits` not in 0..7 | `KeyError` from `PHASE_LINE_MAP`/`PHASE_INFO` | Raise `ValueError` / `KeyError` |
| `ternary_state` not in {0,1,2} | **Silent fall-through** → returns `"stable_yang"` | **DECISION NEEDED**: Raise or document fall-through |
| `temporal` not in 8 valid frames | **Silent fall-through** → returns default for ternary_state | **DECISION NEEDED**: Raise or document fall-through |
| `HEXAGRAM_BASE[hex_id]` missing | `KeyError` | Raise `KeyError` |
| `PHASE_LINE_MAP[phase_bits]` missing | `KeyError` | Raise `KeyError` |
| `inject_site.porosity` missing | Fallback to 0.35 in consumers | Canonical producer must include; consumers may fallback |

**Key Finding**: `_line_yao_key()` currently **does not reject invalid inputs** — it has silent fall-through behavior. The contract must explicitly decide: raise on invalid input, or document fall-through as accepted behavior.

---

## 6. Gate Decision Record

### Path A — Implement Five-Valued Model

| Requirement | Status |
|-------------|--------|
| Define 5-valued alphabet semantics | Documented in `ternary-paired-differential-math-correction-2026-08-02.md` |
| Define ternary+temporal → five-valued conversion | **MISSING** |
| Prove information preservation | **NOT DEMONSTRATED** |
| Update all 15+ consumers | **NOT SCOPED** |
| Exhaustive tests for 15,625 space | **NOT DESIGNED** |
| Maintain binary identity preservation | **UNVERIFIED** |

**Risk**: Conflates documented model with runtime; may introduce silent information loss at ternary→five-valued boundary.

---

### Path B — Reconcile Documentation

| Requirement | Status |
|-------------|--------|
| Mark five-valued model as aspirational/conceptual | **NOT DONE** |
| Document runtime canonical representation (binary→phase→ternary→yao) | **PARTIAL** (this contract) |
| Preserve historical document with audit trail | **REQUIRED** |
| Update cross-references in 15+ consumer scripts | **NOT SCOPED** |
| Close semantic gap explicitly | **THIS CONTRACT** |

**Risk**: Documentation drift if not maintained; five-valued model may be needed for future hardware (VHDL) parity.

---

### Decision Required

**Explicit authorization required before either path is implemented.**

| Decision | Authorized By | Date |
|----------|---------------|------|
| Canonical representation | [PENDING] | |
| Path A or Path B (or hybrid) | [PENDING] | |
| Invalid-input behavior for `_line_yao_key()` | [PENDING] | |
| Information-loss budget | [PENDING] | |
| Test suite implementation | [PENDING] | |

---

## 7. Attribution and Reproduction

**Evidence matrix results** in this document were produced by auditor verification on 2026-10-28 against `emotional_engine.py`, `kingwen_ternary_tables_complete.py`, and `collapse_full_128_output.json` (stale). They have **not been independently reproduced** in this session.

**To reproduce**:
1. Run `expand_hexagram()` for all 64×8 combinations
2. Verify `PHASE_LINE_MAP` and `PHASE_INFO` match tables above
3. Exhaustively test `_line_yao_key(ternary_state, temporal)` for 24 combinations
4. Trace all consumer scripts listed in Section 2.4
5. Confirm no five-valued conversion exists in runtime

**Stale Artifact Warning**: `collapse_full_128_output.json` on disk was generated by deprecated pipeline and does not match current `expand_hexagram()` output. Use live function calls only.

---

## 8. Sign-Off

This contract does not close Gate 2. Gate 2 closes only when:

- [ ] Canonical representation explicitly designated (Section 1)
- [ ] Path A or Path B authorized with full implementation + tests
- [ ] All tests in Section 4 pass against current runtime
- [ ] Failure semantics in Section 5 resolved (invalid-input decision for `_line_yao_key()`)
- [ ] Decision record in Section 6 completed with signatures

**Next Action**: Await explicit authorization on canonical representation, path selection, and invalid-input semantics.
