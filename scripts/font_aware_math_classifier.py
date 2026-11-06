#!/usr/bin/env python3
"""
Font-Aware Mathematical Classifier & Citation Discriminator

Preserves:
  - Original character code and Unicode representation
  - Font family identification (TeX math fonts: CMMI, CMSY, CMEX, MSBM, etc.)
  - Font-specific glyph interpretation (e.g., CMEX10 'Z' -> \\int)
  - Citation classification features (year patterns, author-year context)

Does NOT globally classify generic ASCII characters as mathematical;
interpretation is strictly conditioned on font family provenance or Unicode semantics.
"""
from __future__ import annotations

import re
from typing import Any

# --- Inherently Mathematical Unicode Characters ---
GREEK = set("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩϕϑϖϱς")
MATH_OPERATORS = set("∫∬∭∮∯∰∑∏∐√∛∜∝∞∂∇±∓×·÷∗∘∙")
MATH_RELATIONS = set("=≠<≤>≥≈≉≡≢∼∾≃≅≊≈≍≎≏∝∈∉∋∌⊂⊃⊆⊇⊄⊅⊈⊉←→⇐⇒↔⇔↦↤")
MATH_DELIMITERS = set("()[]{}⟨⟩⌊⌋⌈⌉‖|")
MATH_PUNCT = set("+-−*/^_:;,'\"`")

MATH_FUNCTION_NAMES = {
    "log", "ln", "exp", "sin", "cos", "tan", "diag", "det",
    "min", "max", "sup", "inf", "lim", "dim", "ker", "var",
    "cov", "tr", "rank", "sign", "KL", "elbo"
}

# --- TeX Font Family Signatures ---
# CMEX: Computer Modern Math Extension (large operators, extensible delimiters)
# CMMI: Computer Modern Math Italic (math variables, lowercase Greek)
# CMSY: Computer Modern Math Symbols (relations, operators, calligraphic)
# MSBM / MSAM: AMS Math Symbols (blackboard bold, special relations)
# EUFM / EURM: Euler Fraktur / Roman
# CMBX: Computer Modern Bold (when used in math lines for bold vectors/matrices)

TEX_MATH_FONT_PREFIXES = (
    "cmex", "cmmi", "cmsy", "msbm", "msam", "eufm", "eurm",
    "bbm", "dsrom", "stmary", "wasy", "math"
)

# CMEX font-specific encodings (TeX 7-bit math extension encoding)
CMEX_INTERPRETATIONS: dict[str, dict[str, str]] = {
    "Z": {"latex": r"\int", "role": "operator_integral", "name": "integral"},
    "R": {"latex": r"\sum", "role": "operator_sum", "name": "summation"},
    "Q": {"latex": r"\prod", "role": "operator_product", "name": "product"},
    "X": {"latex": r"\oint", "role": "operator_contour_integral", "name": "contour_integral"},
    "b": {"latex": r"\bigcap", "role": "operator_intersection", "name": "intersection"},
    "c": {"latex": r"\bigcup", "role": "operator_union", "name": "union"},
    "d": {"latex": r"\bigsqcup", "role": "operator_square_union", "name": "square_union"},
    "e": {"latex": r"\bigvee", "role": "operator_logical_or", "name": "logical_or"},
    "f": {"latex": r"\bigwedge", "role": "operator_logical_and", "name": "logical_and"},
    "g": {"latex": r"\bigodot", "role": "operator_circle_dot", "name": "circle_dot"},
    "h": {"latex": r"\bigotimes", "role": "operator_circle_times", "name": "circle_times"},
    "i": {"latex": r"\bigoplus", "role": "operator_circle_plus", "name": "circle_plus"},
    "j": {"latex": r"\biguplus", "role": "operator_union_plus", "name": "union_plus"},
}

# MSBM blackboard bold interpretations
MSBM_BLACKBOARD_BOLD: dict[str, str] = {
    "R": r"\mathbb{R}",
    "E": r"\mathbb{E}",
    "N": r"\mathbb{N}",
    "Z": r"\mathbb{Z}",
    "C": r"\mathbb{C}",
    "Q": r"\mathbb{Q}",
    "P": r"\mathbb{P}",
    "D": r"\mathbb{D}",
    "H": r"\mathbb{H}",
    "K": r"\mathbb{K}",
}

# --- Citation Regex Patterns ---
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
CITATION_SEMICOLON_RE = re.compile(r"\b(?:19|20)\d{2}\s*;\s*(?:19|20)\d{2}\b")
AUTHOR_YEAR_RE = re.compile(r"([A-Z][a-zA-Z]+(?:\s+et\s+al\.)?)[,\s]+(?:\()?((?:19|20)\d{2})\)?")


