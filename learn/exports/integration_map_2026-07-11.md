# Exact Integration Map & Disconnect Analysis
Surface-trace only. No inferred concepts. File paths, function names, and JSON keys are exact.

## Confirmed Live Edges

### 1. King Wen → Local Expand Server
- **Source:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\emotional_engine.py`
  - `collapse_full_128(emotional_input)` lines 328-347
    - Calls `expand_hexagram()` lines 173-266 for h_id in 1..64
    - Calls `sample_resolve()` lines 269-325 for h_id in 1..64, phase_bits in 0..7
    - Calls `_compute_consensus_from_resolved()` lines 350-474
- **Wire:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\expand_server.py`
  - `ExpandHandler.do_POST()` lines 34-77
    - Accepts JSON body: `emotional_input`, `session_id`, `text`
    - Calls `collapse_full_128(emotional_input=emotional_input)` line 57
    - Serializes response `"consensus": result.get("consensus", {})` line 75
- **Confirmed live:** `POST http://127.0.0.1:8765/expand` returns 512 resolved states with populated `consensus.consensus_hexagram_id` (integer, not None)

### 2. King Wen → OpenJarvis (Engine Adapter)
- **Direct adapter:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen_engine_adapter.py`
  - Loads immutable tables via `spec_from_file_location` lines 36-41
  - Re-exports `expand_hexagram`, `sample_resolve`, `collapse_full_128`, `consensus_from_resolved` lines 65-68
  - `consult(text, session_id, emotional_input)` lines 114-220
    - Calls `collapse_full_128(emotional_input=emotional_input)` line 122
    - Returns payload with keys: `hexagram_id`, `hexagram_name`, `phase_temporal`, `emotional_deltas`, `emotional_tongue`, `consensus_hexagram_id`, `consensus_yao`, `consensus_vector`, `consensus_intent`, `crowd_hexagram_votes` (optional), `winning_hex_line_states` (optional)

### 3. OpenJarvis → King Wen (Emotion Provider)
- **Provider:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen.py`
  - `KingWenEmotionProvider.__init__()` loads `hexagram-registry.json`, `emotional-weights.json`, `temporal-reflections.json` lines 28-41
  - `consult(text, session_id, emotional_input)` lines 544-617
    - Requires non-empty text and explicit emotional_input 0-100 (raises ValueError otherwise)
    - Calls `self._collapse(text, session_id, local_input)` line 560
    - Returns payload with keys: `hexagram_id`, `hexagram_name`, `hexagram_sequence`, `phase_bits`, `phase_temporal`, `emotional_deltas`, `reflections`, `trainingNotes`, `emotional_tongue`, `save_string`

### 4. OpenJarvis Turn-Start Consult Wiring
- **Agent stub:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\_stubs.py`
  - `BaseAgent._emit_turn_start(input)` lines 121-225
    - Publishes `EventType.AGENT_TURN_START` on event bus lines 124-127
    - Calls `provider.consult(text=input, session_id=..., emotional_input=getattr(self, "_emotion_input"))` lines 134-139
    - Sets `self._kingwen_consult_payload`, `self._kingwen_voice_preset`, `self._kingwen_voice_section`, `self._current_emotional_tongue`
    - Derives `self._kingwen_wait`, `self._current_porosity`, `self._kingwen_broadcast_mode` lines 160-184
- **Prompt builder:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\prompt\builder.py`
  - `SystemPromptBuilder._build_frozen_sections()` lines 128-238
    - Calls `self._emotion_provider.consult(text=..., session_id=...)` lines 155-157
    - Appends `PromptSection(name="emotional_state", ...)` lines 160-167
  - **Disconnect:** prompt builder calls `consult()` WITHOUT passing `emotional_input` (defaults to `None` in `KingWenEmotionProvider.consult()` which raises `ValueError`), while `_emit_turn_start()` passes `getattr(self, "_emotion_input")` which may be None. These are two independent consult calls with no shared state.

