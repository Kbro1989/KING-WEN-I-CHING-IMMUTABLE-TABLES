# King Wen External Usage Reconciliation

## Document Metadata
- **File**: docs/KING_WEN_EXTERNAL_USAGE_RECONCILIATION.md
- **Generated**: 2026-11-11
- **Status**: Separate audit — coexisting with, not replacing, inventory/registries/external_systems.json
- **Disposition**: SUPPORTING_EVIDENCE

## 1. Scope and Preservation
This document records external programs that reference or consume King Wen. It is a **separate audit** preserving git-history, code-integration, and artifact-lineage evidence. It does NOT merge into inventory/registries/external_systems.json because the registry counts integration relationships while this document counts physical files, git commits, and evidence layers.

**Authorship perspective**: All King Wen integration commits across external repos are by Kbro/Kristain33rs (you). The external repos themselves (Megatron-LM-review, OpenJarvis, Voicebox, rsmv-upstream, Open Design) are either upstream projects or forks where you added King Wen integration. Integration direction is determined by **who wrote the commit and where it lives**.

**Identity resolution**: You operate as both `kbro1989` (personal GitHub) and `Pick of Gods` (GitHub org). When a fork chain goes `upstream → Pick of Gods → kbro1989` or `upstream → kbro1989 → Pick of Gods`, the **true upstream authority** is the first non-self remote in the chain ("next repo up").

| Question | Registry answers | This audit answers |
|----------|------------------|-------------------|
| How many integration relationships? | 11 systems, 70+ integration points | Commit history, physical file counts, evidence-layer breakdown |
| What is the nature of the integration? | Relationship type, direction, interface | Source/target symbols, code paths, exported artifacts |
| Which artifacts flow where? | Source symbol to target symbol | Exact file paths, sha256, date of generation |

## 2. External Usage Map (all 7 programs) — By Authorship

### 2.1 Programs where YOU committed King Wen integration (in their repos)

| Program | Your commits referencing King Wen | Integration direction | Who wrote the integration |
|---------|---------------------------------|---------------------|--------------------------|
| **OpenJarvis** | 19 commits (2026-07-04 to 2026-08-02) | King Wen → OpenJarvis | YOU (Kbro/Kristain33rs) |
| **Megatron-LM-review** | 1 commit (2026-07-07) | King Wen → Megatron | YOU (Kbro/Kristain33rs) |
| **Voicebox** | 0 commits in Voicebox repo | King Wen → Voicebox | Integration lives in King Wen repo (export scripts) |
| **Open Design** | 0 commits in Open Design repo | King Wen → Open Design | Integration lives in King Wen repo (export scripts) |

### 2.2 Programs you CONSUME (import data FROM them)

| Program | Your commits in that repo | Integration direction | Notes |
|---------|---------------------------|---------------------|-------|
| **rsmv-upstream** | 0 King Wen commits (your rsmv commits are for RSMV features) | rsmv-upstream → King Wen | King Wen IMPORTS cache data FROM rsmv (beta_live_verify.py, placement_diagnostic.py, bridge scripts) |
| **POG2** | Historical only (destroyed device) | POG2 → King Wen | Archaeology only — POG2 is source of provenance |
| **Cinder** | No local repo (dropped for disk space) | King Wen → Cinder (if existed) | Would consume King Wen CSV/JSON artifacts |

### 2.3 Upstream Chain — "Next Repo Up" Resolution

| Program | origin (your fork) | upstream / org remote | **True upstream (next repo up)** | Your relationship |
|---------|-------------------|----------------------|----------------------------------|-------------------|
| **Megatron-LM-review** | git@github.com:Kbro1989/Megatron-LM.git | git@github.com:NVIDIA/Megatron-LM.git | **NVIDIA/Megatron-LM** | Forked from NVIDIA; added King Wen training data in your fork |
| **OpenJarvis** | https://github.com/Kbro1989/OpenJarvis.git | https://github.com/open-jarvis/OpenJarvis.git | **open-jarvis/OpenJarvis** | Forked from open-jarvis; added King Wen integration in your fork |
| **Voicebox** | git@github.com:Kbro1989/voicebox.git | git@github.com:pick-of-gods/voicebox.git | **jamiepine/voicebox** (pick-of-gods is a fork of jamiepine) | Forked from pick-of-gods; pick-of-gods is a fork of jamiepine/voicebox; integration is export-only from King Wen |
| **rsmv-upstream** | git@github.com:Kbro1989/rsmv.git | https://github.com/skillbert/rsmv.git | **skillbert/rsmv** | Forked from skillbert; King Wen CONSUMES rsmv cache data |
| **Open Design** | git@github.com:Kbro1989/voicebox.git* | https://github.com/nexu-io/open-design.git | **nexu-io/open-design** | *Note: origin incorrectly points to voicebox; true upstream is nexu-io/open-design; integration is export-only from King Wen |

