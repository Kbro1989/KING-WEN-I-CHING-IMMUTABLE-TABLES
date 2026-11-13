# Cross-Document Comparison and Authority Mapping

Use this reference when comparing multiple math-related `.md` documents in the King Wen repo to establish canonical finding ownership and prevent duplicate descriptions across docs.

## When to use this reference

- Comparing newly created evidence matrices or audit docs against existing `.md` papers
- Establishing which document governs a particular finding
- Preventing the same finding from being re-described with slightly different wording/status across multiple docs
- Auditing whether vision-related or other domain-specific docs were missed

## Core procedure

### 1. Full recursive search BEFORE comparing

Do NOT rely on files you already know about. Search the entire docs/ directory:

```
search_files(pattern="*.md", target="files", path="docs/")
```

Then cross-reference against `CONSOLIDATED_DOCUMENT_INDEX.md` which lists all 107+ .md files by domain. Any doc not in your comparison set that touches the same domain must be included.

**Pitfall:** The vision-related docs (`numerical-extraction-vision-pipeline.md`, `pix2text-assessment-2026-10-20.md`, `pix2text-three-layer-experiment.md`) were missed in the original 10-doc comparison because the search was limited to files already known about. Always check the consolidated index.

### 2. Identify which doc describes implementation vs. design intent

The Oct 27 document describes a Hamiltonian formula that never existed in source code. Always check `git log -p -- <file>` before treating a doc as "the source." A design-intent doc is not evidence of implementation behavior.

### 3. Distinguish scope for all quantitative claims

- 991 equations = one paper (2605.00155)
- 3,409 equations = 14-paper corpus
- 4,235 equations = full corpus
- 72,478 equations = HTML corpus (241 papers)

Never quote a number without stating its scope. Never conflate counts from different scopes.

### 4. Check for field-name collisions

Two different computations can produce a field with the same name (e.g., `hamiltonian_energy` from M3 emotional_engine vs. JKD ingestion). Consumers cannot distinguish them. Always grep for field names across all producers before assuming uniqueness.

### 5. Verify interface claims against code

A design doc that says "this function exists" is a claim, not evidence. Verify with `grep -rn 'def <name>' scripts/`. The lua-math-tool.md had 8 interface mismatches, all of which were naming differences or unsupported functions.

### 6. Measurement-layer defects must be individually impact-mapped

A defect in the measurement code does not invalidate every measurement. Classify each measurement as:
- **Affected** — depends on the defective operation
- **Unaffected** — does not depend on the defective operation
- **Unverified** — cannot determine dependency

Do not blanket-classify as "all invalid."

### 7. Occurrence identity must remain separate from other identities

SHA-256 over (paper_id, version, locator, occurrence_index). No LaTeX in identity key. This identity must remain separate from:
- Mathematical expression identity
- Parsed AST identity
- Reconstructed expression identity
- Solver-result identity

Two identical LaTeX expressions can be separate occurrences. An equation can be reconstructed differently while remaining the same source occurrence.

### 8. Gate statuses must not be merged

Three independent gate contexts exist:
- QSMC-1 Gate 2: OPEN (mathematical provenance)
- B4 Gate 2: BLOCKED by U-07 (ternary semantic contract)
- Lua migration prerequisite: NOT YET PASSED (migration gate, not evidence of completion)

These are substantively different statuses. "Open" ≠ "blocked" ≠ "not yet passed."

### 9. Seam mismatch detection

When a pipeline claims to use a canonical parser but actually uses a fallback, the seam mismatch is the real defect. Check with `grep -n "<parser_name>" scripts/<pipeline_file>.py`. If no match, the pipeline does not use the parser regardless of what the docs say.

### 10. Canonical finding ownership

Each finding gets one stable ID (CF-NNN) and one canonical owner. The canonical owner governs status, scope, and unresolved questions. Other documents may contain valid measurements, historical observations, or downstream consequences without becoming competing authorities.

**Supersession rule:** If a finding is superseded, record both the original and new finding IDs explicitly. Never silently delete, merge, or reclassify.

## Authority map structure

When creating a cross-document finding authority map, use these 7 sections:

1. Purpose and authority rules
2. Canonical finding registry (one ID per finding, one owner)
3. Cross-document reference map (which docs discuss which findings)
4. Evidence dimensions (implementation, mathematical validity, measurement validity, provenance, downstream impact)
5. Gate-status registry (independent gate contexts)
6. Conflict and supersession rules (known conflicts + supersession chain + historical findings preserved)
7. Completeness and acceptance checks (finding completeness + acceptance criteria + what the map does NOT establish)

## Pitfalls

- **Do not turn the evidence matrix into a repository-wide encyclopedia.** The evidence matrix is the operational baseline; the authority map is the cross-reference. Keep them separate.
- **Do not conflate "evidence collected" with "implementation fixed" with "accepted as shippable."** These are three independent dimensions.
- **Do not quote a metric without stating its scope.** 991 (one paper) ≠ 3,409 (14-paper corpus) ≠ 4,235 (full corpus).
- **Do not trust a commit message as evidence of what code does.** Read the actual file on disk. A commit saying "100% semantic agreement" is a claim, not proof.
- **Do not claim "verified" from solver acceptance alone.** BackendStatus ≠ SolutionStatus. Solver acceptance proves the solver produced a result, not that the result is mathematically correct.
- **When a doc describes a formula, check if it exists in source.** The Oct 27 document describes a formula that never existed in code. Always `git log -p -- <file>` before treating a doc as "the source."
- **When comparing docs, check the consolidated index first.** `CONSOLIDATED_DOCUMENT_INDEX.md` lists all 107+ .md files by domain. Any doc touching the same domain that is not in your comparison set must be included.