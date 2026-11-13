"""
Math Recovery Puzzle Box — Evidence Evidence Layer.

Directory structure:
    audit_evidence/
    ├── per_paper/               # paper_id/ (one subdir per paper)
    │   ├── <paper_id>/
    │   │   ├── crop_detection/   # targeted_depth_ocr.py output (PNGs)
    │   │   ├── pix2text_harvest/ # pix2text_candidates.jsonl
    │   │   ├── adjudication/      # adjudication_report.jsonl
    │   │   ├── adjudication_targets/ # adjudication_targets*.jsonl
    │   │   ├── target_ocr_results/ # targeted_ocr_results.json
    │   │   ├── structural_recovery/ # delimiter_aware_structural_recovery.py output
    │   │   ├── bridge_to_kingwen/ # bridge_math_diagram_extractor.py output
    │   │   └── evidence_manifest.json  # per-paper evidence ledger
    ├── cross_paper/
    │   ├── batch_manifest.json   # batch-level evidence aggregation
    │   └── delimiter_identity_audit.json
    └── documentation/
        └── evidence_role_classifier.md

Usage: read scripts/math_recovery/audit_evidence_classifier.py for the
evidence role classifier (capture / mirror / simulation / synthetic).
"""

# Module is read-only; evidence artifacts are written by their producing scripts.
