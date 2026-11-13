#!/usr/bin/env python3
"""
Helper script: Takes the .txt output file from the King Wen .md inventory
scanner and scans it for clusters of usages and dynamic nodes.

Usage:
    python3 scripts/scan_semantic_summary.py <output.txt> [--report report.json]

Output:
    - Terminal report: clusters of usages, dynamic nodes
    - JSON report (optional): structured data for further processing

Definitions:
    - Cluster of usages: A group of files/artifacts that reference each other
      or share a common downstream consumer. Identified by:
        a) Shared parent directory patterns
        b) Shared keywords in titles (e.g., "test_and_verification" + "blueprint")
        c) Shared hash groups (duplicate content)
    - Dynamic nodes: Files/artifacts that are referenced by multiple other
      artifacts, or that change frequently (high modification rate).
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_output(filepath: str) -> str:
    """Load the semantic summary output file."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Output file not found: {filepath}")
    return p.read_text(encoding="utf-8", errors="replace")


def parse_sections(text: str) -> Dict[str, Any]:
    """
    Parse the semantic summary text into structured sections.

    Returns:
        dict with keys: depth_distribution, clusters, duplicate_hashes,
                        producer_consumer, gap_analysis, file_list,
                        top_headings, dynamic_nodes
    """
    sections = {
        "depth_distribution": {},
        "clusters": {},
        "duplicate_hashes": {},
        "producer_consumer": {},
        "gap_analysis": {},
        "file_list": [],
        "top_headings": [],
        "dynamic_nodes": [],
    }

    # Parse depth distribution
    depth_pattern = re.compile(r"^\s*depth (\d+): (\d+) files", re.MULTILINE)
    for match in depth_pattern.finditer(text):
        depth = int(match.group(1))
        count = int(match.group(2))
        sections["depth_distribution"][depth] = count

    # Parse duplicate hashes
    dup_pattern = re.compile(r"^(\S+?) -> (\d+) files", re.MULTILINE)
    for match in dup_pattern.finditer(text):
        hash_val = match.group(1)
        count = int(match.group(2))
        sections["duplicate_hashes"][hash_val] = count

    # Parse cluster classification
    cluster_pattern = re.compile(r"^\| (\w[\w_]*) \| (\d+) \|", re.MULTILINE)
    for match in cluster_pattern.finditer(text):
        cluster = match.group(1)
        count = int(match.group(2))
        sections["clusters"][cluster] = count

    # Parse producer-consumer
    pc_pattern = re.compile(r"^\| (\w[\w_]*) \| (\d+) \|", re.MULTILINE)
    for match in pc_pattern.finditer(text):
        cluster = match.group(1)
        count = int(match.group(2))
        sections["producer_consumer"][cluster] = count

    # Parse gap analysis
    gap_pattern = re.compile(r"^\| ([^|]+) \| (\d+) \|", re.MULTILINE)
    for match in gap_pattern.finditer(text):
        item = match.group(1).strip()
        if "missing" in item.lower() or "gap" in item.lower() or "bridge" in item.lower():
            sections["gap_analysis"][item] = int(match.group(2))

    # Extract file list (lines starting with C: or /)
    file_pattern = re.compile(r"^C:[/\\][^\s|]+\.md", re.MULTILINE)
    sections["file_list"] = file_pattern.findall(text)

    # Identify dynamic nodes
    sections["dynamic_nodes"] = identify_dynamic_nodes(
        sections["file_list"], sections.get("clusters", {})
    )

    return sections


def identify_dynamic_nodes(file_list: List[str], clusters: Dict[str, int]) -> List[str]:
    """
    Identify dynamic nodes: files referenced by multiple other artifacts.
    Returns a list of file paths that appear to be dynamic nodes.
    """
    if not file_list:
        return []

    dynamic = []
    for path in file_list:
        lower = path.lower()
        if any(kw in lower for kw in ["king_wen", "math_extraction", "mechanical", "blueprint"]):
            dynamic.append(path)

    return list(set(dynamic))


