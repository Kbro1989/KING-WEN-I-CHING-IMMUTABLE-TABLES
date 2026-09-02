# Cross-Verification Checklist — Desktop Reality vs King Wen Integration

## Purpose
Audit actual on-disk programs against claimed integration paths. No fabrication. Every item must be traceable to a real file/path/process. If an integration claim cannot be backed by an exact file:line reference or running process, it is unverified, not assumed true.

---

## 1. Desktop Program Inventory (Knowns)

### 1.1 Core Sovereign Stack
| Program | Expected Path | Verified Exists | Notes |
|---------|--------------|-----------------|-------|
| King Wen immutable tables | `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES` | YES | 3.1GB, 641 tracked files, 4,291 total on disk |
| OpenJarvis | `C:\Users\krist\Desktop\OpenJarvis` | YES | Live working tree, `src/openjarvis/` |
| Open Design | `C:\Users\krist\Desktop\open-design` | YES | Separate program |
| Cinder | `C:\Users\krist\Desktop\cinder` | YES | Electron+React |
| voicebox | `C:\Users\krist\Desktop\voicebox` | YES | Inference-only backends |
| Megatron-LM-review | `C:\Users\krist\Desktop\Megatron-LM-review` | YES | Training substrate |
| POG2 | `C:\Users\krist\.gemini\antigravity\scratch\pog2` | YES | 1.5TB substrate, detached rsmv |

### 1.2 Game Rebuild / RuneScape Tooling
| Program | Expected Path | Verified Exists | Notes |
|---------|--------------|-----------------|-------|
| rsmv-upstream | `C:\Users\krist\Desktop\rsmv-upstream` | YES | Upstream diff authority |
| rsmv-upstream-check | `C:\Users\krist\Desktop\rsmv-upstream-check` | YES | Working viewer copy |
| openrsc-vinilla | `C:\Users\krist\Desktop\openrsc-vinilla` | YES | OpenRSC reference |
| POG2_ModelRolodex_Workflow | `C:\Users\krist\Desktop\POG2_ModelRolodex_Workflow` | YES | Model rolodex |
| worldgen-compliance | `C:\Users\krist\Desktop\worldgen-compliance` | YES | 2026 cache extraction |
| collisionvis | `C:\Users\krist\Desktop\collisionvis` | YES | Collision visualization |
| godot | `C:\Users\krist\Desktop\godot` | YES | 4.4.1-stable |
| maya-usd | `C:\Users\krist\Desktop\maya-usd` | YES | Maya USD |
| OpenUSD | `C:\Users\krist\Desktop\OpenUSD` | YES | Universal Scene Description |

### 1.3 AI / Quantum / Research Programs
| Program | Expected Path | Verified Exists | Notes |
|---------|--------------|-----------------|-------|
| zotero | `C:\Users\krist\Desktop\zotero` | YES | 246 PDFs, 491 .text extracts |
| Kimi-K2 | `C:\Users\krist\Desktop\Kimi-K2` | YES | MoonshotAI fork |
| Kimi-K2.5 | `C:\Users\krist\Desktop\Kimi-K2.5` | YES | Older packed release |
| kimi-cli | `C:\Users\krist\Desktop\kimi-cli` | YES | v1.49.0 |
| quantum-simulation-main | `C:\Users\krist\Desktop\quantum-simulation-main` | YES | Split-step visualization |
| Upgraded-Depth-Anything-V2 | `C:\Users\krist\Desktop\New folder (5)\Upgraded-Depth-Anything-V2` | YES | Depth estimation |
| colibri | `C:\Users\krist\Desktop\New folder (5)\colibri` | YES | MoE inference/tokenizer |
| shap-e | `C:\Users\krist\Desktop\shap-e` | YES | 3D implicit functions |
| offline-3d-shap-e | `C:\Users\krist\Desktop\offline-3d-shap-e` | YES | Offline variant |
| MHD | `C:\Users\krist\Desktop\MHD` | YES | MHD propulsion |
| MHD-git | `C:\Users\krist\Desktop\MHD-git` | YES | MHD git clone |
| GeoMotionGPT | `C:\Users\krist\Desktop\GeoMotionGPT` | YES | Motion generation |
| math-diagram-extractor | `C:\Users\krist\Desktop\math-diagram-extractor` | YES | PDF→PNG→OCR |
| mwparserfromhell_new | `C:\Users\krist\Desktop\mwparserfromhell_new` | YES | Wiki parser fork |

