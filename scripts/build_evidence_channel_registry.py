"""Generate V2.3 Multi-Stage Evidence Channel Registry.

Defines the six-layer architecture, evidence provenance sidecar schema,
and source-level capability & reuse matrix for all 10 legacy visual and
mathematical tools in the repository.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
OUTPUT_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "v2_3_evidence_channel_registry.json"


def build_registry() -> dict:
    registry = {
        "registry_identifier": "V2_3-EVIDENCE-CHANNEL-REGISTRY",
        "schema_version": "1.0.0",
        "created_at": "2026-11-15T18:15:00Z",
        "architecture_layers": {
            "L0_source_acquisition": {
                "name": "Source Acquisition",
                "scope": "Raw PDF character streams, font metrics, vector drawings, source HTML/MathML",
                "producers": ["PyMuPDF rawdict", "PyMuPDF get_drawings", "arxiv_html_parser.py"]
            },
            "L1_physical_discovery": {
                "name": "Physical Candidate Discovery",
                "scope": "Unconditioned proposal of mathematical candidate regions (no gold coordinates)",
                "producers": ["targeted_math_detector.py", "targeted_depth_ocr.py", "g0_unconstrained_discovery.py"]
            },
            "L2_visual_evidence_acquisition": {
                "name": "Visual Evidence Acquisition",
                "scope": "Deterministic high-zoom cropping, context expansion, and full-page targeting overlays",
                "producers": ["vision_comparison_pipeline.py", "cross_reference_pipeline.py", "render_fullpage_depth.py"]
            },
            "L3_independent_physical_cross_verification": {
                "name": "Independent Physical Cross-Verification",
                "scope": "Multi-substrate evidence: 2D geometry, raster matching, OCR, ink perimeter contact",
                "producers": ["chroma_visual_reader.py", "physical_symbol_matcher.py", "pix2text_harvest.py", "audit_rendered_png_producers.py", "experiments_crop_isolation.py"]
            },
            "L4_structural_reconstruction": {
                "name": "Structural Mathematical Reconstruction",
                "scope": "Spatial grammar, typed AST synthesis, MathML generation, delimiter/fraction recovery",
                "producers": ["v2_3_multimodal_math_recovery.py", "mathml_parser.py", "math_ast_integration.py"]
            },
            "L5_evidence_adjudication": {
                "name": "Evidence Adjudication & Gate D4 Verification",
                "scope": "Source correspondence, conflict detection, physical clearance verification (g_min >= 2.0 pt), explicit abstention",
                "producers": ["v2_3_glyph_evidence_adjudicator.py", "audit_candidate_fixtures_p5.py", "association_bridge.py"]
            }
        },
        "evidence_provenance_sidecar_schema": {
            "description": "Standardized schema emitted by intermediate evidence producers to prevent unstructured string passing",
            "required_fields": {
                "evidence_id": "Unique string observation identifier (e.g., OBS-PIAA-001-CHROMA-001)",
                "producer": "Script name and function path (e.g., scripts/chroma_visual_reader.py:detect_structures)",
                "producer_version": "Git commit hash or file SHA-256",
                "layer": "Architecture layer (L0..L5)",
                "input_sha256": "Cryptographic hash of the source PDF, image, or parent evidence artifact",
                "page_id": "Physical 0-based page index and 1-based page number",
                "bbox_pdf_pt": "Physical coordinates [x0, y0, x1, y1] in PDF points (72 DPI, top-left origin)",
                "crop_sha256": "SHA-256 of the cropped raster image (null if non-raster evidence)",
                "observation": "Raw observed output structure (dictionary, AST, or text), never pre-adjudicated truth",
                "confidence": "Producer-specific numerical confidence in [0.0, 1.0]",
                "dependencies": "List of upstream evidence_ids that conditioned this observation",
                "status": "One of: OBSERVED, UNRESOLVED_CONFLICT, REJECTED_BY_FILTER, VERIFIED_BY_GATE"
            }
        },
        "tools_inventory": [
            {
                "tool_id": "TOOL-01",
                "script_path": "scripts/targeted_math_detector.py",
                "rank": 1,
                "assigned_layer": "L1_physical_discovery",
                "role": "Independent physical candidate proposal (observation-only)",
                "integration_disposition": "ADAPTER_REQUIRED",
                "independent_evidence": "Detects font size anomalies, math punctuation, and aspect ratios from rawdict without reference bounding boxes",
                "shared_failure_modes": ["Shares PyMuPDF font extraction substrate with L0", "Heuristic aspect thresholds may miss square symbols"],
                "input_interface": "PDF path, page range (1-based)",
                "output_interface": "Component candidate bboxes in PDF points with aspect ratio and reasons",
                "adapter_needed": "Normalize output dictionary to standardized evidence sidecar schema; remove hardcoded TARGET_LATEX_NAMES bias",
                "validating_tests": ["tests/test_g0_unconstrained_discovery.py"],
                "verification_status": "IMPLEMENTED_REQUIRES_ADAPTER"
            },
            {
                "tool_id": "TOOL-02",
                "script_path": "scripts/chroma_visual_reader.py",
                "rank": 2,
                "assigned_layer": "L3_independent_physical_cross_verification",
                "role": "Physical 2D mathematical structure detection (fractions, tall delimiters, cases)",
                "integration_disposition": "DIRECT_REUSE",
                "independent_evidence": "K-means color clustering + 2D connected component analysis extracts vinculums and braces independently of OCR",
                "shared_failure_modes": ["Raster thresholding can merge closely touching horizontal lines", "Synthetic calibration may shift on real fonts"],
                "input_interface": "PDF page pixmap, page index, zoom factor",
                "output_interface": "VisualMathStructure objects with typed ExprNode children",
                "adapter_needed": "Light wrapper to map VisualMathStructure into V2.3 spatial grammar graph",
                "validating_tests": ["tests/test_chroma_visual_reader.py (4 passed)"],
                "verification_status": "UNIT_TESTED"
            },
            {
                "tool_id": "TOOL-03",
                "script_path": "scripts/targeted_depth_ocr.py",
                "rank": 3,
                "assigned_layer": "L1_physical_discovery / L2_visual_evidence_acquisition",
                "role": "High-zoom (8x) detection and cropping of stretched and wide components",
                "integration_disposition": "ADAPTER_REQUIRED",
                "independent_evidence": "Connected-component row projection profiling isolates multi-line and stretched delimiters",
                "shared_failure_modes": ["Assumes fixed 4x rendering scale for coordinate conversion", "Hardcoded Windows paths in legacy script"],
                "input_interface": "Paper ID, page number, high_zoom=8",
                "output_interface": "8x cropped PNGs and OCR results",
                "adapter_needed": "Abstract out file paths and make coordinate transform scale-aware (dynamic matrix)",
                "validating_tests": ["tests/test_crop_isolation_regression.py"],
                "verification_status": "IMPLEMENTED_REQUIRES_ADAPTER"
            },
            {
                "tool_id": "TOOL-04",
                "script_path": "scripts/vision_comparison_pipeline.py",
                "rank": 4,
                "assigned_layer": "L2_visual_evidence_acquisition",
                "role": "Controlled adaptive cropping, context expansion, and non-white content validation",
                "integration_disposition": "DIRECT_REUSE",
                "independent_evidence": "Pure image-level crop extraction with RGB colorspace enforcement and min_content_ratio validation",
                "shared_failure_modes": ["Requires prior bounding box; cannot propose candidates independently"],
                "input_interface": "pdf_path, bbox dict, padding, zoom=4, min_content_ratio=0.02",
                "output_interface": "3-channel numpy RGB array without channel/stride corruption",
                "adapter_needed": "Isolate crop_pdf_region and expand_crop_context from legacy unified_manifest.json mutation",
                "validating_tests": ["tests/test_expand_crop_context.py (7 passed)"],
                "verification_status": "UNIT_TESTED"
            },
            {
                "tool_id": "TOOL-05",
                "script_path": "scripts/cross_reference_pipeline.py",
                "rank": 5,
                "assigned_layer": "L2_visual_evidence_acquisition / L5_evidence_adjudication",
                "role": "Multi-category visual page overlay drawing and cross-reference reconciliation",
                "integration_disposition": "DIRECT_REUSE",
                "independent_evidence": "PyMuPDF vector overlay drawing (page.draw_rect) color-coding math, text, boundary touches, and prose",
                "shared_failure_modes": ["Requires prior region proposals and text boundary records"],
                "input_interface": "paper_id, page_num, output_dir, cross_refs, vision_rec, ZOOM=4",
                "output_interface": "Annotated full-page PNG (annotated_{paper_id}_p{page_num}.png)",
                "adapter_needed": "None for generate_annotated_page; can be called directly as an evaluation and diagnostic tool",
                "validating_tests": ["tests/test_structural_evidence_graph.py (21 passed)"],
                "verification_status": "UNIT_TESTED"
            },
            {
                "tool_id": "TOOL-06",
                "script_path": "scripts/pix2text_harvest.py",
                "rank": 6,
                "assigned_layer": "L3_independent_physical_cross_verification",
                "role": "Independent OCR candidate channel (historical baseline)",
                "integration_disposition": "DIRECT_REUSE",
                "independent_evidence": "Visual neural recognition of formulas from cropped raster patches",
                "shared_failure_modes": ["Susceptible to hallucinations on out-of-distribution math fonts", "Shares crop boundary targeting errors"],
                "input_interface": "Raw crop PNGs or page images",
                "output_interface": "Recognized LaTeX strings with element IDs and bboxes",
                "adapter_needed": "Enforce strict provenance: raw OCR must never be promoted to verified status without independent physical validation",
                "validating_tests": ["tests/test_pix2text_harvest.py"],
                "verification_status": "IMPLEMENTED"
            },
            {
                "tool_id": "TOOL-07",
                "script_path": "scripts/audit_rendered_png_producers.py",
                "rank": 7,
                "assigned_layer": "L3_independent_physical_cross_verification / L5_evidence_adjudication",
                "role": "Crop boundary verification, 1px/2px outer border touch analysis, ink margin calculation",
                "integration_disposition": "DIRECT_REUSE",
                "independent_evidence": "Exact pixel-level outer boundary touch checking: guarantees that a crop has not clipped symbol strokes",
                "shared_failure_modes": ["Measures raster pixels, not PDF points directly; requires DPI scale factor conversion for Gate D4"],
                "input_interface": "Path to rendered crop image",
                "output_interface": "Dictionary with border_touch_1px, border_touch_2px, min_margin_px, ink_ratio",
                "adapter_needed": "Add scale factor conversion from pixel margin to PDF points (margin_pt = margin_px / zoom)",
                "validating_tests": ["tests/test_crop_isolation_regression.py"],
                "verification_status": "UNIT_TESTED"
            },
            {
                "tool_id": "TOOL-08",
                "script_path": "scripts/adjudicate_candidates_v2.py / scripts/adjudicate_targets.py",
                "rank": 8,
                "assigned_layer": "L5_evidence_adjudication",
                "role": "Multi-layer candidate classification and carry-forward status tracking",
                "integration_disposition": "SELECTIVE_REUSE_ADAPTER_REQUIRED",
                "independent_evidence": "Association tracking between visual candidates and parser identities",
                "shared_failure_modes": ["Defect in _text_match(): empty token sets classified as matching", "VISUALLY_VERIFIED meant only image existence"],
                "input_interface": "JSONL candidate records, parser IDs",
                "output_interface": "adjudication_targets.jsonl with classified statuses",
                "adapter_needed": "Fix empty-token match bug; redefine verification status to require AST and Gate D4 proof",
                "validating_tests": ["tests/test_evaluator_candidate_boundary_isolation.py (3 passed)"],
                "verification_status": "IMPLEMENTED_REQUIRES_REPAIR"
            },
            {
                "tool_id": "TOOL-09",
                "script_path": "scripts/experiments_crop_isolation.py",
                "rank": 9,
                "assigned_layer": "L2_visual_evidence_acquisition / L3_independent_physical_cross_verification",
                "role": "Crop padding parameter calibration (15pt vs 2pt) and prose contamination filtering",
                "integration_disposition": "EXPERIMENTAL_HARNESS",
                "independent_evidence": "Prose detection against math whitelist (sin, cos, lim, log, det, var, cov) to prevent text intrusion",
                "shared_failure_modes": ["Uses preselected candidate boxes; not a discovery mechanism"],
                "input_interface": "Candidate bboxes, source text, experimental padding options",
                "output_interface": "Isolation evaluation metrics (formula_isolated, prose_contamination, latex_plausible)",
                "adapter_needed": "Extract evaluate_isolation function for direct reuse in Gate D4 prose exclusion check",
                "validating_tests": ["tests/test_crop_isolation_regression.py (16 passed)"],
                "verification_status": "UNIT_TESTED"
            },
            {
                "tool_id": "TOOL-10",
                "script_path": "scripts/render_fullpage_depth.py",
                "rank": 10,
                "assigned_layer": "L2_visual_evidence_acquisition",
                "role": "2.5D visual depth estimation via Depth Anything V2 for exploratory spatial layout",
                "integration_disposition": "OPTIONAL_DIAGNOSTIC",
                "independent_evidence": "Monocular depth map provides visual layer separation between text and background",
                "shared_failure_modes": ["Depth does not establish symbolic identity or formula syntax"],
                "input_interface": "PDF page, zoom=2, Depth Anything V2 checkpoint",
                "output_interface": "Grayscale depth, colormapped depth, and combined side-by-side PNGs",
                "adapter_needed": "Keep optional; run on-demand for qualitative visualization rather than automated pipeline",
                "validating_tests": ["Manual inspection / depth manifest verification"],
                "verification_status": "IMPLEMENTED"
            }
        ],
        "mathematical_infrastructure_components": [
            {
                "component_id": "MATH-INFRA-01",
                "script_path": "scripts/mathml_parser.py",
                "role": "Structured Presentation MathML parsing and typed AST generation",
                "disposition": "DIRECT_REUSE",
                "layer": "L4_structural_reconstruction",
                "status": "UNIT_TESTED"
            },
            {
                "component_id": "MATH-INFRA-02",
                "script_path": "scripts/math_symbol_vision_hooks.py",
                "role": "Visual symbol hooks connecting OCR bounding boxes to AST token nodes",
                "disposition": "DIRECT_REUSE",
                "layer": "L4_structural_reconstruction",
                "status": "IMPLEMENTED"
            },
            {
                "component_id": "MATH-INFRA-03",
                "script_path": "scripts/physical_symbol_matcher.py",
                "role": "Bilinear NCC physical raster template matching against 247 verified symbols",
                "disposition": "DIRECT_REUSE",
                "layer": "L3_independent_physical_cross_verification",
                "status": "UNIT_TESTED"
            },
            {
                "component_id": "MATH-INFRA-04",
                "script_path": "scripts/association_bridge.py",
                "role": "Non-leaking cross-evidence association between PDF physical regions and source anchors",
                "disposition": "DIRECT_REUSE",
                "layer": "L5_evidence_adjudication",
                "status": "UNIT_TESTED"
            }
        ]
    }
    return registry


def main():
    reg = build_registry()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
    
    sha256 = hashlib.sha256(OUTPUT_PATH.read_bytes()).hexdigest()
    print(f"Generated Evidence Channel Registry at: {OUTPUT_PATH}")
    print(f"  Architecture Layers: {len(reg['architecture_layers'])}")
    print(f"  Tools Cataloged: {len(reg['tools_inventory'])}")
    print(f"  Math Infrastructure Components: {len(reg['mathematical_infrastructure_components'])}")
    print(f"  SHA-256: {sha256}")


if __name__ == "__main__":
    main()

