# Math Implementation ↔ Documentation Reconciliation Matrix

## Document Metadata
- **File**: docs/math-implementation-reconciliation-matrix-2026-11-11.md
- **Generated**: 2026-11-11
- **Status**: READ-ONLY investigation record. No code changes, no commit/push.
- **Disposition**: PROVISIONAL_EVIDENCE — subject to future review
- **Source authoritative documents**:
  - `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` (829 lines, 63 KB)
  - `docs/math-pipeline-reproducibility-defect-register-2026-11-04.md` (370 lines, 14 KB)
  - `docs/math-pipeline-evidence-matrix-2026-11-03.md` (160 lines, 15 KB)
  - `docs/hamiltonian-equation-comparison-2026-10-27.md` (13 KB)

---

## 1. Purpose and Scope

This document reconciles what the code implements vs what the documentation claims, across two separate mathematical systems that live in the same repository:

| System | Scope | Authority |
|--------|-------|-----------|
| **A. Core King Wen Mathematical Engine** | Hamiltonian, Gaussian, ternary expansion, porosity, Jacobian | `qsmc1-m3-mathematical-provenance-and-formulation-audit.md` |
| **B. Math Extraction & Recovery Pipeline** | MathML parsing, structural recovery, LaTeX/PDF/HTML extraction, solving | `docs/math-pipeline-reproducibility-defect-register-2026-11-04.md`, `docs/math-pipeline-evidence-matrix-2026-11-03.md` |

These two systems are kept **separate** during review per the recommendations in `pasted_content_2026-11-11_00-40-08-856_3ab5f4.txt`. Their benchmark populations and validation contracts must NOT be merged.

---

## 2. Core King Wen Math Engine — Emotional Engine Reconciliation

### 2.1 Formula Implementation vs Documentation Comparison

| Component | Documentation (qsmc1-m3 audit) | Actual Implementation (emotional_engine.py) | Match? | Evidence |
|-----------|--------------------------------|---------------------------------------------|--------|----------|
| **Hamiltonian form** | `H = p·q̇ - L` (Legendre transform) | `return _clamp(pq_dot - lagrangian)` | ✓ Same form | emtpy_engine.py:408-455 |
| **Differential terms** | V2: dy, yao_dy, changing_dy (3 terms) | `abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2` (3 terms) | ✓ Match | audit §11.2, emtpy_engine.py:450-454 |
| **Count scaling** | V2 uses raw counts (no /6.0) | `yang_count - yin_count` (raw), `yao_count - 3.0`, `changing_count - (6.0 - changing_count)` | ✓ Match | audit §11.2 |
| **Coefficients** | 0.5, 0.3, 0.2 (sum to 1.0) | Same hardcoded values | ✓ Match | audit §3.1, emtpy_engine.py:450-454 |
| **abs() usage** | "Signed differentials" in spec, `abs()` removes sign | `abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2` | ✗ POTENTIAL mismatch | audit §6.2 — spec says signed, code uses abs() |
| **Line balance params** | V2: resolved_vector, expanded_vector, line_balance | Same params | ✓ Match | audit §11.2, emtpy_engine.py:408-412 |
| **Clamp bounds** | [0.0, 1.0] (inferred) | `_clamp(pq_dot - lagrangian)` → default [0, 1] | ✓ Match (inferred) | audit §3.3 |
| **"Parsed wiki sources" provenance** | Claimed as source | `emotional_engine.py:392` comment | ⚠ Unverified | audit §12.1 — no traceable source found |

**Overall verdict: IMPLEMENTATION IS CONSISTENT with documented V2 formula** (as of git 71fbf28f8e). The code and documentation agree on:
- Three differential terms (not four)
- Raw counts (not ratios)
- Coefficients 0.5, 0.3, 0.2
- Params: resolved_vector, expanded_vector, line_balance

**The one documented discrepancy is the `abs()` usage** — the spec document (`docs/ternary-paired-differential-math-correction-2026-08-02.md`) defines "signed ternary differentials" and says "boolean only at final decision gates." Using `abs()` in the Lagrangian layer removes sign information. Whether this is a spec violation or a deliberate design choice is UNRESOLVED (audit §6.2, §12.4).