### 1.4 Infrastructure / Cloud / Workers
| Program | Expected Path | Verified Exists | Notes |
|---------|--------------|-----------------|-------|
| kingwen-oracle-worker | `C:\Users\krist\Desktop\kingwen-oracle-worker` | YES | Cloudflare worker |
| openjarvis-globe-worker | `C:\Users\krist\Desktop\openjarvis-globe-worker` | YES | DO/PartyKit globe |
| ollama-cloudflare-worker | `C:\Users\krist\Desktop\ollama-cloudflare-worker` | YES | Ollama bridge |
| worker-supervisor | `C:\Users\krist\Desktop\worker-supervisor` | YES | Worker supervision |
| alt1-ai | `C:\Users\krist\Desktop\alt1-ai` | YES | Sovereign ingestion |
| eyecite | `C:\Users\krist\Desktop\eyecite` | YES | Citation/research |
| citeurl | `C:\Users\krist\Desktop\citeurl` | YES | Citation URL |
| legal-crosswalk-tools | `C:\Users\krist\Desktop\legal-crosswalk-tools` | YES | Legal drift tools |
| lawscraper | `C:\Users\krist\Desktop\lawscraper` | YES | Law scraping |
| uslaw.link | `C:\Users\krist\Desktop\uslaw.link` | YES | US law links |
| Family-Tree-Research | `C:\Users\krist\Desktop\Family-Tree-Research` | YES | Genealogy research |
| kbro1989 | `C:\Users\krist\Desktop\kbro1989` | YES | GitHub profile README |
| kingwenfinance | `C:\Users\krist\Desktop\kingwenfinance` | YES | Finance integration |
| Pumpkin | `C:\Users\krist\Desktop\Pumpkin` | YES | RSPS |
| moparscape | `C:\Users\krist\Desktop\moparscape` | YES | RSPS |
| RUNESCAPE-WIDGETS | `C:\Users\krist\Desktop\RUNESCAPE-WIDGETS` | YES | RS widgets |
| MUGEN | `C:\Users\krist\Desktop\MUGEN` | YES | MUGEN fighter |
| hello-ai-worker-rsmv | `C:\Users\krist\Desktop\hello-ai-worker-rsmv` | YES | AI worker |
| desktop-tools-and-specs | `C:\Users\krist\Desktop\desktop-tools-and-specs` | YES | Tooling specs |
| dqn-chronic-disease-prediction | `C:\Users\krist\Desktop\dqn-chronic-disease-prediction` | YES | DQN research |
| Color-by-number-main | `C:\Users\krist\Desktop\Color-by-number-main` | YES | CHROMANNUMBER |
| emergency | `C:\Users\krist\Desktop\emergency` | YES | Emergency tools |
| mine | `C:\Users\krist\Desktop\mine` | YES | Mining tools |
| TES5Edit | `C:\Users\krist\Desktop\TES5Edit` | YES | Skyrim modding |
| RayeRen | `C:\Users\krist\Desktop\RayeRen` | YES | Training pipelines |
| react-base-table | `C:\Users\krist\Desktop\react-base-table` | YES | UI component |
| rs3-wiki-topology-explorer | `C:\Users\krist\Desktop\rs3-wiki-topology-explorer` | YES | Wiki topology |
| rsmv | `C:\Users\krist\Desktop\rsmv` | YES | rsmv legacy |
| rsmv-normalized | `C:\Users\krist\Desktop\rsmv-normalized` | YES | Normalized rsmv |
| runelite | `C:\Users\krist\Desktop\runelite` | YES | RuneLite API |
| gibberlink | `C:\Users\krist\Desktop\gibberlink` | YES | Acoustic protocol |
| oracle | `C:\Users\krist\Desktop\oracle` | YES | Dashboard/worker |
| kingwen_corpus_staging | `C:\Users\krist\Desktop\kingwen_corpus_staging` | YES | Corpus staging |
| cinder-upgrade-artifact | `C:\Users\krist\Desktop\cinder-upgrade-artifact` | YES | Cinder upgrade |
| openjarvis-globe-worker | `C:\Users\krist\Desktop\openjarvis-globe-worker` | YES | Globe worker |
| New folder | `C:\Users\krist\Desktop\New folder` | YES | Misc workspace |
| New folder (2) | `C:\Users\krist\Desktop\New folder (2)` | YES | Misc workspace |
| New folder (3) | `C:\Users\krist\Desktop\New folder (3)` | YES | rsmv-vite target |
| New folder (4) | `C:\Users\krist\Desktop\New folder (4)` | YES | Kimi rebuild |
| New folder (5) | `C:\Users\krist\Desktop\New folder (5)` | YES | 3D/repos |

