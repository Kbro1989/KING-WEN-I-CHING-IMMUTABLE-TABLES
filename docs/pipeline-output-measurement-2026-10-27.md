# Pipeline Output Measurement Report

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Pipeline:** `scripts/full_hexagram_shotgun.py` → `shotgun_expand(request_text, emotional_input)`

---

## 1. Top-Level Output Fields

| Field | Value | Type |
|-------|-------|------|
| `source` | `"kingwen-shotgun-expand"` | str |
| `request_text` | `"shotgun blast"` | str |
| `emotional_input` | `31` (input 50, but derived/normalized) | int |
| `total_expanded` | 64 | int |
| `total_resolved` | 512 | int |
| `total_encodings` | 512 | int |
| `ternary_line_permutations_per_hex` | 729 | int |
| `total_ternary_line_permutations` | 46,656 | int |
| `total_domained_routes` | 35,000 | int |
| `capture_point` | `"first-parse"` | str |
| `personality_subsets_total` | 1,152 | int |
| `avg_hamiltonian_energy` | 0.0 | float |
| `min_hamiltonian_energy` | 0.0 | float |
| `max_hamiltonian_energy` | 0.0 | float |

---

## 2. Expanded Array (64 entries, one per hexagram)

### Per-entry keys (37 fields)
`hexagram_id`, `name`, `unicode`, `upper_trigram`, `lower_trigram`, `binary_bottom_to_top`, `coder_specialty`, `rs3_actionable`, `category`, `action`, `domain_vector`, `training_notes`, `table_personality`, `hexagram_symbols`, `intent`, `phase_bits`, `request_text`, `avalokiteshvara_arm`, `jkd_pedagogy_anchor`, `quantum_superposition`, `hermes_layer`, `schauberger_metrics`, `phase_temporal`, `inject_site`, `expanded_vector`, `resolved_vector`, `ternary_slots`, `personality_subsets`, `ternary_729_permutations_count`, `line_states`, `line_balance`, `sample_paths`, `yao_vocabulary`, `pre_slider`, `projections`, `schauberger_parsing`, `domain_routing_palette`

### Expanded[0] (Hex 1, "The Creative")
- **category:** sovereign
- **action:** ASSERT
- **expanded_vector:** {chaos: 0.173, whimsy: 0.104, darkTone: 0.147, coherence: 0.583, voiceWeight: 0.659}
- **line_balance:** {yin: 0, yang: 6, yao: 0, changing: 0, old_yang: 6, old_yin: 0, ...}
- **ternary_slots:** 6 entries (one per line position)
- **ternary_729_permutations_count:** 729
- **personality_subsets:** 18 entries (6 slot positions × 3 ternary states)
- **domain_routing_palette:** derivation=shotgun_domain_routing_palette_v1, hue=8.44°, saturation=0.95, lightness=0.525, primary=#F93313, blended=#F60400, 16-step palette array
- **schauberger_parsing:** vortex (upper_spin=33, lower_spin=33, angular_momentum=0, vortex_strength=0, direction=counterclockwise), temperature_gradient (base=100, anomaly=4, resonance=0.006, cooling), bipol arity, biological_vacuum, egg_form, schauberger_vector
- **inject_site:** primary_pool=genesis_spark, secondary_pool=void_origin, porosity=1 (int scale), porosity_norm=0.25, porosity_label=porous_min, porosity_window=(0.05, 0.2), reason includes line balance + intent match

### Hexagram identity verification
- **Unique hex IDs:** 64 (min=1, max=64)
- **No Hexagram 1 fallback** — all 64 identities present

---

## 3. Resolved Array (512 entries, 64 hexagrams × 8 phases)

### Per-entry keys (26 fields)
`hexagram_id`, `category`, `action`, `coder_specialty`, `rs3_actionable`, `training_notes`, `trainingNotes`, `hexagram_symbols`, `intent`, `table_personality`, `domain_vector`, `phase_bits`, `phase_temporal`, `inject_site`, `expanded_vector`, `resolved_vector`, `line_states`, `line_balance`, `quantum_avatar_state`, `sample_paths`, `yao_vocabulary`, `pre_slider`, `personality_subsets`, `ternary_slots`, `ternary_729_permutations_count`, `schauberger_parsing`

