#!/usr/bin/env python3
"""
V2.1.1 Evaluator Contracts — G0 Prediction Adapter
===================================================

Immutable dataclasses and deterministic serialization for the G0
engine-only prediction pipeline. No adjudication dependencies.

Architecture:
    RawCandidate  →  ClassifiedCandidate  →  EnginePrediction
         │                 │                      │
         ▼                 ▼                      ▼
    Discovery          Classification          Pairing

All records are frozen and hash-stable. Candidate IDs are derived
deterministically from source geometry and detection parameters.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any, Literal, Optional

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DetectionConfig:
    """Immutable detector configuration — included in prediction artifact for reproducibility."""
    region_mode: Literal["FULL_PAGE", "PAGE_SEGMENTED"] = "FULL_PAGE"
    raster_scale: float = 2.0
    minimum_text_span_height_pt: float = 12.0
    minimum_raster_stroke_height_px: int = 20
    # Engine version this config was validated against
    engine_version: str = "2.0.0-remediation"

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, d: dict) -> "DetectionConfig":
        return cls(**d)


# ═══════════════════════════════════════════════════════════════════════
# CANDIDATE ID GENERATION
# ═══════════════════════════════════════════════════════════════════════

def make_candidate_id(
    page_index: int,
    source: Literal["text_stream", "raster_stroke"],
    bbox: tuple[float, float, float, float],
    detection_index: int,
) -> str:
    """
    Deterministic candidate ID from geometry and source.
    
    Collision handling: if multiple candidates have identical
    (page_index, source, rounded_bbox), the detection_index
    provides deterministic ordering without relying on iteration order.
    """
    # Round bbox to 0.1 pt for stability across minor floating differences
    rounded_bbox = tuple(round(c, 1) for c in bbox)
    key_parts = [
        f"p{page_index}",
        source[0],  # 't' or 'r'
        f"{rounded_bbox[0]:.1f}",
        f"{rounded_bbox[1]:.1f}",
        f"{rounded_bbox[2]:.1f}",
        f"{rounded_bbox[3]:.1f}",
        f"i{detection_index:03d}",
    ]
    return "_".join(key_parts)


# ═══════════════════════════════════════════════════════════════════════
# STAGE 1: RAW CANDIDATE (DISCOVERY)
# ═══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RawCandidate:
    """
    Raw geometric candidate from detector, before classification.
    
    Every detector output becomes exactly one RawCandidate with a stable ID.
    Unresolved/ambiguous detections are preserved, not filtered.
    """
    candidate_id: str
    page_index: int
    source: Literal["text_stream", "raster_stroke"]
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1) in PDF points
    text: str  # raw text content (may be empty for raster_stroke)
    font: str  # font name or "none" for raster_stroke
    # Detection metadata
    span_height_pt: Optional[float] = None  # for text_stream: span bbox height
    raster_height_px: Optional[int] = None  # for raster_stroke: contour height in pixels
    detection_index: int = 0  # tiebreaker for identical geometries

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, d: dict) -> "RawCandidate":
        return cls(**d)


# ═══════════════════════════════════════════════════════════════════════
# STAGE 2: CLASSIFIED CANDIDATE (CLASSIFICATION)
# ═══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ClassifiedCandidate:
    """
    RawCandidate after font-aware delimiter classification.
    
    Unresolved candidates are preserved with kind=None, is_opening=None.
    Confidence is not a substitute for resolved identity.
    """
    candidate_id: str  # same as raw_candidate_id
    raw_candidate_id: str  # traceability to discovery stage
    kind: Optional[str]  # "parenthesis", "bracket", "brace", "norm", "vertical_bar", "unknown", None
    is_opening: Optional[bool]  # True=opening, False=closing, None=undetermined
    family: Optional[str]  # "cmex", "txexs", "latin_modern", "standard", "raster", None
    resolution_method: str  # "font_aware_cmex_mapping", "font_aware_tx_mapping", "font_aware_latin_modern_mapping", "standard_glyph_mapping", "geometric_aspect_fallback", "unresolved"
    confidence: float  # 0.0-1.0
    # Classification metadata
    font_at_detection: Optional[str] = None
    all_chars_in_span: Optional[str] = None

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, d: dict) -> "ClassifiedCandidate":
        return cls(**d)

    @property
    def is_resolved(self) -> bool:
        """True iff kind and is_opening are both resolved (not None/unknown)."""
        return (
            self.kind is not None
            and self.kind != "unknown"
            and self.is_opening is not None
        )


# ═══════════════════════════════════════════════════════════════════════
# PAIRING REJECTION REASONS
# ═══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PairingRejection:
    """Structured record of why a candidate pair was rejected."""
    opening_candidate_id: str
    closing_candidate_id: str
    reason: Literal[
        "kind_mismatch",
        "direction_mismatch",
        "no_vertical_overlap",
        "height_ratio_exceeded",
        "intervening_candidate",
        "unresolved_identity",
        "wrong_order",
    ]
    detail: str
    opening_kind: Optional[str] = None
    closing_kind: Optional[str] = None
    vertical_overlap_ratio: Optional[float] = None
    height_ratio: Optional[float] = None

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, d: dict) -> "PairingRejection":
        return cls(**d)


# ═══════════════════════════════════════════════════════════════════════
# STAGE 3: ENGINE PREDICTION (PAIRING OUTPUT)
# ═══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PairedStructure:
    """Successfully paired opening + closing delimiters forming a structural unit."""
    opening_candidate_id: str
    closing_candidate_id: str
    enclosure_bbox: tuple[float, float, float, float]  # union of both delimiter bboxes
    pair_score: float
    enclosure_span_x: tuple[float, float]  # (x0, x1) of combined span

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, d: dict) -> "PairedStructure":
        return cls(**d)


@dataclass(frozen=True)
class EnginePrediction:
    """
    Complete engine-only prediction artifact for one PDF page.
    
    Immutable, hash-stable, contains full evidence trace from discovery
    through classification to pairing. No adjudication data.
    """
    schema_version: str = "2.1.1-g0"
    engine_id: str = "KING-WEN-DELIMITER-ENGINE-V2"
    engine_version: str = "2.0.0-remediation"
    pdf_sha256: str = ""
    page_index: int = 0
    detection_config: DetectionConfig = field(default_factory=DetectionConfig)
    # Stage outputs
    raw_candidates: tuple[RawCandidate, ...] = field(default_factory=tuple)
    classified_candidates: tuple[ClassifiedCandidate, ...] = field(default_factory=tuple)
    paired_structures: tuple[PairedStructure, ...] = field(default_factory=tuple)
    unpaired_candidates: tuple[str, ...] = field(default_factory=tuple)  # candidate_ids
    pairing_rejections: tuple[PairingRejection, ...] = field(default_factory=tuple)
    # Metadata
    detector_config: dict = field(default_factory=dict)
    prediction_timestamp: str = ""
    # Artifact integrity
    artifact_hash: str = ""  # SHA-256 of canonical serialization

    def to_dict(self) -> dict:
        """Convert to dict for serialization (excluding artifact_hash)."""
        d = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "artifact_hash"}
        # Convert tuples to lists for JSON
        for k, v in d.items():
            if isinstance(v, tuple):
                d[k] = [item.to_dict() if hasattr(item, "to_dict") else item for item in v]
            elif hasattr(v, "to_dict"):
                d[k] = v.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "EnginePrediction":
        """Reconstruct from dict (including nested objects)."""
        # Convert lists back to tuples of objects
        raw = tuple(RawCandidate.from_dict(x) for x in d.get("raw_candidates", []))
        classified = tuple(ClassifiedCandidate.from_dict(x) for x in d.get("classified_candidates", []))
        paired = tuple(PairedStructure.from_dict(x) for x in d.get("paired_structures", []))
        rejections = tuple(PairingRejection.from_dict(x) for x in d.get("pairing_rejections", []))
        config = DetectionConfig.from_dict(d.get("detection_config", {}))
        
        return cls(
            schema_version=d.get("schema_version", "2.1.1-g0"),
            engine_id=d.get("engine_id", "KING-WEN-DELIMITER-ENGINE-V2"),
            engine_version=d.get("engine_version", "2.0.0-remediation"),
            pdf_sha256=d.get("pdf_sha256", ""),
            page_index=d.get("page_index", 0),
            detection_config=config,
            raw_candidates=raw,
            classified_candidates=classified,
            paired_structures=paired,
            unpaired_candidates=tuple(d.get("unpaired_candidates", [])),
            pairing_rejections=rejections,
            detector_config=d.get("detector_config", {}),
            prediction_timestamp=d.get("prediction_timestamp", ""),
            artifact_hash=d.get("artifact_hash", ""),
        )


# ═══════════════════════════════════════════════════════════════════════
# DETERMINISTIC SERIALIZATION & HASHING
# ═══════════════════════════════════════════════════════════════════════

def canonical_json(obj: Any) -> str:
    """
    Canonical JSON serialization for hash stability.
    
    Rules:
    - Sort all dict keys
    - No whitespace
    - Fixed separators
    - Unicode escaped (ensure_ascii=True)
    """
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=True)


def compute_artifact_hash(prediction: EnginePrediction) -> str:
    """Compute SHA-256 of canonical serialization."""
    d = prediction.to_dict()
    # Exclude artifact_hash itself from the hash computation
    canonical = canonical_json(d)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def serialize_prediction(prediction: EnginePrediction) -> str:
    """Serialize prediction to canonical JSON string (includes artifact_hash)."""
    d = prediction.to_dict()
    if prediction.artifact_hash:
        d["artifact_hash"] = prediction.artifact_hash
    return canonical_json(d)


def deserialize_prediction(json_str: str) -> EnginePrediction:
    """Deserialize from canonical JSON string."""
    d = json.loads(json_str)
    pred = EnginePrediction.from_dict(d)
    # Verify hash if present
    if "artifact_hash" in d:
        computed = compute_artifact_hash(pred)
        if computed != d["artifact_hash"]:
            raise ValueError(f"Artifact hash mismatch: computed {computed}, stored {d['artifact_hash']}")
    return pred


# ═══════════════════════════════════════════════════════════════════════
# FILE I/O
# ═══════════════════════════════════════════════════════════════════════

def write_prediction(prediction: EnginePrediction, path: Path) -> None:
    """Write prediction with verified artifact hash."""
    pred_with_hash = replace(prediction, artifact_hash=compute_artifact_hash(prediction))
    path.write_text(serialize_prediction(pred_with_hash), encoding="utf-8")


def read_prediction(path: Path) -> EnginePrediction:
    """Read prediction and verify artifact hash."""
    return deserialize_prediction(path.read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════════════
# VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════════════════

def validate_g0_prediction(prediction: EnginePrediction) -> list[str]:
    """
    Validate that a prediction satisfies G0 contract requirements.
    
    Returns list of violations (empty = valid).
    """
    violations = []
    
    # Schema version
    if not prediction.schema_version.startswith("2.1.1-g0"):
        violations.append(f"Invalid schema_version: {prediction.schema_version}")
    
    # PDF hash present
    if not prediction.pdf_sha256:
        violations.append("Missing pdf_sha256")
    elif len(prediction.pdf_sha256) != 64:
        violations.append(f"Invalid pdf_sha256 length: {len(prediction.pdf_sha256)}")
    
    # Artifact hash verified
    if prediction.artifact_hash:
        computed = compute_artifact_hash(prediction)
        if computed != prediction.artifact_hash:
            violations.append(f"Artifact hash mismatch: {computed} != {prediction.artifact_hash}")
    
    # All raw candidates have classified counterparts
    raw_ids = {rc.candidate_id for rc in prediction.raw_candidates}
    classified_ids = {cc.candidate_id for cc in prediction.classified_candidates}
    missing = raw_ids - classified_ids
    if missing:
        violations.append(f"Raw candidates missing classification: {missing}")
    
    # All paired structures reference valid candidates
    all_candidate_ids = raw_ids
    for ps in prediction.paired_structures:
        if ps.opening_candidate_id not in all_candidate_ids:
            violations.append(f"Paired structure references unknown opening: {ps.opening_candidate_id}")
        if ps.closing_candidate_id not in all_candidate_ids:
            violations.append(f"Paired structure references unknown closing: {ps.closing_candidate_id}")
    
    # Unpaired candidates must exist in raw
    for uid in prediction.unpaired_candidates:
        if uid not in all_candidate_ids:
            violations.append(f"Unpaired candidate not in raw: {uid}")
    
    # Pairing rejections must reference valid candidates
    for pr in prediction.pairing_rejections:
        if pr.opening_candidate_id not in all_candidate_ids:
            violations.append(f"Rejection references unknown opening: {pr.opening_candidate_id}")
        if pr.closing_candidate_id not in all_candidate_ids:
            violations.append(f"Rejection references unknown closing: {pr.closing_candidate_id}")
    
    return violations


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python contracts.py <validate|hash> <prediction.json>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    path = Path(sys.argv[2])
    
    if cmd == "validate":
        pred = read_prediction(path)
        violations = validate_g0_prediction(pred)
        if violations:
            print("VALIDATION FAILED:")
            for v in violations:
                print(f"  - {v}")
            sys.exit(1)
        else:
            print("VALIDATION PASSED")
            print(f"  Schema: {pred.schema_version}")
            print(f"  Engine: {pred.engine_id} {pred.engine_version}")
            print(f"  PDF: {pred.pdf_sha256[:16]}...")
            print(f"  Page: {pred.page_index}")
            print(f"  Raw candidates: {len(pred.raw_candidates)}")
            print(f"  Classified: {len(pred.classified_candidates)}")
            print(f"  Paired: {len(pred.paired_structures)}")
            print(f"  Unpaired: {len(pred.unpaired_candidates)}")
            print(f"  Rejections: {len(pred.pairing_rejections)}")
            print(f"  Hash: {pred.artifact_hash[:16]}...")
    
    elif cmd == "hash":
        pred = read_prediction(path)
        print(compute_artifact_hash(pred))
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)