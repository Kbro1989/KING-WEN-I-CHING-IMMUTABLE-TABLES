import json
from pathlib import Path
from collections import defaultdict

repo = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
math_dir = repo / "datasets"
version_dirs = sorted([d for d in math_dir.iterdir() if d.is_dir() and d.name.startswith("math_recovery_v")])

paper_data = defaultdict(dict)
for vdir in version_dirs:
    for f in sorted(vdir.glob("*.json")):
        if f.name.startswith(("2605.", "2009.", "2102.", "1406.", "2602.")):
            with open(fpath := vdir / f, 'r') as fh:
                data = json.load(fh)
            paper_data[f.name][vdir.name] = data

# Compare 2605.00155 between v3 and v16
paper_id = "2605.00155"
if paper_id in paper_data:
    versions = sorted(paper_data[paper_id].keys())
    print(f"2605.00155 in versions: {versions}")
    
    v3_data = paper_data[paper_id].get("math_recovery_v3", {})
    v16_data = paper_data[paper_id].get("math_recovery_v16", {})
    
    print(f"\n{'='*60}")
    print(f"2605.00155 - v3 vs v16 field comparison")
    print(f"{'='*60}")
    
    all_keys = set(v3_data.keys()) | set(v16_data.keys())
    same = 0
    different = 0
    
    for key in sorted(all_keys):
        v3_val = v3_data.get(key)
        v16_val = v16_data.get(key)
        if v3_val == v16_val:
            same += 1
        else:
            different += 1
            print(f"\n>>> DIFF: {key}")
            print(f"    v3: {str(v3_val)[:300]}")
            print(f"    v16: {str(v16_val)[:300]}")
    
    print(f"\nSummary: {same} fields same, {different} fields different out of {len(all_keys)} total")
    
    # Expanded list comparison
    print(f"\n--- Expanded list (first 3 entries) ---")
    exp3 = v3_data.get('expanded', [])
    exp16 = v16.get('expanded', [])
    print(f"v3 expanded count: {len(exp3) if isinstance(exp3, list) else 'N/A'}")
    print(f"v16 expanded count: {len(exp16) if isinstance(exp16, list) else 'N/A'}")
    
    for i in range(min(3, len(exp3), len(exp16))):
        e3 = exp3[i] if i < len(exp3) else None
        e16 = exp16[i] if i < len(exp16) else None
        print(f"\n  Expanded[{i}]:")
        print(f"    v3: {json.dumps(e3)[:400] if e3 else 'NULL'}")
        print(f"    v16: {json.dumps(e16)[:300]}")
