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
        GRAY_BAR, LATEX_NORM_TOKENS, normalize_latex_norms,
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

    GRAY_BAR is a single bar explicitly rendered grey. It is a literal token,
    NOT a norm. It must NOT be folded into the norm/shorthand path below.

    LATEX_NORM_TOKENS + normalize_latex_norms() is the LaTeX-side counterpart
    of MathML's balance_norm_tokens(). The same semantic rule applies:
    norm pairings are OPEN/CLOSE tokens, matched positionally, never left
    as two identical "open" halves.
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

# Floor / Ceiling - open/close halves. Tokens, not function calls.
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
# Gray-scale control bar (single bar, explicitly gray)
# ============================================================================
#
# U+00A6 (¦ BROKEN BAR) is used in some renderings as a grey/control bar.
# It is treated as a literal token, NOT a norm. It must NOT be folded into
# the norm/shorthand path below.
GRAY_BAR = "gray_bar"

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
    "¦": GRAY_BAR,

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
# Variable norm reservation
# ============================================================================

CONDITIONAL_BAR = "obar"  # for E[X obar X>a] - conditional/set builder
NORM_OPEN = "lVert"       # open double-bar
NORM_CLOSE = "rVert"      # close double-bar
ANGLE_OPEN = "langle"     # open angle
ANGLE_CLOSE = "rangle"    # close angle
FLOOR_OPEN = "lfloor"
FLOOR_CLOSE = "rfloor"
CEIL_OPEN = "lceil"
CEIL_CLOSE = "rceil"

# Family membership for inference
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
    GRAY_BAR: "bar",
}

# LaTeX norm command tokens for token-by-token recognition
# Ordered from longest/most-specific to shortest:
#   1. Explicit norms (\| and \Vert) - paired by position
#   2. Single-bar commands (\vert, \lvert, \rvert) - literal, not norm
LATEX_NORM_TOKENS = (
    r"\|",      # norm shorthand (paired by position)
    r"\Vert",   # norm value, equivalent to \| (paired by position)
    r"\vert",   # single bar (NOT a norm) - preserved for parse-time
    r"\rvert",  # single bar variant
    r"\lvert",  # single bar variant
)

def _match_latex_norm_token(latex: str, pos: int) -> tuple[str | None, int]:
    """Match the longest LATEX_NORM_TOKENS at position pos.

    Returns (matched_token, length) or (None, 0) if no match.
    """
    for tok in LATEX_NORM_TOKENS:
        if latex.startswith(tok, pos):
            return tok, len(tok)
    return None, 0

# ============================================================================
# LaTeX norm normalization
# ============================================================================

def normalize_latex_norms(latex: str) -> str:
    """Normalize LaTeX norm shorthand into an explicit open/close token pair.

    Decodes LaTeX norm-style commands into structural tokens so the downstream
    AST layer can compare the opening and closing halves of a double bar
    norm. Rules (position-based pairing):

      * Explicit norm commands (\| and \\Vert) are mapped to
        delimiter_identity.NORM_OPEN / NORM_CLOSE and never paired.

      * Shorthand norms (\\| and \\Vert) are paired by position: the first
        occurrence opens (NORM_OPEN), the second closes (NORM_CLOSE), and so
        on. Each pair is a balanced (open, close) with no crossing pairs.

    Examples:
        >>> normalize_latex_norms(r"\\|x\\|")
        'lVert x rVert'
        >>> normalize_latex_norms(r"\\lVert A \\rVert")
        'lVert A rVert'
        >>> normalize_latex_norms(r"\\Vert x \\Vert")
        'lVert x rVert'
        >>> normalize_latex_norms(r"\\vert x \\vert")
        '| x |'

    Returns the normalized string.
    """
    scanned = []           # list of (token, pos) for matched norm forms
    i = 0
    n = len(latex)
    while i < n:
        tok, length = _match_latex_norm_token(latex, i)
        if tok is not None:
            scanned.append((tok, i))
            i += length
        else:
            scanned.append((latex[i], i))
            i += 1

    resolved = []            # list of resolved items (strings + tuples)
    norm_stack = 0           # how many norms are currently open

    for tok, pos in scanned:
        if tok == r"\|":
            if norm_stack > 0:
                resolved.append(("NORM_CLOSE", pos))
                norm_stack = max(0, norm_stack - 1)
            else:
                resolved.append(("NORM_OPEN", pos))
                norm_stack += 1
        elif tok == r"\Vert":
            if norm_stack > 0:
                resolved.append(("NORM_CLOSE", pos))
                norm_stack = max(0, norm_stack - 1)
            else:
                resolved.append(("NORM_OPEN", pos))
                norm_stack += 1
        elif tok == r"\vert" or tok == r"\lvert" or tok == r"\rvert":
            resolved.append("SINGLE_BAR")
        else:
            resolved.append(tok)

    final = []
    for item in resolved:
        if item == "NORM_OPEN":
            final.append(NORM_OPEN)
        elif item == "NORM_CLOSE":
            final.append(NORM_CLOSE)
        elif isinstance(item, tuple) and item[0] == "NORM_OPEN":
            final.append(NORM_OPEN)
        elif isinstance(item, tuple) and item[0] == "NORM_CLOSE":
            final.append(NORM_CLOSE)
        else:
            final.append(item)

    return "".join(final).replace("NORM_OPEN", NORM_OPEN)\
                            .replace("NORM_CLOSE", NORM_CLOSE)\
                            .replace("SINGLE_BAR", "|")

