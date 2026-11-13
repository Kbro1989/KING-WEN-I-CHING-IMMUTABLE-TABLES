#!/usr/bin/env python3
"""Fetch arXiv category/tag metadata for all papers in paper_registry.json."""
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "DATASETS" / "paper_registry.json"
BATCH_SIZE = 10
DELAY = 3.0

NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def fetch_batch(ids):
    """Fetch metadata for a batch of arXiv IDs."""
    id_list = ",".join(ids)
    url = f"https://export.arxiv.org/api/query?id_list={id_list}&max_results={len(ids)}"
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  HTTP error: {e}")
        return {}
    root = ET.fromstring(data)
    results = {}
    for entry in root.findall("atom:entry", NS):
        id_el = entry.find("atom:id", NS)
        if id_el is None:
            continue
        arxiv_id = id_el.text.strip().split("/abs/")[-1]
        # strip version
        if "v" in arxiv_id and arxiv_id.split("v")[-1].isdigit():
            arxiv_id = arxiv_id.rsplit("v", 1)[0]

        cats = []
        for cat in entry.findall("atom:category", NS):
            term = cat.get("term", "").strip()
            if term:
                cats.append(term)

        primary = ""
        pc = entry.find("arxiv:primary_category", NS)
        if pc is not None:
            primary = pc.get("term", "").strip()

        title = ""
        t = entry.find("atom:title", NS)
        if t is not None:
            title = t.text.strip().replace("\n", " ")

        results[arxiv_id] = {
            "primary_category": primary,
            "categories": cats,
            "title": title,
        }
    return results


def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = list(registry.keys())
    print(f"Fetching categories for {len(ids)} papers...")

    fetched = 0
    failed = []
    for i in range(0, len(ids), BATCH_SIZE):
        batch = ids[i:i + BATCH_SIZE]
        print(f"  Batch {i // BATCH_SIZE + 1}/{(len(ids) + BATCH_SIZE - 1) // BATCH_SIZE}: {batch[0]}...{batch[-1]}")
        results = fetch_batch(batch)
        for pid in batch:
            if pid in results:
                r = results[pid]
                registry[pid]["primary_category"] = r["primary_category"]
                registry[pid]["categories"] = r["categories"]
                if r["title"] and not registry[pid].get("title"):
                    registry[pid]["title"] = r["title"]
                fetched += 1
            else:
                failed.append(pid)
                print(f"    MISSING: {pid}")
        time.sleep(DELAY)

    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFetched: {fetched}/{len(ids)}")
    if failed:
        print(f"Failed ({len(failed)}): {failed}")
    print(f"Wrote {REGISTRY.relative_to(ROOT)}")

    # Summary
    from collections import Counter
    cat_counter = Counter()
    for v in registry.values():
        for c in v.get("categories", []):
            cat_counter[c] += 1
    print("\nCategory distribution:")
    for cat, count in cat_counter.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
