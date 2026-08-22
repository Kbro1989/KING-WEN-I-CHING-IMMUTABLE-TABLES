#!/usr/bin/env python3
"""Carefully debug face parsing for file 10."""
import struct, bz2, json

def read_tribyte_be(data, offset):
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    if val & 0x800000:
        val -= 0x1000000
    return val, offset + 3

def read_uint_be(data, offset):
    val = (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]
    return val, offset + 4

def read_ushort_be(data, offset):
    return (data[offset] << 8) | data[offset + 1], offset + 2

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

with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
    raw = f.read()

comp_data = raw[6:6+289816]
data = legacybz2(comp_data)

file_count = (data[0] << 8) | data[1]
offset = 2
indices = []
for i in range(file_count):
    nh = struct.unpack_from('>I', data, offset)[0]
    dl = (data[offset+4] << 16) | (data[offset+5] << 8) | data[offset+6]
    cl = (data[offset+7] << 16) | (data[offset+8] << 8) | data[offset+9]
    indices.append((i, nh, dl, cl))
    offset += 10

data_start = 2 + file_count * 10

# Get file 10 buffer
cur = data_start
for fid in range(11):
    nh, dl, cl = indices[fid][1], indices[fid][2], indices[fid][3]
    if fid == 10:
        buf = data[cur:cur + cl]
        break
    cur += cl

print(f"File 10: bufsize={len(buf)}")
vc, off = read_ushort_be(buf, 0)
fc, off = read_ushort_be(buf, 2)
print(f"vc={vc}, fc={fc}")

# Read vertices
voff = 4
verts = []
for i in range(vc):
    x, voff = read_short_be(buf, voff)
    y, voff = read_short_be(buf, voff)
    z, voff = read_short_be(buf, voff)
    verts.append((x, y, z))
print(f"Vertices: {len(verts)}, end offset: {voff}")

# Now parse faces one by one
use_ushort = vc >= 256
print(f"Vertex index size: {'ushort' if use_ushort else 'ubyte'}")

face_offset = voff
for fi in range(fc):
    if face_offset >= len(buf):
        print(f"Face {fi}: OUT OF DATA at offset {face_offset}")
        break
    
    start_off = face_offset
    nverts = buf[face_offset]
    face_offset += 1
    color, face_offset = read_ushort_be(buf, face_offset)
    backcolor, face_offset = read_ushort_be(buf, face_offset)
    intensity = buf[face_offset]
    face_offset += 1
    
    verts_list = []
    for vi in range(nverts):
        if use_ushort:
            v, face_offset = read_ushort_be(buf, face_offset)
        else:
            v = buf[face_offset]
            face_offset += 1
        verts_list.append(v)
    
    if fi < 5 or fi >= fc - 3:
        print(f"Face {fi}: nverts={nverts}, color={color}, backcolor={backcolor}, "
              f"intensity={intensity}, verts={verts_list}, "
              f"total_bytes={face_offset - start_off}")

print(f"\nTotal faces parsed: {fi + 1}")
print(f"Total bytes consumed: {face_offset}")
print(f"Buffer size: {len(buf)}")
print(f"Remaining: {len(buf) - face_offset}")

# Maybe the face format is different. Let me check if intensity comes before color/backcolor
print("\n--- Trying different face format orderings ---")
# Maybe: nverts, color, backcolor, intensity -> that's what we have
# Try: nverts, color, backcolor (no intensity)
fo2 = voff
for fi in range(fc):
    if fo2 >= len(buf):
        break
    nv = buf[fo2]
    fo2 += 1
    c, fo2 = read_ushort_be(buf, fo2)
    bc, fo2 = read_ushort_be(buf, fo2)
    # No intensity
    verts_list = []
    for vi in range(nv):
        if use_ushort:
            v, fo2 = read_ushort_be(buf, fo2)
        else:
            v = buf[fo2]
            fo2 += 1
    if fi < 3:
        print(f"Face {fi} (no intensity): nverts={nv}, color={c}, backcolor={bc}, "
              f"bytes={(fo2 - voff) - (fi > 0 and prev_off or 0)}")

# Try: nverts, intensity, color, backcolor
fo3 = voff
for fi in range(fc):
    if fo3 >= len(buf):
        break
    nv = buf[fo3]
    fo3 += 1
    inten = buf[fo3]
    fo3 += 1
    c, fo3 = read_ushort_be(buf, fo3)
    bc, fo3 = read_ushort_be(buf, fo3)
    verts_list = []
    for vi in range(nv):
        if use_ushort:
            v, fo3 = read_ushort_be(buf, fo3)
        else:
            v = buf[fo3]
            fo3 += 1
    if fi < 3:
        print(f"Face {fi} (intensity first): nverts={nv}, intensity={inten}, color={c}, backcolor={bc}")

print(f"\nFormat 2 final offset: {fo2}, remaining: {len(buf) - fo2}")
print(f"Format 3 final offset: {fo3}, remaining: {len(buf) - fo3}")