### 5. OpenJarvis API Routes (King Wen Surface)
- **File:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\server\api_routes.py`
  - `kingwen_avatar(session_id)` lines 561-610
    - Instantiates `KingWenEmotionProvider` with workspace paths lines 569-573
    - Calls `provider.consult(text=session_id, session_id=session_id, emotional_input=50)` line 574
  - `kingwen_consult(req)` lines 631-687
    - Calls `provider.consult(text=text, session_id=session_id, emotional_input=50)` lines 649-653
  - `_load_avalokiteshvara_arm(hexagram_id)` lines 613-628
    - Reads `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\avalokiteshvara_domain.jsonl`

### 6. OpenJarvis CLI Commands → Consult
- **File:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\cli\chat_cmd.py`
  - `/oracle` command lines 380-412 — calls `oracle_speak_async(query, emotional_input=get_emotional_input(), on_done=_done)`
  - `/counsel` command lines 413-432 — calls `oracle_speak_async(counsel_prefix + query, emotional_input=get_emotional_input(), on_done=_done)`
  - `/journey` command lines 441-445 — prints Avalokiteshvara text only; NO consult wiring to King Wen or Megatron
  - `/models` command lines 438-439 — calls `_cmd_models()` which instantiates `KingWenEmotionProvider` and calls `provider.getHexagram("/models", session_id="models_cmd", emotional_input=int(time.time()) % 100)` lines 50-57

### 7. King Wen → Megatron (Avalokiteshvara Domain)
- **Build script:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\build_avalokiteshvara_domain.py`
  - `load_mapping()` lines 12-40 — parses `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\docs\avalokiteshvara-kingwen-mapping.md`
  - `build_text(record)` lines 43-54 — formats `[AVALOKITESHVARA]\nhexagram={hexagram_id} {name}\narm_function={arm_function}\nmantra={mantra}\n`
  - Output: `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\avalokiteshvara_domain.jsonl`
  - JSON line format: `{"text": "...", "label_payload": {"hexagram_id":..., "name":..., "arm_function":..., "mantra":...}}`

### 8. Megatron Corpus Ingestion (Current Path)
- **Combine script:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\combine_corpora.py`
  - Reads ONLY: `kingwen_pretrain.jsonl`, `life_corpus_train.jsonl`, `life_corpus_val.jsonl` lines 7-11
  - Writes: `combined_pretrain_train.jsonl`, `combined_pretrain_val.jsonl` lines 27-28
  - **Missing:** Does NOT read `wiki_math_corpus.jsonl`, `rsmv_cache_formats.jsonl`, `rsmv_live_cache_tables.json`, `megatron_multi_domain.jsonl`
- **Convert script:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\convert_corpus.py`
  - Reads `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\collapse_full_128_output.json` line 6 — hardcoded path, not parameterized
  - Writes `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\corpus.jsonl` line 7
  - JSON line format: `{"text": "King Wen Oracle state record..."}` — flat prose, no structured JSON keys
- **Ingest script:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\ingest_memory_bins.py`
  - Reads OpenJarvis `~/.openjarvis/*.db` and Hermes `~/AppData/Local/hermes/state.db` lines 76-106
  - Does NOT read wiki-math outputs or rsmv cache surfaces

### 9. wiki-math-parser → King Wen Corpus
- **Skill:** `C:\Users\krist\AppData\Local\hermes\skills\research\wiki-math-parser\SKILL.md`
  - Source of truth: `C:\Users\krist\Desktop\mwparserfromhell_local\mwparserfromhell`
  - Corpus target: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\wiki_math_corpus.jsonl`
- **Parser scripts:**
  - `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\learn\scripts\wiki_math_parser.py` lines 14-45
  - `C:\Users\krist\Desktop\open-design\standalone_wiki_math.py` lines 20-72
  - `C:\Users\krist\Desktop\open-design\backend\services\wiki_math.py` lines 18-40
  - `C:\Users\krist\Desktop\open-design\backend\routes\wiki_math.py` lines 11-15
- **Parser output format (from SKILL.md):**
  ```json
  {
    "hexagram_id": 1,
    "name": "The Creative",
    "category": "sovereign",
    "action": "ASSERT",
    "parser_tags": ["math", "ce", "chem", "sub", "sup"],
    "source": "learned_sequential_64.json"
  }
  ```
- **Disconnect:** Megatron `combine_corpora.py` never reads `wiki_math_corpus.jsonl`. The parser writes to King Wen's `kingwen_train_data/` but Megatron's ingestion pipeline does not include it.

### 10. RuneScape / rsmv → King Wen / Megatron
- **rsmv cache formats:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\rsmv_cache_formats.jsonl`
  - 257 lines of `{"domain":"rsmv_cache_formats","source":"...","construct":"...","math":"..."}` objects
