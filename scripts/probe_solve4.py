import json, sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

# Find equations with = sign and valid math syntax
count = 0
results = []
for p in data['papers']:
    pdf_name = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
    for expr in p.get('math_expressions', []):
        et = expr.get('expression', '').strip()
        if not et or '=' not in et:
            continue
        # Only look at latex_inline and unicode_equation with simple equations
        if expr.get('type') == 'function_call':
            # function_call types like "log(1 −D(G(z)))" may have = too
            pass
        # Skip complex prose-like equations
        if len(et) > 200:
            continue
        # Skip if contains text words (prose, not math)
        if any(w in et.lower() for w in [' then ', ' is convex', ' for every', ' if ', ' then']):
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
        # Skip if contains prose remnants
        if any(cmd in lhs or cmd in rhs for cmd in ['\\frac', '\\sqrt', '\\mathbf', '\\det', '\\begin', '\\end', '\\item', '\\sum', '\\prod', '\\int', ' and ', ' or ', ' if ', ' then ', ' for ']):
            continue
        try:
            lv = parse_expr(lhs, transformations=transformations)
            rv = parse_expr(rhs, transformations=transformations)
            variables = list(lv.free_symbols) + list(rv.free_symbols)
            if not variables:
                continue
            sol = sympy.solve(lv - rv, variables[0])
            results.append({'pdf': pdf_name, 'expr': et[:120], 'vars': [str(v) for v in variables], 'sol': str(sol)[:100]})
        except Exception as e:
            pass  # Skip unparseable
        count += 1
        if count >= 20:
            break
    if count >= 20:
        break

print(f"Probed {count} equations, solved {len(results)}")
for r in results:
    print(f"  {r['pdf']}: {r['expr'][:100]}")
    print(f"    vars={r['vars']} → {r['sol']}")