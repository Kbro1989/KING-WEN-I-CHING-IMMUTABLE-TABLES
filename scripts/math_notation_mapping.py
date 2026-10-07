"""
Unicode Math Symbol to SymPy / Wolfram Language Mapping
=====================================================

Maps Unicode mathematical operators and letter-like forms to:
1. SymPy-compatible Python expressions (for solving)
2. Wolfram Language StandardForm equivalents (for reference)

Source: Wolfram Language & System Documentation Center
  TECH NOTE: Mathematical and Other Notation
  https://reference.wolfram.com/language/tutorial/MathematicalAndOtherNotation.html
"""

# Unicode -> SymPy operator mapping
UNICODE_TO_SYMPY = {
    '·': '*',      # \cdot
    '×': '*',      # \times
    '÷': '/',      # \div
    '±': '+/-',    # \pm (PlusMinus)
    '∓': '-/+',    # \mp (MinusPlus)
    '≤': '<=',     # \leq
    '≥': '>=',     # \geq
    '≠': '!=',     # \neq
    '≈': '~=',     # \approx
    '≡': '==',     # \equiv (congruent)
    '∝': 'propto', # \propto
    '∞': 'oo',     # \infty
    '√': 'sqrt',   # \sqrt
    '∑': 'Sum',    # \sum
    '∏': 'Product',# \prod
    '∫': 'Integral', # \int
    '∂': 'diff',   # \partial
    '∇': 'del',    # \nabla (Del)
    '∧': '&',      # \wedge (And)
    '∨': '|',      # \vee (Or)
    '¬': '~',      # \neg (Not)
    '∀': 'ForAll', # \forall
    '∃': 'Exists', # \exists
    '∈': 'in',     # \in (Element)
    '∉': 'notin',  # \notin (NotElement)
    '⊆': 'subset', # \subseteq
    '⊂': 'subset', # \subset
    '∪': 'Union',  # \cup
    '∩': 'Intersection', # \cap
    '→': '->',     # \rightarrow (Rule)
    '⟹': '>>',     # \implies (ImpliedRightArrow)
    '⟸': '<<',     # \leftarrow
    '⟷': '<->',    # \leftrightarrow
    '∴': 'therefore', # \therefore
    '∵': 'because',   # \because
    '∶': 'proportion', # \proportion
    '∷': 'EqualProportion', # \EqualProportion
    '≅': 'congruent', # \cong
    '∼': 'sim',    # \sim (TildeTilde)
    '°': 'deg',    # \degree
    'ℏ': 'hbar',   # \hbar
    'ℵ': 'aleph',  # \aleph
    'π': 'pi',     # \pi
    'α': 'alpha',  # \alpha
    'β': 'beta',   # \beta
    'γ': 'gamma',  # \gamma
    'δ': 'delta',  # \delta
    'ε': 'epsilon', # \epsilon
    'ζ': 'zeta',   # \zeta
    'η': 'eta',    # \eta
    'θ': 'theta',  # \theta
    'ι': 'iota',   # \iota
    'κ': 'kappa',  # \kappa
    'λ': 'lambda', # \lambda
    'μ': 'mu',     # \mu
    'ν': 'nu',     # \nu
    'ξ': 'xi',     # \xi
    'ο': 'omicron', # \omicron
    'ρ': 'rho',    # \rho
    'σ': 'sigma',  # \sigma
    'τ': 'tau',    # \tau
    'υ': 'upsilon', # \upsilon
    'φ': 'phi',    # \phi
    'χ': 'chi',    # \chi
    'ψ': 'psi',    # \psi
    'ω': 'omega',  # \omega
    'Γ': 'Gamma',  # \Gamma
    'Δ': 'Delta',  # \Delta
    'Θ': 'Theta',  # \Theta
    'Λ': 'Lambda', # \Lambda
    'Ξ': 'Xi',     # \Xi
    'Π': 'Pi',     # \Pi
    'Σ': 'Sigma',  # \Sigma
    'Υ': 'Upsilon', # \Upsilon
    'Φ': 'Phi',    # \Phi
    'Ψ': 'Psi',    # \Psi
    'Ω': 'Omega',  # \Omega
}

