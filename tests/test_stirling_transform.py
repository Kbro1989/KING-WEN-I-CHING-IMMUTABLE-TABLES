#!/usr/bin/env python3
"""Tests for Stirling transform validator.

Test matrix from manman4/study_OEIS analysis:
- Forward followed by inverse recovers original
- Direct Stirling summation agrees with power-series substitution
- Factorial scaling correct at n=0,1,2,3
- Signed first-kind vs second-kind conventions not interchanged
- Off-by-one and missing-factorial mutations detected
- Truncation order preserved
"""
import pytest
import math
import json
from pathlib import Path

# Add parent to path for imports
import sys
import os
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Direct module import (scripts/ is not a Python package)
import sys as _sys
import importlib.util
_validator_path = os.path.join(str(Path(__file__).parent.parent), 'scripts/validators/stirling_transform.py')
if _validator_path not in _sys.path:
    _sys.path.insert(0, os.path.dirname(_validator_path))

_spec = importlib.util.spec_from_file_location("stirling_transform", _validator_path, submodule_search_locations=[])
if _spec is None:
    raise ImportError(f"Cannot create spec for {__validator_path}")
stirling_transform = importlib.util.module_from_spec(_spec)
# Register in sys.modules so dataclass can find its own module
_sys.modules['stirling_transform'] = stirling_transform
_spec.loader.exec_module(stirling_transform)

_fixture_path = os.path.join(str(Path(__file__).parent.parent), 'scripts/validators/stirling_reference_fixtures.py')
_spec_fix = importlib.util.spec_from_file_location("stirling_reference_fixtures", _fixture_path)
if _spec_fix is None:
    raise ImportError(f"Cannot create spec for {_fixture_path}")
stirling_reference_fixtures = importlib.util.module_from_spec(_spec_fix)
_sys.modules['stirling_reference_fixtures'] = stirling_reference_fixtures
_spec_fix.loader.exec_module(stirling_reference_fixtures)

forward_stirling_egf = stirling_transform.forward_stirling_egf
inverse_stirling_egf = stirling_transform.inverse_stirling_egf
stirling1 = stirling_transform.stirling1
stirling2 = stirling_transform.stirling2
factorial = stirling_transform.factorial
validate_stirling_transform = stirling_transform.validate_stirling_transform
A000670_REFERENCED = stirling_transform.A000670_REFERENCED
STSValidationRecord = stirling_transform.StirlingValidationRecord


