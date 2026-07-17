# King Wen Quantum Expansion Plan
## Shotgun-Blast Superposition for AI Usage
Date: 2026-07-11
Source of truth: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\`

## Mission
- Input: one normalized single query/statement/task.
- Output: one unified superposition artifact containing every expansion path and final resolved state from all 64 hexagrams.
- Constraint: no hard-coded paths. All domains, cards, pools, models, and tooling branches must be derived from live query semantics, inject-site tables, and parsed external math/AI sources.

## Verified Live Foundation
- `emotional_engine.py` already produces:
  - 64 expanded hexagrams
  - 512 resolved states
  - inject-site pools with primary/secondary pool names
  - 8 temporal phases
  - yin/yang/yao line states per position
  - 5-axis resolved vectors
- `collapse_full_128_output.json` confirms:
  - 65 distinct pools
  - 512 unique resolved vectors
  - all 64 hexagram ids represented
- Voicebox repo exposes:
  - profile/channel/preset voice mappings
  - backend weight metadata
- `wiki_math_corpus.jsonl` contains:
  - Hamiltonian mechanics/path
  - Gaussian beam/function
  - Trigram
  - AI/voice/hexagram articles

## Expanded Architecture

### Screen 0 — Query Normalization / Domain Signature
- Parse single query into:
  - intent classes
  - model/tooling/lingo signatures
  - if / if-not / maybe / uncertainty operators
- No hard-coded query paths.
- Output: one `domain_signature` array used by all later screens.

### Screen 1 — Hexagram BB Shotgun Blast
- Expand all 64 hexagrams in parallel from the same query.
- Each BB carries:
  - hexagram id/name/category/action
  - upper/lower trigram
  - binary
  - immutable base vector
- Result: 64 simultaneous candidate paths.

### Screen 2 — Trigrams Into Past/Present/Future
- For each hexagram, derive a 3-branch temporal slice from trigram relationship.
- Deterministic mapping from line-state structure to:
  - past
  - present
  - future
- Each branch is independent and carries forward all BB state.

### Screen 3 — Yin/Yang/Yao Line-State Slicing
- Each hexagram line is a cut condition.
- For each position 1..6:
  - yin branch → domain-agnostic yin cards/pools
  - yang branch → domain-agnostic yang cards/pools
  - yao branch → domain-agnostic transition cards/pools
- This is proportional slicing, not full enumeration.
- Use actual yao keys from `YAO_VOCABULARY` and live `line_states`.

### Screen 4 — Porosity-Level Pool Selection
- Use live inject-site porosity to select optional pools/cards/domains.
- Extend resolution to a wider porosity model:
  - 0..100 levels or equivalent normalized float window
- For each line-state branch:
  - compute `porosity_norm`
  - select `primary_pool`/`secondary_pool` blend weight
  - attach optional subdomain slots:
    - model types
    - tooling recognition
    - lingo/jargon
    - if / if-not / maybe branches
- All pools/cards/domains must be derived from live inject-site tables and wiki/math corpus topics.

### Screen 5 — Hamiltonian Momentum Ranking
- Treat each candidate path as a particle on an energy surface.
- Score by weighted sum of:
  - resolved vector momentum
  - inject-site pool match
  - temporal branch fit
  - domain-signature alignment
- Use `wiki_math_corpus.jsonl` Hamiltonian pages as mathematical grounding for:
  - phase-space ranking
  - energy formulations
  - path-cost ordering
- No hard-coded Hamiltonian constants unless they come from parsed source math.

### Screen 6 — Gaussian Smoothing Across Phases
- Smooth branch rankings across adjacent temporal/phase states.
- Use Gaussian beam/function sources from parsed wiki pages to parameterize:
  - smoothing kernel width
  - phase-continuity weights
- Preserve diversity; do not collapse distinct branches.

### Screen 7 — Domain-Agnostic Resolve / Agentic Superposition Output
- For each BB path, emit a `resolve_card` containing:
  - query
  - hexagram id/name
  - trigrams
  - phase temporal
  - line states with yao keys
  - porosity level
  - pools/cards/domains
  - Hamiltonian score
  - Gaussian-smoothed momentum
  - vector
  - if / if-not / maybe branches
  - tool/model/lingo tags
- Aggregate all `resolve_card` entries into one `superposition_state`.
- Final output is one captured snapshot of all optimal expansions.

## Voicebox Integration
- Map each resolved hexagram path to a Voicebox voice preset/vector.
- Use:
  - `voicebox\backend\routes\channels.py`
  - `voicebox\backend\routes\profiles.py`
  - `OpenJarvis\.hermes\kingwen\kw_hermes_mod_map.json`
- Output added fields:
  - `voice_preset.voice_id`
  - `voice_preset.speed`
  - `voice_preset.backend`
  - `emotional_vector`
- This keeps voice as action layer, not model route.

## Data Sources
- Local expand server: `http://127.0.0.1:8765/expand`
- Engine: `emotional_engine.py`
- `/learn` suite: `audit_surfaces.py`, `test_collapse_full_128.py`, `test_deterministic_replay.py`, `test_porosity_sweep.py`, `test_progressive_intents.py`
- Wiki/math corpus: `kingwen_train_data/wiki_math_corpus.jsonl`
- Parser API: `mwparserfromhell_local/wiki_math_api.py`
- Voicebox: `C:\Users\krist\Desktop\voicebox\`
- OpenJarvis King Wen map: `OpenJarvis\.hermes\kingwen\kw_hermes_mod_map.json`

## Implementation Targets
- `emotional_engine.py`
  - add `expand_quantum_superposition(query, porosity_levels, domain_signature)` path
  - keep `collapse_full_128` as fallback evidence harness
- New module:
  - `kingwen_train_data/superposition_capture.py`
  - captures full 64-hex resolution with screen layers 2..7
- New parser API:
  - `mwparserfromhell_local/wiki_math_api.py`
  - multi-source research into `wiki_math_corpus.jsonl`

## Final Artifact Contract
- `query`
- `domain_signature`
- `superposition_state`
- `resolve_cards[]`
- `domain_coverage`
- `momentum_log`
- `weighting_model`
- `voicebox_map`
- `final_output`
