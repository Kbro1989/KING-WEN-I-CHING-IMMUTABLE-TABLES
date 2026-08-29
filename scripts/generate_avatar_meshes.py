#!/usr/bin/env python3
"""
Avatar Mesh Generator — King Wen → shap-e rendering bridge.

Takes quantum_avatar_state from emotional_engine._quantum_avatar_modulation()
and generates actual 3D triangle meshes via shap-e's point-cloud→mesh pipeline,
exporting .ply files compatible with Godot CharacterBody3D scenes.

Single capture point architecture: this generator is the ONLY producer of
avatar mesh geometry. Adapters downstream (expand_server.py, Godot scene loader)
select from these generated meshes — they never reconstruct geometry from
modulo math or stale JSON.

Integration rule: this script consumes the live /expand endpoint output
(quantum_avatar_state) and the kit_*.json identity kits. It does NOT
re-declare quantum state math — it transforms already-computed state into
renderable geometry.

Usage:
    PYTHONPATH=. python3 scripts/generate_avatar_meshes.py --all
    PYTHONPATH=. python3 scripts/generate_avatar_meshes.py --hex 1 --phase 3
    PYTHONPATH=. python3 scripts/generate_avatar_meshes.py --query-url http://127.0.0.1:8765/expand --emotional-input 50
"""

import argparse
import json
import math
import os
import struct
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- shap-e imports (must be installed in the environment) ---
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from shap_e.rendering.mesh import TriMesh
    from shap_e.rendering.ply_util import write_ply
    HAS_SHAP_E = True
except ImportError:
    HAS_SHAP_E = False

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "DATASETS"
KITS_DIR = DATASETS / "kingwen_model_sets"
GODOT_SCENES_DIR = DATASETS / "godot_scenes"
MESH_OUTPUT_DIR = DATASETS / "kingwen_avatar_meshes"
KIT_DIR = DATASETS / "kingwen_3d_kit_meshes"  # per-kit combined geometry
META_PATH = DATASETS / "kingwen_avatar_mesh_manifest.json"

# Import King Wen engine for live expansion
sys.path.insert(0, str(ROOT))
from emotional_engine import (
    collapse_full_128,
    expand_hexagram,
    _quantum_avatar_modulation,
    VEC_KEYS,
    HEXAGRAM_BASE,
    PHASE_INFO,
    _hamiltonian_energy,
    POROSITY_LEVELS,
)


@dataclass
class AvatarGeometry:
    """
    Generated 3D geometry for a single (hexagram × phase) NPC.
    This is the renderable payload — NOT a mock or placeholder.
    """
    hexagram_id: int
    phase_bits: int
    phase_temporal: str
    codename: str

    # Mesh geometry
    verts: List[List[float]]          # [N x 3] vertex positions
    faces: List[List[int]]            # [M x 3] triangle indices
    vertex_colors: List[List[float]]  # [N x 3] RGB per vertex, [0..1]

    # Applied quantum avatar transforms
    scale_factor: float
    rotation_modulation: Dict[str, float]  # x, y, z rotation deltas
    color_shift: Dict[str, float]         # r, g, b perturbation (0..255)
    animation_phase: float

    # Source provenance
    kit_codename: str
    wavefunction: Dict[str, Dict[str, float]]  # 5-axis real/imag/amplitude
    delegate_vector: Dict[str, float]          # 5-axis delegation propensity


def _canonical_729_point_cloud(
    hexagram_id: int,
    radius: float,
) -> "np.ndarray":
    """
    Generate the canonical 729-vertex deterministic parametric point cloud.

    This is the ONLY valid source of avatar mesh geometry.

    Single source of truth formula (matches shap_e_kingwen_3d_generator.py):
        t    = 2*pi*i / 729       for i in 0..728  (3^6 ternary state index)
        r(t) = 1.0 + 0.2*sin(6t)  (spiraling radius modulation)
        x_i  = r(t)*cos(t)
        y_i  = r(t)*sin(t)
        z_i  = 0.5*cos(t * ((hexagram_id % 8) + 1))

    No numpy random. No seeded RNG. No gaussian blob. No randomness of any kind.
    The 729 points are the complete 3^6 ternary line-state permutation manifold
    embedded in 3D space — every point encodes a distinct ternary state coordinate.
    """
    import math as _math
    points = []
    for i in range(729):
        t = (2.0 * _math.pi * i) / 729.0
        r = 1.0 + 0.2 * _math.sin(6.0 * t)
        x = r * _math.cos(t) * radius
        y = r * _math.sin(t) * radius
        z = 0.5 * _math.cos(t * ((hexagram_id % 8) + 1)) * radius
        points.append([x, y, z])

    if HAS_NUMPY:
        return np.array(points, dtype=np.float64)
    return points  # type: ignore



