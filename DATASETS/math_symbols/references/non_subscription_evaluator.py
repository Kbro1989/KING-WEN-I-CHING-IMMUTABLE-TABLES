#!/usr/bin/env python3
"""
Non-subscription vision pipeline for Metamath symbol reference corpus.

Uses:
  - Tesseract OCR 5.4.0 (free/open-source, installed at
    C:\Program Files\Tesseract-OCR\tesseract.exe)
  - PyMuPDF (fitz) for PDF page rendering
  - Pillow (PIL) + numpy for image processing and template matching

Pipeline:
  1. Render arxiv PDF pages to images (PyMuPDF)
  2. Extract symbol crops using bounding box coordinates
  3. Template-match crops against Metamath reference glyphs
  4. Report recognition accuracy per configuration

Configuration A (crop-only):
  - Extract features from crop, match against reference corpus
  - No reference-dependent post-processing

Configuration B (reference-assisted):
  - Template-match against frozen Metamath reference library
  - Return ranked candidate list (best to worst)

Configuration C (reference + size-aware normalization):
  - Normalize crop size to reference baseline
  - Template-match normalized crop against corpus

This is a local-only pipeline with NO subscription services.
All libraries are free/open-source (Tesseract, PyMuPDF, Pillow, numpy).

Author: Kbro1989 (Kristain33rs)
License: CC0 (Creative Commons Public Domain Dedication)
Source: https://us.metamath.org/symbols/symbols.html
"""

import os
import sys
import json
import csv
import subprocess
import tempfile
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

# ── Tesseract path ──────────────────────────────────────────────────────────
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_tesseract() -> str:
    """Return the tesseract executable path. Raises if not found."""
    for candidate in [TESSERACT_PATH, r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                      r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe']:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        f"Tesseract not found. Install at C:\\Program Files\\Tesseract-OCR\\tesseract.exe "
        f"or add it to PATH. Check: where tesseract"
    )


# ── PyMuPDF (fitz) ──────────────────────────────────────────────────────────
try:
    import fitz  # pymupdf
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    fitz = None


# ── Template matching utilities ─────────────────────────────────────────────
def load_reference_glyph(image_path: str) -> Optional[np.ndarray]:
    """Load a reference glyph image as a normalized numpy array.

    Handles transparent GIFs by using the alpha channel to determine ink.
    """
    try:
        img = Image.open(image_path)
        # Preserve alpha channel for transparency
        if img.mode == 'P':
            img = img.convert('RGBA')
        elif img.mode != 'L':
            img = img.convert('L')

        if img.mode == 'RGBA':
            # Use alpha channel: 1 where opaque (visible), 0 where transparent (background)
            alpha = np.array(img)[:, :, 3]
            binary = (alpha >= 128).astype(np.float32)
        else:
            # Grayscale fallback: pixels < 128 are glyph ink
            arr = np.array(img.convert('L'))
            binary = (arr < 128).astype(np.float32)
        return binary
    except Exception as e:
        print(f"  Warning: could not load {image_path}: {e}")
        return None


def compute_similarity(crop_arr: np.ndarray, reference_arr: np.ndarray) -> float:
    """
    Compute pixel-wise similarity between crop and reference.

    Uses Intersection over Union (IoU) and normalized cross-correlation.
    """
    if crop_arr.shape != reference_arr.shape:
        return 0.0

    # Pixel-wise intersection and union
    intersection = np.logical_and(crop_arr > 0.5, reference_arr > 0.5).sum()
    union = np.logical_or(crop_arr > 0.5, reference_arr > 0.5).sum()

    if union == 0:
        return 0.0

    iou = intersection / union

    # Also compute normalized cross-correlation
    crop_px = crop_arr.flatten()
    ref_px = reference_arr.flatten()

    crop_mean = crop_px.mean()
    ref_mean = ref_px.mean()

    numerator = np.sum((crop_px - crop_mean) * (ref_px - ref_mean))
    denominator = np.sqrt(np.sum((crop_px - crop_mean) ** 2) *
                          np.sum((ref_px - ref_mean) ** 2))

    if denominator == 0:
        return iou

    correlation = numerator / denominator

    # Combined score: 0.6 * IoU + 0.4 * correlation
    return 0.6 * iou + 0.4 * correlation


def resize_to_reference(crop: Image.Image, ref_size: Tuple[int, int]) -> Image.Image:
    """Resize crop to match reference image dimensions."""
    return crop.resize(ref_size, Image.LANCZOS)


