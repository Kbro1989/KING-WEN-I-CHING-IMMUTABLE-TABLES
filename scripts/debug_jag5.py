#!/usr/bin/env python3
import struct, bz2

with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
    raw = f.read()

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

comp_data = raw[6:6+289816]
data = legacybz2(comp_data)
print(f"Decompressed: {len(data)} bytes")

file_count = (data[0] << 8) | data[1]
print(f"File count: {file_count}")

offset = 2
indices = []
for i in range(file_count):
    nh = struct.unpack_from('>I', data, offset)[0]
    dl = (data[offset+4] << 16) | (data[offset+5] << 8) | data[offset+6]
    cl = (data[offset+7] << 16) | (data[offset+8] << 8) | data[offset+9]
    indices.append((i, nh, dl, cl))
    offset += 10

data_start = 2 + file_count * 10
cur = data_start

# Collect buffers for files 0-12
buffers = {}
for fid in range(13):
    nh, dl, cl = indices[fid][1], indices[fid][2], indices[fid][3]
    buf = data[cur:cur + cl]
    cur += cl
    buffers[fid] = buf

# Check file 10 first bytes
print(f"File 10 first 4 bytes: {buffers[10][:4].hex()}")
print(f"  Has BZh header? {buffers[10][:3] == b'BZh'}")

# Try legacybz2 on files 10-12
print("\n--- Trying legacybz2 on files 10-12 ---")
for fid in [10, 11, 12]:
    buf = buffers[fid]
    try:
        dec = legacybz2(buf)
        print(f"File {fid}: legacybz2 OK, decompressed to {len(dec)} bytes")
        vc = dec[0] | (dec[1] << 8)
        fc = dec[2] | (dec[3] << 8)
        print(f"  vc={vc}, fc={fc}")
        face_start = 4 + vc * 6
        if face_start <= len(dec):
            print(f"  face_start={face_start}, remaining={len(dec)-face_start}")
        else:
            print(f"  face_start={face_start} EXCEEDS buffer {len(dec)}")
    except Exception as e:
        print(f"File {fid}: legacybz2 failed: {e}")

# Try legacybz2 on files 0-5
print("\n--- Trying legacybz2 on files 0-5 ---")
for fid in range(6):
    buf = buffers[fid]
    try:
        dec = legacybz2(buf)
        print(f"File {fid}: legacybz2 OK, decompressed to {len(dec)} bytes")
        vc = dec[0] | (dec[1] << 8)
        fc = dec[2] | (dec[3] << 8)
        print(f"  vc={vc}, fc={fc}")
    except Exception as e:
        print(f"File {fid}: legacybz2 failed: {e}")
        vc_be = (buf[0] << 8) | buf[1]
        vc_le = buf[0] | (buf[1] << 8)
        print(f"  Raw: BE vc={vc_be}, LE vc={vc_le}")
