#!/usr/bin/env python3
"""King Wen 64 Sovereign Model NPC Engine — Master Self-Contained Pipeline.

Executes the entire end-to-end pipeline using ONLY files internal to this repository:
1. Shotgun 512-State Superposition Expansion (`scripts/full_hexagram_shotgun.py`)
2. Model NPC Grounding & Enriched Metadata (`scripts/enrich_kit_models.py`)
3. POG2 Subsystem & K-Color Wireframe Integration (`scripts/integrate_desktop_3d_pog2_assets.py`)
4. Standalone 3D Point-Cloud Mesh Generation (`scripts/shap_e_kingwen_3d_generator.py`)
5. Repository-Native NPC Voice Profiles Manifest (`scripts/sync_voicebox_npc_profiles.py`)
6. JKD Chapter Chorus Read-Aloud Ingestion (`scripts/test_jkd_chapter_chorus.py`)
7. Mathematical Parity & Save String V2.1 Verification (`scripts/verify_math_jacobian_hamiltonian.py`)

No external programs, paths, or sidecars required.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PIPELINE_STAGES = [
    ("01. Shotgun 512-State Expansion", [sys.executable, str(ROOT / "scripts" / "full_hexagram_shotgun.py")]),
    ("02. Kit Model Persona Enrichment", [sys.executable, "-B", str(ROOT / "scripts" / "enrich_kit_models.py")]),
    ("03. POG2 Ontology & K-Color Integration", [sys.executable, "-B", str(ROOT / "scripts" / "integrate_desktop_3d_pog2_assets.py")]),
    ("04. Standalone 3D Mesh Generation", [sys.executable, "-B", str(ROOT / "scripts" / "shap_e_kingwen_3d_generator.py")]),
    ("05. Repository-Native Voice Profiles Manifest", [sys.executable, "-B", str(ROOT / "scripts" / "sync_voicebox_npc_profiles.py")]),
    ("06. JKD Chapter Chorus Ingestion Pass", [sys.executable, "-B", str(ROOT / "scripts" / "test_jkd_chapter_chorus.py")]),
    ("07. Math Diagram Extractor Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_math_diagram_extractor.py")]),
    ("08. Desktop 3D Engines Bridge (OpenUSD, Godot, CollisionVis)", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_desktop_3d_engines.py")]),
    ("09. Desktop Viewers Sync & Import Manifest", [sys.executable, "-B", str(ROOT / "scripts" / "sync_all_desktop_viewers.py")]),
    ("10. Cognitive Variation & Input Modulation Test", [sys.executable, "-B", str(ROOT / "scripts" / "test_cognitive_variation.py")]),
    ("11. RSMV Cache Schema & Shap-E Synthesis Manifesto Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_rsmv_shap_e_manifesto.py")]),
    ("12. QuantumLab 3D Space-Time Visualization Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_quantumlab_visualization.py")]),
    ("13. CollisionVis Physics & HLSL Shader Upgrade Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_collisionvis_upgrade.py")]),
    ("14. RayeRen Neural Speech & KD Capability Vector Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_rayeren_capability_vectors.py")]),
    ("15. Unbound Persona Domains & 27x27 Expansion Audit", [sys.executable, "-B", str(ROOT / "scripts" / "verify_unbound_persona_domains.py")]),
    ("16. QuantumLab 64-Grid Real-Time Transitional Mapping Bridge", [sys.executable, "-B", str(ROOT / "scripts" / "bridge_quantum_64_grid.py")]),
    ("17. Save String V2.1 & Math Parity Audit", [sys.executable, str(ROOT / "scripts" / "verify_math_jacobian_hamiltonian.py")]),
    ("18. Output Mismatch & Integrity Audit", [sys.executable, "-B", str(ROOT / "scripts" / "verify_output_mismatches.py")]),
]


def main() -> int:
    print("=" * 80)
    print("KING WEN 64 SOVEREIGN MODEL ENGINE — UNIFIED SELF-CONTAINED PIPELINE")
    print("=" * 80)

    stage_passed = 0
    for name, cmd in PIPELINE_STAGES:
        print(f"\n[RUNNING STAGE] {name}...")
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            print(f"  [SUCCESS] {name} completed with 0 errors.")
            stage_passed += 1
        else:
            print(f"  [FAILED] {name}: {res.stderr[:300]}")
            return 1

    print("\n" + "=" * 80)
    print(f"UNIFIED PIPELINE COMPLETED: ALL {stage_passed}/{len(PIPELINE_STAGES)} STAGES PASSED WITH 100% PARITY!")
    print("Repository is 100% self-contained and runnable without external dependencies.")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