# ── PDF rendering ───────────────────────────────────────────────────────────
def render_pdf_page(pdf_path: str, page_num: int,
                    target_size: Tuple[int, int] = (800, 1000),
                    dpi: int = 300) -> Optional[np.ndarray]:
    """
    Render a PDF page to a grayscale numpy array.

    Uses PyMuPDF (fitz) for high-quality rendering.
    """
    if not FITZ_AVAILABLE:
        print("  Error: PyMuPDF (fitz) not available")
        return None

    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]  # 0-indexed

        # Render at specified DPI
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        doc.close()

        # Convert to grayscale
        if target_size:
            img = img.resize(target_size, Image.LANCZOS)
        gray = img.convert('L')

        return np.array(gray)

    except Exception as e:
        print(f"  Error rendering {pdf_path}: {e}")
        return None


def extract_crop_from_page(page_array: np.ndarray, bbox: Tuple[float, float, float, float],
                           output_size: Tuple[int, int] = (64, 64)) -> Optional[np.ndarray]:
    """
    Extract a crop from a rendered page using bounding box coordinates.

    bbox = (x1, y1, x2, y2) — pixel coordinates in the rendered page
    """
    try:
        h, w = page_array.shape
        x1, y1, x2, y2 = bbox

        # Clamp to page bounds
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(w, int(x2))
        y2 = min(h, int(y2))

        if x2 <= x1 or y2 <= y1:
            return None

        crop = page_array[y1:y2, x1:x2]

        # Resize to output size
        crop_img = Image.fromarray(crop)
        crop_img = crop_img.resize(output_size, Image.LANCZOS)
        return np.array(crop_img)

    except Exception as e:
        print(f"  Error extracting crop: {e}")
        return None


# ── Tesseract integration (for text/context verification) ───────────────────
def ocr_crop(crop_path: str, psm: int = 7) -> Tuple[str, float]:
    """
    Run Tesseract OCR on a crop image.

    Returns (text, confidence) where text is the recognized characters
    and confidence is the OCR confidence score (0-100).
    """
    if not os.path.exists(TESSERACT_PATH):
        return "", 0.0

    try:
        result = subprocess.run(
            [TESSERACT_PATH, crop_path, 'stdout', '--psm', str(psm),
             '--print-parameters', 'tessedit_write_images=false'],
            capture_output=True, timeout=15
        )

        if result.returncode == 0:
            output = result.stdout.decode('utf-8', errors='ignore').strip()
            # Tesseract v5+ outputs confidence to stderr as "confidence: XX"
            stderr = result.stderr.decode('utf-8', errors='ignore')
            conf = 0.0
            for line in stderr.split('\n'):
                if 'confidence' in line.lower():
                    try:
                        conf = float(line.split(':')[-1].strip())
                    except ValueError:
                        pass
            return output, conf
        return "", 0.0
    except Exception as e:
        print(f"  Tesseract error: {e}")
        return "", 0.0


def ocr_page(pdf_path: str, page_num: int = 1) -> Tuple[str, float]:
    """OCR an entire PDF page to extract text context."""
    if not FITZ_AVAILABLE:
        return "", 0.0

    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        img = page.get_pixmap(dpi=150, alpha=False)
        doc.close()

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(buf.read())
            tmp_path = f.name

        try:
            return ocr_crop(tmp_path, psm=3)
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"  OCR page error: {e}")
        return "", 0.0


