import sys
sys.path.insert(0, '.')
import urllib.request
from bs4 import BeautifulSoup
from mathml_parser import MathMLParser

url = 'https://arxiv.org/html/2006.11239'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

def show_children(el, depth=0, maxd=4):
    if depth > maxd:
        return
    for c in el.children:
        if not getattr(c, 'name', None):
            continue
        txt = c.get_text()[:25].replace('\n', ' ')
        print('  ' * depth + f'<{c.name}> {txt!r}')
        if c.name in ('mrow', 'munder', 'mover', 'munderover', 'msub', 'msup', 'msubsup', 'semantics'):
            show_children(c, depth + 1, maxd)

for m in soup.find_all('math'):
    p = MathMLParser()
    e, u = p.parse(m)
    if e and e.startswith('alpha_t=Prod'):
        print('EXPR:', e)
        print()
        print('TREE:')
        show_children(m)
        break

print()
print('=== sigma_t^2 case ===')
for m in soup.find_all('math'):
    p = MathMLParser()
    e, u = p.parse(m)
    if e and 'sigma_t*(2)' in e:
        print('EXPR:', e[:100])
        print()
        print('TREE:')
        show_children(m)
        break
