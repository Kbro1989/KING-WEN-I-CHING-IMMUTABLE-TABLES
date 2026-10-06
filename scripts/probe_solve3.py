import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Test on first 3 papers, first 5 equations each
count = 0
results = []
for p in data['papers'][:3]:
    pdf_name = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
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
        if any(cmd in lhs or cmd in rhs for cmd in ['\\frac', '\\sqrt', '\\mathbf', '\\det', '\\begin', '\\end', '\\item', '\\sum', '\\prod', '\\int']):
            continue
        try:
            lv = parse_expr(lhs, transformations=transformations)
            rv = parse_expr(rhs, transformations=transformations)
            variables = list(lv.free_symbols) + list(rv.free_symbols)
            if not variables:
                continue
            sol = sympy.solve(lv - rv, variables[0])
            results.append({'pdf': pdf_name, 'expr': et[:100], 'vars': [str(v) for v in variables], 'sol': str(sol)[:80]})
        except Exception as e:
            results.append({'pdf': pdf_name, 'expr': et[:100], 'error': str(e)})
        count += 1
        if count >= 15:
            break
    if count >= 15:
        break

print(f"Probed {count} equations")
for r in results:
    if 'error' in r:
        print(f"  ERR {r['pdf']}: {r['expr'][:80]} -> {r['error']}")
    else:
        print(f"  OK  {r['pdf']}: {r['expr'][:80]}")
        print(f"      vars={r['vars']} sol={r['sol']}")