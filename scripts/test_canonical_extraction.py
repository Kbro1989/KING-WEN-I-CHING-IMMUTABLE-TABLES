import re
import json

# Load the unified manifest
with open('DATASETS/unified_manifest.json') as f:
    m = json.load(f)

# Extract x-tex annotations from WDR-RLHF HTML
html_path = 'DATASETS/Wasserstein Distributionally Robust Regret Optimization for Reinforcement Learning from Human Feedback.html'
with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find all <annotation encoding="application/x-tex">...</annotation>
tex_pattern = r'<annotation encoding="application/x-tex">(.*?)</annotation>'
texs = re.findall(tex_pattern, content, re.DOTALL)
print(f"Total x-tex annotations: {len(texs)}")

# Build the canonical source records
canonical_records = []
for i, tex in enumerate(texs):
    tex = tex.strip()
    if tex and len(tex) > 0:
        canonical_records.append({
            'paper': '2605.00155',  # WDR-RLHF paper
            'page': None,
            'equation_index': i,
            'source_text': tex,
            'source': 'x-tex annotation (HTML)',
            'bbox': None,
            'classification': 'canonical',
            'match_symbols_zip': 0,
            'matched_glyphs': 0,
            'alignment': 'canonical_known'
        })

print(f"Canonical records ready: {len(canonical_records)}")

# Load symbols.zip catalog
glyph_catalog = m['symbols_zip_catalog']['catalog']
print(f"Symbols.zip catalog loaded: {len(glyph_catalog)} glyphs")

# Match each canonical equation against the glyph catalog
# First, extract the main symbol name from LaTeX
def extract_symbol_name(tex):
    tex = tex.strip()
    tex = re.sub(r'\^\{\}', '', tex)
    tex = re.sub(r'\_\{\}', '', tex)
    tex = re.sub(r'\\frac\{\{(.*?)\}\}', r'\1', tex)
    tex = re.sub(r'\\frac\{(.*?)\}', r'\1', tex)
    tex = re.sub(r'\\\\[a-zA-Z]+', '', tex)  # Remove command names
    tex = re.sub(r'\{.*?\}', '', tex)
    tex = tex.replace('\\', ' ')
    tex = re.sub(r'\s+', ' ', tex)
    tex = tex.strip()
    return tex

print(f"\nCross-referencing {len(canonical_records)} canonical equations against {len(glyph_catalog)} glyphs")
for rec in canonical_records:
    tex = rec['source_text']
    symbol_name = extract_symbol_name(tex)
    rec['symbol_name'] = symbol_name
    
    matched = []
    for glyph in glyph_catalog:
        if symbol_name in glyph['name'] or glyph['name'] in symbol_name:
            matched.append(glyph['name'])
    rec['match_symbols_zip'] = len(matched)
    rec['matched_glyphs'] = matched[:5]
    
    print(f"  [{rec['equation_index']:4d}] {tex[:60]:60s} -> {symbol_name[:30]:30s} -> {len(matched)} matches")

# Save canonical output
import os
os.makedirs('DATASETS/vision_comparison', exist_ok=True)
with open('DATASETS/vision_comparison/canonical_from_html.json', 'w') as f:
    json.dump(canonical_records, f, indent=2)
print(f"\nSaved canonical_from_html.json ({len(canonical_records)} records)")

PYEOF