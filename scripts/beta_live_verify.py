#!/usr/bin/env python3
"""
LIVE BETA CACHE VERIFIER — test the POG2 Beta signals against ground truth.

POG2's beta_constants.ts asserts a set of identifiers. Some are synthetic
(123/456/789), some irregular and unverified (28749, 13914, 5783, 17062,
17063). A live BETA cache turns those from claims into facts.

Decoding path (from rsmv-upstream/src/constants.ts):
    cacheMajors.clientscript = 12
    cacheMajors.enums        = 17
    cacheMajors.components   = 3
    cacheMajors.config       = 2

.jcache files are SQLite with tables `cache` and `cache_index`.

Usage:
    python3 beta_live_verify.py <signal>
      signal = varbit | clientscript | enums | components | all
"""
import sqlite3
import sys
from pathlib import Path

CACHE = Path(r"C:\ProgramData\Jagex\RuneScape-BETA")

# rsmv-upstream/src/constants.ts
MAJORS = {
    "config": 2, "components": 3, "mapsquares": 5, "sprites": 8,
    "clientscript": 12, "sounds": 14, "locs": 16, "enums": 17,
    "npcs": 18, "items": 19, "sequences": 20, "spotanims": 21,
    "structs": 22, "worldmap": 23, "models": 47, "frames": 48,
}

# POG2 beta_constants.ts claims under test
CLAIMS = {
    "SAVE_CONFIRM": 28749,
    "SAVE_CONFIRM_HANDLER": 13914,
    "EXIT_DIALOG_NO": 17062,
    "EXIT_DIALOG_YES": 17063,
    "EXIT_NO_HANDLER": 10702,
    "EXIT_YES_HANDLER": 10703,
    "VARBIT_OPTION_LOADER": 10896,
    "MASTER_APPEARANCE_BUILDER": 7937,
    "BODY_MORPH_SLIDER": 7893,
    "AVATAR_REFRESH_HANDLER": 11195,
    "CHAR_CREATE_PANEL": 16899,
    "CHAR_CREATE_STATE": 28557,
    "APPEARANCE_BODY": 2830,
    "UI_TAB_STATE": 666,
}
CLAIMED_VARP = {"SAVE_CONFIRM": 5783, "CHAR_CREATE_STATE": 5745}


def open_major(major: int):
    """Open the jcache for a cache major. Returns (conn, path) or (None, path)."""
    p = CACHE / f"js5-{major}.jcache"
    if not p.exists():
        return None, p
    try:
        c = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        return c, p
    except Exception:
        return None, p


def table_info(conn):
    out = {}
    for (name,) in conn.execute(
            "select name from sqlite_master where type='table'"):
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({name})")]
        out[name] = cols
    return out


def scan_blob_for_u16(blob: bytes, value: int) -> list:
    """Find big-endian u16 occurrences of value in a blob."""
    hits = []
    target = value.to_bytes(2, "big")
    start = 0
    while True:
        i = blob.find(target, start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1
    return hits


def scan_blob_for_i32(blob: bytes, value: int) -> list:
    hits = []
    target = value.to_bytes(4, "big", signed=True)
    start = 0
    while True:
        i = blob.find(target, start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1
    return hits


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    print("=" * 78)
    print("LIVE BETA CACHE — GROUND TRUTH VERIFICATION")
    print(f"cache: {CACHE}")
    print("=" * 78)
    print()

    if which in ("clientscript", "all"):
        conn, path = open_major(MAJORS["clientscript"])
        print(f"### clientscript (major 12)  -> {path.name}")
        if conn is None:
            print("    NOT AVAILABLE")
        else:
            info = table_info(conn)
            print(f"    tables: {info}")
            try:
                n = conn.execute("select count(*) from cache").fetchone()[0]
                ni = conn.execute("select count(*) from cache_index").fetchone()[0]
                print(f"    cache rows: {n}   cache_index rows: {ni}")
            except Exception as e:
                print(f"    count error: {e}")
        print()

    if which in ("enums", "all"):
        conn, path = open_major(MAJORS["enums"])
        print(f"### enums (major 17)  -> {path.name}")
        if conn is None:
            print("    NOT AVAILABLE")
        else:
            try:
                n = conn.execute("select count(*) from cache").fetchone()[0]
                print(f"    cache rows: {n}")
            except Exception as e:
                print(f"    error: {e}")
        print()

    if which in ("components", "all"):
        conn, path = open_major(MAJORS["components"])
        print(f"### components (major 3)  -> {path.name}")
        if conn is None:
            print("    NOT AVAILABLE")
        else:
            try:
                n = conn.execute("select count(*) from cache").fetchone()[0]
                print(f"    cache rows: {n}")
            except Exception as e:
                print(f"    error: {e}")
        print()

    if which in ("varbit", "all"):
        print("=" * 78)
        print("SIGNAL TEST — do the claimed IDs exist in the live BETA cache?")
        print("=" * 78)
        print()
        conn, path = open_major(MAJORS["clientscript"])
        if conn is None:
            print("clientscript unavailable — cannot test")
            return

        info = table_info(conn)
        cols = info.get("cache", [])
        print(f"cache columns: {cols}")
        print()

        # Schema is cache(KEY, DATA, VERSION, CRC)
        rows = list(conn.execute("select KEY, DATA from cache"))
        print(f"loaded {len(rows)} clientscript entries")
        print()

        have = {k: v for k, v in rows if isinstance(v, (bytes, bytearray))}
        print(f"entries with blob payload: {len(have)}")
        print()

        print(f"{'claim':30s} {'id':>7s} {'present':>8s} {'u16 refs':>9s}")
        print("-" * 78)
        for name, cid in sorted(CLAIMS.items(), key=lambda x: x[1]):
            present = cid in have
            refs = 0
            if present:
                for b in have.values():
                    if b is not None:
                        refs += len(scan_blob_for_u16(b, cid))
            print(f"{name:30s} {cid:>7d} {str(present):>8s} {refs:>9d}")
        print()

        # varbit 28749 — the central claim
        print("--- central claim: varbit 28749 (SAVE_CONFIRM) ---")
        total28749 = 0
        scripts_with = []
        for sid, b in have.items():
            if b is None:
                continue
            h16 = scan_blob_for_u16(b, 28749)
            h32 = scan_blob_for_i32(b, 28749)
            if h16 or h32:
                total28749 += len(h16) + len(h32)
                scripts_with.append((sid, len(h16), len(h32)))
        print(f"    total occurrences of 28749 across all clientscripts: {total28749}")
        print(f"    scripts containing it: {len(scripts_with)}")
        for sid, a, b in sorted(scripts_with)[:15]:
            print(f"      script {sid}: u16={a} i32={b}")


if __name__ == "__main__":
    main()
