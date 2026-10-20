import re
import json

# Load the symbols.zip catalog
with open('DATASETS/unified_manifest.json') as f:
    manifest = json.load(f)

catalog = manifest.get('symbols_zip_catalog', {}).get('catalog', [])

# Build lookups: by name, by index, by abbrev
by_name = {}
by_alt = {}
by_index = {}
for entry in catalog:
    name = entry.get('name', '').lower()
    if name:
        by_name[name] = entry
    alt = entry.get('alt', '').lower()
    if alt:
        by_alt[alt] = entry
    idx = entry.get('index')
    if idx is not None:
        by_index[idx] = entry

# Symbol aliases: input character → catalog name
SYMBOL_ALIASES = {
    'l': 'subscrl',          # script small l (ℓ)
    'N': 'N',                # natural numbers
    'R': 'R',                # real numbers
    'C': 'C',                # complex numbers
    'Z': 'Z',                # integers
    'Q': 'Q',                # rationals
    'times': 'times',        # multiplication
    'leq': 'leq',            # less-than-or-equal
    'geq': 'geq',            # greater-than-or-equal
    'neq': 'neq',            # not-equal
    'in': 'in',              # element-of
    'notin': 'notin',        # not-an-element-of
    'sub': 'sub',            # subset
    'sup': 'sup',            # superset
    'sube': 'sube',          # subset-or-equal
    'supe': 'supe',          # superset-or-equal
    'cup': 'cup',            # union
    'cap': 'cap',            # intersection
    'sqrt': 'sqrt',          # square root
    'infinity': 'infinity',  # infinity
    'partial': 'partial',    # partial differential
    'nabla': 'nabla',        # nabla
    'int': 'int',            # integral
    'sum': 'sum',            # summation
    'prod': 'prod',          # product
    'alpha': 'alpha',        # Greek alpha
    'beta': 'beta',          # Greek beta
    'gamma': 'gamma',        # Greek gamma
    'delta': 'delta',        # Greek delta
    'epsilon': 'epsilon',    # Greek epsilon
    'theta': 'theta',        # Greek theta
    'lambda': 'lambda',      # Greek lambda
    'mu': 'mu',              # Greek mu
    'pi': 'pi',              # Greek pi
    'sigma': 'sigma',        # Greek sigma
    'omega': 'omega',        # Greek omega
}

# Common LaTeX-to-catalog name mappings
LATEX_TO_CATALOG = {
    'setminus': 'setmn',
    'smallsetminus': 'setmn',
    'mid': 'mid',
    'nmid': 'nmid',
    'parallel': 'par',
    'nparallel': 'npar',
    'propto': 'prop',
    'vdash': 'vdash',
    'dashv': 'dashv',
}

def extract_symbols(line_text):
    """
    Extract individual symbols from a line of text.
    Returns list of (symbol, symbol_type) tuples.
    """
    if not line_text:
        return []
    
    # Regex to split math expressions into tokens
    line_text = line_text.strip()
    if not line_text:
        return []
    
    # Match LaTeX commands: \sin, \log, \sum, \int, \alpha
    latex_pattern = r'\\[a-zA-Z]+'
    # Match unicode math symbols
    unicode_pattern = r'ℓ|ℕ|ℝ|ℂ|ℤ|ℚ|≤|≥|≠|∈|∉|⊂|⊃|⊆|⊇|∪|∩|√|∞|∂|∇|∫|∑|∏|α|β|γ|δ|ε|θ|λ|μ|π|σ|ω'
    # Match single characters/dividers
    single_pattern = r'[{}()\[\]]|\|\||&&|!=|[=+\-*/^><~!]'
    
    # Combined pattern
    pattern = '|'.join([latex_pattern, unicode_pattern, single_pattern])
    
    symbols = []
    for match in re.finditer(pattern, line_text):
        token = match.group(0)
        if token.startswith('\\'):
            # LaTeX command
            cmd = token[1:].lower()
            if cmd in LATEX_TO_CATALOG:
                symbols.append((LATEX_TO_CATALOG[cmd], 'latex'))
            elif cmd in by_name:
                symbols.append((cmd, 'latex'))
            else:
                symbols.append((cmd, 'unknown'))
        elif any(c in token for c in 'abcdefghijklmnopqrstuvwxyz'):
            # Identifier or greek letter
            if token.lower() in by_name:
                symbols.append((token.lower(), 'identifier'))
            else:
                symbols.append((token, 'identifier'))
        elif any(c in token for c in '0123456789'):
            # Number
            symbols.append((token, 'number'))
        elif token in SYMBOL_ALIASES:
            symbols.append((SYMBOL_ALIASES[token], 'unicode'))
        elif len(token) == 1:
            symbols.append((token, 'single'))
        else:
            symbols.append((token, 'other'))
    
    return symbols

# Test
if __name__ == '__main__':
    test_lines = [
        '(ℓ)×f',
        'e^{i\\pi} + 1 = 0',
        '∑_{k=1}^{n} k^2',
        '∀x ∈ ℝ, ∃y ∈ ℤ',
        'sin^2(x) + cos^2(x) = 1',
        'P(A|B) = P(B|A)P(A) / P(B)',
    ]
    
    for line in test_lines:
        symbols = extract_symbols(line)
        print(f"'{line}' → {symbols}")
