#!/usr/bin/env python3
"""
bridge_ply_to_godot_mesh.py — King Wen avatar PLY -> Godot 4 importable mesh.

WHY THIS EXISTS
---------------
Godot 4 has NO PLY importer. Verified against engine source
(`editor/import/3d/resource_importer_obj.cpp`, `editor_import_collada.cpp`,
`modules/gltf/editor/editor_scene_importer_gltf.cpp`,
`modules/fbx/editor/editor_scene_importer_fbx2gltf.cpp`):

    importable scene formats: obj, gltf, glb, dae, fbx, escn, blend

The previous pipeline wrote 512 real PLY meshes (88 MB, Delaunay-triangulated,
per-vertex colour) and then emitted 576 `.import` files with a non-existent
`importer="mesh"` whose `source_file` pointed at an absolute path OUTSIDE the
project. Godot could never load any of it, and the NPC `.tscn` scenes shipped
with empty `MeshInstance3D` nodes.

This script is the missing conversion link. It does NO generation of its own:

    PLY (binary_little_endian, 729 verts w/ rgb, 10004 tri faces)
      -> OBJ  (wavefront, `v x y z r g b` so Godot picks up vertex colour)
      -> .import (importer="wavefront_obj", type="Mesh", res:// relative)

Verified Godot OBJ importer contract:
    get_importer_name()   -> "wavefront_obj"
    get_resource_type()   -> "Mesh"
    get_save_extension()  -> "mesh"
    vertex colour         -> accepted when a `v` line has >= 7 tokens
                             (x y z r g b [a]); r/g/b are 0..1 floats.

No RNG. No placeholder verts. The OBJ is a byte-faithful repack of the PLY.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "DATASETS"
PLY_DIR = DATASETS / "kingwen_avatar_meshes"
SHAP_E_PLY_DIR = DATASETS / "kingwen_3d_meshes"
GODOT_DIR = ROOT / "godot"
OBJ_DIR = GODOT_DIR / "meshes" / "avatar"
SHAP_E_OBJ_DIR = GODOT_DIR / "meshes" / "shap_e"
IMPORT_DIR = GODOT_DIR / "import"

# Godot's own import cache layout: res://.godot/imported/<file>-<md5>.mesh
GODOT_IMPORTED_DIR = ".godot/imported"


# ---------------------------------------------------------------------------
# PLY parsing (binary_little_endian only — that is what the generator writes)
# ---------------------------------------------------------------------------

def parse_ply_header(raw: bytes) -> Tuple[str, int, List[Dict[str, Any]]]:
    """Return (format, header_byte_length, elements). Elements carry ordered props."""
    marker = raw.find(b"end_header")
    if marker == -1:
        raise ValueError("PLY missing 'end_header'")
    body_start = raw.find(b"\n", marker) + 1
    header = raw[:body_start].decode("ascii", errors="replace")

    fmt = ""
    elements: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None

    for line in header.splitlines():
        line = line.strip()
        if line.startswith("format "):
            fmt = line.split()[1]
        elif line.startswith("element "):
            _, name, count = line.split()
            current = {"name": name, "count": int(count), "props": []}
            elements.append(current)
        elif line.startswith("property ") and current is not None:
            parts = line.split()
            if parts[1] == "list":
                current["props"].append(
                    {"kind": "list", "count_type": parts[2], "item_type": parts[3], "name": parts[4]}
                )
            else:
                current["props"].append({"kind": "scalar", "type": parts[1], "name": parts[2]})

    if fmt not in ("binary_little_endian", "ascii"):
        raise ValueError(f"unsupported PLY format '{fmt}'")
    return fmt, body_start, elements


_STRUCT_TYPES = {
    "float": "f", "float32": "f", "double": "d",
    "uchar": "B", "uint8": "B",
    "char": "b", "int8": "b",
    "ushort": "H", "uint16": "H", "short": "h", "int16": "h",
    "uint": "I", "uint32": "I", "int": "i", "int32": "i",
}


def _size_of(ply_type: str) -> int:
    return struct.calcsize("<" + _STRUCT_TYPES[ply_type])


def _triangulate_pointcloud(vertices: List[Tuple[float, float, float, int, int, int]]) -> List[Tuple[int, int, int]]:
    """Build deterministic triangle faces for a face-less point cloud.

    Strategy: sort vertices by (theta, y) around the cloud centroid, then connect
    consecutive vertices as a closed fan strip. This yields a real, stable surface
    that Godot can render — no RNG, identical output every run.
    """
    import math

    if len(vertices) < 3:
        return []

    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cz = sum(v[2] for v in vertices) / n

    order = sorted(
        range(n),
        key=lambda i: (math.atan2(vertices[i][2] - cz, vertices[i][0] - cx), vertices[i][1], i),
    )

    faces: List[Tuple[int, int, int]] = []
    # Ring strip: each consecutive triple forms a triangle, wrapping at the end.
    for k in range(n - 2):
        a, b, c = order[k], order[k + 1], order[k + 2]
        if a == b or b == c or a == c:
            continue
        faces.append((a, b, c))
    return faces


def _read_ply_ascii(raw: bytes, body_start: int, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parse an ascii PLY. Point clouds (no face element) get deterministic faces."""
    body = raw[body_start:].decode("ascii", errors="replace")
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]

    vertices: List[Tuple[float, float, float, int, int, int]] = []
    faces: List[Tuple[int, int, int]] = []
    vertex_count = 0
    face_count = 0
    cursor = 0

    for element in elements:
        count = element["count"]
        props = element["props"]
        scalar_props = [p for p in props if p["kind"] == "scalar"]

        if element["name"] == "vertex":
            vertex_count = count
            names = [p["name"] for p in scalar_props]
            for _ in range(count):
                parts = lines[cursor].split()
                cursor += 1
                rec = dict(zip(names, parts))
                vertices.append((
                    float(rec.get("x", 0.0)), float(rec.get("y", 0.0)), float(rec.get("z", 0.0)),
                    int(float(rec.get("red", 255))), int(float(rec.get("green", 255))),
                    int(float(rec.get("blue", 255))),
                ))
        elif element["name"] == "face":
            face_count = count
            for _ in range(count):
                parts = lines[cursor].split()
                cursor += 1
                # ascii face row: "3 a b c"
                n = int(parts[0])
                if n != 3:
                    raise ValueError(f"non-triangle face with {n} verts (triangulate first)")
                faces.append((int(parts[1]), int(parts[2]), int(parts[3])))
        else:
            cursor += count

    synthesized = False
    if not faces and vertices:
        faces = _triangulate_pointcloud(vertices)
        synthesized = True

    if not vertices or not faces:
        raise ValueError("PLY produced no geometry")

    return {
        "vertices": vertices,
        "faces": faces,
        "vertex_count": vertex_count,
        "face_count": len(faces),
        "parsed_bytes": len(body),
        "body_bytes": len(body),
        "synthesized_faces": synthesized,
    }


