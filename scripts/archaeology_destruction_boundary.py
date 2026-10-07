#!/usr/bin/env python3
"""
DESTRUCTION BOUNDARY classifier.

D-sovereign- is the save made immediately before the device was destroyed.
Its final commit is therefore the boundary between:
  PRE  (<= boundary) : content that originated on the DESTROYED device
                       (survived only because it was cloned or saved)
  POST (>  boundary) : content authored on the CURRENT machine

This gives every artifact a two-era classification that does not depend on
which repository currently holds it.
"""
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# D-sovereign- final commit / pushed_at — the last save before destruction.
BOUNDARY = datetime(2026, 7, 7, 1, 51, 42, tzinfo=timezone.utc)
BOUNDARY_STR = "2026-07-07T01:51:42Z"

REPOS = {
    "POG2": Path(r"C:\Users\krist\.gemini\antigravity\scratch\POG2"),
    "rsmv-upstream": Path(r"C:\Users\krist\Desktop\rsmv-upstream"),
    "KING-WEN": Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES"),
    "OpenJarvis": Path(r"C:\Users\krist\Desktop\OpenJarvis"),
    "cinder": Path(r"C:\Users\krist\Desktop\cinder"),
}


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo)] + list(args),
                       capture_output=True, text=True, errors="replace")
    return r.stdout.strip()


print("=" * 74)
print(f"DESTRUCTION BOUNDARY = {BOUNDARY_STR}")
print("(D-sovereign- final commit — the save made before the device died)")
print("=" * 74)
print()

for name, path in REPOS.items():
    if not (path / ".git").exists():
        print(f"--- {name}: no .git ---\n")
        continue

    total = git(path, "rev-list", "--count", "HEAD")
    first = git(path, "log", "--reverse", "--format=%cI|%h|%s").splitlines()
    if not first:
        print(f"--- {name}: no commits ---\n")
        continue

    first_line = first[0].split("|", 2)

    # commits at/after boundary
    post = git(path, "log", f"--since={BOUNDARY_STR}",
               "--format=%cI|%h|%s").splitlines()
    post = [l for l in post if l]

    pre_count = int(total) - len(post)

    print(f"--- {name} ---")
    print(f"  first commit : {first_line[0]}  {first_line[1]}  {first_line[2][:52]}")
    print(f"  total commits: {total}")
    print(f"  PRE  (<= {BOUNDARY_STR[:10]}) : {pre_count}   [destroyed-device era]")
    print(f"  POST (>  {BOUNDARY_STR[:10]}) : {len(post)}   [current machine]")
    if post:
        print("  post-boundary commits:")
        for l in post[:12]:
            d, sha, subj = l.split("|", 2)
            print(f"      {d[:19]}  {sha}  {subj[:48]}")
        if len(post) > 12:
            print(f"      ... and {len(post) - 12} more")
    print()

print("=" * 74)
print("ARTIFACT CLASSIFICATION (embedded timestamps / mtimes)")
print("=" * 74)
ARTIFACTS = [
    ("POG2 first commit",              "2026-03-12T21:25:49-05:00", "PRE"),
    ("atlas 1420 generated",           "2026-03-22T21:46:46.890Z",  "PRE"),
    ("D-sovereign- repo created",      "2026-04-19T16:34:41Z",      "PRE"),
    ("POG2 bulk import (Beta cluster)", "2026-05-21T12:20:06-05:00", "PRE"),
    ("Beta enum outputs written",      "2026-06-17T15:19:43-05:00", "PRE"),
    ("D-sovereign- final commit",      BOUNDARY_STR,                "BOUNDARY"),
    ("rsmv .pog2/ dir created",        "2026-09-18T19:33:08-05:00", "POST"),
]
for label, ts, era in ARTIFACTS:
    print(f"  {era:9s}  {ts[:19]:20s}  {label}")
