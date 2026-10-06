import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Quick probe: look at first paper's expressions
p = data['papers'][0]
print(f"Source: {p['source_pdf']}")
exprs = p.get('math_expressions', [])
print(f"Total expressions: {len(exprs)}")
for e in exprs[:10]:
    print(f"  type={e.get('type')}: {e.get('expression', '')[:100]}")