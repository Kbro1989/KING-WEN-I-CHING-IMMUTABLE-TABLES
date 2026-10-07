import sys, urllib.request
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup

aid = sys.argv[1] if len(sys.argv) > 1 else "2006.11239"
url = f"https://arxiv.org/html/{aid}"
req = urllib.request.Request(url, headers={"User-Agent": "inspect/1.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
soup = BeautifulSoup(html, "html.parser")

# find every element whose class mentions eqno / equation number
print("=== classes containing 'eqno' ===")
seen = {}
for el in soup.find_all(True):
    for c in (el.get("class") or []):
        if "eqno" in c.lower() or "equation" in c.lower():
            seen.setdefault(c, 0)
            seen[c] += 1
for k, v in sorted(seen.items(), key=lambda x: -x[1])[:20]:
    print(f"  {v:5d}  {k}")

print()
print("=== sample eqno element raw ===")
for el in soup.find_all(class_=lambda c: c and any("eqno" in x for x in c)):
    print(str(el)[:200])
    break
else:
    # fallback: find the (N) text near equations
    print("no eqno class; scanning for '(N)' spans near math")
    for sp in soup.find_all("span"):
        t = sp.get_text(strip=True)
        if t and len(t) < 8 and t.startswith("(") and t.endswith(")") and t[1:-1].isdigit():
            print(f"  span: {t!r} class={sp.get('class')}")
            break
