#!/usr/bin/env python3
"""
Combinatorics Benchmark — End-to-End Stirling Validation Trial
==============================================================
Benchmark Sources:
  1. Primary: Mourad Rahmani (2012), arXiv:1212.0957v1 [math.CO]
     "The Generalized Stirling Transform"
     SHA-256: 1c734a4e0a29c8eae4b94d8033351b62bf8411a78e5d9798b904dcd4e86c14d1
  2. Independent Reference: Milan Janjić (2008), arXiv:0806.2366v1 [math.CO]
     "On a non-combinatorial definition of Stirling numbers"
     SHA-256: ed9e309127125306f12da104d810cfb1a7f6cefb8123382f9167d730b2496dde
  3. External Reference Fixtures: OEIS A000110, A000670, A000045

Protocol:
  - Separate extraction correctness from mathematical residual validation.
  - Record convention (EGF), index base (0), and transform direction (forward/inverse).
  - Explicitly document source dependencies to prevent shared-error survivorship.
"""

import sys
import os
import json
import math
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Literal, Optional

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validators.stirling_transform as validator_mod

BENCHMARK_DIR = REPO_ROOT / 'DATASETS' / 'combinatorics_benchmark'
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
TRIAL_OUTPUT = BENCHMARK_DIR / 'combinatorics_validation_trial.jsonl'

PINNED_SOURCES = {
    'primary_paper': {
        'arxiv_id': '1212.0957v1',
        'title': 'The Generalized Stirling Transform',
        'author': 'Mourad Rahmani',
        'year': 2012,
        'pdf_path': 'DATASETS/benchmark_pdfs/1212.0957.pdf',
        'retrieval_date': '2026-10-23',
        'sha256': '1c734a4e0a29c8eae4b94d8033351b62bf8411a78e5d9798b904dcd4e86c14d1',
    },
    'reference_oracle_paper': {
        'arxiv_id': '0806.2366v1',
        'title': 'On a non-combinatorial definition of Stirling numbers',
        'author': 'Milan Janjić',
        'year': 2008,
        'pdf_path': 'DATASETS/benchmark_pdfs/0806.2366.pdf',
        'retrieval_date': '2026-10-23',
        'sha256': 'ed9e309127125306f12da104d810cfb1a7f6cefb8123382f9167d730b2496dde',
    },
    'external_fixtures': {
        'A000110': 'Bell numbers: 1, 1, 2, 5, 15, 52, 203, 877, 4140, 21147',
        'A000670': 'Ordered Bell numbers: 1, 1, 3, 13, 75, 541, 4683, 47293, 545835',
        'A000045': 'Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55',
    }
}


@dataclass
class CombinatoricsBenchmarkCase:
    case_id: str
    source_document: str
    paper_locator: str
    equation_label: str
    source_raw_latex: str
    normalized_expression: str
    input_coefficients: tuple[int, ...]
    claimed_output_coefficients: tuple[int, ...]
    transform_direction: Literal['forward', 'inverse']
    coefficient_convention: Literal['EGF', 'OGF']
    index_base: int
    independent_reference_source: str
    expected_validation_verdict: Literal['pass', 'mismatch']
    extraction_correctness: Literal['verified_exact', 'verified_normalized']


