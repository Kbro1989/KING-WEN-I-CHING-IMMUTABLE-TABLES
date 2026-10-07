#!/usr/bin/env python3
"""
Meaningful inventory drift: ALL-FILES.csv vs live disk, excluding .git internals.

The raw diff is dominated by git object churn (not project content). This
reports the drift that actually matters: files added/removed from the
project's own subtrees.

Also checks the self-reference hazard: the generator writes ALL-FILES.csv into
the root it walks, so the inventory should contain itself.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
CSV_PATH = ROOT / "ALL-FILES.csv"
FIND_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_kw_files_tmp.txt"

IGNORE_PREFIXES = (".git/",)


def norm(p: str) -> str:
    return p.replace("\\", "/").strip()


def ignored(p: str) -> bool:
    return p.startswith(IGNORE_PREFIXES)


csv_files, csv_dirs = set(), set()
with open(CSV_PATH, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        rel = norm(r["relative_path"])
        (csv_files if r["type"] == "file" else csv_dirs).add(rel.rstrip("/"))

find_files = set()
for line in open(FIND_PATH, encoding="utf-8", errors="replace"):
    p = line.strip()
    if p.startswith("./"):
        p = p[2:]
    if p:
        find_files.add(norm(p))

cf = {p for p in csv_files if not ignored(p)}
ff = {p for p in find_files if not ignored(p)}

only_csv = cf - ff
only_find = ff - cf

print("=== INVENTORY SUMMARY ===")
print(f"CSV rows           : {len(csv_files) + len(csv_dirs)}  "
      f"({len(csv_files)} files + {len(csv_dirs)} dirs)")
print(f"live (excluding .git): {len(ff)} files")
print()
print(f"CSV files, excl .git : {len(cf)}")
print(f"live files, excl .git: {len(ff)}")
print(f"  gone since CSV     : {len(only_csv)}")
print(f"  added since CSV    : {len(only_find)}")
print()

print("=== ADDED since CSV — by top-level dir ===")
for k, v in Counter(p.split("/")[0] for p in only_find).most_common(20):
    print(f"  {v:6d}  {k}")
print()

print("=== ADDED since CSV — by extension ===")
for k, v in Counter(Path(p).suffix.lower() or "(none)" for p in only_find).most_common(15):
    print(f"  {v:6d}  {k}")
print()

print("=== GONE since CSV — by top-level dir ===")
for k, v in Counter(p.split("/")[0] for p in only_csv).most_common(20):
    print(f"  {v:6d}  {k}")
print()

print(f"=== GONE — full list ({len(only_csv)}) ===")
for p in sorted(only_csv):
    print("  ", p)
print()

print("=== ADDED — scripts/ (full list) ===")
for p in sorted(p for p in only_find if p.startswith("scripts/")):
    print("  ", p)
print()

print("=== ADDED — DATASETS/ (first 40) ===")
ds = sorted(p for p in only_find if p.startswith("DATASETS/"))
for p in ds[:40]:
    print("  ", p)
if len(ds) > 40:
    print(f"   ... and {len(ds) - 40} more")
print()

print("=== ADDED — docs/ (full list) ===")
for p in sorted(p for p in only_find if p.startswith("docs/")):
    print("  ", p)
print()

print("=== SELF-REFERENCE CHECK ===")
for self_file in ["ALL-FILES.csv", "ALL-FILES.md", "make_all_files_csv.py"]:
    print(f"  {self_file:24s} in CSV inventory: {self_file in csv_files}")
