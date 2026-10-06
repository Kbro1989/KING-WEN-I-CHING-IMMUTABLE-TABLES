import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Just try the first 10 unicode equations
count = 0
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        if expr.get('type') != 'unicode_equation':
            continue
        expr_text = expr.get('expression', '').strip()
        if not expr_text or len(expr_text) < 5:
            continue
        if '=' not in expr_text:
            continue
        if expr_text.rstrip().endswith(('=', '+', '-', '\\', 'frac', 'sqrt', 'cdot')):
            continue
        try:
            s = expr_text.replace('\\cdot', '*').replace('\\times', '*')
            s = s.replace('\\frac', '').replace('\\sqrt', '')
            s = s.replace('\\mathbf', '').replace('\\det', '')
            s = s.replace('\\(', '').replace('\\)', '')
            s = s.replace('$', '').strip().rstrip(',.')
            parts = s.split('=')
            if len(parts) != 2:
                continue
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            if not lhs or not rhs:
                continue
            lhs_val = parse_expr(lhs, transformations=transformations)
            rhs_val = parse_expr(rhs, transformations=transformations)
            variables = list(lhs_val.free_symbols) + list(rhs_val.free_symbols)
            if not variables:
                continue
            sol = sympy.solve(lhs_val - rhs_val, variables[0])
            print(f'{expr_text[:80]} -> {sol}')
        except Exception as e:
            pass
        count += 1
        if count >= 10:
            break
    if count >= 10:
        break