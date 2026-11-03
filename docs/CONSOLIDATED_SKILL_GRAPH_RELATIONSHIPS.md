# Skill Graph / Relationship Semantics — Consolidated Domain Document

**Domain:** King Wen Journey Weave / Skill Graph Integrity / Relationship Semantics / Tier 1 Verification / Markdown Evidence
**Consolidated from:** 5 source documents (113,242 bytes total)
**Date:** 2026-11-03
**Status:** Step 1 (Archive filtering) COMPLETE; Tier 1 verification COMPLETE; Relationship semantics audit COMPLETE

---

## Source Document Index

| # | File | Bytes | Role |
|---|------|-------|------|
| 1 | docs/journey-weave-audit-2026-11-03.md | ~176 lines | Weave audit (241 skills, 155 edges, 49 missing targets, 141 orphans) |
| 2 | docs/markdown-evidence-to-skill-relationship-matrix.md | 30,633 | Read-only Markdown evidence inventory (166 files) |
| 3 | docs/markdown-evidence-validation-artifact-qsmc1-field-lineage.md | 31,319 | Validation artifact (20 docs, 24 observations, 18 skills, 24 candidates) |
| 4 | docs/tier1-relationship-verification-matrix.md | 19,293 | Tier 1 verification (7/8 supported, 1/8 inconclusive) |
| 5 | docs/relationship-semantics-and-directionality-audit.md | 17,784 | Relationship semantics audit (T1-07 reversed, schema assessment, vocabulary) |

---

## Weave Audit Results (2026-11-03)

### Baseline Metrics
- **Skills:** 241 (129 active + 110 archived + 2 discrepancy)
- **Edges:** 155
- **Missing targets:** 49 (26 unique)
- **Orphans:** 141 (78 active + 63 archived)
- **Clusters:** 42
- **Memory cards:** 951
- **Empty domains:** 3 (learned_abilities, code_agnostic, user_intents)

### Phantom References (24)
External tools not installed as skills: airtable, ascii-video, audiocraft, browser, claude-code (×5), claude-design, cloudflare-capability-audit, dogfood, github-code-review (×3), grok, hermes-agent, hermes-agent-skill-authoring, image_gen, kanban-orchestrator, notion, openjarvis-save-string, pog2-local-build, powerpoint (×4), reddit-reading, rss-feeds, sovereign-state-agents, test-driven-development (×3), verified-engineering

### Path-Mismatched References (3, not 2)
1. `canonical-table-audit` → `verification/canonical-table-audit` (fixable)
2. `verification-rules` → `verification/verification-artifact-hygiene` (fixable)
3. `verified-engineering` → `software-development/verified-engineering` (fixable)

### King Wen Skills (Highest Priority Orphans)
kingwen, megatron, openjarvis, openjarvis/openjarvis-kingwen-integration, research/kingwen-jarvis-megatron-learn, research/kingwen-oracle-advisory, research/kingwen-learn-suite-runner, research/avalokiteshvara-kingwen, research/learn_king_wen_math_extractors, autonomous-ai-agents/kingwen-3d-tooling, autonomous-ai-agents/kingwen-paper-math-bridge, autonomous-ai-agents/kingwen-emotion-voice

---

## Step 1: Archive Filtering (COMPLETE)

### Filtering Rule
A skill is "archived" if any path component of its SKILL.md relative path contains `.archive`. No archive/status frontmatter keys exist in any SKILL.md.

