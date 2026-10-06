import json, sympy, re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

# Try to parse and solve LaTeX expressions
transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

solvable = []
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        if expr.get('type') == 'latex_inline':
            expr_text = expr.get('expression', '').strip()
            if not expr_text or len(expr_text) < 3:
                continue
            # Skip if it's just a fragment (ends with =, +, etc.)
            if expr_text.rstrip().endswith(('=', '+', '-', '\\', 'frac', 'sqrt')):
                continue
            # Try to parse
            try:
                # Replace common LaTeX with sympy-compatible
                s = expr_text.replace('\\frac', ' ').replace('\\sqrt', ' ').replace('\\(', '').replace('\\)', '')
                # Check if it has an equation
                if '=' in s:
                    parts = s.split('=')
                    if len(parts) == 2:
                        lhs = parts[0].strip()
                        rhs = parts[1].strip()
                        if lhs and rhs:
                            solvable.append({
                                'pdf': p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1],
                                'page': expr.get('page'),
                                'expression': expr_text,
                                'lhs': lhs,
                                'rhs': rhs,
                            })
            except Exception:
                pass

print(f"Solvable equations found: {len(solvable)}")
for s in solvable[:15]:
    print(f"\n{s['pdf']} p.{s['page']}:")
    print(f"  {s['expression'][:150]}")
    print(f"  LHS: {s['lhs'][:80]}")
    print(f"  RHS: {s['rhs'][:80]}")