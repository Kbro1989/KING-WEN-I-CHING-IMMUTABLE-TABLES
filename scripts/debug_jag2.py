#!/usr/bin/env python3
import struct, bz2, os

def read_tribyte_be_signed(data, offset):
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    if val & 0x800000:
        val -= 0x1000000
    return val, offset + 3

def legacybz2(raw_data):
    processed = bytearray(len(raw_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = raw_data
    return bz2.decompress(bytes(processed))

# Check for .mem files
for root, dirs, files in os.walk('C:/Users/krist/Desktop/openrsc-vinilla/public'):
    for f in files:
        if 'model' in f.lower():
            fpath = os.path.join(root, f)
            print(f"Model file: {fpath} ({os.path.getsize(fpath)} bytes)")

with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
    raw = f.read()

print(f"\nRaw file size: {len(raw)}")

# Outer header
uncomp_len, o1 = read_tribyte_be_signed(raw, 0)
comp_len, o2 = read_tribyte_be_signed(raw, 3)
print(f"Outer: uncomp={uncomp_len}, comp={comp_len}")

comp_data = raw[o2:o2 + comp_len]
data = legacybz2(comp_data)
print(f"Decompressed: {len(data)} bytes")
print(f"First 16 bytes: {data[:16].hex()}")

# Read as little-endian ushort
le_count = (data[1] << 8) | data[0]
be_count = (data[0] << 8) | data[1]
print(f"File count: LE={le_count}, BE={be_count}")

# The correct count should be 50433 = 0xC501
# LE read: data[0]=0x01, data[1]=0xc5 -> (0xc5 << 8) | 0x01 = 50433
# So the file count is stored in LITTLE-endian!
# But rsmv reads it as big-endian (true parameter)
# This means rsmv's code has a bug, OR the .jag version is different from what rsmv expects

# Let's use LE count and re-parse
file_count = le_count
print(f"\nUsing file_count = {file_count}")

# Parse indices (each entry: namehash(4 BE uint), decomp_len(3 BE tribyte), comp_len(3 BE tribyte))
offset = 2
indices = []
for i in range(file_count):
    namehash = struct.unpack_from('>I', data, offset)[0]
    dl, _ = read_tribyte_be_signed(data, offset + 4)
    cl, _ = read_tribyte_be_signed(data, offset + 7)
    indices.append((namehash, dl, cl))
    offset += 10

data_offset = offset
print(f"Data starts at offset: {data_offset}")
print(f"Remaining data bytes: {len(data) - data_offset}")

# Check first few entries
for i in range(min(5, file_count)):
    print(f"  Entry {i}: namehash={indices[i][0]:#010x}, decomp={indices[i][1]}, comp={indices[i][2]}")

# Check entries 10-12
for i in range(10, 13):
    print(f"  Entry {i}: namehash={indices[i][0]:#010x}, decomp={indices[i][1]}, comp={indices[i][2]}")

# Now parse the actual file data
files = []
cur = data_offset
for i, (nh, dl, cl) in enumerate(indices):
    raw_buf = data[cur:cur + cl]
    cur += cl
    
    if dl != cl and len(raw_buf) > 0:
        try:
            raw_buf = legacybz2(raw_buf)
        except Exception as e:
            if i < 15:
                print(f"  File {i}: bz2 failed")
    
    files.append({'fileid': i, 'namehash': nh, 'buffer': raw_buf, 'size': len(raw_buf)})

print(f"\nParsed {len(files)} files")
print(f"Total data consumed: {cur - data_offset}")

# Check models 10-12
import json
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

for mid in all_models:
    if mid < len(files):
        buf = files[mid]['buffer']
        if len(buf) >= 4:
            vc = struct.unpack_from('<H', buf, 0)[0]
            fc = struct.unpack_from('<H', buf, 2)[0]
            print(f"  Model {mid} (fileid {mid}): namehash={files[mid]['namehash']:#010x}, "
                  f"bufsize={len(buf)}, vc={vc}, fc={fc}")
