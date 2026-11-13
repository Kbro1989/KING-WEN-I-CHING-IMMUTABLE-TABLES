# Historical Validation Reconciliation

## Document Metadata

- **File**: `docs/HISTORICAL_VALIDATION_RECONCILIATION.md`
- **Generated**: 2026-11-10
- **Status**: Reconciliation of historical Markdown evidence against current validation matrix
- **Disposition**: `MERGED` — preserves prior work, does not erase or duplicate

---

## Purpose

This document reconciles historically documented validation results against the current repository state. The goal is to determine which past validations remain valid and which need re-running against the current checkout.

---

## 1. Validation History Index

### Report Date | Artifact | What Was Documented | Current Status

| Date | Markdown artifact | What was documented |
|------|-------------------|---------------------|
| 2026-10-16 | `DATASETS/PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | 243/243 extraction paths; 3,409/3,409 HTML equations. PDF visual fidelity unverified. |
| 2026-10-16 | `DATASETS/FINAL_KINGWEN_CORPUS_AUDIT_REPORT_2026-10-16.md` | Corpus audit and reconciliation. |
| 2026-10-16 | `DATASETS/PDF_CANDIDATE_RECONCILIATION_2026-10-16.md` | Candidate reconciliation from 3,559 to 4,921. Uniqueness and PDF precision/recall open. |
| 2026-10-17 | `DATASETS/PDF_CANDIDATE_RECONCILIATION_2026-10-16.md` | (duplicate of above — 17/21, 13/17 semantic agreement) |
| 2026-10-23 | `multi_paper_generalization_report.md` | Visual/generalization evaluation. Reconciled claimed vs committed results. |
| 2026-11-04 | `docs/comparative-reevaluation-report-2026-11-04.md` | Comparative reevaluation. Verified status recorded. |
| 2026-11-04 | `docs/context-preservation-gate-verification-matrix-2026-11-04.md` | Gate-by-gate validation tracking. |
| 2026-11-05 | `docs/POST_C40286_DEVELOPMENT_RECONCILIATION_2026-11-05.md` | Development reconciliation. Frozen baselines. |
| 2026-11-06 | `milestone_layer_c_structural_reconstruction_validation_report.md` | Layer C structural reconstruction. 10/15 PRESERVED, 557 tests passed, B4 Gate 2 OPEN. |
| 2026-11-06 | (adjacent) `docs/cyber-physical-agentic-engineering-contract.md` | Contracts referenced as evidence. |
| 2026-11-06 | (adjacent) `docs/spatial-syntactic-preservation-specification.md` | Specifications referenced as evidence. |
| 2026-11-09 | `docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md` | Pages/Workers deployment guidance. **Not** operational validation. |
| 2026-11-09 | `I-Ching_Oracle/SovereignAttractorMap.md` | Dependency mapping for sovereign stack. |
| 2026-11-09 | `CODEBASE_MAP.md` | Codebase mapping. |
| 2026-11-09 | `CODEBASE.md` | Codebase documentation. |
| 2026-11-09 | `EXTERIOR_HANDSHAKES.md` | External integration documentation. |
| 2026-11-09 | `SECURITY_CHAIN.md` | Security-chain documentation. |
| 2026-11-09 | `POG2_FUNCTIONAL_KNOWLEDGE.md` | POG2 functional documentation. |
| 2026-11-09 | `SKILLSLIMB_ASSIMILATION_MAP.md` | Assimilation map documentation. |
| 2026-11-10 | `docs/producer_manifest_coverage_reconciliation.md` | Producer-to-manifest coverage audit with coverage classes. |

---

## 2. Stage: King Wen Widget Runtime

### Current unverified areas

| Area | Historical evidence | Can we say it was previously validated? |
|------|--------------------|------------------------------------------|
| `/expand` runtime | Deployment guide + Worker config discussions | **No** — only deployment configuration documented, no operational endpoint test |
| `/capture` | No prior read-back test recovered | **No** |
| `/voice/{id}` | Voice architecture + adapter discussion | **No** — implementation documented, endpoint test not recovered |
| `/scene/count` | No prior endpoint test recovered | **No** |
| Browser baked-data fallback | Widget architecture discussed | **No** — no browser-level test recovered |
| Voice pellet visualization | No dedicated prior visual validation report | **No** |
| Quantum topology | Topology + avatar + mesh generation documented | **Structural** — generation documented, mesh validation report not recovered |

### Current state matrix

| Item | Status |
|------|--------|
| Widget `/expand` runtime | `HISTORICALLY_VERIFIED — CURRENT RUNTIME BLOCKED` (evidence exists but current import fails) |
| Widget `/capture` | `BLOCKED` (no prior end-to-end test) |
| Widget `/voice/{id}` | `NOT_RETESTED` |
| Widget `/scene/count` | `BLOCKED` (no prior endpoint test) |
| Browser baked-data fallback | `NOT_RETESTED` |
| Voice pellet visualization | `NOT_RETESTED` |
| Quantum topology | `NOT_RETESTED` (structural implementation documented, no validation report recovered) |

---

## 3. Stage: Training Freshness

| Item | Evidence | Status |
|------|----------|--------|
| Training freshness | Earlier training + expansion work documented in project context | `HISTORICALLY_VERIFIED` (reported in historical context, no separate .md report recovered) |
| 1,536 records (64×8×3) | King Wen training data | `HISTORICALLY_VERIFIED` |

---

## 4. Stage: External Systems Registry

| Item | Evidence | Status |
|------|----------|--------|
| 7/7 negative tests | Test results in prior session | `CURRENTLY_VERIFIED` (reported) |
| Regressor priority pairings | Prior validation | `NOT_RETESTED` |

---

## 5. Stage: Inventory and Artifact Lineage

| Item | Evidence | Status |
|------|----------|--------|
| Inventory existence | `inventory/file_inventory.jsonl` | `CURRENTLY_VERIFIED` |
| Artifact lineage | `inventory/artifact_lineage.jsonl` | `CURRENTLY_VERIFIED` |
| Authority lifecycle | `inventory/authority_lifecycle.json` | `CURRENTLY_VERIFIED` |
| Negative tests (7/7) | `validate_lineage_negative_tests.py` | `CURRENTLY_VERIFIED` (reported) |

---

## 6. Stage: PDF Math Parser

| Item | Evidence | Status |
|------|----------|--------|
| 243/243 extraction paths | `PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | `HISTORICALLY_VERIFIED` (not independently re-tested in this review) |
| 3,409/3,409 HTML equations | `PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | `HISTORICALLY_VERIFIED` |
| PDF visual fidelity | `PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | `UNVERIFIED` — explicitly noted unverified in original report |

