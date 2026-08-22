import json
from pathlib import Path

p = Path("DATASETS/kingwen_model_sets/kit_1.json")
data = json.loads(p.read_text(encoding="utf-8"))

def print_keys(d, indent=0):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                print("  " * indent + f"{k}: (dict)")
                print_keys(v, indent + 1)
            elif isinstance(v, list):
                print("  " * indent + f"{k}: (list of len {len(v)})")
                if len(v) > 0 and isinstance(v[0], dict):
                    print("  " * (indent + 1) + "[sample element keys]:")
                    print_keys(v[0], indent + 2)
            else:
                print("  " * indent + f"{k}: {type(v).__name__} (value: {v})")
    elif isinstance(d, list):
        print("  " * indent + f"list of len {len(d)}")

print_keys(data)