### Counts
- Active skills: 129
- Archived skills: 110
- Total: 239 (2-skill discrepancy with weave audit's 241)

### Key Finding: False Relationship Resolution
32 active-skill declarations resolved only to archived skills via `stem_lookup` (directory-name-based matching). When archived skills were removed, these edges became dangling missing targets. This exposed edges that appeared valid only because they pointed to archived skills.

### Three Populations (Overlap, NOT One-to-One)
1. **86 original archived-target resolutions** — edges in original 150-edge graph attributed to archived targets
2. **32 captured active-skill provenance records** — specific active-skill declarations resolving to archived skills via stem_lookup (DATASETS/resolution_provenance_step1.json)
3. **64 active-only unresolved targets** — all phantom references in active graph (includes 32 formerly-resolved archived targets + 32 independently unresolved)

### Original Baseline Preserved
- `journey_web_alignment_report_2026-07-11.json` and `journey_web_alignment_weave_2026-07-11.json` restored via git checkout; no diff confirmed

### Active-Only Artifacts
- `journey_web_alignment_report_active_2026-11-03.json` (131 active skills, 64 edges)
- `journey_web_alignment_weave_active_2026-11-03.json`

---

## Markdown Evidence → Skill Relationship Inventory

### Git State (Reconciled)
- 18 modified tracked files (8 Python source + 7 data + 3 config/docs)
- 98 untracked files (63 docs/*.md + 20+ DATASETS + 10+ scripts + 3 weave artifacts + 1 cache script + journey_weave_active.py + check_reclassified.py + resolution_provenance_step1.py + resolution_provenance_step1.json)
- 0 staged changes
- 0 local commits ahead of origin
- HEAD == @{u} == 71fbf28f8e92c6a7de74c50a304906ef81963a7d

### Three Populations of Markdown Files
1. **Population A (1 file):** Modified tracked — README.md
2. **Population B (63 files):** Newly created untracked docs/*.md
3. **Population C (102 files):** Unmodified historical tracked .md

### 24 Candidate related_skills Relationships for kingwen
Proposed but NOT created. Classified into 5 tiers.

---

## Tier 1 Relationship Verification (7/8 Supported, 1/8 Inconclusive)

### Schema Assessment
`related_skills` is **undirected association only** — flat YAML string array, no type, direction, evidence, advisory/dependency distinction, archived/active status, reciprocal tracking, or confidence. Cannot faithfully represent 24 directed relationships. Recommend typed relationship store or frontmatter extension before creating any relationships.

### Results
| ID | Source | Target | Type | Direction | Status | Confidence |
|----|--------|--------|------|-----------|--------|------------|
| T1-01 | kingwen | kingwen-ternary-expansion | Produces | kingwen → ternary | Supported | High |
| T1-02 | kingwen | openjarvis-kingwen-integration | Produces | kingwen → OpenJarvis | Supported | High |
| T1-03 | kingwen | kingwen-emotion-voice | Produces | kingwen → Cartesia TTS | Supported | High |
| T1-04 | kingwen | kingwen-jarvis-megatron-learn | Produces | kingwen → training corpora | Supported | High |
| T1-05 | kingwen | kingwen-oracle-advisory | Produces | kingwen → advisory wrapping | Supported | High |
| T1-06 | kingwen | avalokiteshvara-kingwen | Produces | kingwen → multi-arm routing | Supported | High |
| T1-07 | kingwen | learn_king_wen_math_extractors | — | May be reversed | Inconclusive | — |
| T1-08 | kingwen | kingwen-3d-tooling | Produces | kingwen → 3D generation | Supported | High |

### Pilot Chain Verified
Computation ownership → ternary specialization → OpenJarvis integration → verification

### T1-07 Specific Gap
`learn_king_wen_math_extractors` does NOT declare `kingwen` in its `related_skills` frontmatter. Its declared targets are: `research/pdf-learning-corpus`, `research/math-pdf-parser`, `research/arxiv-math-extraction`. Direction may be reversed: math extractors produce FOR King Wen, not vice versa. Missing reciprocal declaration is a separate observation, not proof of invalidity.

---

## Relationship Semantics and Directionality Audit

### T1-07 Resolution: Direction Reversed (Confirmed)
- `learn_king_wen_math_extractors` **produces** math extraction output
- `kingwen` **consumes** it
- Math extraction scripts (`mathml_parser.py`, `math_recovery_tool.py`, `arxiv_html_parser.py`) produce `ExprNode`/`Integral` IR
- No bidirectional data flow found
- T1-07 marked **Unsupported** (wrong direction)
- New candidate T1-07c recorded with corrected direction: `learn_king_wen_math_extractors → kingwen`

### 5 Relationship Types Defined

| Type | Meaning |
|------|---------|
| Produces | Generates an output or capability |
| Consumes | Uses another capability's output |
| Integrates | Connects or embeds another capability |
| Verifies | Independently checks a result |
| Advises | Supplies guidance without execution dependency |

### Additional Classification Dimension: `relationship_class`
- `capability_dependency` — execution dependency (target cannot function without source output)
- `advisory_association` — guidance without execution dependency
- `verification_association` — independent check
- `integration_association` — connection/embedding

This prevents the relationship type from carrying two meanings simultaneously.

### Vocabulary Test Results (24+1 candidates across 5 tiers)

| Tier | Description | Count | Results |
|------|-------------|-------|---------|
| 1 | Core capability dependencies | 8 | 7 supported + 1 inconclusive (T1-07c) + 1 unsupported (T1-07 original) |
| 2 | Verification/governance | 4 | 4 supported |
| 3 | Math extraction (advisory) | 5 | 5 supported (advisory) |
| 4 | RSMV/cache tooling (advisory) | 4 | 4 supported (advisory) |
| 5 | OpenJarvis integration | 3 | 3 supported |
| **Total** | | **24+1** | **23 supported, 1 inconclusive, 1 unsupported** |

### 4 Missing Reciprocal Declarations
1. `learn_king_wen_math_extractors` — does not declare `kingwen`
2. `kingwen-3d-tooling` — path mismatch
3. `kingwen-ternary-expansion` — path mismatch
4. `kingwen-emotion-voice` — path mismatch

### Advisory vs Dependency Distinction
- Tiers 1-2: capability dependency (execution dependency)
- Tiers 3-4: advisory association (guidance without execution dependency)
- Tier 5: mixed (integration + verification)

### No Changes Made
All results are validation-only. No files, frontmatter, skill definitions, or graph edges modified.

---

## Registry Design Specification Requirements (from assessment)

### Four Additional Design Requirements (Authorized)

1. **Immutable relationship identity:** Once assigned, a relationship ID identifies that historical assertion. If direction or meaning changes, create a superseding record rather than silently rewriting the original.

2. **Separate validation from lifecycle:** `validation_status` and `lifecycle_status` as separate fields. A relationship can be `supported` while remaining `proposed`. Validation does not authorize implementation.

3. **Evidence provenance:** Every disposition identifies supporting evidence and distinguishes:
   - Direct implementation evidence
   - Declared skill capability
   - Observed data flow
   - Historical or documentary evidence
   - Inference

4. **Explicit unresolved states:** Missing evidence, missing reciprocal declarations, archived targets, and unsupported relationships must not be represented by the same null or Boolean value.

### Acceptance Test (25-Record)

| Population | Count | Required Behavior |
|------------|-------|-------------------|
| Supported | 23 | Retain supported evidence and classification |
| Inconclusive | 1 | Preserve uncertainty without promotion |
| Unsupported | 1 | Preserve original direction and rejection history |

T1-07 and T1-07c must remain separate records.

### Five Questions for Registry Specification

1. What is the canonical identity of a relationship?
2. Are relationships stored once as directed records, or declared independently by both skills?
3. How are capability dependency and advisory association distinguished?
4. How are evidence, confidence, and validation status preserved?
5. How are archived targets and historical relationships represented without contaminating the active graph?

### Acceptance Criterion

The registry must represent the existing evidence without:
- Inventing reciprocal edges
- Losing direction
- Promoting advisory associations to dependencies

### Governance Boundary

Specification authorized as described. Work remains documentation-only:
- No frontmatter modifications
- No relationship creation
- No graph regeneration
- No source changes
- No commits or staging
- No implementation acceptance

A registry specification is not yet a registry implementation. Passing all 25 candidate records demonstrates that the proposed model can represent the evidence. It does not establish that the model is ready for production.

### Final Section: Traceability Table

The specification's final section must be a traceability table mapping every candidate to its proposed registry representation and recording any information that cannot yet be represented.

---

## Machine-Readable Summary

```json
{
  "domain": "skill_graph_relationship_semantics",
  "status": "step1_complete_tier1_verified_semantics_audited",
  "weave": {
    "skills": 241,
    "edges": 155,
    "missing_targets": 49,
    "orphans": 141,
    "clusters": 42,
    "memory_cards": 951,
    "empty_domains": 3
  },
  "step1": {
    "active_skills": 129,
    "archived_skills": 110,
    "false_resolutions": 32,
    "original_baseline_preserved": true
  },
  "tier1": {
    "supported": 7,
    "inconclusive": 1,
    "unsupported": 0,
    "schema": "undirected_association_only"
  },
  "semantics_audit": {
    "supported": 23,
    "inconclusive": 1,
    "unsupported": 1,
    "relationship_types": ["Produces", "Consumes", "Integrates", "Verifies", "Advises"],
    "relationship_classes": ["capability_dependency", "advisory_association", "verification_association", "integration_association"],
    "missing_reciprocals": 4
  },
  "registry_design": {
    "status": "authorized_specification_pending",
    "requirements": 9,
    "acceptance_test": "25_records",
    "governance": "documentation_only"
  },
  "frozen": ["original_weave_baseline", "step1_provenance", "tier1_matrix", "semantics_audit"]
}
```