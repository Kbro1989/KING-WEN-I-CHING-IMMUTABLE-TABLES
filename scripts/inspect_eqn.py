import urllib.request
from bs4 import BeautifulSoup

url = 'https://arxiv.org/html/2006.11239'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

# Find all elements whose class contains 'eqn_cell'
hits = []
for el in soup.find_all(True):
    cls = el.get('class') or []
    if any('eqn_cell' in c for c in cls):
        hits.append(el)

print('eqn_cell elements:', len(hits))
if hits:
    el = hits[0]
    print('TAG:', el.name)
    print('CLASS:', el.get('class'))
    print()
    print('FULL ELEMENT:')
    print(str(el)[:2000])
    print()
    print('ANCESTORS:')
    for p in el.parents:
        if p.name:
            print(' ', p.name, p.get('class'))
