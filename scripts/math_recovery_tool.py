"""
Math Recovery Tool
==================
Combines arxiv HTML extraction + bracket/command dictionary + equation recovery + solving.

Pipeline:
  1. FETCH   - pull arxiv HTML (MathML + LaTeX annotations)
  2. EXTRACT - get every equation with its exact LaTeX (brackets intact)
  3. LEARN   - build a command dictionary from actual usage in the corpus
  4. RECOVER - convert LaTeX to solver form using learned definitions
  5. SOLVE   - attempt solution, report honestly
  6. REPORT  - per-paper stats + aggregate recovery rate

No fabrication. Every number comes from real execution.

Usage:
  python math_recovery_tool.py --arxiv 1406.2661
  python math_recovery_tool.py --batch 1406.2661 2006.11239 --output-dir DATASETS/math_recovery
  python math_recovery_tool.py --corpus DATASETS/arxiv_html_corpus
"""
import json, os, re, sys, argparse
import urllib.request
from pathlib import Path
from collections import Counter, defaultdict

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from pylatexenc.latex2text import LatexNodes2Text
    HAS_PYLATEXENC = True
except ImportError:
    HAS_PYLATEXENC = False

TRANSFORMS = standard_transformations + (implicit_multiplication_application,)
HTML_BASE = "https://arxiv.org/html/"
USER_AGENT = "math-recovery-tool/1.0"


# ============================================================================
# LAYER 1: FETCH
# ============================================================================

def fetch_arxiv_html(arxiv_id, timeout=30):
    """Fetch HTML version of an arxiv paper."""
    url = f"{HTML_BASE}{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), url
    except Exception as e:
        print(f"  [FETCH] failed {url}: {e}")
        return None, url


# ============================================================================
# LAYER 2: EXTRACT
# ============================================================================

def extract_equations(html, arxiv_id=None, display_only=False):
    """
    Extract every equation with exact LaTeX from arxiv HTML.

    Primary path: walk the MathML tree (structured, correct grouping).
    Fallback path: LaTeX annotation string (when tree walk fails).

    display_only=True restricts to COMPLETE display equations
    (tr.ltx_equation rows), skipping inline fragments. This is the path
    to complete formulas rather than sub-expression fragments.

    Each result carries BOTH:
      - 'expr': tree-derived solver expression
      - 'latex': original LaTeX (for provenance/audit)
    """
    if not HAS_BS4:
        raise RuntimeError("beautifulsoup4 required: pip install beautifulsoup4")

    from mathml_parser import MathMLParser

    # --- DISPLAY-ONLY PATH: complete formulas from ltx_equation rows
    if display_only:
        from display_equation_extractor import parse_display_equations
        parsed = parse_display_equations(html, MathMLParser)

        # Join continuation rows: a row whose expr starts with '=' continues
        # the previous row in the same equation group (multi-line derivations).
        joined = []
        last_by_group = {}
        for row in parsed:
            expr = row.get("expr")
            if not expr:
                continue
            gid = row.get("group_id")
            if expr.lstrip().startswith("=") and gid in last_by_group:
                prev = last_by_group[gid]
                prev["expr"] = prev["expr"] + expr
                prev["joined_rows"] = prev.get("joined_rows", 1) + 1
                continue
            row["joined_rows"] = 1
            joined.append(row)
            last_by_group[gid] = row

        equations = []
        for row in joined:
            equations.append({
                "latex": row["expr"],          # solver expr doubles as source here
                "expr": row["expr"],
                "tree_unsupported": row.get("unsupported", []),
                "context_before": "",
                "context_after": "",
                "is_display": True,
                "eqno": row.get("eqno"),
                "group_id": row.get("group_id"),
                "row_index": row.get("row_index"),
                "is_multiline_group": row.get("is_multiline_group", False),
                "joined_rows": row.get("joined_rows", 1),
                "source": "display_equation",
            })
        return equations

    # --- ALL-MATH PATH (inline + display)
    soup = BeautifulSoup(html, "html.parser")
    equations = []

    # OCCURRENCE IDENTITY (2026-10-07).
    #
    # This previously deduped by CONTENT (`key = tree_expr or latex; if key in
    # seen: continue`). On 2605.00155 that discarded 340 of 991 occurrences:
    # the paper uses `\ell_{1}` 25 times, `\delta` 20 times, and so on. The
    # recovery files therefore contained 651 records for 991 source equations.
    #
    # Consequence: "651 matched" never meant 651 of 991 occurrences were
    # handled — it meant 651 unique STRINGS were represented. Any per-occurrence
    # question ("did occurrence #417 regress while #691 did not?") was
    # unanswerable, and aggregate rates were computed over a silently reduced
    # denominator.
    #
    # The witness needs a LOCATION dimension. Every <math> tag is now recorded
    # with its document order, and duplicates are preserved. A content hash is
    # kept so duplicates remain GROUPABLE without being COLLAPSED.
    import hashlib

    for occ_index, math_tag in enumerate(soup.find_all("math")):
        alttext = math_tag.get("alttext") or ""
        ann = math_tag.find("annotation")
        latex = ann.get_text().strip() if ann else alttext

        parser = MathMLParser()
        tree_expr, unsupported = parser.parse(math_tag)

        key = tree_expr if tree_expr else latex
        if not key or len(key) < 2:
            continue

        content_sha = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

        # Context: nearest sibling text
        ctx_before = ""
        ctx_after = ""
        prev = math_tag.find_previous_sibling()
        nxt = math_tag.find_next_sibling()
        if prev:
            ctx_before = prev.get_text(" ", strip=True)[:200]
        if nxt:
            ctx_after = nxt.get_text(" ", strip=True)[:200]

        # Display detection: arxiv sets display="inline" always; the real
        # signal is an ancestor tr.ltx_equation / ltx_eqn_row.
        is_display = False
        for anc in math_tag.parents:
            cls = anc.get("class") or []
            if any("ltx_equation" in c or "ltx_eqn_row" in c for c in cls):
                is_display = True
                break

        equations.append({
            "latex": latex,
            "expr": tree_expr,
            "tree_unsupported": unsupported,
            # --- occurrence identity: the witness has a LOCATION dimension.
            # `occurrence` is document order across ALL <math> tags (stable
            # across runs for a fixed paper version). `content_sha` lets
            # duplicates be GROUPED without being COLLAPSED.
            "occurrence": occ_index,
            "content_sha": content_sha,
            "context_before": ctx_before,
            "context_after": ctx_after,
            "is_display": is_display,
            "source": "mathml_tree" if tree_expr else "latex_fallback",
        })

    return equations


# ============================================================================
# LAYER 3: LEARN  (command + bracket dictionary from real usage)
# ============================================================================

# Bracket-ish commands we track. Learned counts come from the corpus itself.
BRACKET_FAMILIES = {
    "round":       ["(", ")"],
    "square":      ["[", "]"],
    "curly":       ["{", "}"],
    "angle":       ["\\langle", "\\rangle"],
    "floor":       ["\\lfloor", "\\rfloor"],
    "ceil":        ["\\lceil", "\\rceil"],
    "bar":         ["|", "\\lvert", "\\rvert"],
    "double_bar":  ["\\|", "\\lVert", "\\rVert"],
    "auto_left":   ["\\left"],
    "auto_right":  ["\\right"],
    "big":         ["\\big", "\\Big", "\\bigg", "\\Bigg", "\\bigl", "\\bigr", "\\Bigl", "\\Bigr"],
    "brace_ext":   ["\\overbrace", "\\underbrace"],
    "arrow_ext":   ["\\overrightarrow", "\\overleftarrow", "\\overleftrightarrow", "\\underrightarrow"],
    "accent_ext":  ["\\widehat", "\\widetilde", "\\overline", "\\underline"],
}


def learn_dictionary(equations):
    """
    Build a command dictionary from ACTUAL usage across the corpus.
    Returns: {command: count}, {family: count}, {family: sample_latex}
    """
    cmd_counts = Counter()
    family_counts = Counter()
    family_samples = defaultdict(list)

    for eq in equations:
        latex = eq["latex"]

        # Every backslash command
        for m in re.finditer(r"\\[a-zA-Z]+", latex):
            cmd_counts[m.group(0)] += 1

        # Bracket families
        for family, tokens in BRACKET_FAMILIES.items():
            for tok in tokens:
                if tok.startswith("\\"):
                    n = latex.count(tok)
                else:
                    n = latex.count(tok)
                if n:
                    family_counts[family] += n
                    if len(family_samples[family]) < 5:
                        family_samples[family].append(latex[:160])

    return dict(cmd_counts), dict(family_counts), {k: v for k, v in family_samples.items()}


# ============================================================================
# LAYER 4: RECOVER  (LaTeX -> solver form, bracket-aware)
# ============================================================================

