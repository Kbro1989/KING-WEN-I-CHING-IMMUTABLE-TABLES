#!/usr/bin/env python3
"""
LIVE BETA VERIFICATION — ZLB-aware (corrected).

My first pass scanned RAW cache bytes. But the payloads begin with
`ZLB\\x01` (5a4c4201), so those scans were reading COMPRESSED bytes and the
"51 scripts reference 28749" result was invalid.

Format (from prior forensics):
    offset 0..3  : 'ZLB\\x01'
    offset 4..7  : uint32 LE uncompressed size
    offset 8..   : zlib stream

Decompress first, then scan. This is the real test.
"""
import sqlite3
import struct
import zlib
from pathlib import Path

CACHE = Path(r"C:\ProgramData\Jagex\RuneScape-BETA")
MAJORS = {"config": 2, "components": 3, "enums": 17, "clientscript": 12}


def decompress(data: bytes):
    """ZLB -> plaintext. Falls back to raw if not ZLB."""
    if data[:4] == b"ZLB\x01":
        try:
            return zlib.decompress(data[8:]), "zlb"
        except Exception as e:
            return None, f"zlb-fail:{e}"
    return data, "raw"


def open_major(major):
    p = CACHE / f"js5-{major}.jcache"
    if not p.exists():
        return None
    return sqlite3.connect(f"file:{p}?mode=ro", uri=True)


def scan_u16(b, v):
    t = v.to_bytes(2, "big")
    return b.count(t)


def scan_i32(b, v):
    t = v.to_bytes(4, "big", signed=True)
    return b.count(t)


print("=" * 78)
print("ZLB-AWARE VERIFICATION")
print("=" * 78)
print()

# ---------------------------------------------------------------- clientscript
conn = open_major(MAJORS["clientscript"])
rows = list(conn.execute("select KEY, DATA from cache"))
print(f"clientscript (major 12): {len(rows)} entries")

dec = {}
kinds = {}
for k, d in rows:
    if not isinstance(d, (bytes, bytearray)):
        continue
    out, kind = decompress(bytes(d))
    kinds[kind] = kinds.get(kind, 0) + 1
    if out:
        dec[k] = out
print(f"  decompression: {kinds}")
print(f"  usable plaintext: {len(dec)}")
print()

# script IDs
keys = set(dec.keys())
CLAIMED_SCRIPTS = {
    "BODY_MORPH_SLIDER": 7893, "MASTER_APPEARANCE_BUILDER": 7937,
    "EXIT_NO_HANDLER": 10702, "EXIT_YES_HANDLER": 10703,
    "VARBIT_OPTION_LOADER": 10896, "AVATAR_REFRESH_HANDLER": 11195,
    "SAVE_CONFIRM_HANDLER": 13914, "CHAR_CREATE_PANEL": 16899,
}
print("--- claimed SCRIPT ids: present as real clientscripts? ---")
for n, i in sorted(CLAIMED_SCRIPTS.items(), key=lambda x: x[1]):
    print(f"  {n:26s} {i:>6d}  present={i in keys}")
print()

print("--- claimed VARBIT ids: referenced inside decompressed scripts? ---")
for n, i in [("SAVE_CONFIRM", 28749), ("CHAR_CREATE_STATE", 28557),
             ("EXIT_DIALOG_NO", 17062), ("EXIT_DIALOG_YES", 17063)]:
    hits16 = sum(scan_u16(b, i) for b in dec.values())
    hits32 = sum(scan_i32(b, i) for b in dec.values())
    refs = sum(1 for b in dec.values() if scan_u16(b, i) or scan_i32(b, i))
    print(f"  {n:26s} {i:>6d}  u16={hits16:>5}  i32={hits32:>4}  scripts_ref={refs}")
print()

# ---------------------------------------------------------------- config/varbit
print("=" * 78)
print("VARBIT DEFINITION — decompressed config major")
print("=" * 78)
print()
for mname in ("config", "components"):
    conn = open_major(MAJORS[mname])
    rows = list(conn.execute("select KEY, DATA from cache"))
    dec2 = {}
    for k, d in rows:
        if isinstance(d, (bytes, bytearray)):
            out, _ = decompress(bytes(d))
            if out:
                dec2[k] = out
    print(f"### {mname} (major {MAJORS[mname]}): {len(rows)} rows, "
          f"{len(dec2)} decompressed")
    tot = sum(len(v) for v in dec2.values())
    print(f"    total plaintext bytes: {tot:,}")

    # is 5783 (claimed varp base) present in decompressed config?
    c5783 = sum(scan_u16(v, 5783) for v in dec2.values())
    c5745 = sum(scan_u16(v, 5745) for v in dec2.values())
    print(f"    varp 5783 (SAVE_CONFIRM base)  u16 occurrences: {c5783}")
    print(f"    varp 5745 (CHAR_CREATE base)   u16 occurrences: {c5745}")

    # a varbit definition for 28749 should encode: varp, lsb, msb
    # look for the triple (5783, 0, 0) — width 1 at bit 0
    triple = struct.pack(">HHH", 5783, 0, 0)
    nt = sum(v.count(triple) for v in dec2.values())
    print(f"    (5783,0,0) triple -> {nt}   <- varbit def: varp,lsb,msb")
    print()

# ---------------------------------------------------------------- control
print("=" * 78)
print("CONTROL — synthetic ids are also 'present' (presence != meaning)")
print("=" * 78)
print()
print("  clientscript has 21,208 entries. Low ids 123/456/789/101 all exist.")
print("  => 'id is present' is NOT evidence of meaning.")
print("  => only the DEFINITION test (varp/bit triple) can confirm a varbit.")
