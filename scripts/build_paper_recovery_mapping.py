#!/usr/bin/env python3
import json
from pathlib import Path

repo = Path("/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")

# Build a mapping of paper_id -> recovered data from all JSON sources
paper_data = {}

# 1. math_recovery/*.json
recovery_dir = repo / "DATASETS/math_recovery"
for f in recovery_dir.glob("*_recovery.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        arxiv_id = data.get("stats", {}).get("arxiv_id", f.stem)
        s = data.get("stats", {})
        paper_data[arxiv_id] = {
            "source": str(f.relative_to(repo)),
            "type": "math_recovery",
            "recoverable": s.get("recoverable"),
            "solvable": s.get("solvable"),
            "total_equations": s.get("total_equations"),
            "recoverable_pct": s.get("recoverable_pct"),
            "unique_commands": s.get("unique_commands"),
            "bracket_families": s.get("bracket_families"),
            "top_errors": s.get("errors", {}),
        }
    except Exception:
        pass

# 2. output/hexagram_vocabulary_by_paper.json
v2p = repo / "output/hexagram_vocabulary_by_paper.json"
if v2p.exists():
    try:
        v2p_data = json.loads(v2p.read_text(encoding="utf-8"))
        paper_data["V2P"] = {"source": "output/hexagram_vocabulary_by_paper.json", "type": "vocabulary_by_paper", "fields": list(v2p_data.keys())[:5]}
    except Exception:
        pass

# 3. arxiv_html_corpus/*.json
ahc = repo / "DATASETS/arxiv_html_corpus"
for f in ahc.glob("*.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        arxiv_id = data.get("arxiv_id", f.stem)
        paper_data[arxiv_id] = {"source": str(f.relative_to(repo)), "type": "arxiv_html", "sections": len(data.get("sections", []))}
    except:
        pass

# 4. structural_preservation/*.json (per-paper hierarchical proposals)
sp_dir = repo / "DATASETS/structural_preservation"
for f in sp_dir.glob("*.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            arxiv_id = data.get("arxiv_id", f.stem)
            paper_data[arxiv_id] = {"source": str(f.relative_to(repo)), "type": "structural_preservation", "fields": list(data.keys())}
    except:
        pass

# 5. cross_reference/cross_refs_*.json
cr_dir = repo / "DATASETS/cross_reference"
for f in cr_dir.glob("cross_refs_*.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        arxiv_id = f.stem.replace("cross_refs_", "")
        paper_data[arxiv_id] = {"source": str(f.relative_to(repo)), "type": "cross_refs", "fields": list(data.keys())}
    except:
        pass

# 6. other paper-level outputs
for f in repo.glob("output/*.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if "paper" in f.name.lower() or "vocabulary" in f.name.lower():
            paper_data[f.name] = {"source": "output/" + f.name, "type": "output", "fields": list(data.keys())}
    except:
        pass

print(f"=== PAPER_ID -> RECOVERED DATA MAPPING ===")
print(f"Total paper_ids captured: {len(paper_data)}")

from collections import Counter
cat_counts = Counter()
for k, v in paper_data.items():
    cat = v.get("type", "unknown")
    cat_counts[cat] += 1

for cat, count in sorted(cat_counts.items()):
    print(f"  {cat}: {count} entries")

print("\n=== SAMPLE per-paper recovery data ===")
shown = 0
for k, v in sorted(paper_data.items()):
    if "recovery" in v.get("source", ""):
        print(f"  {k}: {v}")
        shown += 1
        if shown >= 5:
            break

print("\n=== FULL LIST (paper_id -> recovered data) ===")
for k, v in sorted(paper_data.items()):
    if k != "V2P":
        print(f"  {k}: {v.get('type')} - recoverable={v.get('recoverable')}/{v.get('total_equations') if v.get('total_equations') else '?'} solvable={v.get('solvable')}")
