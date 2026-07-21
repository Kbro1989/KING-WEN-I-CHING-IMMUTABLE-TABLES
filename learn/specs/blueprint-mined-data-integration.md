# /blueprint — Mined Data Integration Map

Generated: 2026-07-14
Sources: ishandutta2007 (2054 repos), StepFun AI (32 repos), NVIDIA (764 repos), transformer-circuits.pub/2026/workspace
Verified artifacts: `kingwen_corpus_staging/manifest.json` (20 entries, all size-verified)

## How to read this blueprint

Each entry maps a **verified on-disk artifact** to an **exact integration point** in the
King Wen / Jarvis / Megatron / Voice stack. No speculative wiring; every target path
is taken from live source code or confirmed skill contracts.

Legend:
- `P1` = immediate, unblocked
- `P2` = high value, minor dependency
- `P3` = useful, deferred OK
- `P4` = reference only

---

## 1. Voice / Prosody / TTS

### Step-Audio2 voice configs
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|
| `flashcosyvoice/config.py` | `mine/stepfun/Step-Audio2-real/flashcosyvoice/config.py` | `src/openjarvis/speech/cartesia_adapter.py` speed/emotion mapping | Replace hardcoded Option B speed formula with Step-Audio2 `SamplingParams` trajectory deltas | P1 |
| `flashcosyvoice/cli.py` | `mine/stepfun/Step-Audio2-real/flashcosyvoice/cli.py` | `src/openjarvis/cli/_oracle_speak.py` `_tts_worker_with_vector()` | Use Step-Audio2 speaker embedding prompt pattern for `speaker_rep.pt` conditioning | P1 |
| `flashcosyvoice/modules/flow.py` | `mine/stepfun/Step-Audio2-real/flashcosyvoice/modules/flow.py` | `CartesiaAdapter.synthesize()` condition projection | Map `spks` tensor conditioning to 5-axis vector → discrete emotion tag pipeline | P2 |
| `assets/default_female.wav` | `mine/stepfun/Step-Audio2-real/assets/default_female.wav` | `_oracle_speak.py` `SPEAKER_MAP` reference voices | Add StepFun default voices as Cartesia speaker fallbacks | P2 |
| `assets/default_male.wav` | `mine/stepfun/Step-Audio2-real/assets/default_male.wav` | `_oracle_speak.py` `SPEAKER_MAP` reference voices | Add StepFun default voices as Cartesia speaker fallbacks | P2 |

### Step-Audio-R1 inference wiring
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `examples-vllm_r1.py` | `mine/stepfun/Step-Audio-R1-sparse/examples-vllm_r1.py` | `src/openjarvis/speech/cartesia_tts.py` backend selection | Add vLLM-hosted Step-Audio-R1 as a TTS backend option | P2 |
| `stepaudior1vllm.py` | `mine/stepfun/Step-Audio-R1-sparse/stepaudior1vllm.py` | `src/openjarvis/speech/` new `stepfun_r1_tts.py` | Prosthetic adapter for Step-Audio-R1 vLLM runtime | P2 |