# Learned/default command definitions. Order matters: multi-char before single.
TEXT_CMDS = [
    "text", "mbox", "textrm", "textbf", "textit", "texttt", "textsf",
    "textup", "textnormal", "textsc", "textsl", "textmd", "textsuperscript",
    "mathrm", "mathbf", "mathit", "mathsf", "mathtt", "mathcal", "mathbb",
    "mathfrak", "mathscr", "boldsymbol", "bm", "operatorname", "mathnormal",
]

ACCENT_CMDS = {
    "widehat": "hat", "widetilde": "tilde", "overline": "bar", "underline": "under",
    "overrightarrow": "vec", "overleftarrow": "vec", "overleftrightarrow": "vec",
    "hat": "hat", "bar": "bar", "vec": "vec", "dot": "dot", "ddot": "ddot",
    "tilde": "tilde", "check": "check", "breve": "breve", "acute": "acute", "grave": "grave",
}

OPERATOR_MAP = {
    "\\cdot": "*", "\\times": "*", "\\div": "/", "\\ast": "*", "\\star": "*",
    "\\oplus": "+", "\\ominus": "-", "\\otimes": "*", "\\odot": "*",
    "\\pm": "+", "\\mp": "-", "\\circ": "*", "\\bullet": "*",
    "\\wedge": "*", "\\vee": "+", "\\cap": "*", "\\cup": "+",
}

RELATION_MAP = {
    "\\leq": "<=", "\\geq": ">=", "\\neq": "!=", "\\approx": "=", "\\equiv": "=",
    "\\sim": "=", "\\simeq": "=", "\\cong": "=", "\\propto": "=", "\\ll": "<",
    "\\gg": ">", "\\subset": "=", "\\supset": "=",
    "\\subseteq": "=", "\\supseteq": "=",
    "\\Rightarrow": "=", "\\Leftarrow": "=",
    "\\Leftrightarrow": "=", "\\rightarrow": "=", "\\leftarrow": "=", "\\mapsto": "=",
    "\\to": "=", "\\gets": "=", "\\implies": "=", "\\iff": "=",
}

# Relations that are NOT equations. Mapping these to '=' fabricates equations
# that do not exist in the paper. They are membership/set relations.
NON_EQUATION_RELATIONS = {
    "\\in", "\\notin", "\\ni", "\\forall", "\\exists", "\\mid",
}

# ---------------------------------------------------------------------------
# ZERO-ARG COMMANDS (measured 2026-10-07 from the arxiv HTML corpus)
#
# These take NO brace argument. Leaving them to the generic fallback either
# drops them (losing the operator) or fuses the following token. Each entry is
# a (pattern, replacement) applied in order.
#
# Evidence:
#   N_{\rm H}        -> 'N_ H'    fused the subscript token
#   a\cdots b        -> 'a*s b'   ellipsis became a multiplication
#   f^{\prime}       -> 'f**()'   empty exponent, derivative marker destroyed
#   v_{\perp}        -> 'v_'      subscript destroyed
#   A^{\dagger}      -> 'A**()'   conjugate marker destroyed
#   x\uparrow 0      -> 'x 0'     limit relation destroyed
# ---------------------------------------------------------------------------
ZERO_ARG_RULES = [
    # --- font switches: \rm \bf \it take no argument and switch font for the
    #     REST of the group. They are presentation only, so they are removed
    #     with NO replacement — not even a space. Leaving a space caused the
    #     subscript token to split:  N_{\rm H} -> 'N_ H' instead of 'N_H'.
    (r"\\(rm|bf|it|sf|tt|cal|frak)\b", ""),
    # --- ellipses: a punctuation token, not an operator
    (r"\\(ldots|dots|cdots|vdots|ddots)\b", " ... "),
    # --- limit arrows: a relation, keep it visible
    (r"\\uparrow\b", "->"),
    (r"\\downarrow\b", "->"),
    (r"\\updownarrow\b", "->"),
    # --- binary relations / operators
    (r"\\triangleright\b", ">"),
    (r"\\triangleleft\b", "<"),
    (r"\\lesssim\b", "<="),
    (r"\\gtrsim\b", ">="),
    (r"\\succ\b", ">"),
    (r"\\prec\b", "<"),
    (r"\\succsim\b", ">="),
    (r"\\precsim\b", "<="),
    (r"\\Longleftrightarrow\b", "="),
    (r"\\longleftrightarrow\b", "="),
    # --- degree / markers
    (r"\\textdegree\b", " "),
    (r"\\degree\b", " "),
    (r"\\checkmark\b", " "),
    # --- structural symbols that must become named tokens, not vanish
    (r"\\emptyset\b", "emptyset"),
    (r"\\infty\b", "oo"),
    # --- colour: \color[rgb]{r,g,b} is presentation only; drop the spec
    (r"\\color\s*\[[^\]]*\]\s*\{[^{}]*\}", " "),
    (r"\\color\s*\{[^{}]*\}", " "),
]

# ---------------------------------------------------------------------------
# SUPERSCRIPT MARKERS — commands valid only as a superscript. They must become
# a NAMED exponent, never an empty group. Measured damage:
#   f^{\prime}   -> 'f**()'   (derivative destroyed)
#   A^{\dagger}  -> 'A**()'   (conjugate destroyed)
# ---------------------------------------------------------------------------
SUPERSCRIPT_MARKERS = {
    "prime": "prime",
    "dagger": "dag",
    "ddagger": "ddag",
    "ast": "ast",
    "star": "star",
    "perp": "perp",
    "top": "top",
    "bot": "bot",
    "circ": "circ",
    "bullet": "bullet",
    "flat": "flat",
    "natural": "natural",
    "sharp": "sharp",
}

FUNC_MAP = {
    "sin": "sin", "cos": "cos", "tan": "tan", "cot": "cot", "sec": "sec", "csc": "csc",
    "arcsin": "asin", "arccos": "acos", "arctan": "atan",
    "sinh": "sinh", "cosh": "cosh", "tanh": "tanh", "coth": "coth",
    "log": "log", "ln": "log", "exp": "exp",
    "det": "det", "dim": "dim", "min": "Min", "max": "Max",
    "sup": "sup", "inf": "inf", "arg": "arg", "gcd": "gcd", "lcm": "lcm",
}

GREEK_MAP = {
    "\\alpha": "alpha", "\\beta": "beta", "\\gamma": "gamma", "\\delta": "delta",
    "\\epsilon": "epsilon", "\\varepsilon": "epsilon", "\\zeta": "zeta", "\\eta": "eta",
    "\\theta": "theta", "\\vartheta": "theta", "\\iota": "iota", "\\kappa": "kappa",
    "\\lambda": "lambda", "\\mu": "mu", "\\nu": "nu", "\\xi": "xi",
    "\\pi": "pi", "\\varpi": "pi", "\\rho": "rho", "\\varrho": "rho",
    "\\sigma": "sigma", "\\varsigma": "sigma", "\\tau": "tau", "\\upsilon": "upsilon",
    "\\phi": "phi", "\\varphi": "phi", "\\chi": "chi", "\\psi": "psi", "\\omega": "omega",
    "\\Gamma": "Gamma", "\\Delta": "Delta", "\\Theta": "Theta", "\\Lambda": "Lambda",
    "\\Xi": "Xi", "\\Pi": "Pi", "\\Sigma": "Sigma", "\\Upsilon": "Upsilon",
    "\\Phi": "Phi", "\\Psi": "Psi", "\\Omega": "Omega",
    "\\infty": "oo", "\\partial": "d", "\\nabla": "grad", "\\ell": "l",
    "\\mathbb{E}": "E", "\\mathbb{R}": "R", "\\mathbb{N}": "N", "\\mathbb{Z}": "Z",
}

# Environments that mean "this is a system / matrix" -> not single-equation solvable
STRUCTURAL_ENVS = [
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "cases", "array", "aligned", "align", "gathered", "gather", "split",
    "subarray", "smallmatrix", "equation", "multline",
]


def _brace_scan(s, start):
    """
    From index `start` (which must point at '{'), return (inner, end_index)
    where end_index is the index just past the balancing '}'.

    Returns (None, start) if no group opens at `start`.
    """
    if start >= len(s) or s[start] != "{":
        return None, start
    depth = 0
    k = start
    while k < len(s):
        if s[k] == "{":
            depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:k], k + 1
        k += 1
    return None, start


