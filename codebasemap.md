# King Wen Workspace Codebasemap
Source of truth: `Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES`
Canonical tables: `data/hexagram-registry.json`, `data/emotional-weights.json`, `data/temporal-reflections.json`

---

## Files

### `KING_WEN_TABLES.py`
- Static 64-hex registry with verification asserts.
- `HEXAGRAMS[]`: id, name, chinese, pinyin, binary, unicode, upper/lower trigram, category, action.
- Validates unique binaries, inversion pairs, complementary pairs.
- Python entrypoint for table inspection and validation.
- Active dependents: `scripts/verify_registry.py`, Python inspection paths.
- Reactive dependents: generator/deprecated outputs if regenerated.

### `data/hexagram-registry.json`
- 64-hex table with id, name, chinese, binary, unicode, trigrams, category, action.
- Consumed by `src/core/OracleEngine.ts`, `src/parser/NarrativeEngine.ts`, OpenJarvis `emotion/kingwen.py`.
- Active dependents: `OracleEngine`, `NarrativeEngine`, King Wen emotion provider.

### `data/emotional-weights.json`
- 64 entries of emotional deltas: `chaos`, `whimsy`, `darkTone`, `coherence`, `voiceWeight`.
- Each entry carries `trainingNotes`: phrase-level voice/persona training context.
- Consumed by `OracleEngine.computeEmotionalDeltas`, OpenJarvis prompt emotion/voice sections, Oracle Console outputs.
- Active dependents: prompt emotion/voice sections, Oracle Console outputs.

### `data/temporal-reflections.json`
- 64 reflection triples: `past`, `present`, `future`.
- Consumed by `NarrativeEngine.generateReflections`, OpenJarvis Oracle Console/prompt reflections.
- Active dependents: Oracle Console, prompt reflections, voice modulation inputs.

### `emotionalweights.json`
- Python/deprecated artifact mirror of `data/emotional-weights.json`.
- Contains the full `EMOTIONAL_WEIGHTS` dict with `trainingNotes`.
- Not an active runtime path; useful for regeneration semantics.
- Reactive dependent: generated via `scripts/generate_*.py`.

### `src/index.ts`
- Public export surface: `OracleEngine`, `EmotionalParser`, `NarrativeEngine`, temporal math, deterministic hash, types.
- Active dependents: any TS consumer importing from `src/`.

### `src/core/OracleEngine.ts`
- Main consultation class.
- Loads registry, weights, reflections into runtime maps.
- `consult(query)` → selects hexagram, computes temporal phase, generates reflections/emotional deltas, returns `OracleResponse`.
- Uses `EmotionalParser`, `NarrativeEngine`, `DeterministicHash`, temporal math.
- Active dependents: OpenJarvis `emotion/kingwen.py` bridge logic and runtime consultation paths.

### `src/parser/EmotionalParser.ts`
- Parses `OracleQuery.user_context` and `emotional_input` into `EmotionalVector`.
- Maps fatigue/context into emotional deltas.
- Active dependents: `OracleEngine.consult`.

### `src/parser/NarrativeEngine.ts`
- Generates `ReflectionSet` from registry reflections + emotional weights.
- Throws if reflections missing for a hexagram.
- Active dependents: `OracleEngine.consult`.

### `src/utils/TemporalMath.ts` / `TemporalMath.js`
- `computeTemporalPhase(tick, emotionalInput)`:
  - `phase = tick % 3` → `0=past`, `1=present`, `2=future`
  - `substate = emotionalInput < 33 ? 'old' : emotionalInput > 66 ? 'young' : 'transition'`
  - returns dominant weight `0.6` and side weights `0.2`
- `phaseToString(phase)` → `past|present|future`
- Active dependents: `OracleEngine.consult`, deterministic routing/time gates.

### `src/utils/DeterministicHash.ts` / `DeterministicHash.js`
- SHA-256-based deterministic selection; uses `crypto.subtle.digest('SHA-256', ...)`.
- `deterministicIndex(input, maxExclusive)` → `DataView.getUint32(0) % maxExclusive`
- `deterministicHexagramSelect(tick, sessionId, previousHex, selector)` → `1..64`
- No `Math.random()`.
- Active dependents: `OracleEngine.selectHexagram`

