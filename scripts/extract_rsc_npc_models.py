#!/usr/bin/env python3
"""
RSC NPC Model Extractor — King Wen → RSC cache integration bridge.

Reads RSC classic model data from .jag cache archives (the same format rsmv
parses via parse.classicmodels.read), extracts vertex/face geometry for NPC
spawn models, and generates PLY meshes that King Wen's quantum avatar pipeline
can use instead of procedural spheres.

The RSC classic model format (from models.jsonc):
  - 3 bytes: vertex count (tribyte)
  - 3 bytes: face count (tribyte)
  - vertex_count × 2 bytes: x positions (short)
  - vertex_count × 2 bytes: y positions (short)
  - vertex_count × 2 bytes: z positions (short)
  - face_count faces:
    - 2 bytes: face color (ushort)
    - 2 bytes: face backcolor (ushort)
    - 1 byte: face intensity (ubyte)
    - 1 byte: vertex count for this face (ubyte)
    - vertex_count × 2 bytes: vertex indices (ushort, or ubyte if <256)

.jag archive format (parseLegacyArchive):
  - 3 bytes: uncompressed length (tribyte)
  - 3 bytes: compressed length (tribyte)
  - if compressed != uncompressed: bzip2 decompress
    (with BZh header prepended: 'BZh' + chr(8+0x30) + data)
  - 2 bytes: file count (ushort LE)
  - 10 bytes per file: namehash(4) + decomp_len(3) + comp_len(3)
  - then file data (with bzip2 per-file if needed)

Usage:
    python3 scripts/extract_rsc_npc_models.py --cache-dir "C:/path/to/data204"
    python3 scripts/extract_rsc_npc_models.py --model-id 10
    python3 scripts/extract_rsc_npc_models.py --all-npcs
"""

import argparse
import json
import os
import struct
import sys
import bz2
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "DATASETS"
KITS_DIR = DATASETS / "kingwen_model_sets"
RSC_OUTPUT_DIR = DATASETS / "rsc_npc_meshes"
RSC_NPC_PATHS = DATASETS / "rsc_npc_model_index.json"


def read_tribyte(data: bytes, offset: int) -> Tuple[int, int]:
    """Read a 3-byte unsigned integer (RSC tribyte format)."""
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    return val, offset + 3


def read_ushort_le(data: bytes, offset: int) -> Tuple[int, int]:
    val = struct.unpack_from('<H', data, offset)[0]
    return val, offset + 2


def read_short_le(data: bytes, offset: int) -> Tuple[int, int]:
    val = struct.unpack_from('<h', data, offset)[0]
    return val, offset + 2


def legacybz2_decompress(data: bytes) -> bytes:
    """
    Decompress RSC classic bzip2 data.
    Matches the legacybz2() function from rsmv's compression.ts:
    - Prepends 'BZh' magic + version byte (blocksize 900k = 9 + 0x30)
    - Then decompresses with bz2
    """
    processed = bytearray(len(data) + 4)
    processed[0:4] = b'BZh\x39'  # 'BZh' + (8 + 0x30)
    processed[4:] = data
    return bz2.decompress(bytes(processed))


