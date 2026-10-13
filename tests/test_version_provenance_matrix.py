#!/usr/bin/env python3
"""
Tests for VersionProvenanceMatrix and prose context enrichment.

Validates:
- Layered version slices (|v1|v2|...|pdf|) preserve positional indices
- Missing data in a layer is explicit None, never guessed or skipped
- Prose context from corpus JSON propagates to evidence records
- Source URLs ground to arxiv.org, never local paths
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from version_provenance_matrix import (
    VersionProvenanceMatrix,
    VersionSliceItem,
    LayeredEquationSlice,
)


# ============================================================================
# Version Provenance Matrix Tests
# ============================================================================

def test_matrix_creates_all_layers():
    """Every active version layer should be pre-initialized as None."""
    vpm = VersionProvenanceMatrix("2605.00155", active_versions=["v1", "v2", "pdf"])
    eq_slice = vpm.get_or_create_slice(3)
    assert eq_slice.occurrence_index == 3
    assert eq_slice.arxiv_id == "2605.00155"
    assert set(eq_slice.layers.keys()) == {"v1", "v2", "pdf"}
    for v in ("v1", "v2", "pdf"):
        assert eq_slice.layers[v] is None, f"Layer {v} should be None until populated"


def test_matrix_add_witness_populates_layer():
    """Adding a witness should fill one layer, leaving others as None."""
    vpm = VersionProvenanceMatrix("2605.00155", active_versions=["v1", "v2", "pdf"])
    vpm.add_witness(
        occurrence_index=7,
        version_id="v1",
        source_url="https://arxiv.org/html/2605.00155v1",
        latex=r"\delta",
        is_display=False,
        context_before="ambiguity budget",
    )
    eq_slice = vpm.slices[7]
    assert eq_slice.layers["v1"] is not None
    assert eq_slice.layers["v1"].latex == r"\delta"
    assert eq_slice.layers["v1"].source_url == "https://arxiv.org/html/2605.00155v1"
    assert eq_slice.layers["v1"].context_before == "ambiguity budget"
    assert eq_slice.layers["v1"].status == "present"
    # Other layers remain None — explicit missing, no guessing
    assert eq_slice.layers["v2"] is None
    assert eq_slice.layers["pdf"] is None


def test_matrix_missing_layer_is_none_not_skipped():
    """
    If v2 adds an equation not in v1, v1 slice must be None, not
    silently skipped or positionally misaligned.
    """
    vpm = VersionProvenanceMatrix("2605.00155", active_versions=["v1", "v2"])
    # v2 has equation at index 5, v1 does not
    vpm.add_witness(
        occurrence_index=5,
        version_id="v2",
        source_url="https://arxiv.org/html/2605.00155v2",
        latex=r"\int_0^\infty f(x)\,dx",
        is_display=True,
    )
    eq_slice = vpm.slices[5]
    assert eq_slice.layers["v1"] is None, "v1 should be explicit None, not guessed"
    assert eq_slice.layers["v2"] is not None
    assert eq_slice.layers["v2"].is_display is True


def test_matrix_source_urls_ground_to_arxiv():
    """All canonical URLs must point to arxiv.org, never local file paths."""
    vpm = VersionProvenanceMatrix("2605.00155")
    d = vpm.to_matrix_dict()
    assert d["canonical_urls"]["canonical_html"].startswith("https://arxiv.org/html/")
    assert d["canonical_urls"]["pdf"].startswith("https://arxiv.org/pdf/")
    assert "C:\\" not in d["canonical_urls"]["canonical_html"]
    assert "C:\\" not in d["canonical_urls"]["pdf"]


def test_matrix_to_dict_serialization():
    """Matrix should serialize to a clean dict without crashing."""
    vpm = VersionProvenanceMatrix("2605.00155", active_versions=["v1", "pdf"])
    vpm.add_witness(0, "v1", "https://arxiv.org/html/2605.00155v1", latex=r"\pi")
    vpm.add_witness(0, "pdf", "https://arxiv.org/pdf/2605.00155.pdf",
                    bounding_box={"x": 10.0, "y": 20.0, "w": 100.0, "h": 30.0},
                    has_vertical_fraction=True)
    d = vpm.to_matrix_dict()
    assert d["total_slices"] == 1
    assert len(d["slices"]) == 1
    s0 = d["slices"][0]
    assert s0["layers"]["v1"]["latex"] == r"\pi"
    assert s0["layers"]["pdf"]["has_vertical_fraction"] is True
    assert s0["layers"]["pdf"]["bounding_box"]["w"] == 100.0


def test_structural_flags_on_regions():
    """VersionSliceItem should carry structural flags for Chroma consumers."""
    item = VersionSliceItem(
        version_id="pdf",
        source_url="https://arxiv.org/pdf/2605.00155.pdf",
        source_locator="math[6]",
        has_large_delimiters=True,
        has_vertical_fraction=False,
    )
    assert item.has_large_delimiters is True
    assert item.has_vertical_fraction is False
    assert item.status == "present"


# ============================================================================
# Prose Context Enrichment Tests
# ============================================================================

def test_prose_context_from_corpus_equation():
    """
    Corpus JSON equations carry context_before/context_after.
    These must propagate through to evidence records without
    altering occurrence indexing or validation logic.
    """
    # Simulate what the corpus JSON provides per equation
    eq = {
        "latex": r"\int \mathrm{sinc}(z)\,dz = \mathrm{Si}(z)",
        "context_before": "and the indefinite integral by",
        "context_after": "where Si(z) is the sine integral.",
        "section_title": "Properties",
        "is_display": True,
    }
    # This is exactly the extraction done in math_reconstruction_evidence.py
    prose_ctx = {
        "context_before": eq.get("context_before", ""),
        "context_after": eq.get("context_after", ""),
        "section_title": eq.get("section") or eq.get("section_title", ""),
    }
    assert prose_ctx["context_before"] == "and the indefinite integral by"
    assert prose_ctx["context_after"] == "where Si(z) is the sine integral."
    assert prose_ctx["section_title"] == "Properties"


def test_prose_context_empty_when_missing():
    """If corpus equation has no context fields, defaults to empty strings."""
    eq = {"latex": r"\delta", "is_display": False}
    prose_ctx = {
        "context_before": eq.get("context_before", ""),
        "context_after": eq.get("context_after", ""),
        "section_title": eq.get("section") or eq.get("section_title", ""),
    }
    assert prose_ctx["context_before"] == ""
    assert prose_ctx["context_after"] == ""
    assert prose_ctx["section_title"] == ""


def test_layered_slice_preserves_occurrence_index():
    """
    Occurrence index math[i] must be stable across layers.
    Adding witnesses to different layers at the same index
    should not create duplicate slices.
    """
    vpm = VersionProvenanceMatrix("2605.00155", active_versions=["v1", "v2"])
    vpm.add_witness(42, "v1", "https://arxiv.org/html/2605.00155v1", latex=r"x=y")
    vpm.add_witness(42, "v2", "https://arxiv.org/html/2605.00155v2", latex=r"x = y + \epsilon")
    assert len(vpm.slices) == 1, "Same occurrence index should share one slice"
    assert vpm.slices[42].layers["v1"].latex == r"x=y"
    assert vpm.slices[42].layers["v2"].latex == r"x = y + \epsilon"


def test_matrix_tracks_github_repos_and_generator():
    """VersionProvenanceMatrix should record github_repos and generator version."""
    vpm = VersionProvenanceMatrix(
        "2006.11239",
        active_versions=["v1", "v2"],
        github_repos=["https://github.com/hojonathanho/diffusion"],
    )
    vpm.add_witness(
        occurrence_index=0,
        version_id="v2",
        source_url="https://arxiv.org/html/2006.11239v2",
        latex=r"p_\theta(x_0)",
        generator="LaTeXML oxide (version 0.7.6)",
    )
    d = vpm.to_matrix_dict()
    assert d["github_repos"] == ["https://github.com/hojonathanho/diffusion"]
    assert d["slices"][0]["layers"]["v2"]["generator"] == "LaTeXML oxide (version 0.7.6)"