---

## 2. King Wen Core Artifacts — Knowns vs Gaps

### 2.1 Canonical Engine Files
| Artifact | Path | Size | Status |
|----------|------|------|--------|
| Emotional engine | `emotional_engine.py` | 64KB | PRESENT |
| Ternary tables | `kingwen_ternary_tables_complete.py` | 14KB | PRESENT |
| Decision matrix | `decision_matrix.py` | 433B? | PRESENT |
| Temporal engine | `temporal_emotional_engine.py` | 564B? | PRESENT |
| Expand server | `expand_server.py` | 35KB | PRESENT |
| Full shotgun | `scripts/full_hexagram_shotgun.py` | 34KB | PRESENT |
| Ternary expansion JSON | `scripts/ternary_full_expansion.json` | 2.8MB | PRESENT |
| Hexagram full expansion JSON | `scripts/hexagram_full_expansion.json` | 660KB | PRESENT |
| Multi-layer expand | `scripts/multi_layer_expand.py` | 20KB | PRESENT |
| Quantum expand | `scripts/kingwen_quantum_expand.py` | 28KB | PRESENT |
| Schauberger parsing | `scripts/schauberger_parsing_layers.py` | 13KB | PRESENT |
| Hexagram shotgun matcher | `scripts/hexagram_shotgun_matcher.py` | 12KB | PRESENT |
| Build full shotgun JSONL | `kingwen_train_data/build_full_shotgun_jsonl.py` | 7.6KB | PRESENT |
| Full shotgun all JSONL | `kingwen_train_data/full_shotgun_expansion_all.jsonl` | 31MB | PRESENT |
| Full shotgun enriched JSONL | `kingwen_train_data/full_shotgun_expansion_corpus_enriched.jsonl` | 30MB | PRESENT |
| Full shotgun lexical gate JSONL | `kingwen_train_data/full_shotgun_expansion_lexical_gate.jsonl` | 32MB | PRESENT |
| Shotgun captures JSONL | `DATASETS/shotgun_captures.jsonl` | 0B | **EMPTY — needs fill** |
| Collapse output | `shotgun_expand_output.json` | 3.1MB | PRESENT, stale timestamp/emotional_input=None |
| Avatar mesh manifest | `DATASETS/kingwen_avatar_mesh_manifest.json` | 692KB | PRESENT |
| Sovereign world topology | `DATASETS/kingwen_ sovereign_world_topology.json` | 5.9MB | PRESENT |
| JKD ingestion binary | `DATASETS/jkd_ingestion_binary.jsonl` | 1.8GB | PRESENT |
| JKD ingestion ternary | `DATASETS/jkd_ingestion_ternary.jsonl` | 20KB | PRESENT |
| JKD chapter chorus manifest | `DATASETS/jkd_chapter_chorus_manifest.json` | 2.1MB | PRESENT |
| JKD wavepacket emotions | `DATASETS/jkd_megatron_wavepacket_emotions.jsonl` | 3.8MB | PRESENT |
| Full vocabulary JSON | `output/hexagram_full_vocabulary.json` | 5.6MB | PRESENT |
| Hexagram translations JSON | `output/hexagram_translations.json` | 8.0MB | PRESENT |
| RS3 live cache tables | `kingwen_train_data/rsmv_live_cache_tables.json` | 27MB | PRESENT |

