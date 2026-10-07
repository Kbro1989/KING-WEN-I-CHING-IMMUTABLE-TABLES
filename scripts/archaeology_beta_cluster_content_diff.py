#!/usr/bin/env python3
"""
PASS 2 (full) — quantify the POG2 scratch/ -> rsmv .pog2/ migration.

420 shared filenames is not a "few scratch scripts". Determine the true
transfer size and how uniform the import rewrite is. A uniform rewrite across
hundreds of files is machine-performed relocation, not independent authorship.
"""
import hashlib
import re
import subprocess
from collections import Counter
from pathlib import Path

POG2 = Path(r"C:\Users\krist\.gemini\antigravity\scratch\POG2\scratch")
RSMV = Path(r"C:\Users\krist\Desktop\rsmv-upstream\scripts\.pog2\sovereign\sovereign")


def md5(p):
    try:
        return hashlib.md5(p.read_bytes()).hexdigest()
    except Exception:
        return None


def imports(p):
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    return [m.group(1) for m in re.finditer(r'from\s+"(\.[^"]*)"', txt)]


pog2_files = {f.name: f for f in POG2.iterdir() if f.is_file()}
rsmv_files = {f.name: f for f in RSMV.iterdir() if f.is_file()}

shared = set(pog2_files) & set(rsmv_files)
print("=== TRANSFER SIZE ===")
print(f"  POG2 scratch/ files        : {len(pog2_files)}")
print(f"  rsmv .pog2/ files          : {len(rsmv_files)}")
print(f"  shared filenames           : {len(shared)}")
print(f"  only in POG2               : {len(set(pog2_files) - set(rsmv_files))}")
print(f"  only in rsmv               : {len(set(rsmv_files) - set(pog2_files))}")
print()

ident, differ = [], []
for n in sorted(shared):
    if md5(pog2_files[n]) == md5(rsmv_files[n]):
        ident.append(n)
    else:
        differ.append(n)

print(f"  byte-identical             : {len(ident)}")
print(f"  differing                  : {len(differ)}")
print()

# --- How uniform is the rewrite? ---
print("=== IMPORT REWRITE UNIFORMITY ===")
rewrites = Counter()
with_rsmv_seg = 0
for n in differ:
    pi, ri = imports(pog2_files[n]), imports(rsmv_files[n])
    for a in pi:
        if "rsmv" in a:
            with_rsmv_seg += 1
            b = a.replace("/rsmv/", "/").replace("../rsmv/", "../")
            rewrites["rsmv_segment_stripped"] += 1
    for a in pi:
        if "rsmv" not in a and a not in ri and ri:
            rewrites["other_import_change"] += 1

print(f"  files whose POG2 import path contains 'rsmv' : {with_rsmv_seg}")
for k, v in rewrites.most_common():
    print(f"  {k:28s}: {v}")
print()

# Sample the rewrite map
print("=== SAMPLE IMPORT REWRITE MAP (POG2 -> rsmv) ===")
shown = 0
for n in sorted(differ):
    pi, ri = imports(pog2_files[n]), imports(rsmv_files[n])
    for a, b in zip(pi, ri):
        if a != b:
            print(f"  {a:42s} ->  {b}")
            shown += 1
            break
    if shown >= 14:
        break
print()

# --- Other kinds of change ---
print("=== NON-IMPORT CHANGES (sample) ===")
ts_modern = 0
for n in sorted(differ):
    r = subprocess.run(["diff", "-u", str(pog2_files[n]), str(rsmv_files[n])],
                       capture_output=True, text=True, errors="replace")
    d = [l for l in r.stdout.splitlines()
         if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))]
    if d and not any("import" in l for l in d):
        ts_modern += 1
        if ts_modern <= 6:
            print(f"\n  {n}")
            for l in d[:8]:
                print(f"    {l[:110]}")
print(f"\n  files with non-import edits: {ts_modern}")
print()

# --- Which POG2 scratch files did NOT migrate? ---
print("=== POG2 scratch/ FILES NOT PRESENT IN rsmv .pog2/ ===")
notmig = sorted(set(pog2_files) - set(rsmv_files))
for n in notmig[:40]:
    print(f"  {n}")
if len(notmig) > 40:
    print(f"  ... and {len(notmig) - 40} more")
