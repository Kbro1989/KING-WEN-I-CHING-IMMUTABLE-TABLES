"""
Comprehensive LaTeX Command Registry
=====================================
Defines ALL LaTeX commands for proper equation parsing.
Covers: bracing, structures, environments, delimiters,
accents, operators, functions, matrices, cases, and more.

This is the complete definition set for research paper LaTeX.
"""
import json, re
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

transformations = standard_transformations + (implicit_multiplication_application,)

def is_complete_equation(latex):
    """Check if a LaTeX string is a complete equation."""
    if not latex or len(latex) < 3:
        return False
    if '=' in latex:
        return True
    if any(op in latex for op in ['+', '-', '*', '/']):
        return True
    if any(fn in latex for fn in ['frac', 'sum', 'int', 'prod', 'sqrt']):
        return True
    return False

# ============================================================================
# COMPREHENSIVE LaTeX COMMAND DEFINITIONS
# ============================================================================

# 1. BRACING AND GROUPING
# ============================================================================
# Braces {} are used for grouping in LaTeX
# \left and \right create scalable delimiters
# \big, \Big, \bigg, \Bigg create fixed-size delimiters

BRACING_COMMANDS = {
    # Left/right delimiters
    'left': 'delimiter_start',
    'right': 'delimiter_end',
    
    # Fixed-size delimiters
    'big': 'delimiter',
    'Big': 'delimiter',
    'bigg': 'delimiter',
    'Bigg': 'delimiter',
    'bigl': 'delimiter',
    'Bigl': 'delimiter',
    'biggr': 'delimiter',
    'Biggr': 'delimiter',
    'biggl': 'delimiter',
    'Biggl': 'delimiter',
    'biggr': 'delimiter',
    'Biggr': 'delimiter',
    
    # Middle delimiter (for cases)
    'middle': 'delimiter',
}

# 2. FRACTIONS AND BINOMIALS
# ============================================================================
# \frac{a}{b} -> (a)/(b)
# \dfrac{a}{b} -> (a)/(b) (display style)
# \tfrac{a}{b} -> (a)/(b) (text style)
# \binom{n}{k} -> binomial(n, k)
# \dbinom{n}{k} -> binomial(n, k)
# \tbinom{n}{k} -> binomial(n, k)

FRACTION_COMMANDS = {
    'frac': 'fraction',
    'dfrac': 'fraction',
    'tfrac': 'fraction',
    'binom': 'binomial',
    'dbinom': 'binomial',
    'tbinom': 'binomial',
    'cfrac': 'continued_fraction',
}

# 3. ROOTS AND RADICALS
# ============================================================================
# \sqrt{a} -> sqrt(a)
# \sqrt[n]{a} -> a**(1/n)

ROOT_COMMANDS = {
    'sqrt': 'root',
}

# 4. SUPERSCRIPTS AND SUBSCRIPTS
# ============================================================================
# x^{n} -> x**n
# x^n -> x**n
# x_{n} -> x_n
# x_{i,j} -> x_{i,j}

SCRIPT_COMMANDS = {
    '^': 'superscript',
    '_': 'subscript',
}

# 5. ACCENTS AND MODIFIERS
# ============================================================================
# \hat{x} -> x_hat
# \bar{x} -> x_bar
# \vec{x} -> x_vec
# \dot{x} -> x_dot
# \ddot{x} -> x_ddot
# \tilde{x} -> x_tilde
# \widehat{x} -> x_widehat
# \overline{x} -> x_overline
# \underline{x} -> x_underline
# \overrightarrow{x} -> x_overrightarrow
# \overleftarrow{x} -> x_overleftarrow

ACCENT_COMMANDS = {
    'hat': 'accent',
    'bar': 'accent',
    'vec': 'accent',
    'dot': 'accent',
    'ddot': 'accent',
    'tilde': 'accent',
    'widehat': 'accent',
    'overline': 'accent',
    'underline': 'accent',
    'overrightarrow': 'accent',
    'overleftarrow': 'accent',
    'overleftrightarrow': 'accent',
    'acute': 'accent',
    'grave': 'accent',
    'breve': 'accent',
    'check': 'accent',
}

# 6. TEXT IN MATH MODE
# ============================================================================
# \text{text} -> text
# \mbox{text} -> text
# \mathrm{text} -> text
# \mathbf{text} -> text
# \mathit{text} -> text
# \mathsf{text} -> text
# \mathtt{text} -> text
# \mathcal{text} -> text
# \mathbb{text} -> text
# \mathfrak{text} -> text
# \mathscr{text} -> text
# \boldsymbol{text} -> text

