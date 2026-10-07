"""
Solve extracted math equations with SymPy.
Improved LaTeX parsing: handles \\frac, \\sqrt, \\cdot, \\times, etc.
"""
import json, sympy, re
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

with open('DATASETS/semantic_math_zotero_full.json') as f:
    data = json.load(f)

transformations = standard_transformations + (implicit_multiplication_application,)

def normalize_latex(expr_text):
    """Normalize LaTeX expression for SymPy parsing."""
    s = expr_text.strip()
    
    # Replace Unicode operators with ASCII equivalents
    unicode_to_ascii = {
        '−': '-',      # Unicode minus
        '·': '*',      # Middle dot
        '×': '*',      # Multiplication sign
        '÷': '/',      # Division sign
        '±': '+/-',    # Plus-minus
        '∓': '-/+',    # Minus-plus
        '≤': '<=',     # Less than or equal
        '≥': '>=',     # Greater than or equal
        '≠': '!=',     # Not equal
        '≈': '~=',     # Approximately equal
        '≡': '==',     # Equivalent
        '∝': 'propto', # Proportional
        '∞': 'oo',     # Infinity
        '√': 'sqrt',   # Square root
        '∑': 'Sum',    # Sum
        '∏': 'Product',# Product
        '∫': 'Integral',# Integral
        '∂': 'diff',   # Partial derivative
        '∇': 'del',    # Nabla
        '∧': '&',      # And
        '∨': '|',      # Or
        '¬': '~',      # Not
        '∀': 'ForAll', # For all
        '∃': 'Exists', # Exists
        '∈': 'in',     # Element
        '∉': 'notin',  # Not element
        '⊆': 'subset', # Subset
        '⊂': 'subset', # Subset
        '∪': 'Union',  # Union
        '∩': 'Intersection', # Intersection
        '→': '->',     # Right arrow
        '⟹': '>>',     # Implies
        '⟸': '<<',     # Left arrow
        '⟷': '<->',    # Left-right arrow
        '∴': 'therefore', # Therefore
        '∵': 'because',   # Because
        '∶': 'proportion', # Proportion
        '∷': 'EqualProportion', # Equal proportion
        '≅': 'congruent', # Congruent
        '∼': 'sim',    # Similar
        '°': 'deg',    # Degree
        'ℏ': 'hbar',   # H-bar
        'ℵ': 'aleph',  # Aleph
        'π': 'pi',     # Pi
        'α': 'alpha',  # Alpha
        'β': 'beta',   # Beta
        'γ': 'gamma',  # Gamma
        'δ': 'delta',  # Delta
        'ε': 'epsilon', # Epsilon
        'ζ': 'zeta',   # Zeta
        'η': 'eta',    # Eta
        'θ': 'theta',  # Theta
        'ι': 'iota',   # Iota
        'κ': 'kappa',  # Kappa
        'λ': 'lambda', # Lambda
        'μ': 'mu',     # Mu
        'ν': 'nu',     # Nu
        'ξ': 'xi',     # Xi
        'ο': 'omicron', # Omicron
        'ρ': 'rho',    # Rho
        'σ': 'sigma',  # Sigma
        'τ': 'tau',    # Tau
        'υ': 'upsilon', # Upsilon
        'φ': 'phi',    # Phi
        'χ': 'chi',    # Chi
        'ψ': 'psi',    # Psi
        'ω': 'omega',  # Omega
        'Γ': 'Gamma',  # Capital Gamma
        'Δ': 'Delta',  # Capital Delta
        'Θ': 'Theta',  # Capital Theta
        'Λ': 'Lambda', # Capital Lambda
        'Ξ': 'Xi',     # Capital Xi
        'Π': 'Pi',     # Capital Pi
        'Σ': 'Sigma',  # Capital Sigma
        'Υ': 'Upsilon', # Capital Upsilon
        'Φ': 'Phi',    # Capital Phi
        'Ψ': 'Psi',    # Capital Psi
        'Ω': 'Omega',  # Capital Omega
        '˜': '~',      # Small tilde
        'ˆ': '^',      # Circumflex
        '¯': '-',      # Macron
        '¨': '',       # Diaeresis
        '´': '',       # Acute accent
        '`': '',       # Grave accent
        'ˇ': '',       # Caron
        '˘': '',       # Breve
        '˙': '',       # Dot above
        '¸': '',       # Cedilla
        '˝': '',       # Double acute
        '˛': '',       # Ogonek
        '˚': '',       # Ring above
        '˜': '~',      # Tilde
        '¯': '-',      # Overline
        '¨': '',       # Diaeresis
        '´': '',       # Acute accent
        '`': '',       # Grave accent
        'ˇ': '',       # Caron
        '˘': '',       # Breve
        '˙': '',       # Dot above
        '¸': '',       # Cedilla
        '˝': '',       # Double acute
        '˛': '',       # Ogonek
        '˚': '',       # Ring above
    }
    for unicode_char, ascii_char in unicode_to_ascii.items():
        s = s.replace(unicode_char, ascii_char)
    
    # Remove LaTeX commands that SymPy can't handle
    # \frac{a}{b} -> (a)/(b)
    s = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', s)
    # \sqrt{a} -> sqrt(a)
    s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)
    # \mathbf{a} -> a
    s = re.sub(r'\\mathbf\{([^{}]+)\}', r'\1', s)
    # \det -> det
    s = s.replace('\\det', 'det')
    # \cdot -> *
    s = s.replace('\\cdot', '*')
    # \times -> *
    s = s.replace('\\times', '*')
    # \ge -> >=
    s = s.replace('\\ge', '>=')
    # \le -> <=
    s = s.replace('\\le', '<=')
    # \neq -> !=
    s = s.replace('\\neq', '!=')
    # \infty -> oo
    s = s.replace('\\infty', 'oo')
    # \pi -> pi
    s = s.replace('\\pi', 'pi')
    # \alpha -> alpha
    s = s.replace('\\alpha', 'alpha')
    # \beta -> beta
    s = s.replace('\\beta', 'beta')
    # \gamma -> gamma
    s = s.replace('\\gamma', 'gamma')
    # \sigma -> sigma
    s = s.replace('\\sigma', 'sigma')
    # \epsilon -> epsilon
    s = s.replace('\\epsilon', 'epsilon')
    # \lambda -> lambda
    s = s.replace('\\lambda', 'lambda')
    # \mu -> mu
    s = s.replace('\\mu', 'mu')
    # \theta -> theta
    s = s.replace('\\theta', 'theta')
    # \phi -> phi
    s = s.replace('\\phi', 'phi')
    # \omega -> omega
    s = s.replace('\\omega', 'omega')
    # \sum -> Sum
    s = s.replace('\\sum', 'Sum')
    # \prod -> Product
    s = s.replace('\\prod', 'Product')
    # \int -> Integral
    s = s.replace('\\int', 'Integral')
    # \partial -> diff
    s = s.replace('\\partial', 'diff')
    # \nabla -> del
    s = s.replace('\\nabla', 'del')
    # \forall -> ForAll
    s = s.replace('\\forall', 'ForAll')
    # \exists -> Exists
    s = s.replace('\\exists', 'Exists')
    # \in -> in
    s = s.replace('\\in', 'in')
    # \notin -> notin
    s = s.replace('\\notin', 'notin')
    # \subset -> subset
    s = s.replace('\\subset', 'subset')
    # \subseteq -> subseteq
    s = s.replace('\\subseteq', 'subseteq')
    # \cup -> Union
    s = s.replace('\\cup', 'Union')
    # \cap -> Intersection
    s = s.replace('\\cap', 'Intersection')
    # \wedge -> &
    s = s.replace('\\wedge', '&')
    # \vee -> |
    s = s.replace('\\vee', '|')
    # \neg -> ~
    s = s.replace('\\neg', '~')
    # \rightarrow -> ->
    s = s.replace('\\rightarrow', '->')
    # \Rightarrow -> >>
    s = s.replace('\\Rightarrow', '>>')
    # \LeftArrow -> <<
    s = s.replace('\\LeftArrow', '<<')
    # \leftrightarrow -> <->
    s = s.replace('\\leftrightarrow', '<->')
    # \boxed{...} -> ...
    s = re.sub(r'\\boxed\{([^{}]+)\}', r'\1', s)
    # \text{...} -> ...
    s = re.sub(r'\\text\{([^{}]+)\}', r'\1', s)
    # \mathrm{...} -> ...
    s = re.sub(r'\\mathrm\{([^{}]+)\}', r'\1', s)
    # \mathbb{...} -> ...
    s = re.sub(r'\\mathbb\{([^{}]+)\}', r'\1', s)
    # \mathcal{...} -> ...
    s = re.sub(r'\\mathcal\{([^{}]+)\}', r'\1', s)
    # \left( -> (
    s = s.replace('\\left(', '(')
    # \right) -> )
    s = s.replace('\\right)', ')')
    # \left[ -> [
    s = s.replace('\\left[', '[')
    # \right] -> ]
    s = s.replace('\\right]', ']')
    # \left\{ -> {
    s = s.replace('\\left\\{', '{')
    # \right\} -> }
    s = s.replace('\\right\\}', '}')
    # Remove remaining backslash commands
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    # Remove braces
    s = s.replace('{', '').replace('}', '')
    # Remove dollar signs
    s = s.replace('$', '')
    # Strip whitespace
    s = s.strip()
    
    return s

