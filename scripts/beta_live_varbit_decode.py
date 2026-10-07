#!/usr/bin/env python3
"""
Final: decode the varbit table records and test 28749 -> varp 5783.

Two structures found in config major 2, key 69:
  A) around offset 477783: repeated `0100 1697 02 LLHH 000100`
     -> varp 5783 with a bit-range family (31,31),(0,2),(3,8),(9,10),(12,12)..
  B) around offset 21495: ascending ids 28725,28733,...,28749,... (+8 stride)

Determine whether (B) is the varbit id table and whether it links to (A).
"""
import sqlite3
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
blobs = {}
for k, d in conn.execute("select KEY, DATA from cache"):
    o = dz(bytes(d))
    if o:
        blobs[k] = o

b69 = blobs[69]
print(f"config key 69: {len(b69):,} bytes")
print()

# ---- structure B: region around 28749 ----
print("=" * 78)
print("STRUCTURE B — region around 28749 (offset 21495)")
print("=" * 78)
off = 21495
lo, hi = off - 96, off + 96
chunk = b69[lo:hi]
print(f"bytes [{lo}:{hi}]")
print(chunk.hex())
print()

# parse ascending u16 ids
print("ascending u16 values in region:")
i = 0
vals = []
while i + 2 <= len(chunk):
    v = int.from_bytes(chunk[i:i + 2], "big")
    if 28000 < v < 29600:
        vals.append((lo + i, v))
    i += 1
for o, v in vals[:40]:
    tag = "  <-- 28749" if v == 28749 else ""
    print(f"  off={o:>7}  {v}{tag}")
print()

# ---- structure A: region around 5783 ----
print("=" * 78)
print("STRUCTURE A — varbit family on varp 5783 (offset 477783)")
print("=" * 78)
off2 = 477783
lo2, hi2 = off2 - 16, off2 + 260
chunk2 = b69[lo2:hi2]
print(f"bytes [{lo2}:{hi2}]")
print(chunk2.hex())
print()

# parse the repeated record
print("parsed records (looking for 1697 = 5783):")
import re
for m in re.finditer(rb"\x01\x00\x16\x97\x02(..)(..)\x00\x01\x00", chunk2):
    lsb, msb = m.group(1)[0], m.group(2)[0]
    print(f"  varp=5783  lsb={lsb:>3}  msb={msb:>3}  width={msb - lsb + 1}")
print()

# ---- the key question: does 28749 appear near 5783 anywhere? ----
print("=" * 78)
print("KEY QUESTION — does the varbit table link 28749 to 5783?")
print("=" * 78)
t5783 = (5783).to_bytes(2, "big")
t28749 = (28749).to_bytes(2, "big")
# search a wide window around every 5783 for 28749
s = 0
hits = 0
while True:
    i = b69.find(t5783, s)
    if i < 0:
        break
    s = i + 1
    w = b69[max(0, i - 64):i + 64]
    if t28749 in w:
        print(f"  FOUND: 5783 at {i} has 28749 within +/-64 bytes")
        hits += 1
print(f"  total co-occurrences within +/-64 bytes: {hits}")
print()

# ---- check: is there a table mapping varbit-id -> varp? ----
# If yes, 28749 should appear as a u16 immediately followed by a varp id.
print("=" * 78)
print("SEARCH — 28749 as a u16, showing the 8 bytes that follow")
print("=" * 78)
s = 0
seen = 0
while seen < 12:
    i = b69.find(t28749, s)
    if i < 0:
        break
    s = i + 1
    tail = b69[i:i + 10]
    nxt = int.from_bytes(b69[i + 2:i + 4], "big") if i + 4 <= len(b69) else -1
    print(f"  off={i:>7}  28749 | next u16 = {nxt:>6}  bytes={tail.hex()}")
    seen += 1
print()

print("=" * 78)
print("VERDICT INPUTS")
print("=" * 78)
print(f"  varp 5783 present in config key 69 : {t5783 in b69}")
print(f"  varbit 28749 present in config key 69: {t28749 in b69}")
print(f"  config key 69 size                 : {len(b69):,}")
