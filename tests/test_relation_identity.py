"""
Regression test for relation identity preservation (P1 fix).

Verifies that recover_latex preserves distinct mathematical relations
as typed tokens instead of collapsing them all to '=', and that
solve_recovered refuses to solve non-equality relations.

Run:  PYTHONPATH=. python -m pytest tests/test_relation_identity.py -v
"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from math_recovery_tool import recover_latex, solve_recovered


# --- Non-equality relations that must NOT collapse to '=' ---

NON_EQUALITY_RELATIONS = [
    (r"a \approx b", "approx"),
    (r"a \sim b", "sim"),
    (r"a \simeq b", "simeq"),
    (r"a \cong b", "cong"),
    (r"a \propto b", "propto"),
    (r"a \equiv b", "equiv"),
    (r"a \subseteq b", "subseteq"),
    (r"a \supseteq b", "supseteq"),
    (r"a \subset b", "subset"),
    (r"a \supset b", "supset"),
    (r"a \Rightarrow b", "Rightarrow"),
    (r"a \Leftarrow b", "Leftarrow"),
    (r"a \Leftrightarrow b", "Leftrightarrow"),
    (r"a \rightarrow b", "rightarrow"),
    (r"a \leftarrow b", "leftarrow"),
    (r"a \mapsto b", "mapsto"),
    (r"a \to b", "to"),
    (r"a \gets b", "gets"),
    (r"a \implies b", "implies"),
    (r"a \iff b", "iff"),
]

# --- Relations that ARE solver-compatible (inequalities) ---

INEQUALITY_RELATIONS = [
    (r"a \leq b", "<="),
    (r"a \geq b", ">="),
    (r"a \ll b", "<"),
    (r"a \gg b", ">"),
]

# --- True equality ---

TRUE_EQUALITY = [
    (r"a = b", "="),
]


class TestRelationIdentity:
    """Non-equality relations must be preserved as typed tokens, not collapsed."""

    @pytest.mark.parametrize("latex,expected_token", NON_EQUALITY_RELATIONS)
    def test_non_equality_relation_preserved(self, latex, expected_token):
        """recover_latex must emit the typed token, not '='."""
        recovered, _ = recover_latex(latex)
        assert expected_token in recovered, (
            f"{latex}: expected '{expected_token}' in recovered, got '{recovered}'"
        )
        # Must NOT contain a bare '=' (which would fabricate an equation)
        assert "=" not in recovered or expected_token == "=", (
            f"{latex}: recovered '{recovered}' contains '=', "
            f"which fabricates an equation the source never stated"
        )

    @pytest.mark.parametrize("latex,expected_token", INEQUALITY_RELATIONS)
    def test_inequality_preserved(self, latex, expected_token):
        """Inequalities map to their solver-compatible ASCII form."""
        recovered, _ = recover_latex(latex)
        assert expected_token in recovered, (
            f"{latex}: expected '{expected_token}' in recovered, got '{recovered}'"
        )

    @pytest.mark.parametrize("latex,expected_token", TRUE_EQUALITY)
    def test_true_equality_preserved(self, latex, expected_token):
        """True equality still maps to '='."""
        recovered, _ = recover_latex(latex)
        assert expected_token in recovered, (
            f"{latex}: expected '{expected_token}' in recovered, got '{recovered}'"
        )


class TestSolverRefusesNonEquality:
    """solve_recovered must refuse to solve non-equality relations."""

    @pytest.mark.parametrize("latex,_", NON_EQUALITY_RELATIONS)
    def test_solver_refuses_non_equality(self, latex, _):
        """Solver must reject non-equality relations, not fabricate solutions."""
        recovered, _ = recover_latex(latex)
        success, result, error, variables, preserved = solve_recovered(recovered, latex)
        assert not success, (
            f"{latex}: solver accepted non-equality relation as solvable. "
            f"recovered='{recovered}', result='{result}'"
        )
        assert "relation" in str(error) or "no_equality" in str(error), (
            f"{latex}: expected relation/no_equality error, got '{error}'"
        )

    @pytest.mark.parametrize("latex,_", TRUE_EQUALITY)
    def test_solver_accepts_true_equality(self, latex, _):
        """Solver must still accept true equalities."""
        recovered, _ = recover_latex(latex)
        success, result, error, variables, preserved = solve_recovered(recovered, latex)
        assert success, (
            f"{latex}: solver rejected true equality. "
            f"recovered='{recovered}', error='{error}'"
        )


class TestNoFabricatedSolutions:
    """The false-positive class from the P1 audit must be eliminated."""

    FALSE_POSITIVE_INPUTS = [
        r"x \sim q(x)",
        r"p \approx q",
        r"f \propto g",
        r"A \Rightarrow B",
        r"P \cong Q",
    ]

    @pytest.mark.parametrize("latex", FALSE_POSITIVE_INPUTS)
    def test_no_fabricated_solution(self, latex):
        """The solver must not report success on relations it cannot solve."""
        recovered, _ = recover_latex(latex)
        success, result, error, variables, preserved = solve_recovered(recovered, latex)
        assert not success, (
            f"FALSE POSITIVE: {latex} was accepted as solvable. "
            f"recovered='{recovered}', result='{result}', error='{error}'"
        )