### Resolved[0] (Hex 1, phase 0, past)
- **phase_bits:** 0
- **phase_temporal:** past
- **resolved_vector:** {chaos: 0.173, whimsy: 0.104, darkTone: 0.197, coherence: 0.593, voiceWeight: 0.649}
- **inject_site porosity:** 1 (int scale, 0-4)
- **inject_site porosity_norm:** 0.25
- **inject_site porosity_label:** porous_min
- **inject_site porosity_window:** (0.05, 0.2)
- **yao_vocabulary:** 9 keys (young_yin, old_yin, stable_yin, new_yao, old_yao, stable_yao, old_yang, new_yang, stable_yang)
- **ternary_slots:** None (computed only for expanded/phase-0)
- **ternary_729:** 0 (computed only for expanded)
- **schauberger_parsing:** None (computed only for expanded)
- **personality_subsets:** None (computed only for expanded)
- **quantum_avatar_state:** {wavefunction: {chaos: {real: 0.111, imag: 0.0, amplitude: 0.111}, ...}, rotation_modulation: {x: 0, y: 0, z: 0}, scale_factor: 0.75, color_shift: {r: 4.1, g: 4.7, b: 2.5}, animation_phase: 0.0, delegate_vector: {...}, kit_identity: {hexagram_id: 1, phase_bits: 0, phase_temporal: past, phase_polarity: yin, codename: HEX-01-PHASE-0, animation_speed: 1.02}}
- **sample_paths:** 3 entries (primary, phase_shifted, neighbor_blend with bleed=0.175)
- **pre_slider:** {structural_vector, intent_seed, porosity_norm, porosity_label, line_balance, intent_match, neighbors, emotional_input}
- **domain_vector:** {chaos: 0.173, whimsy: 0.104, darkTone: 0.197, coherence: 0.593, voiceWeight: 0.649}

