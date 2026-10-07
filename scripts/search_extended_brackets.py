import urllib.request
from bs4 import BeautifulSoup

# Fetch 2605.00155 which had lots of extended brackets
url = 'https://arxiv.org/html/2605.00155'
req = urllib.request.Request(url, headers={'User-Agent': 'arxiv-parser/1.0'})
with urllib.request.urlopen(req) as r:
    html = r.read()

soup = BeautifulSoup(html, 'html.parser')

# Patterns to search for
patterns = [
    '\\overbrace',
    '\\underbrace',
    '\\overrightarrow',
    '\\overleftarrow',
    '\\widehat',
    '\\widetilde',
    '\\overline',
    '\\underline',
    '\\langle',
    '\\rangle',
    '\\lfloor',
    '\\rfloor',
    '\\lceil',
    '\\rceil',
    '\\overbrace',
    '\\underbrace',
    '\\overrightarrow',
    '\\overleftarrow',
]

print("Searching for extended bracket patterns in 2605.00155...")
print("=" * 60)

# Find all <math> tags
math_tags = soup.find_all('math')
print(f"Total <math> tags: {len(math_tags)}")

found = 0
for math in math_tags:
    annotation = math.find('annotation')
    if annotation:
        latex = annotation.text.strip()
        # Check for extended bracket patterns
        for p in patterns:
            if p in latex:
                print(f"FOUND: {p}")
                print(f"  LATEX: {latex}")
                print()
                found += 1
                break

print(f"\nTotal equations with extended brackets: {found}")