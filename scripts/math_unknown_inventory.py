#!/usr/bin/env python3
"""
EXPOSE THE UNKNOWNS — mine every unhandled LaTeX command from the real corpus.

Reads the arxiv HTML corpus (pulled directly from arxiv.org), runs recover_latex
on every equation, and inventories every command that ends up in the
"unknown:" note. Then reports each one's STRUCTURE so the parsing rules can be
written from evidence instead of guesswork.

For each unknown command we report:
  - occurrence count
  - the argument shape it appears with (braced / bare / none)
  - representative raw LaTeX
  - what the current code does to it (drops it, keeps arg, mangles)
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from math_recovery_tool import recover_latex  # noqa: E402

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"

# ---------------------------------------------------------------- collect latex
latex_all = []
for jf in sorted(CORPUS.glob("*.json")):
    try:
        d = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        continue
    for e in d.get("equations", []):
        L = e.get("latex")
        if L:
            latex_all.append((jf.stem, L))

print("=" * 78)
print("CORPUS INPUT — verified direct from arxiv.org HTML")
print("=" * 78)
print(f"  corpus dir : {CORPUS}")
print(f"  papers     : {len(list(CORPUS.glob('*.json')))}")
print(f"  equations  : {len(latex_all)}")
print()

# ---------------------------------------------------------------- run recovery
unknown_counter = Counter()
unknown_examples = defaultdict(list)
unknown_shape = defaultdict(Counter)

for pid, L in latex_all:
    try:
        _out, notes = recover_latex(L)
    except Exception:
        continue
    for n in notes:
        if not n.startswith("unknown:"):
            continue
        for cmd in n[len("unknown:"):].split(","):
            cmd = cmd.strip()
            if not cmd:
                continue
            unknown_counter[cmd] += 1
            if len(unknown_examples[cmd]) < 4:
                unknown_examples[cmd].append((pid, L))

# ---------------------------------------------------------------- classify shape
def shape_of(cmd, latex_samples):
    """Determine how the command is used: braced / bare-arg / zero-arg."""
    braced = bare = none = 0
    for _pid, L in latex_samples:
        # find every occurrence
        for m in re.finditer(re.escape(cmd) + r"\s*(.)", L):
            nxt = m.group(1)
            if nxt == "{":
                braced += 1
            elif nxt in " \\":
                none += 1
            else:
                bare += 1
    if braced and not bare and not none:
        return "braced{arg}"
    if bare and not braced and not none:
        return "bare_arg"
    if none and not braced and not bare:
        return "zero_arg"
    parts = []
    if braced:
        parts.append(f"braced={braced}")
    if bare:
        parts.append(f"bare={bare}")
    if none:
        parts.append(f"none={none}")
    return "mixed(" + ",".join(parts) + ")"


print("=" * 78)
print(f"UNKNOWN COMMANDS — {len(unknown_counter)} distinct")
print("=" * 78)
print()
print(f"{'command':26s} {'count':>6s}  {'shape':22s}")
print("-" * 78)
for cmd, n in unknown_counter.most_common():
    sh = shape_of(cmd, unknown_examples[cmd])
    unknown_shape[cmd] = sh
    print(f"{cmd:26s} {n:>6d}  {sh:22s}")
print()

# ---------------------------------------------------------------- detail per cmd
print("=" * 78)
print("STRUCTURE DETAIL (top 25) — what each command actually looks like")
print("=" * 78)
print()
for cmd, n in unknown_counter.most_common(25):
    print(f"─── {cmd}   ({n} occurrences, {unknown_shape[cmd]}) ───")
    for pid, L in unknown_examples[cmd][:3]:
        # show the command in context
        m = re.search(r".{0,40}" + re.escape(cmd) + r".{0,55}", L)
        ctx = m.group(0) if m else L[:95]
        print(f"    [{pid}] …{ctx}…")
    # what does the current pipeline turn it into?
    try:
        out, _ = recover_latex(unknown_examples[cmd][0][1])
        m2 = re.search(r".{0,30}" + re.escape(cmd.lstrip("\\")) + r".{0,30}", out)
        print(f"    after recovery: {out[:95]}")
    except Exception as e:
        print(f"    after recovery: <error {e}>")
    print()

# ---------------------------------------------------------------- shape summary
print("=" * 78)
print("SHAPE SUMMARY — group by argument structure")
print("=" * 78)
print()
by_shape = defaultdict(list)
for cmd, sh in unknown_shape.items():
    key = sh.split("(")[0]
    by_shape[key].append(cmd)
for sh, cmds in sorted(by_shape.items(), key=lambda x: -len(x[1])):
    print(f"  {sh:12s} ({len(cmds):>2d}): {' '.join(sorted(cmds))}")
print()

# ---------------------------------------------------------------- fix priority
print("=" * 78)
print("FIX PRIORITY — ranked by equations that would gain a known-clean path")
print("=" * 78)
print()
# count equations whose ONLY unknowns are a given command
sole = Counter()
for pid, L in latex_all:
    try:
        _o, notes = recover_latex(L)
    except Exception:
        continue
    cmds = set()
    for n in notes:
        if n.startswith("unknown:"):
            cmds |= {c.strip() for c in n[len("unknown:"):].split(",") if c.strip()}
    if len(cmds) == 1:
        sole[list(cmds)[0]] += 1
print(f"  equations where a single unknown is the ONLY blocker:")
for cmd, n in sole.most_common(20):
    print(f"    {n:>4}  {cmd}   ({unknown_shape.get(cmd,'?')})")

# save
outp = ROOT / "DATASETS" / "unknown_command_inventory.json"
outp.write_text(json.dumps({
    "corpus": str(CORPUS),
    "papers": len(list(CORPUS.glob('*.json'))),
    "equations": len(latex_all),
    "distinct_unknowns": len(unknown_counter),
    "unknowns": [
        {"command": c, "count": n, "shape": unknown_shape[c],
         "examples": [{"paper": p, "latex": L} for p, L in unknown_examples[c][:4]],
         "sole_blocker_equations": sole.get(c, 0)}
        for c, n in unknown_counter.most_common()
    ],
}, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"inventory written: {outp}")
