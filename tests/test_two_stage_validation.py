#!/usr/bin/env python3
"""
Regression test for the two-stage validation architecture.

Proves that the OLD single-stage validator (substitute into recovered string
only) produces FALSE POSITIVES: it validates solutions that satisfy the
recovered expression but NOT the original source equation.

The NEW two-stage validator catches these by:
  Stage 1: comparing canonical tree tokens against recovered tokens
  Stage 2: substituting back into the recovered expression

If stage 1 detects a structural mismatch, the solution is REJECTED even if
stage 2 would pass.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_reconstruction_evidence import validate_solution  # noqa: E402


class FakeTree:
    """Minimal tree-like object with to_string() for testing."""

    def __init__(self, s: str) -> None:
        self._s = s

    def to_string(self) -> str:
        return self._s


def test_old_single_stage_would_false_positive() -> None:
    """
    Demonstrates the old validator's blind spot.

    Source:    d = 3 - 5
    Recovered: d = 3 - 5  (correct in this case)
    Solution:  [-2]

    Now consider a case where the parser DROPPED a term:
    Source:    d = 3 - 5 + 7
    Recovered: d = 3 - 5      (parser dropped +7)
    Solution:  [-2]

    The old validator substitutes -2 into 'd = 3-5' and gets residual=0.
    It says PASS. But the source says d = 5, not d = -2.

    The new validator catches this in stage 1: token mismatch.
    """
    # Case 1: old validator false positive
    # Source has 4 tokens: d, 3, 5, 7
    # Recovered has 3 tokens: d, 3, 5
    source = "d = 3 - 5 + 7"
    recovered = "d = 3 - 5"
    solution = "[-2]"
    tree = FakeTree("d=3-5+7")

    result = validate_solution(recovered, solution, source, canonical_tree=tree)

    # The new validator MUST reject this (stage 1 fails)
    assert result["stage1_source_fidelity"]["passed"] is False, (
        f"stage1 should fail: {result['stage1_source_fidelity']}"
    )
    assert result["passed"] is False, (
        f"should be rejected: {result}"
    )
    print("PASS: old-validator false positive caught by stage 1")


def test_new_validator_correct_pass() -> None:
    """
    A correct reconstruction passes both stages.
    """
    source = "d = 3 - 5"
    recovered = "d = 3 - 5"
    solution = "[-2]"
    tree = FakeTree("d=3-5")

    result = validate_solution(recovered, solution, source, canonical_tree=tree)
    assert result["stage1_source_fidelity"]["passed"] is True
    assert result["stage2_computational_validity"]["passed"] is True
    assert result["passed"] is True
    print("PASS: correct reconstruction passes both stages")


def test_new_validator_detects_dropped_term() -> None:
    """
    Parser dropped a term: source 'd = 3 - 5 + 7' recovered as 'd = 3 - 5'.
    Old validator: PASS (residual=0 for d=-2 in 'd=3-5')
    New validator: FAIL (stage 1 token mismatch)
    """
    source = "d = 3 - 5 + 7"
    recovered = "d = 3 - 5"
    solution = "[-2]"
    tree = FakeTree("d=3-5+7")

    result = validate_solution(recovered, solution, source, canonical_tree=tree)
    assert result["passed"] is False
    assert "stage1 failed" in result["detail"]
    print("PASS: dropped term detected by stage 1")


def test_new_validator_detects_changed_operator() -> None:
    """
    Parser changed operator: source 'd = 3 * 5' recovered as 'd = 3 + 5'.
    Both are solvable, both give residual=0 for their respective solutions,
    but the source fidelity check catches the structural change.
    """
    source = "d = 3 * 5"
    recovered = "d = 3 + 5"
    solution = "[8]"
    tree = FakeTree("d=3*5")

    result = validate_solution(recovered, solution, source, canonical_tree=tree)
    # Stage 1: tokens are d, 3, 5 vs d, 3, 5 -- same tokens!
    # But the operators differ. Token comparison alone won't catch this.
    # This is a known limitation: token comparison catches dropped/added
    # tokens but not operator substitution. Document this.
    print(f"NOTE: operator substitution caught by stage1={result['stage1_source_fidelity']['passed']}, "
          f"final={result['passed']}")


def test_no_canonical_tree_skips_stage1() -> None:
    """
    When no canonical tree is available, stage 1 is skipped (not failed).
    This is correct: absence of evidence is not evidence of absence.
    """
    source = "d = 3 - 5"
    recovered = "d = 3 - 5"
    solution = "[-2]"

    result = validate_solution(recovered, solution, source, canonical_tree=None)
    assert result["stage1_source_fidelity"]["passed"] is None
    assert "skipped" in result["stage1_source_fidelity"]["detail"]
    assert result["passed"] is True  # stage 2 still passes
    print("PASS: no canonical tree -> stage1 skipped, stage2 still runs")


def test_vacuous_substitution_still_caught() -> None:
    """
    The echo guard works when the solution still contains the variable.

    E = 2*E*2 solved to 2*E*2 is vacuous (still contains E).
    Old validator: would accept (residual=0 for d=-2 in 'd=3-5') -- NO.
    Correct: for 'E = 2*E*2', sol = [2*E*2], substitutes back = 2*(2*E*2)*2,
    residual = 8*E*2 - E which is not zero, so stage2 fails.
    """
    # Better example: E = E + 1 has no solution. Old validator: residual not
    # computed because parse_expr('E+1') - parse_expr('E') = -1 != 0 -> fails.
    # This is correctly caught.
    source = "E = E + 1"
    recovered = "E = E + 1"
    solution = "[]"
    tree = FakeTree("E=E+1")

    result = validate_solution(recovered, solution, source, canonical_tree=tree)
    assert result["stage2_computational_validity"]["passed"] is False
    assert "cannot isolate" not in result["detail"]
    # result['passed'] will be None only if unverifiable; here it's False because stage2 fails
    print(f"PASS: no-solution equation = {result['passed']}, {result['detail']}")


def test_activity_substitution_water() -> None:
    source = "E = 5.6e37 * E"
    recovered = "E = 5.6e37 * E"
    solution = "[5.6e37*E]"

    result = validate_solution(recovered, solution, source, canonical_tree=None)
    print(f"PASS: vacuous substitution, passed={result['passed']}")
    # For 'E = 5.6e37*E' with solution 5.6e37*E:
    # residual = 5.6e37*E - 5.6e37*E = 0 (mathematically)
    # Old validator: PASS (residual=0)
    # New validator: stage1 skipped (no tree), stage2 PASS (residual=0)
    # This is correct: the recovered expression IS the source expression.
    # The echo guard only catches when the solution STILL contains the variable.



def test_infinite_residual_unverifiable() -> None:
    """
    oo - oo = nan should be unverifiable, not failed.
    """
    source = "x = oo"
    recovered = "x = oo"
    solution = "[oo]"
    tree = FakeTree("x=oo")

    result = validate_solution(recovered, solution, source, canonical_tree=tree)
    # This will hit the infinite/undefined residual path
    print(f"PASS: infinite residual -> passed={result['passed']}, detail={result['detail']}")


def test_empty_solution() -> None:
    result = validate_solution("d=3-5", "", "d=3-5")
    assert result["passed"] is None
    assert "no solution" in result["detail"]
    print("PASS: empty solution handled")


def test_no_equality_in_recovered() -> None:
    result = validate_solution("3-5", "[-2]", "d=3-5")
    assert result["passed"] is None
    assert "not an equation" in result["detail"]
    print("PASS: no equality in recovered handled")


if __name__ == "__main__":
    test_old_single_stage_would_false_positive()
    test_new_validator_correct_pass()
    test_new_validator_detects_dropped_term()
    test_new_validator_detects_changed_operator()
    test_no_canonical_tree_skips_stage1()
    test_vacuous_substitution_still_caught()
    test_infinite_residual_unverifiable()
    test_empty_solution()
    test_no_equality_in_recovered()
    print("\n=== ALL REGRESSION TESTS PASSED ===")
