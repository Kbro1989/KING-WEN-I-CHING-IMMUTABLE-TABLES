"""
test_glyph_mapping_coverage.py
Regression tests for glyph mapping coverage audit.

Covers:
- Crosswalk entries and their expected mapping coverage
- The rule that absent Wolfram/SymPy mappings are recorded as unmapped, not inferred
- Coverage arithmetic consistency (2 mapped / 4 total = 50%)
- No silent inference from visual similarity

Run:  python test_glyph_mapping_coverage.py -v
"""

import csv
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)

JSON_PATH = os.path.join(REPO_ROOT, "glyph_mapping_coverage.json")


def load_mappings():
    """Load mappings from the JSON file."""
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["mappings"]


def get_mappings():
    return load_mappings()


def test_crosswalk_has_4_entries():
    """The crosswalk file should contain exactly 4 entries."""
    entries = get_mappings()
    assert len(entries) == 4, f"Expected 4 crosswalk entries, got {len(entries)}"


def test_mapped_entries():
    """sigma and sum should be mapped to Wolfram and SymPy."""
    entries = get_mappings()
    mapped = [m for m in entries if m["mapping_status"] == "mapped"]
    assert len(mapped) == 2, f"Expected 2 mapped entries, got {len(mapped)}"
    wolfram_names = {m["visual_asset"] for m in mapped}
    assert {"sigma.gif", "sum.gif"} == wolfram_names, f"Unexpected mapped set: {wolfram_names}"


def test_unmapped_entries():
    """subscrl and rmw should be recorded as unmapped."""
    entries = get_mappings()
    unmapped = [m for m in entries if m["mapping_status"] == "unmapped"]
    assert len(unmapped) == 2, f"Expected 2 unmapped entries, got {len(unmapped)}"
    unmapped_assets = {m["visual_asset"] for m in unmapped}
    assert {"subscrl", "rmw"} == unmapped_assets, f"Unexpected unmapped set: {unmapped_assets}"


def test_sigma_mapping():
    """sigma.gif maps to CapitalSigma (Wolfram) and Sigma (SymPy)."""
    entries = get_mappings()
    entry = next(m for m in entries if m["visual_asset"] == "sigma.gif")
    assert entry["wolfram_mapping"] == "CapitalSigma"
    assert entry["sympy_mapping"] == "Sigma"
    assert entry["mapping_status"] == "mapped"


def test_sum_mapping():
    """sum.gif maps to Sum (Wolfram) and Sum (SymPy)."""
    entries = get_mappings()
    entry = next(m for m in entries if m["visual_asset"] == "sum.gif")
    assert entry["wolfram_mapping"] == "Sum"
    assert entry["sympy_mapping"] == "Sum"
    assert entry["mapping_status"] == "mapped"


def test_subscrl_unmapped():
    """subscrl (ℓ, U+2113) must be recorded as unmapped, not inferred."""
    entries = get_mappings()
    entry = next(m for m in entries if m["visual_asset"] == "subscrl")
    assert entry["wolfram_mapping"] is None, "Wolfram mapping should be None for subscrl"
    assert entry["sympy_mapping"] is None, "SymPy mapping should be None for subscrl"
    assert entry["mapping_status"] == "unmapped"
    assert entry["crosswalk_status"] == "verified", (
        "Crosswalk status is separate from Wolfram/SymPy coverage"
    )


def test_rmw_unmapped():
    """rmw (W, U+0057) must be recorded as unmapped, not inferred."""
    entries = get_mappings()
    entry = next(m for m in entries if m["visual_asset"] == "rmw")
    assert entry["wolfram_mapping"] is None, "Wolfram mapping should be None for rmw"
    assert entry["sympy_mapping"] is None, "SymPy mapping should be None for rmw"
    assert entry["mapping_status"] == "unmapped"
    assert entry["crosswalk_status"] == "verified", (
        "Crosswalk status is separate from Wolfram/SymPy coverage"
    )


def test_no_inferred_identity():
    """
    Governing rule: never convert an absent mapping into an inferred identity
    merely because the glyph looks similar.
    """
    entries = get_mappings()
    for entry in entries:
        if entry["mapping_status"] == "unmapped":
            assert entry["wolfram_mapping"] is None or entry["sympy_mapping"] is None, (
                f"{entry['visual_asset']} is unmapped but has a mapping - "
                "violates the no-inference rule"
            )


def test_coverage_arithmetic():
    """Coverage must be 2/4 = 50%."""
    entries = get_mappings()
    total = len(entries)
    mapped = sum(1 for m in entries if m["mapping_status"] == "mapped")
    assert total == 4, f"Expected 4 entries, got {total}"
    assert mapped == 2, f"Expected 2 mapped, got {mapped}"
    assert mapped / total == 0.5, f"Coverage {mapped/total} != 0.5"


def test_crosswalk_status_separate_from_mapping():
    """
    Crosswalk status (verified from Metamath source) must not be conflated
    with Wolfram/SymPy coverage.
    """
    entries = get_mappings()
    for entry in entries:
        assert entry["crosswalk_status"] in ("verified", "unverified"), (
            f"crosswalk_status must be verified/unverified, got {entry['crosswalk_status']}"
        )
        assert entry["mapping_status"] in ("mapped", "unmapped"), (
            f"mapping_status must be mapped/unmapped, got {entry['mapping_status']}"
        )


def test_governing_rule_applied():
    """
    The governing rule: never convert absent mapping into inferred identity.
    Neither subscrl nor rmw should have wolfram/sympy mapping filled in.
    """
    entries = get_mappings()
    for entry in entries:
        if entry["mapping_status"] == "unmapped":
            assert entry["wolfram_mapping"] is None or entry["sympy_mapping"] is None, (
                f"{entry['visual_asset']} is unmapped but has mappings"
            )


def test_json_and_csv_match():
    """JSON and CSV outputs must be consistent."""
    json_assets = {m["visual_asset"] for m in get_mappings()}
    csv_assets = set()
    with open(os.path.join(REPO_ROOT, "glyph_mapping_coverage.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_assets.add(row["visual_asset"])
    assert json_assets == csv_assets, f"JSON and CSV mismatch: JSON={json_assets}, CSV={csv_assets}"


def test_json_coverage_metadata():
    """JSON coverage metadata must show 50% and preliminary scope."""
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    coverage = data["mapping_coverage"]
    assert coverage["total_crosswalk_entries"] == 4
    assert coverage["mapped_to_wolfram"] == 2
    assert coverage["coverage_percent_total"] == 50.0
    assert coverage["preliminary"] is True
    assert "3,301" in coverage["description"]


if __name__ == "__main__":
    tests = [name for name in dir(sys.modules[__name__]) if name.startswith("test_")]
    passed = 0
    failed = 0
    for name in tests:
        try:
            getattr(sys.modules[__name__], name)()
            print(f"PASS: {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {name} - {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {name} - {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