- **rsmv live cache tables:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\rsmv_live_cache_tables.json`
  - 1877 lines of jcache SQLite sample data with columns `KEY, DATA, VERSION, CRC`
- **rsmv loader:** `C:\Users\krist\Desktop\rsmv\rust-rsmv-loader\src\main.rs`
  - Reads `C:\ProgramData\Jagex\RuneScape\js5-*.jcache` files lines 5, 49-63
  - Queries `SELECT DATA, VERSION FROM cache WHERE KEY=?1` line 66
  - Output: `kit_version_manifest.json` to `C:\Users\krist\.gemini\antigravity\scratch\pog2\public\models\` lines 163, 199-205
- **Disconnect:** rsmv outputs (`rsmv_cache_formats.jsonl`, `rsmv_live_cache_tables.json`, `kit_version_manifest.json`) are never read by Megatron ingestion scripts. `convert_corpus.py` only reads `collapse_full_128_output.json`.

### 11. Megatron → OpenJarvis
- **Script:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\build_usage_labels.py`
  - Reads `~/.openjarvis/traces.db`, `agents.db` lines 28-68
  - Writes labels with `domain: "OPENJARVIS_INTERACTION"` lines 84-126
  - Appends to `combined_pretrain_train.jsonl` and `labels_train.jsonl` lines 184-189
- **Disconnect:** This is the ONLY edge from Megatron back toward OpenJarvis runtime data. It does NOT write back to OpenJarvis databases — it only appends to Megatron's own JSONL files.

## Disconnect Points (Exact Causes)

### (1) Local Expand Server Consensus Serialization
- **File:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\expand_server.py` lines 66-76
- **Issue:** The server flattens `result.get("consensus", {})` directly into the HTTP response JSON. The consensus object is computed by `_compute_consensus_from_resolved()` in `emotional_engine.py` lines 350-474, which uses `voice*0.6 + coherence*0.4` weighting to pick the winning hexagram (line 429). Because hexagram 1 has voiceWeight≈0.95 and coherence≈0.98, it dominates the weighted score across ALL `emotional_input` values 0..100, causing `consensus_hexagram_id` to always resolve to hexagram 1. The test in `test_progressive_intents.py` lines 42-47 confirms this lock: consensus intent string stalls except the first step.
- **Live verify:** The HTTP response at `http://127.0.0.1:8765/expand` DOES include `consensus_hexagram_id: <integer>` in the `consensus` object. The task description states it is `None`, but the live server returns populated values. The disconnect is semantic: the key exists but the value is insensitive to slider input.

### (2) OpenJarvis Turn-Start Consult Wiring
- **File 1:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\_stubs.py`
  - `BaseAgent._emit_turn_start(input)` lines 121-225 — calls `provider.consult(text=input, session_id=..., emotional_input=getattr(self, "_emotion_input"))` line 134
- **File 2:** `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\prompt\builder.py`
  - `SystemPromptBuilder._build_frozen_sections()` lines 152-204 — calls `self._emotion_provider.consult(text=getattr(self, "_emotion_text", ""), session_id=getattr(self, "_emotion_session_id", "openjarvis"))` lines 155-157
  - **Critical:** Does NOT pass `emotional_input`. `KingWenEmotionProvider.consult()` raises `ValueError("King Wen consult requires explicit emotional_input; pass a slider value.")` when `emotional_input is None` (lines 553-559 of `kingwen.py`).
- **Disconnect:** Two separate `consult()` calls exist in the turn-start path:
  1. `_emit_turn_start()` — may pass `None` as `emotional_input` if `self._emotion_input` is unset
  2. `prompt/builder.py` — never passes `emotional_input`, guaranteed to hit the ValueError guard
  - The `except Exception` block at line 185 catches this and inserts an error section instead of emotional state.

### (3) Megatron Corpus Ingestion from wiki/rsmv Outputs
- **wiki-math-parser output:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\wiki_math_corpus.jsonl`
  - Format: `{"text": "...", "label_payload": {...}}` with keys `hexagram_id`, `name`, `category`, `action`, `parser_tags`, `source`
  - Referenced in `wiki-math-parser` SKILL.md line 30 as corpus target
