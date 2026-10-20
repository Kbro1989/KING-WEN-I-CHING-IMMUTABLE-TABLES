"""
Vision Comparison Pipeline
===========================
Compare PDF formula positions against the Metamath glyph catalog (symbols.zip)
using Pix2Text OCR + vision crop comparison.

Pipeline:
  1. Load positional entries from unified_manifest.json
  2. Crop PDF region using bbox coordinates (with padding)
  3. Run Pix2Text recognize_formula() on crop
  4. Cross-reference with symbols.zip catalog (3304 glyphs)
  5. Classify alignment failure (stretch, brace, image, divider, etc.)
  6. Append result to unified_manifest.json

This module is fork-safe: no Hermes imports, pure Python + bundled libraries.
"""

import json
import os
import sys
import glob
import argparse
import logging
from pathlib import Path

# Load bundled libraries
import fitz  # PyMuPDF 1.28.2
import cv2  # OpenCV 5.0.0
import numpy as np

# Pix2Text imports
from pix2text import Pix2Text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
REPO_ROOT = Path(__file__).parent.parent if '__file__' in globals() else Path.cwd()
MANIFEST_PATH = REPO_ROOT / 'DATASETS' / 'unified_manifest.json'
SYMBOLS_ZIP_DIR = REPO_ROOT / 'symbols' / 'symbols'
PDF_DIR = REPO_ROOT / 'DATASETS' / 'benchmark_pdfs'
OUTPUT_DIR = REPO_ROOT / 'DATASETS' / 'vision_comparison'

