"""
Math Expression Extractor with Context Preservation
====================================================
Extracts math expressions from PDF pages with their surrounding context intact.
Uses ChromaNumber-style region detection to find math, then extracts
the full text with layout preservation to maintain context.

Output: Structured extractions with math expressions, their context,
spatial relationships, and page metadata. No solving, no derivation.
"""
import json, os, re, tempfile, subprocess
import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

def kmeans_quantize(image_array, max_colors=16):
    """K-Means color quantization using scipy.cluster.vq.kmeans2."""
    height, width = image_array.shape[:2]
    pixel_count = width * height
    data = image_array.reshape(-1, 3).astype(np.float64)
    centroids, labels = kmeans2(data, max_colors, minit='points', iter=10)
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
    return centroids, remapped, palette

def find_math_regions(image_array, assignments, palette, min_size=50, max_size=5000):
    """
    Find regions that likely contain math using connected components.
    Returns list of bounding boxes with shape metadata.
    """
    height, width = image_array.shape[:2]
    pixel_count = width * height
    
    # Create binary mask: dark pixels (likely text/math)
    luminance = np.zeros(pixel_count, dtype=np.float64)
    for i, color_dict in enumerate(palette):
        mask = assignments == i
        r, g, b = color_dict['rgb']
        lum = (r * 299 + g * 587 + b * 114) / 1000
        luminance[mask] = lum
    
    text_mask = (luminance < 128).reshape(height, width)
    labeled_array, num_features = ndimage.label(text_mask)
    
    regions = []
    for region_id in range(1, min(num_features + 1, 500)):
        region_pixels_2d = np.where(labeled_array == region_id)
        if len(region_pixels_2d[0]) == 0:
            continue
        ys = region_pixels_2d[0]
        xs = region_pixels_2d[1]
        region_pixels = ys * width + xs
        
        if len(region_pixels) < min_size or len(region_pixels) > max_size:
            continue
        
        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()
        w, h = x_max - x_min, y_max - y_min
        
        if w < 5 or h < 5:
            continue
        
        # Classify by shape
        aspect_ratio = w / h
        fill_ratio = len(region_pixels) / (w * h)
        stroke_width = np.sqrt(len(region_pixels) / (np.pi * max(w, h)))
        normalized_stroke = stroke_width / max(w, h)
        
        # Determine if this looks like math (not just text)
        is_math = False
        math_indicators = []
        
        # Check for math-like shapes
        if aspect_ratio < 0.3 or aspect_ratio > 3.0:
            is_math = True
            math_indicators.append('extreme_aspect')
        if fill_ratio < 0.05:
            is_math = True
            math_indicators.append('sparse_fill')
        if normalized_stroke < 0.05:
            is_math = True
            math_indicators.append('thin_stroke')
        
        # Check for math symbols in OCR (if available)
        # This is a placeholder - actual OCR would go here
        
        regions.append({
            'bbox': (int(x_min), int(y_min), int(w), int(h)),
            'pixel_count': int(len(region_pixels)),
            'aspect_ratio': float(aspect_ratio),
            'fill_ratio': float(fill_ratio),
            'normalized_stroke': float(normalized_stroke),
            'is_math': is_math,
            'math_indicators': math_indicators,
            'centroid': (int(np.mean(xs)), int(np.mean(ys))),
        })
    
    return regions

def extract_text_with_context(pdf_path, page_num, math_regions, dpi=200):
    """
    Extract text from a PDF page with context preservation.
    Associates math regions with their surrounding text.
    """
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    
    # Extract text blocks with positions
    blocks = page.get_text("blocks")
    
    # Extract text with layout preservation
    text = page.get_text("text")
    
    # Extract words with positions
    words = page.get_text("words")
    
    # Associate math regions with nearby text
    math_with_context = []
    for region in math_regions:
        if not region['is_math']:
            continue
        
        rx, ry, rw, rh = region['bbox']
        rcx, rcy = region['centroid']
        
        # Find text blocks that overlap or are near this region
        nearby_blocks = []
        for block in blocks:
            bx, by, bw, bh = block[:4]
            bcx, bcy = bx + bw/2, by + bh/2
            
            # Check if block is near the math region
            distance = np.sqrt((bcx - rcx)**2 + (bcy - rcy)**2)
            if distance < 200:  # Within 200 pixels
                nearby_blocks.append({
                    'text': block[4],
                    'bbox': (bx, by, bw, bh),
                    'distance': float(distance),
                })
        
        # Sort by distance
        nearby_blocks.sort(key=lambda x: x['distance'])
        
        # Get surrounding text (before and after)
        context_before = []
        context_after = []
        
        for block in blocks:
            bx, by, bw, bh = block[:4]
            bcy = by + bh/2
            
            # Block is above the math region
            if bcy < ry and abs(bcy - ry) < 100:
                context_before.append(block[4])
            
            # Block is below the math region
            if bcy > ry + rh and abs(bcy - (ry + rh)) < 100:
                context_after.append(block[4])
        
        math_with_context.append({
            'math_region': region,
            'nearby_blocks': nearby_blocks[:5],  # Top 5 nearest
            'context_before': context_before[:3],  # Top 3 before
            'context_after': context_after[:3],   # Top 3 after
        })
    
    doc.close()
    
    return {
        'page_text': text,
        'math_with_context': math_with_context,
    }