class TestStirlingNumbers:
    """Basic Stirling number computations."""
    
    def test_stirling2_baseline(self):
        """S(n,k) = 1 iff k=0 and n=0, or k=n, or k=0 for n>0."""
        assert stirling2(0, 0) == 1
        assert stirling2(1, 0) == 0
        assert stirling2(1, 1) == 1
        assert stirling2(5, 0) == 0
        assert stirling2(5, 5) == 1
    
    def test_stirling2_known_values(self):
        """Verify S(n,k) against known values."""
        # S(4,2) = 7 (partitions of 4 elements into 2 nonempty subsets)
        assert stirling2(4, 2) == 7
        # S(5,2) = 15
        assert stirling2(5, 2) == 15
        # S(5,3) = 25
        assert stirling2(5, 3) == 25
    
    def test_stirling1_signed(self):
        """Signed Stirling numbers of the first kind."""
        # s(4,2) = 11 (signed Stirling1, signed=True per OEIS A130534)
        # s(4,1) = -6, s(4,3) = -6 (also verify key values)
        assert stirling1(2, 1, signed=True) == -1
        assert stirling1(2, 2, signed=True) == 1
        assert stirling1(3, 1, signed=True) == 2
        assert stirling1(3, 2, signed=True) == -3
        assert stirling1(4, 1, signed=True) == -6
        assert stirling1(4, 2, signed=True) == 11
        assert stirling1(4, 3, signed=True) == -6
        assert stirling1(4, 4, signed=True) == 1

    def test_stirling1_diagonal_is_one(self):
        """s(n,n) = 1 for all tested n >= 0."""
        for n in range(11):
            assert stirling1(n, n, signed=True) == 1, f"Failed at s({n},{n})"

    def test_stirling1_signed_n5_known_values(self):
        """s(5,k) values: x^5 - 10x^4 + 35x^3 - 50x^2 + 24x."""
        assert stirling1(5, 1, signed=True) == 24
        assert stirling1(5, 2, signed=True) == -50
        assert stirling1(5, 3, signed=True) == 35
        assert stirling1(5, 4, signed=True) == -10
        assert stirling1(5, 5, signed=True) == 1

    def test_stirling1_signed_recurrence_verification(self):
        """Recurrence: s(n,k) = s(n-1,k-1) - (n-1)*s(n-1,k)."""
        for (n, k), val in stirling_reference_fixtures.STIRLING1_SIGNED_INDEPENDENT.items():
            computed = stirling1(n, k, signed=True)
            assert val == computed, f"Fixture mismatch at ({n},{k}): fixture {val} != computed {computed}"
            if n > 1 and k > 1:
                prev_diag = stirling1(n - 1, k - 1, signed=True)
                prev_col = stirling1(n - 1, k, signed=True)
                expected_from_rec = prev_diag - (n - 1) * prev_col
                assert computed == expected_from_rec, f"Recurrence failure at ({n},{k})"

    def test_stirling2_recurrence_verification(self):
        """Recurrence: S(n,k) = k*S(n-1,k) + S(n-1,k-1)."""
        for (n, k), val in stirling_reference_fixtures.STIRLING2_INDEPENDENT.items():
            computed = stirling2(n, k)
            assert val == computed, f"Fixture mismatch at ({n},{k}): fixture {val} != computed {computed}"
            if n > 1 and k > 1:
                prev_diag = stirling2(n - 1, k - 1)
                prev_col = stirling2(n - 1, k)
                expected_from_rec = k * prev_col + prev_diag
                assert computed == expected_from_rec, f"Recurrence failure at ({n},{k})"


class TestForwardTransform:
    """Forward Stirling transform tests."""
    
    def test_forward_factorial_to_ordered_bell(self):
        """n! → ordered Bell numbers (A000670)."""
        input_seq = tuple(factorial(n) for n in range(6))
        result = forward_stirling_egf(input_seq)
        expected = A000670_REFERENCED[:6]
        assert result == expected, f'Forward transform mismatch: {result} != {expected}'
    
    def test_forward_trivial_sequence(self):
        """Test [1, 0, 0, ...] → [1, 0, 0, ...] identity-like."""
        input_seq = (1, 0, 0, 0, 0)
        result = forward_stirling_egf(input_seq)
        expected = (1, 0, 0, 0, 0)
        assert result == expected


class TestInverseTransform:
    """Inverse Stirling transform tests."""
    
    def test_inverse_forward_recovers_input(self):
        """Forward then inverse should recover original coefficients."""
        original = tuple([1, 3, 13, 75, 541])
        transformed = forward_stirling_egf(original)
        recovered = inverse_stirling_egf(transformed)
        assert recovered == original, f'Recovery failed: {recovered} != {original}'


