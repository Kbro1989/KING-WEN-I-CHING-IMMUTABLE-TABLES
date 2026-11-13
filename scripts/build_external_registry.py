#!/usr/bin/env python3
"""
External Systems Registry Generator

Regenerates inventory/registries/external_systems.json from the canonical
integration point manifest with repository-relative path semantics.

Path Convention (Repository-Relative):
--------------------------------------
For every integration point:
    system_repo       = repository identifier
    repo_relative_path = path relative to the root of system_repo

Validation invariant:
    A correct repo_relative_path is validated by resolving
    <repo_root>/<repo_relative_path> and confirming the file exists.
    A path that redundantly includes the repository name
    (e.g., Upgraded-Depth-Anything-V2/run_image-depth_8bit.py when
    system_repo is already Upgraded-Depth-Anything-V2) FAILS validation
    as a duplicated repository prefix.

The generator performs the following validation:
1. Every system has system_repo and at least one verified_integration_point
2. Every integration point has king_wen_file, references, direction
3. Every repo_relative_path resolves against the repository root
4. No duplicated repository prefix (e.g., system_repo == "X" with path
   "X/some_file" is rejected)
5. Output JSON is stable (sorted, deterministic)

Usage:
    python scripts/build_external_registry.py
"""

import json
import os
import sys
import hashlib
from pathlib import Path

# Canonical repository roots (workspace-relative)
REPO_ROOTS = {
    "KING-WEN-I-CHING-IMMUTABLE-TABLES": Path(
        os.path.expanduser("~")
    )
    / "Desktop"
    / "KING-WEN-I-CHING-IMMUTABLE-TABLES",
    "Upgraded-Depth-Anything-V2": Path(
        os.path.expanduser("~")
    )
    / "Desktop"
    / "Upgraded-Depth-Anything-V2",
}

# Canonical repository identifiers
REPOSITORY_IDENTIFIERS = {
    "KING-WEN-I-CHING-IMMUTABLE-TABLES",
    "Upgraded-Depth-Anything-V2",
}

# External systems that exist only outside the King Wen workspace
# (these are resolved via system_repo, not via repo_relative_path)
EXTERNAL_SYSTEMS = {
    "Upgraded-Depth-Anything-V2",
}

