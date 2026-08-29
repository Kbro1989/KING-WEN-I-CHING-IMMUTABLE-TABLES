# scripts/

Active generation, bridge, and verification surface for the King Wen 64 Sovereign Model Engine.

## Unified 18-Stage Self-Contained Pipeline (`run_all_unified_pipeline.py`)

Run all stages with 100% self-contained parity:
```bash
python scripts/run_all_unified_pipeline.py
```

| Stage | Script | Description |
|---|---|---|
| **01** | `full_hexagram_shotgun.py` | 512-state Hamiltonian expansion & CSV datasets |
| **02** | `enrich_kit_models.py` | NPC model kit persona & skill card enrichment |
| **03** | `bridge_pog2_ontology.py` | POG2 ontology, K-color & CNS module integration |
| **04** | `shap_e_kingwen_3d_generator.py` | 729-vertex deterministic parametric PLY generator |
| **05** | `sync_voicebox_npc_profiles.py` | 64-model FastSpeech/WaveNet voice profiles manifest |
| **06** | `test_jkd_chapter_chorus.py` | 64 audio pellet JKD chapter chorus ingestion |
| **07** | `bridge_math_diagram_extractor.py` | Mathematical diagram extraction bridge |
| **08** | `bridge_desktop_3d_engines.py` | OpenUSD, Godot scene, and CollisionVis generator |
| **09** | `sync_all_desktop_viewers.py` | Desktop viewers sync & import manifest |
| **10** | `test_cognitive_variation.py` | Cognitive variation & input modulation test |
| **11** | `bridge_rsmv_shap_e_manifesto.py` | RSMV cache schema & Shap-E synthesis manifesto |
| **12** | `bridge_quantumlab_visualization.py` | 3D space-time wave packet evolution plots |
| **13** | `bridge_collisionvis_upgrade.py` | CollisionVis physics & HLSL shader upgrade |
| **14** | `bridge_rayeren_capability_vectors.py` | RayeRen neural speech & KD capability vectors |
| **15** | `verify_unbound_persona_domains.py` | 27×27 (729) unbound persona domain matrix audit |
| **16** | `bridge_quantum_64_grid.py` | QuantumLab 64-grid transitional density mapping |
| **17** | `verify_math_jacobian_hamiltonian.py` | SaveString V2.1 & Jacobian/Hamiltonian audit |
| **18** | `verify_output_mismatches.py` | Exhaustive 64-component output mismatch audit |

## Hardware & VHDL Generators
- `generate_vhdl_roms.py` — Emits `KingWen9BitResolver.vhd` from `HEXAGRAM_BASE`.
- `generate_vhdl_testbench.py` — Emits `tb_KingWen9BitResolver.vhd` and `KingWenExpected_pkg.vhd`.
- `verify_vhdl_resolver_parity.py` — 512-address functional VHDL simulation with 0 failures.

## Full Expansion Artifacts
- `ternary_full_expansion.json` — 27 trigrams, 729 hexagrams, 5,832 resolved states (2.9 MB)
- `hexagram_full_expansion.json` — 64 hexagrams, 512 resolved states, personalities, inversion pairs