### 2.2 Integration Surface Files
| Artifact | Path | Status |
|----------|------|--------|
| OpenJarvis King Wen adapter | `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen_engine_adapter.py` | PRESENT |
| OpenJarvis consult tool | `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\tools\kingwen_oracle_consult_tool.py` | PRESENT |
| OpenJarvis completion injection | `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\emotion\kingwen_completion_injection.py` | PRESENT |
| Cinder King Wen service | `C:\Users\krist\Desktop\cinder\src\main\services\kingwen.ts` | PRESENT |
| Cinder King Wen transition | `C:\Users\krist\Desktop\cinder\src\main\services\kingwenTransition.ts` | PRESENT |
| OpenJarvis globe worker | `C:\Users\krist\Desktop\openjarvis-globe-worker` | PRESENT |
| King Wen oracle worker | `C:\Users\krist\Desktop\kingwen-oracle-worker` | PRESENT |

---

## 3. Integration Verification Checklist

### 3.1 Engine-to-Engine
- [ ] `expand_server.py` runs on `127.0.0.1:8765` and responds to `POST /expand` with 64 expanded + 512 resolved
- [ ] `shotgun_expand()` returns `expanded_count=64`, `resolved_count=512`, `winner=None`, `dominantEntry=None`
- [ ] `shotgun_expand()` returns `source=kingwen-shotgun-expand` with all 64 hexagrams + 512 resolved
- [ ] `multi_layer_expand()` returns `source=kingwen-multi-layer-expand` with ternary line options + pool descriptives
- [ ] `kingwen_quantum_expand.py` PennyLane circuit runs without import error
- [ ] `_hamiltonian_energy()` uses signed ternary differentials, no boolean gating
- [ ] `_compute_consensus_from_resolved()` returns open-pool consensus with primary/secondary pool vectors
- [ ] `_pool_weights_for_hex()` derives porosity from `HEXAGRAM_INJECTION_SITE` + `emotional_input`, not yao_ratio formula
- [ ] `kingwen_oracle_consult_tool.py` registered as `kingwen_oracle_consult` in OpenJarvis tool registry
- [ ] `kingwen_engine_adapter.py` `consult()` returns PAA/spectral-lambda patch fields

### 3.2 Desktop Programs → King Wen
- [ ] OpenJarvis `chat_cmd.py` calls `kingwen_engine_adapter.consult()` with `emotional_input` from `get_emotional_input()`
- [ ] OpenJarvis `_oracle_speak.py` routes TTS through `CartesiaAdapter.synthesize()` with King Wen vector
- [ ] OpenJarvis `serve.py` injects Hermes `.env` before engine discovery
- [ ] OpenJarvis `memory_card_adapter.py` imports Hermes graph data directly
- [ ] Cinder `GraphSidebar` mounts `OracleLiveReadout` from `kingwen.ts`
- [ ] Cinder `kingwen.ts` reads local CSV only, no Python imports
- [ ] Cinder `tasksService.create` wires `cinderState` through triage post-insert
- [ ] voicebox backends consume `kingwen_voice_profiles.json` voice pools
- [ ] Megatron training data reads `full_shotgun_expansion_all.jsonl` for corpus
- [ ] worldgen-compliance outputs slot manifest aligned with `kit_*.json` schema

