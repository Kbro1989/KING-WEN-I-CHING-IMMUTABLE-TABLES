"""
Correctness harness for LaTeX -> SymPy paths.

A parser that returns an expression is NOT correct. It must return an expression
whose free symbols match the identifiers actually present in the LaTeX, and whose
structure survives round-trip.

This measures SILENT CORRUPTION, not just parse success.
"""
import re
import sympy
from sympy.parsing.latex import parse_latex

CASES = [
    # (latex, must_not_contain_symbols)
    (r"\Delta\mathbf{W}=\mathbf{B}\mathbf{A}", {"mathbf"}),
    (r"\sigma_t^2=\beta_t", set()),
    (r"L_{t-1}=E_q[|\mu_t(x_t,x_0)-\mu_\theta(x_t,t)|^2]+C", set()),
    (r"q(x_t|x_0)=N(x_t,\sqrt{\alpha_t}x_0,(1-\alpha_t)I)", set()),
    (r"\frac{1}{n}\sum_{i=1}^{n}\hat{r}_i", set()),
    (r"\mathbb{E}_{q}\left[-\log p_\theta(x_0)\right]", {"mathbb"}),
    (r"\bar{\alpha}_t\coloneqq\prod_{s=1}^{t}\alpha_s", {"bar"}),
    (r"\mathcal{L}(\theta)=\mathbb{E}[\epsilon-\epsilon_\theta(x_t,t)]", {"mathcal", "mathbb"}),
]

# Markup commands that must NEVER appear as symbols in a correct parse
MARKUP = {
    "mathbf", "mathbb", "mathcal", "mathrm", "mathit", "mathsf", "mathtt",
    "mathfrak", "mathscr", "boldsymbol", "text", "mbox", "operatorname",
    "bar", "hat", "vec", "dot", "ddot", "tilde", "widehat", "widetilde",
    "overline", "underline", "left", "right", "big", "Big", "frac", "sqrt",
}

def symbols_of(expr):
    try:
        return {str(s) for s in expr.free_symbols}
    except Exception:
        return set()

def check_parse_latex(latex):
    """Return (parsed_ok, corrupted, symbols, note)."""
    try:
        e = parse_latex(latex)
    except Exception as ex:
        return False, False, set(), f"parse_error:{type(ex).__name__}"

    syms = symbols_of(e)
    leaked = {s for s in syms if s.lower() in MARKUP}
    # Also detect a "parse" that dropped most of the expression
    note = ""
    if leaked:
        note = f"markup_leaked:{sorted(leaked)}"
        return True, True, syms, note

    # Structural collapse: input has '=' but output has no Eq / relational
    if "=" in latex and not isinstance(e, (sympy.Eq, sympy.Rel)):
        # could be a function call parsed as a bare symbol
        note = f"structure_lost:got_{type(e).__name__}"
        return True, True, syms, note

    return True, False, syms, note


if __name__ == "__main__":
    print("=== parse_latex SILENT-CORRUPTION CHECK ===")
    print()
    parsed = corrupted = 0
    for latex, must_not in CASES:
        ok, bad, syms, note = check_parse_latex(latex)
        parsed += 1 if ok else 0
        corrupted += 1 if bad else 0
        tag = "CORRUPT" if bad else ("ok" if ok else "parse-fail")
        print(f"[{tag:10s}] {latex[:60]}")
        if note:
            print(f"             {note}")
        print(f"             symbols: {sorted(syms)[:8]}")
        print()

    print(f"parsed:    {parsed}/{len(CASES)}")
    print(f"corrupted: {corrupted}/{len(CASES)}   <-- silently wrong")
    print(f"clean:     {parsed - corrupted}/{len(CASES)}")
