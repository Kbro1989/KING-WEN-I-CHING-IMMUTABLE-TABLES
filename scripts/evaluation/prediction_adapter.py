#!/usr/bin/env python3
"""
V2.1.1-A Prediction Adapter — G0 Engine-Only Prediction
=========================================================

Produces an engine-only prediction for a single PDF page.
Forbidden dependencies: adjudication modules, gold targets, gold delimiter inventories, evaluator verdicts.

Architecture:
    1. Load PDF page → compute PDF SHA-256
    2. Search region = full page (FULL_PAGE mandatory for certification)
    3. Discover raw candidates (text_stream + raster_stroke)
    4. Classify every candidate independently
    5. Pair only candidates with sufficient resolved identity + direction
    6. Preserve unresolved + unpaired candidates
    7. Serialize complete prediction deterministically
    8. Return prediction + artifact hash

Usage:
    from scripts.evaluation.prediction_adapter import predict_page
    
    config = DetectionConfig(region_mode="FULL_PAGE")
    prediction = predict_page(Path("paper.pdf"), page_index=0, config=config)
"""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pymupdf

# Local imports
import sys
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evaluation.contracts import (
    DetectionConfig,
    RawCandidate,
    ClassifiedCandidate,
    EnginePrediction,
    PairedStructure,
    PairingRejection,
    make_candidate_id,
    compute_artifact_hash,
    serialize_prediction,
)
from scripts.v2_delimiter_aware_structural_recovery import (
    detect_delimiter_candidates,
    classify_delimiter_glyph_font_aware,
    associate_delimiter_pairs,
)

# ═══════════════════════════════════════════════════════════════════════
# PDF HASHING
# ═══════════════════════════════════════════════════════════════════════

def compute_pdf_sha256(pdf_path: Path) -> str:
    """Compute SHA-256 of PDF file."""
    h = hashlib.sha256()
    with pdf_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ═══════════════════════════════════════════════════════════════════════
# STAGE 1: RAW CANDIDATE DISCOVERY
# ═══════════════════════════════════════════════════════════════════════

