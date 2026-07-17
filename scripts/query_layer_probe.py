"""3-query layer activation probe for King Wen expansion pipeline.

Asks 3 questions, expands all 64 hexagrams for each, captures outputs,
and analyzes whether layer activation is flat/passive or expansive.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

IMMUTABLE_PATH = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py")
ENGINE_PATH = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\emotional_engine.py")

for path in [IMMUTABLE_PATH, ENGINE_PATH]:
    if not path.exists():
        raise SystemExit(f"missing: {path}")

# Ensure the tables package root is importable for emotional_engine.py
TABLES_DIR = IMMUTABLE_PATH.parent
if str(TABLES_DIR) not in sys.path:
    sys.path.insert(0, str(TABLES_DIR))

# Load immutable tables via direct import (engine depends on it)
spec = importlib.util.spec_from_file_location("kwt_probe", str(IMMUTABLE_PATH))
mod = importlib.util.module_from_spec(spec)
sys.modules["kwt_probe"] = mod
spec.loader.exec_module(mod)

# Load emotional engine
spec2 = importlib.util.spec_from_file_location("emotional_engine_probe", str(ENGINE_PATH))
mod2 = importlib.util.module_from_spec(spec2)
sys.modules["emotional_engine_probe"] = mod2
spec2.loader.exec_module(mod2)

expand_hexagram = mod2.expand_hexagram
sample_resolve = mod2.sample_resolve
collapse_full_128 = mod2.collapse_full_128

QUERIES = [
    "What is the optimal path forward for this session?",
    "What does this situation resolve into when viewed across all possibilities?",
    "What is the minimal viable expression of this state?",
]

OUTPUT_DIR = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\docs\query_probe")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _vec_norm(vec: dict) -> float:
    return math.sqrt(sum(v**2 for v in vec.values()))


def _vec_range(vec: dict) -> float:
    vals = list(vec.values())
    return max(vals) - min(vals) if vals else 0.0


def analyze_hexagram_expansion(hid: int, request_text: str, emotional_input: int = 50) -> dict:
    """Expand one hexagram and return analysis metrics."""
    base = expand_hexagram(hid, request_text, phase_bits=0, emotional_input=emotional_input)
    resolved = sample_resolve(hid, phase_bits=0, request_text=request_text, emotional_input=emotional_input)
    
    # Layer activation analysis
    inject_site = base.get("inject_site", {})
    bleed = base.get("bleed", 0.5)
    expanded_vector = base.get("expanded_vector", {})
    resolved_vector = resolved.get("resolved_vector", {})
    line_states = base.get("line_states", [])
    yao_vocab = base.get("yao_vocabulary", [])
    
    # Measure expressiveness
    vec_range = _vec_range(expanded_vector) if expanded_vector else 0.0
    vec_norm = _vec_norm(expanded_vector) if expanded_vector else 0.0
    yao_diversity = len(set(yao_vocab)) if yao_vocab else 0
    changing_count = sum(1 for ls in line_states if ls == 2) if line_states else 0
    
    # Classify pattern
    if vec_range < 0.1 and yao_diversity <= 1:
        pattern = "flat_passive"
    elif vec_range < 0.2 and changing_count == 0:
        pattern = "passive"
    elif changing_count >= 3 or vec_range >= 0.5:
        pattern = "expansive"
    else:
        pattern = "minimal_viable"
    
    return {
        "hexagram_id": hid,
        "pattern": pattern,
        "bleed": bleed,
        "vec_range": round(vec_range, 4),
        "vec_norm": round(vec_norm, 4),
        "yao_diversity": yao_diversity,
        "changing_count": changing_count,
        "yao_vocabulary": yao_vocab,
        "expanded_vector": expanded_vector,
        "resolved_vector": resolved_vector,
    }


def run_query_probe(query: str, query_idx: int) -> dict:
    """Run full 64-hex expansion for one query."""
    print(f"\n{'='*70}")
    print(f"QUERY {query_idx+1}/3: {query[:80]}...")
    print(f"{'='*70}")
    
    results = []
    pattern_counts = {"flat_passive": 0, "passive": 0, "minimal_viable": 0, "expansive": 0}
    
    for hid in range(1, 65):
        analysis = analyze_hexagram_expansion(hid, query, emotional_input=50)
        results.append(analysis)
        pattern_counts[analysis["pattern"]] += 1
    
    # Layer activation summary
    layer_summary = {
        "total_hexagrams": 64,
        "pattern_distribution": pattern_counts,
        "avg_bleed": round(sum(r["bleed"] for r in results) / 64, 4),
        "avg_vec_range": round(sum(r["vec_range"] for r in results) / 64, 4),
        "avg_changing_count": round(sum(r["changing_count"] for r in results) / 64, 2),
        "expansive_hexagrams": [r["hexagram_id"] for r in results if r["pattern"] == "expansive"],
        "flat_passive_hexagrams": [r["hexagram_id"] for r in results if r["pattern"] == "flat_passive"],
        "passive_hexagrams": [r["hexagram_id"] for r in results if r["pattern"] == "passive"],
        "minimal_viable_hexagrams": [r["hexagram_id"] for r in results if r["pattern"] == "minimal_viable"],
    }
    
    print(f"Pattern distribution: {pattern_counts}")
    print(f"Avg bleed: {layer_summary['avg_bleed']}")
    print(f"Avg vec_range: {layer_summary['avg_vec_range']}")
    print(f"Avg changing_count: {layer_summary['avg_changing_count']}")
    print(f"Expansive hexagrams: {len(layer_summary['expansive_hexagrams'])}")
    print(f"Flat/passive hexagrams: {len(layer_summary['flat_passive_hexagrams']) + len(layer_summary['passive_hexagrams'])}")
    
    return {
        "query": query,
        "query_idx": query_idx,
        "layer_summary": layer_summary,
        "hexagram_results": results,
    }


def main():
    print("=== 3-Query Layer Activation Probe ===")
    print(f"Immutable tables: {IMMUTABLE_PATH}")
    print(f"Engine: {ENGINE_PATH}")
    print()
    
    all_query_results = []
    
    for idx, query in enumerate(QUERIES):
        result = run_query_probe(query, idx)
        all_query_results.append(result)
        
        # Save per-query output
        out_path = OUTPUT_DIR / f"query_{idx+1}_expanded.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved: {out_path}")
    
    # Cross-query analysis
    print(f"\n{'='*70}")
    print("CROSS-QUERY ANALYSIS")
    print(f"{'='*70}")
    
    all_patterns = {"flat_passive": 0, "passive": 0, "minimal_viable": 0, "expansive": 0}
    for qr in all_query_results:
        for pattern, count in qr["layer_summary"]["pattern_distribution"].items():
            all_patterns[pattern] += count
    
    total = sum(all_patterns.values())
    print(f"\nAggregate pattern distribution across 3 queries × 64 hexagrams ({total} total):")
    for pattern, count in sorted(all_patterns.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {pattern:20s}: {count:4d} ({pct:5.1f}%)")
    
    # Identify consistently flat/passive hexagrams
    flat_passive_sets = [
        set(qr["layer_summary"]["flat_passive_hexagrams"] + qr["layer_summary"]["passive_hexagrams"])
        for qr in all_query_results
    ]
    consistently_flat = flat_passive_sets[0] & flat_passive_sets[1] & flat_passive_sets[2]
    print(f"\nConsistently flat/passive hexagrams across all 3 queries: {len(consistently_flat)}")
    if consistently_flat:
        print(f"  IDs: {sorted(consistently_flat)[:20]}...")
    
    # Identify consistently expansive hexagrams
    expansive_sets = [set(qr["layer_summary"]["expansive_hexagrams"]) for qr in all_query_results]
    consistently_expansive = expansive_sets[0] & expansive_sets[1] & expansive_sets[2]
    print(f"\nConsistently expansive hexagrams across all 3 queries: {len(consistently_expansive)}")
    if consistently_expansive:
        print(f"  IDs: {sorted(consistently_expansive)[:20]}...")
    
    # Save cross-query summary
    summary_path = OUTPUT_DIR / "cross_query_summary.json"
    summary = {
        "queries": QUERIES,
        "aggregate_patterns": all_patterns,
        "total_expansions": total,
        "consistently_flat_passive": sorted(consistently_flat),
        "consistently_expansive": sorted(consistently_expansive),
        "query_results": all_query_results,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved cross-query summary: {summary_path}")


if __name__ == "__main__":
    main()