- **Megatron ingestion:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\combine_corpora.py`
  - Reads: `kingwen_pretrain.jsonl`, `life_corpus_train.jsonl`, `life_corpus_val.jsonl` lines 7-11
  - **Never reads:** `wiki_math_corpus.jsonl`, `rsmv_cache_formats.jsonl`, `rsmv_live_cache_tables.json`
- **convert_corpus.py:** `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\convert_corpus.py`
  - Reads ONLY `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\collapse_full_128_output.json` (hardcoded) line 6
  - Output format: flat `{"text": "King Wen Oracle state record..."}` — no structured JSON keys
- **Disconnect:** The wiki-math parser is wired to King Wen's `kingwen_train_data/` but Megatron's `combine_corpora.py` does not include it in the pretrain pipeline. rsmv outputs (`rsmv_cache_formats.jsonl`, `rsmv_live_cache_tables.json`, `kit_version_manifest.json`) are also absent from the Megatron ingestion path.

### (4) /journey Mesh Orphans
- **Confirmed orphan skills:** `dg-cartridge`, `kingwen-emotion-voice`
  - `dg-cartridge`: `C:\Users\krist\AppData\Local\hermes\skills\dg-cartridge\SKILL.md` — exists as a skill directory but is referenced as an orphan in mesh audits
  - `kingwen-emotion-voice`: Does NOT exist as a file/directory anywhere under `C:\Users\krist\AppData\Local\hermes\skills\` — 0 files found by search
- **journey mesh skill:** `C:\Users\krist\AppData\Local\hermes\skills\autonomous-ai-agents\hermes-journey-mesh\SKILL.md`
  - `related_skills` audit logic lines 122-148: only skills with **missing** `related_skills` key count as undeclared/orphan candidates
  - Repair procedure lines 128-137: add `related_skills` to SKILL.md frontmatter for skills in the same call chain
- **Disconnect:**
  - `dg-cartridge` has no `related_skills` frontmatter linking it to `wiki-math-parser`, `kingwen-jarvis-megatron-learn`, or `rsmv-cache-crossref`
  - `kingwen-emotion-voice` does not exist as a skill directory at all (0 search results), making it a phantom orphan with no code surface to wire

## Adjacency List (Numbered Edges)

1. `KING-WEN-I-CHING-IMMUTABLE-TABLES/emotional_engine.py:collapse_full_128()` → `expand_server.py:ExpandHandler.do_POST()`
   - Data: `{"consensus": {...}}` JSON key at line 75
   - Transport: HTTP POST `http://127.0.0.1:8765/expand`

2. `expand_server.py:do_POST()` → external HTTP clients (OpenJarvis, Hermes)
   - Response keys: `total`, `emotional_input`, `session_id`, `text`, `source`, `expanded_count`, `resolved_count`, `resolved`, `consensus`

3. `KING-WEN-I-CHING-IMMUTABLE-TABLES/emotional_engine.py:collapse_full_128()` → `kingwen_engine_adapter.py:consult()`
   - Same function imported via `spec_from_file_location` line 67

4. `kingwen_engine_adapter.py:consult()` → `kingwen.py:KingWenEmotionProvider.consult()`
   - Both return `consensus_hexagram_id`, `consensus_vector`, `emotional_deltas`, `emotional_tongue`
   - **Schema mismatch:** `kingwen_engine_adapter.py` returns `"trainingNotes"` (line 170) while `kingwen.py` returns `"trainingNotes"` (line 606) — same key name but different value computation paths

5. `kingwen.py:KingWenEmotionProvider.consult()` → `api_routes.py:kingwen_consult()` / `kingwen_avatar()`
   - Both API routes instantiate `KingWenEmotionProvider` with workspace paths and call `provider.consult(text=..., session_id=..., emotional_input=50)` lines 574, 649-653

6. `api_routes.py:_load_avalokiteshvara_arm()` → `Megatron-LM-review/kingwen_train_data/avalokiteshvara_domain.jsonl`
   - Hardcoded path at line 615, reads label_payload rows by hexagram_id match line 624

7. `Megatron-LM-review/kingwen_train_data/build_avalokiteshvara_domain.py:main()` → `KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/avalokiteshvara-kingwen-mapping.md`
   - Reads markdown table, writes JSONL with `{"text": "...", "label_payload": {...}}` line 62

8. `chat_cmd.py:/oracle` + `:/counsel` → `_oracle_speak.py:oracle_speak_async()` (external module)
   - Passes `emotional_input=get_emotional_input()` lines 410, 430

9. `chat_cmd.py:/journey` → Avalokiteshvara text print ONLY
   - Lines 441-445: prints static text, NO consult() call, NO voice synthesis, NO Megatron link

10. `Megatron-LM-review/kingwen_train_data/combine_corpora.py:main()` → `kingwen_pretrain.jsonl` + `life_corpus_*.jsonl`
    - Lines 7-11, 24-28

