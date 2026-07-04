# King Wen Workflow Paths
Plugin artifact POV for `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES`

Model: every file is an artifact/plugin with:
- artifact id
- role
- inputs
- outputs
- active consumers
- reactive dependents
- hard rules

No guessing. Paths are exact. Consumers are exact.

---

## Artifact Index

### `data/hexagram-registry.json`
- Artifact id: `hexagram-registry`
- Role: 64-hex identity table
- Inputs: none; source of truth
- Outputs: registry records consumed by runtime
- Active consumers:
  - `src/core/OracleEngine.ts`
  - `src/parser/NarrativeEngine.ts`
  - `OpenJarvas/src/openjarvis/emotion/kingwen.py`
- Reactive dependents: generator scripts, deprecated mirrors

### `data/emotional-weights.json`
- Artifact id: `emotional-weights`
- Role: 64 emotional-delta table
- Inputs: none; source of truth
- Outputs: weights consumed by runtime
- Active consumers:
  - `src/core/OracleEngine.ts`
  - `src/parser/NarrativeEngine.ts`
  - `OpenJarvas/src/openjarvis/emotion/kingwen.py`
- Reactive dependents: generator scripts, deprecated mirrors

### `data/temporal-reflections.json`
- Artifact id: `temporal-reflections`
- Role: 64 temporal-reflection triple table
- Inputs: none; source of truth
- Outputs: reflections consumed by runtime
- Active consumers:
  - `src/core/OracleEngine.ts`
  - `src/parser/NarrativeEngine.ts`
  - `OpenJarvas/src/openjarvis/emotion/kingwen.py`
- Reactive dependents: generator scripts, deprecated mirrors

### `KING_WEN_TABLES.py`
- Artifact id: `python-registry`
- Role: Python verification entrypoint
- Inputs: none
- Outputs: verification asserts, console output
- Active consumers:
  - `scripts/verify_registry.py`
- Reactive dependents: any Python inspection path

### `src/index.ts`
- Artifact id: `ts-public-surface`
- Role: public export surface
- Inputs: `src/core/OracleEngine.ts`, `src/parser/*`, `src/utils/*`, `src/types/oracle.ts`
- Outputs: exports for TS consumers
- Active consumers:
  - any TS code importing from `src/`

### `src/core/OracleEngine.ts`
- Artifact id: `oracle-engine`
- Role: consultation runtime
- Inputs:
  - `data/hexagram-registry.json`
  - `data/emotional-weights.json`
  - `data/temporal-reflections.json`
  - `src/parser/EmotionalParser.ts`
  - `src/parser/NarrativeEngine.ts`
  - `src/utils/DeterministicHash.ts`
  - `src/utils/TemporalMath.ts`
- Outputs: `OracleResponse`
- Active consumers:
  - `OpenJarvas/src/openjarvis/emotion/kingwen.py`
- Reactive dependents: tests, deprecated mirrors

### `src/parser/EmotionalParser.ts`
- Artifact id: `emotional-parser`
- Role: query -> emotional vector
- Inputs: `OracleQuery.user_context`, `OracleQuery.emotional_input`
- Outputs: `EmotionalVector`
- Active consumers:
  - `src/core/OracleEngine.ts`

### `src/parser/NarrativeEngine.ts`
- Artifact id: `narrative-engine`
- Role: reflection + unified weave generation
- Inputs:
  - `data/temporal-reflections.json`
  - `data/emotional-weights.json`
  - `HexagramState`
  - `TemporalState`
  - `EmotionalVector`
- Outputs: `ReflectionSet`
- Active consumers:
  - `src/core/OracleEngine.ts`

### `src/utils/TemporalMath.ts`
- Artifact id: `temporal-math`
- Role: temporal phase computation
- Inputs: `tick`, `emotionalInput`
- Outputs: `TemporalState`
- Active consumers:
  - `src/core/OracleEngine.ts`
  - `src/utils/DeterministicHash.ts` indirectly via router

### `src/utils/DeterministicHash.ts`
- Artifact id: `deterministic-hash`
- Role: SHA-256 based deterministic selection
- Inputs: `tick`, `sessionId`, `previousHex`, `selector`
- Outputs: `1..64` hexagram id
- Active consumers:
  - `src/core/OracleEngine.ts`

### `src/types/oracle.ts`
- Artifact id: `oracle-types`
- Role: type definitions
- Inputs: none
- Outputs: interfaces/types
- Active consumers:
  - all TS source files in workspace

