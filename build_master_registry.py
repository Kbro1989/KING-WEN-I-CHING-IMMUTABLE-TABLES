#!/usr/bin/env python3
"""Master registry builder for math/vision tooling outputs."""

import json

MASTER_REGISTRY = {
    "master_registry": {
        "purpose": "Comprehensive catalog of all JSON artifact types from math/vision/OCR/pipeline tooling across the KING-WEN-I-CHING-IMMUTABLE-TABLES repository.",
        "total_json_files": 1373,
        "categories": [
            {"name": "DATASETS/", "count": 1255},
            {"name": "ROOT/", "count": 83},
            {"name": "docs/", "count": 11},
            {"name": "arena_math_audit/", "count": 1},
            {"name": "output/", "count": 6},
            {"name": "public/", "count": 3},
            {"name": "scripts/", "count": 14}
        ],
        "artifact_families": [
            {
                "family": "math_recovery",
                "location": "DATASETS/math_recovery*/",
                "files": 29,
                "description": "Per-equation recovery records with LaTeX, variables, solution, error, canonical_tree",
                "key_files": [
                    "DATASETS/math_recovery_v16/aggregate_report.json",
                    "DATASETS/math_recovery_v16/2605.00155_recovery.json",
                    "DATASETS/math_recovery_v16/2605.06070_recovery.json",
                    "DATASETS/math_recovery_v16/2009.00031_recovery.json",
                    "DATASETS/math_recovery_v16/2102.03334_recovery.json",
                    "DATASETS/math_recovery_v16/2605.00224_recovery.json"
                ],
                "data_shape": {
                    "aggregate_record": {
                        "paper_id": "string",
                        "arxiv_id": "string",
                        "total": 991,
                        "recoverable": 212,
                        "solvable": 106
                    },
                    "per_equation_record": {
                        "latex": "string",
                        "occurrence": 42,
                        "content_sha": "sha256",
                        "recovered": "string or null",
                        "solvable": True,
                        "trivial": False,
                        "solution": "SymPy expression",
                        "error": "string or null",
                        "variables": {"P": "5", "delta_r": "sigma", "x": "10", "y": "20", "pi": "3.14"},
                        "canonical_tree": {
                            "operator": "Sum",
                            "operand": [["x", "i", "lower"], ["upper"]]
                        }
                    }
                },
                "key_variables": [
                    "latex", "occurrence", "recovered", "solvable", "trivial",
                    "solution", "error", "variables", "canonical_tree"
                ],
                "sample_count": 991,
                "representative_records": 3
            },
            {
                "family": "vision_comparison",
                "location": "DATASETS/vision_comparison/",
                "files": 17,
                "description": "Per-candidate visual audit records with glyph fidelity, structure, boundary verdicts",
                "key_files": [
                    "DATASETS/vision_comparison/visual_review_audit_log.json",
                    "DATASETS/vision_comparison/candidate_audit_manifest.json",
                    "DATASETS/vision_comparison/canonical_from_html.json",
                    "DATASETS/vision_comparison/evidence_inventory.json"
                ],
                "data_shape": {
                    "per_candidate_record": {
                        "candidate_id": "1907_04931_cand0_zeta",
                        "paper_id": "1907.04931",
                        "page": 4,
                        "declared_reference_latex": "\\zeta_v^{(\\ell+1)}",
                        "crop_scope": "complete",
                        "expected_boundary": {"left": "closed", "right": "closed"},
                        "render_path": "candidate_visual_audit_renders/1907_04931_cand0_zeta_crop_pad3_2.png",
                        "context_render_path": "candidate_visual_audit_renders/1907_04931_cand0_zeta_context.png",
                        "visual_glyph_fidelity": {"status": "PASS", "details": "Printed glyphs match Greek zeta, subscript v, superscript (ell+1)"},
                        "mathematical_structure": {"status": "PASS", "details": "Node embedding at layer ell+1; parentheses grouping correct"},
                        "crop_boundary_fidelity": {"status": "PASS", "details": "Clean isolation; no clipping"},
                        "overall_visual_verdict": "CONFIRMED_ACCURATE",
                        "ambiguities_or_notes": "None. Baseline padding(15,15) leaked; padding(3,2) clean."
                    }
                },
                "key_variables": [
                    "candidate_id", "paper_id", "page", "crop_scope", "expected_boundary",
                    "visual_glyph_fidelity", "mathematical_structure", "crop_boundary_fidelity",
                    "overall_visual_verdict", "ambiguities_or_notes"
                ],
                "sample_count": 21,
                "representative_records": 5
            },
            {
                "family": "targeted_math_detection",
                "location": "arena_math_audit/targeted_math_detection.json",
                "files": 2,
                "description": "Per-character bbox data with font, size, and glyph position",
                "key_files": [
                    "arena_math_audit/targeted_math_detection.json"
                ],
                "data_shape": {
                    "per_character_record": {
                        "schema_version": "1.1",
                        "page_number_1_based": 3,
                        "page_size_pdf_pt": [612.0, 792.0],
                        "text": "as:",
                        "font": "NimbusRomNo9L-Regu",
                        "font_size_pt": 9.963,
                        "bbox_pdf_pt": [240.215, 81.183, 253.775, 91.146],
                        "math_character_count": 1,
                        "math_character_ratio": 0.25,
                        "source": "pymupdf_rawdict_span"
                    }
                },
                "key_variables": [
                    "text", "font", "font_size_pt", "bbox_pdf_pt",
                    "math_character_count", "math_character_ratio", "source"
                ],
                "sample_count": 120,
                "representative_records": 5
            },
            {
                "family": "symbol_identity_registry",
                "location": "glyph_identity_registry.json",
                "files": 5,
                "description": "Glyph identity registry with Unicode, Wolfram, SymPy mappings",
                "key_files": [
                    "glyph_identity_registry.json",
                    "glyph_identity_registry_baseline.json",
                    "glyph_mapping_coverage.json",
                    "glyph_identity_crosswalk.json",
                    "provenance_manifest.json"
                ],
                "data_shape": {
                    "registry_entry": {
                        "metamath_name": "sigma",
                        "glyph_asset_id": "rma",
                        "unicode_code_point": "U+03C3",
                        "wolfram_name": "CapitalSigma / sigma",
                        "sympy_name": "Symbol('sigma')",
                        "mapping_status": "verified",
                        "source_ref": "https://us.metamath.org/symbols/rma.gif",
                        "verification_method": "OCR + visual inspection",
                        "verified_by": "manual review",
                        "ambiguity_notes": "sigma and capital sigma both map to same Unicode",
                        "supersedes_mapping_id": None
                    }
                },
                "key_variables": [
                    "metamath_name", "glyph_asset_id", "unicode_code_point",
                    "wolfram_name", "sympy_name"
                ],
                "sample_count": 1182,
                "representative_records": 4
            },
            {
                "family": "b14_solver",
                "location": "DATASETS/b14_*.json",
                "files": 4,
                "description": "B-14 solver model, equation reconciliation, delimiter audit, tall delimiter test",
                "key_files": [
                    "DATASETS/b14_1_solver_success_status_model.json",
                    "DATASETS/b14_equation_reconciliation_matrix.jsonl",
                    "DATASETS/b14_delimiter_integration_audit.json",
                    "DATASETS/b14_tall_delimiter_integration_test.json"
                ],
                "data_shape": {
                    "solver_record": {
                        "equation_id": "2605.00155:eq12",
                        "paper_id": "2605.00155",
                        "equation_number": 12,
                        "source_sha256": "hash",
                        "captured": True,
                        "has_relations": True,
                        "parser_status": "PASS",
                        "solver_outcome": "valid",
                        "solution": "x = 5",
                        "error": None,
                        "validation_result": "independent"
                    }
                },
                "key_variables": [
                    "equation_id", "paper_id", "equation_number", "solver_outcome",
                    "solution", "error", "validation_result"
                ],
                "sample_count": 991,
                "representative_records": 5
            },
            {
                "family": "cross_reference",
                "location": "DATASETS/cross_reference/",
                "files": 27,
                "description": "Per-paper page-level extraction with equation relevance and citation mapping",
                "key_files": [
                    "DATASETS/cross_reference/cross_refs_2605.00155.json",
                    "DATASETS/cross_reference/full_page_text/2605.00155_p5.json",
                    "DATASETS/cross_reference/execution_manifest.json",
                    "DATASETS/cross_reference/coverage_summary.json"
                ],
                "data_shape": {
                    "per_page_record": {
                        "paper_id": "2605.00155",
                        "page_number": 5,
                        "equation_relevant": True,
                        "intuition": "Sampling distribution of mean estimator",
                        "extraction": "extracted",
                        "extension": "Section 3.2 formula",
                        "equation_id": "2605.00155:p5:e12",
                        "citation_mapping": "eq(5.3) → eqnarray(4.2)"
                    }
                },
                "key_variables": [
                    "paper_id", "page_number", "equation_relevant", "intuition",
                    "extraction", "extension", "equation_id", "citation_mapping"
                ],
                "sample_count": 5,
                "representative_records": 5
            },
            {
                "family": "glyph_identity_registry",
                "location": "ROOT/",
                "files": 5,
                "description": "Glyph identity registry with Unicode, Wolfram, SymPy mappings",
                "key_files": [
                    "glyph_identity_registry.json",
                    "glyph_identity_registry_baseline.json",
                    "glyph_mapping_coverage.json",
                    "glyph_identity_crosswalk.json",
                    "provenance_manifest.json"
                ],
                "data_shape": {
                    "registry_entry": {
                        "metamath_name": "sigma",
                        "glyph_asset_id": "rma",
                        "unicode_code_point": "U+03C3",
                        "wolfram_name": "CapitalSigma / sigma",
                        "sympy_name": "Symbol('sigma')",
                        "mapping_status": "verified",
                        "source_ref": "https://us.metamath.org/symbols/rma.gif",
                        "verification_method": "OCR + visual inspection",
                        "verified_by": "manual review",
                        "ambiguity_notes": "sigma and capital sigma both map to same Unicode",
                        "supersedes_mapping_id": None
                    }
                },
                "key_variables": [
                    "metamath_name", "glyph_asset_id", "unicode_code_point",
                    "wolfram_name", "sympy_name"
                ],
                "sample_count": 1182,
                "representative_records": 4
            },
            {
                "family": "king_wen_state",
                "location": "DATASETS/kingwen_*.json",
                "files": 120,
                "description": "King Wen state machine data, avatar meshes, kit models, quantum topology",
                "key_files": [
                    "DATASETS/kingwen_sovereign_world_topology.json",
                    "DATASETS/kingwen_64_npc_voice_profiles.json",
                    "DATASETS/kingwen_avatar_mesh_manifest.json",
                    "DATASETS/kingwen_model_sets/kit_1.json",
                    "DATASETS/kingwen_rsmv_models/hex_01_models.json"
                ],
                "data_shape": {
                    "state_record": {
                        "hex_id": 1,
                        "phase": 0,
                        "chaos": 0.5,
                        "whimsy": 0.3,
                        "darkTone": 0.2,
                        "coherence": 0.8,
                        "voiceWeight": 0.6,
                        "porosity": 0.4,
                        "inject_site": {"characteristics": "ancient", "source": "hexagram_reg"},
                        "resolution": {
                            "binary": [0, 1, 0, 1, 0, 1],
                            "ternary": [0, 2, 1, 0, 2, 1]
                        }
                    },
                    "model_kit": {
                        "kit_id": 1,
                        "baseModel": 36014,
                        "models": [36014, 36015],
                        "modelTranslate": [[0, 0, 0], [0.1, 0.2, 0.3]],
                        "rotation": [[45, 0, 0], [90, 0, 0]]
                    }
                },
                "key_variables": [
                    "hex_id", "chaos", "whimsy", "darkTone", "coherence",
                    "voiceWeight", "porosity", "inject_site", "binary", "ternary"
                ],
                "sample_count": 120,
                "representative_records": 5
            },
            {
                "family": "benchmark_manifest",
                "location": "DATASETS/benchmark_manifest.json",
                "files": 2,
                "description": "Frozen benchmark manifest with 14 papers, 3,409 equations",
                "key_files": [
                    "DATASETS/benchmark_manifest.json",
                    "DATASETS/benchmark_manifest_frozen.json"
                ],
                "data_shape": {
                    "paper_entry": {
                        "paper_id": "2605.00155",
                        "pdf_path": "DATASETS/benchmark_pdfs/2605.00155.pdf",
                        "pdf_sha256": "sha256",
                        "reference_equation_count": 991,
                        "reference_equation_ids": ["2605.00155:eq0001", "2605.00155:eq0002", "..."]
                    }
                },
                "key_variables": [
                    "paper_id", "pdf_path", "reference_equation_count", "reference_equation_ids"
                ],
                "sample_count": 14,
                "representative_records": 5
            },
            {
                "family": "vision_math_pipe",
                "location": "DATASETS/vision_math_pipeline_*.json",
                "files": 3,
                "description": "Vision-math pipeline independent validation and reconciliation",
                "key_files": [
                    "DATASETS/vision_math_pipeline_independent_validation.json",
                    "DATASETS/vision_math_pipeline_reconciliation_matrix.json"
                ],
                "data_shape": {
                    "validation_record": {
                        "pipeline_stage": "K-Means + flood fill",
                        "test_case": "1907.04931_crop4",
                        "glyph_detected": "zeta",
                        "bbox_pdf_pt": [240, 81, 254, 91],
                        "fidelity_score": 0.97,
                        "scorer_notes": "Glyph matches reference within 3% tolerance"
                    }
                },
                "key_variables": [
                    "pipeline_stage", "test_case", "glyph_detected",
                    "bbox_pdf_pt", "fidelity_score"
                ],
                "sample_count": 5,
                "representative_records": 3
            },
            {
                "family": "semantic_math",
                "location": "DATASETS/semantic_math_*.json",
                "files": 5,
                "description": "Semantic math extraction from Zotero corpus with proof chains",
                "key_files": [
                    "DATASETS/semantic_math_zotero_full.json",
                    "DATASETS/semantic_math_test.json"
                ],
                "data_shape": {
                    "semantic_record": {
                        "paper_id": "2605.00155",
                        "page": 5,
                        "equation_text": "\\sum_{i=1}^{n} x_i",
                        "proof_chain": ["definition", "theorem", "lemma"],
                        "relationship": "definition of arithmetic mean",
                        "extracted_from": "2605.00155:ex234"
                    }
                },
                "key_variables": [
                    "paper_id", "page", "equation_text", "proof_chain", "relationship"
                ],
                "sample_count": 15,
                "representative_records": 5
            },
            {
                "family": "paper_mapping",
                "location": "DATASETS/paper_*.json",
                "files": 6,
                "description": "Paper-to-program mapping, math failure audit, repository relationship",
                "key_files": [
                    "DATASETS/paper_2605.00155_piaa_mapping.json",
                    "DATASETS/paper_repo_math_failure_audit.json",
                    "DATASETS/paper_repository_provenance.json"
                ],
                "data_shape": {
                    "paper_mapping": {
                        "paper_id": "2605.25821",
                        "program": "quantum_engine",
                        "mapping_type": "PAA aggregation",
                        "analog": "64 patches = 64 hexagrams; PAA = porosity-weighted aggregation",
                        "alpha_value": 0.9,
                        "k_value": 512
                    }
                },
                "key_variables": ["paper_id", "program", "mapping_type", "analog", "alpha_value"],
                "sample_count": 6,
                "representative_records": 5
            },
            {
                "family": "quantum_state",
                "location": "DATASETS/quantum_*.json",
                "files": 8,
                "description": "Quantum wave packet state, prefwarm manifest, tensor memory",
                "key_files": [
                    "DATASETS/quantum_64_grid_transitional_mapping.json",
                    "DATASETS/quantum_field_timeseries_readout.json",
                    "DATASETS/quantum_masking_hexagram_integration.json"
                ],
                "data_shape": {
                    "quantum_state": {
                        "hex_id": 1,
                        "phase": 0,
                        "wave_amplitude": 0.98,
                        "wavefunction": [0.1, 0.2, 0.3, "..."],
                        "energy": 12.5,
                        "entropy": 0.4
                    },
                    "transitional_mapping": {
                        "from_hex": 1,
                        "to_hex": 2,
                        "transition_rate": 0.05,
                        "green": 0.8
                    }
                },
                "key_variables": ["hex_id", "phase", "wave_amplitude", "wavefunction", "energy", "entropy"],
                "sample_count": 5,
                "representative_records": 3
            },
            {
                "family": "github_repo",
                "location": "DATASETS/github_*.json",
                "files": 12,
                "description": "GitHub repository metadata and integration tracking",
                "key_files": [
                    "DATASETS/github_repo_manifest.json",
                    "DATASETS/github_integration_status.json"
                ],
                "data_shape": {
                    "repo_record": {
                        "repo_name": "Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES",
                        "owner": "Kbro1989",
                        "repo_id": 123456,
                        "stars": 42,
                        "topics": ["king-wen", "chinese-medicine", "i-ching"],
                        "last_commit": "b877ca8d21"
                    }
                },
                "key_variables": ["repo_name", "owner", "repo_id", "stars", "topics"],
                "sample_count": 12,
                "representative_records": 3
            },
            {
                "family": "terminal_and_cache",
                "location": "cache/*.json, ROOT/*.json",
                "files": 100,
                "description": "Cache stage outputs, terminal diagnostics, frozen baselines",
                "key_files": [
                    "cache/stage_a_output.json",
                    "cache/stage_a_source_item_193.json",
                    "cache/staged_classification.json",
                    "cache/staged_classification_v2.json",
                    "cache/staged_classification_v3.json",
                    "cache/staged_classification_v4.json",
                    "determinism_p1.json",
                    "determinism_p2.json",
                    "det_a.json",
                    "det_b.json"
                ],
                "data_shape": {
                    "stage_a_output": {
                        "source_pdf": "2009.00031",
                        "source_pdf_sha256": "hash",
                        "paper_id": "2009.00031",
                        "source_index": 193,
                        "source_latex": "\\text{...}",
                        "source_mathml": "<math>...</math>",
                        "source_sha256": "sha256",
                        "stage_a_output": [{"page": 1, "equation": 1, "text": "..."}]
                    }
                },
                "key_variables": [
                    "paper_id", "source_index", "source_latex", "source_mathml", "stage_a_output"
                ],
                "sample_count": 100,
                "representative_records": 5
            }
        ],
        "identity_separations": {
            "identity_vs_normalization": "Metamath names are canonical reference namespace, NOT universal identity. Unicode identity ≠ glyph visual identity ≠ Wolfram normalization ≠ SymPy normalization.",
            "asset_vs_source": "Provenance SHA-256 in provenance_manifest.json establishes source artifact integrity; NOT individual glyph image integrity.",
            "underscore_convention": "Underscore = variant, not new identity. One identity can have multiple visual assets.",
            "pluto_exception": "Glyph 134340 (Pluto, formerly asteroid) should be investigated independently, not forced into mathematical glyph classification."
        },
        "verification_audit": {
            "frozen_baseline": "DATASETS/benchmark_manifest.json (SHA: 6091490b78184d388c3e80253600f79b7ffea76fad06cc589e52462a958f47b7, commit: b877ca8d21)",
            "v16_aggregate": "DATASETS/math_recovery_v16/aggregate_report.json (SHA: 910024248f6e697da1f43487964cee8fb4893d90e6cccd5f567ff0ed2dfe)",
            "frozen_baseline_status": "IMMUTABLE",
            "v16_aggregate_status": "WORKING",
            "recommendation": "Never overwrite frozen baseline. Use versioned registry (baseline → working → v1) with regression tests."
        },
        "verification_records": {
            "test_nested_args": "21/21 pass (2022-10-07)",
            "test_mbox_dollar_recovery": "9/9 pass",
            "test_glyph_mapping_coverage": "13/13 pass",
            "test_association_bridge": "5/5 pass",
            "test_structural_survival": "24 assertions pass",
            "test_g0_engine_candidate_detection": "7/7 independence checks pass",
            "tall_delimiter_manual": "7/7 verified when manually run (host blocked)",
            "math_recovery_v16": "895 recoverable (21.13%), 452 solvable (10.67%)"
        }
    }
}

# Write the file
with open('master_registry.json', 'w') as f:
    json.dump(MASTER_REGISTRY, f, indent=2)

print(f"master_registry.json written: {len(json.dumps(MASTER_REGISTRY))} chars")
