"""
Forensic findings — what the diffs prove is needed.

Case A: \mathbf{Y}^{\top}\mathbf{X}  ->  ((Y)*)X
  \top (transpose) is dropped, leaving a DANGLING '**'.
  In a different context that dangling '**' becomes a POWER.
  e.g. Q_Delta^{\top}Q_GS  ->  Q_Delta**Q_GS  = Q_Delta RAISED TO Q_GS. WRONG MATH.

Case B: \hat{\tilde{\mathbf{h}}}_{\Delta} - \tilde{\mathbf{h}}_{\Delta}
     -> h_tilde_Delta - h_tilde_Delta
  Nested accent collapsed: the hat was LOST, so two DISTINCT symbols
  became the SAME symbol. The expression now subtracts to zero.
  This is silent corruption, not a parse error.

Case C: \cos\theta_{i}  ->  costheta_i
  Function application without parens is glued.

Case D: \quad\text{where}\quad\mathbf{g}_j\in\mathbf{W}
  Prose 'where' glued into the formula; membership left as broken indexing.

Case E: \infty  ->  ∞  (not normalized to oo)

Case F: \|...\|_F^2  ->  |...|_F**(2)
  Double-bar norm delimiters not paired.

Each check below asserts the REQUIRED behaviour.
"""
import sys
sys.path.insert(0, 'scripts')
from mathml_parser import MathMLParser, normalize_char

print("=== normalize_char coverage ===")
for ch, want in [("∞", "oo"), ("⊤", "T"), ("∈", ""), ("∀", "")]:
    got = normalize_char(ch)
    status = "OK " if (got == want or (want == "" and got == "")) else "MISS"
    print(f"  [{status}] {ch!r} -> {got!r}  (want {want!r})")

print()
print("=== these must be FALSE today (proving the bug) ===")

# Case A: transpose must not become a power
src = '<math><semantics><mrow><msup><mi>Q</mi><mo>⊤</mo></msup><mi>Q</mi></mrow><annotation>x</annotation></semantics></math>'
from bs4 import BeautifulSoup
node = BeautifulSoup(src, "html.parser").find("math")
p = MathMLParser()
e, u = p.parse(node)
print(f"  transpose  -> {e!r}")
print(f"    creates power? {'**' in (e or '')}  (must be False)")

# Case B: nested accents must not collapse
src2 = ('<math><semantics><mrow>'
        '<mover><mover><mi>h</mi><mo>~</mo></mover><mo>^</mo></mover>'
        '<mo>-</mo>'
        '<mover><mi>h</mi><mo>~</mo></mover>'
        '</mrow><annotation>x</annotation></semantics></math>')
node2 = BeautifulSoup(src2, "html.parser").find("math")
p2 = MathMLParser()
e2, u2 = p2.parse(node2)
print(f"  nested accents -> {e2!r}")
print(f"    collapse to identical terms? {e2 is not None and e2.count('h_') >= 2 and 'h_tilde-h_tilde' in e2.replace(' ','')}  (must be False)")
