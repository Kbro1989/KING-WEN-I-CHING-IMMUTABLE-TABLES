import sys, urllib.request
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup

url = 'https://arxiv.org/html/2605.28896'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
soup = BeautifulSoup(html, 'html.parser')

# find every math node whose raw HTML contains the transpose char
for m in soup.find_all('math'):
    s = str(m)
    if '\u22a4' in s and 'Q' in s:
        i = s.find('\u22a4')
        print('RAW around transpose:')
        print(s[max(0, i - 340):i + 70])
        print()
        print('msup present?', '<msup>' in s)
        break
