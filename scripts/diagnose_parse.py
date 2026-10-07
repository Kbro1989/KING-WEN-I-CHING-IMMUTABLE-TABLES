import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
import urllib.request, json
from bs4 import BeautifulSoup
from mathml_parser import MathMLParser
from display_equation_extractor import parse_display_equations

sys.path.insert(0, 'scripts')
from math_recovery_tool import solve_recovered, _extract_symbols
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

url = 'https://arxiv.org/html/2006.11239'
req = urllib.request.Request(url, headers={'User-Agent': 'x/1.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

rows = parse_display_equations(html, MathMLParser)
print('=== DIAGNOSING PARSE FAILURES ===')
for r in rows:
    e = r.get('expr')
    if not e or e.count('=') != 1:
        continue
    ok, sol, err, v, triv = solve_recovered(e)
    if ok:
        continue
    if err and err.startswith('parse:'):
        print()
        print('EXPR:', e[:110])
        print('ERR :', err)
        # reproduce the parse to get the real message
        lhs, rhs = e.split('=')
        names, funcs = _extract_symbols(e)
        ld = {n: sympy.Symbol(n) for n in names}
        for f in funcs:
            ld[f] = sympy.Function(f)
        try:
            parse_expr(lhs.strip(), transformations=standard_transformations + (implicit_multiplication_application,), local_dict=dict(ld))
        except Exception as ex:
            print('  LHS parse error:', type(ex).__name__, str(ex)[:150])
        try:
            parse_expr(rhs.strip(), transformations=standard_transformations + (implicit_multiplication_application,), local_dict=dict(ld))
        except Exception as ex:
            print('  RHS parse error:', type(ex).__name__, str(ex)[:150])
