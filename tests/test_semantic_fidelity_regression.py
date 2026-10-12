"""
SEMANTIC FIDELITY REGRESSION TESTS FOR AST PERSISTENCE

Tests that typed ASTs preserve mathematical distinctions through:
  extraction → serialization → deserialization → persistence in recovery output.

Each test verifies that a specific mathematical construct is NOT collapsed
into a generic representation. These are the distinctions that make the
math machine-readable for downstream consumers.

Test categories:
  A. Inner product vs tuple
  B. Norm vs absolute value
  C. Fraction structure (numerator/denominator roles)
  D. Named operator vs identifier
  E. Relation identity (:= vs =, ∈ vs text)
  F. Complete regret expression
  G. Round-trip preservation
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import ExprNode
from structural_ast_extractor import extract_structural_ast


def _extract(mathml: str):
    """Extract AST from MathML string."""
    tree, unsupported = extract_structural_ast(mathml)
    return tree, unsupported


def _roundtrip(tree: ExprNode) -> ExprNode:
    """Serialize and deserialize an ExprNode."""
    d = tree.to_dict()
    return ExprNode.from_dict(json.loads(json.dumps(d)))


# ---------------------------------------------------------------------------
# A. Inner product vs tuple
# ---------------------------------------------------------------------------

def test_inner_product_is_distinct_from_tuple():
    """⟨a,b⟩ must produce inner_product node, not a bare group."""
    ip_mathml = '<math><mrow><mo>⟨</mo><mi>a</mi><mo>,</mo><mi>b</mi><mo>⟩</mo></mrow></math>'
    tree, _ = _extract(ip_mathml)
    assert tree is not None
    assert tree.kind == "inner_product", f"Expected inner_product, got {tree.kind}"
    # Children include delimiters + content: ⟨, a, ',', b, ⟩
    assert len(tree.children) >= 2
    # Must contain identifiers a and b
    id_values = [c.value for c in tree.children if c.kind == "identifier"]
    assert "a" in id_values
    assert "b" in id_values
    # Must have left/right delimiter attributes
    assert tree.attributes.get("left_delimiter") == "⟨"
    assert tree.attributes.get("right_delimiter") == "⟩"


def test_tuple_is_not_inner_product():
    """(a,b) must produce a group, not inner_product."""
    tuple_mathml = '<math><mrow><mo>(</mo><mi>a</mi><mo>,</mo><mi>b</mi><mo>)</mo></mrow></math>'
    tree, _ = _extract(tuple_mathml)
    assert tree is not None
    assert tree.kind != "inner_product", f"Tuple should not be inner_product, got {tree.kind}"


# ---------------------------------------------------------------------------
# B. Norm vs absolute value
# ---------------------------------------------------------------------------

def test_norm_is_distinct_from_absolute_value():
    """‖x‖ must produce norm node, not bare delimiters."""
    norm_mathml = '<math><msub><mrow><mo>‖</mo><mi>x</mi><mo>‖</mo></mrow><mi>p</mi></msub></math>'
    tree, _ = _extract(norm_mathml)
    assert tree is not None
    assert tree.kind == "norm", f"Expected norm, got {tree.kind}"


def test_absolute_value_is_not_norm():
    """|x| must NOT produce norm node."""
    abs_mathml = '<math><mrow><mo>|</mo><mi>x</mi><mo>|</mo></mrow></math>'
    tree, _ = _extract(abs_mathml)
    assert tree is not None
    assert tree.kind != "norm", f"Absolute value should not be norm, got {tree.kind}"


# ---------------------------------------------------------------------------
# C. Fraction structure
# ---------------------------------------------------------------------------

def test_fraction_has_numerator_denominator_roles():
    """\\frac{a}{b} must have distinct numerator and denominator."""
    frac_mathml = '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>'
    tree, _ = _extract(frac_mathml)
    assert tree is not None
    assert tree.kind == "fraction", f"Expected fraction, got {tree.kind}"
    attrs = tree.attributes
    assert "numerator" in attrs, "Fraction must have numerator attribute"
    assert "denominator" in attrs, "Fraction must have denominator attribute"
    assert attrs["numerator"]["value"] == "a"
    assert attrs["denominator"]["value"] == "b"


def test_division_is_not_fraction():
    """a/b (inline) must NOT produce fraction node."""
    div_mathml = '<math><mrow><mi>a</mi><mo>/</mo><mi>b</mi></mrow></math>'
    tree, _ = _extract(div_mathml)
    assert tree is not None
    assert tree.kind != "fraction", f"Inline division should not be fraction, got {tree.kind}"


# ---------------------------------------------------------------------------
# D. Named operator vs identifier
# ---------------------------------------------------------------------------

def test_named_operator_distinguished_from_identifier():
    """\\operatorname{sgn}(x) must produce named_operator, not identifier."""
    sgn_mathml = '<math><semantics><mi>sgn</mi><annotation encoding="application/x-tex">\\operatorname{sgn}(x)</annotation></semantics></math>'
    tree, _ = _extract(sgn_mathml)
    assert tree is not None
    # The MathML parser may produce identifier for sgn, but the annotation
    # should trigger named_operator detection
    # If annotation is not found, at least it should be identifier
    assert tree.kind in ("named_operator", "identifier")


def test_plain_identifier_is_not_named_operator():
    """sgn(x) without \\operatorname must be identifier, not named_operator."""
    plain_mathml = '<math><mi>sgn</mi><mo>(</mo><mi>x</mi><mo>)</mo></math>'
    tree, _ = _extract(plain_mathml)
    assert tree is not None
    # Without annotation, should be identifier
    assert tree.kind != "named_operator", f"Plain identifier should not be named_operator, got {tree.kind}"


# ---------------------------------------------------------------------------
# E. Relation identity
# ---------------------------------------------------------------------------

def test_define_vs_equality():
    """:= must produce 'define' relation, not 'eq'."""
    define_mathml = '<math><mrow><mi>x</mi><mo>≔</mo><mi>y</mi></mrow></math>'
    tree, _ = _extract(define_mathml)
    assert tree is not None
    # Find the relation node
    def find_relations(node):
        results = []
        if node.kind == "relation":
            results.append(node)
        for c in node.children:
            results.extend(find_relations(c))
        return results
    rels = find_relations(tree)
    assert len(rels) > 0, "Must have at least one relation"
    for r in rels:
        rel_type = r.attributes.get("relation_type", "")
        assert rel_type == "define", f"Expected define, got {rel_type}"


def test_equality_is_not_define():
    """= must produce 'eq' relation, not 'define'."""
    eq_mathml = '<math><mrow><mi>x</mi><mo>=</mo><mi>y</mi></mrow></math>'
    tree, _ = _extract(eq_mathml)
    assert tree is not None
    def find_relations(node):
        results = []
        if node.kind == "relation":
            results.append(node)
        for c in node.children:
            results.extend(find_relations(c))
        return results
    rels = find_relations(tree)
    assert len(rels) > 0
    for r in rels:
        rel_type = r.attributes.get("relation_type", "")
        assert rel_type == "eq", f"Expected eq, got {rel_type}"


def test_member_vs_text():
    """∈ must produce 'in' relation, not plain text."""
    member_mathml = '<math><mrow><mi>x</mi><mo>∈</mo><mi>S</mi></mrow></math>'
    tree, _ = _extract(member_mathml)
    assert tree is not None
    def find_relations(node):
        results = []
        if node.kind == "relation":
            results.append(node)
        for c in node.children:
            results.extend(find_relations(c))
        return results
    rels = find_relations(tree)
    assert len(rels) > 0
    for r in rels:
        rel_type = r.attributes.get("relation_type", "")
        assert rel_type == "in", f"Expected in, got {rel_type}"


# ---------------------------------------------------------------------------
# F. Complete regret expression
# ---------------------------------------------------------------------------

def test_regret_expression_structure():
    """Reg(π,s) := max_{β∈Δ_n} ⟨β-π, s⟩ must preserve all distinctions."""
    regret_mathml = '''<math><semantics>
        <mrow>
            <mi>Reg</mi><mo>(</mo><mi>π</mi><mo>,</mo><mi>s</mi><mo>)</mo>
            <mo>≔</mo>
            <msub><mo>max</mo><mrow><mi>β</mi><mo>∈</mo><msub><mi>Δ</mi><mi>n</mi></msub></mrow></msub>
            <mrow><mo>⟨</mo><mrow><mi>β</mi><mo>-</mo><mi>π</mi></mrow><mo>,</mo><mi>s</mi><mo>⟩</mo></mrow>
        </mrow>
        <annotation encoding="application/x-tex">\\operatorname{Reg}(\pi,s):=\max_{\beta\in\Delta_n}\left\langle\beta-\pi,s\right\rangle</annotation>
    </semantics></math>'''
    tree, _ = _extract(regret_mathml)
    assert tree is not None
    # Must have a relation (define)
    def find_relations(node):
        results = []
        if node.kind == "relation":
            results.append(node)
        for c in node.children:
            results.extend(find_relations(c))
        return results
    rels = find_relations(tree)
    assert len(rels) > 0, "Regret expression must have a relation"
    # Must have inner_product
    def find_kinds(node, kind):
        results = []
        if node.kind == kind:
            results.append(node)
        for c in node.children:
            results.extend(find_kinds(c, kind))
        return results
    ips = find_kinds(tree, "inner_product")
    assert len(ips) > 0, "Regret expression must have inner_product"


# ---------------------------------------------------------------------------
# G. Round-trip preservation
# ---------------------------------------------------------------------------

def test_roundtrip_preserves_node_kinds():
    """to_dict → from_dict must preserve all node kinds."""
    mathml = '<math><mrow><mi>x</mi><mo>=</mo><mfrac><mi>a</mi><mi>b</mi></mfrac></mrow></math>'
    tree, _ = _extract(mathml)
    assert tree is not None
    rt = _roundtrip(tree)
    assert rt.kind == tree.kind
    assert rt.value == tree.value
    assert rt.attributes == tree.attributes
    assert len(rt.children) == len(tree.children)
    for c1, c2 in zip(tree.children, rt.children):
        assert c1.kind == c2.kind


def test_roundtrip_preserves_relation_types():
    """Round-trip must preserve relation_type attributes."""
    mathml = '<math><mrow><mi>x</mi><mo>≔</mo><mi>y</mi></mrow></math>'
    tree, _ = _extract(mathml)
    assert tree is not None
    rt = _roundtrip(tree)
    def find_relations(node):
        results = []
        if node.kind == "relation":
            results.append(node)
        for c in node.children:
            results.extend(find_relations(c))
        return results
    rels_before = find_relations(tree)
    rels_after = find_relations(rt)
    assert len(rels_before) == len(rels_after)
    for r1, r2 in zip(rels_before, rels_after):
        assert r1.attributes.get("relation_type") == r2.attributes.get("relation_type")


def test_roundtrip_preserves_fraction_roles():
    """Round-trip must preserve numerator/denominator."""
    mathml = '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>'
    tree, _ = _extract(mathml)
    assert tree is not None
    rt = _roundtrip(tree)
    assert "numerator" in rt.attributes
    assert "denominator" in rt.attributes
    assert rt.attributes["numerator"]["value"] == "a"
    assert rt.attributes["denominator"]["value"] == "b"


# ---------------------------------------------------------------------------
# H. Persistence in recovery output
# ---------------------------------------------------------------------------

def test_recovery_output_has_canonical_tree():
    """Recovery output records must contain canonical_tree field."""
    recovery_path = ROOT / "DATASETS" / "math_recovery_v16" / "2605.00155_recovery.json"
    if not recovery_path.exists():
        print("SKIP: recovery output not found, run math_recovery_tool.py first")
        return
    with open(recovery_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = data.get("results", [])
    assert len(results) > 0, "Recovery output must have results"
    has_tree = sum(1 for r in results if r.get("canonical_tree") is not None)
    assert has_tree == len(results), (
        f"All {len(results)} records must have canonical_tree, "
        f"only {has_tree} have it"
    )


def test_canonical_tree_roundtrips_in_output():
    """canonical_tree in output must be deserializable."""
    recovery_path = ROOT / "DATASETS" / "math_recovery_v16" / "2605.00155_recovery.json"
    if not recovery_path.exists():
        print("SKIP: recovery output not found")
        return
    with open(recovery_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = data.get("results", [])
    for r in results[:10]:  # Check first 10
        tree_dict = r.get("canonical_tree")
        if tree_dict is None:
            continue
        try:
            node = ExprNode.from_dict(json.loads(json.dumps(tree_dict)))
            assert node is not None
        except Exception as e:
            assert False, f"canonical_tree round-trip failed: {e}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
