#!/usr/bin/env python3
"""
FAILURE CORPUS — one durable record per failing equation.

Every failure is retained as:
    input -> parser stage -> exact exception -> structural context
          -> attempted repair -> successful repair -> regression case

This is the artifact that turns "we fixed 5 regexes" into a mathematical
language front-end: one real-world construct -> one invariant -> one repair.

Output: DATASETS/math_failure_corpus.jsonl
        DATASETS/math_failure_corpus_summary.json
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex, _brace_scan  # noqa: E402

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"

# ---------------------------------------------------------------- stage model
# The transformation state machine. Each equation lands in exactly one state.
STATES = [
    "NO_EQUATION",       # no relation at all -> correctly rejected
    "MULTI_EQUATION",    # more than one top-level relation -> ambiguous
    "EMPTY",             # nothing left after normalisation
    "UNKNOWN_COMMAND",   # a LaTeX command we do not handle survived
    "BACKSLASH_LEFT",    # a backslash reached the target language
    "PARSE_SYNTAX",      # target-language syntax error
    "PARSE_TYPE",        # target-language type error
    "PARSE_TOKEN",       # target-language token error
    "NOT_PRESERVED",     # translation changed the mathematics
    "RECOVERABLE",       # translates cleanly, not solved
    "SOLVABLE",          # solved
]

# ---------------------------------------------------------------- structures
def structural_signature(L):
    """Which LaTeX constructs are present — the reusable-invariant key."""
    sig = {}
    for name, pat in (
        ("frac", r"\\[dtc]?frac"),
        ("sqrt", r"\\sqrt"),
        ("sum", r"\\sum"), ("prod", r"\\prod"), ("int", r"\\int"),
        ("lim", r"\\lim"), ("bigop_limits", r"\\[a-z]+\s*[_^]\s*\{"),
        ("sub", r"_"), ("sup", r"\^"),
        ("text_cmd", r"\\text|\\mbox|\\mathrm|\\textup|\\textbf"),
        ("accent", r"\\hat|\\bar|\\tilde|\\dot|\\vec|\\widehat|\\widetilde"),
        ("matrix_env", r"\\begin\{(?:matrix|pmatrix|bmatrix|cases|array|aligned|split)"),
        ("left_right", r"\\left|\\right"),
        ("norm", r"\\\||\\lVert|\\rVert"),
        ("relation", r"=|\\leq|\\geq|\\approx|\\sim|\\in|\\propto"),
        ("set", r"\\\{|\\\}"),
        ("comma", r","), ("semicolon", r";"),
        ("prime", r"\\prime|\^\{\\prime"), ("dagger", r"\\dagger"),
        ("mathbb", r"\\mathbb"), ("mathcal", r"\\mathcal"), ("bm", r"\\bm|\\boldsymbol"),
        ("operatorname", r"\\operatorname"), ("mathop", r"\\mathop"),
        ("nonascii", r"[^\x00-\x7F]"),
        ("dollar", r"\$"),
        ("nbsp_cmd", r"\\,|\\!|\\;|\\quad|\\qquad"),
    ):
        if re.search(pat, L):
            sig[name] = True
    return sig


def nesting_depth(L):
    """Max brace depth — the recurring root cause."""
    d = mx = 0
    for ch in L:
        if ch == "{":
            d += 1
            mx = max(mx, d)
        elif ch == "}":
            d -= 1
    return mx


def classify(L, rec, notes):
    """Map an equation to exactly one state."""
    unk = [n for n in notes if n.startswith("unknown:")]
    if unk:
        return "UNKNOWN_COMMAND"
    if "\\" in rec:
        return "BACKSLASH_LEFT"
    if not rec.strip():
        return "EMPTY"
    rel = re.findall(r"(?<![<>!=])=(?!=)", rec)
    if len(rel) == 0:
        return "NO_EQUATION"
    if len(rel) > 1:
        return "MULTI_EQUATION"
    return "RECOVERABLE"


records = []
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
            crash = ""
        except Exception as ex:
            rec, notes = "", []
            crash = f"{type(ex).__name__}: {ex}"
        state = "PARSE_SYNTAX" if crash else classify(L, rec, notes)
        records.append({
            "paper": jf.stem,
            "index": e.get("index"),
            "is_display": e.get("is_display"),
            "state": state,
            "latex": L,
            "recovered": rec,
            "crash": crash,
            "unknown": [n[8:] for n in notes if n.startswith("unknown:")],
            "notes": notes,
            "structure": structural_signature(L),
            "max_brace_depth": nesting_depth(L),
            "latex_len": len(L),
        })

print("=" * 78)
print(f"FAILURE CORPUS — {len(records)} equations")
print("=" * 78)
print()

by_state = Counter(r["state"] for r in records)
print("TRANSFORMATION STATE MACHINE — every equation classified")
print()
for s in STATES:
    n = by_state.get(s, 0)
    pct = 100 * n / len(records)
    print(f"  {s:18s} {n:>6d}  {pct:>6.2f}%")
print()

# --- structural signature of the FIXABLE states ---
FIXABLE = ("UNKNOWN_COMMAND", "BACKSLASH_LEFT", "PARSE_SYNTAX", "EMPTY")
fixable = [r for r in records if r["state"] in FIXABLE]
print("=" * 78)
print(f"FIXABLE SET: {len(fixable)} equations")
print("=" * 78)
print()
sig_count = Counter()
for r in fixable:
    for k in r["structure"]:
        sig_count[k] += 1
print("structural constructs in the fixable set:")
for k, v in sig_count.most_common(25):
    print(f"  {v:>5}  {k}")
print()

print("max brace depth distribution (fixable):")
dep = Counter(r["max_brace_depth"] for r in fixable)
for k in sorted(dep):
    print(f"  depth {k}: {dep[k]}")
print()

# --- unknown command inventory with structure ---
print("=" * 78)
print("UNKNOWN COMMANDS — with the constructs they co-occur with")
print("=" * 78)
print()
unk_struct = defaultdict(Counter)
unk_count = Counter()
for r in fixable:
    for u in r["unknown"]:
        for c in u.split(","):
            c = c.strip()
            if not c:
                continue
            unk_count[c] += 1
            for k in r["structure"]:
                unk_struct[c][k] += 1
for c, n in unk_count.most_common(25):
    top = ", ".join(k for k, _ in unk_struct[c].most_common(4))
    print(f"  {n:>5}  {c:22s}  co-occurs with: {top}")
print()

# --- the highest-value artifact: repair candidates grouped by construct ---
print("=" * 78)
print("REPAIR CANDIDATES — grouped by the construct that causes them")
print("=" * 78)
print()
groups = defaultdict(list)
for r in fixable:
    if r["unknown"]:
        key = "unknown:" + r["unknown"][0].split(",")[0].strip()
    elif "\\" in r["recovered"]:
        m = re.search(r"\\[a-zA-Z]+", r["recovered"])
        key = "backslash:" + (m.group(0) if m else "?")
    elif not r["recovered"].strip():
        key = "empty_output"
    else:
        key = "other"
    groups[key].append(r)

for key, items in sorted(groups.items(), key=lambda x: -len(x[1]))[:20]:
    ex = items[0]
    print(f"  {len(items):>5}  {key}")
    print(f"         e.g. {ex['latex'][:96]}")
print()

# ---------------------------------------------------------------- write
out = ROOT / "DATASETS" / "math_failure_corpus.jsonl"
with open(out, "w", encoding="utf-8") as fh:
    for r in records:
        if r["state"] in FIXABLE or r["state"] == "PARSE_SYNTAX":
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

summary = {
    "corpus": str(CORPUS),
    "total": len(records),
    "by_state": dict(by_state),
    "fixable": len(fixable),
    "unknown_commands": dict(unk_count.most_common()),
    "brace_depth_fixable": {str(k): v for k, v in sorted(dep.items())},
    "repair_groups": {k: len(v) for k, v in sorted(groups.items(), key=lambda x: -len(x[1]))},
}
out2 = ROOT / "DATASETS" / "math_failure_corpus_summary.json"
out2.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"wrote: {out}  ({len(fixable)} fixable records)")
print(f"wrote: {out2}")
