"""
Multi-Engine Math Parser Comparison
====================================
Runs all available parsing techniques in parallel on the same PDF pages.
Produces a comparison report showing what each engine captures,
what it misses, and where they agree/disagree.

Engines:
  A. PyMuPDF text blocks (layout-preserving)
  B. PyMuPDF raw text (no layout)
  C. Vision regions + Tesseract OCR (per-region)
  D. Text-based regex extraction (semantic patterns)
  E. pdftotext -layout (external tool)

Output: Side-by-side comparison with agreement analysis.
"""
import json, os, re, tempfile, subprocess, sys
import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

# ============================================================================
# Engine A: PyMuPDF Text Blocks (layout-preserving)
# ============================================================================

def engine_a_text_blocks(pdf_path, page_num):
    """Extract text blocks with positions."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    blocks = page.get_text("blocks")
    doc.close()
    
    expressions = []
    for block in blocks:
        text = block[4].strip()
        if text and len(text) > 2:
            # Check if block contains math-like content
            if any(c in text for c in '=<>≤≥≠+-*/^_{}[]()') or \
               any(c in text for c in 'αβγδεζηθικλμνξπρστυφχψω∫∑∏√∂∇∈∉⊆⊂∪∩∧∨¬∀∃→←↔'):
                expressions.append({
                    'text': text,
                    'bbox': (block[0], block[1], block[2], block[3]),
                    'type': 'text_block',
                })
    
    return expressions

# ============================================================================
# Engine B: PyMuPDF Raw Text (no layout)
# ============================================================================

def engine_b_raw_text(pdf_path, page_num):
    """Extract raw text without layout."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    text = page.get_text("text")
    doc.close()
    
    expressions = []
    # Split by lines and look for math patterns
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        # Check for math patterns
        has_math = False
        if any(c in line for c in '=<>≤≥≠+-*/^_{}[]()'):
            has_math = True
        if any(c in line for c in 'αβγδεζηθικλμνξπρστυφχψω∫∑∏√∂∇∈∉⊆⊂∪∩∧∨¬∀∃→←↔'):
            has_math = True
        
        if has_math:
            # Get context (previous and next lines)
            context_before = lines[i-1].strip() if i > 0 else ''
            context_after = lines[i+1].strip() if i < len(lines)-1 else ''
            
            expressions.append({
                'text': line,
                'line_number': i,
                'context_before': context_before,
                'context_after': context_after,
                'type': 'raw_text',
            })
    
    return expressions

# ============================================================================
# Engine C: Vision Regions + Tesseract OCR
# ============================================================================

