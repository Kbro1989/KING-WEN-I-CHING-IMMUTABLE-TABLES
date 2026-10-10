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
    r"\lVert": LNORM,     # explicit left norm
    r"\rVert": RNORM,     # explicit right norm
    r"\left\lVert": LNORM,
    r"\right\rVert": RNORM,

    # Single bar (divides, set builder, not norm)
    r"\lvert": BAR,
    r"\rvert": BAR,
    r"\left\lvert": BAR,
    r"\right\rvert": BAR,
    r"\vert": BAR,
    r"\Vert": LNORM,   # capital-V Vert = double bar norm (single token)
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

# ============================================================================
# LaTeX norm command tokens for token-by-token recognition
# ============================================================================
# Ordered from longest/most-specific to shortest:
#   1. Explicit left/right norms (\lVert, \rVert) - directional, paired
#   2. Shorthand norm commands (\|, \Vert) - alternate open/close by position
#   3. Single-bar commands (\vert, \lvert, \rvert) - NOT norms
LATEX_NORM_TOKENS = (
    r"\lVert",     # explicit left norm
    r"\rVert",     # explicit right norm
    r"\|",         # norm shorthand - alternates open/close
    r"\Vert",      # norm shorthand via \Vert - alternates open/close
    r"\vert",      # single bar (NOT a norm)
    r"\rvert",     # single bar variant
    r"\lvert",     # single bar variant
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
    """Normalize LaTeX norm shorthand into explicit open/close token pairs.

    Rules:

      * Explicit left/right norms (\lVert and \rVert) are paired by position.
        The first \lVert opens (NORM_OPEN), the first \rVert closes
        (NORM_CLOSE). Nested explicit pairs preserve nesting:
        \\lVert\\lVert x\\\\rVert\\\\rVert -> lVert lVert x rVert rVert
        Crossed explicit pairs (e.g., \\rVert...\\lVert) are reported as
        unmatched/ambiguous.

      * Shorthand norm commands (\\| and \\Vert) alternate by position:
        the 1st occurrence opens (NORM_OPEN), the 2nd closes (NORM_CLOSE),
        the 3rd opens, the 4th closes, etc. This produces no crossing pairs
        and preserves the original token sequence order. For example:
        \\|\\|x\\|\\| -> (NORM_OPEN, NORM_CLOSE, NORM_OPEN, NORM_CLOSE)

      * Single-bar commands (\\vert, \\lvert, \\rvert) are NOT norms and are
        converted to the single-bar token "|".

    Examples:
        >>> normalize_latex_norms(r"\\|x\\|")
        'lVert x rVert'
        >>> normalize_latex_norms(r"\\lVert\\\\lVert x\\\\rVert\\\\rVert")
        'lVert lVert x rVert rVert'
        >>> normalize_latex_norms(r"\\Vert x \\\\Vert")
        'lVert x rVert'
        >>> normalize_latex_norms(r"\\vert x \\\\vert")
        '| x |'
        >>> normalize_latex_norms(r"\\|\\|x\\|\\|")
        'lVert x rVert lVert x rVert'  # alternating, no crossing

    Returns the normalized string.
    """
    # Pass 1: token scan — identify each norm token and its position.
    # We track explicit opens separately from shorthand alternates.
    # 'explicit' = \lVert or \rVert (directional, push/pop stack)
    # 'shorthand' = \| or \Vert (alternating open/close by position)
    # 'single_bar' = \vert, \lvert, \rvert (NOT a norm)
    # 'other' = everything else
    scanned = []           # list of (kind, pos, token)
    i = 0
    n = len(latex)
    while i < n:
        tok, length = _match_latex_norm_token(latex, i)
        if tok is not None:
            if tok in (r"\lVert", r"\rVert"):
                scanned.append(("explicit", i, tok))
            elif tok in (r"\|", r"\Vert"):
                scanned.append(("shorthand", i, tok))
            else:
                scanned.append(("single_bar", i, tok))
            i += length
        else:
            scanned.append(("other", i, latex[i]))
            i += 1

    # Pass 2: resolve pairs.
    # For explicit: use a stack. Push open, pop on close. Unmatched close
    # is reported but not paired. Crossed explicit pairs are preserved
    # (each close matches the most recent open, even if that creates crossing).
    #
    # For shorthand: alternate by position. The first shorthand token in the
    # sequence opens, the second closes, the third opens, the fourth closes,
    # etc. This maintains the original order with no crossing pairs.
    resolved = []            # list of (kind, pos, token)
    explicit_stack = []      # stack of (pos, token)
    shorthand_count = 0      # how many shorthands seen so far

    for kind, pos, token in scanned:
        if kind == "explicit":
            if token == r"\lVert":
                # Open
                explicit_stack.append((pos, token))
                resolved.append(("pending", pos, token))
            else:  # \rVert
                # Close: match with most recent explicit open
                if explicit_stack:
                    explicit_stack.pop()
                    resolved.append(("pair", pos, token))
                else:
                    # No matching open - unmatched close (honest)
                    resolved.append(("unmatched_close", pos, token))
        elif kind == "shorthand":
            shorthand_count += 1
            if shorthand_count % 2 == 1:
                # Odd (1st, 3rd, 5th...) - open
                resolved.append(("pending", pos, token))
            else:
                # Even (2nd, 4th, 6th...) - close: emit NORM_CLOSE ONLY.
                # The open was already emitted as pending in the previous odd.
                # Re-emitting open + close would create a crossing pair.
                resolved.append(("close", pos, token))
        elif kind == "single_bar":
            resolved.append(("single_bar", pos, token))
        else:
            resolved.append(("other", pos, token))

    # Pass 3: reconstruct.
    # Pending opens emit NORM_OPEN only. Shorthand closes emit NORM_CLOSE only
    # (open was already emitted as pending). Explicit pairs emit NORM_CLOSE
    # only — the open was already emitted as pending. Single bar -> "|".
    # Other -> original token.
    final = []
    for kind, pos, token in resolved:
        if kind == "pending":
            # Open (1st, 3rd, 5th... shorthand, or explicit left norm)
            # The close will be emitted when we see the matching token.
            final.append(NORM_OPEN)
        elif kind == "pair":
            # Explicit close of explicit open = matched pair.
            # Open was already emitted as pending above; only emit close.
            final.append(NORM_CLOSE)
        elif kind == "close":
            # Shorthand close (2nd, 4th, 6th occurrence) - open was already
            # emitted as pending above; only emit close.
            final.append(NORM_CLOSE)
        elif kind == "single_bar":
            final.append("|")
        else:
            final.append(token)

    return "".join(final)

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
    # 4th is its close, etc. This is what the single-glyph encoding means
    # (there is no nesting information to preserve — MathML gives us none).
    # So we alternate O, C, O, C... over the open tokens in order.
    open_indices = [idx for idx, (pos, kind) in enumerate(positions) if kind == "O"]
    rewrite = {}
    # The 1st open stays open, 2nd open becomes close, 3rd opens, 4th closes...
    for seq, idx in enumerate(open_indices):
        pos, _ = positions[idx]
        # If this open is already correctly an open (alternation says 'O'),
        # leave it. If alternation says 'C' (2nd, 4th, ... open), rewrite to close.
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
