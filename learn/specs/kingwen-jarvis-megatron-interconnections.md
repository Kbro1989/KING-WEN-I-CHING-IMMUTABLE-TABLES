# King Wen / Jarvis / Megatron Interconnections Audit
Date: 2026-07-16
Scope: read-only audit of canonical live surfaces from immutable tables, OpenJarvis runtime, OpenJarvis audit sidecar, and Megatron training substrate.

## Source of truth
- King Wen engine: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\emotional_engine.py`
- Immutable tables: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py`
- OpenJarvis runtime: `C:\Users\krist\Desktop\OpenJarvis`
- Audit sidecar: `C:\Users\krist\Desktop\OpenJarvis`
- Megatron training: `C:\Users\krist\Desktop\Megatron-LM-review\kingwen_train_data`

## Verified live endpoints
- King Wen worker: `https://kingwen-oracle.kristain33rs.workers.dev/health`
- King Wen worker: `https://kingwen-oracle.kristain33rs.workers.dev/consult`
- King Wen worker: `https://kingwen-oracle.kristain33rs.workers.dev/tts`
- Local expand server: `http://127.0.0.1:8765/expand`

## King Wen local surfaces
- `emotional_engine.py`
  - `collapse_full_128(emotional_input, request_text)` expands all 64 hexagrams × 8 phases → 512 resolved states
  - `_tau_for_resolved(...)` uses vector base + inject-site porosity + line balance + slider factor + hex weight
  - `_compute_consensus_from_resolved(...)` returns consensus block with `consensus_hexagram_id`, `consensus_temporal`, `consensus_yao`, `consensus_vector`, `consensus_intent`, `consensus_explanation`
  - `capture_pre_slider(request_text)` returns full pre-slider expansion + resolved + consensus metadata
- `expand_server.py`
  - `POST /expand` accepts `emotional_input` and `session_id`
  - Response includes `total`, `emotional_input`, `session_id`, `source`, `expanded_count`, `resolved_count`, `resolved[]`, `consensus`
- `/learn` scripts:
  - `learn/scripts/test_collapse_full_128.py` — verified PASS at emotional_input=50
  - `learn/scripts/test_deterministic_replay.py` — verified PASS
  - `learn/scripts/test_porosity_sweep.py` — verified PASS
  - `learn/scripts/test_progressive_intents.py` — exits 0, currently DIAGNOSTIC because consensus is not slider-sensitive; known upstream lock, not test failure
  - `learn/scripts/audit_surfaces.py` — verified PASS; integration surface files exist and are nonzero
  - `learn/scripts/export_megatron_weights.py` — exports expanded/resolved/weights/consensus artifacts
- `/learn` artifacts:
  - `collapse_full_128_output.json` — canonical batch artifact with `expanded=64`, `resolved=512`
  - `kingwen_sections.jsonl` — section-level batch corpus
  - `DATASETS/` — dataset drift files including schema drift between immutable tables and master JSON

## OpenJarvis runtime surfaces
- `src/openjarvis/cli/_oracle_speak.py`
  - `/consult` → worker consult; `/tts` → worker vector TTS with compliance headers
  - `_kingwen_router()` returns mode/scenes/tool_hint + `vision_block` when consult includes parsed image data
  - `_play_audio_path(..., porosity=...)` supports porosity-gated playback routing via `winappaudiorouter` when available
  - `oracle_speak()` returns `director_payload` with scene description/visualPrompt/styleInfluence/prosody/voicePath/voiceStatus/imagePath + playback_instructions
- `src/openjarvis/cli/chat_cmd.py`
  - `/oracle`, `/counsel` render director payload before audio evidence
  - `/blueprint` maps to `/consult` agentic instruction flow
  - `/learn status|run|ingests` reads Hermes cache ledgers + `~/.openjarvis/learning` + `LearningOrchestrator`
  - `/journey lookup|replay|weave` uses `JourneyExecutor` against Hermes cache scripts
  - `/agents` lists `AgentRegistry` default + registered agents
- `src/openjarvis/cli/audio_dsp.py`
  - `modulate_with_headers(...)` applies edge DSP after worker TTS
- `src/openjarvis/core/journey_executor.py`
  - `lookup()` runs `journey_lookup.py`; emits `JOURNEY_ARRIVAL` and optional `LEARN_AUTO_INGEST`
  - `replay()` hydrates session dumps from `~/.hermes/sessions`
  - `weave()` runs `journey_weave.py`
- `src/openjarvis/learning/learning_orchestrator.py`
  - `run(agent_id=None)` mines traces, updates routing, evolves agent configs, and optionally runs LoRA/SFT training
- `src/openjarvis/tools/mcp_adapter.py`
  - MCP tool surface adapter for external schema execution
- `src/openjarvis/speech/backend_registry.py`
  - Backend descriptors: cloudflare_ai, cartesia, kingwen_worker, chatterbox, kokoro, qwen_custom_voice
- `src/openjarvis/learning/kingwen_pseudopod_ingest.py`
  - `KingWenPseudopodIngestor` writes pseudopod ingest JSONL from `TraceStore`
  - `CorpusIntegrityValidator` checks required keys across corpus files

## Megatron surfaces
- `kingwen_pretrain.jsonl` — primary training corpus
- `life_corpus_train.jsonl`, `combined_pretrain_train.jsonl`
- `runtime/kingwen_dataset.py` — domain-aware `SampleMeta` dataset runtime
- `build_usage_labels.py` — live trace ingestion into training labels
- `integrity_check.py` — corpus schema validation
- `model/jarvis-native-kingwen-life/{manifest.json, vocab_manifest.json, porosity_head.json, kingwen_curriculum.md}` — training manifests
- `wiki_math_research_batch_2026-07-11.json` / layer2 — wiki-math corpus for ingestion
- `rsmv_live_cache_tables.json`, `rsmv_kit_version_manifest.json`, `rsmv_common_structures.json` — RuneScape cache schema corpus

## Known gaps / exact targets
1. Consensus lock in `emotional_engine.py:_compute_consensus_from_resolved()` — identical output across `emotional_input=0..100`; variance source is in `_tau_for_resolved()` / line-state sampling, not `expand_server.py` serialization
2. `/journey` has no King Wen consult wiring; currently Avalokiteshvara text only
3. `prompt/builder.py` consult path may miss `emotional_input`; needs verification against `kingwen.py:consult()` required-arg contract
4. `combine_corpora.py` does not ingest `wiki_math_research_batch_*.jsonl` or `rsmv_*` tables from King Wen training data
5. `kingwen_pseudopod_ingest.py` is created but not wired into `/learn run` or CLI entrypoints
6. `backend_registry.py` is created but fallback selector not yet used in production TTS path
7. Mesh orphan: `dg-cartridge` skill lacks `related_skills` for wiki-math-parser / kingwen mesh
8. Immutable tables directory has drifted artifacts outside canonical `data/`, `scripts/`, `learn/`; `/learn` spec should treat only canonical tables as source of truth
