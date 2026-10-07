import urllib.request
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, '.')

from mathml_parser import MathMLParser

url = 'https://arxiv.org/html/2006.11239'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

# Find a math node that produces 'E*['
for m in soup.find_all('math'):
    p = MathMLParser()
    e, u = p.parse(m)
    if e and 'E*[' in e:
        print('PROBLEM EXPR:', e[:120])
        print()
        print('MATHML STRUCTURE (first 1200 chars):')
        print(str(m)[:1200])
        print()
        # Walk top-level children to see the sequence
        print('TOP-LEVEL CHILDREN:')
        sem = m.find('semantics')
        if sem:
            mrow = sem.find('mrow')
            if mrow:
                for i, c in enumerate(mrow.children):
                    if getattr(c, 'name', None):
                        txt = c.get_text()[:30]
                        print(f'  [{i}] <{c.name}> {txt!r}')
        break