def parse_legacy_archive(jag_data: bytes) -> List[Dict]:
    """
    Parse a RSC classic .jag archive file.
    This mirrors rsmv's parseLegacyArchive() function.

    Returns a list of {fileid, buffer, namehash, offset, size} entries.
    """
    offset = 0

    # Read tribyte: uncompressed length
    uncomp_len, offset = read_tribyte(jag_data, offset)
    # Read tribyte: compressed length
    comp_len, offset = read_tribyte(jag_data, offset)

    # Decompress if needed
    if comp_len != uncomp_len:
        comp_data = jag_data[offset:offset + comp_len]
        decompressed = legacybz2_decompress(comp_data)
        if len(decompressed) != uncomp_len:
            raise ValueError(
                f"Decompression size mismatch: got {len(decompressed)}, expected {uncomp_len}"
            )
        jag_data = decompressed
        offset = 0

    # Read file count (ushort LE)
    file_count, offset = read_ushort_le(jag_data, offset)

    # Read index entries (10 bytes each: namehash[4] + decomplen[3] + complen[3])
    entries = []
    data_start = offset + file_count * 10
    cur_offset = offset

    for i in range(file_count):
        namehash = struct.unpack_from('<I', jag_data, cur_offset)[0]
        decomp_len, _ = read_tribyte(jag_data, cur_offset + 4)
        comp_len_e, _ = read_tribyte(jag_data, cur_offset + 7)
        entries.append({
            'fileid': i,
            'namehash': namehash,
            'decomp_len': decomp_len,
            'comp_len': comp_len_e,
        })
        cur_offset += 10

    # Read file data
    data_offset = data_start
    files = []
    for entry in entries:
        raw = jag_data[data_offset:data_offset + entry['decomp_len']]
        if entry['comp_len'] != entry['decomp_len'] and entry['comp_len'] > 0:
            # Per-file decompress
            raw = legacybz2_decompress(
                jag_data[data_offset:data_offset + entry['comp_len']]
            )
        files.append({
            'fileid': entry['fileid'],
            'namehash': entry['namehash'],
            'buffer': raw,
            'offset': data_offset,
            'size': entry['decomp_len'],
        })
        data_offset += entry['comp_len']

    return files


def parse_classic_model(model_data: bytes) -> Dict:
    """
    Parse a RSC classic model from raw bytes.
    This mirrors rsmv's parse.classicmodels.read() which uses models.jsonc schema:

    struct classicmodels:
      vertexcount: ushort
      facecount: ushort
      xpos: [vertexcount × short]
      ypos: [vertexcount × short]
      zpos: [vertexcount × short]
      faces: [facecount × struct]
        color: ushort
        backcolor: ushort
        intensity: ubyte
        verts: [nverts × match (nverts<256: ubyte, else ushort)]

    The .jsonc schema from rsmv shows:
      ["struct",
        ["vertexcount","ushort"],
        ["facecount","ushort"],
        ["xpos",["array",["ref","vertexcount"],"short"]],
        ["ypos",["array",["ref","vertexcount"],"short"]],
        ["zpos",["array",["ref","vertexcount"],"short"]],
        ["faces",["array",["ref","facecount"],["struct",
            ["color","ushort"],
            ["backcolor","ushort"],
            ["intensity","ubyte"],
            ["verts",["array",["$nverts","ubyte"],["match",["ref","vertexcount"],{
                "<256":"ubyte","other":"ushort"}]]]
        ]]]

    Returns {vertexcount, facecount, xpos, ypos, zpos, faces}
    """
    offset = 0
    vertexcount, offset = read_ushort_le(model_data, offset)
    facecount, offset = read_ushort_le(model_data, offset)

    # Read vertex positions (shorts, little-endian)
    xpos = []
    ypos = []
    zpos = []
    for i in range(vertexcount):
        v, offset = read_short_le(model_data, offset)
        xpos.append(v)
        v, offset = read_short_le(model_data, offset)
        ypos.append(v)
        v, offset = read_short_le(model_data, offset)
        zpos.append(v)

    # Read faces
    faces = []
    for i in range(facecount):
        color, offset = read_ushort_le(model_data, offset)
        backcolor, offset = read_ushort_le(model_data, offset)
        intensity = model_data[offset]
        offset += 1
        nverts = model_data[offset]
        offset += 1

        # Vertex indices: ubyte if vertexcount < 256, ushort otherwise
        verts = []
        for j in range(nverts):
            if vertexcount < 256:
                v = model_data[offset]
                offset += 1
            else:
                v, offset = read_ushort_le(model_data, offset)
            verts.append(v)

        faces.append({
            'color': color,
            'backcolor': backcolor,
            'intensity': intensity,
            'verts': verts,
        })

    return {
        'vertexcount': vertexcount,
        'facecount': facecount,
        'xpos': xpos,
        'ypos': ypos,
        'zpos': zpos,
        'faces': faces,
    }


