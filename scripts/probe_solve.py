import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Quick probe: just first 5 papers, first 3 equations each
count = 0
results = []
for p in data['papers'][:5]:
    for expr in p.get('math_expressions', []):
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
            if not s or s in ('=', '+', '-', '*', '/'):
                continue
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
            results.append({'pdf': p['source_pdf'].rsplit('/', 1)[-1], 'expr': expr_text[:100], 'vars': [str(v) for v in variables], 'sol': str(sol)[:80]})
        except Exception:
            pass
        count += 1
        if count >= 15:
            break
    if count >= 15:
        break

print(f"Probed {count} equations, solved {len(results)}")
for r in results:
    print(f"  {r['pdf']}: {r['expr'][:80]} = {r['sol']}")