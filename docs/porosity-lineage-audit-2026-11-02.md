# L2 — Porosity Field-Level Lineage Audit

## Scope

Read-only investigation. No source changes, no commits, no remediation acceptance.
Investigates the complete lifecycle of porosity from definition through production, serialization, import, transformation, consumption, and export.

## 1. Producer

### 1.1 Canonical source

- **File**: `emotional_engine.py` (HEXAGRAM_INJECTION_SITE, imported from `kingwen_ternary_tables_complete.py` or similar)
- **Type**: `Dict[int, Dict[str, Any]]` keyed by hexagram_id (1-64)
- **Field**: `inject_site["porosity"]` — integer 0-4 (structural porosity per hexagram topology)
- **Example**: Hex 1 → porosity=1, Hex 64 → porosity=3

### 1.2 Production path

```
_pool_weights_for_hex(hex_id, intent, phase_bits, emotional_input)
  ├── base_porosity = float(HEXAGRAM_INJECTION_SITE[hex_id]["porosity"])  # 0-4 int
  ├── slider_factor = _clamp(emotional_input / 100.0)  # 0.0-1.0
  ├── phase_overdrive = _clamp(phase_bits / 8.0) * (0.5 + slider_factor * 0.5)  # 0.0-0.875
  ├── porosity_score = _clamp(base_porosity / 4.0 + phase_overdrive * 0.5)  # 0.0-1.0
  ├── porosity_index = int(porosity_score * 4.0)  # 0-4
  ├── porosity_index = min(porosity_index, 4)
  ├── porosity_meta = POROSITY_LEVELS[porosity_index]
  ├── porosity_norm = porosity_index / 4.0  # 0.0, 0.25, 0.5, 0.75, 1.0
  └── inject["porosity"] = porosity_index  # int 0-4
      inject["porosity_norm"] = porosity_norm  # float 0.0-1.0
      inject["porosity_label"] = porosity_meta["label"]
      inject["porosity_window"] = porosity_meta["window"]
      inject["porosity_description"] = porosity_meta["description"]
```

### 1.3 shotgun_expand() integration

- **Expanded (64 states, phase=0)**: `base = expand_hexagram(h_id, ..., phase_bits=0, ...)`
  - `inject = base.get("inject_site") or {}`
  - Stores: `inject_site` (full dict including porosity, porosity_norm, porosity_label, etc.)
- **Resolved (512 states, phase=0-7)**: `r_base = expand_hexagram(h_id, ..., phase_bits=p, ...)`
  - Same inject_site structure, but porosity_index varies by phase (phase_overdrive)

### 1.4 Key production characteristics

| Characteristic | Value |
|---|---|
| Canonical porosity (injection site) | Integer 0-4 (structural topology) |
| Phase-modulated porosity (inject_site.porosity) | Integer 0-4 (canonical + phase overdrive) |
| Phase-modulated porosity_norm | Float 0.0, 0.25, 0.5, 0.75, 1.0 |
| Expanded porosity distribution | {0: 2, 1: 18, 2: 22, 3: 12, 4: 10} |
| Resolved porosity by phase | Phase 0-5: all 5 values; Phase 6-7: missing 0 (void phase) |
| emotional_input effect | Modulates phase_overdrive (slider_factor) |
| base_porosity source | HEXAGRAM_INJECTION_SITE (immutable tables) |

### 1.5 Three independent porosity computations

| # | Computation | Scale | Source | Location |
|---|---|---|---|---|
| 1 | Injection site porosity | Integer 0-4 | HEXAGRAM_INJECTION_SITE (immutable tables) | `_pool_weights_for_hex()` line 651 |
| 2 | Phase-modulated porosity | Integer 0-4 → float 0.0-1.0 | base_porosity + phase_overdrive | `_pool_weights_for_hex()` lines 659-663 |
| 3 | Kit QWP porosity | Float 0.15-0.71 | `kingwen_model_sets/kit_*.json` | `enrich_kit_models.py` (QWP = quantum wave packet) |

**Not reconciled**: These three computations use different scales, different sources, and different semantics. No conversion function exists between them.

## 2. Transformation

### 2.1 Phase modulation

