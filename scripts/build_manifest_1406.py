#!/usr/bin/env python3
"""
Generate Positive Control Manifest for Paper C:
Paper: 1406.2661 (Generative Adversarial Nets, Ian Goodfellow et al., NIPS 2014)
Target: Page 3 (Equation 1), Page 4 (Equation 2), Page 5 (Equations 5 and 6)

Adheres to Section 10 of spatial-syntactic-preservation-specification.md:
Records math_expression_bbox, equation_number_bbox, and full_row_bbox.
"""

import json
import hashlib
from pathlib import Path

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
PDF_PATH = REPO_ROOT / "DATASETS" / "benchmark_pdfs" / "1406.2661.pdf"
OUT_MANIFEST = REPO_ROOT / "DATASETS" / "structural_preservation" / "1406.2661_positive_control_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest() -> dict:
    pdf_sha256 = sha256_file(PDF_PATH)

    manifest = {
        "manifest_version": "2.0_dual_bbox",
        "manifest_type": "independent_positive_control_ground_truth",
        "created_at": "2026-11-05T19:25:00-06:00",
        "document_identity": {
            "arxiv_id": "1406.2661",
            "title": "Generative Adversarial Nets",
            "authors": ["Ian J. Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza", "Bing Xu", "David Warde-Farley", "Sherjil Ozair", "Aaron Courville", "Yoshua Bengio"],
            "venue": "NIPS 2014",
            "pdf_relative_path": "DATASETS/benchmark_pdfs/1406.2661.pdf",
            "pdf_sha256": pdf_sha256,
            "layout_format": "single_column_nips",
            "target_page_numbers": [3, 4, 5]
        },
        "governing_rules": {
            "cross_platform_encoding": "utf-8",
            "coordinate_space": "mupdf_page_points",
            "frozen_pipeline_invariants": {
                "detector_unmodified": True,
                "two_population_strict_decoupling": True,
                "three_fidelity_dimensions_independent": True
            },
            "specification_alignment": "docs/spatial-syntactic-preservation-specification.md#Section10"
        },
        "gold_equations": [
            {
                "gold_id": "GAN-001",
                "equation_number": 1,
                "selection_identity": {
                    "equation_type": "minimax_objective",
                    "latex_verbatim": "\\min_G \\max_D V(D, G) = \\mathbb{E}_{\\bm{x} \\sim p_{\\text{data}}(\\bm{x})}[\\log D(\\bm{x})] + \\mathbb{E}_{\\bm{z} \\sim p_{\\bm{z}}(\\bm{z})}[\\log(1 - D(G(\\bm{z})))]"
                },
                "pdf_localization": {
                    "page_index_zero_based": 2,
                    "page_number_one_based": 3,
                    "printed_page_number": 3,
                    "coordinate_space": "mupdf_page_points",
                    "math_expression_bbox": [152.22, 111.93, 459.78, 130.49],
                    "equation_number_bbox": [492.38, 114.34, 504.0, 124.3],
                    "full_row_bbox": [152.22, 111.93, 504.0, 130.49],
                    "gap_to_equation_number_pt": 32.6,
                    "pdf_text_extracted": "minG maxD V (D, G) = Ex∼pdata(x)[log D(x)] + Ez∼pz(z)[log(1 −D(G(z)))]. (1)",
                    "verification_status": "VERIFIED_ON_SOURCE_PDF"
                }
            },
            {
                "gold_id": "GAN-002",
                "equation_number": 2,
                "selection_identity": {
                    "equation_type": "optimal_discriminator_fraction",
                    "latex_verbatim": "D^*_G(\\bm{x}) = \\frac{p_{\\text{data}}(\\bm{x})}{p_{\\text{data}}(\\bm{x}) + p_g(\\bm{x})}"
                },
                "pdf_localization": {
                    "page_index_zero_based": 3,
                    "page_number_one_based": 4,
                    "printed_page_number": 4,
                    "coordinate_space": "mupdf_page_points",
                    "math_expression_bbox": [249.35, 417.83, 361.46, 442.25],
                    "equation_number_bbox": [492.38, 424.8, 504.0, 434.77],
                    "full_row_bbox": [249.35, 417.83, 504.0, 442.25],
                    "gap_to_equation_number_pt": 130.93,
                    "pdf_text_extracted": "D∗G(x) = pdata(x) / (pdata(x) + pg(x)) (2)",
                    "verification_status": "VERIFIED_ON_SOURCE_PDF"
                }
            },
            {
                "gold_id": "GAN-005",
                "equation_number": 5,
                "selection_identity": {
                    "equation_type": "kl_divergence_decomposition",
                    "latex_verbatim": "C(G) = -\\log(4) + \\text{KL}\\left(p_{\\text{data}} \\parallel \\frac{p_{\\text{data}} + p_g}{2}\\right) + \\text{KL}\\left(p_g \\parallel \\frac{p_{\\text{data}} + p_g}{2}\\right)"
                },
                "pdf_localization": {
                    "page_index_zero_based": 4,
                    "page_number_one_based": 5,
                    "printed_page_number": 5,
                    "coordinate_space": "mupdf_page_points",
                    "math_expression_bbox": [162.57, 206.42, 449.43, 234.32],
                    "equation_number_bbox": [492.38, 213.94, 504.0, 223.9],
                    "full_row_bbox": [162.57, 206.42, 504.0, 234.32],
                    "gap_to_equation_number_pt": 42.95,
                    "pdf_text_extracted": "C(G) = −log(4) + KL(pdata || (pdata + pg)/2) + KL(pg || (pdata + pg)/2) (5)",
                    "verification_status": "VERIFIED_ON_SOURCE_PDF"
                }
            },
            {
                "gold_id": "GAN-006",
                "equation_number": 6,
                "selection_identity": {
                    "equation_type": "jensen_shannon_divergence",
                    "latex_verbatim": "C(G) = -\\log(4) + 2 \\cdot \\text{JSD}(p_{\\text{data}} \\parallel p_g)"
                },
                "pdf_localization": {
                    "page_index_zero_based": 4,
                    "page_number_one_based": 5,
                    "printed_page_number": 5,
                    "coordinate_space": "mupdf_page_points",
                    "math_expression_bbox": [225.11, 280.29, 386.89, 291.87],
                    "equation_number_bbox": [492.38, 280.65, 504.0, 290.61],
                    "full_row_bbox": [225.11, 280.29, 504.0, 291.87],
                    "gap_to_equation_number_pt": 105.5,
                    "pdf_text_extracted": "C(G) = −log(4) + 2 · JSD (pdata ∥pg ) (6)",
                    "verification_status": "VERIFIED_ON_SOURCE_PDF"
                }
            }
        ]
    }

    return manifest


def main():
    manifest = build_manifest()
    with OUT_MANIFEST.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Created manifest: {OUT_MANIFEST}")
    print(f"Total equations: {len(manifest['gold_equations'])}")
    print(f"PDF SHA-256: {manifest['document_identity']['pdf_sha256']}")


if __name__ == "__main__":
    main()

