#!/usr/bin/env python3
"""
CONTAMINATION TEST — is page/footer/sidebar numbering leaking into the math?

Hypothesis: the extractor is capturing surrounding chrome (equation tags like
"(1)", page numbers, footer/sidebar text) as part of the equation, and that is
what produces the residual SyntaxErrors.

Tests, in order:
  1. Do failing equations contain a trailing/leading number in parens?
  2. Do they contain known chrome words (Page, Figure, Table, arXiv, Preprint)?
  3. Do they contain long digit runs (page numbers / dates)?
  4. Does the raw HTML region around the <math> contain chrome that we capture?
  5. Compare chrome presence in FAILING vs PASSING equations (control).
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

# --- chrome signatures that would indicate page/footer/sidebar capture ---
CHROME = {
    "paren_number":     r"\(\s*\d{1,3}\s*\)",         # equation tag (1)
    "bracket_number":   r"\[\s*\d{1,3}\s*\]",         # [12] citation
    "page_word":        r"\b[Pp]age\b",
    "figure_word":      r"\b[Ff]igure\b",
    "table_word":       r"\b[Tt]able\b",
    "section_word":     r"\b[Ss]ection\b",
    "arxiv_word":       r"arXiv",
    "preprint":         r"[Pp]reprint",
    "doi":              r"doi|DOI",
    "copyright":        r"[Cc]opyright|©",
    "sidebar":          r"\b(Home|Browse|Search|Submit|Login|Help)\b",
    "long_digits":      r"\d{4,}",
    "date_like":        r"\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
    "trailing_num":     r"[\s,;]\d{1,3}\s*$",
    "leading_num":      r"^\s*\d{1,3}[\s,;]",
    "nl_artifact":      r"\\n|\r|\t",
    "html_tag":         r"<[a-zA-Z/]",
    "amp_entity":       r"&[a-z]+;|&#\d+;",
}

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
        except Exception:
            rec, notes = "", []
        unk = [n for n in notes if n.startswith("unknown:")]
        # classify outcome
        has_bs = "\\" in rec
        rows.append({
            "paper": jf.stem, "latex": L, "recovered": rec,
            "unknown": bool(unk), "backslash_left": has_bs,
        })

print("=" * 80)
print(f"CONTAMINATION TEST — {len(rows)} equations")
print("=" * 80)
print()

failing = [r for r in rows if r["unknown"] or r["backslash_left"]]
passing = [r for r in rows if not (r["unknown"] or r["backslash_left"])]
print(f"  still-broken : {len(failing)}")
print(f"  clean        : {len(passing)}")
print()

def chrome_profile(items, key):
    c = Counter()
    for r in items:
        t = r[key]
        for name, pat in CHROME.items():
            if re.search(pat, t):
                c[name] += 1
    return c

print("=" * 80)
print("CHROME SIGNATURES — FAILING vs CLEAN  (count / percentage)")
print("=" * 80)
print()
cf = chrome_profile(failing, "latex")
cp = chrome_profile(passing, "latex")
print(f"{'signature':18s} {'failing':>16s} {'clean':>16s}  verdict")
print("-" * 80)
for name in CHROME:
    nf, np_ = cf.get(name, 0), cp.get(name, 0)
    pf = 100 * nf / max(len(failing), 1)
    pp = 100 * np_ / max(len(passing), 1)
    # is it enriched in failing?
    verdict = ""
    if nf and pf > pp * 2 and nf >= 3:
        verdict = "  <<< ENRICHED IN FAILING"
    print(f"{name:18s} {nf:>7d} ({pf:>5.1f}%) {np_:>7d} ({pp:>5.1f}%){verdict}")

print()
print("=" * 80)
print("SAMPLE FAILING EQUATIONS WITH CHROME MARKERS")
print("=" * 80)
print()
shown = 0
for r in failing:
    t = r["latex"]
    hits = [n for n, p in CHROME.items() if re.search(p, t)]
    if hits:
        print(f"[{r['paper']}] markers={hits}")
        print(f"  LATEX : {t[:150]}")
        print(f"  RECOV : {r['recovered'][:110]}")
        print()
        shown += 1
        if shown >= 15:
            break
if shown == 0:
    print("  (none — no failing equation carries a chrome marker)")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
enriched = [n for n in CHROME
            if cf.get(n, 0) >= 3 and
            (100 * cf.get(n, 0) / max(len(failing), 1)) > 2 * (100 * cp.get(n, 0) / max(len(passing), 1))]
if enriched:
    print(f"  chrome signatures enriched in FAILING: {enriched}")
    print("  => contamination is a real contributor. Investigate the extractor.")
else:
    print("  NO chrome signature is enriched in the failing set.")
    print("  => page/footer/sidebar numbering is NOT the cause of the residual")
    print("     parse failures. The failures are LaTeX-structure defects.")
