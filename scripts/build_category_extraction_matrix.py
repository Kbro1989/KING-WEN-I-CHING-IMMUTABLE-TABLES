#!/usr/bin/env python3
"""Build category-vs-extraction-quality matrix from paper registry + corpus + eval data."""
import json
import glob
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "DATASETS" / "paper_registry.json"
CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
REP_EVAL = ROOT / "DATASETS" / "vision_comparison" / "representative_page_evaluation.jsonl"
CR_RECORDS = ROOT / "DATASETS" / "cross_reference" / "cross_reference_records.jsonl"
OUTPUT = ROOT / "DATASETS" / "category_extraction_matrix.json"

def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    # Load corpus equation counts
    corpus_eq = {}
    for f in glob.glob(str(CORPUS_DIR / "*.json")):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            pid = d.get("arxiv_id", Path(f).stem)
            corpus_eq[pid] = d.get("equation_count", 0)
        except Exception:
            pass

    # Load representative page eval data (per paper)
    rep_pages = collections.defaultdict(lambda: {"pages": 0, "regions": 0, "primary_white": None})
    with open(REP_EVAL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if "paper_id" not in rec:
                continue  # skip coverage summary
            pid = rec.get("paper_id", "")
            rep_pages[pid]["pages"] += 1
            # Count regions from page eval (not directly stored, but we can note)
            pwd = rec.get("primary_white_detection", {})
            if pwd:
                rep_pages[pid]["primary_white"] = pwd.get("primary_white")

    # Load cross-reference counts per paper
    cr_counts = collections.Counter()
    with open(CR_RECORDS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            pid = rec.get("paper_id", "")
            cr_counts[pid] += 1

    # Build per-paper rows
    rows = []
    for pid, info in sorted(registry.items()):
        cats = info.get("categories", [])
        primary = info.get("primary_category", "")
        eq_count = corpus_eq.get(pid, info.get("equation_count", 0))
        rp = rep_pages.get(pid, {})
        cr = cr_counts.get(pid, 0)
        rows.append({
            "paper_id": pid,
            "primary_category": primary,
            "categories": cats,
            "equation_count": eq_count,
            "pages_evaluated": rp.get("pages", 0),
            "cross_ref_records": cr,
            "primary_white": rp.get("primary_white"),
        })

    # Build category-level aggregation
    cat_agg = collections.defaultdict(lambda: {
        "paper_count": 0,
        "equation_count": 0,
        "cross_ref_records": 0,
        "pages_evaluated": 0,
        "papers": [],
    })
    for row in rows:
        for cat in row["categories"]:
            agg = cat_agg[cat]
            agg["paper_count"] += 1
            agg["equation_count"] += row["equation_count"] or 0
            agg["cross_ref_records"] += row["cross_ref_records"]
            agg["pages_evaluated"] += row["pages_evaluated"]
            agg["papers"].append(row["paper_id"])

    # Sort by paper count descending
    sorted_cats = sorted(cat_agg.items(), key=lambda x: -x[1]["paper_count"])

    matrix = {
        "generated_at": "2026-11-04",
        "total_papers": len(rows),
        "total_equations": sum(r["equation_count"] or 0 for r in rows),
        "total_cross_refs": sum(r["cross_ref_records"] for r in rows),
        "per_paper": rows,
        "per_category": {cat: {k: v for k, v in agg.items() if k != "papers"} for cat, agg in sorted_cats},
    }

    OUTPUT.write_text(json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    print(f"Total papers: {len(rows)}")
    print(f"Total equations: {matrix['total_equations']}")
    print(f"Total cross-refs: {matrix['total_cross_refs']}")
    print(f"\nTop 10 categories by paper count:")
    for cat, agg in sorted_cats[:10]:
        print(f"  {cat}: papers={agg['paper_count']}, eqs={agg['equation_count']}, crossrefs={agg['cross_ref_records']}, pages={agg['pages_evaluated']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