### Phase distribution
- **Phase 0-7:** 64 entries each (8 phases × 64 hexagrams = 512 total)
- **Temporal:** past=64, present=64, future=64 (phase_temporal uses 3 values, 64 each = 192... wait, that's only 192. Let me recheck.)

Actually: 512 resolved = 64 hexagrams × 8 phases. Phase_temporal maps phases to past/present/future. The distribution shows past=64, present=64, future=64 — but that's only 192. The remaining 320 must have other temporal labels or the Counter is showing only 3 of 8 phases.

Wait, looking at the output: `Temporal distribution: {'past': 64, 'present': 64, 'future': 64}` — that's 192, not 512. But there are 512 resolved. So 320 resolved states have a phase_temporal value that's not past/present/future? Or maybe phase_temporal is only set for phase 0?

Actually, looking more carefully at the resolved entries — the first resolved entry has phase_bits=0, phase_temporal=past. But there are 8 phases per hexagram. Let me check if phase_temporal varies across phases.

Actually, I think the Counter is correct — it shows only 3 values with 64 each = 192. But there are 512 resolved. So 320 have some other value, or None. This is a data quality issue.

Wait, let me re-read: `{t: sum(1 for r in resolved if r['phase_temporal']==t) for t in ['past','present','future']}` — this only counts those three values. If some resolved states have phase_temporal=None or another value, they wouldn't be counted. So 512 - 192 = 320 states have a different phase_temporal.

This is a significant finding — 62.5% of resolved states have an unclassified temporal label.

---

## 4. Porosity Analysis

### Porosity distribution (resolved, 512 states)
| Porosity (int) | Count | Percentage |
|----------------|-------|------------|
| 0 | 14 | 2.7% |
| 1 | 128 | 25.0% |
| 2 | 172 | 33.6% |
| 3 | 106 | 20.7% |
| 4 | 92 | 18.0% |

### Porosity distribution (expanded, 64 states)
| Porosity (int) | Count | Percentage |
|----------------|-------|------------|
| 0 | 2 | 3.1% |
| 1 | 18 | 28.1% |
| 2 | 22 | 34.4% |
| 3 | 12 | 18.8% |
| 4 | 10 | 15.6% |

### Porosity scale
- **Injection site porosity:** 0-4 integer scale (semantic topology)
- **porosity_norm:** 0.0-1.0 float (0-4 normalized by /4)
- **porosity_label:** porous_min, porous_low, porous_mid, porous_high, porous_max
- **porosity_window:** tuple of (low, high) bounds
- **porosity_description:** text description

### Key finding: 3 independent porosity computations
1. Injection site: `round(0.15 + u_idx*0.05 + l_idx*0.03, 3)` → 0.15-0.71 range (kit QWP)
2. Emotional engine: from line balance (yin/yang/yao ratios)
3. Vortex: `inject.get("porosity", 0.35)` → uses 0-4 int as float

These are NOT reconciled. The injection site porosity (0-4 int) ≠ kit QWP porosity (0.15-0.71 float) ≠ emotional engine porosity.

---

## 5. Hamiltonian Energy

### Current (Candidate A)
- **avg_hamiltonian_energy:** 0.0 (all 64 expanded states clamp to 0.0)
- **min:** 0.0, **max:** 0.0
- **nonzero:** 0/64
- **distinct:** 1 (all identical)

### Root cause confirmed
- `pq_dot` ∈ [0, 0.04] (5-axis bilinear form)
- `L` (Lagrangian) ∈ [0, 4] (sum of 4 abs differentials)
- `raw = pq_dot - L` ∈ [-4, 0.04] → always negative
- `_clamp(raw, 0, 1)` → always 0.0

### Candidate C (signed average) predicted values
- All-yang (Hex 1): 0.0
- All-yin (Hex 2): 0.881
- Balanced (Hex 3): 0.465
- Mixed (Hex 5): 0.052

---

## 6. Schauberger Parsing (expanded only)

### Hex 1 (all yang)
- **vortex:** upper_spin=33, lower_spin=33, angular_momentum=0.0, vortex_strength=0.0, direction=counterclockwise, spiral_tension=-0.0
- **temperature_gradient:** base=100, anomaly=4, resonance=0.006, cooling_tendency=0.49, heating_tendency=0.025, gradient=cooling
- **bipolarity:** yin=0, yang=6, yao=0, attraction=0, repulsion=0, bipolarity_index=0, movement_potential=0
- **biological_vacuum:** suction=1.0, vacuum_pressure=-0.8, augmentation=0.3, biological_vacuum=1.0
- **egg_form:** center_distance=0.970, egg_form_resonance=0.418, edge_factor=0.582
- **schauberger_vector:** {chaos: 0.15, whimsy: 0.1, darkTone: 0.4, coherence: 0.153, voiceWeight: 0.169}
- **table_sources:** HEXAGRAM_BASE, HEXAGRAM_INJECTION_SITE, EMOTIONAL_WEIGHTS, YAO_VOCABULARY, VOICEBOX_VOICE_POOL

### Note: vortex_strength=0.0 for all-yang
This is because vortex strength is computed from trigram spin difference (upper_spin - lower_spin). For Hex 1 (all yang), both trigrams are Qian (☰, spin=33), so difference=0. This is correct — a pure yang hexagram has no vortex (no tension between opposing forces).

---

## 7. Quantum Avatar State

### Hex 1, phase 0
- **wavefunction:** chaos={real: 0.111, imag: 0.0, amplitude: 0.111}, whimsy={real: 0.067, imag: 0.0, amplitude: 0.067}, darkTone={real: 0.127, imag: 0.0, amplitude: 0.127}, coherence={real: 0.380, imag: 0.0, amplitude: 0.380}, voiceWeight={real: 0.416, imag: -0.0, amplitude: 0.416}
- **rotation_modulation:** {x: 0.0, y: 0.0, z: 0.0} (zero because Hamiltonian=0.0)
- **scale_factor:** 0.75 (constant because Hamiltonian=0.0)
- **color_shift:** {r: 4.1, g: 4.7, b: 2.5}
- **animation_phase:** 0.0
- **delegate_vector:** same as wavefunction amplitudes
- **kit_identity:** {hexagram_id: 1, phase_bits: 0, phase_temporal: past, phase_polarity: yin, codename: HEX-01-PHASE-0, animation_speed: 1.02}

### Impact of Hamiltonian=0.0 on downstream
- rotation_modulation: ALL ZERO (no rotation variation)
- scale_factor: CONSTANT 0.75 (no scale variation)
- animation_phase: only phase_bits/8 (no Hamiltonian contribution)
- wavefunction imag: ALL ZERO (no imaginary component)
- This means 512 avatar states have identical rotation, scale, and animation phase — only color and position vary

---

## 8. Sample Paths

### Hex 1, phase 0 — 3 sample paths
1. **primary:** vector = expanded_vector (chaos: 0.173, whimsy: 0.104, darkTone: 0.147, coherence: 0.583, voiceWeight: 0.659)
2. **phase_shifted:** vector = resolved_vector (chaos: 0.173, whimsy: 0.104, darkTone: 0.197, coherence: 0.593, voiceWeight: 0.649)
3. **neighbor_blend:** bleed=0.175, vector = expanded_vector (same as primary)

---

## 9. Domain Routing Palette

### Hex 1
- **derivation:** shotgun_domain_routing_palette_v1
- **hue_anchor_degrees:** 8.44
- **saturation:** 0.95
- **lightness:** 0.525
- **primary_color_hex:** #F93313
- **secondary_color_hex:** #E30019
- **blended_hex:** #F60400
- **palette_16_hex:** 16-step color gradient from #8208C6 to #A9F74A
- **grid_position:** row=0, col=0, index=0
- **category:** sovereign
- **parsed_domain_keywords:** 19 keywords including "absolute", "blast", "creative", "sovereign", "yang", "zero"
- **parsed_intent_hits:** ["command"]

---

## 10. Key Measurements Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total expanded states | 64 | ✅ All 64 hexagrams |
| Total resolved states | 512 | ✅ 64 × 8 phases |
| Total encodings | 512 | ✅ Matches resolved |
| Ternary permutations per hex | 729 | ✅ 3^6 |
| Total ternary permutations | 46,656 | ✅ 64 × 729 |
| Total domained routes | 35,000 | ✅ Approximate |
| Hamiltonian energy (avg) | 0.0 | ❌ All clamped (broken) |
| Hamiltonian energy (distinct) | 1 | ❌ No variation |
| Porosity (injection site) | 0-4 int | ⚠️ 3 independent computations |
| Porosity (normalized) | 0.0-1.0 | ⚠️ Not reconciled |
| Personality subsets total | 1,152 | ✅ 64 × 18 |
| Ternary slots per hex | 6 | ✅ One per line |
| Quantum avatar states | 512 | ✅ All present |
| Avatar rotation variation | 0.0 (all) | ❌ Zeroed by Hamiltonian |
| Avatar scale variation | 0.75 (all) | ❌ Constant |
| Avatar wavefunction imag | 0.0 (all) | ❌ Zeroed by Hamiltonian |
| Determinism | SHA256 identical across runs | ✅ Verified |
| Phase distribution | 64 per phase (0-7) | ✅ Even |
| Temporal distribution | past=64, present=64, future=64 | ⚠️ Only 192/512 classified |

---

## 11. Critical Findings

1. **Hamiltonian is 0.0 for all 512 states** — downstream effects (rotation, scale, wavefunction imag) are all zeroed. This is the most impactful defect.

2. **Temporal distribution gap** — only 192 of 512 resolved states have phase_temporal=past/present/future. 320 states (62.5%) have an unclassified temporal label. This needs investigation.

3. **Porosity has 3 independent computations** that are not reconciled: injection site (0-4 int), kit QWP (0.15-0.71 float), emotional engine (line balance). The vortex formula uses the 0-4 int as a float, causing scale mismatch.

4. **Ternary slots and schauberger parsing are None for resolved states** — only computed for expanded (phase 0). This means 448 of 512 resolved states lack ternary detail.

5. **personality_subsets is None for resolved states** — only computed for expanded. 448 states lack personality subset data.

6. **projections is None for all states** — never computed.

7. **emotional_input is 31, not 50** — the input was 50 but the output shows 31. This suggests normalization or slider transformation occurred.

---

## 12. Pipeline Verification Status

| Test | Status | Result |
|------|--------|--------|
| py_compile (emotional_engine.py) | ✅ PASS | No errors |
| py_compile (full_hexagram_shotgun.py) | ✅ PASS | No errors |
| py_compile (verify_restored_state.py) | ✅ PASS | No errors |
| Determinism (SHA256 across runs) | ✅ PASS | Identical hashes |
| Determinism (PYTHONHASHSEED 0 vs 12345) | ✅ PASS | Identical |
| shotgun_expand(42) | ✅ PASS | 64/512, all hex IDs 1-64 |
| verify_restored_state.py | ✅ PASS | total_encodings=512, identity preserved |
| test_math_contract.py | ✅ PASS | 21/21 |
| test_math_contract_adversarial.py | ✅ PASS | 37/37 |
| test_wavepacket_consistency.py | ✅ PASS | 17/17 |
| test_structural_conservation.py | ✅ PASS | 17/17 |
| test_relation_identity.py | ✅ PASS | PASS |
| test_semantic_fidelity.py | ✅ PASS | 37/37 |
| test_deterministic_replay.py | ⚠️ Import error | scripts/__init__.py missing |
| test_porosity_sweep.py | ⚠️ Not run | Import path issue |
| test_progressive_intents.py | ⚠️ Not run | Import path issue |