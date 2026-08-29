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

            elevation = round(
                math.sin(col * 0.8) * math.cos(row * 0.8) * 14.0
                + (u_idx * 2.5) + (l_idx * 1.5), 2
            )
            row_heights.append(elevation)

            biome_id = row
            biome = temporal_biomes[biome_id]

            # 6-Yao Line Quantum Pellets (L1 to L6)
            yao_pellets = []
            for line_idx in range(6):
                bit = int(binary_str[line_idx]) if line_idx < len(binary_str) else 1
                orbit_radius = round(6.0 + line_idx * 2.2, 2)
                orbital_speed = round(0.5 + (line_idx + 1) * 0.25 * (1.0 + vortex_tension), 3)
                yao_pellets.append({
                    "line_position": line_idx + 1,
                    "line_type": "yang" if bit == 1 else "yin",
                    "orbit_radius": orbit_radius,
                    "orbital_speed": orbital_speed,
                    "color_hex": "#FFD700" if bit == 1 else "#38BDF8",
                    "energy_intensity": 1.0 if bit == 1 else 0.6
                })

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
                "quantum_physics": {
                    "vortex_tension": vortex_tension,
                    "suction_coefficient": suction_coeff,
                    "porosity_level": porosity_level,
                    "implosion_funnel_depth": round(vortex_tension * 18.0, 2),
                    "porosity_cloud_radius": round(12.0 + porosity_level * 16.0, 2)
                },
                "yao_pellets": yao_pellets,
                "assets": {
                    "3d_mesh": f"DATASETS/kingwen_3d_meshes/shap_e_hex_{h_id:02d}.ply",
                    "openusd_stage": f"DATASETS/openusd_stages/npc_hex_{h_id:02d}.usda",
                    "godot_scene": f"DATASETS/godot_scenes/npc_hex_{h_id:02d}.tscn",
                    "rsmv_model": f"DATASETS/kingwen_rsmv_models/hex_{h_id:02d}_models.json",
                    "quantum_surface_plot": f"DATASETS/quantumlab_plots/quantum_3d_hex_{h_id:02d}.png"
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
    .legend { display: flex; gap: 12px; margin-top: 10px; font-size: 11px; }
    .leg-item { display: flex; align-items: center; gap: 5px; }
    .dot-gold { width: 8px; height: 8px; border-radius: 50%; background: #FFD700; box-shadow: 0 0 6px #FFD700; }
    .dot-blue { width: 8px; height: 8px; border-radius: 50%; background: #38BDF8; box-shadow: 0 0 6px #38BDF8; }
    .dot-purple { width: 8px; height: 8px; border-radius: 50%; background: #A855F7; }
    .dot-white { width: 8px; height: 8px; border-radius: 50%; background: #fff; border: 1px solid #888; }
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
    <div class="stat-row"><span>Vortex Physics:</span><span class="stat-val">Schauberger Centripetal Implosion</span></div>
    <div class="legend">
      <div class="leg-item"><div class="dot-gold"></div> Yang Pellet</div>
      <div class="leg-item"><div class="dot-blue"></div> Yin Pellet</div>
      <div class="leg-item"><div class="dot-purple"></div> Porosity Shell</div>
      <div class="leg-item"><div class="dot-white"></div> Rose-Curve Core</div>
    </div>
    <div id="inspector">
      <div class="inspect-name" id="sel-name">Hover over any Sovereign Node</div>
      <div class="inspect-grid" id="sel-grid">
        <div class="inspect-cell"><div class="inspect-label">Regional Biome</div><span id="val-biome">All 8 Sectors Active</span></div>
        <div class="inspect-cell"><div class="inspect-label">Action &amp; Archetype</div><span id="val-action">Superposition Field</span></div>
        <div class="inspect-cell"><div class="inspect-label">Schauberger Vortex</div><span id="val-vortex">&tau;: 0.02..1.0</span></div>
        <div class="inspect-cell"><div class="inspect-label">Porosity Window</div><span id="val-porosity">&Pi;: 0.15..0.70</span></div>
      </div>
      <div class="pellet-row" id="pellet-indicators"></div>
    </div>
  </div>
  <div id="instructions">&#x1F5B1;&#xFE0F; Left Click + Drag: Orbit | Scroll: Zoom | Right Click: Pan | Hover: Live Node Telemetry</div>

  <script>
    // === DATA INGESTION ===
    const worldData = __WORLD_JSON_PLACEHOLDER__;

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
      const roseMesh = new THREE.Line(rGeo, new THREE.LineBasicMaterial({
        color: 0xFFD700, transparent: true, opacity: 0.85
      }));
      group.add(roseMesh);

      // --- Central Sovereign Beacon ---
      const beacon = new THREE.Mesh(
        new THREE.OctahedronGeometry(2.5),
        new THREE.MeshStandardMaterial({
          color: 0xffd700, emissive: 0xd97706, emissiveIntensity: 0.6, roughness: 0.2
        })
      );
      beacon.position.y = 8;
      beacon.userData = sec;
      group.add(beacon);
      raycastTargets.push(beacon);

      // --- D. 6-Yao Line Quantum Orbiting Pellets ---
      const pelletMeshes = [];
      sec.yao_pellets.forEach((yp, pIdx) => {
        const pm = new THREE.Mesh(
          new THREE.SphereGeometry(yp.line_type === 'yang' ? 0.9 : 0.65, 12, 12),
          new THREE.MeshStandardMaterial({
            color: new THREE.Color(yp.color_hex),
            emissive: new THREE.Color(yp.color_hex),
            emissiveIntensity: yp.energy_intensity * 0.7,
            roughness: 0.3
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
        document.getElementById('val-vortex').innerText =
          '\u03C4: ' + d.quantum_physics.vortex_tension +
          ' (Depth: ' + d.quantum_physics.implosion_funnel_depth + 'm)';
        document.getElementById('val-porosity').innerText =
          '\u03A0: ' + d.quantum_physics.porosity_level +
          ' (R: ' + d.quantum_physics.porosity_cloud_radius + 'm)';
        let ph = '';
        d.yao_pellets.forEach((yp, idx) => {
          const c = yp.line_type === 'yang' ? '#FFD700' : '#38BDF8';
          ph += '<div class="pellet-dot" style="background:' + c +
                ';" title="L' + (idx+1) + ': ' + yp.line_type + '"></div>';
        });
        document.getElementById('pellet-indicators').innerHTML = ph;
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
        });
      });

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
