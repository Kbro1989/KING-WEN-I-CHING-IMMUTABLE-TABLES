#!/usr/bin/env python3
"""Diagnostic: reproduce exact pipeline crop and test recognition flow."""

import sys
import os
import tempfile

script_path = "/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/vision_comparison_pipeline.py"
print(f"Loading: {script_path}")
import importlib.util
spec = importlib.util.spec_from_file_location("vision_comparison_pipeline", script_path)
vision_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vision_module)
VisionComparer = vision_module.VisionComparer

import fitz
import cv2
import numpy as np
import logging
logging.basicConfig(level=logging.WARNING)

def diagnose():
    comparer = VisionComparer()
    
    candidate = {
        'paper_id': '1907.04931',
        'page': 4,
        'bbox': {'x0': 179.552001953125, 'y0': 551.40673828125, 'x1': 204.29542541503906, 'y1': 564.20849609375},
        'line_text': 'ζ(ℓ+1)',
        'classification': 'inline_math'
    }
    
    from pypdf import PdfWriter
    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_pdf_path = temp_pdf.name
    temp_pdf.close()
    
    with open(temp_pdf_path, 'wb') as f:
        f.write(b'%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000020 00000 n 
0000000030 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
40
%%EOF')
    
    try:
        crop = comparer.crop_pdf_region(
            Path(temp_pdf_path),
            candidate['bbox'],
            padding=15,
            page_num=0,
            zoom=4
        )
        print(f"Crop: {crop is not None}")
        if crop is not None:
            print(f"Crop shape: {crop.shape}")
        
        if crop is not None:
            result_text, confidence, method = comparer.recognize_formula(crop)
            print(f"Recognize result: text={result_text}, confidence={confidence}, method={method}")
    finally:
        try:
            os.unlink(temp_pdf_path)
        except:
            pass

if __name__ == '__main__':
    diagnose()