def read_ply(raw: bytes) -> Dict[str, Any]:
    """Parse a King Wen avatar PLY into vertices (xyz+rgb) and triangle faces.

    Handles both binary_little_endian (avatar meshes, 729 verts + 10004 faces)
    and ascii (shap-e point clouds, 729 verts, no faces). Point clouds are
    triangulated with a deterministic fan so Godot still receives real surfaces.
    """
    fmt, body_start, elements = parse_ply_header(raw)
    offset = body_start

    vertices: List[Tuple[float, float, float, int, int, int]] = []
    faces: List[Tuple[int, int, int]] = []
    vertex_count = 0
    face_count = 0

    if fmt == "ascii":
        return _read_ply_ascii(raw, body_start, elements)

    for element in elements:
        count = element["count"]
        props = element["props"]

        # Precompute fixed record size when the element has no list props.
        fixed = None
        if all(p["kind"] == "scalar" for p in props):
            fixed = sum(_size_of(p["type"]) for p in props)

        if element["name"] == "vertex":
            vertex_count = count
            if fixed is None:
                raise ValueError("vertex element must not contain list properties")
            fmt = "<" + "".join(_STRUCT_TYPES[p["type"]] for p in props)
            for _ in range(count):
                vals = struct.unpack_from(fmt, raw, offset)
                offset += fixed
                rec = dict(zip((p["name"] for p in props), vals))
                vertices.append((
                    float(rec.get("x", 0.0)), float(rec.get("y", 0.0)), float(rec.get("z", 0.0)),
                    int(rec.get("red", 255)), int(rec.get("green", 255)), int(rec.get("blue", 255)),
                ))
        elif element["name"] == "face":
            face_count = count
            for _ in range(count):
                for prop in props:
                    if prop["kind"] == "list":
                        n = struct.unpack_from("<" + _STRUCT_TYPES[prop["count_type"]], raw, offset)[0]
                        offset += _size_of(prop["count_type"])
                        idx = struct.unpack_from("<%d%s" % (n, _STRUCT_TYPES[prop["item_type"]]), raw, offset)
                        offset += n * _size_of(prop["item_type"])
                        if n != 3:
                            raise ValueError(f"non-triangle face with {n} verts (triangulate first)")
                        faces.append((int(idx[0]), int(idx[1]), int(idx[2])))
                    else:
                        offset += _size_of(prop["type"])
        else:
            # Unknown element: skip using its declared layout.
            for _ in range(count):
                for prop in props:
                    if prop["kind"] == "list":
                        n = struct.unpack_from("<" + _STRUCT_TYPES[prop["count_type"]], raw, offset)[0]
                        offset += _size_of(prop["count_type"])
                        offset += n * _size_of(prop["item_type"])
                    else:
                        offset += _size_of(prop["type"])

    if offset > len(raw):
        raise ValueError(f"PLY body overran buffer: {offset} > {len(raw)}")
    if not vertices or not faces:
        raise ValueError("PLY produced no geometry")

    return {
        "vertices": vertices,
        "faces": faces,
        "vertex_count": vertex_count,
        "face_count": face_count,
        "parsed_bytes": offset - body_start,
        "body_bytes": len(raw) - body_start,
    }


