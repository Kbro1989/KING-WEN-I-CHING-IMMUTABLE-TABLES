"""Regression tests for the Pix2Text candidate harvest script.

These tests cover:
- candidate record structure (all required fields present)
- malformed-page graceful recovery (pages 14/16/17/18/19)
- PAGE-12 parser matching behaviour
- candidate classification (FORMULA -> DISPLAY_EQUATION, etc.)
- reproducibility metadata (pix2text_version, input_sha256, etc.)

IMPORTANT: This test file must not touch the frozen benchmark
(DATASETS/candidates_1907.04931.json) or any existing artifacts.
All verification is read-only against the generated
DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_candidates.jsonl.
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

OUT_PATH = os.path.join(
    REPO_ROOT,
    "DATASETS",
    "PDF_FIDELITY_RENDERINGS",
    "1907_04931",
    "pix2text_candidates.jsonl",
)

REQUIRED_FIELDS = {
    "paper_id", "pdf_sha256", "page_index", "pdf_page", "render_sha256",
    "image_path", "pix2text_element_id", "element_index", "element_type",
    "bbox_original", "raw_ocr", "element_score", "metadata_score",
    "parser_match_ids", "match_status", "adjudication", "candidate_class",
    "parse_error", "source_image_sha256", "pix2text_version",
    "input_sha256", "harvest_script_sha256", "harvest_script_version",
}

MALFORMED_PAGES = {14, 16, 17, 18, 19}
EXPECTED_TOTAL_RECORDS = 158  # 18 + 38 + 54 + 11 + 17 + 9 + 9 + 2


def load_records():
    records = []
    with open(OUT_PATH, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def test_record_structure():
    """All required fields must be present on every record."""
    records = load_records()
    missing = []
    for i, rec in enumerate(records):
        miss = REQUIRED_FIELDS - set(rec.keys())
        if miss:
            missing.append((i, sorted(miss)))
    assert not missing, f"Records with missing fields: {missing[:5]}"
    # Every record must have a non-null paper_id
    assert all(r["paper_id"] == "1907.04931" for r in records)
    print(f"PASS: record structure — {len(records)} records, all required fields present")


def test_malformed_pages():
    """Malformed repr pages must produce PROSE records, never crash."""
    records = load_records()
    for page in MALFORMED_PAGES:
        page_recs = [r for r in records if r["pdf_page"] == page]
        assert page_recs, f"No records for malformed page {page}"
        assert all(r["candidate_class"] == "PROSE" for r in page_recs), \
            f"Page {page}: expected PROSE classes, got {[r['candidate_class'] for r in page_recs]}"
        assert all(r["parse_error"] is not None for r in page_recs), \
            f"Page {page}: malformed pages must record a parse_error"
    print("PASS: malformed-page recovery — pages 14/16/17/18/19 handled gracefully")


def test_page12_parser_match():
    """Page 12 must have parser_match_ids attached to spatially-matched records."""
    records = load_records()
    p12 = [r for r in records if r["pdf_page"] == 12]
    matched = [r for r in p12 if r["parser_match_ids"]]
    assert len(matched) >= 1, "Page 12 should have at least one parser match"
    # Every matched record must have a non-empty parser_match_ids
    for rec in matched:
        assert rec["parser_match_ids"], "parser_match_ids must not be empty for matched records"
    print(f"PASS: page-12 parser match — {len(matched)} records matched parser candidates")


def test_candidate_classification():
    """FORMULA elements must be CLASSIFIED as DISPLAY_EQUATION, not PROSE."""
    records = load_records()
    formula_recs = [r for r in records if r["element_type"] == "FORMULA"]
    assert formula_recs, "No FORMULA records found"
    assert all(r["candidate_class"] == "DISPLAY_EQUATION" for r in formula_recs), \
        "FORMULA elements must be classified as DISPLAY_EQUATION"
    print(f"PASS: candidate classification — {len(formula_recs)} FORMULA records = DISPLAY_EQUATION")


def test_reproducibility_metadata():
    """Records must carry version/input/script provenance."""
    records = load_records()
    first = records[0]
    assert first["pix2text_version"], "pix2text_version must not be empty"
    assert first["input_sha256"], "input_sha256 must not be empty"
    assert first["harvest_script_sha256"], "harvest_script_sha256 must not be empty"
    assert first["harvest_script_version"], "harvest_script_version must not be empty"
    assert first["source_image_sha256"] is None or \
        isinstance(first["source_image_sha256"], str), \
        "source_image_sha256 must be a string or null"
    print("PASS: reproducibility metadata — version/input/script anchors present")


def test_total_record_count():
    """Total records across all pages must equal 158."""
    records = load_records()
    assert len(records) == EXPECTED_TOTAL_RECORDS, \
        f"Expected {EXPECTED_TOTAL_RECORDS} records, got {len(records)}"
    print(f"PASS: total record count — {len(records)} == {EXPECTED_TOTAL_RECORDS}")


def main():
    test_record_structure()
    test_malformed_pages()
    test_page12_parser_match()
    test_candidate_classification()
    test_reproducibility_metadata()
    test_total_record_count()
    print("\nAll pix2text-harvest regression tests passed.")


if __name__ == "__main__":
    main()
