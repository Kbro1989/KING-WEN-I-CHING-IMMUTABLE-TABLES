#!/usr/bin/env python3
"""Hardened desktop-3D-engine bridge with zero fallbacks.

Rules:
- No silent defaults. Missing required hexagram fields halt immediately.
- BVH bounds come from real PLY vertex data, not hardcoded values.
- All dict access is direct; any missing key is a loud failure.
"""

from __future__ import annotations

import json
import math
import sys
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

_TABLE_PATH = Path(__file__).resolve().parents[1] / "kingwen_ternary_tables_complete.py"
_spec = spec_from_file_location("kingwen_ternary_tables_complete", _TABLE_PATH)
_mod = module_from_spec(_spec)
sys.modules["kingwen_ternary_tables_complete"] = _mod
_spec.loader.exec_module(_mod)
HEXAGRAM_BASE = _mod.HEXAGRAM_BASE

_REQUIRED_HEX_FIELDS = (
    "upper_idx",
    "lower_idx",
    "category",
    "action",
    "name",
    "binary_bottom_to_top",
    "upper_trigram",
    "lower_trigram",
)
_INTEGRITY = "ZERO_FALLBACKS"
_BVH_SOURCE = "PLY_VERTEX_DATA"
_BVH_METHOD = "ACTUAL_BOUNDS_FROM_VERTICES"


def validate_hexagram_base(hex_info: dict, hexagram_id: int) -> None:
    missing = [k for k in _REQUIRED_HEX_FIELDS if k not in hex_info]
    if missing:
        raise KeyError(f"hexagram {hexagram_id} missing required fields: {missing}")


def parse_ply_vertices(ply_path: Path) -> tuple[list[tuple[float, float, float]], int]:
    if not ply_path.exists():
        raise FileNotFoundError(f"PLY missing: {ply_path}")

    raw = ply_path.read_bytes().decode("utf-8", errors="strict")
    header_end = raw.index("end_header") + len("end_header")
    header = raw[:header_end]

    vertex_count = 0
    for line in header.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == "element" and parts[1] == "vertex":
            vertex_count = int(parts[2])
            break

    body = raw[header_end:]
    vertices: list[tuple[float, float, float]] = []
    for line in body.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
        except ValueError:
            continue
        vertices.append((x, y, z))

    if vertex_count and len(vertices) != vertex_count:
        raise ValueError(
            f"{ply_path.name}: header vertex_count={vertex_count}, parsed={len(vertices)}"
        )
    if not vertices:
        raise ValueError(f"{ply_path.name}: no vertices parsed")
    return vertices, len(vertices)


def compute_bvh_from_vertices(
    vertices: list[tuple[float, float, float]], hexagram_id: int
) -> dict:
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    cz = (min_z + max_z) / 2.0
    radius = max(math.dist((cx, cy, cz), v) for v in vertices)
    return {
        "hexagram_id": hexagram_id,
        "aabb": {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "min_z": min_z,
            "max_z": max_z,
        },
        "center": {"x": cx, "y": cy, "z": cz},
        "radius": radius,
        "vertex_count": len(vertices),
    }


def build_manifest(
    base: dict,
    ply_root: Path,
    output_path: Path,
) -> dict:
    entries = []
    bvh_entries = []

    for hex_id in range(1, 65):
        hex_info = base[hex_id]
        validate_hexagram_base(hex_info, hex_id)

        category = hex_info["category"]
        action = hex_info["action"]

        ply_path = ply_root / f"depth_cloud_hex_{hex_id:02d}.ply"
        vertices, vertex_count = parse_ply_vertices(ply_path)
        bvh = compute_bvh_from_vertices(vertices, hex_id)

        entries.append(
            {
                "hexagram_id": hex_id,
                "name": hex_info["name"],
                "category": category,
                "action": action,
                "upper_trigram": hex_info["upper_trigram"],
                "lower_trigram": hex_info["lower_trigram"],
                "binary_bottom_to_top": hex_info["binary_bottom_to_top"],
                "vertex_count": vertex_count,
                "ply_path": str(ply_path),
            }
        )
        bvh_entries.append(bvh)

    manifest = {
        "integrity": _INTEGRITY,
        "validation": "64/64 hexagrams direct-access verified",
        "bvh_source": _BVH_SOURCE,
        "bvh_method": _BVH_METHOD,
        "count": len(entries),
        "entries": entries,
        "bvh": bvh_entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ply_root = root / "DATASETS" / "depth_pointclouds"
    output_path = root / "DATASETS" / "desktop_3d_engines_manifest.json"

    build_manifest(HEXAGRAM_BASE, ply_root, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