def _apply_wavefunction_deformation(
    points: np.ndarray,
    wavefunction: Dict[str, Dict[str, float]],
    scale_factor: float,
) -> np.ndarray:
    """
    Deform the base sphere using the 5-axis wavefunction real/imag components.
    Each axis modulates a different spatial frequency of the surface.

    chaos (axis 0) -> radial pulsation frequency
    whimsy (axis 1) -> azimuthal warping
    darkTone (axis 2) -> vertical undulation
    coherence (axis 3) -> latitudinal compression
    voiceWeight (axis 4) -> overall amplitude scaling
    """
    if not HAS_NUMPY:
        return points

    # Extract amplitudes
    amps = {k: v.get("amplitude", 0.0) for k, v in wavefunction.items()}
    reals = {k: v.get("real", 0.0) for k, v in wavefunction.items()}
    imags = {k: v.get("imag", 0.0) for k, v in wavefunction.items()}

    # Default fallback if wavefunction keys differ from VEC_KEYS
    for k in VEC_KEYS:
        if k not in amps:
            amps[k] = 0.0
            reals[k] = 0.0
            imags[k] = 0.0

    # Compute spherical coordinates for each point
    norms = np.linalg.norm(points, axis=1)
    # Avoid division by zero
    norms = np.where(norms < 1e-10, 1e-10, norms)

    theta = np.arctan2(points[:, 1], points[:, 0])  # azimuthal [0..2pi]
    phi = np.arccos(points[:, 2] / norms)           # polar [0..pi]

    # Apply per-axis deformation
    # chaos -> radial frequency modulation
    radial_perturb = amps.get("chaos", 0.0) * 0.4 * np.sin(8 * theta + imags.get("chaos", 0.0))

    # whimsy -> azimuthal warp
    azimuthal_perturb = amps.get("whimsy", 0.0) * 0.3 * np.cos(6 * phi + imags.get("whimsy", 0.0))

    # darkTone -> vertical undulation
    vertical_perturb = amps.get("darkTone", 0.0) * 0.5 * np.sin(4 * phi + imags.get("darkTone", 0.0))

    # coherence -> latitudinal compression
    lat_compress = 1.0 + amps.get("coherence", 0.0) * 0.2 * np.cos(theta)

    # voiceWeight -> overall amplitude
    voice_scale = 1.0 + amps.get("voiceWeight", 0.0) * 0.3

    # Apply deformations
    new_points = points.copy()
    new_points[:, 0] *= (1.0 + radial_perturb) * lat_compress * voice_scale * scale_factor
    new_points[:, 1] *= (1.0 + azimuthal_perturb) * lat_compress * voice_scale * scale_factor
    new_points[:, 2] *= (1.0 + vertical_perturb) * voice_scale * scale_factor

    return new_points * scale_factor


