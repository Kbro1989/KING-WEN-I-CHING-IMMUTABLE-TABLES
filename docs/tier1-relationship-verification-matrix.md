# Tier 1 Relationship Verification Matrix — King Wen Core Capability Dependencies

## Scope and Method

- **Read-only validation.** No files, frontmatter, skill definitions, or graph edges were modified.
- **8 candidates** from Tier 1 of the validation artifact (core capability dependencies).
- **Validation standard:** Each candidate must have source evidence (actual capability ownership), target evidence (actual consumption), direction verified (traceable execution/data flow), dependency verified (demonstrated capability dependency), active (current active skill and path), and distinct (not merely another description of the same capability).
- **Schema question addressed:** Whether `related_skills` can represent directed relationships (Produces, Consumes, Integrates, Advises) or only undirected associations.

---

## Schema Capability Assessment

### Question: Can `related_skills` represent directed relationships?

**Answer: No.** The `related_skills` field in SKILL.md frontmatter is a flat YAML list of skill name strings. It has no type, direction, or evidence metadata. It represents **undirected association only**.

### Implications

| Capability Needed | `related_skills` Supports? | Alternative |
|-------------------|---------------------------|-------------|
| Relationship type (Produces/Consumes/Integrates/Advises) | No | Separate typed relationship store or frontmatter extension |
| Directionality | No | Direction must be inferred from skill descriptions and implementation paths |
| Reciprocal declarations | Partial — some skills declare each other, some don't | Audit reciprocal declarations separately |
| Advisory vs execution dependency | No | Advisory relationships must be documented separately or use a different field |
| Archived vs active targets | No | Archive filtering must be applied at graph-generation time |

### Current `related_skills` State

| Skill | Declares `related_skills`? | Declares `kingwen`? | Declares `kingwen-ternary-expansion`? | Notes |
|-------|---------------------------|--------------------|--------------------------------------|-------|
| `kingwen` | Yes (12 targets) | N/A (self) | Yes | Declares 12 targets including 3 archived skills (kingwen-gibberlink-bridge, openjarvis-kingwen-receptive-map, kingwen-truth-reconciliation) |
| `kingwen-ternary-expansion` | Yes (11 targets, many duplicates) | Yes (as `king-wen`) | N/A (self) | Duplicate declarations; uses `king-wen` not `kingwen` |
| `openjarvis-kingwen-integration` | Yes (2 targets) | Yes | No | Minimal declaration set |
| `kingwen-emotion-voice` | Yes (5 targets) | Yes (as `king-wen`) | Yes | Uses `king-wen` not `kingwen` |
| `kingwen-jarvis-megatron-learn` | Yes (4 targets) | Yes | Yes | Declares `kingwen-batch-domain-test` (archived) |
| `kingwen-oracle-advisory` | Yes (4 targets) | Yes | Yes | Declares `kingwen-batch-domain-test` (archived) |
| `avalokiteshvara-kingwen` | Yes (4 targets) | Yes | Yes | Declares `kingwen-batch-domain-test` (archived) |
| `learn_king_wen_math_extractors` | Yes (3 targets) | **No** | No | Does NOT declare `kingwen` despite being a King Wen math extractor skill |
| `kingwen-3d-tooling` | Yes (2 targets) | Yes (as `autonomous-ai-agents/king-wen`) | Yes | Uses `autonomous-ai-agents/king-wen` not `kingwen` |

### Schema Finding

The `related_skills` field is an **undirected association list**. It cannot represent:
- Relationship type (Produces/Consumes/Integrates/Advises)
- Directionality
- Evidence provenance
- Advisory vs execution dependency
- Archived vs active status

**Recommendation:** Before creating any relationships, decide whether to:
1. Extend `related_skills` with typed sub-fields (requires schema change)
2. Create a separate typed relationship store
3. Document directed relationships in `references/` files until schema is extended

---

## Tier 1 Verification Matrix

