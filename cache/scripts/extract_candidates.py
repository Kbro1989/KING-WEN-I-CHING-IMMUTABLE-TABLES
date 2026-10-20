import json
import re
from pathlib import Path
import fitz

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
pdfs = list(pdf_dir.rglob('*.pdf'))

MATH_SYMBOLS = r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]'

def extract_candidates(pdf_path):
    doc = fitz.open(str(pdf_path))
    candidates = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        words = page.get_text("words")
        # Group words by line number (y0 rounded), then sort each line by x0.
        # BUG FIX: original code grouped by (y0, x0) which created a unique
        # group per word, causing each word to be extracted as its own
        # candidate instead of complete lines. Now we group by y0 FIRST,
        # then sort by x0 within each group to get complete lines.
        line_groups = {}
        for w in words:
            x0, y0, x1, y1, text, block, line_no, word_no = w
            # Group by y0 (rounded to 0.1) to identify line groups
            key = round(y0, 1)
            if key not in line_groups:
                line_groups[key] = []
            line_groups[key].append(w)
        
        # Process each line group: sort words left-to-right, combine text
        for y_key, line_words in line_groups.items():
            line_words.sort(key=lambda w: w[0])  # sort left to right
            line_text = ' '.join(w[4] for w in line_words)
            if re.search(MATH_SYMBOLS, line_text):
                x0_min = min(w[0] for w in line_words)
                y0_min = min(w[1] for w in line_words)
                x1_max = max(w[2] for w in line_words)
                y1_max = max(w[3] for w in line_words)
                candidates.append({
                    'paper_id': pdf_path.stem,
                    'page': page_num + 1,
                    'line_text': line_text[:200],
                    'bbox': {'x0': x0_min, 'y0': y0_min, 'x1': x1_max, 'y1': y1_max},
                    'char_count': len(line_text),
                })
    doc.close()
    return candidates

all_candidates = []
for pid in missing:
    p = None
    for f in pdfs:
        if f.name.startswith(pid):
            p = f
            break
    if p is None:
        print(f'{pid}: NOT FOUND')
        continue
    candidates = extract_candidates(p)
    print(f'{pid}: {len(candidates)} candidates')
    all_candidates.extend(candidates)

with open('DATASETS/PDF_CANDIDATE_MANIFEST_2026-10-16.json', 'w', encoding='utf-8') as f:
    json.dump(all_candidates, f, indent=2, ensure_ascii=False)

print(f'Total candidates: {len(all_candidates)}')