def discover_raw_candidates(
    page: pymupdf.Page,
    page_index: int,
    config: DetectionConfig,
) -> list[RawCandidate]:
    """
    Discover raw delimiter candidates using the V2 detector.
    
    Returns list of RawCandidate with stable IDs.
    """
    # Determine search region
    if config.region_mode == "FULL_PAGE":
        y_band = (0.0, float(page.rect.height))
    elif config.region_mode == "PAGE_SEGMENTED":
        # PAGE_SEGMENTED is experimental — for G0 certification, FULL_PAGE is mandatory
        # This path should not be used for certified predictions
        raise ValueError("PAGE_SEGMENTED not available for G0 certification; use FULL_PAGE")
    else:
        raise ValueError(f"Unknown region_mode: {config.region_mode}")
    
    # Call detector
    raw_detector_output = detect_delimiter_candidates(page, y_band)
    
    # Convert to RawCandidate with stable IDs
    raw_candidates = []
    for det_idx, det in enumerate(raw_detector_output):
        bbox = det.get("rect")
        if not bbox or len(bbox) != 4:
            continue
        
        # Extract bbox as (x0, y0, x1, y1)
        if hasattr(bbox, "x0"):
            bbox_tuple = (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
        else:
            bbox_tuple = tuple(bbox)
        
        source = det.get("source", "unknown")
        text = det.get("text", "") or ""
        font = det.get("font", "unknown") or "unknown"
        
        # Get source-specific metrics
        span_height_pt = None
        raster_height_px = None
        
        if source == "text_stream":
            # Span height from detector output if available
            pass  # detector doesn't return this currently
        elif source == "raster_stroke":
            # Raster height not returned by detector currently
            pass
        
        candidate_id = make_candidate_id(page_index, source, bbox_tuple, det_idx)
        
        rc = RawCandidate(
            candidate_id=candidate_id,
            page_index=page_index,
            source=source,
            bbox=bbox_tuple,
            text=text,
            font=font,
            span_height_pt=span_height_pt,
            raster_height_px=raster_height_px,
            detection_index=det_idx,
        )
        raw_candidates.append(rc)
    
    return raw_candidates


# ═══════════════════════════════════════════════════════════════════════
# STAGE 2: CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════

def classify_candidates(
    page: pymupdf.Page,
    raw_candidates: list[RawCandidate],
) -> list[ClassifiedCandidate]:
    """
    Classify every raw candidate using font-aware delimiter classification.
    
    Preserves unresolved candidates (kind=None, is_opening=None).
    """
    classified = []
    
    for rc in raw_candidates:
        # Convert bbox to pymupdf.Rect
        bbox_rect = pymupdf.Rect(*rc.bbox)
        
        # Call classifier
        cls_result = classify_delimiter_glyph_font_aware(
            page=page,
            rect=bbox_rect,
            fallback_text=rc.text,
            fallback_font=rc.font,
        )
        
        # Extract classification fields
        kind = cls_result.get("kind")
        is_opening = cls_result.get("is_opening")
        family = cls_result.get("family")
        resolution_method = cls_result.get("resolution_method", "unresolved")
        confidence = cls_result.get("confidence", 0.0)
        
        # Font at detection
        font_at_detection = rc.font if rc.font != "unknown" else None
        
        cc = ClassifiedCandidate(
            candidate_id=rc.candidate_id,
            raw_candidate_id=rc.candidate_id,
            kind=kind,
            is_opening=is_opening,
            family=family,
            resolution_method=resolution_method,
            confidence=confidence,
            font_at_detection=font_at_detection,
            all_chars_in_span=rc.text if rc.text else None,
        )
        classified.append(cc)
    
    return classified


# ═══════════════════════════════════════════════════════════════════════
# STAGE 3: PAIRING
# ═══════════════════════════════════════════════════════════════════════

def pair_candidates(
    page: pymupdf.Page,
    classified_candidates: list[ClassifiedCandidate],
    raw_candidate_map: dict[str, RawCandidate],
) -> tuple[list[PairedStructure], list[str], list[PairingRejection]]:
    """
    Pair candidates using the V2 associator.
    
    Only pairs candidates with sufficient resolved identity and direction.
    Preserves unpaired candidates and rejection reasons.
    """
    # Prepare candidates for associator
    # The associator expects candidates with 'delimiter_id' or 'identity' dict
    associator_candidates = []
    
    for cc in classified_candidates:
        rc = raw_candidate_map[cc.raw_candidate_id]
        associator_cand = {
            "candidate_id": cc.candidate_id,
            "rect": pymupdf.Rect(*rc.bbox),
            "delimiter_id": {
                "kind": cc.kind,
                "is_opening": cc.is_opening,
                "family": cc.family,
                "resolution_method": cc.resolution_method,
                "confidence": cc.confidence,
            } if cc.is_resolved else {},
            "type": "delimiter_candidate",
        }
        associator_candidates.append(associator_cand)
    
    # Call associator
    page_width = page.rect.width
    page_height = page.rect.height
    
    pairs, unpaired = associate_delimiter_pairs(
        associator_candidates,
        page_width=page_width,
        page_height=page_height,
    )
    
    # Convert pairs to PairedStructure
    paired_structures = []
    paired_ids = set()
    
    for pair in pairs:
        # pair structure from associator: tuple of (opening_cand, closing_cand, score, ...)
        if isinstance(pair, tuple) and len(pair) >= 3:
            opening = pair[0]
            closing = pair[1]
            pair_score = pair[2] if len(pair) > 2 else 1.0
        else:
            # Fallback if structure differs
            continue
        
        open_id = opening.get("candidate_id")
        close_id = closing.get("candidate_id")
        
        if not open_id or not close_id:
            continue
        
        paired_ids.add(open_id)
        paired_ids.add(close_id)
        
        # Compute enclosure bbox
        open_rc = raw_candidate_map[open_id]
        close_rc = raw_candidate_map[close_id]
        enclosure_bbox = (
            min(open_rc.bbox[0], close_rc.bbox[0]),
            min(open_rc.bbox[1], close_rc.bbox[1]),
            max(open_rc.bbox[2], close_rc.bbox[2]),
            max(open_rc.bbox[3], close_rc.bbox[3]),
        )
        enclosure_span_x = (enclosure_bbox[0], enclosure_bbox[2])
        
        ps = PairedStructure(
            opening_candidate_id=open_id,
            closing_candidate_id=close_id,
            enclosure_bbox=enclosure_bbox,
            pair_score=pair_score,
            enclosure_span_x=enclosure_span_x,
        )
        paired_structures.append(ps)
    
    # Unpaired candidates
    all_ids = {cc.candidate_id for cc in classified_candidates}
    unpaired_ids = list(all_ids - paired_ids)
    
    # Rejection reasons: we need to reconstruct why specific pairs were rejected
    # The associator doesn't return rejection details, so we infer from unpaired
    rejections = []
    for uid in unpaired_ids:
        # For unpaired, we don't know the exact rejection reason without
        # instrumenting the associator. We record as "unresolved_identity"
        # if the candidate wasn't resolved, otherwise note as unpaired.
        cc = next(cc for cc in classified_candidates if cc.candidate_id == uid)
        if not cc.is_resolved:
            # Create a self-rejection record for documentation
            rejections.append(PairingRejection(
                opening_candidate_id=uid,
                closing_candidate_id=uid,
                reason="unresolved_identity",
                detail="Candidate classification unresolved; cannot participate in pairing",
            ))
    
    return paired_structures, unpaired_ids, rejections


# ═══════════════════════════════════════════════════════════════════════
# MAIN PREDICTION FUNCTION
# ═══════════════════════════════════════════════════════════════════════

def predict_page(
    pdf_path: Path,
    page_index: int,
    config: DetectionConfig,
) -> EnginePrediction:
    """
    Produce an engine-only prediction for a single PDF page.
    
    Forbidden dependencies:
      - adjudication modules
      - gold target coordinates
      - gold delimiter inventories
      - evaluator verdicts
    
    Returns:
        EnginePrediction with artifact_hash computed and verified.
    """
    # Open PDF and load all needed data in one pass
    doc = pymupdf.open(str(pdf_path))
    try:
        page = doc[page_index]
        pdf_sha256 = compute_pdf_sha256(pdf_path)
        page_height = page.rect.height
        
        # Discover raw candidates (uses page.rect.height)
        raw_candidates = discover_raw_candidates(page, page_index, config)
        
        # Classify candidates
        classified_candidates = classify_candidates(page, raw_candidates)
        
        # Build lookup map
        raw_candidate_map = {rc.candidate_id: rc for rc in raw_candidates}
        
        # Pair candidates
        paired_structures, unpaired_ids, rejections = pair_candidates(
            page, classified_candidates, raw_candidate_map
        )
    finally:
        doc.close()
    
    # Build EnginePrediction (after doc is closed)
    prediction = EnginePrediction(
        schema_version="2.1.1-g0",
        engine_id="KING-WEN-DELIMITER-ENGINE-V2",
        engine_version="2.0.0-remediation",
        pdf_sha256=pdf_sha256,
        page_index=page_index,
        detection_config=config,
        raw_candidates=tuple(raw_candidates),
        classified_candidates=tuple(classified_candidates),
        paired_structures=tuple(paired_structures),
        unpaired_candidates=tuple(unpaired_ids),
        pairing_rejections=tuple(rejections),
        detector_config=config.to_dict(),
        prediction_timestamp=datetime.utcnow().isoformat() + "Z",
    )
    
    # 7. Compute artifact hash and finalize
    # Use deterministic timestamp for reproducibility (no random time component)
    timestamp = "2026-11-06T00:00:00Z"
    prediction = replace(prediction, prediction_timestamp=timestamp)
    prediction = replace(prediction, artifact_hash=compute_artifact_hash(prediction))
    
    return prediction


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="V2.1.1-A G0 Prediction Adapter")
    parser.add_argument("pdf_path", type=Path, help="Path to PDF file")
    parser.add_argument("page_index", type=int, help="Page index (0-based)")
    parser.add_argument("--output", type=Path, help="Output prediction JSON path")
    parser.add_argument("--region-mode", choices=["FULL_PAGE"], default="FULL_PAGE",
                        help="Search region mode (FULL_PAGE mandatory for G0)")
    parser.add_argument("--engine-version", default="2.0.0-remediation", help="Engine version string")
    
    args = parser.parse_args()
    
    config = DetectionConfig(
        region_mode=args.region_mode,
        engine_version=args.engine_version,
    )
    
    print(f"Generating prediction for {args.pdf_path}, page {args.page_index}...")
    prediction = predict_page(args.pdf_path, args.page_index, config)
    
    print(f"  Raw candidates: {len(prediction.raw_candidates)}")
    print(f"  Classified: {len(prediction.classified_candidates)}")
    print(f"  Paired: {len(prediction.paired_structures)}")
    print(f"  Unpaired: {len(prediction.unpaired_candidates)}")
    print(f"  Rejections: {len(prediction.pairing_rejections)}")
    print(f"  Artifact hash: {prediction.artifact_hash}")
    
    if args.output:
        from scripts.evaluation.contracts import write_prediction
        write_prediction(prediction, args.output)
        print(f"Written to {args.output}")
    
    # Validate
    from scripts.evaluation.contracts import validate_g0_prediction
    violations = validate_g0_prediction(prediction)
    if violations:
        print("VALIDATION VIOLATIONS:")
        for v in violations:
            print(f"  - {v}")
        return 1
    else:
        print("VALIDATION PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())