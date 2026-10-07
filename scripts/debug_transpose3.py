import sys, urllib.request
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
from mathml_parser import MathMLParser

url = 'https://arxiv.org/html/2605.28896'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

for m in soup.find_all('math'):
    alt = (m.get('alttext') or '')
    if 'Q_A' in alt or 'Q_{\\Delta}' in alt or 'Q_{\\text{GS}}' in alt:
        print('ALT:', alt[:80])
        # dump the raw structure around the transpose
        s = str(m)
        i = s.find('⊤')
        if i > 0:
            print('RAW around transpose:')
            print(s[max(0, i - 260):i + 90])
        print()
        break