### `tests/oracle.test.ts`
- Artifact id: `oracle-tests`
- Role: validation suite
- Inputs:
  - `src/core/OracleEngine.ts`
  - `data/hexagram-registry.json`
  - `data/emotional-weights.json`
  - `data/temporal-reflections.json`
- Outputs: pass/fail assertions
- Active dependents: test runner
- Reactive dependents: schema changes

### `scripts/verify_registry.py`
- Artifact id: `registry-verifier`
- Role: validate `KING_WEN_TABLES.py`
- Inputs: `KING_WEN_TABLES.py`
- Outputs: asserts/console
- Reactive dependents: validation passes

### `scripts/generate_*.py`
- Artifact id: `artifact-generators`
- Role: generate engine/parser/types/tests/deprecated artifacts
- Inputs: `KING_WEN_TABLES.py`
- Outputs: generated files
- Reactive dependents: table updates

### `README.md`
- Artifact id: `workspace-readme`
- Role: documentation
- Inputs: none
- Outputs: markdown
- Active dependents: humans, plugin loaders

### `package.json`
- Artifact id: `workspace-package`
- Role: build/test metadata
- Inputs: none
- Outputs: scripts
- Active dependents: `npm run build`, `npm test`

### `tsconfig.json`
- Artifact id: `workspace-tsconfig`
- Role: TS compilation config
- Inputs: none
- Outputs: `dist/`
- Active dependents: `tsc`

---

## Plugin Workflow Paths

### Active workflow 1: Consultation
1. `OpenJarvas/src/openjarvis/emotion/kingwen.py` loads:
   - `data/hexagram-registry.json`
   - `data/emotional-weights.json`
   - `data/temporal-reflections.json`
2. Calls `consult(text, session_id, emotional_input)`
3. Returns payload with:
   - `hexagram_id`, `hexagram_name`, `hexagram_unicode`, `binary`, `upper_trigram`, `lower_trigram`, `category`, `action`
   - `emotional_deltas.chaos/whimsy/darkTone/coherence/voiceWeight`
   - `reflections.past/present/future`
   - `trainingNotes`
4. Active consumers append payload to:
   - prompt sections via `OpenJarvas/src/openjarvis/prompt/builder.py`
   - response Oracle Console via `OpenJarvas/src/openjarvis/agents/_stubs.py`
   - CLI response via `OpenJarvas/src/openjarvis/cli/ask.py`
   - chat REPL response via `OpenJarvas/src/openjarvis/cli/chat_cmd.py`
   - channel response via `OpenJarvas/src/openjarvis/agents/channel_agent.py`

### Active workflow 2: Morning digest voice
1. `OpenJarvas/src/openjarvis/agents/morning_digest.py` loads provider via `_load_kingwen_emotion_provider(config)`
2. Calls `provider.consult(text="morning-digest", session_id="morning-digest")`
3. Calls `provider.voice_preset(tts_backend, voice_weight)`
4. Stores `voice_id` and `speed` on agent instance
5. `OpenJarvas/src/openjarvas/system/orchestrator.py` and `OpenJarvas/src/openjarvas/sdk.py` wire provider when `digest.emotion_enabled` is true

### Active workflow 3: Deterministic selection in TS runtime
1. `src/core/OracleEngine.ts` loads tables into maps
2. `consult(query)` calls `EmotionalParser.parse(query)`
3. `computeTemporalPhase(tick, emotional_input)`
4. `deterministicHexagramSelect(tick, session_id, previousHex, selector)`
5. Returns `OracleResponse` with reflections and emotional deltas

### Reactive workflow 1: Verification
1. `scripts/verify_registry.py` reads `KING_WEN_TABLES.py`
2. Validates uniqueness, inversion pairs, complementary pairs
3. Outputs pass/fail

### Reactive workflow 2: Regeneration
1. `scripts/generate_*.py` read `KING_WEN_TABLES.py`
2. Generate engine/parser/types/tests/deprecated artifacts
3. Run when tables are updated

---

## Hard Rules

- No hardcoded absolute King Wen paths.
- Only `KING_WEN_IMMUTABLE_TABLES` env override is allowed.
- All usages must pass the live King Wen prompt/tables expected by the workspace API.
- Zero mock/stub/fabrication allowed in King Wen integration paths.
- Plugin artifacts must not duplicate tables; they must consume the source-of-truth JSON files.
