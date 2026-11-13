# Godot Resource Architecture and Separation-of-Concerns Contract

**Status:** Proposed architecture contract (companion to `math-implementation-reconciliation-matrix-2026-11-11.md`)
**Scope:** Godot resource population, generation lineage, presentation dependencies, and validation independence
**Related document:** `docs/math-implementation-reconciliation-matrix-2026-11-11.md`
**Validation mode:** Read-only; no repository modifications implied by this document

---

## 1. Purpose

This repository contains multiple independently meaningful systems: mathematical computation, mathematical extraction and recovery, and Godot-based resource and presentation infrastructure.

The existing reconciliation matrix (`math-implementation-reconciliation-matrix-2026-11-11.md`, §5, lines 154-164) explicitly requires the mathematical engine and extraction pipeline to remain separate during review. This document extends that principle to the Godot resource layer.

The purpose is to establish independently typed relationships between mathematical authority, resource generation, presentation dependencies, and validation evidence.

**Core rule:** A relationship between two artifacts does not automatically establish equivalence, authority, provenance, or correctness.

---

## 2. Architectural Domains

| Domain | Responsibility | Authority |
|--------|----------------|-----------|
| Mathematical engine | Mathematical formulations, state transformations, immutable registries | Mathematical specifications and validated implementations |
| Extraction pipeline | ArXiv HTML, MathML, PDF, OCR, equation recovery | Source documents and extraction validation contracts |
| Godot resource layer | Serialized resources, materials, meshes, visual assets | Resource schemas and generator specifications |
| Presentation layer | Scenes and their referenced resources | Scene structure and presentation validation |
| Documentation/provenance | Specifications, audit records, lineage evidence | Traceable source artifacts and recorded evidence |

These domains may exchange data. They must not inherit one another's validation status implicitly.

---

## 3. Relationship Types

Every recorded relationship must have an explicit type.

| Relationship type | Meaning | Does not establish |
|-------------------|---------|-------------------|
| `mathematical_authority` | A specification or registry defines the expected mathematical content | That a generated resource is correct |
| `generation_lineage` | A generator produces or transforms an artifact | That the output passed validation |
| `resource_dependency` | A scene or resource references another resource | Mathematical authority or generator ancestry |
| `documentation_reference` | Documentation mentions or describes an artifact | Runtime dependency or generation lineage |
| `upstream_ancestry` | An artifact or project derives from an upstream source | Current runtime dependency |
| `fork_derivative` | A repository is a fork or derivative of another repository | That the upstream implementation is currently consumed |
| `runtime_code_dependency` | Executable code imports, invokes, or consumes another component | That the dependency is mathematically authoritative |

Do not collapse these relationships into a generic `consumer` field.

---

## 4. Mathematical Authority

Mathematical authority must be established from the repository's existing immutable registries, specifications, and validated mathematical implementations.

For every resource family claimed to represent mathematical data, record:

- The authoritative registry or specification.
- The relevant identifier and state domain.
- The transformation or serialization rules.
- The expected mathematical invariants.
- The validation procedure and evidence.

A `.tres` file containing a hexagram identifier is not, by that fact alone, authoritative evidence of the hexagram's mathematical definition.

Likewise, visual agreement with an expected representation does not certify the underlying mathematical computation.

---

## 5. Generation Lineage

Generation lineage records the actual producer-consumer chain for generated resources.

The desired relationship is:

`authoritative input → generator → generated resource → validation evidence`

Record, where available:

- Generator path and version.
- Input artifact identifiers and hashes.
- Generator configuration and parameters.
- Output path and content hash.
- Generation timestamp or commit association.
- Validation results.
- Whether the output is generated, manually authored, modified, or of unknown origin.

Do not infer generator lineage from naming conventions, directory placement, timestamps, or documentation references alone.

Unknown lineage must remain explicitly unknown.

---

## 6. Presentation Dependencies

Godot presentation dependencies must be derived from actual serialized references.

In particular:

- `.tres` files are Godot text resources.
- `.tscn` files are Godot scene files.
- A scene referencing a `.tres` file establishes a `resource_dependency`.
- A resource referencing another resource establishes a resource-level dependency.
- A Markdown mention establishes only a `documentation_reference`, unless separate evidence establishes another relationship.