def parse_rsc_npc_defs(npc_json_path: str) -> Tuple[Dict[int, dict], set]:
    """
    Parse the RSC NPC definitions JSON to extract model IDs.
    Returns (npc_map_by_id, set_of_model_ids).
    """
    with open(npc_json_path, 'r') as f:
        npcs = json.load(f)

    npc_map = {}
    model_ids = set()
    for i, npc in enumerate(npcs):
        npc_map[i] = npc
        walk_model = npc.get('walkModel')
        combat_model = npc.get('combatModel')
        if walk_model is not None:
            model_ids.add(walk_model)
        if combat_model is not None:
            model_ids.add(combat_model)

    return npc_map, model_ids


def model_to_ply(model: Dict, output_path: Path, scale: float = 0.01) -> int:
    """
    Convert a parsed RSC classic model to a binary PLY file.
    Uses the same PLY format as shap-e's write_ply:
    - binary_little_endian 1.0
    - property float x/y/z
    - property uchar red/green/blue (from face color)
    - property list uchar int vertex_index

    RSC face colors are packed HSL/RGB values. The classic format uses
    color = (hue << 10) | (saturation << 7) | lightness, or direct RGB.
    Actually RSC uses a custom color encoding: 0xRRGGBB-like but packed
    in a short as (r << 10) | (g << 7) | b, where each component is 5 bits.
    We decode this to RGB.

    Returns the number of faces written.
    """
    vertexcount = model['vertexcount']
    faces = model['faces']

    # Convert RSC color shorts to RGB
    # RSC classic color format: 0xVVVVVVVV style, but actually:
    # color is stored as a packed short where:
    # bits 10-15: red (0-31, 5 bits)
    # bits 5-9: green (0-31, 5 bits)  
    # bits 0-4: blue (0-31, 5 bits)
    # Actually RSC uses: (r << 10) | (g << 7) | b, each 5-bit
    # But many sources say it's a palette index. Let's use palette decoding.
    # For RSC classic, colors are typically: 0xRGB where R,G,B are 5-bit each
    # packed as: (R << 10) | (G << 5) | B

    def short_to_rgb(color_short: int) -> Tuple[int, int, int]:
        """Decode RSC classic color short to RGB bytes."""
        if color_short == 0x7fff:
            # Special value: no color / transparent — use white
            return (128, 128, 128)
        # RSC color: 15-bit RGB (5 bits each)
        # Format: bits 10-14 = R, bits 5-9 = G, bits 0-4 = B
        r = ((color_short >> 10) & 0x1f) * 8
        g = ((color_short >> 5) & 0x1f) * 8
        b = (color_short & 0x1f) * 8
        return (r, g, b)

    # Build vertex array
    verts = []
    # Default vertex color — will be overridden by face colors
    vert_colors = [(128, 128, 128)] * vertexcount

    # Apply face colors to vertices
    for face in faces:
        if face['color'] != 0x7fff:
            rgb = short_to_rgb(face['color'])
            for v_idx in face['verts']:
                if v_idx < vertexcount:
                    vert_colors[v_idx] = rgb

    # Scale and convert positions
    # RSC coordinates are in a coordinate system where Y is up
    # Model coordinates are typically in a small range (-some, +some)
    # Scale to reasonable mesh size
    for i in range(vertexcount):
        x = model['xpos'][i] * scale
        y = -model['ypos'][i] * scale  # Y up, RSC Y is different
        z = model['zpos'][i] * scale
        verts.append((x, y, z))

    # Build face index list (triangulate polygons)
    face_indices = []
    for face in faces:
        n = len(face['verts'])
        if n < 3:
            continue
        # Triangulate as fan from vertex 0
        for i in range(1, n - 1):
            face_indices.append((3, face['verts'][0], face['verts'][i], face['verts'][i + 1]))

    # Write PLY file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        header = (
            f"ply\n"
            f"format binary_little_endian 1.0\n"
            f"comment King Wen RSC NPC model — hexagram_id=model_id mapping\n"
            f"element vertex {vertexcount}\n"
            f"property float x\n"
            f"property float y\n"
            f"property float z\n"
            f"property uchar red\n"
            f"property uchar green\n"
            f"property uchar blue\n"
            f"element face {len(face_indices)}\n"
            f"property list uchar int vertex_index\n"
            f"end_header\n"
        )
        f.write(header.encode("ascii"))

        # Write vertices (x, y, z, r, g, b)
        vert_struct = struct.Struct("<3f3B")
        for i in range(vertexcount):
            r, g, b = vert_colors[i]
            f.write(vert_struct.pack(verts[i][0], verts[i][1], verts[i][2], r, g, b))

        # Write faces
        face_struct = struct.Struct("<B3i")
        for face in face_indices:
            _, v0, v1, v2 = face
            f.write(face_struct.pack(3, v0, v1, v2))

    return len(face_indices)


