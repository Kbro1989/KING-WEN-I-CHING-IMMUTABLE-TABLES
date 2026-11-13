"""Structural Evidence Graph: Cross-modal evidence representation for delimiter recovery.

Builds a directed graph of structural evidence across all extraction channels
(PDF text stream, font/glyph identity, geometry, continuation topology, gold AST)
for a single recovered mathematical candidate.

Design principles (from ContractShield arXiv:2604.02771 architecture):
  - Each evidence channel is represented as an independent sub-graph (intra-modal).
  - Explicit cross-modal edges link corresponding observations across channels.
  - Disagreements between channels are preserved as explicit CONFLICT nodes,
    not silently resolved by a scoring function.
  - Every node carries provenance (source, coordinates, hashes) as attributes.

This module is a non-invasive diagnostic layer.
  - It does NOT modify the frozen engine (delimiter_aware_structural_recovery.py).
  - It does NOT modify the registry or acceptance specification.
  - It operates on evaluation report data and registry data as read-only inputs.

Output formats:
  - networkx.DiGraph (authoritative in-memory graph)
  - DOT-format string (via networkx.drawing.nx_pydot or manual serialization)
  - JSON adjacency list (for persistent artifact storage)

Usage:
    from scripts.structural_evidence_graph import build_evidence_graph, export_dot, export_json

    graph = build_evidence_graph(case_data, engine_classification)
    dot_text = export_dot(graph)
    json_text = export_json(graph)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import networkx as nx


# ---------------------------------------------------------------------------
# Node kinds (used as the 'kind' attribute on every node)
# ---------------------------------------------------------------------------
KIND_PAPER_RECORD = "paper_record"
KIND_PAGE = "page"
KIND_DISPLAY_BBOX = "display_bbox"
KIND_GOLD_AST = "gold_ast"
KIND_FONT_GLYPH_INVENTORY = "font_glyph_inventory"
KIND_GLYPH_PIECE = "glyph_piece"
KIND_ASSEMBLED_DELIMITER = "assembled_delimiter"
KIND_DELIMITER_PAIR = "delimiter_pair"
KIND_ENCLOSURE = "enclosure"
KIND_GRID_TOPOLOGY = "grid_topology"
KIND_CONTINUATION_SYMBOL = "continuation_symbol"
KIND_BOUNDARY_CONSTRAINT = "boundary_constraint"
KIND_NEGATIVE_CONTROL = "negative_control"
KIND_DIM_CLAIM = "dimension_claim"
KIND_TERMINAL_VERDICT = "terminal_verdict"
KIND_CONFLICT = "conflict"
KIND_EVIDENCE_CHANNEL = "evidence_channel"


# ---------------------------------------------------------------------------
# Edge relation labels
# ---------------------------------------------------------------------------
REL_HAS_PAGE = "has_page"
REL_CONTAINS = "contains"
REL_GOLD_FOR = "gold_for"
REL_HAS_PIECE = "has_piece"
REL_ASSEMBLES_TO = "assembles_to"
REL_PAIRS_WITH = "pairs_with"
REL_ENCLOSES = "encloses"
REL_HAS_ROW = "has_row"
REL_HAS_CELL = "has_cell"
REL_HAS_CONTINUATION = "has_continuation"
REL_SUPPORTED_BY = "supported_by"
REL_CONSTRAINED_BY = "constrained_by"
REL_CONFLICTS_WITH = "conflicts_with"
REL_EVALUATES_TO = "evaluates_to"
REL_AGGREGATES = "aggregates"
REL_OBSERVED_BY = "observed_by"


def _node(graph: nx.DiGraph, node_id: str, **attrs) -> str:
    """Add a node to graph with attributes, return node_id."""
    graph.add_node(node_id, **attrs)
    return node_id


def _edge(graph: nx.DiGraph, src: str, dst: str, relation: str, **attrs):
    """Add a directed edge with a relation label."""
    graph.add_edge(src, dst, relation=relation, **attrs)


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_evidence_graph(
    case_data: dict,
    engine_classification: dict,
    paper_data: dict | None = None,
    eval_results: dict | None = None,
) -> nx.DiGraph:
    """Build a cross-modal structural evidence graph for a single case.

    Parameters
    ----------
    case_data:
        A case record from cross_paper_case_registry_v1.json.
    engine_classification:
        The engine_classification block from the evaluation report for this case
        (keys: opening, closing, paired).
    paper_data:
        The paper record for the case's parent paper (optional enrichment).
    eval_results:
        The full case evaluation block from the evaluation report (optional).
        When provided, dimension verdict nodes and negative control verdict
        nodes carry actual PASS/FAIL/NOT_VERIFIED status and are linked to
        their specific source evidence nodes. When absent, verdict is NOT_VERIFIED.

    Returns
    -------
    nx.DiGraph with all structural evidence nodes, cross-modal edges,
    CONFLICT/AGREE cross-modal nodes, and per-axis verdict nodes linked
    to their specific source evidence.
    """
    G = nx.DiGraph()
    cid = case_data["case_id"]
    pid = case_data.get("parent_paper_id", "unknown_paper")

    # ------------------------------------------------------------------
    # Level 0: Paper and page provenance
    # ------------------------------------------------------------------
    paper_node = _node(G, f"paper:{pid}", kind=KIND_PAPER_RECORD,
                       paper_id=pid,
                       label=f"Paper\\n{pid}")
    if paper_data:
        G.nodes[paper_node]["font_family"] = paper_data.get("math_font_family", "unknown")
        G.nodes[paper_node]["pdf_sha256"] = paper_data.get("pdf_sha256", "")[:16] + "..."

    page_idx = case_data.get("source_location", {}).get("page_0based", "?")
    page_node = _node(G, f"page:{pid}:p{page_idx}", kind=KIND_PAGE,
                      page_0based=page_idx,
                      label=f"Page {page_idx}")
    _edge(G, paper_node, page_node, REL_HAS_PAGE)

    # ------------------------------------------------------------------
    # Level 1: Display bounding box (independent ground truth)
    # ------------------------------------------------------------------
    disp_bbox = case_data.get("exact_display_bbox_pdf_pt", [])
    bbox_node = _node(G, f"bbox:{cid}", kind=KIND_DISPLAY_BBOX,
                      bbox=disp_bbox,
                      label=f"Display BBox\\n{disp_bbox}",
                      channel="ground_truth")
    _edge(G, page_node, bbox_node, REL_CONTAINS)

    # ------------------------------------------------------------------
    # Level 2: Gold AST (independent ground truth channel)
    # ------------------------------------------------------------------
    gold_ast = case_data.get("gold_ast", {})
    gold_node = _node(G, f"gold_ast:{cid}", kind=KIND_GOLD_AST,
                      delimiter_type=gold_ast.get("environment_type", "unknown"),
                      structure_type=gold_ast.get("grid_topology", {}).get("structure_type", "unknown"),
                      transcription=case_data.get("transcription", "")[:80],
                      label=f"Gold AST\\nenv={gold_ast.get('environment_type','?')}",
                      channel="ground_truth")
    _edge(G, bbox_node, gold_node, REL_GOLD_FOR)

    # ------------------------------------------------------------------
    # Level 3: Glyph inventory (independent ground truth channel)
    # ------------------------------------------------------------------
    glyph_inv = case_data.get("delimiter_glyph_inventory", {})

    for side in ("opening", "closing"):
        side_data = glyph_inv.get(side, {})
        if not side_data:
            continue

        delim_node = _node(G, f"delim:{cid}:{side}", kind=KIND_ASSEMBLED_DELIMITER,
                           side=side,
                           font=side_data.get("font_name", "?"),
                           pieces_count=side_data.get("pieces_count", 0),
                           bbox=side_data.get("bbox", []),
                           label=f"Delimiter\\n{side}\\n{side_data.get('font_name','?')}",
                           channel="ground_truth")
        _edge(G, bbox_node, delim_node, REL_CONTAINS)

        # Individual glyph pieces
        for i, piece in enumerate(side_data.get("glyph_codes", [])):
            piece_node = _node(G, f"piece:{cid}:{side}:{i}", kind=KIND_GLYPH_PIECE,
                               index=i,
                               glyph_code=piece,
                               role=side_data.get("piece_roles", ["?"] * 10)[i] if i < len(side_data.get("piece_roles", [])) else "unknown",
                               label=f"Glyph\\n{piece}",
                               channel="ground_truth")
            _edge(G, delim_node, piece_node, REL_HAS_PIECE)

    # Pairing claim (ground truth)
    if "opening" in glyph_inv and "closing" in glyph_inv:
        pair_gt_node = _node(G, f"pair_gt:{cid}", kind=KIND_DELIMITER_PAIR,
                             source="ground_truth",
                             delimiter_type=gold_ast.get("delimiter_type", "unknown"),
                             label="GT Pair\\n(ground truth)",
                             channel="ground_truth")
        _edge(G, f"delim:{cid}:opening", pair_gt_node, REL_PAIRS_WITH)
        _edge(G, f"delim:{cid}:closing", pair_gt_node, REL_PAIRS_WITH)

    # ------------------------------------------------------------------
    # Level 4: Continuation symbols (ground truth channel)
    # continuation_marker_inventory is a list of dicts, each with a 'role' key
    # ------------------------------------------------------------------
    cont_inv = case_data.get("continuation_marker_inventory", [])
    if isinstance(cont_inv, list):
        for j, sym in enumerate(cont_inv):
            sym_type = sym.get("role", f"continuation_{j}")
            cont_node = _node(G, f"cont:{cid}:{j}", kind=KIND_CONTINUATION_SYMBOL,
                              sym_type=sym_type,
                              bbox=sym.get("bbox", []),
                              label=f"Continuation\\n{sym_type[:20]}[{j}]",
                              channel="ground_truth")
            _edge(G, gold_node, cont_node, REL_HAS_CONTINUATION)
    elif isinstance(cont_inv, dict):
        for sym_type, sym_list in cont_inv.items():
            if not isinstance(sym_list, list):
                continue
            for j, sym in enumerate(sym_list):
                cont_node = _node(G, f"cont:{cid}:{sym_type}:{j}", kind=KIND_CONTINUATION_SYMBOL,
                                  sym_type=sym_type,
                                  bbox=sym.get("bbox", []),
                                  label=f"Continuation\\n{sym_type}[{j}]",
                                  channel="ground_truth")
                _edge(G, gold_node, cont_node, REL_HAS_CONTINUATION)

    # ------------------------------------------------------------------
    # Level 5: Engine observation channel
    # ------------------------------------------------------------------
    eng_open = engine_classification.get("opening", {})
    eng_close = engine_classification.get("closing", {})
    eng_paired = engine_classification.get("paired", False)

    eng_open_node = _node(G, f"eng_open:{cid}", kind=KIND_ASSEMBLED_DELIMITER,
                          side="opening",
                          kind_classified=eng_open.get("kind", "unknown"),
                          family=eng_open.get("family", "unknown"),
                          confidence=eng_open.get("confidence", 0.0),
                          resolution_method=eng_open.get("resolution_method", "?"),
                          font_lineage=eng_open.get("font_lineage", []),
                          raw_characters=eng_open.get("raw_characters", []),
                          label=f"Engine\\nOpening\\nkind={eng_open.get('kind','?')}",
                          channel="engine")
    _edge(G, bbox_node, eng_open_node, REL_OBSERVED_BY)

    eng_close_node = _node(G, f"eng_close:{cid}", kind=KIND_ASSEMBLED_DELIMITER,
                           side="closing",
                           kind_classified=eng_close.get("kind", "unknown"),
                           family=eng_close.get("family", "unknown"),
                           confidence=eng_close.get("confidence", 0.0),
                           resolution_method=eng_close.get("resolution_method", "?"),
                           font_lineage=eng_close.get("font_lineage", []),
                           raw_characters=eng_close.get("raw_characters", []),
                           label=f"Engine\\nClosing\\nkind={eng_close.get('kind','?')}",
                           channel="engine")
    _edge(G, bbox_node, eng_close_node, REL_OBSERVED_BY)

    # Engine pairing result
    pair_eng_node = _node(G, f"pair_eng:{cid}", kind=KIND_DELIMITER_PAIR,
                          source="engine",
                          paired=eng_paired,
                          label=f"Engine Pair\\n{'FORMED' if eng_paired else 'UNPAIRED'}",
                          channel="engine")
    _edge(G, eng_open_node, pair_eng_node, REL_PAIRS_WITH)
    _edge(G, eng_close_node, pair_eng_node, REL_PAIRS_WITH)

    # ------------------------------------------------------------------
    # Level 6: Cross-modal agreement / conflict detection
    # ------------------------------------------------------------------
    gt_env_type = gold_ast.get("environment_type", "unknown")
    eng_kind_open = eng_open.get("kind", "unknown")

    # Map gold environment_type to expected classified kind
    env_to_kind = {
        "bmatrix": "bracket",
        "Bmatrix": "brace",
        "pmatrix": "parenthesis",
        "vmatrix": "vertical_bar",
        "nested_sequence_vector": "bracket",
        "extended_norm_squared_with_embedded_math": "norm",
        "norm": "norm",
    }
    expected_kind = env_to_kind.get(gt_env_type, "unknown")

    if expected_kind != "unknown" and eng_kind_open != "unknown":
        if eng_kind_open == expected_kind:
            # Agreement node
            agree_node = _node(G, f"agree_kind:{cid}", kind="agreement",
                               dimension="kind_identity",
                               gold=gt_env_type, engine=eng_kind_open,
                               label=f"AGREE\\nkind={eng_kind_open}",
                               channel="cross_modal")
            _edge(G, gold_node, agree_node, REL_SUPPORTED_BY)
            _edge(G, eng_open_node, agree_node, REL_SUPPORTED_BY)
        else:
            # Explicit conflict node
            conflict_node = _node(G, f"conflict_kind:{cid}", kind=KIND_CONFLICT,
                                  dimension="kind_identity",
                                  gold_says=f"{gt_env_type}→{expected_kind}",
                                  engine_says=eng_kind_open,
                                  label=f"CONFLICT\\nGold: {expected_kind}\\nEngine: {eng_kind_open}",
                                  channel="cross_modal")
            _edge(G, gold_node, conflict_node, REL_CONFLICTS_WITH)
            _edge(G, eng_open_node, conflict_node, REL_CONFLICTS_WITH)
    elif expected_kind != "unknown" and eng_kind_open == "unknown":
        # Engine produced no classification — another kind of conflict
        conflict_node = _node(G, f"conflict_unresolved:{cid}", kind=KIND_CONFLICT,
                              dimension="kind_identity",
                              gold_says=f"{gt_env_type}→{expected_kind}",
                              engine_says="unresolved",
                              label=f"CONFLICT\\nGold: {expected_kind}\\nEngine: unresolved",
                              channel="cross_modal")
        _edge(G, gold_node, conflict_node, REL_CONFLICTS_WITH)
        _edge(G, eng_open_node, conflict_node, REL_CONFLICTS_WITH)

    # Pairing conflict check
    gt_has_pair = ("opening" in glyph_inv and "closing" in glyph_inv)
    if gt_has_pair != eng_paired:
        pair_conflict = _node(G, f"conflict_pair:{cid}", kind=KIND_CONFLICT,
                              dimension="pairing",
                              gold_says=str(gt_has_pair),
                              engine_says=str(eng_paired),
                              label=f"CONFLICT\\nPairing\\nGT={gt_has_pair} Eng={eng_paired}",
                              channel="cross_modal")
        _edge(G, gold_node, pair_conflict, REL_CONFLICTS_WITH)
        _edge(G, pair_eng_node, pair_conflict, REL_CONFLICTS_WITH)

    # ------------------------------------------------------------------
    # Level 7: Five-axis dimension verdict nodes (first-class evaluation artifacts)
    #
    # Each dimension node records:
    #   - The registry criterion (independent ground truth expectation)
    #   - The evaluation report verdict (PASS / FAIL / NOT_VERIFIED)
    #   - Edges to the specific source evidence nodes it evaluates
    # ------------------------------------------------------------------
    dim_verdicts = {}
    if eval_results is not None:
        for d, r in eval_results.get("five_dimension_results", {}).items():
            dim_verdicts[d] = r.get("status", "NOT_VERIFIED")

    dim_evidence_links = {
        "dim_1_geometric_localization": [bbox_node, pair_eng_node],
        "dim_2_glyph_completeness":     [eng_open_node, eng_close_node,
                                         f"delim:{cid}:opening", f"delim:{cid}:closing"],
        "dim_3_structural_recovery":    [pair_eng_node],
        "dim_4_semantic_fidelity":      [gold_node, eng_open_node, pair_eng_node],
        "dim_5_boundary_isolation":     [bbox_node, pair_eng_node],
    }

    for dim_id, dim_criterion in case_data.get("five_axis_acceptance_criteria", {}).items():
        verdict = dim_verdicts.get(dim_id, "NOT_VERIFIED")
        dim_node = _node(G, f"dim:{cid}:{dim_id}", kind=KIND_DIM_CLAIM,
                         dimension=dim_id,
                         criterion=dim_criterion.get("criterion", ""),
                         required=dim_criterion.get("required", "PASS"),
                         verdict=verdict,
                         label=f"Dim\\n{dim_id}\\n{verdict}",
                         channel="acceptance_contract")
        # Link to specific evidence sources for this dimension
        for src_node_id in dim_evidence_links.get(dim_id, []):
            if G.has_node(src_node_id):
                _edge(G, src_node_id, dim_node, REL_SUPPORTED_BY)
        # If verdict is FAIL, also link any active conflict nodes
        if verdict == "FAIL":
            for n, attrs in G.nodes(data=True):
                if attrs.get("kind") == KIND_CONFLICT:
                    _edge(G, n, dim_node, REL_SUPPORTED_BY,
                          note="conflict contributes to dimension failure")

    # ------------------------------------------------------------------
    # Level 8: Negative controls with actual verdict from evaluation report
    # ------------------------------------------------------------------
    nc_verdicts = {}
    if eval_results is not None:
        for n in eval_results.get("negative_control_results", []):
            nc_verdicts[n["control_id"]] = n.get("status", "NOT_VERIFIED")

    for nc in case_data.get("negative_control_pairs", []):
        nc_id = nc["control_id"]
        nc_verdict = nc_verdicts.get(nc_id, "NOT_VERIFIED")
        nc_node = _node(G, f"nc:{cid}:{nc_id}", kind=KIND_NEGATIVE_CONTROL,
                        control_id=nc_id,
                        verdict=nc_verdict,
                        expected_rejection=nc.get("expected_rejection_reason", ""),
                        label=f"NEG\\n{nc_id.replace('NEG_','')[:20]}\\n{nc_verdict}",
                        channel="negative_control")
        _edge(G, pair_eng_node, nc_node, REL_CONSTRAINED_BY)

    # ------------------------------------------------------------------
    # Level 9: Boundary constraints
    # ------------------------------------------------------------------
    for bc in case_data.get("five_axis_acceptance_criteria", {}).get(
        "dim_5_boundary_isolation", {}
    ).get("criterion", "").split(";"):
        if bc.strip():
            bc_node = _node(G, f"bc:{cid}:{hash(bc) % 9999}", kind=KIND_BOUNDARY_CONSTRAINT,
                            constraint=bc.strip(),
                            label=f"BoundaryConstraint\\n{bc.strip()[:30]}",
                            channel="acceptance_contract")
            _edge(G, bbox_node, bc_node, REL_CONSTRAINED_BY)

    return G


# ---------------------------------------------------------------------------
# DOT export (manual, no pygraphviz required)
# ---------------------------------------------------------------------------

def _escape_dot(s: str) -> str:
    """Escape a string for DOT node label."""
    return str(s).replace('"', '\\"').replace('\n', '\\n')


def export_dot(G: nx.DiGraph, graph_label: str = "Structural Evidence Graph") -> str:
    """Export a NetworkX DiGraph to Graphviz DOT format.

    Uses manual serialization so no pygraphviz or pydot installation is required.
    Compatible with Graphviz CLI (dot, neato) if installed separately.
    """
    lines = [
        'digraph evidence_graph {',
        f'  label="{_escape_dot(graph_label)}";',
        '  labelloc=t;',
        '  rankdir=TB;',
        '  node [fontname="Helvetica", fontsize=10];',
        '  edge [fontname="Helvetica", fontsize=9];',
        '',
    ]

    # Channel → shape/color mapping
    channel_style = {
        "ground_truth": 'shape=box, style=filled, fillcolor="#d4edda", color="#28a745"',
        "engine":       'shape=ellipse, style=filled, fillcolor="#cce5ff", color="#004085"',
        "cross_modal":  'shape=diamond, style=filled, fillcolor="#fff3cd", color="#856404"',
        "acceptance_contract": 'shape=hexagon, style=filled, fillcolor="#f8d7da", color="#721c24"',
        "negative_control": 'shape=octagon, style=filled, fillcolor="#e2e3e5", color="#383d41"',
    }
    conflict_style = 'shape=doubleoctagon, style=filled, fillcolor="#f5c6cb", color="#721c24"'

    for node_id, attrs in G.nodes(data=True):
        node_kind = attrs.get("kind", "")
        channel = attrs.get("channel", "")
        label = _escape_dot(attrs.get("label", node_id))
        safe_id = _escape_dot(node_id).replace(":", "_").replace(" ", "_")

        if node_kind == KIND_CONFLICT:
            style = conflict_style
        else:
            style = channel_style.get(channel, 'shape=plaintext')

        lines.append(f'  "{safe_id}" [{style}, label="{label}"];')

    lines.append('')

    for src, dst, attrs in G.edges(data=True):
        relation = attrs.get("relation", "")
        safe_src = _escape_dot(src).replace(":", "_").replace(" ", "_")
        safe_dst = _escape_dot(dst).replace(":", "_").replace(" ", "_")
        lines.append(f'  "{safe_src}" -> "{safe_dst}" [label="{relation}"];')

    lines.append('}')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# JSON export (authoritative structured artifact)
# ---------------------------------------------------------------------------

def export_json(G: nx.DiGraph) -> str:
    """Export a NetworkX DiGraph to JSON adjacency format.

    The JSON format is the authoritative storage format.
    DOT is a rendering/export layer.
    """
    data = nx.node_link_data(G)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Conflict and agreement inspection utilities
# ---------------------------------------------------------------------------

def get_conflicts(G: nx.DiGraph) -> list[dict]:
    """Return all CONFLICT nodes with their attributes."""
    return [
        {"node_id": n, **attrs}
        for n, attrs in G.nodes(data=True)
        if attrs.get("kind") == KIND_CONFLICT
    ]


def get_agreements(G: nx.DiGraph) -> list[dict]:
    """Return all agreement nodes."""
    return [
        {"node_id": n, **attrs}
        for n, attrs in G.nodes(data=True)
        if attrs.get("kind") == "agreement"
    ]


def get_channel_nodes(G: nx.DiGraph, channel: str) -> list[dict]:
    """Return all nodes from a specific evidence channel."""
    return [
        {"node_id": n, **attrs}
        for n, attrs in G.nodes(data=True)
        if attrs.get("channel") == channel
    ]


def summarize_graph(G: nx.DiGraph) -> dict:
    """Return a brief summary of the evidence graph."""
    conflicts = get_conflicts(G)
    agreements = get_agreements(G)
    channels = {}
    for _, attrs in G.nodes(data=True):
        ch = attrs.get("channel", "unassigned")
        channels[ch] = channels.get(ch, 0) + 1

    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "conflict_count": len(conflicts),
        "agreement_count": len(agreements),
        "nodes_by_channel": channels,
        "conflicts": [
            {
                "node_id": c["node_id"],
                "dimension": c.get("dimension"),
                "gold_says": c.get("gold_says"),
                "engine_says": c.get("engine_says"),
            }
            for c in conflicts
        ],
    }


# ---------------------------------------------------------------------------
# CLI entry point: build graphs for all three cross-paper cases
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
    REGISTRY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
    EVAL_REPORT = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_generalization_evaluation_v1.json"
    OUT_DIR = REPO_ROOT / "DATASETS" / "structural_preservation" / "evidence_graphs"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(REGISTRY_PATH, encoding="utf-8") as f:
        registry = json.load(f)
    with open(EVAL_REPORT, encoding="utf-8") as f:
        eval_report = json.load(f)

    papers_map = {p["paper_id"]: p for p in registry["papers"]}
    eval_map = {c["case_id"]: c for c in eval_report["case_evaluations"]}

    all_summaries = []
    for case_data in registry["cases"]:
        cid = case_data["case_id"]
        pid = case_data["parent_paper_id"]
        eng_class = eval_map[cid]["engine_classification"]
        paper_data = papers_map.get(pid)
        eval_results = eval_map[cid]  # full case evaluation block

        G = build_evidence_graph(case_data, eng_class, paper_data, eval_results)
        summary = summarize_graph(G)
        summary["case_id"] = cid
        all_summaries.append(summary)

        # Write DOT
        dot_path = OUT_DIR / f"{cid.lower().replace('-', '_')}_evidence.dot"
        with open(dot_path, "w", encoding="utf-8") as f:
            f.write(export_dot(G, graph_label=f"Evidence Graph: {cid}"))
        print(f"[{cid}] DOT -> {dot_path}")

        # Write JSON
        json_path = OUT_DIR / f"{cid.lower().replace('-', '_')}_evidence.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(export_json(G))
        print(f"[{cid}] JSON -> {json_path}")

        print(f"  Nodes: {summary['total_nodes']}  Edges: {summary['total_edges']}  "
              f"Conflicts: {summary['conflict_count']}  Agreements: {summary['agreement_count']}")
        for conf in summary["conflicts"]:
            print(f"    CONFLICT [{conf['dimension']}]  gold={conf['gold_says']}  engine={conf['engine_says']}")

    # Write combined summary
    summary_path = OUT_DIR / "evidence_graph_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)
    print(f"\nSummary -> {summary_path}")
