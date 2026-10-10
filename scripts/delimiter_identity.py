"""
Delimiter Identity Preservation
================================

Canonical delimiter tokens that preserve structural identity across parsing layers.

These tokens are the ONLY acceptable output for delimiter categories. No collapse.

Usage:
    from delimiter_identity import (
        MO_MAP_DELIMITERS, LATEX_DELIMITER_MAP, DELIMITER_FAMILY_MAP,
        LANGLE, RANGLE, LNORM, RNORM, BAR, LFLOOR, RFLOOR, LCEIL, RCEIL,
        CONDITIONAL_BAR, NORM_OPEN, NORM_CLOSE, ANGLE_OPEN, ANGLE_CLOSE,
        FLOOR_OPEN, FLOOR_CLOSE, CEIL_OPEN, CEIL_CLOSE,
    )

NOTE ON SEMANTICS:
    An identity token in the recovered string is NOT a SymPy-callable symbol
    that produces the bracket glyph. It is a STRUCTURAL MARKER that tells the
    downstream AST / scoreboard layer "this position was a floor / ceil /
    norm / angle / conditional delimiter". The AST layer turns these into
    typed AST nodes (Floor(x), Ceil(x), Norm(x), AngleBracket(...),
    Conditional(value, condition), ...) — see delimiter_inference.py.

    A literal floor( or ceil( in the solver string IS a function call and
    would fail SymPy. That is WHY we emit the identity token at the lexical
    layer and defer to the AST layer for grouping, not before.

    E[X obar X>a]  (conditional bar) is a SET-BUILDER / CONDITIONAL, NOT a
    product of "o", "b", "a", "r". It is a single token.
"""

# ============================================================================
# Canonical delimiter tokens (IDENTITY PRESERVATION)
# ============================================================================

# Generic brackets (structural, no special meaning)
LBRACKET = "("
RBRACKET = ")"
LSQUARE = "["
RSQUARE = "]"
LCURLY = "{"
RCURLY = "}"

# Angle brackets (inner product, expectation, lattice, NOT parentheses)
# SymPy will NOT accept "langle" as a standalone symbol; we turn it into a
# typed AST AngleBracket node downstream, never solve on it as text.
LANGLE = "langle"
RANGLE = "rangle"

# Floor / Ceiling — open/close halves. Tokens, not function calls.
LFLOOR = "lfloor"
RFLOOR = "rfloor"
LCEIL = "lceil"
RCEIL = "rceil"

# Norm brackets (double bar) - NOT single bar.
# We keep separate open/close so the AST can pair them: Norm(x).
LNORM = "lVert"
RNORM = "rVert"

# Set builder / conditional bar (single bar, not norm).
# "|x|" as absolute value vs "|x|" as norm MID is ambiguous; the AST layer
# uses PAIR RESOLUTION (delimiter_inference.py) to disambiguate: a bar that
# closes an open bar is ABS; a bar paired with an open double-bar is NORM.
BAR = "|"

# ============================================================================
# MathML char -> canonical token mapping
# ============================================================================

MO_MAP_DELIMITERS = {
    # Generic brackets
    "(": "(", ")": ")",
    "[": "[", "]": "]",
    "{": "{", "}": "}",

    # Angle brackets (NOT parentheses!)
    "⟨": LANGLE, "⟩": RANGLE,

    # Floor / Ceiling
    "⌊": LFLOOR, "⌋": RFLOOR,
    "⌈": LCEIL, "⌉": RCEIL,

    # Norm bars (double bar)
    "‖": LNORM, "∥": LNORM,

    # Single bar (divides / set builder / absolute / norm mid)
    "∣": BAR,
    "|": BAR,
    "¦": BAR,

    # Differential
    "𝑑": "d", "ⅆ": "d", "ⅅ": "d",
}

# ============================================================================
# LaTeX command -> canonical token mapping
# ============================================================================

LATEX_DELIMITER_MAP = {
    # Angle brackets (preserve identity, NOT become parentheses)
    r"\langle": LANGLE,
    r"\rangle": RANGLE,
    r"\left\langle": LANGLE,
    r"\right\rangle": RANGLE,

    # Floor / Ceiling
    r"\lfloor": LFLOOR,
    r"\rfloor": RFLOOR,
    r"\left\lfloor": LFLOOR,
    r"\right\rfloor": RFLOOR,

    # Ceiling
    r"\lceil": LCEIL,
    r"\rceil": RCEIL,
    r"\left\lceil": LCEIL,
    r"\right\rceil": RCEIL,

    # Norm (double bar) - identity preserved, NOT collapsed to single bar
    r"\lVert": LNORM,
    r"\rVert": RNORM,
    r"\left\lVert": LNORM,
    r"\right\rVert": RNORM,

    # Single bar (divides, set builder, not norm)
    r"\lvert": BAR,
    r"\rvert": BAR,
    r"\left\lvert": BAR,
    r"\right\rvert": BAR,
    r"\vert": BAR,
    r"\Vert": LNORM,   # capital-V Vert = double bar norm (single token)

    # Note: \mid stays as BAR (divides/conditional); it is NOT a norm.
}

# ============================================================================
# Family membership for inference
# ============================================================================

DELIMITER_FAMILY_MAP = {
    LANGLE: "angle",
    RANGLE: "angle",
    LNORM: "norm",
    RNORM: "norm",
    LFLOOR: "floor",
    RFLOOR: "floor",
    LCEIL: "ceil",
    RCEIL: "ceil",
    BAR: "bar",
}

# ============================================================================
# Reserved tokens for structured representation
# ============================================================================

# These are the tokens that downstream parsers consume
# They represent structured constructs, not atomic symbols

CONDITIONAL_BAR = "obar"  # for E[X obar X>a] - conditional/set builder
NORM_OPEN = "norml"       # open double-bar
NORM_CLOSE = "normr"      # close double-bar
ANGLE_OPEN = "langle"     # open angle
ANGLE_CLOSE = "rangle"    # close angle
FLOOR_OPEN = "lfloor"
FLOOR_CLOSE = "rfloor"
CEIL_OPEN = "lceil"
CEIL_CLOSE = "rceil"


# ============================================================================
# Ambiguous-glyph normalization
# ============================================================================
#
# MathML encodes BOTH halves of a norm as the SAME single glyph (U+2016 ‖,
# U+2225 ∥). A <mo> carries no open/close information, so walking the tree
# emits `lVert` for both sides:
#       ‖x‖   ->   'lVert*x*lVert'      (WRONG: no close token)
# The pairing layer then cannot match the pair and the norm is lost.
#
# LaTeX is unambiguous (\lVert vs \rVert), so only the glyph path needs this.
# We normalize by ALTERNATION: the 1st, 3rd, 5th... lVert stays open; the
# 2nd, 4th, ... becomes rVert. This is correct for sequential (non-nested)
# norms, which is what the single-glyph encoding can express.
#
# Nesting: `‖‖x‖‖` alternates to lVert rVert lVert rVert — correct.
# A norm inside an angle bracket is unaffected (different token families).

def balance_norm_tokens(s):
    """Alternate lVert -> rVert for each closing occurrence.

    MathML's single-glyph norm has no open/close distinction. This restores
    the pairing so downstream layers can match them.

    Returns the normalized string.
    """
    if "lVert" not in s:
        return s
    out = []
    i = 0
    depth = 0
    while i < len(s):
        if s.startswith("lVert", i):
            if depth % 2 == 1:
                out.append("rVert")
            else:
                out.append("lVert")
            depth += 1
            i += len("lVert")
        else:
            out.append(s[i])
            i += 1
    return "".join(out)
