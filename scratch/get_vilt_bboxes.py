import fitz

doc = fitz.open("DATASETS/benchmark_pdfs/2102.03334.pdf")
p = doc[3]  # Page 4
raw = p.get_text("rawdict")

# Let's extract line blocks for each equation
eq_y_ranges = [
    ("VILT-001", "Eq 1", (500.0, 517.0)),
    ("VILT-002", "Eq 2", (517.0, 532.0)),
    ("VILT-003", "Eq 3", (532.0, 548.0)),
    ("VILT-004", "Eq 4", (548.0, 564.0)),
    ("VILT-005", "Eq 5", (564.0, 581.0)),
    ("VILT-006", "Eq 6", (581.0, 600.0)),
]

for vid, label, (y0, y1) in eq_y_ranges:
    spans = []
    for b in raw.get("blocks", []):
        for l in b.get("lines", []):
            if y0 <= l["bbox"][1] <= y1 and l["bbox"][0] > 300.0:
                for s in l.get("spans", []):
                    text = "".join(c.get("c", "") for c in s.get("chars", []))
                    spans.append((s["bbox"], text))
    if spans:
        bx0 = min(sb[0] for sb, _ in spans)
        by0 = min(sb[1] for sb, _ in spans)
        bx1 = max(sb[2] for sb, _ in spans)
        by1 = max(sb[3] for sb, _ in spans)
        full_text = " ".join(t for _, t in spans if t.strip())
        print(f"{vid} ({label}): bbox={[round(v, 2) for v in (bx0, by0, bx1, by1)]}")
        print(f"  text: {repr(full_text)}")
doc.close()