def _apply_command(s, cmd, nargs, fn, max_passes=8):
    """
    Apply `fn(*args)` to every `\\cmd{...}{...}` occurrence, matching to the
    BALANCING brace rather than using a [^{}]+ regex.

    This is the structural fix: real LaTeX arguments nest, so any regex that
    excludes braces cannot match them. `fn` receives the raw inner strings and
    returns the replacement.

    If fn returns None the occurrence is left untouched.
    """
    marker = "\\" + cmd
    for _ in range(max_passes):
        out = []
        i = 0
        changed = False
        while i < len(s):
            if s.startswith(marker, i):
                after = i + len(marker)
                # must not be followed by another letter (avoid \frac vs \fracfoo)
                if after < len(s) and s[after].isalpha():
                    out.append(s[i])
                    i += 1
                    continue
                pos = after
                while pos < len(s) and s[pos].isspace():
                    pos += 1
                args = []
                ok = True
                for _a in range(nargs):
                    inner, pos2 = _brace_scan(s, pos)
                    if inner is None:
                        ok = False
                        break
                    args.append(inner)
                    pos = pos2
                    while pos < len(s) and s[pos].isspace():
                        pos += 1
                if ok:
                    rep = fn(*args)
                    if rep is not None:
                        out.append(rep)
                        i = pos
                        changed = True
                        continue
            out.append(s[i])
            i += 1
        s = "".join(out)
        if not changed:
            break
    return s


def count_equalities(expr):
    """
    Count TRUE equality operators in a recovered expression.

    `expr.count("=")` is WRONG: the relation tokens contain '=' as a substring
    ('~=' contains '='), so relations were miscounted as equations. v13's
    'recoverable' figure was inflated by 78 such cases.

    A true equality is an '=' that is NOT part of a longer relation token.
    """
    if not expr:
        return 0
    # strip known multi-char relation tokens first
    cleaned = expr
    for tok in ("~=", "!=", "<=", ">=", "=>", "<=>", "<->", "|->", "_eq_"):
        cleaned = cleaned.replace(tok, "\x00")
    # also strip the typed relation tokens (they never contain '=' but be safe)
    for tok in ("sim", "approx", "simeq", "cong", "asymp", "propto",
                "equiv", "prec", "succ"):
        cleaned = re.sub(r"\b" + tok + r"\b", "\x00", cleaned)
    return cleaned.count("=")