# Pix2Text initialization
class VisionComparer:
    def __init__(self):
        self.pix2text = Pix2Text()
        self.success = 0
        self.failed = 0
        self.comparisons = []
        
    def load_manifest(self):
        """Load the unified manifest."""
        with open(MANIFEST_PATH) as f:
            self.manifest = json.load(f)
        self.glyph_catalog = self.manifest.get('symbols_zip_catalog', {}).get('catalog', [])
        logger.info(f"Loaded {len(self.glyph_catalog)} symbols.zip glyphs")
        
    def load_candidates(self, paper_id=None, source_file=None):
        """Load positional candidates from the candidates_*.json files."""
        candidates = []
        if paper_id:
            pattern = REPO_ROOT / 'DATASETS' / f'candidates_{paper_id}.json'
            if pattern.exists():
                with open(pattern) as f:
                    candidates = json.load(f)
                logger.info(f"Loaded {len(candidates)} candidates for {paper_id} from {pattern}")
        elif source_file:
            if source_file.exists():
                with open(source_file) as f:
                    candidates = json.load(f)
                logger.info(f"Loaded {len(candidates)} candidates from {source_file}")
        else:
            for f in sorted(REPO_ROOT.glob('DATASETS/candidates_*.json')):
                with open(f) as fh:
                    candidates.extend(json.load(fh))
        return candidates
    
    def crop_pdf_region(self, pdf_path, bbox, padding=2, page_num=0):
        """
        Crop PDF region using bbox coordinates with padding.
        pdf_path: path to PDF file
        bbox: {x0, y0, x1, y1} in PDF points
        page_num: page number (0-indexed)
        Returns: numpy array (image) or None if crop failed
        """
        doc = fitz.open(str(pdf_path))
        page = doc[page_num]  # use specified page
        rect = fitz.Rect(bbox['x0'] - padding, bbox['y0'] - padding,
                        bbox['x1'] + padding, bbox['y1'] + padding)
        try:
            # Get pixmap and convert to numpy array
            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=rect)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            doc.close()
            return img
        except Exception as e:
            doc.close()
            logger.warning(f"Crop failed: {e}")
            return None
    
    def recognize_formula(self, crop):
        """
        Run Pix2Text on the crop and get reconstructed LaTeX.
        Returns: (reconstructed_text, confidence, method)
        """
        if crop is None:
            return None, 0.0, 'crop_failed'
        
        try:
            # Pix2Text recognize_formula expects a numpy array
            # Convert BGR to RGB for pix2text
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            result = self.pix2text.recognize_formula(crop_rgb)
            if result:
                return result.get('text', ''), result.get('confidence', 0.0), 'pix2text'
            else:
                return '', 0.0, 'empty'
        except Exception as e:
            logger.warning(f"Recognition failed: {e}")
            return None, 0.0, 'recognition_error'
    
    def classify_alignment(self, source_text, recognized_text, source_bbox):
        """
        Classify alignment failure type.
        Returns: (alignment_class, description)
        """
        if source_text is None:
            return 'unknown', 'source null'
        
        source_clean = source_text.strip()
        recognized_clean = recognized_text.strip() if recognized_text else ''
        
        if not recognized_clean:
            return 'empty_recognition', 'recognition produced no text'
        
        # Check for divBy
        if len(source_clean) == 1 and len(recognized_clean) == 1:
            if source_clean in '[]{}()|' or recognized_clean in '[]{}()|':
                return 'divider_bracket', f'single char: source={source_clean}, recognized={recognized_clean}'
        
        # Check for possibility of stretch
        if len(source_clean) == 1 and len(recognized_clean) > 1:
            return 'stretch_suspect', f'possible stretch: source="{source_clean}", recognized="{recognized_clean}"'
        
        if len(source_clean) > 1 and len(recognized_clean) == 1:
            return 'merge_suspect', f'possible merge: source="{source_clean}", recognized="{recognized_clean}"'
        
        # Check for symbols that might be images
        if source_clean == '':
            return 'image_region', 'source region appears to be an image, not text'
        
        # Verify overlap
        if not recognized_clean:
            return 'unrecognized', f'reconstructed "{recognized_clean}" does not match "{source_clean}"'
        
        # Check if recognized text contains source text
        if source_clean in recognized_clean or recognized_clean in source_clean:
            return 'matched', f'matched: source="{source_clean}", recognized="{recognized_clean}"'
        
        return 'mismatch', f'diff: source="{source_clean}", recognized="{recognized_clean}"'
    
    def compare_candidate(self, candidate):
        """
        Compare a single candidate against the symbols.zip catalog.
        Returns: comparison dict
        """
        paper = candidate.get('paper_id', 'unknown')
        page = candidate.get('page', 0)
        bbox = candidate.get('bbox', {})
        source_text = candidate.get('line_text', '')
        classification = candidate.get('classification', 'unknown')
        
        # Crop PDF region or render HTML page using bbox coordinates
        # Locate actual source file (PDF or HTML)
        # Locate actual source file (PDF or HTML)
        source_path = PDF_DIR / f"{paper}.pdf"
        if not source_path.exists():
            # Try HTML version
            html_path = REPO_ROOT / 'DATASETS' / f"{paper}.html"
            if html_path.exists():
                source_path = html_path
            else:
                # Search for any file matching paper ID (including zotero directory)
                search_paths = [
                    REPO_ROOT,
                    Path("C:/Users/krist/Desktop/zotero"),
                    Path("C:/Users/krist/Desktop/zotero/learning-corpus"),
                ]
                for search_path in search_paths:
                    if search_path.exists():
                        for f in search_path.glob('**/*' + paper + '*'):
                            if f.is_file() and f.suffix.lower() in ['.pdf', '.html']:
                                source_path = f
                                break
                    if source_path.exists():
                        break
        
        if not source_path.exists():
            logger.warning(f"Source not found: {source_path}")
            return {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop': None,
                'recognized': '',
                'confidence': 0.0,
                'alignment': 'source_missing',
                'method': 'source_missing'
            }
        
        # Crop PDF region using bbox coordinates (PDF points)
        crop = self.crop_pdf_region(source_path, bbox, padding=15, page_num=candidate.get("page", 0) - 1)
        if crop is None:
            logger.warning(f"Failed to crop region for {paper} p{page}")
            return {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop': None,
                'recognized': '',
                'confidence': 0.0,
                'alignment': 'crop_failed',
                'method': 'crop_failed'
            }
        
        # Run Pix2Text
        recognized_text, confidence, method = self.recognize_formula(crop)
        
        # Classify alignment
        alignment_class, description = self.classify_alignment(source_text, recognized_text, bbox)        # Classify alignment
        alignment_class, description = self.classify_alignment(source_text, recognized_text, bbox)
        
        # Cross-reference with symbols.zip catalog
        matched_glyphs = []
        for glyph in self.glyph_catalog:
            if glyph.get('name') and source_text in glyph['name']:
                matched_glyphs.append(glyph['name'])
        
        result = {
            'paper': paper,
            'page': page,
            'bbox': bbox,
            'source_text': source_text,
            'classification': classification,
            'crop': crop,
            'recognized': recognized_text,
            'confidence': confidence,
            'alignment': alignment_class,
            'method': method,
            'matched_glyphs': matched_glyphs,
            'surveyed': 0
        }
        
        self.comparisons.append(result)
        self.success += 1
        
        return result
    
    def run_batch(self, paper_ids=None, max_per_paper=None):
        """
        Run comparison batch on all positional entries.
        """
        candidates = self.load_candidates(paper_id=paper_ids)
        if max_per_paper:
            candidates = candidates[:max_per_paper]
        
        logger.info(f"Processing {len(candidates)} candidates...")
        
        for i, candidate in enumerate(candidates):
            result = self.compare_candidate(candidate)
            if i % 10 == 0:
                logger.info(f"Processed {i+1}/{len(candidates)} candidates")
        
        # Save results
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / 'vision_comparison_results.jsonl'
        with open(output_file, 'w') as f:
            for c in self.comparisons:
                f.write(json.dumps(c) + '\n')
        
        logger.info(f"Completed {len(self.comparisons)} comparisons")
        logger.info(f"Successful: {self.success}, Failed: {self.failed}")
        
        return self.comparisons
    
    def save_manifest_update(self):
        """Append comparison results to unified_manifest.json."""
        if not self.comparisons:
            logger.warning("No comparisons to update")
            return
        
        # Check if 'vision_results' section exists
        if 'vision_results' not in self.manifest:
            self.manifest['vision_results'] = {
                'artifact': 'DATASETS/vision_comparison/maintenance/vision_comparison_results.jsonl',
                'run_date': 'no date',
                'glyph_catalog': 'symbols.zip (3304 glyphs)',
                'method': 'pix2text',
                'positional_entries': len(self.comparisons),
                'alignment_classes': {}
            }
        
        # Count alignment classes
        alignment_counts = {}
        for c in self.comparisons:
            cls = c['alignment']
            alignment_counts[cls] = alignment_counts.get(cls, 0) + 1
        
        # Add to manifest
        self.manifest['vision_results']['run_date'] = '2026-10-20'
        self.manifest['vision_results']['positional_entries'] = len(self.comparisons)
        self.manifest['vision_results']['alignment_classes'] = alignment_counts
        
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        logger.info(f"Updated manifest with {len(self.comparisons)} vision results")
        logger.info(f"Alignment distribution: {alignment_counts}")


