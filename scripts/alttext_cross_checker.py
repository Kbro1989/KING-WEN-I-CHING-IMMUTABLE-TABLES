"""
AltText Cross-Checker
=====================
Reads the LaTeX `alttext` / `<annotation>` that arXiv embeds in every <math>
tag and compares it against what the MathML tree walk produced.

Purpose
-------
The MathML walk works bottom-up on the structured tree, which is ideal for
solving but can drop or mangle:
  - Large operator symbols (∑ ∫ ∏) when LaTeXML oxide puts their limits as
    empty-base siblings rather than proper msubsup children
  - Greek letters that appear in unusual math-alphabet variants (bold italic, etc.)
  - Bracket variants: \left( \right|  \Bigg[  \lVert \rVert
  - Division lines / fractions rendered as \cfrac, \dfrac, \tfrac
  - Accents: \hat \tilde \bar \vec \dot over named identifiers
  - Prime and double-prime marks (′ ″) when used as <mo> not inside <msup>
  - Vertical sizing: \Big \Bigg \bigg on brackets

The alttext is the author's original LaTeX — it is ALWAYS correct and
complete. When the two disagree, the alttext wins as ground truth.

Output per equation
-------------------
Each equation record gets an `alttext_diff` dict:
  {
    "alttext":   str,          # the raw LaTeX alttext
    "tokens":    [...],        # recognized math-object tokens from alttext
    "expr_tokens": [...],      # tokens found in the MathML-derived expr
    "missing_from_expr": [...],# in alttext but absent from expr  <- the gap
    "extra_in_expr": [...],    # in expr but not in alttext (usually harmless)
    "gap_categories": [...],   # which symbol classes are missing (Greek, bracket, etc.)
    "scope": str,              # "display_numbered" | "display_unnumbered" | "inline_context"
    "context_role": str | None # for inline: definitional hint from surrounding prose
  }

Inline equations between prose text are flagged as `scope: "inline_context"`.
They are not solver candidates but carry the symbol-definition vocabulary of
the paper — useful for knowing what each Greek/bracket symbol means in context.
"""

from __future__ import annotations
import re
from typing import Any

# ---------------------------------------------------------------------------
# LaTeX token families with their canonical ASCII name used in expr strings
# ---------------------------------------------------------------------------

# Greek letters: \alpha -> alpha, \Gamma -> Gamma, etc.
GREEK_CMD = {
    r"\alpha": "alpha", r"\beta": "beta", r"\gamma": "gamma", r"\delta": "delta",
    r"\epsilon": "epsilon", r"\varepsilon": "epsilon", r"\zeta": "zeta", r"\eta": "eta",
    r"\theta": "theta", r"\vartheta": "theta", r"\iota": "iota", r"\kappa": "kappa",
    r"\lambda": "lambda", r"\mu": "mu", r"\nu": "nu", r"\xi": "xi",
    r"\pi": "pi", r"\varpi": "pi", r"\rho": "rho", r"\varrho": "rho",
    r"\sigma": "sigma", r"\varsigma": "sigma", r"\tau": "tau", r"\upsilon": "upsilon",
    r"\phi": "phi", r"\varphi": "phi", r"\chi": "chi", r"\psi": "psi", r"\omega": "omega",
    r"\Gamma": "Gamma", r"\Delta": "Delta", r"\Theta": "Theta", r"\Lambda": "Lambda",
    r"\Xi": "Xi", r"\Pi": "Pi", r"\Sigma": "Sigma", r"\Upsilon": "Upsilon",
    r"\Phi": "Phi", r"\Psi": "Psi", r"\Omega": "Omega",
}

# Large / big operators: \sum -> Sum, \int -> Integral, etc.
BIG_OPS = {
    r"\sum": "Sum", r"\prod": "Prod",
    r"\int": "Integral", r"\oint": "ContourIntegral",
    r"\iint": "DoubleIntegral", r"\iiint": "TripleIntegral",
    r"\bigcup": "Union", r"\bigcap": "Intersect",
    r"\lim": "Limit", r"\max": "Max", r"\min": "Min",
    r"\sup": "sup", r"\inf": "inf",
    r"\argmax": "argmax", r"\argmin": "argmin",
    r"\limsup": "limsup", r"\liminf": "liminf",
}

# Bracket / norm pairs: left-hand token -> expr marker
BRACKETS = {
    r"\left(": "(", r"\right)": ")", r"\left[": "[", r"\right]": "]",
    r"\left\{": "{", r"\right\}": "}", r"\left|": "|", r"\right|": "|",
    r"\langle": "langle", r"\rangle": "rangle",
    r"\lVert": "lVert", r"\rVert": "rVert",
    r"\lvert": "lvert", r"\rvert": "rvert",
    r"\lfloor": "lfloor", r"\rfloor": "rfloor",
    r"\lceil": "lceil", r"\rceil": "rceil",
    r"\|": "lVert",  # \| usually means \|...\| = double-bar norm
    r"\left\|": "lVert", r"\right\|": "rVert",
    r"\big(": "(", r"\Big(": "(", r"\bigg(": "(", r"\Bigg(": "(",
    r"\big)": ")", r"\Big)": ")", r"\bigg)": ")", r"\Bigg)": ")",
    r"\big[": "[", r"\Big[": "[", r"\bigg[": "[", r"\Bigg[": "[",
    r"\big]": "]", r"\Big]": "]", r"\bigg]": "]", r"\Bigg]": "]",
    r"\big\|": "lVert", r"\Big\|": "lVert", r"\bigg\|": "lVert", r"\Bigg\|": "lVert",
}

