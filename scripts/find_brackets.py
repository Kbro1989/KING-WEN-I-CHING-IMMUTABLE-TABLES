import urllib.request
from bs4 import BeautifulSoup
import re
import sys

def find_brackets(arxiv_id):
    url = f'https://arxiv.org/html/{arxiv_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'arxiv-parser/1.0'})
    with urllib.request.urlopen(req) as r:
        html = r.read()

    soup = BeautifulSoup(html, 'html.parser')
    all_text = soup.get_text()

    # In the HTML text, LaTeX commands appear as \command (single backslash)
    # In Python regex, we need to match literal backslash + command
    # So pattern should be \\command (two backslashes in regex = one literal backslash)
    patterns = [
        (r'\\langle[^}]*\\rangle', 'angle_brackets'),
        (r'\\lfloor[^}]*\\rfloor', 'floor_brackets'),
        (r'\\lceil[^}]*\\rceil', 'ceiling_brackets'),
        (r'\\left[^}]*\\right', 'left_right'),
        (r'\\big[^}]*\\big', 'big_variants'),
        (r'\\overbrace', 'overbrace'),
        (r'\\underbrace', 'underbrace'),
        (r'\\overrightarrow', 'overrightarrow'),
        (r'\\overleftarrow', 'overleftarrow'),
        (r'\\widehat', 'widehat'),
        (r'\\widetilde', 'widetilde'),
        (r'\\overline', 'overline'),
        (r'\\underline', 'underline'),
        (r'\\coloneqq', 'coloneqq'),
        (r'\\stackrel', 'stackrel'),
        (r'\\mathbin', 'mathbin'),
        (r'\\mathrel', 'mathrel'),
        (r'\\mathop', 'mathop'),
    ]

    print(f"Searching for special bracket patterns in {arxiv_id}...")
    print("=" * 60)

    found_any = False
    for pattern, name in patterns:
        matches = re.findall(pattern, all_text)
        if matches:
            print(f"{name}: {len(matches)} matches")
            for m in matches[:3]:
                print(f"  {m[:100]}")
            print()
            found_any = True

    if not found_any:
        print("No special bracket patterns found.")

    # Also search for all LaTeX commands that might be brackets
    print("\n" + "=" * 60)
    print("All LaTeX commands containing bracket keywords:")

    cmd_pattern = r'\\[a-zA-Z]+'
    all_commands = set(re.findall(cmd_pattern, all_text))
    print(f"\nTotal unique LaTeX commands: {len(all_commands)}")

    bracket_keywords = ['brace', 'bracket', 'ceil', 'floor', 'angle', 'vert', 'left', 'right', 'big', 'over', 'under', 'arrow', 'hat', 'bar', 'vec', 'dot', 'tilde', 'widehat', 'widetilde', 'overline', 'underline']

    for keyword in bracket_keywords:
        matching = [cmd for cmd in all_commands if keyword in cmd.lower()]
        if matching:
            print(f"\n  {keyword}: {matching[:20]}")

if __name__ == '__main__':
    arxiv_ids = ['1406.2661', '2006.11239', '2102.09672', '2605.28615', '2605.25334']
    if len(sys.argv) > 1:
        arxiv_ids = sys.argv[1:]

    for arxiv_id in arxiv_ids:
        find_brackets(arxiv_id)
        print("\n" + "=" * 80 + "\n")