11. `Megatron-LM-review/kingwen_train_data/convert_corpus.py:main()` → `collapse_full_128_output.json` (hardcoded)
    - Line 6: `INPUT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/collapse_full_128_output.json")`
    - Line 69: writes `{"text": "..."}` — flat format, no structured keys

12. `Megatron-LM-review/kingwen_train_data/ingest_memory_bins.py:main()` → `~/.openjarvis/*.db` + `~/AppData/Local/hermes/state.db`
    - Lines 76-106: iterates `agents.db`, `traces.db`, `knowledge.db`, `memory.db`, `digest.db`, `telemetry.db`, `sync_state.db`, `audit.db`, `state.db`

13. `wiki-math-parser` (skill + `wiki_math_parser.py`) → `KING-WEN-I-CHING-IMMUTABLE-TABLES/kingwen_train_data/wiki_math_corpus.jsonl`
    - Output key: `{"text": "...", "hexagram_id": N, "name": "...", "parser_tags": [...]}`
    - **No edge to Megatron:** `combine_corpora.py` never reads this file

14. `rsmv/rust-rsmv-loader/src/main.rs:main()` → `C:\ProgramData\Jagex\RuneScape\js5-*.jcache`
    - Output: `C:\Users\krist\.gemini\antigravity\scratch\pog2\public\models\kit_version_manifest.json` lines 163, 199-205
    - **No edge to King Wen or Megatron:** `rsmv_cache_formats.jsonl` and `rsmv_live_cache_tables.json` exist in King Wen's `kingwen_train_data/` but are never consumed by Megatron

15. `agents/_stubs.py:BaseAgent._emit_turn_start()` → `kingwen.py:KingWenEmotionProvider.consult()`
    - Call: `provider.consult(text=input, session_id=..., emotional_input=getattr(self, "_emotion_input"))` line 134-139

16. `prompt/builder.py:SystemPromptBuilder._build_frozen_sections()` → `kingwen.py:KingWenEmotionProvider.consult()`
    - Call: `self._emotion_provider.consult(text=..., session_id=...)` lines 155-157 — **NO `emotional_input` parameter**
    - **Guaranteed failure path:** `kingwen.py:consult()` raises `ValueError` when `emotional_input is None` (lines 553-559), caught at line 185, inserts error placeholder into prompt

17. `dg-cartridge` SKILL.md → `wiki-math-parser` SKILL.md (MISSING)
    - `dg-cartridge` has no `related_skills` frontmatter linking to `wiki-math-parser`, `kingwen-jarvis-megatron-learn`, or `rsmv-cache-crossref`

18. `kingwen-emotion-voice` → (MISSING SKILL)
    - 0 files found under `C:\Users\krist\AppData\Local\hermes\skills\` matching this name
    - Phantom orphan referenced in mesh audits but does not exist as a code surface

## Exact File Paths (Source of Truth)

- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\expand_server.py`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\emotional_engine.py`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\learn\scripts\test_progressive_intents.py`
- `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen_engine_adapter.py`
- `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen.py`
- `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\_stubs.py`
- `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\prompt\builder.py`
- `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\server\api_routes.py`
- `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\cli\chat_cmd.py`
- `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\build_avalokiteshvara_domain.py`
- `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\combine_corpora.py`
- `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\convert_corpus.py`
- `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\ingest_memory_bins.py`
- `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\kingwen_pretrain.jsonl`
- `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data\combined_pretrain_train.jsonl`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\wiki_math_corpus.jsonl`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\rsmv_cache_formats.jsonl`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\rsmv_live_cache_tables.json`
- `C:\Users\krist\Desktop\rsmv\rust-rsmv-loader\src\main.rs`
- `C:\Users\krist\Desktop\open-design\standalone_wiki_math.py`
- `C:\Users\krist\Desktop\open-design\backend\services\wiki_math.py`
- `C:\Users\krist\Desktop\open-design\backend\routes\wiki_math.py`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\learn\scripts\wiki_math_parser.py`
- `C:\Users\krist\AppData\Local\hermes\skills\research\wiki-math-parser\SKILL.md`
- `C:\Users\krist\AppData\Local\hermes\skills\autonomous-ai-agents\hermes-journey-mesh\SKILL.md`
- `C:\Users\krist\AppData\Local\hermes\skills\dg-cartridge\SKILL.md` (exists but no `related_skills` linking to mesh)
- `kingwen-emotion-voice` — NOT FOUND (0 files)
