# Documentation Registry — KING-WEN-I-CHING-IMMUTABLE-TABLES

**Generated:** 2026-11-04
**Scope:** All project `.md` files excluding vendored dependencies (`node_modules/`, `.venv/`, `.pytest_cache/`, `cache/`)
**Total project markdown files:** 201 (130 in docs/, 48 in DATASETS/, 5 in learn/, 9 at root, 2 in openjarvis_blueprints_extracted/, 1 each in data/, references/, scripts/, skills/, src/)

## Registry Schema

Each document should carry the following metadata fields (to be populated incrementally):

| Field | Purpose |
|---|---|
| `document_id` | Stable identity independent of filename |
| `document_type` | Evidence, finding, specification, verification, remediation, index |
| `status` | Proposed, active, frozen, superseded, accepted, rejected |
| `authority` | Informational, normative, evidentiary, acceptance |
| `created` / `updated` | Lifecycle tracking |
| `supersedes` | Explicit replacement relationship |
| `depends_on` | Source or evidence dependencies |
| `related_findings` | Cross-document finding references |
| `content_hash` | Detect changes to frozen documents |

## Document Lifecycle Roles (Recommended Directory Architecture)

| Role | Directory | Purpose |
|---|---|---|
| 00 — Documentation Registry | `docs/DOCUMENTATION_REGISTRY.md` | This file — single index of all documentation |
| 01 — Evidence | `docs/` + `DATASETS/` | Original observations, frozen results, source records, measurements |
| 02 — Findings | `docs/` | Audits, cross-document findings, discrepancies, dispositions |
| 03 — Specifications | `docs/` | Proposed contracts, schemas, protocols, acceptance criteria |
| 04 — Verification | `docs/` + `tests/` | Test plans, execution results, regression mappings, acceptance records |
| 05 — Remediation | `docs/` | Remediation proposals, implementation records, closure evidence |

These are documentation roles, not instructions to physically move or merge existing files.

## Inventory by Directory

### New Documentation Governance & Engineering Contract Files (2026-11-04 to 2026-11-05)

| File | Purpose | Status |
|---|---|---|
| `docs/DOCUMENTATION_REGISTRY.md` | This file — central documentation index | Active |
| `docs/DOCUMENTATION_OVERLAP_ANALYSIS_2026-11-04.md` | Read-only overlap analysis (exact/near duplicates, orphans, unresolved) | Active |
| `docs/RELATIONSHIP_DECISION_REGISTER_2026-11-04.md` | Relationship adjudication register (RD-001 through RD-004d) | Active |
| `docs/spatial-syntactic-preservation-specification.md` | Spatial-syntactic preservation specification (Sections 1–11) | Active / Normative |
| `docs/cyber-physical-agentic-engineering-contract.md` | 6-gate cyber-physical architecture, 3 reference domains, fidelity metrics | Active / Normative |
| `DATASETS/documentation_hash_manifest_2026-11-04.json` | SHA-256 hash manifest for project .md files | Frozen (evidence) |
| `DATASETS/structural_preservation/layer_c_post_implementation_baseline.json` | Layer C post-implementation frozen baseline manifest | Frozen (evidence) |
| `DATASETS/structural_preservation/v2_v3_comparison_evaluation.json` | Layer B vs Layer C comparative evaluation record (10/15 PRESERVED) | Frozen (evidence) |
| `DATASETS/structural_preservation/contract_verification_audit_report.json` | Machine-checked 6-gate audit certifying engineering contract | Frozen (evidence) |

### Root (9 files)

| File | Size (bytes) | Status | Notes |
|---|---|---|---|
| `README.md` | — | active | Project README |
| `AGENTS.md` | — | active | Agent instructions |
| `KINGWEN_AGENT_ONBOARDING.md` | — | active | 6-layer read order for agents |
| `king-wen-workflow-paths.md` | — | active | Workflow paths reference |
| `jarvis-kingwen-missed-integrations.md` | — | active | Integration gap audit |
| `SKILL_hexagram_state_machine.md` | — | active | Skill definition |
| `codebasemap.md` | — | active | Codebase map |
| `lua-math-tool.md` | — | active | Lua math tool reference |
| `ALL-FILES.md` | 31,677,898 | generated | **Untracked** (removed from Git tracking 2026-11-04); reproducible via `make_all_files_csv.py` |

