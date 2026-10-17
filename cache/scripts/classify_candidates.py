import json
import re
from pathlib import Path
import fitz

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
pdfs = list(pdf_dir.rglob('*.pdf'))

MATH_SYMBOLS = r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]'
# Pattern for inline math (has fraction or arrow)
INLINE_PATTERN = r'[=/−→]'

def classify_candidate(line_text, is_fraction, is_equation):
    """Classify a candidate into: true_equation, inline_math, isolated_symbol, false_positive, uncertain."""
    if not line_text.strip():
        return 'false_positive'
    
    # Isolated symbol: only one symbol, no letters or numbers
    symbols_only = re.findall(MATH_SYMBOLS, line_text)
    letters = re.findall(r'[a-zA-Z]', line_text)
    digits = re.findall(r'\d', line_text)
    
    if is_equation or is_fraction:
        return 'true_equation'
    
    # Has math symbols but no equation-level
    if len(symbols_only) >= 1 and not letters and not digits:
        return 'isolated_symbol'
    
    # Has math symbols plus letters/digits
    if symbols_only and (letters or digits):
        return 'inline_math'
    
    # Prose with occasional math symbol (e.g. "and & x")
    if re.search(r'\s[=&+,]\s', line_text) or re.search(r'&[a-z]', line_text):
        return 'false_positive'
    
    return 'uncertain'

for pid in missing:
    p = None
    for f in pdfs:
        if f.name.startswith(pid):
            p = f
            break
    if p is None:
        continue
    doc = fitz.open(str(p))
    pages = doc
    candidates = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        words = page.get_text("words")
        lines = {}
        for w in words:
            x0, y0, x1, y1, text, block, line, word_no = w
            key = (round(y0, 1), round(x0, 1))
            if key not in lines:
                lines[key] = []
            lines[key].append(w)
        for y_key, line_words in lines.items():
            line_words.sort(key=lambda w: w[0])
            line_text = ' '.join(w[4] for w in line_words)
            if re.search(MATH_SYMBOLS, line_text):
                is_fraction = bool(re.search(r'[=/−→]', line_text))
                is_equation = bool(re.search(r'[=∑∫√]', line_text))
                classification = classify_candidate(line_text, is_fraction, is_equation)
                
                candidates.append({
                    'paper_id': pid,
                    'page': page_num + 1,
                    'line_text': line_text[:250],
                    'bbox': {'x0': min(w[0] for w in line_words), 'y0': min(w[1] for w in line_words),
                             'x1': max(w[2] for w in line_words), 'y1': max(w[3] for w in line_words)},
                    'classification': classification,
                    'char_count': len(line_text),
                })
    doc.close()
    
    # Save per-paper classification
    out = Path(f'DATASETS/candidates_{pid}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    from collections import Counter
    counts = Counter(c['classification'] for c in candidates)
    print(f'{pid}: {len(candidates)} candidates')
    for cls, cnt in counts.most_common():
        print(f'  {cls}: {cnt}')

# Also load the original PDF_FALLBACK file to get the 3,559 baseline
with open('DATASETS/PDF_FALLBACK_8_PAPERS_2026-10-16.json', encoding='utf-8') as f:
    fallback = json.load(f)

# Print original baseline
print()
print('Original baseline (from PDF_FALLBACK_8_PAPERS_2026-10-16.json):')
total = 0
for entry in fallback:
    print(f'  {entry["paper_id"]}: {entry["formula_candidates"]}')
    total += entry['formula_candidates']
print(f'  Total: {total}')
