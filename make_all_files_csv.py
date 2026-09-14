import os
import csv
from pathlib import Path

root = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
csv_path = root / "ALL-FILES.csv"

fields = ["relative_path", "type", "size_bytes", "depth", "extension", "parent_dir"]
rows = []

for dirpath, dirnames, filenames in os.walk(str(root)):
    dp = Path(dirpath)
    rel_root = dp.relative_to(root)

    for d in sorted(dirnames):
        p = dp / d
        rel = p.relative_to(root)
        depth = len(rel.parts)
        rows.append({
            "relative_path": str(rel) + "/",
            "type": "directory",
            "size_bytes": "",
            "depth": depth,
            "extension": "",
            "parent_dir": str(rel.parent) if rel.parent != Path(".") else ""
        })

    for f in sorted(filenames):
        p = dp / f
        rel = p.relative_to(root)
        depth = len(rel.parts)
        ext = p.suffix.lower()
        try:
            sz = p.stat().st_size
        except Exception:
            sz = ""
        rows.append({
            "relative_path": str(rel),
            "type": "file",
            "size_bytes": sz,
            "depth": depth,
            "extension": ext,
            "parent_dir": str(rel.parent) if rel.parent != Path(".") else ""
        })

with open(csv_path, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"WROTE {csv_path}")
print(f"rows: {len(rows)}")
print(f"files: {sum(1 for r in rows if r['type']=='file')}")
print(f"dirs: {sum(1 for r in rows if r['type']=='directory')}")
