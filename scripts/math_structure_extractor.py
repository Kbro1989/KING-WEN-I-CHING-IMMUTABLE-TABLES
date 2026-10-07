"""
Math Structure Extractor with Relationship Preservation
=======================================================
Extracts math expressions from PDFs with complete structural relationships.
Preserves bracket nesting, fraction structure, sub/superscripts, and spatial
relationships between math elements.

Output: Structured math trees with director signals for relationships.
No solving, no derivation — pure extraction with context intact.
"""
import json, os, re, tempfile, subprocess
import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

def kmeans_quantize(image_array, max_colors=16):
    """K-Means color quantization."""
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
    """Find regions that likely contain math."""
    height, width = image_array.shape[:2]
    pixel_count = width * height
    
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
        
        aspect_ratio = w / h
        fill_ratio = len(region_pixels) / (w * h)
        stroke_width = np.sqrt(len(region_pixels) / (np.pi * max(w, h)))
        normalized_stroke = stroke_width / max(w, h)
        
        # Classify region type
        region_type = classify_region_type(aspect_ratio, fill_ratio, normalized_stroke, w, h)
        
        regions.append({
            'bbox': (int(x_min), int(y_min), int(w), int(h)),
            'pixel_count': int(len(region_pixels)),
            'aspect_ratio': float(aspect_ratio),
            'fill_ratio': float(fill_ratio),
            'normalized_stroke': float(normalized_stroke),
            'region_type': region_type,
            'centroid': (int(np.mean(xs)), int(np.mean(ys))),
        })
    
    return regions

def classify_region_type(aspect_ratio, fill_ratio, normalized_stroke, w, h):
    """Classify a region by its shape characteristics."""
    # Fraction bar or horizontal line
    if aspect_ratio > 3.0 and fill_ratio < 0.1:
        return 'fraction_bar'
    
    # Square root vinculum (horizontal line with hook)
    if aspect_ratio > 2.0 and fill_ratio < 0.15:
        return 'sqrt_vinculum'
    
    # Large bracket (tall, narrow)
    if aspect_ratio < 0.4 and h > 50:
        return 'large_bracket'
    
    # Vertical bar or bracket
    if aspect_ratio < 0.3:
        return 'vertical_bar'
    
    # Subscript or superscript (small)
    if w < 20 and h < 20:
        return 'script'
    
    # Regular symbol
    return 'symbol'

def extract_spatial_relationships(regions):
    """
    Extract spatial relationships between math regions.
    Returns a list of relationships with director signals.
    """
    relationships = []
    
    # Sort regions by vertical position (top to bottom)
    sorted_regions = sorted(regions, key=lambda r: r['centroid'][1])
    
    for i, region in enumerate(sorted_regions):
        rx, ry, rw, rh = region['bbox']
        rcx, rcy = region['centroid']
        
        # Find regions above
        above = []
        for j, other in enumerate(sorted_regions):
            if i == j:
                continue
            ox, oy, ow, oh = other['bbox']
            ocx, ocy = other['centroid']
            
            # Other is above this region
            if ocy < ry and abs(ocx - rcx) < max(rw, ow):
                above.append({
                    'region_index': j,
                    'region_type': other['region_type'],
                    'vertical_distance': float(ry - ocy),
                    'horizontal_overlap': float(min(rx + rw, ox + ow) - max(rx, ox)),
                })
        
        # Find regions below
        below = []
        for j, other in enumerate(sorted_regions):
            if i == j:
                continue
            ox, oy, ow, oh = other['bbox']
            ocx, ocy = other['centroid']
            
            # Other is below this region
            if ocy > ry + rh and abs(ocx - rcx) < max(rw, ow):
                below.append({
                    'region_index': j,
                    'region_type': other['region_type'],
                    'vertical_distance': float(ocy - (ry + rh)),
                    'horizontal_overlap': float(min(rx + rw, ox + ow) - max(rx, ox)),
                })
        
        # Find regions inside (for brackets)
        inside = []
        if region['region_type'] in ['large_bracket', 'vertical_bar']:
            for j, other in enumerate(sorted_regions):
                if i == j:
                    continue
                ox, oy, ow, oh = other['bbox']
                
                # Other is inside this bracket
                if ox >= rx and ox + ow <= rx + rw and oy >= ry and oy + oh <= ry + rh:
                    inside.append({
                        'region_index': j,
                        'region_type': other['region_type'],
                    })
        
        # Find fraction relationships
        fraction_parts = []
        if region['region_type'] == 'fraction_bar':
            # Fraction bar contains numerator (top) and denominator (bottom)
            # The bar itself is the horizontal line in the middle
            numerator_regions = []
            denominator_regions = []
            
            for j, other in enumerate(sorted_regions):
                if i == j:
                    continue
                ox, oy, ow, oh = other['bbox']
                ocx, ocy = other['centroid']
                
                # Check if region is inside the fraction bar's horizontal span
                if ocx >= rx and ocx <= rx + rw:
                    # Numerator: in the top half of the fraction bar
                    if ocy >= ry and ocy < ry + rh * 0.5:
                        numerator_regions.append({
                            'region_index': j,
                            'region_type': other['region_type'],
                            'centroid': other['centroid'],
                            'bbox': other['bbox'],
                        })
                    
                    # Denominator: in the bottom half of the fraction bar
                    if ocy >= ry + rh * 0.5 and ocy <= ry + rh:
                        denominator_regions.append({
                            'region_index': j,
                            'region_type': other['region_type'],
                            'centroid': other['centroid'],
                            'bbox': other['bbox'],
                        })
            
            # Sort numerator by x position (left to right)
            numerator_regions.sort(key=lambda x: x['centroid'][0])
            denominator_regions.sort(key=lambda x: x['centroid'][0])
            
            if numerator_regions or denominator_regions:
                fraction_parts.append({
                    'numerator': numerator_regions,
                    'denominator': denominator_regions,
                })
        
        # Only add relationships if there are any
        if above or below or inside or fraction_parts:
            relationships.append({
                'region_index': i,
                'region_type': region['region_type'],
                'bbox': region['bbox'],
                'above': above[:3],
                'below': below[:3],
                'inside': inside[:5],
                'fraction_parts': fraction_parts,
            })
    
    return relationships