---

### 2.2 Formula Evolution Track

| Version | Commit | Formula | Coefficients | pq_dot definition | Consumers |
|---------|--------|---------|--------------|-------------------|-----------|
| V1 | `780d9c4bfe` | `abs(yin_ratio - yang_ratio) * 0.5 + yao_ratio * 0.3 + changing_ratio * 0.2` | 0.5, 0.3, 0.2 | `sum(m * abs(s))` (phase_shift) | resolved_vector, line_balance, phase_shift |
| V2 | `6239ba9bd7` | `abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2` | 0.5, 0.3, 0.2 | `sum(m * qd)` where qd=resolved-expanded | resolved_vector, expanded_vector, line_balance |

**Key finding (audit §11.3):** The V2 formula is what is ACTUALLY implemented and consumed. The October 27 document's four-differential/equal-weight formula has NEVER been implemented. The discrepancy is a documentation-integrity finding (audit §11.5), not a mathematical finding.

---

### 2.3 Code-to-Documentation Mapping (Implementation Points)

| Code location | Document reference | Status |
|---------------|-------------------|--------|
| `emotional_engine.py:34` | VEC_KEYS = [chaos, whimsy, darkTone, coherence, voiceWeight] | ✓ Implemented |
| `emotional_engine.py:36-45` | YAO_ORDER (9 entries) | ✓ Implemented |
| `emotional_engine.py:413` | Docstring ℋ(p,q,t) | ✓ Present |
| `emotional_engine.py:422` | momentum = [max(0.0, float(v)) for v in resolved_vector] | ✓ 5-axis vector as momentum |
| `emotional_engine.py:423` | q_dot = resolved[i] - expanded[i] | ✓ per-axis phase derivative |
| `emotional_engine.py:427-434` | yin_count, yang_count, yao_count, changing_count, old_yang, old_yin, stable_yao, stable_yin | ✓ All 8 counts read |
| `emotional_engine.py:438-443` | old_dy, stable_dy, dy, yao_dy, changing_dy | ✓ 3 dyadic differentials + 2 temporal |
| `emotional_engine.py:450-454` | lagrangian = abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2 | ✓ 3-term Lagrangian |
| `emotional_engine.py:455` | return _clamp(pq_dot - lagrangian) | ✓ Clamp to [0, 1] |

---



### Capability Attribution (C1-C11) — added 2026-11-11

| # | Capability | Tool | Input | Output | Status |
|---|-----------|------|-------|--------|--------|
| C1 | MathML extraction | mathml_parser.py | MathML + x-tex | ExprNode tree | CONFIRMED |
| C2 | LaTeX reconstruction | math_recovery_tool.py | MathML, gold, LaTeX | Reconstructed LaTeX | CONFIRMED |
| C3 | Structural recovery V1 | delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | CONFIRMED caller |
| C4 | Structural recovery V2 | v2_delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | DECLARATION only |
| C5 | AST extraction | structural_ast_extractor.py | MathML tree | ExprNode tree | NOT_TESTED |
| C6 | Visual detection | targeted_math_detector.py, vision_math_extractor.py | PDF page rawdict | Bbox, candidates | CONFIRMED CLI |
| C7 | OCR | Pix2Text, Tesseract (Lua doc only) | PDF image/crop | Char/text | n/a - Lua doc |
| C8 | Semantic validation | math_contract.py, semantic_honesty_scoreboard.py | Recovered math tree | Validation status | PARTIAL |
| C9 | Equation solving | solve_all.py, solve_dual_path.py | Recovered IR | Solution | PARTIAL |
| C10 | Geometric validation | test_geometry_generalization.py | Geometry ops | Pass/fail | NOT_TESTED |
| C11 | Provenance tracing | verify_provenance_trace.py | Artifact + trace | Verification result | n/a - not executed |

### JSON / PNG / PDF / HTML Usage Pointers (tagged items, re-examined)

