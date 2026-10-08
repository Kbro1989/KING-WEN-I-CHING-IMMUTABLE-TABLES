"""
MathML Tree Parser
==================
Walks arxiv's MathML tree and emits a solver-ready expression.

Why this exists: regexing a LaTeX *string* cannot handle nested braces.
The HTML already contains a parsed tree (mrow/mfrac/msub/msup). Walking it
gives correct grouping for free.

Mapping:
  <mrow>            -> sequence (implicit product between adjacent atoms)
  <mfrac><a><b>     -> (a)/(b)
  <msup><a><b>      -> (a)**(b)
  <msub><a><b>      -> a_b
  <msubsup><a><b><c>-> a_b**(c)
  <msqrt><a>        -> sqrt(a)
  <mroot><a><b>     -> (a)**(1/(b))
  <mo>              -> operator (mapped to ASCII)
  <mi>              -> identifier (multi-char preserved as ONE symbol)
  <mn>              -> number
  <mtable>          -> UNSUPPORTED (system/matrix, not a single equation)
  <mstyle>          -> unwrap
  <mover>/<munder>  -> unwrap base (accent/limit decoration)
  <semantics>       -> first child only (presentation), skip annotation

No fabrication: unsupported constructs return (None, reason) instead of guessing.
"""
import re
import unicodedata

# ---------------------------------------------------------------------------
# Operator mapping: MathML <mo> content -> ASCII
# ---------------------------------------------------------------------------
MO_MAP = {
    # arithmetic
    "+": "+", "−": "-", "-": "-", "±": "+", "∓": "-",
    "×": "*", "⋅": "*", "·": "*", "∗": "*", "⋆": "*",
    "÷": "/", "∕": "/",
    # --- EQUALITY: only true equality operators map to '='
    "=": "=", "≡": "=", "≔": "=", "≕": "=", ":=": "=", "≝": "=",
    # --- NON-EQUALITY RELATIONS -------------------------------------------
    # These are NOT equality. Mapping them to '=' fabricates solutions the
    # paper never stated (x ~ q(x) is NOT x = q(x)). Each keeps its own
    # marker token so the relation survives into the expression.
    "≠": "!=",
    "≈": "~=", "≃": "~=", "≅": "~=", "∼": "~=", "∽": "~=",
    "∝": "propto", "≍": "~=",
    "≤": "<=", "⩽": "<=", "≥": ">=", "⩾": ">=", "<": "<", ">": ">",
    "≪": "<<", "≫": ">>", "≺": "prec", "≻": "succ",
    # logic / sets -- membership is NOT equality
    "∈": "in", "∉": "notin", "∋": "ni", "⊂": "subset", "⊃": "supset",
    "⊆": "subseteq", "⊇": "supseteq",
    "∧": "and", "∨": "or", "¬": "not", "∀": "forall", "∃": "exists",
    "∩": "cap", "∪": "cup", "∖": "setminus", "∅": "emptyset",
    # arrows are relations/maps, NOT equality
    "→": "->", "←": "<-", "↔": "<->", "⇒": "=>", "⇐": "<=", "⇔": "<=>",
    "↦": "|->", "⟶": "->", "⟵": "<-", "⟹": "=>", "⟸": "<=", "⟺": "<=>",
    # grouping (kept as literal brackets)
    "(": "(", ")": ")", "[": "[", "]": "]",
    "{": "{", "}": "}",
    "⟨": "(", "⟩": ")",
    "⌊": "floor(", "⌋": ")",
    "⌈": "ceil(", "⌉": ")",
    "|": "|", "‖": "|", "∥": "|",
    # named constants
    "∞": "oo", "ℵ": "aleph", "ℏ": "hbar", "ℯ": "e", "ⅈ": "i",
    "∂": "partial", "∇": "grad", "Δ": "Delta", "√": "sqrt",
    # big operators (limits, extrema) — must be named tokens, not dropped
    "max": "Max", "min": "Min", "sup": "sup", "inf": "inf",
    "lim": "Limit", "argmax": "argmax", "argmin": "argmin",
    "limsup": "limsup", "liminf": "liminf",
    # accent operators (hat, bar, tilde, etc.) — must be preserved as markers
    "^": "^", "‾": "bar", "˜": "tilde", "¯": "bar", "ˆ": "hat",
    "˙": "dot", "¨": "ddot", "˚": "ring", "˘": "breve", "ˇ": "check",
    # misc
    "!": "", "%": "/100", ",": ",", ";": ";", ":": ":",
    ".": ".", "…": "", "⋯": "", "⋮": "", "⋱": "",
    "′": "", "″": "", "‴": "",
    # invisible operators -> drop
    "\u2061": "", "\u200b": "", "\u2060": "", "\u200c": "", "\u200d": "",
    "\ufeff": "", "\u00ad": "",
}

