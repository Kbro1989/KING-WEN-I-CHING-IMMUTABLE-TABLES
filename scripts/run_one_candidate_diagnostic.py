#!/usr/bin/env python3
"""One-candidate diagnostic test with full boundary trace."""

import json
import os
import sys
import tempfile
import logging
from pathlib import Path

REPO_ROOT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')
os.chdir(REPO_ROOT)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(REPO_ROOT / 'cache' / 'one_candidate_diagnostic.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('one_candidate_diagnostic')

import fitz  # PyMuPDF 1.28.2
import cv2  # OpenCV 5.0.0
import numpy as np
from PIL import Image as PILImage

from pix2text import Pix2Text

MANIFEST_PATH = REPO_ROOT / 'DATASETS' / 'unified_manifest.json'
PDF_DIR = REPO_ROOT / 'DATASETS' / 'benchmark_pdfs'
DIAG_OUTPUT = REPO_ROOT / 'cache' / 'candidate_1907_04931_diag.json'
DIAG_OUTPUT.parent.mkdir(parents=True, exist_ok=True)


def trace_boundary(name, data, extra_info=None):
    logger.debug(f"=== {name} ===")
    if isinstance(data, np.ndarray):
        logger.debug(f"  Array: shape={data.shape}, dtype={data.dtype}, size={data.size}")
    elif isinstance(data, (str, Path)):
        p = Path(data)
        logger.debug(f"  Path: {data}, exists={p.exists()}, size={p.stat().st_size if p.exists() else 'N/A'}")
    else:
        logger.debug(f"  Value: {data}")
    if extra_info:
        logger.debug(f"  Extra: {extra_info}")
    logger.debug(f"=== END {name} ===")


class OneCandidateDiagnostic:
    def __init__(self):
        self.pix2text = Pix2Text()
        self.result = None

    def run_one_candidate(self, candidate):
        paper = candidate.get('paper_id', 'unknown')
        page = candidate.get('page', 0)
        bbox = candidate.get('bbox', {})
        source_text = candidate.get('line_text', '')
        classification = candidate.get('classification', 'unknown')

        logger.info(f"\n{'='*60}")
        logger.info(f"DIAGNOSTIC: paper={paper}, page={page}, source={source_text}")
        logger.info(f"{'='*60}")

        source_path = PDF_DIR / f"{paper}.pdf"
        if not source_path.exists():
            html_path = REPO_ROOT / 'DATASETS' / f"{paper}.html"
            if html_path.exists():
                source_path = html_path
            else:
                for search_path in [REPO_ROOT, Path("C:/Users/krist/Desktop/zotero"), Path("C:/Users/krist/Desktop/zotero/learning-corpus")]:
                    if search_path.exists():
                        for f in search_path.glob('**/*' + paper + '*'):
                            if f.is_file() and f.suffix.lower() in ['.pdf', '.html']:
                                source_path = f
                                break
                        if source_path.exists():
                            break

        if not source_path.exists():
            logger.error(f"Source not found: {source_path}")
            return None

        logger.info(f"Using source: {source_path}")

        # Step 1: Crop with full trace
        crop = self.crop_pdf_region_debug(source_path, bbox, padding=15, page_num=page - 1)

        if crop is None:
            logger.error("Crop failed!")
            return None

        # Step 2: Recognize with trace
        recognized_text, confidence, method = self.recognize_formula_with_trace(crop)

        self.result = {
            'paper': paper, 'page': page, 'bbox': bbox,
            'source_text': source_text, 'classification': classification,
            'crop': crop.tolist() if crop is not None else None,
            'recognized': recognized_text, 'confidence': confidence,
            'method': method,
            'diagnostic_passed': crop is not None and recognized_text is not None,
            'crop_shape': crop.shape if crop is not None else None
        }

        logger.info(f"DIAGNOSTIC RESULT: crop={crop is not None}, recognized={recognized_text}, "
                   f"confidence={confidence}, method={method}")
        return self.result

    def crop_pdf_region_debug(self, pdf_path, bbox, padding=15, page_num=0, zoom=4):
        doc = fitz.open(str(pdf_path))
        page = doc[page_num]
        rect = fitz.Rect(bbox['x0'] - padding, bbox['y0'] - padding,
                        bbox['x1'] + padding, bbox['y1'] + padding)
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
            trace_boundary("PyMuPDF pixmap", pix, {
                'width': pix.width, 'height': pix.height, 'n': pix.n,
                'stride': pix.stride, 'samples_len': len(pix.samples),
                'expected_samples': pix.height * pix.stride
            })
            if len(pix.samples) != pix.height * pix.stride:
                logger.error(f"CONSISTENCY FAILURE: len(samples)={len(pix.samples)} != height*stride={pix.height * pix.stride}")
                return None

            img_array = np.frombuffer(pix.samples, dtype=np.uint8).copy()
            trace_boundary("NumPy array from pixmap", img_array)

            if pix.height == 0 or pix.width == 0:
                logger.error(f"ZERO-DIMENSION PIXMAP")
                doc.close(); return None

            num_channels = pix.n
            trace_boundary("Channel count check", {
                'pix.n': num_channels,
                'expected_size_from_stride': pix.height * pix.stride,
                'buffer_size': img_array.size
            })

            try:
                img_array = img_array.reshape(pix.height, pix.width, num_channels)
                trace_boundary("Reshaped numpy array", img_array)
            except ValueError as e:
                logger.error(f"RESHAPE FAILED: {e}")
                doc.close(); return None

            tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmpfile_path = tmpfile.name
            tmpfile.close()
            trace_boundary("Temp file created", tmpfile_path)

            cv2.imwrite(tmpfile_path, img_array)
            trace_boundary("cv2.imwrite", None)

            with PILImage.open(tmpfile_path) as img_pil:
                trace_boundary("Pillow opened temp PNG", img_pil, {
                    'format': img_pil.format, 'mode': img_pil.mode, 'size': img_pil.size
                })
                img_pil.load()
                trace_boundary("Pillow decoded", None)

            img = cv2.imread(tmpfile_path, cv2.IMREAD_COLOR)
            trace_boundary("cv2.imread", img)

            os.remove(tmpfile_path)
            trace_boundary("Temp file deleted", None)

            if img is None:
                logger.error("cv2.imread returned None!"); doc.close(); return None

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            non_white_ratio = np.mean(gray < 250)
            logger.info(f"Crop content ratio: {non_white_ratio:.3f}")

            doc.close()
            return img
        except Exception as e:
            logger.error(f"Crop failed: {e}")
            import traceback; traceback.print_exc()
            doc.close(); return None

    def recognize_formula_with_trace(self, crop):
        if crop is None:
            logger.warning("Crop is None!"); return None, 0.0, 'crop_none'

        tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        tmpfile_path = tmpfile.name
        tmpfile.close()
        trace_boundary("recognize_formula: temp file created", tmpfile_path)

        cv2.imwrite(tmpfile_path, crop)
        trace_boundary("recognize_formula: cv2.imwrite", None)

        with PILImage.open(tmpfile_path) as img_check:
            logger.info(f"Recognizer input - PIL opened: format={img_check.format}, mode={img_check.mode}, size={img_check.size}")

        logger.info("Calling Pix2Text.recognize_formula()...")
        try:
            result = self.pix2text.recognize_formula(tmpfile_path)
            trace_boundary("recognize_formula returned", result)
        except Exception as e:
            logger.error(f"recognize_formula EXCEPTION: {e}")
            import traceback; traceback.print_exc()
            os.remove(tmpfile_path)
            return None, 0.0, 'recognition_exception'

        os.remove(tmpfile_path)
        trace_boundary("Temp file deleted", None)

        # Handle actual Pix2Text return type (str or dict)
        if isinstance(result, str):
            # Direct LaTeX string from Pix2Text
            return result, 0.0, 'pix2text'
        elif isinstance(result, dict):
            # Dictionary result - use the first available text field
            text = result.get('latex') or result.get('text') or result.get('expression') or ''
            if text:
                return text, result.get('confidence', result.get('confidence_score', 0.0)), 'pix2text'
            else:
                return str(result), 0.0, 'pix2text'
        else:
            return str(result), 0.0, type(result).__name__


def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    candidates = []
    candidates_file = REPO_ROOT / 'DATASETS' / 'candidates_1907.04931.json'
    if candidates_file.exists():
        candidates = json.load(open(candidates_file))
    else:
        for f in REPO_ROOT.glob('DATASETS/candidates_*.json'):
            candidates = json.load(open(f)); break

    if not candidates:
        logger.error("No candidates found!"); return 1

    logger.info(f"Loaded {len(candidates)} candidates")
    diag = OneCandidateDiagnostic()
    candidate = candidates[0]
    result = diag.run_one_candidate(candidate)

    with open(DIAG_OUTPUT, 'w') as f:
        json.dump(result, f, indent=2)

    logger.info(f"Diagnostic output saved to: {DIAG_OUTPUT}")
    return 0 if result and result.get('diagnostic_passed') else 1


if __name__ == '__main__':
    sys.exit(main())
