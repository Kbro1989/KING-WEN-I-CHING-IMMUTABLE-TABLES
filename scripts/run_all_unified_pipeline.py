#!/usr/bin/env python3
"""King Wen 64 Sovereign Model NPC Engine — Master Self-Contained Pipeline.

Executes the entire end-to-end pipeline using ONLY files internal to this repository.
Each stage reads from the output of all prior stages. generate_sovereign_world.py is LAST.

Stage dependency order (data flows must not be skipped):
  00. prewarm_quantum_wavepackets.py     → quantum_prewarm_cache.npz + quantum_prewarm_manifest.json
  01. full_hexagram_shotgun.py           → 64×8 phase states, all kit JSON wave packet fields
  02. update_3d_kits_with_quantum_wavepackets.py → 64 kit JSONs (quantum_wave_packet + yao_pellets)
  03. enrich_kit_models.py               → enriched kit personas reading layer-02 output
  04. ingest_jkd_megatron_wavepackets.py → jkd_megatron_wavepacket_emotions.jsonl (2471 chunks)
  05-20. bridges, audits, verifications  → all read enriched kit output
  21. generate_sovereign_world.py        → FINAL: reads prewarm cache + kits + JKD corpus → 3D world

No external programs, paths, or sidecars required.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PIPELINE_STAGES = [
    # -- LAYER 0: QUANTUM WAVE PACKET PRE-WARM (must run first -- all downstream reads this cache) --
    ("00. Quantum Wave Packet Pre-Warm (1D->2D->3D, 5832 states)", [sys.executable, str(ROOT / "scripts" / "prewarm_quantum_wavepackets.py")]),

    # -- LAYER 1: SHOTGUN -- 512-state superposition expansion across all 64 --
    ("01. Shotgun 512-State Expansion (64x8 vortex blast)", [sys.executable, str(ROOT / "scripts" / "full_hexagram_shotgun.py")]),

    # -- LAYER 2: INJECT wave packets from shotgun into 64 model kit JSONs --
    ("02. Inject Quantum Wave Packets & 6-Yao Pellets into 64 3D Kits", [sys.executable, "-B", str(ROOT / "scripts" / "update_3d_kits_with_quantum_wavepackets.py")]),

    # -- LAYER 3: KIT ENRICHMENT -- reads kits written in layer 2 --
    ("03. Kit Model Persona Enrichment", [sys.executable, "-B", str(ROOT / "scripts" / "enrich_kit_models.py")]),

    # -- LAYER 4: CORPUS INGESTION -- JKD megatron wave packet emotions mapped to 64 hexagrams --
    ("04. JKD Megatron Wave Packet Emotion Ingestion (2471 chunks -> 64 hexagrams)", [sys.executable, "-B", str(ROOT / "scripts" / "ingest_jkd_megatron_wavepackets.py")]),

    # -- LAYER 5: 3D ASSET BRIDGES -- read enriched kits --
    ("05. POG2 Ontology & K-Color Integration", [sys.executable, "-B", str(ROOT / "scripts" / "integrate_desktop_3d_pog2_assets.py")]),
    ("06. Standalone 3D Mesh Generation", [sys.executable, "-B", str(ROOT / "scripts" / "shap_e_kingwen_3d_generator.py")]),
    ("07. Repository-Native Voice Profiles Manifest", [sys.executable, "-B", str(ROOT / "scripts" / "sync_voicebox_npc_profiles.py")]),
    ("08. JKD Chapter Chorus Ingestion Pass", [sys.executable, "-B", str(ROOT / "scripts" / "test_jkd_chapter_chorus.py")]),
    ("09. Math Diagram Extractor Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_math_diagram_extractor.py")]),
    ("10. Desktop 3D Engines Bridge (OpenUSD, Godot, CollisionVis)", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_desktop_3d_engines.py")]),
    ("11. Desktop Viewers Sync & Import Manifest", [sys.executable, "-B", str(ROOT / "scripts" / "sync_all_desktop_viewers.py")]),
    ("12. Cognitive Variation & Input Modulation Test", [sys.executable, "-B", str(ROOT / "scripts" / "test_cognitive_variation.py")]),
    ("13. RSMV Cache Schema & Shap-E Synthesis Manifesto Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_rsmv_shap_e_manifesto.py")]),
    ("14. QuantumLab 3D Space-Time Visualization Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_quantumlab_visualization.py")]),
    ("15. CollisionVis Physics & HLSL Shader Upgrade Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_collisionvis_upgrade.py")]),
    ("16. RayeRen Neural Speech & KD Capability Vector Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_rayeren_capability_vectors.py")]),
    ("17. Unbound Persona Domains & 27x27 Expansion Audit", [sys.executable, "-B", str(ROOT / "scripts" / "verify_unbound_persona_domains.py")]),
    ("18. QuantumLab 64-Grid Real-Time Transitional Mapping Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_quantum_64_grid.py")]),
    ("19. Save String V2.1 & Math Parity Audit", [sys.executable, str(ROOT / "scripts" / "verify_math_jacobian_hamiltonian.py")]),
    ("20. Output Mismatch & Integrity Audit", [sys.executable, "-B", str(ROOT / "scripts" / "verify_output_mismatches.py")]),

    # -- LAYER FINAL: 3D WORLD -- runs last, reads ALL upstream output --
    # prewarm_cache.npz -> quantum_wave_packet kit data -> jkd_passages -> yao_pellets -> sovereign world
    ("21. Generate 64-Sovereign 3D World (egg + vortex + JKD unison + 384 pellets)", [sys.executable, "-B", str(ROOT / "scripts" / "generate_sovereign_world.py")]),
]


def main() -> int:
    print("=" * 80)
    print("KING WEN 64 SOVEREIGN MODEL ENGINE -- UNIFIED SELF-CONTAINED PIPELINE (22 STAGES)")
    print("Stage 00 (prewarm) -> Stage 01 (shotgun) -> ... -> Stage 21 (generate_sovereign_world)")
    print("=" * 80)

    sub_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    stage_passed = 0
    for name, cmd in PIPELINE_STAGES:
        print(f"\n[RUNNING STAGE] {name}...")
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", env=sub_env)
        if res.returncode == 0:
            print(f"  [SUCCESS] {name} completed with 0 errors.")
            stage_passed += 1
        else:
            print(f"  [FAILED] {name}:\n{res.stderr[:600]}")
            return 1

    print("\n" + "=" * 80)
    print(f"UNIFIED PIPELINE COMPLETED: ALL {stage_passed}/{len(PIPELINE_STAGES)} STAGES PASSED -- 100% FULL OUTPUT")
    print("quantum_prewarm_cache -> shotgun -> kits -> JKD corpus -> 3D sovereign world: COMPLETE")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
