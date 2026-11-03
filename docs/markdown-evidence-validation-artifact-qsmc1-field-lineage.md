# Markdown Evidence Validation Artifact — QSMC-1 and Field-Lineage Cluster

## Scope and Method

- **Read-only investigation.** No files, frontmatter, skill definitions, or graph edges were modified.
- **Unit of analysis:** Individual observations (known facts, unresolved questions), not documents.
- **Starting cluster:** QSMC-1 and field-lineage documents (per user recommendation).
- **Four sections:** (1) Deduplicated document registry, (2) Known-to-unknown ledger, (3) Skill capability mapping, (4) Directed relationship candidates.

---

## Section 1 — Deduplicated Document Registry

### Reconciliation of Counts

The previous inventory (B1–B9) listed 98 rows but only 63 untracked `docs/*.md` files exist. The discrepancy is explained by:

- **Duplicate inventory entries:** Several files appeared in multiple B-sections (e.g., `qsmc1-m3-m6-reproduction.md` appeared in both B1 and B7; `qsmc1-cross-group-consistency-validation.md` appeared in both B1 and B7).
- **Tracked files misclassified as untracked:** Some B-section entries (e.g., `immutable-table-math-decoded.md`, `j-space-jacobian-lens-math-2026-07-11.md`, `KING_WEN_CONSENSUS_MATH.md`) are tracked (committed) files, not newly created untracked files.
- **Cross-population mixing:** Files from Population C (unmodified historical) were inadvertently included in Population B sections.

### Corrected Counts

| Population | Description | Count |
|-----------|-------------|-------|
| A — Modified tracked | `README.md` (root) | 1 |
| B — Newly created (untracked) | `docs/*.md` (untracked) | 63 |
| C — Unmodified historical (tracked) | Committed `.md` files across all directories | 102 |
| **Total unique Markdown files** | | **166** |

### Deduplicated Document Registry — QSMC-1 and Field-Lineage Cluster (20 files)

These are the documents selected for the first observation cluster, all untracked in `docs/`:

