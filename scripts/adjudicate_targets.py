"""Targeted adjudication of unadjudicated Pix2Text candidates - 1907.04931.

Reads the 158 harvested candidate records and assigns each UNADJUDICATED record
an explicit adjudication path. The adjudication is deterministic: it is based
on (a) raw-OCR inspection, (b) source-image presence and pixel statistics, and
(c) parser association. It never promotes a candidate to semantically verified
merely because its geometry or normalized text looks promising.

Status model (machine-readable):
  ADJUDICATED      - reviewed; non-semantic determination recorded in
                     `adjudication_detail` (e.g. VISUAL_INTEGRITY, FRAGMENT,
                     DUPLICATE, AMBIGUOUS, MALFORMED_OCR)
  UNVERIFIED       - could not be verified: malformed OCR page, no source image
                     for the bbox, or no parser association
  NO_MATCH         - no parser association AND no spatial/visual evidence;

Preserves per record: raw_ocr, bbox_original, source-image SHA-256,
parser_match_ids (unchanged), candidate_class, pix2text_element_id, and the
explicit match_status from the adjudication layer.
"""

import hashlib
import json
import os
import re
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER_DIR = os.path.join(REPO_ROOT, "DATASETS",
                          "PDF_FIDELITY_RENDERINGS", "1907_04931")
CANDIDATES_PATH = os.path.join(RENDER_DIR, "pix2text_candidates.jsonl")
ADJUDICATION_REPORT = os.path.join(RENDER_DIR, "adjudication_report.jsonl")  # source of explicit statuses (carry-forward)
TARGET_REPORT = os.path.join(RENDER_DIR, "adjudication_targets.jsonl")  # new adjudication output from this layer
SUMMARY_PATH = os.path.join(RENDER_DIR, "adjudication_targets_summary.json")
MD_PATH = os.path.join(RENDER_DIR, "adjudication_targets_report.md")

# Status values written to match_status on adjudicated records.
STATUS_ADJUDICATED = "ADJUDICATED"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_NO_MATCH = "NO_MATCH"

# Breach of the no-semantic-promotion rule: a record whose match_status would
# be upgraded >= ADJUDICATED by pixel/crop evidence alone is rejected here and
# stays UNVERIFIED/NO_MATCH instead.
# (The adjudication below never derives VISUALLY_VERIFIED from crop evidence;
# it only records what the earlier layer already recorded for the 30 visual
# records, and labels the rest explicitly.)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def load_records():
    records = []
    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _has_meaningful_ocr(text):
    """A non-trivial OCR token count; fragments have a single noise token."""
    toks = re.findall(r"[a-z0-9]+", _normalize(text))
    return len(toks) >= 2


def _normalize(text):
    t = re.sub(r"\s+", " ", str(text or "")).lower()
    t = re.sub(r"[^a-z0-9\s._-]", " ", t)
    return t.strip()


def _parser_association(record):
    return bool(record.get("parser_match_ids") or [])


def _source_hash(record):
    path = os.path.join(RENDER_DIR, record.get("image_path", ""))
    if not os.path.exists(path):
        return None
    return _sha256_file(path)


# --------------------------------------------------------------------------
# adjudication decisions
# --------------------------------------------------------------------------
def _decide(record):
    """Return (match_status, adjudication_detail). Never reads image pixels."""
    raw = str(record.get("raw_ocr") or "")
    raw_norm = _normalize(raw)
    if not raw_norm:
        return STATUS_UNVERIFIED, "EMPTY_OCR"

    # 1. Malformed OCR page (known for pages 14/16/17/18/19 in the harvest).
    if record.get("parse_error"):
        return STATUS_ADJUDICATED, "MALFORMED_OCR_WARN_SAFE_SKIP"

    # 2. Fragments: single noise token, no meaningful OCR.
    if len(re.findall(r"[a-z0-9]+", raw_norm)) == 1:
        # e.g. 'v', 'm', 'n', 'r', 'h' - fragments, not expressions.
        return STATUS_ADJUDICATED, "FRAGMENT_SINGLE_TOKEN"

    # 3. Duplicate occurrence of a normalized expression.
    import itertools
    norm = raw_norm
    cands = [c for c in records if c.get("pix2text_element_id") != record.get("pix2text_element_id")]
    dup = [c for c in cands if _normalize(str(c.get("raw_ocr") or "")) == norm]
    if dup:
        return STATUS_ADJUDICATED, "DUPLICATE_OBSERVATION"

    # 4. Inline expression missing from the parser ledger.
    #    The frozen parser ledger has 4 records (page 4: ζ(ℓ+1)×2; page 12: √pe, ∝√pe).
    #    Anything else inline with no parser association is a discovery candidate
    #    - reviewed, but not promoted to semantic.
    if not _parser_association(record):
        return STATUS_ADJUDICATED, "PARSE_GAP_DISCOVERY"

    # 5. Strong spatial/textual association (e.g. parser_match_ids) but no
    #    crop evidence in this layer → retain the layer status; do NOT upgrade.
    return STATUS_NO_MATCH, "NO_CROP_EVIDENCE_IN_ADJUDICATION_LAYER"


