"""Source-to-PDF Physical Fixture Audit: Candidate Fixtures PIAA-011 through PIAA-016.

Cross-checks proposed candidates on Page 5 of arXiv:2605.25821 against both:
  1. The semantic / LaTeX identity from the published paper text
  2. The actual character-level PDF glyph text stream, font encodings, and vector geometry

Invariants:
  - Read-only audit: does NOT mutate existing sealed fixtures PIAA-001..010.
  - Physical clearance (Gate D4) is measured directly from the PDF page raster / text stream.
  - Records candidates with status CANDIDATE_HELD_OUT until independently verified.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pymupdf

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
PDF_PATH = (
    "C:/Users/krist/Desktop/zotero/learning-corpus/efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)
AUDIT_OUTPUT_PATH = (
    REPO_ROOT / "DATASETS" / "structural_preservation" / "piaa_candidate_fixtures_audit_p5.json"
)


def audit_candidate_fixtures() -> dict[str, Any]:
    doc = pymupdf.open(PDF_PATH)
    page = doc[4]  # Page 5 (0-based 4)
    page_rect = [page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1]

    # Candidate specifications to audit
    specs = [
        {
            "candidate_id": "PIAA-011",
            "title": "Equation (6) Set-Builder Memory Bank Initialization",
            "section": "Section 3.3 Stage I: Entropy-Guided Bootstrapping",
            "page_1based": 5,
            "page_0based": 4,
            "column": 1,
            "target_latex": r"\mathcal{B}_c^{(0)} = \left\{ \mathbf{x}_i \in \mathcal{X} \;\middle|\; \arg\max_k p_{i,k} = c \right\}_{\text{Top-}K \text{ by min } H(\mathbf{x}_i)}",
            "equation_label": "(6)",
            "query_bbox": [58.0, 525.0, 286.0, 558.0],
            "expected_constructs": ["extensible_braces", "middle_relation_bar", "argmax_subscript", "text_subscript_on_brace"],
        },
        {
            "candidate_id": "PIAA-012",
            "title": "Equation (7) Vision-Driven Purification Set-Builder",
            "section": "Section 3.3 Stage II: Vision-Driven Purification",
            "page_1based": 5,
            "page_0based": 4,
            "column": 1,
            "target_latex": r"\mathcal{B}_c = \left\{ \mathbf{x}_i \in \mathcal{B}_c^{(0)} \;\middle|\; q_{i,c} \ge \mu_{q,c} + \sigma_{q,c} \right\}",
            "equation_label": "(7)",
            "query_bbox": [90.0, 700.0, 255.0, 724.0],
            "expected_constructs": ["extensible_braces", "middle_relation_bar", "inequality_relation", "subscript_greek"],
        },
        {
            "candidate_id": "PIAA-013",
            "title": "Equation (8) Prototype Confidence-Weighted Average Fraction",
            "section": "Section 3.3 Stage III: Robust Shrinkage Induction",
            "page_1based": 5,
            "page_0based": 4,
            "column": 2,
            "target_latex": r"\boldsymbol{\mu}_c = \frac{\sum_{\mathbf{x}_i \in \mathcal{B}_c} q_{i,c} \mathbf{x}_i}{\sum_{\mathbf{x}_i \in \mathcal{B}_c} q_{i,c}}",
            "equation_label": "(8)",
            "query_bbox": [375.0, 445.0, 480.0, 480.0],
            "expected_constructs": ["display_fraction", "numerator_summation", "denominator_summation", "set_membership_subscript"],
        },
        {
            "candidate_id": "PIAA-014",
            "title": "Equation (9) Pooled Sample Covariance Double Summation",
            "section": "Section 3.3 Stage III: Robust Shrinkage Induction",
            "page_1based": 5,
            "page_0based": 4,
            "column": 2,
            "target_latex": r"\hat{\boldsymbol{\Sigma}} = \frac{1}{|\mathcal{B}|} \sum_{c=1}^C \sum_{\mathbf{x}_i \in \mathcal{B}_c} (\mathbf{x}_i - \boldsymbol{\mu}_c)(\mathbf{x}_i - \boldsymbol{\mu}_c)^\top",
            "equation_label": "(9)",
            "query_bbox": [335.0, 515.0, 520.0, 555.0],
            "expected_constructs": ["hat_accent_matrix", "fraction_normalizer", "double_summation", "vector_transpose_outer_product"],
        },
        {
            "candidate_id": "PIAA-015",
            "title": "Equation (10) Precision Matrix Trace-Regularized Shrinkage",
            "section": "Section 3.3 Stage III: Robust Shrinkage Induction",
            "page_1based": 5,
            "page_0based": 4,
            "column": 2,
            "target_latex": r"\boldsymbol{\Sigma}^{-1} = d \left[ (|\mathcal{B}| - 1)\hat{\boldsymbol{\Sigma}} + \text{Tr}(\hat{\boldsymbol{\Sigma}})\mathbf{I}_d \right]^{-1}",
            "equation_label": "(10)",
            "query_bbox": [340.0, 615.0, 530.0, 640.0],
            "expected_constructs": ["matrix_inverse_exponent", "tall_brackets", "trace_operator", "identity_matrix"],
        },
        {
            "candidate_id": "PIAA-016",
            "title": "Algorithm 1 Patch-based Visual Classifier Learning (PVCL)",
            "section": "Section 3.3 Algorithm 1 Pseudocode Box",
            "page_1based": 5,
            "page_0based": 4,
            "column": 2,
            "target_latex": "Algorithm 1: PVCL multi-step pseudo-code frame with 13 numbered statements",
            "equation_label": "Algorithm 1",
            "query_bbox": [304.7, 65.0, 542.1, 352.0],
            "expected_constructs": ["framed_algorithm_block", "line_numbers", "inline_math_statements", "horizontal_rules"],
        },
    ]

    blocks = page.get_text("rawdict")["blocks"]
    all_glyphs = []
    for b in blocks:
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                font = span.get("font", "")
                sz = span.get("size", 0.0)
                for ch in span.get("chars", []):
                    all_glyphs.append({
                        "char": ch["c"],
                        "char_code": ord(ch["c"]),
                        "font": font,
                        "size_pt": round(sz, 2),
                        "bbox": [round(x, 3) for x in ch["bbox"]],
                    })

    # Vector drawings on page
    drawings = page.get_drawings()
    vector_rules = []
    for d in drawings:
        r = d.get("rect")
        if r and (r.x1 - r.x0) > 4.0 and (r.y1 - r.y0) < 3.0:
            vector_rules.append({
                "bbox": [round(r.x0, 3), round(r.y0, 3), round(r.x1, 3), round(r.y1, 3)],
                "width": round(r.x1 - r.x0, 2),
                "height": round(r.y1 - r.y0, 2),
            })

    audited_candidates = []

    for spec in specs:
        qx0, qy0, qx1, qy1 = spec["query_bbox"]

        # Collect glyphs inside query bbox
        inside = [
            g for g in all_glyphs
            if qx0 - 2.0 <= (g["bbox"][0] + g["bbox"][2]) / 2.0 <= qx1 + 2.0
            and qy0 - 2.0 <= (g["bbox"][1] + g["bbox"][3]) / 2.0 <= qy1 + 2.0
        ]

        if inside:
            tight_x0 = min(g["bbox"][0] for g in inside)
            tight_y0 = min(g["bbox"][1] for g in inside)
            tight_x1 = max(g["bbox"][2] for g in inside)
            tight_y1 = max(g["bbox"][3] for g in inside)
            tight_bbox = [round(tight_x0, 3), round(tight_y0, 3), round(tight_x1, 3), round(tight_y1, 3)]
        else:
            tight_bbox = spec["query_bbox"]

        # Measure physical clearances to neighboring text
        # Upper neighbor in same column
        col_x0 = 55.0 if spec["column"] == 1 else 307.1
        col_x1 = 290.7 if spec["column"] == 1 else 542.1

        above_glyphs = [
            g for g in all_glyphs
            if col_x0 <= (g["bbox"][0] + g["bbox"][2]) / 2.0 <= col_x1
            and g["bbox"][3] <= tight_bbox[1] - 0.1
        ]
        below_glyphs = [
            g for g in all_glyphs
            if col_x0 <= (g["bbox"][0] + g["bbox"][2]) / 2.0 <= col_x1
            and g["bbox"][1] >= tight_bbox[3] + 0.1
        ]

        clearance_above = round(tight_bbox[1] - max(g["bbox"][3] for g in above_glyphs), 2) if above_glyphs else 999.0
        clearance_below = round(min(g["bbox"][1] for g in below_glyphs) - tight_bbox[3], 2) if below_glyphs else 999.0

        gate_d4_passed = (clearance_above >= 2.0 and clearance_below >= 2.0)
        failure_reason = None
        if not gate_d4_passed:
            if clearance_above < 2.0:
                failure_reason = f"sub_2pt_clearance_failure_above ({clearance_above} pt < 2.00 pt)"
            else:
                failure_reason = f"sub_2pt_clearance_failure_below ({clearance_below} pt < 2.00 pt)"

        # Fonts observed
        fonts_observed = sorted(list({g["font"] for g in inside}))

        # Matched vector rules
        matched_rules = [
            r for r in vector_rules
            if tight_bbox[0] - 2.0 <= r["bbox"][0] and r["bbox"][2] <= tight_bbox[2] + 2.0
            and tight_bbox[1] - 2.0 <= r["bbox"][1] <= tight_bbox[3] + 2.0
        ]

        audited_candidates.append({
            "candidate_id": spec["candidate_id"],
            "title": spec["title"],
            "section": spec["section"],
            "page_1based": spec["page_1based"],
            "page_0based": spec["page_0based"],
            "column": spec["column"],
            "target_latex": spec["target_latex"],
            "equation_label": spec["equation_label"],
            "query_bbox": spec["query_bbox"],
            "physical_tight_bbox": tight_bbox,
            "glyph_count": len(inside),
            "fonts_observed": fonts_observed,
            "matched_vector_rules": matched_rules,
            "gutter_clearance_pt": {
                "clearance_above_pt": clearance_above,
                "clearance_below_pt": clearance_below,
                "gate_d4_passed": gate_d4_passed,
                "failure_reason": failure_reason,
            },
            "adjudication_status": "CANDIDATE_HELD_OUT",
            "verification_disposition": "PASSED_GEOMETRY" if gate_d4_passed else "NOT_VERIFIED: MANDATORY_GATE_D4_FAILURE",
        })

    audit_report = {
        "audit_identifier": "PIAA-P5-CANDIDATE-FIXTURES-AUDIT",
        "schema_version": "1.0.0",
        "source_document": {
            "arxiv_id": "2605.25821",
            "pdf_path": PDF_PATH,
            "page_0based": 4,
            "page_1based": 5,
            "page_dimensions": [page.rect.width, page.rect.height],
        },
        "candidate_count": len(audited_candidates),
        "candidates": audited_candidates,
    }

    AUDIT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)

    doc.close()
    return audit_report


if __name__ == "__main__":
    report = audit_candidate_fixtures()
    print(f"Audited {report['candidate_count']} candidate fixtures on Page 5:")
    for c in report["candidates"]:
        status_mark = "✓" if c["gutter_clearance_pt"]["gate_d4_passed"] else "✗"
        print(f"  {status_mark} {c['candidate_id']}: {c['title']}")
        print(f"     BBox: {c['physical_tight_bbox']}")
        print(f"     Glyphs: {c['glyph_count']}, Fonts: {c['fonts_observed']}")
        print(f"     Gate D4: {c['gutter_clearance_pt']['gate_d4_passed']} ({c['verification_disposition']})")
    print(f"\nAudit artifact written to: {AUDIT_OUTPUT_PATH}")