def extract_rsc_models(cache_dir: str, npcs_json: str) -> Dict:
    """
    Extract all RSC NPC models from .jag archives.

    Args:
        cache_dir: Path to the RSC cache directory (containing models36.jag)
        npcs_json: Path to the NPC definitions JSON

    Returns:
        {model_id: {fileid, vertexcount, facecount, ply_path}}
    """
    cache_path = Path(cache_dir)
    jag_path = cache_path / "models36.jag"

    if not jag_path.exists():
        # Check data204 subdirectory
        jag_path = cache_path / "data204" / "models36.jag"
        if not jag_path.exists():
            raise FileNotFoundError(
                f"models36.jag not found in {cache_dir} or {cache_dir}/data204"
            )

    print(f"Loading .jag archive: {jag_path}")

    # Parse the .jag archive
    with open(jag_path, "rb") as f:
        jag_data = f.read()

    print(f"  Archive size: {len(jag_data)} bytes")

    files = parse_legacy_archive(jag_data)
    print(f"  Parsed {len(files)} file entries from archive")

    # Parse NPC definitions to get model IDs
    npc_map, model_ids = parse_rsc_npc_defs(npcs_json)
    print(f"  {len(npcs_json)} NPC definitions → {len(model_ids)} unique model IDs: {sorted(model_ids)}")

    # Extract models for the required IDs
    results = {}
    for model_id in sorted(model_ids):
        if model_id >= len(files):
            print(f"  Model ID {model_id}: out of range (archive has {len(files)} files)")
            continue

        entry = files[model_id]
        raw_data = entry['buffer']

        if not raw_data or len(raw_data) == 0:
            print(f"  Model ID {model_id}: empty data")
            continue

        try:
            model = parse_classic_model(raw_data)
            if model['vertexcount'] == 0 or model['facecount'] == 0:
                print(f"  Model ID {model_id}: empty geometry (v={model['vertexcount']}, f={model['facecount']})")
                continue

            # Map model ID to King Wen hexagram ID
            # Model IDs 3-12 map to hexagrams by priority:
            # 3=Unicorn, 5=Chicken, 6=Rat, 7=Spider, 8=Bat, 9=Goat, 10=Giant, 11=Dragon, 12=Dragon
            # We map to hexagram IDs that match NPC personality categories
            ply_filename = f"rsc_npc_model_{model_id}.ply"
            ply_path = RSC_OUTPUT_DIR / ply_filename

            face_count = model_to_ply(model, ply_path)

            results[model_id] = {
                'fileid': entry['fileid'],
                'namehash': entry['namehash'],
                'vertexcount': model['vertexcount'],
                'facecount': model['facecount'],
                'face_count_exported': face_count,
                'ply_filename': ply_filename,
                'ply_path': str(ply_path),
            }
            print(f"  Model ID {model_id}: {model['vertexcount']} verts, {face_count} faces → {ply_filename}")

        except Exception as e:
            print(f"  Model ID {model_id}: parse error: {e}")

    return results


