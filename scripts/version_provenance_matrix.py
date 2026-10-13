#!/usr/bin/env python3
"""
Version Provenance Matrix
=========================
Maintains multi-version document provenance for arXiv mathematical literature
in parallel columnar layers (|v1|v2|...|pdf|) rather than destructive flattening
or lossy positional guessing.

Guarantees:
1. Grounded Source Origin: Points directly to arxiv.org URLs:
   - Canonical HTML: https://arxiv.org/html/<paper_id>
   - Versioned HTML: https://arxiv.org/html/<paper_id>v<N>
   - Versioned PDF:  https://arxiv.org/pdf/<paper_id>v<N>.pdf
2. Position Invariance: Retains exact document order locators math[i]
   and marks gaps across versions explicitly (None) instead of skipping
   or misaligning.
3. Symbol & Structure Awareness: Holds metadata on operator fidelity,
   delimiters, 2D structures (cases, fractions, binomials) per version slice.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class VersionSliceItem:
    """A single version witness for a mathematical occurrence."""
    version_id: str                      # e.g. "v1", "v2", "canonical_html", "pdf"
    source_url: str                      # e.g. "https://arxiv.org/html/2605.00155v1"
    source_locator: str                  # e.g. "math[3]"
    latex: Optional[str] = None          # extracted LaTeX string
    mathml: Optional[str] = None         # raw MathML when available
    recovered_expr: Optional[str] = None # normalized algebraic / structural expression
    is_display: bool = False
    context_before: str = ""
    context_after: str = ""
    section_title: str = ""
    bounding_box: Optional[Dict[str, float]] = None # for PDF/chroma visual layer
    has_large_delimiters: bool = False   # cases, tall brackets, norms
    has_vertical_fraction: bool = False  # fraction vinculum
    generator: Optional[str] = None      # e.g. "LaTeXML oxide (version 0.7.6)"
    status: str = "present"              # "present", "missing", "unparsed"


@dataclass
class LayeredEquationSlice:
    """
    A multi-layer slice |v1|v2|...|pdf| for a specific mathematical occurrence index.
    Prevents positional guessing by aligning occurrences explicitly across layers.
    """
    occurrence_index: int                # 0-indexed document occurrence math[i]
    arxiv_id: str                        # base paper ID (e.g. "2605.00155")
    layers: Dict[str, Optional[VersionSliceItem]] = field(default_factory=dict)

    def get_layer(self, layer_id: str) -> Optional[VersionSliceItem]:
        return self.layers.get(layer_id)

    def set_layer(self, layer_id: str, item: Optional[VersionSliceItem]) -> None:
        self.layers[layer_id] = item

    def to_dict(self) -> Dict[str, Any]:
        return {
            "occurrence_index": self.occurrence_index,
            "arxiv_id": self.arxiv_id,
            "layers": {
                k: (asdict(v) if v is not None else None)
                for k, v in self.layers.items()
            }
        }


class VersionProvenanceMatrix:
    """
    Manages multi-version parallel slices for an arXiv paper.
    """
    def __init__(self, arxiv_id: str, active_versions: Optional[List[str]] = None, github_repos: Optional[List[str]] = None):
        self.arxiv_id = arxiv_id
        self.active_versions = active_versions or ["v1", "v2", "canonical_html", "pdf"]
        self.github_repos = github_repos or []
        self.slices: Dict[int, LayeredEquationSlice] = {}

    def get_or_create_slice(self, occurrence_index: int) -> LayeredEquationSlice:
        if occurrence_index not in self.slices:
            self.slices[occurrence_index] = LayeredEquationSlice(
                occurrence_index=occurrence_index,
                arxiv_id=self.arxiv_id,
                layers={v: None for v in self.active_versions}
            )
        return self.slices[occurrence_index]

    def add_witness(
        self,
        occurrence_index: int,
        version_id: str,
        source_url: str,
        latex: Optional[str] = None,
        mathml: Optional[str] = None,
        recovered_expr: Optional[str] = None,
        is_display: bool = False,
        context_before: str = "",
        context_after: str = "",
        section_title: str = "",
        bounding_box: Optional[Dict[str, float]] = None,
        has_large_delimiters: bool = False,
        has_vertical_fraction: bool = False,
        generator: Optional[str] = None,
    ) -> None:
        """Add or update a witness at a specific version layer."""
        eq_slice = self.get_or_create_slice(occurrence_index)
        item = VersionSliceItem(
            version_id=version_id,
            source_url=source_url,
            source_locator=f"math[{occurrence_index}]",
            latex=latex,
            mathml=mathml,
            recovered_expr=recovered_expr,
            is_display=is_display,
            context_before=context_before,
            context_after=context_after,
            section_title=section_title,
            bounding_box=bounding_box,
            has_large_delimiters=has_large_delimiters,
            has_vertical_fraction=has_vertical_fraction,
            generator=generator,
            status="present" if latex or mathml or recovered_expr else "missing",
        )
        eq_slice.set_layer(version_id, item)

    def to_matrix_dict(self) -> Dict[str, Any]:
        """Export matrix structured as parallel columns / layers."""
        return {
            "arxiv_id": self.arxiv_id,
            "canonical_urls": {
                "canonical_html": f"https://arxiv.org/html/{self.arxiv_id}",
                "pdf": f"https://arxiv.org/pdf/{self.arxiv_id}.pdf",
            },
            "github_repos": self.github_repos,
            "layers": self.active_versions,
            "total_slices": len(self.slices),
            "slices": [
                self.slices[i].to_dict()
                for i in sorted(self.slices.keys())
            ],
        }
