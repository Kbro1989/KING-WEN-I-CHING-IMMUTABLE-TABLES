import sys, json, glob
sys.path.insert(0, 'scripts')
from math_recovery_tool import (_repair_token_boundaries, _normalize_pipes,
                                _extract_symbols, _normalize_function_brackets)
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

TR = standard_transformations + (implicit_multiplication_application,)

shown = 0
for f in sorted(glob.glob('DATASETS/math_recovery_display/*_recovery.json')):
    d = json.load(open(f))
    for r in d.get('results', []):
        if r.get('error') != 'parse:SyntaxError':
            continue
        if shown >= 10:
            break
        e = r['recovered']
        p = _repair_token_boundaries(e)
        p = _normalize_pipes(p)
        parts = [x.strip() for x in p.split("=")]
        if len(parts) >= 3 and parts[0] and parts[1]:
            p = parts[0] + "=" + parts[1]
        if p.count("=") != 1:
            continue
        names, funcs = _extract_symbols(p)
        p2 = _normalize_function_brackets(p, funcs)
        lhs, rhs = p2.split("=")
        ld = {n: sympy.Symbol(n) for n in names}
        for op in ("Sum", "Prod", "Integral", "Limit"):
            ld.setdefault(op, sympy.Symbol(op))
        for fn in funcs:
            ld[fn] = sympy.Function(fn)
        for side, txt in (("LHS", lhs), ("RHS", rhs)):
            try:
                parse_expr(txt.strip(), transformations=TR, local_dict=dict(ld))
            except Exception as ex:
                print(f"EXPR: {p2[:100]}")
                print(f"  {side} FAIL: {type(ex).__name__}: {str(ex)[:90]}")
                print(f"  {side} TEXT: {txt.strip()[:100]}")
                print()
                shown += 1
                break
    if shown >= 10:
        break