### Step-Audio-R1.1 streaming + quantization
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `app.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/app.py` | `src/openjarvis/speech/cartesia_tts.py` backend selection | Flask API exposing s2t/understand/translate/summarize/asr modes via Step-Audio-R1.1 | P1 |
| `examples-vllm_r1.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/examples-vllm_r1.py` | `src/openjarvis/speech/` new `stepfun_r1_tts.py` | vLLM streaming examples with exact sampler params: temperature=0.7, repetition_penalty=1.0/1.07, stop_token_ids=[151665], max_tokens=32000 | P1 |
| `mcp_server.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/mcp_server.py` | `src/openjarvis/tools/mcp_adapter.py` | exposes Step-Audio-R1.1 as MCP tool: process_audio, audio_info | P2 |
| `int4_server.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/int4_server.py` | `src/openjarvis/speech/` quantized inference path | INT4 quantized Step-Audio-R1.1 inference server for edge deployment | P2 |
| `quantize_gptq.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/quantize_gptq.py` | `src/openjarvis/speech/` model packaging | GPTQ quantization recipe for voice adapter | P3 |
| `quantize_gptq_v2.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/quantize_gptq_v2.py` | `src/openjarvis/speech/` model packaging | GPTQ v2 quantization recipe | P3 |
| `quantize_bnb.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/quantize_bnb.py` | `src/openjarvis/speech/` model packaging | bitsandbytes quantization recipe | P3 |
| `smart_audio_processor.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/smart_audio_processor.py` | `src/openjarvis/cli/audio_dsp.py` | smart audio pipeline for pre-DSP conditioning | P2 |
| `long_audio_processor.py` | `mine/stepfun-ssh/Step-Audio-R1.1-ssh/long_audio_processor.py` | `src/openjarvis/cli/audio_dsp.py` | long-audio chunking/pipeline for extended oracle speech | P2 |

### xVA-Synth voice assets
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `python/xvapitch/speaker_rep/speaker_rep.pt` | `mine/ishandutta/xVA-Synth/xVA-Synth-master/python/xvapitch/speaker_rep/speaker_rep.pt` | `src/openjarvis/speech/cartesia_adapter.py` vector resolution | Train speaker-conditioned voice model on 42.5 MB xVA speaker reps | P1 |
| `arpabet/cmudict.json` | `mine/ishandutta/xVA-Synth/xVA-Synth-master/arpabet/cmudict.json` | `src/openjarvis/cli/audio_dsp.py` phoneme alignment | Map CMU phonemes to King Wen yao-state timing for prosodic rendering | P2 |
| `arpabet/xvasynth.json` | `mine/ishandutta/xVA-Synth/xVA-Synth-master/arpabet/xvasynth.json` | `src/openjarvis/cli/audio_dsp.py` custom phoneme set | Game-character voice fingerprinting for avatar voice selection | P3 |

### RadTTs / Mellotron reference
| Artifact | GitHub raw URL | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `NVIDIA/radtts` repo | `https://github.com/NVIDIA/radtts` | `src/openjarvis/speech/` | RADTTS prosody control: duration/pitch/energy conditioning | P3 |
| `NVIDIA/mellotron` repo | `https://github.com/NVIDIA/mellotron` | `src/openjarvis/speech/` | Mellotron GST-style style tokens for voiceWeight→style mapping | P3 |

---

## 2. LLM Training / Megatron Corpus

### ChatRWKV tokenizer + vocab
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `20B_tokenizer.json` | `mine/ishandutta/ChatRWKV-main/20B_tokenizer.json` | `Megatron-LM-review/kingwen_train_data/model/local-tokenizer/` | RWKV 20B tokenizer as fallback when GPT-2 BPE unavailable offline | P2 |
| `rwkv_vocab_v20230424.txt` | `mine/ishandutta/ChatRWKV-main/rwkv_vocab_v20230424.txt` | `build_tokenizer_offline.py` vocab source | 1 GB vocab text for numpy-only tokenizer rebuild on Windows | P2 |
| `misc/lambada_test.jsonl` | `mine/ishandutta/ChatRWKV-main/misc/lambada_test.jsonl` | `kingwen_train_data/combined_pretrain_val.jsonl` append | Lambada benchmark as validation set mix-in for reasoning eval | P3 |

### Megatron training pipeline
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `tools/preprocess_data.py` | `mine/nvidia/megatron-lm-main/tools/preprocess_data.py` | `kingwen_train_data/tokenize_for_megatron.py` | Replace numpy-only tokenizer with official Megatron preprocessor when WSL available | P2 |
| `cosmos` prompt datasets | `mine/nvidia/cosmos-main/evaluation/.../t2v_prompts.json` | `kingwen_train_data/scene_prompts/` | Text-to-video prompts as sovereign pipeline scene generation seeds | P3 |