### Candidate 1: `kingwen` → `kingwen-ternary-expansion`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-01 |
| **Source skill** | `kingwen` |
| **Target skill** | `kingwen-ternary-expansion` |
| **Relationship type** | Produces → Consumes |
| **Source evidence** | `kingwen` owns computation: `emotional_engine.py` (5-axis vector, Hamiltonian energy, consensus), `decision_matrix.py` (phase routing), `full_hexagram_shotgun.py` (shotgun_expand() producer). Immutable tables at `KING-WEN-I-CHING-IMMUTABLE-TABLES/`. |
| **Target evidence** | `kingwen-ternary-expansion` consumes: `ternary_full_expansion.json` (2.9MB, 27 trigrams, 729 hexagrams, 5,832 resolved states), `multi_layer_expand.py` (ternary layer), `kingwen_quantum_expand.py` (quantum expansion). Frontmatter declares `kingwen` (as `king-wen`) in `related_skills`. |
| **Direction verified** | Yes — `kingwen` produces shotgun_expand() output; `kingwen-ternary-expansion` consumes it via `ternary_full_expansion.json` and `multi_layer_expand.py`. Data flow: producer → consumer. |
| **Dependency verified** | Yes — `kingwen-ternary-expansion` cannot function without `kingwen`'s expanded states. The ternary layer is computed FROM the binary layer. |
| **Active** | Yes — both skills are active (not in `.archive/`). Both SKILL.md files present. |
| **Distinct** | Yes — `kingwen` owns binary computation (512 states); `kingwen-ternary-expansion` owns ternary computation (5,832 states). Different representation spaces. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists (as `king-wen`). No change needed for compatibility. |
| **Disposition** | **Supported** |

### Candidate 2: `kingwen` → `openjarvis/openjarvis-kingwen-integration`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-02 |
| **Source skill** | `kingwen` |
| **Target skill** | `openjarvis/openjarvis-kingwen-integration` |
| **Relationship type** | Produces → Consumes |
| **Source evidence** | `kingwen` produces: shotgun_expand() output (64 expanded, 512 resolved, consensus, ternary_permutations), emotional_tongue, inject_site, porosity. `emotional_engine.py` produces 5-axis vectors. |
| **Target evidence** | `openjarvis-kingwen-integration` consumes: `kingwen_oracle_consult_tool.py` (wraps consult()), `ggwaveBridge.ts` (loads kit_*.json), `avatarProtocol.ts` (avatar payload). Frontmatter declares `kingwen` in `related_skills`. |
| **Direction verified** | Yes — King Wen produces cognitive state; OpenJarvis consumes it for voice, avatar, and runtime surfaces. Data flow: producer → consumer. |
| **Dependency verified** | Yes — OpenJarvis integration cannot function without King Wen output. The consult tool, avatar bridge, and voice preset all depend on King Wen's expanded state. |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns computation; `openjarvis-kingwen-integration` owns integration/consumption. Different responsibilities. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists. |
| **Disposition** | **Supported** |

### Candidate 3: `kingwen` → `autonomous-ai-agents/kingwen-emotion-voice`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-03 |
| **Source skill** | `kingwen` |
| **Target skill** | `autonomous-ai-agents/kingwen-emotion-voice` |
| **Relationship type** | Produces → Consumes |
| **Source evidence** | `kingwen` produces: 5-axis emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight), porosity, inject_site, emotional_tongue. `emotional_engine.py` produces these via `_hamiltonian_energy()`, `_pool_weights_for_hex()`, etc. |
| **Target evidence** | `kingwen-emotion-voice` consumes: CartesiaAdapter reads emotional-weights.json; voice reward sidecar subscribes to KINGWEN_VOICE_COMPLETE; `cartesia_tts.py` dual-path. Frontmatter declares `king-wen` (as `king-wen`) in `related_skills`. |
| **Direction verified** | Yes — King Wen produces emotional vector; emotion-voice consumes it for TTS parameters (speed, voice_id, emotion tags). Data flow: producer → consumer. |
| **Dependency verified** | Yes — emotion-voice cannot produce TTS parameters without King Wen's emotional vector. The CartesiaAdapter reads from King Wen's emotional-weights.json. |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns emotional computation; `kingwen-emotion-voice` owns TTS parameter mapping. Different responsibilities. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists (as `king-wen`). |
| **Disposition** | **Supported** |

### Candidate 4: `kingwen` → `research/kingwen-jarvis-megatron-learn`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-04 |
| **Source skill** | `kingwen` |
| **Target skill** | `research/kingwen-jarvis-megatron-learn` |
| **Relationship type** | Produces → Integrates |
| **Source evidence** | `kingwen` produces: expanded states, resolved states, consensus, personality_subsets, training_notes. `full_hexagram_shotgun.py` produces 1,536 records (64×8×3). |
| **Target evidence** | `kingwen-jarvis-megatron-learn` integrates: training corpora routing, embedding generation, model identity. Frontmatter declares `kingwen` in `related_skills`. Skill description: "Learning-loop skill connecting King Wen cognitive outputs to OpenJarvis runtime and Megatron-LM training surfaces." |
| **Direction verified** | Yes — King Wen produces training data; megatron-learn integrates it into Megatron-LM training. Data flow: producer → integrator. |
| **Dependency verified** | Yes — megatron-learn cannot route training corpora without King Wen's expanded states and personality_subsets. |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns state computation; `kingwen-jarvis-megatron-learn` owns training integration. Different responsibilities. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists. |
| **Disposition** | **Supported** |

