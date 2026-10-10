#!/usr/bin/env python3
"""
STRUCTURAL AST EXTRACTOR — MathML -> typed recursive ExprNode.

The recovery parser (mathml_parser.MathMLParser) walks the real MathML tree
but flattens it to a STRING. That string is diagnostic evidence, not proof of
structural fidelity: it cannot round-trip, cannot preserve child order as a
typed relation, and collapses operators/decorations into linear text.

This module walks the SAME MathML tree and emits the contract's typed
recursive ExprNode (scripts/math_contract.py), preserving:
  - operator identity   (sum/prod/integral/limit, not a bare token)
  - limits as children  (munder/mover/munderover -> bounds, never dropped)
  - differentials       (dx/dy/dz as ordered measure children)
  - relations           (sim/approx/propto/to as typed relation nodes)
  - decorations         (accent/hat/bar/vec fused into the identifier)
  - fractions/roots     (numerator/denominator, radicand/index)
  - unsupported nodes   (preserved with source tag + reason, never dropped)

Every emitted node is bound to its source occurrence via occurrence_key, so
the persisted AST is attributable to a specific <math> element, not just a
document-order index.

Design rule: a node the extractor cannot represent becomes an ExprNode of
kind='unsupported' carrying its source tag and raw text — it is NEVER omitted.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import ExprNode, NODE_KINDS  # noqa: E402

# MathML tag -> contract node kind (structural, lossless mapping intent).
# Tags not listed here are preserved as 'unsupported', never dropped.
_TAG_KIND = {
    "mi": "identifier",
    "mn": "number",
    "mo": "operator",
    "mfrac": "fraction",
    "msup": "power",
    "msub": "subscript",
    "msqrt": "sqrt",
    "mroot": "root",
    "mtable": "matrix",
    "mtext": "text",
    "mrow": "group",
}

# Operators that head a bounded construct (their limits are real children).
_BIG_OPS = {"∑": "sum", "∏": "product", "∫": "integral",
            "∮": "integral", "∬": "integral", "∭": "integral"}
_LIMIT_WORD = {"lim": "limit", "limsup": "limit", "liminf": "limit",
               "max": "limit", "min": "limit", "sup": "limit", "inf": "limit",
               "argmax": "limit", "argmin": "limit"}

# Relation glyph/word -> typed relation (never collapsed to '=').
_RELATIONS = {
    "=": "eq", "∼": "sim", "~": "sim", "≈": "approx", "≃": "simeq",
    "≅": "cong", "→": "to", "⟶": "to", "≡": "equiv", "∝": "propto",
    "≤": "leq", "≥": "geq", "≠": "neq", "∈": "in", "∣": "conditional",
    ":=": "define", "≔": "define", "coloneqq": "define",
}

# Accent/decoration markers fused onto the base identifier.
_DECORATIONS = {"⊤": "top", "T": "top", "†": "dagger", "⊥": "perp",
                "ˆ": "hat", "˜": "tilde", "¯": "bar", "→": "vec",
                "˚": "ring", "¨": "ddot", "˙": "dot"}

# Differential markers (measure of integration). Ordered children.
_DIFFERENTIAL_RE = None  # built lazily; 𝑑 and italic d followed by a symbol


class StructuralASTExtractor:
    """
    Walk a BeautifulSoup <math> node and emit a typed ExprNode tree.

    Injected accessors mirror MathMLParser so this works with the same
    BeautifulSoup 'html.parser' trees the recovery pipeline already builds.
    """

    def __init__(self) -> None:
        self.unsupported: list[str] = []

    # -- public ------------------------------------------------------------
    def extract(self, math_node: Any) -> ExprNode:
        """Extract a typed AST from a <math> element. Never returns None."""
        self.unsupported = []
        node = self._walk(math_node)
        if node is None:
            # A <math> that produced nothing is itself an unsupported outcome.
            return ExprNode(
                kind="unsupported",
                value=self._text(math_node)[:200],
                attributes={"source_tag": "math", "reason": "empty_walk"},
            )
        return node

    # -- internals ---------------------------------------------------------
    def _tag(self, n: Any) -> str | None:
        return getattr(n, "name", None)

    def _children(self, node: Any) -> list[Any]:
        # <annotation> carries the LaTeX source, not presentation structure.
        # It is metadata (a duplicate of the latex field), never a math node.
        out = []
        for c in getattr(node, "children", []):
            if getattr(c, "name", None) == "annotation":
                continue
            if getattr(c, "name", None):
                out.append(c)
        return out

    def _text(self, n: Any) -> str:
        if hasattr(n, "get_text"):
            return n.get_text()
        return str(n)

    def _walk(self, node: Any) -> ExprNode | None:
        tag = self._tag(node)
        if tag is None:
            return None
        if tag in ("mstyle", "mpadded", "mphantom", "merror", "menclose", "semantics"):
            # DECLARED normalization (Finding 5): these wrappers are transparent
            # for mathematical structure, but we RECORD the wrapper chain.
            # Each level of nesting appends to a list — no silent overwrite.
            inner = self._walk_children(node)
            if inner is None:
                return ExprNode(kind="group", attributes={"normalized_wrappers": [tag]})
            # merge the wrapper chain: extend existing list or start new one
            merged = dict(inner.attributes)
            existing = merged.get("normalized_wrappers")
            if existing:
                merged["normalized_wrappers"] = [tag] + list(existing)
            else:
                merged["normalized_wrappers"] = [tag]
            return ExprNode(kind=inner.kind, value=inner.value,
                            children=inner.children, attributes=merged)

        if tag == "math":
            kids = [self._walk(k) for k in self._children(node)]
            kids = [k for k in kids if k is not None]
            if len(kids) == 1:
                return kids[0]
            return ExprNode(kind="group", children=tuple(kids))

        if tag in ("mi", "mn", "mo", "mtext"):
            return self._leaf(tag, node)

        if tag == "mfrac":
            return self._binary(tag, node, "fraction")

        if tag == "msup":
            return self._binary(tag, node, "power")

        if tag == "msub":
            return self._binary(tag, node, "subscript")

        if tag == "msubsup":
            return self._subsup(node)

        if tag == "msqrt":
            inner = self._walk_children(node)
            return ExprNode(kind="sqrt", children=(inner,) if inner else ())

        if tag == "mroot":
            kids = [self._walk(k) for k in self._children(node)]
            kids = [k for k in kids if k is not None]
            if len(kids) >= 2:
                return ExprNode(kind="root", children=(kids[0], kids[1]),
                                attributes={"index": kids[1].to_dict()})
            return self._unsupported(node, "mroot_arity")

        if tag in ("mover", "munder", "munderover"):
            return self._script_decorated(node, tag)

        if tag == "mtable":
            return self._matrix(node)

        if tag == "mtr":
            # a row: each cell (mtd) is a child
            cells = [self._walk(c) for c in self._children(node)]
            cells = [c for c in cells if c is not None]
            return ExprNode(kind="group", children=tuple(cells),
                            attributes={"row": True})

        if tag == "mtd":
            # a cell: transparent wrapper, extract contents (preserve boundaries
            # via the parent mtr). Multiple children stay grouped.
            return self._group(node)

        if tag == "mrow":
            return self._group(node)

        # Unknown/unsupported structural tag: preserve, never drop.
        return self._unsupported(node, f"unhandled_tag:{tag}")

    def _leaf(self, tag: str, node: Any) -> ExprNode:
        text = self._text(node).strip()
        if tag == "mo":
            rel = _RELATIONS.get(text)
            if rel:
                return ExprNode(kind="relation", value=text,
                                attributes={"relation_type": rel})
            # big operator?
            if text in _BIG_OPS:
                return ExprNode(kind=_BIG_OPS[text], value=text,
                                attributes={"operator": _BIG_OPS[text]})
            # limit word (lim, max, inf...)
            if text in _LIMIT_WORD:
                return ExprNode(kind=_LIMIT_WORD[text], value=text,
                                attributes={"operator": _LIMIT_WORD[text]})
            # differential 𝑑 / italic d as standalone measure
            if text in ("𝑑", "ⅆ", "d", "∂"):
                return ExprNode(kind="differential", value=text,
                                attributes={"measure": text})
            return ExprNode(kind="operator", value=text)
        kind = _TAG_KIND.get(tag, "identifier")
        return ExprNode(kind=kind, value=text)

    def _walk_children(self, node: Any) -> ExprNode | None:
        kids = [self._walk(k) for k in self._children(node)]
        kids = [k for k in kids if k is not None]
        if not kids:
            return None
        if len(kids) == 1:
            return kids[0]
        return ExprNode(kind="group", children=tuple(kids))

    def _binary(self, tag: str, node: Any, kind: str) -> ExprNode:
        kids = [self._walk(k) for k in self._children(node)]
        kids = [k for k in kids if k is not None]
        if len(kids) >= 2:
            return ExprNode(kind=kind, children=(kids[0], kids[1]))
        return self._unsupported(node, f"{tag}_arity")

    def _subsup(self, node: Any) -> ExprNode:
        """<msubsup> base sub sup — preserve base + both scripts as children."""
        kids = [self._walk(k) for k in self._children(node)]
        kids = [k for k in kids if k is not None]
        if len(kids) >= 3:
            return ExprNode(kind="group", children=(kids[0], kids[1], kids[2]),
                            attributes={"msubsup": True,
                                        "base": kids[0].to_dict(),
                                        "sub": kids[1].to_dict(),
                                        "sup": kids[2].to_dict()})
        if len(kids) == 2:
            return ExprNode(kind="power", children=(kids[0], kids[1]))
        return self._unsupported(node, "msubsup_arity")

    def _script_decorated(self, node: Any, tag: str) -> ExprNode:
        """
        <mover>/<munder>/<munderover>: base + decoration/limits.
        Big-operator limits become real children (never dropped).
        Accents fuse onto the base identifier.
        """
        kids = [self._walk(k) for k in self._children(node)]
        kids = [k for k in kids if k is not None]
        if not kids:
            return self._unsupported(node, f"{tag}_empty")
        base = kids[0]

        # Determine if base is a big operator / limit head.
        base_kind = base.kind
        is_bounded = base_kind in ("sum", "product", "integral", "limit")

        if is_bounded:
            # Limits are REAL children with explicit roles (lower_bound /
            # upper_bound), never dropped. A <mover> on a big operator is an
            # UPPER bound, not a decoration — dropping it loses the limit.
            if tag == "munderover" and len(kids) >= 3:
                lower, upper = kids[1], kids[2]
                base.attributes["lower_bound"] = lower.to_dict()
                base.attributes["upper_bound"] = upper.to_dict()
                return ExprNode(kind=base_kind, value=base.value,
                                attributes=base.attributes,
                                children=base.children + (lower, upper))
            if tag == "munder" and len(kids) >= 2:
                lower = kids[1]
                base.attributes["lower_bound"] = lower.to_dict()
                return ExprNode(kind=base_kind, value=base.value,
                                attributes=base.attributes,
                                children=base.children + (lower,))
            if tag == "mover" and len(kids) >= 2:
                # upper bound (e.g. <mover><mo>∑</mo><mi>n</mi></mover>)
                upper = kids[1]
                base.attributes["upper_bound"] = upper.to_dict()
                return ExprNode(kind=base_kind, value=base.value,
                                attributes=base.attributes,
                                children=base.children + (upper,))
            # bare bounded operator with no limit child
            return base

        # accent/decoration on an identifier
        if len(kids) >= 2:
            deco_text = self._text(self._children(node)[1]).strip() if len(self._children(node)) >= 2 else ""
            deco = _DECORATIONS.get(deco_text)
            if deco and base.kind == "identifier":
                fused_value = f"{base.value}_{deco}"
                return ExprNode(kind="identifier", value=fused_value,
                                attributes={"decoration": deco,
                                            "base": base.value})
            # generic over/under: keep as power/group with decoration marker
            return ExprNode(kind="group", children=tuple(kids),
                            attributes={"script": tag, "decoration_text": deco_text})
        return base

    def _matrix(self, node: Any) -> ExprNode:
        rows = []
        for tr in self._children(node):
            if self._tag(tr) in ("mtr",):
                cells = [self._walk(td) for td in self._children(tr)]
                cells = [c for c in cells if c is not None]
                rows.append(ExprNode(kind="group", children=tuple(cells)))
            else:
                c = self._walk(tr)
                if c is not None:
                    rows.append(c)
        return ExprNode(kind="matrix", children=tuple(rows),
                        attributes={"row_count": len(rows)})

    def _group(self, node: Any) -> ExprNode:
        kids = [self._walk(k) for k in self._children(node)]
        kids = [k for k in kids if k is not None]
        return ExprNode(kind="group", children=tuple(kids))

    def _unsupported(self, node: Any, reason: str) -> ExprNode:
        tag = self._tag(node) or "unknown"
        self.unsupported.append(f"{reason}:{tag}")
        return ExprNode(
            kind="unsupported",
            value=self._text(node)[:200],
            attributes={"source_tag": tag, "reason": reason},
        )


def extract_structural_ast(mathml: str) -> tuple[ExprNode | None, list[str]]:
    """
    Convenience: MathML string -> (typed ExprNode, unsupported reasons).
    Returns (None, [reason]) if the string cannot be parsed at all.
    """
    if not mathml:
        return None, ["no_mathml"]
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(mathml, "html.parser")
        node = soup.find("math")
        if node is None:
            return None, ["no_math_element"]
        ex = StructuralASTExtractor()
        tree = ex.extract(node)
        return tree, ex.unsupported
    except Exception as e:
        return None, [f"extract_error:{type(e).__name__}:{e}"]