def recover_latex(latex):
    """
    Convert a LaTeX equation into a solver-ready string.
    Bracket-aware: preserves structure, defines commands rather than stripping blind.

    Returns (recovered_string, notes_list).
    """
    s = latex.strip()
    notes = []

    # --- Strip display wrappers
    s = re.sub(r"\\displaystyle", "", s)
    s = re.sub(r"\\textstyle", "", s)
    s = re.sub(r"\\scriptstyle", "", s)

    # --- Environments
    env_found = []
    for env in STRUCTURAL_ENVS:
        if f"\\begin{{{env}}}" in s:
            env_found.append(env)
    if env_found:
        notes.append(f"env:{','.join(env_found)}")
    s = re.sub(r"\\begin\{[^}]+\}", "", s)
    s = re.sub(r"\\end\{[^}]+\}", "", s)

    # --- Multi-line breaks
    s = s.replace("\\\\", " ")
    s = s.replace("\\cr", " ")

    # --- Auto-sizing delimiters: \left( -> (  \right) -> )
    #     Must handle \left\langle, \left\|, \left\{ etc.
    s = re.sub(r"\\left\s*\\\{", "(", s)
    s = re.sub(r"\\right\s*\\\}", ")", s)
    s = re.sub(r"\\left\s*\\\|", "|", s)
    s = re.sub(r"\\left\s*\\\|", "|", s)
    s = re.sub(r"\\left\s*\\langle", "(", s)
    s = re.sub(r"\\right\s*\\rangle", ")", s)
    s = re.sub(r"\\left\s*\\lfloor", "floor(", s)
    s = re.sub(r"\\right\s*\\rfloor", ")", s)
    s = re.sub(r"\\left\s*\\lceil", "ceil(", s)
    s = re.sub(r"\\right\s*\\rceil", ")", s)
    s = re.sub(r"\\left\s*\\lvert", "|", s)
    s = re.sub(r"\\right\s*\\rvert", "|", s)
    s = re.sub(r"\\left\s*\\lVert", "|", s)
    s = re.sub(r"\\right\s*\\rVert", "|", s)
    # plain \left( etc
    s = re.sub(r"\\left\s*", "", s)
    s = re.sub(r"\\right\s*", "", s)
    # bare angle/floor/ceil
    s = s.replace("\\langle", "(").replace("\\rangle", ")")
    s = s.replace("\\lfloor", "floor(").replace("\\rfloor", ")")
    s = s.replace("\\lceil", "ceil(").replace("\\rceil", ")")
    s = s.replace("\\lvert", "|").replace("\\rvert", "|")
    s = s.replace("\\lVert", "|").replace("\\rVert", "|")

    # --- Sizing commands (no semantic content)
    s = re.sub(r"\\(bigg|Bigg|bigl|bigr|Bigl|Bigr|big|Big)\s*", "", s)
    s = re.sub(r"\\big[lr]?", "", s)
    s = re.sub(r"\\Big[lr]?", "", s)

    # --- Extended braces: \overbrace{x}^{label} -> (x)   \underbrace{x}_{label} -> (x)
    s = re.sub(r"\\overbrace\s*\{", "(", s)
    s = re.sub(r"\\underbrace\s*\{", "(", s)

    # --- Escaped characters: \_ \& \% \# \$ are LITERAL characters, not
    # commands. arxiv emits them inside \text{} for identifiers like
    # \mathcal{L}_{text\_aux}. If \_ survives it reaches Python as a
    # line-continuation and the whole equation is lost.
    #   \text\_aux  ->  text_aux   (one identifier, not an operator)
    s = s.replace("\\_", "_")
    s = s.replace("\\&", "&")
    s = s.replace("\\%", "%")
    s = s.replace("\\#", "#")
    s = s.replace("\\$", "$")
    s = s.replace("\\{", "{").replace("\\}", "}")
    # Collapse a subscript marker that is now adjacent to a literal underscore,
    # so `text_\_aux` style output does not become `text__aux`.
    s = re.sub(r"__+", "_", s)

    # --- Math-mode delimiters ($ ... $) are presentation-only and carry no
    # mathematical meaning. arxiv emits unit exponents as \mbox{ cm${}^{-2}$};
    # if the $ survives it reaches Python as a syntax error and the entire
    # equation is lost. There was previously NO $ handling at all.
    if "$" in s:
        s = s.replace("$", "")
        notes.append("stripped math-mode $ delimiters")
    # Collapse empty brace groups ({}) left behind by the removal above, so
    # that {}^{-2} becomes ^{-2} and the superscript rule can read it.
    if "{}" in s:
        s = s.replace("{}", "")

    # --- Text commands: \text{foo} -> foo, BRACE-AWARE.
    #
    # NOTE: a trailing '*' is the starred form (\operatorname*{ess sup}) and
    # must be consumed, or it is left behind as a multiplication operator:
    #   \operatorname*{ess\,sup}  ->  '*(ess sup)'    WRONG
    marker_suffix = "*"
    #
    # The previous implementation used \{([^{}]*)\}, which cannot match a
    # nested group. \mbox{ cm${}^{-2}$} therefore never matched and the literal
    # token \mbox survived into the solver. This scanner matches to the
    # balancing close brace instead.
    #
    # The `{` requirement after the command name is what stops \text from
    # matching inside \textbf: after "text" comes "bf", not "{", so the scan
    # skips ahead rather than consuming it.
    for cmd in TEXT_CMDS:
        marker = "\\" + cmd
        search_from = 0
        while True:
            i = s.find(marker, search_from)
            if i < 0:
                break
            j = i + len(marker)
            while j < len(s) and s[j].isspace():
                j += 1
            # consume a starred form: \operatorname*{...}
            if j < len(s) and s[j] == "*":
                j += 1
                while j < len(s) and s[j].isspace():
                    j += 1
            if j >= len(s) or s[j] != "{":
                # not this command (e.g. \textbf seen while scanning \text)
                search_from = i + len(marker)
                continue
            depth = 0
            k = j
            while k < len(s):
                if s[k] == "{":
                    depth += 1
                elif s[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            if k >= len(s):
                break  # unbalanced braces; leave the remainder alone
            inner = s[j + 1:k]
            s = s[:i] + inner + s[k + 1:]
            search_from = i  # re-scan: inner may contain further commands
    s = re.sub(r"\\operatorname\s*\{\s*([a-zA-Z]+)\s*\}", r"\1", s)

    # --- Superscript markers: \prime \dagger etc. must become a NAMED
    # exponent. Without this, f^{\prime} -> f**() and the derivative is lost.
    for _name, _tag in SUPERSCRIPT_MARKERS.items():
        s = re.sub(r"\^\s*\{\s*\\" + _name + r"\s*\}", "**(" + _tag + ")", s)
        s = re.sub(r"\^\s*\\" + _name + r"\b", "**(" + _tag + ")", s)

    # --- Subscript markers: the SAME commands appear as subscripts and would
    # otherwise be destroyed. v_{\perp} -> 'v_' loses the marker entirely.
    for _name, _tag in SUPERSCRIPT_MARKERS.items():
        s = re.sub(r"_\s*\{\s*\\" + _name + r"\s*\}", "_" + _tag, s)
        s = re.sub(r"_\s*\\" + _name + r"\b", "_" + _tag, s)

    # --- Zero-arg commands: font switches, ellipses, arrows, markers.
    # Must run BEFORE the generic leftover handler, otherwise these either
    # vanish silently or fuse the following token.
    for _pat, _rep in ZERO_ARG_RULES:
        s = re.sub(_pat, _rep, s)

    # --- Accents: \hat{x} -> x_hat. The argument may itself be a
    # backslash-command (\hat{\mu}, \dot{\nu}) — the old [a-zA-Z0-9]+ pattern
    # rejected those and the literal command survived as "unknown".
    # Command args are stripped of their backslash so the accent fuses into a
    # single identifier: \hat{\mu} -> mu_hat.
    #
    # Accents ACCUMULATE: \bar{\hat{r}} must give r_hat_bar, not r_hat.
    # Run repeated passes so an inner accent resolves before the outer one.
    #
    # The replacement is SPACE-PADDED. Without it the accent fuses with a
    # preceding command name and destroys it:
    #   \log\bar{\pi}  ->  '\log' + 'pi_bar'  =  '\logpi_bar'
    #   then \b fails (next char 'p' is a word char), \log is never matched as
    #   a function, and the generic handler deletes '\logpi' as an unknown
    #   command -> '_bar'.  The logarithm was silently destroyed.
    def _accent_sub(m, tag):
        inner = m.group(1).strip()
        if inner.startswith("\\"):
            inner = re.sub(r"^\\+", "", inner)
        inner = inner.replace("\\", "")
        return f" {inner}_{tag} "

    for _pass in range(4):
        before = s
        for cmd, tag in ACCENT_CMDS.items():
            # The argument may contain SPACES introduced by an inner accent
            # that already resolved: \bar{\hat{r}} -> \bar{ r_hat }.
            # A pattern excluding whitespace cannot match that and \bar
            # survives to be reported unknown.
            pat = re.compile(r"\\" + cmd + r"\s*\{([a-zA-Z0-9_\s\\]+)\}")
            s = pat.sub(lambda m, t=tag: _accent_sub(m, t), s)
        if s == before:
            break

    # --- Fractions / roots / binomials / set-operators: BALANCING-BRACE.
    #
    # These previously used [^{}]+ regexes, which cannot match a nested
    # argument. \frac{u^{(k)}}{x} and \frac{\operatorname{sgn}((e_k-\pi)_j)}{...}
    # therefore failed and the literal \frac survived into the solver.
    # _apply_command matches to the balancing brace instead.
    s = _apply_command(s, "frac", 2, lambda a, b: f"(({a})/({b}))")
    s = _apply_command(s, "dfrac", 2, lambda a, b: f"(({a})/({b}))")
    s = _apply_command(s, "tfrac", 2, lambda a, b: f"(({a})/({b}))")
    s = _apply_command(s, "cfrac", 2, lambda a, b: f"(({a})/({b}))")
    s = _apply_command(s, "binom", 2, lambda a, b: f"binomial({a},{b})")
    s = _apply_command(s, "sqrt", 1, lambda a: f"sqrt({a})")
    # roots with an explicit index: \sqrt[3]{x} -> (x)**(1/(3))
    # Do this as a single balancing-brace pass so the body may nest.
    def _sqrt_indexed(s_):
        marker = "\\sqrt"
        out = []
        i = 0
        changed = False
        while i < len(s_):
            if s_.startswith(marker, i):
                after = i + len(marker)
                pos = after
                while pos < len(s_) and s_[pos].isspace():
                    pos += 1
                if pos < len(s_) and s_[pos] == "[":
                    close = s_.find("]", pos)
                    if close > 0:
                        idx = s_[pos + 1:close]
                        p2 = close + 1
                        while p2 < len(s_) and s_[p2].isspace():
                            p2 += 1
                        body, end = _brace_scan(s_, p2)
                        if body is not None:
                            out.append(f"(({body})**(1/({idx})))")
                            i = end
                            changed = True
                            continue
            out.append(s_[i])
            i += 1
        return "".join(out), changed
    for _ in range(4):
        s, _ch = _sqrt_indexed(s)
        if not _ch:
            break
    # \underset / \overset: keep the BASE, drop the annotation
    s = _apply_command(s, "underset", 2, lambda a, b: f"({b})")
    s = _apply_command(s, "overset", 2, lambda a, b: f"({b})")
    s = _apply_command(s, "stackrel", 2, lambda a, b: f"({b})")
    # \mathop{\mathrm{arg\,max}}_{...} -> argmax
    s = _apply_command(s, "mathop", 1, lambda a: f"({a})")

    # --- Named operators that take no brace argument.
    # \max \min \sup \Pr \det \gcd etc. are function names, not commands to
    # delete. Dropping them loses the operator (max_{x} f -> _x f).
    #
    # NOTE: \b does NOT work here. '_' is a word character, so in `\max_{x}`
    # there is no word boundary after "max" and the pattern never fires.
    # Use a negative lookahead for a letter instead.
    for _op in ("max", "min", "sup", "inf", "argmax", "argmin"):
        _rep = _op.capitalize() if _op in ("max", "min") else _op
        s = re.sub(r"\\" + _op + r"(?![a-zA-Z])", _rep, s)
    s = re.sub(r"\\Pr(?![a-zA-Z])", "Pr", s)
    s = re.sub(r"\\det(?![a-zA-Z])", "det", s)
    s = re.sub(r"\\gcd(?![a-zA-Z])", "gcd", s)
    s = re.sub(r"\\lcm(?![a-zA-Z])", "lcm", s)

    # --- Norms: \| ... \|  and  \lVert ... \rVert
    # \| survives as a backslash and reaches Python as an error.
    s = s.replace("\\lVert", "||").replace("\\rVert", "||")
    s = s.replace("\\lvert", "|").replace("\\rvert", "|")
    s = s.replace("\\|", "||")
    s = s.replace("\\Vert", "||").replace("\\vert", "|")

    # --- Sums / products / integrals: drop the limits, keep the operator name.
    #
    # MUST run BEFORE the generic sub/superscript pass. That pass unbraces
    # `_{...}` into `_...`, after which the limits are indistinguishable from
    # ordinary arithmetic and leak into the expression:
    #     \sum_{\ell=1}^{G}  ->  'Sum=1**(G)'   and left a stray ')' behind.
    #
    # The original patterns were `(_[^{}\s]+)?(\^[^{}\s]+)?`, which cannot
    # match a braced limit at all. That left `_{\ell=1}^{G}` in the stream,
    # the brace cleanup turned it into `(ell=1)^(G)`, and equations ended with
    # UNBALANCED PARENS:
    #     \frac{a}{\sum_{k=1}^{K}b}  ->  '((a)/(Sum'    <- 1 unclosed '('
    # which turned 9 previously-solvable equations into TokenErrors.
    def _bigop(s_, cmd, name):
        marker = "\\" + cmd
        out = []
        i = 0
        while i < len(s_):
            if s_.startswith(marker, i):
                after = i + len(marker)
                if after < len(s_) and s_[after].isalpha():
                    out.append(s_[i])
                    i += 1
                    continue
                pos = after
                # consume up to two limits, braced or bare
                for _lim in range(2):
                    p = pos
                    while p < len(s_) and s_[p].isspace():
                        p += 1
                    if p < len(s_) and s_[p] in "_^":
                        p += 1
                        while p < len(s_) and s_[p].isspace():
                            p += 1
                        if p < len(s_) and s_[p] == "{":
                            _inner, end = _brace_scan(s_, p)
                            if _inner is not None:
                                pos = end
                                continue
                        # bare limit: one token, stopping at any delimiter
                        # ('{' included, so we never swallow a group opener)
                        start = p
                        while p < len(s_) and s_[p] not in " \t\n,;{)}]":
                            p += 1
                        if p > start:
                            pos = p
                            continue
                        pos = p + 1
                        continue
                    break
                out.append(name)
                i = pos
                continue
            out.append(s_[i])
            i += 1
        return "".join(out)

    for _cmd, _name in (("sum", "Sum"), ("prod", "Prod"), ("int", "Integral"),
                        ("oint", "Integral"), ("iint", "Integral"),
                        ("lim", "Limit"), ("bigcup", "Union"), ("bigcap", "Intersect")):
        s = _bigop(s, _cmd, _name)

    # --- Superscripts / subscripts
    for _ in range(4):
        new = re.sub(r"\^\s*\{([^{}]+)\}", r"**(\1)", s)
        if new == s:
            break
        s = new
    s = re.sub(r"\^\s*([a-zA-Z0-9])", r"**\1", s)
    for _ in range(4):
        new = re.sub(r"_\s*\{([^{}]+)\}", r"_\1", s)
        if new == s:
            break
        s = new

    # --- Operators / relations / functions
    for k, v in OPERATOR_MAP.items():
        s = s.replace(k, v)
    for k, v in RELATION_MAP.items():
        s = s.replace(k, v)
    # Membership/set relations: remove them (they are not equations and
    # mapping them to '=' fabricates equations the paper never wrote)
    for k in NON_EQUATION_RELATIONS:
        s = s.replace(k, " ")
    for k, v in FUNC_MAP.items():
        # (?![a-zA-Z]) not \b: after "log" in "\log_2" or "\logpi" the next
        # char is a word char, so \b never fires and the function is missed.
        s = re.sub(r"\\" + k + r"(?![a-zA-Z])", v, s)

    # --- Function application: join a function name to its argument.
    # An accent replacement is space-padded, which can leave
    #     log pi_bar (y)
    # Python then reads `log` as a Symbol and `pi_bar` as another, producing a
    # TYPE error (Symbol * Symbol) rather than a clean application.
    # Join `fname arg` -> `fname(arg)` for known function names only.
    _FUNCS = ("log", "exp", "sin", "cos", "tan", "asin", "acos", "atan",
              "sinh", "cosh", "tanh", "sqrt", "abs", "det", "Min", "Max")
    for _fn in _FUNCS:
        # fname <space> <identifier-or-paren-group>
        s = re.sub(r"\b" + _fn + r"\s+([A-Za-z_][A-Za-z0-9_]*(?:\([^()]*\))?)",
                   _fn + r"(\1)", s)
        # fname <space> (expr)
        s = re.sub(r"\b" + _fn + r"\s+\(", _fn + "(", s)
        # fname(...) <space> (y)  ->  fname(..., y)
        # The argument may already be parenthesised, so a following group is
        # an ADDITIONAL argument, not a detached product:
        #   log(pi_bar) (y)  ->  log(pi_bar, y)
        # The existing group's OUTER parens are stripped so we do not produce
        # log((pi_bar), y).
        def _join_paren(m, _f=_fn):
            first = m.group(1)[1:-1]
            return f"{_f}({first}, {m.group(2)})"
        s = re.sub(r"\b" + _fn + r"(\([^()]*\))\s+\(([^()]*)\)", _join_paren, s)
        # fname(...) <space> identifier  ->  fname(..., identifier)
        def _join_ident(m, _f=_fn):
            first = m.group(1)[1:-1]
            return f"{_f}({first}, {m.group(2)})"
        s = re.sub(r"\b" + _fn + r"(\([^()]*\))\s+([A-Za-z_][A-Za-z0-9_]*)",
                   _join_ident, s)
    for k, v in GREEK_MAP.items():
        s = s.replace(k, v)

    # --- Spacing / punctuation commands
    s = re.sub(r"\\[,;:!>]", " ", s)
    s = re.sub(r"\\quad|\\qquad|\\;|\\,|\\!|\\ ", " ", s)
    s = s.replace("\\coloneqq", "=").replace("\\coloneq", "=")
    s = s.replace("\\vphantom{", "(").replace("\\phantom{", "(")
    s = s.replace("\\bigl", "").replace("\\bigr", "")

    # --- Remaining unknown commands: record them, then drop the backslash (keep arg)
    leftovers = set(re.findall(r"\\[a-zA-Z]+", s))
    if leftovers:
        notes.append("unknown:" + ",".join(sorted(leftovers)[:6]))
    s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", "", s)

    # --- Final brace cleanup
    s = s.replace("{", "(").replace("}", ")")

    # --- Subscript/superscript space repair.
    # Removing a zero-arg font switch inside a subscript leaves a gap:
    #   N_{\rm H}  ->  N_\rm H  ->  N_ H
    # A space directly after _ or ^ is never valid math, so re-join it.
    s = re.sub(r"_\s+([A-Za-z0-9])", r"_\1", s)
    s = re.sub(r"\^\s+([A-Za-z0-9])", r"^\1", s)
    # An accent replacement is space-padded to protect a preceding command
    # name (\log\bar{\pi} -> 'log pi_bar'). That padding must not split an
    # identifier from its subscript: 'alpha_bar _t' -> 'alpha_bar_t'.
    s = re.sub(r"([A-Za-z0-9])\s+(_[A-Za-z0-9])", r"\1\2", s)
    # Same hazard from a dropped command inside a group: "( x)" -> "(x)".
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    # A subscript left with nothing after it (v_) is a lost marker, not math.
    s = re.sub(r"[_^]\s*(?=[,)\]}])", "", s)

    s = re.sub(r"\s+", " ", s).strip()

    return s, notes


# ============================================================================
# LAYER 5: SOLVE
# ============================================================================

def _extract_symbols(expr_str):
    """
    Classify identifiers in an expression.

    Returns (names, funcnames):
      names     -> multi-letter identifiers to bind as single Symbols
                   ('DeltaW' is ONE symbol, not D*e*l*t*a*W)
      funcnames -> identifiers immediately followed by '(' or '[' — these are
                   function applications (E_q[...], N(x,mu,sigma)) and must be
                   bound as sympy.Function, not Symbol.
    """
    # Function names must never be bound as symbols
    func_names = set(FUNC_MAP.values()) | {
        "sin", "cos", "tan", "cot", "sec", "csc", "asin", "acos", "atan",
        "sinh", "cosh", "tanh", "coth", "log", "exp", "sqrt", "Abs",
        "Min", "Max", "Sum", "Prod", "Integral", "Limit", "binomial",
        "floor", "ceil", "det", "diag", "grad",
    }
    names = set()
    funcnames = set()

    for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]*)\s*([\(\[])?", expr_str):
        tok = m.group(1)
        following = m.group(2)
        if not tok:
            continue
        if tok in func_names:
            continue
        if following in ("(", "["):
            # identifier applied to arguments -> a function
            funcnames.add(tok)
            continue
        if len(tok) < 2:
            continue
        names.add(tok)

    # A name that is also applied is a function, never a symbol
    names -= funcnames
    return names, funcnames


def _repair_token_boundaries(expr):
    """
    Fix token gluing and non-SymPy tokens introduced by the MathML walk.

    Problems seen in real arxiv MathML:
      'SumD_KL(...)'   -> 'Sum' + 'D_KL' glued  -> 'Sum*D_KL(...)'
      'logp(...)'      -> 'log' + 'p' glued     -> 'log*p(...)'
      'wheremu_t(...)' -> prose 'where' glued to a symbol
      ':='             -> assignment, means '='
      '[a;b;c]'        -> column-vector notation, not a Python list
      'and'/'or'       -> logical words inside formulas
    """
    if not expr:
        return expr

    # ':=' / '≔' are definitions -> '='
    expr = expr.replace(":=", "=")

    # Column-vector / stacked notation: [a;b;c] -> a*b*c is wrong;
    # it is a vector literal. Represent as a bracketed product-free tuple
    # by joining with '*_' is wrong too. Use (a, b, c) so SymPy sees a tuple,
    # which the caller flattens to its first component.
    def _brackets_to_tuple(m):
        inner = m.group(1)
        parts = [p.strip().strip("*") for p in inner.split(";") if p.strip().strip("*")]
        if not parts:
            return "0"
        return "(" + ",".join(parts) + ")"

    for _ in range(3):
        new = re.sub(r"\[([^\[\]]*;[^\[\]]*)\]", _brackets_to_tuple, expr)
        if new == expr:
            break
        expr = new

    # Empty separators left by the walk: ';;' or ',,' -> single
    expr = re.sub(r";\s*;", ";", expr)
    expr = re.sub(r",\s*,", ",", expr)
    expr = expr.replace(";", ",")

    # Prose words that are not math
    for word in ["where", "such_that", "subject_to", "and", "or", "for", "with"]:
        expr = re.sub(rf"\b{word}\b", "", expr)

    # Known keywords that must be separated from what follows
    keywords = ["Sum", "Prod", "Integral"]
    for kw in keywords:
        expr = re.sub(rf"\b{kw}(?=[A-Za-z])", kw + "*", expr)

    # 'log'/'ln'/'exp'/'sqrt' immediately followed by an identifier
    for fn in ["log", "ln", "exp", "sqrt", "sin", "cos", "tan", "min", "max"]:
        expr = re.sub(rf"\b{fn}(?=[A-Za-z])", fn + "*", expr)

    # Dangling relational operators (from truncated/continuation rows):
    # 'X*<' or 'X <' at the end carries no meaning for solving.
    expr = re.sub(r"[*+\-/]\s*[<>]=?\s*$", "", expr)
    expr = re.sub(r"\s*[<>]=?\s*$", "", expr)
    # Leading relational operators
    expr = re.sub(r"^\s*[<>]=?\s*[*+\-/]?", "", expr)

    # Star immediately before a relation: 'A*<=B' -> 'A<=B'
    expr = re.sub(r"\*\s*([<>]=?)", r"\1", expr)

    # Curly braces are not Python grouping: {a,b} -> (a,b)
    expr = expr.replace("{", "(").replace("}", ")")

    # Star at the start of a group: '(*(G))' -> '((G))'  (starred-expr artifact)
    expr = re.sub(r"\(\s*\*", "(", expr)
    expr = re.sub(r"(\w)\s*\*\s*\(", r"\1*(", expr)

    # Trailing dot / star-dot from sentence punctuation inside math
    expr = re.sub(r"[\*\.]+\s*$", "", expr)
    expr = re.sub(r"^\s*[\*\.]+", "", expr)

    # Trailing/leading stray operators
    expr = re.sub(r"[\*\+\-/=,]\s*$", "", expr)
    expr = re.sub(r"^\s*[\*\+\-/,]", "", expr)

    # NOTE: do NOT collapse '**' here. '**' is exponentiation and collapsing it
    # to '*' silently changes meaning (sigma_t**2 -> sigma_t*2). Only runs of
    # three-or-more stars are artifacts.

    # Clean repeated operators
    expr = re.sub(r"\*{3,}", "*", expr)
    expr = re.sub(r"\s+", " ", expr)

    return expr.strip()


def _normalize_function_brackets(expr, funcnames):
    """
    Convert square-bracket function application to parentheses.

    'E_q[...]' -> 'E_q(...)'   (sympy Functions do not support [] application)
    Only applies to identifiers known to be functions in this expression.
    """
    if not expr or not funcnames:
        return expr
    for fn in sorted(funcnames, key=len, reverse=True):
        # fn[ ... ]  ->  fn( ... )   with balanced-bracket matching
        out = []
        i = 0
        n = len(expr)
        while i < n:
            if expr.startswith(fn, i):
                j = i + len(fn)
                # allow optional space then '['
                k = j
                while k < n and expr[k] == " ":
                    k += 1
                if k < n and expr[k] == "[":
                    # find matching ']'
                    depth = 0
                    m = k
                    while m < n:
                        if expr[m] == "[":
                            depth += 1
                        elif expr[m] == "]":
                            depth -= 1
                            if depth == 0:
                                break
                        m += 1
                    if m < n:
                        inner = expr[k + 1:m]
                        out.append(fn + "(" + inner + ")")
                        i = m + 1
                        continue
            out.append(expr[i])
            i += 1
        expr = "".join(out)
    return expr


def _normalize_pipes(expr):
    """
    Replace math '|' with a SymPy-safe token.

    '|' in math is ambiguous. Classify each occurrence by its neighbours:

      ABS OPENER   preceded by '(' '[' '=' '+' '-' '*' '/' ',' or start
      ABS CLOSER   followed by ')' ']' '=' '+' '-' '*' '/' ',' or end
      SEPARATOR    anything else  -> conditional  p(x|y)  ->  p(x,y)

    Then pair each opener with the next closer at the same bracket depth.

    This correctly separates:
      D_KL(q(x_T)|p(x_T))            -> separator (prev char ')')
      (|mu_t(x_t,x_0)-mu_theta|)**2 -> Abs opener/closer (prev '(' / next ')')
      q(x_t-1|x_t)                   -> separator (prev '1', next 'x')
    """
    if not expr or "|" not in expr:
        return expr

    n = len(expr)

    def classify(i):
        prev = expr[i - 1] if i > 0 else ""
        nxt = expr[i + 1] if i + 1 < n else ""
        opener_prev = prev in "([{=+-*/," or prev == ""
        closer_next = nxt in ")]}=+-*/," or nxt == ""
        if opener_prev and not closer_next:
            return "open"
        if closer_next and not opener_prev:
            return "close"
        if opener_prev and closer_next:
            # both -> prefer close (end of an Abs group)
            return "close"
        return "sep"

    kinds = {}
    for i, c in enumerate(expr):
        if c == "|":
            kinds[i] = classify(i)

    # Pair openers with the next unpaired closer (by position)
    result = list(expr)
    pipe_positions = sorted(kinds)
    stack = []
    for i in pipe_positions:
        k = kinds[i]
        if k == "open":
            stack.append(i)
        elif k == "close" and stack:
            o = stack.pop()
            result[o] = "\x00"   # marker: Abs opener
            result[i] = "\x01"   # marker: Abs closer
        # else: separator, leave as '|'

    s = "".join(result)
    s = s.replace("\x00", "Abs(").replace("\x01", ")")
    s = s.replace("|", ",")
    return s


# Markup command names that must NEVER survive as symbols in a translation.
# If one appears, the translation corrupted the original math.
MARKUP_LEAK_TOKENS = {
    "mathbf", "mathbb", "mathcal", "mathrm", "mathit", "mathsf", "mathtt",
    "mathfrak", "mathscr", "boldsymbol", "text", "mbox", "textrm", "textbf",
    "textit", "texttt", "operatorname", "displaystyle", "textstyle",
    "bar", "hat", "vec", "dot", "ddot", "tilde", "widehat", "widetilde",
    "overline", "underline", "overrightarrow", "overleftarrow",
    "left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr",
    "frac", "dfrac", "tfrac", "binom", "coloneqq", "eqqcolon",
    "langle", "rangle", "lfloor", "rfloor", "lceil", "rceil", "lVert", "rVert",
    "qquad", "quad", "hspace", "vspace", "vphantom", "phantom", "limits",
    "substack", "mathop", "mathbin", "mathrel", "overset", "underset",
    "color", "textcolor", "tiny", "small", "large", "huge",
}

# Tokens that LOOK like markup but are legitimate emitted functions.
# They must be exempt or every radical/text-labelled answer is falsely rejected.
LEAK_EXEMPT = {
    "sqrt", "text",   # sqrt(a) is a real function; 'text' appears in subscripts
}


def _markup_leak(expr):
    """
    Return the set of markup tokens that leaked into the expression as symbols.

    A translation that contains these has CORRUPTED the original math: the
    markup became a variable. Empty set means the translation is clean.
    """
    if not expr:
        return set()
    found = set()
    for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]*)\b", expr):
        tok = m.group(1)
        low = tok.lower()
        if low in LEAK_EXEMPT:
            continue
        if low in MARKUP_LEAK_TOKENS:
            found.add(tok)
    return found