### Candidate 5: `kingwen` → `research/kingwen-oracle-advisory`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-05 |
| **Source skill** | `kingwen` |
| **Target skill** | `research/kingwen-oracle-advisory` |
| **Relationship type** | Produces → Integrates |
| **Source evidence** | `kingwen` produces: consult() output (hexagram_sequence, phase_bits, emotional_deltas, trainingNotes, unified_weave). `emotional_engine.py` produces consensus. |
| **Target evidence** | `kingwen-oracle-advisory` integrates: advisory surface for King Wen oracle consults. Frontmatter declares `kingwen` in `related_skills`. Skill description: "Advisory surface for King Wen oracle consults." |
| **Direction verified** | Yes — King Wen produces consult output; oracle-advisory wraps it for product/tooling integration. Data flow: producer → integrator. |
| **Dependency verified** | Yes — oracle-advisory cannot provide advisory without King Wen's consult output. |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns computation; `kingwen-oracle-advisory` owns advisory wrapping. Different responsibilities. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists. |
| **Disposition** | **Supported** |

### Candidate 6: `kingwen` → `research/avalokiteshvara-kingwen`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-06 |
| **Source skill** | `kingwen` |
| **Target skill** | `research/avalokiteshvara-kingwen` |
| **Relationship type** | Produces → Integrates |
| **Source evidence** | `kingwen` produces: skill cards (12 slots), domain vectors, inject_site, ternary_slots. `build_hexagram_skill_cards.py` produces skill cards. |
| **Target evidence** | `avalokiteshvara-kingwen` integrates: multi-arm capability registry for King Wen. Frontmatter declares `kingwen` in `related_skills`. Skill description: "Multi-arm mapping registry for compassionate/domain reconfiguration in King Wen outputs." |
| **Direction verified** | Yes — King Wen produces skill cards/domain vectors; avalokiteshvara maps them to multi-arm routing. Data flow: producer → integrator. |
| **Dependency verified** | Yes — avalokiteshvara cannot map multi-arm capabilities without King Wen's skill cards and domain vectors. |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns state computation; `avalokiteshvara-kingwen` owns multi-arm routing. Different responsibilities. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists. |
| **Disposition** | **Supported** |

### Candidate 7: `kingwen` → `research/learn_king_wen_math_extractors`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-07 |
| **Source skill** | `kingwen` |
| **Target skill** | `research/learn_king_wen_math_extractors` |
| **Relationship type** | Produces → Consumes |
| **Source evidence** | `kingwen` produces: math extraction pipeline (arxiv_html_parser.py, math_recovery_tool.py, mathml_parser.py), math contract (ExprNode, Integral), structural conservation (21/21 tests). |
| **Target evidence** | `learn_king_wen_math_extractors` consumes: math extraction knowledge base. Skill description: "Use when working the non-I-Ching math/chroma extractors." Frontmatter declares `research/pdf-learning-corpus`, `research/math-pdf-parser`, `research/arxiv-math-extraction` — but **does NOT declare `kingwen`**. |
| **Direction verified** | Partially — math extractors feed King Wen engine (King Wen consumes math extraction output), but the skill's `related_skills` does not include `kingwen`. The direction may be reversed: `learn_king_wen_math_extractors` produces math extraction that King Wen consumes, not the other way around. |
| **Dependency verified** | Partially — King Wen's math pipeline depends on math extraction, but `learn_king_wen_math_extractors` is a knowledge-base skill, not a runtime dependency. |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns state computation; `learn_king_wen_math_extractors` owns math extraction knowledge. Different responsibilities. |
| **Historical compatibility** | **NOT preserved** — `learn_king_wen_math_extractors` does NOT declare `kingwen` in `related_skills`. This is a missing reciprocal declaration. |
| **Disposition** | **Inconclusive** — Direction may be reversed (math extractors produce for King Wen, not King Wen produces for math extractors). Missing reciprocal declaration. Requires further investigation. |

### Candidate 8: `kingwen` → `autonomous-ai-agents/kingwen-3d-tooling`

