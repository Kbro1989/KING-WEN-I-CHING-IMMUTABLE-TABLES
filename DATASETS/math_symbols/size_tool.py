#!/usr/bin/env python3
"""
Size-Aware Symbol Reference Tool for ArXiv Math Papers
======================================================
Uses Metamath symbol library as the reference.
All Metamath symbols are n x 19 pixels (12pt font baseline).
When analyzing paper symbols, use this to detect:
  - Subscripts/superscripts (height < 19px)
  - Large operators (height > 19px)
  - Wide operators (aspect ratio > 1.5)
  - Variable identification via shape matching
"""

import json
import os

METAMATH_DIR = r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols'

def load_manifest():
    with open(os.path.join(METAMATH_DIR, 'manifest.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

# Build index from manifest
_symbol_index = load_manifest()
name_to_symbol = {s['name']: s for s in _symbol_index}

def analyze_symbol(detected_w, detected_h, baseline=19):
    """
    Analyze a symbol's dimensions against the Metamath 19px baseline.
    
    Returns dict with size category, role, and reference info.
    """
    scale = detected_h / baseline
    aspect = detected_w / detected_h if detected_h > 0 else 0
    
    result = {
        'detected_w': detected_w,
        'detected_h': detected_h,
        'baseline': baseline,
        'size_category': _classify_size(detected_h, detected_w),
        'aspect': aspect,
        'scale_factor': scale,
        'role': _infer_role(detected_h, aspect, scale),
    }
    return result

def _classify_size(height, width):
    """Classify symbol size based on detected dimensions."""
    aspect = width / height if height > 0 else 0
    
    if height < 8:
        return 'superscript_or_sub'
    elif height < 12:
        return 'tiny_subscript'
    elif height < 16:
        return 'small_script'
    elif height < 22:
        return 'normal_inline'
    elif height < 30:
        return 'large_operator'
    elif height < 45:
        return 'very_large'
    else:
        return 'equation_level'

def _infer_role(height, aspect, scale):
    """Infer the mathematical role from dimensions."""
    if scale < 0.5:
        return 'subscript_or_superscript'
    elif scale < 0.8:
        return 'script_or_small'
    elif scale < 1.2:
        if aspect < 0.6:
            return 'variable_or_function'
        elif aspect < 1.2:
            return 'binary_operator'
        else:
            return 'wide_operator'
    elif scale < 1.5:
        if aspect > 2.0:
            return 'large_operator'
        return 'normal_operator'
    elif scale < 2.0:
        if aspect > 1.5:
            return 'big_operator'
        return 'large_operator'
    else:
        return 'equation_level_operator'

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        dw = int(sys.argv[1])
        dh = int(sys.argv[2])
        result = analyze_symbol(dw, dh)
        print(f"  Detected: {dw}x{dh}px")
        print(f"  Size: {result['size_category']}")
        print(f"  Role: {result['role']}")
        print(f"  Scale: {result['scale_factor']:.2f}x baseline")
        print(f"  Aspect: {result['aspect']:.2f}")
