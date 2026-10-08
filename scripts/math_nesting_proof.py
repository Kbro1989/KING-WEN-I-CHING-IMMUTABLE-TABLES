#!/usr/bin/env python3
"""
PROVE the root cause: nested braces, not missing commands.

Hypothesis: \frac, \bar, \hat, \dot, \sqrt etc. are ALREADY handled, but the
handlers use [^{}]+ which cannot match a nested group. So \frac{1}{\bar{x}}
fails and the literal \frac survives to be reported "unknown".

Test: does the unknown-ness correlate with NESTING?
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"

# commands the code ALREADY has handlers for
HANDLED = {"\\frac", "\\bar", "\\hat", "\\dot", "\\sqrt", "\\widetilde",
           "\\widehat", "\\ddot", "\\check", "\\vec", "\\tilde", "\\dddot",
           "\\text", "\\mbox", "\\mathrm", "\\mathbf", "\\mathcal", "\\mathbb",
           "\\operatorname", "\\overset", "\\underset"}

latex_all = []
for jf in sorted(CORPUS.glob("*.json")):
    try:
        d = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        continue
    for e in d.get("equations", []):
        if e.get("latex"):
            latex_all.append(e["latex"])

print("=" * 78)
print("NESTING TEST — is 'unknown' caused by nested braces?")
print("=" * 78)
print()

# For each handled command, split occurrences into nested vs flat arg
stats = {}
for cmd in sorted(HANDLED):
    pat = re.compile(re.escape(cmd) + r"\s*\{")
    nested = flat = 0
    for L in latex_all:
        for m in pat.finditer(L):
            i = m.end() - 1
            depth = 0
            k = i
            while k < len(L):
                if L[k] == "{":
                    depth += 1
                elif L[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            inner = L[i + 1:k]
            if "{" in inner:
                nested += 1
            else:
                flat += 1
    if nested or flat:
        stats[cmd] = (nested, flat)

print(f"{'command':16s} {'nested':>8s} {'flat':>8s}  {'%nested':>8s}   reported-unknown?")
print("-" * 78)
# which commands were reported unknown
unknown_seen = Counter()
for L in latex_all:
    try:
        _o, notes = recover_latex(L)
    except Exception:
        continue
    for n in notes:
        if n.startswith("unknown:"):
            for c in n[8:].split(","):
                unknown_seen[c.strip()] += 1

for cmd, (nested, flat) in sorted(stats.items(), key=lambda x: -x[1][0]):
    tot = nested + flat
    pct = 100 * nested / tot if tot else 0
    rep = "YES" if cmd in unknown_seen else "no"
    print(f"{cmd:16s} {nested:>8d} {flat:>8d}  {pct:>7.1f}%   {rep}")

print()
print("=" * 78)
print("DECISIVE CHECK — what property do the FAILING args share?")
print("=" * 78)
print()
print("Corrected hypothesis: handlers use [^{}]+ or [a-zA-Z0-9]+, which")
print("exclude BOTH nested braces AND backslash-commands inside the arg.")
print("  \\hat{r}     -> matches  (r is alphanumeric)")
print("  \\hat{\\mu}  -> FAILS    (arg starts with a backslash)")
print("  \\dot{\\nu}  -> FAILS    (same, and it is 'flat')")
print()

# classify each failing occurrence by what the ARG contains
buckets = Counter()
examples = {}
for L in latex_all:
    try:
        _o, notes = recover_latex(L)
    except Exception:
        continue
    unk = set()
    for n in notes:
        if n.startswith("unknown:"):
            unk |= {c.strip() for c in n[8:].split(",") if c.strip()}
    for cmd in HANDLED:
        if cmd not in unk:
            continue
        pat = re.compile(re.escape(cmd) + r"\s*\{")
        for m in pat.finditer(L):
            i = m.end() - 1
            depth = 0
            k = i
            while k < len(L):
                if L[k] == "{":
                    depth += 1
                elif L[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            inner = L[i + 1:k]
            has_cmd = "\\" in inner
            has_brace = "{" in inner
            if has_brace and has_cmd:
                key = "nested + backslash-cmd"
            elif has_brace:
                key = "nested braces only"
            elif has_cmd:
                key = "backslash-cmd only (FLAT)"
            else:
                key = "plain alphanumeric"
            buckets[key] += 1
            examples.setdefault(key, (cmd, L))

for k, v in buckets.most_common():
    print(f"  {v:>5}  {k}")
print()

plain = buckets.get("plain alphanumeric", 0)
print(f"  occurrences with a PLAIN alphanumeric arg that failed: {plain}")
if plain == 0:
    print("  => ROOT CAUSE CONFIRMED.")
    print("     No plain arg ever fails. Every failure has a nested brace")
    print("     and/or a backslash-command inside the argument.")
else:
    print("  => some plain args still fail; there is a second cause.")
print()

for k, (cmd, L) in examples.items():
    m = re.search(r".{0,22}" + re.escape(cmd) + r".{0,55}", L)
    print(f"  [{k}]")
    print(f"    {cmd}: …{m.group(0) if m else L[:80]}…")
print()
