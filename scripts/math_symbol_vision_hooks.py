"""
Math Symbol Vision Hooks
========================
Descriptive hooks for the vision parser that leverage ChromaNumber's
K-Means + flood fill region detection to identify math symbols in PDF pages.

This module adds a "math symbol detection layer" on top of the existing
vision_math_extractor.py pipeline. It uses ChromaNumber's image processing
to find regions that look like math symbols, then classifies them by
shape, size, and aspect ratio.

Math Symbol Taxonomy:
- Operators: +, -, ×, ÷, =, <, >, ≤, ≥, ≠, ≈, ≡, ∝
- Greek letters: α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, π, ρ, σ, τ, υ, φ, χ, ψ, ω
- Capital Greek: Γ, Δ, Θ, Λ, Ξ, Π, Σ, Υ, Φ, Ψ, Ω
- Calculus: ∫, ∮, ∂, ∇, ∑, ∏, √, ∞
- Logic: ∧, ∨, ¬, ∀, ∃, ∈, ∉, ⊆, ⊂, ∪, ∩
- Arrows: →, ←, ↔, ⟹, ⟸, ↦
- Functions: sin, cos, tan, log, ln, exp, det, dim, rank, trace, diag
- Subscripts/Superscripts: x₁, x², x₃, etc.
- Fractions: a/b, (a+b)/(c+d), etc.
- Brackets: (), [], {}, ⟨⟩, ||, ⌊⌋, ⌈⌉

Tool Expectations:
- Equation solvers (SymPy, Wolfram): expect clean variable/operator/symbol tuples
- LaTeX generators: expect symbol sequences with spatial relationships
- Wolfram Language converters: expect StandardForm-compatible symbol names
- Math OCR: expect bounding boxes + confidence scores
"""

import json, os, re, tempfile, subprocess
import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

def kmeans_quantize(image_array, max_colors=16):
    """K-Means color quantization using scipy.cluster.vq.kmeans2 (fast)."""
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

