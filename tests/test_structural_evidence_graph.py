"""Tests for the structural_evidence_graph module.

Verifies that:
  - build_evidence_graph produces a valid DiGraph for each registered case.
  - Known conflicts are correctly represented as explicit CONFLICT nodes.
  - Known agreements are present where the engine correctly identifies a kind.
  - Cross-modal edges exist between ground-truth and engine channels.
  - DOT and JSON export produce valid non-empty strings.
  - The module does not modify the frozen registry or evaluation report.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import networkx as nx
import pytest

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from structural_evidence_graph import (
    KIND_CONFLICT,
    REL_CONFLICTS_WITH,
    REL_SUPPORTED_BY,
    build_evidence_graph,
    export_dot,
    export_json,
    get_agreements,
    get_conflicts,
    get_channel_nodes,
    summarize_graph,
)

REGISTRY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
EVAL_REPORT_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_generalization_evaluation_v1.json"

EXPECTED_REGISTRY_SHA = "da4c166b7a5c7b1808d33b2d9f2ca0d71a0d60bf19d6844796506a51da36e6ba"
EXPECTED_REPORT_SHA = "85320ae710afe3af4cb56c626691c6c76b9f93611258610d11eb76d505614454"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def eval_report() -> dict:
    with open(EVAL_REPORT_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def graphs(registry, eval_report) -> dict[str, nx.DiGraph]:
    papers_map = {p["paper_id"]: p for p in registry["papers"]}
    eval_map = {c["case_id"]: c for c in eval_report["case_evaluations"]}
    result = {}
    for case_data in registry["cases"]:
        cid = case_data["case_id"]
        pid = case_data["parent_paper_id"]
        eng_class = eval_map[cid]["engine_classification"]
        paper_data = papers_map.get(pid)
        result[cid] = build_evidence_graph(case_data, eng_class, paper_data)
    return result


# ---------------------------------------------------------------------------
# 0. Input artifact integrity (must not be modified by the graph module)
# ---------------------------------------------------------------------------


def test_registry_sha256_unmodified():
    assert _sha256_file(REGISTRY_PATH) == EXPECTED_REGISTRY_SHA


def test_eval_report_sha256_unmodified():
    assert _sha256_file(EVAL_REPORT_PATH) == EXPECTED_REPORT_SHA


# ---------------------------------------------------------------------------
# 1. Graph structure: all three cases produce a valid DiGraph
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_graph_is_digraph(graphs, case_id):
    G = graphs[case_id]
    assert isinstance(G, nx.DiGraph)


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_graph_has_nodes(graphs, case_id):
    G = graphs[case_id]
    assert G.number_of_nodes() > 10, f"{case_id}: graph has too few nodes ({G.number_of_nodes()})"


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_graph_has_edges(graphs, case_id):
    G = graphs[case_id]
    assert G.number_of_edges() > 10, f"{case_id}: graph has too few edges ({G.number_of_edges()})"


# ---------------------------------------------------------------------------
# 2. Channel coverage: ground_truth, engine, and cross_modal nodes present
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_ground_truth_channel_present(graphs, case_id):
    G = graphs[case_id]
    nodes = get_channel_nodes(G, "ground_truth")
    assert len(nodes) > 0, f"{case_id}: no ground_truth channel nodes"


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_engine_channel_present(graphs, case_id):
    G = graphs[case_id]
    nodes = get_channel_nodes(G, "engine")
    assert len(nodes) > 0, f"{case_id}: no engine channel nodes"


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_acceptance_contract_channel_present(graphs, case_id):
    G = graphs[case_id]
    nodes = get_channel_nodes(G, "acceptance_contract")
    assert len(nodes) > 0, f"{case_id}: no acceptance_contract channel nodes"


# ---------------------------------------------------------------------------
# 3. Conflicts: verified against known evaluation results
# ---------------------------------------------------------------------------


def test_cp001_has_kind_identity_conflict(graphs):
    """CP-001: Engine classifies txexs U+F8EE as 'brace'; gold expects 'bracket'.
    This must be represented as an explicit CONFLICT node, not a silent failure.
    """
    G = graphs["CP-001-CLUSTER-GCN-BMATRIX"]
    conflicts = get_conflicts(G)
    kind_conflicts = [c for c in conflicts if c.get("dimension") == "kind_identity"]
    assert len(kind_conflicts) >= 1, "CP-001 missing kind_identity CONFLICT node"
    c = kind_conflicts[0]
    assert "bracket" in c.get("gold_says", ""), f"Expected gold bracket in conflict: {c}"
    assert c.get("engine_says") == "brace", f"Expected engine=brace in conflict: {c}"


def test_cp002_has_agreement_no_conflict(graphs):
    """CP-002: CMR10 brackets correctly recognized by engine.
    Should have agreement node, no kind_identity conflict.
    """
    G = graphs["CP-002-VILT-NESTED-BRACKETS"]
    agreements = get_agreements(G)
    assert len(agreements) >= 1, "CP-002 missing agreement node (CMR10 bracket should be recognized)"

    conflicts = get_conflicts(G)
    kind_conflicts = [c for c in conflicts if c.get("dimension") == "kind_identity"]
    assert len(kind_conflicts) == 0, f"CP-002 unexpected kind_identity conflict: {kind_conflicts}"


def test_cp003_has_unresolved_conflict(graphs):
    """CP-003: LMMathExtension10 U+000D classified as 'unknown' by engine.
    Gold expects 'norm'. Must be an explicit CONFLICT node.
    """
    G = graphs["CP-003-LINEAR-PROBING-NORM"]
    conflicts = get_conflicts(G)
    kind_conflicts = [c for c in conflicts if c.get("dimension") == "kind_identity"]
    assert len(kind_conflicts) >= 1, "CP-003 missing kind_identity CONFLICT node"
    c = kind_conflicts[0]
    assert "norm" in c.get("gold_says", ""), f"Expected norm in gold_says: {c}"
    assert c.get("engine_says") == "unresolved", f"Expected engine=unresolved: {c}"


# ---------------------------------------------------------------------------
# 4. Conflict edges go through the graph
# ---------------------------------------------------------------------------


def test_cp001_conflict_has_incoming_edges(graphs):
    G = graphs["CP-001-CLUSTER-GCN-BMATRIX"]
    conflicts = [n for n, a in G.nodes(data=True) if a.get("kind") == KIND_CONFLICT]
    for cn in conflicts:
        preds = list(G.predecessors(cn))
        assert len(preds) >= 2, f"Conflict node {cn} has fewer than 2 incoming edges: {preds}"


def test_cp003_conflict_has_incoming_edges(graphs):
    G = graphs["CP-003-LINEAR-PROBING-NORM"]
    conflicts = [n for n, a in G.nodes(data=True) if a.get("kind") == KIND_CONFLICT]
    for cn in conflicts:
        preds = list(G.predecessors(cn))
        assert len(preds) >= 2, f"Conflict node {cn} has fewer than 2 incoming edges: {preds}"


# ---------------------------------------------------------------------------
# 5. Export: DOT and JSON
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_export_dot_non_empty(graphs, case_id):
    G = graphs[case_id]
    dot = export_dot(G)
    assert dot.startswith("digraph"), f"{case_id}: DOT output does not start with 'digraph'"
    assert len(dot) > 200, f"{case_id}: DOT output suspiciously short ({len(dot)} chars)"


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_export_json_valid(graphs, case_id):
    G = graphs[case_id]
    json_str = export_json(G)
    parsed = json.loads(json_str)
    assert "nodes" in parsed, f"{case_id}: JSON export missing 'nodes'"
    # NetworkX >= 3.4 uses 'edges'; earlier versions use 'links'
    assert "edges" in parsed or "links" in parsed, f"{case_id}: JSON export missing 'edges'/'links'"
    assert len(parsed["nodes"]) == G.number_of_nodes()


# ---------------------------------------------------------------------------
# 6. Summarize graph utility
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
])
def test_summarize_graph_keys(graphs, case_id):
    G = graphs[case_id]
    summary = summarize_graph(G)
    for key in ("total_nodes", "total_edges", "conflict_count", "agreement_count",
                "nodes_by_channel", "conflicts"):
        assert key in summary, f"{case_id}: summarize_graph missing key '{key}'"


def test_cp001_summary_conflict_count(graphs):
    G = graphs["CP-001-CLUSTER-GCN-BMATRIX"]
    summary = summarize_graph(G)
    assert summary["conflict_count"] >= 1


def test_cp002_summary_agreement_count(graphs):
    G = graphs["CP-002-VILT-NESTED-BRACKETS"]
    summary = summarize_graph(G)
    assert summary["agreement_count"] >= 1


def test_cp003_summary_conflict_count(graphs):
    G = graphs["CP-003-LINEAR-PROBING-NORM"]
    summary = summarize_graph(G)
    assert summary["conflict_count"] >= 1
