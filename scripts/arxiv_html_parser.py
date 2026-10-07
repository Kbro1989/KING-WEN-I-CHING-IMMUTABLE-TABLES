"""
ArXiv HTML Math Parser
======================
Fetches HTML versions of arxiv papers and extracts math equations
with structure intact. Uses BeautifulSoup to parse MathML and
LaTeX annotations from arxiv HTML.

This bypasses the OCR bottleneck — arxiv HTML contains structured
math markup that can be extracted directly.

Usage:
  python arxiv_html_parser.py <arxiv_id> [--output FILE]
  python arxiv_html_parser.py --batch <id1> <id2> ... --output-dir DIR
"""
import json, os, re, sys, time, argparse
import urllib.request
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

# Arxiv API and HTML endpoints
ABS_BASE = "https://arxiv.org/abs/"
PDF_BASE = "https://arxiv.org/pdf/"
HTML_BASE = "https://arxiv.org/html/"
API_BASE = "https://export.arxiv.org/api/query"
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

def fetch_arxiv_html(arxiv_id, version=None):
    """Fetch HTML version of an arxiv paper."""
    # Try with version first, then without
    if version:
        url = f"{HTML_BASE}{arxiv_id}v{version}"
        content = fetch_url(url)
        if content:
            return content, url
    
    # Try without version
    url = f"{HTML_BASE}{arxiv_id}"
    content = fetch_url(url)
    if content:
        return content, url
    
    return None, None

