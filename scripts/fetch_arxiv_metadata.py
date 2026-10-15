#!/usr/bin/env python3
"""
Fetch arXiv metadata for papers missing from paper_registry.json.

WHY THIS IS NEEZED
==================
The repo-relationship registry needs paper authors to distinguish
"official implementation" (repo owner is a paper author) from
"third_party_reference" (repo owner is not). Without author metadata
for all 125 papers in the provenance file, only the 14 already in
paper_registry.json can be classified.

The arXiv abs page exposes author/title/date as <meta> tags:
  <meta name="citation_author" content="...">
  <meta name="citation_title" content="...">
  <meta name="citation_date" content="...">

These are the same fields Crossref/Google Scholar index. No API key needed.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SRC = ROOT / "DATASETS" / "paper_registry.json"
PROVENANCE_SRC = ROOT / "DATASETS" / "paper_repository_provenance.jsonl"
ABS_BASE = "https://arxiv.org/abs/"
REQUEST_DELAY = 3.0  # be polite to arxiv.org


def fetch_abs(arxiv_id: str) -> dict | None:
    """Fetch and parse an arXiv abs page. Returns metadata or None on failure."""
    url = ABS_BASE + arxiv_id
    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (research-metadata-fetcher; contact: local)"
        })
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")

        authors = []
        for m in soup.find_all("meta", attrs={"name": "citation_author"}):
            c = m.get("content", "").strip()
            if c:
                authors.append(c)

        title = ""
        m = soup.find("meta", attrs={"name": "citation_title"})
        if m:
            title = m.get("content", "").strip()

        date = ""
        m = soup.find("meta", attrs={"name": "citation_date"})
        if m:
            date = m.get("content", "").strip()

        # fallback: parse from the abs page text itself
        if not authors:
            for a in soup.select("a[href^='/search/?searchtype=author']"):
                t = a.get_text().strip()
                if t:
                    authors.append(t)

        if not title:
            h1 = soup.find("h1", class_="title")
            if h1:
                title = h1.get_text().replace("Title:", "").strip()

        if authors or title:
            return {"authors": authors, "title": title, "date": date}
        return None
    except Exception:
        return None


def main() -> int:
    registry = json.loads(REGISTRY_SRC.read_text(encoding="utf-8"))
    provenance = [json.loads(l) for l in PROVENANCE_SRC.read_text(encoding="utf-8").splitlines() if l.strip()]

    all_pids = sorted(set(r["paper_id"] for r in provenance))
    missing = [pid for pid in all_pids if pid not in registry]

    print(f"registry has {len(registry)} papers")
    print(f"provenance has {len(all_pids)} papers")
    print(f"missing metadata for {len(missing)} papers")

    if not missing:
        print("nothing to do")
        return 0

    print(f"\nfetching {len(missing)} papers from arxiv.org (delay={REQUEST_DELAY}s)...")

    fetched = 0
    failed = []
    for i, pid in enumerate(missing, 1):
        print(f"  [{i}/{len(missing)}] {pid}...", end=" ", flush=True)
        meta = fetch_abs(pid)
        if meta:
            registry[pid] = {
                "arxiv_id": pid,
                "version": None,
                "primary_category": None,
                "categories": [],
                "title": meta["title"],
                "authors": meta["authors"],
                "date": meta["date"],
                "canonical_abs": ABS_BASE + pid,
                "canonical_html": f"https://arxiv.org/html/{pid}",
                "stamp": None,
                "equation_count": None,
                "source_file": None,
            }
            fetched += 1
            print(f"OK ({len(meta['authors'])} authors)")
        else:
            failed.append(pid)
            print("FAILED")
        time.sleep(REQUEST_DELAY)

    REGISTRY_SRC.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nfetched {fetched}/{len(missing)} papers")
    if failed:
        print(f"failed: {failed}")
    print(f"registry now has {len(registry)} papers")
    print(f"wrote {REGISTRY_SRC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())