*Open Design origin remote incorrectly points to voicebox repos — true upstream is nexu-io/open-design.

**Key principle**: When the org remote is your own (Pick of Gods), the true upstream is the next non-self remote. For Voicebox, pick-of-gods/voicebox IS a fork of jamiepine/voicebox — the true upstream is jamiepine/voicebox. For Megatron/OpenJarvis/rsmv/Open Design, the upstream remote is a third party.

**Important wording**: "0 commits in external repo" means the integration code lives in **King Wen repo** (export scripts, build scripts), not in the consumer repo.

## 3. File Type Usage Per Program (King Wen Integration Files)

| Program | Your King Wen integration files | Primary file types in integration |
|---------|--------------------------------|----------------------------------|
| **OpenJarvis** (your fork) | 26 files in src/openjarvis/emotion/, tools/, blueprints/, cli/ | py (7,196), js (25,699), ts (11,267), json (2,338) |
| **Megatron-LM-review** (your fork) | kingwen_train_data/ (build scripts, runtime, data) | py (5,751), md (1,546), json (994), yaml (411) |
| **Voicebox** (your fork) | 0 in Voicebox; exports in King Wen scripts/ | js (13,656), ts (8,835), mjs/cjs (9,539) |
| **rsmv-upstream** (your fork) | King Wen IMPORTS from rsmv: scripts/beta_live_verify.py, placement_diagnostic.py, bridge_*.py | js (6,949), ts (4,473), json (935) |
| **Open Design** (your fork) | 0 in Open Design; King Wen exports to DATASETS/ | js (38,394), ts (21,871), json (2,560) |

## 4. Three Evidence Layers (per Program)

### 4.1 OpenJarvis — 19 commits by YOU (2026-07-04 to 2026-08-02)
#### Layer 1: Git provenance (your commits in OpenJarvis fork)
| Commit | Date | Changed files | King Wen reference |
|--------|------|---------------|-------------------|
| abb092a | 2026-08-02 | jarvis-router | kingwen interaction documentation |
| d3d2358 | 2026-07-21 | jarvis-router, frontend, tests | King Wen/Jarvis integration head — WS-01..WS-06 |
| 755e2c9 | 2026-07-17 | save schema, model router | state management |
| 9a7f4ca | 2026-07-17 | task engine | deterministic task decomposition |
| 5961892 | 2026-07-07 | execution layer | wire King Wen 512-state consensus |
| a061fbf | 2026-07-07 | engine adapter | direct King Wen engine adapter |
| 77cbb22 | 2026-07-07 | kingwen dashboard | emotional vector from provider payload |
| 547d7b0 | 2026-07-07 | dashboard renderer | King Wen dashboard renderer |
| 3260e41 | 2026-07-07 | jarvis-router | King Wen only separation; remove ichingoracle |
| 8a11772 | 2026-07-07 | /models card renderer | King Wen getHexagram |
| 1d9596f | 2026-07-07 | sovereign agent stack | King Wen intent decoding, Hermes event bridge |
| 4df56c6 | 2026-07-06 | TTS backends | Cloudflare AI and Windows SAPI |
| 9ff0069 | 2026-07-05 | actionable manifest | generation and testing |
| 87a9b36 | 2026-07-05 | emotion provider | King Wen emotion provider + Hermes runtime |

#### Layer 2: Code integration (your code in OpenJarvis fork)
- `src/openjarvis/emotion/kingwen.py` — King Wen consult integration
- `src/openjarvis/emotion/kingwen_engine_adapter.py` — engine adapter
- `src/openjarvis/emotion/kingwen_completion_injection.py` — completion injection
- `src/openjarvis/prompt/builder.py` — prompt building with King Wen
- `src/openjarvis/agents/morning_digest.py` — morning digest with King Wen
- `src/openjarvis/speech/cartesia_adapter.py` — prosthetic voice adapter
- `src/openjarvis/tools/kingwen_oracle_consult_tool.py` — oracle consult tool
- `src/openjarvis/tools/kingwen_top_k_router.py` — top-K router with skill cards
- `src/openjarvis/tools/kingwen_skill_card_renderer.py` — skill card renderer
- `src/openjarvis/core/env_integration.py` — Hermes env bridge
- `src/openjarvis/core/kingwen_swarm_store.py` — swarm store
- `src/openjarvis/blueprints/` — blueprint system with King Wen
- `src/openjarvis/cli/kingwen_dashboard.py` — dashboard CLI

