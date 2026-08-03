# King Wen + Supportive Research: Execution Guide
**Version:** 2026-08-02  
**Status:** Live reference — edit as implementation proceeds  
**Companion:** `KING-WEN-RESEARCH-CHECKLIST.md`

---

## 1. Scope & Hard Constraints

| Constraint | Rule |
|---|---|
| **No superposition flattening** | Never collapse the 512 resolved states to a single "answer." All-or-nothing only; "nothing" is invalid. |
| **No folklore** | No divination framing, no symbolic interpretation without executable math. |
| **No POG2 runtime imports** | POG2 is 1D 64 ternary selection matrix. Examine patterns only. |
| **Canonical runtime** | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES` + `expand_server.py` at `127.0.0.1:8765/expand` |
| **Worker role** | Thin proxy / reasoning shell. Real engine is local Python. |
| **Porosity mandatory** | Every voice artifact must carry `porosity` alongside 5-axis vector. |
| **Voice is authority, not decoration** | Default silence. Speaks only when demanded. |

### 1.1 Source-of-Truth Map
```
KING-WEN-I-CHING-IMMUTABLE-TABLES/
  emotional_engine.py      -> expand_hexagram(), collapse_full_128()
  expand_server.py         -> /expand (POST), /capture (POST JSONL)
  collapse_full_128_output.json  -> 3.1MB canonical snapshot
  hexagram_full_expansion.json   -> 64 expanded, 512 resolved
  scripts/
    full_hexagram_shotgun.py     -> 64/512/729/46656 canonical counts
    build_hexagram_skill_cards.py -> 12-card renderer input

kingwen-oracle-worker/
  src/index.ts             -> Worker consult(), buildReasonedOutput()
  src/data/                -> voicebox exports, collapse_full_128_output.json
  tests/                   -> 4/4 passing

OpenJarvis/
  src/openjarvis/emotion/kingwen.py  -> consult() router
  src/openjarvis/cli/_oracle_speak.py -> voice/turn-start wiring