def engine_c_vision_ocr(pdf_path, page_num, dpi=200):
    """Extract math regions and OCR them."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    
    # Render page
    mat = pymupdf.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_array = np.array(img)
    
    # K-Means quantization
    height, width = img_array.shape[:2]
    pixel_count = width * height
    data = img_array.reshape(-1, 3).astype(np.float64)
    centroids, labels = kmeans2(data, 16, minit='points', iter=10)
    unique_labels = np.unique(labels)
    palette = []
    label_map = {}
    for new_idx, old_label in enumerate(unique_labels):
        mask = labels == old_label
        count = np.sum(mask)
        if count == 0:
            continue
        r, g, b = centroids[old_label].astype(int)
        palette.append({'id': new_idx, 'rgb': (r, g, b), 'hex': f'#{r:02x}{g:02x}{b:02x}', 'textColor': '#000', 'count': int(count)})
        label_map[old_label] = new_idx
    remapped = np.zeros(pixel_count, dtype=np.int32)
    for old_label, new_label in label_map.items():
        remapped[labels == old_label] = new_label
    
    # Find dark regions
    luminance = np.zeros(pixel_count, dtype=np.float64)
    for i, color_dict in enumerate(palette):
        mask = remapped == i
        r, g, b = color_dict['rgb']
        lum = (r * 299 + g * 587 + b * 114) / 1000
        luminance[mask] = lum
    
    text_mask = (luminance < 128).reshape(height, width)
    labeled_array, num_features = ndimage.label(text_mask)
    
    expressions = []
    for region_id in range(1, min(num_features + 1, 500)):
        region_pixels_2d = np.where(labeled_array == region_id)
        if len(region_pixels_2d[0]) == 0:
            continue
        ys = region_pixels_2d[0]
        xs = region_pixels_2d[1]
        region_pixels = ys * width + xs
        
        if len(region_pixels) < 50 or len(region_pixels) > 5000:
            continue
        
        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()
        w, h = x_max - x_min, y_max - y_min
        
        if w < 5 or h < 5:
            continue
        
        # OCR this region
        region = img_array[y_min:y_max, x_min:x_max]
        region_img = Image.fromarray(region)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            region_img.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = subprocess.run(
                [r"C:\Program Files\Tesseract-OCR\tesseract.exe", tmp_path, 'stdout', '--psm', '10'],
                capture_output=True, text=True, timeout=5, encoding='utf-8', errors='replace'
            )
            ocr_text = result.stdout.strip() if result.returncode == 0 else None
        except:
            ocr_text = None
        
        os.unlink(tmp_path)
        
        if ocr_text:
            expressions.append({
                'text': ocr_text,
                'bbox': (int(x_min), int(y_min), int(w), int(h)),
                'pixel_count': int(len(region_pixels)),
                'aspect_ratio': float(w / h),
                'type': 'vision_ocr',
            })
    
    doc.close()
    return expressions

# ============================================================================
# Engine D: Text-based Regex Extraction
# ============================================================================

def engine_d_regex_extraction(pdf_path, page_num):
    """Extract math using regex patterns on text."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    text = page.get_text("text")
    doc.close()
    
    expressions = []
    
    # Pattern 1: LaTeX inline $...$
    for match in re.finditer(r'\$([^$]+)\$', text):
        expressions.append({
            'text': match.group(1),
            'position': match.start(),
            'type': 'latex_inline',
        })
    
    # Pattern 2: LaTeX display $$...$$
    for match in re.finditer(r'\$\$([^$]+)\$\$', text):
        expressions.append({
            'text': match.group(1),
            'position': match.start(),
            'type': 'latex_display',
        })
    
    # Pattern 3: Unicode math sequences (comprehensive Wolfram symbol set)
    unicode_pattern = r'[α-ωΑ-Ωϵ∫∑∏√∂∇∈∉⊆⊂∪∩∧∨¬∀∃→←↔⟹⟸↦⌊⌋⌈⌉⟨⟩ℂℍℕℙℚℛℝℤℒℬℳ𝒞𝒢𝒥𝒦𝒩𝒪𝒫𝒬𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵𝔄𝔅𝔉𝔊𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔘𝔙𝔚𝔛𝔜𝔷ΓΔΘΛΞΠΣΥΦΨΩ×÷±∓∝≈≡∼≅⊕⊗⨯∮∞ℏℵ°∴∵∶∷²·ℯⅈⅉ]+'
    for match in re.finditer(unicode_pattern, text):
        expressions.append({
            'text': match.group(0),
            'position': match.start(),
            'type': 'unicode_math',
        })
    
    # Pattern 4: Equations with = sign
    eq_pattern = r'[a-zA-Zα-ωΑ-Ω0-9\s\+\-\*/\(\)\[\]\{\}^_]+=[a-zA-Zα-ωΑ-Ω0-9\s\+\-\*/\(\)\[\]\{\}^_]+'
    for match in re.finditer(eq_pattern, text):
        expr = match.group(0).strip()
        if len(expr) > 3 and not expr.startswith(' '):
            expressions.append({
                'text': expr,
                'position': match.start(),
                'type': 'equation',
            })
    
    # Remove duplicates
    seen = set()
    unique = []
    for expr in expressions:
        key = (expr['type'], expr['text'])
        if key not in seen:
            seen.add(key)
            unique.append(expr)
    
    return unique

# ============================================================================
# Engine E: pdftotext -layout (external tool)
# ============================================================================

