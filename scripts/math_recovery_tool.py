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
    seen = set()

    for math_tag in soup.find_all("math"):
        alttext = math_tag.get("alttext") or ""
        ann = math_tag.find("annotation")
        latex = ann.get_text().strip() if ann else alttext

        # Dedup key prefers the tree expression, falls back to latex
        parser = MathMLParser()
        tree_expr, unsupported = parser.parse(math_tag)

        key = tree_expr if tree_expr else latex
        if not key or len(key) < 2 or key in seen:
            continue
        seen.add(key)

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
    "mathrm", "mathbf", "mathit", "mathsf", "mathtt", "mathcal", "mathbb",
    "mathfrak", "mathscr", "boldsymbol", "operatorname", "mathrm",
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

    # --- Text commands: \text{foo} -> foo
    for cmd in TEXT_CMDS:
        pat = re.compile(r"\\" + cmd + r"\s*\{([^{}]*)\}")
        for _ in range(3):  # nested-ish passes
            s, n = pat.subn(r"\1", s)
            if n == 0:
                break
    s = re.sub(r"\\operatorname\s*\{\s*([a-zA-Z]+)\s*\}", r"\1", s)

    # --- Accents: \hat{x} -> x_hat
    for cmd, tag in ACCENT_CMDS.items():
        pat = re.compile(r"\\" + cmd + r"\s*\{([a-zA-Z0-9]+)\}")
        s = pat.sub(lambda m, t=tag: f"{m.group(1)}_{t}", s)

    # --- Fractions (nested-aware via repeated passes)
    for _ in range(6):
        new = re.sub(r"\\[dtc]?frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"((\1)/(\2))", s)
        if new == s:
            break
        s = new
    for _ in range(3):
        new = re.sub(r"\\binom\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"binomial(\1,\2)", s)
        if new == s:
            break
        s = new

    # --- Roots
    for _ in range(4):
        new = re.sub(r"\\sqrt\s*\[([^\]]+)\]\s*\{([^{}]+)\}", r"((\2)**(1/(\1)))", s)
        if new == s:
            break
        s = new
    for _ in range(4):
        new = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"sqrt(\1)", s)
        if new == s:
            break
        s = new

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

    # --- Sums / products / integrals (with limits -> plain functions)
    s = re.sub(r"\\sum\s*(_[^{}\s]+)?\s*(\^[^{}\s]+)?", "Sum", s)
    s = re.sub(r"\\prod\s*(_[^{}\s]+)?\s*(\^[^{}\s]+)?", "Prod", s)
    s = re.sub(r"\\int\s*(_[^{}\s]+)?\s*(\^[^{}\s]+)?", "Integral", s)
    s = re.sub(r"\\oint\s*(_[^{}\s]+)?\s*(\^[^{}\s]+)?", "Integral", s)
    s = re.sub(r"\\lim\s*(_[^{}\s]+)?", "Limit", s)

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
        s = re.sub(r"\\" + k + r"\b", v, s)
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

    # Must have exactly one top-level '='
    if recovered.count("=") != 1:
        if recovered.count("=") == 0:
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
        is_eq = recovered.count("=") == 1
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
        for eq in data.get("equations", []):
            equations.append({
                "latex": eq.get("latex", ""),
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
            recovered, notes = recover_latex(eq["latex"])
            ok, solution, error, variables, trivial = solve_recovered(recovered, original=eq["latex"])

            has_unknown = any(n.startswith("unknown:") for n in notes)
            if recovered.count("=") == 1 and not has_unknown:
                recoverable += 1
            if ok:
                solved += 1
            else:
                error_hist[error or "unknown"] += 1

            results.append({
                "latex": eq["latex"],
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