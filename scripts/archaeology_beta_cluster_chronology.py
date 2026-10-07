#!/usr/bin/env python3
"""
PASS 1 (full) — Beta investigation cluster: complete first-appearance chronology.

The dossier listed ~11 Beta probes. POG2 actually tracks 32. Dating all of them
reveals whether the cluster landed in one bulk import (authoring date unknown)
or accumulated over time (real sequence recoverable).
"""
import subprocess
from pathlib import Path

POG2 = Path(r"C:\Users\krist\.gemini\antigravity\scratch\POG2")


def git(*args):
    r = subprocess.run(["git", "-C", str(POG2)] + list(args),
                       capture_output=True, text=True, errors="replace")
    return r.stdout.strip()


tracked = [l for l in git("ls-files", "scratch/").splitlines() if l]

# Beta investigation cluster: any file whose name references beta/import_save
CLUSTER = [f for f in tracked
           if any(k in f.lower() for k in ("beta", "import_save", "importsave"))]

print(f"=== Beta cluster in POG2 scratch/ : {len(CLUSTER)} tracked files ===")
print()

rows = []
for f in CLUSTER:
    out = git("log", "--diff-filter=A", "--follow", "--format=%ci|%h|%s", "--", f)
    lines = [l for l in out.splitlines() if "|" in l]
    if not lines:
        rows.append((f, "NO COMMIT", "", ""))
        continue
    date, sha, subj = lines[-1].split("|", 2)
    rows.append((f, date, sha, subj))

# Group by first-appearance commit
from collections import defaultdict
by_commit = defaultdict(list)
for f, date, sha, subj in rows:
    by_commit[(date, sha, subj)].append(f)

print("=== FIRST APPEARANCE — grouped by commit ===")
for (date, sha, subj), files in sorted(by_commit.items()):
    print(f"\n  {date}  {sha}")
    print(f"  {subj[:78]}")
    print(f"  files: {len(files)}")
    for f in sorted(files):
        print(f"      {f.replace('scratch/', '')}")

print()
print("=== COMMIT COUNT DISTINCT ===")
print(f"  distinct first-appearance commits: {len(by_commit)}")
print(f"  total cluster files             : {len(CLUSTER)}")

print()
print("=== ALL COMMITS TOUCHING THE CLUSTER (chronological, reverse) ===")
out = git("log", "--reverse", "--format=%ci|%h|%s", "--", "scratch/")
seen = set()
for line in out.splitlines():
    if "|" not in line:
        continue
    date, sha, subj = line.split("|", 2)
    if sha in seen:
        continue
    seen.add(sha)
    print(f"  {date[:19]}  {sha}  {subj[:64]}")
