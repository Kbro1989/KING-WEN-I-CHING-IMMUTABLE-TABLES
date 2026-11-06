import json

with open("DATASETS/structural_preservation/2102.03334_hierarchical_proposals_p004.json", encoding="utf-8") as f:
    d = json.load(f)

spans_map = {}
for p in d.get("level4_level5_proposals", []):
    pass

# Read spans from rawdict
import fitz
doc = fitz.open("DATASETS/benchmark_pdfs/2102.03334.pdf")
p = doc[3]
raw = p.get_text("rawdict")

spans_eq1 = []
for b in raw.get("blocks", []):
    for l in b.get("lines", []):
        for s in l.get("spans", []):
            if 500.0 <= s["bbox"][1] <= 517.0 and s["bbox"][0] > 300.0:
                t = "".join(c.get("c", "") for c in s.get("chars", []))
                cy = (s["bbox"][1] + s["bbox"][3]) / 2
                spans_eq1.append((s["bbox"], cy, s["font"], t))

print("=== SPANS AROUND EQ 1 (y in [500, 517]) ===")
for bb, cy, fn, t in spans_eq1:
    print(f"  bbox={[round(v,1) for v in bb]} cy={cy:.2f} font={fn:<18} text={repr(t)}")

doc.close()