BENCHMARK_CASES = [
    CombinatoricsBenchmarkCase(
        case_id='rahmani_2012_eq1.1_bell_forward',
        source_document='arxiv:1212.0957v1',
        paper_locator='Page 1, Eq (1.1) & Page 6, Example 1',
        equation_label='(1.1) with a_k = 1',
        source_raw_latex='b_n = \\sum_{k=0}^n \\left\\{ \\begin{matrix} n \\\\ k \\end{matrix} \\right\\} a_k, \\quad a_k = 1',
        normalized_expression='b_n = \\sum_{k=0}^n S(n,k) \\cdot 1 = B_n',
        input_coefficients=(1, 1, 1, 1, 1, 1, 1),
        claimed_output_coefficients=(1, 1, 2, 5, 15, 52, 203),
        transform_direction='forward',
        coefficient_convention='EGF',
        index_base=0,
        independent_reference_source='OEIS A000110 & Janjić (2008) Section 3',
        expected_validation_verdict='pass',
        extraction_correctness='verified_exact',
    ),
    CombinatoricsBenchmarkCase(
        case_id='rahmani_2012_eq1.2_bell_inverse',
        source_document='arxiv:1212.0957v1',
        paper_locator='Page 1, Eq (1.2) & Page 6, Example 1 inverse',
        equation_label='(1.2) with b_k = B_k',
        source_raw_latex='a_n = \\sum_{k=0}^n s(n, k) b_k, \\quad b_k = B_k',
        normalized_expression='a_n = \\sum_{k=0}^n s(n,k) B_k = 1',
        input_coefficients=(1, 1, 2, 5, 15, 52, 203),
        claimed_output_coefficients=(1, 1, 1, 1, 1, 1, 1),
        transform_direction='inverse',
        coefficient_convention='EGF',
        index_base=0,
        independent_reference_source='Riordan (1958) & Janjić (2008) Theorem 4',
        expected_validation_verdict='pass',
        extraction_correctness='verified_exact',
    ),
    CombinatoricsBenchmarkCase(
        case_id='rahmani_2012_p1_ordered_bell_forward',
        source_document='arxiv:1212.0957v1',
        paper_locator='Page 1, paragraph 3 (Combinatorial Interpretation)',
        equation_label='Ordered Bell Transform a_k = k!',
        source_raw_latex='b_n = \\sum_{k=0}^n \\left\\{ \\begin{matrix} n \\\\ k \\end{matrix} \\right\\} k!',
        normalized_expression='b_n = \\sum_{k=0}^n S(n,k) k! = F_n',
        input_coefficients=(1, 1, 2, 6, 24, 120, 720),
        claimed_output_coefficients=(1, 1, 3, 13, 75, 541, 4683),
        transform_direction='forward',
        coefficient_convention='EGF',
        index_base=0,
        independent_reference_source='OEIS A000670 & Janjić (2008) Theorem 5',
        expected_validation_verdict='pass',
        extraction_correctness='verified_exact',
    ),
    CombinatoricsBenchmarkCase(
        case_id='rahmani_2012_example2_fibonacci_inverse',
        source_document='arxiv:1212.0957v1',
        paper_locator='Page 6, Example 2 (Fibonacci sequence matrix S row 0)',
        equation_label='Example 2 Matrix S row 0',
        source_raw_latex='a_{0,m} = \\sum_{k=0}^m s(m,k) F_k, \\quad F_n = 0, 1, 1, 2, 3, 5, 8, 13',
        normalized_expression='a_{0,m} = \\sum_{k=0}^m s(m,k) F_k = [0, 1, 0, 1, -4, 19, -108, 719]',
        input_coefficients=(0, 1, 1, 2, 3, 5, 8, 13),
        claimed_output_coefficients=(0, 1, 0, 1, -4, 19, -108, 719),
        transform_direction='inverse',
        coefficient_convention='EGF',
        index_base=0,
        independent_reference_source='Rahmani (2012) Matrix S Row 0 & OEIS A000045',
        expected_validation_verdict='pass',
        extraction_correctness='verified_exact',
    ),
    CombinatoricsBenchmarkCase(
        case_id='negative_control_bell_deliberate_corruption',
        source_document='synthetic://negative_control',
        paper_locator='Mutation Control on A000110',
        equation_label='Corrupted Bell Claim B_4 = 999',
        source_raw_latex='b_n = \\sum_{k=0}^n S(n,k) \\cdot 1, \\quad b_4 = 999',
        normalized_expression='Corrupted Bell sequence: [1, 1, 2, 5, 999, 52, 203]',
        input_coefficients=(1, 1, 1, 1, 1, 1, 1),
        claimed_output_coefficients=(1, 1, 2, 5, 999, 52, 203),
        transform_direction='forward',
        coefficient_convention='EGF',
        index_base=0,
        independent_reference_source='Synthetic mutation check',
        expected_validation_verdict='mismatch',
        extraction_correctness='verified_exact',
    ),
]


def run_benchmark_trial():
    """Execute validation trial on the combinatorics benchmark cases."""
    results = []

    for case in BENCHMARK_CASES:
        if case.transform_direction == 'forward':
            computed = validator_mod.forward_stirling_egf(case.input_coefficients)
        else:
            computed = validator_mod.inverse_stirling_egf(case.input_coefficients)

        # Match check
        matches = computed == case.claimed_output_coefficients
        first_mismatch = None
        if not matches:
            for idx, (c, cl) in enumerate(zip(computed, case.claimed_output_coefficients)):
                if c != cl:
                    first_mismatch = idx
                    break

        verdict = 'pass' if matches else 'mismatch'

        record = {
            'case_id': case.case_id,
            'source_document': case.source_document,
            'paper_locator': case.paper_locator,
            'equation_label': case.equation_label,
            'source_raw_latex': case.source_raw_latex,
            'normalized_expression': case.normalized_expression,
            'transform_direction': case.transform_direction,
            'coefficient_convention': case.coefficient_convention,
            'index_base': case.index_base,
            'input_coefficients': list(case.input_coefficients),
            'computed_coefficients': list(computed),
            'claimed_coefficients': list(case.claimed_output_coefficients),
            'first_mismatch_index': first_mismatch,
            'extraction_correctness': case.extraction_correctness,
            'mathematical_validation_verdict': verdict,
            'expected_verdict': case.expected_validation_verdict,
            'independent_reference_source': case.independent_reference_source,
            'verdict_matches_expected': verdict == case.expected_validation_verdict,
        }
        results.append(record)

    with open(TRIAL_OUTPUT, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # Also save metadata manifest
    manifest_path = BENCHMARK_DIR / 'benchmark_manifest.json'
    manifest_data = {
        'pinned_sources': PINNED_SOURCES,
        'total_cases': len(results),
        'passed_cases': sum(1 for r in results if r['mathematical_validation_verdict'] == 'pass'),
        'mismatch_cases': sum(1 for r in results if r['mathematical_validation_verdict'] == 'mismatch'),
        'all_verdicts_as_expected': all(r['verdict_matches_expected'] for r in results),
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    return results, manifest_data


if __name__ == '__main__':
    records, manifest = run_benchmark_trial()
    print("Combinatorics Benchmark Trial Results:")
    print(f"  Total Cases: {manifest['total_cases']}")
    print(f"  Passed: {manifest['passed_cases']}, Mismatch (expected): {manifest['mismatch_cases']}")
    print(f"  Contract Parity: {manifest['all_verdicts_as_expected']}")
    print(f"  Output: {TRIAL_OUTPUT}")