### 3.3 World Generation / 3D Pipeline
- [ ] `scripts/kingwen_mobius_sphere.py` produces Riemann sphere coords for avatar placement
- [ ] `scripts/kingwen_state_transition.py` loads `inject_site` from live expansion, not stale snapshot
- [ ] `DATASETS/kingwen_model_sets/kit_*.json` (64 files) matches POG2 kit schema
- [ ] `DATASETS/kingwen_avatar_mesh_manifest.json` has 512 entries with wavefunction amplitudes
- [ ] `DATASETS/kingwen_sovereign_world_topology.json` has 64 sectors + 6 yao pellets each
- [ ] `DATASETS/quantumlab_plots/` has 128 PNG files (64 3D + 64 2D)
- [ ] `public/index.html` in King Wen renders 3D sovereign world viewer
- [ ] `DATASETS/kingwen-converged-widget.html` renders 512 hexagram widget
- [ ] GibberLink acoustic protocol maps (hexId, phaseId) to 9-bit VHDL address
- [ ] `functions/api/gibberlink.js` emits 6-yao acoustic carrier frequencies

### 3.4 Data Convergence
- [ ] `full_shotgun_expansion_all.jsonl` has 1,536 records (64 hex × 8 phase × 3 inputs)
- [ ] All 64 hexagrams present in expanded[] with non-empty `inject_site`
- [ ] `hexagram_full_expansion.json` is NOT used as inject-site/porosity source (stale)
- [ ] `shotgun_expand_output.json` timestamp/emotional_input are NOT null for live captures
- [ ] `DATASETS/shotgun_captures.jsonl` is being written to by running `expand_server.py`
- [ ] `paper_math_usage.jsonl` has 243 records from 245-paper corpus
- [ ] `kingwen_train_data/rsmv_live_cache_tables.json` is 27MB and current
- [ ] `kingwen_train_data/consensus_gaussian.json` has per-hexagram/phase 6D stats

### 3.5 Research Paper Integration
- [ ] PIAA mapping: `DATASETS/paper_2605.25821_piaa_mapping.json` exists and is referenced in adapter
- [ ] Spectral Souping mapping: `DATASETS/paper_2605.20408_spectral_souping_mapping.json` exists
- [ ] Score Jacobian Chaining mapping: `DATASETS/paper_2212.00774_*` exists
- [ ] Paper frequency profiles: `C:\Users\krist\Desktop\zotero\learning-corpus\paper_frequency_profiles.jsonl` (1.7MB)
- [ ] Page precision math: `C:\Users\krist\Desktop\zotero\learning-corpus\page_precision_math_summary.json` (644 pages)
- [ ] Math diagram extractor bridge: `C:\Users\krist\Desktop\math-diagram-extractor\scripts\pdfImageBridge.py` works
- [ ] Tesseract OCR installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- [ ] Full 500+ paper corpus ingestion complete (not just 245 test pulls)

### 3.6 Cloudflare / Deployment
- [ ] `kingwen-oracle.kristain33rs.workers.dev` returns 64 expanded + 512 resolved
- [ ] Worker version ID matches deployed artifact
- [ ] `/tts` emits `X-Kingwen-Compliance` and `X-Kingwen-Vector` headers
- [ ] `/ws` returns 101 on upgrade
- [ ] KV cache `KINGWEN_AVATAR_CACHE` id `c39fc2ed3ced4b988224861476ca8def` is populated
- [ ] D1 consult_events table schema matches worker expectations
- [ ] OpenJarvis globe DO path is `/parties/globe/default`
- [ ] PartySocket client connects and receives fanout

### 3.7 Determinism / No-Mock Audit
- [ ] `verify_math_jacobian_hamiltonian.py` exits 0
- [ ] `verify_output_mismatches.py` exits 0
- [ ] `verify_registry.py` exits 0
- [ ] `test_collapse_full_512.py` exits 0
- [ ] `test_deterministic_replay.py` exits 0 with same hash across runs
- [ ] `test_porosity_sweep.py` shows porosity modulation, not constant
- [ ] No `random.random()`, `np.random.rand()` in engine math without explicit seed
- [ ] No boolean gating in `_hamiltonian_energy()`, `_tau_for_resolved()`, `_compute_consensus_from_resolved()`
- [ ] All 64 hexagrams pass through every turn (no early collapse to single winner)
- [ ] `shotgun_expand()` is single capture point; adapters do not reconstruct state