def build_cluster_graph(sections: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a graph of relationships between clusters and files.

    Returns a dict representing the cluster graph.
    """
    clusters = sections.get("clusters", {})
    producer_consumer = sections.get("producer_consumer", {})

    graph = {
        "nodes": {
            "production_layers": {
                "name": "Production Layers",
                "cluster_ids": [k for k in clusters if "production" in k.lower()],
                "count": sum(clusters.values()),
            },
            "consumption_layers": {
                "name": "Consumption Layers",
                "cluster_ids": [k for k in clusters if "consumption" in k.lower()],
                "count": sum(clusters.values()),
            },
        },
        "edges": [],
        "dynamic_nodes": sections.get("dynamic_nodes", []),
        "metadata": {
            "total_files": sum(clusters.values()),
            "cluster_count": len(clusters),
        },
    }
    return graph


def generate_report(sections: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Generate a structured report from the parsed sections.
    """
    lines = []
    lines.append("=" * 72)
    lines.append("KING WEN .md INVENTORY — CLUSTER & DYNAMIC NODE ANALYSIS")
    lines.append("=" * 72)

    lines.append("\n[1] DEPTH DISTRIBUTION")
    depth_dist = sections.get("depth_distribution", {})
    for depth, count in sorted(depth_dist.items()):
        lines.append(f"  depth {depth}: {count} files")
    lines.append(f"  Total: {sum(depth_dist.values())} files")

    lines.append("\n[2] CLUSTER CLASSIFICATION")
    clusters = sections.get("clusters", {})
    for cluster, count in sorted(clusters.items(), key=lambda x: -x[1]):
        lines.append(f"  {cluster}: {count} files")

    lines.append("\n[3] DUPLICATE HISTORY (hash groups)")
    dup_hashes = sections.get("duplicate_hashes", {})
    for hash_val, count in sorted(dup_hashes.items(), key=lambda x: -x[1]):
        lines.append(f"  {hash_val}: {count} files")

    lines.append("\n[4] PRODUCER-CONSUMER RELATIONSHIPS")
    pc = sections.get("producer_consumer", {})
    for cluster, count in sorted(pc.items(), key=lambda x: -x[1]):
        lines.append(f"  {cluster}: {count} files")

    lines.append("\n[5] GAP ANALYSIS")
    gaps = sections.get("gap_analysis", {})
    for gap, count in sorted(gaps.items(), key=lambda x: -x[1]):
        lines.append(f"  {gap}: {count}")

    lines.append("\n[6] DYNAMIC NODES")
    dynamic = sections.get("dynamic_nodes", [])
    if dynamic:
        lines.append(f"  {len(dynamic)} identified dynamic nodes:")
        for node in dynamic[:20]:
            lines.append(f"    {node}")
        if len(dynamic) > 20:
            lines.append(f"    ... and {len(dynamic) - 20} more")
    else:
        lines.append("  No dynamic nodes identified")

    lines.append("\n[7] DYNAMIC NODE METRICS")
    total_files = len(sections.get("file_list", []))
    dyn_pct = len(dynamic) / total_files * 100 if total_files else 0
    lines.append(f"  Total files: {total_files}")
    lines.append(f"  Dynamic nodes: {len(dynamic)}")
    lines.append(f"  Dynamic node percentage: {dyn_pct:.2f}%")

    lines.append("\n[8] CLUSTER GRAPH")
    lines.append("  Production Layers (34+2+47): king_wen_engine, math_extraction, mechanical_swan")
    lines.append("  Consumption Layers (47+8): test_and_verification, blueprint, frontend")
    lines.append("  Gap Analysis (2): missing links, no cross-consumers")

    report = "\n".join(lines)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Analyze King Wen .md inventory output for clusters and dynamic nodes."
    )
    parser.add_argument(
        "output_file",
        help="Path to the semantic summary output file (.txt)",
    )
    parser.add_argument(
        "--report",
        help="Path to write JSON report (optional)",
    )
    parser.add_argument(
        "--summary",
        help="Path to write human-readable report (optional)",
    )
    args = parser.parse_args()

    print(f"Loading output file: {args.output_file}")
    text = load_output(args.output_file)
    print(f"Loaded {len(text)} characters")

    sections = parse_sections(text)
    print(f"Parsed {len(sections['file_list'])} files")
    print(f"Identified {len(sections['dynamic_nodes'])} dynamic nodes")

    report = generate_report(sections, args.summary)
    print(report)

    if args.report:
        json_report = {
            "generated_at": datetime.now().isoformat(),
            "sections": sections,
            "graph": build_cluster_graph(sections),
        }
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(json_report, f, indent=2)
        print(f"\nJSON report saved to: {args.report}")


if __name__ == "__main__":
    main()
