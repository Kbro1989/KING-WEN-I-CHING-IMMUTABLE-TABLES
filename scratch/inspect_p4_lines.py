import fitz, json, hashlib
from pathlib import Path

PDF_PATH = Path("DATASETS/benchmark_pdfs/2102.03334.pdf")

h = hashlib.sha256()
with PDF_PATH.open("rb") as f:
    for chunk in iter(lambda: f.read(1048576), b""):
        h.update(chunk)
pdf_sha = h.hexdigest()
print(f"PDF SHA-256: {pdf_sha}")

doc = fitz.open(PDF_PATH)
page = doc[3]  # Page 4 (0-based 3)

raw = page.get_text("rawdict")
print(f"Page 4 size: {page.rect}")

# Find blocks and lines in y in [490, 620]
print("\n--- Display Math Lines on Page 4 (y in [490, 620]) ---")
for b_idx, b in enumerate(raw.get("blocks", [])):
    for l_idx, l in enumerate(b.get("lines", [])):
        by = l["bbox"][1]
        if 490.0 <= by <= 620.0:
            text = "".join(c.get("c", "") for s in l.get("spans", []) for c in s.get("chars", []))
            fonts = list(set(s.get("font", "") for s in l.get("spans", [])))
            print(f"  line y={by:.1f} bbox={[round(v,1) for v in l['bbox']]} fonts={fonts} text={repr(text)}")

doc.close()