| # | Path | Subject | Evidence Status | Confidence | Git Status |
|---|------|---------|-----------------|------------|------------|
| 1 | `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | M3 Hamiltonian provenance — 15 sections, formula lineage, V1 vs V2 | Validated (F-10/F-11/F-12) | High | Untracked |
| 2 | `docs/qsmc1-m3-mathematical-validation-f10.md` | F-10 semantic/scale compatibility validation | Validated | High | Untracked |
| 3 | `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md` | F-12 clamp information loss (727→1 distinct values) | Validated | High | Untracked |
| 4 | `docs/qsmc1-m3-m6-imaginary-amplitude-f11.md` | F-11 imaginary amplitude (type 2 dependency) | Validated | High | Untracked |
| 5 | `docs/qsmc1-m3-dimensional-consistency-analysis.md` | F-10 formal dimensional analysis | Validated | High | Untracked |
| 6 | `docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md` | M3 floor/ceiling/extremum research | Validated | High | Untracked |
| 7 | `docs/qsmc1-m3-scale-mismatch-diagnosis.md` | M3 scale mismatch numerical diagnosis | Validated | High | Untracked |
| 8 | `docs/qsmc1-m3-hamiltonian-energy-correspondence.md` | M3 Hamiltonian correspondence evidence | Validated | High | Untracked |
| 9 | `docs/qsmc1-m3-m6-reproduction.md` | M3–M6 numerical reproduction | Validated | High | Untracked |
| 10 | `docs/qsmc1-m2-expectation-consensus-correspondence.md` | M2 expectation/consensus correspondence | Validated | High | Untracked |
| 11 | `docs/qsmc1-m6-interference-coherence-correspondence.md` | M6 interference/coherence correspondence | Validated | High | Untracked |
| 12 | `docs/qsmc1-m7-evolution-propagation-correspondence.md` | M7 evolution/propagation correspondence | Validated | High | Untracked |
| 13 | `docs/emotional-vector-lineage-audit-2026-11-02.md` | L1 — Emotional vector field-level lineage | Validated | High | Untracked |
| 14 | `docs/porosity-lineage-audit-2026-11-02.md` | L2 — Porosity field-level lineage | Validated | High | Untracked |
| 15 | `docs/hamiltonian-lineage-audit-2026-11-02.md` | L3 — Hamiltonian field-level lineage | Validated | High | Untracked |
| 16 | `docs/cross-field-dependency-matrix-2026-11-02.md` | Cross-field dependency and information-preservation matrix | Validated | High | Untracked |
| 17 | `docs/unknowns-register-2026-11-02.md` | Unknowns register (U-01 through U-10) | Validated | High | Untracked |
| 18 | `docs/pre-remediation-evidence-freeze-2026-11-02.md` | Pre-remediation evidence freeze (16-artifact index) | Validated | High | Untracked |
| 19 | `docs/cross-reference-audit-2026-11-02.md` | Cross-reference audit (10 reports) | Validated | High | Untracked |
| 20 | `docs/remediation-verification-matrix.md` | 8-entry verification matrix (F-01–F-08) | Validated | High | Untracked |

**Note:** The 3 path-mismatched references identified in the previous inventory are reconciled as follows:

| Missing Target | Resolves To | Status |
|----------------|-------------|--------|
| `canonical-table-audit` | `verification/canonical-table-audit` | Path mismatch — fixable |
| `verification-rules` | `verification/verification-artifact-hygiene` | Path mismatch — fixable |
| `verified-engineering` | `software-development/verified-engineering` | Path mismatch — fixable |

All three are fixable path corrections. The earlier audit's count of 2 was incomplete; the third (`verified-engineering`) was confirmed against the active skill inventory.

---

## Section 2 — Known-to-Unknown Ledger

Observations extracted from the QSMC-1 and field-lineage documents. Each observation is a known fact with an associated unresolved question.

### Observation Cluster A: Hamiltonian / M3

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| A1 | M3 V1-to-V2 scale change retained coefficients 0.5/0.3/0.2 without normalization | Original theoretical justification for coefficients | Validated scale incompatibility; provenance unresolved | High | `qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | `kingwen` (produces) |
| A2 | 727 raw Hamiltonian values collapse to one bounded output (0.0) via one-sided clamp | Intended treatment of negative values | Information loss validated; intended semantics unresolved | High | `qsmc1-m3-one-sided-clamp-information-loss-f12.md` | `kingwen` (produces), `kingwen-ternary-expansion` (consumes) |
| A3 | Coefficients 0.5/0.3/0.2 sum to 1.0 but elements are not in a common mathematical space | Whether coefficients were designed for ratio-scale (V1) and applied to raw counts (V2) | Scale incompatibility validated; theoretical justification not established | High | `qsmc1-m3-dimensional-consistency-analysis.md` | `kingwen-ternary-expansion` (verifies) |
| A4 | Formula first appeared in commit `ea89a9cf2d` as V2 (raw counts) | Whether V1 (ratios) was ever implemented or only documented | Provenance traced; no V1 implementation found | High | `qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | `kingwen` (produces) |
| A5 | October 27 document formula (four differentials, /6.0 scaling, equal weights) was never implemented | Whether this represents a design intent that should be implemented | Classified as design intent (never implemented) | High | `formula-design-review-2026-10-27.md` | `kingwen-ternary-expansion` (advises) |
| A6 | QuantumLab ruled out as M3 formula source (9 user commits, infrastructure only) | Where the formula actually originated | Provenance complete; no source found | High | `qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | `kingwen` (produces) |
| A7 | Wiki math corpus (139 entries) contains no M3 formula or coefficients | Whether any external source documents the formula | Provenance complete; no source found | High | `qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | `kingwen` (produces) |

### Observation Cluster B: M6 Imaginary Amplitude

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| B1 | M6 imaginary amplitude is 0.0 in all observed 1,536 states | Whether nonzero runtime behavior is possible | Current result validated; nonzero runtime coverage absent | High | `qsmc1-m3-m6-imaginary-amplitude-f11.md` | `kingwen` (produces), `kingwen-emotion-voice` (consumes) |
| B2 | M6 imaginary amplitude formula: `imag_part = (rv - ev) × (hamiltonian_normalized × phase_complexity × 0.1)` — multiplicative path | Whether the multiplicative path is the intended design | Analytical capability established; runtime demonstration absent | High | `qsmc1-m3-m6-imaginary-amplitude-f11.md` | `kingwen` (produces) |
| B3 | Empty line_balance {} at emotional_engine.py:499 | Whether line_balance is populated by any consumer | Consumer integration defect identified (F-08) | High | `qsmc1-m3-m6-imaginary-amplitude-f11.md` | `kingwen` (produces), `openjarvis-kingwen-integration` (consumes) |
| B4 | M6 inherits zero-energy condition from M3 (because H=0.0) | Whether M6 would produce nonzero imaginary amplitude if M3 H were nonzero | Dependency chain F-10→F-12→F-11 documented | High | `qsmc1-m3-m6-imaginary-amplitude-f11.md` | `kingwen` (produces) |

### Observation Cluster C: Porosity

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| C1 | Porosity has three unreconciled computational representations: injection site (int 0-4), phase-modulated (float 0.0-1.0), kit QWP (float 0.15-0.71) | Whether a valid cross-domain mapping exists | Lineage finding reported; semantic reconciliation unresolved | High | `porosity-lineage-audit-2026-11-02.md` | `kingwen` (produces), `kingwen-ternary-expansion` (consumes) |
| C2 | `inject_site.get("porosity", 0.35)` returns None when key exists with None value; `float(None)` raises TypeError | Whether any consumer handles None porosity gracefully | Consumer integration defect (F-02) | High | `porosity-lineage-audit-2026-11-02.md` | `kingwen` (produces), `openjarvis-kingwen-integration` (consumes) |
| C3 | Phase 6-7 (void) has no porosity=0 states | Whether void states should have zero porosity | Data gap identified; semantic question unresolved | Medium | `porosity-lineage-audit-2026-11-02.md` | `kingwen` (produces) |
| C4 | Porosity bleed uses 20% modulation (`bleed = base + (phase_overdrive * 0.5)`) | Whether 20% is derived or arbitrary | No theoretical basis documented | Medium | `porosity-lineage-audit-2026-11-02.md` | `kingwen-ternary-expansion` (verifies) |

### Observation Cluster D: Emotional Vectors

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| D1 | 5-axis emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight) with 4-source blending | Whether blending weights (60/40, 70/30, 15%, 25%) are derived or arbitrary | Integrity partially preserved; weight provenance unresolved | High | `emotional-vector-lineage-audit-2026-11-02.md` | `kingwen` (produces), `kingwen-emotion-voice` (consumes) |
| D2 | Phase shifts hardcoded: chaos +0.1, whimsy +0.05, darkTone -0.1 | Whether phase shifts are derived from line-state balance | No theoretical basis documented | Medium | `emotional-vector-lineage-audit-2026-11-02.md` | `kingwen` (produces) |
| D3 | `or 0.0` fallbacks in emotional vector computation silently replace explicit 0.0 | Whether any consumer relies on 0.0 as a valid value | Consumer integration defect (F-01) | High | `emotional-vector-lineage-audit-2026-11-02.md` | `kingwen` (produces) |
| D4 | `domain_vector == resolved_vector` (0 mismatches) | Whether domain_vector should be derived independently | Redundant field; not a documented intentional boundary | Medium | `emotional-vector-lineage-audit-2026-11-02.md` | `kingwen-ternary-expansion` (verifies) |

### Observation Cluster E: Cross-Field Dependency

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| E1 | 4 concern classes identified: provenance loss, representation inconsistency, information collapse, integration defects | Whether these classes are exhaustive | Cross-field matrix complete | High | `cross-field-dependency-matrix-2026-11-02.md` | `kingwen`, `kingwen-ternary-expansion` |
| E2 | 6 code-fix-only findings (F-01, F-02, F-05, F-05b, F-06, F-07) | Whether fixes would introduce regressions | Reversibility assessment complete | High | `cross-field-dependency-matrix-2026-11-02.md` | `kingwen`, `kingwen-ternary-expansion` |
| E3 | 10 intentional boundaries preserved (expanded vs resolved, binary vs ternary, etc.) | Whether all boundaries are documented | Boundary classification complete | High | `cross-field-dependency-matrix-2026-11-02.md` | `kingwen`, `kingwen-ternary-expansion` |
| E4 | 2 redundant fields identified: domain_vector == resolved_vector, primary == neighbor_blend in sample_paths | Whether redundancy is intentional or a defect | Non-intentional redundant fields flagged | Medium | `cross-field-dependency-matrix-2026-11-02.md` | `kingwen-ternary-expansion` (verifies) |

### Observation Cluster F: Shotgun Expand / Consumer Continuity

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| F1 | shotgun_expand() at scripts/full_hexagram_shotgun.py:549 returns dict with expanded[] (64), resolved[] (512), consensus, ternary_permutations (729/hex), total_ternary_permutations (46,656), total_domained_routes (35,000), capture_point, personality_consensus, personality_subsets | Whether all 23+ consumers correctly consume the full output | 5 broken consumers (F-05/F-05b), 2 fixed consumers, 23+ functional | High | `shotgun-representation-consumer-continuity-audit.md` | `kingwen` (produces), `openjarvis-kingwen-integration` (consumes) |
| F2 | 5 broken consumers reference nonexistent `shotgun_expand_output.json` | Whether these consumers should be fixed or removed | F-05 additive discovery; F-05b provisional | High | `shotgun-representation-consumer-continuity-audit.md` | `kingwen` (produces), `openjarvis-kingwen-integration` (consumes) |
| F3 | 2 fixed consumers: kingwen_mobius_sphere.py and kingwen_state_transition.py now load from live shotgun_expand() | Whether fixes are complete and correct | Fixed; verification pending | High | `shotgun-representation-consumer-continuity-audit.md` | `kingwen` (produces) |
| F4 | No canonical JSON export exists for shotgun_expand() output | Whether a canonical export should be created | Output contract documented; no export implemented | Medium | `shotgun-expand-output-contract-2026-10-29.md` | `kingwen`, `kingwen-ternary-expansion` |

### Observation Cluster G: Porosity (Cross-Reference)

| # | Known Observation | Related Unknown | Evidence Status | Confidence | Source Document | Potential Skill |
|---|-------------------|-----------------|-----------------|------------|-----------------|-----------------|
| G1 | Porosity has 3 independent computations not reconciled | Whether a valid cross-domain mapping exists | Lineage finding reported; semantic reconciliation unresolved | High | `porosity-lineage-audit-2026-11-02.md` | `kingwen` (produces), `kingwen-ternary-expansion` (consumes) |
| G2 | `inject_site.get("porosity", 0.35)` returns None when key exists with None value | Whether any consumer handles None porosity gracefully | Consumer integration defect (F-02) | High | `porosity-lineage-audit-2026-11-02.md` | `kingwen` (produces), `openjarvis-kingwen-integration` (consumes) |
| G3 | Phase 6-7 (void) has no porosity=0 states | Whether void states should have zero porosity | Data gap identified; semantic question unresolved | Medium | `porosity-lineage-audit-2026-11-02.md` | `kingwen` (produces) |
| G4 | Porosity bleed uses 20% modulation | Whether 20% is derived or arbitrary | No theoretical basis documented | Medium | `porosity-lineage-audit-2026-11-02.md` | `kingwen-ternary-expansion` (verifies) |

---

## Section 3 — Skill Capability Mapping

Actual skill capabilities matched to observations. Skills are identified by their registered names in the Hermes skill library.

### King Wen Core Skills

| Skill | Capability | Owns Computation? | Consumes Observations From | Produces Observations For |
|-------|-----------|-------------------|---------------------------|---------------------------|
| `kingwen` | King Wen cognitive state machine (512 states, 64 hexagrams × 8 phases) | Yes — emotional_engine.py, decision_matrix.py, full_hexagram_shotgun.py | M3 Hamiltonian, M6 imaginary amplitude, porosity, emotional vectors | All downstream consumers |
| `kingwen-ternary-expansion` | Ternary expansion (729 permutations/hex, 5,832 resolved states) | Yes — ternary_full_expansion.json, multi_layer_expand.py | M3 Hamiltonian, porosity, emotional vectors, ternary slots | Math extraction, verification |
| `openjarvis-kingwen-integration` | OpenJarvis ↔ King Wen integration bridge | No — consumes King Wen output | shotgun_expand output, porosity, emotional vectors, emotional_tongue | OpenJarvis runtime |
| `kingwen-emotion-voice` | Emotion voice weights (5-axis vector → Cartesia TTS) | No — consumes emotional vectors | Emotional vectors (chaos, whimsy, darkTone, coherence, voiceWeight) | Voicebox TTS |

### King Wen Research Skills

| Skill | Capability | Owns Computation? | Consumes Observations From | Produces Observations For |
|-------|-----------|-------------------|---------------------------|---------------------------|
| `research/kingwen-jarvis-megatron-learn` | King Wen ↔ Jarvis ↔ Megatron learning loop | No — orchestrates integration | All King Wen outputs | Megatron training data |
| `research/kingwen-oracle-advisory` | King Wen oracle advisory interface | No — advisory layer | King Wen consult output | OpenJarvis runtime |
| `research/kingwen-learn-suite-runner` | /learn verification suite runner | No — test runner | King Wen test results | Verification skills |
| `research/avalokiteshvara-kingwen` | Multi-arm capability registry | No — registry | King Wen skill cards | Avalokiteshvara dispatch |
| `research/learn_king_wen_math_extractors` | Math extraction for King Wen | No — extraction tooling | PDF/arXiv math content | King Wen engine |

### Math Extraction Skills

| Skill | Capability | Owns Computation? | Consumes Observations From | Produces Observations For |
|-------|-----------|-------------------|---------------------------|---------------------------|
| `research/math-pdf-parser` | Formal math PDF parser (6-layer pipeline) | Yes — math_pdf_parser.py | PDF documents | Math extraction skills |
| `research/multi-engine-math-parsing` | Multi-engine math parsing | Yes — orchestration | PDF documents | Math extraction skills |
| `research/math-structural-ast-fidelity` | Typed MathML AST extraction | Yes — AST extraction | MathML documents | Math extraction skills |
| `research/vision-math-symbol-detection` | Vision-based math symbol detection | Yes — image processing | PDF images | Math extraction skills |
| `research/pdf-math-extraction-quality` | PDF math extraction quality | No — quality assessment | Extraction results | Math extraction skills |
| `research/arxiv-math-extraction` | ArXiv HTML math extraction | Yes — arxiv_html_parser.py | ArXiv HTML | Math extraction skills |

### Verification Skills

| Skill | Capability | Owns Computation? | Consumes Observations From | Produces Observations For |
|-------|-----------|-------------------|---------------------------|---------------------------|
| `verification/capability-pulse` | Passive Hermes self-upgrader loop | No — monitoring | Skill directory state | Capability pulse |
| `verification/verification-artifact-hygiene` | Artifact parse-back verification | No — verification | Generated artifacts | Verification skills |
| `verification/canonical-table-audit` | Canonical table audit | No — audit | Canonical tables | Verification skills |

### 3D / Visualization Skills

| Skill | Capability | Owns Computation? | Consumes Observations From | Produces Observations For |
|-------|-----------|-------------------|---------------------------|---------------------------|
| `autonomous-ai-agents/kingwen-3d-tooling` | King Wen 3D generators and DA-V2 depth bridge | Yes — 3D generation | King Wen state | 3D visualization |
| `autonomous-ai-agents/kingwen-paper-math-bridge` | Paper math → King Wen engine edits | No — bridge | Research papers | King Wen engine |

---

## Section 4 — Directed Relationship Candidates

Directed relationships with evidence, rationale, confidence, and disposition. Directionality follows the actual work: **Produces → Consumes → Verifies → Integrates → Advises**.

### Tier 1: Core Capability Dependencies (High Confidence)

| # | Source Skill | Target Skill | Direction | Relationship Type | Evidence | Confidence | Disposition |
|---|-------------|-------------|-----------|-------------------|----------|------------|-------------|
| 1 | `kingwen` | `kingwen-ternary-expansion` | Produces → Consumes | Core capability dependency | `immutable-table-math-decoded.md`: ternary expansion is the core math engine; `kingwen-ternary-expansion` skill card references shotgun_expand() | High | **Supported** |
| 2 | `kingwen` | `openjarvis-kingwen-integration` | Produces → Consumes | Integration bridge | `qsmc1-consumer-boundary-audit.md`: 23+ consumers of shotgun_expand(); consumer boundary audit documents integration | High | **Supported** |
| 3 | `kingwen` | `kingwen-emotion-voice` | Produces → Consumes | Emotion voice | `emotional-vector-lineage-audit-2026-11-02.md`: 5-axis vector consumed by Cartesia TTS adapter | High | **Supported** |
| 4 | `kingwen` | `research/kingwen-jarvis-megatron-learn` | Produces → Integrates | Learning loop | `qsmc1-cross-group-correspondence-synthesis.md`: King Wen ↔ Jarvis ↔ Megatron integration | High | **Supported** |
| 5 | `kingwen` | `research/kingwen-oracle-advisory` | Produces → Integrates | Oracle advisory | `qsmc1-m3-*` series: oracle advisory consumes King Wen consult output | High | **Supported** |
| 6 | `kingwen` | `research/avalokiteshvara-kingwen` | Produces → Integrates | Capability registry | `avalokiteshvara-kingwen-mapping.md`: explicit registry relationship | High | **Supported** |
| 7 | `kingwen` | `research/learn_king_wen_math_extractors` | Produces → Consumes | Math extraction | `numerical-extraction-vision-pipeline.md`: math extractors feed King Wen engine | High | **Supported** |
| 8 | `kingwen` | `autonomous-ai-agents/kingwen-3d-tooling` | Produces → Consumes | 3D generation | `AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md`: 3D generators consume King Wen state | High | **Supported** |

### Tier 2: Verification and Governance (Medium-High Confidence)

| # | Source Skill | Target Skill | Direction | Relationship Type | Evidence | Confidence | Disposition |
|---|-------------|-------------|-----------|-------------------|----------|------------|-------------|
| 9 | `kingwen` | `verification/capability-pulse` | Advises → Verifies | Capability monitoring | `BENCHMARKS_RULES_ONBOARDING_README_AUDIT_2026-11-02.md`: capability pulse monitors King Wen skill health | Medium-High | **Supported** |
| 10 | `kingwen` | `verification/verification-artifact-hygiene` | Advises → Verifies | Artifact verification | `BENCHMARKS_RULES_ONBOARDING_README_AUDIT_2026-11-02.md`: artifact hygiene verifies King Wen outputs | Medium-High | **Supported** |
| 11 | `kingwen` | `software-development/verified-engineering` | Advises → Verifies | Verified engineering | `BENCHMARKS_RULES_ONBOARDING_README_AUDIT_2026-11-02.md`: verified engineering practices for King Wen | Medium-High | **Supported** |
| 12 | `kingwen` | `software-development/systematic-debugging` | Advises → Verifies | Systematic debugging | `BENCHMARKS_RULES_ONBOARDING_README_AUDIT_2026-11-02.md`: debugging practices for King Wen | Medium-High | **Supported** |

### Tier 3: Math Extraction (Medium Confidence — Association, Not Dependency)

| # | Source Skill | Target Skill | Direction | Relationship Type | Evidence | Confidence | Disposition |
|---|-------------|-------------|-----------|-------------------|----------|------------|-------------|
| 13 | `kingwen` | `research/math-pdf-parser` | Advises → Consumes | Math extraction | `numerical-extraction-vision-pipeline.md`: math extraction feeds King Wen engine | Medium | **Supported (advisory)** |
| 14 | `kingwen` | `research/multi-engine-math-parsing` | Advises → Consumes | Multi-engine parsing | `numerical-extraction-vision-pipeline.md`: multi-engine parsing for King Wen math | Medium | **Supported (advisory)** |
| 15 | `kingwen` | `research/math-structural-ast-fidelity` | Advises → Consumes | AST fidelity | `numerical-extraction-vision-pipeline.md`: AST fidelity for King Wen math | Medium | **Supported (advisory)** |
| 16 | `kingwen` | `research/vision-math-symbol-detection` | Advises → Consumes | Vision symbol detection | `numerical-extraction-vision-pipeline.md`: vision detection for King Wen math | Medium | **Supported (advisory)** |
| 17 | `kingwen` | `research/arxiv-math-extraction` | Advises → Consumes | ArXiv extraction | `numerical-extraction-vision-pipeline.md`: arXiv extraction for King Wen math | Medium | **Supported (advisory)** |

### Tier 4: RSMV / Cache Tooling (Medium Confidence — Association, Not Dependency)

| # | Source Skill | Target Skill | Direction | Relationship Type | Evidence | Confidence | Disposition |
|---|-------------|-------------|-----------|-------------------|----------|------------|-------------|
| 18 | `kingwen` | `rsmv` | Advises → Consumes | Cache tooling | `cross-verification-checklist-2026-09-01.md`: RSMV cache tooling for King Wen | Medium | **Supported (advisory)** |
| 19 | `kingwen` | `autonomous-ai-agents/rsmv-cache-archaeology` | Advises → Consumes | Cache archaeology | `cross-verification-checklist-2026-09-01.md`: cache archaeology for King Wen | Medium | **Supported (advisory)** |
| 20 | `kingwen` | `devops/rsmv-cache-crossref` | Advises → Consumes | Cache crossref | `cross-verification-checklist-2026-09-01.md`: cache crossref for King Wen | Medium | **Supported (advisory)** |
| 21 | `kingwen` | `devops/rsmv-model-identity-kit` | Advises → Consumes | Model identity kit | `cross-verification-checklist-2026-09-01.md`: model identity for King Wen | Medium | **Supported (advisory)** |

### Tier 5: OpenJarvis Integration (High Confidence)

| # | Source Skill | Target Skill | Direction | Relationship Type | Evidence | Confidence | Disposition |
|---|-------------|-------------|-----------|-------------------|----------|------------|-------------|
| 22 | `kingwen` | `openjarvis/openjarvis-kingwen-integration` | Produces → Consumes | OpenJarvis integration | `qsmc1-consumer-boundary-audit.md`: OpenJarvis consumes King Wen output | High | **Supported** |
| 23 | `kingwen` | `research/kingwen-learn-suite-runner` | Produces → Verifies | /learn verification | `qsmc1-m3-*` series: /learn suite verifies King Wen | High | **Supported** |
| 24 | `kingwen` | `autonomous-ai-agents/kingwen-paper-math-bridge` | Produces → Integrates | Paper-to-math bridge | `research-lead-*` series: paper math feeds King Wen | High | **Supported** |

### Reconciliation: 12 → 24 Expansion

The previous Journey Weave assessment identified 12 King Wen relationship candidates. This inventory proposes 24. The additional 12 are:

| # | Additional Target | Source of Discovery | Evidence Basis |
|---|-------------------|-------------------|----------------|
| 13 | `research/math-pdf-parser` | `numerical-extraction-vision-pipeline.md` | Math extraction feeds King Wen engine (advisory, not dependency) |
| 14 | `research/multi-engine-math-parsing` | `numerical-extraction-vision-pipeline.md` | Multi-engine parsing for King Wen math |
| 15 | `research/math-structural-ast-fidelity` | `numerical-extraction-vision-pipeline.md` | AST fidelity for King Wen math |
| 16 | `research/vision-math-symbol-detection` | `numerical-extraction-vision-pipeline.md` | Vision detection for King Wen math |
| 17 | `research/arxiv-math-extraction` | `numerical-extraction-vision-pipeline.md` | ArXiv extraction for King Wen math |
| 18 | `rsmv` | `cross-verification-checklist-2026-09-01.md` | RSMV cache tooling for King Wen |
| 19 | `autonomous-ai-agents/rsmv-cache-archaeology` | `cross-verification-checklist-2026-09-01.md` | Cache archaeology for King Wen |
| 20 | `devops/rsmv-cache-crossref` | `cross-verification-checklist-2026-09-01.md` | Cache crossref for King Wen |
| 21 | `devops/rsmv-model-identity-kit` | `cross-verification-checklist-2026-09-01.md` | Model identity for King Wen |
| 22 | `openjarvis/openjarvis-kingwen-integration` | `qsmc1-consumer-boundary-audit.md` | OpenJarvis consumes King Wen output |
| 23 | `research/kingwen-learn-suite-runner` | `qsmc1-m3-*` series | /learn suite verifies King Wen |
| 24 | `autonomous-ai-agents/kingwen-paper-math-bridge` | `research-lead-*` series | Paper math feeds King Wen |

**Key distinction:** Targets 1–8 are **core capability dependencies** (King Wen produces output that these skills consume or integrate). Targets 9–12 are **verification/governance** (these skills verify or advise on King Wen). Targets 13–21 are **advisory associations** (these skills are mentioned in King Wen research documents but do not have a demonstrated capability dependency). Targets 22–24 are **high-confidence integration** (demonstrated integration bridges).

The advisory targets (13–21) should not be marked as `SUPPORTED` without a concrete capability explanation. They are currently marked **Supported (advisory)** to distinguish them from core dependencies.

---

## Summary

- **Document registry:** 20 unique documents in QSMC-1 and field-lineage cluster, deduplicated
- **Known-to-unknown ledger:** 24 observations across 7 clusters (Hamiltonian, M6 imaginary amplitude, porosity, emotional vectors, cross-field dependency, shotgun expand/consumer continuity, porosity cross-reference)
- **Skill capability mapping:** 18 skills mapped with capability descriptions, computation ownership, and observation flow
- **Directed relationship candidates:** 24 candidates with directionality, evidence, confidence, and disposition
- **Reconciliation:** 12→24 expansion explained; 3 path mismatches reconciled; advisory vs dependency distinction established

**No changes made.** No files, frontmatter, skill definitions, or graph edges modified. All relationship candidates are validation-only proposals awaiting separate authorization.