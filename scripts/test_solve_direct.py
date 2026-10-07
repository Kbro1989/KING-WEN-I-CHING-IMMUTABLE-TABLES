import sys
sys.path.insert(0, 'scripts')
from math_recovery_tool import solve_recovered, _repair_token_boundaries, _normalize_pipes

cases = [
    "L =D_KL(q(x_T)|p(x_T))+E_q[SumD_KL(q(x_t-1|x_t)|p_theta(x_t-1|x_t))]+H(x_0)",
    "L =E_q[-log((p*_theta(x*_0_T))/(q(x*_1_T|x*_0)))]",
    "L =E_q[-logp(x_T)-Sumlog((p_theta(x_t-1|x_t))/(q(x_t|x_t-1)))]",
    "L_t-1=E_q[((1)/(2sigma_t**(2)))((|mu_t(x_t,x_0)-mu_theta(x_t,t)|)**(2))]+C",
]

for c in cases:
    print("IN  :", c[:100])
    print("  repair->", _repair_token_boundaries(c)[:100])
    print("  pipes ->", _normalize_pipes(_repair_token_boundaries(c))[:100])
    ok, sol, err, v, triv = solve_recovered(c)
    print(f"  RESULT ok={ok} err={err} sol={str(sol)[:60]}")
    print()
