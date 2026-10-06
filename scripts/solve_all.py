import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Collect all solvable equations, write results to JSON
results = []
errors = []
skipped = 0
total = 0

for p in data['papers']:
    pdf_name = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
    for expr in p.get('math_expressions', []):
        total += 1
        expr_text = expr.get('expression', '').strip()
        if not expr_text or len(expr_text) < 5:
            skipped += 1
            continue
        if '=' not in expr_text:
            skipped += 1
            continue
        if expr_text.rstrip().endswith(('=', '+', '-', '\\', 'frac', 'sqrt', 'cdot', '·', '×')):
            skipped += 1
            continue
        try:
            s = expr_text.replace('\\cdot', '*').replace('\\times', '*').replace('·', '*')
            s = s.replace('\\frac', '').replace('\\sqrt', '')
            s = s.replace('\\mathbf', '').replace('\\det', '')
            s = s.replace('\\(', '').replace('\\)', '')
            s = s.replace('$', '').strip().rstrip(',.')
            if not s or s in ('=', '+', '-', '*', '/'):
                skipped += 1
                continue
            parts = s.split('=')
            if len(parts) != 2:
                skipped += 1
                continue
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            if not lhs or not rhs:
                skipped += 1
                continue
            if any(cmd in lhs or cmd in rhs for cmd in ['\\frac', '\\sqrt', '\\mathbf', '\\det', '\\begin', '\\end', '\\item', '\\sum', '\\prod', '\\int']):
                skipped += 1
                continue
            lv = parse_expr(lhs, transformations=transformations)
            rv = parse_expr(rhs, transformations=transformations)
            variables = list(lv.free_symbols) + list(rv.free_symbols)
            if not variables:
                skipped += 1
                continue
            sol = sympy.solve(lv - rv, variables[0])
            results.append({
                'pdf': pdf_name,
                'page': expr.get('page'),
                'expression': expr_text[:150],
                'lhs': lhs[:80],
                'rhs': rhs[:80],
                'variables': [str(v) for v in variables],
                'solution': str(sol)[:120],
            })
        except Exception as e:
            errors.append({'pdf': pdf_name, 'expression': expr_text[:80], 'error': str(e)})

output = {
    'total_expressions_scanned': total,
    'skipped': skipped,
    'solved': len(results),
    'errors': len(errors),
    'results': results,
    'error_samples': errors[:20],
}

with open('DATASETS/solved_equations.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Scanned: {total}, Solved: {len(results)}, Skipped: {skipped}, Errors: {len(errors)}")
print(f"Results written to DATASETS/solved_equations.json")
print("\nFirst 10 results:")
for r in results[:10]:
    print(f"  {r['pdf']} p.{r['page']}: {r['expression'][:80]}")
    print(f"    vars: {r['variables']} → {r['solution'][:80]}")