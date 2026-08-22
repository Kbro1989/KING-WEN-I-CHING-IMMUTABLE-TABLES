"""
transform_object_rsmv.py — King Wen shap-E PLY -> rsmv `models` wire format.

This is the STRUCTURAL COMPLIANCE LAYER. It does no generation of its own;
it reads a real shap-e point cloud (.ply, ascii, 729 verts w/ rgb) and
repacks the float geometry into the exact TypeScript struct declared in
rsmv/generated/models.d.ts:

    type models = {
      format, version, always_0f, meshCount,
      unkCount0..4,
      meshes: [{
        unkint, materialArgument, faceCount, hasVertices,
        hasVertexAlpha, hasFaceBones, hasBoneIds, isHidden, hasSkin,
        colourBuffer: Uint16Array | null,
        alphaBuffer: Uint8Array | null,
        faceboneidBuffer: Uint16Array | null,
        indexBuffers: Uint16Array[],
        vertexCount, positionBuffer: Int16Array | null,
        normalBuffer, tagentBuffer, uvBuffer, boneidBuffer, skin
      }] | null
    }

No RNG. No placeholder verts. The source data is the shap-e PLY; the output
is the same data in rsmv's native integer-buffer representation.

Quantization:
  - positionBuffer: float xyz -> Int16. We fit the cloud's bbox into the
    signed-int16 cube [-32768, 32767] with a uniform scale, preserving the
    relative shape. RSMV stores positions as Int16Array.
  - colourBuffer: uchar rgb (0-255) -> Uint16 RGB555 with high bit set
    (standard RSMV packed color: 0x8000 | (r>>3)<<10 | (g>>3)<<5 | (b>>3)).
  - indexBuffers: point cloud has no faces -> one empty Uint16Array
    (meshCount=1, faceCount=0). Structurally valid; rsmv accepts it.

Run:
  python scripts/transform_object_rsmv.py \
      --ply DATASETS/kingwen_3d_meshes/shap_e_hex_01.ply \
      --out DATASETS/kingwen_rsmv_models/hex_01_models.json
"""

from __future__ import annotations
import argparse
import json
import struct
from pathlib import Path


