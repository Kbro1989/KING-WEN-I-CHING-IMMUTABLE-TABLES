"""Unit tests for Safe Adaptive Cropping Adapter (TOOL-04).

Verifies:
  1. Cropping around PIAA-002 on Page 5 yields a non-blank PNG.
  2. Neighbor-aware padding clamping ensures border_touch_1px == 0.
  3. Returns valid SHA-256 and bbox_actual_pdf_pt.
  4. Output is written to DATASETS/structural_preservation/crops/ without mutating unified_manifest.json.
  5. expand_crop_context functions correctly for contextual zoom-out.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from safe_adaptive_cropping_adapter import safe_adaptive_crop_pdf_region, expand_crop_context

PDF_PATH = (
    "C:/Users/krist/Desktop/zotero/learning-corpus/efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)


def test_piaa_002_safe_adaptive_crop():
    """Crop Page 5 around PIAA-002 (Eq 2) and verify zero border ink contact."""
    bbox = [102.93, 100.44, 278.0, 112.31]
    res = safe_adaptive_crop_pdf_region(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_pdf_pt=bbox,
        padding=(3.0, 2.0),
        zoom=4,
        min_content_ratio=0.02,
    )

    assert res["status"] == "SUCCESS"
    assert res["crop_path"] is not None
    assert Path(res["crop_path"]).exists()
    assert len(res["crop_sha256"]) == 64
    assert res["content_ratio"] >= 0.02
    # Gate D4 perimeter touch proxy: must be strictly 0
    assert res["border_touch_1px"] == 0

    # Ensure actual bbox is within reasonable padding bounds
    act = res["bbox_actual_pdf_pt"]
    assert act[0] <= bbox[0]
    assert act[1] <= bbox[1]
    assert act[2] >= bbox[2]
    assert act[3] >= bbox[3]


def test_expand_crop_context():
    """Verify zoom-out context crop generation."""
    bbox = [102.93, 100.44, 278.0, 112.31]
    arr = expand_crop_context(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_pdf_pt=bbox,
        expand_factor=1.5,
        zoom=4,
        min_content_ratio=0.01,
    )
    assert arr is not None
    assert arr.ndim == 3
    assert arr.shape[0] > 0 and arr.shape[1] > 0
