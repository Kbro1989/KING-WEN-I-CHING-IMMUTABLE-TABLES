# Rule Verification Gate (RVG) — Governance Addition to Controlled Remediation Protocol

## Scope

This document is a separately versioned governance addition to the controlled remediation verification protocol. It does not modify source code, the unknowns register, the evidence freeze, or the remediation matrix. It introduces a mandatory verification stage that must be satisfied before any controlled resolution begins and again before any resolution is accepted.

**Date**: 2026-11-03
**Repository**: KING-WEN-I-CHING-IMMUTABLE-TABLES
**Baseline commit**: `71fbf28f8e92c6a7de74c50a304906ef81963a7d`
**Parent protocol**: `docs/controlled-remediation-verification-protocol.md`

## 1. Rationale

A rule that exists only in documentation is advisory. A rule that is checked against actual outputs, consumers, and regression evidence becomes an enforceable engineering constraint.

The discovery phase identified that agents repeatedly violated architectural rules (non-collapse, per-hexagram identity, full expansion before selection, derive-as-well-as-not-instead-of) because compliance was never verified as part of execution and acceptance. The rules were available to read but were never demonstrated to have been read, understood, or obeyed.

RVG addresses this gap by making rule compliance a mandatory, evidence-producing stage with two gates: pre-execution and post-execution.

## 2. Controlled Resolution Lifecycle (6 Stages)

| Stage | Name | Description |
|---|---|---|
| 1 | Target authorization | Identify exact unknown or remediation entry, scope, and affected consumers |
| 2 | Rule verification | Identify and read applicable governing rules, immutable tables, architecture documents, historical usage evidence, and current implementation state |
| 3 | Pre-change evidence | Demonstrate current behavior, including preserved ranges, identities, representations, and consumer outputs |
| 4 | Controlled resolution | Make only the explicitly authorized change; preserve unrelated behavior and capabilities |
| 5 | Regression verification | Test original behavior, affected consumers, architectural invariants, and newly introduced behavior |
| 6 | Acceptance review | Independently verify rule compliance, representation continuity, provenance, and acceptance criteria |

## 3. Pre-Execution Gate (Gate 1)

No implementation begins until applicable rules and current-state evidence are verified.

### 3.1 Required evidence

The resolving agent must demonstrate five things:

| Requirement | Evidence |
|---|---|
| Rule discovery | Relevant rule documents identified (exact paths) |
| Rule comprehension | Applicable constraints summarized accurately (not "I read AGENTS.md") |
| Current-state inspection | Actual implementation and consumers inspected (file paths, line numbers, observed behavior) |
| Constraint preservation | Before/after behavior comparison plan documented |
| Acceptance compliance | Tests and evidence satisfy the authorized criteria |

### 3.2 Governing documents (minimum set)

The resolving agent must identify and read at least:

- `CLAUDE.md` (operating principles, no-mock policy, precision over speed)
- `docs/remediation-verification-matrix.md` (authoritative source for F-01 through F-08)
- `docs/unknowns-register-2026-11-02.md` (unresolved definitions and semantics)
- `docs/pre-remediation-evidence-freeze-2026-11-02.md` (repository and investigation state)
- The specific source files identified as in scope for the target
- The specific audit reports referenced by the target's finding

### 3.3 Pre-execution gate status

Possible values: `NOT_REVIEWED`, `RULES_IDENTIFIED`, `RULES_VERIFIED`, `BLOCKED`

- `NOT_REVIEWED`: No rule verification attempted
- `RULES_IDENTIFIED`: Relevant documents found but comprehension not yet demonstrated
- `RULES_VERIFIED`: Agent has demonstrated understanding of applicable constraints and current state
- `BLOCKED`: Rule verification cannot proceed (missing documents, inaccessible code, etc.)

`RULES_VERIFIED` does NOT mean the implementation is authorized. It means the agent has demonstrated that it understands the applicable constraints.

## 4. Post-Execution Gate (Gate 2)

No resolution is accepted until independent verification demonstrates that the rules remain satisfied.

### 4.1 Rule-compliance record

Each resolution must produce a rule-compliance record (separate from the unknowns register and remediation matrix):

```
resolution_id
authorized_target
authorization_scope
governing_documents[]
governing_rules[]
current_state_inspected[]
affected_consumers[]
historical_behaviors[]
pre_change_evidence[]
proposed_change
preserved_invariants[]
regression_tests[]
post_change_evidence[]
acceptance_criteria[]
rule_compliance_status
acceptance_status
reviewer
```

### 4.2 Status values

