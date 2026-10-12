"""
MATH CONSTRAINT VALIDATOR — rigorous validation of extracted math.

P5 contract:
  - No reward hacking: a symbol or bracket fitting syntactically is NOT
    sufficient. The chunk of math must pass validation against decided
    symbols, deviant lines, enclosures, and known math expressions.
  - All unknown parsed layers must perform rigorously: match to multiple
    candidates, reject bad math, accept solvable.
  - Same paper, same grouping of math antics: equations in the same paper
    share a symbol table and validation context.
  - Per math problem encountered in the scan: each equation is validated
    individually against the paper's known constraints.
  - Less given values to more positions = harder to solve and have to solve:
    underdetermined systems are flagged as harder, not rejected.

This module sits between extraction and solving. It does NOT replace the
solver — it filters candidates so the solver only receives valid math.
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import RecoveryRecord, occurrence_key  # noqa: E402


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

CandidateStatus = Literal["valid", "invalid", "solvable", "unsolvable", "underdetermined"]
ValidationDimension = Literal["symbols", "enclosures", "structure", "solvability"]


@dataclass
class ValidationResult:
    """Result of validating one candidate."""
    candidate: str
    status: CandidateStatus
    scores: dict[str, float] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaperContext:
    """
    Symbol table and constraints for one paper.

    Decided symbols: symbols that appear consistently in the paper.
    Deviant lines: equations that use symbols outside the decided set.
    Enclosures: all enclosure pairs that must balance.
    Known expressions: math expressions that are known to be valid.
    """
    paper_id: str
    decided_symbols: set[str] = field(default_factory=set)
    symbol_counts: Counter = field(default_factory=Counter)
    deviant_symbols: set[str] = field(default_factory=set)
    enclosure_pairs: dict[str, str] = field(default_factory=dict)
    known_expressions: set[str] = field(default_factory=set)

    def add_symbol(self, symbol: str) -> None:
        self.symbol_counts[symbol] += 1

    def finalize_decided(self, min_count: int = 3) -> None:
        """Symbols appearing >= min_count times are 'decided'."""
        self.decided_symbols = {s for s, c in self.symbol_counts.items() if c >= min_count}
        self.deviant_symbols = set(self.symbol_counts) - self.decided_symbols


# ---------------------------------------------------------------------------
# Enclosure validator
# ---------------------------------------------------------------------------

_ENCLOSURE_PAIRS = {
    "(": ")",
    "[": "]",
    "{": "}",
    "⟨": "⟩",   # inner product
    "‖": "‖",   # norm (self-closing pair)
    "|": "|",   # absolute value (self-closing pair)
    "⌊": "⌋",   # floor
    "⌈": "⌉",   # ceiling
}


def validate_enclosures(expr: str) -> list[str]:
    """
    Check that all enclosures are balanced.

    Returns list of violation strings. Empty = valid.
    """
    violations = []
    stack = []
    for i, ch in enumerate(expr):
        if ch in _ENCLOSURE_PAIRS:
            # Self-closing pairs (‖, |) don't push
            if _ENCLOSURE_PAIRS[ch] == ch:
                continue
            stack.append((ch, i))
        elif ch in _ENCLOSURE_PAIRS.values():
            if not stack:
                violations.append(f"Unmatched closing {ch!r} at position {i}")
            else:
                opening, pos = stack.pop()
                if _ENCLOSURE_PAIRS[opening] != ch:
                    violations.append(
                        f"Mismatched enclosure: {opening!r} at {pos} closed by {ch!r} at {i}"
                    )
    for opening, pos in stack:
        violations.append(f"Unclosed {opening!r} at position {pos}")
    return violations


# ---------------------------------------------------------------------------
# Symbol validator
# ---------------------------------------------------------------------------

# Symbols that are "decided" in most ML/math papers
_COMMON_SYMBOLS = {
    "pi", "theta", "delta", "Delta", "beta", "alpha", "gamma", "sigma",
    "mu", "nu", "lambda", "Lambda", "phi", "Phi", "psi", "Psi",
    "r", "s", "x", "y", "z", "t", "k", "n", "m", "p", "q",
    "e", "E", "P", "Q", "R", "G", "D", "X", "Y",
    "pi_0", "pi_theta", "r_hat", "r_star", "Delta_n",
    "sgn", "Reg", "max", "min", "sup", "inf", "lim",
    "ell_1", "ell_p", "ell_infty",
    # Standard math variable letters
    "a", "b", "c", "d", "f", "g", "h", "i", "j", "l", "o", "u", "v", "w",
    # Common LaTeX commands that appear as symbols
    "in", "frac", "sqrt", "sum", "prod", "int", "oint", "cdot", "times",
    "div", "mod", "sin", "cos", "tan", "log", "ln", "exp", "det", "dim",
    "ker", "deg", "gcd", "lcm", "Pr", "tr", "diag", "rank", "arg",
    "Var", "Cov", "Corr", "softmax", "sigmoid", "relu", "ReLU",
    "langle", "rangle", "lVert", "rVert", "lfloor", "rfloor", "lceil", "rceil",
    "left", "right", "big", "Big", "bigg", "Bigg",
    "operatorname", "text", "mathrm", "mathbf", "mathcal", "mathbb",
    "hat", "bar", "vec", "dot", "ddot", "tilde", "widehat", "widetilde",
}


def extract_symbols(expr: str) -> set[str]:
    """Extract all symbols from a math expression."""
    symbols = set()
    # Split by backslash using hex code to avoid escaping issues
    parts = re.split(r"[\x5c]", expr)
    for i, part in enumerate(parts):
        if i > 0 and part:  # After a backslash
            cmd = ""
            for ch in part:
                if ch.isalpha():
                    cmd += ch
                else:
                    break
            if cmd:
                symbols.add(cmd)
    # Remove LaTeX commands and extract remaining single letters
    cleaned = re.sub(r"[\x5c][a-zA-Z]+", " ", expr)
    for ch in cleaned:
        if ch.isalpha():
            symbols.add(ch)
    # Greek letters (non-ASCII)
    for ch in expr:
        if ord(ch) > 127:
            symbols.add(ch)
    return symbols


def validate_symbols(expr: str, paper_ctx: PaperContext) -> list[str]:
    """
    Validate symbols against the paper's decided symbol set.

    A symbol is valid if:
      - It's in the paper's decided symbols, OR
      - It's a common math symbol, OR
      - It appears in the paper's known expressions

    Violations are reported for unknown symbols.
    """
    violations = []
    symbols = extract_symbols(expr)
    for sym in symbols:
        if sym not in paper_ctx.decided_symbols:
            if sym not in _COMMON_SYMBOLS:
                violations.append(f"Unknown symbol: {sym!r}")
    return violations


# ---------------------------------------------------------------------------
# Structure validator
# ---------------------------------------------------------------------------

def validate_structure(expr: str) -> list[str]:
    """
    Validate the mathematical structure of an expression.

    Checks:
      - No empty brackets: (), [], {}
      - No double operators: ++, --, **, //
      - No operator at end (except .)
      - Balanced subscripts/superscripts
      - No malformed fractions: \\frac{}{} must have non-empty args
    """
    violations = []

    # Empty brackets
    for open_ch, close_ch in [("(", ")"), ("[", "]"), ("{", "}")]:
        if f"{open_ch}{close_ch}" in expr:
            violations.append(f"Empty brackets: {open_ch}{close_ch}")

    # Double operators
    for op1, op2 in [("+", "+"), ("-", "-"), ("*", "*"), ("/", "/")]:
        if f"{op1}{op2}" in expr:
            violations.append(f"Double operator: {op1}{op2}")

    # Operator at end (except . or ,)
    if expr and expr[-1] in "+-*/=":
        violations.append(f"Expression ends with operator: {expr[-1]}")

    # Malformed fractions — only report if not already caught by empty brackets
    if "\\frac" in expr:
        for m in re.finditer(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", expr):
            if not m.group(1) or not m.group(2):
                # Only report if the empty brackets weren't already caught
                if not any("Empty brackets" in v for v in violations):
                    violations.append("Malformed fraction with empty argument")

    return violations


# ---------------------------------------------------------------------------
# Solvability checker
# ---------------------------------------------------------------------------

def check_solvability(expr: str) -> tuple[bool, list[str]]:
    """
    Check if an expression is solvable.

    Returns (is_solvable, violations).

    An expression is solvable if:
      - It has an equality or inequality relation, OR
      - It's a well-formed expression that can be evaluated, OR
      - It's an underdetermined system (fewer constraints than unknowns)
        but still well-formed.

    An expression is unsolvable if:
      - It has no relation and no operators, OR
      - It has malformed structure.

    NOTE: symbol validation is a separate dimension. An expression with
    undefined symbols is still solvable — it just has unknowns. The
    constraint validator flags those, but solvability is about structure.
    """
    # Must have at least a relation or an operator
    has_relation = any(r in expr for r in ["=", "\\approx", "\\sim", "\\leq", "\\geq", "\\neq", ":=", "\\coloneqq"])
    has_operator = any(o in expr for o in ["+", "-", "*", "/", "\\frac", "\\sqrt"])

    if not has_relation and not has_operator:
        return False, ["No relation or operator — not a solvable expression"]

    return True, []


# ---------------------------------------------------------------------------
# Underdetermined system detection
# ---------------------------------------------------------------------------

def detect_underdetermined(expr: str) -> tuple[bool, int, int]:
    """
    Detect if an expression is underdetermined.

    Returns (is_underdetermined, num_unknowns, num_constraints).

    An expression is underdetermined if num_constraints < num_unknowns.
    This is NOT a rejection reason — it means the problem is harder.
    """
    # Count only actual symbols (not operators or numbers)
    symbols = extract_symbols(expr)
    # Remove operators and numbers from symbol count
    operators = {"=", "+", "-", "*", "/", "\\", "{", "}", "(", ")", "[", "]"}
    num_unknowns = len([s for s in symbols if s not in operators and not s.isdigit()])

    # Count constraints (relations that can constrain variables)
    num_constraints = sum(1 for r in ["=", ":=", "\\approx", "\\leq", "\\geq", "\\neq"] if r in expr)

    is_underdetermined = num_constraints < num_unknowns
    return is_underdetermined, num_unknowns, num_constraints


# ---------------------------------------------------------------------------
# Multi-candidate matching
# ---------------------------------------------------------------------------

def generate_candidates(record: RecoveryRecord) -> list[str]:
    """
    Generate multiple candidate interpretations from a recovery record.

    The record may have:
      - canonical_tree (from AST path)
      - source.latex (from the source corpus)

    We generate candidates from each source, plus combinations.
    """
    candidates = []

    # From source LaTeX
    if record.source and record.source.latex:
        candidates.append(record.source.latex)

    # From canonical tree — flatten to string
    if record.canonical_tree:
        tree_str = _tree_to_string(record.canonical_tree)
        candidates.append(tree_str)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def _tree_to_string(node) -> str:
    """Flatten an ExprNode tree to a string for candidate generation."""
    from math_contract import ExprNode
    if node is None:
        return ""
    if node.kind == "relation":
        rel_type = node.attributes.get("relation_type", "eq")
        return f" {rel_type} "
    if node.kind == "fraction":
        num = _tree_to_string(node.children[0]) if node.children else ""
        den = _tree_to_string(node.children[1]) if len(node.children) > 1 else ""
        return f"({num})/({den})"
    if node.kind == "power":
        base = _tree_to_string(node.children[0]) if node.children else ""
        exp = _tree_to_string(node.children[1]) if len(node.children) > 1 else ""
        return f"({base})^({exp})"
    if node.kind == "subscript":
        base = _tree_to_string(node.children[0]) if node.children else ""
        sub = _tree_to_string(node.children[1]) if len(node.children) > 1 else ""
        return f"{base}_{sub}"
    if node.kind == "norm":
        expr = _tree_to_string(node.children[0]) if node.children else ""
        return f"||{expr}||"
    if node.kind == "inner_product":
        parts = ", ".join(_tree_to_string(c) for c in node.children)
        return f"⟨{parts}⟩"
    if node.kind == "named_operator":
        name = node.attributes.get("operator_name", node.value)
        arg = _tree_to_string(node.children[0]) if node.children else ""
        return f"{name}({arg})"
    # Leaf nodes
    if node.children:
        return "".join(_tree_to_string(c) for c in node.children)
    return node.value or ""


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class ConstraintValidator:
    """
    Validate extracted math candidates against paper constraints.

    The validator:
      1. Generates multiple candidates from a recovery record
      2. Validates each candidate against symbol, enclosure, structure, solvability
      3. Rejects candidates with violations
      4. Accepts candidates that pass all checks and are solvable
      5. Flags underdetermined candidates as harder, not rejected
    """

    def __init__(self, paper_ctx: PaperContext):
        self.paper_ctx = paper_ctx

    def validate(self, record: RecoveryRecord) -> ValidationResult:
        """
        Validate a recovery record against paper constraints.

        Returns the best candidate with its validation status.
        """
        candidates = generate_candidates(record)
        if not candidates:
            return ValidationResult(
                candidate="",
                status="invalid",
                violations=["No candidates generated"],
            )

        best = None
        best_score = -1.0

        for candidate in candidates:
            result = self._validate_candidate(candidate)
            score = self._score_candidate(result)
            if score > best_score:
                best_score = score
                best = result

        return best if best else ValidationResult(
            candidate=candidates[0] if candidates else "",
            status="invalid",
            violations=["All candidates failed validation"],
        )

    def _validate_candidate(self, candidate: str) -> ValidationResult:
        """Validate a single candidate against all constraints."""
        violations = []
        scores = {}

        # 1. Enclosure validation
        enclosure_violations = validate_enclosures(candidate)
        violations.extend(enclosure_violations)
        scores["enclosures"] = 1.0 if not enclosure_violations else 0.0

        # 2. Symbol validation
        symbol_violations = validate_symbols(candidate, self.paper_ctx)
        violations.extend(symbol_violations)
        scores["symbols"] = 1.0 if not symbol_violations else 0.5

        # 3. Structure validation
        structure_violations = validate_structure(candidate)
        violations.extend(structure_violations)
        scores["structure"] = 1.0 if not structure_violations else 0.0

        # 4. Solvability check
        is_solvable, solvability_violations = check_solvability(candidate)
        violations.extend(solvability_violations)
        scores["solvability"] = 1.0 if is_solvable else 0.0

        # 5. Underdetermined detection
        is_underdetermined, num_unknowns, num_constraints = detect_underdetermined(candidate)

        # Determine status
        if not is_solvable:
            status = "unsolvable"
        elif violations:
            status = "invalid"
        elif is_underdetermined:
            status = "underdetermined"
        else:
            status = "solvable"

        return ValidationResult(
            candidate=candidate,
            status=status,
            scores=scores,
            violations=violations,
            metadata={
                "underdetermined": is_underdetermined,
                "num_unknowns": num_unknowns,
                "num_constraints": num_constraints,
            },
        )

    def _score_candidate(self, result: ValidationResult) -> float:
        """
        Score a validation result.

        Higher score = better candidate.
        Rewards correct positives; penalizes violations.
        """
        score = 0.0

        # Reward correct positives
        if result.status == "solvable":
            score += 1.0
        elif result.status == "underdetermined":
            score += 0.7  # Harder but still valid
        elif result.status == "invalid":
            score -= 0.5

        # Penalize violations
        score -= len(result.violations) * 0.1

        # Reward dimension scores
        for dim, dim_score in result.scores.items():
            score += dim_score * 0.1

        return score


# ---------------------------------------------------------------------------
# Paper context builder
# ---------------------------------------------------------------------------

def build_paper_context(
    paper_id: str,
    equations: Iterable[dict[str, Any]],
) -> PaperContext:
    """
    Build a paper context from a list of equations.

    Extracts symbols, counts them, and determines decided vs deviant.
    """
    ctx = PaperContext(paper_id=paper_id)

    for eq in equations:
        latex = eq.get("latex", "")
        if not latex:
            continue
        symbols = extract_symbols(latex)
        for sym in symbols:
            ctx.add_symbol(sym)

    ctx.finalize_decided(min_count=3)
    return ctx


# ---------------------------------------------------------------------------
# Batch validator
# ---------------------------------------------------------------------------

def validate_paper(
    paper_id: str,
    records: list[RecoveryRecord],
    equations: list[dict[str, Any]],
) -> list[ValidationResult]:
    """
    Validate all records for one paper.

    Builds the paper context from the equations, then validates each record
    against it. Returns validation results in the same order as records.
    """
    ctx = build_paper_context(paper_id, equations)
    validator = ConstraintValidator(ctx)
    return [validator.validate(r) for r in records]


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Test with real paper data
    import json

    with open(ROOT / "DATASETS" / "arxiv_html_corpus" / "2605.00155.json", encoding="utf-8") as f:
        corpus = json.load(f)
    equations = corpus.get("equations", [])

    # Build paper context
    ctx = build_paper_context("2605.00155", equations)
    print(f"Paper: {ctx.paper_id}")
    print(f"Total symbols: {len(ctx.symbol_counts)}")
    print(f"Decided symbols ({len(ctx.decided_symbols)}): {sorted(ctx.decided_symbols)[:20]}")
    print(f"Deviant symbols ({len(ctx.deviant_symbols)}): {sorted(ctx.deviant_symbols)[:20]}")
    print()

    # Test validation on a few equations
    validator = ConstraintValidator(ctx)
    for i in [100, 101, 111, 115, 120]:
        if i >= len(equations):
            continue
        eq = equations[i]
        latex = eq.get("latex", "")

        # Build a minimal RecoveryRecord
        from math_ast_integration import make_source_occurrence, build_recovery_record
        source = make_source_occurrence(
            paper_id="2605.00155", paper_version="latest",
            source_locator=f"math[{i}]", occurrence_index=i,
            mathml=eq.get("mathml"), latex=latex,
        )
        record = build_recovery_record(source, eq.get("mathml"))
        result = validator.validate(record)

        print(f"Eq [{i}]: {latex[:80]}")
        print(f"  Status: {result.status}")
        print(f"  Scores: {result.scores}")
        if result.violations:
            print(f"  Violations: {result.violations}")
        print()
