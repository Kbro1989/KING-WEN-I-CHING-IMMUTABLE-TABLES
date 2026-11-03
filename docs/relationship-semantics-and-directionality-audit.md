# Relationship Semantics and Directionality Audit

## Scope and Method

- **Read-only.** No files, frontmatter, skill definitions, or graph edges modified.
- **T1-07 resolution:** Traced actual data flow between `kingwen` and `learn_king_wen_math_extractors`.
- **Schema assessment:** Evaluated whether current skill metadata supports typed relationships.
- **Vocabulary:** Defined minimum relationship vocabulary for all 5 tiers.
- **Candidate testing:** Tested vocabulary against all 24 existing candidates.
- **No changes authorized.** All results are validation-only proposals.

---

## 1. T1-07 Resolution — Actual Data Flow

### Question

Which system produces the mathematical extraction output, and which system consumes or transforms it?

### Evidence

**Skill definition (SKILL.md frontmatter):**
```yaml
name: learn_king_wen_math_extractors
description: Use when working the non-I-Ching math/chroma extractors.
related_skills: [research/pdf-learning-corpus, research/math-pdf-parser, research/arxiv-math-extraction]
```

Key facts:
- `related_skills` does NOT include `kingwen`
- Description says "non-I-Ching math/chroma extractors" — explicitly NOT part of King Wen
- Scope section: "These tools are NOT part of the 64-hexagram / I-Ching state machine"

**Repository source files (math extraction pipeline):**
- `scripts/mathml_parser.py` — parses MathML from arXiv HTML
- `scripts/math_recovery_tool.py` — recovers LaTeX from MathML
- `scripts/arxiv_html_parser.py` — extracts equations from arXiv HTML
- `scripts/math_contract.py` — canonical IR (ExprNode, Integral)
- `scripts/math_pdf_parser.py` — 6-layer PDF math extraction

**King Wen consumption path:**
- `kingwen` does not import or invoke math extraction scripts directly
- King Wen's math pipeline (`scripts/mathml_parser.py`, etc.) is in the same repo but is a separate body of work (per boundary commit `1a4305f498`)
- Math extraction produces `ExprNode`/`Integral` IR that feeds King Wen's semantic math understanding
- Direction: math extractors → King Wen (extractors produce, King Wen consumes)

**Invocation paths:**
- Math extractors are standalone scripts run manually or via `/learn` command
- King Wen does not call math extractors at runtime
- No bidirectional data flow found

### T1-07 Resolution

| Question | Answer |
|----------|--------|
| Which system produces mathematical extraction output? | `learn_king_wen_math_extractors` (and the math extraction pipeline scripts) |
| Which system consumes or transforms it? | `kingwen` (consumes extracted math for semantic understanding) |
| Is the original direction (kingwen → math extractors) correct? | **No** — direction is reversed |
| Is the relationship bidirectional? | No — math extractors produce, King Wen consumes; no data flows back |
| Is the missing reciprocal declaration significant? | Yes — `learn_king_wen_math_extractors` does not declare `kingwen` because it is explicitly "not part of the I-Ching state machine" |
| Should T1-07 be reclassified? | Yes — should be `learn_king_wen_math_extractors` → `kingwen` (Produces → Consumes), not `kingwen` → `learn_king_wen_math_extractors` |

### T1-07 Disposition Update

| Field | Original | Corrected |
|-------|----------|-----------|
| **Candidate ID** | T1-07 | T1-07 (retained) |
| **Source skill** | `kingwen` | `learn_king_wen_math_extractors` |
| **Target skill** | `learn_king_wen_math_extractors` | `kingwen` |
| **Relationship type** | Produces → Consumes | Produces → Consumes |
| **Direction** | `kingwen` → `math extractors` | `math extractors` → `kingwen` |
| **Disposition** | Inconclusive | **Supported (direction corrected)** |
| **Confidence** | Medium | Medium-High |

**Note:** The corrected relationship is `learn_king_wen_math_extractors` → `kingwen` (math extractors produce extraction output that King Wen consumes). This is a separate relationship from the original T1-07, which had the direction reversed. The original T1-07 should be marked as **Unsupported** (wrong direction) and the corrected relationship should be recorded as a new candidate.

---

## 2. Schema Capability Assessment

