# King Wen Workspace Codebasemap
Source of truth: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES`
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

### `README.md`
- Documents 9-bit state shell: 6-bit identity + 3-bit temporal.
- Documents pipeline: `1(state/question) -> 3(temporal) -> 64(hexagram|emotion) -> 3(temporal) -> 2(subsets) -> 1(resolve)`.
- Documents invariants and source-of-truth rule.

### `package.json`
- Name: `oracle-emotional-state-machine`
- Scripts:
  - `build`: `tsc`
  - `test`: `node --test dist/tests/*.js`
  - `demo`: `node scripts/demo.js`
  - `verify`: `python scripts/verify_registry.py && python scripts/run_all.py && npm test`
- Active dependents: build/test tooling.

### `tsconfig.json`
- TS config targeting `ES2022`, `NodeNext` module resolution.
- Includes `src/**/*` and `data/**/*`.
- Active dependents: TypeScript compilation pipeline.

### `src/__init__.py`, `data/__init__.py`
- Empty package markers.
- Active dependents: Python package resolution paths.

---

## Active vs Reactive Toolchain Dependents

Active:
- `src/core/OracleEngine.ts`
- `src/parser/NarrativeEngine.ts`
- `src/parser/EmotionalParser.ts`
- `src/utils/TemporalMath.ts`
- `src/utils/DeterministicHash.ts`
- `src/types/oracle.ts`
- OpenJarvis `emotion/kingwen.py`
- OpenJarvis `agents/_stubs.py`
- OpenJarvis `prompt/builder.py`
- OpenJarvis CLI response paths (`ask.py`, `chat_cmd.py`, `channel_agent.py`)
- `ollama_launch_cmd.py` task fit (`kingwen`)

Reactive:
- `scripts/verify_registry.py`
- `scripts/generate_*.py`
- `tests/oracle.test.ts`
- deprecated generator outputs