#### Layer 3: Artifact lineage
- **King Wen source artifacts consumed**: `king_wen_64_verified.json`, `hexagram_full_expansion.json`, `kingwen_512_oracle_widget.html`, `emotional-weights.json`
- **OpenJarvis exports**: `data/jarvis_save_schema.json`, `data/model_router_schema.json`

### 4.2 Megatron-LM-review — 1 commit by YOU (2026-07-07)
#### Layer 1: Git provenance (your commit in Megatron fork)
| Commit | Date | Changed files | King Wen reference |
|--------|------|---------------|-------------------|
| 5cbf627 | 2026-07-07 | kingwen_train_data/, transformers-src, tokenizer patches | King Wen emotional pretraining pipeline |

#### Layer 2: Code integration (your code in Megatron fork)
- `kingwen_train_data/build_full_shotgun_jsonl.py` — training record builder
- `kingwen_train_data/build_hybrid_kimi_k2.py` — hybrid K2 config generator
- `kingwen_train_data/build_pretrain.py` — pretraining construction
- `kingwen_train_data/build_usage_labels.py` — usage-label construction
- `kingwen_train_data/build_vocab.py` — vocabulary builder
- `kingwen_train_data/combine_corpora.py` — corpus combining
- `kingwen_train_data/convert_corpus.py` — corpus conversion
- `kingwen_train_data/extract_labels.py` — label extraction
- `kingwen_train_data/runtime/kingwen_dataset.py` — dataset runtime
- `kingwen_train_data/runtime/test_kingwen_dataset.py` — dataset tests

#### Layer 3: Artifact lineage
- **King Wen source artifacts consumed**: `full_shotgun_expansion_all.jsonl`, `hybrid_kimi_k2_config.json`, `per_hex_training/*.jsonl`
- **Megatron outputs**: `kingwen_pretrain.jsonl`, `megatron_multi_domain.jsonl`

### 4.3 Voicebox — 0 commits in Voicebox repo; exports from King Wen
#### Layer 1: Git provenance
No King Wen commits in Voicebox repo by anyone. The integration is **export-only from King Wen**:
- King Wen scripts: `scripts/sync_voicebox_npc_profiles.py`, `scripts/export_voicebox_training.py`, `scripts/verify_output_mismatches.py`
- Voicebox exports generated: `kingwen_64_npc_voice_profiles.json`, `voicebox_profile_payload.json`, `voicebox_training_vector.json`

#### Layer 2: Code integration (in King Wen, not Voicebox)
- `scripts/sync_voicebox_npc_profiles.py` — sync 64 Sovereign King Wen Model NPC Voice Profiles
- `scripts/export_voicebox_training.py` — King Wen → Voicebox training-data exporter
- `scripts/export_all_64_answers.py` — voicebox_engine preset selection
- `scripts/full_pool_voice_pick.py` — reads VOICEBOX_VOICE_POOL and EMOTIONAL_WEIGHTS
- `src/core/kingwen_shotgun_pipeline.py` — `to_voicebox_payload()` method

#### Layer 3: Artifact lineage
- **King Wen source artifacts consumed by Voicebox**: `DATASETS/kingwen_64_npc_voice_profiles.json`, `data/emotional-weights.json`, `VOICEBOX_VOICE_POOL` (66 entries)
- **Voicebox repo consumes**: Exported JSON files, not King Wen code

### 4.4 rsmv-upstream — 0 King Wen commits; King Wen CONSUMES rsmv data
#### Layer 1: Git provenance
Your commits in rsmv-upstream are for **RSMV features** (marketplace bundle, varbit decoding, 3D rendering), NOT King Wen. King Wen imports FROM rsmv via scripts in King Wen repo.

#### Layer 2: Code integration (King Wen scripts consuming rsmv)
- `scripts/beta_live_verify.py` — RS3 BETA cache verification (js5-major.jcache via sqlite3+zlib)
- `scripts/placement_diagnostic.py` — RSMV model placement diagnostics
- `scripts/bridge_collisionvis_upgrade.py` — RSMV collision visualization upgrade
- `scripts/bridge_desktop_3d_engines.py` — RSMV 3D engine bridging
- `scripts/integrate_desktop_3d_pog2_assets.py` — POG2 assets → desktop 3D via RSMV
- `scripts/transform_object_rsmv.py` — RSMV object transformation

