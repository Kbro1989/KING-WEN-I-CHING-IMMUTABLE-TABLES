import fitz

doc = fitz.open("DATASETS/benchmark_pdfs/2102.03334.pdf")
p = doc[3]
raw = p.get_text("rawdict")

spans_eq4 = []
for b in raw.get("blocks", []):
    for l in b.get("lines", []):
        for s in l.get("spans", []):
            if 548.0 <= s["bbox"][1] <= 564.0 and s["bbox"][0] > 300.0:
                t = "".join(c.get("c", "") for c in s.get("chars", []))
                cy = (s["bbox"][1] + s["bbox"][3]) / 2
                spans_eq4.append((s["bbox"], cy, s["font"], t))

print("=== SPANS AROUND EQ 4 (y in [548, 564]) ===")
for bb, cy, fn, t in spans_eq4:
    print(f"  bbox={[round(v,1) for v in bb]} cy={cy:.2f} font={fn:<18} text={repr(t)}")

doc.close()