# Fraction / division variants -> fraction
FRAC_CMDS = {r"\frac", r"\dfrac", r"\tfrac", r"\cfrac", r"\nicefrac", r"\sfrac"}

# Accent commands: \hat{x} -> x_hat-alike in expr
ACCENTS = {
    r"\hat": "hat", r"\tilde": "tilde", r"\bar": "bar", r"\overline": "bar",
    r"\vec": "vec", r"\dot": "dot", r"\ddot": "ddot", r"\widehat": "hat",
    r"\widetilde": "tilde", r"\acute": "acute", r"\grave": "grave",
    r"\check": "check", r"\breve": "breve", r"\mathring": "ring",
}

# Misc named operators
NAMED_OPS = {
    r"\coloneqq": ":=", r"\defeq": ":=", r"\triangleq": ":=",
    r"\approx": "approx", r"\sim": "sim", r"\simeq": "simeq",
    r"\cong": "cong", r"\equiv": "equiv", r"\propto": "propto",
    r"\neq": "!=", r"\leq": "<=", r"\geq": ">=", r"\ll": "<<", r"\gg": ">>",
    r"\prec": "prec", r"\succ": "succ",
    r"\in": "in", r"\notin": "notin", r"\subset": "subset", r"\supset": "supset",
    r"\subseteq": "subseteq", r"\supseteq": "supseteq",
    r"\pm": "pm", r"\mp": "mp", r"\times": "*", r"\cdot": "*", r"\div": "/",
    r"\infty": "oo", r"\partial": "partial", r"\nabla": "grad",
    r"\sqrt": "sqrt",
    r"\log": "log", r"\ln": "ln", r"\exp": "exp",
    r"\sin": "sin", r"\cos": "cos", r"\tan": "tan",
    r"\mathbb{E}": "E", r"\mathbb{R}": "R", r"\mathbb{N}": "N",
    r"\mathbb{Z}": "Z", r"\mathbb{P}": "P", r"\mathcal{D}": "D",
}

# Prime / superscript operators
PRIME_MARKS = {r"'": "_prime", r"''": "_prime_prime", r"'''": "_prime_prime_prime",
               r"\prime": "_prime", r"\dprime": "_prime_prime"}


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def _latex_tokens(alttext: str) -> list[dict]:
    """
    Extract recognized math-object tokens from a LaTeX alttext string.

    Returns a list of dicts:
      {"kind": "greek"|"bigop"|"bracket"|"frac"|"accent"|"named_op"|"prime"|"identifier"|"number",
       "latex": the raw latex token,
       "name": normalized ASCII name (what expr should contain)}
    """
    if not alttext:
        return []

    tokens = []
    seen_positions = set()

    # Helper: scan for all occurrences of a dict of patterns
    def scan(mapping: dict, kind: str) -> None:
        for pat, name in mapping.items():
            # Escape for regex but keep \\ as literal backslash
            escaped = re.escape(pat)
            for m in re.finditer(escaped, alttext):
                start = m.start()
                if start not in seen_positions:
                    seen_positions.add(start)
                    tokens.append({"kind": kind, "latex": pat, "name": name, "pos": start})

    scan(GREEK_CMD, "greek")
    scan(BIG_OPS, "bigop")
    scan(BRACKETS, "bracket")
    scan(NAMED_OPS, "named_op")
    scan(PRIME_MARKS, "prime")

    # Fraction commands (just presence, not mapping to name)
    for fc in FRAC_CMDS:
        for m in re.finditer(re.escape(fc), alttext):
            start = m.start()
            if start not in seen_positions:
                seen_positions.add(start)
                tokens.append({"kind": "frac", "latex": fc, "name": "frac", "pos": start})

    # Accent commands: record the accent kind
    for ac, aname in ACCENTS.items():
        for m in re.finditer(re.escape(ac) + r"(?:\{([^}]+)\})?", alttext):
            start = m.start()
            if start not in seen_positions:
                seen_positions.add(start)
                inner = m.group(1) or ""
                tokens.append({"kind": "accent", "latex": ac, "name": aname, "inner": inner, "pos": start})

    # Plain identifiers and numbers not already covered
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9]*", alttext):
        start = m.start()
        # Skip if start is right after a backslash (part of a command)
        if start > 0 and alttext[start - 1] == "\\":
            continue
        if start not in seen_positions:
            seen_positions.add(start)
            tokens.append({"kind": "identifier", "latex": m.group(), "name": m.group(), "pos": start})

    for m in re.finditer(r"\d+(?:\.\d+)?", alttext):
        start = m.start()
        if start not in seen_positions:
            seen_positions.add(start)
            tokens.append({"kind": "number", "latex": m.group(), "name": m.group(), "pos": start})

    tokens.sort(key=lambda t: t["pos"])
    return tokens