TEXT_COMMANDS = {
    'text': 'text',
    'mbox': 'text',
    'mathrm': 'text',
    'mathbf': 'text',
    'mathit': 'text',
    'mathsf': 'text',
    'mathtt': 'text',
    'mathcal': 'text',
    'mathbb': 'text',
    'mathfrak': 'text',
    'mathscr': 'text',
    'boldsymbol': 'text',
    'textbf': 'text',
    'textit': 'text',
    'textrm': 'text',
    'texttt': 'text',
    'textsf': 'text',
}

# 7. OPERATORS
# ============================================================================
# \cdot -> *
# \times -> *
# \div -> /
# \pm -> +/-
# \mp -> -/+
# \oplus -> +
# \otimes -> *
# \odot -> *
# \circ -> o
# \bullet -> *

OPERATOR_COMMANDS = {
    'cdot': 'operator',
    'times': 'operator',
    'div': 'operator',
    'pm': 'operator',
    'mp': 'operator',
    'oplus': 'operator',
    'otimes': 'operator',
    'odot': 'operator',
    'circ': 'operator',
    'bullet': 'operator',
    'star': 'operator',
    'ast': 'operator',
    'dagger': 'operator',
    'ddagger': 'operator',
    'amalg': 'operator',
    'cap': 'operator',
    'cup': 'operator',
    'uplus': 'operator',
    'sqcap': 'operator',
    'sqcup': 'operator',
    'vee': 'operator',
    'wedge': 'operator',
    'setminus': 'operator',
    'wr': 'operator',
    'diamond': 'operator',
    'bigtriangleup': 'operator',
    'bigtriangledown': 'operator',
    'triangleleft': 'operator',
    'triangleright': 'operator',
    'lhd': 'operator',
    'rhd': 'operator',
    'unlhd': 'operator',
    'unrhd': 'operator',
    'oplus': 'operator',
    'ominus': 'operator',
    'oslash': 'operator',
    'bigcirc': 'operator',
}

# 8. RELATIONS
# ============================================================================
# \leq -> <=
# \geq -> >=
# \neq -> !=
# \approx -> ~
# \equiv -> ==
# \sim -> ~
# \simeq -> ~
# \cong -> ~
# \propto -> ~
# \ll -> <<
# \gg -> >>
# \in -> in
# \notin -> not in
# \subset -> subset
# \supset -> superset
# \subseteq -> subseteq
# \supseteq -> supseteq
# \cup -> union
# \cap -> intersection
# \emptyset -> empty
# \forall -> forall
# \exists -> exists
# \nexists -> not exists
# \neg -> not
# \wedge -> and
# \vee -> or
# \Rightarrow -> implies
# \Leftarrow -> impliedby
# \Leftrightarrow -> iff
# \rightarrow -> to
# \leftarrow -> gets
# \mapsto -> mapsto

RELATION_COMMANDS = {
    'leq': 'relation',
    'geq': 'relation',
    'neq': 'relation',
    'approx': 'relation',
    'equiv': 'relation',
    'sim': 'relation',
    'simeq': 'relation',
    'cong': 'relation',
    'propto': 'relation',
    'll': 'relation',
    'gg': 'relation',
    'in': 'relation',
    'notin': 'relation',
    'subset': 'relation',
    'supset': 'relation',
    'subseteq': 'relation',
    'supseteq': 'relation',
    'cup': 'relation',
    'cap': 'relation',
    'emptyset': 'relation',
    'forall': 'relation',
    'exists': 'relation',
    'nexists': 'relation',
    'neg': 'relation',
    'wedge': 'relation',
    'vee': 'relation',
    'Rightarrow': 'relation',
    'Leftarrow': 'relation',
    'Leftrightarrow': 'relation',
    'rightarrow': 'relation',
    'leftarrow': 'relation',
    'mapsto': 'relation',
    'to': 'relation',
    'gets': 'relation',
    'implies': 'relation',
    'impliedby': 'relation',
    'iff': 'relation',
    'land': 'relation',
    'lor': 'relation',
    'lnot': 'relation',
}

