import sys, urllib.request
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
from mathml_parser import MathMLParser

url = 'https://arxiv.org/html/2605.28896'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

hits = 0
for m in soup.find_all('math'):
    alt = (m.get('alttext') or '')
    if 'top' not in alt:
        continue
    p = MathMLParser()
    e, u = p.parse(m)
    if e and '**' in e and ('Q' in e or 'Y' in e):
        print('ALT :', alt[:95])
        print('TREE:', e[:95])
        print()
        hits += 1
        if hits >= 3:
            break