# Math symbol shape profiles (aspect ratio, fill ratio, stroke width)
# Used to classify regions by shape
MATH_SYMBOL_PROFILES = {
    # Operators (roughly square, medium fill)
    'equals': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'plus': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'minus': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'times': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'divide': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'less': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'greater': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'leq': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'geq': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'neq': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'approx': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'equiv': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'propto': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    
    # Greek letters (roughly square, medium fill)
    'alpha': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'beta': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'gamma': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'delta': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'epsilon': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'zeta': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'eta': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'theta': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'iota': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'kappa': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'lambda': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'mu': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'nu': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'xi': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'pi': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'rho': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'sigma': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'tau': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'upsilon': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'phi': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'chi': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'psi': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    'omega': {'aspect_range': (0.6, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    
    # Calculus symbols (tall, narrow)
    'integral': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'contour_integral': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'partial': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'nabla': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'sum': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'product': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'sqrt': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'infinity': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    
    # Logic symbols
    'and': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'or': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'not': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'forall': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'exists': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'element': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'not_element': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'subset': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'subseteq': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'union': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    'intersection': {'aspect_range': (0.8, 1.2), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    
    # Arrows (wide, short)
    'rightarrow': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'leftarrow': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'leftrightarrow': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'implies': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'impliedby': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'mapsto': {'aspect_range': (2.0, 5.0), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    
    # Brackets (tall, narrow)
    'lparen': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'rparen': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'lbracket': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'rbracket': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'lbrace': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'rbrace': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'langle': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'rangle': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'lfloor': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'rfloor': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'lceil': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'rceil': {'aspect_range': (0.2, 0.5), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'vertical_bar': {'aspect_range': (0.1, 0.3), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    'double_vertical_bar': {'aspect_range': (0.1, 0.3), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2)},
    
    # Large brackets and fraction bars (sparse thin strokes)
    'large_bracket': {'aspect_range': (0.1, 0.5), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'fraction_bar': {'aspect_range': (2.0, 20.0), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'sqrt_vinculum': {'aspect_range': (2.0, 20.0), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    'horizontal_line': {'aspect_range': (5.0, 50.0), 'fill_range': (0.001, 0.03), 'stroke_range': (0.001, 0.03)},
    'vertical_line': {'aspect_range': (0.02, 0.2), 'fill_range': (0.001, 0.05), 'stroke_range': (0.001, 0.05)},
    
    # Digits (roughly square, medium fill)
    'digit': {'aspect_range': (0.5, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    
    # Letters (roughly square, medium fill)
    'letter': {'aspect_range': (0.5, 1.0), 'fill_range': (0.1, 0.5), 'stroke_range': (0.05, 0.2)},
    
    # Subscript/superscript (small, offset)
    'subscript': {'aspect_range': (0.3, 0.7), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2), 'size_ratio': (0.3, 0.7)},
    'superscript': {'aspect_range': (0.3, 0.7), 'fill_range': (0.05, 0.3), 'stroke_range': (0.05, 0.2), 'size_ratio': (0.3, 0.7)},
    
    # Fraction (tall, narrow, with horizontal line)
    'fraction': {'aspect_range': (0.2, 0.5), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    
    # Decimal point (small, round)
    'decimal': {'aspect_range': (0.8, 1.2), 'fill_range': (0.3, 0.8), 'stroke_range': (0.1, 0.5), 'size_ratio': (0.1, 0.3)},
    
    # Comma (small, round, with tail)
    'comma': {'aspect_range': (0.5, 1.0), 'fill_range': (0.2, 0.6), 'stroke_range': (0.1, 0.4), 'size_ratio': (0.1, 0.3)},
    
    # Period (small, round)
    'period': {'aspect_range': (0.8, 1.2), 'fill_range': (0.3, 0.8), 'stroke_range': (0.1, 0.5), 'size_ratio': (0.1, 0.3)},
    
    # Colon (two dots)
    'colon': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
    
    # Semicolon (dot + comma)
    'semicolon': {'aspect_range': (0.3, 0.7), 'fill_range': (0.1, 0.4), 'stroke_range': (0.05, 0.2)},
}

# Tool expectations: what each tool expects to find in equations
TOOL_EXPECTATIONS = {
    'sympy_solver': {
        'description': 'SymPy equation solver expects clean variable/operator/symbol tuples',
        'required_symbols': ['variable', 'operator', 'value'],
        'optional_symbols': ['function', 'subscript', 'superscript', 'fraction'],
        'output_format': 'Python expression string',
        'example': 'x = 5, y = 10, z = x + y',
    },
    'latex_generator': {
        'description': 'LaTeX generator expects symbol sequences with spatial relationships',
        'required_symbols': ['symbol', 'position', 'size'],
        'optional_symbols': ['subscript', 'superscript', 'fraction', 'bracket'],
        'output_format': 'LaTeX string',
        'example': 'x^2 + y^2 = z^2',
    },
    'wolfram_converter': {
        'description': 'Wolfram Language converter expects StandardForm-compatible symbol names',
        'required_symbols': ['wolfram_name', 'unicode_equivalent'],
        'optional_symbols': ['alias', 'escape_sequence'],
        'output_format': 'Wolfram Language expression',
        'example': 'x^2 + y^2 == z^2',
    },
    'math_ocr': {
        'description': 'Math OCR expects bounding boxes + confidence scores',
        'required_symbols': ['symbol', 'bbox', 'confidence'],
        'optional_symbols': ['context', 'page_number'],
        'output_format': 'JSON with symbol detections',
        'example': '{"symbol": "x", "bbox": [100, 200, 50, 30], "confidence": 0.95}',
    },
    'equation_extractor': {
        'description': 'Equation extractor expects complete equations with metadata',
        'required_symbols': ['equation', 'variables', 'operators'],
        'optional_symbols': ['functions', 'constants', 'units'],
        'output_format': 'JSON with equation metadata',
        'example': '{"equation": "E = mc^2", "variables": ["E", "m", "c"], "operators": ["=", "^"]}',
    },
    'notation_mapper': {
        'description': 'Notation mapper expects Unicode math symbols mapped to tool-specific names',
        'required_symbols': ['unicode', 'tool_name'],
        'optional_symbols': ['category', 'subcategory'],
        'output_format': 'JSON mapping',
        'example': '{"unicode": "π", "tool_name": "Pi", "category": "greek"}',
    },
}

def classify_region_shape(width, height, pixel_count):
    """
    Classify a region by its shape profile.
    Returns a list of possible symbol types.
    """
    if width == 0 or height == 0:
        return []
    
    aspect_ratio = width / height
    fill_ratio = pixel_count / (width * height)
    
    # Normalized stroke width (stroke_width / max_dimension)
    # For a region with N pixels in a WxH box, the stroke width is roughly
    # sqrt(N / (π * max(W, H))) for a circular stroke
    stroke_width = np.sqrt(pixel_count / (np.pi * max(width, height)))
    normalized_stroke = stroke_width / max(width, height)
    
    matches = []
    for symbol_type, profile in MATH_SYMBOL_PROFILES.items():
        aspect_min, aspect_max = profile['aspect_range']
        fill_min, fill_max = profile['fill_range']
        stroke_min, stroke_max = profile['stroke_range']
        
        if (aspect_min <= aspect_ratio <= aspect_max and
            fill_min <= fill_ratio <= fill_max and
            stroke_min <= normalized_stroke <= stroke_max):
            matches.append(symbol_type)
    
    # If no match, try without stroke constraint
    if not matches:
        for symbol_type, profile in MATH_SYMBOL_PROFILES.items():
            aspect_min, aspect_max = profile['aspect_range']
            fill_min, fill_max = profile['fill_range']
            
            if (aspect_min <= aspect_ratio <= aspect_max and
                fill_min <= fill_ratio <= fill_max):
                matches.append(symbol_type)
    
    return matches

def detect_math_symbols(image_array, assignments, palette, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe", min_size=50, max_size=5000):
    """
    Detect math symbols in a page image using ChromaNumber-style region detection.
    Each detected region is OCR'd with Tesseract for precise symbol identification.
    Returns a list of detected symbols with their bounding boxes, OCR text, and classifications.
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
    
    # Dark pixels = text/math
    text_mask = (luminance < 128).reshape(height, width)
    
    # Label connected components
    labeled_array, num_features = ndimage.label(text_mask)
    
    # Get region properties
    symbols = []
    for region_id in range(1, min(num_features + 1, 500)):
        region_pixels_2d = np.where(labeled_array == region_id)
        if len(region_pixels_2d[0]) == 0:
            continue
        # Convert 2D indices to flat indices
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
        shape_classes = classify_region_shape(w, h, len(region_pixels))
        
        # Get color
        color_idx = int(assignments[region_pixels[0]])
        if color_idx < len(palette):
            color = palette[color_idx]['rgb']
        else:
            color = (0, 0, 0)
        
        # OCR this specific region for precise symbol identification
        ocr_text = ocr_region_from_array(image_array, (x_min, y_min, w, h), tesseract_path)
        
        symbols.append({
            'bbox': (int(x_min), int(y_min), int(w), int(h)),
            'pixel_count': int(len(region_pixels)),
            'aspect_ratio': float(w / h),
            'fill_ratio': float(len(region_pixels) / (w * h)),
            'shape_classes': shape_classes,
            'color': tuple(int(c) for c in color),
            'centroid': (int(np.mean(xs)), int(np.mean(ys))),
            'ocr_text': ocr_text,
        })
    
    return symbols

def ocr_region_from_array(image_array, region_bbox, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    """
    Run Tesseract OCR on a specific region of an image array.
    region_bbox = (x, y, width, height)
    """
    try:
        x, y, w, h = region_bbox
        # Extract region from image array
        region = image_array[y:y+h, x:x+w]
        # Convert to PIL Image
        img = Image.fromarray(region)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        
        # Run Tesseract with single character mode for symbols
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

def hook_math_symbols_to_vision(pdf_path, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe", max_pages=3, dpi=200):
    """
    Hook math symbol detection into the vision pipeline.
    Returns a list of pages with detected math symbols and OCR text.
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
            
            # Apply K-Means quantization (ChromaNumber-style)
            centroids, assignments, palette = kmeans_quantize(img_array, max_colors=16)
            
            # Detect math symbols (with per-region OCR)
            symbols = detect_math_symbols(img_array, assignments, palette, tesseract_path)
            
            # Save full page for OCR
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                img.save(tmp.name)
                tmp_path = tmp.name
            
            # OCR full page
            ocr_text = ocr_full_page(tmp_path, tesseract_path)
            
            os.unlink(tmp_path)
            
            if symbols or ocr_text:
                results.append({
                    'page': page_num + 1,
                    'symbols_detected': len(symbols),
                    'symbols': symbols,
                    'ocr_text': ocr_text[:500] if ocr_text else None,
                })
        
        doc.close()
        
    except Exception as e:
        import traceback
        print(f"Error processing {pdf_path}: {repr(e)}")
        traceback.print_exc()
    
    return results

def ocr_full_page(image_path, tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    """Run Tesseract OCR on the full page."""
    try:
        result = subprocess.run(
            [tesseract_path, image_path, 'stdout', '--psm', '6'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Math symbol vision hooks')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--tesseract', default=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    parser.add_argument('--max-pages', type=int, default=3)
    parser.add_argument('--dpi', type=int, default=200)
    parser.add_argument('--output', default='DATASETS/math_symbols_detected.json')
    
    args = parser.parse_args()
    
    print(f"Processing: {args.pdf_path}")
    print(f"Max pages: {args.max_pages}")
    print(f"DPI: {args.dpi}")
    
    results = hook_math_symbols_to_vision(args.pdf_path, args.tesseract, args.max_pages, args.dpi)
    
    output = {
        'pdf_path': args.pdf_path,
        'total_pages_processed': args.max_pages,
        'pages_with_symbols': len(results),
        'tool_expectations': TOOL_EXPECTATIONS,
        'results': results,
    }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nFound {len(results)} pages with math symbols")
    print(f"Results written to {args.output}")
    
    for r in results:
        print(f"\n  Page {r['page']}: {r['symbols_detected']} symbols detected")
        for sym in r['symbols'][:5]:
            print(f"    {sym['shape_classes']}: bbox={sym['bbox']}, aspect={sym['aspect_ratio']:.2f}")

if __name__ == '__main__':
    main()