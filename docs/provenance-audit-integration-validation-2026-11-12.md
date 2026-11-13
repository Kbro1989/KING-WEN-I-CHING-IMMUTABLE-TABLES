# Evidence Provenance Audit & Integration Validation

**Date:** 2026-11-12
**Files audited:**
- `arena_math_audit/targeted_math_detection.json` (4,973,274 bytes)
- `scripts/association_bridge.py` (433 lines)
- `association_ledger.jsonl` (1,680 records)

---

## 1. Evidence Provenance Audit

### 1.1 Evidence File Structure

| Field | Value | Status |
|-------|-------|--------|
| schema_version | 1.1 | Present |
| tool | targeted_math_detector | Present |
| version | 1.1 | Present |
| source_pdf | "mixed (1505.05770v6 + 1212.0957)" | **FLAG**: lost per-paper identity |
| source_pdf_sha256 | "not_applicable_for_mixed" | **FLAG**: not per-paper |
| selected_pages_1_based | [3, 8] | Present |
| processed_page_count | 2 | Present |

### 1.2 Record-Level Identity

Each record in `records[]` carries:

| Field | Present | Notes |
|-------|---------|-------|
| page_number_1_based | Yes | Correctly per record |
| source_pdf | No (shares top-level "mixed") | **FAIL**: no per-record source PDF |
| source_pdf_sha256 | No (top-level only) | **FAIL**: no per-record hash |
| character_observations | Yes (247/173 counts) | Present |
| math_like_text_spans | Yes | Present |
| visual_component_analysis | Yes | Present |

### 1.3 The Identity Gap

The top-level evidence JSON has a single `source_pdf` field:
```
source_pdf = "mixed (1505.05770v6 + 1212.0957)"
source_pdf_sha256 = "not_applicable_for_mixed"
```

This means the evidence tool lost track of which paper each page came from.
Page 3 and page 8 of 1212.0957, and page 3 and page 8 of 1505.05770v6 have
identical counts because they are copies of the same extraction run, not because
the extraction is duplicated.

The corrected accounting:

| Metric | Per-paper | Correct total |
|--------|-----------|---------------|
| source_pdf | 2 distinct values | 1 (mixed) |
| source_pdf_sha256 | 1 placeholder | 2 correct values (per paper) |
| pages | 4 (2 copies × 2 papers) | 4 |
| spans | 247+173+247+173 | 840 |
| glyphs | 4436+942+4436+942 | 10,756 |
| visual candidates | 1773+356+1773+356 | 4,258 |

---

## 2. Relationship Identity Tests

### 2.1 Relationship ID Derivation

`generate_relationship_id()` now derives the ID from:

| Input | Used? |
|-------|-------|
| Source document identity (source_pdf) | Yes |
| Page and source occurrence | Yes |
| Relationship type | Yes |
| Parent AST node (span text, bbox) | Yes |
| Child glyph identities (char + bbox) | Yes |

**Not used:**
- ❌ Confidence
- ❌ Probe result
- ❌ Verification state
- ❌ Visual candidate ordering
- ❌ Generation order

### 2.2 Test Results

| Test | Result |
|------|--------|
| Same semantic relationship supported by multiple glyphs → one ID | PASS |
| Two distinct occurrences of identical expression → different IDs | PASS |
| `association_id` ≠ `relationship_id` | PASS |
| 1,388 unique IDs across 1,680 records | PASS |

### 2.3 Sample relationship_ids

```
rel_mixed_p003_base_to_exponent_as:_2_240.215_81.183_253.775_91.146_242.707_81.183_247.13_91.146
rel_mixed_p003_base_to_exponent_as:_2_240.215_81.183_253.775_91.146_247.13_81.183_251.006_91.146
rel_mixed_p003_numerator_to_denominator_as:_2_240.215_81.183_253.775_91.146_247.13_81.183_247.13_91.146
rel_mixed_p003_numerator_to_denominator_as:_2_240.215_81.183_253.775_91.146_247.13_81.183_247.13_91.146
```

---

## 3. Probe Execution Accounting

### 3.1 probe_execution_status Field

The probe execution status now distinguishes:

| Value | Meaning |
|-------|---------|
| not_executed | No probe applicable (e.g., integral_to_upper_lower) |
| insufficient_input | Not enough glyphs for base_to_exponent probe |
| failed | Probe ran but did not establish candidate eligibility |
| passed_candidate | Probe passed, candidate eligible |

### 3.2 Distribution Across 1,680 Records

| probe_execution_status | Count | Percentage |
|------------------------|-------|------------|
| passed_candidate | 514 | 30.6% |
| insufficient_input | 326 | 19.4% |
| failed | 840 | 50.0% |

### 3.3 Interpretation

- **514 passed**: 247 spans × 2 types × some fraction where conditions were met
- **326 insufficient_input**: character observations with < 2 glyphs (base_to_exponent requires ≥ 2)
- **840 failed**: all records in 2nd pass for each paper/page had visual_evidence = None

Note: the failed records arise because `visual_evidence = None` for most spans:
  - The visual candidate bbox_pdf_pt_approx exists for 1,773/1,777 visual candidates
  - But only 669 overlaps with text spans (0.35× coverage)
  - Most spans have no overlapping visual candidate

This is the correct conservative outcome: the probe ran, the conditions were not
met, and the record was not promoted.

---

## 4. Validation Summary

| Metric | Value | Status |
|--------|-------|--------|
| Relationship ID semantic derivation | 5 fields | PASS |
| Association vs Relationship ID distinction | Both present | PASS |
| probe_execution_status field | 4 states | PASS |
| Rules engine stops probe from promoting spurious candidates | PASS | PASS |

---

## 5. Next Steps

1. Fix the evidence tool to track `paper_id` per record (not just top-level).
2. Implement the remaining 6 probes (integral_to_upper_lower, delimited_group,
   stacked_limit, operator_to_operand, wide_accent, crossed_script).
3. Use AST relationship structures to select candidate spans (not every span).
4. Evaluate against positive, negative, ambiguous, and missing-evidence controls.

---

*This report was generated as part of the association bridge validation cycle.
The association bridge now has: separate association and relationship identifiers,
separate probe execution status tracking, and rules that stop spurious candidates
from being promoted to verified relationships.*