# 9. ARROWS
# ============================================================================
# \rightarrow -> to
# \leftarrow -> gets
# \leftrightarrow -> iff
# \Rightarrow -> implies
# \Leftarrow -> impliedby
# \Leftrightarrow -> iff
# \longrightarrow -> longrightarrow
# \longleftarrow -> longleftarrow
# \longleftrightarrow -> longleftrightarrow
# \Longrightarrow -> Longrightarrow
# \Longleftarrow -> Longleftarrow
# \Longleftrightarrow -> Longleftrightarrow
# \xrightarrow{text} -> xrightarrow
# \xleftarrow{text} -> xleftarrow

ARROW_COMMANDS = {
    'rightarrow': 'arrow',
    'leftarrow': 'arrow',
    'leftrightarrow': 'arrow',
    'Rightarrow': 'arrow',
    'Leftarrow': 'arrow',
    'Leftrightarrow': 'arrow',
    'longrightarrow': 'arrow',
    'longleftarrow': 'arrow',
    'longleftrightarrow': 'arrow',
    'Longrightarrow': 'arrow',
    'Longleftarrow': 'arrow',
    'Longleftrightarrow': 'arrow',
    'xrightarrow': 'arrow',
    'xleftarrow': 'arrow',
    'xrightarrow': 'arrow',
    'xleftarrow': 'arrow',
    'uparrow': 'arrow',
    'downarrow': 'arrow',
    'updownarrow': 'arrow',
    'Uparrow': 'arrow',
    'Downarrow': 'arrow',
    'Updownarrow': 'arrow',
    'nearrow': 'arrow',
    'searrow': 'arrow',
    'swarrow': 'arrow',
    'nwarrow': 'arrow',
    'mapsto': 'arrow',
    'hookleftarrow': 'arrow',
    'hookrightarrow': 'arrow',
    'rightleftharpoons': 'arrow',
    'leftrightharpoons': 'arrow',
    'overleftrightarrow': 'arrow',
    'overrightarrow': 'arrow',
    'overleftarrow': 'arrow',
    'underrightarrow': 'arrow',
    'underleftarrow': 'arrow',
}

# 10. CALCULUS OPERATORS
# ============================================================================
# \int -> Integral
# \oint -> Integral
# \iint -> Integral
# \iiint -> Integral
# \iiiint -> Integral
# \sum -> Sum
# \prod -> Prod
# \lim -> Limit
# \partial -> diff
# \nabla -> nabla
# \infty -> oo
# \bigcup -> Union
# \bigcap -> Intersection
# \bigvee -> Or
# \bigwedge -> And
# \bigoplus -> Oplus
# \bigotimes -> Otimes
# \bigodot -> Odot
# \biguplus -> Uplus

CALCULUS_COMMANDS = {
    'int': 'integral',
    'oint': 'integral',
    'iint': 'integral',
    'iiint': 'integral',
    'iiiint': 'integral',
    'idotsint': 'integral',
    'sum': 'sum',
    'prod': 'product',
    'lim': 'limit',
    'partial': 'partial',
    'nabla': 'nabla',
    'infty': 'infinity',
    'bigcup': 'union',
    'bigcap': 'intersection',
    'bigvee': 'or',
    'bigwedge': 'and',
    'bigoplus': 'oplus',
    'bigotimes': 'otimes',
    'bigodot': 'odot',
    'biguplus': 'uplus',
    'bigsqcup': 'sqcup',
    'bigsqcap': 'sqcap',
}

# 11. GREEK LETTERS
# ============================================================================
# Lowercase: \alpha \beta \gamma \delta \epsilon \zeta \eta \theta \iota \kappa
#            \lambda \mu \nu \xi \pi \rho \sigma \tau \upsilon \phi \chi \psi \omega
# Uppercase: \Gamma \Delta \Theta \Lambda \Xi \Pi \Sigma \Upsilon \Phi \Psi \Omega
# Variants: \varepsilon \vartheta \varpi \varrho \varsigma \varphi

GREEK_LOWERCASE = {
    '\\alpha': 'alpha',
    '\\beta': 'beta',
    '\\gamma': 'gamma',
    '\\delta': 'delta',
    '\\epsilon': 'epsilon',
    '\\varepsilon': 'epsilon',
    '\\zeta': 'zeta',
    '\\eta': 'eta',
    '\\theta': 'theta',
    '\\vartheta': 'theta',
    '\\iota': 'iota',
    '\\kappa': 'kappa',
    '\\lambda': 'lambda',
    '\\mu': 'mu',
    '\\nu': 'nu',
    '\\xi': 'xi',
    '\\pi': 'pi',
    '\\varpi': 'pi',
    '\\rho': 'rho',
    '\\varrho': 'rho',
    '\\sigma': 'sigma',
    '\\varsigma': 'sigma',
    '\\tau': 'tau',
    '\\upsilon': 'upsilon',
    '\\phi': 'phi',
    '\\varphi': 'phi',
    '\\chi': 'chi',
    '\\psi': 'psi',
    '\\omega': 'omega',
}

