#!/usr/bin/env python3
"""Test script to debug models36.jag parsing and namehash lookup."""
import struct, bz2, json

def read_tribyte_be(data, offset):
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    return val, offset + 3

def read_uint_be(data, offset):
    val = (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]
    return val, offset + 4

def read_ushort_be(data, offset):
    val = (data[offset] << 8) | data[offset + 1]
    return val, offset + 2

def read_short_be(data, offset):
    val = (data[offset] << 8) | data[offset + 1]
    if val > 32767:
        val -= 65536
    return val, offset + 2

def legacybz2(raw_data):
    processed = bytearray(len(raw_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = raw_data
    return bz2.decompress(bytes(processed))

def cacheFilenameHash(name, oldhash):
    h = 0
    if oldhash:
        name = name.upper()
        for ch in name:
            h = (h * 61 + ord(ch) - 32) & 0xFFFFFFFF
    else:
        for ch in name:
            h = (((h << 5) - h) | 0) + ord(ch) | 0
    return h & 0xFFFFFFFF

def parse_legacy_archive(file_data, is_classic=True):
    """Parse a legacy .jag or .mem archive file."""
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

    data_offset = offset
    files = []
    cur = data_offset
    for i, (nh, dl, cl) in enumerate(indices):
        raw_buf = data[cur:cur + cl]
        cur += cl

        if dl != cl and len(raw_buf) > 0:
            try:
                raw_buf = legacybz2(raw_buf)
                if len(raw_buf) != dl:
                    print(f"  File {i}: decompress size mismatch! got {len(raw_buf)}, expected {dl}")
            except Exception as e:
                print(f"  File {i}: decompress failed: {e}")

        files.append({'fileid': i, 'namehash': nh, 'buffer': raw_buf, 'size': len(raw_buf)})

    return files

def parse_classic_model(buf):
    """Parse RSC classic model format per classicmodels.jsonc."""
    offset = 0
    vertexcount, offset = read_ushort_le(buf, 0)
    facecount, offset = read_ushort_le(buf, 2)
    offset = 4

    xpos, ypos, zpos = [], [], []
    for i in range(vertexcount):
        v, offset = read_short_le(buf, offset)
        xpos.append(v)
        v, offset = read_short_le(buf, offset)
        ypos.append(v)
        v, offset = read_short_le(buf, offset)
        zpos.append(v)

    # Vertex index size: ubyte if vertexcount < 256, ushort if >= 256
    use_ushort = vertexcount >= 256

    faces = []
    for i in range(facecount):
        color, offset = read_ushort_le(buf, offset)
        backcolor, offset = read_ushort_le(buf, offset)
        intensity = buf[offset]
        offset += 1
        nverts = buf[offset]
        offset += 1

        verts = []
        for j in range(nverts):
            if use_ushort:
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

def read_ushort_le(data, offset):
    return struct.unpack_from('<H', data, offset)[0], offset + 2

def read_short_le(data, offset):
    return struct.unpack_from('<h', data, offset)[0], offset + 2

def write_ply(filepath, model):
    """Write model as PLY file."""
    vc = model['vertexcount']
    fc = model['facecount']

    with open(filepath, 'wb') as f:
        header = f"ply\nformat binary_little_endian 1.0\nelement vertex {vc}\n"
        header += "property float x\nproperty float y\nproperty float z\n"
        header += f"element face {fc}\nproperty list uchar int vertex_index\nend_header\n"
        f.write(header.encode())

        for i in range(vc):
            f.write(struct.pack('<fff', float(model['xpos'][i]), float(model['ypos'][i]), float(model['zpos'][i])))

        for face in model['faces']:
            f.write(struct.pack('<B', len(face['verts'])))
            for vi in face['verts']:
                f.write(struct.pack('<i', vi))

    return vc, fc

if __name__ == '__main__':
    # Parse the .jag archive
    with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
        raw = f.read()

    files = parse_legacy_archive(raw)
    print(f"Parsed {len(files)} files from models36.jag")

    # Build namehash -> fileid lookup
    hash_to_fileid = {}
    for f in files:
        hash_to_fileid[f['namehash']] = f['fileid']

    # Load NPC data to get model IDs
    npcs = json.load(open('C:/Users/krist/Desktop/openrsc-vinilla/rsc-data/config/npcs.json'))

    walk_models = set()
    combat_models = set()
    for npc in npcs:
        if npc.get('walkModel') is not None:
            walk_models.add(npc['walkModel'])
        if npc.get('combatModel') is not None:
            combat_models.add(npc['combatModel'])

    all_models = sorted(walk_models | combat_models)
    print(f"\nNPC model IDs: {all_models}")

    # Try different name patterns
    print("\n--- Searching for model namehash matches ---")
    for mid in all_models:
        found = False
        for suffix in ['', '.ob3', '.jag', '.dat', '.mod']:
            h = cacheFilenameHash(f"{mid}{suffix}", True)
            if h in hash_to_fileid:
                print(f"  Model {mid} -> hash of '{mid}{suffix}' = {h:#010x} -> fileid {hash_to_fileid[h]}")
                found = True
                break

        if not found:
            # Try without old hash
            h = cacheFilenameHash(str(mid), False)
            if h in hash_to_fileid:
                print(f"  Model {mid} -> NEW hash of '{mid}' = {h:#010x} -> fileid {hash_to_fileid[h]}")
                found = True

        if not found:
            # Try zero-padded
            for pad in ['', '0', '00', '000']:
                h = cacheFilenameHash(f"{pad}{mid}", True)
                if h in hash_to_fileid:
                    print(f"  Model {mid} -> padded '{pad}{mid}' -> fileid {hash_to_fileid[h]}")
                    found = True
                    break

        if not found:
            print(f"  Model {mid} -> NOT FOUND")

    # Also try direct file index (fileid == model id)
    print("\n--- Direct fileid lookup for models 3-12 ---")
    for mid in all_models:
        if mid < len(files):
            buf = files[mid]['buffer']
            if len(buf) >= 4:
                vc = struct.unpack_from('<H', buf, 0)[0]
                fc = struct.unpack_from('<H', buf, 2)[0]
                print(f"  Model {mid} (fileid {mid}): namehash={files[mid]['namehash']:#010x}, "
                      f"bufsize={len(buf)}, vc={vc}, fc={fc}")
                if vc > 0 and vc < 5000 and fc > 0 and fc < 50000:
                    try:
                        model = parse_classic_model(buf)
                        print(f"    -> VALID: vc={model['vertexcount']}, fc={model['facecount']}")
                    except Exception as e:
                        print(f"    -> PARSE ERROR: {e}")