# Unicode -> Wolfram Language StandardForm mapping
UNICODE_TO_WOLFRAM = {
    'π': 'Pi',
    '∞': 'Infinity',
    'ℯ': 'E',
    'ⅈ': 'I',
    'ⅉ': 'I',
    '°': 'Degree',
    '∂': 'DifferentialD',
    '∇': 'Del',
    '∑': 'Sum',
    '∏': 'Product',
    '∫': 'Integral',
    '√': 'Sqrt',
    '×': 'Times',
    '⨯': 'Cross',
    '÷': 'Divide',
    '±': 'PlusMinus',
    '∓': 'MinusPlus',
    '⊕': 'CirclePlus',
    '⊗': 'CircleTimes',
    '∩': 'Intersection',
    '∪': 'Union',
    '≥': 'GreaterEqual',
    '≤': 'LessEqual',
    '≠': 'Unequal',
    '≈': 'ApproximateEqual',
    '≡': 'Congruent',
    '∼': 'TildeTilde',
    '∝': 'Proportional',
    '∈': 'Element',
    '∉': 'NotElement',
    '⊆': 'Subset',
    '⊂': 'SubsetEqual',
    '∧': 'And',
    '∨': 'Or',
    '¬': 'Not',
    '∀': 'ForAll',
    '∃': 'Exists',
    '→': 'Rule',
    '⟹': 'ImpliedRightArrow',
    '⟸': 'LeftArrow',
    '⟷': 'DoubleArrow',
    '∴': 'Therefore',
    '∵': 'Because',
    '∶': 'Proportion',
    '∷': 'EqualProportion',
    '≅': 'Congruent',
    'ℏ': 'HBar',
    'ℵ': 'Aleph',
    'α': 'Alpha',
    'β': 'Beta',
    'γ': 'Gamma',
    'δ': 'Delta',
    'ε': 'Epsilon',
    'ζ': 'Zeta',
    'η': 'Eta',
    'θ': 'Theta',
    'ι': 'Iota',
    'κ': 'Kappa',
    'λ': 'Lambda',
    'μ': 'Mu',
    'ν': 'Nu',
    'ξ': 'Xi',
    'ο': 'Omicron',
    'ρ': 'Rho',
    'σ': 'Sigma',
    'τ': 'Tau',
    'υ': 'Upsilon',
    'φ': 'Phi',
    'χ': 'Chi',
    'ψ': 'Psi',
    'ω': 'Omega',
    'Γ': 'CapitalGamma',
    'Δ': 'CapitalDelta',
    'Θ': 'CapitalTheta',
    'Λ': 'CapitalLambda',
    'Ξ': 'CapitalXi',
    'Π': 'CapitalPi',
    'Σ': 'CapitalSigma',
    'Υ': 'CapitalUpsilon',
    'Φ': 'CapitalPhi',
    'Ψ': 'CapitalPsi',
    'Ω': 'CapitalOmega',
}