### docs/ (130 files)

#### Core Specifications
| File | Size (bytes) |
|---|---|
| `docs/immutable-table-math-decoded.md` | — |
| `docs/j-space-jacobian-lens-math-2026-07-11.md` | — |
| `docs/ternary-paired-differential-math-correction-2026-08-02.md` | — |
| `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` | — |
| `docs/TERNARY-SEMANTICS-RECONCILIATION.md` | — |

#### Math Pipeline & Evidence
| File | Size (bytes) |
|---|---|
| `docs/math-pipeline-evidence-matrix-2026-11-03.md` | — |
| `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | 63,465 |
| `docs/qsmc1-m3-dimensional-consistency-analysis.md` | 34,475 |
| `docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md` | 25,772 |
| `docs/qsmc1-cross-group-consistency-validation.md` | 27,464 |
| `docs/traceability-matrix-2026-10-27.md` | 34,768 |
| `docs/traceability-matrix-audit-2026-10-27.md` | — |
| `docs/research-to-test-traceability-matrix-2026-10-29.md` | — |
| `docs/occurrence-lifecycle-ledger-contract-2026-11-03.md` | — |
| `docs/semantic_math_pipeline_report.md` | — |
| `docs/pipeline-gap-analysis-2026-10-27.md` | — |
| `docs/pipeline-output-measurement-2026-10-27.md` | — |
| `docs/math-term-usage-analysis-2026-10-27.md` | — |
| `docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` | — |
| `docs/yao-line-semantic-audit-2026-10-29.md` | — |
| `docs/room-5-typed-integral-ir-2026-10-08.md` | — |
| `docs/room-4-typed-expression-ir-2026-10-08.md` | — |
| `docs/numerical-extraction-vision-pipeline.md` | — |

#### Vision & Context Preservation
| File | Size (bytes) |
|---|---|
| `docs/standalone-context-preservation-test-plan-2026-11-04.md` | — |
| `docs/context-preservation-implementation-evaluation-spec-2026-11-04.md` | — |
| `docs/context-preservation-gate-verification-matrix-2026-11-04.md` | — |
| `docs/vision-stretched-symbols-border-recognition-audit-2026-11-03.md` | — |
| `docs/lossy-coverage-cross-examination-2026-11-04.md` | — |
| `docs/glyph-catalog-template-matching-p1-spec-2026-11-03.md` | — |
| `docs/pix2text-three-layer-experiment.md` | — |
| `docs/pix2text-assessment-2026-10-20.md` | — |
| `docs/adjudication-layer-contract.md` | — |
| `docs/cross-verification-checklist-2026-09-01.md` | — |

#### Cross-Reference & Field Availability
| File | Size (bytes) |
|---|---|
| `docs/field-availability-and-derivation-matrix-2026-11-04.md` | — |
| `docs/measurement-enrichment-schema-specification-2026-11-04.md` | — |
| `docs/full-page-text-math-extraction-cross-reference-plan-2026-11-04.md` | — |
| `docs/cross-reference-authorization-boundary-2026-11-04.md` | — |
| `docs/cohort-comparison-zero-pass-vs-full-pass-2026-11-04.md` | — |

#### Frozen Regression & Evaluation
| File | Size (bytes) |
|---|---|
| `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | — |
| `docs/frozen-regression-execution-results-2026-11-03.md` | — |

#### Cross-Document Finding Authority
| File | Size (bytes) |
|---|---|
| `docs/cross-document-finding-authority-map-2026-11-03.md` | 42,953 |

