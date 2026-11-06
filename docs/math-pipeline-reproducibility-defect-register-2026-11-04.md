# Math Pipeline Reproducibility Defect Register — 2026-11-04

## Status: READ-ONLY (no source modifications, no commits, no pushes)

This register documents reproducibility defects discovered during the Math Output
Retention and Reproducibility Review. It is a separate, versioned artifact from
the retention review and the candidate audit. Each defect includes evidence,
reproduction conditions, impact, proposed correction direction, and verification
criteria.

## Register metadata

| Field | Value |
|-------|-------|
| Register version | 1.0 |
| Date | 2026-11-04 |
| Scope | Math recovery pipeline reproducibility |
| Source of discovery | Math Output Retention and Reproducibility Review (docs/math-output-retention-review-2026-11-04.md) |
| Governance status | Read-only assessment; no fixes authorized |
| Related artifacts | docs/math-output-candidate-audit-2026-11-04.md, docs/math-output-retention-review-2026-11-04.md, docs/math-output-regeneration-verification-2026-11-04.md, DATASETS/math_output_candidate_manifest_2026-11-04.json |

---

## DEFECT 1: None MathML crash in source_hash()

### ID
MPRD-001

### Severity
Blocking — prevents regeneration of 2 consumer files

### Affected files
- `scripts/math_contract.py` (source_hash function, line ~300)
- `scripts/math_reconstruction_evidence.py` (consumer, crashes at line 761)
- `scripts/cross_stage_drop_trace.py` (consumer, crashes at math_contract.py:300)

### Evidence
```
math_reconstruction_evidence.py:
  File "scripts/math_reconstruction_evidence.py", line 761, in main
    "source_mathml_len": len(mathml),
  TypeError: object of type 'NoneType' has no len()

cross_stage_drop_trace.py:
  File "scripts/math_contract.py", line 300, in source_hash
    return hash_bytes(mathml.encode("utf-8"))
  AttributeError: 'NoneType' object has no attribute 'encode'
```

### Reproduction conditions
1. Run `python scripts/math_reconstruction_evidence.py` from repo root
2. Script processes arxiv HTML corpus equations
3. Some equations have `mathml=None` in the corpus JSON
4. Script calls `len(mathml)` and `source_hash(mathml)` without null check
5. Crash occurs on first None-mathml equation encountered

### Impact
- 2 of 41 content-consuming files cannot be regenerated
- `math_reconstruction_evidence.jsonl` (8.1 MB) and `cross_stage_drop_trace.jsonl` (2.2 MB) are blocked
- Downstream consumers of these files may also be affected

### Root cause
`math_contract.py:source_hash()` assumes `mathml` is always a non-null string.
The function calls `mathml.encode("utf-8")` without checking for None.
The caller (`math_reconstruction_evidence.py:761`) calls `len(mathml)` without null check.

### Proposed correction direction (NOT yet authorized)
Establish an explicit representation policy for MathML availability:

| Input state | Meaning | Hash behavior |
|-------------|---------|---------------|
| `None` | MathML unavailable | Hash a type-tagged null sentinel (e.g., `b"\x00NONE"`) |
| `""` | MathML present but empty | Hash the empty string (distinct from None) |
| Nonempty string | MathML available | Hash the string content |

The hash function should preserve the distinction between unavailable, empty, and present
MathML. Additionally, the hash's purpose (source identity vs. content identity) should
be clarified: if the intended identity is based on paper + locator + occurrence index,
MathML should not silently determine it.

### Verification criteria (for future fix)
1. `source_hash(None)` returns a valid hash without crashing
2. `source_hash("")` returns a different hash from `source_hash(None)`
3. `source_hash("x")` returns a different hash from both
4. `math_reconstruction_evidence.py` runs to completion without TypeError
5. `cross_stage_drop_trace.py` runs to completion without AttributeError
6. Regenerated output hashes are recorded and compared to originals
7. No hash collisions between None/empty/present states

### Status
OPEN — read-only, no fix authorized

---

## DEFECT 2: Training-data population variance

### ID
MPRD-002

### Severity
High — unexplained 20.55× output expansion

### Affected files
- `scripts/build_training_data.py` (generator)
- `DATASETS/extractor_training_data.jsonl` (original, 3,090 lines, 2.0 MB)
- `DATASETS/extractor_training_data_fresh.jsonl` (original, 3,090 lines, 2.0 MB)
- Regenerated output: 63,504 lines, 41.8 MB

### Evidence
```
Original: 3,090 lines, 2,020,851 bytes
Regenerated: 63,504 lines, 41,784,263 bytes
Difference: +60,414 lines (+40 MB)
Ratio: 20.55×
```

