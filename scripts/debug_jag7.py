#!/usr/bin/env python3
"""Debug archive structure precisely following legacycache.ts parseLegacyArchive()."""
import struct, bz2

def read_ushort_be(data, offset):
    return (data[offset] << 8) | data[offset + 1], offset + 2

def read_tribyte_be_unsigned(data, offset):
    """Read unsigned 3-byte big-endian integer."""
    val = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
    return val, offset + 3

def read_uint_be(data, offset):
    return struct.unpack_from('>I', data, offset)[0], offset + 4

def legacybz2(raw_data):
    processed = bytearray(len(raw_data) + 4)
    processed[0:4] = b'BZh\x39'
    processed[4:] = raw_data
    return bz2.decompress(bytes(processed))

with open('C:/Users/krist/Desktop/openrsc-vinilla/public/models36.jag', 'rb') as f:
    raw = f.read()

print(f"Raw file size: {len(raw)}")

# Decompress outer archive
# According to legacycache.ts, the BZh stream has a 9-byte header:
# 'BZh' + digit + 4 bytes block info, then compressed data
# Let's try different header sizes
for header_size in [5, 6, 9, 13]:
    comp_data = raw[header_size:]
    try:
        processed = bytearray(len(comp_data) + 4)
        processed[0:4] = b'BZh\x39'
        processed[4:] = comp_data
        data = bz2.decompress(bytes(processed))
        dec_size = len(data)
        # Read file count as big-endian ushort
        file_count = (data[0] << 8) | data[1]
        # Compute data start
        data_start = 2 + file_count * 10
        total_expected = data_start + sum(
            read_tribyte_be_unsigned(data, 2 + i * 10 + 7)[0] 
            for i in range(file_count)
        )
        print(f"\nHeader size {header_size}: decompressed={dec_size}")
        print(f"  file_count (BE ushort)={file_count}, data_start={data_start}")
        # Check if LE file count works
        file_count_le = data[0] | (data[1] << 8)
        print(f"  file_count (LE ushort)={file_count_le}")
        # Check actual data
        remaining_after_index = dec_size - data_start
        all_cl = []
        cur = data_start
        for i in range(13):
            if i < file_count:
                _, cl_off = read_tribyte_be_unsigned(data, 2 + i * 10 + 7)
                cl = read_tribyte_be_unsigned(data, 2 + i * 10 + 7)[0]
                all_cl.append(cl)
                cur += cl
        
        total_cl_13 = sum(all_cl)
        print(f"  First 13 comp_lens: {all_cl}")
        print(f"  Sum of first 13 comp_lens: {total_cl_13}")
        print(f"  Remaining after index + 13 entries: {remaining_after_index - total_cl_13}")
        
        # Check if the total comp_len matches
        all_comp_lens = []
        for i in range(file_count):
            cl, _ = read_tribyte_be_unsigned(data, 2 + i * 10 + 7)
            all_comp_lens.append(cl)
        total_all = sum(all_comp_lens)
        print(f"  Total comp_len sum: {total_all}, dec_size: {dec_size}, data_start: {data_start}")
        print(f"  data_start + total_comp = {data_start + total_all}")
        print(f"  Match: {data_start + total_all == dec_size}")
        break
    except Exception as e:
        print(f"Header size {header_size}: FAILED - {e}")
