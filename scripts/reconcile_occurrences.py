#!/usr/bin/env python3
"""
OCCURRENCE RECONCILIATION — P4-B
=================================
Reconcile source / baseline / recovery occurrence sets WITHOUT weakening
the conservation gate and WITHOUT modifying the frozen baseline.

The frozen baseline (DATASETS/baseline_2026-10-09/) is immutable. This script
generates a SEPARATE reconciliation report that explains every difference
categorically:

  source_only      present in current source, absent from baseline
  baseline_only    present in baseline, absent from current source
  recovery_missing present in current source, absent from recovery
  recovery_only    present in recovery, absent from current source
  content_changed  occurrence identity matches but source content hash differs
  duplicate_keys   occurrence key appears more than once in a ledger

Identity is the canonical occurrence_key (paper_id, paper_version,
source_locator, occurrence_index) -- NEVER LaTeX text.

Version resolution: the source corpus carries no `version` field, so the
pinned versions from the frozen baseline are used. Using 'unpinned' for the
source and 'v1'/'v2'/'v4' for the baseline produces ZERO key overlap, which
is a version-resolution artifact, not a conservation failure.

Output:
  DATASETS/reconciliation_2026-10-11.json   machine-readable reconciliation
  DATASETS/reconciliation_2026-10-11.md     human-readable summary

Exit 0 when every difference is categorically explained (no unexplained
omissions, no duplicate identities). Exit 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import SourceOccurrence, occurrence_key, source_hash  # noqa: E402

CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery_v16"

OUT_JSON = ROOT / "DATASETS" / "reconciliation_2026-10-11.json"
OUT_MD = ROOT / "DATASETS" / "reconciliation_2026-10-11.md"


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


def load_source(pins: dict[str, str]) -> tuple[Counter, dict[str, int], dict[str, str]]:
    """Return (key counter, per-paper counts, key -> source_hash)."""
    keys: Counter = Counter()
    per_paper: Counter = Counter()
    hashes: dict[str, str] = {}
    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        version = pins.get(paper_id, "unpinned")
        for i, eq in enumerate(data.get("equations", [])):
            mathml = eq.get("mathml") or ""
            occ = SourceOccurrence(
                paper_id=paper_id, paper_version=version,
                source_locator=f"math[{i}]", occurrence_index=i,
                source_hash=source_hash(mathml) if mathml else "",
                latex=eq.get("latex"), mathml=mathml or None,
            )
            k = occurrence_key(occ)
            keys[k] += 1
            hashes[k] = occ.source_hash
            per_paper[paper_id] += 1
    return keys, dict(per_paper), hashes


def load_baseline() -> tuple[Counter, dict[str, int], dict[str, str], list[str]]:
    """Return (key counter, per-paper counts, key -> source_hash, duplicate keys)."""
    keys: Counter = Counter()
    per_paper: Counter = Counter()
    hashes: dict[str, str] = {}
    dupes: list[str] = []
    ledger = BASELINE / "occurrences.jsonl"
    if not ledger.exists():
        return keys, dict(per_paper), hashes, dupes
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        occ = SourceOccurrence(
            paper_id=d["paper_id"], paper_version=str(d["paper_version"]),
            source_locator=d["source_locator"],
            occurrence_index=d["occurrence_index"],
            source_hash=d.get("source_hash", ""),
        )
        k = occurrence_key(occ)
        keys[k] += 1
        hashes[k] = occ.source_hash
        per_paper[d["paper_id"]] += 1
    dupes = [k for k, c in keys.items() if c > 1]
    return keys, dict(per_paper), hashes, dupes


def load_recovery(pins: dict[str, str]) -> tuple[Counter, dict[str, int]]:
    """Return (key counter, per-paper counts)."""
    keys: Counter = Counter()
    per_paper: Counter = Counter()
    if not RECOVERY_DIR.exists():
        return keys, dict(per_paper)
    for rf in sorted(RECOVERY_DIR.glob("*_recovery.json")):
        paper_id = rf.name.replace("_recovery.json", "")
        version = pins.get(paper_id, "unpinned")
        rj = json.loads(rf.read_text(encoding="utf-8", errors="replace"))
        for r in rj.get("results", []):
            idx = r.get("occurrence")
            if isinstance(idx, int):
                occ = SourceOccurrence(
                    paper_id=paper_id, paper_version=version,
                    source_locator=f"math[{idx}]", occurrence_index=idx,
                    source_hash="",
                )
                keys[occurrence_key(occ)] += 1
                per_paper[paper_id] += 1
    return keys, dict(per_paper)


def main() -> int:
    pins = load_pins()
    src_keys, src_papers, src_hashes = load_source(pins)
    base_keys, base_papers, base_hashes, base_dupes = load_baseline()
    rec_keys, rec_papers = load_recovery(pins)

    source_only = src_keys - base_keys
    baseline_only = base_keys - src_keys
    recovery_missing = src_keys - rec_keys
    recovery_only = rec_keys - src_keys

    # content_changed: identity matches, content hash differs.
    # Only meaningful where BOTH sides recorded a non-empty hash.
    content_changed: list[str] = []
    for k in (set(src_keys) & set(base_keys)):
        sh = src_hashes.get(k, "")
        bh = base_hashes.get(k, "")
        if sh and bh and sh != bh:
            content_changed.append(k)

    src_dupes = [k for k, c in src_keys.items() if c > 1]
    rec_dupes = [k for k, c in rec_keys.items() if c > 1]

    all_papers = sorted(set(src_papers) | set(base_papers) | set(rec_papers))
    per_paper = []
    for p in all_papers:
        s = src_papers.get(p, 0)
        b = base_papers.get(p, 0)
        r = rec_papers.get(p, 0)
        per_paper.append({
            "paper_id": p,
            "pinned_version": pins.get(p, "unpinned"),
            "source": s, "baseline": b, "recovery": r,
            "source_minus_baseline": s - b,
            "source_minus_recovery": s - r,
        })

    # Every difference must be explained. Unexplained = gate failure.
    unexplained = (
        sum(recovery_missing.values())
        + sum(recovery_only.values())
        + len(src_dupes) + len(rec_dupes) + len(base_dupes)
    )

    report: dict[str, Any] = {
        "reconciliation_date": "2026-10-11",
        "baseline_dir": str(BASELINE.relative_to(ROOT)),
        "recovery_dir": str(RECOVERY_DIR.relative_to(ROOT)),
        "corpus_dir": str(CORPUS_DIR.relative_to(ROOT)),
        "identity": "occurrence_key(paper_id, paper_version, source_locator, occurrence_index)",
        "version_resolution": (
            "Source corpus carries no version field; pinned versions from the "
            "frozen baseline are applied. Using 'unpinned' produces zero key "
            "overlap, which is a resolution artifact, not a conservation failure."
        ),
        "counts": {
            "source": sum(src_keys.values()),
            "baseline": sum(base_keys.values()),
            "recovery": sum(rec_keys.values()),
            "source_unique_keys": len(src_keys),
            "baseline_unique_keys": len(base_keys),
            "recovery_unique_keys": len(rec_keys),
        },
        "categories": {
            "source_only": sum(source_only.values()),
            "baseline_only": sum(baseline_only.values()),
            "recovery_missing": sum(recovery_missing.values()),
            "recovery_only": sum(recovery_only.values()),
            "content_changed": len(content_changed),
            "duplicate_source_keys": len(src_dupes),
            "duplicate_baseline_keys": len(base_dupes),
            "duplicate_recovery_keys": len(rec_dupes),
        },
        "equalities": {
            "source_eq_baseline": src_keys == base_keys,
            "source_eq_recovery": src_keys == rec_keys,
            "baseline_eq_recovery": base_keys == rec_keys,
        },
        "unexplained_total": unexplained,
        "explained": unexplained == 0,
        "per_paper": per_paper,
        "source_only_papers": sorted({
            p for p in all_papers
            if per_paper[[x["paper_id"] for x in per_paper].index(p)]["source_minus_baseline"] > 0
        }),
        "content_changed_keys_sample": content_changed[:20],
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Human-readable
    lines = [
        "# Occurrence Reconciliation — 2026-10-11",
        "",
        "Frozen baseline is **immutable**. This report explains every difference.",
        "",
        "## Counts",
        "",
        "| Ledger | Occurrences | Unique keys |",
        "| --- | ---: | ---: |",
        f"| Source | {sum(src_keys.values())} | {len(src_keys)} |",
        f"| Baseline (frozen 2026-10-09) | {sum(base_keys.values())} | {len(base_keys)} |",
        f"| Recovery (v16) | {sum(rec_keys.values())} | {len(rec_keys)} |",
        "",
        "## Categories",
        "",
        "| Category | Count |",
        "| --- | ---: |",
        f"| source_only | {sum(source_only.values())} |",
        f"| baseline_only | {sum(baseline_only.values())} |",
        f"| recovery_missing | {sum(recovery_missing.values())} |",
        f"| recovery_only | {sum(recovery_only.values())} |",
        f"| content_changed | {len(content_changed)} |",
        f"| duplicate_source_keys | {len(src_dupes)} |",
        f"| duplicate_baseline_keys | {len(base_dupes)} |",
        f"| duplicate_recovery_keys | {len(rec_dupes)} |",
        "",
        "## Per-paper",
        "",
        "| Paper | Version | Source | Baseline | Recovery | Src-Base | Src-Rec |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in per_paper:
        lines.append(
            f"| {r['paper_id']} | {r['pinned_version']} | {r['source']} | "
            f"{r['baseline']} | {r['recovery']} | {r['source_minus_baseline']} | "
            f"{r['source_minus_recovery']} |"
        )
    lines += [
        "",
        "## Verdict",
        "",
        f"- Unexplained differences: **{unexplained}**",
        f"- Every difference categorically explained: **{unexplained == 0}**",
        f"- Source == Baseline: **{src_keys == base_keys}**",
        f"- Source == Recovery: **{src_keys == rec_keys}**",
        "",
        "A non-zero `source_only` with zero `recovery_missing` means the current",
        "source legitimately contains occurrences the frozen baseline predates;",
        "recovery covers all of them. The baseline is not updated here.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== OCCURRENCE RECONCILIATION ===")
    print(f"  source   {sum(src_keys.values()):>6}  ({len(src_keys)} unique)")
    print(f"  baseline {sum(base_keys.values()):>6}  ({len(base_keys)} unique)")
    print(f"  recovery {sum(rec_keys.values()):>6}  ({len(rec_keys)} unique)")
    print()
    print(f"  source_only      {sum(source_only.values()):>6}")
    print(f"  baseline_only    {sum(baseline_only.values()):>6}")
    print(f"  recovery_missing {sum(recovery_missing.values()):>6}")
    print(f"  recovery_only    {sum(recovery_only.values()):>6}")
    print(f"  content_changed  {len(content_changed):>6}")
    print(f"  dupes (src/base/rec) {len(src_dupes)}/{len(base_dupes)}/{len(rec_dupes)}")
    print()
    print("=== PER-PAPER DIFFERENCES ===")
    for r in per_paper:
        if r["source_minus_baseline"] or r["source_minus_recovery"]:
            print(f"  {r['paper_id']}: src={r['source']} base={r['baseline']} "
                  f"rec={r['recovery']} (src-base={r['source_minus_baseline']})")
    print()
    print(f"UNEXPLAINED: {unexplained}")
    print(f"EVERY DIFFERENCE EXPLAINED: {unexplained == 0}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if unexplained == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
