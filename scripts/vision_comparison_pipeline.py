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
import pymupdf
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
    
    def crop_pdf_region(self, pdf_path: Path, bbox: dict, padding: int | tuple[int, int] = (3, 2), page_num: int = 0, zoom: int = 4, min_content_ratio: float = 0.02) -> np.ndarray | None:
        """Crop PDF region using bbox coordinates with adaptive zoom and content validation.
        pdf_path: path to PDF file
        bbox: {x0, y0, x1, y1} in PDF points
        padding: padding in points
        page_num: page number (0-indexed)
        zoom: zoom factor for pixmap (higher = more detail)
        min_content_ratio: minimum non-white pixel ratio to accept crop (filter empty crops)

        Returns: numpy array (image) or None if crop failed
        """
        if isinstance(padding, (tuple, list)):
            pad_x, pad_y = padding[0], padding[1]
        else:
            pad_x, pad_y = padding, padding

        doc = pymupdf.open(str(pdf_path))
        page = doc[page_num]  # use specified page
        rect = pymupdf.Rect(bbox['x0'] - pad_x, bbox['y0'] - pad_y,
                        bbox['x1'] + pad_x, bbox['y1'] + pad_y)
        try:
            # Get pixmap with adaptive zoom for better OCR quality
            # Use explicit RGB colorspace and disable alpha for deterministic 3-channel output
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(zoom, zoom),
                clip=rect,
                colorspace=pymupdf.csRGB,
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

        Stretch-vs-hallucination distinction (Gap 2):
        - stretch_recognized: single source char expanded to multi-char where the
          source char appears as a substring of the recognized text (correct stretch)
        - stretch_suspect: single source char expanded to multi-char where the
          source char does NOT appear in the recognized text (possible hallucination)
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
        
        # Check for stretch: single char -> multiple (Gap 2 distinction)
        if len(source_clean) == 1 and len(recognized_clean) > 1:
            # Stretch recognized: source char appears as substring of recognized
            if source_clean in recognized_clean:
                return 'stretch_recognized', (
                    f'stretch recognized: source="{source_clean}" found in '
                    f'recognized="{recognized_clean}" (correct stretch)'
                ), 0.8
            # Stretch suspect: source char NOT in recognized (possible hallucination)
            return 'stretch_suspect', (
                f'possible hallucination: source="{source_clean}" NOT in '
                f'recognized="{recognized_clean}"'
            ), 0.3
        
        # Check for merge suspect (multiple -> 1)
        if len(source_clean) > 1 and len(recognized_clean) == 1:
            return 'merge_suspect', f'possible merge: source="{source_clean}", recognized="{recognized_clean}"', 0.3
        
        # Check if recognized contains source or vice versa
        if source_clean in recognized_clean or recognized_clean in source_clean:
            return 'matched', f'matched: source="{source_clean}", recognized="{recognized_clean}"', 1.0
        
        # Compare structural similarity using ASCII pattern (Gap 1: size/role-aware)
        src_ascii = self.get_ascii_pattern_v2(source_clean)
        rec_ascii = self.get_ascii_pattern_v2(recognized_clean)
        
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
        Preserves original identity (backward-compatible).
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
    
    def get_ascii_pattern_v2(self, text: str) -> str | None:
        """
        Size/role-aware ASCII pattern (Gap 1 fix).
        
        Preserves distinctions between:
        - Original glyph identity (letters L, digits D)
        - Glyph size and aspect ratio (big delimiters D, big operators P)
        - Structural role (subscript S, superscript T)
        - Delimiter/operator category (small bracket B, big delimiter D, big operator P)
        
        Big delimiters: \\left(, \
ight), \\lfloor, \
floor, \\lceil, \
ceil, \\langle, \
angle, \\vert, \\Vert
        Big operators: \\sum, \\int, \\prod, \\coprod, \\bigcup, \\bigcap, \\bigoplus, \\bigotimes, \\bigwedge, \\bigvee
        """
        if not text:
            return None
        result: list[str] = []
        # Big delimiter patterns (multi-char LaTeX commands)
        big_delimiters = {'\\left', '\
ight', '\\lfloor', '\
floor', '\\lceil', '\
ceil',
                         '\\langle', '\
angle', '\\vert', '\\Vert', '\\lvert', '\
vert',
                         '\\lVert', '\
Vert', '\\ulcorner', '\\urcorner', '\\llcorner', '\\lrcorner'}
        big_operators = {'\\sum', '\\int', '\\prod', '\\coprod', '\\bigcup', '\\bigcap',
                        '\\bigoplus', '\\bigotimes', '\\bigwedge', '\\bigvee', '\\bigodot',
                        '\\bigsqcup', '\\oiint', '\\oiiint', '\\oint'}
        # Check for multi-char LaTeX commands first
        i = 0
        while i < len(text):
            # Try to match a LaTeX command (backslash + letters)
            if text[i] == '\\':
                # Find end of command
                j = i + 1
                while j < len(text) and text[j].isalpha():
                    j += 1
                cmd = text[i:j]
                if cmd in big_delimiters:
                    result.append('D')  # big delimiter
                    i = j
                    continue
                elif cmd in big_operators:
                    result.append('P')  # big operator
                    i = j
                    continue
                elif cmd in ('\\frac', '\\dfrac', '\\tfrac', '\\cfrac'):
                    result.append('F')  # fraction
                    i = j
                    continue
                elif cmd in ('\\sqrt', '\
oot'):
                    result.append('Q')  # root
                    i = j
                    continue
                elif cmd in ('\\lim', '\\limsup', '\\liminf', '\\max', '\\min', '\\sup', '\\inf'):
                    result.append('M')  # limit/max/min
                    i = j
                    continue
                elif cmd:
                    # Other LaTeX command — treat as operator
                    result.append('O')
                    i = j
                    continue
            c = text[i]
            if c.isalpha():
                result.append('L')
            elif c.isdigit():
                result.append('D')
            elif c in '[]{}()|':
                result.append('B')  # small bracket
            elif c in '^_':
                result.append('S')  # subscript/superscript
            elif c in '*/+':
                result.append('O')  # small operator
            elif c in '=<>':
                result.append('R')  # relation
            elif c == ',':
                result.append('C')  # comma
            else:
                result.append('X')  # unknown
            i += 1
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
            crop = self.crop_pdf_region(source_path, bbox, padding=(3, 2), page_num=max(0, candidate.get("page", 0) - 1))
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


