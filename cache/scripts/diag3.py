#!/usr/bin/env python3
"""Diagnostic: isolate pipeline failure."""

import sys
import os
import tempfile

script_path = "/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/vision_comparison_pipeline.py"

# Read and patch the file
with open(script_path, 'r') as f:
    content = f.read()

# 1. Add debug in recognize_formula for empty results
old1 = """            if result:
                return result.get('text', ''), result.get('confidence', 0.0), 'pix2text'
            else:
                return '', 0.0, 'empty'"""

new1 = """            if result:
                print(f"DEBUG: result has text, skipping empty check: {[k: v for k, v in result.items() if k != 'confidence'] if isinstance(result, dict) else result}")
                return result.get('text', ''), result.get('confidence', 0.0), 'pix2text'
            else:
                return '', 0.0, 'empty'"""

content = content.replace(old1, new1)

# 2. Add debug in classify_alignment for empty recognition
old2 = """        source_clean = source_text.strip()
        recognized_clean = recognized_text.strip() if recognized_text else ''"""

new2 = """        source_clean = source_text.strip()
        recognized_clean = recognized_text.strip() if recognized_text else ''
        print(f"DEBUG: source='{source_clean}', recognized='{recognized_clean}', method={method if 'method' in locals() else 'N/A'}")"""

content = content.replace(old2, new2)

with open(script_path, 'w') as f:
    f.write(content)

print("Patched")