Porosity varies by phase because `phase_overdrive` depends on `phase_bits`:
- Phase 0 (past): phase_overdrive = 0.0 → porosity = base
- Phase 7 (void): phase_overdrive = 0.875 (max) → porosity may increase

**Information loss**: The phase modulation is a simple linear addition, not a transformation that preserves the canonical base. The original base_porosity is not stored separately in the output — only the modulated result.

### 2.2 Porosity in consensus computation

- `multi_layer_expand.py:231`: `porosities.append(float(item.get("inject_site", {}).get("porosity", 0.35)))` — F-01 bug
- `multi_layer_expand.py:235`: `porosity_norms.append(float(item.get("inject_site", {}).get("porosity_norm", 0.0875) or 0.0875))` — F-01 bug
- `emotional_engine.py:1048`: `porosity = float(inject.get("porosity_norm", inject.get("porosity", 0.35)))` — F-02 bug (float(None))
- `emotional_engine.py:1113`: `porosity_norms = [float(item.get("inject_site", {}).get("porosity_norm", porosity_mean / 4.0) or porosity_mean / 4.0) for item in resolved]` — F-02 bug

### 2.3 Porosity in decision matrix

- `decision_matrix.py:198`: `porosity_norm = float(inject.get("porosity_norm", inject.get("porosity", 0.35)))` — F-02 bug
- `decision_matrix.py:99`: `_porosity_window_score(porosity_norm, emotional_input)` — uses porosity_norm for decision window
- `decision_matrix.py:409-410`: `porosity_norm = float(inject.get("porosity", 0) or 0) / 4.0` — converts int 0-4 to float 0.0-1.0

## 3. Serialization

### 3.1 In-memory (live producer)

- `shotgun_expand()` stores `inject_site` dict in each expanded/resolved entry
- `inject_site` contains: `porosity` (int 0-4), `porosity_norm` (float 0.0-1.0), `porosity_label`, `porosity_window`, `porosity_description`, `primary_pool`, `secondary_pool`, `reason`, `neighbors`, `intent_match`, `line_balance`

### 3.2 JSONL serialization

- `build_full_shotgun_jsonl.py` writes `full_shotgun_expansion_all.jsonl` (32MB)
- Porosity fields preserved in JSONL

### 3.3 JSON export (broken consumers)

- 5 consumers reference `shotgun_expand_output.json` which never existed (F-05 + F-05b)
- No canonical JSON file export of porosity exists on disk

## 4. Consumers

### 4.1 Direct consumers (call shotgun_expand())

| Consumer | Porosity field used | Transformation applied |
|---|---|---|
| `emotional_engine.py` (line 1048) | `inject.get("porosity_norm", inject.get("porosity", 0.35))` | F-02 bug: float(None) crash |
| `emotional_engine.py` (line 1113) | `item.get("inject_site", {}).get("porosity_norm", porosity_mean / 4.0)` | F-02 bug: or fallback masks 0.0 |
| `decision_matrix.py` (line 198) | `inject.get("porosity_norm", inject.get("porosity", 0.35))` | F-02 bug: float(None) crash |
| `decision_matrix.py` (line 409) | `inject.get("porosity", 0) / 4.0` | Converts int 0-4 to float 0.0-1.0 |
| `multi_layer_expand.py` (line 231) | `item.get("inject_site", {}).get("porosity", 0.35)` | F-01 bug: or 0.0875 masks 0.0 |
| `multi_layer_expand.py` (line 235) | `item.get("inject_site", {}).get("porosity_norm", 0.0875)` | F-01 bug: or 0.0875 masks 0.0 |
| `expand_server.py` (line 343) | `_inj.get("porosity", 0.5)` | Rounds to 3 decimal places |
| `kingwen_training.py` (line 519) | `hexagram['porosity']` | Uses hexagram porosity (int 0-4) |
| `kingwen_training.py` (line 574) | `vector.porosity_norm` | Formats as string `<|porosity|>{:.2f}` |
| `scripts/enrich_kit_models.py` | Kit QWP porosity (0.15-0.71) | Different scale, different source |

### 4.2 Broken consumers (reference nonexistent JSON) — F-05 + F-05b