# ============================================================================
# Glyph Balloon, Border Detection, Math Region Boxing, Text Boundaries
# ============================================================================

GLYPH_BALLOON_FACTOR = 9
GLYPH_BALLOON_INTERP = cv2.INTER_CUBIC


def balloon_glyph(img, factor=GLYPH_BALLOON_FACTOR):
    """Upscale a tiny Metamath glyph to ~factorx with edge smoothing (bicubic + Gaussian blur)."""
    if img is None or (isinstance(img, np.ndarray) and img.size == 0):
        return img
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return img
    new_w = w * factor
    new_h = h * factor
    ballooned = cv2.resize(img, (new_w, new_h), interpolation=GLYPH_BALLOON_INTERP)
    ksize = max(3, factor // 3 * 2 + 1)
    if ksize % 2 == 0:
        ksize += 1
    ballooned = cv2.GaussianBlur(ballooned, (ksize, ksize), 0)
    return ballooned


def balloon_glyph_to_match(crop_shape, glyph):
    """Balloon a glyph to approximately match a crop's dimensions (height-matched)."""
    if glyph is None or (isinstance(glyph, np.ndarray) and glyph.size == 0):
        return glyph
    gh, gw = glyph.shape[:2]
    ch, cw = crop_shape[:2]
    if gh == 0 or gw == 0:
        return glyph
    scale = ch / gh
    new_w = max(1, int(gw * scale))
    new_h = max(1, int(gh * scale))
    ballooned = cv2.resize(glyph, (new_w, new_h), interpolation=GLYPH_BALLOON_INTERP)
    ksize = max(3, int(scale) // 3 * 2 + 1)
    if ksize % 2 == 0:
        ksize += 1
    ballooned = cv2.GaussianBlur(ballooned, (ksize, ksize), 0)
    return ballooned


def detect_border_contamination(crop, border_px=2, density_threshold=0.15):
    """Detect whether content touches any crop border.

    Returns three distinct concepts:
    - border_contact: geometric contact (any dark pixel at border)
    - suspected_clipping: contact with density suggesting content is being cut off
    - confirmed_information_loss: requires external verification (OCR/structural), default False
    """
    if crop is None or (isinstance(crop, np.ndarray) and crop.size == 0):
        return {
            'contaminated': False,
            'border_contact': False,
            'suspected_clipping': False,
            'confirmed_information_loss': False,
            'borders': [],
            'edge_pixel_counts': {},
            'border_density': 0.0,
            'overall_density': 0.0,
        }
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop
    h, w = gray.shape[:2]
    threshold = 250
    borders = []
    counts = {}
    top_count = int(np.sum(gray[:border_px, :] < threshold))
    counts['top'] = top_count
    if top_count > 0:
        borders.append('top')
    bottom_count = int(np.sum(gray[-border_px:, :] < threshold))
    counts['bottom'] = bottom_count
    if bottom_count > 0:
        borders.append('bottom')
    left_count = int(np.sum(gray[:, :border_px] < threshold))
    counts['left'] = left_count
    if left_count > 0:
        borders.append('left')
    right_count = int(np.sum(gray[:, -border_px:] < threshold))
    counts['right'] = right_count
    if right_count > 0:
        borders.append('right')

    border_contact = len(borders) > 0

    # Suspected clipping: border contact where the border pixel density
    # is high relative to the overall image density, suggesting content
    # is being cut off rather than merely touching the edge.
    total_border_pixels = sum(counts.values())
    total_pixels = h * w
    border_density = total_border_pixels / max(total_pixels, 1)
    overall_density = float(np.sum(gray < threshold)) / max(total_pixels, 1)

    # If border density is significantly higher than overall density,
    # content is likely being clipped (concentrated at edge).
    if border_contact and overall_density > 0:
        density_ratio = border_density / overall_density
        suspected_clipping = density_ratio > 1.5 and border_density > density_threshold
    else:
        suspected_clipping = False

    # --- Bracket tracking at borders ---
    # Detect open/close bracket pairs at borders. A vertical stroke at a border
    # without its matching stroke at the opposite border indicates a clipped
    # bracket/delimiter. Stretched symbols (>50%% height) are flagged.
    min_stroke_height = max(3, h // 4)
    bracket_contacts = {'top': [], 'bottom': [], 'left': [], 'right': []}

    if left_count > 0:
        col_profile = np.sum(gray[:, :border_px] < threshold, axis=1)
        in_stroke = False
        stroke_start = 0
        for y in range(h):
            if col_profile[y] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = y
            elif col_profile[y] == 0 and in_stroke:
                in_stroke = False
                if y - stroke_start >= min_stroke_height:
                    bracket_contacts['left'].append('vertical_stroke')
        if in_stroke and h - stroke_start >= min_stroke_height:
            bracket_contacts['left'].append('vertical_stroke')

    if right_count > 0:
        col_profile = np.sum(gray[:, -border_px:] < threshold, axis=1)
        in_stroke = False
        stroke_start = 0
        for y in range(h):
            if col_profile[y] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = y
            elif col_profile[y] == 0 and in_stroke:
                in_stroke = False
                if y - stroke_start >= min_stroke_height:
                    bracket_contacts['right'].append('vertical_stroke')
        if in_stroke and h - stroke_start >= min_stroke_height:
            bracket_contacts['right'].append('vertical_stroke')

    if top_count > 0:
        row_profile = np.sum(gray[:border_px, :] < threshold, axis=0)
        in_stroke = False
        stroke_start = 0
        for x in range(w):
            if row_profile[x] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = x
            elif row_profile[x] == 0 and in_stroke:
                in_stroke = False
                if x - stroke_start >= min(w // 4, 10):
                    bracket_contacts['top'].append('horizontal_stroke')
        if in_stroke and w - stroke_start >= min(w // 4, 10):
            bracket_contacts['top'].append('horizontal_stroke')

    if bottom_count > 0:
        row_profile = np.sum(gray[-border_px:, :] < threshold, axis=0)
        in_stroke = False
        stroke_start = 0
        for x in range(w):
            if row_profile[x] > 0 and not in_stroke:
                in_stroke = True
                stroke_start = x
            elif row_profile[x] == 0 and in_stroke:
                in_stroke = False
                if x - stroke_start >= min(w // 4, 10):
                    bracket_contacts['bottom'].append('horizontal_stroke')
        if in_stroke and w - stroke_start >= min(w // 4, 10):
            bracket_contacts['bottom'].append('horizontal_stroke')

    has_left_vertical = len(bracket_contacts['left']) > 0
    has_right_vertical = len(bracket_contacts['right']) > 0

    unmatched_brackets_at_border = []
    if has_left_vertical and not has_right_vertical:
        unmatched_brackets_at_border.append('left')
    if has_right_vertical and not has_left_vertical:
        unmatched_brackets_at_border.append('right')

    stretched_at_border = []
    for border_name, col_slice in [('left', gray[:, :border_px]),
                                   ('right', gray[:, -border_px:])]:
        col_profile = np.sum(col_slice < threshold, axis=1)
        max_run = 0
        current_run = 0
        for y in range(h):
            if col_profile[y] > 0:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        if max_run > h * 0.5:
            stretched_at_border.append(border_name)

    return {
        'contaminated': border_contact,
        'border_contact': border_contact,
        'suspected_clipping': suspected_clipping,
        'confirmed_information_loss': False,
        'borders': borders,
        'edge_pixel_counts': counts,
        'border_density': round(border_density, 6),
        'overall_density': round(overall_density, 6),
        'bracket_contacts': bracket_contacts,
        'vertical_border_strokes': {
            'left': len(bracket_contacts['left']),
            'right': len(bracket_contacts['right']),
        },
        'horizontal_border_strokes': {
            'top': len(bracket_contacts['top']),
            'bottom': len(bracket_contacts['bottom']),
        },
        'unmatched_brackets_at_border': unmatched_brackets_at_border,
        'stretched_symbols_at_border': stretched_at_border,
        'has_left_vertical': has_left_vertical,
        'has_right_vertical': has_right_vertical,
    }


def expand_crop_context(pdf_page, bbox, expand_factor=1.5, zoom=4, min_content_ratio=0.01):
    """Render an expanded crop (zoom-out) around a bbox for context."""
    try:
        pad_x = (bbox['x1'] - bbox['x0']) * (expand_factor - 1) / 2
        pad_y = (bbox['y1'] - bbox['y0']) * (expand_factor - 1) / 2
        rect = pymupdf.Rect(
            bbox['x0'] - pad_x, bbox['y0'] - pad_y,
            bbox['x1'] + pad_x, bbox['y1'] + pad_y
        )
        pix = pdf_page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=rect,
                                  colorspace=pymupdf.csRGB, alpha=False)
        png_bytes = pix.tobytes('png')
        img_array = cv2.imdecode(np.frombuffer(png_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img_array is None:
            return None
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
        if np.mean(gray < 250) < min_content_ratio:
            return None
        return img_array
    except Exception:
        return None


def detect_math_regions_on_page(image_array, min_region_size=50, max_region_size=50000, white_threshold=128):
    """Detect and group math regions on a rendered page image."""
    if image_array is None or (isinstance(image_array, np.ndarray) and image_array.size == 0):
        return []
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
    h, w = gray.shape[:2]
    text_mask = (gray < white_threshold).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    closed = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)

    regions = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        rw = stats[i, cv2.CC_STAT_WIDTH]
        rh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_region_size or area > max_region_size:
            continue
        if rw < 3 or rh < 3:
            continue
        regions.append({'bbox': (int(x), int(y), int(rw), int(rh)),
                        'area': int(area),
                        'centroid': (float(centroids[i][0]), float(centroids[i][1]))})

    if not regions:
        return []
    sorted_regions = sorted(regions, key=lambda r: (r['bbox'][1], r['bbox'][0]))
    groups = []
    used = set()
    for i, r in enumerate(sorted_regions):
        if i in used:
            continue
        group = [r]
        used.add(i)
        changed = True
        while changed:
            changed = False
            for j, r2 in enumerate(sorted_regions):
                if j in used:
                    continue
                for member in group:
                    mx, my, mw, mh = member['bbox']
                    rx, ry, rw2, rh2 = r2['bbox']
                    v_overlap = not (ry + rh2 < my - 15 or my + mh < ry - 15)
                    h_proximity = abs(rx - (mx + mw)) < 20 or abs(mx - (rx + rw2)) < 20
                    if v_overlap and h_proximity:
                        group.append(r2)
                        used.add(j)
                        changed = True
                        break
        groups.append(group)

    result = []
    for group in groups:
        xs = [r['bbox'][0] for r in group]
        ys = [r['bbox'][1] for r in group]
        xe = [r['bbox'][0] + r['bbox'][2] for r in group]
        ye = [r['bbox'][1] + r['bbox'][3] for r in group]
        bbox = (min(xs), min(ys), max(xe) - min(xs), max(ye) - min(ys))
        result.append({
            'bbox': bbox,
            'region_count': len(group),
            'member_bboxes': [r['bbox'] for r in group],
            'is_complex': len(group) > 3 or bbox[3] > bbox[2] * 1.5,
            'centroid': (sum(r['centroid'][0] for r in group) / len(group),
                         sum(r['centroid'][1] for r in group) / len(group)),
        })
    return result


def detect_page_primary_white(image_array, sample_fraction=0.1):
    """Detect the primary (background) shade of white on a page.

    Samples the page image to find the dominant background color.
    Returns a dict with:
      - primary_white: the dominant white value (0-255)
      - white_std: standard deviation of white-ish pixels
      - text_threshold: derived threshold for text detection (primary_white - 127, clamped 1-254)
      - dark_threshold: derived threshold for dark content (primary_white * 0.5)
      - contrast_ratio: ratio of darkest content to background
    """
    if image_array is None or (isinstance(image_array, np.ndarray) and image_array.size == 0):
        return {"primary_white": 255, "white_std": 0, "text_threshold": 128,
                "dark_threshold": 127, "contrast_ratio": 1.0}

    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array

    # Compute histogram
    hist = np.histogram(gray, bins=256, range=(0, 256))[0]

    # Find primary white: the mode, but only considering the top 20% of pixel values
    # (to avoid picking dark text as the "white")
    top_threshold = int(np.percentile(gray, 80))
    white_pixels = gray[gray >= top_threshold]
    if len(white_pixels) == 0:
        white_pixels = gray.ravel()

    primary_white = int(np.median(white_pixels))
    # Also check the mode of the full histogram for the top values
    top_hist = hist[top_threshold:]
    if len(top_hist) > 0:
        mode_offset = np.argmax(top_hist)
        mode_val = top_threshold + mode_offset
        # Use mode if it's close to median, otherwise use median
        if abs(mode_val - primary_white) < 20:
            primary_white = mode_val

    white_std = float(np.std(white_pixels))

    # Text threshold: midpoint between primary white and 0 (black text)
    # Clamped to avoid extremes
    text_threshold = max(1, min(254, primary_white // 2))

    # Dark threshold: half of primary white
    dark_threshold = max(1, min(254, int(primary_white * 0.5)))

    # Darkest-to-primary-white ratio: darkest non-zero pixel / primary white
    # (NOT WCAG contrast ratio — that uses relative luminance: (L_light+0.05)/(L_dark+0.05))
    nonzero = gray[gray > 0]
    darkest = int(nonzero.min()) if len(nonzero) > 0 else 0
    darkest_to_primary_white_ratio = darkest / max(primary_white, 1)

    return {
        "primary_white": primary_white,
        "white_std": round(white_std, 2),
        "text_threshold": text_threshold,
        "dark_threshold": dark_threshold,
        "darkest_to_primary_white_ratio": round(darkest_to_primary_white_ratio, 4),
    }


def extract_text_boundaries(page, clip_rect=None):
    """Extract text word boundaries from a PDF page using PyMuPDF."""
    try:
        words = page.get_text("words", clip=clip_rect)
    except Exception:
        words = page.get_text("words")
    result = []
    for w in words:
        x0, y0, x1, y1, word = w[0], w[1], w[2], w[3], w[4]
        is_math = any(c in word for c in '=+-*/^_{}[]()∑∫∏∂∇∞αβγδεζηθικλμνξπρστυφχψω')
        result.append({
            'text': word,
            'bbox': (x0, y0, x1, y1),
            'font_size': (y1 - y0),
            'is_math': is_math,
        })
    return result


def detect_partial_formulas(page, clip_rect=None):
    """Detect partial formulas (inline math) in paragraphs."""
    words = extract_text_boundaries(page, clip_rect)
    if not words:
        return []
    sorted_words = sorted(words, key=lambda w: (w['bbox'][1], w['bbox'][0]))
    lines = []
    current_line = [sorted_words[0]]
    for w in sorted_words[1:]:
        if abs(w['bbox'][1] - current_line[-1]['bbox'][1]) < 5.0:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]
    if current_line:
        lines.append(current_line)
    for line in lines:
        line.sort(key=lambda w: w['bbox'][0])

    partials = []
    for line in lines:
        math_words = [w for w in line if w['is_math']]
        if 0 < len(math_words) < len(line) and len(math_words) >= 1:
            x0 = min(w['bbox'][0] for w in line)
            y0 = min(w['bbox'][1] for w in line)
            x1 = max(w['bbox'][2] for w in line)
            y1 = max(w['bbox'][3] for w in line)
            partials.append({
                'text': ' '.join(w['text'] for w in line),
                'bbox': (x0, y0, x1, y1),
                'is_inline': True,
                'math_word_count': len(math_words),
                'total_word_count': len(line),
                'math_words': [w['text'] for w in math_words],
            })
    return partials


def recognize_formula_multiscale(comparer, crop, page=None, bbox=None, zoom_levels=None):
    """Multi-scale recognition with border detection and context expansion."""
    if zoom_levels is None:
        zoom_levels = [2, 4, 8]

    border_info = detect_border_contamination(crop)

    for zoom in zoom_levels:
        text, conf, method, status = comparer.recognize_formula(crop)
        if text and status == 'nonempty':
            return text, conf, method, status, border_info, zoom

    if border_info['contaminated'] and page is not None and bbox is not None:
        expanded = expand_crop_context(page, bbox, expand_factor=1.5, zoom=4)
        if expanded is not None:
            text, conf, method, status = comparer.recognize_formula(expanded)
            if text and status == 'nonempty':
                return text, conf, method, status, border_info, 'context_expanded'

    if page is not None and bbox is not None:
        expanded = expand_crop_context(page, bbox, expand_factor=2.0, zoom=4)
        if expanded is not None:
            text, conf, method, status = comparer.recognize_formula(expanded)
            if text and status == 'nonempty':
                return text, conf, method, status, border_info, 'context_2x'

    return '', None, 'empty', 'empty', border_info, None
