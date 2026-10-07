"""
Inspect arxiv HTML for DECISION-RATIONALE structure.

Theory papers state: if we want X -> math -> because -> therefore Y is needed.
That structure has HTML markers. Find them before building for them.
"""
import sys, urllib.request, re
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup

aid = sys.argv[1] if len(sys.argv) > 1 else "2006.11239"
url = f"https://arxiv.org/html/{aid}"
req = urllib.request.Request(url, headers={"User-Agent": "inspect/1.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
soup = BeautifulSoup(html, "html.parser")

print("=" * 74)
print(f"STRUCTURE MARKERS in {aid}")
print("=" * 74)

# 1. Section headings (the argument's skeleton)
print("\n1. SECTION HEADINGS (argument skeleton):")
for h in soup.find_all(["h2", "h3"])[:18]:
    t = h.get_text(" ", strip=True)[:72]
    if t:
        print(f"   <{h.name}> {t}")

# 2. Theorem-like environments
print("\n2. THEOREM / PROOF ENVIRONMENTS:")
envs = {}
for el in soup.find_all(class_=True):
    for c in (el.get("class") or []):
        for key in ("theorem", "lemma", "proof", "definition", "corollary",
                    "proposition", "remark", "assumption"):
            if key in c.lower():
                envs[key] = envs.get(key, 0) + 1
print("  ", envs if envs else "none found")

# 3. Reasoning connectives in prose (the 'because / therefore' layer)
print("\n3. REASONING CONNECTIVES in prose:")
text = soup.get_text(" ", strip=True)
connectives = {
    "because": 0, "since": 0, "therefore": 0, "thus": 0, "hence": 0,
    "we want": 0, "we need": 0, "to achieve": 0, "allows us": 0,
    "in order to": 0, "this ensures": 0, "it follows": 0, "implies": 0,
    "where": 0, "such that": 0, "given that": 0, "motivates": 0,
}
low = text.lower()
for k in connectives:
    connectives[k] = low.count(k)
for k, v in sorted(connectives.items(), key=lambda x: -x[1]):
    if v:
        print(f"   {k:14s} {v}")

# 4. Equation cross-references (the relation graph edges)
print("\n4. EQUATION CROSS-REFERENCES (relation edges):")
refs = re.findall(r"\(\d+\)", text)
print(f"   inline '(N)' style refs: {len(refs)}")
eqrefs = re.findall(r"\bEq(?:uation|s)?\.?\s*\(?\d+", text)
print(f"   'Eq. N' style refs:      {len(eqrefs)}")
# eqno cells we already extract
eqno = soup.find_all("td", class_=lambda c: c and any("ltx_eqn_eqno" in x for x in c))
print(f"   numbered equations:      {len(eqno)}")
labels = [e.get_text(" ", strip=True) for e in eqno][:10]
print(f"   sample labels: {labels}")
