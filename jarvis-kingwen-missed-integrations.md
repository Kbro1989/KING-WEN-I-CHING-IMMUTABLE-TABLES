# King Wen Integration Gap Audit
Comparing:
- `C:\Users\krist\Desktop\king_wen_codebasemap.md`
- `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\king-wen-workflow-paths.md`
Against live repo: `C:\Users\krist\Desktop\OpenJarvis`

Rule: exact file paths, exact line numbers, no guessing, no fabrication.

---

## Critical typo correction
Both docs previously used `OpenJarvas`. Live repo is `OpenJarvis`. (Corrected.)
All paths below use `C:\Users\krist\Desktop\OpenJarvis`.

---

## Missed integration points

### 1. `prompt/builder.py` exact King Wen prompt injection contract
- Docs do not document this exact prompt-side wiring.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\prompt\builder.py`
- Lines 150-203
- Exact behavior:
  - builds `PromptSection(name="emotional_state", source="kingwen-emotion", ...)`
  - builds `PromptSection(name="voice_preset", source="kingwen-voice", ...)`
  - on provider error, builds `PromptSection(name="emotional_state", source="kingwen-emotion-error", ...)`
  - sets `_kingwen_voice_preset` from live provider output
- Gap: docs list `prompt/builder.py` but miss the exact section names/source labels and error path.

### 2. `agents/_stubs.py` exact agent-side King Wen state preservation
- Docs do not document this exact runtime wiring.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\_stubs.py`
- Lines 72, 78-83, 220, 258, 285-293
- Exact behavior:
  - `__init__` preserves `_emotion_provider`, `_capture_writer`, `_kingwen_session_id` with `hasattr` guards
  - `_build_capture_emotion()` calls `emotion_provider.consult()` and `voice_preset()`
  - `_build_kingwen_response_block()` appends live Oracle Console block
  - capture write logs King Wen metadata alongside inference telemetry
- Gap: docs list `_stubs.py` but miss the exact hasattr/guard pattern and capture write path.

### 3. `cli/ask.py` exact response append
- Docs do not document this exact return path.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\cli\ask.py`
- Line 467
- Exact behavior:
  - `return agent.run(query_text, context=ctx) + "\n\n" + getattr(agent, "_build_kingwen_response_block", lambda: "")()`
- Gap: docs list `ask.py` but miss the exact append expression.

### 4. `cli/chat_cmd.py` exact response append
- Docs do not document this exact REPL path.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\cli\chat_cmd.py`
- Lines 280-283
- Exact behavior:
  - `kingwen_block = agent._build_kingwen_response_block()`
  - `if kingwen_block: content = f"{content or ''}\n\n{kingwen_block}"`
- Gap: docs list `chat_cmd.py` but miss the exact REPL append path.

### 5. `agents/channel_agent.py` exact response append
- Docs do not document this exact channel path.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\channel_agent.py`
- Lines 138-140
- Exact behavior:
  - `kingwen_block = getattr(self._agent, "_build_kingwen_response_block", lambda: "")()`
  - `if kingwen_block: reply = f"{reply}\n\n{kingwen_block}"`
- Gap: docs list `channel_agent.py` but miss the exact channel append path.

### 6. `agents/morning_digest.py` exact loader and voice preset
- Docs do not document this exact digest/wiring path.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\morning_digest.py`
- Lines 21-47, 85-103
- Exact behavior:
  - `_load_kingwen_emotion_provider(config)` loads provider from `DigestConfig`
  - `_resolve_voice_preset(text)` calls `provider.consult(text="morning-digest")` and `provider.voice_preset(...)`
  - stores `voice_id`, `voice_speed`, `_last_emotion_payload`
- Gap: docs list `morning_digest.py` but miss the exact loader function and voice preset resolution path.

### 7. `sdk.py` and `system/orchestrator.py` exact wiring
- Docs do not document this exact runtime wiring.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\sdk.py`
- Lines 502-504
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\system\orchestrator.py`
- Lines 180-182
- Exact behavior:
  - `from openjarvis.agents.morning_digest import _load_kingwen_emotion_provider`
  - `emotion_provider = _load_kingwen_emotion_provider(self._config)` / `s.config`
- Gap: docs list `sdk.py` and `orchestrator.py` but miss the exact runtime wiring path.

### 8. `core/types.py` exact King Wen capture fields
- Docs do not document this exact type contract.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\core\types.py`
- Lines 198-208, 250-251
- Exact behavior:
  - `TelemetryRecord` fields: `hexagram_id`, `hexagram_category`, `hexagram_action`, `voice_weight`, `voice_backend`, `voice_id`, `voice_speed`, `emotional_deltas`, `kingwen_training_notes`, `kingwen_session_id`
  - `TraceStep` fields: `kingwen_session_id`
- Gap: docs list `core/types.py` but miss the exact King Wen metadata fields and their placement in telemetry.

### 9. `core/config.py` exact King Wen config schema
- Docs do not document this exact config schema.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\core\config.py`
- Lines 1512-1530
- Exact behavior:
  - `KingWenEmotionConfig.registry_path`
  - `KingWenEmotionConfig.weights_path`
  - `KingWenEmotionConfig.reflections_path`
  - `KingWenEmotionConfig.enabled`