def _structure_preserved(original, translated):
    """
    Cheap structural preservation check between the source math and the
    translation. Catches translations that silently dropped a whole side.

    Returns (ok, reason).
    """
    if not translated or len(translated) < 3:
        return False, "translation_empty"

    # If the source states a relation, the translation must keep one.
    src_has_eq = ("=" in original) or ("\\coloneqq" in original) or (":=" in original)
    if src_has_eq and translated.count("=") == 0:
        return False, "relation_dropped"

    # Length collapse: translation an order of magnitude shorter than source
    # means content was silently discarded.
    if len(original) > 30 and len(translated) < len(original) / 6:
        return False, "content_collapsed"

    return True, None


def solve_recovered(recovered, original=None):
    """
    Attempt to solve a recovered expression string.

    original: the source math (LaTeX or tree expr) this was translated from.
    When supplied, the translation must PRESERVE the original math:
      - no markup token may survive as a symbol
      - a stated relation must not be dropped
      - content must not silently collapse
    A translation failing preservation is rejected, never reported as a solve.

    Key correctness rule: multi-letter identifiers are bound as SINGLE symbols
    via local_dict. Without this, SymPy's implicit multiplication splits
    'DeltaW' into D*e*l*t*a*W and reports a garbage "solution".

    Returns (success, solution_str_or_None, error_or_None, variables).
    """
    if not recovered or len(recovered) < 3:
        return False, None, "empty", [], False

    # --- PRESERVATION GATE -------------------------------------------------
    # The translation must carry the original math, not corrupt it.
    leak = _markup_leak(recovered)
    if leak:
        return False, None, f"markup_leaked:{','.join(sorted(leak))}", [], False

    if original is not None:
        ok_struct, reason = _structure_preserved(original, recovered)
        if not ok_struct:
            return False, None, f"not_preserved:{reason}", [], False

    # Normalize math tokens that are not valid Python/SymPy
    recovered = _repair_token_boundaries(recovered)
    recovered = _normalize_pipes(recovered)

    # --- RELATION GUARD ----------------------------------------------------
    # If the expression contains a non-equality relation, it is NOT an
    # equation. Solving 'lhs = rhs' on a relation fabricates a conclusion the
    # paper never made (x ~ q(x) is not x = q(x); the false answer was [0]).
    # Report the relation honestly and refuse to solve it.
    try:
        from mathml_parser import NON_EQUALITY_TOKENS as _REL_TOKENS
    except Exception:
        _REL_TOKENS = set()
    for tok in sorted(_REL_TOKENS, key=len, reverse=True):
        # word tokens need boundaries; symbol tokens do not
        if tok.isalpha():
            hit = re.search(rf"\b{re.escape(tok)}\b", recovered)
        else:
            hit = tok in recovered
        if hit:
            return False, None, f"not_an_equation:relation:{tok}", [], False

    # Must have exactly one top-level '='
    if count_equalities(recovered) != 1:
        if count_equalities(recovered) == 0:
            return False, None, "no_equality", [], False
        # Chained equality a = b = c: reduce to the FIRST relation a = b,
        # which is a real, solvable relation the paper states.
        parts = [p.strip() for p in recovered.split("=")]
        if len(parts) >= 3 and parts[0] and parts[1]:
            recovered = f"{parts[0]}={parts[1]}"
            chain_reduced = True
        else:
            return False, None, "multiple_equalities", [], False
    else:
        chain_reduced = False

    lhs, rhs = [p.strip() for p in recovered.split("=")]
    if not lhs or not rhs:
        return False, None, "empty_side", [], False

    # Bind multi-letter identifiers as single symbols, and applied identifiers
    # as sympy Functions (E_q[...], N(x,mu,sigma) are calls, not products).
    names, funcnames = _extract_symbols(recovered)

    # Square-bracket application is not valid for sympy Functions:
    #   E_q[...] -> E_q(...)
    recovered = _normalize_function_brackets(recovered, funcnames)
    lhs, rhs = [p.strip() for p in recovered.split("=")]

    local_dict = {}
    for name in names:
        local_dict[name] = sympy.Symbol(name)
    # Sum/Prod/Integral are bound operators in our expressions; when they appear
    # as a multiplied atom (Sum*D_KL) they must be Symbols, not sympy classes.
    for op in ("Sum", "Prod", "Integral", "Limit"):
        local_dict.setdefault(op, sympy.Symbol(op))
    for fname in funcnames:
        try:
            local_dict[fname] = sympy.Function(fname)
        except Exception:
            local_dict[fname] = sympy.Symbol(fname)

    try:
        lhs_expr = parse_expr(lhs, transformations=TRANSFORMS, local_dict=dict(local_dict))
        rhs_expr = parse_expr(rhs, transformations=TRANSFORMS, local_dict=dict(local_dict))
    except Exception as e:
        return False, None, f"parse:{type(e).__name__}", [], False

    # parse_expr can return a Python tuple when the expression is comma-separated
    # at top level (e.g. "a, b"). A tuple is not a sympy expression and has no
    # free_symbols; take the first element, which is the primary relation value.
    if isinstance(lhs_expr, tuple):
        lhs_expr = lhs_expr[0] if lhs_expr else sympy.Integer(0)
    if isinstance(rhs_expr, tuple):
        rhs_expr = rhs_expr[0] if rhs_expr else sympy.Integer(0)

    try:
        variables = sorted(lhs_expr.free_symbols | rhs_expr.free_symbols, key=lambda v: str(v))
    except Exception as e:
        return False, None, f"vars:{type(e).__name__}", [], False

    if not variables:
        return False, None, "no_variables", [], False

    # Prefer the variable that appears on the left (the "subject")
    try:
        lhs_vars = sorted(lhs_expr.free_symbols, key=lambda v: str(v))
    except Exception:
        lhs_vars = variables
    target = lhs_vars[0] if lhs_vars else variables[0]

    try:
        sol = sympy.solve(sympy.Eq(lhs_expr, rhs_expr), target)
    except Exception as e:
        return False, None, f"solve:{type(e).__name__}", [str(v) for v in variables], False

    if not sol:
        return False, None, "no_solution", [str(v) for v in variables], False

    solution_str = str(sol)

    # --- VERIFICATION GATE: reject fabricated solutions -----------------
    # A real solution must not introduce symbols that were not in the equation.
    # Function names emitted by SymPy (sqrt, Abs, sin, ...) are not symbols and
    # must be exempt, or every radical answer is falsely rejected.
    SOLUTION_FUNCS = {
        "sqrt", "Abs", "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan", "sinh", "cosh", "tanh", "coth",
        "log", "exp", "Min", "Max", "Sum", "Prod", "Integral", "Limit",
        "binomial", "floor", "ceil", "re", "im", "arg", "conjugate",
    }
    input_chars = set(recovered)
    sol_identifiers = set(re.findall(r"[A-Za-z]+", solution_str))
    for ident in sol_identifiers:
        if ident in SOLUTION_FUNCS:
            continue
        if ident in {"I", "E", "oo", "nan", "zoo", "pi"}:
            continue
        # Any letter in the answer must appear in the source equation
        for ch in ident:
            if ch not in input_chars:
                return False, None, "fabricated_solution", [str(v) for v in variables], False

    # Reject trivial identity echo (solve returned the equation itself)
    if solution_str.replace(" ", "") == lhs.replace(" ", ""):
        return False, None, "identity_echo", [str(v) for v in variables], False

    # NOTE: a solution equal to the RHS of "X = <expr>" is CORRECT, just trivial
    # (the variable was already isolated). It is not fabrication and must not be
    # rejected. Callers can filter on the 'trivial' flag if they want only
    # non-trivial derivations.
    trivial = solution_str.strip("[] ").replace(" ", "") == rhs.replace(" ", "")

    return True, solution_str, None, [str(v) for v in variables], trivial