| Field | Value |
|-------|-------|
| **Candidate ID** | T1-08 |
| **Source skill** | `kingwen` |
| **Target skill** | `autonomous-ai-agents/kingwen-3d-tooling` |
| **Relationship type** | Produces → Consumes |
| **Source evidence** | `kingwen` produces: 512 avatar meshes (64 hex × 8 phases), Möbius sphere coordinates, quantum wave packets, kit_*.json state packets. `kingwen_mobius_sphere.py`, `kingwen_state_transition.py`. |
| **Target evidence** | `kingwen-3d-tooling` consumes: 3D generators and DA-V2 depth bridge. Frontmatter declares `autonomous-ai-agents/kingwen-ternary-expansion` and `autonomous-ai-agents/king-wen` in `related_skills`. |
| **Direction verified** | Yes — King Wen produces 3D state (meshes, coordinates, wave packets); 3D-tooling consumes them for rendering. Data flow: producer → consumer. |
| **Dependency verified** | Yes — 3D-tooling cannot generate 3D output without King Wen's state packets (kit_*.json, avatar meshes). |
| **Active** | Yes — both skills active. |
| **Distinct** | Yes — `kingwen` owns state computation; `kingwen-3d-tooling` owns 3D generation/rendering. Different responsibilities. |
| **Historical compatibility** | Preserved — existing `related_skills` declaration exists (as `autonomous-ai-agents/king-wen`). |
| **Disposition** | **Supported** |

---

## Pilot Chain Verification

### Proposed pilot: King Wen capability flow

1. **Capability ownership:** `kingwen` owns computation — `emotional_engine.py`, `decision_matrix.py`, `full_hexagram_shotgun.py`. Authoritative output: shotgun_expand() returns 64 expanded + 512 resolved + consensus + ternary_permutations. ✓ Verified.

2. **Specialized computation:** `kingwen-ternary-expansion` owns ternary computation — `ternary_full_expansion.json` (2.9MB, 27 trigrams, 729 hexagrams, 5,832 resolved states). Consumes binary layer from `kingwen`. ✓ Verified.

3. **Integration:** `openjarvis-kingwen-integration` consumes King Wen output — consult tool, avatar bridge, voice preset. Does NOT own computation. ✓ Verified.

4. **Verification:** `verification/capability-pulse` and `verification/verification-artifact-hygiene` provide independent verification. `research/kingwen-learn-suite-runner` runs /learn verification suite. ✓ Verified (advisory, not execution dependency).

### Pilot Result

| Relationship | Source | Target | Type | Direction | Evidence | Confidence | Disposition |
|-------------|--------|--------|------|-----------|----------|------------|-------------|
| T1-01 | kingwen | kingwen-ternary-expansion | Produces → Consumes | Verified | shotgun_expand → ternary_full_expansion | High | Supported |
| T1-02 | kingwen | openjarvis-kingwen-integration | Produces → Consumes | Verified | consult → avatar/voice bridge | High | Supported |
| T1-03 | kingwen | kingwen-emotion-voice | Produces → Consumes | Verified | emotional vector → Cartesia TTS | High | Supported |
| T1-04 | kingwen | kingwen-jarvis-megatron-learn | Produces → Integrates | Verified | expanded states → training corpora | High | Supported |
| T1-05 | kingwen | kingwen-oracle-advisory | Produces → Integrates | Verified | consult output → advisory surface | High | Supported |
| T1-06 | kingwen | avalokiteshvara-kingwen | Produces → Integrates | Verified | skill cards → multi-arm routing | High | Supported |
| T1-07 | kingwen | learn_king_wen_math_extractors | Produces → Consumes | **Partial** | Direction may be reversed; missing reciprocal declaration | Medium | **Inconclusive** |
| T1-08 | kingwen | kingwen-3d-tooling | Produces → Consumes | Verified | avatar meshes → 3D generation | High | Supported |

### Pilot Acceptance Criteria Met

- ✅ Every relationship has a source, target, type, direction, evidence reference, and explicit confidence
- ✅ No relationship was created during the pilot (read-only validation only)
- ✅ One relationship (T1-07) flagged as Inconclusive with specific evidence gap
- ✅ The relationship model describes the system (7/8 Supported, 1/8 Inconclusive)

---

## Summary

- **Schema assessment:** `related_skills` is undirected association only. Cannot represent type, direction, evidence, or advisory vs dependency. Recommend typed relationship store or frontmatter extension before creating any relationships.
- **Tier 1 validation:** 7/8 Supported, 1/8 Inconclusive (T1-07: direction may be reversed, missing reciprocal declaration).
- **Pilot chain verified:** King Wen capability flow (computation → ternary → integration → verification) traced end-to-end.
- **No changes made.** No files, frontmatter, skill definitions, or graph edges modified. All results are validation-only.