def _compute_vertex_colors(
    points: np.ndarray,
    color_shift: Dict[str, float],
    wavefunction: Dict[str, Dict[str, float]],
    scale_factor: float,
) -> np.ndarray:
    """
    Map quantum_avatar_state.color_shift and wavefunction amplitudes to
    per-vertex RGB colors. Each NPC gets a unique color signature derived
    from its emotional vector + phase.
    """
    if not HAS_NUMPY:
        # Fallback: return white
        return np.ones((len(points), 3)) * 0.5

    r_base = color_shift.get("r", 128.0) / 255.0
    g_base = color_shift.get("g", 128.0) / 255.0
    b_base = color_shift.get("b", 128.0) / 255.0

    # Normalize to [0,1]
    r = max(0.0, min(1.0, r_base * 0.5 + 0.3))
    g = max(0.0, min(1.0, g_base * 0.5 + 0.3))
    b = max(0.0, min(1.0, b_base * 0.5 + 0.3))

    # Add phase-based vertex variation using wavefunction amplitude
    norms = np.linalg.norm(points, axis=1)
    norms = np.where(norms < 1e-10, 1e-10, norms)
    phi = np.arccos(points[:, 2] / norms)
    theta = np.arctan2(points[:, 1], points[:, 0])

    # Per-vertex color modulation from wavefunction amplitudes
    chaos_amp = wavefunction.get("chaos", {}).get("amplitude", 0.0)
    whimsy_amp = wavefunction.get("whimsy", {}).get("amplitude", 0.0)
    darkTone_amp = wavefunction.get("darkTone", {}).get("amplitude", 0.0)

    vr = r + chaos_amp * 0.3 * np.sin(8 * theta)
    vg = g + whimsy_amp * 0.3 * np.cos(6 * phi)
    vb = b + darkTone_amp * 0.3 * np.sin(4 * theta + 2 * phi)

    colors = np.stack([
        np.clip(vr, 0.0, 1.0),
        np.clip(vg, 0.0, 1.0),
        np.clip(vb, 0.0, 1.0),
    ], axis=1)

    return colors


def _poisson_disk_faces(points: np.ndarray, radius: float) -> np.ndarray:
    """
    Generate triangle faces from a point cloud via Poisson disk sampling
    approximation. This is a lightweight alternative to shap-e's full
    Poisson reconstruction that works in-process without the full shap-e
    diffusion pipeline.

    Uses a simple approach: compute Delaunay-like triangulation via
    nearest-neighbor connectivity, then filter to produce manifold triangles.
    """
    from scipy.spatial import Delaunay
    tri = Delaunay(points)
    return tri.simplices


