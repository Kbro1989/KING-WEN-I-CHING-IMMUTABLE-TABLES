import urllib.request, re, json
from bs4 import BeautifulSoup

url = 'https://arxiv.org/html/2006.11239'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

print("=== ALL <meta> TAGS ===")
metas = soup.find_all('meta')
print(f"count: {len(metas)}")
for m in metas[:30]:
    attrs = {k: (v[:90] if isinstance(v, str) else v) for k, v in m.attrs.items()}
    print("  ", attrs)

print()
print("=== arXiv stamp in text (raw search) ===")
for pat in [r'arXiv:\s*[\d.]+v\d+\s*\[[^\]]+\]',
            r'\[[a-z]+\.[A-Z]{2}\]',
            r'arXiv:[\d.]+']:
    hits = re.findall(pat, html)
    print(f"  {pat!r:52s} -> {hits[:3]}")

print()
print("=== title tag ===")
print("  ", soup.title.get_text(strip=True)[:100] if soup.title else "none")
