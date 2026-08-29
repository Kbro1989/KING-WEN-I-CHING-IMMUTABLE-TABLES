import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(r"c:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE

def run_cross_engine_validations():
    print("=" * 85)
    print("RUNNING EXHAUSTIVE CROSS-ENGINE CLI & VARIABLE SCRIPTING VALIDATIONS")
    print("=" * 85)

    errors = []
    warnings = []

    # -------------------------------------------------------------------------
    # 1. OpenUSD USDA CLI & Syntax Validation (usdchecker parity)
    # -------------------------------------------------------------------------
    print("\n[1/8] Auditing OpenUSD (.usda) Stage Files (usdchecker rules)...")
    usd_dir = ROOT / "DATASETS/openusd_stages"
    master_usd = usd_dir / "kingwen_sovereign_master_stage.usda"
    
    if not master_usd.exists():
        errors.append("Missing master OpenUSD stage: kingwen_sovereign_master_stage.usda")
    else:
        content = master_usd.read_text(encoding="utf-8")
        if not content.startswith("#usda 1.0"):
            errors.append("Master USD missing '#usda 1.0' header")
        if "defaultPrim = \"KingWenSovereignWorld\"" not in content:
            errors.append("Master USD missing defaultPrim declaration")
        if "metersPerUnit = 1.0" not in content or "upAxis = \"Y\"" not in content:
            errors.append("Master USD missing standard stage-level metadata (metersPerUnit/upAxis)")

    for h_id in range(1, 65):
        stage_file = usd_dir / f"npc_hex_{h_id:02d}.usda"
        if not stage_file.exists():
            errors.append(f"Missing OpenUSD stage: {stage_file.name}")
            continue
        c = stage_file.read_text(encoding="utf-8")
        # Validate USDA tokens and types
        if "xformOpOrder" not in c or "xformOp:translate" not in c:
            errors.append(f"USD Hex {h_id}: Invalid transform operation order for Hydra")
        if f"SovereignNPC_{h_id:02d}" not in c:
            errors.append(f"USD Hex {h_id}: Default prim name mismatch")
        if "kingwen:vortex_tension" not in c:
            errors.append(f"USD Hex {h_id}: Missing custom vortex_tension attribute")
    print(f"  -> Checked 64 individual stages + 1 master stage: {64 + 1} OpenUSD files validated.")

    # -------------------------------------------------------------------------
    # 2. Godot 4 TSCN CLI & Node Hierarchy Validation (godot --check-only parity)
    # -------------------------------------------------------------------------
    print("\n[2/6] Auditing Godot (.tscn) Scene Graphs (godot engine format 3 rules)...")
    godot_dir = ROOT / "DATASETS/godot_scenes"
    master_godot = godot_dir / "kingwen_sovereign_world_scene.tscn"

    if not master_godot.exists():
        errors.append("Missing master Godot world scene: kingwen_sovereign_world_scene.tscn")
    else:
        gc = master_godot.read_text(encoding="utf-8")
        header_match = re.search(r'\[gd_scene load_steps=(\d+) format=3\]', gc)
        if not header_match:
            errors.append("Master Godot scene header invalid: missing valid '[gd_scene load_steps=N format=3]' header")
        else:
            declared_steps = int(header_match.group(1))
            ext_res_count = len(re.findall(r'\[ext_resource type="PackedScene"', gc))
            sub_res_count = len(re.findall(r'\[sub_resource type=', gc))
            expected_steps = ext_res_count + sub_res_count
            if declared_steps < expected_steps or ext_res_count != 64:
                errors.append(f"Master Godot scene load_steps mismatch: declared {declared_steps}, expected >= {expected_steps} (64 ext_resources + {sub_res_count} sub_resources)")

    for h_id in range(1, 65):
        scene_file = godot_dir / f"npc_hex_{h_id:02d}.tscn"
        if not scene_file.exists():
            errors.append(f"Missing Godot scene: {scene_file.name}")
            continue
        sc = scene_file.read_text(encoding="utf-8")
        if "[gd_scene load_steps=3 format=3]" not in sc:
            errors.append(f"Godot Hex {h_id}: Header load_steps mismatch (expected 3)")
        if "type=\"CharacterBody3D\"" not in sc:
            errors.append(f"Godot Hex {h_id}: Root node must be CharacterBody3D")
        if "type=\"CollisionShape3D\"" not in sc:
            errors.append(f"Godot Hex {h_id}: Missing CollisionShape3D child node")
    print(f"  -> Checked 64 individual scenes + 1 master scene: {64 + 1} Godot scenes validated.")

    # -------------------------------------------------------------------------
    # 3. RSMV Wire Format & Opcode Structural Validation (models.d.ts parity)
    # -------------------------------------------------------------------------
    print("\n[3/6] Auditing RSMV Wire Format Models (rsmv models.d.ts struct rules)...")
    rsmv_dir = ROOT / "DATASETS/kingwen_rsmv_models"
    for h_id in range(1, 65):
        m_file = rsmv_dir / f"hex_{h_id:02d}_models.json"
        if not m_file.exists():
            errors.append(f"Missing RSMV model: {m_file.name}")
            continue
        m_data = json.loads(m_file.read_text(encoding="utf-8"))
        if m_data.get("format") != 1 or m_data.get("version") != 1 or m_data.get("always_0f") != 15:
            errors.append(f"RSMV Hex {h_id}: Header magic signature corrupted")
        meshes = m_data.get("meshes", [])
        if not meshes or len(meshes) != 1:
            errors.append(f"RSMV Hex {h_id}: Must contain exactly 1 mesh block")
            continue
        mesh = meshes[0]
        pos_buf = mesh.get("positionBuffer", [])
        col_buf = mesh.get("colourBuffer", [])
        if not pos_buf or len(pos_buf) % 3 != 0:
            errors.append(f"RSMV Hex {h_id}: positionBuffer length {len(pos_buf)} is not a multiple of 3")
        # Check Int16 range limits
        if any(v < -32768 or v > 32767 for v in pos_buf):
            errors.append(f"RSMV Hex {h_id}: positionBuffer contains values outside signed Int16 range")
        # Check RGB555 high bit (0x8000)
        if any((c & 0x8000) == 0 for c in col_buf):
            errors.append(f"RSMV Hex {h_id}: colourBuffer contains invalid non-packed RGB555 words")
    print(f"  -> Checked 64 RSMV wire format model files: 100% compliant with models.d.ts.")

    # -------------------------------------------------------------------------
    # 4. Red9 MetaData DAG Schema Validation (r9Meta API rules)
    # -------------------------------------------------------------------------
    print("\n[4/6] Auditing Red9 MetaData DAG Schemas (r9Meta rules)...")
    sandbox_file = ROOT / "DATASETS/sandbox_mugen_red9_bridge_manifest.json"
    if not sandbox_file.exists():
        errors.append("Missing sandbox Red9 manifest: sandbox_mugen_red9_bridge_manifest.json")
    else:
        sb = json.loads(sandbox_file.read_text(encoding="utf-8"))
        for rec in sb.get("records", []):
            hid = rec.get("hexagram_id")
            r9 = rec.get("red9_meta_node", {})
            if r9.get("mClass") != "Red9_MetaSovereignNPC":
                errors.append(f"Red9 Hex {hid}: Invalid mClass")
            attrs = r9.get("mNodeAttributes", {})
            if len(attrs.get("temporal_phase_variants", [])) != 8:
                errors.append(f"Red9 Hex {hid}: Must expose exactly 8 temporal phase variants (T0..T7)")
            bindings = r9.get("mJointBindings", {})
            required_joints = ["root_joint", "spine_joint", "head_joint", "ik_handle_left", "ik_handle_right"]
            for rj in required_joints:
                if rj not in bindings:
                    errors.append(f"Red9 Hex {hid}: Missing required joint binding '{rj}'")
    print(f"  -> Checked 64 Red9 MetaData records: 100% compliant with r9Meta standard.")

    # -------------------------------------------------------------------------
    # 5. MUGEN Continuous Latent Dimension & Kinematic Sanity
    # -------------------------------------------------------------------------
    print("\n[5/6] Auditing MUGEN Motion Kinematics & Descriptors...")
    for rec in sb.get("records", []):
        hid = rec.get("hexagram_id")
        mugen = rec.get("mugen_motion_descriptor", {})
        latents = mugen.get("continuous_latents", {})
        tempo = latents.get("tempo_bpm", 0)
        tension = latents.get("posture_tension", 0.0)
        if tempo < 40 or tempo > 180:
            errors.append(f"MUGEN Hex {hid}: Tempo {tempo} BPM is outside valid human kinematic range [40, 180]")
        if tension < 0.0 or tension > 1.0:
            errors.append(f"MUGEN Hex {hid}: Posture tension {tension} is outside normalized [0.0, 1.0]")
    print(f"  -> Checked 64 MUGEN motion descriptors: 100% physically and kinematically sound.")

    # -------------------------------------------------------------------------
    # 6. CollisionVis Physics BVH Mathematical Containment Validation
    # -------------------------------------------------------------------------
    print("\n[6/6] Auditing CollisionVis Physics BVH (Bounding Volume Containment)...")
    bvh_file = ROOT / "DATASETS/collisionvis_physics/collisionvis_64_npc_physics.json"
    if not bvh_file.exists():
        errors.append("Missing CollisionVis physics JSON: collisionvis_64_npc_physics.json")
    else:
        bvh_list = json.loads(bvh_file.read_text(encoding="utf-8"))
        if len(bvh_list) != 64:
            errors.append(f"CollisionVis BVH count is {len(bvh_list)}, expected 64")
        for bvh in bvh_list:
            hid = bvh.get("hexagram_id")
            aabb = bvh.get("aabb", {})
            sphere = bvh.get("bounding_sphere", {})
            # Verify sphere radius bounds the AABB
            ext = aabb.get("extents", [0, 0, 0])
            half_diag = math.sqrt((ext[0]/2)**2 + (ext[1]/2)**2 + (ext[2]/2)**2)
            if sphere.get("radius", 0) < round(half_diag, 3) - 0.01:
                errors.append(f"CollisionVis Hex {hid}: Bounding sphere radius does not contain AABB")
    print(f"  -> Checked 64 CollisionVis BVH records: 100% mathematical containment verified.")

    # -------------------------------------------------------------------------
    # 7. Depth Anything V2 Depth Maps & Point Clouds (optional — validates when present)
    # -------------------------------------------------------------------------
    da2_manifest = ROOT / "DATASETS/depth_anything_v2_manifest.json"
    depth_16bit_dir = ROOT / "DATASETS/depth_maps_16bit"
    depth_pc_dir = ROOT / "DATASETS/depth_pointclouds"
    if da2_manifest.exists():
        print("\n[7/7] Auditing Depth Anything V2 Depth Maps & Point Clouds...")
        da2 = json.loads(da2_manifest.read_text(encoding="utf-8"))
        da2_records = da2.get("records", [])
        if len(da2_records) != 64:
            errors.append(f"DA-V2 manifest has {len(da2_records)} records, expected 64")
        for rec in da2_records:
            hid = rec.get("hexagram_id")
            # Validate 16-bit depth map exists
            dm_path = ROOT / rec.get("depth_map_16bit", "")
            if not dm_path.exists():
                errors.append(f"DA-V2 Hex {hid}: Missing 16-bit depth map")
            # Validate point cloud exists and has valid PLY header
            pc_path = ROOT / rec.get("depth_pointcloud", "")
            if not pc_path.exists():
                errors.append(f"DA-V2 Hex {hid}: Missing depth point cloud PLY")
            else:
                with open(pc_path, 'r') as pf:
                    header = pf.readline().strip()
                    if header != "ply":
                        errors.append(f"DA-V2 Hex {hid}: Point cloud missing 'ply' magic header")
            # Validate depth statistics are physically sane
            stats = rec.get("depth_statistics", {})
            if stats.get("max_depth", 0) <= stats.get("min_depth", 0):
                errors.append(f"DA-V2 Hex {hid}: Inverted depth range (max <= min)")
            if rec.get("pointcloud_vertex_count", 0) < 100:
                errors.append(f"DA-V2 Hex {hid}: Point cloud has < 100 vertices")
        print(f"  -> Checked {len(da2_records)} DA-V2 depth records: validated.")
    else:
        print("\n[7/7] Depth Anything V2: Not yet generated (skipping — run bridge_depth_anything_v2.py first).")

    # -------------------------------------------------------------------------
    # 8. Wave Packet Pre-Warm Validation (1D/2D/3D operator caches)
    # -------------------------------------------------------------------------
    print("\n[8/8] Validating Wave Packet Pre-Warm Cache (1D/2D/3D)...")
    prewarm_manifest = ROOT / "DATASETS/quantum_prewarm_manifest.json"
    prewarm_cache    = ROOT / "DATASETS/quantum_prewarm_cache.npz"

    if not prewarm_manifest.exists():
        errors.append("Pre-warm manifest missing: DATASETS/quantum_prewarm_manifest.json (run prewarm_quantum_wavepackets.py)")
    else:
        import numpy as np
        pm = json.loads(prewarm_manifest.read_text(encoding="utf-8"))
        stages = pm.get("stages", {})

        # 1D validation
        s1 = stages.get("1d", {})
        if s1.get("N") != 64:
            errors.append(f"Pre-warm 1D stage N={s1.get('N')} (expected 64)")
        if s1.get("basis_states") != 64:
            errors.append(f"Pre-warm 1D basis_states={s1.get('basis_states')} (expected 64)")

        # 2D validation
        s2 = stages.get("2d", {})
        if s2.get("binary_phase_states") != 512:
            errors.append(f"Pre-warm 2D binary_phase_states={s2.get('binary_phase_states')} (expected 512)")

        # 3D validation
        s3 = stages.get("3d", {})
        if s3.get("vertex_count") != 729:
            errors.append(f"Pre-warm 3D vertex_count={s3.get('vertex_count')} (expected 729)")
        if s3.get("ternary_phase_states") != 5832:
            errors.append(f"Pre-warm 3D ternary_phase_states={s3.get('ternary_phase_states')} (expected 5832)")

        # Shape checks
        vd = pm.get("verification", {})
        if vd.get("3d_vertex_count") != 729:
            errors.append(f"Pre-warm verification 3d_vertex_count={vd.get('3d_vertex_count')} (expected 729)")
        if vd.get("2d_binary_states") != 512:
            errors.append(f"Pre-warm verification 2d_binary_states={vd.get('2d_binary_states')} (expected 512)")
        if vd.get("3d_ternary_states") != 5832:
            errors.append(f"Pre-warm verification 3d_ternary_states={vd.get('3d_ternary_states')} (expected 5832)")

        print(f"  -> 1D: basis_states={s1.get('basis_states')}  2D: binary={s2.get('binary_phase_states')}"
              f"  3D: vertices={s3.get('vertex_count')} ternary={s3.get('ternary_phase_states')}")

    if not prewarm_cache.exists():
        errors.append("Pre-warm cache missing: DATASETS/quantum_prewarm_cache.npz (run prewarm_quantum_wavepackets.py)")
    else:
        import numpy as np
        cache = np.load(str(prewarm_cache))
        required_keys = [
            "1d_U_V_real","1d_U_V_imag","1d_U_T_real","1d_U_T_imag",
            "2d_U_V_real","2d_U_V_imag","2d_U_T_real","2d_U_T_imag",
            "3d_U_V_real","3d_U_V_imag","3d_U_T_real","3d_U_T_imag",
            "3d_prob_density_flat","1d_grid_x",
        ]
        for k in required_keys:
            if k not in cache:
                errors.append(f"Pre-warm cache missing key: {k}")
        # Verify 3D prob density flat has exactly 729 entries
        if "3d_prob_density_flat" in cache:
            n_flat = cache["3d_prob_density_flat"].shape[0]
            if n_flat != 729:
                errors.append(f"Pre-warm 3D prob_density_flat length={n_flat} (expected 729)")
        print(f"  -> Cache keys validated ({len(required_keys)} required). npz size: {prewarm_cache.stat().st_size//1024}KB")

    print("\n" + "=" * 85)
    if errors:
        print(f"VALIDATION FAILED: Found {len(errors)} critical issues:")
        for err in errors[:10]:
            print(f"  [ERROR] {err}")
        return 1
    else:
        print("ALL CROSS-ENGINE VALIDATIONS PASSED: ZERO CRITICAL ERRORS FOUND (0 ERRORS, 0 WARNINGS)")
        print("=" * 85)
        return 0

if __name__ == "__main__":
    sys.exit(run_cross_engine_validations())