# Wolfram Language escape aliases (for keyboard entry)
WOLFRAM_ESCAPE_ALIASES = {
    'Esc p Esc': '\\[Pi]',
    'Esc inf Esc': '\\[Infinity]',
    'Esc ee Esc': '\\[ExponentialE]',
    'Esc ii Esc': '\\[ImaginaryI]',
    'Esc jj Esc': '\\[ImaginaryJ]',
    'Esc deg Esc': '\\[Degree]',
    'Esc dd Esc': '\\[DifferentialD]',
    'Esc alpha Esc': '\\[Alpha]',
    'Esc beta Esc': '\\[Beta]',
    'Esc gamma Esc': '\\[Gamma]',
    'Esc delta Esc': '\\[Delta]',
    'Esc epsilon Esc': '\\[Epsilon]',
    'Esc zeta Esc': '\\[Zeta]',
    'Esc eta Esc': '\\[Eta]',
    'Esc theta Esc': '\\[Theta]',
    'Esc iota Esc': '\\[Iota]',
    'Esc kappa Esc': '\\[Kappa]',
    'Esc lambda Esc': '\\[Lambda]',
    'Esc mu Esc': '\\[Mu]',
    'Esc nu Esc': '\\[Nu]',
    'Esc xi Esc': '\\[Xi]',
    'Esc pi Esc': '\\[Pi]',
    'Esc rho Esc': '\\[Rho]',
    'Esc sigma Esc': '\\[Sigma]',
    'Esc tau Esc': '\\[Tau]',
    'Esc upsilon Esc': '\\[Upsilon]',
    'Esc phi Esc': '\\[Phi]',
    'Esc chi Esc': '\\[Chi]',
    'Esc psi Esc': '\\[Psi]',
    'Esc omega Esc': '\\[Omega]',
    'Esc sum Esc': '\\[Sum]',
    'Esc prod Esc': '\\[Product]',
    'Esc int Esc': '\\[Integral]',
    'Esc sqrt Esc': '\\[Sqrt]',
    'Esc infty Esc': '\\[Infinity]',
    'Esc elem Esc': '\\[Element]',
    'Esc subset Esc': '\\[Subset]',
    'Esc subseteq Esc': '\\[SubsetEqual]',
    'Esc cup Esc': '\\[Union]',
    'Esc cap Esc': '\\[Intersection]',
    'Esc wedge Esc': '\\[Wedge]',
    'Esc vee Esc': '\\[Vee]',
    'Esc forall Esc': '\\[ForAll]',
    'Esc exists Esc': '\\[Exists]',
    'Esc partial Esc': '\\[PartialD]',
    'Esc del Esc': '\\[Del]',
    'Esc grad Esc': '\\[Grad]',
    'Esc times Esc': '\\[Times]',
    'Esc cross Esc': '\\[Cross]',
    'Esc cdot Esc': '\\[CenterDot]',
    'Esc div Esc': '\\[Divide]',
    'Esc pm Esc': '\\[PlusMinus]',
    'Esc mp Esc': '\\[MinusPlus]',
    'Esc le Esc': '\\[LessEqual]',
    'Esc ge Esc': '\\[GreaterEqual]',
    'Esc ne Esc': '\\[Unequal]',
    'Esc approx Esc': '\\[ApproximateEqual]',
    'Esc equiv Esc': '\\[Congruent]',
    'Esc sim Esc': '\\[TildeTilde]',
    'Esc propto Esc': '\\[Proportional]',
    'Esc rightarrow Esc': '\\[RightArrow]',
    'Esc leftarrow Esc': '\\[LeftArrow]',
    'Esc leftrightarrow Esc': '\\[LeftRightArrow]',
    'Esc rule Esc': '\\[Rule]',
    'Esc implies Esc': '\\[Implies]',
    'Esc therefore Esc': '\\[Therefore]',
    'Esc because Esc': '\\[Because]',
    'Esc aleph Esc': '\\[Aleph]',
    'Esc hbar Esc': '\\[HBar]',
    'Esc degree Esc': '\\[Degree]',
}

