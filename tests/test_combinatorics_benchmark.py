"""
Unit tests for Combinatorics Benchmark (arXiv:1212.0957 & arXiv:0806.2366)
=========================================================================
Verifies:
1. Source PDF provenance and immutable SHA-256 checksums.
2. End-to-end forward and inverse Stirling transforms against literature cases.
3. Mutation detection on combinatorial sequences.
"""

import sys
import hashlib
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

from validators.combinatorics_benchmark import PINNED_SOURCES, BENCHMARK_CASES, run_benchmark_trial
from validators.stirling_transform import forward_stirling_egf, inverse_stirling_egf


def test_primary_paper_sha256_provenance():
    """Verify arXiv 1212.0957v1 PDF matches pinned SHA-256."""
    info = PINNED_SOURCES['primary_paper']
    pdf_path = REPO_ROOT / info['pdf_path']
    assert pdf_path.exists(), f"Primary PDF {pdf_path} not found"
    actual_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    assert actual_hash == info['sha256'], f"SHA-256 mismatch: {actual_hash} != {info['sha256']}"


def test_reference_oracle_paper_sha256_provenance():
    """Verify arXiv 0806.2366v1 PDF matches pinned SHA-256."""
    info = PINNED_SOURCES['reference_oracle_paper']
    pdf_path = REPO_ROOT / info['pdf_path']
    assert pdf_path.exists(), f"Reference PDF {pdf_path} not found"
    actual_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    assert actual_hash == info['sha256'], f"SHA-256 mismatch: {actual_hash} != {info['sha256']}"


def test_case1_all_ones_to_bell_numbers():
    """Verify forward Stirling of all-ones sequence yields Bell numbers (OEIS A000110)."""
    case = next(c for c in BENCHMARK_CASES if c.case_id == 'rahmani_2012_eq1.1_bell_forward')
    computed = forward_stirling_egf(case.input_coefficients)
    assert computed == case.claimed_output_coefficients
    assert computed == (1, 1, 2, 5, 15, 52, 203)


def test_case2_bell_numbers_inverse_to_all_ones():
    """Verify inverse Stirling of Bell numbers yields all-ones sequence."""
    case = next(c for c in BENCHMARK_CASES if c.case_id == 'rahmani_2012_eq1.2_bell_inverse')
    computed = inverse_stirling_egf(case.input_coefficients)
    assert computed == case.claimed_output_coefficients
    assert computed == (1, 1, 1, 1, 1, 1, 1)


def test_case3_factorials_to_ordered_bell_numbers():
    """Verify forward Stirling of factorials yields ordered Bell numbers (OEIS A000670)."""
    case = next(c for c in BENCHMARK_CASES if c.case_id == 'rahmani_2012_p1_ordered_bell_forward')
    computed = forward_stirling_egf(case.input_coefficients)
    assert computed == case.claimed_output_coefficients
    assert computed == (1, 1, 3, 13, 75, 541, 4683)


def test_case4_fibonacci_inverse_matches_rahmani_matrix_row0():
    """Verify inverse Stirling of Fibonacci yields Rahmani (2012) Matrix S row 0."""
    case = next(c for c in BENCHMARK_CASES if c.case_id == 'rahmani_2012_example2_fibonacci_inverse')
    computed = inverse_stirling_egf(case.input_coefficients)
    assert computed == case.claimed_output_coefficients
    assert computed == (0, 1, 0, 1, -4, 19, -108, 719)


def test_case5_negative_control_flags_mismatch():
    """Verify deliberate corruption of Bell claim is flagged at index 4."""
    case = next(c for c in BENCHMARK_CASES if c.case_id == 'negative_control_bell_deliberate_corruption')
    computed = forward_stirling_egf(case.input_coefficients)
    assert computed != case.claimed_output_coefficients
    # Find mismatch index
    first_diff = next(i for i, (a, b) in enumerate(zip(computed, case.claimed_output_coefficients)) if a != b)
    assert first_diff == 4


def test_full_benchmark_trial_contract_parity():
    """Verify run_benchmark_trial executes cleanly with 100% expected verdict matching."""
    records, manifest = run_benchmark_trial()
    assert manifest['total_cases'] == 5
    assert manifest['passed_cases'] == 4
    assert manifest['mismatch_cases'] == 1
    assert manifest['all_verdicts_as_expected'] is True