| Consumer | Line | Porosity usage |
|---|---|---|
| `scripts/build_512_widget.py` | 6 | Cannot verify (file not found) |
| `scripts/build_per_hex_training_data.py` | 30 | Cannot verify (file not found) |
| `scripts/hexagram_shotgun_matcher.py` | 28 | Cannot verify (file not found) |
| `scripts/kingwen_quantum_expand.py` | 46 | Cannot verify (file not found) |
| `scripts/build_unified_bin.py` | 23 | Cannot verify (file not found) |

## 5. Information Loss Points

### 5.1 Production-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| Phase overdrive masking | `_pool_weights_for_hex()` | Phase 6-7 (void) has no porosity=0 states; phase overdrive pushes base up | Medium |
| Three unreconciled computations | Multiple | Injection site (0-4 int), phase-modulated (0.0-1.0), kit QWP (0.15-0.71) — no conversion | High |
| Canonical base not preserved | `_pool_weights_for_hex()` | Only modulated result stored; original base_porosity not in output | Medium |
| `or` fallback masking | multi_layer_expand.py:231,235; emotional_engine.py:1048,1113; decision_matrix.py:198 | Explicit 0.0 masked by `or 0.35`/`or 0.0875` | High (F-01, F-02) |

### 5.2 Serialization-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| No canonical JSON export | `shotgun_expand()` | No file written; 5 consumers broken | High |
| JSONL serialization | `build_full_shotgun_jsonl.py` | Porosity preserved but import path broken (F-06) | High |
| `inject_site` full dict | shotgun_expand() | Full dict preserved including all porosity fields | None — consistent |

### 5.3 Consumer-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| F-01: `or 0.0875` | `multi_layer_expand.py:235` | Masks explicit 0.0 in porosity_norm | High |
| F-02: `float(None)` | 3 locations | Crashes when None reaches numeric conversion | High |
| F-08: porosity unverified | 4 consumers | Cannot verify porosity consumption for broken consumers | Medium |
| `or 0.0` fallbacks | Various consumers | `rv.get(k, 0.0) or 0.0` masks explicit 0.0 in vector values | Medium |

### 5.4 Field-name inconsistencies

| Field name | Meaning | Used in | Risk |
|---|---|---|---|
| `porosity` | Integer 0-4 (injection site) | `inject_site["porosity"]` | Consistent within inject_site |
| `porosity` | Integer 0-4 (phase-modulated) | `inject_site["porosity"]` (overwritten) | Original base_porosity lost |
| `porosity_norm` | Float 0.0-1.0 | `inject_site["porosity_norm"]` | Consistent |
| `porosity` (kit QWP) | Float 0.15-0.71 | `kit_*.json` | Different scale, different source, no conversion |
| `porosity` (fallback) | Float 0.0-1.0 | `inject.get("porosity", 0.35)` | Conflates int 0-4 with float 0.0-1.0 |

## 6. Summary

### Porosity integrity: NOT PRESERVED (three unreconciled computations)

- **Production**: Porosity is correctly computed from canonical injection site + phase modulation. Phase overdrive creates meaningful variation.
- **Serialization**: No canonical JSON export. JSONL exists but import path broken.
- **Consumption**: Multiple consumers use `or` fallbacks that mask explicit 0.0. 5 consumers broken. 3 independent porosity computations not reconciled.
- **Transformation**: Phase modulation is simple linear addition. Canonical base not preserved separately. `or` fallbacks conflate 0.0 with None/missing.
- **Kit QWP**: Different scale (0.15-0.71), different source, no conversion function. Cannot be compared with injection site porosity.

### Open findings affecting porosity
- F-01: `or 0.0875` masks 0.0 in porosity_norm
- F-02: `float(None)` crashes in 3 locations
- F-05/F-05b: 5 consumers reference nonexistent JSON
- F-06: Broken import path
- F-07: Missing `__init__.py`
- F-08: Porosity consumption unverified for 4 consumers

### Recommended next investigation
L3 — Hamiltonian lineage audit. Trace formula identity → numerical result → downstream meaning, including the M3 formula, pq_dot, lagrangian, and M6 imaginary amplitude. The M3 Hamiltonian is the most complex field with the most documented information loss (F-10/F-11/F-12).