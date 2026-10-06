import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Look at all expression types in first paper
p = data['papers'][0]
exprs = p.get('math_expressions', [])
print(f"Source: {p['source_pdf']}")
print(f"Total: {len(exprs)}")
from collections import Counter
types = Counter(e.get('type') for e in exprs)
print(f"Types: {dict(types)}")
for e in exprs:
    print(f"  type={e.get('type')}: {repr(e.get('expression', '')[:120])}")