```

---

## 2. King Wen Implementation Workstreams

### 2.1 State Expansion Engine [CHECKLIST A1-A8]

**Objective:** Full 64-hex expansion before slider. Slider is post-hoc rank-axis.

**Key files:**
- `emotional_engine.py`: `expand_hexagram()`, `sample_resolve()`, `collapse_full_128()`
- `full_hexagram_shotgun.py`: `shotgun_expand()`
- `hexagram_full_expansion.json`: 64 expanded, 512 resolved

**Steps:**
1. Verify `collapse_full_128(emotional_input=50)` returns `expanded_count=64`, `resolved_count=512`
2. Verify phase_bits distribution: 64 states per phase 0..7
3. Verify porosity normalization: source integer 0-4 → float 0.0-1.0
4. Verify `hexagram_full_expansion.json` inject_site fields: `yao_vocabulary`, `line_states`, `sample_paths`, `expanded_vector`, `resolved_vector`
5. Fallback order when inject_site empty: `collapse_full_128_output.json` → `emotional-weights.json` → `hexagram-registry.json`
6. Do NOT trim VOICEBOX_VOICE_POOL (66 pools canonical)
7. Do NOT collapse to single dominant in `_build_batch()`
8. All 64 hexagram slots in order 1-64 inclusive, no winner removal

**Pitfalls:**
- `hexagram_full_expansion.json` is stale: phase-level inject_site empty, porosity fixed 0.5
- `collapse_full_128_output.json` is the live snapshot
- `YAO_VOCABULARY[phase_temporal]` is keyed by integer `0` only — use `base.get("yao_vocabulary", {})` from `expand_hexagram()`

### 2.2 Worker Consult Rewrite [CHECKLIST B1-B10]

**Objective:** Question-aware 512-state ranking with reasoned output. No 1-hex collapse.

**Key file:** `kingwen-oracle-worker/src/index.ts`

**Steps:**
1. Remove `stableHash(text:sessionId:emotionalInput) % 64 + 1` dominant selection
2. Rank all 512 resolved states by: keyword overlap + vector quality + normalized porosity + phase tiebreak
3. Add `normalizePorosity()`: source integer 0-4 → 0.0-1.0
4. Return `all_hexagrams[]` with per-entry: `relevance_score`, `query_tokens`, `phase_temporal`, `phase_polarity`, `phase_description`, `line_states`, `yao_vocabulary`, `checklist`, `sample_paths`, `resolved_vector`, `expanded_vector`
5. Top result generates `buildReasonedOutput()`: `unified_weave`, `sovereign_assertion`, `boundary_condition`, `dissipator_warning`, `past_reflection`, `present_reflection`, `future_reflection`
6. Add `query_tokens`, `resolved_count`, `expanded_count`, `runtime_consensus`, `runtime_source`
7. matchesFilter reads `hex.hexagram_symbols.category/action` when top-level fields absent
8. `if_is` / `if_is_not` filtering must operate on full 64, not filtered subset
9. Verify `npm run test` 4/4 passing after changes
10. Deploy and verify live consult returns full 512 states with reasoned output

**Pitfalls:**
- Tied relevance scores are structurally guaranteed without non-negative margin constraint
- Category/action live under `hexagram_symbols`, not expanded-item root

### 2.3 Reasoning Layer [CHECKLIST C1-C9]

**Objective:** Dynamic generation from question + 512 states, not templates.

**Current state:** `buildReasonedOutput()` uses static reflections from JSON.

**Steps:**
1. Add signed preference deltas: `delta = resolved_vector.voiceWeight - expanded_vector.voiceWeight` per state
2. Enforce non-negative effective margin: `relevance = max(0, textScore + delta*weight + porosity*weight)`
3. Principle-first generation: seed `unified_weave` from `trainingNotes` + `inject_site.reason` as generative prompts
4. Context distillation split: return `raw_state` (what 512 states say) + `distilled_answer` (what question demands) as separate fields
5. Spec-aware generalization: use `phase_description` and `yao_vocabulary` as generative priors
6. Add phase-aware delta scoring: `resolved_vector - expanded_vector` per axis
7. Checklist/phase_description keyword overlap for tiebreak
8. Line states diversity tiebreak
9. Verify ranked output changes meaningfully between different questions (not degenerate)

**Pitfalls:**
- Without signed deltas, top entries can tie because scoring is mostly static per-hex
- Template-based `unified_weave` produces identical output for different questions

### 2.4 Voice / Porosity Mapping [CHECKLIST D1-D8]

**Objective:** Per-hexagram domain-gated voice assignment tied to porosity/tone.

**Current state:** `chooseSpeaker()` maps to Cloudflare speaker enum only. CF TTS models accept no expressive weight params.

**Steps:**
1. Verify real voicebox weights in `voicebox_profile_payload.json` and `voicebox_training_vector.json`
2. Map hexagram categories to voice domains: `sovereign→mars`, `boundary→juno`, `dissipator→saturn`, `transformer→jupiter`
3. Map actions to speaker hints: `ASSERT→atlas`, `YIELD→viga`, `ADAPT→echo`, `WAIT→luna`
4. Include `tts_speaker_hint` in consult payload per hexagram
5. Include `porosity` in every voice artifact (mandatory carrier)
6. For real weight-driven expression, route `/tts` to Voicebox/Cartesia (CF TTS = coarse fallback only)
7. Voice adapter must not depend on POG2
8. Voice is sensor, not model route — sidecar subscribes `KINGWEN_VOICE_COMPLETE`

**Pitfalls:**
- Cloudflare AI TTS models (`@cf/deepgram/aura-2-en`, `@cf/myshell-ai/melotts`) accept no emotion/vector parameters
- Speaker-as-voice mapping is coarse fallback only

### 2.5 Expand Server & Capture Pipeline [CHECKLIST E1-E6]

**Objective:** Live engine at `127.0.0.1:8765/expand` with append-only JSONL capture.

**Steps:**
1. Verify `/expand` POST returns full 512 resolved states with `expanded[]`, `resolved[]`, `top_10`, `selected`
2. Verify `bleed = porosity_lo + (porosity_hi - porosity_lo) * _clamp(emotional_input / 100.0)`
3. Add `/capture` POST endpoint → `DATASETS/shotgun_captures.jsonl` (append-only, non-blocking)
4. Widget fires `captureEvent` on tab switches, shotgun selects, jspace view switches
5. Never nullify existing disk artifacts — preserve baked `hexagrams[]` identity, merge live `resolved[]`
6. Verify expand_server.py process is running before relying on it

**Pitfalls:**
- `hexagram_full_expansion.json` inject_site is empty at phase level — do not use as inject-site source
- Stale `collapse_full_128_output.json` drift: verify timestamp before using

### 2.6 Save-String & Batch Protocol [CHECKLIST F1-F7]

**Objective:** 64-slot batch save string with phase encoding and inject-site base64.

**Steps:**
1. Save-string format: `hex_id:phase:vw:ch:cc:wh:dt:porosity:timestamp:domain`
2. Phase encoding: `a`=past, `p`=present, `f`=future
3. Batch format: 64 comma-separated compact strings, `;` separates payload from metadata
4. Inject-site fields with `:` or `|` delimiters must be base64-encoded: `yao_vocabulary`, `sample_paths`, `line_states`, `porosity_window`
5. Validate structurally, not by single mega-regex
6. Backward compatibility: parsers must accept legacy 10-segment singles and 7-section batches
7. `AvatarSaveString.to_compact()` appends `INJECT=<base64>` after 11 fixed extra fields

**Pitfalls:**
- Reusing `;` for both payload/metadata separation and entry separation causes collapsing
- Single-slot extension: `version|payload;extra_meta` — `;` separates payload from metadata only

### 2.7 Frontend / Widget [CHECKLIST G1-G8]

**Objective:** Pedagogical viewport with live 512-state data. Not runtime engine.

**Steps:**
1. Verify 7 tabs: Vector Space → Shotgun Blast → Hexagram Grid → Phase Explorer → State Matrix → Quantum Masking → J-space Jacobian
2. J-space renders: 1D Hamiltonian histogram, 2D Jacobian scatter, 3D Riemann sphere projection
3. Tab labels must match rendered content (not "3D Riemann" — that was wrong)
4. Shared state: `hexagrams[]` (64 identity base), `resolved[]` (512 live states), `selectedHexagram`, `selectedPhase`
5. Preserve baked `hexagrams[]`; merge live `resolved[]` over it
6. Iframe mount for kingwen mode in Cinder/OpenJarvis
7. `loadKit()` reads `DATASETS/kingwen_model_sets/kit_{hex_id}.json` directly
8. `kitToHexagramNode()` maps sovereign kit schema to renderer nodes

**Pitfalls:**
- Detached-tab failure: missing tab-matrix panel + missing `showTab('grid')` handler causes blank panels
- Widget display_approximation callouts mandatory if simplified formulas used

### 2.8 Sovereign Kit Pipeline [CHECKLIST H1-H6]

**Objective:** Detached renderer-agnostic state packets for avatar/UI.

**Steps:**
1. Build `DATASETS/kingwen_model_sets/kit_{1..64}.json` via `scripts/build_kingwen_model_sets.py`
2. Schema: `baseModel`, `maleModels_0`, `femaleModels_0`, `modelTranslate_0/1/2` (Riemann xyz), `rotation_0` (angle_deg), `rotation_1` (magnitude capped 999999), `big_value [live_bits, void_flag]`, `positions[6]`, `extra[14]`
3. Void hexes 15/20/30/40 → South Pole (0,0,-1)
4. Worker `/v1/kingwen/avatar/{session_id}` serves pure JS math port of `kingwen_mobius_sphere.py`
5. KV cache `KINGWEN_AVATAR_CACHE` id `c39fc2ed3ced4b988224861476ca8def` with 5min TTL
6. Frontend `ggwaveBridge.ts` loads kit_{hex_id}.json directly

---

## 3. Supportive Research Segments

### 3.1 Zotero Corpus Study [CHECKLIST R1-R10]

**Objective:** Extract logic/patterns from 245 PDFs for King Wen domain mapping, alignment theory, and voice training.

**Corpus root:** `C:\Users\krist\Desktop\zotero\learning-corpus\.text\`

**Domain inventory:**
| Domain | PDF Count | Representative Papers |
|---|---|---|
| graph-neural-networks | 67 | Graph4NLP, GNN survey |
| diffusion-generative | 64 | DDPM, Stable Diffusion |
| llm-alignment | 48 | RLHF Part II, DPO/RLHF equivalence, Self-Alignment, Model Spec Midtraining |
| efficient-inference-quantization | 42 | GGML, GPTQ, AWQ |
| multimodal-learning | 24 | CLIP, Stable Audio |
| unknown | 2 | — |

**Steps:**
1. Build corpus frequency profile: per-paper word/symbol/number/phrase counts with context windows
2. Route papers to hexagrams by `(category, action)` from `hexagram-registry.json`
3. Aggregate per hexagram WITHOUT cross-paper dedup — each hex should have hundreds to low thousands of unique words
4. Extract alignment math patterns:
   - Bradley-Terry preference model → King Wen signed margin ranking
   - DPO/RLHF conditional equivalence → non-negative effective margin enforcement
   - SELF-ALIGN 16 principles → 64-hex principle set mapping
   - Model Spec midtraining → `trainingNotes` as generative prior
5. Extract diffusion/generation patterns for voice synthesis:
   - DDPM noise schedule → porosity-timed voice modulation
   - CLIP contrastive learning → vector-space alignment for voiceWeight/coherence
6. Extract GNN patterns for state transition:
   - Graph neural message passing → hexagram-to-hexagram influence propagation
   - Node embeddings → 512-state vector space
7. Verify extraction script runs without fabrication: all samples trace back to actual corpus text
8. Write findings to `docs/zotero-corpus-findings.md` with exact paper IDs and page references
9. Cross-reference findings to guide sections 2.3 (Reasoning Layer) and 2.4 (Voice Mapping)
10. Update `kingwen_skill_card_renderer.py` with domain-specific tool mappings from corpus

**Pitfalls:**
- `.text` files are truncated extracts (~8k chars), not full papers
- Do not build page-by-page study notes from `.text` alone
- No synthetic/fabricated oracle resolves in dataset construction

### 3.2 POG2 Reference Audit [CHECKLIST R11-R14]

**Objective:** Extract non-folklore logic patterns from POG2 as reference only.

**Files examined:**
- `POG2/src/core/HexagramDefinitions.ts` (380 lines) — deterministic binary-keyed registry, derived context from trigram composition
- `POG2/src/routing/HexagramManager.ts` (907 lines) — CanonicalClock, ClockAuthorityRegistry, SovereignClockController, HexagramNetworkBridge, Pog2HexagramBridge
- `POG2/src/utils/CanonicalClock.ts` (579 lines) — 3-tier clock
- `POG2/src/utils/ClockAuthorityRegistry.ts` (62 lines) — domain-scoped time
- `POG2/src/utils/SovereignClockController.ts` (263 lines) — pause/resume per tier
- `POG2/src/sovereign/Pog2HexagramBridge.ts` (166 lines) — permission verdicts

**Steps:**
1. Document transferable patterns: clock authority, state machine boundaries, network bridge contracts
2. Document anti-patterns to avoid: 1D selection matrix, randomness injection, folklore labels
3. Verify zero POG2 runtime imports in King Wen codebase
4. Add findings to `docs/pog2-reference-patterns.md`

### 3.3 Alignment Theory Integration [CHECKLIST R15-R18]

**Objective:** Wire alignment theory into King Wen reasoning layer.

**Key papers:**
- RLHF Part II (2401.06080): Bradley-Terry, preference strength, contrastive learning
- DPO/RLHF equivalence (2605.20834): conditional equivalence, CPO, non-negative margins
- SELF-ALIGN (2305.03047): principle-driven generation, 16 principles → 64 hex principles
- Model Spec Midtraining (2605.02087): spec as generative prior, value generalization

**Steps:**
1. Map Bradley-Terry `p(y_w ≻ y_l) = σ(r_w - r_l)` to King Wen `relevance_score` between resolved states
2. Implement non-negative effective margin: `relevance = max(0, base_score + delta_margin)`
3. Map 16 SELF-ALIGN principles to 64 hexagram `trainingNotes` as generative priors
4. Implement context distillation: `raw_state` (512 states) → `distilled_answer` (question-aware)

---

## 4. Verification Gates

Every gate must pass before marking section complete.

| Gate | Command | Expected |
|---|---|---|
| A | `py_compile emotional_engine.py expand_server.py` | Exit 0 |
| B | `curl -X POST http://127.0.0.1:8765/expand -H "Content-Type: application/json" -d "{}"` | `expanded_count=64`, `resolved_count=512` |
| C | `npm run test` in kingwen-oracle-worker | 4/4 passing |
| D | `npm run build` in kingwen-oracle-worker | Exit 0 |
| E | `pytest tests/cli/test_chat_cmd.py` | Green (or explicit blocker report) |
| F | `grep -r "openjarvas" src/` | Zero matches |
| G | `grep -r "stableHash" src/index.ts` | Zero matches (no 1-hex collapse) |
| H | `grep -r "template" buildReasonedOutput` | Template-only patterns flagged for rewrite |