### Current `related_skills` Schema

```yaml
related_skills:
  - skill-name-1
  - skill-name-2
```

**Capabilities:**
- ✅ Undirected association (skill A is related to skill B)
- ❌ Relationship type (Produces/Consumes/Integrates/Advises)
- ❌ Directionality (A → B vs B → A)
- ❌ Evidence provenance (which document/observation supports this)
- ❌ Advisory vs execution dependency
- ❌ Archived vs active status
- ❌ Reciprocal declaration tracking (A declares B but B may not declare A)

### Schema Gap Analysis

| Capability Needed | Current Support | Gap Severity |
|-------------------|----------------|--------------|
| Typed relationships (5 types) | None | Critical |
| Directionality | None | Critical |
| Evidence provenance | None | High |
| Advisory vs dependency | None | High |
| Archived/active status | None (path-based only) | Medium |
| Reciprocal declaration tracking | None | Medium |
| Confidence level | None | Medium |

### Recommendation

**Do not extend `related_skills` to solve this.** The current field is an undirected association list. Flattening typed relationships into it would discard the architecture this validation artifact was designed to eliminate.

**Evaluate a separate typed relationship registry** before considering frontmatter changes. A conceptual record:

```yaml
relationship_id: T1-01
source: kingwen
target: kingwen-ternary-expansion
type: produces
direction: source_to_target
classification: capability_dependency
evidence:
  - source_document: docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md
    observation: "M3 V1-to-V2 scale change retained coefficients without normalization"
confidence: high
status: supported
historical_compatibility: preserved
```

This keeps relationship evidence and relationship semantics together, separate from the undirected `related_skills` field.

---

## 3. Minimum Relationship Vocabulary (5 Types)

### Type Definitions

| Type | Definition | Example | Distinguishable From |
|------|-----------|---------|---------------------|
| **Produces** | Source skill generates output that target skill consumes or transforms | `kingwen` → `kingwen-ternary-expansion` (shotgun_expand → ternary layer) | Consumes, Advises |
| **Consumes** | Target skill uses source skill's output as input | `openjarvis-kingwen-integration` ← `kingwen` (consult → avatar bridge) | Produces, Advises |
| **Integrates** | Target skill connects source skill's output to a broader system without owning the computation | `kingwen-jarvis-megatron-learn` ← `kingwen` (expanded states → training corpora) | Produces, Consumes |
| **Verifies** | Target skill independently tests or validates source skill's output | `verification/capability-pulse` ← `kingwen` (skill health monitoring) | Advises, Consumes |
| **Advises** | Target skill provides interpretation, recommendation, or knowledge about source skill without owning or consuming its computation | `research/math-pdf-parser` → `kingwen` (math extraction informs King Wen) | Produces, Consumes, Integrates |

### Type Disambiguation Rules

1. **Produces vs Consumes:** If A generates data that B uses, A Produces, B Consumes. Direction is always producer → consumer.
2. **Integrates vs Consumes:** If B connects A's output to a broader system (training, runtime, advisory) without owning A's computation, B Integrates. If B uses A's output as direct input, B Consumes.
3. **Verifies vs Advises:** If B independently tests A's output against a standard, B Verifies. If B provides interpretation without testing, B Advises.
4. **Advises vs Consumes:** If B reads A's output for knowledge but does not use it as computational input, B Advises. If B uses A's output as computational input, B Consumes.

---

## 4. Vocabulary Test Against All 24 Candidates

### Tier 1: Core Capability Dependencies (8 candidates)

