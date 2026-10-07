"""
Build Extractor Training Data from ArXiv HTML Corpus
=====================================================
Converts fetched arxiv HTML JSON files into structured training data
for improving the math extractors.

Output: JSONL file with one record per equation, containing:
- latex: the LaTeX source
- context_before/after: surrounding text
- is_display: display vs inline
- arxiv_id: source paper
- category: vision/math/3d/chromanumber
- symbol_counts: frequency of each symbol in the equation
- has_fraction, has_integral, has_sum, etc.: structural flags

This training data can be used to:
1. Train symbol classifiers (which symbols appear in which contexts)
2. Validate OCR output (compare OCR results to known LaTeX)
3. Build equation assembly rules (how symbols combine)
4. Test the full pipeline (end-to-end verification)
"""
import json, os, re
from pathlib import Path
from collections import Counter

# Symbol categories for training
SYMBOL_CATEGORIES = {
    'greek': set('αβγδεζηθικλμνξπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'),
    'operators': set('+-*/=<>≤≥≠≈≡∝±∓×÷·'),
    'calculus': set('∫∏∑√∂∇∞ℏℵ'),
    'logic': set('∧∨¬∀∃∈∉⊆⊂∪∩'),
    'arrows': set('→←↔⟹⟸↦'),
    'brackets': set('()[]{}⟨⟩⌊⌋⌈⌉|‖'),
    'scripts': set('ℒℬℳ𝒞𝒢𝒥𝒦𝒩𝒪𝒫𝒬𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵'),
    'double_struck': set('ℂℍℕℙℚℛℝℤ'),
    'formal': set('𝔄𝔅𝔉𝔊𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔘𝔙𝔚𝔛𝔜𝔷'),
}

# Structural patterns
STRUCTURAL_PATTERNS = {
    'has_fraction': r'\\frac|\\dfrac|\\tfrac',
    'has_integral': r'\\int|\\oint',
    'has_sum': r'\\sum',
    'has_product': r'\\prod',
    'has_sqrt': r'\\sqrt',
    'has_partial': r'\\partial',
    'has_nabla': r'\\nabla',
    'has_limit': r'\\lim',
    'has_superscript': r'\^',
    'has_subscript': r'_',
    'has_big_bracket': r'\\left|\\right',
    'has_matrix': r'\\begin\{matrix|\\begin\{pmatrix|\\begin\{bmatrix',
    'has_cases': r'\\begin\{cases',
    'has_alignment': r'\\begin\{align|\\begin\{equation',
}

def count_symbols(latex):
    """Count symbol frequencies in a LaTeX string."""
    counts = {}
    for char in latex:
        if char.isalpha() or char in 'αβγδεζηθικλμνξπρστυφχψω':
            counts[char] = counts.get(char, 0) + 1
    return counts

def extract_structural_features(latex):
    """Extract structural features from a LaTeX string."""
    features = {}
    for name, pattern in STRUCTURAL_PATTERNS.items():
        features[name] = bool(re.search(pattern, latex))
    return features

def categorize_equation(latex):
    """Categorize an equation by its symbol content."""
    categories = set()
    for char in latex:
        for cat, symbols in SYMBOL_CATEGORIES.items():
            if char in symbols:
                categories.add(cat)
    return list(categories)

def build_training_record(equation, arxiv_id, category):
    """Build a training record from an equation."""
    latex = equation.get('latex', '')
    if not latex or len(latex) < 2:
        return None
    
    return {
        'latex': latex,
        'context_before': equation.get('context_before', ''),
        'context_after': equation.get('context_after', ''),
        'is_display': equation.get('is_display', False),
        'source': equation.get('source', 'unknown'),
        'arxiv_id': arxiv_id,
        'category': category,
        'symbol_counts': count_symbols(latex),
        'structural_features': extract_structural_features(latex),
        'equation_categories': categorize_equation(latex),
    }

def build_training_data(input_dir, output_file, category_map=None):
    """
    Build training data from a directory of arxiv HTML JSON files.
    
    Args:
        input_dir: Directory containing arxiv HTML JSON files
        output_file: Output JSONL file path
        category_map: Dict mapping arxiv_id -> category (vision/math/3d/chromanumber)
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Input directory not found: {input_dir}")
        return
    
    # Default category map
    if category_map is None:
        category_map = {}
    
    records = []
    stats = {
        'total_files': 0,
        'total_equations': 0,
        'valid_records': 0,
        'by_category': Counter(),
        'by_arxiv_id': Counter(),
    }
    
    for json_file in input_path.glob('*.json'):
        stats['total_files'] += 1
        arxiv_id = json_file.stem
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  Error reading {json_file}: {e}")
            continue
        
        equations = data.get('equations', [])
        category = category_map.get(arxiv_id, 'unknown')
        
        stats['total_equations'] += len(equations)
        stats['by_arxiv_id'][arxiv_id] += len(equations)
        
        for eq in equations:
            record = build_training_record(eq, arxiv_id, category)
            if record:
                records.append(record)
                stats['valid_records'] += 1
                stats['by_category'][category] += 1
    
    # Write JSONL
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    # Print summary
    print(f"\n{'='*60}")
    print("Training Data Build Summary")
    print(f"{'='*60}")
    print(f"Files processed: {stats['total_files']}")
    print(f"Total equations: {stats['total_equations']}")
    print(f"Valid records: {stats['valid_records']}")
    print(f"Output: {output_file}")
    print(f"\nBy category:")
    for cat, count in stats['by_category'].most_common():
        print(f"  {cat}: {count}")
    print(f"\nBy arxiv_id:")
    for aid, count in stats['by_arxiv_id'].most_common():
        print(f"  {aid}: {count}")
    
    return records

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Build extractor training data from arxiv HTML corpus')
    parser.add_argument('--input-dir', default='DATASETS/arxiv_html_corpus', help='Input directory')
    parser.add_argument('--output', default='DATASETS/extractor_training_data.jsonl', help='Output JSONL file')
    parser.add_argument('--category-map', help='JSON file mapping arxiv_id to category')
    
    args = parser.parse_args()
    
    # Load category map if provided
    category_map = {}
    if args.category_map and os.path.exists(args.category_map):
        with open(args.category_map) as f:
            category_map = json.load(f)
    
    build_training_data(args.input_dir, args.output, category_map)

if __name__ == '__main__':
    main()