| Status | Meaning |
|---|---|
| `NOT_REVIEWED` | No review attempted |
| `RULES_IDENTIFIED` | Relevant rules found, comprehension not demonstrated |
| `RULES_VERIFIED` | Agent demonstrated understanding of applicable constraints |
| `BLOCKED` | Verification cannot proceed |
| `INCONCLUSIVE` | Verification attempted but evidence insufficient |
| `ACCEPTED` | Independent verification confirms rule compliance and acceptance criteria met |

`RULES_VERIFIED` must not mean the implementation is accepted. It means the agent has demonstrated that it understands the applicable constraints.

### 4.3 Independent acceptance

Three responsibilities must be separated:

| Responsibility | Role | Function |
|---|---|---|
| Resolver | Investigates and performs authorized work | Makes the change |
| Verifier | Independently examines behavior and regression evidence | Confirms or denies rule compliance |
| Acceptance authority | Determines whether acceptance criteria are met | Grants or denies acceptance |

The resolver must not be the sole authority certifying its own work. Independent verification is required, even if performed by the same agent in a separate review pass.

## 5. Executable Architectural Constraints

The following constraints must be verified independently. Passing one does not compensate for violating another.

| Constraint | Required verification | Test type |
|---|---|---|
| Non-collapse | Preserve full numerical range, including negative and positive values | Numerical range check |
| Simultaneous identity | Preserve all 64 hexagram identities; no single-dominant substitution | Cardinality check (64) |
| Per-hexagram uniqueness | Verify individual outputs rather than assuming shared output is valid | Uniqueness check across 64 |
| Derive as well as, not instead of | Preserve existing derivations while adding downstream outputs | Before/after diff |
| Full expansion before selection | Verify complete expansion populations before filtering or projection | Population count check (512) |
| Emotional range preservation | Measure pooled output distributions rather than assuming their range | Distribution check |
| Historical compatibility | Verify previously working consumers and behaviors | Consumer regression test |
| Representation continuity | Preserve binary, ternary, positional, and persona distinctions | Cross-representation identity check |

### 5.1 Constraint-to-finding mapping

| Constraint | Related findings | Related unknowns |
|---|---|---|
| Non-collapse | F-12 (clamp), F-10 (scale mismatch) | U-01 (Hamiltonian) |
| Simultaneous identity | F-09 (q̇ degeneracy) | U-05 (consensus terminology) |
| Per-hexagram uniqueness | F-09 | U-09 (output contract, 448/512 None) |
| Derive as well as, not instead of | F-05 (broken consumers), F-06 (import paths) | U-09 |
| Full expansion before selection | F-05, F-06 | U-09 |
| Emotional range preservation | F-03, F-04 | U-03 (coherence), U-04 (voice weight) |
| Historical compatibility | F-05, F-08 (empty line_balance) | U-09 |
| Representation continuity | F-10, F-11 | U-02/U-08 (porosity), U-07 (yao vocabulary) |

## 6. Finding vs. Causal Explanation Distinction

The RVG preserves the distinction between confirmed findings and proposed causal explanations:

- **Confirmed findings** (F-10, F-11, F-12): Validated through independent investigation with defined evidence
- **Proposed causal explanations** (governance failure diagnosis): Strong synthesis but does not prove every listed symptom has the same immediate technical cause
- **Semantic questions** (U-05, U-09): Separate from validated findings; describe interface and terminology concerns, not implementation defects
- **Implementation findings** (F-01 through F-08): Track existing defects in the codebase

A universal instruction to "preserve everything" is insufficient unless each rule has a measurable test appropriate to its domain. The constraint table in Section 5 provides those domain-specific tests.

## 7. Amendment Status

This document is a governance addition, not a modification to any existing artifact. It does not change:
- Source code
- `docs/unknowns-register-2026-11-02.md`
- `docs/pre-remediation-evidence-freeze-2026-11-02.md`
- `docs/remediation-verification-matrix.md`
- `docs/controlled-remediation-verification-protocol.md`

It is subject to explicit approval as a separately versioned governance document before it becomes binding on resolution work.

## 8. Governing State (unchanged by this document)

| Item | Status |
|---|---|
| Discovery investigation | Complete |
| Evidence freeze | Preserved |
| Unknowns register | Complete (10 unknowns) |
| Remediation matrix | Separate and unchanged |
| B4 Gate 2 | BLOCKED (U-07) |
| QSMC-1 Gate 2 | OPEN |
| Remediation authorization | Process-level granted; individual-change pending |
| Remediation acceptance | Not started |
| Rule Verification Gate | Proposed (pending approval) |