#### Layer 3: Artifact lineage
- **RSMV cache artifacts consumed by King Wen**: `js5-{major}.jcache` (ZLB-compressed), `extracted_layers/`
- **Direction**: rsmv-upstream → King Wen (data source). King Wen READS rsmv cache, does not write to it.

### 4.5 POG2 — Historical provenance only (destroyed device)
#### Layer 1: Git provenance
POG2 was on destroyed device (D: drive). King Wen archaeology scripts trace provenance:
- `scripts/archaeology_beta_cluster_content_diff.py`
- `scripts/archaeology_beta_probe_provenance.py`
- `scripts/archaeology_boundary_authorship.py`
- `scripts/archaeology_destruction_boundary.py`
- `scripts/bridge_rsmv_shap_e_manifesto.py`

#### Layer 2: Artifact lineage
- **POG2 → King Wen**: Provenance tracing only. POG2 is the ORIGIN system.
- Migration: POG2 scratch/ → rsmv-upstream/scripts/.pog2/ (420 files, 482 import rewrites)

### 4.6 Open Design — 0 commits; exports from King Wen
#### Layer 1: Git provenance
No King Wen commits in Open Design repo. King Wen exports 3D assets to DATASETS/:
- `scripts/sync_all_desktop_viewers.py`
- `scripts/bridge_desktop_3d_engines.py` / `_hardened.py`
- `scripts/generate_avatar_meshes.py`
- `scripts/generate_sovereign_world.py`

#### Layer 3: Artifact lineage
- **King Wen source artifacts consumed by Open Design**: `kingwen_avatar_meshes/` (512 PLY), `kingwen_model_sets/kit_*.json` (64 kits), `kingwen_sovereign_world_topology.json`, `godot_scenes/`, `openusd_stages/`

### 4.7 Cinder — No local repo (dropped for disk space)
Would consume King Wen CSV/JSON artifacts via `kingwen.ts` native TS resolver if repo existed.

## 5. Direction Reconciliation Against external_systems.json

| System | Registry direction | Authorship-verified direction | Note |
|--------|-------------------|-------------------------------|------|
| OpenJarvis | KING_WEN → OPENJARVIS | **KING_WEN → OPENJARVIS** ✓ | Your 19 commits in OpenJarvis fork |
| Megatron-LM-review | KING_WEN → MEGATRON | **KING_WEN → MEGATRON** ✓ | Your 1 commit in Megatron fork |
| Voicebox | KING_WEN → VOICEBOX | **KING_WEN → VOICEBOX** ✓ | Export scripts in King Wen repo |
| Cinder | KING_WEN → CINDER | **KING_WEN → CINDER** (if existed) | Export scripts in King Wen repo |
| POG2 | POG2 → KING_WEN | **POG2 → KING_WEN** ✓ | Archaeology scripts in King Wen repo |
| rsmv-upstream | RSMV → KING_WEN | **RSMV → KING_WEN** ✓ | Your King Wen scripts IMPORT from rsmv |
| Open Design | KING_WEN → OPEN_DESIGN | **KING_WEN → OPEN_DESIGN** ✓ | Export scripts in King Wen repo |

## 6. Key Findings (Authorship-Corrected)

