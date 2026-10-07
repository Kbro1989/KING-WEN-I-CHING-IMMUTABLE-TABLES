#!/usr/bin/env python3
"""
Targeted: locate the varbit table and test 28749 -> varp 5783.

The (5783,0,0) triple guess found 0, so the record format differs. Find which
config key holds the varbit table (largest, most-record-like), then inspect
around 28749.
"""
import sqlite3
import struct
import zlib
from pathlib import Path

CACHE = Path(r"C:\ProgramData\Jagex\RuneScape-BETA")


def dz(d):
    if d[:4] == b"ZLB\x01":
        try:
            return zlib.decompress(d[8:])
        except Exception:
            return None
    return d


conn = sqlite3.connect(f"file:{CACHE / 'js5-2.jcache'}?mode=ro", uri=True)
rows = list(conn.execute("select KEY, DATA from cache"))
blobs = {}
for k, d in rows:
    o = dz(bytes(d))
    if o:
        blobs[k] = o

print("=" * 78)
print("CONFIG MAJOR 2 — key sizes (candidate varbit tables)")
print("=" * 78)
for k in sorted(blobs):
    b = blobs[k]
    print(f"  key={k:>4}  {len(b):>9,} bytes")
print()

# The varbit table should be large and contain many small records.
# Test each blob: does it contain the u16 28749?
print("=" * 78)
print("WHICH CONFIG KEY CONTAINS 28749 ?")
print("=" * 78)
target = 28749
t = target.to_bytes(2, "big")
for k in sorted(blobs):
    b = blobs[k]
    n = b.count(t)
    if n:
        offs = []
        s = 0
        while True:
            i = b.find(t, s)
            if i < 0:
                break
            offs.append(i)
            s = i + 1
        print(f"  key={k:>4}  {n} occurrence(s) at {offs[:8]}")
print()

# Inspect context around 28749 in the biggest candidate
print("=" * 78)
print("CONTEXT AROUND 28749 (looking for varp 5783 nearby)")
print("=" * 78)
v5783 = (5783).to_bytes(2, "big")
for k in sorted(blobs):
    b = blobs[k]
    s = 0
    while True:
        i = b.find(t, s)
        if i < 0:
            break
        s = i + 1
        lo = max(0, i - 12)
        hi = min(len(b), i + 14)
        ctx = b[lo:hi]
        near = "  <-- 5783 NEARBY" if v5783 in ctx else ""
        hexs = ctx.hex()
        mark = " " * (2 * (i - lo)) + "^^"
        print(f"  key={k} off={i}")
        print(f"    {hexs}{near}")
        print(f"    {mark}")
print()

# Reverse: where does 5783 appear, and is 28749 nearby?
print("=" * 78)
print("REVERSE — context around varp 5783 (looking for 28749 nearby)")
print("=" * 78)
s = 0
count = 0
for k in sorted(blobs):
    b = blobs[k]
    s = 0
    while count < 12:
        i = b.find(v5783, s)
        if i < 0:
            break
        s = i + 1
        lo = max(0, i - 10)
        hi = min(len(b), i + 16)
        ctx = b[lo:hi]
        near = "  <-- 28749 NEARBY" if t in ctx else ""
        print(f"  key={k} off={i}  {ctx.hex()}{near}")
        count += 1
    if count >= 12:
        break
