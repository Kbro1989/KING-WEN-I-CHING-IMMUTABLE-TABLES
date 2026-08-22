#!/usr/bin/env python3
"""Debug: find the missing 1 byte per face in RSC models."""
import struct, bz2

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

comp_data = raw[6:]
processed = bytearray(len(comp_data) + 4)
processed[0:4] = b'BZh\x39'
processed[4:] = comp_data
data = bz2.decompress(bytes(processed))

file_count = (data[0] << 8) | data[1]
data_start = 2 + file_count * 10

# Get file 10 buffer
offset = data_start
for i in range(10):
    cl = (data[2 + i * 10 + 7] << 16) | (data[2 + i * 10 + 8] << 8) | data[2 + i * 10 + 9]
    offset += cl
cl10 = (data[2 + 10 * 10 + 7] << 16) | (data[2 + 10 * 10 + 8] << 8) | data[2 + 10 * 10 + 9]
buf = data[offset:offset + cl10]

vc = (buf[0] << 8) | buf[1]
fc = (buf[2] << 8) | buf[3]

off = 4
# Read vertices
for i in range(vc):
    off += 6  # 3 shorts

print(f"vc={vc}, fc={fc}, buf_size={len(buf)}")
print(f"Header + verts: {off}")

# Chunk 1: nverts (fc bytes)
nverts = []
for i in range(fc):
    nverts.append(buf[off])
    off += 1
print(f"After nverts: {off}")

# Chunk 2: color (fc * 2 bytes)
colors = []
for i in range(fc):
    c = (buf[off] << 8) | buf[off+1]
    colors.append(c)
    off += 2
print(f"After colors: {off}")

# Chunk 3: backcolor (fc * 2 bytes)
backcolors = []
for i in range(fc):
    bc = (buf[off] << 8) | buf[off+1]
    backcolors.append(bc)
    off += 2
print(f"After backcolors: {off}")

# Chunk 4: intensity (fc bytes)
intensities = []
for i in range(fc):
    intensities.append(buf[off])
    off += 1
print(f"After intensities: {off}")

# Now we have the verts arrays (chunk 5)
# After verts, there should be 0 remaining
total_vert_verts = sum(nverts)
print(f"Total vert indices: {total_vert_verts}")

# Try ubyte indices
vert_start = off
off_ubyte = vert_start
for i in range(fc):
    for vi in range(nverts[i]):
        idx = buf[off_ubyte]
        off_ubyte += 1

print(f"After ubyte verts: offset={off_ubyte}, end of buffer={len(buf)}, remaining={len(buf) - off_ubyte}")

# If there's still data remaining, it's the extra byte per face
if len(buf) - off_ubyte > 0:
    remaining = len(buf) - off_ubyte
    print(f"\n*** REMAINING: {remaining} bytes (= fc={fc}) ***")
    print(f"Extra bytes: {[hex(b) for b in buf[off_ubyte:]]}")
    
    # These extra bytes are per-face, after the verts
    # Maybe it's a "renderback" or "render_type" byte?
    print(f"\nExtra bytes per face:")
    for i in range(fc):
        print(f"  Face {i}: extra={hex(buf[off_ubyte + i])}, nverts={nverts[i]}, color={hex(colors[i])}, backcolor={hex(backcolors[i])}, intensity={intensities[i]}")
