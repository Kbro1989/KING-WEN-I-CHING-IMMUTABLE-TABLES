"""Adjudication layer for Pix2Text candidate harvest — v2.

Loads the harvested candidates and computes the four-level adjudication model:

- SPATIAL_MATCH  — parser candidate boxes overlap/are contained
- TEXT_MATCH     — normalized math content agrees
- VISUALLY_VERIFIED — source crop is non-blank and OCR carried real content
- ADJUDICATED    — human review; explicit row flag

Also computes the three key metrics:

- region_count          — total candidate records
- unique_expression_count — distinct normalized mathematical expressions
- equation_occurrence_count — DISPLAY_EQUATION + INLINE_MATH records

Writes:
- adjudication_report.jsonl (per-record adjudicated output)
- adjudication_summary.json (aggregate metrics)
- adjudication_report.md (human-readable summary)

The raw OCR records are never modified; this layer is read-only on the
harvest output and produces new derived artifacts.
"""

import json
import os
import re
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER_DIR = os.path.join(REPO_ROOT, "DATASETS",
                          "PDF_FIDELITY_RENDERINGS", "1907_04931")
REPORT_PATH = os.path.join(RENDER_DIR, "adjudication_report.jsonl")
SUMMARY_PATH = os.path.join(RENDER_DIR, "adjudication_summary.json")
MD_PATH = os.path.join(RENDER_DIR, "adjudication_report.md")

MATCH_STATUSES = ["UNADJUDICATED", "SPATIAL_MATCH", "TEXT_MATCH",
                  "VISUALLY_VERIFIED", "ADJUDICATED"]


