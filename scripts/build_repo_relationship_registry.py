#!/usr/bin/env python3
"""
Build the paper↔repo relationship registry.

THE CORE DISTINCTION
====================
Not all repositories linked from a paper are the paper's own implementation.
This registry classifies each relationship using the one reliable signal
available in the source metadata: whether the repo owner matches a paper
author.

  official_implementation  repo owner is a paper author
  third_party_reference   repo owner is NOT a paper author

This distinction matters because conflating the two is precisely the kind of
fabrication-adjacent error the project has zero tolerance for: treating a
cited tool as if it were the paper's code silently misattributes work.

WHY NOT GUESS FROM NAMES
========================
Repository names like `openai/guided-diffusion` or `NVlabs/stylegan2`
are NOT evidence of official status — organizations publish many repos and
papers cite many repos. The only defensible classification compares the
repo owner against the paper's author list recorded in the registry.

For owners not in the author list, the relationship is recorded as
third_party_reference. That is a factual statement about the metadata, not
a judgment about the repository's quality or provenance.

OUTPUT
======
DATASETS/paper_repo_relationship_registry.json
  - one record per (paper, repo) pair
  - relationship_type: official_implementation | third_party_reference
  - verification: how the classification was derived
  - counts by type and per paper
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SRC = ROOT / "DATASETS" / "paper_registry.json"
REPO_SRC = ROOT / "DATASETS" / "paper_repository_provenance.jsonl"
OUT_JSON = ROOT / "DATASETS" / "paper_repo_relationship_registry.json"


def normalize(name: str) -> str:
    """Normalize a person/org name for comparison."""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def extract_owner(repo_url: str) -> str | None:
    """Extract the GitHub owner from a repo URL."""
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", repo_url)
    if m:
        owner = m.group(1)
        if owner.lower() in ("www", "features", "topics", "collections",
                             "orgs", "users", "settings", "login", "search"):
            return None
        return owner
    return None


def main() -> int:
    registry = json.loads(REGISTRY_SRC.read_text(encoding="utf-8"))
    repos = [json.loads(l) for l in REPO_SRC.read_text(encoding="utf-8").splitlines() if l.strip()]

    records = []
    for r in repos:
        pid = r.get("paper_id")
        if not pid or pid not in registry:
            continue
        paper = registry[pid]
        authors = paper.get("authors", [])
        author_norm = {normalize(a) for a in authors if a.strip()}

        url = r.get("repository_url", "")
        owner = extract_owner(url)
        if owner is None:
            continue

        owner_norm = normalize(owner)
        is_official = owner_norm in author_norm

        records.append({
            "paper_id": pid,
            "paper_title": paper.get("title", ""),
            "paper_authors": authors,
            "repository_url": url,
            "repo_owner": owner,
            "repo_name": url.rstrip("/").split("/")[-1] if "/" in url else "",
            "relationship_type": (
                "official_implementation" if is_official else "third_party_reference"
            ),
            "verification": (
                f"repo owner '{owner}' matches a paper author"
                if is_official
                else f"repo owner '{owner}' not found in paper author list"
            ),
        })

    by_type = Counter(x["relationship_type"] for x in records)
    by_paper = defaultdict(Counter)
    for x in records:
        by_paper[x["paper_id"]][x["relationship_type"]] += 1

    summary = {
        "total_records": len(records),
        "by_relationship_type": dict(by_type),
        "official_implementation_count": by_type.get("official_implementation", 0),
        "third_party_reference_count": by_type.get("third_party_reference", 0),
        "by_paper": {pid: dict(c) for pid, c in sorted(by_paper.items())},
        "method": (
            "classification derived by comparing the GitHub repo owner against "
            "the paper's author list in paper_registry.json; no inference from "
            "repository names"
        ),
    }

    out = {"summary": summary, "records": records}
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"total records: {len(records)}")
    print(f"  official_implementation: {by_type.get('official_implementation', 0)}")
    print(f"  third_party_reference:   {by_type.get('third_party_reference', 0)}")
    print(f"\nwrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())