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

# Outer header
uncomp_len, o1 = read_tribyte_be(raw, 0)
comp_len, o2 = read_tribyte_be(raw, 3)
print(f"Outer: uncomp={uncomp_len}, comp={comp_len}")

comp_data = raw[o2:o2 + comp_len]
data = legacybz2(comp_data)
print(f"Decompressed: {len(data)} bytes")

# Parse indices with unsigned tribytes
file_count = (data[0] << 8) | data[1]  # BE ushort
print(f"File count: {file_count}")

offset = 2
indices = []
for i in range(file_count):
    nh = struct.unpack_from('>I', data, offset)[0]
    dl = (data[offset+4] << 16) | (data[offset+5] << 8) | data[offset+6]
    cl = (data[offset+7] << 16) | (data[offset+8] << 8) | data[offset+9]
    indices.append((i, nh, dl, cl))
    offset += 10

# Show first 15
for fid, nh, dl, cl in indices[:15]:
    print(f"  File {fid}: namehash={nh:#010x}, dl={dl}, cl={cl}")

data_start = 2 + file_count * 10
print(f"\nData start: {data_start}")
total_cl = sum(cl for _, _, _, cl in indices)
print(f"Total comp_len: {total_cl}, available: {len(data) - data_start}")

# Read file 0
cur = data_start
for fid, nh, dl, cl in indices:
    raw_buf = data[cur:cur + cl]
    cur += cl
    
    if fid < 13:
        vc_be = (raw_buf[0] << 8) | raw_buf[1]
        vc_le = raw_buf[0] | (raw_buf[1] << 8)
        fc_be = (raw_buf[2] << 8) | raw_buf[3]
        fc_le = raw_buf[2] | (raw_buf[3] << 8)
        print(f"File {fid}: bufsize={len(raw_buf)} "
              f"vc BE={vc_be} LE={vc_le}, fc BE={fc_be} LE={fc_le}")

# Check if any files have dl != cl
diff_count = sum(1 for _, _, dl, cl in indices if dl != cl)
print(f"\nFiles with dl!=cl: {diff_count}")

# The total_cl should match available bytes
if total_cl == len(data) - data_start:
    print("Total comp_len matches available data perfectly!")
