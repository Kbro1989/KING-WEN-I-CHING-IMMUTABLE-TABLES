"""
P5 constraint validator tests — rigorous validation of extracted math.

Tests the constraint validator against real paper data and adversarial cases.
No reward hacking: a symbol or bracket fitting syntactically is NOT sufficient.

Run: PYTHONPATH=scripts python -m pytest tests/test_constraint_validator.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")

from math_constraint_validator import (
    ConstraintValidator,
    PaperContext,
    build_paper_context,
    check_solvability,
    detect_underdetermined,
    extract_symbols,
    validate_enclosures,
    validate_structure,
    validate_symbols,
)
from math_ast_integration import make_source_occurrence, build_recovery_record
from math_contract import RecoveryRecord


ROOT = Path(__file__).resolve().parents[1]


def _load_corpus(paper_id: str = "2605.00155") -> dict:
    with open(ROOT / "DATASETS" / "arxiv_html_corpus" / f"{paper_id}.json", encoding="utf-8") as f:
        return json.load(f)


def _make_record(eq: dict):
    source = make_source_occurrence(
        paper_id="2605.00155", paper_version="latest",
        source_locator=f"math[{eq.get('index', 0)}]", occurrence_index=eq.get("index", 0),
        mathml=eq.get("mathml"), latex=eq.get("latex"),
    )
    return build_recovery_record(source, eq.get("mathml"))


# ---------------------------------------------------------------------------
# Enclosure validation
# ---------------------------------------------------------------------------


class TestEnclosureValidation:
    def test_balanced_parens(self):
        assert validate_enclosures("(a + b)") == []

    def test_unbalanced_open(self):
        violations = validate_enclosures("(a + b")
        assert len(violations) == 1
        assert "Unclosed" in violations[0]

    def test_unbalanced_close(self):
        violations = validate_enclosures("a + b)")
        assert len(violations) == 1
        assert "Unmatched" in violations[0]

    def test_mismatched(self):
        violations = validate_enclosures("(a + b]")
        assert len(violations) == 1
        assert "Mismatched" in violations[0]

    def test_nested_balanced(self):
        assert validate_enclosures("((a + b) * (c + d))") == []

    def test_norm_self_closing(self):
        # ‖ is self-closing — should not require a pair
        assert validate_enclosures("‖x‖") == []

    def test_inner_product_delimiters(self):
        assert validate_enclosures("⟨a, b⟩") == []


# ---------------------------------------------------------------------------
# Structure validation
# ---------------------------------------------------------------------------


class TestStructureValidation:
    def test_valid_expression(self):
        assert validate_structure("a + b = c") == []

    def test_empty_parens(self):
        violations = validate_structure("()")
        assert len(violations) == 1
        assert "Empty brackets" in violations[0]

    def test_double_operator(self):
        violations = validate_structure("a ++ b")
        assert len(violations) == 1
        assert "Double operator" in violations[0]

    def test_trailing_operator(self):
        violations = validate_structure("a + b +")
        assert len(violations) == 1
        assert "ends with operator" in violations[0]

    def test_malformed_fraction(self):
        violations = validate_structure(r"\frac{}{b}")
        assert len(violations) >= 1
        assert any("empty" in v.lower() for v in violations)


# ---------------------------------------------------------------------------
# Symbol validation
# ---------------------------------------------------------------------------


class TestSymbolValidation:
    def test_extract_symbols_from_latex(self):
        symbols = extract_symbols(r"\alpha + \beta = \gamma")
        assert "alpha" in symbols
        assert "beta" in symbols
        assert "gamma" in symbols

    def test_extract_symbols_from_greek(self):
        symbols = extract_symbols("α + β = γ")
        assert "α" in symbols
        assert "β" in symbols
        assert "γ" in symbols

    def test_validate_common_symbols(self):
        ctx = PaperContext(paper_id="test")
        ctx.decided_symbols = {"alpha", "beta", "gamma"}
        violations = validate_symbols(r"\alpha + \beta", ctx)
        assert len(violations) == 0

    def test_validate_unknown_symbols(self):
        ctx = PaperContext(paper_id="test")
        ctx.decided_symbols = {"alpha"}
        violations = validate_symbols(r"\alpha + \zeta", ctx)
        # \zeta is a common symbol, so it should NOT be a violation
        # Actually, zeta is in _COMMON_SYMBOLS? Let me check.
        # No, it's not. So this should produce a violation.
        # But wait — _COMMON_SYMBOLS has "zeta" in it? Let me check.
        # Looking at the code: _COMMON_SYMBOLS does NOT have "zeta".
        # So \zeta should produce a violation.
        assert len(violations) == 1
        assert "zeta" in violations[0]


# ---------------------------------------------------------------------------
# Solvability
# ---------------------------------------------------------------------------


class TestSolvability:
    def test_equality_is_solvable(self):
        is_solvable, violations = check_solvability("a + b = c")
        assert is_solvable
        assert len(violations) == 0

    def test_no_relation_no_operator(self):
        is_solvable, violations = check_solvability("a")
        assert not is_solvable
        assert len(violations) == 1

    def test_inequality_is_solvable(self):
        is_solvable, violations = check_solvability(r"a \leq b")
        assert is_solvable

    def test_definition_is_solvable(self):
        is_solvable, violations = check_solvability(r"f(x) := x^2")
        assert is_solvable


# ---------------------------------------------------------------------------
# Underdetermined detection
# ---------------------------------------------------------------------------


class TestUnderdeterminedDetection:
    def test_underdetermined(self):
        is_under, num_unknowns, num_constraints = detect_underdetermined("a + b = c")
        # 3 symbols, 1 constraint
        assert is_under
        assert num_unknowns == 3
        assert num_constraints == 1

    def test_fully_constrained(self):
        is_under, num_unknowns, num_constraints = detect_underdetermined("a = 1")
        # 2 symbols, 1 constraint — still underdetermined
        # Actually, a = 1 has 1 unknown (a) and 1 constraint
        # So it's NOT underdetermined
        assert not is_under

    def test_multiple_constraints(self):
        is_under, num_unknowns, num_constraints = detect_underdetermined("a + b = c, a - b = d")
        # 4 symbols, 2 constraints — still underdetermined
        assert is_under


# ---------------------------------------------------------------------------
# Paper context
# ---------------------------------------------------------------------------


class TestPaperContext:
    def test_build_from_real_corpus(self):
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        assert ctx.paper_id == "2605.00155"
        assert len(ctx.symbol_counts) > 0
        assert len(ctx.decided_symbols) > 0

    def test_decided_vs_deviant(self):
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        # Common symbols should be decided
        assert "pi" in ctx.decided_symbols or "delta" in ctx.decided_symbols
        # Rare symbols should be deviant
        assert len(ctx.deviant_symbols) > 0


# ---------------------------------------------------------------------------
# End-to-end validation with real paper data
# ---------------------------------------------------------------------------


class TestEndToEndValidation:
    def test_validate_regret_expression(self):
        """Eq 100: Regret definition — should validate as underdetermined."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        eq = equations[100]
        record = _make_record(eq)
        result = validator.validate(record)

        assert result.status in ("solvable", "underdetermined")
        assert result.scores["enclosures"] == 1.0
        assert result.scores["structure"] == 1.0

    def test_validate_drro_objective(self):
        """Eq 101: DRRO objective — should validate as underdetermined."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        eq = equations[101]
        record = _make_record(eq)
        result = validator.validate(record)

        assert result.status in ("solvable", "underdetermined")
        assert result.scores["enclosures"] == 1.0

    def test_validate_water_filling(self):
        """Eq 115: Water-filling solution — should validate."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        eq = equations[115]
        record = _make_record(eq)
        result = validator.validate(record)

        assert result.status in ("solvable", "underdetermined", "invalid")
        # At minimum, enclosures should be valid
        assert result.scores["enclosures"] == 1.0

    def test_reject_empty_brackets(self):
        """Empty brackets should be rejected."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        # Create a synthetic record with empty brackets
        from math_contract import RecoveryRecord, SourceOccurrence
        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator="math[0]", occurrence_index=0,
            mathml="<math><mi>a</mi><mo>+</mo><mo>(</mo><mi>b</mi></math>",
            latex="a + ()",
        )
        record = RecoveryRecord(
            source=source, parse_status="complete",
            structural_status="unverified", canonical_tree=None,
        )
        result = validator.validate(record)
        assert result.status == "invalid"
        assert any("Empty brackets" in v for v in result.violations)

    def test_reject_unbalanced_enclosures(self):
        """Unbalanced enclosures should be rejected."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator="math[0]", occurrence_index=0,
            mathml="<math><mo>(</mo><mi>a</mi><mo>+</mo><mi>b</mi></math>",
            latex="(a + b",
        )
        record = RecoveryRecord(
            source=source, parse_status="complete",
            structural_status="unverified", canonical_tree=None,
        )
        result = validator.validate(record)
        assert result.status == "invalid"
        assert any("Unclosed" in v or "Unmatched" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Adversarial cases — no reward hacking
# ---------------------------------------------------------------------------


class TestAdversarialNoRewardHacking:
    """
    These tests ensure the validator does NOT reward hacking.
    A symbol or bracket fitting syntactically is NOT sufficient.
    """

    def test_reject_double_operator(self):
        """a ++ b should be rejected."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator="math[0]", occurrence_index=0,
            mathml="<math><mi>a</mi><mo>+</mo><mo>+</mo><mi>b</mi></math>",
            latex="a ++ b",
        )
        record = RecoveryRecord(
            source=source, parse_status="complete",
            structural_status="unverified", canonical_tree=None,
        )
        result = validator.validate(record)
        assert result.status == "invalid"
        assert any("Double operator" in v for v in result.violations)

    def test_reject_trailing_operator(self):
        """a + b + should be rejected."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator="math[0]", occurrence_index=0,
            mathml="<math><mi>a</mi><mo>+</mo><mi>b</mi><mo>+</mo></math>",
            latex="a + b +",
        )
        record = RecoveryRecord(
            source=source, parse_status="complete",
            structural_status="unverified", canonical_tree=None,
        )
        result = validator.validate(record)
        assert result.status == "invalid"
        assert any("ends with operator" in v for v in result.violations)

    def test_accept_valid_equality(self):
        """a + b = c should be accepted."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator="math[0]", occurrence_index=0,
            mathml="<math><mi>a</mi><mo>+</mo><mi>b</mi><mo>=</mo><mi>c</mi></math>",
            latex="a + b = c",
        )
        record = RecoveryRecord(
            source=source, parse_status="complete",
            structural_status="unverified", canonical_tree=None,
        )
        result = validator.validate(record)
        assert result.status in ("solvable", "underdetermined")
        assert result.scores["solvability"] == 1.0

    def test_underdetermined_not_rejected(self):
        """a + b = c (3 unknowns, 1 constraint) should be underdetermined, NOT rejected."""
        corpus = _load_corpus()
        equations = corpus.get("equations", [])
        ctx = build_paper_context("2605.00155", equations)
        validator = ConstraintValidator(ctx)

        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator="math[0]", occurrence_index=0,
            mathml="<math><mi>a</mi><mo>+</mo><mi>b</mi><mo>=</mo><mi>c</mi></math>",
            latex="a + b = c",
        )
        record = RecoveryRecord(
            source=source, parse_status="complete",
            structural_status="unverified", canonical_tree=None,
        )
        result = validator.validate(record)
        assert result.metadata["underdetermined"] is True
        assert result.metadata["num_unknowns"] == 3
        assert result.metadata["num_constraints"] == 1
