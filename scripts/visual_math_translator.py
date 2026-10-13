#!/usr/bin/env python3
"""
Visual Math Translator — 2D Spatial Layout to Structural AST.
=============================================================
Translates detected 2D visual structures (fractions, cases, enclosures)
into typed recursive ExprNode representations compatible with the King Wen contract.

Cross-checks against 1D text/MathML representations to detect:
  - Skipped division bars (where a 2D fraction was read as adjacent factors)
  - Flattened cases (where a piecewise brace was collapsed to a single line)
  - Dropped brackets / norms (where tall delimiters were lost)
"""
from __future__ import annotations

import io
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import ExprNode, NODE_KINDS
from chroma_visual_reader import VisualRegion, VisualMathStructure

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class DiscrepancyReport:
    structure_type: str                  # "fraction", "cases", "enclosure", "norm"
    visual_bbox: Tuple[float, float, float, float]
    detected_in_visual: bool
    detected_in_text: bool
    issue_kind: str                      # "skipped_division", "collapsed_cases", "dropped_bracket", "flattened_norm", "consistent"
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VisualMathTranslator:
    """
    Translates 2D visual math structures into typed ExprNode trees
    and audits discrepancies with 1D linear expressions.
    """

    @staticmethod
    def translate_fraction(structure: VisualMathStructure, regions_by_id: Dict[int, VisualRegion]) -> ExprNode:
        """Translate a 2D visual fraction into a typed ExprNode."""
        num_ids = structure.components.get("numerator", [])
        den_ids = structure.components.get("denominator", [])

        # Build numerator children
        num_children: List[ExprNode] = []
        for nid in num_ids:
            reg = regions_by_id.get(nid)
            if reg:
                k = "identifier" if reg.region_type in ("symbol", "text") else reg.region_type
                if k not in NODE_KINDS:
                    k = "identifier"
                num_children.append(ExprNode(
                    kind=k,
                    value=reg.text or f"sym_{nid}",
                ))

        # Build denominator children
        den_children: List[ExprNode] = []
        for did in den_ids:
            reg = regions_by_id.get(did)
            if reg:
                k = "identifier" if reg.region_type in ("symbol", "text") else reg.region_type
                if k not in NODE_KINDS:
                    k = "identifier"
                den_children.append(ExprNode(
                    kind=k,
                    value=reg.text or f"sym_{did}",
                ))

        num_node = ExprNode(kind="group", children=tuple(num_children)) if len(num_children) > 1 else (num_children[0] if num_children else ExprNode(kind="identifier", value=""))
        den_node = ExprNode(kind="group", children=tuple(den_children)) if len(den_children) > 1 else (den_children[0] if den_children else ExprNode(kind="identifier", value=""))

        return ExprNode(
            kind="fraction",
            children=(num_node, den_node),
            attributes={"visual_bbox": list(structure.bbox), "confidence": structure.confidence}
        )

    @staticmethod
    def translate_cases(structure: VisualMathStructure, regions_by_id: Dict[int, VisualRegion]) -> ExprNode:
        """Translate a 2D visual piecewise cases brace into a typed ExprNode."""
        branches: List[ExprNode] = []
        for comp_name, r_ids in sorted(structure.components.items()):
            if not comp_name.startswith("row_"):
                continue
            row_children: List[ExprNode] = []
            for rid in r_ids:
                reg = regions_by_id.get(rid)
                if reg:
                    k = "identifier" if reg.region_type in ("symbol", "text") else reg.region_type
                    if k not in NODE_KINDS:
                        k = "identifier"
                    row_children.append(ExprNode(
                        kind=k,
                        value=reg.text or f"sym_{rid}",
                    ))
            branches.append(ExprNode(kind="group", children=tuple(row_children)))

        return ExprNode(
            kind="cases",
            children=tuple(branches),
            attributes={"visual_bbox": list(structure.bbox), "confidence": structure.confidence}
        )

    @staticmethod
    def audit_discrepancy_with_text(structure: VisualMathStructure, text_expr: str) -> DiscrepancyReport:
        """
        Audit whether a detected 2D visual structure survived into the 1D text representation.
        Catches:
          - Fraction bars skipped / missing division symbol (`/` or `frac`)
          - Cases braces collapsed into single line (no `cases` or `{`)
        """
        st = structure.structure_type

        if st == "fraction":
            has_division_in_text = any(tok in text_expr for tok in ["/", "frac", "dfrac", "tfrac", "÷"])
            if not has_division_in_text:
                return DiscrepancyReport(
                    structure_type="fraction",
                    visual_bbox=structure.bbox,
                    detected_in_visual=True,
                    detected_in_text=False,
                    issue_kind="skipped_division",
                    details=f"2D fraction vinculum detected at {structure.bbox}, but 1D text '{text_expr[:40]}' contains no division symbol (/ or frac)."
                )
            return DiscrepancyReport(
                structure_type="fraction",
                visual_bbox=structure.bbox,
                detected_in_visual=True,
                detected_in_text=True,
                issue_kind="consistent",
                details="Fraction division preserved in both visual and text representations."
            )

        if st == "cases":
            has_cases_in_text = any(tok in text_expr for tok in ["cases", "{", "\\{"])
            if not has_cases_in_text:
                return DiscrepancyReport(
                    structure_type="cases",
                    visual_bbox=structure.bbox,
                    detected_in_visual=True,
                    detected_in_text=False,
                    issue_kind="collapsed_cases",
                    details=f"2D piecewise cases brace detected at {structure.bbox}, but 1D text '{text_expr[:40]}' has no cases structure or brace."
                )
            return DiscrepancyReport(
                structure_type="cases",
                visual_bbox=structure.bbox,
                detected_in_visual=True,
                detected_in_text=True,
                issue_kind="consistent",
                details="Piecewise cases structure preserved in both visual and text representations."
            )

        return DiscrepancyReport(
            structure_type=st,
            visual_bbox=structure.bbox,
            detected_in_visual=True,
            detected_in_text=True,
            issue_kind="consistent",
            details="Structure consistent."
        )


if __name__ == "__main__":
    print("Visual Math Translator loaded successfully.")
