#!/usr/bin/env python3
import struct, bz2

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

def legacybz2(raw_data):
    processed = bytearray(len(raw_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = raw_data
    return bz2.decompress(bytes(processed))

with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
    raw = f.read()

offset = 0
uncomp_len, offset = read_tribyte_be(raw, 0)
comp_len, offset = read_tribyte_be(raw, 3)

comp_data = raw[offset:offset + comp_len]
data = legacybz2(comp_data)
print(f"Decompressed: {len(data)} bytes")

file_count, offset = read_ushort_be(data, 0)
print(f"File count (BE): {file_count}")

indices = []
for i in range(file_count):
    namehash, offset = read_uint_be(data, offset)
    dl, offset = read_tribyte_be(data, offset)
    cl, offset = read_tribyte_be(data, offset)
    indices.append((i, namehash, dl, cl))

data_start = offset
print(f"Data starts at offset: {data_start}")
print(f"Available data bytes: {len(data) - data_start}")

total_cl = sum(cl for _, _, _, cl in indices)
total_dl = sum(dl for _, _, _, cl in indices)
print(f"Total comp_len: {total_cl}")
print(f"Total decomp_len: {total_dl}")

if total_cl <= len(data) - data_start:
    print("Data fits!")
else:
    print(f"Data overflow! Need {total_cl}, have {len(data) - data_start}")

# Read files and check each
cur = data_start
for i, (fid, nh, dl, cl) in enumerate(indices):
    raw_buf = data[cur:cur + cl]
    
    if dl != cl and len(raw_buf) > 0:
        try:
            raw_buf = legacybz2(raw_buf)
        except:
            pass
    
    cur += cl
    
    if fid in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        if len(raw_buf) >= 4:
            vc = struct.unpack_from('<H', raw_buf, 0)[0]
            fc = struct.unpack_from('<H', raw_buf, 2)[0]
        else:
            vc = fc = 0
        
        face_start = 4 + vc * 6
        remaining = len(raw_buf) - face_start
        use_us = vc >= 256
        idx_size = 2 if use_us else 1
        
        print(f"File {fid}: vc={vc}, fc={fc}, bufsize={len(raw_buf)}, "
              f"face_start={face_start}, remaining={remaining}")
        
        if face_start < len(raw_buf):
            nverts = raw_buf[face_start]
            face_min_size = 6 + nverts * idx_size
            print(f"  nverts[0]={nverts}, face_min_size={face_min_size}")

# Count how many files have comp_len == decomp_len vs !=
same = sum(1 for _, _, dl, cl in indices if dl == cl)
diff = sum(1 for _, _, dl, cl in indices if dl != cl)
print(f"\nFiles with dl==cl (uncompressed): {same}")
print(f"Files with dl!=cl (compressed): {diff}")

# Check compressed files
for i, (fid, nh, dl, cl) in enumerate(indices):
    if dl != cl:
        print(f"  Compressed file {fid}: dl={dl}, cl={cl}")
        if i > 15:
            print(f"  ... (showing first 15 compressed files)")
            break