### `src/types/oracle.ts` / `oracle.js`
- Type definitions:
  - `TemporalPhase`, `TemporalSubstate`, `HexagramAction`, `HexagramCategory`
  - `EmotionalVector` with `chaos|whimsy|darkTone|coherence|voiceWeight`
  - `HexagramState`, `EmotionalWeightEntry extends EmotionalVector + trainingNotes`
  - `TemporalReflection`
  - `OracleQuery`, `UserContext`
  - `TemporalState`
  - `ReflectionSet`
  - `OracleResponse`
  - `OracleConfig`
- Active dependents: all TS source files in workspace.

### `tests/oracle.test.ts`
- Validates workspace behavior/outputs using `node:test`.
- Asserts:
  - `hexagram_id` in `1..64`
  - `hexagram_name` non-empty
  - `past_reflection`, `present_reflection`, `future_reflection`, `unified_weave` non-empty
  - `action` in `ASSERT|YIELD|ADAPT|WAIT`
  - `category` in `sovereign|boundary|transformer|dissipator`
  - determinism across identical inputs and session ids
- Reactive dependent: executes on test runs; fails if table schema changes.

### `scripts/verify_registry.py`
- Validates `KING_WEN_TABLES.py` consistency.
- Reactive dependent: run during validation passes.

### `scripts/generate_*.py`
- Generates engine/parser/types/tests/deprecated artifacts from tables.
- Reactive dependents: run when regenerating artifacts from updated tables.

### `generate *.deprecated`
- Deprecated generated files.
- Do not use in active paths; only for reference if regeneration is needed.

### `src/hardware/`
- `KingWen9BitResolver.vhd`: 9-bit deterministic hardware resolver synthesizing ROM tables directly from `HEXAGRAM_BASE`.
- `KingWenExpected_pkg.vhd`: Full 512-state simulation expected vectors package.
- `tb_KingWen9BitResolver.vhd`: 512-address hardware testbench.
- `ConsensusAccumulator.vhd` & `DynamicEmotionalInputDerivator.vhd`: Hardware consensus & entropy derivators.

### `README.md`
- Documents the 6-Layer Deterministic Pipeline: Parse $\to$ Pool $\to$ Expand $\to$ Tag $\to$ Consensus $\to$ Telemetry.
- Documents 5 coprime prime extractor $(97, 89, 83, 79, 73)$ and 8-phase King Wen temporal math.
- Documents Dual Orthogonal Coordinates: 512 Binary Phase Space vs 729 Ternary Manifold vs 5,832 Full Resolved States.

### `package.json`
- Name: `king-wen-64-sovereign-model-engine` (v2.1.0)
- Scripts:
  - `build`: `tsc`
  - `test`: `node --test dist/tests/*.js`
  - `pipeline`: `python scripts/run_all_unified_pipeline.py`
  - `server`: `python expand_server.py`
  - `verify`: `npm run pipeline`
- Active dependents: build/test tooling.

### `tsconfig.json`
- TS config targeting `ES2022`, `NodeNext` module resolution.
- Includes `src/**/*` and `data/**/*`.
- Active dependents: TypeScript compilation pipeline.

---

## Active vs Reactive Toolchain Dependents

Active:
- `src/core/OracleEngine.ts` (Active input transformation + transparent relay)
- `src/parser/EmotionalParser.ts` (15-intent keyword dictionary + coprime prime hash)
- `src/utils/TemporalMath.ts` (8-phase King Wen temporal math)
- `src/utils/DeterministicHash.ts` (5 coprime prime extractors + SHA-256 inject hashing)
- `src/hardware/KingWen9BitResolver.vhd` (9-bit deterministic hardware resolver)
- `scripts/run_all_unified_pipeline.py` (Unified 18-stage pipeline)
- `expand_server.py` (Local HTTP expansion server)

Reactive:
- `scripts/verify_vhdl_resolver_parity.py`
- `scripts/verify_unbound_persona_domains.py`
- `scripts/verify_output_mismatches.py`
- `tests/oracle-runtime-audit.test.js`
