"""
Targeted HTML Parser for LaTeX Brackets and Braces
==================================================
Parses arxiv HTML to extract exact bracket/brace usage patterns.
Focuses on: (), [], {}, \langle\rangle, \lfloor\rfloor, \lceil\rceil,
extended brackets, sideways brackets, and nested structures.

Output: JSON with exact bracket patterns found in each paper.
"""
import json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup
import urllib.request

HTML_BASE = "https://arxiv.org/html/"
USER_AGENT = "arxiv-html-parser/1.0 (math extraction tool)"

def fetch_url(url, timeout=30):
    """Fetch URL content with proper headers."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None

def extract_math_from_html(html_content):
    """Extract all math elements from arxiv HTML."""
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    math_elements = []
    
    # Find all <math> tags (MathML)
    for math_tag in soup.find_all('math'):
        # Get the LaTeX annotation if available
        annotation = math_tag.find('annotation')
        if annotation:
            latex = annotation.text.strip()
            math_elements.append({
                'latex': latex,
                'mathml': str(math_tag)[:500],
            })
    
    # Find all <span class="ltx_Math"> elements
    for span in soup.find_all('span', class_='ltx_Math'):
        # Get the text content
        text = span.get_text(strip=True)
        if text:
            math_elements.append({
                'latex': text,
                'mathml': None,
            })
    
    # Find all elements with class containing 'math'
    for elem in soup.find_all(class_=re.compile(r'math|equation')):
        text = elem.get_text(strip=True)
        if text and len(text) > 1:
            math_elements.append({
                'latex': text,
                'mathml': None,
            })
    
    return math_elements

def analyze_brackets(latex):
    """
    Analyze bracket and brace usage in a LaTeX string.
    Returns detailed information about each bracket type.
    """
    analysis = {
        'latex': latex,
        'brackets': {
            'parentheses': {'count': 0, 'patterns': []},
            'square_brackets': {'count': 0, 'patterns': []},
            'curly_braces': {'count': 0, 'patterns': []},
            'angle_brackets': {'count': 0, 'patterns': []},
            'floor_brackets': {'count': 0, 'patterns': []},
            'ceiling_brackets': {'count': 0, 'patterns': []},
            'vertical_bars': {'count': 0, 'patterns': []},
            'double_vertical_bars': {'count': 0, 'patterns': []},
        },
        'left_right': {'count': 0, 'patterns': []},
        'big_variants': {'count': 0, 'patterns': []},
        'nested_depth': 0,
        'max_nested_depth': 0,
        'sideways_brackets': [],
        'extended_brackets': [],
    }
    
    # Count parentheses
    paren_count = latex.count('(') + latex.count(')')
    analysis['brackets']['parentheses']['count'] = paren_count
    
    # Count square brackets
    square_count = latex.count('[') + latex.count(']')
    analysis['brackets']['square_brackets']['count'] = square_count
    
    # Count curly braces
    curly_count = latex.count('{') + latex.count('}')
    analysis['brackets']['curly_braces']['count'] = curly_count
    
    # Count angle brackets
    angle_count = latex.count('\\langle') + latex.count('\\rangle')
    analysis['brackets']['angle_brackets']['count'] = angle_count
    
    # Count floor brackets
    floor_count = latex.count('\\lfloor') + latex.count('\\rfloor')
    analysis['brackets']['floor_brackets']['count'] = floor_count
    
    # Count ceiling brackets
    ceil_count = latex.count('\\lceil') + latex.count('\\rceil')
    analysis['brackets']['ceiling_brackets']['count'] = ceil_count
    
    # Count vertical bars
    bar_count = latex.count('|') + latex.count('\\lvert') + latex.count('\\rvert')
    analysis['brackets']['vertical_bars']['count'] = bar_count
    
    # Count double vertical bars
    double_bar_count = latex.count('\\|') + latex.count('\\lVert') + latex.count('\\rVert')
    analysis['brackets']['double_vertical_bars']['count'] = double_bar_count
    
    # Count \left and \right
    left_right_count = latex.count('\\left') + latex.count('\\right')
    analysis['left_right']['count'] = left_right_count
    
    # Count \big, \Big, \bigg, \Bigg
    big_count = latex.count('\\big') + latex.count('\\Big') + latex.count('\\bigg') + latex.count('\\Bigg')
    analysis['big_variants']['count'] = big_count
    
    # Calculate nested depth
    depth = 0
    max_depth = 0
    for char in latex:
        if char in '({[':
            depth += 1
            max_depth = max(max_depth, depth)
        elif char in ')}]':
            depth -= 1
    analysis['nested_depth'] = depth
    analysis['max_nested_depth'] = max_depth
    
    # Find sideways brackets (using \rotatebox or \text)
    sideways_patterns = re.findall(r'\\rotatebox\{[^}]*\}\{[^}]*\}', latex)
    analysis['sideways_brackets'] = sideways_patterns
    
    # Find extended brackets (using \overbrace, \underbrace, \overrightarrow, etc.)
    extended_patterns = re.findall(r'\\overbrace|\\underbrace|\\overrightarrow|\\overleftarrow|\\overleftrightarrow|\\widehat|\\widetilde|\\overline|\\underline', latex)
    analysis['extended_brackets'] = extended_patterns
    
    # Extract specific bracket patterns
    # Parentheses with content
    paren_patterns = re.findall(r'\([^()]*\)', latex)
    analysis['brackets']['parentheses']['patterns'] = paren_patterns[:10]
    
    # Square brackets with content
    square_patterns = re.findall(r'\[[^\[\]]*\]', latex)
    analysis['brackets']['square_brackets']['patterns'] = square_patterns[:10]
    
    # Curly braces with content
    curly_patterns = re.findall(r'\{[^{}]*\}', latex)
    analysis['brackets']['curly_braces']['patterns'] = curly_patterns[:10]
    
    # Angle brackets with content
    angle_patterns = re.findall(r'\\langle[^}]*\\rangle', latex)
    analysis['brackets']['angle_brackets']['patterns'] = angle_patterns[:10]
    
    # Floor brackets with content
    floor_patterns = re.findall(r'\\lfloor[^}]*\\rfloor', latex)
    analysis['brackets']['floor_brackets']['patterns'] = floor_patterns[:10]
    
    # Ceiling brackets with content
    ceil_patterns = re.findall(r'\\lceil[^}]*\\rceil', latex)
    analysis['brackets']['ceiling_brackets']['patterns'] = ceil_patterns[:10]
    
    # Vertical bars with content
    bar_patterns = re.findall(r'\|[^|]*\|', latex)
    analysis['brackets']['vertical_bars']['patterns'] = bar_patterns[:10]
    
    # Double vertical bars with content
    double_bar_patterns = re.findall(r'\\|[^|]*\\|', latex)
    analysis['brackets']['double_vertical_bars']['patterns'] = double_bar_patterns[:10]
    
    # \left...\right patterns
    left_right_patterns = re.findall(r'\\left[^}]*\\right', latex)
    analysis['left_right']['patterns'] = left_right_patterns[:10]
    
    # \big...\big patterns
    big_patterns = re.findall(r'\\big[^}]*\\big', latex)
    analysis['big_variants']['patterns'] = big_patterns[:10]
    
    return analysis

def process_paper(arxiv_id, output_dir=None):
    """Process a single arxiv paper and analyze bracket usage."""
    print(f"Processing {arxiv_id}...")
    
    # Fetch HTML
    url = f"{HTML_BASE}{arxiv_id}"
    html_content = fetch_url(url)
    if not html_content:
        print(f"  Failed to fetch HTML for {arxiv_id}")
        return None
    
    print(f"  Fetched {len(html_content)} bytes from {url}")
    
    # Extract math elements
    math_elements = extract_math_from_html(html_content)
    print(f"  Found {len(math_elements)} math elements")
    
    # Analyze brackets in each math element
    bracket_analyses = []
    for elem in math_elements:
        latex = elem.get('latex', '')
        if latex and len(latex) > 1:
            analysis = analyze_brackets(latex)
            bracket_analyses.append(analysis)
    
    # Aggregate statistics
    total_equations = len(bracket_analyses)
    equations_with_parens = sum(1 for a in bracket_analyses if a['brackets']['parentheses']['count'] > 0)
    equations_with_square = sum(1 for a in bracket_analyses if a['brackets']['square_brackets']['count'] > 0)
    equations_with_curly = sum(1 for a in bracket_analyses if a['brackets']['curly_braces']['count'] > 0)
    equations_with_angle = sum(1 for a in bracket_analyses if a['brackets']['angle_brackets']['count'] > 0)
    equations_with_floor = sum(1 for a in bracket_analyses if a['brackets']['floor_brackets']['count'] > 0)
    equations_with_ceiling = sum(1 for a in bracket_analyses if a['brackets']['ceiling_brackets']['count'] > 0)
    equations_with_bars = sum(1 for a in bracket_analyses if a['brackets']['vertical_bars']['count'] > 0)
    equations_with_double_bars = sum(1 for a in bracket_analyses if a['brackets']['double_vertical_bars']['count'] > 0)
    equations_with_left_right = sum(1 for a in bracket_analyses if a['left_right']['count'] > 0)
    equations_with_big = sum(1 for a in bracket_analyses if a['big_variants']['count'] > 0)
    equations_with_sideways = sum(1 for a in bracket_analyses if a['sideways_brackets'])
    equations_with_extended = sum(1 for a in bracket_analyses if a['extended_brackets'])
    
    max_nested_depth = max((a['max_nested_depth'] for a in bracket_analyses), default=0)
    
    result = {
        'arxiv_id': arxiv_id,
        'url': url,
        'total_math_elements': len(math_elements),
        'total_equations_analyzed': total_equations,
        'bracket_usage': {
            'parentheses': equations_with_parens,
            'square_brackets': equations_with_square,
            'curly_braces': equations_with_curly,
            'angle_brackets': equations_with_angle,
            'floor_brackets': equations_with_floor,
            'ceiling_brackets': equations_with_ceiling,
            'vertical_bars': equations_with_bars,
            'double_vertical_bars': equations_with_double_bars,
            'left_right': equations_with_left_right,
            'big_variants': equations_with_big,
            'sideways_brackets': equations_with_sideways,
            'extended_brackets': equations_with_extended,
        },
        'max_nested_depth': max_nested_depth,
        'sample_analyses': bracket_analyses[:5],
    }
    
    # Save to file if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{arxiv_id}_brackets.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {output_file}")
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Targeted HTML parser for LaTeX brackets and braces')
    parser.add_argument('arxiv_id', nargs='?', help='ArXiv ID (e.g., 1406.2661)')
    parser.add_argument('--output-dir', default='DATASETS/bracket_analysis', help='Output directory')
    parser.add_argument('--batch', nargs='+', help='Batch process multiple arxiv IDs')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch processing
        output_dir = args.output_dir or 'DATASETS/bracket_analysis'
        results = []
        for arxiv_id in args.batch:
            result = process_paper(arxiv_id, output_dir)
            if result:
                results.append(result)
        
        # Print summary
        print(f"\n{'='*60}")
        print("Batch Processing Summary")
        print(f"{'='*60}")
        print(f"Papers processed: {len(results)}")
        
        # Aggregate bracket usage
        total_equations = sum(r['total_equations_analyzed'] for r in results)
        total_parens = sum(r['bracket_usage']['parentheses'] for r in results)
        total_square = sum(r['bracket_usage']['square_brackets'] for r in results)
        total_curly = sum(r['bracket_usage']['curly_braces'] for r in results)
        total_angle = sum(r['bracket_usage']['angle_brackets'] for r in results)
        total_floor = sum(r['bracket_usage']['floor_brackets'] for r in results)
        total_ceiling = sum(r['bracket_usage']['ceiling_brackets'] for r in results)
        total_bars = sum(r['bracket_usage']['vertical_bars'] for r in results)
        total_double_bars = sum(r['bracket_usage']['double_vertical_bars'] for r in results)
        total_left_right = sum(r['bracket_usage']['left_right'] for r in results)
        total_big = sum(r['bracket_usage']['big_variants'] for r in results)
        total_sideways = sum(r['bracket_usage']['sideways_brackets'] for r in results)
        total_extended = sum(r['bracket_usage']['extended_brackets'] for r in results)
        
        print(f"\nTotal equations analyzed: {total_equations}")
        print(f"\nBracket usage:")
        print(f"  Parentheses: {total_parens}")
        print(f"  Square brackets: {total_square}")
        print(f"  Curly braces: {total_curly}")
        print(f"  Angle brackets: {total_angle}")
        print(f"  Floor brackets: {total_floor}")
        print(f"  Ceiling brackets: {total_ceiling}")
        print(f"  Vertical bars: {total_bars}")
        print(f"  Double vertical bars: {total_double_bars}")
        print(f"  \\left/\\right: {total_left_right}")
        print(f"  \\big variants: {total_big}")
        print(f"  Sideways brackets: {total_sideways}")
        print(f"  Extended brackets: {total_extended}")
        
        # Find max nested depth
        max_depth = max((r['max_nested_depth'] for r in results), default=0)
        print(f"\nMax nested depth: {max_depth}")
        
    elif args.arxiv_id:
        # Single paper processing
        result = process_paper(args.arxiv_id, args.output_dir)
        
        if result:
            print(f"\n{'='*60}")
            print(f"Bracket Analysis for {args.arxiv_id}")
            print(f"{'='*60}")
            print(f"Total math elements: {result['total_math_elements']}")
            print(f"Total equations analyzed: {result['total_equations_analyzed']}")
            print(f"\nBracket usage:")
            for bracket_type, count in result['bracket_usage'].items():
                print(f"  {bracket_type}: {count}")
            print(f"\nMax nested depth: {result['max_nested_depth']}")
            
            # Print sample analyses
            print(f"\nSample analyses:")
            for i, analysis in enumerate(result['sample_analyses'][:3]):
                print(f"\n  Equation {i+1}:")
                print(f"    LaTeX: {analysis['latex'][:80]}")
                print(f"    Parentheses: {analysis['brackets']['parentheses']['count']}")
                print(f"    Square brackets: {analysis['brackets']['square_brackets']['count']}")
                print(f"    Curly braces: {analysis['brackets']['curly_braces']['count']}")
                print(f"    Angle brackets: {analysis['brackets']['angle_brackets']['count']}")
                print(f"    Floor brackets: {analysis['brackets']['floor_brackets']['count']}")
                print(f"    Ceiling brackets: {analysis['brackets']['ceiling_brackets']['count']}")
                print(f"    Vertical bars: {analysis['brackets']['vertical_bars']['count']}")
                print(f"    Double vertical bars: {analysis['brackets']['double_vertical_bars']['count']}")
                print(f"    \\left/\\right: {analysis['left_right']['count']}")
                print(f"    \\big variants: {analysis['big_variants']['count']}")
                print(f"    Sideways brackets: {len(analysis['sideways_brackets'])}")
                print(f"    Extended brackets: {len(analysis['extended_brackets'])}")
                print(f"    Max nested depth: {analysis['max_nested_depth']}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()