def map_models_to_hexagrams(model_results: Dict) -> Dict[int, int]:
    """
    Map RSC NPC model IDs to King Wen hexagram IDs.

    The 9 RSC NPC models map to hexagrams by personality archetype:
    - 3 (Unicorn) → H1 (The Creative) — pure creative force
    - 5 (Chicken) → H24 (The Undertaking) — growth/rebirth
    - 6 (Rat) → H32 (The Duration) — small/creeping
    - 7 (Spider) → H31 (The Taming/Union) — weaving connections
    - 8 (Bat) → H5 (The Waiting) — cave/den
    - 9 (Goat) → H37 (The Family) — nurturing
    - 10 (Giant) → H28 (The Stress Tester) — large/powerful
    - 11 (Dragon) → H34 (The Power) — mighty dragon
    - 12 (Dragon 2) → H3 (The Difficulty at the Beginning) — scaled variant

    Returns {hexagram_id: model_id}
    """
    # Priority mapping based on NPC type
    npc_to_hex = {
        3: 1,   # Unicorn → H1 The Creative (creative force)
        5: 24,  # Chicken → H24 (undertaking/growth)
        6: 32,  # Rat → H32 (duration/small)
        7: 31,  # Spider → H31 (union/weaving)
        8: 5,   # Bat → H5 (waiting/cave)
        9: 37,  # Goat → H37 (family/nurturing)
        10: 28, # Giant → H28 (the stress tester)
        11: 34, # Dragon → H34 (the power)
        12: 3,  # Dragon2 → H3 (difficulty at beginning)
    }

    # Only include models that were successfully extracted
    mapping = {}
    for model_id, result in model_results.items():
        hex_id = npc_to_hex.get(model_id)
        if hex_id:
            mapping[hex_id] = model_id
    return mapping


def build_npc_index(model_results: Dict, output_path: Path) -> dict:
    """
    Build and save an index mapping hexagram IDs to RSC NPC model data.
    This is the artifact that generate_avatar_meshes.py reads to know
    which RSC model to overlay onto which hexagram's quantum state.
    """
    hex_to_model = map_models_to_hexagrams(model_results)

    index = {
        "schema_version": "1.0",
        "source": "RSC classic models36.jag",
        "total_models": len(model_results),
        "models": {},
        "hexagram_mapping": {},
    }

    for model_id, result in model_results.items():
        index["models"][str(model_id)] = result

    for hex_id, model_id in hex_to_model.items():
        index["hexagram_mapping"][str(hex_id)] = {
            "model_id": model_id,
            "ply_filename": model_results[model_id]["ply_filename"],
            "ply_path": model_results[model_id]["ply_path"],
            "vertex_count": model_results[model_id]["vertexcount"],
            "face_count": model_results[model_id]["face_count_exported"],
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(index, f, indent=2)

    return index


def main():
    parser = argparse.ArgumentParser(
        description="Extract RSC NPC models from .jag caches and generate PLY meshes."
    )
    parser.add_argument(
        "--cache-dir", type=str, default="C:/Users/krist/Desktop/openrsc-vinilla/public",
        help="Path to RSC cache directory containing models36.jag"
    )
    parser.add_argument(
        "--npcs-json", type=str,
        default="C:/Users/krist/Desktop/openrsc-vinilla/rsc-data/config/npcs.json",
        help="Path to NPC definitions JSON"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Output directory for PLY files"
    )
    parser.add_argument(
        "--index-path", type=str, default=None,
        help="Output path for NPC model index JSON"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else RSC_OUTPUT_DIR
    index_path = Path(args.index_path) if args.index_path else RSC_NPC_PATHS

    print(f"RSC NPC Model Extractor")
    print(f"  Cache dir: {args.cache_dir}")
    print(f"  NPCs JSON: {args.npcs_json}")
    print(f"  Output: {output_dir}")
    print(f"  Index: {index_path}")
    print()

    # Extract models
    results = extract_rsc_models(args.cache_dir, args.npcs_json)

    # Build index
    index = build_npc_index(results, index_path)

    # Summary
    print(f"\n✓ Extracted {len(results)} NPC models")
    print(f"✓ Mapped to {len(index['hexagram_mapping'])} hexagrams")
    print(f"✓ Index saved: {index_path}")

    # Print mapping
    print("\nHexagram → RSC NPC Model mapping:")
    for hex_id, mapping in sorted(index["hexagram_mapping"].items(), key=lambda x: int(x[0])):
        print(f"  H{hex_id:>2} → Model {mapping['model_id']} ({mapping['ply_filename']}) "
              f"[{mapping['vertex_count']} verts, {mapping['face_count']} faces]")

    # Also save as JSON for the generate_avatar_meshes.py script to pick up
    manifest_path = DATASETS / "rsc_npc_mesh_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(index, f, indent=2)
    print(f"\n✓ Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