def engine_e_pdftotext(pdf_path, page_num):
    """Extract text using pdftotext -layout."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', '-f', str(page_num + 1), '-l', str(page_num + 1), pdf_path, '-'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            text = result.stdout
            lines = text.split('\n')
            expressions = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                has_math = False
                if any(c in line for c in '=<>≤≥≠+-*/^_{}[]()'):
                    has_math = True
                if any(c in line for c in 'αβγδεζηθικλμνξπρστυφχψω∫∑∏√∂∇∈∉⊆⊂∪∩∧∨¬∀∃→←↔'):
                    has_math = True
                if has_math:
                    context_before = lines[i-1].strip() if i > 0 else ''
                    context_after = lines[i+1].strip() if i < len(lines)-1 else ''
                    expressions.append({
                        'text': line,
                        'line_number': i,
                        'context_before': context_before,
                        'context_after': context_after,
                        'type': 'pdftotext_layout',
                    })
            return expressions
    except Exception:
        pass
    return []

# ============================================================================
# Comparison Analysis
# ============================================================================

def compare_engines(results):
    """Compare results from all engines."""
    comparison = {
        'engines': {},
        'agreement': {},
        'unique': {},
    }
    
    # Flatten results: {page_num: {engine_name: [expressions]}}
    # Count per engine across all pages
    engine_counts = {}
    all_texts = {}
    
    for page_num, page_results in results.items():
        for engine_name, expressions in page_results.items():
            if engine_name not in engine_counts:
                engine_counts[engine_name] = {'count': 0, 'types': {}}
            
            for expr in expressions:
                engine_counts[engine_name]['count'] += 1
                t = expr.get('type', 'unknown')
                engine_counts[engine_name]['types'][t] = \
                    engine_counts[engine_name]['types'].get(t, 0) + 1
                
                text = expr.get('text', '').strip()
                if text not in all_texts:
                    all_texts[text] = []
                all_texts[text].append(engine_name)
    
    comparison['engines'] = engine_counts
    
    # Find agreements (same text found by multiple engines)
    agreements = {text: engines for text, engines in all_texts.items() if len(engines) > 1}
    comparison['agreement'] = {
        'count': len(agreements),
        'examples': list(agreements.items())[:10],
    }
    
    # Find unique contributions (only found by one engine)
    unique = {text: engines[0] for text, engines in all_texts.items() if len(engines) == 1}
    comparison['unique'] = {
        'count': len(unique),
        'examples': list(unique.items())[:10],
    }
    
    return comparison

# ============================================================================
# Main Pipeline
# ============================================================================

def process_pdf(pdf_path, max_pages=5, dpi=200):
    """Process a PDF with all engines and compare."""
    all_results = {}
    
    try:
        doc = pymupdf.open(pdf_path)
        num_pages = min(max_pages, len(doc))
        doc.close()
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return None
    
    for page_num in range(num_pages):
        print(f"  Processing page {page_num + 1}/{num_pages}...")
        
        page_results = {
            'A_text_blocks': engine_a_text_blocks(pdf_path, page_num),
            'B_raw_text': engine_b_raw_text(pdf_path, page_num),
            'C_vision_ocr': engine_c_vision_ocr(pdf_path, page_num, dpi),
            'D_regex': engine_d_regex_extraction(pdf_path, page_num),
            'E_pdftotext': engine_e_pdftotext(pdf_path, page_num),
        }
        
        all_results[page_num + 1] = page_results
    
    return all_results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-engine math parser comparison')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--max-pages', type=int, default=5)
    parser.add_argument('--dpi', type=int, default=200)
    parser.add_argument('--output', default='DATASETS/engine_comparison.json')
    
    args = parser.parse_args()
    
    print(f"Processing: {args.pdf_path}")
    print(f"Max pages: {args.max_pages}")
    print(f"DPI: {args.dpi}")
    print()
    
    results = process_pdf(args.pdf_path, args.max_pages, args.dpi)
    
    if not results:
        print("Error processing PDF")
        return
    
    # Compare engines
    print("\nComparing engines...")
    comparison = compare_engines(results)
    
    output = {
        'pdf_path': args.pdf_path,
        'total_pages': len(results),
        'engine_results': results,
        'comparison': comparison,
    }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults written to {args.output}")
    
    # Print summary
    print("\n" + "="*60)
    print("ENGINE COMPARISON SUMMARY")
    print("="*60)
    
    for engine_name, stats in comparison['engines'].items():
        print(f"\n{engine_name}:")
        print(f"  Total expressions: {stats['count']}")
        print(f"  Types: {stats['types']}")
    
    print(f"\nAgreement: {comparison['agreement']['count']} expressions found by multiple engines")
    print(f"Unique: {comparison['unique']['count']} expressions found by only one engine")
    
    print("\nAgreement examples:")
    for text, engines in comparison['agreement']['examples'][:5]:
        print(f"  '{text[:50]}' -> {engines}")
    
    print("\nUnique examples:")
    for text, engine in comparison['unique']['examples'][:5]:
        print(f"  '{text[:50]}' -> {engine}")

if __name__ == '__main__':
    main()