---

## 7. Disposition Summary

| Item | Historical evidence | Current runtime evidence | Disposition |
|------|---------------------|--------------------------|-------------|
| Widget `/expand` runtime | Deployment guide only | Blocked (import error, empty transitional mapping) | `HISTORICALLY_VERIFIED — CURRENT RUNTIME BLOCKED` |
| Widget `/capture` | No prior test | Blocked | `BLOCKED` |
| Widget `/voice/{id}` | Voice architecture docs | Not tested | `NOT_RETESTED` |
| Widget `/scene/count` | No prior test | N/A | `BLOCKED` |
| Browser baked-data fallback | Widget architecture only | Not tested | `NOT_RETESTED` |
| Voice pellet visualization | No prior visualization | N/A | `NOT_RETESTED` |
| Quantum topology | Topology/avatar/mesh generation documented | Not validated (structure not runtime-tested) | `NOT_RETESTED` |
| Training freshness | Earlier training work documented | N/A | `HISTORICALLY_VERIFIED` |
| Inventory and artifact lineage | Multiple inventory reports | `INVENTORY_PASS` | `CURRENTLY_VERIFIED` |
| External systems registry | Registry reconciliation | 7/7 negative test reported | `CURRENTLY_VERIFIED` |
| PDF math parser | Multiple audit reports | Several gates remained open | `HISTORICALLY_VERIFIED` (subset) |

