"""Multimodal Mathematical PDF Recovery Engine (V2.3 Comprehensive).

Fuses multi-channel physical evidence to recover mathematical formulas across pages:
  - Channel 1: Font Layout Stream (TeX font families: CMBX, CMMIB, CMMI, CMSY, CMEX, MSBM)
  - Channel 2: Vector Path Geometry (horizontal fraction rules and radical vinculums)
  - Channel 3: High-Resolution Raster Visible Ink (GLEA 20x zoom, delimiter feet, descender whitespace purge)
  - Channel 4: Macro Candidate Proposal & Spatial Grammar (display, clustered quad, inline, metric)

Ensures:
  - Delimiters (tall vs short, extensible parentheses, brackets, braces, determinant bars)
  - Glyph formatting (bold vectors, bold Greek, math italics, blackboard bold, transpose, accents, sub/superscripts)
  - Diverse math contexts (display equations, multi-expression lines with quad separation, inline math in prose)
  - Structural reconstruction (LaTeX and Presentation MathML)
  - Canonical Typed AST extraction (via structural_ast_extractor)
  - Independent Gate D4 physical clearance verification (anti-override guarantee)
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

import pymupdf

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from structural_ast_extractor import extract_structural_ast, ExprNode
from v2_3_glyph_evidence_adjudicator import GlyphEvidenceAdjudicator
from font_aware_math_classifier import classify_glyph, is_math_font, CMEX_INTERPRETATIONS


# ---------------------------------------------------------------------------
# TeX Glyph & Font Interpretation Dictionary
# ---------------------------------------------------------------------------

TEX_GLYPH_MAP = {
    # CMEX10 (Math Extension)
    "cmex": {
        "p": {"latex": r"\sqrt", "role": "radical", "type": "operator"},
        "\x12": {"latex": r"\left(", "role": "tall_delimiter_open", "type": "delimiter"},
        "\x13": {"latex": r"\right)", "role": "tall_delimiter_close", "type": "delimiter"},
        "X": {"latex": r"\sum", "role": "large_operator", "type": "operator"},
        "R": {"latex": r"\sum", "role": "large_operator", "type": "operator"},
        "P": {"latex": r"\sum", "role": "large_operator", "type": "operator"},
        "\ufffd": {"latex": r"\sum", "role": "large_operator", "type": "operator"},
        "Z": {"latex": r"\int", "role": "large_operator", "type": "operator"},
        "Q": {"latex": r"\prod", "role": "large_operator", "type": "operator"},
    },
    # CMSY10 / CMSY7 (Math Symbols)
    "cmsy": {
        "|": {"latex": "|", "role": "delimiter_bar", "type": "delimiter"},
        "\u2212": {"latex": "-", "role": "minus", "type": "operator"},
        "-": {"latex": "-", "role": "minus", "type": "operator"},
        "\u22a4": {"latex": r"^\top", "role": "transpose", "type": "superscript_operator"},
        "\u221d": {"latex": r"\propto", "role": "proportional", "type": "relation"},
        "N": {"latex": r"\mathcal{N}", "role": "distribution_gaussian", "type": "identifier"},
        "\u2208": {"latex": r"\in", "role": "set_membership", "type": "relation"},
        "{": {"latex": r"\{", "role": "brace_open", "type": "delimiter"},
        "}": {"latex": r"\}", "role": "brace_close", "type": "delimiter"},
        "\u2264": {"latex": r"\le", "role": "relation_le", "type": "relation"},
        "\u2265": {"latex": r"\ge", "role": "relation_ge", "type": "relation"},
        "\u2248": {"latex": r"\approx", "role": "relation_approx", "type": "relation"},
    },
    # MSBM10 (Blackboard Bold)
    "msbm": {
        "R": {"latex": r"\mathbb{R}", "role": "reals", "type": "identifier"},
        "E": {"latex": r"\mathbb{E}", "role": "expectation", "type": "operator"},
        "N": {"latex": r"\mathbb{N}", "role": "naturals", "type": "identifier"},
        "Z": {"latex": r"\mathbb{Z}", "role": "integers", "type": "identifier"},
        "C": {"latex": r"\mathbb{C}", "role": "complex", "type": "identifier"},
    },
    # Greek translations for CMMI / CMBX / CMMIB
    "greek": {
        "\u03c0": r"\pi",
        "\u03bc": r"\mu",
        "\u00b5": r"\mu",
        "\u03a3": r"\Sigma",
        "\u03b1": r"\alpha",
        "\u03b2": r"\beta",
        "\u03b3": r"\gamma",
        "\u03b8": r"\theta",
        "\u03c3": r"\sigma",
        "\u03c4": r"\tau",
        "\u03c9": r"\omega",
        "\u03d5": r"\phi",
        "\u03c8": r"\psi",
    }
}


class MultimodalMathRecoveryEngine:
    """Multi-channel mathematical PDF recovery engine."""

    def __init__(self, zoom: int = 20, ink_threshold: int = 128):
        self.glea = GlyphEvidenceAdjudicator(zoom=zoom, ink_threshold=ink_threshold)

    def extract_page_vector_drawings(self, page: pymupdf.Page) -> list[dict[str, Any]]:
        """Extract horizontal vector rule paths (fractions, radical vinculums)."""
        rules = []
        for d in page.get_drawings():
            rect = d["rect"]
            w = rect.width
            h = rect.height
            # Horizontal line or thin rectangle (height <= 2.5 pt, width >= 4.0 pt)
            if h <= 2.5 and w >= 4.0:
                rules.append({
                    "rect": [round(rect.x0, 3), round(rect.y0, 3), round(rect.x1, 3), round(rect.y1, 3)],
                    "y_center": round((rect.y0 + rect.y1) / 2.0, 3),
                    "width": round(w, 3),
                    "items": d.get("items", []),
                })
        return rules

    def extract_candidate_glyphs(
        self,
        page: pymupdf.Page,
        bbox_clip: list[float] | None = None,
        column_x_bounds: tuple[float, float] | None = None,
    ) -> list[dict[str, Any]]:
        """Extract character-level glyph observations with font metadata."""
        rawdict = page.get_text("rawdict")
        extracted = []

        clip_rect = pymupdf.Rect(bbox_clip) if bbox_clip else page.rect

        for block in rawdict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font = span["font"]
                    font_lower = font.lower()
                    size = round(span["size"], 2)

                    for ch in span.get("chars", []):
                        cb = ch["bbox"]
                        c_rect = pymupdf.Rect(cb)
                        if not clip_rect.intersects(c_rect):
                            continue
                        if column_x_bounds and not (column_x_bounds[0] - 5.0 <= cb[0] and cb[2] <= column_x_bounds[1] + 5.0):
                            continue

                        char_c = ch["c"]
                        extracted.append({
                            "char": char_c,
                            "char_code": ord(char_c),
                            "font": font,
                            "size_pt": size,
                            "origin": [round(x, 2) for x in ch.get("origin", [])],
                            "metric_bbox": [round(x, 3) for x in cb],
                        })
        return extracted

    def interpret_glyph_channel(self, glyph: dict[str, Any]) -> dict[str, Any]:
        """Classify glyph identity, font styling, and TeX role."""
        font = glyph["font"]
        font_lower = font.lower()
        c = glyph["char"]

        # Check TeX CMEX special encodings
        if "cmex" in font_lower:
            if c in TEX_GLYPH_MAP["cmex"]:
                info = TEX_GLYPH_MAP["cmex"][c]
                return {
                    **glyph,
                    "latex": info["latex"],
                    "role": info["role"],
                    "kind": info["type"],
                    "is_bold": False,
                    "is_italic": False,
                    "is_math": True,
                }

        # Check MSBM Blackboard Bold
        if "msbm" in font_lower:
            if c in TEX_GLYPH_MAP["msbm"]:
                info = TEX_GLYPH_MAP["msbm"][c]
                return {
                    **glyph,
                    "latex": info["latex"],
                    "role": info["role"],
                    "kind": info["type"],
                    "is_bold": False,
                    "is_italic": False,
                    "is_math": True,
                }

        # Check CMSY math symbols
        if "cmsy" in font_lower:
            if c in TEX_GLYPH_MAP["cmsy"]:
                info = TEX_GLYPH_MAP["cmsy"][c]
                return {
                    **glyph,
                    "latex": info["latex"],
                    "role": info["role"],
                    "kind": info["type"],
                    "is_bold": False,
                    "is_italic": False,
                    "is_math": True,
                }

        # Greek characters in math fonts
        greek_tex = TEX_GLYPH_MAP["greek"].get(c)
        is_bold = "cmbx" in font_lower or "cmmib" in font_lower
        is_italic = "cmmi" in font_lower

        if greek_tex:
            latex_repr = f"\\boldsymbol{{{greek_tex}}}" if is_bold else greek_tex
            return {
                **glyph,
                "latex": latex_repr,
                "role": "greek_symbol",
                "kind": "identifier",
                "is_bold": is_bold,
                "is_italic": is_italic,
                "is_math": True,
            }

        # Bold vectors (e.g. x, w, z)
        if is_bold and c.isalpha():
            return {
                **glyph,
                "latex": f"\\mathbf{{{c}}}",
                "role": "vector",
                "kind": "identifier",
                "is_bold": True,
                "is_italic": is_italic,
                "is_math": True,
            }

        # Math italic scalars
        if is_italic and c.isalpha():
            return {
                **glyph,
                "latex": c,
                "role": "variable",
                "kind": "identifier",
                "is_bold": False,
                "is_italic": True,
                "is_math": True,
            }

        # Accents
        if c in ("~", "\u0303", "\u02dc", "\u223c"):
            return {
                **glyph,
                "latex": r"\tilde",
                "role": "accent_tilde",
                "kind": "accent",
                "is_bold": False,
                "is_italic": False,
                "is_math": True,
            }

        # Numbers and standard punctuation
        if c.isdigit():
            return {
                **glyph,
                "latex": c,
                "role": "number",
                "kind": "number",
                "is_bold": is_bold,
                "is_italic": is_italic,
                "is_math": True,
            }

        if c in "=≠<≤>≥≈∝":
            return {
                **glyph,
                "latex": c,
                "role": "relation",
                "kind": "relation",
                "is_bold": False,
                "is_italic": False,
                "is_math": True,
            }

        if c in "+-*/":
            return {
                **glyph,
                "latex": c,
                "role": "operator",
                "kind": "operator",
                "is_bold": False,
                "is_italic": False,
                "is_math": True,
            }

        if c in "()[]{}|":
            return {
                **glyph,
                "latex": c,
                "role": "delimiter",
                "kind": "delimiter",
                "is_bold": False,
                "is_italic": False,
                "is_math": True,
            }

        # Default fallback
        return {
            **glyph,
            "latex": c,
            "role": "text_or_symbol",
            "kind": "symbol",
            "is_bold": is_bold,
            "is_italic": is_italic,
            "is_math": is_math_font(font),
        }

    def adjudicate_glyphs_with_raster(
        self,
        page: pymupdf.Page,
        glyphs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Adjudicate physical visible ink boundaries via GLEA."""
        adjudicated = []
        for g in glyphs:
            # High-resolution raster envelope with 1.0 pt search padding
            env = self.glea.extract_glyph_ink_envelope(page, g["metric_bbox"], pad_pt=1.0)
            
            # Check tall vs short delimiter
            is_tall_delimiter = False
            if g.get("kind") == "delimiter" or g["char"] in "()[]{}|":
                box = env["ink_bbox"] or g["metric_bbox"]
                height = box[3] - box[1]
                is_tall_delimiter = height >= 12.0 or g.get("role") in ("tall_delimiter_open", "tall_delimiter_close")

            # Check cross-channel disagreement
            has_disagreement = False
            disagreement_pt = 0.0
            if env["ink_bbox"]:
                metric_b = g["metric_bbox"]
                ink_b = env["ink_bbox"]
                dy_top = abs(metric_b[1] - ink_b[1])
                dy_bot = abs(metric_b[3] - ink_b[3])
                disagreement_pt = round(max(dy_top, dy_bot), 3)
                has_disagreement = disagreement_pt > 2.0

            adjudicated.append({
                **g,
                "has_visible_ink": env["has_visible_ink"],
                "ink_bbox": env["ink_bbox"],
                "is_tall_delimiter": is_tall_delimiter,
                "cross_channel_disagreement_pt": disagreement_pt,
                "cross_channel_conflict": has_disagreement,
            })
        return adjudicated

    def cluster_quad_expressions(
        self,
        glyphs: list[dict[str, Any]],
        quad_threshold_pt: float = 14.0,
    ) -> list[list[dict[str, Any]]]:
        """Partition glyph sequence into sub-expressions separated by quad space."""
        if not glyphs:
            return []
        
        # Sort glyphs by horizontal position
        sorted_glyphs = sorted(glyphs, key=lambda g: g["metric_bbox"][0])
        clusters = [[sorted_glyphs[0]]]

        for g in sorted_glyphs[1:]:
            prev_g = clusters[-1][-1]
            gap = g["metric_bbox"][0] - prev_g["metric_bbox"][2]
            if gap >= quad_threshold_pt:
                clusters.append([g])
            else:
                clusters[-1].append(g)

        return clusters

    def recover_spatial_grammar(
        self,
        glyphs: list[dict[str, Any]],
        vector_rules: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Recover spatial relationships: fractions, radicals, scripts, delimiters."""
        if not glyphs:
            return {
                "latex": "",
                "mathml": "<math></math>",
                "spatial_graph": [],
                "visible_ink_bbox": None,
            }

        # Compute base font size
        base_size = max(g["size_pt"] for g in glyphs)
        
        # Identify fraction rules within the glyph horizontal bounds
        x_min = min(g["metric_bbox"][0] for g in glyphs)
        x_max = max(g["metric_bbox"][2] for g in glyphs)
        y_min = min(g["metric_bbox"][1] for g in glyphs)
        y_max = max(g["metric_bbox"][3] for g in glyphs)

        matched_fractions = []
        for r in vector_rules:
            rx0, ry0, rx1, ry1 = r["rect"]
            if (x_min - 2.0 <= rx0 and rx1 <= x_max + 2.0 and
                    y_min <= ry0 <= y_max):
                matched_fractions.append(r)

        # 1. Process Large Operators and their 2D vertical limits (e.g. \sum_{c=1}^C)
        consumed_by_large_op = set()
        large_op_latex = {}
        for idx, g in enumerate(glyphs):
            if g.get("role") == "large_operator":
                ox0, oy0, ox1, oy1 = g["metric_bbox"]
                upper = []
                lower = []
                for j, other in enumerate(glyphs):
                    if j == idx or other.get("role") == "large_operator":
                        continue
                    other_cx = (other["metric_bbox"][0] + other["metric_bbox"][2]) / 2.0
                    if ox0 - 4.0 <= other_cx <= ox1 + 4.0:
                        if other["metric_bbox"][3] <= oy0 + 2.0:
                            upper.append((j, other))
                        elif other["metric_bbox"][1] >= oy1 - 2.0:
                            lower.append((j, other))

                upper.sort(key=lambda item: item[1]["metric_bbox"][0])
                lower.sort(key=lambda item: item[1]["metric_bbox"][0])

                for j, _ in upper:
                    consumed_by_large_op.add(j)
                for j, _ in lower:
                    consumed_by_large_op.add(j)

                op_latex = g["latex"]
                if lower:
                    low_str = "".join(item[1]["latex"] for item in lower)
                    op_latex += f"_{{{low_str}}}"
                if upper:
                    up_str = "".join(item[1]["latex"] for item in upper)
                    op_latex += f"^{{{up_str}}}"
                large_op_latex[idx] = op_latex

        # 2. Process Fractions from vector horizontal rules
        consumed_by_fraction = set()
        fraction_tokens = {}  # rule x0 -> token
        for r in matched_fractions:
            rx0, ry0, rx1, ry1 = r["rect"]
            ry = r.get("y_center", (ry0 + ry1) / 2.0)
            num = []
            den = []
            for j, g in enumerate(glyphs):
                if j in consumed_by_large_op:
                    continue
                gcx = (g["metric_bbox"][0] + g["metric_bbox"][2]) / 2.0
                if rx0 - 2.0 <= gcx <= rx1 + 2.0:
                    if g["metric_bbox"][3] <= ry + 1.5:
                        num.append((j, g))
                    elif g["metric_bbox"][1] >= ry - 1.5:
                        den.append((j, g))
            if num and den:
                for j, _ in num:
                    consumed_by_fraction.add(j)
                for j, _ in den:
                    consumed_by_fraction.add(j)
                num.sort(key=lambda item: item[1]["metric_bbox"][0])
                den.sort(key=lambda item: item[1]["metric_bbox"][0])
                num_lat = "".join(item[1]["latex"] for item in num)
                den_lat = "".join(item[1]["latex"] for item in den)
                frac_lat = f"\\frac{{{num_lat}}}{{{den_lat}}}"
                fraction_tokens[rx0] = {
                    "type": "standard",
                    "char": "frac",
                    "latex": frac_lat,
                    "role": "fraction",
                    "kind": "operator",
                    "relation": "base",
                    "size_pt": base_size,
                    "metric_bbox": [rx0, ry0, rx1, ry1],
                    "ink_bbox": [rx0, ry0, rx1, ry1],
                }

        # 3. Pre-process accents (tilde, hat, etc.) with clean attachment
        modified_base = {}
        skip_accents = set()
        for idx, g in enumerate(glyphs):
            if idx in consumed_by_large_op or idx in consumed_by_fraction:
                continue
            if g.get("role") == "accent_tilde" or g.get("char") in ("~", "\u0303", "\u02dc", "\u223c"):
                g_cx = (g["metric_bbox"][0] + g["metric_bbox"][2]) / 2.0
                best_base_idx = None
                best_dist = 999.0
                for j, other in enumerate(glyphs):
                    if (j == idx or j in consumed_by_large_op or j in consumed_by_fraction
                            or other.get("role") == "accent_tilde"):
                        continue
                    o_cx = (other["metric_bbox"][0] + other["metric_bbox"][2]) / 2.0
                    dist = abs(g_cx - o_cx)
                    if dist < 4.0 and dist < best_dist:
                        best_dist = dist
                        best_base_idx = j
                if best_base_idx is not None:
                    modified_base[best_base_idx] = f"\\tilde{{{glyphs[best_base_idx]['latex']}}}"
                    skip_accents.add(idx)

        # 4. Build sequential tokens
        ordered_items = []
        for idx, g in enumerate(glyphs):
            if idx in consumed_by_large_op or idx in consumed_by_fraction or idx in skip_accents:
                continue
            g_copy = dict(g)
            if idx in large_op_latex:
                g_copy["latex"] = large_op_latex[idx]
                g_copy["role"] = "large_operator"
                g_copy["kind"] = "operator"
                ordered_items.append((g["metric_bbox"][0], g_copy))
            elif idx in modified_base:
                g_copy["latex"] = modified_base[idx]
                ordered_items.append((g["metric_bbox"][0], g_copy))
            else:
                ordered_items.append((g["metric_bbox"][0], g_copy))

        for frac_x0, frac_token in fraction_tokens.items():
            ordered_items.append((frac_x0, frac_token))

        ordered_items.sort(key=lambda item: item[0])

        tokens = []
        for _, g in ordered_items:
            rel = g.get("relation", "base")
            if g.get("role") == "transpose":
                rel = "superscript"
                lat = "\\top"
            elif g.get("role") == "large_operator":
                rel = "base"
                lat = g["latex"]
            elif g.get("role") == "fraction":
                rel = "base"
                lat = g["latex"]
            elif g.get("size_pt", base_size) < base_size * 0.85:
                mid_y = (y_min + y_max) / 2.0
                g_y = (g["metric_bbox"][1] + g["metric_bbox"][3]) / 2.0
                rel = "subscript" if g_y > mid_y + 1.0 else "superscript"
                lat = g["latex"].lstrip("^").lstrip("_")
            else:
                lat = g["latex"]

            tokens.append({
                "type": "standard",
                "char": g["char"],
                "latex": lat,
                "role": g.get("role", "symbol"),
                "kind": g.get("kind", "symbol"),
                "relation": rel,
                "is_tall_delimiter": g.get("is_tall_delimiter", False),
                "metric_bbox": g["metric_bbox"],
                "ink_bbox": g.get("ink_bbox"),
            })

        # 5. Synthesize LaTeX string with strict script transition
        latex_parts = []
        in_sub = False
        in_sup = False

        for t in tokens:
            if t["type"] == "accented":
                latex_parts.append(f"{t['accent']}{{{t['base']}}}")
                continue

            rel = t.get("relation", "base")
            lat = t["latex"]

            if rel == "subscript":
                if in_sup:
                    latex_parts.append("}")
                    in_sup = False
                if not in_sub:
                    latex_parts.append(f"_{{{lat}")
                    in_sub = True
                else:
                    latex_parts.append(lat)
            elif rel == "superscript":
                if in_sub:
                    latex_parts.append("}")
                    in_sub = False
                if not in_sup:
                    latex_parts.append(f"^{{{lat}")
                    in_sup = True
                else:
                    latex_parts.append(lat)
            else:
                if in_sub:
                    latex_parts.append("}")
                    in_sub = False
                if in_sup:
                    latex_parts.append("}")
                    in_sup = False

                if t["role"] == "relation":
                    latex_parts.append(f" {lat} ")
                elif t["role"] == "operator" and lat in "+-":
                    latex_parts.append(f" {lat} ")
                elif t.get("is_tall_delimiter"):
                    if lat in ("(", "\\left("):
                        latex_parts.append(r"\left(")
                    elif lat in (")", "\\right)"):
                        latex_parts.append(r"\right)")
                    else:
                        latex_parts.append(lat)
                else:
                    latex_parts.append(lat)

        if in_sub or in_sup:
            latex_parts.append("}")

        synthesized_latex = "".join(latex_parts).strip()
        synthesized_latex = re.sub(r"\s+", " ", synthesized_latex)

        # Generate Presentation MathML for AST parser
        mathml_elements = []
        for t in tokens:
            kind = t.get("kind", "symbol")
            raw_val = t.get("char") or t.get("base") or t.get("latex")
            val = str(raw_val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if kind == "operator" or kind == "accent":
                mathml_elements.append(f"<mo>{val}</mo>")
            elif kind == "relation":
                mathml_elements.append(f"<mo>{val}</mo>")
            elif kind == "delimiter":
                mathml_elements.append(f"<mo>{val}</mo>")
            elif kind == "number":
                mathml_elements.append(f"<mn>{val}</mn>")
            else:
                mathml_elements.append(f"<mi>{val}</mi>")

        mathml_str = f'<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow>{"".join(mathml_elements)}</mrow></math>'

        # Micro visible ink bounding box
        ink_boxes = [g["ink_bbox"] for g in glyphs if g.get("ink_bbox") is not None]
        if ink_boxes:
            refined_bbox = [
                round(min(b[0] for b in ink_boxes), 3),
                round(min(b[1] for b in ink_boxes), 3),
                round(max(b[2] for b in ink_boxes), 3),
                round(max(b[3] for b in ink_boxes), 3),
            ]
        else:
            refined_bbox = [round(x_min, 3), round(y_min, 3), round(x_max, 3), round(y_max, 3)]

        return {
            "latex": synthesized_latex,
            "mathml": mathml_str,
            "spatial_graph": tokens,
            "visible_ink_bbox": refined_bbox,
            "vector_rules_matched": len(matched_fractions),
        }

    def verify_gate_d4_clearance(
        self,
        page: pymupdf.Page,
        math_bbox: list[float],
        required_clearance_pt: float = 2.0,
    ) -> dict[str, Any]:
        """Gate D4: Strict physical clearance verification to nearest external token."""
        crop_x0 = math_bbox[0] - required_clearance_pt
        crop_y0 = math_bbox[1] - required_clearance_pt
        crop_x1 = math_bbox[2] + required_clearance_pt
        crop_y1 = math_bbox[3] + required_clearance_pt

        all_words = page.get_text("words")
        crop_rect = pymupdf.Rect(crop_x0, crop_y0, crop_x1, crop_y1)

        clearance_above = float("inf")
        clearance_below = float("inf")
        nearest_above = None
        nearest_below = None

        for w in all_words:
            wr = pymupdf.Rect(w[:4])
            # Skip words inside math proposal itself
            if wr.intersects(crop_rect) and wr.y0 >= crop_y0 and wr.y1 <= crop_y1:
                continue
            # Horizontal overlap required for direct vertical gutter check
            has_h_overlap = max(wr.x0, crop_x0) < min(wr.x1, crop_x1)
            if not has_h_overlap:
                continue

            if wr.y1 <= crop_y0:
                d = crop_y0 - wr.y1
                if d < clearance_above:
                    clearance_above = d
                    nearest_above = {"token": w[4], "clearance_pt": round(d, 2), "bbox": [round(c, 2) for c in w[:4]]}
            elif wr.y0 >= crop_y1:
                d = wr.y0 - crop_y1
                if d < clearance_below:
                    clearance_below = d
                    nearest_below = {"token": w[4], "clearance_pt": round(d, 2), "bbox": [round(c, 2) for c in w[:4]]}

        pass_clearance = (clearance_above >= required_clearance_pt) and (clearance_below >= required_clearance_pt)

        # Explicit failure diagnosis
        failure_reason = None
        if not pass_clearance:
            if clearance_above < required_clearance_pt:
                failure_reason = f"sub_2pt_clearance_failure_above ({clearance_above:.2f} pt < {required_clearance_pt:.2f} pt)"
            else:
                failure_reason = f"sub_2pt_clearance_failure_below ({clearance_below:.2f} pt < {required_clearance_pt:.2f} pt)"

        return {
            "gate_d4_passed": pass_clearance,
            "clearance_above_pt": round(clearance_above, 2) if clearance_above != float("inf") else 999.0,
            "clearance_below_pt": round(clearance_below, 2) if clearance_below != float("inf") else 999.0,
            "nearest_neighbor_above": nearest_above,
            "nearest_neighbor_below": nearest_below,
            "failure_reason": failure_reason,
            "crop_evaluated": [round(c, 2) for c in [crop_x0, crop_y0, crop_x1, crop_y1]],
        }

    def recover_equation_region(
        self,
        pdf_path: str | Path,
        page_idx: int,
        bbox_clip: list[float] | None = None,
        column_x_bounds: tuple[float, float] | None = None,
        equation_hint_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute full multimodal recovery on a specified equation region."""
        doc = pymupdf.open(str(pdf_path))
        page = doc[page_idx]

        # 1. Vector drawings
        vector_rules = self.extract_page_vector_drawings(page)

        # 2. Glyph extraction
        raw_glyphs = self.extract_candidate_glyphs(
            page,
            bbox_clip=bbox_clip,
            column_x_bounds=column_x_bounds,
        )

        if not raw_glyphs:
            return {
                "status": "NO_GLYPHS_FOUND",
                "page_index": page_idx,
                "bbox_clip": bbox_clip,
            }

        # 3. TeX Font Interpretation
        interpreted_glyphs = [self.interpret_glyph_channel(g) for g in raw_glyphs]

        # 4. Raster visible ink adjudication (GLEA)
        adjudicated_glyphs = self.adjudicate_glyphs_with_raster(page, interpreted_glyphs)

        # 5. Check clustered quad expressions
        clusters = self.cluster_quad_expressions(adjudicated_glyphs, quad_threshold_pt=14.0)

        recovered_clusters = []
        for cluster in clusters:
            rec = self.recover_spatial_grammar(cluster, vector_rules)
            recovered_clusters.append(rec)

        # Combine into complete LaTeX
        if len(recovered_clusters) > 1:
            full_latex = r" \qquad ".join(c["latex"] for c in recovered_clusters)
            combined_mathml = f'<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow>{"".join(c["mathml"] for c in recovered_clusters)}</mrow></math>'
            all_ink_boxes = [c["visible_ink_bbox"] for c in recovered_clusters if c["visible_ink_bbox"]]
            if all_ink_boxes:
                full_ink_bbox = [
                    min(b[0] for b in all_ink_boxes),
                    min(b[1] for b in all_ink_boxes),
                    max(b[2] for b in all_ink_boxes),
                    max(b[3] for b in all_ink_boxes),
                ]
            else:
                full_ink_bbox = bbox_clip or [0, 0, page.rect.width, page.rect.height]
        else:
            full_latex = recovered_clusters[0]["latex"]
            combined_mathml = recovered_clusters[0]["mathml"]
            full_ink_bbox = recovered_clusters[0]["visible_ink_bbox"]

        # 6. Canonical Typed AST Extraction
        ast_root, ast_errors = extract_structural_ast(combined_mathml)

        # 7. Independent Gate D4 Verification
        gate_d4 = self.verify_gate_d4_clearance(page, full_ink_bbox, required_clearance_pt=2.0)

        # Final verdict: Gate D4 is conjunctive and can NEVER be overridden
        if not gate_d4["gate_d4_passed"]:
            verdict = f"NOT_VERIFIED: {gate_d4['failure_reason']}"
        elif ast_root is not None:
            verdict = "PASSED_VERIFIED"
        else:
            verdict = "AST_PARSE_FAILURE"

        return {
            "status": "RECOVERED",
            "equation_id": equation_hint_id,
            "page_index": page_idx,
            "reconstructed_latex": full_latex,
            "reconstructed_mathml": combined_mathml,
            "cluster_count": len(recovered_clusters),
            "glyph_count": len(adjudicated_glyphs),
            "visible_ink_math_bbox": full_ink_bbox,
            "canonical_ast": {
                "success": ast_root is not None,
                "root_kind": ast_root.kind if ast_root else None,
                "children_count": len(ast_root.children) if ast_root else 0,
                "ast_errors": ast_errors,
            },
            "gate_d4_verification": gate_d4,
            "final_verdict": verdict,
        }