GREEK_UPPERCASE = {
    '\\Gamma': 'Gamma',
    '\\Delta': 'Delta',
    '\\Theta': 'Theta',
    '\\Lambda': 'Lambda',
    '\\Xi': 'Xi',
    '\\Pi': 'Pi',
    '\\Sigma': 'Sigma',
    '\\Upsilon': 'Upsilon',
    '\\Phi': 'Phi',
    '\\Psi': 'Psi',
    '\\Omega': 'Omega',
}

# 12. FUNCTIONS
# ============================================================================
# Trig: \sin \cos \tan \cot \sec \csc
# Inverse: \arcsin \arccos \arctan \arccot \arcsec \arccsc
# Hyperbolic: \sinh \cosh \tanh \coth \sech \csch
# Inverse hyp: \arcsinh \arccosh \arctanh \arccoth \arcsech \arccsch
# Log: \log \ln \exp
# Other: \det \dim \rank \trace \diag \ker \hom \deg \gcd \lcm \min \max \sup \inf \arg \mod

FUNCTION_COMMANDS = {
    'sin': 'sin',
    'cos': 'cos',
    'tan': 'tan',
    'cot': 'cot',
    'sec': 'sec',
    'csc': 'csc',
    'arcsin': 'asin',
    'arccos': 'acos',
    'arctan': 'atan',
    'arccot': 'acot',
    'arcsec': 'asec',
    'arccsc': 'acsc',
    'sinh': 'sinh',
    'cosh': 'cosh',
    'tanh': 'tanh',
    'coth': 'coth',
    'sech': 'sech',
    'csch': 'csch',
    'arcsinh': 'asinh',
    'arccosh': 'acosh',
    'arctanh': 'atanh',
    'arccoth': 'acoth',
    'arcsech': 'asech',
    'arccsch': 'acsch',
    'log': 'log',
    'ln': 'log',
    'exp': 'exp',
    'det': 'det',
    'dim': 'dim',
    'rank': 'rank',
    'trace': 'trace',
    'diag': 'diag',
    'ker': 'ker',
    'hom': 'hom',
    'deg': 'deg',
    'gcd': 'gcd',
    'lcm': 'lcm',
    'min': 'Min',
    'max': 'Max',
    'sup': 'sup',
    'inf': 'inf',
    'arg': 'arg',
    'mod': 'mod',
    'Pr': 'Pr',
    'E': 'E',
    'Var': 'Var',
    'Cov': 'Cov',
    'Corr': 'Corr',
}

# 13. DELIMITERS
# ============================================================================
# Parentheses: ( ) \left( \right)
# Brackets: [ ] \left[ \right]
# Braces: \{ \} \left\{ \right\}
# Angle: \langle \rangle \left\langle \right\rangle
# Vertical: | \lvert \rvert \left| \right|
# Double vertical: \| \lVert \rVert \left\| \right\|
# Floor: \lfloor \rceil \left\lfloor \right\rceil
# Ceiling: \lceil \rceil \left\lceil \right\rceil

DELIMITER_MAP = {
    '\\left(': '(',
    '\\right)': ')',
    '\\left[': '[',
    '\\right]': ']',
    '\\left\\{': '{',
    '\\right\\}': '}',
    '\\left|': '|',
    '\\right|': '|',
    '\\left\\|': '||',
    '\\right\\|': '||',
    '\\left\\langle': 'langle',
    '\\right\\rangle': 'rangle',
    '\\left\\lfloor': 'lfloor',
    '\\right\\rfloor': 'rfloor',
    '\\left\\lceil': 'lceil',
    '\\right\\rceil': 'rceil',
    '\\left\\lvert': '|',
    '\\right\\rvert': '|',
    '\\left\\lVert': '||',
    '\\right\\rVert': '||',
    '\\langle': 'langle',
    '\\rangle': 'rangle',
    '\\lfloor': 'lfloor',
    '\\rfloor': 'rfloor',
    '\\lceil': 'lceil',
    '\\rceil': 'rceil',
    '\\lvert': '|',
    '\\rvert': '|',
    '\\lVert': '||',
    '\\rVert': '||',
    '\\{': '{',
    '\\}': '}',
    '\\|': '||',
}

