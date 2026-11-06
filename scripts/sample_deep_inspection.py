import json
from pathlib import Path

report_path = Path("DATASETS/audit_rendered_png_producers_report.json")
with open(report_path, "r", encoding="utf-8") as f:
    d = json.load(f)

print("=== SAMPLE TARGETED OCR CROPS ===")
t_crops = d["producers"]["targeted_ocr"]["sample_analyzed_crops"]
for c in t_crops[:12]:
    print(f"File: {c['filename']}")
    print(f"  Dimensions: {c['width']}x{c['height']} (AR: {c['aspect_ratio']}), Ink ratio: {c['ink_ratio']}")
    print(f"  Border touch 1px: {c['border_touch_1px']}, Min margin: {c['min_margin_px']}px, Margins: {c['margins']}")
    print(f"  OCR: {c['ocr_result']}")
    print()

print("=== SAMPLE 2009.00031 NEGATIVE CONTROL CROPS ===")
neg_crops = [c for c in t_crops if "2009.00031" in c["filename"]]
for c in neg_crops[:6]:
    print(f"File: {c['filename']}")
    print(f"  Dimensions: {c['width']}x{c['height']}, Border touch 1px: {c['border_touch_1px']}")
    print(f"  OCR Result (Hallucinated formula): {c['ocr_result']}")
    print()

print("=== SAMPLE VISUAL RECOVERY PAGES ===")
v_pages = d["producers"]["visual_recovery"]["sample_analyzed_pages"]
for p in v_pages[:8]:
    print(f"File: {p['filename']}")
    print(f"  Dimensions: {p['width']}x{p['height']} (Size: {p['file_size_kb']} KB)")
    print(f"  Annotation px: Blue (text): {p['annotation_pixels']['blue_text_boundary']}, "
          f"Green (clean): {p['annotation_pixels']['green_clean_math']}, "
          f"Yellow (touch): {p['annotation_pixels']['yellow_boundary_touch']}, "
          f"Purple (stretch): {p['annotation_pixels']['purple_stretched_partial']}, "
          f"Red (no text): {p['annotation_pixels']['red_no_text']}")
    print()