### Reproduction conditions
1. Run `python scripts/build_training_data.py --input-dir DATASETS/arxiv_html_corpus --output /tmp/test_training_data.jsonl`
2. Script processes all 240 papers in the corpus
3. Output is 63,504 lines (41.8 MB)
4. Original files are 3,090 lines (2.0 MB)

### Impact
- Training data population is not reproducible as-is
- Cannot determine whether original was a subset, filtered, or differently configured
- Downstream solve scripts consume this data; variance affects all solve results

### Potential explanations (NOT yet tested)
1. Different input corpus population (subset vs. all 240 papers)
2. Different filtering or eligibility rules
3. Duplicate occurrence expansion
4. Changed augmentation or sampling behavior
5. Different command-line parameters
6. A change in record granularity

### Proposed investigation (NOT yet authorized)
Compare record identity between original and regenerated:
- Unique occurrence IDs
- Duplicate IDs
- Paper distribution
- Equation distribution
- Record-type distribution
- Source-to-output lineage
- Missing and additional occurrences

### Verification criteria (for future investigation)
1. Original and regenerated record IDs are extracted and compared
2. Input population difference is identified (if any)
3. Filtering/augmentation difference is identified (if any)
4. The 60,414-record difference is explained
5. Both outputs preserved until adjudication
6. Downstream solve results compared before/after

### Status
OPEN — read-only, no fix authorized

---

## DEFECT 3: Structural-survival baseline staleness

### ID
MPRD-003

### Severity
High — generated output cannot be accepted as replacement

### Affected files
- `scripts/structural_survival.py` (consumer)
- `DATASETS/structural_survival.jsonl` (original, 6.5 MB)
- `DATASETS/structural_survival_report.json` (baseline)

### Evidence
```
ROUND-TRIP GATE:        PASS
STRUCTURAL SURVIVAL:   FAIL
BASELINE ALIGNMENT:    STALE - see reconcile_occurrences.py
```

Script executed and wrote output, but reported:
1. STRUCTURAL SURVIVAL: FAIL
2. BASELINE ALIGNMENT: STALE

### Reproduction conditions
1. Run `python scripts/structural_survival.py` from repo root
2. Script processes the structural survival baseline
3. Reports FAIL and STALE
4. Output file is written but may not be equivalent

### Impact
- `structural_survival.jsonl` (6.5 MB) cannot be regenerated as replacement
- The stale baseline alignment is independent of the None MathML bug (DEFECT 1)
- Fixing DEFECT 1 would not automatically resolve this

### Root cause (preliminary)
The script's baseline alignment check compares against a recorded baseline that
is stale (different revision than expected). The "STALE" message references
`reconcile_occurrences.py` as the resolution path. The exact cause of staleness
has not been investigated.

### Proposed investigation (NOT yet authorized)
1. Identify the expected baseline revision
2. Identify the actual baseline revision used
3. Determine why alignment failed
4. Establish whether the generated output is comparable
5. Do not accept as replacement evidence until verified

### Verification criteria (for future investigation)
1. Expected baseline revision identified
2. Actual baseline revision identified
3. Staleness cause determined
4. Generated output compared to original (schema, count, content)
5. Downstream consumers verified
6. Baseline updated or reconciliation completed

### Status
OPEN — read-only, no fix authorized

---

## DEFECT 4: verify_provenance_trace.py crashes

### ID
MPRD-004

### Severity
Medium — prevents regeneration of 1 content-consuming file

### Affected files
- `scripts/verify_provenance_trace.py` (consumer)
- `DATASETS/arxiv_html_corpus/1505.05770.json` (0.3 MB)

### Evidence
```
TypeError: list indices must be integers or slices, not str
  (in bbox handling code)
```

### Reproduction conditions
1. Run `python scripts/verify_provenance_trace.py` from repo root
2. Script crashes with TypeError on bbox data structure

### Impact
- `arxiv_html_corpus/1505.05770.json` cannot be verified
- Provenance trace for paper 1505.05770 is blocked

### Root cause (preliminary)
Data structure mismatch: code expects bbox to be a dict with keys like 'x0', 'x1',
but the data contains a list instead.

### Status
OPEN — read-only, no fix authorized

---

## DEFECT 5: test_canonical_extraction.py partial crash

### ID
MPRD-005

### Severity
Low — produces output but crashes at end

### Affected files
- `scripts/test_canonical_extraction.py`
- `DATASETS/canonical_from_html.json` (produced before crash)

