import json, sympy, re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# Try to parse and solve all expressions, focusing on clean results
results = []
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        expr_text = expr.get('expression', '').strip()
        if not expr_text or len(expr_text) < 3:
            continue
        # Skip fragments
        if expr_text.rstrip().endswith(('=', '+', '-', '\\', 'frac', 'sqrt', 'cdot')):
            continue
        # Try to parse as sympy expression
        try:
            s = expr_text
            s = s.replace('\\cdot', '*')
            s = s.replace('\\frac', '')
            s = s.replace('\\sqrt', '')
            s = s.replace('\\mathbf', '')
            s = s.replace('\\det', '')
            s = s.replace('\\(', '').replace('\\)', '')
            s = s.replace('$', '')
            s = s.strip()
            if not s or s in ('=', '+', '-', '*', '/'):
                continue
            # Check if it has an equation
            if '=' in s:
                parts = s.split('=')
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    rhs = parts[1].strip().rstrip(',.')
                    if lhs and rhs:
                        try:
                            lhs_val = parse_expr(lhs, transformations=transformations)
                            rhs_val = parse_expr(rhs, transformations=transformations)
                            # Try to solve
                            variables = list(lhs_val.free_symbols) + list(rhs_val.free_symbols)
                            if variables:
                                sol = sympy.solve(lhs_val - rhs_val, variables[0])
                                results.append({
                                    'pdf': p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1],
                                    'page': expr.get('page'),
                                    'expression': expr_text[:150],
                                    'lhs': lhs[:80],
                                    'rhs': rhs[:80],
                                    'variables': [str(v) for v in variables],
                                    'solution': str(sol)[:100],
                                })
                        except Exception:
                            pass
        except Exception:
            pass

# Print clean, coherent results
print(f"Total solvable equations: {len(results)}")
print("\n=== CLEAN SOLUTIONS ===")
for r in results:
    print(f"\n{r['pdf']} p.{r['page']}:")
    print(f"  {r['expression'][:150]}")
    print(f"  → {r['solution'][:120]}")