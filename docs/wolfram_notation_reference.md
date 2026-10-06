Wolfram Language & System Documentation Center
================================================

TECH NOTE: Mathematical and Other Notation

KEY NOTATION PATTERNS FROM WOLFRAM DOC
========================================

1. ESCAPE ALIASES (entered via Esc key sequences)
   Esc p Esc      -> \[Pi] (π)
   Esc inf Esc    -> \[Infinity] (∞)
   Esc ee Esc     -> \[ExponentialE] (e)
   Esc ii Esc     -> \[ImaginaryI] (i)
   Esc deg Esc    -> \[Degree]

2. KEYBOARD SHORTCUTS
   Ctrl+^ or Ctrl+6   -> superscript (power)
   Ctrl + /           -> denominator (fraction)
   Ctrl+@ or Ctrl+2   -> square root
   Ctrl + Space       -> return from superscript/denominator/sqrt

3. SPECIAL CHARACTER NAMES
   \[Infinity]        -> Infinity
   \[Pi]              -> Pi
   \[ExponentialE]    -> E
   \[ImaginaryI]      -> I
   \[DifferentialD]   -> differential operator (EscddEsc)

4. OPERATOR CHARACTERS
   ×  -> Times (multiplication)
   ⨯  -> Cross (vector cross product)
   ⊕  -> CirclePlus
   ∩  -> Intersection
   ∪  -> Union
   ≥  -> GreaterEqual
   ≤  -> LessEqual
   ≠  -> Unequal
   ∈  -> Element
   ∉  -> NotElement
   ∂  -> PartialD
   ∇  -> Del
   ∑  -> Sum
   ∏  -> Product
   ∫  -> Integral

5. LETTER-LIKE FORMS
   Greek letters: α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, ο, π, ρ, σ, τ, υ, φ, χ, ψ, ω
   Capital Greek: Α, Β, Γ, Δ, Ε, Ζ, Η, Θ, Ι, Κ, Λ, Μ, Ν, Ξ, Ο, Π, Ρ, Σ, Τ, Υ, Φ, Χ, Ψ, Ω
   Script: ℒ, ℳ, ℛ, ℬ, 𝒞, 𝒢, 𝒥, 𝒦, 𝒩, 𝒪, 𝒫, 𝒬, ℛ, 𝒮, 𝒯, 𝒰, 𝒱, 𝒲, 𝒳, 𝒴, 𝒵
   Double-struck: ℂ, ℍ, ℕ, ℙ, ℚ, ℝ, ℤ
   Formal: 𝔄, 𝔅, 𝔉, 𝔊, 𝔍, 𝔎, 𝔏, 𝔐, 𝔑, 𝔒, 𝔓, 𝔘, 𝔙, 𝔚, 𝔛, 𝔜, 𝔷

6. BRACKETING OPERATORS
   ⌊x⌋  -> Floor[x]
   ⌈x⌉  -> Ceiling[x]
   ⟨x,y⟩ -> AngleBracket[x,y]
   |x|  -> VerticalBar[x]
   ||x|| -> DoubleBracketingBar[x]

7. ARROW OPERATORS
   ->  -> Rule
   ⟹  -> ImpliedRightArrow
   ⟸  -> LeftArrow
   ⟷  -> DoubleArrow
   ↦  -> RuleDelayed

8. RELATIONAL OPERATORS
   =   -> Equal
   ≠   -> Unequal
   <   -> Less
   >   -> Greater
   ≤   -> LessEqual
   ≥   -> GreaterEqual
   ≈   -> ApproximateEqual
   ≡   -> Congruent
   ∼   -> TildeTilde
   ∝   -> Proportional

9. LOGICAL OPERATORS
   ∧   -> And
   ∨   -> Or
   ¬   -> Not
   ∀   -> ForAll (Subscript[ForAll, x])
   ∃   -> Exists (Subscript[Exists, x])
   ∈   -> Element
   ∉   -> NotElement
   ⊆   -> Subset
   ⊂   -> SubsetEqual

10. DIFFERENTIAL AND CALCULUS
    d   -> DifferentialD (EscddEsc)
    ∂   -> PartialD
    ∇   -> Del
    ∫   -> Integral
    ∮   -> ContourIntegral

NOTATION MAPPING FOR EXTRACTION PIPELINE
==========================================
When extracting math from PDFs, the following Unicode
characters map to Wolfram Language operators:

Unicode -> Wolfram Function
  α     -> Alpha (symbol name)
  β     -> Beta (symbol name)
  γ     -> Gamma (symbol name)
  ∂     -> PartialD
  ∇     -> Del
  ∑     -> Sum
  ∏     -> Product
  ∫     -> Integral
  ∈     -> Element
  ∉     -> NotElement
  ⊆     -> Subset
  ⊂     -> SubsetEqual
  ∪     -> Union
  ∩     -> Intersection
  ×     -> Times
  ÷     -> Divide
  ±     -> PlusMinus
  ∓     -> MinusPlus
  √     -> Sqrt
  ∞     -> Infinity
  π     -> Pi
  ℏ     -> HBar
  ℵ     -> Aleph
  °     -> Degree
  →     -> Rule
  ⟹     -> ImpliedRightArrow
  ⟸     -> LeftArrow
  ⟷     -> DoubleArrow
  ∴     -> Therefore
  ∵     -> Because
  ∶     -> Proportion
  ∷     -> EqualProportion
  ≅     -> Congruent
  ∼     -> TildeTilde
  ≈     -> ApproximateEqual
  ≠     -> Unequal
  ≡     -> Congruent
  ≤     -> LessEqual
  ≥     -> GreaterEqual
  <     -> Less
  >     -> Greater
  +     -> Plus
  -     -> Minus
  *     -> Times
  /     -> Divide
  ^     -> Power
  _     -> Subscript
  !     -> Factorial
  |x|   -> AbsoluteValue[x] or VerticalBar[x]
  ||x|| -> Norm[x] or DoubleBracketingBar[x]

EXTRACTION PIPELINE NOTES
==========================
1. PyMuPDF get_text("blocks") extracts rendered glyphs,
   not LaTeX source. Unicode equations captured directly.
   LaTeX commands (\frac, \sqrt, \mathbf) appear as
   literal text, not rendered math.

2. math_images field captures rendered math as images
   (PNG) when PyMuPDF cannot extract text. These require
   OCR (Tesseract) or vision model for content extraction.

3. Proof chains extracted from text blocks using
   keyword detection: proof, theorem, lemma, corollary,
   proposition, axiom, definition, example, exercise,
   solution, derivation, calculation, method, algorithm,
   result, claim, remark, note, case, step.

4. Garbled content (C0 control chars, CRLF artifacts,
   replacement chars) is filtered out entirely rather
   than cleaned, to avoid misinterpreting corrupted data.

5. Wolfram Language input uses StandardForm by default.
   Special characters have immediate meanings (π → Pi,
   ∞ → Infinity) or generic function names (⊕ → CirclePlus).
   Esc aliases provide keyboard entry for all special chars.