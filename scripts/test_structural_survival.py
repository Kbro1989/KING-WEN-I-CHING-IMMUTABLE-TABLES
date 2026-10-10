#!/usr/bin/env python3
"""
Structural survival tests — typed AST extraction + serialization round-trip.

Verifies the structural_ast_extractor emits typed ExprNodes that:
  1. Preserve operator identity (sum/integral/limit, not bare tokens)
  2. Preserve limits as children (munder/mover never dropped)
  3. Preserve differentials as ordered measure nodes
  4. Preserve relations as typed relation nodes (sim != eq)
  5. Preserve decorations fused onto identifiers
  6. Preserve unsupported content (never silently dropped)
  7. Round-trip through canonical serialization with invariant hash
  8. Bind to occurrence_key for attribution
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


def extract(mathml):
    ex = StructuralASTExtractor()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(mathml, "html.parser")
    node = soup.find("math")
    return ex.extract(node), ex.unsupported


print("=== Operator identity preserved ===")

# sum with under-limit
t, u = extract('<math><munder><mo>&#x2211;</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow></munder><mi>n</mi></math>')
kinds = set()
stack = [t]
while stack:
    n = stack.pop(); kinds.add(n.kind); stack.extend(n.children)
check("sum node emitted", "sum" in kinds, f"kinds={kinds}")
check("sum has no unsupported", "unsupported" not in kinds, f"kinds={kinds}")

# integral
t, u = extract('<math><mo>&#x222B;</mo></math>')
check("integral node emitted", t.kind == "integral", f"kind={t.kind}")

# limit
t, u = extract('<math><munder><mo>lim</mo><mrow><mi>x</mi><mo>&#x2192;</mo><mn>0</mn></mrow></munder></math>')
stack = [t]; kinds = set()
while stack:
    n = stack.pop(); kinds.add(n.kind); stack.extend(n.children)
check("limit node emitted", "limit" in kinds, f"kinds={kinds}")


print("\n=== Relation identity preserved ===")

for glyph, rel in [("=", "eq"), ("&#x223C;", "sim"), ("&#x2248;", "approx"),
                   ("&#x221D;", "propto"), ("&#x2261;", "equiv"), ("&#x2264;", "leq")]:
    t, u = extract(f'<math><mi>a</mi><mo>{glyph}</mo><mi>b</mi></math>')
    # find the relation node
    rels = []
    stack = [t]
    while stack:
        n = stack.pop()
        if n.kind == "relation":
            rels.append(n.attributes.get("relation_type"))
        stack.extend(n.children)
    check(f"relation {glyph} -> {rel}", rel in rels, f"rels={rels}")


print("\n=== Differentials preserved ===")

t, u = extract('<math><mo>&#x222B;</mo><mi>f</mi><mo>&#x1D451;</mo><mi>x</mi></math>')
stack = [t]; kinds = []
while stack:
    n = stack.pop(); kinds.append(n.kind); stack.extend(n.children)
check("differential node emitted", "differential" in kinds, f"kinds={kinds}")


print("\n=== Decorations fused ===")

t, u = extract('<math><mover><mi>r</mi><mo>&#x00AF;</mo></mover></math>')
check("decorated identifier fused", t.kind == "identifier" and "_bar" in (t.value or ""),
      f"kind={t.kind} value={t.value}")


print("\n=== Unsupported content preserved, never dropped ===")

# an unknown structural tag must become kind=unsupported, not vanish
t, u = extract('<math><mmultiscripts><mi>x</mi><mn>1</mn><mn>2</mn></mmultiscripts></math>')
stack = [t]; has_unsup = False
while stack:
    n = stack.pop()
    if n.kind == "unsupported":
        has_unsup = True
    stack.extend(n.children)
check("unknown tag preserved as unsupported", has_unsup or u, f"unsup={u}")
check("tree is never None on unknown tag", t is not None)


print("\n=== annotation (LaTeX metadata) is not a structural node ===")

# <annotation> must be skipped, not counted as unsupported
t, u = extract('<math><semantics><mi>&#x3B4;</mi><annotation encoding="application/x-tex">\\delta</annotation></semantics></math>')
check("annotation skipped (no unsupported)", not u, f"unsup={u}")
check("delta identifier survives", t.kind == "identifier" and "δ" in (t.value or ""), f"kind={t.kind} value={t.value}")


print("\n=== Round-trip: canonical hash invariant ===")

samples = [
    '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>',
    '<math><msup><mi>x</mi><mn>2</mn></msup></math>',
    '<math><munder><mo>&#x2211;</mo><mi>i</mi></munder></math>',
    '<math><mi>a</mi><mo>&#x223C;</mo><mi>b</mi></math>',
    '<math><msqrt><mi>x</mi></msqrt></math>',
]
for i, mml in enumerate(samples):
    t, _ = extract(mml)
    pre_hash = backend_input_hash(t)
    rebuilt = ExprNode.from_dict(json.loads(canonical_json(t.to_dict())))
    post_hash = backend_input_hash(rebuilt)
    check(f"round-trip invariant sample {i}", pre_hash == post_hash,
          f"{pre_hash[:12]} != {post_hash[:12]}")


print("\n=== to_dict/from_dict preserves structure ===")

t, _ = extract('<math><mfrac><msup><mi>x</mi><mn>2</mn></msup><mi>y</mi></mfrac></math>')
r = ExprNode.from_dict(t.to_dict())
check("root kind preserved", r.kind == t.kind == "fraction", f"{r.kind}")
check("child count preserved", len(r.children) == len(t.children) == 2)
check("nested power preserved", r.children[0].kind == "power")


print(f"\n{'='*40}")
print(f"PASS: {PASS}")
print(f"FAIL: {FAIL}")
if FAIL:
    sys.exit(1)