### Quill-NLP corpus
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `README.md` | `mine/ishandutta/Quill-NLP/Quill-NLP-Tools-and-Datasets-master/README.md` | `build_usage_labels.py` new domain | 100k Wikipedia sentences domain label: `[QUILL_WIKI]` | P3 |
| `vocabindex.csv` | `mine/ishandutta/Quill-NLP/Quill-NLP-Tools-and-Datasets-master/vocabindex.csv` | `kingwen_train_data/model/jarvis-native-kingwen-life/vocab_manifest.json` | Extend vocab manifest with Quill NLP vocabulary index | P4 |

### ChatRTX RAG + inference
| Artifact | Local path | Integration point | What it enables | Priority |
|---|---|---|---|---|
| `ChatRTX_APIs/ChatRTX/chatrtx_rag.py` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/chatrtx_rag.py` | `src/openjarvis/tools/mcp_adapter.py` | LlamaIndex RAG pipeline: `SimpleDirectoryReader`, `VectorStoreIndex`, `HuggingFaceEmbedding`, `load_index_from_storage` | P1 |
| `ChatRTX_APIs/ChatRTX/config/app_config.json` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/config/app_config.json` | `src/openjarvis/tools/mcp_adapter.py` embedding config | `embedded_model=intfloat/multilingual-e5-base`, `embedded_dimension=768` | P1 |
| `ChatRTX_APIs/ChatRTX/config/config.json` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/config/config.json` | `src/openjarvis/server/api_routes.py` model catalog | Llama-3.1-8B-Instruct, Mistral-7B-Int4, LLaMA2-13B; TRTLLM engine build commands; NIM IDs | P2 |
| `ChatRTX_APIs/ChatRTX/chatrtx.py` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/chatrtx.py` | `src/openjarvis/core/env_integration.py` model loader pattern | TRTLLM/NIM model init, engine/tokenizer/vocab path resolution | P2 |
| `ChatRTX_APIs/ChatRTX/model_manager/model_manager.py` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/model_manager/model_manager.py` | `src/openjarvis/core/model_registry.py` | model download/install/verify logic for TRTLLM/NIM backends | P3 |
| `ChatRTX_APIs/ChatRTX/examples/clip.py` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/examples/clip.py` | `src/openjarvis/tools/` vision tool | CLIP image-text retrieval example | P3 |
| `ChatRTX_APIs/ChatRTX/inference/trtllm/trtllm.py` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/ChatRTX/inference/trtllm/trtllm.py` | `src/openjarvis/speech/cartesia_tts.py` backend fallback | TRTLLM inference backend pattern for local voice model serving | P3 |
| `ChatRTX_APIs/ChatRTX/dist/tensorrt_llm-0.9.0-cp310-cp310-win_amd64.whl` | `mine/nvidia-ssh/ChatRTX-ssh/ChatRTX_APIs/dist/tensorrt_llm-0.9.0-cp310-cp310-win_amd64.whl` | offline install for TRTLLM | prebuilt TRTLLM wheel for Windows/Python 3.10 | P4 |

---

## 3. King Wen Engine Upgrades

### Consensus engine repair
| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `emotional_engine.py: _tau_for_resolved()` | Increase `emotional_input` weight from 0.2 to ≥0.5; inject `inject_site.porosity_norm` + `EMOTIONAL_WEIGHTS[str(h_id)]` | Slider-sensitive consensus across 0..100 | P1 |
| `emotional_engine.py: _compute_consensus_from_resolved()` | Replace `voiceWeight*0.6 + coherence*0.4` with open-pool surface: primary/secondary pool vectors + porosity window + yin/yang/yao balance | Distinct consensus per emotional_input step | P1 |
| `expand_server.py` | Serialize full `consensus` block into HTTP `/expand` JSON | HTTP callers see open consensus output | P1 |

### 16-phase expansion target
| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `emotional_engine.py: collapse_full_128()` | Extend from 8 phases per hex to 16 phases when 2× expansion requested | Double state coverage for training | P2 |
| `learn/scripts/test_collapse_full_1024.py` | Update assertion from `total_resolved == 1024` to match actual phase count | Test passes after engine upgrade | P2 |

---

## 4. OpenJarvis Runtime Wiring

### Missing `emotional_input` propagation
| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `src/openjarvis/prompt/builder.py` consult call sites | Pass `emotional_input=get_emotional_input()` into `consult()` | Eliminates ValueError when `emotional_input is None` | P1 |
| `src/openjarvis/server/api_routes.py: /v1/kingwen/consult` | Accept `emotional_input` from request body instead of hardcoding 50 | Live slider control via HTTP | P1 |

### `/journey` → King Wen consult
| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `src/openjarvis/cli/chat_cmd.py: /journey` | Wire `/journey` to `kingwen_engine_adapter.consult()` | Journey lookup returns live hexagram state, not static Avalokiteshvara text | P2 |
| `src/openjarvis/tools/kingwen_consensus_tailer.py` | Subscribe to `KINGWEN_CONSENSUS_UPDATE` events | Workflow engine routes by consensus delta | P2 |

---

## 5. Cartesia Voice Adapter Upgrades

### Step-Audio2 schema alignment
| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `src/openjarvis/speech/cartesia_adapter.py: CartesiaAdapter.synthesize()` | Map Step-Audio2 `spks` speaker tensor to `vector` input via trained projection | Speaker-conditioned voice output | P1 |
| `src/openjarvis/speech/cartesia_adapter.py: Option B speed formula` | Replace `trajectory_delta + emotional_velocity * 0.1` with Step-Audio2 `SamplingParams.temperature/top_k/tau_r` modulation | Dynamic speed derived from actual TTS config | P2 |

### xVA-Synth phoneme conditioning
| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `src/openjarvis/cli/audio_dsp.py` | Load `cmudict.json` phoneme durations; map yao-state timing to phoneme boundaries | Prosody timing grounded in phoneme data | P2 |
| `src/openjarvis/speech/cartesia_adapter.py` | Use `xvasynth.json` custom phoneme set for game-character voice fingerprints | Avatar voice selection by hexagram category | P3 |

---

## 6. Avalokiteshvara Domain

| Target file | Exact change | Enables | Priority |
|---|---|---|---|
| `Megatron-LM-review/kingwen_train_data/avalokiteshvara_domain.jsonl` | Append 64-arm registry from `docs/avalokiteshvara-kingwen-arms.json` | Train model on compassionate-reconfiguration mapping | P2 |
| `src/openjarvis/cli/chat_cmd.py: /journey` | Render avalokiteshvara arm record per consultation | 64-arm output with mantra/mudra/face/direction | P3 |

---

## 7. NVIDIA Quantum / Inference

| Artifact | Integration point | What it enables | Priority |
|---|---|---|---|
| `TransformerEngine` code | `kingwen_train_data/runtime/kingwen_dataset.py` domain-aware loader | FP8/quantized training for King Wen dataset when GPU available | P3 |
| `cosmos` prompt datasets | `kingwen_train_data/scene_prompts/` | Physical AI world-model prompts for sovereign pipeline scene generation | P4 |
| `Model-Optimizer` quantization configs | `cartesia_adapter.py` INT4/INT8 voice model path | Quantized voice adapter for edge deployment | P4 |

---

## 9. Transformer Circuits / J-Lens Global Workspace

Source: `https://transformer-circuits.pub/2026/workspace/index.html`
Paper: "Verbalizable Representations Form a Global Workspace in Language Models"