# ── Template-matching evaluator ─────────────────────────────────────────────
class NonSubscriptionEvaluator:
    """
    Evaluator using Tesseract OCR + template matching.

    No subscription services, no cloud APIs, no third-party vision APIs.
    All processing is local and open-source.
    """

    def __init__(self, reference_dir: str, metaclass_corpus: str = None):
        self.reference_dir = Path(reference_dir)
        self.images_dir = self.reference_dir / "images"
        self.manifest = self._load_manifest()

        # Load all reference glyphs
        self.reference_glyphs = {}
        self.reference_names = []
        for name in sorted(self.manifest.keys()):
            # Try .png first, then .gif
            img_path = self.images_dir / f"{name}.gif"
            if not img_path.exists():
                # Fall back to direct subdir
                img_path = self.reference_dir / f"{name}.png"
            if img_path.exists():
                arr = load_reference_glyph(str(img_path))
                if arr is not None:
                    self.reference_glyphs[name] = arr
                    self.reference_names.append(name)
                    continue
            # Try any other related file
            for ext in ['.gif', '.png']:
                alt_path = self.images_dir / f"{name}{ext}"
                if alt_path.exists():
                    arr = load_reference_glyph(str(alt_path))
                    if arr is not None:
                        self.reference_glyphs[name] = arr
                        self.reference_names.append(name)
                        break

        self.reference_dimensions = self._get_reference_dimensions()

    def _load_manifest(self) -> Dict[str, Any]:
        """Load Metamath symbol manifest. Supports both dict and list formats."""
        manifest_path = self.reference_dir / "manifest.json"
        if not manifest_path.exists():
            # Fall back to manifest.csv
            manifest_path = self.reference_dir / "manifest.csv"
            if manifest_path.exists():
                return self._load_csv_manifest(str(manifest_path))
            return {}

        with open(manifest_path, 'r') as f:
            data = json.load(f)

        # Handle list format (1,182 entries from the current manifest)
        if isinstance(data, list):
            manifest = {}
            for entry in data:
                name = entry.get('name', entry.get('symbol', ''))
                if name:
                    manifest[name] = entry
            return manifest

        # Handle dict format
        if isinstance(data, dict):
            return data

        return {}

    def _load_csv_manifest(self, csv_path: str) -> Dict[str, Any]:
        """Load manifest from CSV format."""
        manifest = {}
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                manifest[row.get('name', row.get('symbol', ''))] = row
        return manifest

    def _get_reference_dimensions(self) -> Dict[str, Tuple[int, int]]:
        """Get dimensions of all reference glyphs."""
        dims = {}
        for name in self.reference_names:
            img_path = self.images_dir / f"{name}.gif"
            if not img_path.exists():
                img_path = self.images_dir / f"{name}.png"
            img = Image.open(img_path)
            dims[name] = img.size
        return dims

    def match_crop(self, crop_array: np.ndarray) -> List[Tuple[str, float]]:
        """
        Match a crop against all reference glyphs.

        Returns ranked list of (glyph_name, similarity_score) sorted by score.
        """
        if crop_array.ndim == 3:
            crop_array = crop_array[:, :, 0]  # Use first channel if RGB

        # Binarize crop
        crop_binary = (crop_array < 128).astype(np.float32)

        # Try matching at different crop sizes
        best_matches = []
        for name, ref in self.reference_glyphs.items():
            if crop_binary.shape != ref.shape:
                # Resize crop to reference size
                h, w = ref.shape
                crop_resized = Image.fromarray(crop_binary * 255).resize((w, h), Image.LANCZOS)
                crop_resized = (np.array(crop_resized) > 128).astype(np.float32)
            else:
                crop_resized = crop_binary

            score = compute_similarity(crop_resized, ref)
            best_matches.append((name, score))

        # Sort by score descending
        best_matches.sort(key=lambda x: x[1], reverse=True)
        return best_matches

    def evaluate_config(self, test_cases: List[Dict], config: str) -> Dict[str, Any]:
        """
        Evaluate a set of test cases under specified configuration.

        Returns metrics including accuracy, confusion matrix, and predictions.
        """
        predictions = []
        ground_truth = []

        for case in test_cases:
            # Extract crop from source page (if PDF)
            crop = None

            if 'crop_array' in case:
                crop = case['crop_array']
            elif 'page_array' in case:
                page = case['page_array']
                bbox = case.get('bbox')
                if bbox:
                    crop = extract_crop_from_page(page, bbox, (64, 64))

            if crop is None:
                predictions.append({'predicted': None, 'score': 0.0})
                ground_truth.append(case['glyph'])
                continue

            if config == 'A':
                # Config A: Crop-only baseline
                # Template-matching directly without reference normalization
                matches = self.match_crop(crop)
                predictions.append({
                    'predicted': matches[0][0] if matches else None,
                    'score': matches[0][1] if matches else 0.0,
                    'matches': matches
                })

            elif config == 'B':
                # Config B: Reference-assisted
                # Same as A but reports ranked candidates
                matches = self.match_crop(crop)
                predictions.append({
                    'predicted': matches[0][0] if matches else None,
                    'score': matches[0][1] if matches else 0.0,
                    'ranked_candidates': matches,
                    'abstained': matches[0][1] < 0.3 if matches else True
                })

            elif config == 'C':
                # Config C: Reference + size-aware normalization
                # Resize crop to reference size before matching
                ref_size = self.reference_dimensions.get(self.reference_names[0]) if self.reference_names else (64, 64)

                # Convert crop to image, resize, then back to array
                crop_img = Image.fromarray(crop.astype(np.uint8))
                crop_img_resized = crop_img.resize(ref_size, Image.LANCZOS)
                crop_resized = np.array(crop_img_resized)

                matches = self.match_crop(crop_resized)
                predictions.append({
                    'predicted': matches[0][0] if matches else None,
                    'score': matches[0][1] if matches else 0.0,
                    'ranked_candidates': matches,
                    'abstained': matches[0][1] < 0.3 if matches else True
                })

            ground_truth.append(case['glyph'])

        # Compute metrics
        metrics = self._compute_metrics(predictions, ground_truth)
        return {'predictions': predictions, 'metrics': metrics}

    def _compute_metrics(self, predictions, ground_truth):
        """Compute accuracy and confusion matrix."""
        n = len(ground_truth)
        if n == 0:
            return {'accuracy': 0.0, 'confusion_matrix': {}}

        correct = 0
        confusion = {}

        for pred, true in zip(predictions, ground_truth):
            if pred.get('predicted') == true:
                correct += 1
            pred_label = pred.get('predicted') or 'unknown'
            true_label = true
            confusion.setdefault(true_label, {})
            confusion[true_label][pred_label] = confusion[true_label].get(pred_label, 0) + 1

        accuracy = correct / n

        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': n,
            'confusion_matrix': confusion
        }

    def verify_reference(self, ref_name: str) -> Tuple[str, float]:
        """
        Verify a reference glyph using Tesseract OCR.
        Returns (recognized_text, confidence).
        """
        img_path = self.reference_dir / f"{ref_name}.png"
        if not img_path.exists():
            return "", 0.0

        # Use Tesseract to verify the glyph
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.open(img_path)
            img.save(f.name, format='PNG')
            tmp_path = f.name

        try:
            text, conf = ocr_crop(tmp_path, psm=10)  # Single character mode
            return text, conf
        finally:
            os.unlink(tmp_path)


