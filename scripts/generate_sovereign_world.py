import base64
import io
import json
import math
import sys
import wave
from pathlib import Path

ROOT = Path(r"c:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE
from emotional_engine import EMOTIONAL_WEIGHTS, _compute_consensus_from_resolved
from full_hexagram_shotgun import shotgun_expand
from scripts.generate_deterministic_64_color_spectrum import TRIGRAM_TEMP, hsl_to_rgb_hex
from scripts.full_hexagram_shotgun import _ternary_slot_matrix

def prewarm_egg_keyframes(sectors, num_frames=60):
    """Pre-computes 60 keyframes of 3D Centripetal Egg vertex deformation from all 64 citadel vortex outputs."""
    segs_w, segs_h = 48, 36
    verts = []
    for j in range(segs_h + 1):
        v = j / segs_h
        theta = v * math.pi
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        for i in range(segs_w + 1):
            u = i / segs_w
            phi = u * 2.0 * math.pi
            x = 340.0 * sin_theta * math.cos(phi)
            y = 340.0 * cos_theta
            z = 340.0 * sin_theta * math.sin(phi)
            verts.append((x, y, z))

    sec_influences = []
    for s in sectors:
        pos = s["world_position"]
        qp = s["quantum_physics"]
        avg_pellet_e = sum(p.get("energy_intensity", 0.5) for p in s["yao_pellets"]) / 6.0
        sec_influences.append({
            "nx": pos["x"] / 280.0,
            "nz": pos["z"] / 280.0,
            "tension": qp.get("vortex_tension", 0.5),
            "suction": qp.get("suction_coefficient", 0.3),
            "porosity": qp.get("porosity_level", 0.45),
            "energy": avg_pellet_e,
            "freqs": [p.get("frequency_hz", 146.0) for p in s["yao_pellets"]]
        })

    keyframes = []
    for f_idx in range(num_frames):
        t = f_idx * (2.0 * math.pi / num_frames)
        frame_coords = []
        for vx, vy, vz in verts:
            length = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.0
            nx, ny, nz = vx / length, vy / length, vz / length
            norm_y = vy / 340.0

            radial_disp = 0.0
            angular_twist = 0.0
            for s_idx, si in enumerate(sec_influences):
                align = nx * si["nx"] + nz * si["nz"]
                pellet_phase = sum(
                    math.sin(t * (freq / 108.0) * 0.4 + s_idx * 0.098 + p_i * 1.047)
                    for p_i, freq in enumerate(si["freqs"])
                ) / 6.0
                implosion = si["tension"] * si["suction"] * si["energy"]
                radial_disp += align * implosion * 28.0 * pellet_phase
                angular_twist += si["porosity"] * align * math.sin(norm_y * math.pi + t * 1.2 + s_idx * 0.049) * 8.0

            scale = 1.0 + (radial_disp + angular_twist) / 340.0
            frame_coords.extend([round(vx * scale, 2), round(vy * scale, 2), round(vz * scale, 2)])
        keyframes.append(frame_coords)

    return keyframes

def prewarm_unison_audio_wav_b64(sectors, duration_sec=4.0, sample_rate=22050):
    """Pre-renders 384 sound pellet wavepacket ground field PCM audio buffer into Base64 WAV."""
    num_samples = int(duration_sec * sample_rate)
    buffer = [0.0] * num_samples

    for sec in sectors:
        for p in sec["yao_pellets"]:
            freq = p.get("frequency_hz", 146.0)
            amp = p.get("energy_intensity", 0.5) * 0.008
            w_type = p.get("waveform", "sine")
            omega = 2.0 * math.pi * freq / sample_rate

            for i in range(num_samples):
                t_sample = i * omega
                if w_type == "sine":
                    val = math.sin(t_sample)
                elif w_type == "triangle":
                    val = 2.0 * abs(2.0 * (t_sample / (2.0 * math.pi) - math.floor(t_sample / (2.0 * math.pi) + 0.5))) - 1.0
                else:
                    val = 2.0 * (t_sample / (2.0 * math.pi) - math.floor(t_sample / (2.0 * math.pi) + 0.5))
                buffer[i] += val * amp

    import struct
    max_peak = max(abs(s) for s in buffer) or 1.0
    norm_factor = 0.90 / max_peak

    byte_io = io.BytesIO()
    with wave.open(byte_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        pcm_bytes = bytearray()
        for sample in buffer:
            val_int = int(max(-32767, min(32767, sample * norm_factor * 32767.0)))
            pcm_bytes.extend(struct.pack('<h', val_int))
        wav_file.writeframes(pcm_bytes)

    return base64.b64encode(byte_io.getvalue()).decode('ascii')


def _hue_to_rgb(hue_deg):
    """Convert a 0-360 hue (full saturation, 50% lightness) to (r, g, b) floats 0-1."""
    h = hue_deg / 60.0
    hi = int(h) % 6
    f = h - int(h)
    q, t = 1.0 - f, f
    lut = [(1, t, 0), (q, 1, 0), (0, 1, t), (0, q, 1), (t, 0, 1), (1, 0, q)]
    return lut[hi]

def generate_sovereign_world():
    print("=" * 85)
    print("GENERATING KING WEN 64-SOVEREIGN MACRO-WORLD WITH REAL VORTEX, POROSITY & PELLETS")
    print("=" * 85)

    # 1. Temporal Biome & Regional Zone Taxonomy (8 Canonical Sectors)
    temporal_biomes = {
        0: {"name": "Past Domain (Primordial Granite)", "color": "#4B5563", "accent": "#9CA3AF", "ambient": 0.3},
        1: {"name": "Present Domain (Solar Citadel)", "color": "#F59E0B", "accent": "#FDE047", "ambient": 0.8},
        2: {"name": "Future Domain (Auroral Expanse)", "color": "#10B981", "accent": "#6EE7B7", "ambient": 0.6},
        3: {"name": "Transition Domain (Tectonic Rift)", "color": "#EF4444", "accent": "#FCA5A5", "ambient": 0.5},
        4: {"name": "Resolution Domain (Crystalline Plateau)", "color": "#3B82F6", "accent": "#93C5FD", "ambient": 0.7},
        5: {"name": "Dissolution Domain (Abyssal Ocean)", "color": "#6366F1", "accent": "#A5B4FC", "ambient": 0.4},
        6: {"name": "Crystallization Domain (Obsidian Spire)", "color": "#8B5CF6", "accent": "#C4B5FD", "ambient": 0.5},
        7: {"name": "Void Domain (Null Field Expanse)", "color": "#1F2937", "accent": "#64748B", "ambient": 0.2}
    }

    # 2. Build 64 World Sectors with full Quantum Physics Nodes
    sectors = []
    heightmap_grid = []

    # Load DA-V2 Depth Manifest if present
    da2_manifest_path = ROOT / "DATASETS" / "depth_anything_v2_manifest.json"
    da2_lookup = {}
    if da2_manifest_path.exists():
        try:
            da2_data = json.loads(da2_manifest_path.read_text(encoding="utf-8"))
            for rec in da2_data.get("records", []):
                da2_lookup[rec["hexagram_id"]] = rec
        except Exception:
            pass

    # Load JKD Megatron Wavepacket Emotions JSONL if present
    jkd_jsonl_path = ROOT / "DATASETS" / "jkd_megatron_wavepacket_emotions.jsonl"
    jkd_passages_by_hex = {h: [] for h in range(1, 65)}
    if jkd_jsonl_path.exists():
        try:
            with open(jkd_jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    rec = json.loads(line)
                    res_hex = rec.get("resolved_hexagram", {}).get("hexagram_id")
                    prompt_text = rec.get("prompt", "").strip()
                    if res_hex and 1 <= res_hex <= 64 and prompt_text:
                        if len(jkd_passages_by_hex[res_hex]) < 5:  # Keep top 5 key passages per hexagram
                            jkd_passages_by_hex[res_hex].append({
                                "chunk_id": rec.get("chunk_id"),
                                "text": prompt_text,
                                "emotion": rec.get("emotion_vector", {}),
                                "energy": rec.get("hamiltonian_energy", 0.75)
                            })
        except Exception:
            pass

    # Load Quantum Wave Packet Pre-Warm Manifest if present
    prewarm_manifest_path = ROOT / "DATASETS" / "quantum_prewarm_manifest.json"
    prewarm_data = {}
    if prewarm_manifest_path.exists():
        try:
            prewarm_data = json.loads(prewarm_manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    for row in range(8):
        row_heights = []
        for col in range(8):
            h_id = row * 8 + col + 1
            base = HEXAGRAM_BASE[h_id]
            binary_str = base.get("binary_bottom_to_top", "111111")

            # Position (8x8 world grid, [-280, +280] meters, 70m sector spacing)
            world_x = round((col - 3.5) * 70.0, 2)
            world_z = round((row - 3.5) * 70.0, 2)

            u_idx = base.get("upper_idx", 1)
            l_idx = base.get("lower_idx", 1)

            # Derive 5-Axis Emotional Vector directly from emotional_engine EMOTIONAL_WEIGHTS
            ew = EMOTIONAL_WEIGHTS.get(h_id, {})
            vec5 = {
                "chaos": round(ew.get("chaos", 2000) / 10000.0, 4),
                "whimsy": round(ew.get("whimsy", 1500) / 10000.0, 4),
                "darkTone": round(ew.get("darkTone", 1500) / 10000.0, 4),
                "coherence": round(ew.get("coherence", 5000) / 10000.0, 4),
                "voiceWeight": round(ew.get("voiceWeight", 6000) / 10000.0, 4)
            }

            # Physical vortex field properties derived strictly from the 5-axis emotional vector
            vortex_tension = round(0.20 + 0.55 * vec5["chaos"] + 0.25 * vec5["darkTone"], 4)
            suction_coeff  = round(0.20 + 0.50 * vec5["coherence"] + 0.30 * vec5["voiceWeight"], 4)
            porosity_level = round(0.15 + 0.60 * vec5["whimsy"] * (1.0 - 0.40 * vec5["coherence"]), 4)

            da2_rec = da2_lookup.get(h_id, {})
            depth_stats = da2_rec.get("depth_statistics", {
                "min_depth": 0.0,
                "max_depth": 20.0,
                "mean_depth": 10.0,
                "std_depth": 3.5
            })
            pc_verts = da2_rec.get("pointcloud_vertex_count", 122150)

            elevation = round(
                math.sin(col * 0.8) * math.cos(row * 0.8) * 14.0
                + (u_idx * 2.5) + (l_idx * 1.5), 2
            )
            row_heights.append(elevation)

            biome_id = row
            biome = temporal_biomes[biome_id]

            # Unified Continuous (X, Y, Z) Spatial Acoustic Tensor
            norm_x = world_x / 280.0
            norm_z = world_z / 280.0
            norm_y = elevation / 35.0
            norm_r = math.sqrt(norm_x * norm_x + norm_z * norm_z)
            spatial_theta = math.atan2(world_z, world_x)

            # Unified fundamental spatial carrier frequency from (x, y, z) field operator
            spatial_fundamental_hz = round(
                108.0 * (1.0 + 0.40 * norm_r + 0.25 * norm_y + 0.15 * math.sin(3.0 * spatial_theta + norm_y * math.pi)),
                2
            )
            spatial_cutoff_hz = round(350.0 + porosity_level * 2400.0 + 300.0 * norm_y, 1)
            spatial_q = round(1.2 + vortex_tension * 3.5 + 0.8 * norm_r, 2)
            spatial_phase_rad = round((2.0 * math.pi / 560.0) * (world_x + world_z) + (math.pi * elevation / 35.0), 4)

            # 6-Yao Line Quantum Pellets (L1 to L6) — Unified (X, Y, Z) Spatial Harmonic Resolution
            yao_pellets = []
            for line_idx in range(6):
                bit = int(binary_str[line_idx]) if line_idx < len(binary_str) else 1
                # Changing line (yao / ternary 2) fires on any of the 64 hexagrams:
                # A yang line (bit=1) becomes yao when vortex_tension exceeds the per-line threshold.
                # A yin  line (bit=0) becomes yao when suction_coeff exceeds the per-line threshold.
                yang_yao_thresh = 0.45 + (line_idx * 0.07)   # lines 0-5: 0.45 .. 0.80
                yin_yao_thresh  = 0.60 + (line_idx * 0.05)   # lines 0-5: 0.60 .. 0.85
                if bit == 1 and vortex_tension > yang_yao_thresh:
                    ternary_state = 2
                elif bit == 0 and suction_coeff > yin_yao_thresh:
                    ternary_state = 2
                else:
                    ternary_state = 1 if bit == 1 else 0

                orbit_radius = round(6.0 + line_idx * 2.2, 2)
                orbital_speed = round(0.5 + (line_idx + 1) * 0.25 * (1.0 + vortex_tension) * (1.2 if ternary_state == 2 else 1.0), 3)

                line_ratio = 1.0 + (line_idx / 6.0) * 0.618
                line_phase_mod = 1.0 + 0.12 * math.cos(spatial_theta * (line_idx + 1) + elevation / 10.0)
                ternary_mult = 1.18 if ternary_state == 2 else (1.0 if ternary_state == 1 else 0.82)
                freq_hz = round(spatial_fundamental_hz * line_ratio * ternary_mult * line_phase_mod * (1.0 + vortex_tension * 0.20), 2)

                # Pellet spectral color: derived from hexagram spectral hue + line index offset (384 unique colors)
                # NOT a 3-value ternary collapse. Base hue from hexagram (h_id - 1) * 5.625°, shifted
                # per line by (line_idx * 60°) and per ternary state by (ternary_state * 20°).
                pellet_hue = ((h_id - 1) * 5.625 + line_idx * 60.0 + ternary_state * 20.0) % 360.0
                pr, pg, pb = _hue_to_rgb(pellet_hue)
                pr_i, pg_i, pb_i = int(pr * 255), int(pg * 255), int(pb * 255)
                color_hex = f"#{pr_i:02X}{pg_i:02X}{pb_i:02X}"

                # Waveform: derived from upper + lower trigram index pair, not ternary state alone.
                # 8 trigrams (Heaven=1..Earth=8), upper drives coarse waveform family,
                # lower drives sub-variant. Maps to 8 waveform shapes across the 64.
                trigram_pair_key = (u_idx - 1) % 4  # 0..3 coarse families
                sub_key = (l_idx - 1) % 2            # 0..1 sub-variant
                waveform_table = [
                    ["sine",     "triangle"],   # Heaven/Creative family
                    ["sawtooth", "square"],     # Thunder/Arousing family
                    ["triangle", "sine"],       # Water/Abysmal family
                    ["sawtooth", "triangle"]    # Mountain/Keeping Still family
                ]
                waveform = waveform_table[trigram_pair_key][sub_key]
                line_type = "yao" if ternary_state == 2 else ("yang" if ternary_state == 1 else "yin")

                # Energy uniquely derived per-hexagram per-line from full spatial field (not a 3-value enum)
                energy = round(
                    (0.5 + vortex_tension * 0.6 + suction_coeff * 0.25)
                    * (line_phase_mod * ternary_mult)
                    * (0.85 + (line_idx / 6.0) * 0.30),
                    4
                )

                yao_pellets.append({
                    "line_position": line_idx + 1,
                    "sub_trigram": "lower" if line_idx < 3 else "upper",
                    "sub_position": (line_idx % 3) + 1,
                    "ternary_state": ternary_state,
                    "line_type": line_type,
                    "orbit_radius": orbit_radius,
                    "orbital_speed": orbital_speed,
                    "color_hex": color_hex,
                    "pellet_hue_degrees": round(pellet_hue, 3),
                    "waveform": waveform,
                    "energy_intensity": energy,
                    "frequency_hz": freq_hz
                })

            # Load Deterministic Spectral Color Map & Quantum Wave Packet from Kit
            kit_path = ROOT / "DATASETS" / "kingwen_model_sets" / f"kit_{h_id}.json"
            k_color = {}
            quantum_wp = {}
            if kit_path.exists():
                try:
                    kit_json = json.loads(kit_path.read_text(encoding="utf-8"))
                    k_color = kit_json.get("grounded_npc", {}).get("k_color_map", {})
                    quantum_wp = kit_json.get("quantum_wave_packet", {})
                except Exception:
                    pass
            spectral_color = k_color.get("primary_color", None)
            base_hue = k_color.get("final_hue_degrees", None)
            if not spectral_color or base_hue is None:
                # Directly invoke mathematical derivation from scripts.generate_deterministic_64_color_spectrum
                hue_base = (h_id - 1) * (360.0 / 64.0)
                yang_count = binary_str.count("1")
                sat = max(0.35, min(0.95, (yang_count / 6.0) * 0.40 + 0.50))
                light = max(0.35, min(0.70, vec5["coherence"] * 0.30 + 0.40))
                u_temp = TRIGRAM_TEMP.get(base.get("upper_trigram", "Qian"), 0.0)
                l_temp = TRIGRAM_TEMP.get(base.get("lower_trigram", "Kun"), 0.0)
                trigram_pert = ((u_temp + l_temp) / 2.0) * 2.8125
                base_hue = (hue_base + trigram_pert) % 360.0
                _, _, _, hex_code = hsl_to_rgb_hex(base_hue, sat, light)
                spectral_color = {"hex": hex_code, "name": f"{base['name']} Spectrum"}

            palette_16 = k_color.get("palette_16", [])
            if not palette_16:
                # Generate 16 distinct harmonic palette steps directly using hsl_to_rgb_hex
                palette_16 = []
                for i in range(16):
                    step_hue = (base_hue + (i - 8) * 11.25) % 360.0
                    _, _, _, p_hex = hsl_to_rgb_hex(step_hue, 0.70, 0.50)
                    palette_16.append({"step": i, "hue_deg": round(step_hue, 2), "hex": p_hex})

            sector = {
                "sector_id": h_id,
                "hexagram_id": h_id,
                "name": f"Citadel of {base['name']}",
                "hexagram_name": base["name"],
                "hanzi": base.get("unicode", "\u4dc0"),
                "binary": binary_str,
                "upper_trigram": base.get("upper_trigram", "Heaven"),
                "lower_trigram": base.get("lower_trigram", "Heaven"),
                "grid_coordinates": {"row": row, "col": col},
                "world_position": {"x": world_x, "y": elevation, "z": world_z},
                "sector_bounds": {
                    "min_x": world_x - 35.0, "max_x": world_x + 35.0,
                    "min_z": world_z - 35.0, "max_z": world_z + 35.0
                },
                "regional_biome": biome,
                "citadel_archetype": base.get("category", "sovereign"),
                "action_doctrine": base.get("action", "ASSERT"),
                "spectral_color": spectral_color,
                "palette_16": palette_16,
                "base_hue_degrees": base_hue,
                "emotional_vector_5axis": vec5,
                "quantum_physics": {
                    "vortex_tension": vortex_tension,
                    "suction_coefficient": suction_coeff,
                    "porosity_level": porosity_level,
                    "fundamental_frequency_hz": spatial_fundamental_hz,
                    "spatial_cutoff_hz": spatial_cutoff_hz,
                    "spatial_q_factor": spatial_q,
                    "spatial_phase_rad": spatial_phase_rad,
                    "implosion_funnel_depth": round(vortex_tension * 18.0, 2),
                    "porosity_cloud_radius": round(12.0 + porosity_level * 16.0, 2),
                    "depth_statistics": depth_stats,
                    "depth_pointcloud_vertices": pc_verts
                },
                "quantum_wave_packet": quantum_wp,
                "yao_pellets": yao_pellets,
                "ternary_slot_matrix": _ternary_slot_matrix(h_id),
                "jkd_passages": jkd_passages_by_hex.get(h_id, []),
                "assets": {
                    "3d_mesh": f"DATASETS/kingwen_3d_meshes/shap_e_hex_{h_id:02d}.ply",
                    "openusd_stage": f"DATASETS/openusd_stages/npc_hex_{h_id:02d}.usda",
                    "godot_scene": f"DATASETS/godot_scenes/npc_hex_{h_id:02d}.tscn",
                    "rsmv_model": f"DATASETS/kingwen_rsmv_models/hex_{h_id:02d}_models.json",
                    "quantum_surface_plot": f"DATASETS/quantumlab_plots/quantum_3d_hex_{h_id:02d}.png",
                    "depth_map_16bit": f"DATASETS/depth_maps_16bit/depth_hex_{h_id:02d}_16bit.png",
                    "depth_pointcloud": f"DATASETS/depth_pointclouds/depth_cloud_hex_{h_id:02d}.ply"
                }
            }
            sectors.append(sector)
        heightmap_grid.append(row_heights)

    print("[PRE-WARMING] Building 60 pre-warmed 3D Egg Mesh keyframes & 384-pellet audio WAV buffer...")
    egg_keyframes = prewarm_egg_keyframes(sectors, num_frames=60)
    audio_wav_b64 = prewarm_unison_audio_wav_b64(sectors, duration_sec=4.0)

    # Compute 512 Resolved Phase States and Gaussian Consensus from emotional_engine.py
    _shotgun_result = shotgun_expand(emotional_input=50.0, request_text="")
    resolved_512 = _shotgun_result.get("resolved", [])
    _consensus = _compute_consensus_from_resolved(resolved_512, 50.0)
    consensus_vec = _consensus.get("consensus_vector", [0.2, 0.15, 0.15, 0.5, 0.6])

    # 3. Master World Topology Manifest
    world_topology = {
        "world_name": "King Wen Sovereign Macro-World",
        "version": "3.2.0",
        "spatial_metrics": {
            "world_dimensions_meters": [560.0, 560.0],
            "total_sectors": 64,
            "sector_dimensions_meters": [70.0, 70.0],
            "elevation_range_meters": [-15.0, 35.0]
        },
        "temporal_biomes": temporal_biomes,
        "heightmap_matrix_8x8": heightmap_grid,
        "emotional_engine_consensus": {
            "input_emotional_value": 50.0,
            "resolved_state_count": len(resolved_512),
            "gaussian_consensus_vector_5axis": consensus_vec
        },
        "quantum_prewarm": prewarm_data if prewarm_data else {"status": "unwarmed"},
        "prewarmed_egg_keyframes": egg_keyframes,
        "prewarmed_audio_wav_b64": audio_wav_b64,
        "sectors": sectors
    }

    topo_file = ROOT / "DATASETS/kingwen_sovereign_world_topology.json"
    topo_file.write_text(json.dumps(world_topology, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[1/4] Exported Master World Topology Manifest: {topo_file.name}")

    # 4. Master OpenUSD World Stage (Terrain + 64 Citadels + Vortex Attributes)
    usd_out = ROOT / "DATASETS/openusd_stages/kingwen_sovereign_master_stage.usda"
    usd_citadels = []
    for s in sectors:
        hid = s["hexagram_id"]
        pos = s["world_position"]
        qp = s["quantum_physics"]
        usd_citadels.append(f"""
    def "Citadel_{hid:02d}_{s['hexagram_name'].replace(' ', '_')}" (
        references = @./npc_hex_{hid:02d}.usda@</SovereignNPC_{hid:02d}>
    )
    {{
        double3 xformOp:translate = ({pos['x']}, {pos['y']}, {pos['z']})
        uniform token[] xformOpOrder = ["xformOp:translate"]
        custom string kingwen:biome = "{s['regional_biome']['name']}"
        custom float kingwen:vortex_tension = {qp['vortex_tension']}
        custom float kingwen:porosity = {qp['porosity_level']}
        custom float kingwen:implosion_depth = {qp['implosion_funnel_depth']}
    }}""")

    usd_stage_content = f"""#usda 1.0
(
    defaultPrim = "KingWenSovereignWorld"
    metersPerUnit = 1.0
    upAxis = "Y"
    doc = "Master 64-Sovereign Macro World: 8 Biomes, Schauberger Centripetal Egg Vortices, 6-Yao Pellets, 64 Citadels"
)

def Xform "KingWenSovereignWorld"
(
    kind = "assembly"
)
{{
    def Scope "EnvironmentalLighting"
    {{
        def DomeLight "SkyDome"
        {{
            float inputs:intensity = 1000.0
            color3f inputs:color = (0.85, 0.9, 1.0)
        }}
    }}

    def Scope "MasterCentripetalEggVortex"
    {{
        double3 xformOp:translate = (0, 40.0, 0)
        double3 xformOp:scale = (340.0, 180.0, 340.0)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        custom string kingwen:attractor_mode = "implosion"
        custom bool kingwen:egg_active = true
        custom float kingwen:present_time = 0.0
    }}

    def Scope "SovereignCitadels"
    {{
{''.join(usd_citadels)}
    }}
}}
"""
    usd_out.write_text(usd_stage_content, encoding="utf-8")
    print(f"[2/4] Generated Master OpenUSD Macro-World Stage: {usd_out.name}")

    # 5. Master Godot World Scene
    godot_out = ROOT / "DATASETS/godot_scenes/kingwen_sovereign_world_scene.tscn"
    godot_ext_res = []
    godot_nodes = []
    for s in sectors:
        hid = s["hexagram_id"]
        pos = s["world_position"]
        qp = s["quantum_physics"]
        godot_ext_res.append(
            f'[ext_resource type="PackedScene" uid="uid://hex_{hid:02d}" '
            f'path="res://DATASETS/godot_scenes/npc_hex_{hid:02d}.tscn" id="{hid}"]'
        )
        godot_nodes.append(f"""
[node name="Citadel_{hid:02d}" parent="Citadels" instance=ExtResource("{hid}")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {pos['x']}, {pos['y']}, {pos['z']})
metadata/biome = "{s['regional_biome']['name']}"
metadata/vortex_tension = {qp['vortex_tension']}
metadata/porosity = {qp['porosity_level']}
""")

    godot_content = f"""[gd_scene load_steps=67 format=3]

[sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_1"]
sky_top_color = Color(0.1, 0.2, 0.4, 1)
sky_horizon_color = Color(0.4, 0.5, 0.7, 1)

[sub_resource type="Sky" id="Sky_1"]
sky_material = SubResource("ProceduralSkyMaterial_1")

[sub_resource type="Environment" id="Environment_1"]
background_mode = 2
sky = SubResource("Sky_1")
ambient_light_source = 3
ambient_light_color = Color(0.5, 0.5, 0.6, 1)
tonemap_mode = 2
glow_enabled = true

{chr(10).join(godot_ext_res)}

[node name="KingWenSovereignWorld" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Environment_1")

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866, -0.353, 0.353, 0, 0.707, 0.707, -0.5, -0.612, 0.612, 0, 50, 0)
shadow_enabled = true

[node name="MasterCentripetalEggVortex" type="Node3D" parent="."]
transform = Transform3D(340, 0, 0, 0, 180, 0, 0, 0, 340, 0, 40, 0)
metadata/egg_active = true
metadata/attractor_mode = "implosion"

[node name="Citadels" type="Node3D" parent="."]
{chr(10).join(godot_nodes)}
"""
    godot_out.write_text(godot_content, encoding="utf-8")
    print(f"[3/4] Generated Master Godot 3D World: {godot_out.name}")

    # 6. High-Fidelity Three.js 3D World Viewer
    #    with: Schauberger vortex spirals, 6-yao orbiting pellets,
    #          porosity resonance shells, parametric rose-curve avatar cores,
    #          64 Gaussian potential-well terrain deformation
    viewer_out = ROOT / "DATASETS/kingwen_sovereign_world_viewer.html"

    # Build the JSON string separately to avoid f-string brace issues
    world_json = json.dumps(world_topology)

    viewer_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>King Wen 64-Sovereign Quantum World 3D Viewfinder</title>
  <style>
    body { margin: 0; overflow: hidden; background: #070913; font-family: 'Segoe UI', system-ui, sans-serif; color: #fff; }
    #canvas-container { width: 100vw; height: 100vh; position: absolute; }
    #hud {
      position: absolute; top: 20px; left: 20px; z-index: 10;
      background: rgba(11, 15, 25, 0.88); backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 215, 0, 0.35); border-radius: 14px;
      padding: 20px 24px; max-width: 440px; box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }
    h1 { margin: 0 0 8px 0; font-size: 20px; color: #FFD700; display: flex; align-items: center; gap: 8px; letter-spacing: 0.5px; }
    .badge { background: #1e293b; border: 1px solid #3b82f6; color: #60a5fa; font-size: 11px; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
    .stat-row { display: flex; justify-content: space-between; margin: 6px 0; font-size: 13px; color: #94a3b8; }
    .stat-val { color: #e2e8f0; font-weight: 600; font-family: monospace; }
    #inspector { margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.12); }
    .inspect-name { font-size: 17px; color: #38bdf8; font-weight: 700; margin-bottom: 6px; }
    .inspect-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; color: #cbd5e1; }
    .inspect-cell { background: rgba(30, 41, 59, 0.6); padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); }
    .inspect-label { color: #94a3b8; font-size: 10px; text-transform: uppercase; }
    .pellet-row { display: flex; gap: 4px; margin-top: 8px; }
    .pellet-dot { width: 14px; height: 14px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.4); }
    #instructions {
      position: absolute; bottom: 20px; left: 20px; z-index: 10;
      background: rgba(11, 15, 25, 0.75); padding: 10px 18px; border-radius: 8px; font-size: 12px; color: #94a3b8; border: 1px solid rgba(255,255,255,0.1);
    }
    .legend { display: flex; gap: 12px; margin-top: 10px; font-size: 11px; flex-wrap: wrap; }
    .leg-item { display: flex; align-items: center; gap: 5px; }
    .dot-gold { width: 8px; height: 8px; border-radius: 50%; background: #FFD700; box-shadow: 0 0 6px #FFD700; }
    .dot-blue { width: 8px; height: 8px; border-radius: 50%; background: #38BDF8; box-shadow: 0 0 6px #38BDF8; }
    .dot-purple { width: 8px; height: 8px; border-radius: 50%; background: #A855F7; box-shadow: 0 0 6px #A855F7; }
    .dot-white { width: 8px; height: 8px; border-radius: 50%; background: #fff; border: 1px solid #888; }
    .audio-bar { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 10px; }
    .audio-btn {
      background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 5px 10px;
      border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; transition: all 0.2s ease;
    }
    .audio-btn:hover { background: #38bdf8; color: #0f172a; }
    .audio-select {
      background: #0f172a; color: #f8fafc; border: 1px solid #3b82f6; padding: 4px 8px;
      border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; outline: none;
    }
    .audio-bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 12px; }
    .unified-field-btn {
      background: linear-gradient(135deg, #0284c7 0%, #7c3aed 100%); color: #ffffff; border: 1px solid #38bdf8;
      padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: 800;
      letter-spacing: 0.5px; box-shadow: 0 0 16px rgba(56,189,248,0.4); transition: all 0.2s ease; width: 100%; text-align: center;
    }
    .unified-field-btn:hover { transform: translateY(-1px); box-shadow: 0 0 24px rgba(168,85,247,0.7); }
    .unified-field-btn.active {
      background: linear-gradient(135deg, #059669 0%, #0284c7 100%); border-color: #34d399;
      box-shadow: 0 0 24px rgba(52,211,153,0.8); color: #fff;
    }
    .audio-select {
      background: #0f172a; color: #f8fafc; border: 1px solid #3b82f6; padding: 6px 10px;
      border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; outline: none; flex: 1;
    }
    .rec-btn {
      background: #1e293b; color: #f59e0b; border: 1px solid #f59e0b; padding: 6px 12px;
      border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; transition: all 0.2s ease;
    }
    .rec-btn:hover { background: #f59e0b; color: #0f172a; }

    /* === CENTRIPETAL EGG VORTEX SWITCHBOARD === */
    .egg-switchboard {
      background: rgba(15, 23, 42, 0.92); border: 1px solid #8b5cf6;
      border-radius: 10px; padding: 10px; margin-top: 10px;
      box-shadow: 0 0 20px rgba(139, 92, 246, 0.35); backdrop-filter: blur(8px);
    }
    .egg-header {
      font-size: 11px; font-weight: 800; color: #c4b5fd; text-transform: uppercase;
      letter-spacing: 0.8px; display: flex; align-items: center; justify-content: space-between;
    }
    .egg-btn-row { display: flex; gap: 6px; width: 100%; margin-top: 6px; }
    .egg-toggle-btn {
      background: #1e1b4b; color: #a78bfa; border: 1px solid #8b5cf6;
      padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 11px;
      font-weight: 700; transition: all 0.2s ease; flex: 1; text-align: center;
    }
    .egg-toggle-btn:hover { background: #8b5cf6; color: #ffffff; box-shadow: 0 0 16px rgba(139,92,246,0.6); }
    .egg-toggle-btn.active {
      background: linear-gradient(135deg, #7c3aed 0%, #d946ef 100%);
      color: #ffffff; border-color: #f472b6; box-shadow: 0 0 20px rgba(217,70,239,0.8);
    @keyframes pulseGlow {
      0% { box-shadow: 0 0 10px rgba(168, 85, 247, 0.6); transform: translateX(-50%) scale(1.0); }
      50% { box-shadow: 0 0 26px rgba(236, 72, 153, 0.9); transform: translateX(-50%) scale(1.03); }
      100% { box-shadow: 0 0 10px rgba(168, 85, 247, 0.6); transform: translateX(-50%) scale(1.0); }
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
  <div id="prewarm-loader-overlay" style="position:fixed; inset:0; z-index:10000; background:radial-gradient(circle at center, #0f172a 0%, #020617 100%); display:flex; flex-direction:column; align-items:center; justify-content:center; font-family:sans-serif; color:#f8fafc; transition:opacity 0.6s ease;">
    <div style="font-size:28px; font-weight:900; letter-spacing:2px; color:#f59e0b; text-shadow:0 0 20px rgba(245,158,11,0.6); margin-bottom:6px; text-align:center;">
      &#x26A1; KING WEN 64 SOVEREIGN ENGINE
    </div>
    <div style="font-size:12px; font-weight:700; color:#a78bfa; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:20px; text-align:center;">
      Edge Pre-Warm Cache &amp; Phased Layer Pipeline
    </div>
    <div style="width:340px; height:10px; background:#1e293b; border-radius:5px; overflow:hidden; border:1px solid #475569; box-shadow:0 0 15px rgba(124,58,237,0.4); margin-bottom:12px;">
      <div id="prewarm-progress-bar" style="width:5%; height:100%; background:linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); border-radius:5px; transition:width 0.3s ease-out; box-shadow:0 0 10px #8b5cf6;"></div>
    </div>
    <div id="prewarm-layer-status" style="font-size:12px; font-family:monospace; color:#38bdf8; font-weight:600; text-align:center; min-height:18px;">
      [LAYER 0/3] Connecting to Cloudflare Edge Pre-Warm Cache...
    </div>
    <div id="prewarm-stats" style="font-size:10px; font-family:monospace; color:#64748b; margin-top:8px;">
      64 Citadels &bull; 384 Sound Pellets &bull; 5,832 Quantum States
    </div>
  </div>
  <div id="audio-unlock-overlay" onclick="unlockAudioSystem()" style="position:fixed; top:16px; left:50%; transform:translateX(-50%); z-index:9999; background:rgba(124, 58, 237, 0.95); color:#ffffff; font-weight:800; font-size:13px; padding:12px 28px; border-radius:30px; border:2px solid #c4b5fd; box-shadow:0 0 25px rgba(168, 85, 247, 0.95); cursor:pointer; font-family:sans-serif; letter-spacing:0.5px; animation: pulseGlow 1.8s infinite;">
    &#x1F50A; CLICK ANYWHERE ON SCREEN TO ACTIVATE UNIFIED 384-PELLET QUANTUM AUDIO FIELD
  </div>
  <div id="canvas-container"></div>
  <div id="hud">
    <h1>&#x1F451; King Wen Quantum World <span class="badge">64 Sovereign Nodes</span></h1>
    <div class="stat-row"><span>World Grid:</span><span class="stat-val">560m &times; 560m (8&times;8 Sectors)</span></div>
    <div class="stat-row"><span>Dual Coordinates:</span><span class="stat-val">512 Binary &times; 729 Ternary</span></div>
    <div class="stat-row"><span>Wave Packets:</span><span class="stat-val">1D&rarr;2D&rarr;3D Pre-Warmed (5,832 States)</span></div>
    <div class="stat-row"><span>Depth Engine:</span><span class="stat-val">Depth Anything V2 (16-bit)</span></div>
    <div class="stat-row"><span>Vortex Physics:</span><span class="stat-val">Schauberger Centripetal Implosion</span></div>
    <div class="legend">
      <div class="leg-item"><div class="dot-gold"></div> Yang (1)</div>
      <div class="leg-item"><div class="dot-blue"></div> Yin (0)</div>
      <div class="leg-item"><div class="dot-purple"></div> Yao/Changing (2)</div>
      <div class="leg-item"><div class="dot-white"></div> Rose Core</div>
    </div>
    <div class="audio-bar">
      <button class="unified-field-btn" id="unified-field-btn" onclick="toggleUnifiedField()">&#x26A1; ACTIVATE UNIFIED QUANTUM GROUND FIELD (1..64)</button>
      <div style="display: flex; gap: 6px; width: 100%; margin-top: 4px;">
        <select id="audio-mode-select" class="audio-select" onchange="changeAudioMode()">
          <option value="field">&#x1F30C; Continuous Ground Superposition (1..64)</option>
          <option value="hover">&#x1F3AF; Focused Node Spatial Isolation</option>
          <option value="binaural">&#x262F;&#xFE0F; Yin/Yang Binaural Carrier</option>
        </select>
        <button class="rec-btn" id="record-btn" onclick="recordAudioSample()">&#x1F399;&#xFE0F; Sample WAV</button>
      </div>
    </div>
    <div class="egg-switchboard">
      <div class="egg-header">
        <span>&#x1F95A; CENTRIPETAL EGG VORTEX ATTRACTOR</span>
        <span style="font-size:9px; background:#7c3aed; color:#fff; padding:1px 6px; border-radius:4px;">ALL 64 UNISON</span>
      </div>
      <div class="egg-btn-row">
        <button class="egg-toggle-btn active" id="egg-toggle-btn" onclick="toggleCentripetalEgg()">&#x1F95A; EGG VORTEX: ACTIVE (1..64 UNISON)</button>
        <select id="attractor-mode-select" class="audio-select" onchange="changeAttractorMode()">
          <option value="implosion">&#x1F300; Schauberger Implosion Egg</option>
          <option value="toroidal">&#x1F369; Toroidal Egg Oscillation</option>
          <option value="unison_resonance">&#x1F50A; 64-Unison Pellet Resonance</option>
        </select>
      <div class="egg-btn-row" style="margin-top: 6px;">
        <button class="rec-btn" id="jkd-unison-btn" onclick="toggleJKDUnison()" style="background:#0284c7; border-color:#38bdf8; color:#fff; font-weight:800; width:100%;">📖 READ JKD TAO CORPUS IN UNISON (ALL 64)</button>
      </div>
      <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-size: 10px; color: #cbd5e1;">
        <span style="font-weight:700; color:#c4b5fd;">Present Time Speed (t):</span>
        <input type="range" id="time-speed-slider" min="0.1" max="5.0" step="0.1" value="1.0" oninput="updateTimeSpeed(this.value)" style="flex:1; cursor:pointer;">
        <span id="time-speed-val" style="font-family:monospace; color:#38bdf8; font-weight:700;">1.0x</span>
      </div>
    </div>
    <div id="inspector">
      <div class="inspect-name" id="sel-name">Hover over any Sovereign Node to observe local interference</div>
      <div class="inspect-grid" id="sel-grid">
        <div class="inspect-cell"><div class="inspect-label">Regional Biome</div><span id="val-biome">All 8 Sectors Active</span></div>
        <div class="inspect-cell"><div class="inspect-label">Action &amp; Archetype</div><span id="val-action">Superposition Field</span></div>
        <div class="inspect-cell" style="grid-column: span 2;"><div class="inspect-label">DA-V2 Metric Depth &amp; Point Cloud</div><span id="val-depth">Mean: 10.0m | 122,150 vertices</span></div>
        <div class="inspect-cell" style="grid-column: span 2;"><div class="inspect-label">Deterministic Spectral Hue (6-Bit Embodiment)</div><span id="val-spectral" style="display:flex;align-items:center;gap:6px;"><span id="spectral-badge" style="width:12px;height:12px;border-radius:3px;background:#FFD700;display:inline-block;box-shadow:0 0 6px rgba(255,215,0,0.6);"></span> <span id="spectral-text">#FFD700 (0.0&deg;)</span></span></div>
        <div class="inspect-cell" style="grid-column: span 2;"><div class="inspect-label">6-Yao Acoustic Harmonics &amp; Filter</div><span id="val-audio">Field Active: Approaching nodes modulates local acoustic interference</span></div>
        <div class="inspect-cell" style="grid-column: span 2; background: rgba(13, 148, 136, 0.15); border: 1px solid #14b8a6;">
          <div class="inspect-label" style="color: #2dd4bf;">📖 JKD Tao Unison Corpus Recitation</div>
          <span id="val-jkd-text" style="font-style: italic; color: #5eead4; font-size: 11px;">"Take what is useful, discard what is useless, add what is specifically your own." — JKD Tao Unison Corpus Field Active</span>
        </div>
      </div>
    </div>
  </div>
  <div id="instructions">&#x1F5B1;&#xFE0F; Left Click + Drag: Orbit | Scroll: Zoom | Hover: Live Node Telemetry &amp; Acoustic Harmonics</div>

  <script>
    // === MASTER DATA STATE & LAYERED PRE-WARM REPOSITORY ===
    const worldData = {
      sectors: [],
      egg_keyframes: [],
      prewarmed_egg_keyframes: [],
      audio_unison_wav_b64: "",
      jkd_passages_by_hex: {}
    };

    const embeddedTopology = __WORLD_JSON_PLACEHOLDER__;

    // === WEB AUDIO API UNIFIED QUANTUM GROUND FIELD ENGINE ===
    let audioCtx = null;
    let fieldActive = true;
    let groundVoices = [];
    let focusOscillators = [];
    let focusGains = [];
    let masterFilter = null;
    let masterGain = null;
    let activeHexData = null;
    let currentAudioMode = 'field';
    let audioUnlocked = false;

    function unlockAudioSystem() {
      if (audioUnlocked) {
        // Already unlocked — just resume if browser suspended it again
        if (audioCtx && audioCtx.state === 'suspended') {
          audioCtx.resume();
        }
        return;
      }
      if (!audioCtx) {
        initAudio();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume().then(() => {
          console.log('[AUDIO] AudioContext resumed successfully!');
        });
      }
      fieldActive = true;
      audioUnlocked = true;
      if (masterGain && audioCtx) {
        masterGain.gain.setTargetAtTime(0.55, audioCtx.currentTime, 0.05);
      }
      const overlay = document.getElementById('audio-unlock-overlay');
      if (overlay) overlay.style.display = 'none';
      const btn = document.getElementById('unified-field-btn');
      if (btn) {
        btn.innerText = '🌌 UNIFIED QUANTUM GROUND FIELD: ACTIVE (1..64)';
        btn.classList.add('active');
      }
    }

    window.addEventListener('click', unlockAudioSystem, { once: true });
    window.addEventListener('touchstart', unlockAudioSystem, { once: true });
    window.addEventListener('keydown', unlockAudioSystem, { once: true });

    function initAudio() {
      if (audioCtx) return;
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();

      masterGain = audioCtx.createGain();
      masterGain.gain.setValueAtTime(0.55, audioCtx.currentTime);

      masterFilter = audioCtx.createBiquadFilter();
      masterFilter.type = 'lowpass';
      masterFilter.frequency.setValueAtTime(2400, audioCtx.currentTime);
      masterFilter.Q.setValueAtTime(2.5, audioCtx.currentTime);

      masterGain.connect(masterFilter);
      masterFilter.connect(audioCtx.destination);

      // 1. Focused node 6-yao harmonic oscillators
      for (let i = 0; i < 6; i++) {
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = (i % 2 === 0) ? 'triangle' : 'sine';
        osc.frequency.setValueAtTime(146.0 * (1.0 + i * 0.15), audioCtx.currentTime);
        g.gain.setValueAtTime(0.0, audioCtx.currentTime);
        osc.connect(g);
        g.connect(masterGain);
        osc.start();
        focusOscillators.push(osc);
        focusGains.push(g);
      }

      // 2. The Unified Quantum Ground Field: All 64 Hexagrams & 384 Sound Pellets (1..64)
      if (worldData.sectors) {
        worldData.sectors.forEach((sec) => {
          const pos = sec.world_position;
          const normX = pos.x / 280.0, normZ = pos.z / 280.0, normY = pos.y / 35.0;
          const normR = Math.sqrt(normX * normX + normZ * normZ);
          const theta = Math.atan2(pos.z, pos.x);
          const fundamentalFreq = 108.0 * (1.0 + 0.40 * normR + 0.25 * normY + 0.15 * Math.sin(3.0 * theta + normY * Math.PI));

          const sFilter = audioCtx.createBiquadFilter();
          sFilter.type = 'lowpass';
          const qp = sec.quantum_physics || {};
          const cutoff = 350 + (qp.porosity_level || 0.45) * 2400 + 300 * normY;
          const qRes = 1.2 + (qp.vortex_tension || 0.5) * 3.5 + 0.8 * normR;
          sFilter.frequency.setValueAtTime(cutoff, audioCtx.currentTime);
          sFilter.Q.setValueAtTime(qRes, audioCtx.currentTime);

          const sGain = audioCtx.createGain();
          const baseGain = Math.min(0.035, 0.012 + (qp.vortex_tension || 0.5) * 0.018);
          sGain.gain.setValueAtTime(baseGain, audioCtx.currentTime);

          sFilter.connect(sGain);
          sGain.connect(masterGain);

          // Instantiate 6-Yao Line Sound Pellet Oscillators (384 Total Oscillators Across World)
          const pelletOscillators = [];
          const pelletGains = [];
          const pellets = sec.yao_pellets || [];

          pellets.forEach((yp) => {
            const pOsc = audioCtx.createOscillator();
            const pGain = audioCtx.createGain();

            pOsc.type = yp.waveform || (yp.ternary_state === 2 ? 'sawtooth' : (yp.ternary_state === 1 ? 'triangle' : 'sine'));
            pOsc.frequency.setValueAtTime(yp.frequency_hz || fundamentalFreq, audioCtx.currentTime);

            pGain.gain.setValueAtTime(yp.energy_intensity ? yp.energy_intensity * 0.12 : 0.08, audioCtx.currentTime);

            pOsc.connect(pGain);
            pGain.connect(sFilter);
            pOsc.start();

            pelletOscillators.push(pOsc);
            pelletGains.push(pGain);
          });

          groundVoices.push({
            hexId: sec.hexagram_id,
            sector: sec,
            pos3D: new THREE.Vector3(pos.x, pos.y, pos.z),
            filter: sFilter,
            gain: sGain,
            pelletOscillators: pelletOscillators,
            pelletGains: pelletGains,
            fundamentalFreq: fundamentalFreq
          });
        });
      }
    }

    function toggleUnifiedField() {
      initAudio();
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      fieldActive = !fieldActive;
      const btn = document.getElementById('unified-field-btn');
      if (fieldActive) {
        btn.innerText = '🌌 UNIFIED QUANTUM GROUND FIELD: ACTIVE (ALL 64 IN UNISON)';
        btn.classList.add('active');
        masterGain.gain.setTargetAtTime(0.55, audioCtx.currentTime, 0.05);
        // Activate base gain across ALL 64 ground voices simultaneously — no 1-hex singling out
        const now = audioCtx.currentTime;
        groundVoices.forEach(gv => {
          const qp = gv.sector ? (gv.sector.quantum_physics || {}) : {};
          const vGain = Math.min(0.035, 0.012 + (qp.vortex_tension || 0.5) * 0.018);
          gv.gain.gain.setTargetAtTime(vGain, now, 0.10);
        });
      } else {
        btn.innerText = '⚡ ACTIVATE UNIFIED QUANTUM GROUND FIELD (ALL 64 IN UNISON)';
        btn.classList.remove('active');
        masterGain.gain.setTargetAtTime(0.0, audioCtx.currentTime, 0.05);
      }
    }


    let centripetalEggActive = true;
    let attractorMode = 'implosion';
    let timeSpeed = 1.0;
    let presentTime = 0.0;

    function toggleCentripetalEgg() {
      centripetalEggActive = !centripetalEggActive;
      const btn = document.getElementById('egg-toggle-btn');
      if (centripetalEggActive) {
        btn.innerText = '🥚 EGG VORTEX: ACTIVE (1..64 UNISON)';
        btn.classList.add('active');
      } else {
        btn.innerText = '⚡ EGG VORTEX: OFF';
        btn.classList.remove('active');
      }
    }

    function changeAttractorMode() {
      attractorMode = document.getElementById('attractor-mode-select').value;
    }

    function updateTimeSpeed(val) {
      timeSpeed = parseFloat(val);
      document.getElementById('time-speed-val').innerText = timeSpeed.toFixed(1) + 'x';
    }

    let jkdUnisonActive = false;
    let jkdReciteIndex = 0;

    function toggleJKDUnison() {
      jkdUnisonActive = !jkdUnisonActive;
      const btn = document.getElementById('jkd-unison-btn');
      if (jkdUnisonActive) {
        btn.innerText = '📖 JKD UNISON RECITING (ALL 64)...';
        btn.style.background = '#059669';
        btn.style.borderColor = '#34d399';
        if (!centripetalEggActive) toggleCentripetalEgg();
        if (!fieldActive) toggleUnifiedField();
        reciteNextJKDPassage();
      } else {
        btn.innerText = '📖 READ JKD TAO CORPUS IN UNISON (ALL 64)';
        btn.style.background = '#0284c7';
        btn.style.borderColor = '#38bdf8';
        // Silence all ground voices when stopped
        if (audioCtx && groundVoices.length > 0) {
          const now = audioCtx.currentTime;
          groundVoices.forEach(gv => gv.gain.gain.setTargetAtTime(0.0, now, 0.15));
        }
      }
    }

    function reciteNextJKDPassage() {
      if (!jkdUnisonActive) return;
      if (!audioCtx || groundVoices.length === 0) {
        jkdReciteIndex++;
        if (jkdUnisonActive) setTimeout(reciteNextJKDPassage, 1800);
        return;
      }

      const now = audioCtx.currentTime;
      const cycle = jkdReciteIndex;
      let activeTextSamples = [];

      // === CONSTANT GENERATION OF ALL 64 CITADELS IN PARALLEL UNISON AS INDIVIDUALS ===
      worldData.sectors.forEach((sec, sIdx) => {
        const passages = sec.jkd_passages || [];
        if (passages.length === 0) return;

        // Each citadel derives its own individual passage continuously
        const passageIdx = (cycle + sIdx) % passages.length;
        const passage = passages[passageIdx];
        if (!passage) return;

        const text = passage.text || '"Formlessness — be like water."';
        const hamiltonian = passage.energy || 0.75;
        const emotion = passage.emotion || {};

        if (sIdx % 8 === (cycle % 8)) {
          activeTextSamples.push(`Hex #${sec.hexagram_id} (${sec.hexagram_name}): "${text.slice(0, 45)}..."`);
        }

        // Modulate this individual citadel's 6 yao line pellet oscillators & ground voice
        const gv = groundVoices.find(v => v.hexId === sec.hexagram_id);
        if (gv && gv.pelletOscillators) {
          const coherence   = emotion.coherence   || 0.8;
          const chaos       = emotion.chaos       || 0.2;
          const voiceWeight = emotion.voiceWeight || 0.9;
          const darkTone    = emotion.darkTone    || 0.2;

          // Modulate all 6 pellets for this individual citadel
          gv.pelletOscillators.forEach((pOsc, pIdx) => {
            const pellet = sec.yao_pellets && sec.yao_pellets[pIdx];
            if (!pellet) return;

            // Individual JKD emotion vector modulates pellet frequency & harmonic state
            const jkdFreq = pellet.frequency_hz
              * (1.0 + chaos * 0.18 - darkTone * 0.08)
              * (1.0 + 0.12 * Math.sin(pIdx * 1.27 + hamiltonian * Math.PI + cycle * 0.2));
            pOsc.frequency.setTargetAtTime(jkdFreq, now, 0.08);

            // Smooth 0.35s gain envelope for audible per-word acoustic resonance
            const jkdGain = hamiltonian * voiceWeight * (pellet.energy_intensity || 0.5) * 0.14;
            gv.pelletGains[pIdx].gain.setTargetAtTime(jkdGain, now, 0.35);
          });

          // Modulate citadel master ground gain in unison with smooth acoustic sustain
          const targetGain = Math.min(0.065, (hamiltonian * 0.045) * (1.0 + (sec.quantum_physics.vortex_tension || 0.5) * 0.5));
          gv.gain.gain.setTargetAtTime(targetGain, now, 0.35);
        }

        // Modulate 3D node visual wavepacket pulse for this individual citadel
        const node = animatedNodes[sIdx];
        if (node && node.superpositionCore) {
          const visPulse = 1.0 + 0.50 * hamiltonian * Math.sin(presentTime * 4.0 + sIdx * 0.1);
          node.superpositionCore.scale.set(visPulse, visPulse, visPulse);
        }
      });

      // Update UI Ticker with live multi-node JKD Tao Unison Stream
      if (activeTextSamples.length > 0) {
        document.getElementById('val-jkd-text').innerHTML =
          `<strong style="color:#5eead4;">📖 [ALL 64 UNISON GENERATION ACTIVE]:</strong> ` + activeTextSamples.join(' &bull; ');
      }

      jkdReciteIndex++;

      // At 1.0 Present Time Speed, hold audible per-word output for ~5.2s (scales inversely with timeSpeed)
      const holdDurationMs = Math.max(1200, Math.round(5200 / timeSpeed));

      if (jkdUnisonActive) {
        setTimeout(reciteNextJKDPassage, holdDurationMs);
      }
    }

    function changeAudioMode() {
      currentAudioMode = document.getElementById('audio-mode-select').value;
      if (activeHexData) playHexHarmonics(activeHexData);
    }



    function playHexHarmonics(d) {
      activeHexData = d;
      if (!fieldActive || !audioCtx) return;
      const now = audioCtx.currentTime;

      // When hovering a node, modulate the 6 focus oscillators to show local interference
      // The ground field keeps running — this is observation, not collapse
      const qp = d.quantum_physics || {};
      const porosity = qp.porosity_level || 0.45;
      const vortex = qp.vortex_tension || 0.5;

      if (currentAudioMode === 'hover') {
        // Bring focus oscillators forward to hear local pellet harmonics
        d.yao_pellets.forEach((yp, idx) => {
          if (focusOscillators[idx]) {
            focusOscillators[idx].frequency.setTargetAtTime(yp.frequency_hz || 146.0, now, 0.05);
            focusOscillators[idx].type = yp.ternary_state === 2 ? 'sawtooth' : (yp.ternary_state === 1 ? 'triangle' : 'sine');
            focusGains[idx].gain.setTargetAtTime(yp.ternary_state === 2 ? 0.12 : 0.08, now, 0.04);
          }
        });
      } else {
        // In field/binaural mode, focus oscillators stay silent — ground field speaks
        focusGains.forEach(g => g.gain.setTargetAtTime(0.0, now, 0.03));
      }
    }

    function recordAudioSample() {
      if (!worldData.sectors || worldData.sectors.length === 0) {
        alert('No world data loaded.');
        return;
      }
      // Record the ENTIRE unified ground field — all 64 voices as one continuous medium
      const sampleRate = 44100;
      const durationSec = 5.0;
      const numSamples = Math.floor(sampleRate * durationSec);
      const offlineCtx = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(2, numSamples, sampleRate);

      const offMaster = offlineCtx.createGain();
      offMaster.gain.setValueAtTime(0.30, 0);

      const offFilter = offlineCtx.createBiquadFilter();
      offFilter.type = 'lowpass';
      offFilter.frequency.setValueAtTime(1600, 0);
      offFilter.Q.setValueAtTime(3.0, 0);

      offMaster.connect(offFilter);
      offFilter.connect(offlineCtx.destination);

      // All 64 citadels × 6 yao pellets = 384 oscillators baked into the WAV
      worldData.sectors.forEach((sec) => {
        const pellets = sec.yao_pellets || [];
        pellets.forEach((yp) => {
          const osc = offlineCtx.createOscillator();
          const g = offlineCtx.createGain();
          osc.type = yp.waveform || (yp.ternary_state === 2 ? 'sawtooth' : (yp.ternary_state === 1 ? 'triangle' : 'sine'));
          osc.frequency.setValueAtTime(yp.frequency_hz || 146.0, 0);
          g.gain.setValueAtTime((yp.energy_intensity || 0.5) * 0.018, 0);
          osc.connect(g);
          g.connect(offMaster);
          osc.start(0);
          osc.stop(durationSec);
        });
      });

      offlineCtx.startRendering().then(renderedBuffer => {
        const wavBlob = audioBufferToWavBlob(renderedBuffer);
        const url = URL.createObjectURL(wavBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'kingwen_unified_ground_field_64_voices.wav';
        a.click();
        URL.revokeObjectURL(url);
      });
    }

    function audioBufferToWavBlob(buffer) {
      const numChannels = buffer.numberOfChannels;
      const sampleRate = buffer.sampleRate;
      const format = 1;
      const bitDepth = 16;
      let result;
      if (numChannels === 2) {
        result = interleave(buffer.getChannelData(0), buffer.getChannelData(1));
      } else {
        result = buffer.getChannelData(0);
      }
      const dataLength = result.length * (bitDepth / 8);
      const headerBuffer = new ArrayBuffer(44 + dataLength);
      const view = new DataView(headerBuffer);
      function writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i));
      }
      function interleave(inputL, inputR) {
        const length = inputL.length + inputR.length;
        const result = new Float32Array(length);
        let index = 0, inputIndex = 0;
        while (index < length) { result[index++] = inputL[inputIndex]; result[index++] = inputR[inputIndex]; inputIndex++; }
        return result;
      }
      writeString(view, 0, 'RIFF');
      view.setUint32(4, 36 + dataLength, true);
      writeString(view, 8, 'WAVE');
      writeString(view, 12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, format, true);
      view.setUint16(22, numChannels, true);
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true);
      view.setUint16(32, numChannels * (bitDepth / 8), true);
      view.setUint16(34, bitDepth, true);
      writeString(view, 36, 'data');
      view.setUint32(40, dataLength, true);
      let offset = 44;
      for (let i = 0; i < result.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, result[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      }
      return new Blob([headerBuffer], { type: 'audio/wav' });
    }

    // === RENDERER SETUP ===
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070913);
    scene.fog = new THREE.FogExp2(0x070913, 0.0012);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 3500);
    camera.position.set(0, 260, 420);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2.05;

    // === LIGHTING ===
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const sun = new THREE.DirectionalLight(0xfffaed, 1.4);
    sun.position.set(200, 400, 200);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    scene.add(sun);

    // === 1. QUANTUM POTENTIAL-WELL TERRAIN & GRID ===
    const terrainGeo = new THREE.PlaneGeometry(640, 640, 96, 96);
    terrainGeo.rotateX(-Math.PI / 2);
    terrainGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(terrainGeo.attributes.position.count * 3), 3));
    const terrainMesh = new THREE.Mesh(terrainGeo, new THREE.MeshStandardMaterial({
      vertexColors: true, roughness: 0.70, metalness: 0.30
    }));
    terrainMesh.receiveShadow = true;
    scene.add(terrainMesh);

    const grid = new THREE.GridHelper(560, 8, 0xffd700, 0x334155);
    grid.position.y = 0.6;
    scene.add(grid);

    // Global registries populated layer by layer
    const nodeGroup = new THREE.Group();
    scene.add(nodeGroup);
    const animatedNodes = [];
    const raycastTargets = [];
    const attractorBeams = [];
    const eggCenter = new THREE.Vector3(0, 40, 0);
    let masterEggMesh = null;
    let eggGeo = null;
    let terrainBasePos = null;
    let terrainBaseColors = null;
    let sectorShotgunParams = [];

    // === LAYER 0: SKELETON (64 CITADELS & SPATIAL BIOMES) ===
    function applyLayer0(l0) {
      worldData.sectors = (l0.sectors || []).map(s => ({ ...s }));

      // Deform terrain with 64 Gaussian potential wells
      const tPos = terrainGeo.attributes.position;
      terrainGeo.attributes.position.usage = THREE.DynamicDrawUsage;
      for (let i = 0; i < tPos.count; i++) {
        const x = tPos.getX(i), z = tPos.getZ(i);
        let y = Math.sin(x * 0.012) * Math.cos(z * 0.012) * 16.0 + Math.sin(x * 0.035) * 4.0;
        worldData.sectors.forEach(sec => {
          const dx = x - sec.world_position.x, dz = z - sec.world_position.z;
          const distSq = dx * dx + dz * dz;
          if (distSq < 2500) {
            y += Math.exp(-distSq / 400.0) * (sec.world_position.y - y) * 0.7;
          }
        });
        tPos.setY(i, y);
      }
      terrainGeo.computeVertexNormals();
      tPos.needsUpdate = true;

      // Cache REST position for dynamic centripetal wave attractor
      terrainBasePos = new Float32Array(tPos.array.length);
      terrainBasePos.set(tPos.array);

      // Compute Hexagrams Spectral Color Map across ground vertices
      const tCol = terrainGeo.attributes.color;
      terrainBaseColors = new Float32Array(tPos.count * 3);
      for (let i = 0; i < tPos.count; i++) {
        const x = tPos.getX(i), z = tPos.getZ(i);
        let rSum = 0.08, gSum = 0.09, bSum = 0.16, wSum = 1.0;

        worldData.sectors.forEach(sec => {
          const dx = x - sec.world_position.x, dz = z - sec.world_position.z;
          const distSq = dx * dx + dz * dz;
          if (distSq < 14400) {
            const w = Math.exp(-distSq / 3200.0);
            const sc = sec.spectral_color || { r: 255, g: 215, b: 0 };
            const hexR = (sc.r !== undefined ? sc.r : 255) / 255.0;
            const hexG = (sc.g !== undefined ? sc.g : 215) / 255.0;
            const hexB = (sc.b !== undefined ? sc.b : 0) / 255.0;
            rSum += hexR * w * 1.8;
            gSum += hexG * w * 1.8;
            bSum += hexB * w * 1.8;
            wSum += w * 1.8;
          }
        });
        const finalR = Math.min(1.0, rSum / wSum);
        const finalG = Math.min(1.0, gSum / wSum);
        const finalB = Math.min(1.0, bSum / wSum);
        terrainBaseColors[i * 3]     = finalR;
        terrainBaseColors[i * 3 + 1] = finalG;
        terrainBaseColors[i * 3 + 2] = finalB;
        tCol.setXYZ(i, finalR, finalG, finalB);
      }
      tCol.needsUpdate = true;

      // Spawn 64 Sovereign Beacon Skeletons
      worldData.sectors.forEach((sec, sIdx) => {
        const group = new THREE.Group();
        group.position.set(sec.world_position.x, sec.world_position.y, sec.world_position.z);

        const specColor = new THREE.Color(sec.spectral_color ? sec.spectral_color.hex : '#FFD700');
        const beacon = new THREE.Mesh(
          new THREE.OctahedronGeometry(2.5),
          new THREE.MeshStandardMaterial({
            color: specColor, emissive: specColor, emissiveIntensity: 0.6, roughness: 0.2
          })
        );
        beacon.position.y = 8;
        beacon.userData = sec;
        group.add(beacon);
        raycastTargets.push(beacon);

        nodeGroup.add(group);
        animatedNodes.push({
          group, beacon, pellets: [], vortexTension: 0.5,
          vortex: null, porosity: null, rose: null
        });
      });
    }

    // === LAYER 1: QUANTUM PHYSICS (VORTICES, POROSITY & ROSES) ===
    function applyLayer1(l1) {
      (l1.sectors || []).forEach((ls, idx) => {
        const sec = worldData.sectors[idx];
        if (!sec) return;
        sec.quantum_physics = ls.quantum_physics || {};
        sec.quantum_wave_packet = ls.quantum_wave_packet || {};
        sec.action_doctrine = ls.action_doctrine || "ASSERT";
        sec.citadel_archetype = ls.citadel_archetype || "sovereign";

        const node = animatedNodes[idx];
        if (!node) return;
        const qp = sec.quantum_physics;
        node.vortexTension = qp.vortex_tension || 0.5;
        const uIdx = (sec.grid_coordinates ? sec.grid_coordinates.col : (idx % 8)) + 1;
        const lIdx = (sec.grid_coordinates ? sec.grid_coordinates.row : Math.floor(idx / 8)) + 1;

        // Schauberger Centripetal Implosion Vortex Spiral
        // Number of turns = upper_trigram_idx + lower_trigram_idx (unique per hexagram, 2..16)
        const vortexTurns = uIdx + lIdx;
        const vCount = 120;
        const vGeo = new THREE.BufferGeometry();
        const vPos = new Float32Array(vCount * 3);
        const vCol = new Float32Array(vCount * 3);
        const vBase = new THREE.Color(sec.regional_biome ? sec.regional_biome.accent : '#9CA3AF');
        const vSpec = new THREE.Color(sec.spectral_color ? sec.spectral_color.hex : '#FFD700');
        for (let p = 0; p < vCount; p++) {
          const t = p / vCount;
          const theta = t * Math.PI * 2.0 * vortexTurns;
          const r = (1.0 - t) * 14.0 * (1.0 + (qp.vortex_tension || 0.5));
          vPos[p*3]   = Math.cos(theta) * r;
          vPos[p*3+1] = -(t) * (qp.implosion_funnel_depth || 8.0) + 6.0;
          vPos[p*3+2] = Math.sin(theta) * r;
          // Radial color blend: biome accent at outer edge → hexagram spectral_color at vortex core
          vCol[p*3]   = vBase.r + (vSpec.r - vBase.r) * t;
          vCol[p*3+1] = vBase.g + (vSpec.g - vBase.g) * t;
          vCol[p*3+2] = vBase.b + (vSpec.b - vBase.b) * t;
        }
        vGeo.setAttribute('position', new THREE.BufferAttribute(vPos, 3));
        vGeo.setAttribute('color', new THREE.BufferAttribute(vCol, 3));
        const vortex = new THREE.Points(vGeo, new THREE.PointsMaterial({
          size: 1.8, vertexColors: true, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending
        }));
        node.group.add(vortex);
        node.vortex = vortex;

        // Volumetric Porosity Resonance Shell
        const pShell = new THREE.Mesh(
          new THREE.SphereGeometry((qp.porosity_cloud_radius || 15.0) * 0.7, 16, 16),
          new THREE.MeshBasicMaterial({
            color: new THREE.Color(sec.regional_biome ? sec.regional_biome.color : '#4B5563'),
            wireframe: true, transparent: true,
            opacity: Math.max(0.12, (qp.porosity_level || 0.45) * 0.35)
          })
        );
        pShell.position.y = 8;
        node.group.add(pShell);
        node.porosity = pShell;

        // Parametric Rose-Curve Avatar Core (Lissajous)
        const rCount = 360;
        const rGeo = new THREE.BufferGeometry();
        const rPos = new Float32Array(rCount * 3);
        for (let r = 0; r < rCount; r++) {
          const t = (r / rCount) * Math.PI * 2.0;
          rPos[r*3]   = Math.cos(uIdx * t) * Math.sin(lIdx * t) * 4.5;
          rPos[r*3+1] = Math.cos(lIdx * t) * 4.5 + 8.0;
          rPos[r*3+2] = Math.sin(uIdx * t) * Math.sin(lIdx * t) * 4.5;
        }
        rGeo.setAttribute('position', new THREE.BufferAttribute(rPos, 3));
        const specColor = new THREE.Color(sec.spectral_color ? sec.spectral_color.hex : '#FFD700');
        const roseMesh = new THREE.Line(rGeo, new THREE.LineBasicMaterial({
          color: specColor, transparent: true, opacity: 0.9
        }));
        node.group.add(roseMesh);
        node.rose = roseMesh;
      });
    }

    // === LAYER 2: 384 SOUND PELLETS & ATTRACTOR BEAMS ===
    function applyLayer2(l2) {
      (l2.sectors || []).forEach((ls, idx) => {
        const sec = worldData.sectors[idx];
        if (!sec) return;
        sec.yao_pellets = ls.yao_pellets || [];

        const node = animatedNodes[idx];
        if (!node) return;

        const pelletMeshes = [];
        sec.yao_pellets.forEach((yp, pIdx) => {
          const rad = yp.ternary_state === 2 ? 1.1 : (yp.ternary_state === 1 ? 0.9 : 0.65);
          const geo = yp.ternary_state === 2 ? new THREE.IcosahedronGeometry(rad, 1) : new THREE.SphereGeometry(rad, 12, 12);
          const pm = new THREE.Mesh(
            geo,
            new THREE.MeshStandardMaterial({
              color: new THREE.Color(yp.color_hex),
              emissive: new THREE.Color(yp.color_hex),
              emissiveIntensity: (yp.energy_intensity || 0.5) * 0.8,
              roughness: 0.25,
              wireframe: yp.ternary_state === 2
            })
          );
          node.group.add(pm);
          pelletMeshes.push({ mesh: pm, spec: yp, angle: pIdx * (Math.PI / 3.0) });
        });
        node.pellets = pelletMeshes;

        // King Wen Link Superposition Quantum Wave Packet Core (Central Interference Node)
        const coreGeo = new THREE.IcosahedronGeometry(1.6, 1);
        const coreMat = new THREE.MeshStandardMaterial({
          color: specColor,
          emissive: specColor,
          emissiveIntensity: 0.90,
          wireframe: true,
          transparent: true,
          opacity: 0.85
        });
        const superpositionCore = new THREE.Mesh(coreGeo, coreMat);
        superpositionCore.position.y = 8.0;
        node.group.add(superpositionCore);
        node.superpositionCore = superpositionCore;

        // 6 King Wen Link Quantum Wavepacket Convergence Conduits (Pellets -> Core)
        const convergenceBeams = [];
        sec.yao_pellets.forEach((yp, pIdx) => {
          const beamGeo = new THREE.BufferGeometry();
          const beamPos = new Float32Array(20 * 3);
          const beamCol = new Float32Array(20 * 3);
          const pCol = new THREE.Color(yp.color_hex);
          for (let k = 0; k < 20; k++) {
            beamCol[k * 3] = pCol.r;
            beamCol[k * 3 + 1] = pCol.g;
            beamCol[k * 3 + 2] = pCol.b;
          }
          beamGeo.setAttribute('position', new THREE.BufferAttribute(beamPos, 3));
          beamGeo.setAttribute('color', new THREE.BufferAttribute(beamCol, 3));
          const beamLine = new THREE.Line(beamGeo, new THREE.LineBasicMaterial({
            vertexColors: true, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending
          }));
          node.group.add(beamLine);
          convergenceBeams.push({ line: beamLine, geo: beamGeo, spec: yp, color: pCol, pIdx });
        });
        node.convergenceBeams = convergenceBeams;

        // 64 Centripetal Attractor Energy Beams (Connecting Citadels to Master Egg)
        const pos = sec.world_position;
        const citadelPos = new THREE.Vector3(pos.x, pos.y + 8.0, pos.z);
        const bGeo = new THREE.BufferGeometry();
        const bPos = new Float32Array(60 * 3);
        const bCol = new Float32Array(60 * 3);
        const specColor = new THREE.Color(sec.spectral_color ? sec.spectral_color.hex : '#FFD700');

        bGeo.setAttribute('position', new THREE.BufferAttribute(bPos, 3));
        bGeo.setAttribute('color', new THREE.BufferAttribute(bCol, 3));
        const bMesh = new THREE.Line(bGeo, new THREE.LineBasicMaterial({
          vertexColors: true, transparent: true, opacity: 0.70
        }));
        scene.add(bMesh);
        attractorBeams.push({
          mesh: bMesh, geo: bGeo, startPos: citadelPos, color: specColor, sector: sec
        });
      });

      // Cache Shotgun Wave Parameters from all 64 sectors for Ground Position & Masking Logic
      sectorShotgunParams = worldData.sectors.map((sec) => {
        const pos = sec.world_position;
        const qp = sec.quantum_physics || {};
        const pellets = sec.yao_pellets || [];
        const qwp = sec.quantum_wave_packet || {};
        const qwpPellets = qwp.sound_pellets || [];
        return {
          x: pos.x,
          z: pos.z,
          tension: qp.vortex_tension || 0.5,
          suction: qp.suction_coefficient || 0.3,
          porosity: qp.porosity_level || 0.45,
          freqs: pellets.map(p => p.frequency_hz || 146.0),
          energies: pellets.map(p => p.energy_intensity || 0.5),
          waveforms: pellets.map(p => p.waveform || "sine"),
          ternaryStates: pellets.map(p => p.ternary_state !== undefined ? p.ternary_state : 1),
          // Quantum Wave Packet superposition vectors from pre-computed kit
          qwpFreqs: qwpPellets.map(qp => qp.frequency_hz || 200.0),
          qwpEnergies: qwpPellets.map(qp => qp.energy_intensity || 1.0),
          qwpFundHz: qwp.fundamental_frequency_hz || qp.fundamental_frequency_hz || 108.0,
          color: new THREE.Color(sec.spectral_color ? sec.spectral_color.hex : '#FFD700')
        };
      });
    }

    // === LAYER 3: MASTER CENTRIPETAL EGG & UNISON AUDIO ===
    function applyLayer3(l3) {
      worldData.egg_keyframes = l3.egg_keyframes || [];
      worldData.prewarmed_egg_keyframes = l3.egg_keyframes || [];
      worldData.audio_unison_wav_b64 = l3.audio_unison_wav_b64 || "";
      worldData.jkd_passages_by_hex = l3.jkd_passages_by_hex || {};

      worldData.sectors.forEach(sec => {
        sec.jkd_passages = worldData.jkd_passages_by_hex[sec.hexagram_id] || [];
      });

      // Master 3D Centripetal Egg Resonator Mesh
      const EGG_SEGS_W = 48, EGG_SEGS_H = 36;
      eggGeo = new THREE.SphereGeometry(340, EGG_SEGS_W, EGG_SEGS_H);
      eggGeo.attributes.position.usage = THREE.DynamicDrawUsage;

      masterEggMesh = new THREE.Mesh(eggGeo, new THREE.MeshStandardMaterial({
        color: 0x8b5cf6,
        emissive: 0x6d28d9,
        emissiveIntensity: 0.45,
        wireframe: true,
        transparent: true,
        opacity: 0.38,
        roughness: 0.15
      }));
      masterEggMesh.position.set(0, 40, 0);
      masterEggMesh.userData = { isMasterEgg: true, name: 'Master Centripetal Egg Vortex' };
      scene.add(masterEggMesh);
      raycastTargets.unshift(masterEggMesh);
    }

    // === PROGRESSIVE EDGE PRE-WARM CACHE PIPELINE ===
    async function startLayeredPrewarmPipeline() {
      const progressBar = document.getElementById('prewarm-progress-bar');
      const statusText = document.getElementById('prewarm-layer-status');
      const overlay = document.getElementById('prewarm-loader-overlay');

      try {
        // [LAYER 0/3]
        if (statusText) statusText.innerText = '[LAYER 0/3] Pre-warming 64 Spatial Skeleton Citadels & Biomes...';
        if (progressBar) progressBar.style.width = '20%';
        let l0 = null;
        try {
          const r0 = await fetch('/api/cache/layer/0');
          if (r0.ok) { const j0 = await r0.json(); l0 = j0.data; }
        } catch(e) {}
        if (!l0 && embeddedTopology.sectors) { l0 = { sectors: embeddedTopology.sectors }; }
        applyLayer0(l0);
        if (progressBar) progressBar.style.width = '25%';

        // [LAYER 1/3]
        if (statusText) statusText.innerText = '[LAYER 1/3] Synthesizing 64 Quantum Physics Vortices & Depth Clouds...';
        let l1 = null;
        try {
          const r1 = await fetch('/api/cache/layer/1');
          if (r1.ok) { const j1 = await r1.json(); l1 = j1.data; }
        } catch(e) {}
        if (!l1 && embeddedTopology.sectors) { l1 = { sectors: embeddedTopology.sectors }; }
        applyLayer1(l1);
        if (progressBar) progressBar.style.width = '50%';

        // [LAYER 2/3]
        if (statusText) statusText.innerText = '[LAYER 2/3] Tuning 384 Sound Pellets & Web Audio Ground Field...';
        let l2 = null;
        try {
          const r2 = await fetch('/api/cache/layer/2');
          if (r2.ok) { const j2 = await r2.json(); l2 = j2.data; }
        } catch(e) {}
        if (!l2 && embeddedTopology.sectors) { l2 = { sectors: embeddedTopology.sectors }; }
        applyLayer2(l2);
        if (progressBar) progressBar.style.width = '75%';

        // [LAYER 3/3]
        if (statusText) statusText.innerText = '[LAYER 3/3] Materializing 60-Keyframe Centripetal Egg & Audio Unison...';
        let l3 = null;
        try {
          const r3 = await fetch('/api/cache/layer/3');
          if (r3.ok) { const j3 = await r3.json(); l3 = j3.data; }
        } catch(e) {}
        if (!l3) {
          l3 = {
            egg_keyframes: embeddedTopology.prewarmed_egg_keyframes || embeddedTopology.egg_keyframes || [],
            audio_unison_wav_b64: embeddedTopology.audio_unison_wav_b64 || "",
            jkd_passages_by_hex: (embeddedTopology.sectors || []).reduce((acc, s) => {
              if (s.jkd_passages) acc[s.hexagram_id] = s.jkd_passages;
              return acc;
            }, {})
          };
        }
        applyLayer3(l3);
        if (progressBar) progressBar.style.width = '100%';
        if (statusText) statusText.innerText = '✨ [ALL 4 LAYERS PRE-WARMED] Sovereign 3D Macro-World Ready!';

        setTimeout(() => {
          if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
            setTimeout(() => { overlay.style.display = 'none'; }, 600);
          }
        }, 350);

      } catch(err) {
        console.error('[PREWARM] Phased loader fallback:', err);
        if (overlay) overlay.style.display = 'none';
      }
    }

    // === RAYCASTING INTERACTION ===
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    window.addEventListener('mousemove', (e) => {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(raycastTargets);
      if (hits.length > 0) {
        const obj = hits[0].object;
        if (obj.userData && obj.userData.isMasterEgg) {
          document.getElementById('sel-name').innerText = '🥚 Master Centripetal Egg Vortex Attractor (64-Node Matrix)';
          document.getElementById('val-biome').innerText = 'All 8 Regional Biomes Integrated';
          document.getElementById('val-action').innerText = 'Schauberger Implosion (384 Sound Pellets in Unison)';
          document.getElementById('val-depth').innerText = 'Total 64 Citadels | 7,817,600 DA-V2 Point Cloud Vertices';
          document.getElementById('spectral-badge').style.background = '#8b5cf6';
          document.getElementById('spectral-badge').style.boxShadow = '0 0 12px #8b5cf6';
          document.getElementById('spectral-text').innerText = '#8B5CF6 — Universal 64-Node Spectral Matrix';
          document.getElementById('val-audio').innerText = '384 Sound Pellets Active | Unified Field Fundamental Range: 108.0Hz .. 199.1Hz';
          return;
        }

        const d = obj.userData;
        document.getElementById('sel-name').innerText =
          'Hex #' + d.hexagram_id + ': ' + d.name + ' (' + d.hanzi + ')';
        document.getElementById('val-biome').innerText = d.regional_biome.name;
        const vec5 = d.emotional_vector_5axis || {};
        const vecStr = `Chaos: ${(vec5.chaos || 0.2).toFixed(2)} | Whimsy: ${(vec5.whimsy || 0.15).toFixed(2)} | DarkTone: ${(vec5.darkTone || 0.15).toFixed(2)} | Coherence: ${(vec5.coherence || 0.5).toFixed(2)} | VoiceWeight: ${(vec5.voiceWeight || 0.6).toFixed(2)}`;
        document.getElementById('val-action').innerText =
          d.action_doctrine + ' (' + d.citadel_archetype + ') — ' + vecStr;
        const ds = d.quantum_physics.depth_statistics || {};
        document.getElementById('val-depth').innerText =
          'Mean: ' + (ds.mean_depth || 10.0) + 'm (Range: ' + (ds.min_depth || 0) + '..' + (ds.max_depth || 20) + 'm) | ' + (d.quantum_physics.depth_pointcloud_vertices || 122150) + ' pts';
        
        const sc = d.spectral_color || { hex: '#FFD700', name: 'Spectral' };
        const hueDeg = d.base_hue_degrees !== undefined ? Number(d.base_hue_degrees).toFixed(1) : '0.0';
        document.getElementById('spectral-badge').style.background = sc.hex;
        document.getElementById('spectral-badge').style.boxShadow = '0 0 8px ' + sc.hex;
        document.getElementById('spectral-text').innerText = sc.hex + ' (' + hueDeg + '\u00B0) \u2014 ' + (sc.name || 'Spectral Hue');

        const freqs = (d.yao_pellets || []).map(yp => `L${yp.line_position}:${yp.ternary_state === 2 ? 'YAO' : (yp.ternary_state === 1 ? 'YANG' : 'YIN')}@${yp.frequency_hz}Hz`).join(' | ');
        const cutoff = Math.round(400 + (d.quantum_physics.porosity_level || 0.45) * 3200);
        document.getElementById('val-audio').innerHTML = `<strong style="color:#38bdf8;">📡 Emotional Engine 5-Axis Vector & King Wen Link Wave Packet:</strong><br/><span style="font-size:10px;color:#cbd5e1;">[${freqs}]</span><br/><span style="font-size:10px;color:#a78bfa;">Vortex: ${(d.quantum_physics.vortex_tension || 0.5).toFixed(3)} • Suction: ${(d.quantum_physics.suction_coefficient || 0.3).toFixed(3)} • Cutoff: ${cutoff}Hz</span>`;

        playHexHarmonics(d);
      }
    });

    // === PHYSICS ANIMATION LOOP ===
    let clock = 0;
    function animate() {
      requestAnimationFrame(animate);
      clock += 0.02;
      presentTime += 0.02 * timeSpeed;
      controls.update();

      // === DYNAMIC QUANTUM GROUND FIELD & CENTRIPETAL TERRAIN ATTRACTION (SHOTGUN WAVE FUNCTIONS & MASKING) ===
      if (terrainBasePos && centripetalEggActive) {
        const tPos = terrainGeo.attributes.position;
        const tArr = tPos.array;
        const tCol = terrainGeo.attributes.color.array;
        const tBase = terrainBasePos;
        const tBaseCol = terrainBaseColors;
        const vertCount = tPos.count;

        for (let i = 0; i < vertCount; i++) {
          const idx = i * 3;
          const bx = tBase[idx];
          const by = tBase[idx + 1];
          const bz = tBase[idx + 2];

          // Radial distance & angle from central Master Egg origin (0, 40, 0)
          const r = Math.sqrt(bx * bx + bz * bz);
          const theta = Math.atan2(bz, bx);

          // 1. Centripetal Attractor Inward Traveling Ripple (moving toward Master Egg core)
          const centripetalWave = Math.sin(r * 0.028 - presentTime * 2.4 + theta * 2.0) * (2.8 * Math.exp(-r / 320.0));

          // 2. Quantum Potential-Well Dynamic Surface Breathing
          const wellBreathing = Math.sin(presentTime * 3.5 + bx * 0.015 + bz * 0.015) * 1.2;

          // 3. Dynamic radial suction pull toward Master Egg
          const radialSuction = (attractorMode === 'implosion')
            ? Math.cos(r * 0.018 - presentTime * 3.0) * (1.8 * Math.exp(-r / 240.0))
            : Math.sin(presentTime * 2.0 + theta * 4.0) * 1.0;

          // 4. Shotgun Wave Functions from 64 Converging Citadels with Porosity & Ternary Changing-Line Masking
          let shotgunWave = 0.0;
          let rHexSum = 0.08, gHexSum = 0.09, bHexSum = 0.16, wTotal = 1.0;

          if (sectorShotgunParams.length > 0) {
            const gridCol = Math.max(0, Math.min(7, Math.floor((bx + 280.0) / 70.0)));
            const gridRow = Math.max(0, Math.min(7, Math.floor((bz + 280.0) / 70.0)));

            for (let ro = -1; ro <= 1; ro++) {
              const rIdx = gridRow + ro;
              if (rIdx < 0 || rIdx > 7) continue;
              for (let co = -1; co <= 1; co++) {
                const cIdx = gridCol + co;
                if (cIdx < 0 || cIdx > 7) continue;
                const sIdx = rIdx * 8 + cIdx;
                const sp = sectorShotgunParams[sIdx];
                if (!sp) continue;

                const dx = bx - sp.x, dz = bz - sp.z;
                const distSq = dx * dx + dz * dz;
                if (distSq > 10000) continue; // 100m cutoff

                const dist = Math.sqrt(distSq);
                const spatialWeight = Math.exp(-distSq / (2.0 * 2200.0));

                // Masking: Porosity interference masking & boundary attenuation
                const porosityMask = 1.0 - 0.35 * sp.porosity * Math.sin(bx * 0.12 + bz * 0.12);

                // Quantum Wave Packet Superposition (Spatial Field Wavepacket + Pre-computed Kit Quantum Wavepacket)
                let pelletHarmonicSum = 0.0;
                for (let pIdx = 0; pIdx < sp.freqs.length; pIdx++) {
                  const freq = sp.freqs[pIdx];
                  const energy = sp.energies[pIdx];
                  const wType = sp.waveforms[pIdx];
                  const tState = sp.ternaryStates[pIdx];

                  // 1. Spatial Field Wave Packet Component
                  const phaseSpatial = presentTime * (freq / 110.0) * 1.2 + pIdx * 1.047 + dist * 0.06;
                  let wVal = 0.0;
                  if (wType === 'triangle') {
                    wVal = 2.0 * Math.abs(2.0 * ((phaseSpatial / (Math.PI * 2.0)) % 1.0) - 1.0) - 1.0;
                  } else if (wType === 'sawtooth') {
                    wVal = 2.0 * ((phaseSpatial / (Math.PI * 2.0)) % 1.0) - 1.0;
                  } else {
                    wVal = Math.sin(phaseSpatial);
                  }
                  const ternarySign = tState === 2 ? 1.4 : (tState === 1 ? 1.0 : -0.7);

                  // 2. Pre-computed Kit Quantum Wave Packet Component
                  const qwpFreq = sp.qwpFreqs[pIdx] || freq;
                  const qwpEnergy = sp.qwpEnergies[pIdx] || energy;
                  const phaseKit = presentTime * (qwpFreq / 120.0) + pIdx * 0.523 + dist * 0.04;
                  const wValKit = Math.sin(phaseKit);

                  // Construct superposition Psi_total = Psi_spatial + Psi_kit
                  pelletHarmonicSum += (wVal * energy * ternarySign + 0.45 * wValKit * qwpEnergy);
                }

                const localShotgun = spatialWeight * porosityMask * (pelletHarmonicSum / 6.0) * (sp.tension * 5.5 + sp.suction * 2.5);
                shotgunWave += localShotgun;

                // Accumulate per-hexagram spectral color tag (R, G, B) weighted by spatial proximity & wave oscillation
                const wHex = spatialWeight * (0.85 + 0.35 * Math.sin(presentTime * (sp.qwpFundHz / 35.0) + sIdx * 0.1));
                rHexSum += sp.color.r * wHex * 2.5;
                gHexSum += sp.color.g * wHex * 2.5;
                bHexSum += sp.color.b * wHex * 2.5;
                wTotal += wHex * 2.5;
              }
            }
          }

          tArr[idx + 1] = by + centripetalWave + wellBreathing + radialSuction + shotgunWave;

          // 5. Dynamic Hexagram Spectral Color Pulse derived strictly from per-hexagram color tags
          const coreGlow = Math.exp(-r / 160.0) * 0.35;
          const colorMultiplier = 1.0 + 0.25 * Math.sin(presentTime * 2.5 + theta * 3.0);
          tCol[idx]     = Math.min(1.0, (rHexSum / wTotal) * colorMultiplier + coreGlow * 0.54);
          tCol[idx + 1] = Math.min(1.0, (gHexSum / wTotal) * colorMultiplier + coreGlow * 0.36);
          tCol[idx + 2] = Math.min(1.0, (bHexSum / wTotal) * colorMultiplier + coreGlow * 0.96);
        }
        tPos.needsUpdate = true;
        if (tBaseCol) terrainGeo.attributes.color.needsUpdate = true;
      }

      // === UNIFIED WEAVE EGG — GODHEAD SUPERPOSITION REACTION OF ALL 64 OUTPUTS ===
      if (typeof masterEggMesh !== 'undefined' && masterEggMesh) {
        masterEggMesh.visible = centripetalEggActive;
        if (centripetalEggActive) {
          // Compute live Godhead Superposition Reaction sum from all 64 active citadel outputs
          let godheadInterference = 0.0;
          let godheadEnergy = 0.0;
          if (sectorShotgunParams && sectorShotgunParams.length > 0) {
            for (let sIdx = 0; sIdx < sectorShotgunParams.length; sIdx++) {
              const sp = sectorShotgunParams[sIdx];
              const phase = presentTime * (sp.qwpFundHz / 108.0) * 1.5 + sIdx * 0.098;
              godheadInterference += Math.sin(phase) * sp.tension * sp.suction;
              godheadEnergy += sp.tension * sp.porosity;
            }
            godheadInterference /= 64.0;
            godheadEnergy /= 64.0;
          } else {
            godheadInterference = 0.35 * Math.sin(presentTime * 2.5);
            godheadEnergy = 0.50;
          }

          // Implosion rotation & twist driven by Godhead Superposition Reaction
          const spinRate = (0.005 + godheadEnergy * 0.012) * timeSpeed;
          masterEggMesh.rotation.y += spinRate;
          masterEggMesh.rotation.x = Math.sin(presentTime * 0.8) * 0.12 * godheadInterference;

          // Dynamic scale breathing from Godhead Superposition Reaction
          const godheadScale = 1.0 + 0.35 * godheadInterference + 0.15 * Math.sin(presentTime * 3.2);
          if (attractorMode === 'implosion') {
            masterEggMesh.scale.set(godheadScale * 0.95, godheadScale * 1.25, godheadScale * 0.95);
          } else if (attractorMode === 'toroidal') {
            masterEggMesh.scale.set(godheadScale * 1.30, godheadScale * 0.80, godheadScale * 1.30);
          } else { // unison_resonance
            masterEggMesh.scale.set(godheadScale * 1.15, godheadScale * 1.15, godheadScale * 1.15);
          }

          // Live emissive material glow modulation reacting to Godhead Superposition
          if (masterEggMesh.material) {
            masterEggMesh.material.emissiveIntensity = 0.70 + 0.30 * Math.abs(godheadInterference);
          }

          // === PRE-WARMED 60-KEYFRAME VERTEX ANIMATION WITH GODHEAD DEFORMATION OVERLAY ===
          if (worldData.prewarmed_egg_keyframes && worldData.prewarmed_egg_keyframes.length > 0) {
            const numFrames = worldData.prewarmed_egg_keyframes.length;
            const cycle = (presentTime * 0.4) % 1.0;
            const frameIdx = Math.floor(cycle * numFrames) % numFrames;
            const kf = worldData.prewarmed_egg_keyframes[frameIdx];

            const posAttr = eggGeo.attributes.position;
            const pArray = posAttr.array;
            const deformFactor = 1.0 + 0.18 * godheadInterference;
            for (let i = 0; i < kf.length; i++) {
              pArray[i] = kf[i] * deformFactor;
            }
            posAttr.needsUpdate = true;
            eggGeo.computeVertexNormals();
          }
        }
      }

      animatedNodes.forEach((n, nIdx) => {
        const sec = worldData.sectors[nIdx];
        const pos = sec.world_position;
        const qp = sec.quantum_physics || {};

        // All motion rates derived from the hexagram's own spatial frequency field — not shared clock constants.
        const hexFundHz = qp.fundamental_frequency_hz || (108.0 * (1.0 + 0.40 * Math.sqrt(pos.x*pos.x + pos.z*pos.z) / 280.0));
        const hexDriveRate = hexFundHz / 55.0;
        const hexSpin = hexFundHz / 420.0;

        // Spin speed derived from hexagram vortex tension + suction — not a flat scalar.
        let spinSpeed = hexSpin * (1.0 + qp.vortex_tension * 2.2 + qp.suction_coefficient * 0.8);

        // Pulse derived from hexagram's mean yao pellet frequency — not shared clock * 1.5.
        const meanPelletFreq = n.pellets.length > 0
          ? n.pellets.reduce((s, p) => s + (p.spec.frequency_hz || 146.0), 0) / n.pellets.length
          : hexFundHz;
        let pulse = 1.0 + Math.sin(presentTime * (meanPelletFreq / 90.0) + nIdx * 0.098) * 0.06;

        // === CENTRIPETAL EGG GENERATION FROM PRESENT TIME (ALL 64 UNISON) ===
        if (centripetalEggActive) {
          const eggPhase = presentTime * hexDriveRate + (pos.x * 0.01 + pos.z * 0.01);
          const eggFactor = 1.0 + 0.35 * Math.sin(eggPhase);

          if (attractorMode === 'implosion') {
            // Spin rate from hexagram fundamental, not scripted 3.0 constant.
            spinSpeed *= (1.8 + 0.9 * Math.sin(presentTime * hexDriveRate + nIdx * 0.1));
            pulse *= (0.85 + 0.35 * Math.sin(eggPhase));
            n.vortex.scale.set(eggFactor * 0.9, 1.0 + 0.5 * Math.sin(presentTime * (hexFundHz / 160.0)), eggFactor * 0.9);
          } else if (attractorMode === 'toroidal') {
            const torusPulse = 1.0 + 0.4 * Math.sin(presentTime * (hexFundHz / 55.0) + nIdx * 0.2);
            n.porosity.scale.set(torusPulse, torusPulse * 1.25, torusPulse);
            n.vortex.rotation.z = Math.sin(presentTime * (hexFundHz / 195.0) + nIdx * 0.1) * 0.3;
          } else if (attractorMode === 'unison_resonance') {
            // Drive from hexagram vortex tension + suction — not flat 2.8 constant.
            spinSpeed *= (qp.vortex_tension * 4.2 + qp.suction_coefficient * 1.8);
            pulse = 1.0 + 0.25 * Math.sin(presentTime * (meanPelletFreq / 35.0));
          }

          // Implosion orbital physics for 6-yao sound pellets — each driven by its own frequency
          n.pellets.forEach((p, pIdx) => {
            const pelletFreq = p.spec.frequency_hz || 146.0;
            const pelletPhase = p.angle + presentTime * p.spec.orbital_speed * 1.5;
            // Orbital radius oscillation driven by pellet's own wave frequency — not shared 2.5 constant.
            const implosionRadius = p.spec.orbit_radius * (0.60 + 0.40 * Math.sin(presentTime * (pelletFreq / 50.0) + pIdx * 0.5));
            p.mesh.position.x = Math.cos(pelletPhase) * implosionRadius;
            p.mesh.position.z = Math.sin(pelletPhase) * implosionRadius;
            // Vertical oscillation driven by pellet's own frequency — not shared 3.0 constant.
            p.mesh.position.y = 8.0 + Math.sin(pelletPhase * 2.0 + presentTime * (pelletFreq / 46.0)) * 2.2;
            if (p.spec.ternary_state === 2) {
              p.mesh.rotation.x += 0.08;
              p.mesh.rotation.y += 0.08;
            }
          });
        } else {
          // Standard Orbiting Pellets — still driven by per-pellet orbital_speed from generator
          n.pellets.forEach(p => {
            const pelletFreq = p.spec.frequency_hz || 146.0;
            p.angle += p.spec.orbital_speed * 0.03;
            p.mesh.position.x = Math.cos(p.angle) * p.spec.orbit_radius;
            p.mesh.position.z = Math.sin(p.angle) * p.spec.orbit_radius;
            p.mesh.position.y = 8.0 + Math.sin(p.angle * 2.0 + presentTime * (pelletFreq / 90.0)) * 1.8;
            if (p.spec.ternary_state === 2) {
              p.mesh.rotation.x += 0.05;
              p.mesh.rotation.y += 0.05;
            }
          });
        }

        n.vortex.rotation.y += spinSpeed;
        n.porosity.scale.set(pulse, pulse, pulse);
        n.porosity.rotation.y -= 0.005;

        n.rose.rotation.y += 0.015;
        n.rose.rotation.z = Math.sin(clock + nIdx) * 0.1;

        n.beacon.rotation.y += 0.02;
        n.beacon.position.y = 8 + Math.sin(clock * 2 + nIdx) * 1.0;

        // === KING WEN LINK QUANTUM WAVEPACKET CONVERGENCE CONDUITS (PELLETS -> CORE) ===
        if (n.convergenceBeams && n.convergenceBeams.length > 0) {
          let coreHarmonicInterference = 0.0;
          n.convergenceBeams.forEach((cb, bIdx) => {
            const pMesh = n.pellets[bIdx] ? n.pellets[bIdx].mesh : null;
            if (!pMesh) return;

            const posAttr = cb.geo.attributes.position;
            const pArr = posAttr.array;
            const count = 20;
            const px = pMesh.position.x, py = pMesh.position.y, pz = pMesh.position.z;
            const cx = 0.0, cy = 8.0, cz = 0.0; // Citadel core center

            const freq = cb.spec.frequency_hz || 146.0;
            const energy = cb.spec.energy_intensity || 0.5;
            const pulseSpeed = (freq / 35.0) * timeSpeed;
            const pulseCycle = (presentTime * pulseSpeed + bIdx * 0.3) % 1.0;

            for (let k = 0; k < count; k++) {
              const t = k / (count - 1);
              // Interpolate line from pellet to core
              const lx = px + (cx - px) * t;
              const ly = py + (cy - py) * t;
              const lz = pz + (cz - pz) * t;

              // King Wen Link quantum wave packet pulse envelope: Gaussian peak propagating inward
              const distFromPulse = t - pulseCycle;
              const packetEnvelope = Math.exp(-(distFromPulse * distFromPulse) / 0.04);
              const packetOsc = Math.sin(t * Math.PI * 8.0 - presentTime * (freq / 15.0));

              // Transverse wave packet displacement
              const perpX = -pz * 0.15 * packetOsc * packetEnvelope;
              const perpZ =  px * 0.15 * packetOsc * packetEnvelope;
              const perpY = Math.cos(t * Math.PI * 6.0) * 0.6 * packetEnvelope;

              pArr[k * 3]     = lx + perpX;
              pArr[k * 3 + 1] = ly + perpY;
              pArr[k * 3 + 2] = lz + perpZ;
            }
            posAttr.needsUpdate = true;
            coreHarmonicInterference += Math.sin(presentTime * (freq / 40.0) + bIdx * 1.047) * energy;
          });

          // Animate Superposition Wave Packet Core Mesh
          if (n.superpositionCore) {
            const superScale = 1.0 + 0.45 * Math.abs(coreHarmonicInterference);
            n.superpositionCore.scale.set(superScale, superScale, superScale);
            n.superpositionCore.rotation.x += 0.04 * (1.0 + n.vortexTension);
            n.superpositionCore.rotation.y += 0.05 * (1.0 + n.vortexTension);
          }
        }
      });

      // === UPDATE 64 CENTRIPETAL ATTRACTOR ENERGY BEAMS (ATTRACTING ALL 64 TO MASTER EGG) ===
      if (typeof attractorBeams !== 'undefined' && attractorBeams.length > 0) {
        attractorBeams.forEach((beam, bIdx) => {
          if (centripetalEggActive) {
            beam.mesh.visible = true;
            const posAttr = beam.geo.attributes.position;
            const colAttr = beam.geo.attributes.color;
            const pArray = posAttr.array;
            const cArray = colAttr.array;

            const start = beam.startPos;
            const target = eggCenter;
            const count = 60;

            for (let k = 0; k < count; k++) {
              const t = k / (count - 1);
              // Inward spiral interpolation along centripetal egg curve
              const spiralAngle = t * Math.PI * 6.0 + presentTime * 3.0 + bIdx * 0.1;
              const spiralRadius = (1.0 - t) * 24.0 * (1.0 + (beam.sector.quantum_physics.vortex_tension || 0.5));

              const cx = start.x + (target.x - start.x) * t + Math.cos(spiralAngle) * spiralRadius;
              const cy = start.y + (target.y - start.y) * t + Math.sin(t * Math.PI) * 15.0;
              const cz = start.z + (target.z - start.z) * t + Math.sin(spiralAngle) * spiralRadius;

              pArray[k * 3]     = cx;
              pArray[k * 3 + 1] = cy;
              pArray[k * 3 + 2] = cz;

              // Color gradient from citadel spectral color to egg purple
              const colRatio = Math.sin(t * Math.PI + presentTime * 2.0) * 0.5 + 0.5;
              cArray[k * 3]     = beam.color.r * (1.0 - colRatio) + 0.54 * colRatio;
              cArray[k * 3 + 1] = beam.color.g * (1.0 - colRatio) + 0.36 * colRatio;
              cArray[k * 3 + 2] = beam.color.b * (1.0 - colRatio) + 0.96 * colRatio;
            }
            posAttr.needsUpdate = true;
            colAttr.needsUpdate = true;
          } else {
            beam.mesh.visible = false;
          }
        });
      }

      // === UNIFIED QUANTUM GROUND FIELD — CENTRIPETAL EGG SPATIAL ATTENUATION & UNISON RESONANCE ===
      if (fieldActive && audioCtx && groundVoices.length > 0) {
        const camPos = camera.position;
        const now = audioCtx.currentTime;

        groundVoices.forEach((gv) => {
          const dist = camPos.distanceTo(gv.pos3D);
          // Scaled for macro-world geometry (560m x 560m grid):
          // High base gain (0.08..0.20) so all 64 citadels are clearly audible in unison, plus proximity boost
          let spatialAtten = 0.08 + 0.12 / (1.0 + Math.pow(dist / 180.0, 1.5));

          if (centripetalEggActive) {
            // Modulate each 6-yao pellet oscillator frequency in unison from present time
            const eggOsc = 1.0 + 0.12 * Math.sin(presentTime * 3.0 + gv.hexId * 0.1);
            if (gv.pelletOscillators) {
              gv.pelletOscillators.forEach((pOsc, pIdx) => {
                const pelletBase = (gv.sector.yao_pellets && gv.sector.yao_pellets[pIdx])
                  ? gv.sector.yao_pellets[pIdx].frequency_hz
                  : gv.fundamentalFreq;
                pOsc.frequency.setTargetAtTime(pelletBase * eggOsc, now, 0.04);
              });
            }
            if (attractorMode === 'unison_resonance') {
              spatialAtten *= 1.8; // Boost unison pellet resonance gain
            }
          }
          gv.gain.gain.setTargetAtTime(spatialAtten, now, 0.05);
        });
      }

      renderer.render(scene, camera);
    }
    startLayeredPrewarmPipeline();
    animate();

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
"""
    # Inject the world JSON into the placeholder
    viewer_html = viewer_html.replace("__WORLD_JSON_PLACEHOLDER__", world_json)

    viewer_out.write_text(viewer_html, encoding="utf-8")
    print(f"[4/4] Generated Quantum Viewfinder with Vortices, Pellets & Porosity: {viewer_out.name}")

    print("=" * 85)
    print("KING WEN 64-SOVEREIGN QUANTUM MACRO-WORLD: 100% COMPLETE")
    print("=" * 85)
    return 0

if __name__ == "__main__":
    sys.exit(generate_sovereign_world())
