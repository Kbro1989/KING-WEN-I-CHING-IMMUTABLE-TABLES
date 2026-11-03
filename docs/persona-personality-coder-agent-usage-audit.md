# Persona, Personality, Coder, and Agent Usage Audit

**Date:** 2026-11-02  
**Status:** READ-ONLY AUDIT — no source modifications  
**Scope:** Trace all usages of "persona", "personality", "coder", "agent", "avalokiteshvara" per hexagram or trigram

---

## 1. Persona/Personality Usages

### 1.1 `hexagram_personality.py` — Core Personality Layer

**Functions:**
- `slot_personality(bit_value, position, upper_bits, lower_bits)` — per-slot binary personality from trigram bits
- `hexagram_tags_from_table(hexagram_id)` — extracts personality tags from immutable table data
- `build_hexagram_personality_map()` — builds map for all 64 hexagrams
- `resolve_personality_by_consensus(resolved, consensus_vector)` — resolves active personalities using consensus weights + table tags
- `expand_with_personality(emotional_input, request_text)` — full 64-hex expansion with table-tag personality layer

**Mappings (hardcoded, from immutable tables):**
| Category | Agent Type |
|----------|-----------|
| sovereign | architect |
| transformer | integrator |
| dissipator | navigator |
| boundary | guardian |

| Action | Domain |
|--------|--------|
| ASSERT | assertion |
| YIELD | reception |
| ADAPT | adaptation |
| WAIT | patience |

| Trigram | Element |
|---------|---------|
| Qian | heaven |
| Kun | earth |
| Zhen | thunder |
| Kan | water |
| Li | fire |
| Xun | wind |
| Gen | mountain |
| Dui | lake |

**Usage in shotgun_expand():**
- `pers_map = build_hexagram_personality_map()` (line 557)
- `personality_subsets` built from `_personality_subsets_for_slot()` (line 567)
- `table_personality` stored per expanded hexagram (line 611)
- `personality_consensus` computed via `resolve_personality_by_consensus()` (line 704)
- CSV export: `personality_map.csv` (64 rows, pure table-tag identity)

**Reinvention check:** `hexagram_personality.py` is the SINGLE source of personality mapping. No other file reimplements these mappings. ✅

---

### 1.2 `full_hexagram_shotgun.py` — Personality Integration

**Personality-related fields in expanded[] (64):**
- `table_personality`: full personality tags (category, action, agent_type, domain, upper/lower trigram, element_subset, slot_tags)
- `personality_subsets`: 18 items per hexagram (ternary slot expansion)
- `personality_consensus`: dominant agent type, domain, distribution, consensus vector, dominant intent

**Personality-related fields in resolved[] (512):**
- `table_personality`: full personality tags (SAME as expanded)
- `personality_subsets`: None (computed only for expanded/phase-0)

**Gap:** Resolved states carry `table_personality` but not `personality_subsets`. Consumers reading only resolved[] lose the 18 ternary personality subsets per hexagram.

**personality_subsets_total:** 1152 (64 × 18) — this is the sum across all expanded hexagrams.

---

### 1.3 `kingwen_train_data/build_full_shotgun_jsonl.py` — Personality in JSONL

**Fields extracted:**
- `table_personality`: hexagram personality tags
- `avalokiteshvara_arm`: 9-arm capability mapping
- `coder_specialty`: modulo-derived (see Section 3)

**Usage:** Serializes personality data into training JSONL. Blocked by import failure.

---

### 1.4 `scripts/build_hexagram_skill_cards.py` — Skill Cards from Personality

**Function:** `skill_cards_for_binary(hexagram_id, binary, category, action)`

**Maps hexagram binary → skill cards.** Uses `category` and `action` from personality tags to determine card type.

**Output:** 12 skill cards (6 binary + 6 legal) per hexagram.

---

### 1.5 `scripts/export_voicebox_training.py` — Personality in Voice Training

**Function:** `_build_personality(hexagram_id, ...)` — builds personality data for voicebox training.

**Usage:** Extracts personality tags for voice synthesis. Uses `agent_type`, `domain`, `element_subset` from personality map.

---

### 1.6 `scripts/build_avalokiteshvara_registry.py` — 9-Arm Capability

**Maps hexagram → 9-arm Avalokiteshvara capability registry.** Uses personality tags to determine which arms are active.

**Fields:** `avalokiteshvara_arm` with 9 arms, each with capability, tool mapping, and domain.

---