# ---------------------------------------------------------------------------
# Gap categories
# ---------------------------------------------------------------------------

KIND_CATEGORY = {
    "greek": "Greek letter",
    "bigop": "Large operator (∑ ∫ etc.)",
    "bracket": "Bracket / norm",
    "frac": "Fraction",
    "accent": "Accent (hat, bar, tilde …)",
    "named_op": "Named operator",
    "prime": "Prime mark",
    "identifier": "Plain identifier",
    "number": "Number",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def cross_check(alttext: str, expr: str | None, scope: str, context_role: str | None = None) -> dict:
    """
    Compare alttext tokens against what the MathML walk produced (expr).

    Parameters
    ----------
    alttext : the raw LaTeX alttext from the <math> tag
    expr    : the MathML-derived solver expression (may be None)
    scope   : "display_numbered" | "display_unnumbered" | "inline_context"
    context_role : optional hint inferred from surrounding prose

    Returns
    -------
    dict with keys: alttext, tokens, expr_tokens, missing_from_expr,
                    extra_in_expr, gap_categories, scope, context_role
    """
    tokens = _latex_tokens(alttext)
    expr_lower = (expr or "").lower()

    missing = []
    present = []
    for tok in tokens:
        name = tok["name"].lower()
        # Check if name appears anywhere in expr (substring match, like Stage 1)
        if not name or name in ("", " "):
            continue
        if name in expr_lower or (len(name) > 1 and name[:4] in expr_lower):
            present.append(tok)
        else:
            # Fraction: check for "/"
            if tok["kind"] == "frac" and "/" in expr_lower:
                present.append(tok)
                continue
            # Definition equality: \coloneqq (':=') satisfied by '='
            if tok["name"] == ":=" and "=" in expr_lower:
                present.append(tok)
                continue
            missing.append(tok)

    # Extra tokens in expr not in alttext (usually harmless normalization artifacts)
    # We detect these by finding word-tokens in expr not covered by alttext tokens
    expr_words = set(re.findall(r"[A-Za-z][A-Za-z0-9_]*", expr or ""))
    alttext_names = {t["name"].lower() for t in tokens}
    extra = [w for w in expr_words if w.lower() not in alttext_names and len(w) > 1]

    gap_cats = list({KIND_CATEGORY.get(t["kind"], t["kind"]) for t in missing})

    return {
        "alttext": alttext,
        "tokens": [{"kind": t["kind"], "name": t["name"]} for t in tokens],
        "expr_tokens": list(expr_words),
        "missing_from_expr": [{"kind": t["kind"], "name": t["name"], "latex": t["latex"]} for t in missing],
        "extra_in_expr": extra[:10],  # cap to avoid noise
        "gap_categories": gap_cats,
        "scope": scope,
        "context_role": context_role,
    }


# ---------------------------------------------------------------------------
# Prose-context role detector
# ---------------------------------------------------------------------------

_WHERE_PATTERNS = [
    (re.compile(r"\bwhere\b", re.IGNORECASE), "definitional"),
    (re.compile(r"\bdenotes?\b|\brepresents?\b|\bis defined as\b|\bsuch that\b", re.IGNORECASE), "definitional"),
    (re.compile(r"\bfor example\b|\bfor instance\b|\be\.g\.\b", re.IGNORECASE), "example"),
    (re.compile(r"\brecall\b|\bby definition\b|\bby assumption\b", re.IGNORECASE), "reference"),
    (re.compile(r"\bwe have\b|\bit follows\b|\btherefore\b|\bhence\b", re.IGNORECASE), "derivation"),
    (re.compile(r"\bProposition\b|\bTheorem\b|\bLemma\b|\bCorollary\b", re.IGNORECASE), "theorem"),
]


def infer_context_role(surrounding_text: str) -> str | None:
    """Infer the semantic role of an inline equation from its surrounding prose."""
    for pattern, role in _WHERE_PATTERNS:
        if pattern.search(surrounding_text):
            return role
    return None


# ---------------------------------------------------------------------------
# Convenience: annotate a list of equation records (from extract_equations)
# ---------------------------------------------------------------------------

def annotate_records(records: list[dict]) -> list[dict]:
    """
    Add `alttext_diff` to each equation record in-place.

    Expects records with at least: "latex" (the alttext), "expr", "is_display",
    "eqno" (optional), "context_before", "context_after".
    """
    for rec in records:
        alttext = rec.get("latex") or rec.get("alttext") or ""
        expr = rec.get("expr")
        is_display = rec.get("is_display", False)
        eqno = rec.get("eqno") or rec.get("equation_number")

        if is_display and eqno:
            scope = "display_numbered"
        elif is_display:
            scope = "display_unnumbered"
        else:
            scope = "inline_context"

        ctx_before = rec.get("context_before") or ""
        ctx_after = rec.get("context_after") or ""
        context_role = infer_context_role(ctx_before + " " + ctx_after)

        rec["alttext_diff"] = cross_check(alttext, expr, scope=scope, context_role=context_role)

    return records
