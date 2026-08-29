import json
import sys
from pathlib import Path

ROOT = Path(r"c:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE

# Load auxiliary data
voice_profiles = json.loads((ROOT / "DATASETS/kingwen_64_npc_voice_profiles.json").read_text(encoding="utf-8"))
voice_map = {vp["hexagram_id"]: vp for vp in (voice_profiles if isinstance(voice_profiles, list) else voice_profiles.get("voice_profiles", []))}

quantum_ts = json.loads((ROOT / "DATASETS/quantum_field_timeseries_readout.json").read_text(encoding="utf-8"))

def build_differential_manifest():
    print("=" * 80)
    print("BUILDING DIFFERENTIAL SOVEREIGN NPC MANIFEST & RE-HYDRATION INCLUSION LINKS")
    print("=" * 80)

    # 1. System-wide Invariant Baseline Schema (Same across all NPCs)
    shared_invariant_baseline = {
        "spatial_grid": {
            "dimensions": [8, 8],
            "total_nodes": 64,
            "bounds": {"x": [-28.0, 28.0], "z": [-28.0, 28.0]},
            "node_spacing": 8.0
        },
        "temporal_phase_topology": {
            "total_phases": 8,
            "phases": ["past (T0)", "present (T1)", "future (T2)", "transition (T3)", "resolution (T4)", "dissolution (T5)", "crystallization (T6)", "void (T7)"],
            "phase_bits": ["0b000", "0b001", "0b010", "0b011", "0b100", "0b101", "0b110", "0b111"]
        },
        "state_spaces": {
            "binary_phase_states": 512,
            "ternary_manifold_states": 729,
            "total_resolved_phase_states": 5832
        },
        "coordinate_systems": {
            "emotional_axes": ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"],
            "coprime_prime_extractor": [97, 89, 83, 79, 73],
            "skill_slots_per_npc": 12,
            "k_color_segments_per_npc": 16,
            "schauberger_vortex_physics": "centripetal_implosion"
        },
        "superposition_rule": "ZERO_COLLAPSE_CONTINUOUS_MANIFOLD"
    }

    npc_manifest_records = []

    for h_id in range(1, 65):
        base = HEXAGRAM_BASE[h_id]
        kit_path = ROOT / f"DATASETS/kingwen_model_sets/kit_{h_id}.json"
        kit_data = json.loads(kit_path.read_text(encoding="utf-8"))
        grounded = kit_data.get("grounded_npc", {})

        # Compute differential vector variables
        u_idx = base.get("upper_idx", 1)
        l_idx = base.get("lower_idx", 1)
        vortex_tension = round((u_idx * l_idx) / 49.0, 4)
        suction_coeff = round((u_idx + l_idx) / 14.0, 4)

        # Multi-engine inclusion links for instant re-hydration
        inclusion_links = {
            "shap_e_3d_mesh": f"DATASETS/kingwen_3d_meshes/shap_e_hex_{h_id:02d}.ply",
            "openusd_stage": f"DATASETS/openusd_stages/npc_hex_{h_id:02d}.usda",
            "godot_scene": f"DATASETS/godot_scenes/npc_hex_{h_id:02d}.tscn",
            "rsmv_model": f"DATASETS/kingwen_rsmv_models/hex_{h_id:02d}_models.json",
            "collisionvis_physics": "DATASETS/collisionvis_physics/collisionvis_64_npc_physics.json",
            "quantum_space_time_3d_plot": f"DATASETS/quantumlab_plots/quantum_3d_hex_{h_id:02d}.png",
            "quantum_pellet_2d_heatmap": f"DATASETS/quantumlab_plots/quantum_2d_hex_{h_id:02d}.png",
            "phase_avatar_meshes": [
                f"DATASETS/kingwen_avatar_meshes/hex{h_id:02d}_phase{p}.ply"
                for p in range(8)
            ]
        }

        # Differential identity payload
        diff_npc_record = {
            "hexagram_id": h_id,
            "differential_identity": {
                "name": base["name"],
                "hanzi": grounded.get("unicode", base.get("unicode")),
                "binary_bottom_to_top": base["binary_bottom_to_top"],
                "binary_top_to_bottom": base["binary_top_to_bottom"],
                "upper_trigram": base["upper_trigram"],
                "lower_trigram": base["lower_trigram"],
                "archetype": grounded.get("agent_type", "architect"),
                "category": base["category"],
                "action": base["action"],
                "coder_specialty": grounded.get("coder_specialty", "Dev"),
                "rs3_actionable": grounded.get("rs3_actionable", "gather"),
                "personality_codename": grounded.get("personality_codename", f"NPC-{h_id}")
            },
            "differential_parameters": {
                "emotional_vector": grounded.get("emotional_vector", {}),
                "voice_mode": grounded.get("hermes_voice_mode", "transit"),
                "voice_profile": voice_map.get(h_id, {}),
                "schauberger_vortex": {
                    "motion_type": "centripetal",
                    "vortex_tension": vortex_tension,
                    "suction_coefficient": suction_coeff,
                    "temperature_anomaly_dev": round(0.15 + (h_id * 0.01), 3)
                },
                "k_color_palette": kit_data.get("k_color_palette", {}),
                "skill_cards": kit_data.get("skill_cards", []),
                "quantum_timeseries_summary": quantum_ts.get(str(h_id), {})
            },
            "inclusion_links": inclusion_links
        }

        # Re-attach inclusion_links directly into the kit model file
        kit_data["inclusion_links"] = inclusion_links
        kit_path.write_text(json.dumps(kit_data, ensure_ascii=False, indent=2), encoding="utf-8")

        npc_manifest_records.append(diff_npc_record)

    # Master Manifest Assembly
    master_manifest = {
        "manifest_version": "2.1.0",
        "description": "King Wen 64 Sovereign NPC Differential Manifest & Multi-Engine Inclusion Graph",
        "shared_invariants": shared_invariant_baseline,
        "total_sovereign_npcs": len(npc_manifest_records),
        "npcs": npc_manifest_records
    }

    out_file = ROOT / "DATASETS" / "kingwen_differential_npc_manifest.json"
    out_file.write_text(json.dumps(master_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[SUCCESS] Re-hydrated all 64 kit_*.json files with direct multi-engine inclusion links.")
    print(f"[SUCCESS] Exported Differential Sovereign NPC Manifest to: {out_file}")
    print("=" * 80)
    print("DIFFERENTIAL NPC MANIFEST & RE-HYDRATION: 100% COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    build_differential_manifest()
