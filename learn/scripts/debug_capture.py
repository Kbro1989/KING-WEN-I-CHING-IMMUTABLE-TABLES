from __future__ import annotations
import json, math, collections, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from emotional_engine import collapse_full_128  # noqa: E402


def describe(collapse):
    consensus = collapse.get("consensus") or {}
    return {
        "consensus_hexagram_id": consensus.get("consensus_hexagram_id"),
        "consensus_temporal": consensus.get("consensus_temporal"),
        "consensus_yao": consensus.get("consensus_yao"),
        "consensus_porosity_mean": consensus.get("consensus_porosity_mean"),
        "consensus_intent": consensus.get("consensus_intent"),
        "total_resolved": consensus.get("total_resolved"),
    }


def top_n(resolved, weights, n=10):
    hex_scores = collections.defaultdict(float)
    for item, w in zip(resolved, weights):
        hex_id = item.get("hexagram_id")
        if not hex_id:
            continue
        hex_scores[hex_id] += w
    ranked = sorted(hex_scores.items(), key=lambda kv: kv[1], reverse=True)[:n]
    return ranked


def inject_summary(resolved):
    counts = collections.Counter()
    for item in resolved:
        counts[item.get("inject_site", {}).get("primary_pool", "?")] += 1
    return counts.most_common()


def rollout():
    rows = {}
    for value in [0, 10, 20, 30, 40, 50, 100]:
        collapse = collapse_full_128(emotional_input=value)
        rows[str(value)] = {
            "describe": describe(collapse),
            "top_hex": top_n(collapse.get("resolved", []), [1.0 / 512] * 512, 12),
            "inject_counts": inject_summary(collapse.get("resolved", [])),
            "first_resolved_sample": (collapse.get("resolved") or [None])[0],
        }
    return rows


if __name__ == "__main__":
    data = rollout()
    out = Path("learn/exports/capture.json")
    out.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    print(out)
