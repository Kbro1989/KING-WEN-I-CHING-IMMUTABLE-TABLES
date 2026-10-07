"""
Forensic read v2: show the TRUE source LaTeX (arxiv alttext) next to our
tree-derived translation, so the two can actually be compared.

v1 bug: the display path stores the tree expr in the 'latex' field, so the
comparison was a thing against itself. This version pulls alttext directly
from the live HTML.
"""
import sys, json, urllib.request, re
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
from mathml_parser import MathMLParser

def fetch(aid):
    url = f"https://arxiv.org/html/{aid}"
    req = urllib.request.Request(url, headers={"User-Agent": "forensic/1.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def alttext_map(html):
    """Map tree-expr -> true source LaTeX (alttext)."""
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for m in soup.find_all("math"):
        alt = (m.get("alttext") or "").strip()
        p = MathMLParser()
        e, u = p.parse(m)
        if e and alt:
            out[e] = alt
    return out

TARGETS = ["2605.28896", "2605.25334", "2605.18130"]

for aid in TARGETS:
    d = json.load(open(f"DATASETS/math_recovery_display/{aid}_recovery.json"))
    html = fetch(aid)
    amap = alttext_map(html)

    print("=" * 78)
    print(f"PAPER {aid}")
    print("=" * 78)

    shown = 0
    for r in d.get("results", []):
        if not r.get("error"):
            continue
        if r["error"].startswith("markup_leaked"):
            continue
        if shown >= 5:
            break
        tree = r["recovered"]
        src = amap.get(tree, "(alttext not matched)")
        print()
        print(f"  ERROR      : {r['error']}")
        print(f"  TRUE LATEX : {src[:170]}")
        print(f"  OUR TREE   : {tree[:170]}")
        shown += 1
    print()
