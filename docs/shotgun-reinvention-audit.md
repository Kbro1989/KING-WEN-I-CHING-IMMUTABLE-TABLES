**Cross-reference to current run (2026-11-02):** F-05 (4 of 7 consumers still reference nonexistent `shotgun_expand_output.json`), F-06 (`build_full_shotgun_jsonl.py` import path broken), and F-07 (no `scripts/__init__.py`) are now VALIDATED as separate findings. The `or 0.35` fix was verified (13/13 PASS) but F-01 (`or 0.0875` remaining) and F-02 (None handling) are new findings not identified in this report. See `docs/remediation-verification-matrix.md` Entries 1–2 and `docs/cross-reference-audit-2026-11-02.md`.

# Shotgun Reinvention Audit — Layered vs. Reinvented Capabilities

**Date:** 2026-11-02  
**Status:** READ-ONLY AUDIT — no source modifications  
**Scope:** All Python files referencing `shotgun_expand` or containing "shotgun" in filename

---

## Canonical Producer

`scripts/full_hexagram_shotgun.py` — `shotgun_expand(request_text, emotional_input)` is the single capture point.
- Returns: 64 expanded hexagrams, 512 resolved states, 729 ternary permutations per hex, 46,656 total ternary
- All downstream consumers should CALL this function, not reimplement its logic

## File Inventory: Shotgun-Related Python Files (18 files)

### Layer 1: Canonical Producer
| File | Role | Status |
|------|------|--------|
| `scripts/full_hexagram_shotgun.py` | `shotgun_expand()` — single capture point | ✅ Canonical |

### Layer 2: Direct Consumers (call shotgun_expand, layer on top)
| File | Role | Status |
|------|------|--------|
| `scripts/expand_server.py` | HTTP server wrapping shotgun_expand | ✅ Layers correctly |
| `scripts/generate_canonical_manifest.py` | Generates canonical manifest from shotgun_expand | ✅ Layers correctly |
| `scripts/generate_reference_files.py` | Generates reference files from shotgun_expand | ✅ Layers correctly |
| `scripts/enrich_kit_models.py` | Enriches kit models from shotgun_expand | ✅ Layers correctly |
| `scripts/generate_sovereign_world.py` | Generates sovereign world from shotgun_expand | ✅ Layers correctly (but uses JKD energy, not M3) |
| `scripts/export_voicebox_training.py` | Exports voicebox training from shotgun_expand | ✅ Layers correctly |
| `scripts/math_to_kingwen_adapter.py` | Math→King Wen adapter using shotgun_expand | ✅ Layers correctly |
| `scripts/bridge_math_diagram_extractor.py` | Bridge to quantum resolver | ✅ Layers correctly |
| `scripts/bridge_quantumlab_visualization.py` | Bridge to quantum viz | ✅ Layers correctly |
| `scripts/bridge_rayeren_capability_vectors.py` | Bridge to RayeRen vectors | ✅ Layers correctly |
| `scripts/testbed_2clock.py` | 2-clock measurement test | ✅ Layers correctly |
| `scripts/test_cognitive_variation.py` | Cognitive variation test | ✅ Layers correctly |
| `scripts/test_jkd_chapter_chorus.py` | JKD chapter chorus test | ✅ Layers correctly |
| `scripts/test_wavepacket_consistency.py` | Wavepacket consistency test | ✅ Layers correctly |
| `scripts/verify_math_jacobian_hamiltonian.py` | Math verification | ✅ Layers correctly |
| `scripts/verify_output_mismatches.py` | Output mismatch verification | ✅ Layers correctly |
| `scripts/verify_unbound_persona_domains.py` | Persona domain verification | ✅ Layers correctly |
| `scripts/kingwen_mobius_sphere.py` | Möbius sphere coordinates | ✅ Layers correctly |
| `scripts/kingwen_state_transition.py` | State transition | ✅ Layers correctly |
| `scripts/generate_full_code_solution.py` | Code solution generation | ✅ Layers correctly |
| `scripts/inspect_real_runtime_output.py` | Runtime inspection | ✅ Layers correctly |
| `scripts/export_all_64_answers.py` | Export 64 answers | ✅ Layers correctly |
| `scripts/solve_and_capture.py` | Solve and capture | ✅ Layers correctly |
| `scripts/recover_training_data.py` | Training data recovery | ✅ Layers correctly |
| `scripts/regenerate_training_data.py` | Training data regeneration | ✅ Layers correctly |
| `scripts/query_layer_probe.py` | Query layer probe | ✅ Layers correctly |
| `emotional_engine.py` | Emotional engine (imports shotgun_expand) | ✅ Layers correctly |
| `hexagram_personality.py` | Personality mapping (imports shotgun_expand) | ✅ Layers correctly |
| `kingwen_training.py` | Training (imports shotgun_expand) | ✅ Layers correctly |
| `kingwen_voice_router.py` | Voice router (references shotgun_expand) | ✅ Layers correctly |
| `kingwen_train_data/superposition_capture.py` | Superposition capture | ✅ Layers correctly |
| `kingwen_train_data/kingwen_expansion_wrapper.py` | Expansion wrapper | ✅ Layers correctly |
| `learn/scripts/*` (8 files) | Learn scripts | ✅ Layers correctly |