def is_valid_equation(s):
    """Check if string looks like a valid equation."""
    if not s or len(s) < 3:
        return False
    if '=' not in s:
        return False
    # Skip if contains prose words
    prose_words = ['the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has', 'had', 'been', 'are', 'was', 'were', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cannot', 'not', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither', 'each', 'every', 'all', 'some', 'any', 'no', 'none', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'last', 'next', 'previous', 'following', 'above', 'below', 'under', 'over', 'between', 'among', 'through', 'during', 'before', 'after', 'since', 'until', 'while', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'if', 'then', 'else', 'because', 'as', 'than', 'though', 'although', 'even', 'just', 'only', 'also', 'very', 'too', 'quite', 'rather', 'somewhat', 'almost', 'nearly', 'hardly', 'scarcely', 'barely', 'completely', 'totally', 'entirely', 'fully', 'partly', 'partially', 'half', 'twice', 'thrice', 'once', 'again', 'further', 'moreover', 'furthermore', 'however', 'nevertheless', 'nonetheless', 'otherwise', 'instead', 'meanwhile', 'afterward', 'afterwards', 'earlier', 'later', 'soon', 'now', 'then', 'here', 'there', 'everywhere', 'somewhere', 'anywhere', 'nowhere', 'elsewhere', 'everyplace', 'someplace', 'anyplace', 'noplace', 'elseplace', 'everyway', 'someway', 'anyway', 'noway', 'elseway', 'everytime', 'sometime', 'anytime', 'notime', 'else time', 'everyday', 'someday', 'anyday', 'noday', 'elseday', 'everynight', 'somenight', 'anynight', 'nonight', 'elsenight', 'everyweek', 'someweek', 'anyweek', 'noweek', 'elseweek', 'everymonth', 'somemonth', 'anymonth', 'nomonth', 'elsemonth', 'everyyear', 'someweary', 'anyyear', 'noyear', 'elseyear', 'everyhour', 'somehour', 'anyhour', 'nohour', 'elsehour', 'everyminute', 'someminute', 'anyminute', 'nominute', 'elseminute', 'everysecond', 'somesecond', 'anysecond', 'nosecond', 'elsesecond', 'everymoment', 'somemoment', 'anymoment', 'nomoment', 'elsemoment', 'everywhile', 'somewhile', 'anywhile', 'nowhile', 'elsewhile', 'everywhere', 'somewhere', 'anywhere', 'nowhere', 'elsewhere', 'everyplace', 'someplace', 'anyplace', 'noplace', 'elseplace', 'everyway', 'someway', 'anyway', 'noway', 'elseway', 'everytime', 'sometime', 'anytime', 'notime', 'else time', 'everyday', 'someday', 'anyday', 'noday', 'elseday', 'everynight', 'somenight', 'anynight', 'nonight', 'elsenight', 'everyweek', 'someweek', 'anyweek', 'noweek', 'elseweek', 'everymonth', 'somemonth', 'anymonth', 'nomonth', 'elsemonth', 'everyyear', 'someweary', 'anyyear', 'noyear', 'elseyear', 'everyhour', 'somehour', 'anyhour', 'nohour', 'elsehour', 'everyminute', 'someminute', 'anyminute', 'nominute', 'elseminute', 'everysecond', 'somesecond', 'anysecond', 'nosecond', 'elsesecond', 'everymoment', 'somemoment', 'anymoment', 'nomoment', 'elsemoment', 'everywhile', 'somewhile', 'anywhile', 'nowhile', 'elsewhile']
    s_lower = s.lower()
    for word in prose_words:
        if f' {word} ' in f' {s_lower} ':
            return False
    return True

