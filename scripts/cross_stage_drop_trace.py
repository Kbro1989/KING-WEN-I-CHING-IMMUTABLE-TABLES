#!/usr/bin/env python3
"""
CROSS-STAGE DROP TRACE — measured execution trace, first-pull -> latest.

Unlike a declarative schema, this script INSTRUMENTS the real stage boundary:
it runs scripts/mathml_parser.MathMLParser.parse() on each source MathML and
records the ACTUAL emitted expression + unsupported reasons. It then reconciles
the real recovery records and the frozen baseline ledger by occurrence identity
(multiset), so missing / unexpected / duplicate occurrences stay distinguishable.

Chain stages (measured, not declared):
  S0 first_pull   DATASETS/arxiv_html_corpus/*.json        (source of truth)
  S1 mathml_parse scripts/mathml_parser.MathMLParser.parse (MEASURED here)
  S2 recovery     DATASETS/math_recovery_v15/*.json         (persisted records)
  S3 scoreboard   scripts/semantic_honesty_scoreboard.py    (reads latex only)

Metrics (Finding C — precise):
  src_has_mathml      source occurrence carries a <math> element
  src_no_mathml       source occurrence has no MathML
  struct_preserved    a structural representation survived to recovery output
  struct_lost         source HAD MathML but recovery output has NO structural rep
  recovery_missing    no recovery record for this source occurrence
  recovery_extra      recovery record with no matching source occurrence
  N_lost              struct_lost count (source MathML AND recovery lacks it)

Acceptance gate:
  Source occurrences == Trace occurrences == Baseline occurrences  (identity-level,
  multiset), with missing/unexpected/duplicate explicitly reported.

Root is discovered relative to this file, not hardcoded (Finding D).
Version 'unpinned' is reported explicitly, never silently conflated (Finding D).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# ── portable root discovery (Finding D) ──────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import (  # noqa: E402
    SourceOccurrence, occurrence_key, source_hash, extraction_hash,
)

CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery_v15"
BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"

# First-pull equation field set (S0 schema).
FIRST_PULL_FIELDS = [
    "mathml", "latex", "context_before", "context_after",
    "is_display", "mathml_len", "source", "index",
]


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


def measure_mathml_parse(mathml: str) -> dict[str, Any]:
    """
    Finding A: actually run the parser. Return measured S1 output.
    Does not rely on a declared field map.
    """
    result: dict[str, Any] = {
        "parsed": False,
        "expr": None,
        "unsupported": [],
        "error": None,
    }
    if not mathml:
        return result
    try:
        from bs4 import BeautifulSoup
        from mathml_parser import MathMLParser
        soup = BeautifulSoup(mathml, "html.parser")
        node = soup.find("math")
        if node is None:
            result["error"] = "no_math_element"
            return result
        expr, unsup = MathMLParser().parse(node)
        result["parsed"] = expr is not None
        result["expr"] = expr
        result["unsupported"] = list(unsup)
    except Exception as e:  # parser crash is a measured outcome, not a skip
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def recovery_has_struct(rec: dict[str, Any] | None) -> bool:
    """
    Finding B/C: does the PERSISTED recovery record carry a structural
    representation? v15 output persists latex/recovered/notes but NOT the
    typed expr — so this is False for every persisted v15 record. Measured
    against the actual record keys, not assumed.
    """
    if rec is None:
        return False
    # A structural representation would be 'expr' or an equivalent typed field.
    for key in ("expr", "canonical_tree", "tree", "ast"):
        if key in rec and rec[key] is not None:
            return True
    return False


def main() -> int:
    pins = load_pins()
    unpinned_papers: list[str] = []

    # ── S0: load source occurrences ──
    source: list[dict[str, Any]] = []
    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        version = pins.get(paper_id) or data.get("version") or "unpinned"
        if version == "unpinned":
            unpinned_papers.append(paper_id)
        for i, eq in enumerate(data.get("equations", [])):
            mathml = eq.get("mathml") or None
            latex = eq.get("latex") or None
            occ = SourceOccurrence(
                paper_id=paper_id, paper_version=version,
                source_locator=f"math[{i}]", occurrence_index=i,
                source_hash=source_hash(mathml) if mathml else "",
                latex=latex, mathml=mathml,
            )
            source.append({
                "occ": occ, "eq": eq,
                "mathml": mathml, "latex": latex,
                "version": version,
            })

    # ── S1: measure real parser output per occurrence ──
    for s in source:
        s["s1"] = measure_mathml_parse(s["mathml"])

    # ── S2: load real persisted recovery records, index by (paper, occurrence) ──
    recovery: dict[tuple[str, int], dict[str, Any]] = {}
    recovery_counter: Counter = Counter()
    for rf in sorted(RECOVERY_DIR.glob("*_recovery.json")):
        paper_id = rf.name.replace("_recovery.json", "")
        rj = json.loads(rf.read_text(encoding="utf-8", errors="replace"))
        for r in rj.get("results", []):
            occ_idx = r.get("occurrence")
            if isinstance(occ_idx, int):
                recovery[(paper_id, occ_idx)] = r
                recovery_counter[occurrence_key(SourceOccurrence(
                    paper_id=paper_id,
                    paper_version=pins.get(paper_id) or "unpinned",
                    source_locator=f"math[{occ_idx}]",
                    occurrence_index=occ_idx,
                    source_hash="",
                ))] += 1

    # ── Finding B: multiset reconciliation source vs recovery vs baseline ──
    source_keys = Counter(occurrence_key(s["occ"]) for s in source)
    # baseline ledger keys (identity tuples -> recompute occurrence_key)
    baseline_keys: Counter = Counter()
    ledger_path = BASELINE / "occurrences.jsonl"
    if ledger_path.exists():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            occ = SourceOccurrence(
                paper_id=d["paper_id"], paper_version=str(d["paper_version"]),
                source_locator=d["source_locator"],
                occurrence_index=d["occurrence_index"], source_hash=d["source_hash"],
            )
            baseline_keys[occurrence_key(occ)] += 1

    # ── Build per-occurrence trace + Finding C metrics ──
    trace: list[dict[str, Any]] = []
    m = Counter()
    for s in source:
        occ = s["occ"]
        okey = occurrence_key(occ)
        paper_id = occ.paper_id
        rec = recovery.get((paper_id, occ.occurrence_index))

        src_has_mathml = s["mathml"] is not None
        struct_preserved = recovery_has_struct(rec)
        recovery_present = rec is not None

        m["total"] += 1
        if src_has_mathml:
            m["src_has_mathml"] += 1
        else:
            m["src_no_mathml"] += 1
        if not recovery_present:
            m["recovery_missing"] += 1
        if struct_preserved:
            m["struct_preserved"] += 1
        # Finding C precise N_lost: source HAD mathml AND recovery lacks struct
        if src_has_mathml and not struct_preserved:
            m["struct_lost"] += 1
        if s["s1"]["parsed"]:
            m["s1_parsed"] += 1
        if s["s1"]["unsupported"]:
            m["s1_has_unsupported"] += 1

        trace.append({
            "occurrence_key": okey,
            "paper_id": paper_id,
            "paper_version": s["version"],
            "source_locator": occ.source_locator,
            "source_hash": occ.source_hash,
            "extraction_hash": extraction_hash(s["latex"], s["mathml"]),
            "src_has_mathml": src_has_mathml,
            "s1_parsed": s["s1"]["parsed"],
            "s1_unsupported_count": len(s["s1"]["unsupported"]),
            "s1_error": s["s1"]["error"],
            "recovery_present": recovery_present,
            "struct_preserved": struct_preserved,
            "struct_lost": src_has_mathml and not struct_preserved,
        })

    # Recovery records with no matching source occurrence (Finding B: extras)
    recovery_only = recovery_counter - source_keys
    m["recovery_extra"] = sum(recovery_only.values())

    # Conservation assertions (Finding B)
    src_missing_vs_base = source_keys - baseline_keys
    base_missing_vs_src = baseline_keys - source_keys

    trace_keys = Counter(t["occurrence_key"] for t in trace)
    dupes = [k for k, c in trace_keys.items() if c > 1]

    conservation = {
        "source_occurrences": sum(source_keys.values()),
        "trace_occurrences": sum(trace_keys.values()),
        "baseline_occurrences": sum(baseline_keys.values()),
        "recovery_occurrences": sum(recovery_counter.values()),
        "source_eq_trace": source_keys == trace_keys,
        "source_eq_baseline": source_keys == baseline_keys,
        "missing_from_baseline": sum(src_missing_vs_base.values()),
        "extra_in_baseline": sum(base_missing_vs_src.values()),
        "recovery_extra": m["recovery_extra"],
        "duplicate_trace_keys": len(dupes),
    }

    payload = {
        "conservation": conservation,
        "metrics": dict(m),
        "unpinned_papers": unpinned_papers,
        "root_discovery": str(ROOT),
        "hash_semantics": {
            "source_hash": "SHA-256 of extracted MathML string (documented: not raw HTML bytes)",
            "extraction_hash": "SHA-256 of canonical {latex, mathml}; None distinct from empty",
        },
        "note": (
            "S1 is MEASURED by running MathMLParser.parse on each source MathML. "
            "v15 recovery persists no typed structural representation (expr/ast absent "
            "from output), so struct_preserved is measured against actual record keys. "
            "A validated recursive AST could substitute for MathML downstream."
        ),
    }

    out_json = ROOT / "DATASETS" / "cross_stage_drop_trace.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    out_jsonl = ROOT / "DATASETS" / "cross_stage_drop_trace.jsonl"
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for t in trace:
            f.write(json.dumps(t, ensure_ascii=False, sort_keys=True) + "\n")

    # ── report ──
    print("=== CONSERVATION (multiset, identity-level) ===")
    for k, v in conservation.items():
        print(f"  {k:28s} {v}")
    print("\n=== METRICS (Finding C) ===")
    for k in ("total", "src_has_mathml", "src_no_mathml", "s1_parsed",
              "s1_has_unsupported", "recovery_missing", "recovery_extra",
              "struct_preserved", "struct_lost"):
        print(f"  {k:28s} {m.get(k,0)}")
    if unpinned_papers:
        print(f"\n  UNPINNED papers: {unpinned_papers}")

    # ── acceptance gate ──
    gate_ok = (
        conservation["source_eq_trace"]
        and conservation["source_eq_baseline"]
        and conservation["missing_from_baseline"] == 0
        and conservation["extra_in_baseline"] == 0
        and conservation["duplicate_trace_keys"] == 0
    )
    print(f"\nACCEPTANCE GATE (conservation): {'PASS' if gate_ok else 'FAIL'}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_jsonl}")
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main())