def main():
    parser = argparse.ArgumentParser(description='Vision comparison pipeline')
    parser.add_argument('--paper', help='Specific paper ID to process')
    parser.add_argument('--max-per-paper', type=int, default=None, help='Max candidates per paper')
    parser.add_argument('--output', default=None, help='Output file path')
    
    args = parser.parse_args()
    
    comparer = VisionComparer()
    comparer.load_manifest()
    
    if args.paper:
        candidates = comparer.load_candidates(paper_id=args.paper)
        logger.info(f"Found {len(candidates)} candidates for {args.paper}")
    else:
        candidates = None
    
    results = comparer.run_batch(paper_ids=args.paper, max_per_paper=args.max_per_paper)
    
    # HTML canonical extraction (x-tex annotations) for WDR-RLHF test
    if args.paper == 'wasserstein':
        html_path = REPO_ROOT / 'DATASETS' / 'Wasserstein Distributionally Robust Regret Optimization for Reinforcement Learning from Human Feedback.html'
        if html_path.exists():
            comparer.extract_canonical_from_html(html_path)
    
    # Save manifest update
    comparer.save_manifest_update()
    
    # Print summary
    alignment_counts = {}
    for c in results:
        cls = c['alignment']
        alignment_counts[cls] = alignment_counts.get(cls, 0) + 1
    
    print(f"\n=== Vision Comparison Summary ===")
    print(f"Total comparisons: {len(results)}")
    print(f"Successful: {comparer.success}")
    print(f"Failed: {comparer.failed}")
    print(f"\nAlignment distribution:")
    for cls, count in sorted(alignment_counts.items(), key=lambda x: -x[1]):
        print(f"  {cls}: {count}")
    
    print(f"\nTop aligned glyphs (from symbols.zip):")
    glyph_counts = {}
    for c in results:
        for g in c.get('matched_glyphs', []):
            glyph_counts[g] = glyph_counts.get(g, 0) + 1
    for glyph, count in sorted(glyph_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {glyph}: {count}")
    
    print(f"\nSample results:")
    for c in results[:3]:
        print(f"  {c['paper']} p{c['page']}: '{c['source_text']}' -> '{c['recognized']}' [{c['alignment']}]")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