# ============================================================================
# LAYER 6: REPORT
# ============================================================================

def process_paper(arxiv_id, output_dir=None, verbose=True, display_only=False):
    """Full pipeline for one paper."""
    if verbose:
        print(f"\n{'='*70}")
        print(f"PAPER {arxiv_id}{'  [DISPLAY-ONLY]' if display_only else ''}")
        print(f"{'='*70}")

    html, url = fetch_arxiv_html(arxiv_id)
    if not html:
        return {"arxiv_id": arxiv_id, "status": "fetch_failed", "url": url}

    equations = extract_equations(html, arxiv_id, display_only=display_only)
    if verbose:
        print(f"  [EXTRACT] {len(equations)} unique equations")

    cmd_counts, family_counts, family_samples = learn_dictionary(equations)
    if verbose:
        print(f"  [LEARN]   {len(cmd_counts)} unique commands, {len(family_counts)} bracket families")

    results = []
    solved = 0
    recoverable = 0
    error_hist = Counter()
    strategy_hist = Counter()

    for eq in equations:
        # PATH A: tree-derived expression (preferred - already structured)
        tree_expr = eq.get("expr")
        if tree_expr:
            recovered = tree_expr
            notes = ["path:tree"]
            if eq.get("tree_unsupported"):
                notes.extend(eq["tree_unsupported"])
        else:
            # PATH B: regex recovery from LaTeX (fallback)
            recovered, notes = recover_latex(eq["latex"])
            notes = ["path:latex_fallback"] + notes

        ok, solution, error, variables, trivial = solve_recovered(recovered, original=eq["latex"])

        # Count as "recoverable" if it converted to something parseable-looking
        # (i.e. has an '=' and no unknown-command residue)
        has_unknown = any(n.startswith("unknown:") for n in notes)
        is_eq = count_equalities(recovered) == 1
        if is_eq and not has_unknown:
            recoverable += 1

        if ok:
            solved += 1
            strategy_hist["solved"] += 1
            if trivial:
                strategy_hist["trivial"] += 1
            else:
                strategy_hist["nontrivial"] += 1
        else:
            error_hist[error or "unknown"] += 1

        results.append({
            "latex": eq["latex"],
            "occurrence": eq.get("occurrence"),
            "content_sha": eq.get("content_sha"),
            "recovered": recovered,
            "notes": notes,
            "is_display": eq["is_display"],
            "solvable": ok,
            "trivial": trivial,
            "solution": solution,
            "error": error,
            "variables": variables,
            "context_before": eq["context_before"],
            "context_after": eq["context_after"],
        })

    stats = {
        "arxiv_id": arxiv_id,
        "url": url,
        "status": "ok",
        "total_equations": len(equations),
        "recoverable": recoverable,
        "solvable": solved,
        "solvable_pct": round(100.0 * solved / len(equations), 2) if equations else 0.0,
        "recoverable_pct": round(100.0 * recoverable / len(equations), 2) if equations else 0.0,
        "unique_commands": len(cmd_counts),
        "bracket_families": family_counts,
        "top_commands": dict(Counter(cmd_counts).most_common(25)),
        "errors": dict(error_hist.most_common(20)),
    }

    if verbose:
        print(f"  [RECOVER] {recoverable}/{len(equations)} recovered with '=' and no unknown cmds")
        print(f"  [SOLVE]   {solved}/{len(equations)} solved ({stats['solvable_pct']}%)")
        if error_hist:
            top = ", ".join(f"{k}={v}" for k, v in error_hist.most_common(5))
            print(f"  [ERRORS]  {top}")

    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / f"{arxiv_id}_recovery.json", "w", encoding="utf-8") as f:
            json.dump({"stats": stats, "results": results}, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"  [SAVE]    {out / f'{arxiv_id}_recovery.json'}")

    return {"stats": stats, "results": results}


