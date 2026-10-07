#!/usr/bin/env python3
"""
Destruction boundary — CORRECT classification with identity consolidation.

The same person commits under several git author strings
(Kbro1989 / kbro1989 / Kbro / Pick of Gods). Splitting on a single author
string silently drops commits. Consolidate identities first, then classify
by the destruction boundary.

Also separates UPSTREAM (third-party fork) authorship from LOCAL, because a
forked repo's PRE count would otherwise be attributed to the destroyed device.
"""
import re
import subprocess
from collections import Counter
from pathlib import Path

BOUNDARY = "2026-07-07T01:51:42Z"

# All git author identities belonging to the user (Kbro1989 / Kristain33rs).
LOCAL_IDENTITIES = {
    "Kbro1989 <149967879+Kbro1989@users.noreply.github.com>",
    "kbro1989 <kristain33rs@gmail.com>",
    "Pick of Gods <149967879+Kbro1989@users.noreply.github.com>",
    "Kbro <kristain33rs@gmail.com>",
    "Kbro1989 <kbro1989@users.noreply.github.com>",
    "kbro1989 <kbro1989@users.noreply.github.com>",
}
LOCAL_EMAILS = {"kristain33rs@gmail.com", "149967879+kbro1989@users.noreply.github.com",
                "kbro1989@users.noreply.github.com"}

REPOS = {
    "POG2": Path(r"C:\Users\krist\.gemini\antigravity\scratch\POG2"),
    "rsmv-upstream": Path(r"C:\Users\krist\Desktop\rsmv-upstream"),
    "KING-WEN": Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES"),
    "OpenJarvis": Path(r"C:\Users\krist\Desktop\OpenJarvis"),
    "cinder": Path(r"C:\Users\krist\Desktop\cinder"),
    "OpenJarvis-original": Path(r"C:\Users\krist\Desktop\OpenJarvis-original"),
}


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo)] + list(args),
                       capture_output=True, text=True, errors="replace")
    return r.stdout.strip()


def is_local(author: str) -> bool:
    if author in LOCAL_IDENTITIES:
        return True
    m = re.search(r"<([^>]+)>", author)
    return bool(m and m.group(1).lower() in LOCAL_EMAILS)


print("=" * 80)
print(f"DESTRUCTION BOUNDARY = {BOUNDARY}")
print("=" * 80)
print()

summary = []

for name, path in REPOS.items():
    if not (path / ".git").exists():
        print(f"--- {name}: NOT a git repo / absent ---\n")
        continue

    lines = git(path, "log", "--format=%cI\t%an <%ae>\t%s").splitlines()
    lines = [l for l in lines if l.strip()]

    local_pre = local_post = up_pre = up_post = 0
    earliest_local = None
    for l in lines:
        parts = l.split("\t")
        if len(parts) < 2:
            continue
        date, author = parts[0], parts[1]
        if is_local(author):
            if date <= BOUNDARY:
                local_pre += 1
                if earliest_local is None or date < earliest_local:
                    earliest_local = date
            else:
                local_post += 1
        else:
            if date <= BOUNDARY:
                up_pre += 1
            else:
                up_post += 1

    total = len(lines)
    print(f"--- {name}  ({total} commits) ---")
    print(f"    LOCAL  PRE  (destroyed device) : {local_pre:4d}")
    print(f"    LOCAL  POST (this host)        : {local_post:4d}")
    print(f"    UPSTREAM PRE / POST            : {up_pre:4d} / {up_post}")
    if earliest_local:
        print(f"    earliest LOCAL commit          : {earliest_local[:19]}")
    print()

    summary.append((name, total, local_pre, local_post, up_pre, up_post))

print("=" * 80)
print("SUMMARY — user's own commits, split by destruction")
print("=" * 80)
print(f"{'repo':22s} {'LOCAL PRE':>10s} {'LOCAL POST':>11s} {'upstream':>10s}")
print("-" * 80)
for name, total, lp, lpo, upre, upo in summary:
    print(f"{name:22s} {lp:>10d} {lpo:>11d} {upre + upo:>10d}")
print("-" * 80)
tp = sum(s[2] for s in summary)
tpo = sum(s[3] for s in summary)
tu = sum(s[4] + s[5] for s in summary)
print(f"{'TOTAL':22s} {tp:>10d} {tpo:>11d} {tu:>10d}")
print()
print(f"  Of the user's own commits, {tp} are destroyed-device era and {tpo} are this-host era.")
print(f"  Ratio: {tp / max(tpo,1):.1f} : 1")
