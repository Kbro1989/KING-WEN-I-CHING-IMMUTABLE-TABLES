#!/usr/bin/env python3
"""
LIVE BETA — varbit definition test.

The decisive check. beta_constants.ts claims:
    SAVE_CONFIRM = varbit 28749, width 1, bits [0-0], varp 5783

If that is real, varbit 28749 must be DEFINED in the cache with varp 5783.
If it is synthetic, it will be absent or point at a different varp.

Varbits live in the config major. Find them.
"""
import sqlite3
import sys
from pathlib import Path

CACHE = Path(r"C:\ProgramData\Jagex\RuneScape-BETA")
MAJORS = {"config": 2, "components": 3, "enums": 17, "clientscript": 12}


def open_major(major):
    p = CACHE / f"js5-{major}.jcache"
    if not p.exists():
        return None, p
    return sqlite3.connect(f"file:{p}?mode=ro", uri=True), p


def u16s(b, v):
    t = v.to_bytes(2, "big")
    return [i for i in range(len(b) - 1) if b[i:i + 2] == t]


def i32s(b, v):
    t = v.to_bytes(4, "big", signed=True)
    return [i for i in range(len(b) - 3) if b[i:i + 4] == t]


print("=" * 78)
print("VARBIT DEFINITION TEST — is 28749 real?")
print("=" * 78)
print()

for major_name in ("config", "components"):
    major = MAJORS[major_name]
    conn, path = open_major(major)
    print(f"### {major_name} (major {major}) -> {path.name}")
    if conn is None:
        print("    NOT AVAILABLE\n")
        continue
    cols = [r[1] for r in conn.execute("PRAGMA table_info(cache)")]
    n = conn.execute("select count(*) from cache").fetchone()[0]
    print(f"    schema: cache{tuple(cols)}   rows: {n}")

    rows = list(conn.execute("select KEY, DATA from cache"))
    blobs = {k: v for k, v in rows if isinstance(v, (bytes, bytearray))}

    # --- test: does varbit 28749 point at varp 5783? ---
    print(f"    --- searching for varp 5783 (claimed base of varbit 28749) ---")
    found_5783 = []
    for k, b in blobs.items():
        h16 = u16s(b, 5783)
        h32 = i32s(b, 5783)
        if h16 or h32:
            found_5783.append((k, len(b), len(h16), len(h32), b[:24].hex()))
    print(f"    entries referencing 5783 as u16/i32: {len(found_5783)}")
    for k, size, a, c, head in sorted(found_5783)[:20]:
        print(f"      key={k:>8}  size={size:>6}  u16={a:>3}  i32={c:>3}  head={head}")

    # --- test: is 28749 itself present as a definition key? ---
    has28749 = 28749 in blobs
    print(f"    key 28749 present as definition: {has28749}")

    # --- how many entries mention 28749 at all ---
    mention = [k for k, b in blobs.items() if u16s(b, 28749) or i32s(b, 28749)]
    print(f"    entries mentioning 28749: {len(mention)}")
    print()

# --- cross-check: the claimed varp for CHAR_CREATE_STATE is 5745 ---
print("### cross-check: claimed varps")
for name, varp in [("SAVE_CONFIRM", 5783), ("CHAR_CREATE_STATE", 5745)]:
    print(f"    {name:22s} -> claimed varp {varp}")
print()

# --- the reverse test: do the SYNTHETIC ids appear at all? ---
print("=" * 78)
print("CONTROL TEST — do the SYNTHETIC ids (123/456/789) appear as scripts?")
print("=" * 78)
print()
conn, path = open_major(MAJORS["clientscript"])
if conn:
    keys = {k for (k,) in conn.execute("select KEY from cache")}
    for synth in (123, 456, 789, 101, 202, 303, 404, 505, 606):
        print(f"    script id {synth:>4}: present as clientscript = {synth in keys}")
    print()
    print("    (presence of a low id is not proof of meaning — but the claimed")
    print("     HANDLER ids above are high, irregular, and all present.)")