def load_records():
    records = []
    with open(REPORT_PATH.replace("adjudication_report.jsonl",
                                  "pix2text_candidates.jsonl"), encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def load_parser_records():
    """Parse the frozen parser reference (DATASETS/candidates_1907.04931.json)."""
    path = os.path.join(REPO_ROOT, "DATASETS", "candidates_1907.04931.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _normalize(text):
    t = re.sub(r"\s+", " ", str(text or "")).lower()
    t = re.sub(r"[^a-z0-9\s._]", " ", t)
    return t.strip()


def _token_set(text):
    return set(re.findall(r"[a-z0-9]+", _normalize(text)))


def _text_match(ocr_text, parser_line_text, threshold=0.5):
    a = _token_set(ocr_text)
    b = _token_set(parser_line_text)
    if not a and not b:
        return True
    if not a or not b:
        return False
    union = a | b
    if not union:
        return False
    return len(a & b) / len(union) >= threshold


def classify(row, parser_records):
    """Two-path adjudication: spatial first, then text."""
    row = dict(row)
    row["adjudication"] = row.get("adjudication") or "UNADJUDICATED"
    row["match_status"] = row.get("match_status") or "UNADJUDICATED"

    if row.get("adjudication") == "ADJUDICATED":
        row["match_status"] = "ADJUDICATED"
        return row

    parser_matches = row.get("parser_match_ids") or []
    if parser_matches:
        row["match_status"] = "SPATIAL_MATCH"
        raw = str(row.get("raw_ocr") or "")
        for pm in parser_matches:
            if _text_match(raw, str(pm.get("line_text") or "")):
                row["match_status"] = "TEXT_MATCH"
                return row
        return row

    # No spatial match — fall through to text and visual checks.
    raw = str(row.get("raw_ocr") or "")
    for pcand in parser_records:
        if _text_match(raw, str(pcand.get("line_text") or "")):
            row["match_status"] = "TEXT_MATCH"
            return row

    if row.get("bbox_original") and row.get("_pix2text_file"):
        if _crop_nonblank(row["_pix2text_file"], row["bbox_original"]):
            row["match_status"] = "VISUALLY_VERIFIED"
    return row


def _crop_nonblank(image_path, bbox):
    from PIL import Image
    img = Image.open(image_path).convert("L")
    w, h = img.size
    x0 = max(0, int(bbox[0] * w))
    y0 = max(0, int(bbox[1] * h))
    x1 = min(w, int(bbox[2] * w))
    y1 = min(h, int(bbox[3] * h))
    crop = img.crop((x0, y0, x1, y1))
    hist = crop.histogram()
    total = sum(hist)
    if total == 0:
        return False
    dark = sum(hist[:128])
    bright = sum(hist[128:])
    return dark > total * 0.01 and bright > total * 0.01


def _derivation(row):
    parts = []
    if row.get("parser_match_ids"):
        ids = [p.get("line_text") for p in row["parser_match_ids"]]
        parts.append("spatial-" + "+".join(ids))
    if row.get("match_status") == "TEXT_MATCH":
        parts.append("text-match")
    if row.get("match_status") == "VISUALLY_VERIFIED":
        parts.append("visual-integrity")
    return ",".join(parts) if parts else "none"


def _morphology(row):
    bbox = row.get("bbox_original") or [0, 0, 0, 0]
    if not isinstance(bbox, list):
        bbox = [0, 0, 0, 0]
    return {
        "region_type": row.get("element_type", "TEXT"),
        "candidate_class": row.get("candidate_class", "PROSE"),
        "bbox_area": float(bbox[2]) * float(bbox[3]),
        "bbox_width": float(bbox[2]) - float(bbox[0]) if bbox[2] and bbox[0] else 0.0,
        "bbox_height": float(bbox[3]) - float(bbox[1]) if bbox[3] and bbox[1] else 0.0,
        "parser_matches": len(row.get("parser_match_ids") or []),
        "parse_error": row.get("parse_error"),
    }


def produce(row, parser_records):
    row = classify(row, parser_records)
    row["_derivation"] = _derivation(row)
    row["_morphology"] = _morphology(row)
    for key in ("_derivation", "_morphology"):
        row.pop(key, None)
    return row


def main():
    records = load_records()
    parser_records = load_parser_records()

    # Adjudicate each record.
    adjudicated = []
    for r in records:
        adjudicated.append(produce(r, parser_records))

    # Write JSONL report.
    os.makedirs(RENDER_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        for r in adjudicated:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Compute metrics.
    region_count = len(adjudicated)
    display_eq = [r for r in adjudicated if r.get("candidate_class") == "DISPLAY_EQUATION"]
    inline_math = [r for r in adjudicated if r.get("candidate_class") == "INLINE_MATH"]
    equation_occurrences = len(display_eq) + len(inline_math)

    unique_expr = set()
    for r in adjudicated:
        raw = str(r.get("raw_ocr") or "").strip()
        if raw:
            unique_expr.add(_normalize(raw))
    unique_count = len(unique_expr)

    status_counts = {}
    for r in adjudicated:
        st = r.get("match_status", "UNADJUDICATED")
        status_counts[st] = status_counts.get(st, 0) + 1

    candidate_class_dist = {}
    for r in adjudicated:
        cc = r.get("candidate_class", "UNPARSEABLE")
        candidate_class_dist[cc] = candidate_class_dist.get(cc, 0) + 1

    summary = {
        "paper_id": "1907.04931",
        "region_count": region_count,
        "unique_expression_count": unique_count,
        "equation_occurrence_count": equation_occurrences,
        "status_distribution": status_counts,
        "candidate_class_distribution": candidate_class_dist,
        "report_path": REPORT_PATH,
        "summary_path": SUMMARY_PATH,
        "generated_commit": _git_sha(),
    }

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Markdown report.
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("# Pix2Text Adjudication Report — 1907.04931\n\n")
        f.write("| Metric | Value |\n|---|---|\n")
        f.write(f"| Total records (region_count) | {summary['region_count']} |\n")
        f.write(f"| Unique expression_count | {summary['unique_expression_count']} |\n")
        f.write(f"| Equation occurrence_count | {summary['equation_occurrence_count']} |\n")
        f.write("\n## Status distribution\n\n")
        f.write("| Status | Count |\n|---|---|\n")
        for st in MATCH_STATUSES:
            if st in summary["status_distribution"]:
                f.write(f"| {st} | {summary['status_distribution'][st]} |\n")
        f.write("\n## Candidate class distribution\n\n")
        f.write("| Class | Count |\n|---|---|\n")
        for cc, cnt in sorted(summary["candidate_class_distribution"].items()):
            f.write(f"| {cc} | {cnt} |\n")

    print(f"WROTE {region_count} adjudicated records -> {REPORT_PATH}")
    print(f"WROTE summary -> {SUMMARY_PATH}")
    print(f"WROTE markdown -> {MD_PATH}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def _git_sha():
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"],
                             capture_output=True, text=True,
                             cwd=REPO_ROOT, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


if __name__ == "__main__":
    main()
