#!/usr/bin/env python3
"""Math Recovery Puzzle Box — Evidence Role Classifier

Every artifact in the recovery pipeline is classified by ROLE, not filename.
Role is determined by structural signals, not by what the file is called.

    CAPTURE    — real extraction of the source paper; carries non-fabricable
                 values (SHA-256 hashes, page coordinates, OCR crops).
    MIRROR     — translates observed external behavior into a local interface
                 (e.g., html parser maps DOM MathML to ExprNode).
    SIMULATION — models external state transitions to exercise local logic
                 (e.g., delimiter-pairing test harness over synthetic fixtures).
    SYNTHETIC  — deliberate abstraction/test values (counting sequences,
                 designed failure cases).

Classification rule:
    1. First check: does this artifact carry a hash of real source?
       If YES -> CAPTURE.
    2. Next: does it wrap real paper content with a clean local interface?
       If YES -> MIRROR.
    3. Next: does it work with synthetic inputs to test local logic?
       If YES -> SIMULATION.
    4. Otherwise -> SYNTHETIC.

Never assign evidentiary weight from the filename alone.
"""

# Evidence role taxonomy (applied to targeted_ocr pipeline and arXiv HTML pipeline)
EVIDENCE_ROLES = {
    "DATASETS/benchmark_pdfs/*.pdf": "CAPTURE — real source PDFs, SHA-256 recorded",
    "DATASETS/PDF_FIDELITY_RENDERINGS/**/*.png": "CAPTURE — rendered crop images",
    "DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/*.json": "MIRROR — OCR extraction mirror",
    "scripts/targeted_depth_ocr.py": "MIRROR — translates crop geometry to crop JSON",
    "scripts/pix2text_harvest.py": "MIRROR — maps OCR engine output to candidate records",
    "scripts/adjudicate_candidates_v2.py": "SIMULATION — classifies candidates in isolation",
    "scripts/adjudicate_targets.py": "SIMULATION — adjudicates UNADJUDICATED records",
    "scripts/audit_candidate_crops.py": "SIMULATION — machine-checked manifest validation",
    "scripts/delimiter_aware_structural_recovery.py": "SIMULATION — structural recovery engine",
    "scripts/bridge_math_diagram_extractor.py": "MIRROR — interfaces extractor to King Wen engine",
}
