#!/usr/bin/env python3
"""Verify RSC classic model format endianness by parsing file 10."""
import struct, bz2

def read_ushort_be(data, offset):
    return (data[offset] << 8) | data[offset + 1], offset + 2

def read_short_be(data, offset):
    val = (data[offset] << 8) | data[offset + 1]
    if val > 32767:
        val -= 65536
    return val, offset + 2

def read_tribyte_be(data, offset):
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    if val & 0x800000:
        val -= 0x1000000
    return val, offset + 3

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

# Get buffers for files 0-12
buffers = {}
cur = data_start
for fid in range(13):
    nh, dl, cl = indices[fid][1], indices[fid][2], indices[fid][3]
    buffers[fid] = data[cur:cur + cl]
    cur += cl

# Parse with BE ushort for vc/fc, BE short for positions
for fid in [0, 3, 5, 10, 11, 12]:
    buf = buffers[fid]
    if len(buf) < 4:
        print(f"File {fid}: too short")
        continue
    
    vc, off = read_ushort_be(buf, 0)
    fc, off = read_ushort_be(buf, 2)
    
    use_ushort = vc >= 256
    
    # Read vertices
    voff = 4
    vcount = 0
    for i in range(vc):
        voff += 6  # 3 shorts
        vcount += 1
    
    face_offset = voff
    faces_parsed = 0
    for fi in range(fc):
        if face_offset >= len(buf):
            break
        nverts = buf[face_offset]
        face_offset += 1
        face_offset += 2  # color
        face_offset += 2  # backcolor
        face_offset += 1  # intensity
        face_offset += nverts * (2 if use_ushort else 1)
        faces_parsed += 1
    
    remaining = len(buf) - face_offset
    print(f"File {fid}: vc={vc}, fc={fc}, bufsize={len(buf)}, "
          f"vert_end={voff}, faces_parsed={faces_parsed}, "
          f"consumed={face_offset}, remaining={remaining}")
    
    if faces_parsed == fc and remaining == 0:
        print(f"  -> PERFECT MATCH!")