# 14. SPACING
# ============================================================================
# \, \: \; \! \ \quad \qquad
# \hspace{length} \vspace{length}
# \hfill \vfill \hfill

SPACING_COMMANDS = {
    '\\,': ' ',
    '\\:': ' ',
    '\\;': ' ',
    '\\!': '',
    '\\ ': ' ',
    '\\quad': '  ',
    '\\qquad': '    ',
    '\\hfill': '',
    '\\vfill': '',
    '\\hspace': ' ',
    '\\vspace': ' ',
}

# 15. ENVIRONMENTS
# ============================================================================
# Equation: \begin{equation} ... \end{equation}
# Align: \begin{align} ... \end{align}
# Gather: \begin{gathered} ... \end{gathered}
# Cases: \begin{cases} ... \end{cases}
# Matrix: \begin{matrix} ... \end{matrix}
# Pmatrix: \begin{pmatrix} ... \end{pmatrix}
# Bmatrix: \begin{bmatrix} ... \end{bmatrix}
# Vmatrix: \begin{vmatrix} ... \end{vmatrix}
# Array: \begin{array}{...} ... \end{array}

ENVIRONMENT_COMMANDS = {
    'equation': 'display_math',
    'equation*': 'display_math',
    'align': 'display_math',
    'align*': 'display_math',
    'gather': 'display_math',
    'gather*': 'display_math',
    'multline': 'display_math',
    'multline*': 'display_math',
    'split': 'display_math',
    'cases': 'cases',
    'matrix': 'matrix',
    'pmatrix': 'pmatrix',
    'bmatrix': 'bmatrix',
    'Bmatrix': 'Bmatrix',
    'vmatrix': 'vmatrix',
    'Vmatrix': 'Vmatrix',
    'array': 'array',
    'smallmatrix': 'smallmatrix',
    'subarray': 'subarray',
}

# 16. COMPREHENSIVE PRE-PROCESSOR
# ============================================================================

