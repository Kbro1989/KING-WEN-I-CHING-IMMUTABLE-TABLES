#!/usr/bin/env python3
"""
Extract RSC NPC models from .jag archives using chunkedarray (columnar) face format.
Fixed: faces use chunkedarray — nverts for ALL faces, then color for ALL, then backcolor, then intensity, then verts for ALL.

Output: PLY files for each model, one file per NPC.
"""
import struct
import bz2
import os
import sys
import json

def read_ushort_be(data, offset):
    return (data[offset] << 8) | data[offset + 1], offset + 2

def read_short_be(data, offset):
    val = (data[offset] << 8) | data[offset + 1]
    if val > 32767:
        val -= 65536
    return val, offset + 2

def read_tribyte_be_unsigned(data, offset):
    """Read unsigned 3-byte big-endian integer."""
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    return val, offset + 3

def legacybz2(raw_data):
    """Decompress a single BZh stream from the legacy format."""
    processed = bytearray(len(raw_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = raw_data
    return bz2.decompress(bytes(processed))

def decompress_archive(path):
    """Decompress the .jag archive into a bytes buffer."""
    with open(path, 'rb') as f:
        raw = f.read()
    
    # The .jag format: BZh9 (4 bytes) + 4 bytes + compressed data
    # legacycache.ts does: BZ2 decompression with "BZh\x39" header prepended
    comp_data = raw[6:]  # skip header bytes
    processed = bytearray(len(comp_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = comp_data
    return bz2.decompress(bytes(processed))

def parse_archive(data):
    """Parse the decompressed archive into (namehash, comp_len) entries."""
    file_count = (data[0] << 8) | data[1]
    entries = []
    offset = 2
    for i in range(file_count):
        namehash = struct.unpack_from('>I', data, offset)[0]
        decomp_len = read_tribyte_be_unsigned(data, offset + 4)[0]
        comp_len = read_tribyte_be_unsigned(data, offset + 7)[0]
        entries.append({
            'fileid': i,
            'namehash': namehash,
            'comp_len': comp_len,
            'decomp_len': decomp_len
        })
        offset += 10
    
    data_start = 2 + file_count * 10
    return entries, data_start

def get_file_buffer(data, entries, data_start, fileid):
    """Extract the buffer for a specific file ID."""
    entry = entries[fileid]
    offset = data_start
    for i in range(fileid):
        offset += entries[i]['comp_len']
    return data[offset:offset + entry['comp_len']]

def parse_rsc_model(buf):
    """
    Parse an RSC classic model buffer.
    
    Format (classicmodels.jsonc):
    - vertexcount (ushort BE)
    - facecount (ushort BE)
    - xpos array (vertexcount × short BE)
    - ypos array (vertexcount × short BE)
    - zpos array (vertexcount × short BE)
    - faces: chunkedarray with 5 groups:
      Group 1: nverts (ubyte, facecount entries)  -- per-face vertex count
      Group 2: color (ushort BE, facecount entries)
      Group 3: backcolor (ushort BE, facecount entries)
      Group 4: intensity (ubyte, facecount entries)
      Group 5: verts (variable array, facecount entries, each nverts × (ubyte/ushort))
    """
    offset = 0
    vc = (buf[offset] << 8) | buf[offset + 1]
    offset += 2
    fc = (buf[offset] << 8) | buf[offset + 1]
    offset += 2
    
    if vc == 0 or fc == 0:
        return None
    
    # Vertex arrays: xpos, ypos, zpos (each vertexcount × short)
    xpos = []
    ypos = []
    zpos = []
    for i in range(vc):
        xpos.append(read_short_be(buf, offset)[0])
        offset += 2
    for i in range(vc):
        ypos.append(read_short_be(buf, offset)[0])
        offset += 2
    for i in range(vc):
        zpos.append(read_short_be(buf, offset)[0])
        offset += 2
    
    use_ushort = vc >= 256  # vertex indices use ushort if vertexcount >= 256
    
    # Face data: chunkedarray (columnar)
    # Group 1: all nverts (facecount × ubyte)
    nverts_list = []
    for i in range(fc):
        nverts_list.append(buf[offset])
        offset += 1
    
    # Group 2: all color (facecount × ushort BE)
    color_list = []
    for i in range(fc):
        color_list.append(read_ushort_be(buf, offset)[0])
        offset += 2
    
    # Group 3: all backcolor (facecount × ushort BE)
    backcolor_list = []
    for i in range(fc):
        backcolor_list.append(read_ushort_be(buf, offset)[0])
        offset += 2
    
    # Group 4: all intensity (facecount × ubyte)
    intensity_list = []
    for i in range(fc):
        intensity_list.append(buf[offset])
        offset += 1
    
    # Group 5: all verts (facecount entries, each nverts × index_size)
    faces = []
    for i in range(fc):
        nv = nverts_list[i]
        face_verts = []
        for vi in range(nv):
            if use_ushort:
                v, offset = read_ushort_be(buf, offset)
            else:
                v = buf[offset]
                offset += 1
            face_verts.append(v)
        faces.append({
            'nverts': nv,
            'color': color_list[i],
            'backcolor': backcolor_list[i],
            'intensity': intensity_list[i],
            'verts': face_verts
        })
    
    return {
        'vertexcount': vc,
        'facecount': fc,
        'xpos': xpos,
        'ypos': ypos,
        'zpos': zpos,
        'faces': faces
    }

def write_ply(model, filepath):
    """Write model as binary PLY file."""
    verts = list(zip(model['xpos'], model['ypos'], model['zpos']))
    faces = model['faces']
    
    lines = []
    lines.append("ply")
    lines.append("format binary_little_endian 1.0")
    lines.append("comment King Wen RSC NPC model")
    lines.append("element vertex {}".format(len(verts)))
    lines.append("property float x")
    lines.append("property float y")
    lines.append("property float z")
    lines.append("property uchar red")
    lines.append("property uchar green")
    lines.append("property uchar blue")
    lines.append("element face {}".format(len(faces)))
    lines.append("property list uchar int vertex_index")
    lines.append("end_header\n")
    
    header = "\n".join(lines).encode('ascii')
    
    with open(filepath, 'wb') as f:
        f.write(header)
        
        # Write vertices with per-vertex color derived from face colors
        # Average face colors to get vertex colors
        vertex_colors = [(0, 0, 0)] * len(verts)
        vertex_face_count = [0] * len(verts)
        
        for face in faces:
            color = face['color']
            # Unpack RGB from packed ushort (ARGB or RGB format)
            r = (color >> 10) & 0x3F  # 6 bits
            g = (color >> 5) & 0x1F   # 5 bits 
            b = color & 0x1F          # 5 bits
            # Scale to 0-255
            r = int(r * 255 / 63)
            g = int(g * 255 / 31)
            b = int(b * 255 / 31)
            
            # Assign color to vertices (average if multiple faces share)
            for vi in face['verts']:
                if 0 <= vi < len(verts):
                    if vertex_face_count[vi] == 0:
                        vertex_colors[vi] = (r, g, b)
                    else:
                        # Blend
                        pr, pg, pb = vertex_colors[vi]
                        vertex_colors[vi] = (
                            (pr * vertex_face_count[vi] + r) // (vertex_face_count[vi] + 1),
                            (pg * vertex_face_count[vi] + g) // (vertex_face_count[vi] + 1),
                            (pb * vertex_face_count[vi] + b) // (vertex_face_count[vi] + 1),
                        )
                    vertex_face_count[vi] += 1
        
        for i, (x, y, z) in enumerate(verts):
            packed_verts = struct.pack('<fff', float(x), float(y), float(z))
            r, g, b = vertex_colors[i] if vertex_face_count[i] > 0 else (128, 128, 128)
            packed_color = struct.pack('BBB', r, g, b)
            f.write(packed_verts)
            f.write(packed_color)
        
        # Write faces
        for face in faces:
            # Triangulate faces (fan triangulation for nverts > 3)
            nverts = face['nverts']
            verts = face['verts']
            
            if nverts < 3:
                continue
            
            # Fan triangulation: (v0, v1, v2), (v0, v2, v3), ...
            for ti in range(1, nverts - 1):
                tri = [verts[0], verts[ti], verts[ti + 1]]
                f.write(struct.pack('B', 3))  # 3 vertices per face
                f.write(struct.pack('<iii', tri[0], tri[1], tri[2]))

def main():
    import sys
    jag_path = 'C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag'
    output_dir = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/kingwen_avatar_meshes_rsc'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Decompress archive
    data = decompress_archive(jag_path)
    entries, data_start = parse_archive(data)
    
    print(f"Archive parsed: {len(entries)} entries")
    
    # NPC model IDs from npcs.json
    npc_model_ids = [3, 5, 6, 7, 8, 9, 10, 11, 12]
    
    for model_id in npc_model_ids:
        if model_id >= len(entries):
            print(f"Model {model_id}: skipped (out of range)")
            continue
        
        buf = get_file_buffer(data, entries, data_start, model_id)
        print(f"\nModel {model_id}: bufsize={len(buf)}")
        print(f"  First bytes: {buf[:8].hex()}")
        
        try:
            model = parse_rsc_model(buf)
            if model is None:
                print(f"  Model {model_id}: skipped (empty)")
                continue
            
            output_path = os.path.join(output_dir, f'rsc_npc_{model_id}.ply')
            write_ply(model, output_path)
            
            print(f"  vertexcount={model['vertexcount']}, facecount={model['facecount']}")
            print(f"  Wrote {len(model['xpos'])} verts, {len(model['faces'])} faces")
            
            # Verify byte consumption
            # Format: header(4) + verts(vc*6) + face_metadata(fc*(1+2+2+1)) + face_verts
            expected_bytes = 4 + model['vertexcount'] * 6 + model['facecount'] * 6  # nverts + color + backcolor + intensity
            for face in model['faces']:
                idx_size = 2 if model['vertexcount'] >= 256 else 1
                expected_bytes += face['nverts'] * idx_size
            
            print(f"  Expected bytes: {expected_bytes}, actual: {len(buf)}, "
                  f"remaining: {len(buf) - expected_bytes}")
            
        except Exception as e:
            print(f"  Model {model_id}: ERROR - {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
