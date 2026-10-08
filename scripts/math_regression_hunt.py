#!/usr/bin/env python3
"""
REGRESSION HUNT — solvable went 364 -> 360 while recoverable rose.

Recoverable rising with solvable falling means: some equations now translate
into a form the solver rejects. Find exactly which, and why.

Compares the per-equation outcome between two recovery runs.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
A = ROOT / "DATASETS" / "math_recovery_after_fix"
B = ROOT / "DATASETS" / "math_recovery_nested_fix"


def load(d):
    """paper -> {latex: (solvable, error)}"""
    out = {}
    for f in sorted(d.glob("*_recovery.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for r in j.get("results", []):
            L = r.get("latex")
            if not L:
                continue
            out.setdefault(f.stem, {})[L] = (
                bool(r.get("solvable")),
                str(r.get("error") or ""),
                str(r.get("recovered") or r.get("recovered_latex") or ""),
            )
    return out


a, b = load(A), load(B)

print("=" * 78)
print("REGRESSION HUNT — solvable 364 -> 360")
print("=" * 78)
print()

lost = []      # solvable in A, not in B
gained = []    # not solvable in A, solvable in B

for paper in sorted(set(a) | set(b)):
    pa, pb = a.get(paper, {}), b.get(paper, {})
    for L in set(pa) | set(pb):
        sa = pa.get(L, (False, "", ""))
        sb = pb.get(L, (False, "", ""))
        if sa[0] and not sb[0]:
            lost.append((paper, L, sa, sb))
        elif not sa[0] and sb[0]:
            gained.append((paper, L, sa, sb))

print(f"  LOST solvable   : {len(lost)}")
print(f"  GAINED solvable : {len(gained)}")
print()

print("=" * 78)
print("LOST — was solvable, now is not")
print("=" * 78)
print()
for paper, L, sa, sb in lost[:20]:
    print(f"[{paper}]")
    print(f"  LATEX     : {L[:110]}")
    print(f"  A recovered: {sa[2][:90]}")
    print(f"  B recovered: {sb[2][:90]}")
    print(f"  A err={sa[1][:50]!r}  B err={sb[1][:60]!r}")
    print()

print("=" * 78)
print("GAINED — now solvable")
print("=" * 78)
print()
for paper, L, sa, sb in gained[:10]:
    print(f"[{paper}]  {L[:80]}")
    print(f"  B recovered: {sb[2][:90]}")
print()

# bucket the B-side errors for lost equations
from collections import Counter
c = Counter()
for _p, _L, _sa, sb in lost:
    e = sb[1] or "no_error"
    c[e.split(":")[0] if e else "none"] += 1
print("B-side error classes for the LOST set:")
for k, v in c.most_common():
    print(f"  {v:>4}  {k}")