---

## 5. Execution Order

```
Phase 1: State Expansion (2.1)          -> Gates A, B
Phase 2: Worker Rewrite (2.2)           -> Gates C, D, G
Phase 3: Reasoning Layer (2.3)          -> Gate H
Phase 4: Voice Mapping (2.4)            -> Manual + Gate F
Phase 5: Capture Pipeline (2.5)         -> Gate B + /capture test
Phase 6: Save-String Protocol (2.6)     -> Structural validation
Phase 7: Frontend/Widget (2.7)          -> Visual + tab parity
Phase 8: Sovereign Kit (2.8)            -> Gate D + KV cache test
Phase 9: Zotero Corpus (3.1)            -> Exact paper IDs + frequency profiles
Phase 10: POG2 Reference (3.2)          -> docs/pog2-reference-patterns.md
Phase 11: Alignment Theory (3.3)        -> Gate H + reasoning integration
```

---

## 6. Artifact Registry

| Artifact | Path | Status |
|---|---|---|
| Guide | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\docs\KING-WEN-RESEARCH-GUIDE.md` | This file |
| Checklist | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\docs\KING-WEN-RESEARCH-CHECKLIST.md` | Companion |
| Worker source | `C:\Users\krist\Desktop\kingwen-oracle-worker\kingwen-oracle\src\index.ts` | Live |
| Expand server | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\expand_server.py` | Running |
| Collapse output | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\collapse_full_128_output.json` | 3.1MB canonical |
| Zotero corpus | `C:\Users\krist\Desktop\zotero\learning-corpus\.text\` | 490 files |
| Voice exports | `C:\Users\krist\Desktop\kingwen-oracle-worker\kingwen-oracle\src\data\` | Copied |