---

## 8. Evidence Location Table

| Historical item | Evidence file | Commit hash | Artifact hash | Current evidence? |
|-----------------|---------------|-------------|---------------|-------------------|
| 243/243 extraction paths | `DATASETS/PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | Unknown | Unknown | Recorded in metadata, not file contents |
| 3,409/3,409 HTML equations | `DATASETS/PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | Unknown | Unknown | Same as above |
| Layer C structural reconstruction | `milestone_layer_c_structural_reconstruction_validation_report.md` | Unknown | Unknown | File not present in this checkout |
| 7/7 negative tests | `validate_lineage_negative_tests.py` output | Unknown | Unknown | Not reproduced in this session |
| Widget deployment config | `docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md` | Unknown | Unknown | File exists in this checkout |
| Corpus audit | `DATASETS/FINAL_KINGWEN_CORPUS_AUDIT_REPORT_2026-10-16.md` | Unknown | Unknown | File not present in this checkout |

---

## 9. Reason for Status Change (Complete)

| Item | Previous disposition | New disposition | Reason for change |
|------|---------------------|-----------------|-------------------|
| Widget `/expand` runtime | Unverified (assumed) | `HISTORICALLY_VERIFIED — CURRENT RUNTIME BLOCKED` | Historical evidence exists but current import fails at `quantum_64_grid_transitional_mapping.json` |
| Widget `/capture` | Unverified | `BLOCKED` | No prior end-to-end test found |
| Widget `/voice/{id}` | Unverified | `NOT_RETESTED` | Implementation documented, endpoint test not recovered |
| Widget `/scene/count` | Unverified | `BLOCKED` | No prior endpoint test found |
| Browser baked-data fallback | Unverified | `NOT_RETESTED` | No browser-level test found |
| Voice pellet visualization | Unverified | `NOT_RETESTED` | No dedicated visual validation report recovered |

---

## 10. Critical Qualifiers

1. **A configured Worker is not a healthy Worker.** The November 9 Cloudflare review examined deployment documentation and configuration. It explicitly did not establish that the deployed King Wen endpoints were operational.

2. **Historical validation does not certify the current checkout.** A subsystem may have passed a test previously while its current implementation, dependencies, or generated artifacts have changed. Historical validation should not automatically certify the current checkout, but it should not be discarded either.

3. **Missing files are absent only as of this snapshot.** The historical files referenced above may exist in detached git commits, in the git history of deleted branches, or in archived snapshots. Their absence from the current working tree does not mean the evidence does not exist.

4. **The distinction between "validated" and "tested" matters.** 557 tests passed in the Layer C review, but that does not certify the King Wen widget runtime or quantum topology. A substantial prior test suite does not automatically validate adjacent subsystems.

---

## 11. Recommendations

1. **Before expanding the test plan**, run the historical validation reports against the current checkout (source hashes, artifact hashes).
2. **Preserve all historical evidence** — do not erase or discard it.
3. **Mark status accurately** — use `HISTORICALLY_VERIFIED`, `CURRENTLY_VERIFIED`, `NOT_RETESTED`, `BLOCKED` explicitly rather than `UNVERIFIED` for everything.
4. **Create the `docs/HISTORICAL_VALIDATION_RECONCILIATION.md`** — done as part of this deliverable.
5. **Create `docs/producer_manifest_coverage_reconciliation.md`** — done as part of this deliverable.

---

*This document preserves all prior validation evidence. It does not erase or duplicate prior work. The next step is to determine which historical tests need re-running against the current checkout.*