def read_ply_ascii(path: Path) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    """Parse an ascii PLY point cloud with x/y/z + red/green/blue."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines[0].strip() != "ply":
        raise ValueError(f"{path}: not a PLY file")
    vertex_count = 0
    props: list[str] = []
    in_header = True
    data_start = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == "end_header":
            in_header = False
            data_start = i + 1
            break
        if s.startswith("element vertex"):
            vertex_count = int(s.split()[2])
        elif s.startswith("property"):
            # property <type> <name>
            props.append(s.split()[2])
    if vertex_count == 0 or not props:
        raise ValueError(f"{path}: bad header (count={vertex_count}, props={props})")
    if vertex_count > len(lines) - data_start:
        raise ValueError(f"{path}: declared {vertex_count} verts but only "
                         f"{len(lines) - data_start} data lines")
    verts: list[tuple[float, float, float]] = []
    cols: list[tuple[int, int, int]] = []
    xi = props.index("x") if "x" in props else None
    yi = props.index("y") if "y" in props else None
    zi = props.index("z") if "z" in props else None
    ri = props.index("red") if "red" in props else None
    gi = props.index("green") if "green" in props else None
    bi = props.index("blue") if "blue" in props else None
    if None in (xi, yi, zi):
        raise ValueError(f"{path}: missing x/y/z in props {props}")
    for j in range(vertex_count):
        parts = lines[data_start + j].split()
        pts = [float(parts[k]) for k in (xi, yi, zi)]
        verts.append((pts[0], pts[1], pts[2]))
        if None not in (ri, gi, bi):
            cols.append((int(parts[ri]), int(parts[gi]), int(parts[bi])))
        else:
            cols.append((255, 255, 255))
    return verts, cols


def quantize_positions(verts: list[tuple[float, float, float]]) -> tuple[list[int], float, tuple[float, float, float]]:
    """Fit float xyz into signed-int16 range with uniform scale + offset.

    Returns (flat_int16_list, scale, center_offset).
    """
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    cx, cy, cz = sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)
    max_abs = max(
        max(abs(x - cx) for x in xs),
        max(abs(y - cy) for y in ys),
        max(abs(z - cz) for z in zs),
    )
    if max_abs == 0.0:
        return [0] * (len(verts) * 3), 1.0, (cx, cy, cz)
    # fit half-extent into 30000 to leave headroom (RSMV coords are not full-range)
    scale = 30000.0 / max_abs
    out: list[int] = []
    for (x, y, z) in verts:
        out.append(int(round((x - cx) * scale)))
        out.append(int(round((y - cy) * scale)))
        out.append(int(round((z - cz) * scale)))
    return out, scale, (cx, cy, cz)


def pack_color(r: int, g: int, b: int) -> int:
    """RSMV packed RGB555 with high bit set (0x8000 | r5 g5 b5)."""
    r5 = (r >> 3) & 0x1F
    g5 = (g >> 3) & 0x1F
    b5 = (b >> 3) & 0x1F
    return 0x8000 | (r5 << 10) | (g5 << 5) | b5


def build_rsmv_models(verts, cols, source_hex: int) -> dict:
    """Emit the exact struct from rsmv/generated/models.d.ts as JSON."""
    flat_pos, scale, center = quantize_positions(verts)
    position_buffer = flat_pos  # Int16Array payload (ints in [-32768,32767])
    colour_buffer = [pack_color(r, g, b) for (r, g, b) in cols]  # Uint16Array payload
    vertex_count = len(verts)

    mesh = {
        "unkint": 0,
        "materialArgument": 0,
        "faceCount": 0,                 # point cloud: no faces
        "hasVertices": 1,
        "hasVertexAlpha": 0,
        "hasFaceBones": 0,
        "hasBoneIds": 0,
        "isHidden": 0,
        "hasSkin": 0,
        "colourBuffer": colour_buffer,  # Uint16Array
        "alphaBuffer": None,            # Uint8Array | null
        "faceboneidBuffer": None,       # Uint16Array | null
        "indexBuffers": [[]],           # Uint16Array[] — one empty buffer (structurally valid)
        "vertexCount": vertex_count,
        "positionBuffer": position_buffer,  # Int16Array
        "normalBuffer": None,           # (Int8|Int16)Array | null
        "tagentBuffer": None,
        "uvBuffer": None,               # (Uint16|Float32)Array | null
        "boneidBuffer": None,           # Uint16Array | null
        "skin": None,
    }

    models = {
        "format": 1,
        "version": 1,
        "always_0f": 0x0F,
        "meshCount": 1,
        "unkCount0": 0,
        "unkCount1": 0,
        "unkCount2": 0,
        "unkCount3": 0,
        "unkCount4": 0,
        "meshes": [mesh],
        "_meta": {  # provenance only; not part of rsmv.d.ts, strip before wire use
            "source": "shap-e PLY point cloud",
            "hexagram_id": source_hex,
            "vertex_count": vertex_count,
            "quant_scale": scale,
            "center_offset": list(center),
            "note": "positions quantized to Int16; colors packed RGB555; point cloud has no faces",
        },
    }
    return models


def main() -> None:
    ap = argparse.ArgumentParser(description="shap-e PLY -> rsmv models wire format")
    ap.add_argument("--ply", required=True, type=Path, help="source shap-e .ply point cloud")
    ap.add_argument("--out", required=True, type=Path, help="output rsmv models .json")
    ap.add_argument("--hex", type=int, default=0, help="hexagram id for provenance")
    args = ap.parse_args()

    if not args.ply.exists():
        raise SystemExit(f"PLY not found: {args.ply}")
    verts, cols = read_ply_ascii(args.ply)
    models = build_rsmv_models(verts, cols, args.hex)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(models, indent=2), encoding="utf-8")

    m = models["_meta"]
    print(f"OK {args.ply.name} -> {args.out}")
    print(f"  verts={m['vertex_count']} scale={m['quant_scale']:.4f} "
          f"center={tuple(round(c,3) for c in m['center_offset'])}")


if __name__ == "__main__":
    main()
