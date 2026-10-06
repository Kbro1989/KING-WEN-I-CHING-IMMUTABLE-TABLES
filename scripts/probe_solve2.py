import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Test on first paper
p = data['papers'][0]
print(f"PDF: {p['source_pdf'].rsplit(chr(92), 1)[-1]}")
print(f"Expressions: {len(p.get('math_expressions', []))}")

count = 0
for expr in p.get('math_expressions', []):
    et = expr.get('expression', '').strip()
    if not et or '=' not in et:
        continue
    s = et.replace('\\cdot', '*').replace('\\times', '*').replace('·', '*')
    s = s.replace('\\frac', '').replace('\\sqrt', '')
    s = s.replace('\\(', '').replace('\\)', '')
    s = s.replace('$', '').strip().rstrip(',.')
    parts = s.split('=')
    if len(parts) != 2:
        continue
    lhs = parts[0].strip()
    rhs = parts[1].strip()
    if not lhs or not rhs:
        continue
    try:
        lv = parse_expr(lhs, transformations=transformations)
        rv = parse_expr(rhs, transformations=transformations)
        vars = list(lv.free_symbols) + list(rv.free_symbols)
        if not vars:
            continue
        sol = sympy.solve(lv - rv, vars[0])
        print(f"  {et[:80]} -> {sol}")
        count += 1
    except Exception as e:
        print(f"  {et[:80]} -> ERROR: {e}")
        count += 1
    if count >= 10:
        break