- Gap: docs list `core/config.py` but miss the exact config class and field names.

### 10. `tests/agents/test_morning_digest.py` exact test contract
- Docs do not document this exact test contract.
- File: `C:\Users\krist\Desktop\OpenJarvis\tests\agents\test_morning_digest.py`
- Lines 67-125
- Exact behavior:
  - `DummyProvider` implements `consult(text, session_id)` returning `hexagram_id` and `emotional_deltas.voiceWeight`
  - `DummyProvider.voice_preset(tts_backend, voice_weight)` returns dict with `backend`, `voice_id`, `speed`
  - Asserts `agent._voice_id == "kingwen-voice"`, `agent._voice_speed == 1.05`, `agent._last_emotion_payload`
### 11. TS workspace is documented as consumed by OpenJarvis, but isn’t imported in OpenJarvis
- Docs claim `OpenJarvis/src/openjarvis/emotion/kingwen.py` consumes `src/core/OracleEngine.ts`.
- Actual code: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen.py` reads raw JSON tables only.
- No TS runtime import of `OracleEngine`, `NarrativeEngine`, `TemporalMath`, `DeterministicHash` exists in OpenJarvis.
- Gap: docs overstate the TS runtime dependency. The TS workspace is a source-of-truth table layer; the runtime consumption is Python-only in OpenJarvis.

### 12. Docs do not document `ollama_launch_cmd.py` `kingwen` task fit
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\cli\ollama_launch_cmd.py`
- Line 26
- Exact behavior:
  - `"kingwen": ("gemma4:latest", "qwen3.6:27b", "qwen2.5-coder:7b-instruct-q4_K_M")`
- Gap: docs list `ollama_launch_cmd.py` but miss the exact task-to-model mapping.

### 13. Resolved: Fake/default text fallback in kingwen.py
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen.py`
- Line 551-552
- Exact behavior:
  - Raises `ValueError` for empty text input (`if not text: raise ValueError(...)`) instead of defaulting to `"OpenJarvis session context"`.
- Gap: resolved in code but docs should record this validation behavior instead of the old fallback regression.

### 14. `get_kingwen_workspace_dir()` precedence not documented
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\core\paths.py`
- Lines 125-143
- Exact behavior:
  - `KING_WEN_IMMUTABLE_TABLES` env override
  - fallback: `Path.cwd().resolve()`
- Gap: docs mention path resolution but do not document the exact precedence or cwd fallback.

### 15. DB-backed Telemetry, Event Bus, and Managed Agent Persistence
- Docs do not document the telemetry and rehydration persistence surfaces.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\agents\manager.py`
- Lines 133, 604, 615, 619, 621, 632, 681, 683, 688, 690, 699
  - Persists `tool_calls_json` to local agent message history.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\traces\collector.py`
- Line 64
  - Persists telemetry event logs to SQLite TraceStore.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\server\agent_manager_routes.py`
  - Routes `/v1/managed-agents` endpoints for session state, messages, and learning rehydration.
- File: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\server\ws_bridge.py`
  - Routes `WS /v1/agents/events` for live streaming turn updates.

---

## Summary table

| Doc file | Missed exact point | Live repo path |
|---|---|---|
| `king_wen_codebasemap.md` | prompt/builder exact sections | `prompt/builder.py:150-203` |
| `king_wen_codebasemap.md` | `_stubs.py` exact guards/capture | `agents/_stubs.py:72,78-83,220,258,285-293` |
| `king_wen_codebasemap.md` | `ask.py` exact append | `cli/ask.py:467` |
| `king_wen_codebasemap.md` | `chat_cmd.py` exact append | `cli/chat_cmd.py:280-283` |
| `king_wen_codebasemap.md` | `channel_agent.py` exact append | `agents/channel_agent.py:138-140` |
| `king_wen_codebasemap.md` | `morning_digest.py` loader/voice | `agents/morning_digest.py:21-47,85-103` |
| `king_wen_codebasemap.md` | `sdk.py`/`orchestrator.py` wiring | `sdk.py:502-504`, `system/orchestrator.py:180-182` |
| `king_wen_codebasemap.md` | `core/types.py` fields | `core/types.py:198-208,250-251` |
| `king_wen_codebasemap.md` | `core/config.py` schema | `core/config.py:1512-1530` |
| `king_wen_codebasemap.md` | test contract | `tests/agents/test_morning_digest.py:67-125` |
| `king_wen_codebasemap.md` | TS runtime dependency overstated | no TS import in `OpenJarvis/src/openjarvis/emotion/kingwen.py` |
| `king-wen-workflow-paths.md` | repo name typo: `OpenJarvas` → `OpenJarvis` (corrected) | all OpenJarvis paths |
| `king-wen-workflow-paths.md` | `ollama_launch_cmd.py` kingwen task fit | `cli/ollama_launch_cmd.py:26` |
| `king-wen-workflow-paths.md` | `core/paths.py` precedence | `core/paths.py:125-143` |
| both | fake/default text fallback | `emotion/kingwen.py:60` |
| both | DB/trace/telemetry persistence surfaces | `agents/manager.py`, `traces/collector.py`, `server/agent_manager_routes.py`, `server/ws_bridge.py` |