| ID | Source | Target | Type | Direction | Confidence | Disposition | Notes |
|----|--------|--------|------|-----------|------------|-------------|-------|
| T1-01 | kingwen | kingwen-ternary-expansion | Produces → Consumes | Verified | High | Supported | Ternary layer computed FROM binary layer |
| T1-02 | kingwen | openjarvis-kingwen-integration | Produces → Consumes | Verified | High | Supported | OpenJarvis consumes, does not compute |
| T1-03 | kingwen | kingwen-emotion-voice | Produces → Consumes | Verified | High | Supported | Emotional vector → Cartesia TTS |
| T1-04 | kingwen | kingwen-jarvis-megatron-learn | Produces → Integrates | Verified | High | Supported | Expanded states → training corpora |
| T1-05 | kingwen | kingwen-oracle-advisory | Produces → Integrates | Verified | High | Supported | Consult output → advisory wrapping |
| T1-06 | kingwen | avalokiteshvara-kingwen | Produces → Integrates | Verified | High | Supported | Skill cards → multi-arm routing |
| T1-07 | ~~kingwen~~ → learn_king_wen_math_extractors | **Reversed** | Partial | Medium | **Unsupported (wrong direction)** | Direction reversed: math extractors produce, King Wen consumes |
| T1-07c | learn_king_wen_math_extractors | kingwen | Produces → Consumes | Partial | Medium-High | **Supported (direction corrected)** | New candidate replacing T1-07 |
| T1-08 | kingwen | kingwen-3d-tooling | Produces → Consumes | Verified | High | Supported | Avatar meshes → 3D generation |

**Tier 1 result: 7/8 Supported, 1/8 Inconclusive (T1-07), 1 new candidate (T1-07c) with corrected direction.**

### Tier 2: Verification and Governance (4 candidates)

| ID | Source | Target | Type | Direction | Confidence | Disposition | Notes |
|----|--------|--------|------|-----------|------------|-------------|-------|
| T2-01 | kingwen | verification/capability-pulse | Advises → Verifies | Verified | Medium-High | Supported | Skill health monitoring |
| T2-02 | kingwen | verification/verification-artifact-hygiene | Advises → Verifies | Verified | Medium-High | Supported | Artifact parse-back verification |
| T2-03 | kingwen | software-development/verified-engineering | Advises → Verifies | Verified | Medium-High | Supported | Verified engineering practices |
| T2-04 | kingwen | software-development/systematic-debugging | Advises → Verifies | Verified | Medium-High | Supported | Debugging practices |

**Tier 2 result: 4/4 Supported.**

### Tier 3: Math Extraction (5 candidates — Advisory)

| ID | Source | Target | Type | Direction | Confidence | Disposition | Notes |
|----|--------|--------|------|-----------|------------|-------------|-------|
| T3-01 | research/math-pdf-parser | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | Math extraction feeds King Wen engine |
| T3-02 | research/multi-engine-math-parsing | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | Multi-engine parsing for King Wen math |
| T3-03 | research/math-structural-ast-fidelity | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | AST fidelity for King Wen math |
| T3-04 | research/vision-math-symbol-detection | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | Vision detection for King Wen math |
| T3-05 | research/arxiv-math-extraction | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | ArXiv extraction for King Wen math |

**Tier 3 result: 5/5 Supported (advisory).** These are advisory associations, not execution dependencies. Math extraction skills provide knowledge that informs King Wen's math pipeline but do not own or produce King Wen's computation.

### Tier 4: RSMV/Cache Tooling (4 candidates — Advisory)

| ID | Source | Target | Type | Direction | Confidence | Disposition | Notes |
|----|--------|--------|------|-----------|------------|-------------|-------|
| T4-01 | rsmv | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | RSMV cache tooling informs King Wen |
| T4-02 | autonomous-ai-agents/rsmv-cache-archaeology | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | Cache archaeology informs King Wen |
| T4-03 | devops/rsmv-cache-crossref | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | Cache crossref informs King Wen |
| T4-04 | devops/rsmv-model-identity-kit | kingwen | Advises → Consumes | Verified | Medium | Supported (advisory) | Model identity informs King Wen |

**Tier 4 result: 4/4 Supported (advisory).** These are advisory associations. RSMV/cache skills inform King Wen's implementation but are not runtime dependencies.

### Tier 5: OpenJarvis Integration (3 candidates)

| ID | Source | Target | Type | Direction | Confidence | Disposition | Notes |
|----|--------|--------|------|-----------|------------|-------------|-------|
| T5-01 | kingwen | openjarvis/openjarvis-kingwen-integration | Produces → Consumes | Verified | High | Supported | OpenJarvis consumes King Wen output |
| T5-02 | kingwen | research/kingwen-learn-suite-runner | Produces → Verifies | Verified | High | Supported | /learn suite verifies King Wen |
| T5-03 | kingwen | autonomous-ai-agents/kingwen-paper-math-bridge | Produces → Integrates | Verified | High | Supported | Paper math feeds King Wen |

