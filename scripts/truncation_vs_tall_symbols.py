#!/usr/bin/env python3
"""
TRUNCATION vs TALL SYMBOLS — are the big operators being cut off?

Hypothesis: the 500-char MathML truncation cuts exactly the TALL/STRETCHY
operators (\\sum \\prod \\int \\lVert tall braces), because MathML wraps them
in <mo stretchy="true" maxsize=... minsize=...> deep inside nested <mrow>s.

Test: fetch FRESH HTML for one paper, compare
   full MathML   vs   the 500-char truncation stored in the corpus
and count which operators survive each.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402

# --- tall / stretchy operators to count ---
TALL = {
    "sum":      r"\u2211|∑",
    "prod":     r"\u220F|∏",
    "integral": r"\u222B|∫",
    "oint":     r"\u222E|∮",
    "bigcup":   r"\u22C3|⋃",
    "bigcap":   r"\u22C2|⋂",
    "norm":     r"\u2016|‖",
    "lbrace":   r"\{",
    "lparen":   r"\(",
    "stretchy": r'stretchy="true"',
    "maxsize":  r"maxsize=",
    "minsize":  r"minsize=",
    "munder":   r"<munder",
    "munderover": r"<munderover",
}

PAPER = "2605.00155"
corpus = json.loads((ROOT / "DATASETS" / "arxiv_html_corpus" / f"{PAPER}.json")
                    .read_text(encoding="utf-8", errors="replace"))

print("=" * 80)
print("TRUNCATION vs TALL SYMBOLS")
print("=" * 80)
print()

# --- fetch fresh HTML ---
import urllib.request
url = f"https://arxiv.org/html/{PAPER}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
print(f"  fetched {url}  ({len(html)} bytes)")
print()

soup = BeautifulSoup(html, "html.parser")
fresh = soup.find_all("math")
print(f"  <math> tags in fresh HTML: {len(fresh)}")
print(f"  equations in stored corpus: {len(corpus.get('equations', []))}")
print()

# --- build a map from alttext -> full mathml ---
full_by_alt = {}
for tag in fresh:
    alt = tag.get("alttext") or ""
    if alt and alt not in full_by_alt:
        full_by_alt[alt] = str(tag)

print(f"  unique alttexts in fresh HTML: {len(full_by_alt)}")
print()

# --- compare on the target equations ---
TARGETS = [
    r"\Delta_{n}\coloneqq",
    r"\Reg_{x}",
    r"\operatorname*{ess",
    r"\log\bar{\pi}",
]

print("=" * 80)
print("SIDE BY SIDE — stored(500) vs full")
print("=" * 80)
print()

for needle in TARGETS:
    eqs = [e for e in corpus.get("equations", []) if needle in (e.get("latex") or "")]
    if not eqs:
        continue
    e = eqs[0]
    alt = e.get("latex") or ""
    stored = e.get("mathml") or ""
    full = full_by_alt.get(alt, "")

    print(f"--- {needle} ---")
    print(f"  alttext        : {alt[:90]}")
    print(f"  stored len     : {len(stored)}")
    print(f"  full len       : {len(full)}")
    print(f"  cut off        : {max(0, len(full) - len(stored))} chars")
    print()

    print("  TALL OPERATORS — stored vs full:")
    print(f"    {'operator':14s} {'stored':>8s} {'full':>8s} {'lost':>8s}")
    print("    " + "-" * 42)
    for name, pat in TALL.items():
        s = len(re.findall(pat, stored))
        f = len(re.findall(pat, full))
        lost = f - s
        flag = "  <<<" if lost > 0 else ""
        print(f"    {name:14s} {s:>8d} {f:>8d} {lost:>8d}{flag}")
    print()

# --- bulk: how much is lost across the whole paper? ---
print("=" * 80)
print("BULK LOSS ACROSS THE PAPER")
print("=" * 80)
print()
tot_stored = tot_full = 0
lost_tall = {k: 0 for k in TALL}
n = 0
for e in corpus.get("equations", []):
    alt = e.get("latex") or ""
    stored = e.get("mathml") or ""
    full = full_by_alt.get(alt, "")
    if not full:
        continue
    n += 1
    tot_stored += len(stored)
    tot_full += len(full)
    for name, pat in TALL.items():
        lost_tall[name] += max(0, len(re.findall(pat, full)) - len(re.findall(pat, stored)))

print(f"  matched equations      : {n}")
print(f"  total stored mathml    : {tot_stored:,} chars")
print(f"  total full mathml      : {tot_full:,} chars")
if tot_full:
    print(f"  LOST to truncation     : {tot_full - tot_stored:,} chars "
          f"({100*(tot_full-tot_stored)/tot_full:.1f}%)")
print()
print("  tall operators lost:")
for name, lost in sorted(lost_tall.items(), key=lambda x: -x[1]):
    if lost:
        print(f"    {lost:>6d}  {name}")
