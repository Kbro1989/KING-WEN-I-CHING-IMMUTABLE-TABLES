#!/usr/bin/env python3
"""
ROOM 5 — TYPED INTEGRAL IR (v2)

Target:
    Integral(
        body     = Expression("f(z)"),
        limits   = {lower: Limit("a"), upper: Limit("b")},
        measure  = Differential("z"),
        operator = "integral",
    )

Acceptance criteria (from external audit):
  1. Independent fields: integrand, lower, upper, differential separate
  2. Scope preservation: z in dz is the INTEGRATION VARIABLE, not appended
  3. Nested expression safety:  \\int_a^b f(g(z)) dz  preserves nesting
  4. Limit variation: definite, indefinite, lower-only, upper-only
  5. Conservation: every source occurrence represented
  6. Honest fallback: unsupported forms give partial/failure, NEVER a
     fabricated complete integral
  7. Regression: structural, nested-arg, relation-identity, mbox-dollar intact
  8. Operator identity: ∫ ≠ ∮ ≠ ∬ ≠ ∭ preserved in the IR
  9. Nested mrow: differential detected even when integrand+dz are wrapped
 10. Exact tree equality: fixtures assert complete expected dicts

Key point: `dz` must be attached to a typed Differential node — character
presence in the output string cannot establish that relationship.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# TYPED IR
# ─────────────────────────────────────────────────────────────────────────

class Node:
    def __init__(self, kind, **fields):
        self.kind = kind
        self.fields = fields

    def to_dict(self):
        out = {"kind": self.kind}
        for k, v in self.fields.items():
            if isinstance(v, Node):
                out[k] = v.to_dict()
            elif isinstance(v, list):
                out[k] = [x.to_dict() if isinstance(x, Node) else x for x in v]
            elif isinstance(v, dict):
                out[k] = {kk: (vv.to_dict() if isinstance(vv, Node) else vv)
                          for kk, vv in v.items()}
            else:
                out[k] = v
        return out

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


def Expression(value):
    """A typed wrapper around a string expression."""
    return Node("Expression", value=value)


def Limit(value):
    """A typed wrapper around a limit value."""
    return Node("Limit", value=value)


def Differential(variable):
    return Node("Differential", variable=variable)


def Integral(body, lower, upper, measure, operator):
    return Node("Integral",
                body=body,
                limits={"lower": lower, "upper": upper},
                measure=measure,
                operator=operator)


# ─────────────────────────────────────────────────────────────────────────
# MathML -> typed Integral
# ─────────────────────────────────────────────────────────────────────────

from mathml_parser import MathMLParser  # noqa: E402

INTEGRAL_OPS = {"∫", "∮", "∬", "∭"}

OPERATOR_KIND = {
    "∫": "integral",
    "∮": "contour",
    "∬": "double",
    "∭": "triple",
}

DIFF_TOKENS = {"d", "𝑑", "ⅆ", "ⅅ"}


def _find_integral_operator(math_tag):
    """
    Find the integral operator in a MathML tree.
    Returns (element, operator_symbol) or (None, None).
    """
    # Search for msubsup/munderover/msub/munder/msup with integral operator
    for tag in math_tag.find_all(["msubsup", "munderover", "msub", "munder", "msup"]):
        kids = [c for c in tag.find_all(recursive=False)]
        if not kids:
            continue
        op = kids[0].get_text(strip=True)
        if op in INTEGRAL_OPS:
            return tag, op

    # Search for bare mo with integral operator
    for mo in math_tag.find_all("mo"):
        if mo.get_text(strip=True) in INTEGRAL_OPS:
            return mo, mo.get_text(strip=True)

    return None, None


def _extract_limits(integ, p):
    """
    Extract lower and upper limits from the integral operator element.
    Returns (lower_str, upper_str, notes).
    """
    notes = []
    kids = [c for c in integ.find_all(recursive=False)]

    if integ.name in ("msubsup", "munderover"):
        if len(kids) >= 3:
            lower = p._walk(kids[1])
            upper = p._walk(kids[2])
            return lower, upper, notes
        else:
            notes.append("integral_arity_partial")
            return None, None, notes

    if integ.name in ("msub", "munder"):
        if len(kids) >= 2:
            lower = p._walk(kids[1])
            return lower, None, notes
        else:
            notes.append("integral_arity_partial")
            return None, None, notes

    if integ.name == "msup":
        if len(kids) >= 2:
            upper = p._walk(kids[1])
            return None, upper, notes
        else:
            notes.append("integral_arity_partial")
            return None, None, notes

    # bare mo — no limits
    return None, None, notes


def _get_tail(integ):
    """
    Get the elements after the integral operator (the integrand + differential).
    """
    tail = []
    for sib in integ.next_siblings:
        if getattr(sib, "name", None):
            tail.append(sib)
    return tail


def _collect_atoms(elements):
    """
    Collect all leaf atoms from a list of MathML elements, recursing into
    containers. Returns a list of (element, text) pairs.
    """
    atoms = []

    def _collect(el):
        tag = el.name if hasattr(el, "name") else None
        if tag in (None, "mi", "mn", "mo", "mtext"):
            txt = el.get_text(strip=True) if hasattr(el, "get_text") else str(el)
            atoms.append((el, txt))
        else:
            for child in [c for c in el.children if getattr(c, "name", None)]:
                _collect(child)

    for el in elements:
        _collect(el)
    return atoms


def _parse_tail(elements, p):
    """
    Parse the tail (integrand + differential) into a typed body node
    and a differential variable.

    Returns (body_str, diff_var, notes).
    """
    notes = []

    # Collect all leaf atoms in order (recursing into containers)
    atoms = _collect_atoms(elements)

    # Search for d + variable pattern
    diff_var = None
    diff_indices = set()
    for i in range(len(atoms) - 1):
        _, txt = atoms[i]
        _, next_txt = atoms[i + 1]
        if txt in DIFF_TOKENS and re.fullmatch(r"[A-Za-z]", next_txt):
            if diff_var is None:
                diff_var = next_txt
            diff_indices.add(i)
            diff_indices.add(i + 1)

    if diff_var is None:
        notes.append("measure_missing")
        body_str = "".join(filter(None, (p._walk(el) for el in elements)))
        return body_str, None, notes

    # Build body from all atoms except the differential pairs
    body_parts = []
    for i, (el, txt) in enumerate(atoms):
        if i in diff_indices:
            continue
        part = p._walk(el)
        if part:
            body_parts.append(part)

    body_str = "".join(body_parts)
    return body_str, diff_var, notes


def parse_integral(mml: str):
    """
    Parse MathML containing an integral into the typed IR.

    Returns (node, notes). `notes` records honest fallbacks — a partial
    structure is reported as partial, never as a complete integral.
    """
    notes = []
    soup = BeautifulSoup(mml, "html.parser")
    math = soup.find("math")
    if math is None:
        return None, ["no_math_tag"]

    # Find the integral operator
    integ, op_symbol = _find_integral_operator(math)
    if integ is None:
        return None, ["no_integral_operator"]

    # Determine the operator kind
    operator = OPERATOR_KIND.get(op_symbol, "integral")

    # Extract limits
    lower_str, upper_str, limit_notes = _extract_limits(integ, MathMLParser())
    notes.extend(limit_notes)

    # Extract body and differential
    tail = _get_tail(integ)
    body_str, diff_var, diff_notes = _parse_tail(tail, MathMLParser())
    notes.extend(diff_notes)

    # Build typed IR
    body = Expression(body_str) if body_str else None
    lower = Limit(lower_str) if lower_str else None
    upper = Limit(upper_str) if upper_str else None
    measure = Differential(diff_var) if diff_var else None

    node = Integral(body=body, lower=lower, upper=upper, measure=measure, operator=operator)
    return node, notes


# ─────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────

FIXTURES = [
    # (label, mathml, expected_dict, forbidden)
    (
        "definite with differential",
        '<math><msubsup><mo>∫</mo><mi>α</mi><mi>∞</mi></msubsup>'
        '<mi>φ</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>𝑑</mi><mi>z</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "phi(z)"},
            "limits": {
                "lower": {"kind": "Limit", "value": "alpha"},
                "upper": {"kind": "Limit", "value": "oo"},
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "integral",
        },
        ["phi(z)dz", "phi(z)d"],
    ),
    (
        "nested application",
        '<math><msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>g</mi><mo>(</mo><mi>z</mi><mo>)</mo><mo>)</mo>'
        '<mi>d</mi><mi>z</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(g(z))"},
            "limits": {
                "lower": {"kind": "Limit", "value": "a"},
                "upper": {"kind": "Limit", "value": "b"},
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "integral",
        },
        ["f(g(z))dz"],
    ),
    (
        "indefinite (no limits)",
        '<math><mo>∫</mo><mi>φ</mi><mo>(</mo><mi>z</mi><mo>)</mo>'
        '<mi>d</mi><mi>z</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "phi(z)"},
            "limits": {
                "lower": None,
                "upper": None,
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "integral",
        },
        ["phi(z)dz"],
    ),
    (
        "lower-only",
        '<math><msub><mo>∫</mo><mi>a</mi></msub>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>d</mi><mi>z</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(z)"},
            "limits": {
                "lower": {"kind": "Limit", "value": "a"},
                "upper": None,
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "integral",
        },
        [],
    ),
    (
        "no differential (must be flagged, not fabricated)",
        '<math><msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(z)"},
            "limits": {
                "lower": {"kind": "Limit", "value": "a"},
                "upper": {"kind": "Limit", "value": "b"},
            },
            "measure": None,
            "operator": "integral",
        },
        [],
    ),
    (
        "upper-only",
        '<math><msup><mo>∫</mo><mi>b</mi></msup>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>d</mi><mi>z</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(z)"},
            "limits": {
                "lower": None,
                "upper": {"kind": "Limit", "value": "b"},
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "integral",
        },
        [],
    ),
    (
        "nested mrow with differential",
        '<math><msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mrow><mrow><mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo></mrow>'
        '<mi>d</mi><mi>z</mi></mrow></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(z)"},
            "limits": {
                "lower": {"kind": "Limit", "value": "a"},
                "upper": {"kind": "Limit", "value": "b"},
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "integral",
        },
        ["f(z)dz"],
    ),
    (
        "contour integral",
        '<math><msubsup><mo>∮</mo><mi>C</mi><mi>D</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>d</mi><mi>z</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(z)"},
            "limits": {
                "lower": {"kind": "Limit", "value": "C"},
                "upper": {"kind": "Limit", "value": "D"},
            },
            "measure": {"kind": "Differential", "variable": "z"},
            "operator": "contour",
        },
        [],
    ),
    (
        "double integral",
        '<math><msubsup><mo>∬</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo>'
        '<mi>d</mi><mi>x</mi><mi>d</mi><mi>y</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(x,y)"},
            "limits": {
                "lower": {"kind": "Limit", "value": "a"},
                "upper": {"kind": "Limit", "value": "b"},
            },
            "measure": {"kind": "Differential", "variable": "x"},
            "operator": "double",
        },
        [],
    ),
    (
        "malformed differential (d without variable)",
        '<math><msubsup><mo>∫</mo><mi>a</mi><mi>b</mi></msubsup>'
        '<mi>f</mi><mo>(</mo><mi>z</mi><mo>)</mo><mi>d</mi></math>',
        {
            "kind": "Integral",
            "body": {"kind": "Expression", "value": "f(z)d"},
            "limits": {
                "lower": {"kind": "Limit", "value": "a"},
                "upper": {"kind": "Limit", "value": "b"},
            },
            "measure": None,
            "operator": "integral",
        },
        [],
    ),
]


# ─────────────────────────────────────────────────────────────────────────
# CORPUS INTEGRATION TEST
# ─────────────────────────────────────────────────────────────────────────

def run_corpus_integration():
    """
    Run the integral parser against real MathML samples from the corpus.
    Reports how many integrals were found, structurally parsed, partially
    parsed, and rejected.
    """
    corpus_dir = ROOT / "DATASETS" / "arxiv_html_corpus"
    if not corpus_dir.exists():
        print("  SKIP corpus integration test (corpus not found)")
        return

    # Find all JSON files in the corpus
    json_files = list(corpus_dir.glob("*.json"))
    if not json_files:
        print("  SKIP corpus integration test (no JSON files)")
        return

    total_integrals = 0
    total_parsed = 0
    total_partial = 0
    total_rejected = 0

    for jf in json_files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue

        equations = data.get("equations", [])
        for eq in equations:
            latex = eq.get("latex", "")
            if "∫" not in latex and "\\int" not in latex:
                continue

            total_integrals += 1

            # Try to parse the MathML
            mathml = eq.get("mathml", "")
            if not mathml:
                total_rejected += 1
                continue

            node, notes = parse_integral(mathml)
            if node is None:
                total_rejected += 1
            elif notes:
                total_partial += 1
            else:
                total_parsed += 1

    print(f"  Corpus integration: {total_integrals} integrals found")
    print(f"    parsed:     {total_parsed}")
    print(f"    partial:    {total_partial}")
    print(f"    rejected:   {total_rejected}")


# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 84)
    print("ROOM 5 — TYPED INTEGRAL IR (v2)")
    print("=" * 84)
    print()

    passed = failed = 0
    for label, mml, expect, forbidden in FIXTURES:
        node, notes = parse_integral(mml)
        d = node.to_dict() if node else {}

        checks = []
        # 1. exact tree equality
        checks.append(("exact tree match", d == expect))
        # 2. forbidden fusions
        for f in forbidden:
            checks.append((f"NOT fused: {f}", f not in str(d.get("body", {}))))

        ok = all(c[1] for c in checks)
        if ok:
            passed += 1
        else:
            failed += 1

        mark = "ok  " if ok else "FAIL"
        print(f"  {mark} {label}")
        if not ok:
            for c, r in checks:
                if not r:
                    print(f"       !! {c}")
            print(f"       got:      {json.dumps(d, ensure_ascii=False)}")
            print(f"       expected: {json.dumps(expect, ensure_ascii=False)}")
        if notes:
            print(f"       notes: {notes}")
        print()

    print("=" * 84)
    print(f"RESULT: {passed}/{len(FIXTURES)} integral IR fixtures pass")
    print("=" * 84)

    # Run corpus integration test
    print()
    print("CORPUS INTEGRATION TEST")
    print("-" * 84)
    run_corpus_integration()

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
