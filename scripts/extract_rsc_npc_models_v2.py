#!/usr/bin/env python3
"""
RSC NPC Model Extractor for King Wen quantum avatar pipeline.
Reads models36.jag archive and extracts NPC models referenced by npcs.json,
converting them to PLY files for integration with shap-e and King Wen avatar mesh system.

Format based on:
- rsmv classicloader.ts: ClassicFileSource.getFileArchive() -> parseLegacyArchive(jagfile, major, true)
- rsmv legacycache.ts: parseLegacyArchive() with big-endian index fields
- rsmv opcodes/classicmodels.jsonc: vertexcount(ushort LE), facecount(ushort LE), 
  x/ypos(short LE), faces: nverts(ubyte), color(ushort LE), backcolor(ushort LE), intensity(ubyte), verts(ubyte or ushort LE)
- rsmv 3d/modeltothree.ts: getArchiveById(0, classicGroups.models) -> arch[id].buffer -> parseRT2Model()
- rsmv 3d/rt2model.ts: parseRT2Model calls parse.classicmodels.read()
"""
import struct
import bz2
import json
import os
import sys

def read_tribyte_be(data, offset):
    """Read 3-byte big-endian signed integer (rsmv Stream.readIntBE)."""
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    if val & 0x800000:
        val -= 0x1000000
    return val, offset + 3

def read_uint_be(data, offset):
    """Read 4-byte big-endian unsigned integer."""
    val = (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]
    return val, offset + 4

def read_ushort_be(data, offset):
    """Read 2-byte big-endian unsigned integer (rsmv Stream.readUShort(true))."""
    return (data[offset] << 8) | data[offset + 1], offset + 2

def read_ushort_le(data, offset):
    """Read 2-byte little-endian unsigned integer."""
    return struct.unpack_from('<H', data, offset)[0], offset + 2

def read_short_le(data, offset):
    """Read 2-byte little-endian signed integer."""
    return struct.unpack_from('<h', data, offset)[0], offset + 2

