"""Unit tests for Chroma 2D Geometry and Perimeter Contact Gate (Steps E & F).

Verifies:
  1. Chroma detects fraction vinculum in PIAA-004 (Eq 4) at y≈259.46 pt.
  2. Emits standardized L3 evidence sidecar with structure_type="fraction".
  3. Reconciles with vector rule [201.345, 259.459, 206.326, 259.459].
  4. Physical perimeter contact gate enforces border_touch_1px == 0 and Gate D4 >= 2.0 pt.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pymupdf
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from chroma_geometry_adapter import (
    detect_chroma_vinculums,
    verify_perimeter_clearance_gate_d4,
)
from safe_adaptive_cropping_adapter import safe_adaptive_crop_pdf_region

PDF_PATH = (
    "C:/Users/krist/Desktop/zotero/learning-corpus/efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)


@pytest.fixture(scope="module")
def piaa_page_5():
    doc = pymupdf.open(PDF_PATH)
    return doc[4]


def test_chroma_eq4_vinculum_detection(piaa_page_5):
    """Verify Chroma detects fraction vinculum in Eq 4 (PIAA-004) and fuses with vector rule."""
    eq4_bbox = [90.0, 245.0, 280.0, 275.0]
    records = detect_chroma_vinculums(
        page=piaa_page_5,
        page_index=4,
        target_bbox_pt=eq4_bbox,
        zoom=4,
        pdf_path=PDF_PATH,
    )

    assert len(records) >= 1

    # Find the specific fraction vinculum around x=201, y=259
    vinculum_records = [
        r for r in records
        if abs(r["bbox_pdf_pt"][0] - 201.3) <= 4.0 and abs(r["bbox_pdf_pt"][1] - 259.4) <= 2.0
    ]
    assert len(vinculum_records) >= 1
    vr = vinculum_records[0]

    assert vr["layer"] == "L3"
    assert vr["observation"]["structure_type"] == "fraction"
    assert vr["observation"]["matched_vector_rule"] is not None
    # Confidence should be elevated to 0.95 due to vector match fusion
    assert vr["confidence"] >= 0.90
    assert vr["status"] == "VERIFIED_BY_GATE"


def test_perimeter_contact_gate_d4_pass():
    """Clean crop with padding must pass Gate D4 clearance and zero border contact."""
    bbox = [102.93, 100.44, 278.0, 112.31]  # PIAA-002
    crop_res = safe_adaptive_crop_pdf_region(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_pdf_pt=bbox,
        padding=(3.0, 2.0),
        zoom=4,
    )
    assert crop_res["status"] == "SUCCESS"
    crop_path = crop_res["crop_path"]

    gate_res = verify_perimeter_clearance_gate_d4(crop_path, zoom=4, gate_d4_threshold_pt=2.0)
    assert gate_res["border_touch_1px"] == 0
    assert gate_res["clearance_pt"] >= 2.0
    assert gate_res["gate_d4_passed"] is True
    assert gate_res["status"] == "PASSED"