### Evidence
```
Saved canonical_from_html.json (991 records)
Traceback (most recent call last):
  File "scripts/test_canonical_extraction.py", line 79, in <module>
    PYEOF
NameError: name 'PYEOF' is not defined
```

### Reproduction conditions
1. Run `python scripts/test_canonical_extraction.py` from repo root
2. Script produces `canonical_from_html.json` (991 records) successfully
3. Then crashes with NameError on `PYEOF` (heredoc terminator leaked into file)

### Impact
- Output file is produced but script exit code is non-zero
- The crash is a code artifact (PYEOF leaked into the script), not a data issue

### Root cause
The script file contains a leaked `PYEOF` heredoc terminator, likely from a
previous edit that used a heredoc to write the file. This is a code hygiene issue.

### Status
OPEN — read-only, no fix authorized

---

## DEFECT 6: arxiv_html_corpus regeneration requires network access

### ID
MPRD-006

### Severity
Medium — 237 files cannot be regenerated without network access

### Affected files
- 237 of 240 `arxiv_html_corpus/*.json` files (51.6 MB)
- 3 `arxiv_html_batch/*.json` files (0.4 MB)

### Evidence
- `arxiv_html_parser.py` requires `--batch` with arxiv IDs and network access to arXiv
- `arxiv_provenance.py` requires `--arxiv` argument
- No offline regeneration path exists

### Impact
- These files are source corpus, not reproducible derivatives
- They can only be regenerated by re-downloading from arXiv
- Their lack of script references is because they are consumed by reading, not by `open()` calls

### Status
OPEN — read-only, no fix authorized

---

## Summary of defects

| ID | Severity | Type | Affected files | Evidence dependency | Status |
|----|----------|------|----------------|---------------------|--------|
| MPRD-001 | Blocking | None MathML crash | 2 (math_reconstruction_evidence, cross_stage_drop_trace) | Original MathML availability and occurrence identity | RESOLVED 2026-11-04 |
| MPRD-001-compat | Medium | Cross-version hash compatibility | Frozen manifest, cross_trace | Pre-fix vs post-fix source_hash values | OPEN |
| MPRD-003 | High | Baseline staleness | 1 (structural_survival) | Frozen baseline revision and comparison configuration | OPEN pending closure criteria |
| MPRD-002 | High | Training-data scope change | 1 (extractor_training_data) | Original training-data population and generator configuration | CLOSED 2026-11-04 — EXPLAINED SCOPE CHANGE |
| MPRD-004 | Medium | Bounding-box list-vs-dictionary | 2 (pix2text_harvest, audit_candidate_crops) | Producer-consumer contract for bbox format | OPEN |
| MPRD-005 | Low | Code hygiene (PYEOF leak) | 1 (test_canonical_extraction) | Original script and execution environment | OPEN |
| MPRD-006 | Medium | Network dependency | 240 (arxiv_html_corpus) | Archived source corpus and retrieval metadata | OPEN |

## Recommended investigation sequence

Proposed order (NOT authorization to modify source):

1. **MPRD-001** — Establish representation and hash integrity (None/empty/present MathML contract)
2. **MPRD-003** — Establish baseline authority (frozen baseline revision and comparison configuration)
3. **MPRD-002** — Reconcile training-data populations (record identity comparison)
4. **MPRD-004** — Establish schema consistency (bbox list vs dict)
5. **MPRD-006** — Establish offline source preservation (archived corpus and retrieval metadata)
6. **MPRD-005** — Resolve isolated script hygiene issue (PYEOF leak)

This sequence prioritizes representation integrity and baseline authority before
population reconciliation and schema fixes, and defers the isolated hygiene issue
to last.

## Retention decisions (recommended, NOT authorized)

| Category | Decision | Rationale |
|----------|----------|-----------|
| 5 exact reproductions | RETAIN (both) | Reproducibility established under tested conditions; not necessarily unneeded |
| 1 unexplained variance | RETAIN BOTH | 20× expansion not understood; both outputs preserved |
| 3 failed reproductions | RETAIN + failure evidence | Scripts crash; originals preserved |
| 13 argument-dependent | RETAIN until tested | Not yet validly attempted |
| 19 unverified | RETAIN until verified | Equivalence not established |
| 237 source corpus | RETAIN as source inputs | Original inputs, not disposable |
| 14 version directories | RETAIN; canonical unresolved | Distinct experimental states |
| Frozen evidence | UNTOUCHED | Never modify |

## Governance constraints honored

- No frozen evidence modified
- No source files modified
- No commits or pushes
- No deletions (local copies preserved)
- All hashes recorded in manifest
- Additive documentation only
- Retention review frozen as completed assessment
- Defect register is separate, versioned artifact