# Wolfram Language keyboard shortcuts
WOLFRAM_KEYBOARD_SHORTCUTS = {
    'Ctrl+^ or Ctrl+6': 'superscript (power)',
    'Ctrl + /': 'denominator (fraction)',
    'Ctrl+@ or Ctrl+2': 'square root',
    'Ctrl + Space': 'return from superscript/denominator/sqrt',
    'Ctrl+_ n Ctrl+Space': 'Subscript[x,n]',
    'Ctrl+^ + Ctrl+Space': 'SuperPlus[x]',
    'Ctrl+^ - Ctrl+Space': 'SuperMinus[x]',
    'Ctrl+^ * Ctrl+Space': 'SuperStar[x]',
    'Ctrl+^ EscdgEsc Ctrl+Space': 'SuperDagger[x]',
    'Ctrl+& _ Ctrl+Space': 'OverBar[x]',
    'Ctrl+& EscvecEsc Ctrl+Space': 'OverVector[x]',
    'Ctrl+& ~ Ctrl+Space': 'OverTilde[x]',
    'Ctrl+& ^ Ctrl+Space': 'OverHat[x]',
    'Ctrl+& . Ctrl+Space': 'OverDot[x]',
    'Ctrl+$ _ Ctrl+Space': 'UnderBar[x]',
}


def normalize_for_sympy(expr_text):
    """
    Normalize a Unicode math expression for SymPy parsing.
    
    Replaces Unicode operators with ASCII equivalents,
    removes LaTeX commands, and strips prose remnants.
    
    Returns (normalized_text, was_modified)
    """
    s = expr_text.strip()
    modified = False
    
    # Replace Unicode operators
    for unicode_op, sympy_op in UNICODE_TO_SYMPY.items():
        if unicode_op in s:
            s = s.replace(unicode_op, sympy_op)
            modified = True
    
    # Remove LaTeX commands
    latex_cmds = ['\\cdot', '\\times', '\\frac', '\\sqrt', '\\mathbf', '\\det',
                  '\\begin', '\\end', '\\item', '\\sum', '\\prod', '\\int',
                  '\\(', '\\)', '$']
    for cmd in latex_cmds:
        if cmd in s:
            s = s.replace(cmd, '')
            modified = True
    
    # Strip trailing punctuation
    s = s.strip().rstrip(',.')
    
    return s, modified


def to_wolfram_notation(expr_text):
    """
    Convert a Unicode math expression to Wolfram Language StandardForm.
    
    Returns the Wolfram Language equivalent string.
    """
    s = expr_text.strip()
    
    # Replace Unicode symbols with Wolfram names
    for unicode_char, wolfram_name in UNICODE_TO_WOLFRAM.items():
        if unicode_char in s:
            s = s.replace(unicode_char, f' {wolfram_name} ')
    
    # Clean up extra spaces
    s = ' '.join(s.split())
    
    return s


def get_wolfram_alias(unicode_char):
    """
    Get the Wolfram Language escape alias for a Unicode character.
    
    Returns the alias string or None if not found.
    """
    wolfram_name = UNICODE_TO_WOLFRAM.get(unicode_char)
    if wolfram_name:
        # Convert \[Name] to Esc name Esc
        alias = wolfram_name.replace('\\[', '').replace(']', '')
        return f'Esc {alias} Esc'
    return None


if __name__ == '__main__':
    # Test the mapping
    test_exprs = [
        'αi = ϵ σ²',
        'x ≤ y',
        'a ∈ A',
        'f: X → Y',
        '∑_{i=1}^n x_i',
        '∫_0^1 f(x) dx',
        '∂f/∂x',
        '∇·F',
        'x ≠ y',
        'A ⊆ B',
    ]
    
    print("=== Unicode to SymPy Normalization ===")
    for expr in test_exprs:
        normalized, modified = normalize_for_sympy(expr)
        print(f"  {expr:30s} → {normalized}")
    
    print("\n=== Unicode to Wolfram Language ===")
    for expr in test_exprs:
        wolfram = to_wolfram_notation(expr)
        print(f"  {expr:30s} → {wolfram}")
    
    print("\n=== Wolfram Escape Aliases ===")
    for char in ['π', '∞', 'α', '∑', '∫', '∂', '∇', '∈', '→']:
        alias = get_wolfram_alias(char)
        print(f"  {char} → {alias}")