Reference resolution must distinguish:

1. Existing and resolvable references.
2. Missing references.
3. Duplicate or conflicting resource identities.
4. Unreferenced resources.
5. References whose targets exist but have incompatible or unexpected contents.

A reference graph is evidence of dependency structure, not correctness.

---

## 7. Validation Independence

The following validation domains must remain independently reportable:

| Validation domain | Establishes | Does not certify |
|-------------------|-------------|------------------|
| Mathematical validation | Formula and state correctness under a defined contract | Resource serialization or visual fidelity |
| Resource validation | Resource structure, identity, and serialization integrity | Mathematical correctness |
| Population validation | Expected resource combinations exist without unexplained gaps or duplicates | Correct generation lineage |
| Dependency validation | Scene and resource references resolve correctly | Correct visual or mathematical meaning |
| Presentation validation | Rendered output meets defined visual requirements | Mathematical correctness |
| Provenance validation | Artifact origin and transformation history is traceable | Functional correctness |

No aggregate pass may conceal a failure in an independently mandatory domain.

---

## 8. Resource Population Audit

The reported repository inventory contains:

- 280,448 `.tres` files.
- 130 `.tscn` files.
- 1,225 `.ply` files.
- 576 `.obj` files.
- 65 `.usda` files.

The reported `.tres` population has the following arithmetic decomposition:

[\
64 \times 729 \times 6 = 279{,}936\
]

[\
64 \times 8 = 512\
]

[\
279{,}936 + 512 = 280{,}448\
]

This is a population-count reconciliation, not yet a verified semantic classification of the files.

The audit must establish the actual schema, grouping, identifiers, and contents before treating the decomposition as a proven generation model.

### Recommended validation sequence

1. Inventory resource paths, sizes, and hashes.
2. Parse resource contents and identify actual resource types and serialized properties.
3. Establish the six-resource grouping and identify the 512 phase-resource candidates.
4. Select one hexagram using a recorded selection rule.
5. Inspect all 729 states across six variants and the associated phase resources.
6. Compare identifiers and expected values against the immutable registry.
7. Parse all 130 `.tscn` files and construct the resource dependency graph.
8. Report missing, duplicate, orphaned, malformed, and unresolved resources.
9. Expand validation to the full population only after the schema and identity rules are established.

---

## 9. Evidence and Reporting Requirements

Every audit finding should identify:

- Artifact path.
- Artifact hash, where applicable.
- Relationship type.
- Evidence source.
- Validation procedure.
- Result.
- Confidence or verification status.
- Unresolved assumptions.

Use explicit statuses:

- `VERIFIED`
- `PARTIALLY_VERIFIED`
- `NOT_VERIFIED`
- `FAILED`
- `UNKNOWN`
- `NOT_APPLICABLE`

A missing validation result must not be represented as a pass.

A successful inventory must not be represented as semantic validation.

A successful reference resolution must not be represented as provenance verification.

---

## 10. Non-Regression Constraints

This audit must preserve the existing separation contract:

- Do not merge the King Wen mathematical benchmark with the ArXiv extraction benchmark.
- Do not treat extracted equations as mathematical authority for the King Wen engine.
- Do not treat Godot resources as authoritative mathematical definitions without traceable authority.
- Do not infer runtime dependencies from documentation mentions.
- Do not infer generation lineage from filenames.
- Do not modify immutable registries or frozen baselines during read-only discovery.
- Do not introduce placeholder provenance or synthetic validation results.
- Do not promote development examples into generalization evidence.

---

## 11. Completion Criteria

The resource architecture discovery milestone is complete when:

1. The resource schema is documented from actual serialized contents.
2. The reported population is reconciled against observed resource identities.
3. The six-variant and phase-resource classifications have evidence.
4. The selected sample is reproducible and registry-comparable.
5. The scene/resource dependency graph is constructed from actual references.
6. Generator lineage is established where evidence exists and explicitly marked unknown elsewhere.
7. Resource, mathematical, presentation, and provenance validation results remain independently reportable.

**Final architectural principle:**

Mathematical authority defines what a resource should represent. Generation lineage explains how it was produced. Resource dependencies explain how it is consumed. Presentation validation establishes how it appears. Provenance connects these claims to evidence.

None of these relationships substitutes for another.
