#!/usr/bin/env python3
"""
STRUCTURAL SURVIVAL — persist typed AST through serialization + verify round-trip.

Closes the persistence-boundary gap: the recovery pipeline computes
tree_expr/tree_unsupported (math_recovery_tool.py:1553-1554) but the persisted
record (results.append, lines 1601-1612) omits them. This script:

  1. Extracts a TYPED structural AST (scripts/structural_ast_extractor.py)
     from each source MathML — operators, limits, differentials, relations,
     decorations preserved as typed nodes, unsupported content never dropped.
  2. Binds every AST to its immutable occurrence_key (same identity as the
     frozen baseline ledger).
  3. Serializes the AST to a canonical structural record and round-trips it
     (to_dict -> from_dict) verifying the canonical hash is invariant.
  4. Writes the structural survival ledger + a round-trip report.

Round-trip gate: canonical_json(ast.to_dict()) BEFORE == AFTER serialization.
A tree that does not round-trip is an explicit failure, never silent success.

Output:
  DATASETS/structural_survival.jsonl   one typed structural record per occurrence
  DATASETS/structural_survival_report.json  metrics + round-trip gate
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import (  # noqa: E402
    ExprNode, SourceOccurrence, occurrence_key, source_hash, extraction_hash,
    backend_input_hash, canonical_json,
)
from structural_ast_extractor import extract_structural_ast  # noqa: E402

CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"


def load_pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    p = BASELINE / "pinned_versions.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    pins[parts[0]] = parts[1]
    return pins


def count_nodes(tree: ExprNode) -> Counter:
    """Count node kinds recursively — structural fidelity fingerprint."""
    c: Counter = Counter()
    stack = [tree]
    while stack:
        n = stack.pop()
        c[n.kind] += 1
        stack.extend(n.children)
    return c


def main() -> int:
    pins = load_pins()
    records: list[dict[str, Any]] = []
    m = Counter()
    roundtrip_failures: list[str] = []

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        version = pins.get(paper_id) or data.get("version") or "unpinned"

        for i, eq in enumerate(data.get("equations", [])):
            mathml = eq.get("mathml") or None
            latex = eq.get("latex") or None
            occ = SourceOccurrence(
                paper_id=paper_id, paper_version=version,
                source_locator=f"math[{i}]", occurrence_index=i,
                source_hash=source_hash(mathml) if mathml else "",
                latex=latex, mathml=mathml,
            )
            okey = occurrence_key(occ)

            tree, unsup = extract_structural_ast(mathml)
            m["total"] += 1

            if tree is None:
                m["extract_failed"] += 1
                records.append({
                    "occurrence_key": okey,
                    "paper_id": paper_id,
                    "paper_version": version,
                    "source_locator": occ.source_locator,
                    "structural_status": "failed",
                    "unsupported": unsup,
                    "roundtrip_ok": False,
                })
                roundtrip_failures.append(okey)
                continue

            # -- structural fidelity fingerprint: node-kind histogram --
            kinds = count_nodes(tree)
            has_unsupported = "unsupported" in kinds

            # -- round-trip: canonical hash must be invariant across serialize --
            pre_dict = tree.to_dict()
            pre_hash = backend_input_hash(tree)
            try:
                rebuilt = ExprNode.from_dict(json.loads(canonical_json(pre_dict)))
                post_hash = backend_input_hash(rebuilt)
                roundtrip_ok = (pre_hash == post_hash)
            except Exception as e:
                roundtrip_ok = False
                post_hash = f"error:{type(e).__name__}"

            if not roundtrip_ok:
                roundtrip_failures.append(okey)

            # structural status per contract dimensions
            if has_unsupported:
                struct_status = "partial"   # some nodes preserved, some unsupported
                m["partial"] += 1
            else:
                struct_status = "verified"
                m["verified"] += 1
            if roundtrip_ok:
                m["roundtrip_ok"] += 1
            else:
                m["roundtrip_failed"] += 1
            if unsup:
                m["has_unsupported_tokens"] += 1

            records.append({
                "occurrence_key": okey,
                "paper_id": paper_id,
                "paper_version": version,
                "source_locator": occ.source_locator,
                "source_hash": occ.source_hash,
                "extraction_hash": extraction_hash(latex, mathml),
                "structural_status": struct_status,
                "ast_hash": pre_hash,
                "roundtrip_ok": roundtrip_ok,
                "node_kinds": dict(kinds),
                "unsupported": unsup,
                "canonical_tree": pre_dict,
            })

    # -- conservation vs baseline ledger --
    trace_keys = Counter(r["occurrence_key"] for r in records)
    baseline_keys: Counter = Counter()
    ledger = BASELINE / "occurrences.jsonl"
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                o = SourceOccurrence(
                    paper_id=d["paper_id"], paper_version=str(d["paper_version"]),
                    source_locator=d["source_locator"],
                    occurrence_index=d["occurrence_index"],
                    source_hash=d["source_hash"],
                )
                baseline_keys[occurrence_key(o)] += 1

    conservation = {
        "total": len(records),
        "source_eq_baseline": trace_keys == baseline_keys,
        "missing_from_baseline": sum((baseline_keys - trace_keys).values()),
        "extra_vs_baseline": sum((trace_keys - baseline_keys).values()),
        "duplicate_keys": sum(1 for c in trace_keys.values() if c > 1),
    }

    gate_ok = (
        conservation["source_eq_baseline"]
        and conservation["missing_from_baseline"] == 0
        and conservation["extra_vs_baseline"] == 0
        and conservation["duplicate_keys"] == 0
        and m["roundtrip_failed"] == 0
        and m["extract_failed"] == 0
    )

    report = {
        "conservation": conservation,
        "metrics": dict(m),
        "roundtrip_failures": len(roundtrip_failures),
        "roundtrip_gate": m["roundtrip_failed"] == 0,
        "structural_survival_gate": gate_ok,
        "note": (
            "ast_hash is the canonical hash of the typed ExprNode. roundtrip_ok "
            "verifies to_dict->from_dict->hash invariance. 'verified' means no "
            "unsupported nodes; 'partial' means some source nodes preserved as "
            "kind=unsupported (never dropped). Missing/malformed trees are "
            "explicit failures, never silent success."
        ),
    }

    out_jsonl = ROOT / "DATASETS" / "structural_survival.jsonl"
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    out_report = ROOT / "DATASETS" / "structural_survival_report.json"
    out_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== STRUCTURAL SURVIVAL ===")
    for k in ("total", "verified", "partial", "extract_failed",
              "roundtrip_ok", "roundtrip_failed", "has_unsupported_tokens"):
        print(f"  {k:24s} {m.get(k,0)}")
    print("\n=== CONSERVATION ===")
    for k, v in conservation.items():
        print(f"  {k:24s} {v}")
    print(f"\nROUND-TRIP GATE:        {'PASS' if m['roundtrip_failed']==0 else 'FAIL'}")
    print(f"STRUCTURAL SURVIVAL:   {'PASS' if gate_ok else 'FAIL'}")
    print(f"Wrote {out_jsonl}")
    print(f"Wrote {out_report}")
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main())