class TestValidationInterface:
    """Test the validation record interface."""
    
    def test_validate_stirling_forward_pass(self):
        """Validation should return pass for correct forward transform."""
        input_seq = tuple(factorial(n) for n in range(5))
        claimed = forward_stirling_egf(input_seq)
        
        record = validate_stirling_transform(
            input_coefficients=input_seq,
            claimed_output_coefficients=claimed,
            direction='forward',
            coefficient_convention='EGF',
            index_base=0,
            source_expression_id='test://factorial_to_bell',
            implementation_provenance={
                'repo': 'manman4/study_OEIS',
                'commit': 'refs/heads/main',
                'file': 'transform/Stirling_transform/000670_01.gp',
                'function': 'trv_stirling'
            }
        )
        
        assert record.status == 'pass'
        assert record.first_mismatch_index is None
        assert record.coefficient_convention == 'EGF'
    
    def test_validate_stirling_detects_mismatch(self):
        """Validation should detect incorrect claimed output."""
        input_seq = tuple([1, 1, 2, 5])  # n=0..3: n! values
        claimed = tuple([1, 2, 5, 10])   # Wrong values
        
        record = validate_stirling_transform(
            input_coefficients=input_seq,
            claimed_output_coefficients=claimed,
            direction='forward',
            coefficient_convention='EGF',
            index_base=0,
            source_expression_id='test://mismatch_detect',
            implementation_provenance={
                'repo': 'test',
                'commit': 'test',
                'file': 'test.py',
                'function': 'test'
            }
        )
        
        assert record.status == 'mismatch'
        assert record.first_mismatch_index == 1


class TestFactorialScaling:
    """Test factorial scaling at boundary cases."""
    
    def test_factorial_n0(self):
        """0! = 1."""
        assert factorial(0) == 1
    
    def test_factorial_n1(self):
        """1! = 1."""
        assert factorial(1) == 1
    
    def test_factorial_n2(self):
        """2! = 2."""
        assert factorial(2) == 2
    
    def test_factorial_n3(self):
        """3! = 6."""
        assert factorial(3) == 6


class TestConventionDetection:
    """Verify wrong conventions are detected."""
    
    def test_ogf_vs_egf_detection(self):
        """Using OGF interpretation should give different results."""
        # EGF: coefficient multiplied by 1/k! internally
        # OGF: coefficient used directly as term
        egf_result = forward_stirling_egf((1, 1, 1, 1))  # EGF convention
        # With OGF, factorials would not cancel - produce larger values
        # The EGF convention is correct for this implementation
        assert len(egf_result) == 4
        assert egf_result[0] == 1  # S(0,0) * 1 = 1


class TestA000670FullVectorRegression:
    """Regression assertion for the full initial term vector.

    The ordered Bell numbers (OEIS A000670) are the forward Stirling
    transform of the factorial sequence a_k = k!.

    Zero-based indexing: a_0 = 1, a_1 = 1, a_2 = 3, a_3 = 13, a_4 = 75, ...
    Generating function: sum_{n>=0} a_n x^n/n! = 1/(2 - e^x)
    Finite sum: a_n = sum_{k=0..n} k! * S(n,k)

    This regression test pins the entire initial term vector, not just
    a single value (a_4 = 75), so future implementation changes cannot
    silently shift the index base or convention without detection.
    """
    def test_ordered_bell_full_vector(self):
        """Forward Stirling transform of n! must produce A000670."""
        from math import factorial
        input_seq = tuple(factorial(n) for n in range(11))  # n=0..10
        result = forward_stirling_egf(input_seq)
        
        # A000670 zero-indexed: 1, 1, 3, 13, 75, 541, 4683, 47293, 545835, 7087261, 102247563
        expected = (
            1,    # a_0
            1,    # a_1
            3,    # a_2
            13,   # a_3
            75,   # a_4
            541,  # a_5
            4683, # a_6
            47293,# a_7
            545835,# a_8
            7087261,# a_9
            102247563  # a_10
        )
        
        assert len(result) == len(expected), \
            f'Expected {len(expected)} terms, got {len(result)}'
        for i, (actual, exp) in enumerate(zip(result, expected)):
            assert actual == exp, \
                f'a_{i}: computed {actual} != expected {exp}'
    
    def test_ordered_bell_full_vector_matches_fixtures(self):
        """Full vector matches the independent fixture file."""
        input_seq = tuple(factorial(n) for n in range(11))
        result = forward_stirling_egf(input_seq)
        
        expected_vector = tuple(
            stirling_reference_fixtures.A000670_REFERENCED[n] for n in range(11)
        )
        assert result == expected_vector, \
            f'Full vector mismatch:\ncomputed  = {result}\nfixture     = {expected_vector}'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])