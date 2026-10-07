"""
Formal Math Research PDF Parser / Resolver
==========================================
Unified pipeline that chains all extraction layers:
  1. Text Extraction (PyMuPDF)
  2. Vision Region Detection (K-Means + flood fill)
  3. OCR (Tesseract)
  4. Math Symbol Classification
  5. Spatial Relationship Extraction
  6. Equation Structure Assembly

Output: Structured JSON with classified symbols, spatial relationships,
assembled equation trees, and preserved context. No solving, no derivation.

Usage:
  python math_pdf_parser.py <pdf_path> [--max-pages N] [--dpi N] [--output FILE]
"""
import json, os, re, tempfile, subprocess, sys
import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

# ============================================================================
# Layer 1: Text Extraction
# ============================================================================

def extract_text_blocks(pdf_path, page_num):
    """Extract text blocks with positions from a PDF page."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    blocks = page.get_text("blocks")
    words = page.get_text("words")
    text = page.get_text("text")
    doc.close()
    return blocks, words, text

# ============================================================================
# Layer 2: Vision Region Detection
# ============================================================================

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
    if aspect_ratio > 3.0 and fill_ratio < 0.1:
        return 'fraction_bar'
    if aspect_ratio > 2.0 and fill_ratio < 0.15:
        return 'sqrt_vinculum'
    if aspect_ratio < 0.4 and h > 50:
        return 'large_bracket'
    if aspect_ratio < 0.3:
        return 'vertical_bar'
    if w < 20 and h < 20:
        return 'script'
    return 'symbol'

# ============================================================================
# Layer 3: OCR
# ============================================================================

def ocr_region_from_array(image_array, region_bbox, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    """Run Tesseract OCR on a specific region of an image array."""
    try:
        x, y, w, h = region_bbox
        region = image_array[y:y+h, x:x+w]
        img = Image.fromarray(region)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        result = subprocess.run(
            [tesseract_path, tmp_path, 'stdout', '--psm', '10'],
            capture_output=True, text=True, timeout=5
        )
        os.unlink(tmp_path)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

# ============================================================================
# Layer 4: Math Symbol Classification
# ============================================================================

MATH_SYMBOL_LOOKUP = {
    'α': {'name': 'alpha', 'category': 'greek', 'unicode': 'α', 'latex': '\\alpha'},
    'β': {'name': 'beta', 'category': 'greek', 'unicode': 'β', 'latex': '\\beta'},
    'γ': {'name': 'gamma', 'category': 'greek', 'unicode': 'γ', 'latex': '\\gamma'},
    'δ': {'name': 'delta', 'category': 'greek', 'unicode': 'δ', 'latex': '\\delta'},
    'ε': {'name': 'epsilon', 'category': 'greek', 'unicode': 'ε', 'latex': '\\epsilon'},
    'ζ': {'name': 'zeta', 'category': 'greek', 'unicode': 'ζ', 'latex': '\\zeta'},
    'η': {'name': 'eta', 'category': 'greek', 'unicode': 'η', 'latex': '\\eta'},
    'θ': {'name': 'theta', 'category': 'greek', 'unicode': 'θ', 'latex': '\\theta'},
    'ι': {'name': 'iota', 'category': 'greek', 'unicode': 'ι', 'latex': '\\iota'},
    'κ': {'name': 'kappa', 'category': 'greek', 'unicode': 'κ', 'latex': '\\kappa'},
    'λ': {'name': 'lambda', 'category': 'greek', 'unicode': 'λ', 'latex': '\\lambda'},
    'μ': {'name': 'mu', 'category': 'greek', 'unicode': 'μ', 'latex': '\\mu'},
    'ν': {'name': 'nu', 'category': 'greek', 'unicode': 'ν', 'latex': '\\nu'},
    'ξ': {'name': 'xi', 'category': 'greek', 'unicode': 'ξ', 'latex': '\\xi'},
    'π': {'name': 'pi', 'category': 'greek', 'unicode': 'π', 'latex': '\\pi'},
    'ρ': {'name': 'rho', 'category': 'greek', 'unicode': 'ρ', 'latex': '\\rho'},
    'σ': {'name': 'sigma', 'category': 'greek', 'unicode': 'σ', 'latex': '\\sigma'},
    'τ': {'name': 'tau', 'category': 'greek', 'unicode': 'τ', 'latex': '\\tau'},
    'υ': {'name': 'upsilon', 'category': 'greek', 'unicode': 'υ', 'latex': '\\upsilon'},
    'φ': {'name': 'phi', 'category': 'greek', 'unicode': 'φ', 'latex': '\\phi'},
    'χ': {'name': 'chi', 'category': 'greek', 'unicode': 'χ', 'latex': '\\chi'},
    'ψ': {'name': 'psi', 'category': 'greek', 'unicode': 'ψ', 'latex': '\\psi'},
    'ω': {'name': 'omega', 'category': 'greek', 'unicode': 'ω', 'latex': '\\omega'},
    '+': {'name': 'plus', 'category': 'operator', 'unicode': '+', 'latex': '+'},
    '-': {'name': 'minus', 'category': 'operator', 'unicode': '-', 'latex': '-'},
    '−': {'name': 'minus', 'category': 'operator', 'unicode': '−', 'latex': '-'},
    '×': {'name': 'times', 'category': 'operator', 'unicode': '×', 'latex': '\\times'},
    '·': {'name': 'cdot', 'category': 'operator', 'unicode': '·', 'latex': '\\cdot'},
    '÷': {'name': 'divide', 'category': 'operator', 'unicode': '÷', 'latex': '\\div'},
    '=': {'name': 'equals', 'category': 'operator', 'unicode': '=', 'latex': '='},
    '<': {'name': 'less', 'category': 'operator', 'unicode': '<', 'latex': '<'},
    '>': {'name': 'greater', 'category': 'operator', 'unicode': '>', 'latex': '>'},
    '≤': {'name': 'leq', 'category': 'operator', 'unicode': '≤', 'latex': '\\leq'},
    '≥': {'name': 'geq', 'category': 'operator', 'unicode': '≥', 'latex': '\\geq'},
    '≠': {'name': 'neq', 'category': 'operator', 'unicode': '≠', 'latex': '\\neq'},
    '≈': {'name': 'approx', 'category': 'operator', 'unicode': '≈', 'latex': '\\approx'},
    '≡': {'name': 'equiv', 'category': 'operator', 'unicode': '≡', 'latex': '\\equiv'},
    '∝': {'name': 'propto', 'category': 'operator', 'unicode': '∝', 'latex': '\\propto'},
    '±': {'name': 'pm', 'category': 'operator', 'unicode': '±', 'latex': '\\pm'},
    '∫': {'name': 'integral', 'category': 'calculus', 'unicode': '∫', 'latex': '\\int'},
    '∮': {'name': 'oint', 'category': 'calculus', 'unicode': '∮', 'latex': '\\oint'},
    '∂': {'name': 'partial', 'category': 'calculus', 'unicode': '∂', 'latex': '\\partial'},
    '∇': {'name': 'nabla', 'category': 'calculus', 'unicode': '∇', 'latex': '\\nabla'},
    '∑': {'name': 'sum', 'category': 'calculus', 'unicode': '∑', 'latex': '\\sum'},
    '∏': {'name': 'prod', 'category': 'calculus', 'unicode': '∏', 'latex': '\\prod'},
    '√': {'name': 'sqrt', 'category': 'calculus', 'unicode': '√', 'latex': '\\sqrt'},
    '∞': {'name': 'infty', 'category': 'calculus', 'unicode': '∞', 'latex': '\\infty'},
    '∧': {'name': 'wedge', 'category': 'logic', 'unicode': '∧', 'latex': '\\wedge'},
    '∨': {'name': 'vee', 'category': 'logic', 'unicode': '∨', 'latex': '\\vee'},
    '¬': {'name': 'neg', 'category': 'logic', 'unicode': '¬', 'latex': '\\neg'},
    '∀': {'name': 'forall', 'category': 'logic', 'unicode': '∀', 'latex': '\\forall'},
    '∃': {'name': 'exists', 'category': 'logic', 'unicode': '∃', 'latex': '\\exists'},
    '∈': {'name': 'in', 'category': 'logic', 'unicode': '∈', 'latex': '\\in'},
    '∉': {'name': 'notin', 'category': 'logic', 'unicode': '∉', 'latex': '\\notin'},
    '⊆': {'name': 'subseteq', 'category': 'logic', 'unicode': '⊆', 'latex': '\\subseteq'},
    '⊂': {'name': 'subset', 'category': 'logic', 'unicode': '⊂', 'latex': '\\subset'},
    '∪': {'name': 'cup', 'category': 'logic', 'unicode': '∪', 'latex': '\\cup'},
    '∩': {'name': 'cap', 'category': 'logic', 'unicode': '∩', 'latex': '\\cap'},
    '→': {'name': 'to', 'category': 'arrow', 'unicode': '→', 'latex': '\\to'},
    '←': {'name': 'gets', 'category': 'arrow', 'unicode': '←', 'latex': '\\gets'},
    '↔': {'name': 'leftrightarrow', 'category': 'arrow', 'unicode': '↔', 'latex': '\\leftrightarrow'},
    '⟹': {'name': 'implies', 'category': 'arrow', 'unicode': '⟹', 'latex': '\\implies'},
    '⟸': {'name': 'impliedby', 'category': 'arrow', 'unicode': '⟸', 'latex': '\\impliedby'},
    '↦': {'name': 'mapsto', 'category': 'arrow', 'unicode': '↦', 'latex': '\\mapsto'},
    '(': {'name': 'lparen', 'category': 'bracket', 'unicode': '(', 'latex': '('},
    ')': {'name': 'rparen', 'category': 'bracket', 'unicode': ')', 'latex': ')'},
    '[': {'name': 'lbracket', 'category': 'bracket', 'unicode': '[', 'latex': '['},
    ']': {'name': 'rbracket', 'category': 'bracket', 'unicode': ']', 'latex': ']'},
    '{': {'name': 'lbrace', 'category': 'bracket', 'unicode': '{', 'latex': '\\{'},
    '}': {'name': 'rbrace', 'category': 'bracket', 'unicode': '}', 'latex': '\\}'},
    '⟨': {'name': 'langle', 'category': 'bracket', 'unicode': '⟨', 'latex': '\\langle'},
    '⟩': {'name': 'rangle', 'category': 'bracket', 'unicode': '⟩', 'latex': '\\rangle'},
    '⌊': {'name': 'lfloor', 'category': 'bracket', 'unicode': '⌊', 'latex': '\\lfloor'},
    '⌋': {'name': 'rfloor', 'category': 'bracket', 'unicode': '⌋', 'latex': '\\rfloor'},
    '⌈': {'name': 'lceil', 'category': 'bracket', 'unicode': '⌈', 'latex': '\\lceil'},
    '⌉': {'name': 'rceil', 'category': 'bracket', 'unicode': '⌉', 'latex': '\\rceil'},
    '|': {'name': 'lvert', 'category': 'bracket', 'unicode': '|', 'latex': '|'},
    '‖': {'name': 'lVert', 'category': 'bracket', 'unicode': '‖', 'latex': '\\|'},
    'sin': {'name': 'sin', 'category': 'function', 'unicode': 'sin', 'latex': '\\sin'},
    'cos': {'name': 'cos', 'category': 'function', 'unicode': 'cos', 'latex': '\\cos'},
    'tan': {'name': 'tan', 'category': 'function', 'unicode': 'tan', 'latex': '\\tan'},
    'log': {'name': 'log', 'category': 'function', 'unicode': 'log', 'latex': '\\log'},
    'ln': {'name': 'ln', 'category': 'function', 'unicode': 'ln', 'latex': '\\ln'},
    'exp': {'name': 'exp', 'category': 'function', 'unicode': 'exp', 'latex': '\\exp'},
    'det': {'name': 'det', 'category': 'function', 'unicode': 'det', 'latex': '\\det'},
    'dim': {'name': 'dim', 'category': 'function', 'unicode': 'dim', 'latex': '\\dim'},
    'rank': {'name': 'rank', 'category': 'function', 'unicode': 'rank', 'latex': '\\rank'},
    'trace': {'name': 'trace', 'category': 'function', 'unicode': 'trace', 'latex': '\\trace'},
    'diag': {'name': 'diag', 'category': 'function', 'unicode': 'diag', 'latex': '\\diag'},
    '0': {'name': 'zero', 'category': 'digit', 'unicode': '0', 'latex': '0'},
    '1': {'name': 'one', 'category': 'digit', 'unicode': '1', 'latex': '1'},
    '2': {'name': 'two', 'category': 'digit', 'unicode': '2', 'latex': '2'},
    '3': {'name': 'three', 'category': 'digit', 'unicode': '3', 'latex': '3'},
    '4': {'name': 'four', 'category': 'digit', 'unicode': '4', 'latex': '4'},
    '5': {'name': 'five', 'category': 'digit', 'unicode': '5', 'latex': '5'},
    '6': {'name': 'six', 'category': 'digit', 'unicode': '6', 'latex': '6'},
    '7': {'name': 'seven', 'category': 'digit', 'unicode': '7', 'latex': '7'},
    '8': {'name': 'eight', 'category': 'digit', 'unicode': '8', 'latex': '8'},
    '9': {'name': 'nine', 'category': 'digit', 'unicode': '9', 'latex': '9'},
    'a': {'name': 'a', 'category': 'variable', 'unicode': 'a', 'latex': 'a'},
    'b': {'name': 'b', 'category': 'variable', 'unicode': 'b', 'latex': 'b'},
    'c': {'name': 'c', 'category': 'variable', 'unicode': 'c', 'latex': 'c'},
    'd': {'name': 'd', 'category': 'variable', 'unicode': 'd', 'latex': 'd'},
    'e': {'name': 'e', 'category': 'variable', 'unicode': 'e', 'latex': 'e'},
    'f': {'name': 'f', 'category': 'variable', 'unicode': 'f', 'latex': 'f'},
    'g': {'name': 'g', 'category': 'variable', 'unicode': 'g', 'latex': 'g'},
    'h': {'name': 'h', 'category': 'variable', 'unicode': 'h', 'latex': 'h'},
    'i': {'name': 'i', 'category': 'variable', 'unicode': 'i', 'latex': 'i'},
    'j': {'name': 'j', 'category': 'variable', 'unicode': 'j', 'latex': 'j'},
    'k': {'name': 'k', 'category': 'variable', 'unicode': 'k', 'latex': 'k'},
    'l': {'name': 'l', 'category': 'variable', 'unicode': 'l', 'latex': 'l'},
    'm': {'name': 'm', 'category': 'variable', 'unicode': 'm', 'latex': 'm'},
    'n': {'name': 'n', 'category': 'variable', 'unicode': 'n', 'latex': 'n'},
    'o': {'name': 'o', 'category': 'variable', 'unicode': 'o', 'latex': 'o'},
    'p': {'name': 'p', 'category': 'variable', 'unicode': 'p', 'latex': 'p'},
    'q': {'name': 'q', 'category': 'variable', 'unicode': 'q', 'latex': 'q'},
    'r': {'name': 'r', 'category': 'variable', 'unicode': 'r', 'latex': 'r'},
    's': {'name': 's', 'category': 'variable', 'unicode': 's', 'latex': 's'},
    't': {'name': 't', 'category': 'variable', 'unicode': 't', 'latex': 't'},
    'u': {'name': 'u', 'category': 'variable', 'unicode': 'u', 'latex': 'u'},
    'v': {'name': 'v', 'category': 'variable', 'unicode': 'v', 'latex': 'v'},
    'w': {'name': 'w', 'category': 'variable', 'unicode': 'w', 'latex': 'w'},
    'x': {'name': 'x', 'category': 'variable', 'unicode': 'x', 'latex': 'x'},
    'y': {'name': 'y', 'category': 'variable', 'unicode': 'y', 'latex': 'y'},
    'z': {'name': 'z', 'category': 'variable', 'unicode': 'z', 'latex': 'z'},
    'A': {'name': 'A', 'category': 'variable', 'unicode': 'A', 'latex': 'A'},
    'B': {'name': 'B', 'category': 'variable', 'unicode': 'B', 'latex': 'B'},
    'C': {'name': 'C', 'category': 'variable', 'unicode': 'C', 'latex': 'C'},
    'D': {'name': 'D', 'category': 'variable', 'unicode': 'D', 'latex': 'D'},
    'E': {'name': 'E', 'category': 'variable', 'unicode': 'E', 'latex': 'E'},
    'F': {'name': 'F', 'category': 'variable', 'unicode': 'F', 'latex': 'F'},
    'G': {'name': 'G', 'category': 'variable', 'unicode': 'G', 'latex': 'G'},
    'H': {'name': 'H', 'category': 'variable', 'unicode': 'H', 'latex': 'H'},
    'I': {'name': 'I', 'category': 'variable', 'unicode': 'I', 'latex': 'I'},
    'J': {'name': 'J', 'category': 'variable', 'unicode': 'J', 'latex': 'J'},
    'K': {'name': 'K', 'category': 'variable', 'unicode': 'K', 'latex': 'K'},
    'L': {'name': 'L', 'category': 'variable', 'unicode': 'L', 'latex': 'L'},
    'M': {'name': 'M', 'category': 'variable', 'unicode': 'M', 'latex': 'M'},
    'N': {'name': 'N', 'category': 'variable', 'unicode': 'N', 'latex': 'N'},
    'O': {'name': 'O', 'category': 'variable', 'unicode': 'O', 'latex': 'O'},
    'P': {'name': 'P', 'category': 'variable', 'unicode': 'P', 'latex': 'P'},
    'Q': {'name': 'Q', 'category': 'variable', 'unicode': 'Q', 'latex': 'Q'},
    'R': {'name': 'R', 'category': 'variable', 'unicode': 'R', 'latex': 'R'},
    'S': {'name': 'S', 'category': 'variable', 'unicode': 'S', 'latex': 'S'},
    'T': {'name': 'T', 'category': 'variable', 'unicode': 'T', 'latex': 'T'},
    'U': {'name': 'U', 'category': 'variable', 'unicode': 'U', 'latex': 'U'},
    'V': {'name': 'V', 'category': 'variable', 'unicode': 'V', 'latex': 'V'},
    'W': {'name': 'W', 'category': 'variable', 'unicode': 'W', 'latex': 'W'},
    'X': {'name': 'X', 'category': 'variable', 'unicode': 'X', 'latex': 'X'},
    'Y': {'name': 'Y', 'category': 'variable', 'unicode': 'Y', 'latex': 'Y'},
    'ω': {'name': 'omega', 'category': 'greek', 'unicode': 'ω', 'latex': '\\omega'},
    'ο': {'name': 'omicron', 'category': 'greek', 'unicode': 'ο', 'latex': 'o'},
    
    # Capital Greek (from Wolfram reference)
    'Β': {'name': 'Beta', 'category': 'greek_capital', 'unicode': 'Β', 'latex': '\\Beta'},
    'Γ': {'name': 'Gamma', 'category': 'greek_capital', 'unicode': 'Γ', 'latex': '\\Gamma'},
    'Δ': {'name': 'Delta', 'category': 'greek_capital', 'unicode': 'Δ', 'latex': '\\Delta'},
    'Ε': {'name': 'Epsilon', 'category': 'greek_capital', 'unicode': 'Ε', 'latex': '\\Epsilon'},
    'Ζ': {'name': 'Zeta', 'category': 'greek_capital', 'unicode': 'Ζ', 'latex': '\\Zeta'},
    'Η': {'name': 'Eta', 'category': 'greek_capital', 'unicode': 'Η', 'latex': '\\Eta'},
    'Θ': {'name': 'Theta', 'category': 'greek_capital', 'unicode': 'Θ', 'latex': '\\Theta'},
    'Ι': {'name': 'Iota', 'category': 'greek_capital', 'unicode': 'Ι', 'latex': '\\Iota'},
    'Κ': {'name': 'Kappa', 'category': 'greek_capital', 'unicode': 'Κ', 'latex': '\\Kappa'},
    'Λ': {'name': 'Lambda', 'category': 'greek_capital', 'unicode': 'Λ', 'latex': '\\Lambda'},
    'Μ': {'name': 'Mu', 'category': 'greek_capital', 'unicode': 'Μ', 'latex': '\\Mu'},
    'Ν': {'name': 'Nu', 'category': 'greek_capital', 'unicode': 'Ν', 'latex': '\\Nu'},
    'Ξ': {'name': 'Xi', 'category': 'greek_capital', 'unicode': 'Ξ', 'latex': '\\Xi'},
    'Ο': {'name': 'Omicron', 'category': 'greek_capital', 'unicode': 'Ο', 'latex': '\\Omicron'},
    'Π': {'name': 'Pi', 'category': 'greek_capital', 'unicode': 'Π', 'latex': '\\Pi'},
    'Ρ': {'name': 'Rho', 'category': 'greek_capital', 'unicode': 'Ρ', 'latex': '\\Rho'},
    'Σ': {'name': 'Sigma', 'category': 'greek_capital', 'unicode': 'Σ', 'latex': '\\Sigma'},
    'Τ': {'name': 'Tau', 'category': 'greek_capital', 'unicode': 'Τ', 'latex': '\\Tau'},
    'Υ': {'name': 'Upsilon', 'category': 'greek_capital', 'unicode': 'Υ', 'latex': '\\Upsilon'},
    'Φ': {'name': 'Phi', 'category': 'greek_capital', 'unicode': 'Φ', 'latex': '\\Phi'},
    'Χ': {'name': 'Chi', 'category': 'greek_capital', 'unicode': 'Χ', 'latex': '\\Chi'},
    'Ψ': {'name': 'Psi', 'category': 'greek_capital', 'unicode': 'Ψ', 'latex': '\\Psi'},
    'Ω': {'name': 'Omega', 'category': 'greek_capital', 'unicode': 'Ω', 'latex': '\\Omega'},
    
    # Double-struck (blackboard bold)
    'ℂ': {'name': 'C', 'category': 'double_struck', 'unicode': 'ℂ', 'latex': '\\mathbb{C}'},
    'ℍ': {'name': 'H', 'category': 'double_struck', 'unicode': 'ℍ', 'latex': '\\mathbb{H}'},
    'ℕ': {'name': 'N', 'category': 'double_struck', 'unicode': 'ℕ', 'latex': '\\mathbb{N}'},
    'ℙ': {'name': 'P', 'category': 'double_struck', 'unicode': 'ℙ', 'latex': '\\mathbb{P}'},
    'ℚ': {'name': 'Q', 'category': 'double_struck', 'unicode': 'ℚ', 'latex': '\\mathbb{Q}'},
    'ℛ': {'name': 'R', 'category': 'double_struck', 'unicode': 'ℛ', 'latex': '\\mathbb{R}'},
    'ℝ': {'name': 'R', 'category': 'double_struck', 'unicode': 'ℝ', 'latex': '\\mathbb{R}'},
    'ℤ': {'name': 'Z', 'category': 'double_struck', 'unicode': 'ℤ', 'latex': '\\mathbb{Z}'},
    
    # Script letters
    'ℒ': {'name': 'L', 'category': 'script', 'unicode': 'ℒ', 'latex': '\\mathcal{L}'},
    'ℬ': {'name': 'B', 'category': 'script', 'unicode': 'ℬ', 'latex': '\\mathcal{B}'},
    'ℳ': {'name': 'M', 'category': 'script', 'unicode': 'ℳ', 'latex': '\\mathcal{M}'},
    '𝒞': {'name': 'C', 'category': 'script', 'unicode': '𝒞', 'latex': '\\mathcal{C}'},
    '𝒢': {'name': 'G', 'category': 'script', 'unicode': '𝒢', 'latex': '\\mathcal{G}'},
    '𝒥': {'name': 'J', 'category': 'script', 'unicode': '𝒥', 'latex': '\\mathcal{J}'},
    '𝒦': {'name': 'K', 'category': 'script', 'unicode': '𝒦', 'latex': '\\mathcal{K}'},
    '𝒩': {'name': 'N', 'category': 'script', 'unicode': '𝒩', 'latex': '\\mathcal{N}'},
    '𝒪': {'name': 'O', 'category': 'script', 'unicode': '𝒪', 'latex': '\\mathcal{O}'},
    '𝒫': {'name': 'P', 'category': 'script', 'unicode': '𝒫', 'latex': '\\mathcal{P}'},
    '𝒬': {'name': 'Q', 'category': 'script', 'unicode': '𝒬', 'latex': '\\mathcal{Q}'},
    '𝒮': {'name': 'S', 'category': 'script', 'unicode': '𝒮', 'latex': '\\mathcal{S}'},
    '𝒯': {'name': 'T', 'category': 'script', 'unicode': '𝒯', 'latex': '\\mathcal{T}'},
    '𝒰': {'name': 'U', 'category': 'script', 'unicode': '𝒰', 'latex': '\\mathcal{U}'},
    '𝒱': {'name': 'V', 'category': 'script', 'unicode': '𝒱', 'latex': '\\mathcal{V}'},
    '𝒲': {'name': 'W', 'category': 'script', 'unicode': '𝒲', 'latex': '\\mathcal{W}'},
    '𝒳': {'name': 'X', 'category': 'script', 'unicode': '𝒳', 'latex': '\\mathcal{X}'},
    '𝒴': {'name': 'Y', 'category': 'script', 'unicode': '𝒴', 'latex': '\\mathcal{Y}'},
    '𝒵': {'name': 'Z', 'category': 'script', 'unicode': '𝒵', 'latex': '\\mathcal{Z}'},
    
    # Formal letters
    '𝔄': {'name': 'A', 'category': 'formal', 'unicode': '𝔄', 'latex': '\\mathfrak{A}'},
    '𝔅': {'name': 'B', 'category': 'formal', 'unicode': '𝔅', 'latex': '\\mathfrak{B}'},
    '𝔉': {'name': 'F', 'category': 'formal', 'unicode': '𝔉', 'latex': '\\mathfrak{F}'},
    '𝔊': {'name': 'G', 'category': 'formal', 'unicode': '𝔊', 'latex': '\\mathfrak{G}'},
    '𝔍': {'name': 'J', 'category': 'formal', 'unicode': '𝔍', 'latex': '\\mathfrak{J}'},
    '𝔎': {'name': 'K', 'category': 'formal', 'unicode': '𝔎', 'latex': '\\mathfrak{K}'},
    '𝔏': {'name': 'L', 'category': 'formal', 'unicode': '𝔏', 'latex': '\\mathfrak{L}'},
    '𝔐': {'name': 'M', 'category': 'formal', 'unicode': '𝔐', 'latex': '\\mathfrak{M}'},
    '𝔑': {'name': 'N', 'category': 'formal', 'unicode': '𝔑', 'latex': '\\mathfrak{N}'},
    '𝔒': {'name': 'O', 'category': 'formal', 'unicode': '𝔒', 'latex': '\\mathfrak{O}'},
    '𝔓': {'name': 'P', 'category': 'formal', 'unicode': '𝔓', 'latex': '\\mathfrak{P}'},
    '𝔘': {'name': 'U', 'category': 'formal', 'unicode': '𝔘', 'latex': '\\mathfrak{U}'},
    '𝔙': {'name': 'V', 'category': 'formal', 'unicode': '𝔙', 'latex': '\\mathfrak{V}'},
    '𝔚': {'name': 'W', 'category': 'formal', 'unicode': '𝔚', 'latex': '\\mathfrak{W}'},
    '𝔛': {'name': 'X', 'category': 'formal', 'unicode': '𝔛', 'latex': '\\mathfrak{X}'},
    '𝔜': {'name': 'Y', 'category': 'formal', 'unicode': '𝔜', 'latex': '\\mathfrak{Y}'},
    '𝔷': {'name': 'z', 'category': 'formal', 'unicode': '𝔷', 'latex': '\\mathfrak{z}'},
    
    # Additional operators
    '×': {'name': 'times', 'category': 'operator', 'unicode': '×', 'latex': '\\times'},
    '÷': {'name': 'divide', 'category': 'operator', 'unicode': '÷', 'latex': '\\div'},
    '±': {'name': 'pm', 'category': 'operator', 'unicode': '±', 'latex': '\\pm'},
    '∓': {'name': 'mp', 'category': 'operator', 'unicode': '∓', 'latex': '\\mp'},
    '∝': {'name': 'propto', 'category': 'operator', 'unicode': '∝', 'latex': '\\propto'},
    '≈': {'name': 'approx', 'category': 'operator', 'unicode': '≈', 'latex': '\\approx'},
    '≡': {'name': 'equiv', 'category': 'operator', 'unicode': '≡', 'latex': '\\equiv'},
    '∼': {'name': 'sim', 'category': 'operator', 'unicode': '∼', 'latex': '\\sim'},
    '≅': {'name': 'cong', 'category': 'operator', 'unicode': '≅', 'latex': '\\cong'},
    '⊕': {'name': 'oplus', 'category': 'operator', 'unicode': '⊕', 'latex': '\\oplus'},
    '⊗': {'name': 'otimes', 'category': 'operator', 'unicode': '⊗', 'latex': '\\otimes'},
    '⨯': {'name': 'cross', 'category': 'operator', 'unicode': '⨯', 'latex': '\\times'},
    
    # Additional calculus
    '∮': {'name': 'oint', 'category': 'calculus', 'unicode': '∮', 'latex': '\\oint'},
    '∞': {'name': 'infty', 'category': 'calculus', 'unicode': '∞', 'latex': '\\infty'},
    'ℏ': {'name': 'hbar', 'category': 'calculus', 'unicode': 'ℏ', 'latex': '\\hbar'},
    'ℵ': {'name': 'aleph', 'category': 'calculus', 'unicode': 'ℵ', 'latex': '\\aleph'},
    
    # Additional arrows
    '↦': {'name': 'mapsto', 'category': 'arrow', 'unicode': '↦', 'latex': '\\mapsto'},
    '⟷': {'name': 'leftrightarrow', 'category': 'arrow', 'unicode': '⟷', 'latex': '\\leftrightarrow'},
    '⟸': {'name': 'impliedby', 'category': 'arrow', 'unicode': '⟸', 'latex': '\\impliedby'},
    '⟹': {'name': 'implies', 'category': 'arrow', 'unicode': '⟹', 'latex': '\\implies'},
    
    # Other symbols
    '°': {'name': 'degree', 'category': 'other', 'unicode': '°', 'latex': '^{\\circ}'},
    '∴': {'name': 'therefore', 'category': 'other', 'unicode': '∴', 'latex': '\\therefore'},
    '∵': {'name': 'because', 'category': 'other', 'unicode': '∵', 'latex': '\\because'},
    '∶': {'name': 'ratio', 'category': 'other', 'unicode': '∶', 'latex': ':'},
    '∷': {'name': 'proportion', 'category': 'other', 'unicode': '∷', 'latex': '::'},
    '²': {'name': 'squared', 'category': 'other', 'unicode': '²', 'latex': '^2'},
    '·': {'name': 'cdot', 'category': 'operator', 'unicode': '·', 'latex': '\\cdot'},
    'ϵ': {'name': 'epsilon', 'category': 'greek', 'unicode': 'ϵ', 'latex': '\\epsilon'},
    'ℯ': {'name': 'e', 'category': 'other', 'unicode': 'ℯ', 'latex': 'e'},
    'ⅈ': {'name': 'i', 'category': 'other', 'unicode': 'ⅈ', 'latex': 'i'},
    'ⅉ': {'name': 'j', 'category': 'other', 'unicode': 'ⅉ', 'latex': 'j'},
}

SHAPE_BASED_CLASSIFICATION = {
    'integral': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'sum': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'prod': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'sqrt': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'fraction_bar': {'aspect_range': (2.0, 20.0), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'sqrt_vinculum': {'aspect_range': (2.0, 20.0), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'horizontal_line': {'aspect_range': (5.0, 50.0), 'fill_range': (0.001, 0.03), 'stroke_range': (0.001, 0.03)},
    'vertical_line': {'aspect_range': (0.02, 0.2), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'large_bracket': {'aspect_range': (0.1, 0.5), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
}

def classify_symbol(ocr_text, aspect_ratio, fill_ratio, normalized_stroke, region_type):
    """Classify a math symbol using OCR text and shape characteristics."""
    classifications = []
    
    if ocr_text and ocr_text in MATH_SYMBOL_LOOKUP:
        symbol = MATH_SYMBOL_LOOKUP[ocr_text]
        classifications.append({
            'name': symbol['name'],
            'category': symbol['category'],
            'unicode': symbol['unicode'],
            'latex': symbol['latex'],
            'confidence': 0.9,
            'method': 'direct_lookup',
        })
    
    if not classifications or classifications[0]['confidence'] < 0.5:
        for symbol_name, profile in SHAPE_BASED_CLASSIFICATION.items():
            aspect_min, aspect_max = profile['aspect_range']
            fill_min, fill_max = profile['fill_range']
            stroke_min, stroke_max = profile['stroke_range']
            
            if (aspect_min <= aspect_ratio <= aspect_max and
                fill_min <= fill_ratio <= fill_max and
                stroke_min <= normalized_stroke <= stroke_max):
                classifications.append({
                    'name': symbol_name,
                    'category': 'calculus' if symbol_name in ['integral', 'sum', 'prod', 'sqrt'] else 'structure',
                    'unicode': None,
                    'latex': None,
                    'confidence': 0.5,
                    'method': 'shape_based',
                })
    
    if region_type == 'fraction_bar':
        classifications.append({
            'name': 'fraction_bar',
            'category': 'structure',
            'unicode': None,
            'latex': '\\frac',
            'confidence': 0.8,
            'method': 'region_type',
        })
    elif region_type == 'large_bracket':
        classifications.append({
            'name': 'large_bracket',
            'category': 'bracket',
            'unicode': None,
            'latex': '\\left(',
            'confidence': 0.7,
            'method': 'region_type',
        })
    elif region_type == 'vertical_bar':
        classifications.append({
            'name': 'vertical_bar',
            'category': 'bracket',
            'unicode': '|',
            'latex': '|',
            'confidence': 0.6,
            'method': 'region_type',
        })
    elif region_type == 'script':
        classifications.append({
            'name': 'script',
            'category': 'script',
            'unicode': None,
            'latex': None,
            'confidence': 0.4,
            'method': 'region_type',
        })
    
    if not classifications and ocr_text:
        classifications.append({
            'name': ocr_text,
            'category': 'unknown',
            'unicode': ocr_text,
            'latex': ocr_text,
            'confidence': 0.3,
            'method': 'ocr_fallback',
        })
    
    classifications.sort(key=lambda x: x['confidence'], reverse=True)
    return classifications

# ============================================================================
# Layer 5: Spatial Relationship Extraction
# ============================================================================

def extract_spatial_relationships(regions):
    """Extract spatial relationships between math regions."""
    relationships = []
    sorted_regions = sorted(regions, key=lambda r: r['centroid'][1])
    
    for i, region in enumerate(sorted_regions):
        rx, ry, rw, rh = region['bbox']
        rcx, rcy = region['centroid']
        
        above = []
        below = []
        inside = []
        fraction_parts = []
        
        for j, other in enumerate(sorted_regions):
            if i == j:
                continue
            ox, oy, ow, oh = other['bbox']
            ocx, ocy = other['centroid']
            
            if ocy < ry and abs(ocx - rcx) < max(rw, ow):
                above.append({
                    'region_index': j,
                    'region_type': other['region_type'],
                    'vertical_distance': float(ry - ocy),
                    'horizontal_overlap': float(min(rx + rw, ox + ow) - max(rx, ox)),
                })
            
            if ocy > ry + rh and abs(ocx - rcx) < max(rw, ow):
                below.append({
                    'region_index': j,
                    'region_type': other['region_type'],
                    'vertical_distance': float(ocy - (ry + rh)),
                    'horizontal_overlap': float(min(rx + rw, ox + ow) - max(rx, ox)),
                })
            
            if region['region_type'] in ['large_bracket', 'vertical_bar']:
                if ox >= rx and ox + ow <= rx + rw and oy >= ry and oy + oh <= ry + rh:
                    inside.append({
                        'region_index': j,
                        'region_type': other['region_type'],
                    })
            
            if region['region_type'] == 'fraction_bar':
                if ocx >= rx and ocx <= rx + rw:
                    if ocy >= ry and ocy < ry + rh * 0.5:
                        fraction_parts.append({
                            'role': 'numerator',
                            'region_index': j,
                            'region_type': other['region_type'],
                            'centroid': other['centroid'],
                            'bbox': other['bbox'],
                        })
                    if ocy >= ry + rh * 0.5 and ocy <= ry + rh:
                        fraction_parts.append({
                            'role': 'denominator',
                            'region_index': j,
                            'region_type': other['region_type'],
                            'centroid': other['centroid'],
                            'bbox': other['bbox'],
                        })
        
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

# ============================================================================
# Layer 6: Equation Structure Assembly
# ============================================================================

def assemble_equation_structures(classified_symbols, relationships, text_blocks):
    """
    Assemble complete equation structures from classified symbols and relationships.
    Returns a list of equation trees with director signals.
    """
    equations = []
    
    # Group symbols by proximity (symbols that are close together form expressions)
    symbol_groups = group_symbols_by_proximity(classified_symbols)
    
    for group in symbol_groups:
        # Check if this group contains a fraction
        has_fraction = any(s['region_type'] == 'fraction_bar' for s in group)
        has_bracket = any(s['region_type'] in ['large_bracket', 'vertical_bar'] for s in group)
        has_operator = any(s.get('best_classification', {}).get('category') == 'operator' for s in group)
        
        if has_fraction or has_bracket or has_operator:
            # This group likely contains an equation
            equation = build_equation_tree(group, relationships, text_blocks)
            if equation:
                equations.append(equation)
    
    return equations

def group_symbols_by_proximity(symbols, max_distance=100):
    """Group symbols that are close to each other."""
    if not symbols:
        return []
    
    groups = []
    used = set()
    
    for i, sym in enumerate(symbols):
        if i in used:
            continue
        
        group = [sym]
        used.add(i)
        
        # Find all symbols close to this one
        for j, other in enumerate(symbols):
            if j in used:
                continue
            
            # Check distance
            x1, y1 = sym['centroid']
            x2, y2 = other['centroid']
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            if distance < max_distance:
                group.append(other)
                used.add(j)
        
        groups.append(group)
    
    return groups

def build_equation_tree(group, relationships, text_blocks):
    """Build an equation tree from a group of symbols."""
    # Sort symbols by x position (left to right)
    sorted_symbols = sorted(group, key=lambda s: s['centroid'][0])
    
    # Build expression string
    expression_parts = []
    for sym in sorted_symbols:
        best = sym.get('best_classification')
        if best:
            if best['category'] == 'operator':
                expression_parts.append(best['name'])
            elif best['category'] == 'variable':
                expression_parts.append(best['name'])
            elif best['category'] == 'digit':
                expression_parts.append(best['name'])
            elif best['category'] == 'greek':
                expression_parts.append(best['name'])
            elif best['category'] == 'function':
                expression_parts.append(best['name'])
            elif best['category'] == 'bracket':
                expression_parts.append(best['name'])
            elif best['category'] == 'calculus':
                expression_parts.append(best['name'])
            elif best['category'] == 'structure':
                expression_parts.append(best['name'])
            else:
                expression_parts.append(sym.get('ocr_text', '?'))
    
    expression = ' '.join(expression_parts)
    
    # Find context
    context_before = []
    context_after = []
    
    if sorted_symbols:
        first_sym = sorted_symbols[0]
        last_sym = sorted_symbols[-1]
        fx, fy = first_sym['centroid']
        lx, ly = last_sym['centroid']
        
        for block in text_blocks:
            bx, by, bw, bh = block[:4]
            bcy = by + bh/2
            
            if bcy < fy and abs(bcy - fy) < 100:
                context_before.append(block[4])
            if bcy > ly and abs(bcy - ly) < 100:
                context_after.append(block[4])
    
    return {
        'expression': expression,
        'symbols': sorted_symbols,
        'context_before': context_before[:3],
        'context_after': context_after[:3],
        'has_fraction': any(s['region_type'] == 'fraction_bar' for s in group),
        'has_bracket': any(s['region_type'] in ['large_bracket', 'vertical_bar'] for s in group),
    }

# ============================================================================
# Main Pipeline
# ============================================================================

def process_pdf(pdf_path, max_pages=5, dpi=200, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    """Process a PDF file through all extraction layers."""
    results = []
    
    try:
        doc = pymupdf.open(pdf_path)
        
        for page_num in range(min(max_pages, len(doc))):
            page = doc[page_num]
            
            # Layer 1: Text extraction
            blocks, words, text = extract_text_blocks(pdf_path, page_num)
            
            # Layer 2: Vision region detection
            mat = pymupdf.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_array = np.array(img)
            
            centroids, assignments, palette = kmeans_quantize(img_array, max_colors=16)
            regions = find_math_regions(img_array, assignments, palette)
            
            # Layer 3: OCR per region
            for region in regions:
                ocr_text = ocr_region_from_array(img_array, region['bbox'], tesseract_path)
                region['ocr_text'] = ocr_text
            
            # Layer 4: Symbol classification
            classified = []
            for i, region in enumerate(regions):
                ocr_text = region.get('ocr_text', '')
                aspect_ratio = region.get('aspect_ratio', 1.0)
                fill_ratio = region.get('fill_ratio', 0.5)
                normalized_stroke = region.get('normalized_stroke', 0.1)
                region_type = region.get('region_type', 'symbol')
                
                classifications = classify_symbol(ocr_text, aspect_ratio, fill_ratio, normalized_stroke, region_type)
                
                classified.append({
                    'region_index': i,
                    'bbox': region['bbox'],
                    'centroid': region['centroid'],
                    'region_type': region_type,
                    'ocr_text': ocr_text,
                    'classifications': classifications,
                    'best_classification': classifications[0] if classifications else None,
                })
            
            # Layer 5: Spatial relationships
            relationships = extract_spatial_relationships(regions)
            
            # Layer 6: Equation assembly
            equations = assemble_equation_structures(classified, relationships, blocks)
            
            results.append({
                'page': page_num + 1,
                'text_blocks': len(blocks),
                'math_regions': len(regions),
                'classified_symbols': len(classified),
                'relationships': len(relationships),
                'equations': equations,
                'page_text': text[:500] if text else None,
            })
        
        doc.close()
        
    except Exception as e:
        import traceback
        print(f"Error processing {pdf_path}: {repr(e)}")
        traceback.print_exc()
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Formal math research PDF parser/resolver')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--max-pages', type=int, default=5)
    parser.add_argument('--dpi', type=int, default=200)
    parser.add_argument('--output', default='DATASETS/math_parsed.json')
    
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
        print(f"    Text blocks: {r['text_blocks']}")
        print(f"    Math regions: {r['math_regions']}")
        print(f"    Classified symbols: {r['classified_symbols']}")
        print(f"    Relationships: {r['relationships']}")
        print(f"    Equations: {len(r['equations'])}")
        for eq in r['equations'][:2]:
            print(f"      {eq['expression'][:80]}")

if __name__ == '__main__':
    main()