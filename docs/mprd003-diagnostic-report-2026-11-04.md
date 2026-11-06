# MPRD-003 Diagnostic Investigation Report
## Structural-Survival Baseline Staleness — Evidence Assessment

**Date:** 2026-11-04
**Investigation mode:** Read-only diagnostic comparison
**Baseline frozen?** Yes — `DATASETS/baseline_2026-10-09/` untouched
**Implementation changes since baseline?** Yes — MPRD-001 hash contract fix (Oct 2026)

---

## 1. Baseline Contract

| Artifact | Value |
|----------|-------|
| Contract version file | `DATASETS/baseline_2026-10-09/contract_version.txt` → `2026.10.09-v1` |
| Frozen baseline directory | `DATASETS/baseline_2026-10-09/` |
| Baseline manifest | `DATASETS/baseline_2026-10-09/manifest.json` |
| Baseline ledger | `DATASETS/baseline_2026-10-09/occurrences.jsonl` (3,409 records) |
| Baseline pinned paper versions | `DATASETS/baseline_2026-10-09/pinned_versions.txt` (14 papers) |
| Baseline run metadata | `DATASETS/baseline_2026-10-09/run_metadata.json` (timestamp: 2026-10-10T01:18:03Z) |
| Baseline parser commit | `2a99380e83d168cecbf700d96eaf045f7dbd5a15` |

**Baseline identity:** 14 arXiv papers (2009.00031, 2102.03334, 2605.00155, 2605.00224, 2605.06070, 2605.18130, 2605.22715, 2605.23244, 2605.24807, 2605.24856, 2605.25036, 2605.25334, 2605.28615, 2605.28896), 3,409 occurrence records.

---

## 2. Current Structural-Survival Provenience

| Item | Value |
|------|-------|
| Generator script | `scripts/structural_survival.py` |
| Input corpus | `DATASETS/arxiv_html_corpus/` (241 JSON files) |
| Current total records | 72,478 |
| Pins used | `pinned_versions.txt` → `source.locator=f"math[{i}]"` |

**Current run identity:** 240 arXiv papers, 72,478 occurrence records.

---

## 3. Baseline Alignment Analysis

| Metric | Baseline | Current | Delta |
|--------|----------|---------|-------|
| Total occurrences | 3,409 | 72,478 | +69,069 |
| Papers | 14 | 240 | +226 |
| Common papers | — | 14 | same |
| Removed papers | — | 0 | none |
| Duplicate keys | 0 | 0 | 0 |
| Extract failed | — | 64 | new |
| Round-trip failures | — | 64 | new |

**Cause classification:** `source_only: 69,069` is overwhelmingly explained by corpus population growth (14 → 240 papers), not by any generator defect. Every baseline paper still has records in the current run (`baseline_only: 0`). The corpus directory was expanded by an external ingestion pipeline after the baseline was frozen.

**Secondary cause:** MPRD-001 `source_hash` contract change (None → sentinel) affects hash values in current records, but this is captured separately under MPRD-001-compat.

---

## 4. Structural-Survival Gate Result

| Gate | Result | Details |
|------|--------|---------|
| `structural_survival_gate` | **FAIL** | `roundtrip_failed: 64` (new in current run) |
| `baseline_alignment` | **STALE** | `source_eq_baseline: false` due to corpus expansion |
| `roundtrip_gate` | **PASS** | `roundtrip_failed: 64` are extract failures, not serialization failures |
| `extractor_status` | **partial** | 420 records with unsupported tokens |

---

## 4. Additional Findings (post-diagnostic)

### 4A. 241-vs-240 Paper Discrepancy

The input corpus contains 241 papers. The current structural-survival output contains 240 papers.

- **Missing paper:** `1806.03536`
- **Reason:** Paper `1806.03536` has zero equations in its corpus JSON (`"equations": []`). The structural_survival script iterates `data.get("equations", [])`, producing no records for this paper.
- **Disposition:** Expected behavior, not a defect. No equations → no structural records. Documented for population boundary clarity.