### Key findings
- J-lens identifies privileged internal representations (J-space) that are verbalizable, directionally modulatable, and used for internal reasoning
- J-space is sparse: only 6-7% of concept variance, limited to subset of layers, capacity-limited
- Counterfactual reflection training implants ethical principles into workspace by training model to articulate principles if interrupted
- J-space ablation reverts behavioral improvements, proving workspace governs silent reasoning
- Post-training causes J-space to acquire Assistant's "point of view"

### Integration points

| Target file | Exact change | What it enables | Priority |
|---|---|---|---|
| `emotional_engine.py: collapse_full_128()` | Add J-space pruning: only top-k=25 resolved states carry into consensus, matching J-lens sparsity | Reduce 512-state consensus to privileged subset matching LLM global workspace | P1 |
| `emotional_engine.py: _compute_consensus_from_resolved()` | Apply J-lens-style sparse decomposition: solve for sparse non-negative combination of top-k emotional vectors | Consensus derived from verbalizable emotional directions, not average | P1 |
| `kingwen_train_data/runtime/kingwen_dataset.py` | Add `j_space_component` field to `SampleMeta` | Track which training samples map to privileged emotional vectors | P2 |
| `src/openjarvis/emotion/kingwen_engine_adapter.py` | Expose `j_space_top_tokens` from consult payload | Surface verbalizable emotional concepts to Jarvis prompt builder | P2 |
| `kingwen_train_data/kingwen_pretrain.jsonl` | Append J-lens reflection training examples | Train model to articulate emotional principles before acting | P3 |