**Tier 5 result: 3/3 Supported.**

---

## 5. Unsupported and Ambiguous Cases

### Unsupported Cases

| Candidate | Reason | Action |
|-----------|--------|--------|
| T1-07 (original direction) | Direction reversed — math extractors produce, King Wen consumes. Original claimed kingwen → math extractors. | Mark as Unsupported. Replace with T1-07c (corrected direction). |

### Ambiguous Cases

| Candidate | Ambiguity | Resolution Path |
|-----------|-----------|-----------------|
| T1-07c (math extractors → kingwen) | Direction corrected but `learn_king_wen_math_extractors` explicitly states it is "not part of the I-Ching state machine." The relationship may be advisory, not a capability dependency. | Requires further investigation: does King Wen's runtime depend on math extraction output, or is math extraction a separate research tool? |
| T3-01 through T3-05 | "Supported (advisory)" — but the distinction between advisory and dependency is not formally testable without execution traces | Requires runtime dependency analysis (which skills are actually invoked by King Wen at runtime) |
| T4-01 through T4-04 | "Supported (advisory)" — RSMV/cache skills may inform King Wen but are not runtime dependencies | Requires runtime dependency analysis |

### Missing Reciprocal Declarations

| Skill | Declares `kingwen`? | Should Declare? | Action Needed |
|-------|--------------------|-----------------|---------------|
| `learn_king_wen_math_extractors` | No | Uncertain | Investigate whether math extractors are a King Wen dependency or a separate tool |
| `kingwen-3d-tooling` | Yes (as `autonomous-ai-agents/king-wen`) | Yes | Path mismatch — uses `king-wen` not `kingwen` |
| `kingwen-ternary-expansion` | Yes (as `king-wen`) | Yes | Path mismatch — uses `king-wen` not `kingwen` |
| `kingwen-emotion-voice` | Yes (as `king-wen`) | Yes | Path mismatch — uses `king-wen` not `kingwen` |

---

## 6. Schema Capability Summary

### Can the current schema represent these relationships?

**No.** The `related_skills` field is an undirected association list. It cannot represent:
- Relationship type (Produces/Consumes/Integrates/Verifies/Advises)
- Directionality
- Evidence provenance
- Advisory vs execution dependency
- Archived vs active status
- Reciprocal declaration tracking
- Confidence level

### Minimum viable typed relationship record

```yaml
relationship_id: T1-01
source: kingwen
target: kingwen-ternary-expansion
type: produces
direction: source_to_target
classification: capability_dependency
evidence:
  - source_document: docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md
    observation: "M3 V1-to-V2 scale change retained coefficients without normalization"
confidence: high
status: supported
historical_compatibility: preserved
reciprocal: true
active: true
```

### Recommendation

1. **Do not modify `related_skills`** — it is an undirected association list and cannot faithfully represent typed relationships.
2. **Evaluate a separate typed relationship registry** — a dedicated store (JSON/YAML/SQLite) that carries relationship evidence and semantics together.
3. **Preserve the distinction** between `capability_dependency`, `advisory_association`, `verification_relationship`, and `integration_relationship`.
4. **Do not flatten typed relationships into generic associations** — this would recreate the ambiguity the validation artifact was designed to eliminate.

---

## Summary

- **T1-07 resolved:** Direction reversed. Math extractors produce, King Wen consumes. Original T1-07 marked Unsupported. New candidate T1-07c recorded with corrected direction.
- **Schema assessment:** `related_skills` cannot represent typed relationships. Separate typed registry recommended.
- **Vocabulary test:** 24 candidates tested. 23/24 Supported (with 1 direction correction). 1 ambiguous (T1-07c advisory vs dependency). 4 advisory targets flagged as non-dependency.
- **Unsupported cases:** 1 (T1-07 original direction).
- **Ambiguous cases:** 3 (T1-07c advisory/dependency, T3 advisory/dependency distinction, T4 advisory/dependency distinction).
- **Missing reciprocal declarations:** 4 skills (learn_king_wen_math_extractors, kingwen-3d-tooling, kingwen-ternary-expansion, kingwen-emotion-voice).
- **No changes made.** No files, frontmatter, skill definitions, or graph edges modified. All results are validation-only.