### 1.7 `src/core/pog3_hexagram_runtime_substrate.py` — Runtime Substrate

**Uses:** `table_personality`, `agent_type`, `domain` from shotgun output for runtime state.

**Fields in save string:** `ARM{arm_id}|{jkd_anchor}|{qfid}` — includes Avalokiteshvara arm ID and JKD anchor.

---

## 2. Coder Specialty Usages

### 2.1 Definition

```python
CODER_SPECIALTIES = [
    "Research", "Dev", "HTML", "Robotics", "Game Dev", "Analytics",
    "Blueprinting", "Scribe", "Security Red-Team", "Database/Storage",
    "Async/Networking", "DevOps/CI-CD"
]
```

**12 specialties, assigned by modulo:** `CODER_SPECIALTIES[(h_id - 1) % len(CODER_SPECIALTIES)]`

### 2.2 Usages Across Files

| File | Usage | Derivation |
|------|-------|-----------|
| `scripts/full_hexagram_shotgun.py` | `coder_specialty` field in expanded/resolved | `(h_id - 1) % 12` |
| `kingwen_train_data/build_full_shotgun_jsonl.py` | `coder_specialty` field | `(hexagram_id - 1) % len(CODER_SPECIALTIES)` |
| `scripts/enrich_kit_models.py` | `coder_specialty` field | `(hex_id - 1) % len(CODER_SPECIALTIES)` |
| `output/build_hexagram_archetypes.py` | `coder_specialty` + archetype string | From sample data |
| `scripts/build_per_hex_training_data.py` | `coder_specialty` field | From archetype data |
| `scripts/build_differential_npc_manifest.py` | `coder_specialty` field | From grounded data |

**Pattern:** All files use the same modulo derivation `(h_id - 1) % 12`. No file reinvents the derivation. ✅

**Concern:** The modulo derivation means hexagram 1 and hexagram 13 both get "Research" (1 mod 12 = 0, 13 mod 12 = 0). This is a structural mapping, not a semantic one. The 12 specialties cycle every 12 hexagrams.

---

## 3. Avalokiteshvara Arm Usages

### 3.1 Definition

Each hexagram has an `avalokiteshvara_arm` field with:
- `arm_id`: 1-9 (which of the 9 arms)
- `skill_domain`: same as coder_specialty
- `jkd_anchor`: JKD pedagogy anchor
- `capability`: capability description

### 3.2 Usages Across Files

| File | Usage |
|------|-------|
| `scripts/full_hexagram_shotgun.py` | Generates `avalokiteshvara_arm` per hexagram |
| `scripts/build_avalokiteshvara_registry.py` | Builds 9-arm registry |
| `scripts/build_differential_npc_manifest.py` | Uses `avalokiteshvara_arm` for NPC manifest |
| `kingwen_train_data/build_full_shotgun_jsonl.py` | Serializes `avalokiteshvara_arm` |
| `src/core/pog3_hexagram_runtime_substrate.py` | Includes arm_id in save string |

**Pattern:** All files read from shotgun output. No reinvention. ✅

---

## 4. Agent Type Usages

### 4.1 Definition

```python
CATEGORY_AGENT_TYPE = {
    "sovereign": "architect",
    "transformer": "integrator",
    "dissipator": "navigator",
    "boundary": "guardian",
}
```

### 4.2 Usages Across Files

| File | Usage |
|------|-------|
| `hexagram_personality.py` | Defines CATEGORY_AGENT_TYPE, uses in `hexagram_tags_from_table()` |
| `scripts/full_hexagram_shotgun.py` | Stores `agent_type` in expanded/resolved/table_personality |
| `kingwen_train_data/build_full_shotgun_jsonl.py` | Serializes `agent_type` |
| `scripts/export_voicebox_training.py` | Uses `agent_type` for voice personality |

**Pattern:** All files read from personality map. No reinvention. ✅

---

## 5. Domain Usages

### 5.1 Definition

```python
ACTION_DOMAIN = {
    "ASSERT": "assertion",
    "YIELD": "reception",
    "ADAPT": "adaptation",
    "WAIT": "patience",
}
```

### 5.2 Usages Across Files

| File | Usage |
|------|-------|
| `hexagram_personality.py` | Defines ACTION_DOMAIN, uses in `hexagram_tags_from_table()` |
| `scripts/full_hexagram_shotgun.py` | Stores `domain` in expanded/resolved/table_personality |
| `scripts/_derive_domain_routing_palette` | Uses domain for routing palette |
| `kingwen_train_data/build_full_shotgun_jsonl.py` | Serializes `domain` |
| `scripts/export_voicebox_training.py` | Uses `domain` for voice personality |

