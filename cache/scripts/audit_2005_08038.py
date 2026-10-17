import re
from pathlib import Path
import fitz

pdf_path = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus\graph-neural-networks\2305.08038_Graph State Space Models.pdf')
doc = fitz.open(str(pdf_path))
print(f'Total pages: {len(doc)}')
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    # Check all math-like characters
    special_chars = r'[=+\-×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω∞±]'
    matches = re.findall(f'[{re.escape("=+−×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω")}]', text)
    if matches:
        print(f'Page {page_num + 1}: {len(matches)} symbols')
        for line in text.split('\n'):
            if re.search(r'[=+\-×÷≤≥≠≈∞∂∇∇]', line):
                print(f'  {line[:150]}')

doc.close()