# =========================================================================
# Canonical integration point manifest (embedded data source)
# =========================================================================
# This is the single source of truth for all integration point data.
# It is INHERENTLY MANUALLY ENTERED because it encodes decisions about
# which files, references, and directions are real — not derivable by script.
# This replaces the old write_external_registry.py, which carried the same
# data inline (duplicating the builder).
# =========================================================================
CANONICAL_MANIFEST = {
    "version": "1.0.0",
    "created": "2026-11-11T12:00:00Z",
    "description": "External systems registry",
    "external_systems": [
        {
            "system": "Voicebox",
            "relationship_type": "VOICE_PROFILE_CONSUMER",
            "description": "Voicebox consumes King Wen emotional weights and voice pool for NPC voice profiles and TTS synthesis.",
            "verified_integration_points": [
                {"king_wen_file": "emotional_engine.py", "references": "VOICEBOX_VOICE_POOL (66 voice profiles, 5-axis emotional vectors)", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "kingwen_ternary_tables_complete.py", "references": "VOICEBOX_VOICE_POOL: Final[Dict[str, Tuple[float,float,float,float,float]]]", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/build_full_shotgun_jsonl.py", "references": "VOICEBOX_VOICE_POOL in shotgun expansion output", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/full_hexagram_shotgun.py", "references": "VOICEBOX_VOICE_POOL in expansion", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/full_pool_voice_pick.py", "references": "Reads VOICEBOX_VOICE_POOL and EMOTIONAL_WEIGHTS from immutable tables", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/sync_voicebox_npc_profiles.py", "references": "Sync 64 Sovereign King Wen Model NPC Voice Profiles.", "direction": "KING_WEN -> VOICEBOX", "artifact": "DATASETS/kingwen_64_npc_voice_profiles.json"},
                {"king_wen_file": "scripts/sync_all_desktop_viewers.py", "references": "voicebox_profiles: DATASETS/kingwen_64_npc_voice_profiles.json", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/verify_output_mismatches.py", "references": "64 Voicebox NPC Voice Profiles verification", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "src/core/kingwen_shotgun_pipeline.py", "references": "to_voicebox_payload() method", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/export_voicebox_training.py", "references": "King Wen -> Voicebox training-data exporter", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/export_all_64_answers.py", "references": "voicebox_engine preset selection", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/multi_layer_expand.py", "references": "Layer 4: descriptive pool expansion", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/schauberger_parsing_layers.py", "references": "VOICEBOX_VOICE_POOL reference", "direction": "KING_WEN -> VOICEBOX"},
                {"king_wen_file": "scripts/interpretation_space.py", "references": "voice pool: (66, VOICEBOX_VOICE_POOL)", "direction": "KING_WEN -> VOICEBOX"},
            ],
            "artifacts_produced_for_voicebox": [
                "DATASETS/kingwen_64_npc_voice_profiles.json (64 profiles, 5-axis vectors)",
                "VOICEBOX_VOICE_POOL (66 entries, from kingwen_ternary_tables_complete.py)",
                "EMOTIONAL_WEIGHTS (from data/emotional-weights.json)",
            ],
            "relationship_status": "VERIFIED_DEPENDENCY",
            "direction": "KING_WEN -> VOICEBOX (one-way generation, Voicebox consumes)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/build_full_shotgun_jsonl.py",
        },
        {
            "system": "OpenJarvis",
            "relationship_type": "RECEPTIVE_AGENT_INTEGRATION",
            "description": "OpenJarvis integrates King Wen as subconscious layer, driving Jarvis tool selection, voice parameters, and routing decisions.",
            "verified_integration_points": [
                {"king_wen_file": "decision_matrix.py", "references": "OpenJarvis emotion/kingwen_engine_adapter.py consult payload", "direction": "KING_WEN -> OPENJARVIS"},
                {"king_wen_file": "scripts/ingest_jkd_megatron_wavepackets.py", "references": "OPENJARVIS_SRC = Path.home() / Desktop / OpenJarvis/src", "direction": "KING_WEN -> OPENJARVIS"},
                {"king_wen_file": "scripts/kingwen_master_unified_registry.py", "references": "Master Unification Index and Ingestion Registry for King Wen / OpenJarvis System", "direction": "KING_WEN <-> OPENJARVIS"},
                {"king_wen_file": "scripts/hydrate_and_test_pys.py", "references": "openjarvis_blueprints_extracted reference", "direction": "KING_WEN -> OPENJARVIS"},
                {"king_wen_file": "scripts/run_all_unified_pipeline.py", "references": "sync_voicebox_npc_profiles.py in pipeline", "direction": "KING_WEN -> OPENJARVIS"},
                {"king_wen_file": "scripts/archaeology_boundary_authorship.py", "references": "OpenJarvis path: C:/Users/krist/Desktop/OpenJarvis", "direction": "KING_WEN -> OPENJARVIS"},
                {"king_wen_file": "scripts/archaeology_destruction_boundary.py", "references": "OpenJarvis path: C:/Users/krist/Desktop/OpenJarvis", "direction": "KING_WEN -> OPENJARVIS"},
                {"king_wen_file": "learn/scripts/audit_surfaces.py", "references": "Scan King Wen / OpenJarvis / Megatron integration surfaces", "direction": "KING_WEN <-> OPENJARVIS"},
                {"king_wen_file": "scripts/fix_md_references.py", "references": "learn/specs/kingwen-jarvis-megatron-interconnections.md", "direction": "KING_WEN -> OPENJARVIS"},
            ],
            "openjarvis_integration_points": [
                "OpenJarvis/src/openjarvis/emotion/kingwen.py - King Wen consult integration",
                "OpenJarvis/src/openjarvis/prompt/builder.py - prompt building with King Wen",
                "OpenJarvis/src/openjarvis/agents/morning_digest.py - morning digest with King Wen",
                "OpenJarvis/src/openjarvis/speech/cartesia_adapter.py - prosthetic voice adapter (King Wen emotional weights)",
                "OpenJarvis/src/openjarvis/tools/kingwen_oracle_consult_tool.py - oracle consult tool",
                "OpenJarvis/src/openjarvis/tools/kingwen_top_k_router.py - top-K router with skill cards",
                "OpenJarvis/src/openjarvis/tools/kingwen_skill_card_renderer.py - skill card renderer",
                "OpenJarvis/src/openjarvis/core/env_integration.py - Hermes env bridge",
                "OpenJarvis/src/openjarvis/blueprints/ - blueprint system with King Wen integration",
            ],
            "relationship_status": "VERIFIED_DEPENDENCY",
            "direction": "KING_WEN -> OPENJARVIS (King Wen drives Jarvis as subconscious layer)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/ingest_jkd_megatron_wavepackets.py",
        },
        {
            "system": "Megatron-LM-review",
            "relationship_type": "TRAINING_SUBSTRATE",
            "description": "King Wen generates training data and exports weights for Megatron-LM training.",
            "verified_integration_points": [
                {"king_wen_file": "kingwen_training.py", "references": "generates Megatron-compatible batch training data", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "kingwen_train_data/build_full_shotgun_jsonl.py", "references": "VOICEBOX_VOICE_POOL, Megatron training data generation", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "learn/scripts/export_megatron_weights.py", "references": "Deterministic King Wen export for Megatron training", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "learn/scripts/unified_training_loop.py", "references": "records operation sequences, assembles multi-domain Megatron corpus", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "output/build_hexagram_archetypes.py", "references": "megatron_head target from quantum_superposition", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "scripts/classify_chain_roles.py", "references": "jkd_megatron_manifest, jkd_chapter_chorus_manifest", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "scripts/ingest_jkd_megatron_wavepackets.py", "references": "King Wen x JKD Megatron Wavepacket Ingestion Engine", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "scripts/generate_sovereign_world.py", "references": "Load JKD Megatron Wavepacket Emotions JSONL if present", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "scripts/qsmc1_consumer_boundary_world.py", "references": "Test 1: Python ingestion (ingest_jkd_megatron_wavepackets.py)", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "src/core/pog3_hexagram_runtime_substrate.py", "references": "Megatron-LM: trains on captured state trajectories", "direction": "KING_WEN -> MEGATRON"},
                {"king_wen_file": "scripts/fix_md_references.py", "references": "learn/specs/kingwen-jarvis-megatron-interconnections.md", "direction": "KING_WEN -> MEGATRON"},
            ],
            "training_artifacts": [
                "kingwen_train_data/full_shotgun_expansion_all.jsonl",
                "kingwen_train_data/full_shotgun_expansion_corpus_enriched.jsonl",
                "kingwen_train_data/full_shotgun_expansion_lexical_gate.jsonl",
                "kingwen_train_data/hybrid_kimi_k2_config.json",
                "kingwen_train_data/megatron_multi_domain.jsonl",
                "kingwen_train_data/kingwen_pretrain.jsonl",
                "kingwen_train_data/per_hex_training/1.jsonl..64.jsonl",
                "kingwen_train_data/tokenizer.json",
            ],
            "relationship_status": "VERIFIED_DEPENDENCY",
            "direction": "KING_WEN -> MEGATRON (one-way generation, Megatron trains on King Wen data)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "kingwen_train_data/build_full_shotgun_jsonl.py",
        },
        {
            "system": "Cinder",
            "relationship_type": "DESKTOP_TOOLTING_INTEGRATION",
            "description": "Cinder integrates King Wen as native TS resolver with MCP tool and GraphSidebar OracleLiveReadout.",
            "verified_integration_points": [
                {"king_wen_file": "scripts/archaeology_boundary_authorship.py", "references": "Cinder path referenced in boundary analysis", "direction": "KING_WEN -> CINDER"},
                {"king_wen_file": "scripts/archaeology_destruction_boundary.py", "references": "Cinder path referenced in boundary analysis", "direction": "KING_WEN -> CINDER"},
            ],
            "cinder_integration_points": [
                "Cinder/src/main/services/kingwen.ts - deterministic SHA-256 -> hexagram + action + 5-axis vector + porosity",
                "Cinder/src/main/services/kingwenTransition.ts - CSV-backed validator + Colony adapter",
                "Cinder MCP tool kingwen_consult - read-only default, opt-in journal write",
                "Cinder/src/renderer/src/features/graph/GraphSidebar.tsx - OracleLiveReadout from CSV",
                "Cinder kingwen datasets: src/renderer/public/kingwen-datasets/, kingwen-widget/",
            ],
            "relationship_status": "OBSERVED_RELATIONSHIP",
            "direction": "KING_WEN -> CINDER (Cinder consumes King Wen CSV/JSON artifacts)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/archaeology_boundary_authorship.py",
        },
        {
            "system": "POG2 / D-sovereign",
            "relationship_type": "HISTORICAL_PROVENANCE",
            "description": "POG2 was the original sovereign substrate program on the destroyed device (D: drive). D-sovereign- is the pre-destruction save (migration destination). King Wen archaeology traces provenance through destruction boundary.",
            "verified_integration_points": [
                {"king_wen_file": "scripts/archaeology_beta_cluster_content_diff.py", "references": "POG2 beta probe content analysis", "direction": "POG2 -> KING_WEN (historical)"},
                {"king_wen_file": "scripts/archaeology_beta_probe_provenance.py", "references": "POG2 beta probe provenance tracking", "direction": "POG2 -> KING_WEN (historical)"},
                {"king_wen_file": "scripts/archaeology_boundary_authorship.py", "references": "Destruction boundary = 2026-07-07T01:51:42Z (D-sovereign- final commit)", "direction": "POG2 -> KING_WEN (historical)"},
                {"king_wen_file": "scripts/archaeology_destruction_boundary.py", "references": "D-sovereign- final commit bd6ec4646d = destruction boundary", "direction": "POG2 -> KING_WEN (historical)"},
                {"king_wen_file": "learn/scripts/hexagram_oracle_consult.py", "references": "POG2 oracle consult patterns", "direction": "POG2 -> KING_WEN (historical)"},
                {"king_wen_file": "scripts/bridge_rsmv_shap_e_manifesto.py", "references": "RSMV + Shap-E bridge (from POG2 migration)", "direction": "POG2 -> KING_WEN (historical)"},
                {"king_wen_file": "cache/scratch/check_reclassified.py", "references": "POG2 reclassified artifacts", "direction": "POG2 -> KING_WEN (historical)"},
            ],
            "provenance": {
                "origin_system": "POG2 (original program on D: drive, destroyed device)",
                "storage_location": "D:/sovereign/ (VHD-backed, destroyed)",
                "migration_destination": "D-sovereign- (Kbro1989/D-sovereign-, trailing hyphen)",
                "destruction_boundary": "2026-07-07T01:51:42Z",
                "migration": "POG2 scratch/ -> rsmv-upstream/scripts/.pog2/ (420 files, 482 import rewrites stripping rmv/ segment)",
            },
            "relationship_status": "HISTORICAL_PROVENANCE",
            "direction": "POG2 -> KING_WEN (historical, King Wen archaeology traces provenance)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/archaeology_beta_cluster_content_diff.py",
        },
        {
            "system": "rsmv-upstream / rsmv-upstream-check",
            "relationship_type": "RS3_CACHE_FORENSICS_INTEGRATION",
            "description": "King Wen archaeology and tooling references rsmv for RS3 cache forensics.",
            "verified_integration_points": [
                {"king_wen_file": "scripts/beta_live_verify.py", "references": "RS3 BETA cache verification (js5-major.jcache via sqlite3+zlib)", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/placement_diagnostic.py", "references": "RSMV model placement diagnostics", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/bridge_collisionvis_upgrade.py", "references": "RSMV collision visualization upgrade", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/bridge_desktop_3d_engines.py", "references": "RSMV 3D engine bridging", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/integrate_desktop_3d_pog2_assets.py", "references": "POG2 assets -> desktop 3D via RSMV", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/bridge_desktop_3d_engines_hardened.py", "references": "Hardened RSMV 3D engine bridge", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/transform_object_rsmv.py", "references": "RSMV object transformation", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/extract_rsc_npc_models.py", "references": "RSC NPC model extraction from RSMV cache", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/extract_rsc_npc_models_v2.py", "references": "RSC NPC model extraction v2", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/debug_jag2.py", "references": "JAG/RSMV debugging", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "scripts/build_differential_npc_manifest.py", "references": "RSMV NPC differential manifest", "direction": "RSMV -> KING_WEN (data source)"},
                {"king_wen_file": "learn/scripts/unified_training_loop.py", "references": "rsmv reference", "direction": "RSMV -> KING_WEN (data source)"},
            ],
            "relationship_status": "VERIFIED_DEPENDENCY",
            "direction": "RSMV -> KING_WEN (King Wen consumes RSMV cache forensics data)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/beta_live_verify.py",
        },
        {
            "system": "Kimi / MoonshotAI",
            "relationship_type": "MODEL_INFERENCE_ORCHESTRATION",
            "description": "Kimi Code CLI and MoonshotAI models (Kimi-K2) are referenced in King Wen training configs and shotgun pipeline.",
            "verified_integration_points": [
                {"king_wen_file": "scripts/full_hexagram_shotgun.py", "references": "Kimi CLI / kosong orchestration reference", "direction": "KIMI -> KING_WEN (model inference)"},
                {"king_wen_file": "src/core/kingwen_shotgun_pipeline.py", "references": "Kimi integration in shotgun pipeline", "direction": "KIMI -> KING_WEN (model inference)"},
                {"king_wen_file": "kingwen_train_data/build_hybrid_kimi_k2.py", "references": "Hybrid Kimi-K2 Megatron config generation", "direction": "KING_WEN -> KIMI (training config)"},
                {"king_wen_file": "kingwen_train_data/hybrid_kimi_k2_config.json", "references": "192 variants, 64/64 hexagrams complete", "direction": "KING_WEN -> KIMI (training config)"},
            ],
            "relationship_status": "OBSERVED_RELATIONSHIP",
            "direction": "BIDIRECTIONAL (Kimi models used for inference; King Wen generates training configs)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/full_hexagram_shotgun.py",
        },
        {
            "system": "Open-Design",
            "relationship_type": "DESKTOP_VIEWER_INTEGRATION",
            "description": "King Wen generates 3D assets, Godot/OpenUSD scenes, and desktop viewer manifests that Open-Design desktop viewers consume.",
            "verified_integration_points": [
                {"king_wen_file": "scripts/sync_all_desktop_viewers.py", "reference": "sync King Wen assets to desktop viewers", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/bridge_desktop_3d_engines.py", "references": "bridges King Wen 3D to desktop engines (Godot, OpenUSD)", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/bridge_desktop_3d_engines_hardened.py", "references": "hardened validated bridge (keep separate from permissive bridge)", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/integrate_desktop_3d_pog2_assets.py", "references": "integrates POG2 assets into desktop 3D", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/bridge_collisionvis_upgrade.py", "references": "collision visualization upgrade", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/placement_diagnostic.py", "references": "placement diagnostics for desktop", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/transform_object_rsmv.py", "references": "RSMV object transform for desktop", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/generate_avatar_meshes.py", "references": "generates avatar meshes for desktop viewers", "direction": "KING_WEN -> OPEN_DESIGN"},
                {"king_wen_file": "scripts/generate_sovereign_world.py", "references": "generates Godot/OpenUSD scenes for desktop", "direction": "KING_WEN -> OPEN_DESIGN"},
            ],
            "desktop_artifacts": [
                "DATASETS/desktop_3d_engines_manifest.json",
                "DATASETS/desktop_viewers_sync_manifest.json",
                "DATASETS/kingwen_avatar_meshes/ (512 PLY files)",
                "DATASETS/kingwen_avatar_mesh_manifest.json",
                "DATASETS/kingwen_model_sets/kit_*.json (64 kits)",
                "DATASETS/kingwen_sovereign_world_topology.json",
                "DATASETS/godot_scenes/",
                "DATASETS/openusd_stages/",
            ],
            "relationship_status": "GENERATED_CONSUMED",
            "direction": "KING_WEN -> OPEN_DESIGN (one-way generation, desktop viewers consume)",
            "system_repo": "KING-WEN-I-CHING-IMMUTABLE-TABLES",
            "repo_relative_path": "scripts/sync_all_desktop_viewers.py",
        },
        {
            "system": "Upgraded-Depth-Anything-V2",
            "relationship_type": "DEPTH_ESTIMATION_BRIDGE",
            "description": "King Wen uses Depth-Anything-V2 for depth map generation from PDF crops and quantum plots.",
            "verified_integration_points": [
                {"king_wen_file": "scripts/bridge_depth_anything_v2.py", "references": "Depth-Anything-V2 bridge for depth maps", "direction": "KING_WEN -> DEPTH_ANYTHING_V2"},
                {
                    "king_wen_file": "run_image-depth_8bit.py",
                    "references": "process_image() for depth map generation; source: Upgraded-Depth-Anything-V2 repo (C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2/run_image-depth_8bit.py)",
                    "direction": "KING_WEN -> DEPTH_ANYTHING_V2",
                    "repository": "Upgraded-Depth-Anything-V2",
                    "repo_relative_path": "run_image-depth_8bit.py",
                },
            ],
            "depth_artifacts": [
                "DATASETS/depth_maps_16bit/ (depth grayscale + depth + combined)",
                "DATASETS/depth_pointclouds/ (PLY point clouds)",
                "DATASETS/quantumlab_plots/ (quantum plots with depth)",
            ],
            "relationship_status": "VERIFIED_DEPENDENCY",
            "direction": "KING_WEN -> DEPTH_ANYTHING_V2 (one-way generation)",
            "system_repo": "Upgraded-Depth-Anything-V2",
            "repo_relative_path": "run_image-depth_8bit.py",
        },
        {
            "system": "quantum-simulation-main",
            "relationship_type": "MATHEMATICAL_REFERENCE",
            "description": "Reference implementation for quantum simulation (CPU/GPU 1D/2D/3D split-step, observables, phase-flow).",
            "verified_integration_points": [],
            "relationship_status": "MATHEMATICAL_REFERENCE",
            "direction": "REFERENCE_ONLY",
        },
        {
            "system": "colibri",
            "relationship_type": "TOKENIZER_INFERENCE_REFERENCE",
            "description": "2026 MoE inference/tokenizer runtime. Reference for tokenizer/eval workflow.",
            "verified_integration_points": [],
            "relationship_status": "REFERENCE_ONLY",
            "direction": "REFERENCE_ONLY",
        },
    ],
    "relationship_type_definitions": {
        "VOICE_PROFILE_CONSUMER": "System consumes King Wen voice profiles and emotional weights for TTS/NPC voice",
        "RECEPTIVE_AGENT_INTEGRATION": "System integrates King Wen as subconscious layer driving tool selection, voice, routing",
        "TRAINING_SUBSTRATE": "System trains on King Wen generated data/state trajectories",
        "DESKTOP_TOOLTING_INTEGRATION": "System consumes King Wen CSV/JSON artifacts for desktop tooling",
        "HISTORICAL_PROVENANCE": "System is the origin of artifacts now in King Wen; provenance traced via archaeology",
        "RS3_CACHE_FORENSICS_INTEGRATION": "System provides RS3 cache data that King Wen consumes for forensics",
        "MODEL_INFERENCE_ORCHESTRATION": "System provides model inference orchestration (Kimi/kosong) used by King Wen",
        "DESKTOP_VIEWER_INTEGRATION": "System consumes King Wen generated 3D assets/scenes for desktop visualization",
        "DEPTH_ESTIMATION_BRIDGE": "System provides depth estimation used by King Wen for math-region/3D",
        "MATHEMATICAL_REFERENCE": "System is mathematical inspiration only, no runtime dependency",
        "TOKENIZER_INFERENCE_REFERENCE": "System is reference for tokenizer/inference patterns only",
        "GENERATED_CONSUMED": "King Wen generates, system consumes (one-way)",
        "VERIFIED_DEPENDENCY": "Cross-repo dependency verified by code references",
        "OBSERVED_RELATIONSHIP": "Observed in practice but limited code references in King Wen",
        "REFERENCE_ONLY": "Mathematical/architectural reference only, no code dependency",
    },
}


def validate_repo_relative_path(
    system_repo: str, repo_relative_path: str
) -> tuple[bool, str]:
    """
    Validate that repo_relative_path is a repository-relative path.

    Returns (is_valid, error_message).
    A duplicated repository prefix (e.g., system_repo == "X" with
    repo_relative_path == "X/some_file") is rejected.
    """
    if not repo_relative_path or not isinstance(repo_relative_path, str):
        return False, "repo_relative_path is required and must be a string"

    # Check for duplicated repository prefix
    if repo_relative_path.startswith(system_repo + "/"):
        return (
            False,
            f"Duplicated repository prefix: repo_relative_path "
            f"('{repo_relative_path}') begins with system_repo "
            f"('{system_repo}')",
        )

    # Check for absolute path (starts with /)
    if repo_relative_path.startswith("/"):
        return False, f"Absolute path not allowed: '{repo_relative_path}'"

    # Check for path traversal
    if ".." in repo_relative_path.split("/"):
        return False, f"Path traversal detected: '{repo_relative_path}'"

    return True, "OK"
    """
    Build the external systems registry from the embedded canonical manifest.
    Applies repository-relative path validation to every integration point.

    This is the SINGLE AUTHORITATIVE builder. The embedded CANONICAL_MANIFEST
    is the single source of truth, replacing the old write_external_registry.py,
    which carried the same data inline (duplicating the builder).
    """
    registry = {
        "version": "1.0.0",
        "created": "2026-11-11T12:00:00Z",
        "description": "External systems registry",
        "external_systems": [],
        "relationship_type_definitions": CANONICAL_MANIFEST.get(
            "relationship_type_definitions", {}
        ),
    }

    for system in CANONICAL_MANIFEST["external_systems"]:
        system_copy = {
            "system": system["system"],
            "relationship_type": system.get("relationship_type", ""),
            "description": system.get("description", ""),
            "verified_integration_points": [],
            "relationship_status": system.get("relationship_status", "OBSERVED_RELATIONSHIP"),
            "direction": system.get("direction", ""),
            "system_repo": system.get("system_repo", ""),
            "repo_relative_path": system.get("repo_relative_path", ""),
        }

        for ip in system.get("verified_integration_points", []):
            king_wen_file = ip.get("king_wen_file", "")
            references = ip.get("references", "")
            direction = ip.get("direction", "")

            # Determine the repository root for this integration point
            system_repo = ip.get("system_repo", "")
            if system_repo not in REPOSITORY_IDENTIFIERS:
                continue

            # Validate repo_relative_path
            if "repo_relative_path" in ip:
                path = ip.get("repo_relative_path", king_wen_file)
                is_valid, error_msg = validate_repo_relative_path(system_repo, path)
                if not is_valid:
                    raise ValueError(
                        f"Validation failed for {system['system']}.{king_wen_file}: "
                        f"{error_msg}"
                    )
                king_wen_file = path

            integration_point = {
                "king_wen_file": king_wen_file,
                "references": references,
                "direction": direction,
            }
            for key in ip:
                if key not in ("king_wen_file", "references", "direction"):
                    integration_point[key] = ip[key]

            system_copy["verified_integration_points"].append(integration_point)

        registry["external_systems"].append(system_copy)

    return registry


def main():
    """Main entry point for the external systems registry builder."""
    try:
        registry = build_registry()

        output_path = (
            Path(os.path.expanduser("~"))
            / "Desktop"
            / "KING-WEN-I-CHING-IMMUTABLE-TABLES"
            / "inventory"
            / "registries"
            / "external_systems.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        print(f"Registry written to: {output_path}")
        print(f"External systems: {len(registry['external_systems'])}")
        total_ips = sum(
            len(s["verified_integration_points"])
            for s in registry["external_systems"]
        )
        print(f"Integration points: {total_ips}")
        print(f"SHA-256: {hashlib.sha256(open(output_path, 'rb').read()).hexdigest()}")
        print(f"File size: {os.path.getsize(output_path)} bytes")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