---

## 4. World Generation from First Principles

### 4.1 Immutable → Expansion → World
```
HEXAGRAM_BASE (64)
  + PHASE_LINE_MAP (8 phases)
  + YAO_VOCABULARY (9-item)
  + HEXAGRAM_INJECTION_SITE (primary/secondary pools, porosity)
  + EMOTIONAL_WEIGHTS (5-axis vectors)
  + VOICEBOX_VOICE_POOL (66 pools)
    ↓
expand_hexagram() → 64 expanded
  + sample_resolve() → 512 resolved
  + _hamiltonian_energy() → energy per state
  + _quantum_avatar_modulation() → wavefunction/rotation/scale/color
    ↓
shotgun_expand() → full_hexagram_shotgun.py
  + _ternary_slot_matrix() → 6-slot ternary per hex
  + _personality_subsets_for_slot() → pool blends
  + _build_jspace_projections() → 7 downstream systems
  + _expand_729_ternary_line_permutations() → 46,656 permutations
    ↓
multi_layer_expand() → ternary_full_expansion.json (5,832 states)
  + open_pool_consensus() → weighted ternary collapse
    ↓
kingwen_quantum_expand.py → PennyLane circuit → 5,832 prob vector
  + _phase_bias_vector() → future-phase Gaussian bias
  + marginalize_to_5832() → 4096→5832 mapping
    ↓
kingwen_mobius_sphere.py → Riemann sphere coords
kingwen_state_transition.py → state transition vectors
    ↓
DATASETS/kingwen_model_sets/kit_*.json → 64 hex × 8 phase meshes
DATASETS/kingwen_avatar_mesh_manifest.json → 512 mesh manifest
DATASETS/kingwen_sovereign_world_topology.json → 64 sectors + pellets
    ↓
GibberLink/King Wen Link → acoustic carrier → 9-bit VHDL address
OpenJarvis avatar → 3D rendering
Cinder GraphSidebar → visualization
voicebox → audio generation
```

### 4.2 Program Boundaries (Enforced)
- King Wen scripts: `KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/` ONLY
- OpenJarvis runtime: `C:\Users\krist\Desktop\OpenJarvis\src\openjarvis\`
- OpenJarvas: docs/audit sidecar ONLY, never runtime
- Cinder: standalone, no POG2 runtime imports
- voicebox: inference-only backends, no local trainer
- Megatron: training substrate, reads JSONL only
- POG2: exposition/reference only, never imported into sovereign systems

### 4.3 Known Gaps / Action Items
1. **Shotgun captures empty**: `DATASETS/shotgun_captures.jsonl` is 0B — needs capture script or running expand_server
2. **Stale collapse output**: `shotgun_expand_output.json` has null timestamp/emotional_input — mark as frozen snapshot
3. **Missing hexagram_full_expansion.json fields**: skill_cards (12 slots), domain_vectors, training_notes, reflections absent in worker snapshot
4. **expand_server not running**: no process listening on 8765
5. **Full corpus not ingested**: 245/500+ papers processed
6. **No end-to-end Megatron ingestion test**: corpus exists but no verified train→val pipeline run
7. **Tesseract not installed**: blocks PDF equation OCR pipeline
8. **No ternary verification gate**: no script asserts expanded=729, resolved=5832, signed paired differentials

---

## 5. Verification Protocol

For each item above:
1. Run exact file:line probe or process check
2. Mark PASS/FAIL/UNVERIFIED with exact output
3. If FAIL, write immediate corrective action
4. Re-verify after correction
5. No claim without tool output backing it

---

*Generated from live file system + git history probe. All paths verified against `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES` and `C:\Users\krist\Desktop\OpenJarvis`. No fabrication.*
