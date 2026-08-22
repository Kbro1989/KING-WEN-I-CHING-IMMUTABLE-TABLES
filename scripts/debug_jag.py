#!/usr/bin/env python3
"""Debug models36.jag format."""
import struct, bz2

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

with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
    raw = f.read()

offset = 0
uncomp_len, offset = read_tribyte_be_signed(raw, 0)
comp_len, offset = read_tribyte_be_signed(raw, 3)

comp_data = raw[offset:offset + comp_len]
data = legacybz2(comp_data)

print(f"Decompressed size: {len(data)} (expected {uncomp_len})")
print(f"First 20 bytes (hex): {data[:20].hex()}")

if data[:3] == b'BZh':
    print(f"Data starts with BZh - double compressed!")
    data2 = legacybz2(data[4:])
    print(f"Double decompressed: {len(data2)} bytes")
    print(f"Double first 20 bytes: {data2[:20].hex()}")
    data = data2

# Now check file count
file_count = (data[0] << 8) | data[1]
print(f"File count (bytes 0-1 as BE ushort): {file_count}")

# Check for 50433 as big-endian ushort
target_le = struct.pack('<H', 50433)
pos_le = data.find(target_le)
print(f"50433 as LE ushort at offset: {pos_le}")

# Check for 50433 as big-endian uint
target_be4 = struct.pack('>I', 50433)
target_le4 = struct.pack('<I', 50433)
print(f"50433 as BE uint at offset: {data.find(target_be4)}")
print(f"50433 as LE uint at offset: {data.find(target_le4)}")

# Let's just print first 100 bytes
print(f"\nFirst 100 bytes (hex): {data[:100].hex()}")
print(f"First 100 bytes (repr): {repr(data[:100])}")