### 4B. 64 Round-Trip Failures — Classified as MPRD-001-adjacent

All 64 failures originate from a single paper (`2401.03048`) and all have `unsupported: ["no_mathml"]`. The structural AST extractor fails when MathML is unavailable (the same `None` condition addressed by MPRD-001). This is a **corpus-data limitation**, not a round-trip serialization defect or generator regression.

- `roundtrip_gate` still reports PASS (roundtrip_ok=72414, roundtrip_failed=64 are extract failures, not serialization failures)
- These 64 records are correctly excluded from structural fidelity analysis
- **Disposition:** Separate from MPRD-003 baseline staleness. Should be tracked as a corpus-quality observation, not a generator defect.
- **Recommendation:** When the 2401.03048 paper is re-ingested with MathML, these 64 records will be reprocessed automatically.

---

## 5. Updated MPRD-003 Disposition

| Sub-item | Status | Disposition |
|----------|--------|-------------|
| Baseline staleness | **EXPLAINED** | Corpus expansion (14 → 240 papers), expected growth |
| 241-vs-240 discrepancy | **EXPLAINED** | Paper 1806.03536 has zero equations; expected exclusion |
| 64 round-trip failures | **CLASSIFIED** | All `no_mathml` from paper 2401.03048; corpus-data limitation, not generator defect |
| Baseline refresh | **PENDING** | Requires explicit authorization; new version only, never overwrite frozen baseline |
| Generator regression | **NOT ESTABLISHED** | No evidence of generator defect |

**MPRD-003 status: OPEN** — baseline staleness explained, but the 64 round-trip failures are classified as a separate corpus-quality observation, not a generator regression. The baseline refresh decision remains pending.

| Deliverable | Status |
|-------------|--------|
| Baseline identity | ✅ Identified (contract_version.txt + pinned_versions.txt) |
| Expected identity | ✅ Identified (baseline ledger + manifest) |
| Generator provenance | ✅ Identified (script revision, 240-paper corpus) |
| Mismatch report | ✅ Filed (corpus expansion: 14 → 240 papers) |
| MPRD-001 interaction | ✅ Documented (cross-version hash compatibility issue under MPRD-001-compat) |
| Disposition | ✅ **Baseline is NOT obsolete — it is a frozen subset of the current corpus.** This is expected corpus growth, not generator regression. |

---

## 6. Disposition

**Baseline status: STALE, by design.**

The frozen baseline (`2026.10.09-v1`) represents a 14-paper snapshot of the corpus taken 2026-10-09. The current run processes 240 papers — a 17.1× expansion of the corpus. This is expected corpus growth, not a generator defect.

**Recommended dispositions:**

1. **When corpus growth is expected:** Update pinned_versions.txt to include all corpus papers; create a new baseline snapshot for the expanded corpus. Do NOT overwrite the frozen baseline.
2. **When a specific paper version is frozen for reproducibility:** Pin the exact paper versions in pinned_versions.txt; the structural_survival gate will pass for the pinned subset.

**Do NOT** regenerate or replace `DATASETS/baseline_2026-10-09/` — it is a preserved historical snapshot.

---

## 7. MPRD-001 Interaction

The MPRD-001 hash contract change affects `source_hash` values for records where MathML is `None` (now sentinel `MATHML_UNAVAILABLE` instead of empty-string hash). This is a **cross-version compatibility issue**, tracked separately under **MPRD-001-compat**. It does not invalidate the structural-survival gate result — the gate is about round-trip invariance and structural integrity, not hash stability across contract versions.

---

## 8. Next Steps (auto-requested)

1. **MPRD-001-compat:** Assess persisted hash compatibility for cross-version joins.
2. **MPRD-002:** Investigate the 20.55× training-data expansion (63,504 regenerated lines vs 3,090 original).
3. **MPRD-004:** Resolve the bounding-box list-versus-dictionary schema mismatch.
4. **MPRD-006:** Establish offline reproducibility for the 240 corpus files.
5. **MPRD-005:** Trace the leaked `PYEOF` terminator in the test script.
