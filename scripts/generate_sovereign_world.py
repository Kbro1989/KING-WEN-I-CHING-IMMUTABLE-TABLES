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

            # 6-Yao Line Quantum Pellets (L1 to L6) — Full Ternary Resolution (0=Yin, 1=Yang, 2=Yao/Changing)
            COPRIME_BASE_FREQS = [146.0, 158.0, 166.0, 178.0, 194.0, 206.0]
            yao_pellets = []
            for line_idx in range(6):
                bit = int(binary_str[line_idx]) if line_idx < len(binary_str) else 1
                # Check for temporal phase changing line modulation (ternary state 2 = yao)
                is_changing = (biome_id in [3, 4]) and ((line_idx % 3) == (biome_id % 3))
                ternary_state = 2 if is_changing else (1 if bit == 1 else 0)

                orbit_radius = round(6.0 + line_idx * 2.2, 2)
                orbital_speed = round(0.5 + (line_idx + 1) * 0.25 * (1.0 + vortex_tension) * (1.2 if ternary_state == 2 else 1.0), 3)

                if ternary_state == 1:
                    line_type = "yang"
                    color_hex = "#FFD700"
                    energy = 1.0
                    freq_hz = round(COPRIME_BASE_FREQS[line_idx] * (1.0 + vortex_tension * 0.25), 2)
                elif ternary_state == 0:
                    line_type = "yin"
                    color_hex = "#38BDF8"
                    energy = 0.6
                    freq_hz = round(COPRIME_BASE_FREQS[line_idx] * 0.82 * (1.0 + vortex_tension * 0.25), 2)
                else:
                    line_type = "yao"
                    color_hex = "#A855F7"
                    energy = 1.4
                    freq_hz = round(COPRIME_BASE_FREQS[line_idx] * 1.18 * (1.0 + vortex_tension * 0.25), 2)

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

            # Load Deterministic Spectral Color Map from Kit
            kit_path = ROOT / "DATASETS" / "kingwen_model_sets" / f"kit_{h_id}.json"
            k_color = {}
            if kit_path.exists():
                try:
                    k_color = json.loads(kit_path.read_text(encoding="utf-8")).get("grounded_npc", {}).get("k_color_map", {})
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
    doc = "Master 64-Sovereign Macro World: 8 Biomes, Schauberger Vortices, 6-Yao Pellets, 64 Citadels"
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
    .rec-btn {
      background: #1e293b; color: #f59e0b; border: 1px solid #f59e0b; padding: 5px 10px;
      border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; transition: all 0.2s ease;
    }
    .rec-btn:hover { background: #f59e0b; color: #0f172a; }
    .sw-pill {
      background: #0f172a; color: #94a3b8; border: 1px solid rgba(255,255,255,0.15); padding: 2px 6px;
      border-radius: 4px; font-size: 10px; cursor: pointer; font-weight: 600; transition: all 0.15s ease;
    }
    .sw-pill:hover { background: #334155; color: #fff; border-color: #38bdf8; }
    .line-card-grid {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 8px;
    }
    .line-card {
      background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px;
      padding: 6px 8px; display: flex; flex-direction: column; gap: 4px; transition: all 0.2s ease;
    }
    .line-card.muted { opacity: 0.45; border-color: rgba(239, 68, 68, 0.4); }
    .line-card-header { display: flex; justify-content: space-between; align-items: center; font-size: 10px; }
    .card-toggle-btn {
      background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 2px 6px;
      border-radius: 4px; font-size: 9px; font-weight: 700; cursor: pointer; text-align: center;
    }
    .card-toggle-btn.off { background: #334155; color: #ef4444; border-color: #ef4444; }
    .citadel-matrix-grid {
      display: grid; grid-template-columns: repeat(8, 1fr); gap: 3px; margin-top: 6px; max-height: 110px; overflow-y: auto; padding-right: 2px;
    }
    .citadel-chip {
      background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.12); border-radius: 4px;
      padding: 3px 2px; text-align: center; font-size: 8.5px; cursor: pointer; transition: all 0.15s ease;
      display: flex; flex-direction: column; align-items: center; gap: 1px; color: #cbd5e1;
    }
    .citadel-chip:hover { border-color: #38bdf8; background: #1e293b; color: #fff; }
    .citadel-chip.active { border-color: #38bdf8; box-shadow: 0 0 5px rgba(56,189,248,0.4); }
    .citadel-chip.muted { opacity: 0.35; border-color: rgba(239,68,68,0.3); color: #64748b; }
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
      <button class="audio-btn" id="audio-toggle" onclick="toggleAudio()">&#x1F50A; Master Audio: OFF</button>
      <select id="audio-mode-select" class="audio-select" onchange="changeAudioMode()">
        <option value="field">&#x1F30C; 64-Hex Spatial Superposition</option>
        <option value="hover">&#x1F3AF; Focus / Hover Node Only</option>
        <option value="arpeggio">&#x26A1; 6-Yao Arpeggiator Sweep</option>
        <option value="binaural">&#x262F;&#xFE0F; Yin/Yang Binaural Carrier</option>
        <option value="changing">&#x1F52E; Changing Yao (State 2) Only</option>
      </select>
      <button class="audio-btn" id="toggle-all-lines" onclick="toggleAllLines()" style="border-color:#a855f7;color:#a855f7;">&#x26A1; All Lines: ON</button>
      <a href="kingwen_external_audio_switchboard.html" target="_blank" class="audio-btn" style="text-decoration:none;border-color:#f59e0b;color:#f59e0b;">&#x1F39B;&#xFE0F; Studio Console</a>
      <button class="rec-btn" id="record-btn" onclick="recordAudioSample()">&#x1F399;&#xFE0F; Sample WAV</button>
    </div>
    <div id="inspector">
      <div class="inspect-name" id="sel-name">Hover over any Sovereign Node</div>
      <div class="inspect-grid" id="sel-grid">
        <div class="inspect-cell"><div class="inspect-label">Regional Biome</div><span id="val-biome">All 8 Sectors Active</span></div>
        <div class="inspect-cell"><div class="inspect-label">Action &amp; Archetype</div><span id="val-action">Superposition Field</span></div>
        <div class="inspect-cell" style="grid-column: span 2;"><div class="inspect-label">DA-V2 Metric Depth &amp; Point Cloud</div><span id="val-depth">Mean: 10.0m | 122,150 vertices</span></div>
        <div class="inspect-cell" style="grid-column: span 2;"><div class="inspect-label">Deterministic Spectral Hue (6-Bit Embodiment)</div><span id="val-spectral" style="display:flex;align-items:center;gap:6px;"><span id="spectral-badge" style="width:12px;height:12px;border-radius:3px;background:#FFD700;display:inline-block;box-shadow:0 0 6px rgba(255,215,0,0.6);"></span> <span id="spectral-text">#FFD700 (0.0&deg;)</span></span></div>
        <div class="inspect-cell" style="grid-column: span 2;"><div class="inspect-label">6-Yao Acoustic Harmonics &amp; Filter</div><span id="val-audio">Harmonics: Hover Node | Cutoff: --</span></div>
      </div>

      <!-- 64-Citadel Spatial Superposition Matrix Switchboard -->
      <div id="citadel-matrix-box" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 4px;">
          <div style="font-size: 11px; font-weight: 700; color: #FFD700; text-transform: uppercase; letter-spacing: 0.5px;">&#x1F30C; 64-Citadel Spatial Matrix (<span id="citadel-active-count">64/64 ON</span>)</div>
          <div style="display: flex; gap: 3px; flex-wrap: wrap;">
            <button onclick="filterCitadels('all')" class="sw-pill">All 64</button>
            <button onclick="filterCitadels('Qian')" class="sw-pill">Qian</button>
            <button onclick="filterCitadels('Kun')" class="sw-pill">Kun</button>
            <button onclick="filterCitadels('Zhen')" class="sw-pill">Zhen</button>
            <button onclick="filterCitadels('Kan')" class="sw-pill">Kan</button>
            <button onclick="filterCitadels('Li')" class="sw-pill">Li</button>
            <button onclick="filterCitadels('Xun')" class="sw-pill">Xun</button>
            <button onclick="filterCitadels('Gen')" class="sw-pill">Gen</button>
            <button onclick="filterCitadels('Dui')" class="sw-pill">Dui</button>
            <button onclick="filterCitadels('mute')" class="sw-pill" style="color:#ef4444;">Mute All</button>
          </div>
        </div>
        <div class="citadel-matrix-grid" id="citadel-matrix-container"></div>
      </div>

      <!-- 6-Yao Line Channel Switchboard -->
      <div id="audio-switchboard" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;">&#x1F39B;&#xFE0F; Focused 6-Yao Line Switchboard</div>
          <div style="display: flex; gap: 4px;">
            <button onclick="filterLines('all')" class="sw-pill">All</button>
            <button onclick="filterLines('upper')" class="sw-pill">Upper (L4-6)</button>
            <button onclick="filterLines('lower')" class="sw-pill">Lower (L1-3)</button>
            <button onclick="filterLines('changing')" class="sw-pill">Yao (2)</button>
            <button onclick="filterLines('mute')" class="sw-pill" style="color:#ef4444;">Mute All</button>
          </div>
        </div>
        <div class="line-card-grid" id="line-cards-container"></div>
      </div>
    </div>
  </div>
  <div id="instructions">&#x1F5B1;&#xFE0F; Left Click + Drag: Orbit | Scroll: Zoom | Hover: Live Node Telemetry &amp; Acoustic Harmonics</div>

  <script>
    // === DATA INGESTION ===
    const worldData = __WORLD_JSON_PLACEHOLDER__;

    // === WEB AUDIO API 64-NODE SPATIAL HARMONIC SUPERPOSITION ENGINE ===
    let audioCtx = null;
    let audioEnabled = false;
    let oscillators = [];
    let oscGains = [];
    let spatialVoices = [];
    let masterFilter = null;
    let masterGain = null;
    let activeHexData = null;
    let lineMuteState = [true, true, true, true, true, true];
    let citadelMuteState = Array(64).fill(true);
    let currentAudioMode = 'field';
    let allLinesActive = true;
    let arpIndex = 0;

    function initAudio() {
      if (audioCtx) return;
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();

      masterGain = audioCtx.createGain();
      masterGain.gain.setValueAtTime(0.0, audioCtx.currentTime);

      masterFilter = audioCtx.createBiquadFilter();
      masterFilter.type = 'lowpass';
      masterFilter.frequency.setValueAtTime(1400, audioCtx.currentTime);
      masterFilter.Q.setValueAtTime(3.5, audioCtx.currentTime);

      masterGain.connect(masterFilter);
      masterFilter.connect(audioCtx.destination);

      // 1. Focus Node 6-Yao Harmonic Oscillators
      for (let i = 0; i < 6; i++) {
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = (i % 2 === 0) ? 'triangle' : 'sine';
        osc.frequency.setValueAtTime(146.0 * (1.0 + i * 0.15), audioCtx.currentTime);
        g.gain.setValueAtTime(0.0, audioCtx.currentTime);
        osc.connect(g);
        g.connect(masterGain);
        osc.start();
        oscillators.push(osc);
        oscGains.push(g);
      }

      // 2. Continuous 64-Citadel Spatial Superposition Field Voices
      if (worldData.sectors) {
        worldData.sectors.forEach((sec, sIdx) => {
          const sOsc = audioCtx.createOscillator();
          const sGain = audioCtx.createGain();
          const sFilter = audioCtx.createBiquadFilter();

          const baseFreq = 108.0 + (sec.hexagram_id - 1) * 2.45;
          sOsc.type = (sec.hexagram_id % 3 === 0) ? 'triangle' : ((sec.hexagram_id % 2 === 0) ? 'sine' : 'sawtooth');
          sOsc.frequency.setValueAtTime(baseFreq, audioCtx.currentTime);

          sFilter.type = 'lowpass';
          const qp = sec.quantum_physics || {};
          sFilter.frequency.setValueAtTime(350 + (qp.porosity_level || 0.45) * 1800, audioCtx.currentTime);
          sFilter.Q.setValueAtTime(1.5 + (qp.vortex_tension || 0.5) * 2.5, audioCtx.currentTime);

          sGain.gain.setValueAtTime(0.0, audioCtx.currentTime);

          sOsc.connect(sFilter);
          sFilter.connect(sGain);
          sGain.connect(masterGain);
          sOsc.start();

          spatialVoices.push({
            hexId: sec.hexagram_id,
            sector: sec,
            pos3D: new THREE.Vector3(sec.world_position.x, sec.world_position.y, sec.world_position.z),
            osc: sOsc,
            filter: sFilter,
            gain: sGain,
            baseFreq: baseFreq
          });
        });
      }

      renderCitadelMatrix();
    }

    function toggleAudio() {
      initAudio();
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      audioEnabled = !audioEnabled;
      const btn = document.getElementById('audio-toggle');
      if (audioEnabled) {
        btn.innerText = '🔊 Master Audio: ON';
        btn.style.background = '#38bdf8';
        btn.style.color = '#0f172a';
        masterGain.gain.setTargetAtTime(0.28, audioCtx.currentTime, 0.05);
        if (activeHexData) {
          playHexHarmonics(activeHexData);
        } else if (worldData.sectors && worldData.sectors[0]) {
          playHexHarmonics(worldData.sectors[0]);
        }
      } else {
        btn.innerText = '🔊 Master Audio: OFF';
        btn.style.background = '#1e293b';
        btn.style.color = '#38bdf8';
        masterGain.gain.setTargetAtTime(0.0, audioCtx.currentTime, 0.05);
      }
    }

    function changeAudioMode() {
      currentAudioMode = document.getElementById('audio-mode-select').value;
      if (activeHexData) playHexHarmonics(activeHexData);
    }

    function renderCitadelMatrix() {
      const container = document.getElementById('citadel-matrix-container');
      if (!container || !worldData.sectors) return;
      let html = '';
      let activeCount = 0;
      worldData.sectors.forEach((sec, idx) => {
        const isActive = citadelMuteState[idx];
        if (isActive) activeCount++;
        const sc = sec.spectral_color || { hex: '#FFD700' };
        html += `
          <div class="citadel-chip ${isActive ? 'active' : 'muted'}" onclick="toggleCitadel(${idx})" title="Hex #${sec.hexagram_id} ${sec.hexagram_name} (${sec.upper_trigram}/${sec.lower_trigram})">
            <span style="width:6px;height:6px;border-radius:50%;background:${sc.hex};display:inline-block;"></span>
            <span style="font-weight:700;">#${sec.hexagram_id}</span>
            <span style="font-size:7px;">${sec.hanzi}</span>
          </div>
        `;
      });
      container.innerHTML = html;
      const countEl = document.getElementById('citadel-active-count');
      if (countEl) countEl.innerText = `${activeCount}/64 ON`;
    }

    function toggleCitadel(idx) {
      citadelMuteState[idx] = !citadelMuteState[idx];
      renderCitadelMatrix();
    }

    function filterCitadels(tri) {
      if (!worldData.sectors) return;
      worldData.sectors.forEach((sec, idx) => {
        if (tri === 'all') {
          citadelMuteState[idx] = true;
        } else if (tri === 'mute') {
          citadelMuteState[idx] = false;
        } else {
          citadelMuteState[idx] = (sec.upper_trigram === tri || sec.lower_trigram === tri);
        }
      });
      renderCitadelMatrix();
    }

    function toggleLineAudio(idx) {
      lineMuteState[idx] = !lineMuteState[idx];
      if (activeHexData) {
        renderLineCards(activeHexData);
        playHexHarmonics(activeHexData);
      }
    }

    function toggleAllLines() {
      allLinesActive = !allLinesActive;
      lineMuteState = [allLinesActive, allLinesActive, allLinesActive, allLinesActive, allLinesActive, allLinesActive];
      const btn = document.getElementById('toggle-all-lines');
      btn.innerText = allLinesActive ? '⚡ All Lines: ON' : '🔇 All Lines: MUTED';
      btn.style.color = allLinesActive ? '#a855f7' : '#ef4444';
      btn.style.borderColor = allLinesActive ? '#a855f7' : '#ef4444';
      if (activeHexData) {
        renderLineCards(activeHexData);
        playHexHarmonics(activeHexData);
      }
    }

    function filterLines(type) {
      if (type === 'all') {
        lineMuteState = [true, true, true, true, true, true];
      } else if (type === 'upper') {
        lineMuteState = [false, false, false, true, true, true];
      } else if (type === 'lower') {
        lineMuteState = [true, true, true, false, false, false];
      } else if (type === 'changing') {
        if (activeHexData) {
          lineMuteState = activeHexData.yao_pellets.map(yp => yp.ternary_state === 2);
        } else {
          lineMuteState = [false, false, false, true, false, false];
        }
      } else if (type === 'mute') {
        lineMuteState = [false, false, false, false, false, false];
      }
      if (activeHexData) {
        renderLineCards(activeHexData);
        playHexHarmonics(activeHexData);
      }
    }

    function renderLineCards(d) {
      const container = document.getElementById('line-cards-container');
      if (!container || !d.yao_pellets) return;
      let html = '';
      d.yao_pellets.forEach((yp, idx) => {
        const isMuted = !lineMuteState[idx];
        const stateColor = yp.color_hex;
        const stateName = yp.ternary_state === 2 ? 'YAO 2' : (yp.ternary_state === 1 ? 'YANG 1' : 'YIN 0');
        html += `
          <div class="line-card ${isMuted ? 'muted' : ''}">
            <div class="line-card-header">
              <span style="font-weight:700;color:#fff;">L${yp.line_position} <span style="font-size:9px;color:#94a3b8;">(${yp.sub_trigram[0].toUpperCase()}${yp.sub_position})</span></span>
              <span style="background:${stateColor};color:#0f172a;font-size:8px;font-weight:800;padding:1px 4px;border-radius:3px;">${stateName}</span>
            </div>
            <div style="font-size:10px;color:#cbd5e1;font-family:monospace;">${yp.frequency_hz}Hz</div>
            <button class="card-toggle-btn ${isMuted ? 'off' : ''}" onclick="toggleLineAudio(${idx})">
              ${isMuted ? '🔇 MUTED' : '🔊 LIVE'}
            </button>
          </div>
        `;
      });
      container.innerHTML = html;
    }

    function playHexHarmonics(d) {
      activeHexData = d;
      renderLineCards(d);
      if (!audioEnabled || !audioCtx) return;
      const now = audioCtx.currentTime;
      masterGain.gain.setTargetAtTime(0.24, now, 0.05);

      const qp = d.quantum_physics || {};
      const porosity = qp.porosity_level || 0.45;
      const vortex = qp.vortex_tension || 0.5;

      const cutoff = 400 + porosity * 3200;
      masterFilter.frequency.setTargetAtTime(cutoff, now, 0.06);
      masterFilter.Q.setTargetAtTime(2.0 + vortex * 4.0, now, 0.06);

      d.yao_pellets.forEach((yp, idx) => {
        if (oscillators[idx]) {
          const isMuted = !lineMuteState[idx];
          if (isMuted) {
            oscGains[idx].gain.setTargetAtTime(0.0, now, 0.03);
            return;
          }

          let targetFreq = yp.frequency_hz || (146.0 + idx * 20.0);
          if (currentAudioMode === 'binaural') {
            targetFreq = yp.ternary_state === 1 ? (150.0 + idx * 12.0) : (144.0 + idx * 12.0);
          } else if (currentAudioMode === 'changing' && yp.ternary_state !== 2) {
            oscGains[idx].gain.setTargetAtTime(0.0, now, 0.03);
            return;
          }

          oscillators[idx].frequency.setTargetAtTime(targetFreq, now, 0.05);
          if (yp.ternary_state === 2) {
            oscillators[idx].type = 'sawtooth';
            oscGains[idx].gain.setTargetAtTime(0.18, now, 0.05);
          } else if (yp.ternary_state === 1) {
            oscillators[idx].type = 'triangle';
            oscGains[idx].gain.setTargetAtTime(0.14, now, 0.05);
          } else {
            oscillators[idx].type = 'sine';
            oscGains[idx].gain.setTargetAtTime(0.10, now, 0.05);
          }
        }
      });
    }

    function recordAudioSample() {
      if (!activeHexData) {
        alert('Hover over any Sovereign Citadel node first to sample its live harmonic field!');
        return;
      }
      const d = activeHexData;
      const sampleRate = 44100;
      const durationSec = 3.0;
      const numSamples = Math.floor(sampleRate * durationSec);
      const offlineCtx = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(2, numSamples, sampleRate);

      const offMaster = offlineCtx.createGain();
      offMaster.gain.setValueAtTime(0.25, 0);

      const offFilter = offlineCtx.createBiquadFilter();
      offFilter.type = 'lowpass';
      const qp = d.quantum_physics || {};
      offFilter.frequency.setValueAtTime(400 + (qp.porosity_level || 0.45) * 3200, 0);
      offFilter.Q.setValueAtTime(2.0 + (qp.vortex_tension || 0.5) * 4.0, 0);

      offMaster.connect(offFilter);
      offFilter.connect(offlineCtx.destination);

      d.yao_pellets.forEach((yp, idx) => {
        if (!lineMuteState[idx]) return;
        const osc = offlineCtx.createOscillator();
        const g = offlineCtx.createGain();
        osc.type = yp.ternary_state === 2 ? 'sawtooth' : (yp.ternary_state === 1 ? 'triangle' : 'sine');
        osc.frequency.setValueAtTime(yp.frequency_hz || (146.0 + idx * 20.0), 0);
        g.gain.setValueAtTime(yp.ternary_state === 2 ? 0.2 : (yp.ternary_state === 1 ? 0.15 : 0.10), 0);
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
        a.download = `kingwen_hex_${d.hexagram_id.toString().padStart(2, '0')}_${d.name.replace(/\\s+/g, '_')}_sound.wav`;
        a.click();
        URL.revokeObjectURL(url);
      });
    }

    function audioBufferToWavBlob(buffer) {
      const numChannels = buffer.numberOfChannels;
      const sampleRate = buffer.sampleRate;
      const format = 1;
      const bitDepth = 16;
      const bytesPerSample = bitDepth / 8;
      const blockAlign = numChannels * bytesPerSample;
      const length = buffer.length;
      const bufferLen = 44 + length * blockAlign;
      const out = new DataView(new ArrayBuffer(bufferLen));

      function writeString(view, offset, str) {
        for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
      }

      writeString(out, 0, 'RIFF');
      out.setUint32(4, 36 + length * blockAlign, true);
      writeString(out, 8, 'WAVE');
      writeString(out, 12, 'fmt ');
      out.setUint32(16, 16, true);
      out.setUint16(20, format, true);
      out.setUint16(22, numChannels, true);
      out.setUint32(24, sampleRate, true);
      out.setUint32(28, sampleRate * blockAlign, true);
      out.setUint16(32, blockAlign, true);
      out.setUint16(34, bitDepth, true);
      writeString(out, 36, 'data');
      out.setUint32(40, length * blockAlign, true);

      let offset = 44;
      const channels = [];
      for (let c = 0; c < numChannels; c++) channels.push(buffer.getChannelData(c));

      for (let i = 0; i < length; i++) {
        for (let c = 0; c < numChannels; c++) {
          let s = Math.max(-1, Math.min(1, channels[c][i]));
          s = s < 0 ? s * 0x8000 : s * 0x7FFF;
          out.setInt16(offset, s, true);
          offset += 2;
        }
      }
      return new Blob([out], { type: 'audio/wav' });
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

    // === 2. SOVEREIGN NODES: VORTEX + PELLETS + POROSITY + ROSE CORES ===
    const nodeGroup = new THREE.Group();
    const animatedNodes = [];
    const raycastTargets = [];

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

    // === RAYCASTING INTERACTION ===
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    window.addEventListener('mousemove', (e) => {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(raycastTargets);
      if (hits.length > 0) {
        const d = hits[0].object.userData;
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
      controls.update();

      animatedNodes.forEach((n, nIdx) => {
        // Spin Schauberger centripetal vortex
        n.vortex.rotation.y += 0.03 * (1.0 + n.vortexTension * 2.0);

        // Pulsate porosity shell
        const pulse = 1.0 + Math.sin(clock * 1.5 + nIdx) * 0.06;
        n.porosity.scale.set(pulse, pulse, pulse);
        n.porosity.rotation.y -= 0.005;

        // Rotate rose-curve avatar core
        n.rose.rotation.y += 0.015;
        n.rose.rotation.z = Math.sin(clock + nIdx) * 0.1;

        // Beacon float
        n.beacon.rotation.y += 0.02;
        n.beacon.position.y = 8 + Math.sin(clock * 2 + nIdx) * 1.0;

        // 6-Yao Line Orbiting Pellets
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
      });

      // === 64-CITADEL SPATIAL AUDIO SUPERPOSITION FIELD UPDATE ===
      if (audioEnabled && audioCtx && spatialVoices.length > 0) {
        const camPos = camera.position;
        const isFieldMode = (currentAudioMode === 'field' || currentAudioMode === 'binaural');
        const now = audioCtx.currentTime;

        spatialVoices.forEach((sv, idx) => {
          const isCitadelActive = citadelMuteState[idx];
          if (!isCitadelActive || !isFieldMode) {
            sv.gain.gain.setTargetAtTime(0.0, now, 0.04);
            return;
          }
          const dist = camPos.distanceTo(sv.pos3D);
          // Inverse square distance attenuation with soft roll-off
          const spatialAtten = Math.min(0.045, 0.05 / (1.0 + Math.pow(dist / 95.0, 2)));
          sv.gain.gain.setTargetAtTime(spatialAtten, now, 0.05);
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
