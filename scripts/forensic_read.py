"""
Forensic read: take failed formulas and pull the surrounding paper context so
we can infer what the equation actually needs.

For each failure we show:
  - the source LaTeX (arxiv alttext / annotation)
  - what our translation produced
  - the error class
  - the sentence BEFORE and AFTER in the paper
"""
import sys, json, glob, urllib.request, re
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup

def fetch(aid):
    url = f"https://arxiv.org/html/{aid}"
    req = urllib.request.Request(url, headers={"User-Agent": "forensic/1.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def context_for(html, needle, window=260):
    """Find the needle in the HTML text and return surrounding prose."""
    soup = BeautifulSoup(html, "html.parser")
    # map math node -> surrounding block text
    for m in soup.find_all("math"):
        ann = m.find("annotation")
        if not ann:
            continue
        latex = ann.get_text().strip()
        if needle and needle[:40] in latex:
            block = m.find_parent(["p", "div", "td", "li"])
            if block:
                txt = block.get_text(" ", strip=True)
                txt = re.sub(r"\s+", " ", txt)
                return txt[:window]
    return ""

# failures to investigate, grouped by error class
TARGETS = {
    "2605.28896": ["parse:SyntaxError", "parse:TypeError"],
    "2605.25334": ["parse:TypeError", "solve:NotImplementedError"],
    "2605.18130": ["parse:SyntaxError", "parse:TypeError"],
}

for aid, errs in TARGETS.items():
    path = f"DATASETS/math_recovery_display/{aid}_recovery.json"
    try:
        d = json.load(open(path))
    except Exception as e:
        print(f"skip {aid}: {e}")
        continue

    html = fetch(aid)
    print("=" * 78)
    print(f"PAPER {aid}")
    print("=" * 78)

    shown = 0
    for r in d.get("results", []):
        if r.get("error") not in errs:
            continue
        if shown >= 4:
            break
        print()
        print(f"  ERROR CLASS : {r['error']}")
        print(f"  SOURCE LATEX: {r['latex'][:150]}")
        print(f"  TRANSLATED  : {r['recovered'][:150]}")
        ctx = context_for(html, r["latex"])
        if ctx:
            print(f"  PAPER TEXT  : {ctx}")
        shown += 1
    print()