def extract_math_from_html(html_content, arxiv_id=None):
    """
    Extract math equations from arxiv HTML.
    
    Arxiv HTML contains:
    - MathML markup in <math> tags
    - LaTeX annotations in <annotation> tags
    - Display equations in <div class="ltx_equation"> or similar
    - Inline math in <span class="ltx_Math"> or similar
    
    Returns a list of equations with their context and structure.
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    equations = []
    
    # Method 1: Extract from MathML <math> tags
    math_tags = soup.find_all('math')
    for i, math_tag in enumerate(math_tags):
        # Get the LaTeX annotation if available
        annotation = math_tag.find('annotation')
        latex = annotation.text.strip() if annotation else None
        
        # Get the MathML content
        mathml = str(math_tag)
        
        # Get context (surrounding text)
        context_before = ""
        context_after = ""
        
        # Find the parent element and get surrounding text
        parent = math_tag.parent
        if parent:
            # Get all text before and after this math tag
            prev_sibling = math_tag.find_previous_sibling()
            next_sibling = math_tag.find_next_sibling()
            
            if prev_sibling:
                context_before = prev_sibling.get_text(strip=True)[:200]
            if next_sibling:
                context_after = next_sibling.get_text(strip=True)[:200]
        
        # Determine if display or inline
        is_display = False
        if parent:
            parent_classes = parent.get('class', [])
            if any('display' in str(c).lower() or 'equation' in str(c).lower() for c in parent_classes):
                is_display = True
        
        equations.append({
            'index': i,
            'latex': latex,
            'mathml': mathml[:500] if mathml else None,  # Truncate for storage
            'context_before': context_before,
            'context_after': context_after,
            'is_display': is_display,
            'source': 'mathml',
        })
    
    # Method 2: Extract from LaTeX annotations in <span class="ltx_Math">
    ltx_math_spans = soup.find_all('span', class_='ltx_Math')
    for i, span in enumerate(ltx_math_spans):
        # Check if we already captured this via MathML
        if span.find('math'):
            continue
        
        # Get the text content (may contain LaTeX)
        text = span.get_text(strip=True)
        if text and len(text) > 1:
            # Get context
            context_before = ""
            context_after = ""
            prev_sibling = span.find_previous_sibling()
            next_sibling = span.find_next_sibling()
            if prev_sibling:
                context_before = prev_sibling.get_text(strip=True)[:200]
            if next_sibling:
                context_after = next_sibling.get_text(strip=True)[:200]
            
            equations.append({
                'index': len(equations),
                'latex': text,
                'mathml': None,
                'context_before': context_before,
                'context_after': context_after,
                'is_display': False,
                'source': 'ltx_math_span',
            })
    
    # Method 3: Extract from <div class="ltx_equation"> (display equations)
    equation_divs = soup.find_all('div', class_=re.compile(r'ltx_equation|ltx_math'))
    for i, div in enumerate(equation_divs):
        # Check if we already captured this
        if div.find('math'):
            continue
        
        text = div.get_text(strip=True)
        if text and len(text) > 1:
            equations.append({
                'index': len(equations),
                'latex': text,
                'mathml': None,
                'context_before': "",
                'context_after': "",
                'is_display': True,
                'source': 'ltx_equation_div',
            })
    
    # Method 4: Extract from <annotation> tags (LaTeX source)
    annotations = soup.find_all('annotation')
    for i, ann in enumerate(annotations):
        latex = ann.text.strip()
        if latex and len(latex) > 1:
            # Check if we already captured this
            already_captured = any(e.get('latex') == latex for e in equations)
            if not already_captured:
                equations.append({
                    'index': len(equations),
                    'latex': latex,
                    'mathml': None,
                    'context_before': "",
                    'context_after': "",
                    'is_display': False,
                    'source': 'annotation',
                })
    
    return equations

def extract_document_structure(html_content):
    """Extract document structure (sections, headings) from arxiv HTML."""
    if not html_content:
        return {}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title = ""
    title_tag = soup.find('h1', class_='ltx_title')
    if title_tag:
        title = title_tag.get_text(strip=True)
    
    # Extract authors
    authors = []
    author_tags = soup.find_all('span', class_='ltx_personname')
    for tag in author_tags:
        authors.append(tag.get_text(strip=True))
    
    # Extract abstract
    abstract = ""
    abstract_tag = soup.find('div', class_='ltx_abstract')
    if abstract_tag:
        abstract = abstract_tag.get_text(strip=True)
    
    # Extract sections
    sections = []
    section_tags = soup.find_all(['h2', 'h3', 'h4'])
    for tag in section_tags:
        sections.append({
            'level': tag.name,
            'title': tag.get_text(strip=True),
        })
    
    return {
        'title': title,
        'authors': authors,
        'abstract': abstract,
        'sections': sections,
    }

def process_arxiv_paper(arxiv_id, version=None, output_dir=None):
    """Process a single arxiv paper: fetch HTML, extract math, save results."""
    print(f"Processing {arxiv_id}v{version}..." if version else f"Processing {arxiv_id}...")
    
    # Fetch HTML
    html_content, url = fetch_arxiv_html(arxiv_id, version)
    if not html_content:
        print(f"  Failed to fetch HTML for {arxiv_id}")
        return None
    
    print(f"  Fetched {len(html_content)} bytes from {url}")
    
    # Extract math equations
    equations = extract_math_from_html(html_content, arxiv_id)
    print(f"  Found {len(equations)} equations")
    
    # Extract document structure
    structure = extract_document_structure(html_content)
    print(f"  Title: {structure.get('title', 'N/A')[:60]}")
    print(f"  Authors: {len(structure.get('authors', []))}")
    print(f"  Sections: {len(structure.get('sections', []))}")
    
    result = {
        'arxiv_id': arxiv_id,
        'version': version,
        'url': url,
        'structure': structure,
        'equations': equations,
        'equation_count': len(equations),
    }
    
    # Save to file if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{arxiv_id}v{version}.json" if version else output_path / f"{arxiv_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {output_file}")
    
    return result

def main():
    parser = argparse.ArgumentParser(description='ArXiv HTML math parser')
    parser.add_argument('arxiv_id', nargs='?', help='ArXiv ID (e.g., 1406.2661)')
    parser.add_argument('--version', type=int, help='Version number')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--output-dir', help='Output directory for batch processing')
    parser.add_argument('--batch', nargs='+', help='Batch process multiple arxiv IDs')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch processing
        output_dir = args.output_dir or 'DATASETS/arxiv_html_parsed'
        results = []
        for arxiv_id in args.batch:
            result = process_arxiv_paper(arxiv_id, args.version, output_dir)
            if result:
                results.append(result)
            time.sleep(3)  # Be polite to arxiv
        
        print(f"\n{'='*60}")
        print(f"Batch processing complete: {len(results)} papers")
        print(f"Results saved to {output_dir}")
        
        # Print summary
        total_equations = sum(r['equation_count'] for r in results)
        print(f"Total equations extracted: {total_equations}")
        
    elif args.arxiv_id:
        # Single paper processing
        result = process_arxiv_paper(args.arxiv_id, args.version, args.output_dir)
        
        if result and args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nSaved to {args.output}")
        
        # Print sample equations
        if result and result['equations']:
            print(f"\n{'='*60}")
            print("Sample equations:")
            for eq in result['equations'][:5]:
                latex = eq.get('latex', 'N/A')
                source = eq.get('source', 'unknown')
                print(f"  [{source}] {latex[:80]}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()