# Bases that take under/over LIMITS rather than ordinary sub/superscripts.
# A node whose base is in this set must never fall through to `return base`
# — that silently discards the limit and loses the summation index, the
# constraint set, or the bound.
BIG_OP_BASES = {
    "Sum", "Prod", "Integral", "Limit",
    "Max", "Min", "sup", "inf",
    "argmax", "argmin", "limsup", "liminf",
    "Union", "Intersect",
}

# Relation tokens that are NOT equality. If one of these appears in a
# recovered expression, the expression is a RELATION, not an equation, and
# must never be handed to a solver as 'lhs = rhs'.
NON_EQUALITY_TOKENS = {
    "~=", "!=", "propto", "prec", "succ", "<<", ">>", "<", ">", "<=", ">=",
    "in", "notin", "ni", "subset", "supset", "subseteq", "supseteq",
    "and", "or", "not", "forall", "exists", "cap", "cup", "setminus",
    "->", "<-", "<->", "=>", "<=>", "|->",
}

# Multi-char operators that appear as a single <mo>.
# NOTE: must NOT contain equality substitutions for non-equality relations.
MO_MULTI = {
    "∑": "Sum", "∏": "Prod", "∫": "Integral", "∮": "Integral",
    "∂": "d", "∇": "grad", "∞": "oo",
    "√": "sqrt",
}

# Mathematical alphanumeric Greek: NFKD does NOT decompose these, so map manually.
# Bold/italic/bold-italic Greek used for vectors/matrices in ML papers.
GREEK_MATH_ALPHANUM = {
    # bold italic (U+1D6E2 block variants commonly used)
    "𝜶": "alpha", "𝜷": "beta", "𝜸": "gamma", "𝜹": "delta", "𝜺": "epsilon",
    "𝜻": "zeta", "𝜼": "eta", "𝜽": "theta", "𝜾": "iota", "𝜿": "kappa",
    "𝝀": "lambda", "𝝁": "mu", "𝝂": "nu", "𝝃": "xi", "𝝅": "pi",
    "𝝆": "rho", "𝝈": "sigma", "𝝉": "tau", "𝝊": "upsilon", "𝝋": "phi",
    "𝝌": "chi", "𝝍": "psi", "𝝎": "omega",
    # bold
    "𝜶": "alpha", "𝜷": "beta", "𝜸": "gamma", "𝜹": "delta",
    "𝝁": "mu", "𝝂": "nu", "𝝈": "sigma", "𝝉": "tau", "𝝎": "omega",
    "𝚺": "Sigma", "𝚲": "Lambda", "𝚯": "Theta", "𝚽": "Phi", "𝚿": "Psi",
    "𝛀": "Omega", "𝚷": "Pi", "𝚵": "Xi", "𝚫": "Delta", "𝚪": "Gamma",
    # italic
    "𝛂": "alpha", "𝛃": "beta", "𝛄": "gamma", "𝛅": "delta",
    "𝛉": "theta", "𝛌": "lambda", "𝛍": "mu", "𝛑": "pi", "𝛔": "sigma",
    "𝛕": "tau", "𝛚": "omega", "𝚹": "Theta", "𝚲": "Lambda", "𝚺": "Sigma",
}

# Function names (multi-char <mi> that are operators, not symbols)
FUNCTION_NAMES = {
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan", "arccot",
    "sinh", "cosh", "tanh", "coth", "sech", "csch",
    "log", "ln", "exp", "lg",
    "det", "dim", "ker", "deg", "gcd", "lcm", "arg", "mod",
    "min", "max", "sup", "inf", "lim", "Pr", "tr", "diag", "rank",
    "Var", "Cov", "Corr", "softmax", "sigmoid", "relu", "ReLU",
}

