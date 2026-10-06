import json, sympy, re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# Collect all complete equations from both unicode_equation and latex_inline types
equations = []
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        expr_text = expr.get('expression', '').strip()
        if not expr_text or len(expr_text) < 5:
            continue
        if '=' not in expr_text:
            continue
        # Skip fragments that end with operators
        if expr_text.rstrip().endswith(('=', '+', '-', '\\', 'frac', 'sqrt', 'cdot')):
            continue
        equations.append({
            'pdf': p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1],
            'page': expr.get('page'),
            'type': expr.get('type'),
            'expression': expr_text,
        })

print(f"Total complete equations: {len(equations)}")

# Try to solve each
solved = 0
failed = 0
for eq in equations:
    expr_text = eq['expression']
    try:
        # Clean up: replace common LaTeX artifacts
        s = expr_text
        s = s.replace('\\cdot', '*').replace('\\times', '*')
        s = s.replace('\\frac', '').replace('\\sqrt', '')
        s = s.replace('\\mathbf', '').replace('\\det', '')
        s = s.replace('\\(', '').replace('\\)', '')
        s = s.replace('$', '').strip()
        # Remove trailing punctuation
        s = s.rstrip(',.')
        # Split on =
        parts = s.split('=')
        if len(parts) != 2:
            failed += 1
            continue
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        if not lhs or not rhs:
            failed += 1
            continue
        # Parse with implicit multiplication
        lhs_val = parse_expr(lhs, transformations=transformations)
        rhs_val = parse_expr(rhs, transformations=transformations)
        variables = list(lhs_val.free_symbols) + list(rhs_val.free_symbols)
        if not variables:
            failed += 1
            continue
        sol = sympy.solve(lhs_val - rhs_val, variables[0])
        if sol:
            print(f"\n{eq['pdf']} p.{eq['page']} [{eq['type']}]:")
            print(f"  {expr_text[:120]}")
            print(f"  → {sol}")
            solved += 1
        else:
            failed += 1
    except Exception as e:
        failed += 1

print(f"\n=== Summary: {solved} solved, {failed} failed ===")