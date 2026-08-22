#!/usr/bin/env python3
"""
Debug face parsing to find the missing per-face byte.
Try different interpretations of the face data layout.
"""
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

# Get file 10 buffer (vc=94, fc=61, bufsize=1149)
offset = data_start
for i in range(10):
    cl = (data[2 + i * 10 + 7] << 16) | (data[2 + i * 10 + 8] << 8) | data[2 + i * 10 + 9]
    offset += cl
# Get entry 10
cl10 = (data[2 + 10 * 10 + 7] << 16) | (data[2 + 10 * 10 + 8] << 8) | data[2 + 10 * 10 + 9]
buf = data[offset:offset + cl10]

print(f"File 10: bufsize={len(buf)}, vc=94, fc=61")

vc = (buf[0] << 8) | buf[1]
fc = (buf[2] << 8) | buf[3]
print(f"vc={vc}, fc={fc}")

# Read vertices
off = 4
xpos = []
ypos = []
zpos = []
for i in range(vc):
    x, off = read_short_be(buf, off)
    xpos.append(x)
for i in range(vc):
    y, off = read_short_be(buf, off)
    ypos.append(y)
for i in range(vc):
    z, off = read_short_be(buf, off)
    zpos.append(z)

print(f"After vertices: offset={off}, remaining={len(buf) - off}")

# Chunk 1: nverts (ubyte, fc entries)
nverts_list = []
for i in range(fc):
    nverts_list.append(buf[off])
    off += 1

# Chunk 2: color (ushort, fc entries)
color_list = []
for i in range(fc):
    c, off = read_ushort_be(buf, off)
    color_list.append(c)

# Chunk 3: backcolor (ushort, fc entries)
backcolor_list = []
for i in range(fc):
    bc, off = read_ushort_be(buf, off)
    backcolor_list.append(bc)

# Chunk 4: intensity (ubyte, fc entries)
intensity_list = []
for i in range(fc):
    intensity_list.append(buf[off])
    off += 1

print(f"After face metadata: offset={off}, remaining={len(buf) - off}")
print(f"Expected bytes for metadata: 4 + {vc}*6 + {fc}*(1+2+2+1) = {4 + vc*6 + fc*6}")

# Chunk 5: verts (variable)
total_verts = sum(nverts_list)
print(f"Total verts indices: {total_verts}")

# Try ubyte indices (since vc=94 < 256)
off_ubyte = off
total_bytes_ubyte = 0
for i in range(fc):
    for vi in range(nverts_list[i]):
        idx = buf[off_ubyte + total_bytes_ubyte]
        if idx >= vc:
            print(f"  Face {i}, vert {vi}: invalid index {idx} >= vc {vc}")
        total_bytes_ubyte += 1

print(f"Total bytes for ubyte indices: {total_bytes_ubyte}")
print(f"After ubyte verts: offset={off_ubyte + total_bytes_ubyte}, remaining={len(buf) - off_ubyte - total_bytes_ubyte}")

# Now let's check: the remaining should be fc bytes (61 bytes)
# But if we used ubyte indices, we got 0 remaining
# So the remaining 61 bytes are after the verts arrays
# Let me check what those 61 bytes are
remaining = len(buf) - (off + total_bytes_ubyte)
print(f"\nRemaining bytes after all chunks: {remaining}")
print(f"First 20 remaining bytes: {[hex(b) for b in buf[off + total_bytes_ubyte:off + total_bytes_ubyte + 20]]}")

# Could it be that verts are actually ushort (not ubyte)?
off_ushort = off
total_bytes_ushort = 0
for i in range(fc):
    for vi in range(nverts_list[i]):
        idx = (buf[off_ushort + total_bytes_ushort] << 8) | buf[off_ubyte + total_bytes_ubyte]
        total_bytes_ushort += 2

print(f"\nIf ushort indices: {total_bytes_ushort} bytes needed, remaining would be: {len(buf) - off - total_bytes_ushort}")