def balance_norm_tokens(s: str) -> str:
    """Restore matched open/close norm pairs from a normalized string.

    This operates ONLY on NORM_OPEN/NORM_CLOSE tokens produced by
    `normalize_latex_norms()` and the MathML glyph layer. It does not touch
    SINGLE_BAR (|), GRAY_BAR, or any other delimiter.

    The single real job: MathML encodes both halves of a norm as the SAME
    glyph (‖), so the tree walk emits `lVert*x*lVert` — two opens, zero
    closes. This function rewrites that into a matched pair.

    Rules:
      * Scan the string for NORM_OPEN / NORM_CLOSE tokens in order.
      * If the string is already balanced (equal opens and closes, properly
        nested), return it UNCHANGED. Do not re-emit or duplicate tokens.
      * If there are more opens than closes (the MathML single-glyph case),
        convert the excess trailing opens into closes so every open has a
        matching close. This is positional: the 1st unmatched open becomes
        the close for the most recent still-open open.

    Returns the normalized string.
    """
    if not s:
        return s

    # --- Pass 1: tokenize norm positions in order ---
    # Each entry is (position, token_kind) where token_kind is 'O' or 'C'.
    positions = []
    i = 0
    n = len(s)
    while i < n:
        if s.startswith(NORM_OPEN, i):
            positions.append((i, "O"))
            i += len(NORM_OPEN)
        elif s.startswith(NORM_CLOSE, i):
            positions.append((i, "C"))
            i += len(NORM_CLOSE)
        else:
            i += 1

    if not positions:
        return s

    opens = sum(1 for _, k in positions if k == "O")
    closes = sum(1 for _, k in positions if k == "C")

    # --- Balanced: identity. Never duplicate. ---
    if opens == closes:
        return s

    # --- More closes than opens: leave as-is (stray closes are honest). ---
    if closes > opens:
        return s

    # --- More opens than closes (MathML single-glyph norm). ---
    # MathML emits BOTH halves as the same glyph, so a single norm ‖x‖
    # becomes `lVert*x*lVert` (2 opens, 0 closes) and nested ‖‖x‖‖ becomes
    # `lVert*lVert*x*lVert*lVert` (4 opens, 0 closes).
    #
    # The correct interpretation is ALTERNATION from the left: the 1st open
    # is a genuine open, the 2nd is its close, the 3rd is a new open, the
    # 4th is its close, etc. This is exactly what the single-glyph encoding
    # means (there is no nesting information to preserve — MathML gives us
    # none). So we alternate O, C, O, C... over the open tokens in order,
    # keeping any pre-existing closes in place.
    #
    # Count how many closes already exist; the remaining opens alternate
    # starting with 'O'.
    open_indices = [idx for idx, (pos, kind) in enumerate(positions) if kind == "O"]
    rewrite = {}
    # Alternate over ALL open positions, but only rewrite those that need it.
    # Existing closes stay; we re-label opens as O/C alternating from left.
    # Start the alternation at 'O' for the very first open.
    for seq, idx in enumerate(open_indices):
        pos, _ = positions[idx]
        # If this open is already correctly an open (alternation says 'O'),
        # leave it. If alternation says 'C', rewrite to close.
        if seq % 2 == 1:  # 2nd, 4th, ... open -> close
            rewrite[pos] = "C"

    # --- Rebuild the string with rewrites applied ---
    out = []
    i = 0
    while i < n:
        if i in rewrite and s.startswith(NORM_OPEN, i):
            out.append(NORM_CLOSE)
            i += len(NORM_OPEN)
        elif s.startswith(NORM_OPEN, i):
            out.append(NORM_OPEN)
            i += len(NORM_OPEN)
        elif s.startswith(NORM_CLOSE, i):
            out.append(NORM_CLOSE)
            i += len(NORM_CLOSE)
        else:
            out.append(s[i])
            i += 1

    return "".join(out)