# Upright/blackboard/fraktur single letters -> ASCII equivalents
SPECIAL_LETTERS = {
    "𝔼": "E", "ℝ": "R", "ℕ": "N", "ℤ": "Z", "ℚ": "Q", "ℂ": "C",
    "𝕀": "I", "ℙ": "P", "𝔽": "F", "𝕏": "X", "𝕐": "Y",
    "𝒜": "A", "ℬ": "B", "𝒞": "C", "𝒟": "D", "ℰ": "E", "ℱ": "F",
    "𝒢": "G", "ℋ": "H", "ℐ": "I", "𝒥": "J", "𝒦": "K", "ℒ": "L",
    "ℳ": "M", "𝒩": "N", "𝒪": "O", "𝒫": "P", "𝒬": "Q", "ℛ": "R",
    "𝒮": "S", "𝒯": "T", "𝒰": "U", "𝒱": "V", "𝒲": "W", "𝒳": "X",
    "𝒴": "Y", "𝒵": "Z",
    "ℓ": "l", "ℏ": "hbar", "ℵ": "aleph",
    # misc symbols that appear as <mi>/<mo> in arxiv MathML
    "∞": "oo", "⊤": "T", "⊥": "perp", "∘": "*", "†": "dagger",
    "∠": "angle", "△": "triangle", "□": "square", "◇": "diamond",
    # plain Greek lowercase (U+03B1-U+03C9)
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa",
    "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "π": "pi",
    "ρ": "rho", "ς": "sigma", "σ": "sigma", "τ": "tau", "υ": "upsilon",
    "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    # plain Greek uppercase
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda", "Ξ": "Xi",
    "Π": "Pi", "Σ": "Sigma", "Υ": "Upsilon", "Φ": "Phi", "Ψ": "Psi",
    "Ω": "Omega",
    # variants
    "ϵ": "epsilon", "ϑ": "theta", "ϕ": "phi", "ϖ": "pi", "ϱ": "rho", "ϰ": "kappa",
}


def normalize_char(ch):
    """Map a single unicode math char to an ASCII equivalent."""
    if ch in SPECIAL_LETTERS:
        return SPECIAL_LETTERS[ch]
    if ch in GREEK_MATH_ALPHANUM:
        return GREEK_MATH_ALPHANUM[ch]
    # NFKD decomposes mathematical bold/italic alphanumerics to base ASCII
    d = unicodedata.normalize("NFKD", ch)
    if d and d != ch:
        # keep only ascii letters/digits from the decomposition
        ascii_part = "".join(c for c in d if c.isascii())
        if ascii_part:
            return ascii_part
    if ch.isascii():
        return ch
    return ""


def normalize_text(text):
    """Normalize a run of text (mi/mn/mtext content) to ASCII."""
    out = []
    for ch in text:
        n = normalize_char(ch)
        out.append(n if n else ch)
    return "".join(out)