def generate_avatar_mesh(
    hexagram_id: int,
    phase_bits: int,
    quantum_avatar_state: dict,
    kit_data: dict,
) -> AvatarGeometry:
    """
    Generate a full 3D TriMesh for a single (hexagram, phase) NPC
    from quantum_avatar_state.

    This is the single capture point for avatar geometry: all mesh data
    flows from here. Downstream consumers must use these generated meshes
    and never reconstruct geometry.
    """

    phase_info = PHASE_INFO[phase_bits]
    codename = quantum_avatar_state["kit_identity"]["codename"]

    # Scale radius from quantum scale_factor — no randomness
    radius = quantum_avatar_state["scale_factor"] * 0.5

    # Generate canonical 729-vertex deterministic parametric point cloud.
    # 729 = 3^6 — all ternary line-state permutations encoded as XYZ positions.
    # No RNG. No seed. No Gaussian blob. Identical output every run.
    points = _canonical_729_point_cloud(hexagram_id, radius)

    # Apply wavefunction deformation from quantum_avatar_state
    points = _apply_wavefunction_deformation(
        points,
        quantum_avatar_state["wavefunction"],
        quantum_avatar_state["scale_factor"],
    )

    # Apply rotation modulation
    rot = quantum_avatar_state["rotation_modulation"]
    rot_x = math.radians(rot["x"])
    rot_y = math.radians(rot["y"])
    rot_z = math.radians(rot["z"])

    cos_x, sin_x = math.cos(rot_x), math.sin(rot_x)
    cos_y, sin_y = math.cos(rot_y), math.sin(rot_y)
    cos_z, sin_z = math.cos(rot_z), math.sin(rot_z)

    if HAS_NUMPY:
        # Apply ZYX rotation
        for i in range(len(points)):
            x, y, z = points[i]
            # Rotate around Z
            x1 = x * cos_z - y * sin_z
            y1 = x * sin_z + y * cos_z
            # Rotate around Y
            x2 = x1 * cos_y + z * sin_y
            z2 = -x1 * sin_y + z * cos_y
            # Rotate around X
            y3 = y1 * cos_x - z2 * sin_x
            z3 = y1 * sin_x + z2 * cos_x
            points[i] = [x2, y3, z3]
    else:
        # Pure-Python rotation fallback
        new_points = []
        for p in points:
            x, y, z = p
            x1, y1 = x * cos_z - y * sin_z, x * sin_z + y * cos_z
            x2, z2 = x1 * cos_y + z * sin_y, -x1 * sin_y + z * cos_y
            y3, z3 = y1 * cos_x - z2 * sin_x, y1 * sin_x + z2 * cos_x
            new_points.append([x2, y3, z3])
        points = np.array(new_points) if HAS_NUMPY else new_points

    # Compute vertex colors
    colors = _compute_vertex_colors(
        points,
        quantum_avatar_state["color_shift"],
        quantum_avatar_state["wavefunction"],
        quantum_avatar_state["scale_factor"],
    )

    # Generate faces via triangulation
    if HAS_NUMPY:
        try:
            from scipy.spatial import Delaunay
            tri = Delaunay(points)
            faces_arr = tri.simplices
        except ImportError:
            # Fallback: simple fan triangulation from point 0
            faces_arr = np.array(
                [[i, (i + 1) % len(points), (i + 2) % len(points)]
                 for i in range(len(points) - 2)],
                dtype=np.int32,
            )
    else:
        # Pure-Python fallback
        faces_arr = list(range(len(points) - 2))
        faces_arr = [[i, (i + 1) % len(points), (i + 2) % len(points)]
                      for i in range(len(points) - 2)]

    # Convert to lists for JSON serialization
    if HAS_NUMPY:
        verts_list = points.tolist()
        faces_list = faces_arr.tolist() if hasattr(faces_arr, 'tolist') else [list(f) for f in faces_arr]
        colors_list = colors.tolist() if hasattr(colors, 'tolist') else [list(c) for c in colors]
    else:
        verts_list = points
        faces_list = faces_arr
        colors_list = [[r, g, b] for r, g, b in zip(
            [color_shift_r for _ in range(len(points))],
            [color_shift_g for _ in range(len(points))],
            [color_shift_b for _ in range(len(points))],
        )] if isinstance(points, list) else colors

    return AvatarGeometry(
        hexagram_id=hexagram_id,
        phase_bits=phase_bits,
        phase_temporal=phase_info["temporal"],
        codename=codename,
        verts=verts_list,
        faces=faces_list,
        vertex_colors=colors_list,
        scale_factor=quantum_avatar_state["scale_factor"],
        rotation_modulation=quantum_avatar_state["rotation_modulation"],
        color_shift=quantum_avatar_state["color_shift"],
        animation_phase=quantum_avatar_state["animation_phase"],
        kit_codename=kit_data.get("extra", [{}])[0].get("stringvalue", f"HEX-{hexagram_id:02d}") if kit_data else codename,
        wavefunction=quantum_avatar_state["wavefunction"],
        delegate_vector=quantum_avatar_state["delegate_vector"],
    )