def process_corpus(corpus_dir, output_dir=None):
    """Process an existing corpus of arxiv HTML JSON files."""
    corpus = Path(corpus_dir)
    if not corpus.exists():
        print(f"Corpus not found: {corpus_dir}")
        return []

    all_stats = []
    for jf in sorted(corpus.glob("*.json")):
        try:
            with open(jf, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  skip {jf.name}: {e}")
            continue

        arxiv_id = data.get("arxiv_id", jf.stem)
        equations = []
        for _pos, eq in enumerate(data.get("equations", [])):
            # PATH A: re-derive the tree expression from the STORED MathML.
            #
            # This loader previously dropped `mathml` entirely, so PATH A
            # could never run on the corpus and every equation fell through
            # to regex-on-LaTeX — discarding the placement data (munder,
            # msubsup, mrow nesting) that MathML already encodes.
            tree_expr = None
            tree_unsupported = []
            mml = eq.get("mathml")
            if mml and HAS_BS4:
                try:
                    from mathml_parser import MathMLParser as _MMLP
                    _soup = BeautifulSoup(mml, "html.parser")
                    _mt = _soup.find("math")
                    if _mt is not None:
                        _p = _MMLP()
                        tree_expr, tree_unsupported = _p.parse(_mt)
                except Exception:
                    tree_expr = None

            equations.append({
                "latex": eq.get("latex", ""),
                "expr": tree_expr,
                "tree_unsupported": tree_unsupported,
                # Preserve occurrence identity from the corpus file when
                # present; otherwise use document order so every occurrence
                # remains a separate witness.
                "occurrence": eq.get("occurrence", _pos),
                "content_sha": eq.get("content_sha"),
                "context_before": eq.get("context_before", ""),
                "context_after": eq.get("context_after", ""),
                "is_display": eq.get("is_display", False),
                "source": eq.get("source", "corpus"),
            })

        if not equations:
            continue

        cmd_counts, family_counts, _ = learn_dictionary(equations)

        solved = 0
        recoverable = 0
        error_hist = Counter()
        results = []

        for eq in equations:
            # PATH A: tree-derived expression from MathML (preferred).
            # This loop previously ALWAYS used recover_latex, so the corpus
            # run never exercised the structural path even when the MathML
            # tree was available.
            tree_expr = eq.get("expr")
            if tree_expr:
                recovered = tree_expr
                notes = ["path:tree"]
                if eq.get("tree_unsupported"):
                    notes.extend(eq["tree_unsupported"])
            else:
                recovered, notes = recover_latex(eq["latex"])
                notes = ["path:latex_fallback"] + notes

            ok, solution, error, variables, trivial = solve_recovered(recovered, original=eq["latex"])

            has_unknown = any(n.startswith("unknown:") for n in notes)
            if count_equalities(recovered) == 1 and not has_unknown:
                recoverable += 1
            if ok:
                solved += 1
            else:
                error_hist[error or "unknown"] += 1

            results.append({
                "latex": eq["latex"],
                "occurrence": eq.get("occurrence"),
                "content_sha": eq.get("content_sha"),
                "recovered": recovered,
                "notes": notes,
                "solvable": ok,
                "trivial": trivial,
                "solution": solution,
                "error": error,
                "variables": variables,
            })

        stats = {
            "arxiv_id": arxiv_id,
            "status": "ok",
            "total_equations": len(equations),
            "recoverable": recoverable,
            "solvable": solved,
            "solvable_pct": round(100.0 * solved / len(equations), 2),
            "recoverable_pct": round(100.0 * recoverable / len(equations), 2),
            "unique_commands": len(cmd_counts),
            "bracket_families": family_counts,
            "errors": dict(error_hist.most_common(15)),
        }
        all_stats.append({"stats": stats, "results": results})

        print(f"  {arxiv_id}: {solved}/{len(equations)} solved ({stats['solvable_pct']}%) "
              f"| {recoverable} recoverable ({stats['recoverable_pct']}%)")

        if output_dir:
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            with open(out / f"{arxiv_id}_recovery.json", "w", encoding="utf-8") as f:
                json.dump({"stats": stats, "results": results}, f, indent=2, ensure_ascii=False)

    return all_stats


def aggregate_report(all_stats, output_dir=None):
    """Aggregate honest totals across papers."""
    if not all_stats:
        print("No stats to aggregate.")
        return None

    total_eq = sum(s["stats"]["total_equations"] for s in all_stats)
    total_solved = sum(s["stats"]["solvable"] for s in all_stats)
    total_recoverable = sum(s["stats"]["recoverable"] for s in all_stats)

    # Merge bracket families
    fam = Counter()
    for s in all_stats:
        for k, v in s["stats"].get("bracket_families", {}).items():
            fam[k] += v

    # Merge errors
    err = Counter()
    for s in all_stats:
        for k, v in s["stats"].get("errors", {}).items():
            err[k] += v

    agg = {
        "papers": len(all_stats),
        "total_equations": total_eq,
        "recoverable": total_recoverable,
        "recoverable_pct": round(100.0 * total_recoverable / total_eq, 2) if total_eq else 0.0,
        "solvable": total_solved,
        "solvable_pct": round(100.0 * total_solved / total_eq, 2) if total_eq else 0.0,
        "bracket_families": dict(fam.most_common()),
        "top_errors": dict(err.most_common(20)),
        "per_paper": [
            {
                "arxiv_id": s["stats"]["arxiv_id"],
                "total": s["stats"]["total_equations"],
                "recoverable": s["stats"]["recoverable"],
                "solvable": s["stats"]["solvable"],
                "solvable_pct": s["stats"]["solvable_pct"],
            }
            for s in all_stats
        ],
    }

    # trivial vs non-trivial split (counted from result records)
    total_trivial = 0
    total_nontrivial = 0
    for s in all_stats:
        for r in s.get("results", []):
            if r.get("solvable"):
                if r.get("trivial"):
                    total_trivial += 1
                else:
                    total_nontrivial += 1
    agg["trivial_solutions"] = total_trivial
    agg["nontrivial_solutions"] = total_nontrivial

    print(f"\n{'='*70}")
    print("AGGREGATE RECOVERY REPORT")
    print(f"{'='*70}")
    print(f"Papers:                {agg['papers']}")
    print(f"Total equations:       {agg['total_equations']}")
    print(f"Recoverable (has '='): {agg['recoverable']} ({agg['recoverable_pct']}%)")
    print(f"Solvable by SymPy:     {agg['solvable']} ({agg['solvable_pct']}%)")
    print(f"  - non-trivial solves: {total_nontrivial}")
    print(f"  - trivial (isolated): {total_trivial}")
    print(f"\nBracket family usage across corpus:")
    for k, v in agg["bracket_families"].items():
        print(f"  {k:14s} {v}")
    print(f"\nTop errors:")
    for k, v in list(agg["top_errors"].items())[:12]:
        print(f"  {k:40s} {v}")

    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "aggregate_report.json", "w", encoding="utf-8") as f:
            json.dump(agg, f, indent=2, ensure_ascii=False)
        print(f"\nSaved: {out / 'aggregate_report.json'}")

    return agg


# ============================================================================
# CLI
# ============================================================================

def main():
    ap = argparse.ArgumentParser(description="Math Recovery Tool (arxiv HTML -> recovered -> solved)")
    ap.add_argument("--arxiv", nargs="+", help="arxiv IDs to fetch and process")
    ap.add_argument("--corpus", help="Directory of existing arxiv HTML JSON files")
    ap.add_argument("--output-dir", default="DATASETS/math_recovery", help="Output directory")
    ap.add_argument("--display-only", action="store_true",
                    help="Only complete display equations (ltx_equation rows), skip inline fragments")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    all_stats = []

    if args.arxiv:
        for aid in args.arxiv:
            res = process_paper(aid, args.output_dir, verbose=not args.quiet,
                                display_only=args.display_only)
            if "stats" in res:
                all_stats.append(res)

    if args.corpus:
        print(f"\nProcessing corpus: {args.corpus}")
        all_stats.extend(process_corpus(args.corpus, args.output_dir))

    if not args.arxiv and not args.corpus:
        ap.print_help()
        return

    aggregate_report(all_stats, args.output_dir)


if __name__ == "__main__":
    main()