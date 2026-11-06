#!/usr/bin/env python3
"""Benchmark representativeness report: 16 evaluated vs 118 unevaluated papers."""
import json
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "DATASETS" / "category_extraction_matrix.json"
REGISTRY = ROOT / "DATASETS" / "paper_registry.json"
REP_EVAL = ROOT / "DATASETS" / "vision_comparison" / "representative_page_evaluation.jsonl"
OUTPUT = ROOT / "DATASETS" / "benchmark_representativeness_report.json"

def main():
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    # Identify evaluated papers (those with cross-refs or pages)
    evaluated_pids = set()
    unevaluated_pids = set()
    for row in matrix["per_paper"]:
        if row["cross_ref_records"] > 0 or row["pages_evaluated"] > 0:
            evaluated_pids.add(row["paper_id"])
        else:
            unevaluated_pids.add(row["paper_id"])

    # Per-paper details
    evaluated = [r for r in matrix["per_paper"] if r["paper_id"] in evaluated_pids]
    unevaluated = [r for r in matrix["per_paper"] if r["paper_id"] in unevaluated_pids]

    # Category distribution comparison
    def cat_dist(papers):
        c = collections.Counter()
        for p in papers:
            for cat in p["categories"]:
                c[cat] += 1
        return c

    eval_cats = cat_dist(evaluated)
    uneval_cats = cat_dist(unevaluated)
    all_cats = cat_dist(matrix["per_paper"])

    # Build comparison per category
    cat_comparison = []
    for cat in sorted(all_cats.keys()):
        ec = eval_cats.get(cat, 0)
        uc = uneval_cats.get(cat, 0)
        ac = all_cats.get(cat, 0)
        cat_comparison.append({
            "category": cat,
            "evaluated_papers": ec,
            "unevaluated_papers": uc,
            "total_papers": ac,
            "evaluated_pct": round(100.0 * ec / ac, 1) if ac > 0 else 0.0,
            "evaluation_gap": uc,
        })

    # Equation volume comparison
    eval_eqs = sum(r["equation_count"] or 0 for r in evaluated)
    uneval_eqs = sum(r["equation_count"] or 0 for r in unevaluated)
    total_eqs = sum(r["equation_count"] or 0 for r in matrix["per_paper"])

    # Page evaluation detail
    eval_pages = sum(r["pages_evaluated"] for r in evaluated)
    eval_crossrefs = sum(r["cross_ref_records"] for r in evaluated)

    # Primary category distribution
    eval_primary = collections.Counter(r["primary_category"] for r in evaluated)
    uneval_primary = collections.Counter(r["primary_category"] for r in unevaluated)

    # Representativeness assessment
    representativeness = []
    for cat in sorted(all_cats.keys()):
        ac = all_cats[cat]
        ec = eval_cats.get(cat, 0)
        ratio = ec / ac if ac > 0 else 0
        if ac >= 5 and ec == 0:
            status = "NOT_REPRESENTED"
        elif ratio < 0.1:
            status = "UNDERREPRESENTED"
        elif ratio >= 0.5:
            status = "WELL_REPRESENTED"
        else:
            status = "PARTIALLY_REPRESENTED"
        representativeness.append({
            "category": cat,
            "total": ac,
            "evaluated": ec,
            "ratio": round(ratio, 3),
            "status": status,
        })

    # Integrity checks
    integrity = {
        "equation_reconciliation": {
            "registry_equations": total_eqs,
            "cross_ref_records": matrix["total_cross_refs"],
            "difference": matrix["total_cross_refs"] - total_eqs,
            "explanation": "Cross-reference records (44,297) > registry equations (40,132) because a single equation can generate multiple correspondence records (region-equation pairs, text boundaries, partial matches). These are different measurement units.",
        },
        "category_attribution": {
            "multi_label_papers": sum(1 for r in matrix["per_paper"] if len(r["categories"]) > 1),
            "single_label_papers": sum(1 for r in matrix["per_paper"] if len(r["categories"]) == 1),
            "note": "Category counts are multi-label and cannot be summed to unique paper totals without an attribution rule.",
        },
        "benchmark_lineage": {
            "evaluated_paper_ids": sorted(evaluated_pids),
            "evaluated_paper_count": len(evaluated_pids),
            "rep_eval_records": sum(r["pages_evaluated"] for r in evaluated),
            "cross_ref_records": eval_crossrefs,
        },
    }

    report = {
        "generated_at": "2026-11-04",
        "population": {
            "registry_papers": len(matrix["per_paper"]),
            "evaluated_papers": len(evaluated_pids),
            "unevaluated_papers": len(unevaluated_pids),
            "evaluated_pct": round(100.0 * len(evaluated_pids) / len(matrix["per_paper"]), 1),
            "registry_equations": total_eqs,
            "evaluated_equations": eval_eqs,
            "unevaluated_equations": uneval_eqs,
            "evaluated_pages": eval_pages,
            "evaluated_cross_refs": eval_crossrefs,
        },
        "category_comparison": cat_comparison,
        "representativeness": representativeness,
        "integrity_checks": integrity,
    }

    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    print()
    print("=== REPRESENTATIVENESS SUMMARY ===")
    for r in representativeness:
        if r["status"] in ("NOT_REPRESENTED", "UNDERREPRESENTED"):
            print(f"  {r['status']}: {r['category']} (total={r['total']}, evaluated={r['evaluated']}, ratio={r['ratio']})")
    print()
    print(f"Evaluated papers: {len(evaluated_pids)} / {len(matrix['per_paper'])} ({report['population']['evaluated_pct']}%)")
    print(f"Equations: {eval_eqs} evaluated / {uneval_eqs} unevaluated / {total_eqs} total")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
