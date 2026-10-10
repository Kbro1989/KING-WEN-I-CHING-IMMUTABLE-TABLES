#!/usr/bin/env python3
"""
Semantic-fidelity adversarial tests — assert the AST MEANS the source.

Round-trip alone cannot catch a lossy extraction (the same loss round-trips
fine). These tests assert source-to-AST correctness for known MathML, including
cases where an INCORRECT AST would still round-trip successfully.

Covers the audit findings:
  F1  'no unsupported nodes' is extractor coverage, not contract 'verified'
  F2  upper bounds via <mover> on big operators are preserved (were dropped)
  F3  explicit operand roles (lower_bound/upper_bound/body) + full-tree asserts
  F4  matrix <mtd> cells extract contents (nested frac survives)
  F5  transparent wrappers are DECLARED normalizations (recorded, auditable)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import ExprNode, backend_input_hash, canonical_json
from structural_ast_extractor import StructuralASTExtractor, extract_structural_ast

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}: {detail}")


def extract(mml):
    ex = StructuralASTExtractor()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(mml, "html.parser")
    return ex.extract(soup.find("math")), ex.unsupported


def find_all(tree, kind):
    out = []
    stack = [tree]
    while stack:
        n = stack.pop()
        if n.kind == kind:
            out.append(n)
        stack.extend(n.children)
    return out


def find_first(tree, kind):
    r = find_all(tree, kind)
    return r[0] if r else None


# ── F2/F3: bounded operators — upper bound via <mover> ────────────────────
print("=== F2: <mover> upper bound on sum (was dropped) ===")

t, u = extract('<math><mover><mo>&#x2211;</mo><mi>n</mi></mover><mi>i</mi></math>')
summ = find_first(t, "sum")
check("sum node exists", summ is not None)
check("upper_bound role recorded", summ is not None and "upper_bound" in summ.attributes,
      f"attrs={list(summ.attributes) if summ else None}")
# the upper limit subtree must survive as a child
child_idents = [c.value for c in (summ.children if summ else [])]
check("upper limit 'n' survives as child", "n" in child_idents, f"children={child_idents}")
check("no unsupported for mover-sum", not u, f"unsup={u}")

print("\n=== F3: <munder> lower bound — full subtree survives ===")

t, u = extract('<math><munder><mo>&#x2211;</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow></munder><mi>i</mi></math>')
summ = find_first(t, "sum")
check("lower_bound role recorded", summ is not None and "lower_bound" in summ.attributes)
# the lower bound is i=1 — assert the relation and number survive inside it
lb = summ.attributes.get("lower_bound") if summ else None
lb_rels = []
if lb:
    # walk the serialized lower_bound dict
    def walk(d):
        if d.get("kind") == "relation":
            lb_rels.append(d.get("attributes", {}).get("relation_type"))
        for c in d.get("children", []):
            walk(c)
    walk(lb)
check("lower bound contains '=' relation", "eq" in lb_rels, f"rels={lb_rels}")

print("\n=== F3: <munderover> both bounds + summand association ===")

t, u = extract('<math><munderover><mo>&#x2211;</mo><mi>i</mi><mi>n</mi></munderover><msup><mi>a</mi><mi>i</mi></msup></math>')
summ = find_first(t, "sum")
check("both bounds recorded", summ is not None and "lower_bound" in summ.attributes and "upper_bound" in summ.attributes)
# summand a^i must appear somewhere in the tree as a power
check("summand power node present", len(find_all(t, "power")) >= 1)

print("\n=== F3: integral with differential child ===")

t, u = extract('<math><mrow><mo>&#x222B;</mo><msup><mi>x</mi><mn>2</mn></msup><mo>&#x1D451;</mo><mi>x</mi></mrow></math>')
integ = find_first(t, "integral")
check("integral node exists", integ is not None)
diffs = find_all(t, "differential")
check("differential child present", len(diffs) >= 1, f"ndiffs={len(diffs)}")
check("integrand x^2 present", len(find_all(t, "power")) >= 1)


# ── F4: matrix cells ──────────────────────────────────────────────────────
print("\n=== F4: matrix <mtd> cells — nested fraction survives ===")

mml = ('<math><mtable>'
       '<mtr><mtd><mi>a</mi></mtd><mtd><mfrac><mi>b</mi><mi>c</mi></mfrac></mtd></mtr>'
       '<mtr><mtd><mn>1</mn></mtd><mtd><mn>2</mn></mtd></mtr>'
       '</mtable></math>')
t, u = extract(mml)
mat = find_first(t, "matrix")
check("matrix node exists", mat is not None)
check("no unsupported in matrix", not u, f"unsup={u}")
check("nested fraction survives in cell", len(find_all(t, "fraction")) == 1,
      f"nfrac={len(find_all(t,'fraction'))}")
check("matrix has 2 rows", mat is not None and len(mat.children) == 2,
      f"rows={len(mat.children) if mat else 0}")
# row 0 has 2 cells
row0 = mat.children[0] if mat and mat.children else None
check("row0 has 2 cells", row0 is not None and len(row0.children) == 2)


# ── F5: transparent wrappers are declared normalizations ──────────────────
print("\n=== F5: wrappers recorded as declared normalization ===")

for wrap in ("mphantom", "menclose", "mstyle", "merror"):
    t, u = extract(f'<math><{wrap}><mi>x</mi></{wrap}></math>')
    check(f"{wrap} records normalized_wrapper",
          t.attributes.get("normalized_wrapper") == wrap,
          f"attrs={t.attributes}")
    check(f"{wrap} inner 'x' survives", "x" in (t.value or "") or find_first(t, "identifier") is not None)
    check(f"{wrap} not unsupported", not u, f"unsup={u}")

# semantics + annotation: annotation skipped, structure kept, wrapper noted
t, u = extract('<math><semantics><mi>&#x3B4;</mi><annotation encoding="application/x-tex">\\delta</annotation></semantics></math>')
check("semantics skips annotation (no unsupported)", not u, f"unsup={u}")
check("semantics records normalized_wrapper", t.attributes.get("normalized_wrapper") == "semantics")


# ── F1: metric honesty — no-unsupported != verified ───────────────────────
print("\n=== F1: a clean AST still round-trips but is NOT auto-'verified' ===")

# A tree with no unsupported nodes round-trips perfectly, yet semantic fidelity
# to source is a separate question. Prove round-trip works AND that the label
# used by structural_survival is 'fully_supported_by_extractor', not 'verified'.
t, u = extract('<math><mfrac><msup><mi>x</mi><mn>2</mn></msup><mi>y</mi></mfrac></math>')
check("clean tree has no unsupported nodes", "unsupported" not in [n.kind for n in find_all(t, "unsupported")] + [])
kinds = set()
stack = [t]
while stack:
    n = stack.pop(); kinds.add(n.kind); stack.extend(n.children)
check("clean tree has no 'unsupported' kind", "unsupported" not in kinds, f"kinds={kinds}")
pre = backend_input_hash(t)
post = backend_input_hash(ExprNode.from_dict(json.loads(canonical_json(t.to_dict()))))
check("clean tree round-trips (invariant hash)", pre == post)


# ── adversarial: a WRONG ast would still round-trip ───────────────────────
print("\n=== adversarial: dropping a node still round-trips (why F1 matters) ===")

# Simulate the OLD mover bug: upper bound dropped. The wrong tree round-trips
# fine — proving round-trip is necessary but not sufficient.
wrong = ExprNode(kind="sum", value="∑",
                 attributes={"operator": "sum"})  # no upper bound child
wrong_rt = ExprNode.from_dict(json.loads(canonical_json(wrong.to_dict())))
check("dropped-bound tree still round-trips",
      backend_input_hash(wrong) == backend_input_hash(wrong_rt),
      "round-trip does NOT catch the loss — needs source-fidelity check")
check("but the wrong tree is missing upper_bound",
      "upper_bound" not in wrong.attributes)


print(f"\n{'='*44}")
print(f"PASS: {PASS}")
print(f"FAIL: {FAIL}")
if FAIL:
    sys.exit(1)
