import sys
sys.path.insert(0, 'scripts')
from math_recovery_tool import solve_recovered, _markup_leak

print("=== PRESERVATION GATE: must reject corrupted translations ===\n")

# These are the corruptions parse_latex actually produced in the harness.
corrupt = [
    ("Delta*(W*mathbf)=mathbf*(B*(A*mathbf))", r"\Delta\mathbf{W}=\mathbf{B}\mathbf{A}"),
    ("E*mathbb", r"\mathbb{E}_{q}\left[-\log p_\theta(x_0)\right]"),
    ("alpha*bar", r"\bar{\alpha}_t\coloneqq\prod_{s=1}^{t}\alpha_s"),
    ("hat*r/n", r"\frac{1}{n}\sum_{i=1}^{n}\hat{r}_i"),
    ("q", r"q(x_t|x_0)=N(x_t,\sqrt{\alpha_t}x_0,(1-\alpha_t)I)"),
]
rejected = 0
for translated, original in corrupt:
    ok, sol, err, v, triv = solve_recovered(translated, original=original)
    status = "REJECTED" if not ok else "ACCEPTED (BAD!)"
    if not ok:
        rejected += 1
    print(f"[{status}] {translated[:42]}")
    print(f"           reason: {err}")
print(f"\nrejected {rejected}/{len(corrupt)} corrupted translations")

print("\n=== must still ACCEPT clean translations ===\n")
clean = [
    ("W=W_0+((alpha)/(r))BA", r"\mathbf{W}=\mathbf{W}_{0}+\frac{\alpha}{r}\mathbf{B}\mathbf{A}"),
    ("sigma_t**(2)=beta_t", r"\sigma_t^2=\beta_t"),
    ("L_t_1=C+E_q(Abs(mu_t(x_t,x_0)-mu_theta(x_t,t))**(2))",
     r"L_{t-1}=E_q[|\mu_t(x_t,x_0)-\mu_\theta(x_t,t)|^2]+C"),
]
accepted = 0
for translated, original in clean:
    ok, sol, err, v, triv = solve_recovered(translated, original=original)
    status = "ACCEPTED" if ok else f"REJECTED ({err})"
    if ok:
        accepted += 1
    print(f"[{status}] {translated[:42]}")
    if ok:
        print(f"           solution: {str(sol)[:50]}")
print(f"\naccepted {accepted}/{len(clean)} clean translations")