def legacybz2(raw_data):
    """Decompress RSC legacy bzip2 data (adds BZh9 header prefix)."""
    processed = bytearray(len(raw_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = raw_data
    return bz2.decompress(bytes(processed))

def parse_legacy_archive(file_data):
    """
    Parse legacy .jag archive (parseLegacyArchive with isclassic=true).
    
    Outer format:
    - 3-byte BE tribyte: uncompressed_length
    - 3-byte BE tribyte: compressed_length
    - If compressed != uncompressed: bzip2 decompress (with BZh9 prefix)
    
    Inner format (after decompression):
    - 2-byte BE ushort: file_count
    - file_count * 10 bytes: index entries
      Each entry: namehash(4 BE uint) + decomplen(3 BE tribyte) + complen(3 BE tribyte)
    - file data: sequential, each file read by complen bytes (bz2 decompressed if decomplen != complen)
    """
    offset = 0
    uncomp_len, offset = read_tribyte_be(file_data, 0)
    comp_len, offset = read_tribyte_be(file_data, 3)
    
    if comp_len != uncomp_len:
        comp_data = file_data[offset:offset + comp_len]
        data = legacybz2(comp_data)
        if len(data) != uncomp_len:
            print(f"WARNING: decompress mismatch! got {len(data)}, expected {uncomp_len}")
        offset = 0
    else:
        data = file_data
        offset = 6
    
    file_count, offset = read_ushort_be(data, offset)
    
    indices = []
    for i in range(file_count):
        namehash, offset = read_uint_be(data, offset)
        subdecomplen, offset = read_tribyte_be(data, offset)
        subcomplen, offset = read_tribyte_be(data, offset)
        indices.append((namehash, subdecomplen, subcomplen))
    
    data_start = offset
    files = []
    cur = data_start
    
    for i, (namehash, dl, cl) in enumerate(indices):
        raw_buf = data[cur:cur + cl]
        cur += cl
        
        if dl != cl and len(raw_buf) > 0:
            try:
                raw_buf = legacybz2(raw_buf)
            except Exception:
                pass  # Keep raw data
        
        files.append({
            'fileid': i,
            'namehash': namehash,
            'buffer': raw_buf,
            'size': len(raw_buf),
        })
    
    return files

def parse_classic_model(buf):
    """
    Parse RSC classic model format per rsmv classicmodels.jsonc opcode definition.
    
    Format (all little-endian):
    - vertexcount: ushort
    - facecount: ushort
    - xpos: short[vertexcount]
    - ypos: short[vertexcount]
    - zpos: short[vertexcount]
    - faces[facecount] (chunked format):
      - nverts: ubyte
      - color: ushort
      - backcolor: ushort
      - intensity: ubyte
      - verts: array of (ubyte if vertexcount < 256, else ushort)
    """
    offset = 0
    vertexcount, offset = read_ushort_le(buf, offset)
    facecount, offset = read_ushort_le(buf, offset)
    
    xpos = []
    ypos = []
    zpos = []
    
    for i in range(vertexcount):
        x, offset = read_short_le(buf, offset)
        xpos.append(x)
        y, offset = read_short_le(buf, offset)
        ypos.append(y)
        z, offset = read_short_le(buf, offset)
        zpos.append(z)
    
    use_ushort_verts = vertexcount >= 256
    
    faces = []
    for i in range(facecount):
        nverts = buf[offset]
        offset += 1
        color, offset = read_ushort_le(buf, offset)
        backcolor, offset = read_ushort_le(buf, offset)
        intensity = buf[offset]
        offset += 1
        
        verts = []
        for j in range(nverts):
            if use_ushort_verts:
                v, offset = read_ushort_le(buf, offset)
            else:
                v = buf[offset]
                offset += 1
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

def write_ply(filepath, model, color_id=None):
    """Write model as PLY file (binary little-endian)."""
    vc = model['vertexcount']
    fc = model['facecount']
    
    # Collect all triangle faces (convert n-gons to triangles)
    triangles = []
    for face in model['faces']:
        verts = face['verts']
        color = face['color']
        if len(verts) < 3:
            continue
        # Fan triangulation
        for i in range(1, len(verts) - 1):
            triangles.append((verts[0], verts[i], verts[i + 1], color))
    
    with open(filepath, 'wb') as f:
        header = f"ply\nformat binary_little_endian 1.0\n"
        header += f"element vertex {vc}\n"
        header += "property float x\nproperty float y\nproperty float z\n"
        header += "property uchar red\nproperty uchar green\nproperty uchar blue\n"
        header += f"element face {len(triangles)}\n"
        header += "property list uchar int vertex_index\nend_header\n"
        f.write(header.encode())
        
        for i in range(vc):
            f.write(struct.pack('<fff', float(model['xpos'][i]), float(model['ypos'][i]), float(model['zpos'][i])))
        
        for v0, v1, v2, color in triangles:
            # Unpack HSL color to RGB (simple mapping for now)
            # In RSC, colors are packed HSL (5-5-5-1 format)
            # color & 0x8000 is opaque flag
            # bits 0-4: red, 5-9: green, 10-14: blue
            if color & 0x8000:
                r = ((color >> 10) & 0x1f) * 8
                g = ((color >> 5) & 0x1f) * 8
                b = (color & 0x1f) * 8
            else:
                r, g, b = 255, 255, 255
            rgb = bytes([r, g, b])
            
            f.write(struct.pack('<Biii', 3, v0, v1, v2))

    return vc, len(triangles)

def extract_npc_models(jag_path, npcs_json_path, output_dir):
    """Extract NPC models from .jag archive and write PLY files."""
    # Load .jag archive
    with open(jag_path, 'rb') as f:
        raw = f.read()
    
    files = parse_legacy_archive(raw)
    print(f"Parsed {len(files)} files from {jag_path}")
    
    # Load NPC data
    npcs = json.load(open(npcs_json_path))
    walk_models = set()
    combat_models = set()
    for npc in npcs:
        if npc.get('walkModel') is not None:
            walk_models.add(npc['walkModel'])
        if npc.get('combatModel') is not None:
            combat_models.add(npc['combatModel'])
    
    all_models = sorted(walk_models | combat_models)
    print(f"Unique NPC model IDs: {all_models}")
    
    # Extract each model
    manifest = []
    for mid in all_models:
        if mid >= len(files):
            print(f"  Model {mid}: OUT OF RANGE (max {len(files)-1})")
            continue
        
        buf = files[mid]['buffer']
        if len(buf) < 4:
            print(f"  Model {mid}: too short ({len(buf)} bytes)")
            continue
        
        # Try to parse
        try:
            model = parse_classic_model(buf)
        except Exception as e:
            print(f"  Model {mid}: PARSE ERROR: {e}")
            continue
        
        vc = model['vertexcount']
        fc = model['facecount']
        
        # Sanity check
        if vc > 10000 or fc > 100000 or vc == 0:
            print(f"  Model {mid}: INVALID (vc={vc}, fc={fc})")
            continue
        
        # Write PLY
        output_path = os.path.join(output_dir, f"npc_model_{mid}.ply")
        vcount, tcount = write_ply(output_path, model)
        print(f"  Model {mid}: vc={vc}, fc={fc} -> PLY: {vcount} verts, {tcount} triangles")
        
        manifest.append({
            'model_id': mid,
            'fileid': mid,
            'vertexcount': vc,
            'facecount': fc,
            'triangle_count': tcount,
            'ply_path': output_path,
            'namehash': files[mid]['namehash'],
        })
    
    return manifest

if __name__ == '__main__':
    jag_path = 'C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag'
    npcs_json_path = 'C:/Users/krist/Desktop/openrsc-vinilla/rsc-data/config/npcs.json'
    output_dir = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/rsc_npc_meshes'
    
    os.makedirs(output_dir, exist_ok=True)
    
    manifest = extract_npc_models(jag_path, npcs_json_path, output_dir)
    
    # Write manifest
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nWrote {len(manifest)} meshes + manifest to {output_dir}")
