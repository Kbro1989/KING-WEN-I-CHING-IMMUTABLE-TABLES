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

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        self.glyph_catalog = self.manifest.get('symbols_zip_catalog', {}).get('catalog', [])
        logger.info(f"Loaded {len(self.glyph_catalog)} symbols.zip glyphs")
        
    def load_candidates(self, paper_id: str | None = None, source_file: Path | None = None) -> list[dict]:
        """Load positional candidates from the candidates_*.json files."""
        candidates: list[dict] = []
        if paper_id:
            pattern = REPO_ROOT / 'DATASETS' / f'candidates_{paper_id}.json'
            if pattern.exists():
                with open(pattern, 'r', encoding='utf-8') as f:
                    candidates = json.load(f)
                logger.info(f"Loaded {len(candidates)} candidates for {paper_id} from {pattern}")
        elif source_file:
            if source_file.exists():
                with open(source_file, 'r', encoding='utf-8') as f:
                    candidates = json.load(f)
                logger.info(f"Loaded {len(candidates)} candidates from {source_file}")
        else:
            for f in sorted(REPO_ROOT.glob('DATASETS/candidates_*.json')):
                with open(f, 'r', encoding='utf-8') as fh:
                    candidates.extend(json.load(fh))
        return candidates
    
    def crop_pdf_region(self, pdf_path: Path, bbox: dict, padding: int = 2, page_num: int = 0, zoom: int = 4, min_content_ratio: float = 0.02) -> np.ndarray | None:
        """Crop PDF region using bbox coordinates with adaptive zoom and content validation.
        pdf_path: path to PDF file
        bbox: {x0, y0, x1, y1} in PDF points
        padding: padding in points
        page_num: page number (0-indexed)
        zoom: zoom factor for pixmap (higher = more detail)
        min_content_ratio: minimum non-white pixel ratio to accept crop (filter empty crops)

        Returns: numpy array (image) or None if crop failed
        """
        doc = fitz.open(str(pdf_path))
        page = doc[page_num]  # use specified page
        rect = fitz.Rect(bbox['x0'] - padding, bbox['y0'] - padding,
                        bbox['x1'] + padding, bbox['y1'] + padding)
        try:
            # Get pixmap with adaptive zoom for better OCR quality
            # Use explicit RGB colorspace and disable alpha for deterministic 3-channel output
            pix = page.get_pixmap(
                matrix=fitz.Matrix(zoom, zoom),
                clip=rect,
                colorspace=fitz.csRGB,
                alpha=False
            )
            # Convert pixmap to PNG bytes and decode with OpenCV
            # This avoids manual channel/stride calculations that can corrupt images
            import cv2
            png_bytes = pix.tobytes('png')
            img_array = cv2.imdecode(
                np.frombuffer(png_bytes, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )
            if img_array is None:
                logger.error(f"cv2.imdecode failed for pixmap width={pix.width}, height={pix.height}")
                doc.close()
                return None
            # Verify dimensions match expected crop
            if img_array.shape[:2] != (pix.height, pix.width):
                logger.warning(f"Non-square/rectangular crop: {img_array.shape} (expected {pix.height}x{pix.width})")
            # Validate content: check non-white pixel ratio
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
            non_white_ratio = np.mean(gray < 250)
            if non_white_ratio < min_content_ratio:
                logger.warning(f"Low content ratio {non_white_ratio:.3f} (zoom={zoom})")
                doc.close()
                return None
            doc.close()
            logger.info(f"Cropped, shape={img_array.shape}, zoom={zoom}, content={non_white_ratio:.3f}")
            return img_array
        except Exception as e:
            logger.error(f"Crop failed: {e}")
            import traceback
            traceback.print_exc()
            doc.close()
            return None
    
    def recognize_formula(self, crop: np.ndarray | None) -> tuple[str | None, float | None, str, str]:
        """
        Run Pix2Text on the crop and get reconstructed LaTeX.
        Returns: (reconstructed_text, recognition_confidence, method, recognition_status)
        """
        if crop is None:
            return None, None, 'crop_failed', 'error'
        
        try:
            import tempfile
            tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmpfile_path = tmpfile.name
            tmpfile.close()
            
            if not cv2.imwrite(tmpfile_path, crop):
                if os.path.exists(tmpfile_path):
                    os.remove(tmpfile_path)
                return None, None, 'crop_write_failed', 'error'
            
            result = self.pix2text.recognize_formula(tmpfile_path)
            
            if os.path.exists(tmpfile_path):
                os.remove(tmpfile_path)
            
            if isinstance(result, str):
                text = result.strip()
                status = 'nonempty' if text else 'empty'
                # Pix2Text MFR returns a raw LaTeX string with no confidence score.
                # Never assign 1.0 as a proxy for confidence; record None (null in JSON).
                return text, None, 'pix2text' if text else 'empty', status
            elif isinstance(result, dict):
                text = (result.get('latex') or result.get('text') or result.get('expression') or '').strip()
                raw_conf = result.get('confidence') if 'confidence' in result else result.get('confidence_score')
                conf = float(raw_conf) if raw_conf is not None else None
                status = 'nonempty' if text else 'empty'
                return text, conf, 'pix2text' if text else 'empty', status
            elif result is not None:
                text = str(result).strip()
                status = 'nonempty' if text else 'empty'
                return text, None, 'pix2text' if text else 'empty', status
            else:
                return '', None, 'empty', 'empty'
        except Exception as e:
            if 'tmpfile_path' in locals() and os.path.exists(tmpfile_path):
                try:
                    os.remove(tmpfile_path)
                except OSError:
                    pass
            logger.warning(f'Recognition failed: {e}')
            return None, None, 'recognition_error', 'error'
    
    def classify_alignment(self, source_text, recognized_text, source_bbox):
        """
        Classify alignment failure type with ASCII structural comparison.
        Returns: (alignment_class, description, score)
        """
        if source_text is None:
            return 'unknown', 'source null', 0.0
        
        source_clean = source_text.strip()
        recognized_clean = recognized_text.strip() if recognized_text else ''
        
        # Check for empty recognition
        if not recognized_clean:
            return 'empty_recognition', 'recognition produced no text', 0.0
        
        # Check for single char / bracket cases
        if len(source_clean) == 1 and len(recognized_clean) == 1:
            if source_clean in '[]{}()|' or recognized_clean in '[]{}()|':
                return 'divider_bracket', f'single char: source={source_clean}, recognized={recognized_clean}', 1.0
        
        # Check for stretch suspect (1 char -> multiple)
        if len(source_clean) == 1 and len(recognized_clean) > 1:
            return 'stretch_suspect', f'possible stretch: source="{source_clean}", recognized="{recognized_clean}"', 0.3
        
        # Check for merge suspect (multiple -> 1)
        if len(source_clean) > 1 and len(recognized_clean) == 1:
            return 'merge_suspect', f'possible merge: source="{source_clean}", recognized="{recognized_clean}"', 0.3
        
        # Check if recognized contains source or vice versa
        if source_clean in recognized_clean or recognized_clean in source_clean:
            return 'matched', f'matched: source="{source_clean}", recognized="{recognized_clean}"', 1.0
        
        # Compare structural similarity using ASCII pattern
        src_ascii = self.get_ascii_pattern(source_clean)
        rec_ascii = self.get_ascii_pattern(recognized_clean)
        
        if src_ascii and rec_ascii:
            structural_score = self.compare_structural_similarity(src_ascii, rec_ascii)
            if structural_score >= 0.7:
                return 'partial_match', f'structurally similar: src="{source_clean}", rec="{recognized_clean}"', structural_score
        
        # Check for image region (character level)
        if source_clean == '' or source_bbox:
            return 'image_region', 'source region appears to be an image, not text', 0.1
        
        # Default mismatch
        return 'mismatch', f'diff: source="{source_clean}", recognized="{recognized_clean}"', 0.0
    
    def get_ascii_pattern(self, text: str) -> str | None:
        """
        Convert text to ASCII pattern for structural comparison.
        Maps characters to classes: letters, digits, operators, delimiters, etc.
        """
        if not text:
            return None
        result: list[str] = []
        for c in text:
            if c.isalpha():
                result.append('L')
            elif c.isdigit():
                result.append('D')
            elif c in '[]{}()|':
                result.append('B')
            elif c in '^_':
                result.append('S')
            elif c in '*/+':
                result.append('O')
            elif c in '=<>':
                result.append('R')
            elif c == ',':
                result.append('C')
            else:
                result.append('X')
        return ''.join(result)
    
    def compare_structural_similarity(self, src_pattern, rec_pattern):
        """
        Compare two ASCII patterns with tolerance for minor differences.
        Returns: similarity score (0-1)
        """
        if not src_pattern or not rec_pattern:
            return 0.0
        
        # Normalize both patterns
        src_norm = src_pattern
        rec_norm = rec_pattern
        
        # Basic containment check with len tolerance
        if len(src_norm) == len(rec_norm):
            matches = sum(1 for a, b in zip(src_norm, rec_norm) if a == b)
            return matches / len(src_norm)
        elif len(src_norm) == 1 and len(rec_norm) > 1:
            # Single char expanded
            return 0.2 if rec_norm[0] == src_norm[0] else 0.0
        elif len(rec_norm) == 1 and len(src_norm) > 1:
            # Multiple collapsed to single
            return 0.2 if src_norm[0] == rec_norm[0] else 0.0
        
        return 0.0
    
    def compare_candidate(self, candidate: dict) -> dict:
        """
        Compare a single candidate against the symbols.zip catalog.
        Returns: comparison dict
        """
        paper: str = candidate.get('paper_id', 'unknown')
        page: int = candidate.get('page', 0)
        bbox: dict = candidate.get('bbox', {})
        source_text: str = candidate.get('line_text', '')
        classification: str = candidate.get('classification', 'unknown')
        
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
                        logger.info(f"Searching in {search_path}")
                        for f in search_path.glob('**/*' + paper + '*'):
                            if f.is_file() and f.suffix.lower() in ['.pdf', '.html']:
                                logger.info(f"Found: {f}")
                                source_path = f
                                break
                        if source_path.exists():
                            logger.info(f"Using source: {source_path}")
                            break
        
        if not source_path.exists():
            logger.warning(f"Source not found: {source_path}")
            res = {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop_shape': None,
                'recognized': '',
                'confidence': None,
                'recognition_confidence': None,
                'recognition_status': 'error',
                'alignment': 'source_missing',
                'semantic_validation': 'unverified',
                'method': 'source_missing',
                'matched_glyphs': [],
                'surveyed': 0
            }
            self.failed += 1
            self.comparisons.append(res)
            return res
        
        # Crop PDF region using bbox coordinates (PDF points)
        crop = None
        try:
            crop = self.crop_pdf_region(source_path, bbox, padding=15, page_num=max(0, candidate.get("page", 0) - 1))
            logger.info(f"Crop result: {crop is not None}, type: {type(crop)}, shape: {getattr(crop, 'shape', None)}")
        except Exception as e:
            logger.warning(f"Crop exception: {e}")
            import traceback
            traceback.print_exc()
            res = {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop_shape': None,
                'recognized': '',
                'confidence': None,
                'recognition_confidence': None,
                'recognition_status': 'error',
                'alignment': 'crop_failed',
                'semantic_validation': 'unverified',
                'method': 'crop_failed',
                'matched_glyphs': [],
                'surveyed': 0
            }
            self.failed += 1
            self.comparisons.append(res)
            return res
        
        if crop is None:
            logger.warning(f"Crop is None for {source_text}")
            res = {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop_shape': None,
                'recognized': '',
                'confidence': None,
                'recognition_confidence': None,
                'recognition_status': 'error',
                'alignment': 'crop_failed',
                'semantic_validation': 'unverified',
                'method': 'crop_failed',
                'matched_glyphs': [],
                'surveyed': 0
            }
            self.failed += 1
            self.comparisons.append(res)
            return res
        
        # Run Pix2Text directly on crop array
        recognized_text, confidence, method, recognition_status = self.recognize_formula(crop)
        
        # Classify alignment with ASCII structural comparison
        alignment_class, description, score = self.classify_alignment(source_text, recognized_text, bbox)
        
        # Cross-reference with symbols.zip catalog
        matched_glyphs = []
        for glyph in self.glyph_catalog:
            if glyph.get('name') and source_text in glyph['name']:
                matched_glyphs.append(glyph['name'])
        
        # Determine semantic validation
        # Distinguish between isolated formula extraction and images with embedded prose text
        import re
        is_embedded_prose = False
        if recognized_text:
            if re.search(r'\\(?:mathrm|text|sf)\{[a-zA-Z\s~]{3,}\}', recognized_text) or re.search(r'[a-zA-Z]{4,}', re.sub(r'\\[a-zA-Z]+', '', recognized_text)):
                is_embedded_prose = True

        if alignment_class == 'image_region':
            semantic_validation = 'embedded_in_prose' if is_embedded_prose else 'image_region'
        elif alignment_class == 'matched':
            semantic_validation = 'valid'
        elif not recognized_text:
            semantic_validation = 'empty'
        else:
            semantic_validation = 'unverified'

        result = {
            'paper': paper,
            'page': page,
            'bbox': bbox,
            'source_text': source_text,
            'classification': classification,
            'crop_shape': list(crop.shape) if crop is not None else None,
            'recognized': recognized_text,
            'confidence': confidence,
            'recognition_confidence': confidence,
            'recognition_status': recognition_status,
            'alignment': alignment_class,
            'semantic_validation': semantic_validation,
            'method': method,
            'matched_glyphs': matched_glyphs,
            'surveyed': 0
        }
        
        if recognized_text and method == 'pix2text':
            self.success += 1
        else:
            self.failed += 1
        
        self.comparisons.append(result)
        return result
    
    def run_batch(self, paper_ids: str | None = None, max_per_paper: int | None = None) -> list[dict]:
        """
        Run comparison batch on all positional entries.
        """
        candidates: list[dict] = self.load_candidates(paper_id=paper_ids)
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
        with open(output_file, 'w', encoding='utf-8') as f:
            for c in self.comparisons:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        
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
        
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        
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
    print(f"Candidates processed: {len(results)}")
    print(f"Successfully recognized (non-empty): {comparer.success}")
    print(f"Failed / empty recognition: {comparer.failed}")
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