#### Remediation & Verification
| File | Size (bytes) |
|---|---|
| `docs/remediation-verification-matrix.md` | 26,297 |
| `docs/information-loss-remediation-register.md` | 26,133 |
| `docs/controlled-remediation-verification-protocol.md` | 29,671 |
| `docs/pre-remediation-evidence-freeze-2026-11-02.md` | — |
| `docs/unknowns-register-2026-11-02.md` | — |
| `docs/rv-governance-addition-2026-11-03.md` | — |
| `docs/shotgun-authority-lineage-audit.md` | — |
| `docs/shotgun-expansion-integrity-audit.md` | — |
| `docs/shotgun-representation-consumer-continuity-audit.md` | 30,984 |
| `docs/shotgun-reinvention-audit.md` | — |
| `docs/shotgun-expand-output-contract-2026-10-29.md` | — |

#### Traceability & Audit
| File | Size (bytes) |
|---|---|
| `docs/markdown-evidence-validation-artifact-qsmc1-field-lineage.md` | 31,319 |
| `docs/markdown-evidence-to-skill-relationship-matrix.md` | 30,633 |
| `docs/research-archaeology-baseline-2026-10-07.md` | 38,663 |
| `docs/shotgun-representation-consumer-continuity-audit.md` | 30,984 |

#### QSMC-1 & Field Lineage
| File | Size (bytes) |
|---|---|
| `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | 63,465 |
| `docs/qsmc1-m3-dimensional-consistency-analysis.md` | 34,475 |
| `docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md` | 25,772 |
| `docs/qsmc1-cross-group-consistency-validation.md` | 27,464 |

#### Other docs/ files
| File | Size (bytes) |
|---|---|
| `docs/KINGWEN_AGENT_ONBOARDING.md` | — |
| `docs/CONSOLIDATED_SKILL_GRAPH_RELATIONSHIPS.md` | — |
| `docs/CONSOLIDATED_REMEDIATION_AUDIT.md` | — |
| `docs/CONSOLIDATED_QSMC1_M3_HAMILTONIAN.md` | — |
| `docs/CONSOLIDATED_FIELD_LINEAGE.md` | — |
| `docs/CONSOLIDATED_DOCUMENT_INDEX.md` | — |
| `docs/vision_artifact_manifest.json` | — |

### DATASETS/ (48 .md files)

Includes per-paper pix2text output files, POG3 fungal substrate spec, and other dataset-level documentation. These are generated or data-adjacent artifacts.

### learn/ (5 .md files)

Learning/extraction documentation.

### Root-level (9 files)

See table above.

### Other directories

- `openjarvis_blueprints_extracted/` (2 .md files)
- `data/` (1 .md file)
- `references/` (1 .md file)
- `scripts/` (1 .md file)
- `skills/` (1 .md file)
- `src/` (1 .md file)

### Notes

1. **Generated file:** `ALL-FILES.md` (31 MB) was removed from Git tracking on 2026-11-04. Local copy preserved. Regenerable via `make_all_files_csv.py` (produces `ALL-FILES.csv`; `ALL-FILES.md` is a separate markdown rendering). Verify no script consumes its content before deleting local copy.
2. **No consolidation performed.** Per external assessment, documents are preserved in their original locations. Consolidation should only occur after overlap analysis identifies demonstrably identical authority and compatible lifecycle status.
3. **No frontmatter changes.** Per external assessment, document lifecycle metadata should be added incrementally, not via bulk frontmatter injection.
4. **No commits beyond `c40286cd6a`.** Per user authorization, no further commits are authorized at this time.
5. **DATASETS directory included in all searches.** Per user rule, DATASETS holds much of the files needed for the program; ignoring it would miss more than math tools.
6. **Manifest population:** The hash manifest contains 200 files. The registry references 201+ files. The difference is because the manifest was generated before the overlap analysis and relationship register files were created. Regenerate the manifest if a complete current-state hash is needed.
7. **Recommended metadata fields** (per external assessment, to be populated incrementally): `source_commit` (commit associated with document's original evidence), `evidence_scope` (population, experiment, or dataset covered), `review_state` (unreviewed, reviewed, disputed, accepted), `integrity_state` (mutable, frozen, hash-verified). Document status and evidence integrity are separate dimensions.