def extract_math_expressions_from_text(text):
    """
    Extract math expressions from text using pattern matching.
    Returns a list of expressions with their positions in the text.
    """
    expressions = []
    
    # Pattern 1: LaTeX inline math $...$
    for match in re.finditer(r'\$([^$]+)\$', text):
        expressions.append({
            'type': 'latex_inline',
            'expression': match.group(1),
            'position': match.start(),
            'context_before': text[max(0, match.start()-50):match.start()],
            'context_after': text[match.end():min(len(text), match.end()+50)],
        })
    
    # Pattern 2: LaTeX display math $$...$$
    for match in re.finditer(r'\$\$([^$]+)\$\$', text):
        expressions.append({
            'type': 'latex_display',
            'expression': match.group(1),
            'position': match.start(),
            'context_before': text[max(0, match.start()-50):match.start()],
            'context_after': text[match.end():min(len(text), match.end()+50)],
        })
    
    # Pattern 3: Unicode math symbols
    unicode_math_pattern = r'[α-ωΑ-Ω∫∑∏√∂∇∈∉⊆⊂∪∩∧∨¬∀∃→←↔⟹⟸↦⌊⌋⌈⌉⟨⟩]+'
    for match in re.finditer(unicode_math_pattern, text):
        expressions.append({
            'type': 'unicode_math',
            'expression': match.group(0),
            'position': match.start(),
            'context_before': text[max(0, match.start()-50):match.start()],
            'context_after': text[match.end():min(len(text), match.end()+50)],
        })
    
    # Pattern 4: Equations with = sign
    equation_pattern = r'[a-zA-Zα-ωΑ-Ω0-9\s\+\-\*/\(\)\[\]\{\}^_]+=[a-zA-Zα-ωΑ-Ω0-9\s\+\-\*/\(\)\[\]\{\}^_]+'
    for match in re.finditer(equation_pattern, text):
        expr = match.group(0).strip()
        if len(expr) > 3 and not expr.startswith(' '):
            expressions.append({
                'type': 'equation',
                'expression': expr,
                'position': match.start(),
                'context_before': text[max(0, match.start()-50):match.start()],
                'context_after': text[match.end():min(len(text), match.end()+50)],
            })
    
    # Remove duplicates
    seen = set()
    unique_expressions = []
    for expr in expressions:
        key = (expr['type'], expr['expression'])
        if key not in seen:
            seen.add(key)
            unique_expressions.append(expr)
    
    return unique_expressions

def process_pdf(pdf_path, max_pages=5, dpi=200):
    """
    Process a PDF file and extract math expressions with context.
    """
    results = []
    
    try:
        doc = pymupdf.open(pdf_path)
        
        for page_num in range(min(max_pages, len(doc))):
            page = doc[page_num]
            
            # Render page to image
            mat = pymupdf.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_array = np.array(img)
            
            # Apply K-Means quantization
            centroids, assignments, palette = kmeans_quantize(img_array, max_colors=16)
            
            # Find math regions
            math_regions = find_math_regions(img_array, assignments, palette)
            
            # Extract text with context
            text_data = extract_text_with_context(pdf_path, page_num, math_regions, dpi)
            
            # Extract math expressions from text
            math_expressions = extract_math_expressions_from_text(text_data['page_text'])
            
            results.append({
                'page': page_num + 1,
                'math_regions_detected': len([r for r in math_regions if r['is_math']]),
                'math_regions': math_regions,
                'math_expressions': math_expressions,
                'text_with_context': text_data,
            })
        
        doc.close()
        
    except Exception as e:
        import traceback
        print(f"Error processing {pdf_path}: {repr(e)}")
        traceback.print_exc()
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Math expression extractor with context preservation')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--max-pages', type=int, default=5)
    parser.add_argument('--dpi', type=int, default=200)
    parser.add_argument('--output', default='DATASETS/math_with_context.json')
    
    args = parser.parse_args()
    
    print(f"Processing: {args.pdf_path}")
    print(f"Max pages: {args.max_pages}")
    print(f"DPI: {args.dpi}")
    
    results = process_pdf(args.pdf_path, args.max_pages, args.dpi)
    
    output = {
        'pdf_path': args.pdf_path,
        'total_pages_processed': len(results),
        'results': results,
    }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nProcessed {len(results)} pages")
    print(f"Results written to {args.output}")
    
    for r in results:
        print(f"\n  Page {r['page']}:")
        print(f"    Math regions detected: {r['math_regions_detected']}")
        print(f"    Math expressions found: {len(r['math_expressions'])}")
        for expr in r['math_expressions'][:3]:
            print(f"      [{expr['type']}] {expr['expression'][:60]}")

if __name__ == '__main__':
    main()