def is_math_font(font_name: str | None) -> bool:
    """Return True if font_name belongs to a dedicated mathematical font family."""
    if not font_name:
        return False
    fn_lower = font_name.lower()
    return any(prefix in fn_lower for prefix in TEX_MATH_FONT_PREFIXES)


def classify_glyph(char: str, font_name: str | None, font_size_pt: float = 10.0) -> dict[str, Any]:
    """
    Classify a glyph observation with font awareness.
    Preserves original character, font, and specific interpretation.
    """
    fn = font_name or ""
    fn_lower = fn.lower()

    res: dict[str, Any] = {
        "char": char,
        "font": font_name,
        "font_size_pt": font_size_pt,
        "is_math": False,
        "math_category": "none",
        "latex_interpretation": None,
        "font_family_is_math": is_math_font(font_name),
    }

    # 1. Check font-specific overrides (e.g. CMEX, MSBM)
    if "cmex" in fn_lower and char in CMEX_INTERPRETATIONS:
        interp = CMEX_INTERPRETATIONS[char]
        res["is_math"] = True
        res["math_category"] = "font_specific_operator"
        res["latex_interpretation"] = interp["latex"]
        res["operator_role"] = interp["role"]
        return res

    if "msbm" in fn_lower or "msam" in fn_lower:
        res["is_math"] = True
        res["math_category"] = "blackboard_bold_or_ams_symbol"
        res["latex_interpretation"] = MSBM_BLACKBOARD_BOLD.get(char, f"\\mathbb{{{char}}}")
        return res

    # 2. Check CMMI (Computer Modern Math Italic)
    if "cmmi" in fn_lower:
        res["is_math"] = True
        res["math_category"] = "math_italic_variable"
        res["latex_interpretation"] = char
        return res

    # 3. Check CMSY (Computer Modern Math Symbols)
    if "cmsy" in fn_lower:
        res["is_math"] = True
        res["math_category"] = "math_symbol_or_relation"
        res["latex_interpretation"] = char
        return res

    # 4. Unicode-level inherent mathematics
    if char in GREEK:
        res["is_math"] = True
        res["math_category"] = "greek_letter"
        res["latex_interpretation"] = char
        return res

    if char in MATH_OPERATORS:
        res["is_math"] = True
        res["math_category"] = "math_operator"
        res["latex_interpretation"] = char
        return res

    if char in MATH_RELATIONS:
        res["is_math"] = True
        res["math_category"] = "math_relation"
        res["latex_interpretation"] = char
        return res

    if char in MATH_DELIMITERS:
        res["is_math"] = True
        res["math_category"] = "math_delimiter"
        res["latex_interpretation"] = char
        return res

    if char in MATH_PUNCT:
        res["is_math"] = True
        res["math_category"] = "math_punctuation"
        res["latex_interpretation"] = char
        return res

    if char.isdigit():
        res["is_math"] = True
        res["math_category"] = "numeric_digit"
        res["latex_interpretation"] = char
        return res

    # 5. Non-math character in standard font
    return res


def discriminate_citation(text: str) -> dict[str, Any]:
    """
    Contextual citation discriminator.
    Analyzes whether a string matches bibliographic citation patterns
    rather than mathematical expressions.
    """
    clean_text = text.strip()
    year_matches = YEAR_RE.findall(clean_text)
    has_semicolon = ";" in clean_text
    has_parentheses = ("(" in clean_text and ")" in clean_text) or ("[" in clean_text and "]" in clean_text)
    has_author_year = bool(AUTHOR_YEAR_RE.search(clean_text))
    has_semicolon_years = bool(CITATION_SEMICOLON_RE.search(clean_text))

    # Check for genuine mathematical operators / relations
    has_math_relation = any(r in clean_text for r in "=≠<≤>≥≈∼≡⇔⇒→↦")
    has_math_operator = any(op in clean_text for op in "∫∑∏√∇∂±∓×÷")
    has_greek = any(g in clean_text for g in GREEK)

    citation_score = 0.0
    features = []

    if year_matches:
        citation_score += 0.4
        features.append(f"year_matches:{year_matches}")
    if has_semicolon_years or (has_semicolon and year_matches):
        citation_score += 0.3
        features.append("semicolon_year_pattern")
    if has_author_year:
        citation_score += 0.3
        features.append("author_year_pattern")
    if has_parentheses and year_matches:
        citation_score += 0.2
        features.append("parenthesized_year")

    # Penalize if genuine mathematical relations or operators are present
    if has_math_relation or has_math_operator or has_greek:
        citation_score = max(0.0, citation_score - 0.6)
        features.append("penalized_due_to_math_operators")

    is_citation = citation_score >= 0.5

    return {
        "text": text,
        "is_citation_candidate": is_citation,
        "citation_confidence": round(min(1.0, citation_score), 3),
        "citation_features": features,
        "has_math_operators": has_math_relation or has_math_operator or has_greek,
    }