### Layer 3: Reinventions (reimplement shotgun logic instead of calling it)

| File | Reinvention | What it should do |
|------|------------|-------------------|
| `scripts/generate_full_shotgun_30gb.py` | Reimplements emotional vector calculation (`_calculate_permutation_emotional_vector`) instead of using shotgun_expand output | Should call shotgun_expand() and serialize its output |
| `scripts/generate_729_resolved_full.py` | `compute_ternary_emotional_vector()` — reinvents ternary emotional vector from scratch | Should read from shotgun_expand().resolved[] |
| `scripts/hexagram_shotgun_matcher.py` | References `shotgun_expand_output.json` (doesn't exist) | Should call shotgun_expand() directly |
| `scripts/build_per_hex_training_data.py` | References `shotgun_expand_output.json` (doesn't exist) | Should call shotgun_expand() directly |
| `scripts/kingwen_quantum_expand.py` | References `shotgun_expand_output.json` (doesn't exist) | Should call shotgun_expand() directly |
| `scripts/build_512_widget.py` | References `shotgun_expand_output.json` (doesn't exist) | Should call shotgun_expand() directly |
| `scripts/kingwen_mobius_sphere.py` | References `shotgun_expand_output.json` (doesn't exist) — has comment "Root-level shotgun_expand_output.json never existed" | Should call shotgun_expand() directly (already does via lazy import) |
| `scripts/kingwen_state_transition.py` | Same pattern — references nonexistent file, has lazy import fallback | Should call shotgun_expand() directly (already does via lazy import) |

### Layer 4: Multiple Reinventions of Same Capability

| Capability | Files | Reinvention Count |
|-----------|-------|-------------------|
| Godot 729 world generation | `generate_godot_729.py`, `v2`, `v3`, `v4`, `sovereign.py` | 5 versions |
| Training data generation | `build_full_shotgun_jsonl.py`, `regenerate_training_data.py`, `recover_training_data.py`, `build_per_hex_training_data.py` | 4 implementations |
| Hamiltonian calculation | `emotional_engine.py` (_hamiltonian_energy), `ingest_jkd_megatron_wavepackets.py` (JKD scalar) | 2 different formulas sharing field name |
| Ternary expansion | `full_hexagram_shotgun.py`, `kingwen_quantum_expand.py`, `generate_729_resolved_full.py` | 3 implementations |

### Layer 5: Referenced-But-Missing Files

| Referenced File | Referenced By | Actually Exists? |
|----------------|---------------|------------------|
| `shotgun_expand_output.json` | `hexagram_shotgun_matcher.py:28`, `build_per_hex_training_data.py:30`, `kingwen_quantum_expand.py:46`, `build_512_widget.py:6`, `kingwen_mobius_sphere.py:52`, `kingwen_state_transition.py:59` | NO — only `full_shotgun_expansion_all.jsonl` exists |
| `scripts/__init__.py` | `build_full_shotgun_jsonl.py:34` (import `from scripts.full_hexagram_shotgun`) | NO — scripts/ is not a package |
| `collapse_full_128_output.json` | Multiple (stale) | NO — replaced by shotgun output |

### Layer 6: src/core/ pipeline (separate from scripts/)

| File | Role | Layers on shotgun_expand? |
|------|------|--------------------------|
| `src/core/kingwen_shotgun_pipeline.py` | J-Space manifold bridge, slash commands | Imports CODER_SPECIALTIES etc. from full_hexagram_shotgun but does NOT call shotgun_expand() |

## Key Findings

### 1. `shotgun_expand_output.json` never existed

Multiple files reference `ROOT / "shotgun_expand_output.json"` but this file was never created. The canonical output is `kingwen_train_data/full_shotgun_expansion_all.jsonl` (32MB, 1536 records). Files referencing the nonexistent JSON are either:
- Broken (will fail at runtime)
- Have fallback lazy imports (kingwen_mobius_sphere.py, kingwen_state_transition.py)
- Use a different data source entirely

### 2. `scripts/` is not a Python package

`build_full_shotgun_jsonl.py` imports `from scripts.full_hexagram_shotgun import ...` but `scripts/` has no `__init__.py`. This makes the builder unexecutable as written.

### 3. Multiple Godot generators should be one

Five files (`generate_godot_729.py`, `v2`, `v3`, `v4`, `sovereign.py`) each independently generate Godot 729 ternary worlds. These should be a single generator with version flags, not five separate files.

### 4. `generate_full_shotgun_30gb.py` reinvents emotional vector calculation

Instead of calling `shotgun_expand()` and serializing its output, this file has `_calculate_permutation_emotional_vector()` which recomputes emotional vectors from scratch. This should read from `shotgun_expand()` output.

### 5. `generate_729_resolved_full.py` reinvents ternary emotional vectors

`compute_ternary_emotional_vector()` independently computes ternary emotional vectors instead of reading from `shotgun_expand().resolved[]`.

### 6. `hexagram_shotgun_matcher.py` and `build_per_hex_training_data.py` share the same broken reference

Both reference `ROOT / "shotgun_expand_output.json"` which doesn't exist. Both should call `shotgun_expand()` directly.

## Recommended Layering (Not Yet Authorized)

1. **Create `scripts/__init__.py`** to make `scripts/` a proper package (or adjust all imports to use `sys.path` insertion + flat import)
2. **Consolidate Godot generators** into one file with version flags
3. **Fix `hexagram_shotgun_matcher.py` and `build_per_hex_training_data.py`** to call `shotgun_expand()` instead of reading nonexistent JSON
4. **Fix `kingwen_quantum_expand.py` and `build_512_widget.py`** to call `shotgun_expand()` instead of reading nonexistent JSON
5. **Fix `generate_full_shotgun_30gb.py`** to serialize `shotgun_expand()` output instead of recomputing
6. **Fix `generate_729_resolved_full.py`** to read from `shotgun_expand().resolved[]` instead of recomputing
7. **Fix `build_full_shotgun_jsonl.py`** import path (missing `scripts/__init__.py`)
8. **Fix `src/core/kingwen_shotgun_pipeline.py`** to call `shotgun_expand()` instead of importing constants only

## Research Constraints Honored

- ✅ No source modifications
- ✅ No formula changes
- ✅ No Gate 2 closure
- ✅ All findings recorded as supplementary evidence
- ✅ Observed behavior distinguished from proposed corrections