### J-space alignment with King Wen architecture

| J-lens concept | King Wen equivalent |
|---|---|
| J-space | consensus pool (privileged subset of 512 states) |
| J-lens vectors | emotional vectors from EMOTIONAL_POOL |
| Sparse k=25 | porosity-filtered resolved states |
| Verbalizable representations | yao-state vocabulary (9-item tongue) |
| Counterfactual reflection training | pre-slider / post-slider capture |
| Steering along J-lens vector | emotional_input modulation |
| Ablation reverts behavior | consensus lock when slider inactive |

---

## 10. Missing / Deferred

| Artifact | Blocker | Next step |
|---|---|---|
| `stepfun-ai/Step-Audio-R1` full codebase | 376 MB codeload timeout; disk pressure | Retry from WSL or split download |
| `NVIDIA/TensorRT-LLM` | GitHub API 403 from this host | Proxy via web search or WSL git |
| `NVIDIA/ChatRTX` | Codeload 404 | Repo may be private/renamed; skip |
| `transformers` in current venv | `integrity_check.py` blocked | `pip install transformers` or switch to WSL venv |
| `query_layer_probe.py` emotional_input variance | Consensus lock upstream | Fix `_tau_for_resolved()` first |

---

## Execution order recommendation

```
Phase 1 (unblock):
  1. Fix _tau_for_resolved() weighting
  2. Wire emotional_input through prompt/builder.py
  3. Map Step-Audio2 SamplingParams to Option B speed formula
  4. Train speaker projection from xVA-Synth speaker_rep.pt
  5. Add J-space pruning to collapse_full_128()

Phase 2 (high value):
  6. Extend collapse_full_128 to 16 phases
  7. Wire /journey to King Wen consult
  8. Add xVA-Synth phoneme data to audio_dsp.py
  9. Add ChatRWKV tokenizer as offline fallback
  10. Add J-lens sparse decomposition to consensus engine

Phase 3 (training):
  11. Ingest Quill-NLP + Lambada into corpus
  12. Build avalokiteshvara_domain.jsonl from arms registry
  13. Append J-lens reflection training examples
  14. Rebuild .bin/.idx with updated tokenizer
  15. Run integrity_check.py end-to-end

Phase 4 (reference):
  16. NVIDIA TransformerEngine/Model-Optimizer paths for quantized voice
  17. Cosmos prompts for scene generation
  18. Retry Step-Audio-R1 full repo from alternate network
  19. Mine additional transformer-circuits.pub papers for circuit-level insights
```
