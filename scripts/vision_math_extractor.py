"""
Vision-based math expression extractor.
Uses PyMuPDF for PDF rendering, Tesseract OCR for text extraction.
Optionally uses ChromaNumber-style K-Means to identify math regions.

This is the "extra layer of vision parser" that complements
the text-based semantic_math_extractor.py.
"""
import json, os, sys, subprocess, tempfile, re
import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def get_contrast_color(r, g, b):
    yiq = (r * 299 + g * 587 + b * 114) / 1000
    return '#000000' if yiq >= 128 else '#ffffff'

def color_dist_sq(c1, c2):
    return (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2

def kmeans_quantize(image_array, max_colors=16):
    """
    K-Means color quantization using scipy.cluster.vq.kmeans2 (fast).
    Returns (centroids, assignments, palette)
    """
    height, width = image_array.shape[:2]
    pixel_count = width * height
    data = image_array.reshape(-1, 3).astype(np.float64)
    
    # Use scipy's fast kmeans2
    centroids, labels = kmeans2(data, max_colors, minit='points', iter=10)
    
    # Filter out unused centroids
    unique_labels = np.unique(labels)
    palette = []
    label_map = {}
    
    for new_idx, old_label in enumerate(unique_labels):
        mask = labels == old_label
        count = np.sum(mask)
        if count == 0:
            continue
        r, g, b = centroids[old_label].astype(int)
        palette.append({
            'id': new_idx,
            'rgb': (r, g, b),
            'hex': rgb_to_hex(r, g, b),
            'textColor': get_contrast_color(r, g, b),
            'count': int(count)
        })
        label_map[old_label] = new_idx
    
    # Remap labels
    remapped = np.zeros(pixel_count, dtype=np.int32)
    for old_label, new_label in label_map.items():
        remapped[labels == old_label] = new_label
    
    return centroids, remapped, palette

def find_text_regions(image_array, assignments, palette, min_size=100, max_size=50000):
    """
    Find regions that likely contain text/math using connected components.
    Returns list of bounding boxes.
    """
    height, width = image_array.shape[:2]
    pixel_count = width * height
    
    # Create binary mask: dark pixels (likely text)
    luminance = np.zeros(pixel_count, dtype=np.float64)
    for i, color in enumerate(palette):
        mask = assignments == i
        lum = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
        luminance[mask] = lum
    
    # Dark pixels = text
    text_mask = (luminance < 128).reshape(height, width)
    
    # Label connected components
    labeled_array, num_features = ndimage.label(text_mask)
    
    # Get region properties
    regions = []
    for region_id in range(1, min(num_features + 1, 1000)):
        region_pixels = np.where(labeled_array == region_id)[0]
        
        if len(region_pixels) < min_size or len(region_pixels) > max_size:
            continue
        
        xs = region_pixels % width
        ys = region_pixels // width
        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()
        w, h = x_max - x_min, y_max - y_min
        
        if w < 10 or h < 10:
            continue
        
        regions.append({
            'bbox': (int(x_min), int(y_min), int(w), int(h)),
            'pixel_count': int(len(region_pixels))
        })
    
    return regions

def ocr_region(image_path, region_bbox, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    """
    Run Tesseract OCR on a specific region of an image.
    region_bbox = (x, y, width, height)
    """
    try:
        img = Image.open(image_path)
        x, y, w, h = region_bbox
        cropped = img.crop((x, y, x + w, y + h))
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            cropped.save(tmp.name)
            tmp_path = tmp.name
        
        result = subprocess.run(
            [tesseract_path, tmp_path, 'stdout', '--psm', '7'],
            capture_output=True, text=True, timeout=10
        )
        
        os.unlink(tmp_path)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        return None

def ocr_full_page(image_path, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    """
    Run Tesseract OCR on the full page.
    """
    try:
        result = subprocess.run(
            [tesseract_path, image_path, 'stdout', '--psm', '6'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        return None

def extract_math_from_ocr(text):
    """
    Extract math expressions from OCR text.
    Strict filtering: requires math operators, rejects prose.
    """
    if not text:
        return []
    
    # Common English words to reject (small set)
    stop_words = {
        'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has',
        'been', 'are', 'was', 'were', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'not', 'but', 'or', 'nor', 'so', 'yet',
        'both', 'either', 'neither', 'each', 'every', 'all', 'some', 'any',
        'no', 'none', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
        'eight', 'nine', 'ten', 'first', 'second', 'third', 'last', 'next',
        'previous', 'following', 'above', 'below', 'under', 'over', 'between',
        'among', 'through', 'during', 'before', 'after', 'since', 'until',
        'while', 'when', 'where', 'why', 'how', 'what', 'which', 'who',
        'whom', 'whose', 'if', 'then', 'else', 'because', 'as', 'than',
        'though', 'although', 'even', 'just', 'only', 'also', 'very', 'too',
        'quite', 'rather', 'somewhat', 'almost', 'nearly', 'hardly',
        'scarcely', 'barely', 'completely', 'totally', 'entirely', 'fully',
        'partly', 'partially', 'half', 'twice', 'thrice', 'once', 'again',
        'further', 'moreover', 'furthermore', 'however', 'nevertheless',
        'nonetheless', 'otherwise', 'instead', 'meanwhile', 'afterward',
        'afterwards', 'earlier', 'later', 'soon', 'now', 'here', 'there',
        'everywhere', 'somewhere', 'anywhere', 'nowhere', 'elsewhere',
        'is', 'am', 'be', 'being', 'do', 'does', 'did', 'done', 'get',
        'gets', 'got', 'make', 'makes', 'made', 'take', 'takes', 'took',
        'taken', 'come', 'comes', 'came', 'go', 'goes', 'went', 'gone',
        'see', 'sees', 'saw', 'seen', 'know', 'knows', 'knew', 'known',
        'think', 'thinks', 'thought', 'say', 'says', 'said', 'tell',
        'tells', 'told', 'ask', 'asks', 'asked', 'work', 'works', 'worked',
        'try', 'tries', 'tried', 'want', 'wants', 'wanted', 'give', 'gives',
        'gave', 'given', 'find', 'finds', 'found', 'put', 'puts', 'putting',
        'set', 'sets', 'setting', 'let', 'lets', 'letting', 'begin',
        'begins', 'began', 'begun', 'seem', 'seems', 'seemed', 'feel',
        'feels', 'felt', 'leave', 'leaves', 'left', 'call', 'calls',
        'called', 'keep', 'keeps', 'kept', 'bring', 'brings', 'brought',
        'hold', 'holds', 'held', 'stand', 'stands', 'stood', 'turn',
        'turns', 'turned', 'start', 'starts', 'started', 'show', 'shows',
        'showed', 'shown', 'hear', 'hears', 'heard', 'play', 'plays',
        'played', 'run', 'runs', 'ran', 'move', 'moves', 'moved', 'live',
        'lives', 'lived', 'believe', 'believes', 'believed', 'happen',
        'happens', 'happened', 'write', 'writes', 'wrote', 'written',
        'provide', 'provides', 'provided', 'sit', 'sits', 'sat', 'lose',
        'loses', 'lost', 'pay', 'pays', 'paid', 'meet', 'meets', 'met',
        'include', 'includes', 'included', 'continue', 'continues',
        'continued', 'learn', 'learns', 'learned', 'change', 'changes',
        'changed', 'lead', 'leads', 'led', 'understand', 'understands',
        'understood', 'watch', 'watches', 'watched', 'follow', 'follows',
        'followed', 'stop', 'stops', 'stopped', 'create', 'creates',
        'created', 'speak', 'speaks', 'spoke', 'spoken', 'read', 'reads',
        'allow', 'allows', 'allowed', 'add', 'adds', 'added', 'spend',
        'spends', 'spent', 'grow', 'grows', 'grew', 'grown', 'open',
        'opens', 'opened', 'walk', 'walks', 'walked', 'offer', 'offers',
        'offered', 'remember', 'remembers', 'remembered', 'love', 'loves',
        'loved', 'consider', 'considers', 'considered', 'appear', 'appears',
        'appeared', 'buy', 'buys', 'bought', 'wait', 'waits', 'waited',
        'serve', 'serves', 'served', 'die', 'dies', 'died', 'send', 'sends',
        'sent', 'expect', 'expects', 'expected', 'build', 'builds', 'built',
        'stay', 'stays', 'stayed', 'fall', 'falls', 'fell', 'fallen', 'cut',
        'cuts', 'cutting', 'reach', 'reaches', 'reached', 'kill', 'kills',
        'killed', 'remain', 'remains', 'remained',
    }
    
    # Math expression patterns - strict matching
    patterns = [
        # Greek letter with operator: α = β, γ ≤ δ, etc.
        r'[α-ωΑ-Ω]\s*[=<>≤≥≠+\-*/]\s*[a-zA-Zα-ωΑ-Ω0-9]+',
        # Math function: sin(x), cos(x), log(x), etc.
        r'(?:sin|cos|tan|log|ln|exp|sqrt|det|dim|rank|trace|diag)\s*\([^)]+\)',
        # Variable with subscript/superscript: x_1, x^2, x², etc.
        r'[a-zA-Z]\s*[_^]\s*[0-9]+',
        # Simple equation with single letter: x = 5, y = 10, etc.
        r'^[a-zA-Z]\s*=\s*[0-9]+$',
        # Summation/product: Σx, ∏x, etc.
        r'[∑∏]\s*[a-zA-Z0-9]+',
        # Integral: ∫f(x)dx, etc.
        r'∫\s*[a-zA-Z]\s*[d][a-zA-Z]',
    ]
    
    expressions = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            match = match.strip()
            if len(match) < 2:
                continue
            # Check if match contains any stop words
            words = match.lower().split()
            if any(word in stop_words for word in words):
                continue
            expressions.append(match)
    
    # Remove duplicates
    expressions = list(set(expressions))
    
    return expressions

def process_pdf_vision(pdf_path, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe", max_pages=5, dpi=200):
    """
    Process a PDF file using vision-based math extraction.
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
            
            # Save full page for OCR
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                img.save(tmp.name)
                tmp_path = tmp.name
            
            # OCR full page
            ocr_text = ocr_full_page(tmp_path, tesseract_path)
            
            if ocr_text:
                math_exprs = extract_math_from_ocr(ocr_text)
                if math_exprs:
                    results.append({
                        'page': page_num + 1,
                        'ocr_text': ocr_text[:500],
                        'math_expressions': math_exprs,
                    })
            
            os.unlink(tmp_path)
        
        doc.close()
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Vision-based math expression extractor')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--tesseract', default=r'C:\Program Files\Tesseract-OCR\tesseract.exe', help='Path to tesseract executable')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages to process')
    parser.add_argument('--dpi', type=int, default=200, help='DPI for PDF rendering')
    parser.add_argument('--output', default='DATASETS/vision_math_extraction.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    print(f"Processing: {args.pdf_path}")
    print(f"Tesseract: {args.tesseract}")
    print(f"Max pages: {args.max_pages}")
    print(f"DPI: {args.dpi}")
    
    results = process_pdf_vision(args.pdf_path, args.tesseract, args.max_pages, args.dpi)
    
    output = {
        'pdf_path': args.pdf_path,
        'total_pages_processed': args.max_pages,
        'math_regions_found': len(results),
        'results': results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nFound {len(results)} pages with math expressions")
    print(f"Results written to {args.output}")
    
    for r in results:
        print(f"\n  Page {r['page']}: {len(r['math_expressions'])} expressions")
        for expr in r['math_expressions'][:5]:
            print(f"    {expr}")

if __name__ == '__main__':
    main()