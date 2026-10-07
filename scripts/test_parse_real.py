import sys, traceback
sys.path.insert(0, 'scripts')
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from math_recovery_tool import _extract_symbols, _repair_token_boundaries, _normalize_pipes

TR = standard_transformations + (implicit_multiplication_application,)

cases = [
    "L =D_KL(q(x_T),p(x_T))+E_q[Sum*D_KL(q(x_t-1,x_t),p_theta(x_t-1,x_t))]+H(x_0)",
    "L =E_q[-log((p*_theta(x*_0_T))/(q(x*_1_T,x*_0)))]",
]

for c in cases:
    print("EXPR:", c[:95])
    lhs, rhs = c.split("=")
    names, funcs = _extract_symbols(c)
    print("  names:", sorted(names)[:12])
    print("  funcs:", sorted(funcs)[:12])
    ld = {n: sympy.Symbol(n) for n in names}
    for f in funcs:
        ld[f] = sympy.Function(f)
    try:
        e = parse_expr(rhs.strip(), transformations=TR, local_dict=dict(ld))
        print("  PARSED:", str(e)[:80])
    except Exception as ex:
        print("  ERROR:", type(ex).__name__, str(ex)[:200])
    print()
