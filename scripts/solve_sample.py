import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

count = 0
solved = 0
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        expr_text = expr.get('expression', '').strip()
        if not expr_text or len(expr_text) < 5:
            continue
        if '=' not in expr_text:
            continue
        if expr_text.rstrip().endswith(('=', '+', '-', '\\', 'frac', 'sqrt', 'cdot')):
            continue
        has_op = any(op in expr_text for op in ['=', '+', '-', '*', '/', '^'])
        if not has_op:
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
            solved += 1
        except Exception:
            pass
        count += 1
        if count >= 50:
            break
    if count >= 50:
        break
print(f'--- Attempted {count}, solved {solved} ---')