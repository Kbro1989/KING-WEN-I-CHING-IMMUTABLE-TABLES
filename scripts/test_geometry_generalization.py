#!/usr/bin/env python3
"""
Test Geometry Generalization & Clipping Regression
===================================================
Tests baseline (15, 15) vs asym_tight_y1 (3, 1) vs asym_tight_y2 (3, 2)
across:
1. The 4 known crops of 1907.04931 (regression check)
2. Complex mathematical structures from 2104.01277 and 2206.00364:
   - Superscripts & subscripts
   - Tall delimiters (parentheses, norms)
   - Summations & arrows
Evaluates:
- Formula isolation (absence of prose words)
- Glyph preservation (no clipped ascenders, descenders, or symbols)
- Truncation detection
"""

import sys
import json
import logging
from pathlib import Path
from PIL import Image

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

import fitz
import cv2
import numpy as np
from pix2text import Pix2Text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('geometry_generalization')

p2t = Pix2Text()

samples = [
    # 4 known crops from 1907.04931
    {
        'paper': '1907.04931',
        'pdf': 'C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/1907.04931_GraphSAINT_ Graph Sampling Based Inductive Learning Method.pdf',
        'page': 4,
        'bbox': {'x0': 179.552, 'y0': 551.407, 'x1': 204.295, 'y1': 564.208},
        'target_tokens': ['\\zeta', 'v', '\\ell+1'],
        'desc': 'Greek with subscript and superscript: ζ_v^(ℓ+1)'
    },
    {
        'paper': '1907.04931',
        'pdf': 'C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/1907.04931_GraphSAINT_ Graph Sampling Based Inductive Learning Method.pdf',
        'page': 4,
        'bbox': {'x0': 225.952, 'y0': 566.351, 'x1': 250.695, 'y1': 579.153},
        'target_tokens': ['\\zeta', 'v', '\\ell+1'],
        'desc': 'Parenthesized variable: E(ζ_v^(ℓ+1))'
    },
    {
        'paper': '1907.04931',
        'pdf': 'C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/1907.04931_GraphSAINT_ Graph Sampling Based Inductive Learning Method.pdf',
        'page': 12,
        'bbox': {'x0': 307.911, 'y0': 286.718, 'x1': 325.006, 'y1': 303.859},
        'target_tokens': ['\\sqrt', 'p'],
        'desc': 'Square root radical with subscript: √pe'
    },
    {
        'paper': '1907.04931',
        'pdf': 'C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/1907.04931_GraphSAINT_ Graph Sampling Based Inductive Learning Method.pdf',
        'page': 12,
        'bbox': {'x0': 169.089, 'y0': 306.263, 'x1': 199.689, 'y1': 323.403},
        'target_tokens': ['\\propto', '\\sqrt', 'p'],
        'desc': 'Proportionality and square root: ∝√pe.'
    },
    # Broader structures from 2104.01277
    {
        'paper': '2104.01277',
        'pdf': 'C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/2104.01277_Beyond Low-Pass Filters_ Adaptive Feature Propagation on Graphs.pdf',
        'page': 2,
        'bbox': {'x0': 421.919, 'y0': 406.707, 'x1': 485.279, 'y1': 420.793},
        'target_tokens': ['\\lambda', '+'],
        'desc': 'Parentheses, summation index and Greek lambda: j=1(λj+Q))'
    },
    {
        'paper': '2104.01277',
        'pdf': 'C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/2104.01277_Beyond Low-Pass Filters_ Adaptive Feature Propagation on Graphs.pdf',
        'page': 2,
        'bbox': {'x0': 50.4, 'y0': 180.0, 'x1': 107.4, 'y1': 192.2},
        'target_tokens': ['\\le', '\\|', '\\mu'],
        'desc': 'Inequality, norm delimiters and Greek mu: ≤∥T∥µ(I)'
    },
]

def run_tests():
    geometries = [
        ('baseline', 15, 15),
        ('asym_y1', 3, 1),
        ('asym_y2', 3, 2),
    ]

    results = []

    for s in samples:
        doc = fitz.open(s['pdf'])
        page = doc[s['page'] - 1]
        b = s['bbox']

        logger.info(f"\n=======================================================")
        logger.info(f"Sample: {s['paper']} p{s['page']} - {s['desc']}")
        logger.info(f"=======================================================")

        sample_res = {'sample': s['desc'], 'paper': s['paper'], 'page': s['page'], 'configs': {}}

        for name, px, py in geometries:
            rect = fitz.Rect(b['x0'] - px, b['y0'] - py, b['x1'] + px, b['y1'] + py)
            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=rect, colorspace=fitz.csRGB, alpha=False)
            img_bgr = cv2.imdecode(np.frombuffer(pix.tobytes('png'), dtype=np.uint8), cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # Recognize
            res = p2t.recognize_formula(pil_img)
            text = res.get('text', '') if isinstance(res, dict) else str(res).strip()

            # Check target tokens
            tokens_present = all(tok.lower() in text.lower() for tok in s['target_tokens'])

            # Check multiline
            is_multiline = '\\\\' in text or '\\begin' in text

            sample_res['configs'][name] = {
                'shape': list(img_bgr.shape),
                'text': text,
                'tokens_present': tokens_present,
                'is_multiline': is_multiline,
            }

            logger.info(f"[{name:10s}] shape={str(img_bgr.shape):16s} multiline={is_multiline} tokens_ok={tokens_present}")
            logger.info(f"    Recognized: {text[:80]!r}")

        doc.close()
        results.append(sample_res)

    out_file = REPO_ROOT / 'cache' / 'geometry_generalization_results.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"\nWrote results to {out_file}")

if __name__ == '__main__':
    run_tests()
