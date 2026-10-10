#!/usr/bin/env python3
"""
CROSS-STAGE DROP TRACE — classify what each stage drops, first-pull → latest.

Traces every source occurrence from the first-pull arxiv HTML corpus through
the usage chain (corpus → mathml_parser → recovery → scoreboard) and records,
per stage, which first-pull fields survive and which are dropped. Binds each
occurrence to its contract identity (occurrence_key) so drops are attributable
to a specific source location, not just counted.

This is NOT a re-derivation of the v15 honesty class. It is a usage-chain
provenance audit: the v15 scoreboard matches by LaTeX and cannot see MathML-
level drops; this script closes that gap by walking the field chain directly.

Chain stages (each is a consumer that reads the previous stage's output):
  S0 first_pull   DATASETS/arxiv_html_corpus/*.json   (source of truth)
  S1 mathml_parse scripts/mathml_parser.py             (reads MathML)
  S2 recovery     DATASETS/math_recovery_v15/*.json    (emits per-equation)
  S3 scoreboard   scripts/semantic_honesty_scoreboard.py (classifies by latex)

Drop classification per (occurrence, stage):
  CARRIED   field present in this stage's output
  DROPPED   field absent from this stage's output but present upstream
  N/A       field never existed at this stage's input

Output: DATASETS/cross_stage_drop_trace.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import (
    SourceOccurrence, occurrence_key, source_hash, extraction_hash,
    canonical_json, hash_bytes,
)

CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery_v15"
BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"

# First-pull equation fields (S0 schema) — the canonical field set to trace.
FIRST_PULL_FIELDS = [
    "mathml", "latex", "context_before", "context_after",
    "is_display", "mathml_len", "source", "index",
]

# Which fields each downstream stage carries (from source inspection):
#   S1 mathml_parser : consumes mathml; emits typed tree (context/display not carried)
#   S2 recovery      : carries latex, occurrence, recovered, solvable, notes, error
#   S3 scoreboard    : reads latex, recovered, solvable only
STAGE_FIELD_MAP = {
    "S1_mathml_parse": {"mathml"},                 # only mathml enters the parser
    "S2_recovery": {"latex", "occurrence", "recovered", "solvable", "notes", "error"},
    "S3_scoreboard": {"latex", "recovered", "solvable"},
}


def load_pins() -> dict[str, str]:
    pins = {}
    p = BASELINE / "pinned_versions.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    pins[parts[0]] = parts[1]
    return pins


def build_occurrence(paper_id: str, version: str, i: int, eq: dict[str, Any]) -> SourceOccurrence:
    mathml = eq.get("mathml") or None
    latex = eq.get("latex") or None
    return SourceOccurrence(
        paper_id=paper_id,
        paper_version=version,
        source_locator=f"math[{i}]",
        occurrence_index=i,
        source_hash=source_hash(mathml) if mathml else "",
        latex=latex,
        mathml=mathml,
    )


def trace_occurrence(occ: SourceOccurrence, eq: dict[str, Any],
                     recovery_rec: dict[str, Any] | None) -> dict[str, Any]:
    """
    For one occurrence, record field survival at each chain stage.
    Returns a per-occurrence drop record keyed by occurrence_key.
    """
    okey = occurrence_key(occ)

    # S0: first pull — all fields present (source of truth)
    present_s0 = {f for f in FIRST_PULL_FIELDS if f in eq}

    # S2: recovery record fields (mapped back to first-pull field names where possible)
    present_s2 = set()
    if recovery_rec is not None:
        if recovery_rec.get("latex") is not None or "latex" in recovery_rec:
            present_s2.add("latex")
        if "occurrence" in recovery_rec:
            present_s2.add("index")  # occurrence int == first-pull index
        # mathml, context, is_display, mathml_len, source are NOT in recovery output

    # Build the per-stage drop map
    stages = {}
    # S1 reads mathml only
    stages["S1_mathml_parse"] = {
        f: ("CARRIED" if f in STAGE_FIELD_MAP["S1_mathml_parse"] else "DROPPED")
        for f in FIRST_PULL_FIELDS
    }
    # S2 recovery
    stages["S2_recovery"] = {
        f: ("CARRIED" if f in present_s2 else "DROPPED")
        for f in FIRST_PULL_FIELDS
    }
    # S3 scoreboard reads latex-derived only
    stages["S3_scoreboard"] = {
        f: ("CARRIED" if f in STAGE_FIELD_MAP["S3_scoreboard"] else "DROPPED")
        for f in FIRST_PULL_FIELDS
    }

    # MathML-level drop flag: the recovery stage has no mathml at all, so any
    # MathML structural detail is invisible downstream.
    mathml_dropped_at_recovery = "mathml" not in present_s2

    return {
        "occurrence_key": okey,
        "paper_id": occ.paper_id,
        "paper_version": occ.paper_version,
        "source_locator": occ.source_locator,
        "source_hash": occ.source_hash,
        "extraction_hash": extraction_hash(occ.latex, occ.mathml),
        "is_display": bool(eq.get("is_display")),
        "has_mathml": occ.mathml is not None,
        "mathml_dropped_at_recovery": mathml_dropped_at_recovery,
        "stages": stages,
    }


def main() -> int:
    pins = load_pins()
    trace: list[dict[str, Any]] = []

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        version = pins.get(paper_id) or data.get("version") or "unpinned"
        equations = data.get("equations", [])

        # Load the matching recovery file (by paper_id stem)
        rec_path = RECOVERY_DIR / f"{paper_id}_recovery.json"
        recovery_results: dict[int, dict[str, Any]] = {}
        if rec_path.exists():
            rj = json.loads(rec_path.read_text(encoding="utf-8", errors="replace"))
            for r in rj.get("results", []):
                occ_idx = r.get("occurrence")
                if isinstance(occ_idx, int):
                    recovery_results[occ_idx] = r

        for i, eq in enumerate(equations):
            occ = build_occurrence(paper_id, version, i, eq)
            rec = recovery_results.get(i)
            trace.append(trace_occurrence(occ, eq, rec))

    # ---- Conservation: every first-pull occurrence traced exactly once ----
    keys = [t["occurrence_key"] for t in trace]
    dupes = [k for k, c in Counter(keys).items() if c > 1]

    # ---- Aggregate drop statistics per stage ----
    agg = {}
    for stage in ("S1_mathml_parse", "S2_recovery", "S3_scoreboard"):
        field_counts = defaultdict(Counter)
        for t in trace:
            for f, status in t["stages"][stage].items():
                field_counts[f][status] += 1
        agg[stage] = {f: dict(c) for f, c in field_counts.items()}

    # MathML-level invisibility count
    mathml_invisible = sum(1 for t in trace if t["mathml_dropped_at_recovery"])

    payload = {
        "total_occurrences": len(trace),
        "duplicate_keys": len(dupes),
        "mathml_invisible_at_recovery": mathml_invisible,
        "stage_field_drops": agg,
        "note": (
            "S2 recovery emits no MathML, so all MathML structural detail "
            "(truncation, conditional-bar fusion, dropped munder/mover, tall-"
            "symbol collapse) is invisible to S3 scoreboard, which matches by "
            "LaTeX. This audit exposes that gap; it does not re-classify honesty."
        ),
    }

    out = ROOT / "DATASETS" / "cross_stage_drop_trace.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Full per-occurrence trace as JSONL for drill-down
    jsonl = ROOT / "DATASETS" / "cross_stage_drop_trace.jsonl"
    with open(jsonl, "w", encoding="utf-8") as f:
        for t in trace:
            f.write(canonical_json(t) + "\n")

    print(f"Occurrences traced: {len(trace)}")
    print(f"Duplicate keys:     {len(dupes)}")
    print(f"MathML invisible at recovery: {mathml_invisible}/{len(trace)}")
    print()
    for stage, fields in agg.items():
        print(f"=== {stage} ===")
        for f in FIRST_PULL_FIELDS:
            c = fields.get(f, {})
            print(f"  {f:16s} CARRIED={c.get('CARRIED',0):5d}  DROPPED={c.get('DROPPED',0):5d}")
        print()
    print(f"Wrote {out}")
    print(f"Wrote {jsonl}")

    if dupes:
        print("\nFAIL: duplicate occurrence keys", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