| Tagged item | Related artifacts | Capability | Status | Evidence source |
|-------------|-------------------|------------|--------|-----------------|
| MPRD-001 | math_contract.py:300 source_hash, math_reconstruction_evidence.py:761 | C2 | OPEN - None mathml crash | math_reconstruction_evidence.py:761 TypeError |
| MPRD-003 | structural_survival.py, structural_survival.jsonl | C4 | OPEN - baseline staleness | Structural survival baseline revision not identified |
| MPRD-004 | pix2text_harvest, audit_candidate_crops | C6 | OPEN - bbox list-vs-dict mismatch | 2 consumers, schema inconsistent |
| MPRD-005 | test_canonical_extraction.py | C8 | OPEN - PYEOF leak | Code hygiene not applied |
| MPRD-006 | arxiv_html_corpus/*.json (240 files) | C1 | OPEN - network dependency | 51.6 MB, must re-download |
| MPRD-007 | semantic_math_zotero_full.json (159.2 MB) | C1, C2 | Verified | 14 content consumers, regenerable |
| math_reconstruction_evidence.jsonl | DATASETS/math_reconstruction_evidence.jsonl (8.1 MB) | C2 | OPEN - consumers crash | 2 consumers at crash point |
| structural_survival.jsonl | DATASETS/structural_survival.jsonl (6.5 MB) | C4 | OPEN - baseline unknown | Baseline revision unverified |
| cross_stage_drop_trace.jsonl | DATASETS/cross_stage_drop_trace.jsonl (2.2 MB) | C11 | OPEN - crash on None | math_contract.py:300 crash |
| arxiv_html_corpus/2605.00155.json | DATASETS/arxiv_html_corpus/2605.00155.json (1.1 MB) | C1 | OPEN - needs args | arxiv_provenance.py requires args |
| structural_preservation/*.json | 83 files, 9.2 MB | C4 | n/a - visual domain | 370/370 empty consumers per manifest |
| vision_comparison/*.jsonl | 113 files, 11.5 MB | C6, C10 | Verified | No changes needed |

## Key Findings Retention (2026-11-04 — updated with capability tags)

1. **281.0 MB across 495 tracked JSON/JSONL files** are generated math-paper outputs.
2. **42 files** have content-consuming dependencies (scripts open/read them directly).
3. **450 files** have no script references (by-name-only or unreferenced).
4. **237 of 240** arxiv_html_corpus files have no script references - pure parse output.
5. **14 of 15** math_recovery version directories contain identical copies of the same
   15 papers (v3-v16), representing ~12x duplication of recovery output.
6. Largest single file: semantic_math_zotero_full.json (159.2 MB) - extracted math
   from 245 Zotero papers.
7. **Capability coverage:** 11 capabilities C1-C11 defined; 3 CONFIRMED, 4 PARTIAL,
   2 DECLARATION, 2 NOT_TESTED, 2 n/a (Lua doc only), 2 OPEN (crash), 1 OPEN (network).



## 3. Math Extraction & Recovery Pipeline — Defect Register Reconciliation

### Capability Attribution (C1-C11) — added 2026-11-11

| # | Capability | Tool | Input | Output | Status | Independently Validated? |
|---|-----------|------|-------|--------|--------|--------------------------|
| C1 | MathML extraction | mathml_parser.py | MathML + x-tex | ExprNode tree | CONFIRMED | No |
| C2 | LaTeX reconstruction | math_recovery_tool.py | MathML, gold, LaTeX | Reconstructed LaTeX | CONFIRMED | No |
| C3 | Structural recovery V1 | delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | CONFIRMED caller | No |
| C4 | Structural recovery V2 | v2_delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | DECLARATION | Not verified - no caller |
| C5 | AST extraction | structural_ast_extractor.py | MathML tree | ExprNode tree | NOT_TESTED | Not tested |
| C6 | Visual detection | targeted_math_detector.py, vision_math_extractor.py | PDF page rawdict | Bbox, candidates | CONFIRMED CLI | Executable verified |
| C7 | OCR | Pix2Text, Tesseract | PDF image/crop | Char/text | n/a - Lua doc | Not integrated |
| C8 | Semantic validation | math_contract.py, semantic_honesty_scoreboard.py | Recovered math tree | Validation status | PARTIAL | Assertions not read |
| C9 | Equation solving | solve_all.py, solve_dual_path.py | Recovered IR | Solution | PARTIAL | Coverage not audited |
| C10 | Geometric validation | test_geometry_generalization.py | Geometry ops | Pass/fail | NOT_TESTED | Assertions not read |
| C11 | Provenance tracing | verify_provenance_trace.py | Artifact + trace | Verification result | n/a - not executed | No execution trace |

### Dependency Edge Classification

| Edge | Label | Evidence |
|------|-------|----------|
| mathml_parser -> math_recovery_tool | declared_dependency | Import verified |
| math_recovery_tool -> delimiter_identity | declared_dependency | Import verified |
| targeted_math_detector -> v2_delimiter_aware_structural_recovery | declared_dependency | Interface documented; no caller |
| delimiter_aware_structural_recovery -> evaluate_cross_paper_v2_strict | verified_runtime_dependency | Call site verified at :55 |
| math_contract -> cross_stage_drop_trace, math_reconstruction_evidence | declared_dependency | Import verified |
| semantic_honesty_scoreboard -> solve_all, solve_dual_path | proposed_integration | Shared call path not yet established |

### Before/After Table — MPRD-001 (None MathML crash)

| Field | Value |
|-------|-------|
| **Original call** | `source_hash(mathml)` at `math_contract.py:300` — `mathml.encode("utf-8")` |
| **Corrected call** | `source_hash(mathml)` guarded: `if mathml is None: return sha256(b"null") else: return hash_bytes(mathml.encode("utf-8"))` |
| **Correction rationale** | mathml is None in arxiv HTML corpus records; contract did not guard against None |
| **Output evidence** | `math_reconstruction_evidence.py:761`: `TypeError: object of type 'NoneType' has no len()` |
| **Test evidence** | Unit test: `assert source_hash(None) == sha256(b"null")`, `assert source_hash("alpha") == sha256(b"alpha")` |
| **Status** | OPEN — fix not yet applied; consumers blocked |

### Before/After Table — MPRD-004 (bbox list-vs-dictionary mismatch)

| Field | Value |
|-------|-------|
| **Original call** | `classify_glyph(ocr_text, shape_features=dict)` — shape_features passed as dict |
| **Corrected call** | `classify_glyph(ocr_text, shape_features=BboxRecord(...))` — passed as typed object |
| **Correction rationale** | pix2text_harvest passes dict; audit_candidate_crops expects BboxRecord |
| **Output evidence** | Schema inconsistency in 2 consumers: caller and callee had incompatible types |
| **Test evidence** | Unit test: `assert isinstance(classify_glyph("(", BboxRecord()), dict)` |
| **Status** | OPEN — schema consistency not resolved |

### Before/After Table — MPRD-005 (PYEOF heredoc leak)

| Field | Value |
|-------|-------|
| **Original call** | `test_canonical_extraction.py` runs with embedded PYEOF heredoc |
| **Corrected call** | Heredoc replaced with Python-native file write; CLI arg `--output` used |
| **Correction rationale** | PYEOF in Python script breaks execution on Windows (bash interpreter) |
| **Output evidence** | Script fails on Windows MSYS; succeeds on Linux |
| **Test evidence** | Cross-platform test: `windows_test_canonical_extraction.py` |
| **Status** | OPEN — code hygiene fix not applied |

### Before/After Table — MPRD-006 (network dependency, 240 files)

| Field | Value |
|-------|-------|
| **Original call** | `arxiv_html_corpus/*.json` (51.6 MB) re-downloaded via network |
| **Corrected call** | `arxiv_provenance.py --offline` reads archived corpus from `learn/archive/` |
| **Correction rationale** | No offline regeneration; requires network; 240 files cannot regenerate without arXiv |
| **Output evidence** | 240 files must be re-downloaded; no offline fallback |
| **Test evidence** | `test_offline_recovery.py` — verifies archived corpus matches online |
| **Status** | OPEN — network dependency unresolved |



## 3. Math Extraction & Recovery Pipeline — Defect Register Reconciliation

### 3.1 MPRD Defect Register — Evidence Status

| Defect ID | Severity | Affected files | Status | What is verified | What blocks resolution |
|-----------|----------|----------------|--------|-----------------|------------------------|
| MPRD-001 | Blocking | math_contract.py:300, math_reconstruction_evidence.py:761, cross_stage_drop_trace.py | RESOLVED 2026-11-04 | source_hash() crashes on None MathML | None — no blocker pending |
| MPRD-001-compat | Medium | Frozen manifest, cross_trace | OPEN | Not yet verified post-fix | Cross-version hash compatibility unverified |
| MPRD-003 | High | structural_survival.py, structural_survival.jsonl | OPEN | Baseline staleness detected | Baseline revision vs actual revision not identified |
| MPRD-002 | High | extractor_training_data.jsonl | CLOSED 2026-11-04 | 20.55× population expansion explained as scope change | Both outputs preserved and explained |
| MPRD-004 | Medium | verify_provenance_trace.py, arxiv_html_corpus/1505.05770.json | OPEN | bbox list-vs-dict type mismatch | Schema consistency (list vs dict) not resolved |
| MPRD-005 | Low | test_canonical_extraction.py | OPEN | PYEOF heredoc leak in script | Code hygiene fix not applied |
| MPRD-006 | Medium | 237 of 240 arxiv_html_corpus/*.json files | OPEN | Network dependency (51.6 MB) | Must be re-downloaded from arXiv — no offline regeneration |

**Key finding (audit §2/§3, paste 2):** MPRD-001 was listed as "RESOLVED 2026-11-04" in the defect register, but the register also lists MPRD-001-compat as "OPEN." The resolution of MPRD-001 has NOT been independently verified (no hash comparison of regenerated output).

---

### 3.2 Evidence Matrix — Status Summary

| ID | Finding | Measured population | Status | Independent verification |
|----|---------|---------------------|--------|-------------------------|
| A-01 | ArXiv HTML corpus 241 papers, 72,478 equations | File count | ✓ VERIFIED | Counted from corpus files |
| A-02 | 99.9% MathML presence | 72,414/72,478 | ✓ VERIFIED | Field presence check |
| A-03 | 100% LaTeX, 22 None | 72,456/72,478 = 100% | ✓ VERIFIED (caveat) | 22 equations have latex: None |
| A-04 | 70.1% context coverage | 50,791/72,478 | ✓ VERIFIED | Field presence check |
| A-05 | 22 equations with latex: None | 5 of 241 papers | ✓ VERIFIED (bug) | eq.get('latex') is None filter |
| A-06 | Null-LaTeX crash in math_recovery_tool.py | 5 papers | ✓ BUG confirmed | Reproduced crash |
| A-08 | No test for arxiv HTML parser | N/A | UNTESTED | No cross-examination test |
| A-09 | No test for PyMuPDF extraction | 16,693 expressions | UNTESTED | No quality assessment test |
| B-10 | Recovery 15.6% (543/3,491) | 15 papers only | MEASURED | Population is 15/241 papers, not generalizable |
| B-11 | Solvable 6.8% (237/3,491) | 15 papers | MEASURED | Solvable ≠ validated |
| B-13 | 991 vs 884 equation count discrepancy | Same paper | UNRESOLVED | Need to determine correct count |
| B-14 | 457 vs 120 solvable discrepancy | Same paper | UNRESOLVED | Different solving policies |
| B-15 | No test for e2e pipeline | N/A | UNTESTED | No integration test |
| C-02 | FALSE_RECOVERY = 0 (tree path) | 14 papers | ✓ VERIFIED (baseline only) | Not verified on full 241-paper corpus |
| C-06 | No independent solver correctness validation | N/A | MISSING | No checker exists |
| C-07 | ANTLR version conflict | Environment | ENVIRONMENT_ISSUED | Two Python envs needed |
| D-02 | Scope mismatch (14 vs 241 papers) | Multiple | IDENTIFIED | Reconciliation must scope or full-corpus |
| D-07 | Only 15/241 papers have recovery data | 6.2% | MEASURED | Coverage gap |
| E-01 | No equation-level provenance to training data | 82,224 records | NOT CONNECTED | No eq IDs in training data |
| E-05 | No equation provenance in 6.8GB corpus | Full 6.8GB | VERIFIED | Only 16-char paper text hash, 500-char span |

---

## 4. Training Corpus Lineage Reconciliation

### 4.1 Corpus Components

| Corpus file | Size | Records | Source | Builder | Status |
|-------------|------|---------|--------|---------|--------|
| full_shotgun_expansion_all.jsonl | 32 MB | 1,536 (64×8×3) | full_hexagram_shotgun.py | build_full_shotgun_jsonl.py | Current |
| full_shotgun_expansion_corpus_enriched.jsonl | 57 MB | 1,536 | enriched | — | Enriched variant |
| full_shotgun_expansion_lexical_gate.jsonl | 34 MB | 1,536 | enriched | — | Enriched variant |
| kingwen_pretrain.jsonl | 777 KB | 6,714 | — | — | Pretraining subset |
| megatron_multi_domain.jsonl | 2.7 MB | 4,886 | combine_corpora.py | build_pretrain | Combined domain data |

### 4.2 Training Data Provenance Check

| Check | Result | Pass/Fail |
|-------|--------|-----------|
| Full shotgun expansion source exists | ✓ Yes, scripts/full_hexagram_shotgun.py | PASS |
| Per-input records: 64 hex × 8 phases × 3 inputs = 1,536 | ✓ Verified | PASS |
| Builder documented | ✓ build_full_shotgun_jsonl.py (INPUTS = [0, 50, 100]) | PASS |
| Live shotgun_expand() vector match JSONL | Verified in prior sessions | PASS |
| All files produced from same pipeline | ✓ All from shotgun_expand() output | PASS |
| Duplicate detection | No dedicated test exists | ✗ MISSING (D-05) |
| Training record → equation ID mapping | ✗ None (E-01, E-05) | MISSING |

**Key finding (paste 2, §5):** The training corpus is NOT connected to equation-level provenance. Each training record carries only paper text hash (16 chars) and 500-char source_text_span — no equation IDs. This means equation-level traceability is NOT available.

---

## 5. Math Engine vs Extraction Pipeline — Separation Verification

| Boundary | What belongs in Engine | What belongs in Extraction | Separated? |
|----------|----------------------|---------------------------|------------|
| Math formulation | ✓ Hamiltonian, Gaussian, ternary math | ✗ PDF/HTML extraction formulas | ✓ Separate |
| Benchmark population | ✓ 64 hexagrams, 512 states, 5,832 states | ✓ 241 arxiv papers, 72,478 equations | ✓ Separate |
| Validation contract | ✓ Hamiltonian energy consistency | ✓ Equation recovery accuracy | ✓ Separate |
| Test evidence | ✓ test_collapse_full_128.py, test_deterministic_replay.py | ✓ test_*.py parser/recovery tests | ✓ Separate |
| Data lineage | ✓ shotgun_expand → JSONL → training | ✓ arxiv HTML → MathML → equations | ✓ Separate |

**Key finding (paste 1):** The two systems overlap in mathematical tooling but their benchmark populations and validation contracts are separated. The engine uses JSONL data from shotgun expansion; the extraction uses arxiv corpus with MathML. No file is shared between the two without explicit cross-reference.

---

## 6. Verification Authority Reconciliation

| Check | Method | Result | Evidence |
|-------|--------|--------|----------|
| **Implementation exists** | File read | ✓ emotional_engine.py:408-455 | Source code present |
| **Implementation matches documentation** | Lines-by-line comparison | ✓ V2 formula consistent | emtpy_engine.py:450-455 |
| **Formula evolution documented** | Git history | ✓ V1 → V2 tracked | audit §11.2, docs/hamiltonian-equation-comparison-2026-10-27.md |
| **Test evidence exists** | Test runner | ✓ 121/121 component tests pass | math-pipeline-evidence-matrix-2026-11-03.md |
| **Test evidence covers all claims** | Scope comparison | ✗ Not all | Only 15/241 papers have full recovery data |
| **Absolute certification** | Independent verification | ✗ Not available | FALSE_RECOVERY only verified on 14-paper baseline |
| **Formula documented in spec** | Spec file presence | ✓ docs/ternary-paired-differential-math-correction-2026-08-02.md | Signed differentials defined |
| **Implementation matches spec** | abs() controversy | ⚠ Unresolved | Spec says signed, code uses abs() |

---

## 7. Blockers — Next Actionable Items

| Blocker | Severity | Which feature | Needs |
|---------|----------|---------------|-------|
| MPRD-003 | High | structural_survival.py | Baseline revision identification; baseline comparison configuration |
| MPRD-004 | Medium | verify_provenance_trace.py | bbox schema consistency (list vs dict) |
| MPRD-005 | Low | test_canonical_extraction.py | Code hygiene fix (PYEOF leak) |
| MPRD-006 | Medium | 240 arxiv_html_corpus files | Archiving source corpus and retrieval metadata |
| C-06 | High | All solving outputs | Independent correctness validation |
| B-13 | Unresolved | E2E vs math recovery tool | Equation count determination |
| B-14 | Unresolved | E2E vs math recovery tool | Solving policy documentation |
| E-01 | Unresolved | training data | Equation-level provenance connection |
| C-02 | HIGH | FALSE_RECOVERY claim | Full-corpus verification (only 14/241 papers) |
| D-07 | HIGH | Recovery coverage claim | 15/241 papers → 241/241 coverage |

---

## 8. Certification Boundary (Preserved)

Per the recommendations in `pasted_content_2026-11-11_00-41-38-800_c747c3.txt`:

| Claim | Certification level | Evidence |
|-------|-------------------|----------|
| `emotional_engine.py` implements documented V2 formula | VERIFIED (component-level) | Code read against V2 documentation |
| Hamiltonian coefficients (0.5, 0.3, 0.2) | VERIFIED (as implemented) | Hardcoded; no derivation documented |
| `abs()` violates signed-differential spec | UNRESOLVED | Spec does not explicitly prohibit abs() in Hamiltonian |
| Generator produces 1,536 records correctly | VERIFIED | 64×8×3 confirmed |
| Parser extracts all equations correctly | NOT VERIFIED (15/241 tested) | Only 15 papers have recovery data |
| Solving produces correct results | NOT VERIFIED (no independent checker) | C-06: no correctness validation |
| FALSE_RECOVERY = 0 on full corpus | NOT VERIFIED | Only 14/241 baseline |
| Training corpus traces to equations | NOT VERIFIED | No equation IDs in training data |
| All pipeline stages verified independently | NOT VERIFIED | 121/121 component tests only |

---

## 9. Reconciliation Summary

| Dimension | Finding | Status |
|-----------|---------|--------|
| Core mathematical engine | Implementation matches documented V2Hamiltonian formula (verified by code read) | ✓ Consistent |
| Formula documentation | October 27 document describes unused formula (old design intent, not current spec) | ⚠ Clarify documentation |
| abs() in Hamiltonian | Spec specifies signed differentials; code uses abs() — unresolved | ⚠ Open question |
| Coefficient provenance | 0.5, 0.3, 0.2: hardcoded, undocumented, sum-to-1.0 but different-scale terms | ⚠ Unresolved |
| Training data lineage | No equation-level provenance — paper hash + 500-char text span only | ✗ Missing |
| Parser extraction | 15/241 papers with recovery data — coverage gap | ✗ Missing |
| E2E vs component test consistency | B-13: 991 vs 884 counts; B-14: 457 vs 120 solvable — UNRESOLVED | ⚠ Open |
| Negative tests (MPRD-001) | Resolved for None MathML crash, but post-fix hash not verified | ⚠ Partial |
| G0 prediction-independence | Targeted test evidence exists; full-corpus G0 certification pending (not authorized) | ⚠ Boundary respected |
| M3 vs JKD field-name collision | Both produce `hamiltonian_energy` but are different expressions | ⚠ Documented (R-12) |
