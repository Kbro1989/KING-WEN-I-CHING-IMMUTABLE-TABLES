import json, sympy, re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# Focus on the best-quality expressions: latex_inline with real LaTeX
results = []
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        if expr.get('type') != 'latex_inline':
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
            results.append({
                'pdf': p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1],
                'page': expr.get('page'),
                'expression': expr_text[:150],
                'lhs': lhs[:80],
                'rhs': rhs[:80],
                'variables': [str(v) for v in variables],
                'solution': str(sol)[:120],
            })
        except Exception:
            pass

print(f"LaTeX inline equations solved: {len(results)}")
for r in results[:20]:
    print(f"\n{r['pdf']} p.{r['page']}:")
    print(f"  {r['expression'][:120]}")
    print(f"  vars: {r['variables']}")
    print(f"  → {r['solution'][:100]}")