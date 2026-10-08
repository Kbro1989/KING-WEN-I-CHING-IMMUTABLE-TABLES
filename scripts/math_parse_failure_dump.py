#!/usr/bin/env python3
"""
PARSE-FAILURE DUMP — every equation that fails for a PARSER reason.

Goal: 100% resolvable at the base. That means ZERO of these buckets:
    parse:SyntaxError
    parse:TypeError
    parse:TokenError
    parse:LaTeXParsingError
    <any "unknown:" note surviving to the solver>

These are OUR bugs. The legitimate buckets are:
    no_equality / multiple_equalities  -> not an equation, correctly refused
    empty / empty_side                 -> fragment, correctly refused
    not_an_equation:relation:*         -> relation, correctly refused

Dumps each parse failure with: latex -> recovered -> error, so the defect
is visible without re-running.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"

PARSE_FAIL_PREFIX = ("parse:",)

rows = []
for jf in sorted(CORPUS.glob("*.json")):
    try:
        d = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        continue
    for e in d.get("equations", []):
        L = e.get("latex")
        if not L:
            continue
        try:
            rec, notes = recover_latex(L)
        except Exception as ex:
            rows.append((jf.stem, L, "<RECOVER CRASH>", f"{type(ex).__name__}: {ex}", notes if 'notes' in dir() else []))
            continue
        unk = [n for n in notes if n.startswith("unknown:")]
        rows.append((jf.stem, L, rec, "", unk))

print("=" * 80)
print(f"TOTAL equations: {len(rows)}")
print("=" * 80)
print()

# --- how many still carry an unknown command? ---
with_unk = [r for r in rows if r[4]]
unk_cmds = Counter()
for r in with_unk:
    for n in r[4]:
        for c in n[8:].split(","):
            if c.strip():
                unk_cmds[c.strip()] += 1

print(f"equations still carrying an unknown command: {len(with_unk)}")
print()
print("unknown commands remaining (command: equations affected):")
for c, n in unk_cmds.most_common(40):
    print(f"  {n:>5}  {c}")
print()

# --- dump recovered strings that still contain a backslash (untranslated) ---
print("=" * 80)
print("RECOVERED STRINGS STILL CONTAINING A BACKSLASH  (hard parse failures)")
print("=" * 80)
print()
still_bs = [r for r in rows if "\\" in r[2]]
print(f"count: {len(still_bs)}")
print()
seen_pat = Counter()
for pid, L, rec, err, unk in still_bs:
    # which command is still present?
    import re as _re
    for m in _re.finditer(r"\\[a-zA-Z]+", rec):
        seen_pat[m.group(0)] += 1
print("backslash commands surviving into the recovered string:")
for c, n in seen_pat.most_common(30):
    print(f"  {n:>5}  {c}")
print()

print("=" * 80)
print("SAMPLE — still-broken recovered strings")
print("=" * 80)
print()
for pid, L, rec, err, unk in still_bs[:25]:
    print(f"[{pid}]")
    print(f"  LATEX    : {L[:120]}")
    print(f"  RECOVERED: {rec[:120]}")
    print()

# --- save the full dump ---
out = ROOT / "DATASETS" / "parse_failure_dump.json"
out.write_text(json.dumps([
    {"paper": p, "latex": L, "recovered": r, "error": e, "unknown": u}
    for p, L, r, e, u in rows if u or "\\" in r
], indent=2, ensure_ascii=False), encoding="utf-8")
print(f"dump written: {out}")
