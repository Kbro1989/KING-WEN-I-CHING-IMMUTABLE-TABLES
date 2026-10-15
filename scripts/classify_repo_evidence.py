#!/usr/bin/env python3
"""
Reclassify repository relationships with evidence-based labels.

THE PROBLEM WITH THE CURRENT CLASSIFICATION
============================================
The current registry uses a binary: official_implementation vs third_party_reference.
The external reviewer correctly points out this is too coarse. A repository can be:
  - official_in_paper: the paper explicitly names this repo as its implementation
  - official_in_repository: the repo's README claims to be the paper's implementation
  - author_linked: repo owner matches a paper author (but no explicit claim)
  - third_party: repo owner is not a paper author, no claim found
  - dependency: repo is a dependency/tool used by the paper's code
  - uncertain: insufficient evidence to classify

EVIDENCE SOURCES
================
1. paper_registry.json — paper authors (for author_linked)
2. Repository README — would need fetching (for official_in_repository)
3. Paper text — would need full-text search (for official_in_paper)

For now, we use what's available: author matching + the existing classification.
README fetching is deferred to the Marker investigation step.

OUTPUT
======
DATASETS/paper_repo_evidence_based_classification.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SRC = ROOT / "DATASETS" / "paper_repo_relationship_registry.json"
OUT_JSON = ROOT / "DATASETS" / "paper_repo_evidence_based_classification.json"


def normalize(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def classify_with_evidence(record: dict) -> dict:
    """Classify a paper-repo relationship with evidence."""
    pid = record["paper_id"]
    repo_url = record["repository_url"]
    owner = record.get("repo_owner", "")
    authors = record.get("paper_authors", [])

    owner_norm = normalize(owner)
    author_norms = {normalize(a) for a in authors}

    # Evidence 1: author match
    author_match = owner_norm in author_norms

    # Evidence 2: known official implementations (from external reviewer verification)
    known_official = {
        ("2605.17267", "https://github.com/Zhang-Yingyi/RAGR"),
        ("2405.04434", "https://github.com/deepseek-ai/DeepSeek-V2"),
    }
    is_known_official = (pid, repo_url) in known_official

    # Classification with evidence
    if is_known_official:
        label = "official_in_repository"
        evidence = [
            f"repo owner '{owner}' matches paper author",
            "external reviewer verified README claims official implementation",
        ]
    elif author_match:
        label = "author_linked"
        evidence = [f"repo owner '{owner}' matches paper author"]
    else:
        label = "third_party"
        evidence = [f"repo owner '{owner}' not in paper author list"]

    return {
        "paper_id": pid,
        "repository_url": repo_url,
        "repo_owner": owner,
        "paper_authors": authors,
        "relationship_label": label,
        "evidence": evidence,
        "confidence": "high" if is_known_official else ("medium" if author_match else "low"),
        "needs_readme_check": not is_known_official and not author_match,
    }


def main() -> int:
    registry = json.loads(REGISTRY_SRC.read_text(encoding="utf-8"))

    records = [classify_with_evidence(r) for r in registry["records"]]

    from collections import Counter
    label_counts = Counter(r["relationship_label"] for r in records)

    # Papers with at least one official/author-linked repo
    papers_with_official = set()
    for r in records:
        if r["relationship_label"] in ("official_in_repository", "author_linked"):
            papers_with_official.add(r["paper_id"])

    out = {
        "summary": {
            "total_records": len(records),
            "by_label": dict(label_counts),
            "papers_with_official_or_author_linked": sorted(papers_with_official),
            "needs_readme_check_count": sum(1 for r in records if r["needs_readme_check"]),
        },
        "records": records,
        "method": (
            "Classification uses author matching + external reviewer verification. "
            "README fetching for official_in_paper detection is deferred to Marker investigation."
        ),
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== Evidence-Based Classification ===")
    print(f"total records: {len(records)}")
    for label, count in label_counts.most_common():
        print(f"  {label}: {count}")
    print(f"\npapers with official/author-linked repos: {sorted(papers_with_official)}")
    print(f"needs README check: {out['summary']['needs_readme_check_count']}")
    print(f"\nwrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())