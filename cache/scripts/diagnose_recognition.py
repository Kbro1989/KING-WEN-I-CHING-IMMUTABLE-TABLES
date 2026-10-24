#!/usr/bin/env python3
"""Diagnostic: identify where recognition fails."""

import tempfile
import cv2
import numpy as np
from pix2text import Pix2Text

def test_pix2text():
    """Test Pix2Text with known good formulas vs tiny crops."""
    p2t = Pix2Text()
    
    # Positive control: create a simple test image with formula
    print("=== Test 1: Simple formula (known good) ===")
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255  # white bg
    # Will need actual text - using placeholder
    
    # Test 2: Reproduce actual crop dimensions
    print("\n=== Test 2: Tiny crop (actual dimensions) ===")
    # Based on earlier: 99x51 at zoom=4
    tiny_img = np.ones((51, 99, 3), dtype=np.uint8) * 200  # light gray bg
    # Draw something simple
    cv2.putText(tiny_img, "x^2", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 1)
    
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp_path = tmp.name
    tmp.close()
    
    # Test 1: large image
    cv2.imwrite(tmp_path, img)
    print(f"Large image: {img.shape}")
    try:
        result = p2t.recognize_formula(tmp_path)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception on large: {e}")
    
    # Test 2: tiny image  
    cv2.imwrite(tmp_path, tiny_img)
    print(f"\nTiny image: {tiny_img.shape}")
    try:
        result = p2t.recognize_formula(tmp_path)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception on tiny: {e}")
    
    import os
    os.remove(tmp_path)

if __name__ == '__main__':
    test_pix2text()