### 6.1 OpenJarvis: 19 commits by YOU
- **Establishes**: You built the full King Wen integration in your OpenJarvis fork (engine, agent, service, UI, voice, swarm, deployment)
- **Does not establish**: That upstream OpenJarvis (open-jarvis/OpenJarvis) has this integration (it's in your fork)

### 6.2 Megatron-LM-review: 1 commit by YOU
- **Establishes**: You added kingwen_train_data/ pipeline to your Megatron fork
- **Does not establish**: That upstream Megatron-LM (NVIDIA/Megatron-LM) has King Wen integration (it's in your fork)

### 6.3 Voicebox: 0 commits in Voicebox; export-only from King Wen
- **Establishes**: Voicebox consumes King Wen exports; you did NOT add King Wen code to Voicebox
- **Does not establish**: Voicebox has any King Wen runtime code (it's a static consumer)
- **Upstream chain**: Kbro1989/voicebox → pick-of-gods/voicebox → **jamiepine/voicebox** (true upstream)

### 6.4 rsmv-upstream: King Wen CONSUMES rsmv data (import direction)
- **Establishes**: King Wen reads rsmv cache via your scripts in King Wen repo
- **Does not establish**: rsmv-upstream has any King Wen code (your rsmv commits are for RSMV features)
- **Upstream authority**: skillbert/rsmv

### 6.5 POG2: Historical provenance only
- **Establishes**: King Wen archaeology traces POG2 provenance from destroyed device
- **Does not establish**: POG2 has King Wen integration (direction is POG2 → King Wen)

### 6.6 Open Design: Export-only from King Wen
- **Establishes**: King Wen generates 3D assets; Open Design consumes them
- **Does not establish**: Open Design has King Wen runtime code
- **Note**: origin remote incorrectly points to voicebox; true upstream is nexu-io/open-design

### 6.7 Key architectural finding (authorship-corrected)
All King Wen integration code is written by YOU and lives in **your forks** or **King Wen repo**. The pattern is:
- **King Wen → your fork** for consumers (OpenJarvis, Megatron)
- **King Wen → exported artifacts** for static consumers (Voicebox, Open Design)
- **External → King Wen** for data sources (rsmv-upstream, POG2)

No linear pipeline King Wen → OpenJarvis → Megatron → Voicebox. Each relationship is independent from King Wen as source.

## 7. Preserved Audit Separation
This document preserves the separate audit coexisting with:
- `inventory/registries/external_systems.json` — registry counts integration relationships
- `inventory/authority_lifecycle.json` — authority lifecycle classifications
- `inventory/artifact_lineage.jsonl` — artifact lineage records

## 8. Status Summary

| System | Registry status | Integration author | Your commits in their repo | Direction | True upstream (next repo up) | Primary file types |
|--------|-----------------|-------------------|---------------------------|-----------|----------------------------|-------------------|
| OpenJarvis | VERIFIED_DEPENDENCY | YOU (in fork) | 19 | KING_WEN → OPENJARVIS | open-jarvis/OpenJarvis | py, js, ts |
| Megatron-LM-review | VERIFIED_DEPENDENCY | YOU (in fork) | 1 | KING_WEN → MEGATRON | NVIDIA/Megatron-LM | py, md, json |
| Voicebox | OBSERVED_RELATIONSHIP | YOU (in King Wen) | 0 | KING_WEN → VOICEBOX | jamiepine/voicebox | js, ts (exports) |
| Cinder | OBSERVED_RELATIONSHIP | — | N/A (no local repo) | KING_WEN → CINDER | — | ts, json |
| POG2 | HISTORICAL_PROVENANCE | — | N/A (destroyed) | POG2 → KING_WEN | — | ts, json (archaeology) |
| rsmv-upstream | VERIFIED_DEPENDENCY | YOU (in King Wen) | 0 King Wen commits | RSMV → KING_WEN | skillbert/rsmv | js, ts (import) |
| Open Design | GENERATED_CONSUMED | YOU (in King Wen) | 0 | KING_WEN → OPEN_DESIGN | nexu-io/open-design | js, ts (exports) |

## 9. Verification Commands
```bash
# OpenJarvis: your King Wen commits
git -C OpenJarvis log --all --format="%H|%an|%ae|%ad|%s" --date=short --grep="king" | grep -E "Kbro|kristain33rs"

# Megatron-LM-review: your King Wen commit
git -C Megatron-LM-review log --all --format="%H|%an|%ae|%ad|%s" --date=short --grep="king"

# Voicebox: no King Wen commits
git -C voicebox log --all --format="%H|%an|%ae|%ad|%s" --date=short --grep="king"

# rsmv-upstream: your RSMV commits (not King Wen)
git -C rsmv-upstream log --all --format="%H|%an|%ae|%ad|%s" --date=short --author="Kbro\|kristain33rs"

# King Wen repo: your integration scripts
git log --all --format="%H|%an|%ae|%ad|%s" --date=short -- scripts/export_voicebox_training.py

# Upstream chain verification
git -C OpenJarvis remote -v | grep upstream
git -C Megatron-LM-review remote -v | grep upstream
git -C voicebox remote -v | grep upstream
git -C rsmv-upstream remote -v | grep upstream
git -C open-design remote -v | grep upstream

# Verify true upstream chains
curl -s "https://api.github.com/repos/pick-of-gods/voicebox" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Fork:', d.get('fork')); print('Parent:', d.get('parent', {}).get('full_name') if d.get('parent') else 'N/A')"
```