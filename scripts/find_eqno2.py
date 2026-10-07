import sys, urllib.request
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup

aid = "2006.11239"
url = f"https://arxiv.org/html/{aid}"
req = urllib.request.Request(url, headers={"User-Agent": "x/1.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
soup = BeautifulSoup(html, "html.parser")

# Where does ltx_tag_equation actually sit?
for sp in soup.find_all("span", class_=lambda c: c and any("ltx_tag_equation" in x for x in c)):
    print("SPAN:", sp.get_text(strip=True))
    print("  ancestors:")
    for p in sp.parents:
        if p.name:
            print("   ", p.name, p.get("class"))
        if p.name == "table":
            break
    break