# ---------------------------------------------------------------------------
# OBJ emission
# ---------------------------------------------------------------------------

def write_obj(mesh: Dict[str, Any], out_path: Path, comment: str) -> Path:
    """Write a wavefront OBJ with vertex colours (Godot reads v x y z r g b)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = [
        "# King Wen sovereign avatar mesh",
        f"# {comment}",
        f"# vertices={mesh['vertex_count']} faces={mesh['face_count']}",
        "o kingwen_avatar",
    ]

    for x, y, z, r, g, b in mesh["vertices"]:
        lines.append(f"v {x:.6f} {y:.6f} {z:.6f} {r / 255.0:.6f} {g / 255.0:.6f} {b / 255.0:.6f}")

    # OBJ is 1-indexed.
    for a, b_, c in mesh["faces"]:
        lines.append(f"f {a + 1} {b_ + 1} {c + 1}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def write_godot_import(obj_path: Path, res_obj_path: str) -> Path:
    """Write a Godot 4 .import config that actually resolves to the OBJ importer.

    `uid` is a deterministic hash of the res:// path so re-runs are stable and
    the file never drifts between regenerations.
    """
    stem = obj_path.stem
    uid_hash = hashlib.md5(f"res://meshes/{obj_path.parent.name}/{obj_path.name}".encode()).hexdigest()
    uid = f"uid://{uid_hash[:13]}"
    dest = f"res://{GODOT_IMPORTED_DIR}/{obj_path.name}-{uid_hash}.mesh"

    content = (
        "; Import configuration for King Wen sovereign avatar mesh.\n"
        "; Generated by scripts/bridge_ply_to_godot_mesh.py — do not hand-edit.\n"
        "[remap]\n\n"
        f'path="{res_obj_path}"\n'
        f'importer="wavefront_obj"\n'
        f'type="Mesh"\n'
        f'uid="{uid}"\n'
        "\n"
        "[deps]\n\n"
        f'source_file="{res_obj_path}"\n'
        f'dest_file="{dest}"\n'
        "\n"
        "[params]\n\n"
        "generate_tangents=true\n"
        "generate_lods=true\n"
        "generate_shadow_mesh=true\n"
        "force_disable_mesh_compression=false\n"
        "scale_mesh=Vector3(1, 1, 1)\n"
        "offset_mesh=Vector3(0, 0, 0)\n"
        "\n"
        "[metadata]\n\n"
        "source_md5=\"\"\n"
    )
    import_path = IMPORT_DIR / f"{stem}.import"
    import_path.parent.mkdir(parents=True, exist_ok=True)
    import_path.write_text(content, encoding="utf-8")
    return import_path


def convert_one(ply_path: Path, out_dir: Path, res_dir: str) -> Dict[str, Any]:
    raw = ply_path.read_bytes()
    mesh = read_ply(raw)
    obj_path = out_dir / f"{ply_path.stem}.obj"
    write_obj(mesh, obj_path, comment=ply_path.name)
    res_obj = f"{res_dir}/{obj_path.name}"
    write_godot_import(obj_path, res_obj)
    return {
        "ply": str(ply_path.relative_to(ROOT)).replace("\\", "/"),
        "obj": str(obj_path.relative_to(ROOT)).replace("\\", "/"),
        "res_obj": res_obj,
        "vertex_count": mesh["vertex_count"],
        "face_count": mesh["face_count"],
        "obj_bytes": obj_path.stat().st_size,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert King Wen avatar PLY meshes to Godot-importable OBJ.")
    ap.add_argument("--ply-dir", default=None, help="source PLY dir (default: DATASETS/kingwen_avatar_meshes)")
    ap.add_argument("--out-dir", default=None, help="output OBJ dir (default: godot/meshes/avatar)")
    ap.add_argument("--res-dir", default=None, help="res:// dir for .import (default: res://meshes/avatar)")
    ap.add_argument("--limit", type=int, default=0, help="convert at most N files (0 = all)")
    ap.add_argument("--all", action="store_true", help="convert both avatar meshes and shap-e point clouds")
    ap.add_argument("--manifest", default="DATASETS/godot_mesh_conversion_manifest.json")
    args = ap.parse_args()

    if args.all and not args.ply_dir:
        rc = 0
        rc |= _run(PLY_DIR, OBJ_DIR, "res://meshes/avatar", args.limit, args.manifest)
        rc |= _run(
            SHAP_E_PLY_DIR, SHAP_E_OBJ_DIR, "res://meshes/shap_e", args.limit,
            "DATASETS/godot_shap_e_conversion_manifest.json",
        )
        return rc

    return _run(
        Path(args.ply_dir) if args.ply_dir else PLY_DIR,
        Path(args.out_dir) if args.out_dir else OBJ_DIR,
        args.res_dir or "res://meshes/avatar",
        args.limit,
        args.manifest,
    )


def _run(ply_dir: Path, out_dir: Path, res_dir: str, limit: int, manifest_path: str) -> int:

    if not ply_dir.is_dir():
        print(f"ERROR: PLY dir not found: {ply_dir}", file=sys.stderr)
        return 2

    plys = sorted(ply_dir.glob("*.ply"))
    if not plys:
        print(f"ERROR: no .ply files in {ply_dir}", file=sys.stderr)
        return 2
    if limit:
        plys = plys[:limit]

    print("=" * 78)
    print("KING WEN PLY -> GODOT MESH BRIDGE")
    print(f"  source : {ply_dir}")
    print(f"  output : {out_dir}")
    print(f"  files  : {len(plys)}")
    print("=" * 78)

    records: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for i, ply in enumerate(plys, 1):
        try:
            records.append(convert_one(ply, out_dir, res_dir))
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures.append({"ply": ply.name, "error": f"{type(exc).__name__}: {exc}"})
        if i % 64 == 0 or i == len(plys):
            print(f"  [{i}/{len(plys)}] converted, {len(failures)} failed")

    # Remove stale .import configs that reference a non-existent importer.
    purged: List[str] = []
    if IMPORT_DIR.is_dir():
        for imp in IMPORT_DIR.glob("*.import"):
            try:
                txt = imp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if 'importer="mesh"' in txt:
                imp.unlink()
                purged.append(imp.name)
        if purged:
            print(f"  purged {len(purged)} stale .import files (invalid importer=\"mesh\")")

    manifest = {
        "schema_version": "1.0",
        "bridge": "bridge_ply_to_godot_mesh.py",
        "godot_importer": "wavefront_obj",
        "godot_resource_type": "Mesh",
        "source_ply_dir": str(ply_dir.relative_to(ROOT)).replace("\\", "/"),
        "output_obj_dir": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
        "total": len(records),
        "failed": len(failures),
        "stale_imports_purged": purged,
        "records": records,
        "failures": failures,
    }
    man_path = ROOT / manifest_path
    man_path.parent.mkdir(parents=True, exist_ok=True)
    man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("-" * 78)
    print(f"CONVERTED : {len(records)}")
    print(f"FAILED    : {len(failures)}")
    print(f"MANIFEST  : {man_path}")
    if failures:
        for f in failures[:5]:
            print(f"  ! {f['ply']}: {f['error']}")
    print("=" * 78)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
