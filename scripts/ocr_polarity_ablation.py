#!/usr/bin/env python3
"""OCR polarity ablation: Pix2Text on original vs inverted crops.

Tests whether inverting a math crop's polarity changes Pix2Text's recognition
output (LaTeX, symbol recovery, delimiter recognition, etc.).

Usage:
  python scripts/ocr_polarity_ablation.py
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np
import cv2

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
OUTPUT_DIR = ROOT / "DATASETS" / "ocr_polarity_ablation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Crops to test: 4x versions from 1907_04931 (the crop used in DA-V2 ablation)
# plus 4x versions from 2009.00031 if available
CROP_DIR = ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "1907_04931"
CROPS = sorted(CROP_DIR.glob("crop_*_4x.png"))

print(f"Found {len(CROPS)} crops to test")

# Initialize Pix2Text
from pix2text import Pix2Text
p2t = Pix2Text.from_config()

results = []

for crop_path in CROPS:
    crop_name = crop_path.stem
    print(f"\n=== Processing {crop_name} ===")

    # Read original as PIL Image (Pix2Text expects PIL or file path)
    original_pil = Image.open(crop_path).convert("RGB")
    assert original_pil is not None
    source_sha = hashlib.sha256(crop_path.read_bytes()).hexdigest()

    # Inverted as PIL Image
    original_np = np.array(original_pil)
    inverted_np = 255 - original_np
    inverted_pil = Image.fromarray(inverted_np)

    # Save both for reference
    original_pil.save(OUTPUT_DIR / f"{crop_name}_original.png")
    inverted_pil.save(OUTPUT_DIR / f"{crop_name}_inverted.png")

    # OCR original
    print(f"  OCR original...")
    try:
        original_result = p2t.recognize(original_pil)
        original_latex = original_result.get("text", "") if isinstance(original_result, dict) else str(original_result)
    except Exception as e:
        original_latex = f"ERROR: {type(e).__name__}: {e}"
    print(f"    Original: {original_latex!r}")

    # OCR inverted
    print(f"  OCR inverted...")
    try:
        inverted_result = p2t.recognize(inverted_pil)
        inverted_latex = inverted_result.get("text", "") if isinstance(inverted_result, dict) else str(inverted_result)
    except Exception as e:
        inverted_latex = f"ERROR: {type(e).__name__}: {e}"
    print(f"    Inverted: {inverted_latex!r}")

    # Compare
    exact_match = original_latex == inverted_latex
    original_chars = len(original_latex)
    inverted_chars = len(inverted_latex)
    char_diff = abs(original_chars - inverted_chars)

    # Error classification
    def classify_error(orig, inv):
        if orig == inv:
            return "none"
        if not orig.strip() and not inv.strip():
            return "none (both empty)"
        if orig.strip() and not inv.strip():
            return "deletion (recognition failure)"
        if not orig.strip() and inv.strip():
            return "insertion (hallucination)"
        # Nonempty-to-nonempty: classify as substitution if both have
        # recognized content, even when character sets differ
        orig_norm = orig.strip().replace(" ", "")
        inv_norm = inv.strip().replace(" ", "")
        if orig_norm == inv_norm:
            return "none (whitespace/structural variation only)"
        # Case-only change
        if orig_norm.lower() == inv_norm.lower():
            return "case_change"
        # Character-set comparison
        orig_symbols = set(orig_norm.replace("\\", "").replace("$", ""))
        inv_symbols = set(inv_norm.replace("\\", "").replace("$", ""))
        if orig_symbols == inv_symbols:
            return "structural_layout_change (same symbols, different structure)"
        deleted = orig_symbols - inv_symbols
        inserted = inv_symbols - orig_symbols
        # Both have content and differ in LaTeX. Determine whether the
        # change is deletion (inverted is a content-substring of original)
        # or substitution (different symbols recognized). Use content-only
        # comparison (strip LaTeX delimiters) for substring detection.
        orig_content = orig_norm.replace("$$", "").replace(chr(10), "").replace(chr(92), "")
        inv_content = inv_norm.replace("$$", "").replace(chr(10), "").replace(chr(92), "")
        if inv_content in orig_content or orig_content in inv_content:
            # One content is a substring of the other -> deletion/insertion
            if len(inv_content) < len(orig_content):
                return "deletion (recognition loss: {})".format(
                    ", ".join(sorted(deleted)) if deleted else "content")
            else:
                return "insertion (hallucination: {})".format(
                    ", ".join(sorted(inserted)) if inserted else "content")
        # Different symbols recognized -> substitution
        parts = []
        if deleted:
            parts.append("removed: {}".format(", ".join(sorted(deleted))))
        if inserted:
            parts.append("added: {}".format(", ".join(sorted(inserted))))
        return "substitution ({})".format("; ".join(parts))

    error_class = classify_error(original_latex, inverted_latex)

    result = {
        "crop_name": crop_name,
        "crop_path": str(crop_path),
        "source_sha256": source_sha,
        "crop_dimensions": list(original_pil.size),
        "transformation_identity": {
            "inversion_operation": "pixel_wise_subtraction_from_255",
            "inversion_formula": "inverted = 255 - original (per channel, uint8)",
            "source_hash": source_sha,
            "dimensions_px": list(original_pil.size),
            "pix2text_version": "1.1.7",
            "pix2text_model": "pix2text-mfd-1.5-onnx",
            "recognition_method": "p2t.recognize(pil_image)",
        },
        "original_latex": original_latex,
        "inverted_latex": inverted_latex,
        "exact_match": exact_match,
        "original_char_count": original_chars,
        "inverted_char_count": inverted_chars,
        "char_count_diff": char_diff,
        "error_classification": error_class,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    results.append(result)

# Write results
report = {
    "experiment": "ocr_polarity_ablation",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "crops_tested": len(results),
    "denominators": {
        "total": len(results),
        "exact_matches": sum(1 for r in results if r["exact_match"]),
        "nonempty_original": sum(1 for r in results if r["original_latex"].strip()),
        "nonempty_inverted": sum(1 for r in results if r["inverted_latex"].strip()),
        "nonempty_to_empty": sum(1 for r in results if r["original_latex"].strip() and not r["inverted_latex"].strip()),
        "empty_to_nonempty": sum(1 for r in results if not r["original_latex"].strip() and r["inverted_latex"].strip()),
        "nonempty_to_nonempty": sum(1 for r in results if r["original_latex"].strip() and r["inverted_latex"].strip()),
        "empty_to_empty": sum(1 for r in results if not r["original_latex"].strip() and not r["inverted_latex"].strip()),
    },
    "error_classifications": {},
    "results": results,
}

for r in results:
    ec = r["error_classification"]
    report["error_classifications"][ec] = report["error_classifications"].get(ec, 0) + 1

report_path = OUTPUT_DIR / "ocr_polarity_ablation_report.json"
report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

# Summary
print("\n" + "=" * 60)
print("OCR POLARITY ABLATION SUMMARY")
print("=" * 60)
print(f"Total crops tested: {len(results)}")
exact_matches = sum(1 for r in results if r["exact_match"])
print(f"Exact LaTeX agreement: {exact_matches}/{len(results)}")
print()
for r in results:
    match_str = "MATCH" if r["exact_match"] else "DIFFER"
    print(f"  {r['crop_name']}: {match_str} (orig={r['original_char_count']}ch, inv={r['inverted_char_count']}ch)")
    if not r["exact_match"]:
        print(f"    Original: {r['original_latex']!r}")
        print(f"    Inverted: {r['inverted_latex']!r}")

print(f"\nReport: {report_path}")