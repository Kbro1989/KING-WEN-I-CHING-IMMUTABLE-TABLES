import json
from pathlib import Path
from collections import defaultdict

repo = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
math_dir = repo / "datasets"

# Find version dirs
version_dirs = sorted([d for d in math_dir.iterdir() if d.is_dir() and d.name.startswith("math_recovery_v")])

# Collect data per version
paper_data = defaultdict(dict)
for vdir in version_dirs:
    for f in sorted(vdir.glob("*.json")):
        if f.name.startswith(("2605.", "2009.", "2102.", "1406.", "2602.")):
            with open(fpath := vdir / f, 'r') as fh:
                data = json.load(fh)
            paper_data[f.name][vdir.name] = data

print(f"Loaded papers: {len(paper_data)}")
print(f"Versions: {[d.name for d in version_dirs]}")

# Compare 2605.00155 between v3 and v16
paper_id = "2605.00155"
if paper_id in paper_data:
    versions = sorted(paper_data[paper_id].keys())
    print(f"\n2605.00155 in: {versions}")
    
    # Show top-level fields
    v3 = paper_data[paper_id].get("math_recovery_v3", {})
    v16 = paper_data[paper_id].get("math_recovery_v16", {})
    
    print(f"\n{'='*60}")
    print(f"2605.00155 - v3 vs v16 field comparison")
    print(f"{'='*60}")
    
    # Fields of interest
    fields_of_interest = ['global_intent', 'expanded', 'resolved', 'line_states', 
                          'global_greens', 'relevance', 'priority', 'transformer']
    
    for field in sorted(v3.keys()):
        v3_val = v3.get(field)
        v16_val = v16.get(field)
        
        if v3_val != v16_val:
            print(f"\n>>> DIFF: {field}")
            print(f"    v3 ({type(v3_val).__name__}): {str(v3_val)[:200]}")
            print(f"    v16: {str(v16_val)[:200]}")
    
    # Count differences
    all_keys = set(v3.keys()) | set(v16.keys())
    same = sum(1 for k in all_keys if v3.get(k) == v16.get(k))
    different = len(all_keys) - same
    print(f"\nSummary: {same} fields same, {different} fields different out of {len(all_keys)} total")
    
    # Show expanded list comparison
    print(f"\n--- Expanded list (first 3 entries) ---")
    exp3 = v3.get('expanded', [])
    exp16 = v16.get('expanded', [])
    print(f"v3 expanded count: {len(exp3)}")
    print(f"v16 expanded count: {len(exp16)}")
    
    for i in range(min(3, len(exp3), len(exp16))):
        e3 = exp3[i] if i < len(exp3) else None
        e16 = exp16[i] if i < len(exp16) else None
        print(f"\n  Expanded[{i}]:")
        print(f"    v3: {json.dumps(e3)[:300]}")
        print(f"    v16: {json.dumps(e16)[:300]}")
