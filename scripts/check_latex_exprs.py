import json, sympy, re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

# Collect all latex_inline and latex_display expressions
latex_exprs = []
for p in data['papers']:
    for expr in p.get('math_expressions', []):
        if expr.get('type') in ('latex_inline', 'latex_display'):
            pdf_name = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
            latex_exprs.append({
                'pdf': pdf_name,
                'page': expr.get('page'),
                'expression': expr.get('expression', ''),
                'context': expr.get('context', '')[:100],
            })

print(f"Total LaTeX expressions: {len(latex_exprs)}")
print("Sample expressions:")
for e in latex_exprs[:10]:
    print(f"  {e['pdf']} p.{e['page']}: {e['expression'][:120]}")