def preprocess_latex(latex):
    """
    Comprehensive LaTeX pre-processor.
    Defines ALL commands for proper parsing.
    """
    s = latex.strip()
    
    # Step 1: Handle environments
    # Remove \begin{env} and \end{env}
    s = re.sub(r'\\begin\{([^}]+)\}', '', s)
    s = re.sub(r'\\end\{([^}]+)\}', '', s)
    
    # Step 2: Handle \left and \right
    s = re.sub(r'\\left\s*\(', '(', s)
    s = re.sub(r'\\right\s*\)', ')', s)
    s = re.sub(r'\\left\s*\[', '[', s)
    s = re.sub(r'\\right\s*\]', ']', s)
    s = re.sub(r'\\left\s*\\\{', '{', s)
    s = re.sub(r'\\right\s*\\\}', '}', s)
    s = re.sub(r'\\left\s*\|', '|', s)
    s = re.sub(r'\\right\s*\|', '|', s)
    s = re.sub(r'\\left\s*\\|', '||', s)
    s = re.sub(r'\\right\s*\\|', '||', s)
    s = re.sub(r'\\left\s*\\langle', 'langle', s)
    s = re.sub(r'\\right\s*\\rangle', 'rangle', s)
    s = re.sub(r'\\left\s*\\lfloor', 'lfloor', s)
    s = re.sub(r'\\right\s*\\rfloor', 'rfloor', s)
    s = re.sub(r'\\left\s*\\lceil', 'lceil', s)
    s = re.sub(r'\\right\s*\\rceil', 'rceil', s)
    s = re.sub(r'\\left\s*\\lvert', '|', s)
    s = re.sub(r'\\right\s*\\rvert', '|', s)
    s = re.sub(r'\\left\s*\\lVert', '||', s)
    s = re.sub(r'\\right\s*\\rVert', '||', s)
    
    # Step 3: Handle \big, \Big, \bigg, \Bigg
    s = re.sub(r'\\bigg\s*', '', s)
    s = re.sub(r'\\Bigg\s*', '', s)
    s = re.sub(r'\\big\s*', '', s)
    s = re.sub(r'\\Big\s*', '', s)
    s = re.sub(r'\\bigl\s*', '', s)
    s = re.sub(r'\\Bigl\s*', '', s)
    s = re.sub(r'\\biggr\s*', '', s)
    s = re.sub(r'\\Biggr\s*', '', s)
    
    # Step 4: Handle text commands
    for cmd in TEXT_COMMANDS:
        pattern = rf'\\{cmd}\s*\{{([^{{}}]+)\}}'
        s = re.sub(pattern, r'\1', s)
    
    # Step 5: Handle operator commands
    s = re.sub(r'\\operatorname\s*\{\s*([a-zA-Z]+)\s*\}', r'\1', s)
    
    # Step 6: Handle accents
    for cmd, replacement in ACCENT_COMMANDS.items():
        pattern = rf'\\{cmd}\s*\{{([a-zA-Z]+)\}}'
        s = re.sub(pattern, rf'\1_{replacement}', s)
    
    # Step 7: Handle fractions
    s = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\dfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\tfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\cfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', s)
    
    # Step 8: Handle sqrt
    s = re.sub(r'\\sqrt\s*\[([^\]]+)\]\s*\{([^{}]+)\}', r'(\2)**(1/(\1))', s)
    s = re.sub(r'\\sqrt\s*\{([^{}]+)\}', r'sqrt(\1)', s)
    
    # Step 9: Handle superscripts and subscripts
    s = re.sub(r'\^\s*\{([^{}]+)\}', r'**(\1)', s)
    s = re.sub(r'\^\s*([a-zA-Z0-9])', r'**\1', s)
    s = re.sub(r'_\s*\{([^{}]+)\}', r'_\1', s)
    
    # Step 10: Handle operators
    s = s.replace('\\cdot', '*')
    s = s.replace('\\times', '*')
    s = s.replace('\\div', '/')
    s = s.replace('\\pm', '+/-')
    s = s.replace('\\mp', '-/+')
    s = s.replace('\\oplus', '+')
    s = s.replace('\\otimes', '*')
    s = s.replace('\\odot', '*')
    s = s.replace('\\circ', 'o')
    s = s.replace('\\bullet', '*')
    s = s.replace('\\star', '*')
    s = s.replace('\\ast', '*')
    s = s.replace('\\dagger', '+')
    s = s.replace('\\ddagger', '++')
    s = s.replace('\\amalg', '+')
    s = s.replace('\\cap', '&')
    s = s.replace('\\cup', '|')
    s = s.replace('\\uplus', '+')
    s = s.replace('\\sqcap', '&')
    s = s.replace('\\sqcup', '|')
    s = s.replace('\\vee', '|')
    s = s.replace('\\wedge', '&')
    s = s.replace('\\setminus', '\\')
    s = s.replace('\\wr', 'wreath')
    s = s.replace('\\diamond', '<>')
    s = s.replace('\\bigtriangleup', '^')
    s = s.replace('\\bigtriangledown', 'v')
    s = s.replace('\\triangleleft', '<')
    s = s.replace('\\triangleright', '>')
    s = s.replace('\\lhd', '<')
    s = s.replace('\\rhd', '>')
    s = s.replace('\\unlhd', '<=')
    s = s.replace('\\unrhd', '>=')
    
    # Step 11: Handle relations
    s = s.replace('\\leq', '<=')
    s = s.replace('\\geq', '>=')
    s = s.replace('\\neq', '!=')
    s = s.replace('\\approx', '~')
    s = s.replace('\\equiv', '==')
    s = s.replace('\\sim', '~')
    s = s.replace('\\simeq', '~')
    s = s.replace('\\cong', '~')
    s = s.replace('\\propto', '~')
    s = s.replace('\\ll', '<<')
    s = s.replace('\\gg', '>>')
    s = s.replace('\\in', 'in')
    s = s.replace('\\notin', 'notin')
    s = s.replace('\\subset', 'subset')
    s = s.replace('\\supset', 'supset')
    s = s.replace('\\subseteq', 'subseteq')
    s = s.replace('\\supseteq', 'supseteq')
    s = s.replace('\\cup', 'union')
    s = s.replace('\\cap', 'intersection')
    s = s.replace('\\emptyset', 'empty')
    s = s.replace('\\forall', 'forall')
    s = s.replace('\\exists', 'exists')
    s = s.replace('\\nexists', 'notexists')
    s = s.replace('\\neg', 'not')
    s = s.replace('\\wedge', 'and')
    s = s.replace('\\vee', 'or')
    s = s.replace('\\Rightarrow', 'implies')
    s = s.replace('\\Leftarrow', 'impliedby')
    s = s.replace('\\Leftrightarrow', 'iff')
    s = s.replace('\\rightarrow', 'to')
    s = s.replace('\\leftarrow', 'gets')
    s = s.replace('\\mapsto', 'mapsto')
    s = s.replace('\\to', 'to')
    s = s.replace('\\gets', 'gets')
    s = s.replace('\\implies', 'implies')
    s = s.replace('\\impliedby', 'impliedby')
    s = s.replace('\\iff', 'iff')
    s = s.replace('\\land', 'and')
    s = s.replace('\\lor', 'or')
    s = s.replace('\\lnot', 'not')
    
    # Step 12: Handle arrows
    s = s.replace('\\longrightarrow', 'to')
    s = s.replace('\\longleftarrow', 'gets')
    s = s.replace('\\longleftrightarrow', 'iff')
    s = s.replace('\\Longrightarrow', 'implies')
    s = s.replace('\\Longleftarrow', 'impliedby')
    s = s.replace('\\Longleftrightarrow', 'iff')
    s = s.replace('\\xrightarrow', 'to')
    s = s.replace('\\xleftarrow', 'gets')
    s = s.replace('\\uparrow', 'up')
    s = s.replace('\\downarrow', 'down')
    s = s.replace('\\updownarrow', 'updown')
    s = s.replace('\\Uparrow', 'UP')
    s = s.replace('\\Downarrow', 'DOWN')
    s = s.replace('\\Updownarrow', 'UPDOWN')
    s = s.replace('\\nearrow', 'ne')
    s = s.replace('\\searrow', 'se')
    s = s.replace('\\swarrow', 'sw')
    s = s.replace('\\nwarrow', 'nw')
    s = s.replace('\\hookleftarrow', 'hookgets')
    s = s.replace('\\hookrightarrow', 'hookto')
    s = s.replace('\\rightleftharpoons', 'leftright')
    s = s.replace('\\leftrightharpoons', 'leftright')
    s = s.replace('\\overleftrightarrow', 'over')
    s = s.replace('\\overrightarrow', 'overto')
    s = s.replace('\\overleftarrow', 'overgets')
    s = s.replace('\\underrightarrow', 'under')
    s = s.replace('\\underleftarrow', 'under')
    
    # Step 13: Handle calculus operators
    s = s.replace('\\int', 'Integral')
    s = s.replace('\\oint', 'Integral')
    s = s.replace('\\iint', 'Integral')
    s = s.replace('\\iiint', 'Integral')
    s = s.replace('\\iiiint', 'Integral')
    s = s.replace('\\idotsint', 'Integral')
    s = s.replace('\\sum', 'Sum')
    s = s.replace('\\prod', 'Prod')
    s = s.replace('\\lim', 'Limit')
    s = s.replace('\\partial', 'diff')
    s = s.replace('\\nabla', 'nabla')
    s = s.replace('\\infty', 'oo')
    s = s.replace('\\bigcup', 'Union')
    s = s.replace('\\bigcap', 'Intersection')
    s = s.replace('\\bigvee', 'Or')
    s = s.replace('\\bigwedge', 'And')
    s = s.replace('\\bigoplus', 'Oplus')
    s = s.replace('\\bigotimes', 'Otimes')
    s = s.replace('\\bigodot', 'Odot')
    s = s.replace('\\biguplus', 'Uplus')
    s = s.replace('\\bigsqcup', 'sqcup')
    s = s.replace('\\bigsqcap', 'sqcap')
    
    # Step 14: Handle Greek letters
    for latex_cmd, sympy_name in GREEK_LOWERCASE.items():
        s = s.replace(latex_cmd, sympy_name)
    for latex_cmd, sympy_name in GREEK_UPPERCASE.items():
        s = s.replace(latex_cmd, sympy_name)
    
    # Step 15: Handle functions
    for latex_cmd, sympy_name in FUNCTION_COMMANDS.items():
        s = s.replace('\\' + latex_cmd, sympy_name)
    
    # Step 16: Handle delimiters
    for latex_cmd, replacement in DELIMITER_MAP.items():
        s = s.replace(latex_cmd, replacement)
    
    # Step 17: Handle spacing
    for latex_cmd, replacement in SPACING_COMMANDS.items():
        s = s.replace(latex_cmd, replacement)
    
    # Step 18: Handle remaining LaTeX commands
    # Remove any remaining \command{...} patterns
    s = re.sub(r'\\[a-zA-Z]+\s*\{([^{}]+)\}', r'\1', s)
    # Remove any remaining \command patterns
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    
    # Step 19: Clean up braces
    s = s.replace('{', '').replace('}', '')
    
    # Step 20: Handle multiple = signs
    if s.count('=') > 1:
        parts = s.split('=')
        if len(parts) >= 2:
            s = parts[0] + '=' + parts[1]
    
    return s.strip()