results = []
errors = []
skipped = 0
total = 0

for p in data['papers']:
    pdf_name = p['source_pdf'].replace('\\', '/').rsplit('/', 1)[-1]
    for expr in p.get('math_expressions', []):
        total += 1
        et = expr.get('expression', '').strip()
        if not et or len(et) < 5:
            skipped += 1
            continue
        if '=' not in et:
            skipped += 1
            continue
        
        # Normalize LaTeX
        s = normalize_latex(et)
        
        if not s or s in ('=', '+', '-', '*', '/'):
            skipped += 1
            continue
        
        # Check if valid equation
        if not is_valid_equation(s):
            skipped += 1
            continue
        
        parts = s.split('=')
        if len(parts) != 2:
            skipped += 1
            continue
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        if not lhs or not rhs:
            skipped += 1
            continue
        
        # Skip if too complex
        if len(lhs) > 100 or len(rhs) > 100:
            skipped += 1
            continue
        
        try:
            lv = parse_expr(lhs, transformations=transformations)
            rv = parse_expr(rhs, transformations=transformations)
            variables = list(lv.free_symbols) + list(rv.free_symbols)
            if not variables:
                skipped += 1
                continue
            
            # Only solve if single variable
            if len(variables) > 1:
                skipped += 1
                continue
            
            sol = sympy.solve(lv - rv, variables[0])
            results.append({
                'pdf': pdf_name,
                'page': expr.get('page'),
                'expression': et[:150],
                'normalized': s[:150],
                'lhs': lhs[:80],
                'rhs': rhs[:80],
                'variables': [str(v) for v in variables],
                'solution': str(sol)[:120],
            })
        except Exception as e:
            errors.append({'pdf': pdf_name, 'expression': et[:80], 'normalized': s[:80], 'error': str(e)})

output = {
    'total_expressions_scanned': total,
    'skipped': skipped,
    'solved': len(results),
    'errors': len(errors),
    'results': results,
    'error_samples': errors[:20],
}

with open('DATASETS/solved_equations.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Scanned: {total}, Solved: {len(results)}, Skipped: {skipped}, Errors: {len(errors)}")
print(f"Results written to DATASETS/solved_equations.json")

if results:
    print("\nSolved equations:")
    for r in results:
        print(f"  {r['pdf']} p.{r['page']}: {r['expression'][:80]}")
        print(f"    normalized: {r['normalized'][:80]}")
        print(f"    vars: {r['variables']} → {r['solution'][:80]}")