def extract_math_with_structure(pdf_path, page_num, dpi=200):
    """
    Extract math from a PDF page with complete structural relationships.
    """
    doc = pymupdf.open(pdf_path)
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
    
    # Extract spatial relationships
    relationships = extract_spatial_relationships(math_regions)
    
    # Extract text with positions
    blocks = page.get_text("blocks")
    words = page.get_text("words")
    
    # Extract text with layout preservation
    text = page.get_text("text")
    
    # Associate text with math regions
    text_with_math = []
    for region in math_regions:
        if region['region_type'] == 'symbol':
            rx, ry, rw, rh = region['bbox']
            rcx, rcy = region['centroid']
            
            # Find text that overlaps with this region
            overlapping_text = []
            for block in blocks:
                bx, by, bw, bh = block[:4]
                
                # Check for overlap
                if not (bx + bw < rx or bx > rx + rw or by + bh < ry or by > ry + rh):
                    overlapping_text.append({
                        'text': block[4],
                        'bbox': (bx, by, bw, bh),
                    })
            
            if overlapping_text:
                text_with_math.append({
                    'region': region,
                    'overlapping_text': overlapping_text,
                })
    
    doc.close()
    
    return {
        'page': page_num + 1,
        'math_regions': math_regions,
        'relationships': relationships,
        'text_with_math': text_with_math,
        'page_text': text,
    }

def process_pdf(pdf_path, max_pages=5, dpi=200):
    """Process a PDF file and extract math with structural relationships."""
    results = []
    
    try:
        doc = pymupdf.open(pdf_path)
        
        for page_num in range(min(max_pages, len(doc))):
            result = extract_math_with_structure(pdf_path, page_num, dpi)
            results.append(result)
        
        doc.close()
        
    except Exception as e:
        import traceback
        print(f"Error processing {pdf_path}: {repr(e)}")
        traceback.print_exc()
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Math structure extractor with relationship preservation')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--max-pages', type=int, default=5)
    parser.add_argument('--dpi', type=int, default=200)
    parser.add_argument('--output', default='DATASETS/math_structure.json')
    
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
        print(f"    Math regions: {len(r['math_regions'])}")
        print(f"    Relationships: {len(r['relationships'])}")
        print(f"    Text with math: {len(r['text_with_math'])}")
        
        # Show fraction relationships
        for rel in r['relationships']:
            if rel['fraction_parts']:
                print(f"    Fraction found:")
                for fp in rel['fraction_parts']:
                    print(f"      Numerator: {fp['numerator']}")
                    print(f"      Denominator: {fp['denominator']}")

if __name__ == '__main__':
    main()