def solve_with_comprehensive_definitions(latex):
    """
    Solve equation using comprehensive LaTeX command definitions.
    """
    try:
        # Pre-process LaTeX
        normalized = preprocess_latex(latex)
        
        if not normalized or len(normalized) < 3:
            return {'success': False, 'error': 'empty_after_preprocessing', 'strategy': 'comprehensive'}
        
        if '=' not in normalized:
            return {'success': False, 'error': 'no_equality', 'strategy': 'comprehensive'}
        
        # Split on =
        parts = normalized.split('=')
        if len(parts) != 2:
            return {'success': False, 'error': 'multiple_equalities', 'strategy': 'comprehensive'}
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        if not lhs or not rhs:
            return {'success': False, 'error': 'empty_side', 'strategy': 'comprehensive'}
        
        # Parse both sides
        lhs_expr = parse_expr(lhs, transformations=transformations)
        rhs_expr = parse_expr(rhs, transformations=transformations)
        
        # Get variables
        variables = list(lhs_expr.free_symbols | rhs_expr.free_symbols)
        
        if not variables:
            return {'success': False, 'error': 'no_variables', 'strategy': 'comprehensive'}
        
        # Solve for first variable
        var = variables[0]
        solution = sympy.solve(lhs_expr - rhs_expr, var)
        
        return {
            'success': True,
            'solution': str(solution),
            'variables': [str(v) for v in variables],
            'strategy': 'comprehensive',
            'normalized': normalized,
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'strategy': 'comprehensive'}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive LaTeX solver')
    parser.add_argument('--input', default='DATASETS/extractor_training_data_fresh.jsonl')
    parser.add_argument('--output', default='DATASETS/equation_solve_results_comprehensive.jsonl')
    parser.add_argument('--stats', default='DATASETS/equation_solve_stats_comprehensive.json')
    
    args = parser.parse_args()
    
    # Load records
    with open(args.input) as f:
        records = [json.loads(line) for line in f]
    
    print(f"Loaded {len(records)} records")
    
    # Filter to complete equations
    complete = [r for r in records if is_complete_equation(r['latex'])]
    print(f"Complete equations: {len(complete)}")
    
    # Solve each
    results = []
    stats = {
        'total': len(complete),
        'solvable': 0,
        'not_solvable': 0,
        'by_strategy': {},
        'errors': {},
    }
    
    for i, record in enumerate(complete):
        if (i + 1) % 50 == 0:
            print(f"  Solving {i+1}/{len(complete)}...")
        
        result = solve_with_comprehensive_definitions(record['latex'])
        result['arxiv_id'] = record.get('arxiv_id', 'unknown')
        result['category'] = record.get('category', 'unknown')
        result['context_before'] = record.get('context_before', '')
        result['context_after'] = record.get('context_after', '')
        
        results.append(result)
        
        if result['success']:
            stats['solvable'] += 1
            strategy = result['strategy']
            stats['by_strategy'][strategy] = stats['by_strategy'].get(strategy, 0) + 1
        else:
            stats['not_solvable'] += 1
            error = result.get('error', 'unknown')
            stats['errors'][error] = stats['errors'].get(error, 0) + 1
    
    # Write results
    with open(args.output, 'w') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    # Write stats
    with open(args.stats, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print honest summary
    print(f"\n{'='*60}")
    print("HONEST RESULTS - Comprehensive LaTeX Definitions")
    print(f"{'='*60}")
    print(f"Total complete equations: {stats['total']}")
    print(f"Solvable: {stats['solvable']} ({100*stats['solvable']/stats['total']:.1f}%)")
    print(f"Not solvable: {stats['not_solvable']} ({100*stats['not_solvable']/stats['total']:.1f}%)")
    print(f"\nBy strategy:")
    for strategy, count in stats['by_strategy'].items():
        print(f"  {strategy}: {count}")
    print(f"\nError breakdown:")
    for error, count in sorted(stats['errors'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {error[:60]}: {count}")
    
    print(f"\nSample solutions:")
    for result in results[:10]:
        if result['success']:
            latex = result.get('normalized', 'N/A')
            print(f"  [{result['strategy']}] {latex[:50]}")
            print(f"    -> {result['solution'][:50]}")

if __name__ == '__main__':
    main()