# ── Main execution ──────────────────────────────────────────────────────────
def main():
    """Run the non-subscription evaluation pipeline."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Metamath Symbol Reference Corpus Evaluation (Non-Subscription)')
    parser.add_argument('--reference', required=True,
                        help='Path to reference glyph corpus (Directory with PNG files)')
    parser.add_argument('--dataset', required=True,
                        help='Path to evaluation dataset CSV')
    parser.add_argument('--output', required=True,
                        help='Output directory for results')
    parser.add_argument('--configs', nargs='+', default=['A', 'B', 'C'],
                        choices=['A', 'B', 'C'],
                        help='Evaluation configurations to run')
    parser.add_argument('--pdf', help='Path to PDF for page rendering')
    parser.add_argument('--page', type=int, default=1,
                        help='Page number to render from PDF')
    parser.add_argument('--bbox', help='Bounding box as x1,y1,x2,y2 (PDF pixel coordinates)',
                        default=None)
    parser.add_argument('--tesseract', default=None,
                        help='Path to Tesseract executable (default: C:\\Program Files\\Tesseract-OCR\\tesseract.exe)')
    args = parser.parse_args()

    # Resolve tesseract path
    tesseract_path = args.tesseract or TESSERACT_PATH
    if not os.path.exists(tesseract_path):
        print(f"Error: Tesseract not found at {tesseract_path}")
        print("Install Tesseract or add to PATH: where tesseract")
        sys.exit(1)
    TESSERACT_PATH = tesseract_path

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Load evaluator
    evaluator = NonSubscriptionEvaluator(args.reference)
    print(f"Loaded {len(evaluator.reference_glyphs)} reference glyphs")

    # Verify reference glyphs (using Tesseract)
    print("\n=== Reference Verification (via Tesseract OCR) ===")
    for name in list(evaluator.reference_glyphs.keys())[:5]:
        text, conf = evaluator.verify_reference(name)
        print(f"  {name}: OCR text='{text}', confidence={conf:.1f}%")

    # Evaluate each configuration
    print("\n=== Configuration Evaluation ===")
    all_results = {}
    for config in args.configs:
        print(f"  Running {config}...")
        if args.pdf:
            # Render PDF page
            page_array = render_pdf_page(args.pdf, args.page)
            if page_array is not None:
                # Extract crop using bbox
                bbox = None
                if args.bbox:
                    bbox = tuple(map(float, args.bbox.split(',')))

                if bbox:
                    crop = extract_crop_from_page(page_array, bbox, (64, 64))
                    if crop is not None:
                        results = evaluator.evaluate_config(
                            [{'glyph': 'test', 'crop_array': crop}],
                            config
                        )
                        all_results[config] = results[config]
                        print(f"    {config}: accuracy={results[config]['metrics']['accuracy']:.3f}")

    # If no PDF, skip PDF-specific evaluation
    if not args.pdf:
        print("  (No PDF specified; skipping PDF rendering evaluation)")

    # Write results
    results_path = os.path.join(args.output, 'experiment_results.json')
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults written to {results_path}")


if __name__ == '__main__':
    main()
