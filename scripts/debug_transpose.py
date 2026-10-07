import sys, urllib.request
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup

url = 'https://arxiv.org/html/2605.28896'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

for m in soup.find_all('math'):
    alt = (m.get('alttext') or '')
    if 'top' in alt and 'Q_' in alt:
        print('ALT:', alt[:100])
        print()
        # find the msup containing the transpose
        for ms in m.find_all('msup'):
            print('  msup:', str(ms)[:300])
        print()
        break
