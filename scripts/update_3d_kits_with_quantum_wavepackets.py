"""
update_3d_kits_with_quantum_wavepackets.py — Injects quantum wave packets & 6-yao sound pellet harmonics into all 64 model kit JSON files (DATASETS/kingwen_model_sets/kit_1.json .. kit_64.json).

Connects VHDL 9-bit resolver state space (512 binary phase states) & 729 ternary manifold states directly into the 3D model kit definitions and sovereign world generator.
"""

import json, math, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE

def update_kits():
    print("=" * 80)
    print("INJECTING QUANTUM WAVE PACKETS & 6-YAO SOUND PELLETS INTO 64 3D MODEL KITS")
    print("=" * 80)

    kits_dir = ROOT / "DATASETS" / "kingwen_model_sets"
    updated_count = 0

    for h_id in range(1, 65):
        kit_file = kits_dir / f"kit_{h_id}.json"
        if not kit_file.exists():
            print(f"Warning: {kit_file.name} missing, skipping.")
            continue

        try:
            kit_data = json.loads(kit_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error loading {kit_file.name}: {e}")
            continue

        base = HEXAGRAM_BASE[h_id]
        binary_str = base.get("binary_bottom_to_top", base.get("binary", "111111"))
        u_idx = base.get("upper_idx", 0)
        l_idx = base.get("lower_idx", 0)

        # Spatial grid coordinate
        row = (h_id - 1) // 8
        col = (h_id - 1) % 8
        world_x = (col - 3.5) * 70.0
        world_z = (row - 3.5) * 70.0
        elevation = math.sin(col * 0.8) * math.cos(row * 0.8) * 14.0 + (u_idx * 2.5) + (l_idx * 1.5)

        norm_x = world_x / 280.0
        norm_z = world_z / 280.0
        norm_y = elevation / 35.0
        norm_r = math.sqrt(norm_x**2 + norm_z**2)
        spatial_theta = math.atan2(world_z, world_x)

        # Quantum physics parameters derived from VHDL & spatial tensor
        vortex_tension = round((u_idx * l_idx) / 49.0, 4)
        porosity_level = round(0.15 + u_idx * 0.05 + l_idx * 0.03, 3)
        fundamental_freq_hz = round(108.0 * (1.0 + 0.40 * norm_r + 0.25 * norm_y + 0.15 * math.sin(3.0 * spatial_theta + norm_y * math.pi)), 2)

        # 6-Yao Line Sound Pellets
        yao_pellets = []
        for line_idx in range(6):
            bit = int(binary_str[line_idx]) if line_idx < len(binary_str) else 1
            is_changing = (h_id % 7 == line_idx) or (u_idx == l_idx and line_idx == 2)
            ternary_state = 2 if is_changing else (1 if bit == 1 else 0)

            orbit_radius = round(6.0 + line_idx * 2.2, 2)
            orbital_speed = round(0.5 + (line_idx + 1) * 0.25 * (1.0 + vortex_tension) * (1.2 if ternary_state == 2 else 1.0), 3)

            line_ratio = 1.0 + (line_idx / 6.0) * 0.618
            line_phase_mod = 1.0 + 0.12 * math.cos(spatial_theta * (line_idx + 1) + elevation / 10.0)
            ternary_mult = 1.18 if ternary_state == 2 else (1.0 if ternary_state == 1 else 0.82)
            freq_hz = round(fundamental_freq_hz * line_ratio * ternary_mult * line_phase_mod * (1.0 + vortex_tension * 0.20), 2)

            if ternary_state == 1:
                line_type = "yang"
                color_hex = "#FFD700"
                waveform = "triangle"
                energy = 1.0
            elif ternary_state == 0:
                line_type = "yin"
                color_hex = "#38BDF8"
                waveform = "sine"
                energy = 0.6
            else:
                line_type = "yao"
                color_hex = "#A855F7"
                waveform = "sawtooth"
                energy = 1.4

            yao_pellets.append({
                "line_position": line_idx + 1,
                "sub_trigram": "lower" if line_idx < 3 else "upper",
                "sub_position": (line_idx % 3) + 1,
                "ternary_state": ternary_state,
                "line_type": line_type,
                "waveform": waveform,
                "orbit_radius": orbit_radius,
                "orbital_speed": orbital_speed,
                "color_hex": color_hex,
                "energy_intensity": energy,
                "frequency_hz": freq_hz
            })

        # Inject quantum wave packet metadata block into model kit
        kit_data["quantum_wave_packet"] = {
            "hexagram_id": h_id,
            "vhdl_address_base": (h_id - 1) * 8,
            "vhdl_address_range": [(h_id - 1) * 8, (h_id - 1) * 8 + 7],
            "binary_phase_str": binary_str,
            "upper_trigram_index": u_idx,
            "lower_trigram_index": l_idx,
            "vortex_tension": vortex_tension,
            "porosity_level": porosity_level,
            "fundamental_frequency_hz": fundamental_freq_hz,
            "spatial_elevation_m": round(elevation, 4),
            "sound_pellets": yao_pellets
        }

        kit_file.write_text(json.dumps(kit_data, indent=2), encoding="utf-8")
        updated_count += 1

    print(f"Successfully updated {updated_count}/64 3D model kits with quantum wave packets & 6-yao sound pellets.")
    return 0

if __name__ == "__main__":
    sys.exit(update_kits())