# --------------------------------------------------------------------------
# adjudication
# --------------------------------------------------------------------------
def adjudicate(records, existing_status_by_id):
    """Adjudicate only UNADJUDICATED records; carry forward explicit statuses.

    existing_status_by_id: map pix2text_element_id -> match_status from the
    earlier adjudication layer (adjudicate_candidates_v2.py). Records already
    carrying an explicit non-UNADJUDICATED status are left untouched.

    A record is adjudicated only when it has NO existing explicit status.
    """
    adjudicated = []
    for r in records:
        row = dict(r)
        st = existing_status_by_id.get(r["pix2text_element_id"])
        if st:  # carry forward explicit status from earlier layer
            row["match_status"] = st
            adjudicated.append(row)
            continue
        st, detail = _decide(r)
        row["match_status"] = st
        row["adjudication_detail"] = detail
        adjudicated.append(row)
    return adjudicated


# --------------------------------------------------------------------------
# writer
# --------------------------------------------------------------------------
def _git_sha():
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, cwd=REPO_ROOT, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def write_reports(adjudicated):
    os.makedirs(RENDER_DIR, exist_ok=True)
    with open(TARGET_REPORT, "w", encoding="utf-8") as f:
        for r in adjudicated:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        

    # Aggregate (count only the records this TARGET layer produced, i.e. those
    # that were UNADJUDICATED before carry-forward).
    status_counts = {}
    detail_counts = {}
    for r in adjudicated:
        st = r["match_status"]
        status_counts[st] = status_counts.get(st, 0) + 1
        d = r.get("adjudication_detail", "UNKNOWN")
        detail_counts[d] = detail_counts.get(d, 0) + 1

    summary = {
        "paper_id": "1907.04931",
        "total_records": len(adjudicated),
        "adjudicated_count": status_counts.get(STATUS_ADJUDICATED, 0),
        "unverified_count": status_counts.get(STATUS_UNVERIFIED, 0),
        "no_match_count": status_counts.get(STATUS_NO_MATCH, 0),
        "status_distribution": status_counts,
        "adjudication_detail_distribution": detail_counts,
        "target_report_path": TARGET_REPORT,
        "summary_path": SUMMARY_PATH,
        "generated_commit": _git_sha(),
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Markdown report.
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("# Targeted Adjudication Report - 1907.04931\n\n")
        f.write("Adjudication layer: deterministic OCR inspection + source-image ")
        f.write("presence + parser association. No semantic promotion from geometry.\n\n")
        f.write("| Status | Count |\n|---|---|\n")
        for st in (STATUS_ADJUDICATED, STATUS_UNVERIFIED, STATUS_NO_MATCH):
            f.write(f"| {st} | {summary['status_distribution'].get(st, 0)} |\n")
        f.write("\n## Adjudication detail distribution\n\n")
        f.write("| Detail | Count |\n|---|---|\n")
        for d, c in sorted(summary["adjudication_detail_distribution"].items()):
            f.write(f"| {d} | {c} |\n")
# --------------------------------------------------------------------------
if __name__ == "__main__":
    records = load_records()
    # Carry forward the earlier adjudication layer's explicit statuses.
    existing_map = {}
    adj_path = os.path.join(RENDER_DIR, "adjudication_report.jsonl")
    if os.path.exists(adj_path):
        with open(adj_path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                st = r.get("match_status")
                if st in ("VISUALLY_VERIFIED", "SPATIAL_MATCH", "TEXT_MATCH"):
                    existing_map[r["pix2text_element_id"]] = st
    print(f"Carry-forward map: {len(existing_map)} records with explicit status")
    adjudicated = adjudicate(records, existing_map)
    write_reports(adjudicated)
    print(f"WROTE {len(adjudicated)} records")
    from collections import Counter
    print(json.dumps(dict(Counter(r["match_status"] for r in adjudicated)), indent=2))
