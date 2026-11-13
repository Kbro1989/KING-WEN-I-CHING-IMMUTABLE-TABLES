import json

with open('symbol_identity_integration_audit.json') as f:
    audit = json.load(f)

# Add B-14/benchmark evidence to the audit
audit['b14_benchmark_evidence'] = {
    'b14_1_solver_status_model': {
        'path': 'DATASETS/b14_1_solver_success_status_model.json',
        'entries': 991,
        'pipeline_stages': 6,
        'source_paper': '2605.00155',
        'status': 'IMPLEMENTED'
    },
    'b14_equation_reconciliation_matrix': {
        'path': 'DATASETS/b14_equation_reconciliation_matrix.jsonl',
        'entries': 991,
        'classifications': {
            'E2E_ONLY_NON_EQUATION': 448,
            'UNCLASSIFIED': 264,
            'BOTH_FAIL': 214,
            'REC_ONLY': 53,
            'REC_ONLY_SOLVER': 12
        },
        'solver_stats': {
            'eligible': 267,
            'valid_successes': 65,
            'success_rate': '24.34%'
        },
        'status': 'IMPLEMENTED'
    },
    'b14_delimiter_integration_audit': {
        'path': 'DATASETS/b14_delimiter_integration_audit.json',
        'status': 'IN_PROGRESS',
        'milestone': 'B-14.1',
        'detector_implemented': True,
        'identity_preservation': 'CANONICAL tokens preserved (LANGLE=RANGLE, LNORM=RNORM)',
        'frozen_regression_baseline': 'Border detection only, NOT delimiter identity',
        'tall_delimiter_test_executable': False,
        'acceptance_criteria': [
            'Visual detection != recovery',
            'Independent evaluation of detection/identity/reconstruction/AST',
            'No router before audit'
        ],
        'environment_constraints': 'numpy 2.5.4 cp314 incompatible with Python 3.11'
    },
    'b14_tall_delimiter_integration_test': {
        'path': 'DATASETS/b14_tall_delimiter_integration_test.json',
        'test_status': 'BLOCKED',
        'verification_status': 'PASSED',
        'manual_result': '7/7 tests passed',
        'test_corpus': '1212.0957_p8 tall narrow crops (7 files)',
        'gate_coverages': {
            'D1': 'glyph extent H_crop >= H_glyph',
            'D2': 'font-aware identity (CMEX, txexs, lmex10, standard)',
            'D3': 'pair association & cross-association guard',
            'D4': '2D grid semantic completeness (bmatrix normalized)',
            'D5': 'translation fidelity (pmatrix non-flattening)',
            'D6': 'cryptographic provenance (source hash)',
            'downstream': 'single structural candidate emission'
        },
        'tall_delimiter_reference': '1212.0957_p8_tall_narrow_00_z8.png (55,207 bytes)',
        'note': 'Host execution blocked; manual pass only'
    },
    'audit_rendered_png_producers_report': {
        'path': 'DATASETS/audit_rendered_png_producers_report.json',
        'producers': {
            'targeted_ocr': {
                'total_png_files': 'tracked',
                'detection_images_count': 'tracked',
                'total_crop_images': 'tracked',
                'tall_narrow_crops': 'tracked',
                'wide_crops': 'tracked',
                'crops_with_border_touch_1px': 'tracked',
                'crops_with_border_touch_pct': 'tracked',
                'empty_ocr_count': 'tracked',
                'empty_ocr_pct': 'tracked',
                'negative_control_2009_00031_hallucinations': 'tracked'
            },
            'visual_recovery': {
                'total_png_files': 'tracked',
                'annotated_pages_count': 'tracked',
                'sample_analyzed_pages': 'tracked'
            }
        },
        'status': 'AUDIT_EVIDENCE'
    },
    'benchmark_representativeness_report': {
        'path': 'DATASETS/benchmark_representativeness_report.json',
        'population': {
            'registry_papers': 136,
            'evaluated_papers': 16,
            'unevaluated_papers': 120,
            'evaluated_pct': 11.8,
            'registry_equations': 40132,
            'evaluated_equations': 3409,
            'unevaluated_equations': 36723,
            'evaluated_pages': 344,
            'evaluated_cross_refs': 46105
        },
        'coverage': 'Limited - 11.8% papers, 8.49% equations',
        'status': 'AUDIT_EVIDENCE'
    },
    'missing_artifacts': [
        'execution_manifest.json',
        'synthetic_test_results.json',
        'targeted_ocr_results.json',
        'delimiter_records.json',
        'fullpage_depth_manifest.json',
        'coverage_summary.json',
        'population_intersection.json',
        'cross_refs_*.json',
        '1212.0957_p8.json',
        '2009.00031_p5.json'
    ]
}

# Add evidence classification fields template
audit['evidence_classification_template'] = {
    'artifact_exists': 'boolean - Whether the artifact is present',
    'implementation_status': 'boolean - Whether the capability exists',
    'execution_status': 'boolean - Whether it actually ran',
    'test_status': 'boolean - Whether executable tests passed',
    'verification_status': 'boolean - Whether independent verification occurred',
    'certification_status': 'boolean - Whether formal acceptance criteria passed',
    'environment_constraints': 'string - Runtime limitations',
    'population_scope': 'string - Exact evaluated population',
    'evidence_sha256': 'string - Artifact integrity'
}

# Add revised dispositions
audit['revised_dispositions'] = {
    'b14_1_solver_model': '991 equation records - Not certified',
    'equation_reconciliation': '65 valid solver successes / 267 eligible (24.34%) - Not certified',
    'delimiter_integration': 'IN_PROGRESS - Not certified',
    'tall_delimiter_integration': '7/7 manually passed; host execution blocked - Conditional evidence',
    'd1_d6_engine': 'Implemented, integration evidence incomplete - Not certified',
    'png_producer_traceability': 'Two producers documented - Audit evidence',
    'benchmark_representativeness': '16/136 papers; 3,409/40,132 equations (11.8% / 8.49%) - Limited population coverage'
}

with open('symbol_identity_integration_audit.json', 'w') as f:
    json.dump(audit, f, indent=2)

print('Consolidated audit updated with B-14/benchmark evidence')