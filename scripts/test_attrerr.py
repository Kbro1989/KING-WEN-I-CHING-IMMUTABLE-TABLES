import sys, traceback
sys.path.insert(0, 'scripts')
from math_recovery_tool import (_repair_token_boundaries, _normalize_pipes,
                                _extract_symbols, _normalize_function_brackets)
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

TR = standard_transformations + (implicit_multiplication_application,)

cases = [
 "p_theta(x_0_T) =p(x_T)Prodp_theta(x_t-1|x_t),p_theta(x_t-1|x_t)=N(x_t-1,mu_theta(x_t,t),Sigma_t",
 "q(x_1_T|x_0) =Prodq(x_t|x_t-1),q(x_t|x_t-1)=N(x_t,sqrt(1-beta_t)x_t-1,beta_tI)",
 "q(x_t-1|x_t,x_0) =N(x_t-1,mu_t(x_t,x_0),beta_tI),",
]

for c in cases:
    print("RAW   :", c[:90])
    r = _repair_token_boundaries(c)
    print("REPAIR:", r[:90])
    p = _normalize_pipes(r)
    print("PIPES :", p[:90])
    # chain reduce
    parts = [x.strip() for x in p.split("=")]
    if len(parts) >= 3 and parts[0] and parts[1]:
        p2 = parts[0] + "=" + parts[1]
    else:
        p2 = p
    names, funcs = _extract_symbols(p2)
    p3 = _normalize_function_brackets(p2, funcs)
    lhs, rhs = p3.split("=")
    ld = {n: sympy.Symbol(n) for n in names}
    for op in ("Sum","Prod","Integral","Limit"):
        ld.setdefault(op, sympy.Symbol(op))
    for f in funcs:
        ld[f] = sympy.Function(f)
    try:
        le = parse_expr(lhs.strip(), transformations=TR, local_dict=dict(ld))
        re_ = parse_expr(rhs.strip(), transformations=TR, local_dict=dict(ld))
        print("  parsed OK")
        vs = le.free_symbols | re_.free_symbols
        print("  vars:", sorted(str(v) for v in vs)[:8])
    except Exception as ex:
        print("  ERR:", type(ex).__name__, str(ex)[:160])
        traceback.print_exc(limit=2)
    print()