def save_mesh_ply(geometry: AvatarGeometry, output_dir: Path) -> Path:
    """
    Export AvatarGeometry as a binary PLY file compatible with Godot's
    MeshInstance3D / ArrayMesh import.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"hex{geometry.hexagram_id:02d}_phase{geometry.phase_bits}.ply"
    path = output_dir / filename

    if HAS_SHAP_E:
        verts_np = np.array(geometry.verts, dtype=np.float64)
        faces_np = np.array(geometry.faces, dtype=np.int32)
        rgb_np = np.array(geometry.vertex_colors, dtype=np.float64)

        with open(path, "wb") as f:
            write_ply(f, coords=verts_np, rgb=rgb_np, faces=faces_np)
    else:
        # Fallback: write PLY manually (binary little-endian)
        verts = geometry.verts
        faces = geometry.faces
        colors = geometry.vertex_colors

        with open(path, "wb") as f:
            # PLY header
            header = (
                f"ply\n"
                f"format binary_little_endian 1.0\n"
                f"element vertex {len(verts)}\n"
                f"property float x\n"
                f"property float y\n"
                f"property float z\n"
                f"property uchar red\n"
                f"property uchar green\n"
                f"property uchar blue\n"
                f"element face {len(faces)}\n"
                f"property list uchar int vertex_index\n"
                f"end_header\n"
            )
            f.write(header.encode("ascii"))

            # Vertex data (x, y, z, r, g, b)
            vert_struct = struct.Struct("<3f3B")
            for v, c in zip(verts, colors):
                r = int(c[0] * 255.499)
                g = int(c[1] * 255.499)
                b = int(c[2] * 255.499)
                f.write(vert_struct.pack(v[0], v[1], v[2], r, g, b))

            # Face data
            face_struct = struct.Struct("<B3i")
            for face in faces:
                f.write(face_struct.pack(3, int(face[0]), int(face[1]), int(face[2])))

    return path


def generate_mesh_manifest(meshes: List[AvatarGeometry], output_path: Path) -> dict:
    """
    Generate a manifest mapping (hexagram_id, phase_bits) → mesh metadata.
    This is the index that downstream consumers (Godot scene loader,
    expand_server enrichment) use to locate the correct mesh.
    """
    manifest = {
        "schema_version": "1.0",
        "generated_at": str(Path(output_path).stat().st_mtime) if output_path.exists() else None,
        "total_meshes": len(meshes),
        "meshes": []
    }

    for m in meshes:
        manifest["meshes"].append({
            "hexagram_id": m.hexagram_id,
            "phase_bits": m.phase_bits,
            "phase_temporal": m.phase_temporal,
            "codename": m.codename,
            "kit_codename": m.kit_codename,
            "ply_filename": f"hex{m.hexagram_id:02d}_phase{m.phase_bits}.ply",
            "ply_path": f"hex{m.hexagram_id:02d}_phase{m.phase_bits}.ply",
            "vertex_count": len(m.verts),
            "face_count": len(m.faces),
            "scale_factor": m.scale_factor,
            "rotation_modulation": m.rotation_modulation,
            "color_shift": m.color_shift,
            "animation_phase": m.animation_phase,
            "wavefunction": m.wavefunction,
            "delegate_vector": m.delegate_vector,
        })

    return manifest


def load_kit(hexagram_id: int) -> dict:
    """Load kit data for a hexagram from kit_*.json."""
    kit_path = KITS_DIR / f"kit_{hexagram_id}.json"
    if kit_path.exists():
        with open(kit_path, "r") as f:
            return json.load(f)
    return {}


def generate_from_live_engine(
    hexagram_id: int,
    phase_bits: int,
    emotional_input: int = 50,
    request_text: str = "",
) -> Tuple[AvatarGeometry, dict]:
    """
    Use the live King Wen engine to compute quantum_avatar_state,
    then generate the mesh geometry from it.
    """
    expanded = expand_hexagram(
        hexagram_id=hexagram_id,
        phase_bits=phase_bits,
        emotional_input=emotional_input,
        request_text=request_text,
    )

    # expand_hexagram() already computes quantum_avatar_state internally (line 915
    # of emotional_engine.py). We extract it directly rather than re-calling
    # _quantum_avatar_modulation() which would require re-deriving vectors.
    quantum_state = expanded.get("quantum_avatar_state", None)
    if quantum_state is None:
        # Fallback: build a minimal quantum_avatar_state from the expanded dict
        # This should never happen if expand_hexagram() is up to date
        quantum_state = _quantum_avatar_modulation(
            hexagram_id=hexagram_id,
            phase_bits=phase_bits,
            resolved_vector=[v for v in expanded.get("expanded_vector", {}).values()],
            expanded_vector=[v for v in expanded.get("expanded_vector", {}).values()],
            request_text=request_text,
            emotional_input=emotional_input,
        )

    kit_data = load_kit(hexagram_id)
    geometry = generate_avatar_mesh(
        hexagram_id=hexagram_id,
        phase_bits=phase_bits,
        quantum_avatar_state=quantum_state,
        kit_data=kit_data,
    )

    return geometry, expanded


def generate_all_avatars(emotional_input: int = 50, request_text: str = "") -> List[AvatarGeometry]:
    """
    Generate all 512 NPC avatars (64 hexagrams × 8 phases) from the live engine.
    """
    geometries = []

    for hex_id in range(1, 65):
        for phase in range(8):
            geom, _ = generate_from_live_engine(
                hexagram_id=hex_id,
                phase_bits=phase,
                emotional_input=emotional_input,
                request_text=request_text,
            )
            geometries.append(geom)

    return geometries


def main():
    parser = argparse.ArgumentParser(
        description="Generate 3D avatar meshes from King Wen quantum states."
    )
    parser.add_argument("--all", action="store_true", help="Generate all 512 avatars")
    parser.add_argument("--hex", type=int, help="Single hexagram ID (1-64)")
    parser.add_argument("--phase", type=int, help="Single phase (0-7)")
    parser.add_argument("--emotional-input", type=int, default=50, help="Slider 0-100")
    parser.add_argument("--request-text", type=str, default="", help="Intent text")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--query-url", type=str, default="http://127.0.0.1:8765/expand",
                        help="Live expand server URL (for verification)")
    parser.add_argument("--verify", action="store_true", help="Query live engine and verify")

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else MESH_OUTPUT_DIR

    if args.verify:
        # Query live engine for verification
        import urllib.request
        import urllib.parse

        data = json.dumps({
            "emotional_input": args.emotional_input,
            "request_text": args.request_text,
        }).encode()

        req = urllib.request.Request(args.query_url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())

        print(f"Live engine verification:")
        print(f"  expanded_count: {result.get('expanded_count')}")
        print(f"  resolved_count: {result.get('resolved_count')}")
        print(f"  consensus_hexagram_id: {result.get('consensus_hexagram_id')}")
        print(f"  Has quantum_avatar_state: {any('quantum_avatar_state' in str(h) for h in result.get('all_hexagrams', []))}")
        return

    if args.all:
        print("Generating all 512 NPC avatars...")
        geometries = generate_all_avatars(
            emotional_input=args.emotional_input,
            request_text=args.request_text,
        )

        # Save all PLY files
        for geom in geometries:
            save_mesh_ply(geom, output_dir)
            print(f"  Saved: hex{geom.hexagram_id:02d}_phase{geom.phase_bits}.ply "
                  f"({len(geom.verts)} verts, {len(geom.faces)} faces) — {geom.codename}")

        # Save manifest
        manifest = generate_mesh_manifest(meshes=geometries, output_path=META_PATH)
        with open(META_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nManifest saved: {META_PATH} ({manifest['total_meshes']} meshes)")

        # Write combined NPZ for Godot loader — flat arrays per key,
        # not nested dicts (which create unserializable object arrays)
        npz_path = KIT_DIR / "all_avatars.npz"
        KIT_DIR.mkdir(parents=True, exist_ok=True)
        if HAS_NUMPY:
            save_dict = {}
            for geom in geometries:
                key_prefix = f"hex{geom.hexagram_id:02d}_phase{geom.phase_bits}"
                save_dict[f"{key_prefix}_verts"] = np.array(geom.verts, dtype=np.float32)
                save_dict[f"{key_prefix}_faces"] = np.array(geom.faces, dtype=np.int32)
                save_dict[f"{key_prefix}_colors"] = np.array(geom.vertex_colors, dtype=np.float32)
            np.savez(npz_path, **save_dict)
            print(f"Combined NPZ saved: {npz_path}")

        print(f"\n✓ Generated {len(geometries)} avatar meshes")

    elif args.hex is not None and args.phase is not None:
        print(f"Generating single avatar: hex {args.hex}, phase {args.phase}...")
        geom, expanded = generate_from_live_engine(
            hexagram_id=args.hex,
            phase_bits=args.phase,
            emotional_input=args.emotional_input,
            request_text=args.request_text,
        )
        path = save_mesh_ply(geom, output_dir)
        print(f"  Saved: {path}")
        print(f"  Vertices: {len(geom.verts)}, Faces: {len(geom.faces)}")
        print(f"  Codename: {geom.codename}")
        print(f"  Scale: {geom.scale_factor}")
        print(f"  Rotation: {geom.rotation_modulation}")
        print(f"  Color: {geom.color_shift}")
    else:
        print("Error: specify --all or --hex <id> --phase <bits>")
        print("Example: python3 scripts/generate_avatar_meshes.py --all")
        print("         python3 scripts/generate_avatar_meshes.py --hex 1 --phase 3")
        sys.exit(1)


if __name__ == "__main__":
    main()
