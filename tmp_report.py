import hashlib, json
from pathlib import Path
from collections import defaultdict

repo = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
math_dir = repo / "datasets"
version_dirs = sorted([d for d in math_dir.iterdir() if d.is_dir() and d.name.startswith("math_recovery_v")])

print(f"Version dirs: {[d.name for d in version_dirs]}")
print()

# Collect all JSON files per version
version_files = {}
for vdir in version_dirs:
    files = sorted(vdir.glob("*.json"))
    version_files[vdir.name] = files

print(f"Files per version:")
for vdir in version_dirs:
    names = sorted([f.name for f in version_files[vdir.name]])
    print(f"  [{vdir.name}] {len(names)} files: {sorted(names)}")
