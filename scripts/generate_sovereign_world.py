import json
import math
import sys
from pathlib import Path

ROOT = Path(r"c:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE

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
            vortex_tension = round((u_idx * l_idx) / 49.0, 4)
            suction_coeff = round((u_idx + l_idx) / 14.0, 4)
            porosity_level = round(0.15 + (u_idx * 0.05) + (l_idx * 0.03), 3)

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
                # Check for temporal phase changing line modulation (ternary state 2 = yao)
                is_changing = (biome_id in [3, 4]) and ((line_idx % 3) == (biome_id % 3))
                ternary_state = 2 if is_changing else (1 if bit == 1 else 0)

                orbit_radius = round(6.0 + line_idx * 2.2, 2)
                orbital_speed = round(0.5 + (line_idx + 1) * 0.25 * (1.0 + vortex_tension) * (1.2 if ternary_state == 2 else 1.0), 3)

                line_ratio = 1.0 + (line_idx / 6.0) * 0.618
                line_phase_mod = 1.0 + 0.12 * math.cos(spatial_theta * (line_idx + 1) + elevation / 10.0)
                ternary_mult = 1.18 if ternary_state == 2 else (1.0 if ternary_state == 1 else 0.82)
                freq_hz = round(spatial_fundamental_hz * line_ratio * ternary_mult * line_phase_mod * (1.0 + vortex_tension * 0.20), 2)

                if ternary_state == 1:
                    line_type = "yang"
                    color_hex = "#FFD700"
                    energy = 1.0
                elif ternary_state == 0:
                    line_type = "yin"
                    color_hex = "#38BDF8"
                    energy = 0.6
                else:
                    line_type = "yao"
                    color_hex = "#A855F7"
                    energy = 1.4

                yao_pellets.append({
                    "line_position": line_idx + 1,
                    "sub_trigram": "lower" if line_idx < 3 else "upper",
                    "sub_position": (line_idx % 3) + 1,
                    "ternary_state": ternary_state,
                    "line_type": line_type,
                    "orbit_radius": orbit_radius,
                    "orbital_speed": orbital_speed,
                    "color_hex": color_hex,
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
            spectral_color = k_color.get("primary_color", {"hex": "#FFD700", "name": f"{base['name']} Gold"})
            palette_16 = k_color.get("palette_16", [])
            base_hue = k_color.get("final_hue_degrees", (h_id - 1) * 5.625)

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
                "quantum_physics": {
                    "vortex_tension": vortex_tension,
                    "suction_coefficient": suction_coeff,
                    "porosity_level": porosity_level,
                    "implosion_funnel_depth": round(vortex_tension * 18.0, 2),
                    "porosity_cloud_radius": round(12.0 + porosity_level * 16.0, 2),
                    "depth_statistics": depth_stats,
                    "depth_pointcloud_vertices": pc_verts
                },
                "quantum_wave_packet": quantum_wp,
                "yao_pellets": yao_pellets,
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

    # 3. Master World Topology Manifest
    world_topology = {
        "world_name": "King Wen Sovereign Macro-World",
        "version": "3.1.0",
        "spatial_metrics": {
            "world_dimensions_meters": [560.0, 560.0],
            "total_sectors": 64,
            "sector_dimensions_meters": [70.0, 70.0],
            "elevation_range_meters": [-15.0, 35.0]
        },
        "temporal_biomes": temporal_biomes,
        "heightmap_matrix_8x8": heightmap_grid,
        "quantum_prewarm": prewarm_data if prewarm_data else {"status": "unwarmed"},
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
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
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
      </div>
    </div>
  </div>
  <div id="instructions">&#x1F5B1;&#xFE0F; Left Click + Drag: Orbit | Scroll: Zoom | Hover: Live Node Telemetry &amp; Acoustic Harmonics</div>

  <script>
    // === DATA INGESTION ===
    const worldData = __WORLD_JSON_PLACEHOLDER__;

    // === WEB AUDIO API UNIFIED QUANTUM GROUND FIELD ENGINE ===
    let audioCtx = null;
    let fieldActive = false;
    let groundVoices = [];
    let focusOscillators = [];
    let focusGains = [];
    let masterFilter = null;
    let masterGain = null;
    let activeHexData = null;
    let currentAudioMode = 'field';

    function initAudio() {
      if (audioCtx) return;
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();

      masterGain = audioCtx.createGain();
      masterGain.gain.setValueAtTime(0.0, audioCtx.currentTime);

      masterFilter = audioCtx.createBiquadFilter();
      masterFilter.type = 'lowpass';
      masterFilter.frequency.setValueAtTime(1600, audioCtx.currentTime);
      masterFilter.Q.setValueAtTime(3.0, audioCtx.currentTime);

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

      // 2. The Unified Quantum Ground Field: All 64 Hexagrams (1..64) Resonating As One Field
      if (worldData.sectors) {
        worldData.sectors.forEach((sec) => {
          const sOsc = audioCtx.createOscillator();
          const sGain = audioCtx.createGain();
          const sFilter = audioCtx.createBiquadFilter();

          // Frequency strictly derived from continuous 3D (x, y, z) spatial geometry
          const pos = sec.world_position;
          const normX = pos.x / 280.0, normZ = pos.z / 280.0, normY = pos.y / 35.0;
          const normR = Math.sqrt(normX * normX + normZ * normZ);
          const theta = Math.atan2(pos.z, pos.x);
          const fundamentalFreq = 108.0 * (1.0 + 0.40 * normR + 0.25 * normY + 0.15 * Math.sin(3.0 * theta + normY * Math.PI));

          sOsc.type = (sec.hexagram_id % 3 === 0) ? 'triangle' : ((sec.hexagram_id % 2 === 0) ? 'sine' : 'sawtooth');
          sOsc.frequency.setValueAtTime(fundamentalFreq, audioCtx.currentTime);

          sFilter.type = 'lowpass';
          const qp = sec.quantum_physics || {};
          const cutoff = 350 + (qp.porosity_level || 0.45) * 2400 + 300 * normY;
          const qRes = 1.2 + (qp.vortex_tension || 0.5) * 3.5 + 0.8 * normR;
          sFilter.frequency.setValueAtTime(cutoff, audioCtx.currentTime);
          sFilter.Q.setValueAtTime(qRes, audioCtx.currentTime);

          sGain.gain.setValueAtTime(0.0, audioCtx.currentTime);

          sOsc.connect(sFilter);
          sFilter.connect(sGain);
          sGain.connect(masterGain);
          sOsc.start();

          groundVoices.push({
            hexId: sec.hexagram_id,
            sector: sec,
            pos3D: new THREE.Vector3(pos.x, pos.y, pos.z),
            osc: sOsc,
            filter: sFilter,
            gain: sGain,
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
        btn.innerText = '🌌 UNIFIED QUANTUM GROUND FIELD: ACTIVE (1..64)';
        btn.classList.add('active');
        masterGain.gain.setTargetAtTime(0.30, audioCtx.currentTime, 0.05);
        if (activeHexData) playHexHarmonics(activeHexData);
      } else {
        btn.innerText = '⚡ ACTIVATE UNIFIED QUANTUM GROUND FIELD (1..64)';
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

      // All 64 voices of the ground field baked into the WAV
      worldData.sectors.forEach((sec) => {
        const pos = sec.world_position;
        const normX = pos.x / 280.0, normZ = pos.z / 280.0, normY = pos.y / 35.0;
        const normR = Math.sqrt(normX * normX + normZ * normZ);
        const theta = Math.atan2(pos.z, pos.x);
        const freq = 108.0 * (1.0 + 0.40 * normR + 0.25 * normY + 0.15 * Math.sin(3.0 * theta + normY * Math.PI));

        const osc = offlineCtx.createOscillator();
        const g = offlineCtx.createGain();
        osc.type = (sec.hexagram_id % 3 === 0) ? 'triangle' : ((sec.hexagram_id % 2 === 0) ? 'sine' : 'sawtooth');
        osc.frequency.setValueAtTime(freq, 0);
        g.gain.setValueAtTime(0.035, 0);
        osc.connect(g);
        g.connect(offMaster);
        osc.start(0);
        osc.stop(durationSec);
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

    // === 1. QUANTUM POTENTIAL-WELL TERRAIN ===
    const terrainGeo = new THREE.PlaneGeometry(640, 640, 96, 96);
    terrainGeo.rotateX(-Math.PI / 2);
    const tPos = terrainGeo.attributes.position;
    for (let i = 0; i < tPos.count; i++) {
      const x = tPos.getX(i), z = tPos.getZ(i);
      let y = Math.sin(x * 0.012) * Math.cos(z * 0.012) * 16.0 + Math.sin(x * 0.035) * 4.0;
      // Superpose 64 Gaussian potential wells into the terrain
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
    const terrainMesh = new THREE.Mesh(terrainGeo, new THREE.MeshStandardMaterial({
      color: 0x111827, roughness: 0.85, metalness: 0.2
    }));
    terrainMesh.receiveShadow = true;
    scene.add(terrainMesh);

    // Grid matrix overlay
    const grid = new THREE.GridHelper(560, 8, 0xffd700, 0x334155);
    grid.position.y = 0.6;
    scene.add(grid);

    // === 1B. MASTER 3D CENTRIPETAL EGG RESONATOR MESH ENCLOSURE ===
    const eggGeo = new THREE.SphereGeometry(340, 48, 36);
    const eggPosAttr = eggGeo.attributes.position;
    for (let i = 0; i < eggPosAttr.count; i++) {
      const y = eggPosAttr.getY(i);
      const normY = y / 340.0;
      // Schauberger centripetal egg contour (tapered top, wider bottom)
      const eggContour = 1.0 + 0.25 * (1.0 - normY) * Math.cos(normY * Math.PI * 0.5);
      eggPosAttr.setX(i, eggPosAttr.getX(i) * eggContour);
      eggPosAttr.setZ(i, eggPosAttr.getZ(i) * eggContour);
    }
    eggGeo.computeVertexNormals();

    const masterEggMesh = new THREE.Mesh(eggGeo, new THREE.MeshStandardMaterial({
      color: 0x8b5cf6,
      emissive: 0x6d28d9,
      emissiveIntensity: 0.35,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
      roughness: 0.2
    }));
    masterEggMesh.position.set(0, 40, 0);
    masterEggMesh.userData = { isMasterEgg: true, name: 'Master Centripetal Egg Vortex' };
    scene.add(masterEggMesh);

    // === 2. SOVEREIGN NODES: VORTEX + PELLETS + POROSITY + ROSE CORES ===
    const nodeGroup = new THREE.Group();
    const animatedNodes = [];
    const raycastTargets = [masterEggMesh];
    const attractorBeams = [];
    const eggCenter = new THREE.Vector3(0, 40, 0);

    worldData.sectors.forEach((sec, sIdx) => {
      const group = new THREE.Group();
      group.position.set(sec.world_position.x, sec.world_position.y, sec.world_position.z);
      const qp = sec.quantum_physics;
      const uIdx = sec.grid_coordinates.col + 1;
      const lIdx = sec.grid_coordinates.row + 1;

      // --- A. Schauberger Centripetal Implosion Vortex Spiral ---
      const vCount = 120;
      const vGeo = new THREE.BufferGeometry();
      const vPos = new Float32Array(vCount * 3);
      const vCol = new Float32Array(vCount * 3);
      const vBase = new THREE.Color(sec.regional_biome.accent);
      for (let p = 0; p < vCount; p++) {
        const t = p / vCount;
        const theta = t * Math.PI * 8.0;
        const r = (1.0 - t) * 14.0 * (1.0 + qp.vortex_tension);
        vPos[p*3]   = Math.cos(theta) * r;
        vPos[p*3+1] = -(t) * qp.implosion_funnel_depth + 6.0;
        vPos[p*3+2] = Math.sin(theta) * r;
        vCol[p*3] = vBase.r; vCol[p*3+1] = vBase.g; vCol[p*3+2] = vBase.b;
      }
      vGeo.setAttribute('position', new THREE.BufferAttribute(vPos, 3));
      vGeo.setAttribute('color', new THREE.BufferAttribute(vCol, 3));
      const vortex = new THREE.Points(vGeo, new THREE.PointsMaterial({
        size: 1.8, vertexColors: true, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending
      }));
      group.add(vortex);

      // --- B. Volumetric Porosity Resonance Shell ---
      const pShell = new THREE.Mesh(
        new THREE.SphereGeometry(qp.porosity_cloud_radius * 0.7, 16, 16),
        new THREE.MeshBasicMaterial({
          color: new THREE.Color(sec.regional_biome.color),
          wireframe: true, transparent: true,
          opacity: Math.max(0.12, qp.porosity_level * 0.35)
        })
      );
      pShell.position.y = 8;
      group.add(pShell);

      // --- C. Parametric Rose-Curve Avatar Core (Lissajous) ---
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
      group.add(roseMesh);

      // --- Central Sovereign Beacon ---
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

      // --- D. 6-Yao Line Quantum Orbiting Pellets ---
      const pelletMeshes = [];
      sec.yao_pellets.forEach((yp, pIdx) => {
        const rad = yp.ternary_state === 2 ? 1.1 : (yp.ternary_state === 1 ? 0.9 : 0.65);
        const geo = yp.ternary_state === 2 ? new THREE.IcosahedronGeometry(rad, 1) : new THREE.SphereGeometry(rad, 12, 12);
        const pm = new THREE.Mesh(
          geo,
          new THREE.MeshStandardMaterial({
            color: new THREE.Color(yp.color_hex),
            emissive: new THREE.Color(yp.color_hex),
            emissiveIntensity: yp.energy_intensity * 0.8,
            roughness: 0.25,
            wireframe: yp.ternary_state === 2
          })
        );
        group.add(pm);
        pelletMeshes.push({ mesh: pm, spec: yp, angle: pIdx * (Math.PI / 3.0) });
      });

      animatedNodes.push({
        group, vortex, porosity: pShell, rose: roseMesh,
        beacon, pellets: pelletMeshes, vortexTension: qp.vortex_tension
      });
      nodeGroup.add(group);
    });
    scene.add(nodeGroup);

    // === 2B. 64 CENTRIPETAL ATTRACTOR ENERGY BEAMS (ATTRACTING ALL 64 TO MASTER EGG) ===
    worldData.sectors.forEach((sec, sIdx) => {
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
        document.getElementById('val-action').innerText =
          d.action_doctrine + ' (' + d.citadel_archetype + ')';
        const ds = d.quantum_physics.depth_statistics || {};
        document.getElementById('val-depth').innerText =
          'Mean: ' + (ds.mean_depth || 10.0) + 'm (Range: ' + (ds.min_depth || 0) + '..' + (ds.max_depth || 20) + 'm) | ' + (d.quantum_physics.depth_pointcloud_vertices || 122150) + ' pts';
        
        const sc = d.spectral_color || { hex: '#FFD700', name: 'Spectral' };
        const hueDeg = d.base_hue_degrees !== undefined ? Number(d.base_hue_degrees).toFixed(1) : '0.0';
        document.getElementById('spectral-badge').style.background = sc.hex;
        document.getElementById('spectral-badge').style.boxShadow = '0 0 8px ' + sc.hex;
        document.getElementById('spectral-text').innerText = sc.hex + ' (' + hueDeg + '\u00B0) \u2014 ' + (sc.name || 'Spectral Hue');

        const freqs = d.yao_pellets.map(yp => yp.frequency_hz + 'Hz').join(', ');
        const cutoff = Math.round(400 + (d.quantum_physics.porosity_level || 0.45) * 3200);
        document.getElementById('val-audio').innerText = `Harmonics: [${freqs}] | Cutoff: ${cutoff}Hz`;

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

      if (typeof masterEggMesh !== 'undefined' && masterEggMesh) {
        masterEggMesh.visible = centripetalEggActive;
        if (centripetalEggActive) {
          masterEggMesh.rotation.y += 0.005 * timeSpeed;
          const masterPulse = 1.0 + 0.05 * Math.sin(presentTime * 2.0);
          masterEggMesh.scale.set(masterPulse, 1.0 + 0.08 * Math.cos(presentTime * 1.5), masterPulse);
        }
      }

      animatedNodes.forEach((n, nIdx) => {
        const sec = worldData.sectors[nIdx];
        const pos = sec.world_position;

        let spinSpeed = 0.03 * (1.0 + n.vortexTension * 2.0);
        let pulse = 1.0 + Math.sin(clock * 1.5 + nIdx) * 0.06;

        // === CENTRIPETAL EGG GENERATION FROM PRESENT TIME (ALL 64 UNISON) ===
        if (centripetalEggActive) {
          const eggPhase = presentTime * 2.5 + (pos.x * 0.01 + pos.z * 0.01);
          const eggFactor = 1.0 + 0.35 * Math.sin(eggPhase);

          if (attractorMode === 'implosion') {
            // Schauberger Implosion Funnel Egg: Contract and accelerate inward toward (x, y, z)
            spinSpeed *= (1.8 + 0.9 * Math.sin(presentTime * 3.0 + nIdx * 0.1));
            pulse *= (0.85 + 0.35 * Math.sin(eggPhase));
            n.vortex.scale.set(eggFactor * 0.9, 1.0 + 0.5 * Math.sin(presentTime * 2.0), eggFactor * 0.9);
          } else if (attractorMode === 'toroidal') {
            // Toroidal Egg Oscillation: Breathing torus field
            const torusPulse = 1.0 + 0.4 * Math.sin(presentTime * 4.0 + nIdx * 0.2);
            n.porosity.scale.set(torusPulse, torusPulse * 1.25, torusPulse);
            n.vortex.rotation.z = Math.sin(presentTime * 1.5 + nIdx * 0.1) * 0.3;
          } else if (attractorMode === 'unison_resonance') {
            // 64-Unison Audio Pellet Resonance: High-frequency synchronous vortex spin
            spinSpeed *= 2.8;
            pulse = 1.0 + 0.25 * Math.sin(presentTime * 6.0);
          }

          // Implosion orbital physics for 6-yao sound pellets
          n.pellets.forEach((p, pIdx) => {
            const pelletPhase = p.angle + presentTime * p.spec.orbital_speed * 1.5;
            const implosionRadius = p.spec.orbit_radius * (0.60 + 0.40 * Math.sin(presentTime * 2.5 + pIdx * 0.5));
            p.mesh.position.x = Math.cos(pelletPhase) * implosionRadius;
            p.mesh.position.z = Math.sin(pelletPhase) * implosionRadius;
            p.mesh.position.y = 8.0 + Math.sin(pelletPhase * 2.0 + presentTime * 3.0) * 2.2;
            if (p.spec.ternary_state === 2) {
              p.mesh.rotation.x += 0.08;
              p.mesh.rotation.y += 0.08;
            }
          });
        } else {
          // Standard Orbiting Pellets
          n.pellets.forEach(p => {
            p.angle += p.spec.orbital_speed * 0.03;
            p.mesh.position.x = Math.cos(p.angle) * p.spec.orbit_radius;
            p.mesh.position.z = Math.sin(p.angle) * p.spec.orbit_radius;
            p.mesh.position.y = 8.0 + Math.sin(p.angle * 2.0 + clock) * 1.8;
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
          let spatialAtten = Math.min(0.045, 0.05 / (1.0 + Math.pow(dist / 95.0, 2)));

          if (centripetalEggActive) {
            // Modulate spatial frequency & gain in unison across all 64 nodes from present time
            const eggOsc = 1.0 + 0.12 * Math.sin(presentTime * 3.0 + gv.hexId * 0.1);
            gv.osc.frequency.setTargetAtTime(gv.fundamentalFreq * eggOsc, now, 0.04);
            if (attractorMode === 'unison_resonance') {
              spatialAtten *= 1.8; // Boost unison pellet resonance gain
            }
          }
          gv.gain.gain.setTargetAtTime(spatialAtten, now, 0.05);
        });
      }

      renderer.render(scene, camera);
    }
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