class MathMLParser:
    """Walk a MathML element tree and emit a solver expression."""

    def __init__(self, tag_getter=None, children_getter=None, text_getter=None):
        # allow injection for testability; default works with BeautifulSoup Tag
        self._tag = tag_getter or (lambda n: n.name if hasattr(n, "name") else None)
        self._children = children_getter or (
            lambda n: [c for c in n.children if getattr(c, "name", None)]
        )
        self._text = text_getter or (lambda n: n.get_text() if hasattr(n, "get_text") else str(n))
        self.unsupported = []   # reasons collected during walk
        self.symbols = set()    # identifiers seen

    # -- public ------------------------------------------------------------
    def parse(self, node):
        """Parse a <math> node. Returns (expr_string, unsupported_reasons)."""
        self.unsupported = []
        self.symbols = set()
        expr = self._walk(node)
        if expr is None:
            return None, self.unsupported
        expr = self._tidy(expr)
        return expr, self.unsupported

    # -- internals ---------------------------------------------------------
    def _walk(self, node):
        tag = self._tag(node)
        if tag is None:
            return ""

        # --- root element: recurse into children
        if tag == "math":
            kids = self._children(node)
            return "".join(filter(None, (self._walk(k) for k in kids)))

        # --- leaf tokens
        if tag == "mi":
            return self._handle_mi(self._text(node))
        if tag == "mn":
            return self._handle_mn(self._text(node))
        if tag == "mo":
            return self._handle_mo(self._text(node))
        if tag == "mtext":
            return self._handle_mtext(self._text(node))

        # --- structure
        if tag == "semantics":
            kids = self._children(node)
            # first child is the presentation MathML
            return self._walk(kids[0]) if kids else ""

        if tag == "annotation":
            return ""   # skip LaTeX annotation; we want the tree

        if tag == "mrow":
            return self._handle_mrow(node)

        if tag == "mfrac":
            kids = self._children(node)
            if len(kids) < 2:
                self.unsupported.append("mfrac_arity")
                return None
            num = self._walk(kids[0])
            den = self._walk(kids[1])
            if num is None or den is None:
                return None
            return f"(({num})/({den}))"

        if tag == "msup":
            kids = self._children(node)
            if len(kids) < 2:
                self.unsupported.append("msup_arity")
                return None
            base = self._walk(kids[0])
            exp = self._walk(kids[1])
            if base is None or exp is None:
                return None
            # OPERATOR SUPERSCRIPTS: a superscript that is an operator symbol
            # (transpose, dagger, perp) is a MARKER, not an exponent.
            # Emitting '**' here silently converts transpose into exponentiation.
            raw = (self._text(kids[1]) or "").strip()
            if raw in ("⊤", "\\top") or exp == "T":
                return f"{base}_T"
            if raw in ("†", "\\dagger") or exp == "dagger":
                return f"{base}_dag"
            if raw in ("⊥",):
                return f"{base}_perp"
            # A prime is a derivative marker, not an exponent
            if raw in ("′", "\\prime", "'"):
                return f"{base}_prime"
            # OPTIMALITY / DUALITY markers: \ast and \star in a superscript
            # mean "optimal" or "dual", NOT multiplication.
            # MO_MAP turns ∗ and ⋆ into '*', so without this branch the exponent
            # becomes '**()' after tidy strips the bare operator, destroying it:
            #   p^{\ast}      ->  '((p)**())'   WRONG
            #   \Delta_j^{\star} -> 'Delta_j**()' WRONG
            if raw in ("∗", "⋆", "\\ast", "\\star", "*"):
                return f"{base}_star"
            # INFINITY as an exponent is a genuine value, not an operator
            if raw in ("∞", "\\infty"):
                return f"(({base})**(oo))"
            return f"(({base})**({exp}))"

        if tag == "msub":
            kids = self._children(node)
            if len(kids) < 2:
                self.unsupported.append("msub_arity")
                return None
            base = self._walk(kids[0])
            sub = self._walk(kids[1])
            if base is None or sub is None:
                return None
            return f"{base}_{self._subscript_token(sub)}"

        if tag == "msubsup":
            kids = self._children(node)
            if len(kids) < 3:
                self.unsupported.append("msubsup_arity")
                return None
            base = self._walk(kids[0])
            sub = self._walk(kids[1])
            sup = self._walk(kids[2])
            if base is None or sub is None or sup is None:
                return None

            # Big operator with limits: sum/prod/integral from lo to hi.
            # These are bound operators, not variable subscripts.
            # Max/Min/Limit/argmax also take limits and MUST be included —
            # omitting them dropped the constraint: max_{beta in Delta_n} -> "Max".
            if base in BIG_OP_BASES:
                return f"{base}_{self._limit_token(sub)}_{self._limit_token(sup)}"

            # OPERATOR SUPERSCRIPT on a subscripted symbol:
            # Q_A^{\top} -> Q_A_T   (marker), NOT Q_A ** T (exponentiation).
            raw = (self._text(kids[2]) or "").strip()
            if raw in ("⊤", "\\top") or sup == "T":
                return f"{base}_{self._subscript_token(sub)}_T"
            if raw in ("†", "\\dagger") or sup == "dagger":
                return f"{base}_{self._subscript_token(sub)}_dag"
            if raw in ("⊥",):
                return f"{base}_{self._subscript_token(sub)}_perp"
            if raw in ("′", "\\prime", "'"):
                return f"{base}_{self._subscript_token(sub)}_prime"
            # \ast / \star as an OPERATOR SUPERSCRIPT are optimality/duality
            # markers, not multiplication. Without this branch msubsup emits
            # an empty exponent:  \Delta_j^{\star} -> 'Delta_j**()'.
            if raw in ("∗", "⋆", "\\ast", "\\star", "*"):
                return f"{base}_{self._subscript_token(sub)}_star"
            if raw in ("∞", "\\infty"):
                return f"{base}_{self._subscript_token(sub)}**({sup})"

            return f"{base}_{self._subscript_token(sub)}**({sup})"

        if tag == "msqrt":
            kids = self._children(node)
            inner = "".join(filter(None, (self._walk(k) for k in kids)))
            return f"sqrt({inner})"

        if tag == "mroot":
            kids = self._children(node)
            if len(kids) < 2:
                self.unsupported.append("mroot_arity")
                return None
            arg = self._walk(kids[0])
            idx = self._walk(kids[1])
            if arg is None or idx is None:
                return None
            return f"(({arg})**(1/({idx})))"

        if tag in ("mstyle", "mpadded", "mphantom", "merror", "menclose"):
            kids = self._children(node)
            inner = "".join(filter(None, (self._walk(k) for k in kids)))
            return inner

        if tag in ("mover", "munder", "munderover"):
            kids = self._children(node)
            if not kids:
                return ""
            base = self._walk(kids[0])
            if base is None:
                return None

            if len(kids) > 1:
                script = self._walk(kids[1])
                acc = (self._text(kids[1]) or "").strip()

                # TRANSPOSE / dagger: superscript that is an operator, not a value.
                # Must be attached as a marker, never left dangling as '**',
                # which in other contexts reads as exponentiation.
                if acc in ("⊤", "T", "\\top") or script == "T":
                    return f"{base}_T"
                if acc in ("†", "\\dagger") or script == "dagger":
                    return f"{base}_dag"
                if acc in ("⊥",):
                    return f"{base}_perp"

                # BIG OPERATOR WITH UNDERNEATH LIMITS: \\sum_{y\\in\\mathcal{Y}}
                # In display mode, limits sit UNDER the operator, encoded as
                # <munder> or <munderover> — NOT <msub>. Falling through to
                # `return base` here silently DROPS the limits, which is exactly
                # the "missing nodes" symptom: the summation index and domain
                # vanish from the recovered expression.
                if base in BIG_OP_BASES:
                    if tag == "munderover" and len(kids) >= 3:
                        lo = self._walk(kids[1])
                        hi = self._walk(kids[2])
                        if lo is not None and hi is not None:
                            return f"{base}_{self._limit_token(lo)}_{self._limit_token(hi)}"
                    if tag == "munder" and len(kids) >= 2:
                        lo = self._walk(kids[1])
                        if lo is not None:
                            return f"{base}_{self._limit_token(lo)}"

                # Accent characters: tag the symbol.
                tag_name = self._accent_name(acc)
                if tag_name:
                    # base may already carry an accent (nested: \hat{\tilde{h}}).
                    # Accumulate BOTH so distinct symbols never collapse into one.
                    return f"{base}_{tag_name}"

            return base

        if tag == "mtable":
            # STRUCTURAL CONSERVATION: a table is not a single solvable
            # equation, but returning None DISCARDS every row and cell —
            # information loss, not a backend limitation.
            #
            # Instead, walk the table and preserve its contents in a readable
            # bracketed form, and record the flag so the solver stage can
            # still refuse to treat it as one equation.
            rows = []
            for tr in node.find_all("mtr", recursive=False):
                cells = []
                for td in tr.find_all("mtd", recursive=False):
                    cell = "".join(
                        filter(None, (self._walk(k) for k in self._children(td)))
                    )
                    cells.append(cell)
                rows.append(cells)
            self.unsupported.append("mtable_system")
            if not rows:
                return ""
            # matrix-like rendering: [ a, b ; c, d ]
            body = " ; ".join(", ".join(c for c in row) for row in rows)
            return f"[{body}]"

        if tag == "mspace":
            return ""

        # Unknown element: try to recurse, record the tag
        self.unsupported.append(f"unknown_tag:{tag}")
        kids = self._children(node)
        if kids:
            return "".join(filter(None, (self._walk(k) for k in kids)))
        return ""

    # -- token handlers ----------------------------------------------------
    def _handle_mi(self, text):
        t = normalize_text(text).strip()
        if not t:
            return ""
        if t in FUNCTION_NAMES:
            return t
        # single letter -> symbol
        if len(t) == 1:
            self.symbols.add(t)
            return t
        # multi-letter: keep as ONE symbol (this is the key fix vs regex splitting)
        # but only if it looks like an identifier
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", t):
            self.symbols.add(t)
            return t
        # otherwise it's a decorated/garbled token -> single letters
        return t

    def _handle_mn(self, text):
        t = normalize_text(text).strip()
        # strip thousands separators / spaces inside numbers
        t = t.replace(",", "").replace(" ", "")
        return t

    def _handle_mo(self, text):
        t = text.strip()
        if not t:
            return ""
        if t in MO_MULTI:
            return MO_MULTI[t]
        if t in MO_MAP:
            return MO_MAP[t]
        # unknown operator: normalize, record
        n = normalize_text(t)
        if n and all(c in "+-*/=<>()[]{}.,|" for c in n):
            return n
        self.unsupported.append(f"unknown_mo:{t!r}")
        return ""

    def _handle_mtext(self, text):
        t = normalize_text(text).strip()
        if not t:
            return ""
        # text in math mode is a label -> single symbol
        t = re.sub(r"\s+", "_", t)
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", t):
            self.symbols.add(t)
            return t
        return ""

    def _handle_mrow(self, node):
        """Sequence. Insert '*' between adjacent atoms (implicit product)."""
        kids = self._children(node)
        parts = []
        for k in kids:
            r = self._walk(k)
            if r is None:
                return None
            parts.append((self._tag(k), r))

        out = []
        for i, (tag, r) in enumerate(parts):
            if i > 0 and r and self._needs_product(parts[i - 1], (tag, r)):
                out.append("*")
            out.append(r)
        return "".join(out)

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _needs_product(prev, cur):
        """True if prev and cur should be multiplied (implicit product)."""
        _, a = prev
        _, b = cur
        if not a or not b:
            return False
        # no product after an operator or open bracket
        if a[-1] in "+-*/=(<[{,|:":
            return False
        # no product before an operator or close bracket
        if b[0] in "+-*/=)>,]}|:":
            return False
        # no product if prev ends with an operator word
        if re.search(r"(Sum|Prod|Integral|sqrt|not|forall|exists|floor|ceil)$", a):
            return False
        # no product if cur starts with a function name
        if re.match(r"^(sin|cos|tan|log|ln|exp|min|max|sup|inf|det|dim|Var|Cov|Corr)\b", b):
            return False
        # comma/semicolon are separators, never multiplied
        if b[0] in ",;":
            return False
        # FUNCTION APPLICATION: identifier directly followed by a bracket is a call,
        # not a product. 'p_θ(x_0)' -> p_θ(x_0); 'E[x]' -> E[x]
        if b[0] in "([{" and re.search(r"[A-Za-z0-9_]$", a):
            return False
        # FUNCTION NAME glued to a symbol: 'cos' + 'theta' -> 'cos(theta)'.
        # Trig/log functions take their argument without parens in MathML.
        if re.search(r"(cos|sin|tan|cot|sec|csc|log|ln|exp|max|min|sup|inf)$", a) \
           and re.match(r"^[A-Za-z]", b):
            return False
        return True

    @staticmethod
    def _subscript_token(sub):
        """Make a subscript safe as part of an identifier.

        Subscripts are NAME PARTS, not arithmetic:
          '0:T'   -> '0_T'    (colon = range)
          't-1'   -> 't_1'    (minus is part of the name, NOT subtraction)
          'i,j'   -> 'i_j'
        Getting this wrong silently changes meaning: L_{t-1} must never
        parse as (L_t - 1).
        """
        s = sub.strip()
        s = s.replace(" ", "")
        if not s:
            return "0"
        # range separator
        s = s.replace(":", "_")
        # arithmetic-looking chars inside a subscript are name separators
        s = s.replace("-", "_")
        s = s.replace("+", "_")
        s = s.replace("*", "")
        s = s.replace(",", "_")
        s = s.replace("=", "_")
        s = s.replace("|", "_")
        s = re.sub(r"_+", "_", s)
        s = s.strip("_")
        return s or "0"

    @staticmethod
    def _limit_token(lim):
        """
        Normalise a big-operator limit like 'i=1' or 'n' into a token.

        The equality must NOT be flattened to '_' — that makes `i=1` and `i_1`
        indistinguishable, so the bound is lost as a relation and survives only
        as a separator. Use a distinct 'eq' marker so the limit reads
        unambiguously:  Sum_i=1^n  ->  Sum_i_eq_1_n
        """
        s = lim.strip().replace(" ", "")
        s = s.replace("=", "_eq_")
        s = s.replace("\le", "_le_").replace("\ge", "_ge_")
        s = s.replace("\in", "_in_").replace("\to", "_to_")
        s = s.replace(",", "_")
        s = re.sub(r"_+", "_", s)
        s = s.strip("_")
        return s or "n"

    @staticmethod
    def _accent_name(ch):
        # Both the combining/macron forms AND the standalone MathML operator
        # codepoints must be present. arxiv emits U+203E (overline) for \\bar,
        # not U+00AF (macron) — omitting it silently dropped every overline.
        return {
            "^": "hat", "ˆ": "hat",            # U+005E, U+02C6
            "¯": "bar", "‾": "bar",            # U+00AF macron, U+203E overline
            "~": "tilde", "˜": "tilde",        # U+007E, U+02DC
            "→": "vec", "⟶": "vec",            # arrows used as vector accent
            "˙": "dot", "¨": "ddot",
            "ˇ": "check", "˘": "breve",
            "˚": "ring", "°": "deg",
            "⌢": "frown", "⌣": "smile",
            "⏞": "overbrace", "⏟": "underbrace",
        }.get(ch)

    @staticmethod
    def _tidy(expr):
        """Light cleanup: collapse whitespace, drop empty groups.

        IMPORTANT: must NOT collapse '**' (exponent) into '*'. Only runs of
        three-or-more stars are artifacts and get collapsed.
        """
        if expr is None:
            return None
        s = expr
        s = re.sub(r"\s+", " ", s)
        s = s.replace("()", "")
        s = re.sub(r"\(\s*\)", "", s)
        # collapse only 3+ star runs (artifacts); preserve '**' exponents
        s = re.sub(r"\*{3,}", "*", s)
        s = re.sub(r"\(\*", "(", s)
        s = re.sub(r"\*\)", ")", s)
        s = s.strip()
        s = s.strip("*")
        return s