**Pattern:** All files read from personality map. No reinvention. ✅

---

## 6. Trigram-Level Usages

### 6.1 Trigram Element Mapping

```python
TRIGRAM_ELEMENT = {
    "Qian": "heaven", "Kun": "earth", "Zhen": "thunder",
    "Kan": "water", "Li": "fire", "Xun": "wind",
    "Gen": "mountain", "Dui": "lake",
}
```

### 6.2 Trigram Usages Across Files

| File | Usage |
|------|-------|
| `hexagram_personality.py` | TRIGRAM_ELEMENT mapping, `slot_personality()` uses trigram bits |
| `scripts/full_hexagram_shotgun.py` | `upper_trigram`, `lower_trigram` fields in expanded/resolved |
| `scripts/multi_layer_expand.py` | Trigram-level expansion (9 funcs) |
| `kingwen_ternary_tables_complete.py` | Trigram indices (upper_idx, lower_idx) |

**Pattern:** Trigram identity is carried through all layers. ✅

---

## 7. Skill Card Usages

### 7.1 Definition

`build_hexagram_skill_cards.py` generates 12 skill cards per hexagram:
- 6 binary-slot cards (slots 1-6)
- 6 legal-path cards (slots 7-12, category-seeded)

### 7.2 Usages Across Files

| File | Usage |
|------|-------|
| `scripts/build_hexagram_skill_cards.py` | Generates 12 cards per hexagram |
| `scripts/full_hexagram_shotgun.py` | Stores skill cards in expanded (via `_personality_subsets_for_slot`) |
| `OpenJarvis/src/openjarvis/tools/kingwen_skill_card_renderer.py` | Renders skill cards for OpenJarvis |
| `OpenJarvis/src/openjarvis/tools/kingwen_top_k_router.py` | Top-K routing using skill cards |

**Pattern:** Skill cards are generated from shotgun output and consumed by OpenJarvis. ✅

---

## 8. Summary: Persona/Personality/Coder/Agent Usage Chain

```
Immutable Tables (HEXAGRAM_BASE)
    ↓
hexagram_personality.py (CATEGORY_AGENT_TYPE, ACTION_DOMAIN, TRIGRAM_ELEMENT)
    ↓
build_hexagram_personality_map() → HEXAGRAM_PERSONALITY_MAP (64 entries)
    ↓
full_hexagram_shotgun.py (shotgun_expand)
    ├── expanded[]: table_personality, personality_subsets (18 per hex), coder_specialty, avalokiteshvara_arm, domain_routing_palette
    ├── resolved[]: table_personality, coder_specialty, avalokiteshvara_arm (personality_subsets=None)
    ├── personality_consensus: dominant_agent_type, dominant_domain, agent_distribution, domain_distribution
    └── personality_map: 64 entries (runtime-built)
    ↓
Consumers:
    ├── build_full_shotgun_jsonl.py (serializes all fields)
    ├── generate_sovereign_world.py (uses JKD scalar, not M3 H)
    ├── update_3d_kits (enriches with quantum wavepackets)
    ├── export_voicebox_training.py (voice personality from table tags)
    ├── build_avalokiteshvara_registry.py (9-arm capability)
    ├── build_hexagram_skill_cards.py (12 cards per hexagram)
    ├── kingwen_voice_router.py (voice routing)
    └── OpenJarvis (skill cards, top-K router)
```

### No Reinventions Found

All persona/personality/coder/agent usages trace back to:
1. `hexagram_personality.py` — single source of personality mapping
2. `scripts/full_hexagram_shotgun.py` — single source of shotgun expansion with personality integration
3. Immutable tables — single source of hexagram data

No file reinvents personality mapping, coder specialty assignment, agent type mapping, or domain mapping. All consumers read from the canonical sources. ✅

### Identified Gaps (Not Reinventions)

1. **Resolved states lose personality_subsets** — computed only for expanded (phase=0), None for all 512 resolved
2. **CODER_SPECIALTIES is modulo-derived** — hex 1 and hex 13 both get "Research" (structural, not semantic)
3. **build_full_shotgun_jsonl.py cannot run** — import blocked by missing `__init__.py`
4. **skill cards are generated separately** — not part of shotgun_expand output, generated by build_hexagram_skill_cards.py