# ---------------------------------------------------------------------------
# Extraction: pull every equation out of arxiv HTML with BOTH tree and alttext
# ---------------------------------------------------------------------------

def extract_from_html(html):
    """
    Extract every equation from arxiv HTML.
    Uses the MathML tree as primary (structured) and alttext as cross-check.

    Returns list of dicts:
      {expr, alttext_latex, display, unsupported, symbols, source}
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    out = []

    for math_tag in soup.find_all("math"):
        alttext = math_tag.get("alttext") or ""
        display_attr = (math_tag.get("display") or "inline").lower()

        parser = MathMLParser()
        expr, unsupported = parser.parse(math_tag)

        if expr is None and not unsupported:
            continue

        out.append({
            "expr": expr,
            "alttext_latex": alttext,
            "display": display_attr,
            "unsupported": unsupported,
            "symbols": sorted(parser.symbols),
            "source": "mathml_tree",
        })

    return out


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, json, urllib.request

    if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        url = sys.argv[1]
    elif len(sys.argv) > 1:
        url = f"https://arxiv.org/html/{sys.argv[1]}"
    else:
        url = "https://arxiv.org/html/2006.11239"

    req = urllib.request.Request(url, headers={"User-Agent": "mathml-parser/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

    eqs = extract_from_html(html)
    print(f"Extracted {len(eqs)} math nodes from {url}")
    print()

    solved_like = 0
    for e in eqs[:15]:
        print(f"  display={e['display']:5s} expr={str(e['expr'])[:110]}")
        if e["unsupported"]:
            print(f"          unsupported: {e['unsupported']}")
    print()

    # summary
    has_eq = sum(1 for e in eqs if e["expr"] and e["expr"].count("=") == 1)
    unsup = sum(1 for e in eqs if e["unsupported"])
    print(f"Nodes with exactly one '=': {has_eq}/{len(eqs)}")
    print(f"Nodes with unsupported constructs: {unsup}/{len(eqs)}")
