# Cross-Reference Workstream Authorization Boundary

## Status: Authorization boundary document — no implementation authorized by this document
## Date: 2026-11-04

---

## 1. Authorized Scope (Read-Only, Additive)

The following are authorized as a **single controlled evaluation workstream**:

| Work Item | Authorization Scope | Risk |
|---|---|---|
| Cross-reference implementation | Build a standalone, read-only script | Low |
| Full-page text extraction | Run against explicitly defined PDF population | Low–moderate |
| Parser record inventory | Read existing parser outputs and metadata | Low |
| Vision record inventory | Read existing 988-page and 127-page evidence separately | Low |
| Population intersection | Establish exact paper/page/equation intersections | Low |
| Matching and classification | Generate separate derived records; retain ambiguous matches | Moderate |
| Coverage calculations | Calculate independently for each population and coverage type | Low–moderate |
| Discrepancy report | Produce an additive report with traceable evidence | Low |

### Authorization as separate permissions
- **Implementation** and **execution** are separate permissions.
- Implementation may be authorized now.
- Execution requires separate authorization after implementation review.

## 2. Explicitly Excluded (Remains Blocked)

| Operation | Why Blocked |
|---|---|
| Modifying original JSONL | Violates evidence immutability |
| Changing parser or vision recognition logic | Would alter the systems being evaluated |
| Changing crop dimensions or thresholds | Could contaminate existing baselines |
| Wiring `process_candidates()` into pipeline | G2–G6 remain pending |
| Automatically merging unmatched records | Risks destroying meaningful distinctions |
| Replacing original measurements with derived values | Destroys provenance |
| Accepting G2–G6 based on cross-reference results | Cross-reference is not acceptance evidence |
| Production integration or remediation | Requires separate authorization |

## 3. Authorization Sequence

1. **Authorize implementation only.** Build standalone extraction and cross-reference tooling. Permit tests using synthetic fixtures and existing records. No corpus-wide execution.
2. **Review implementation and test results.** Inspect matching rules, coordinate transformations, page-number conventions, duplicate handling, failure behavior, provenance fields.
3. **Authorize limited pilot.** Run against a small, explicitly identified set of PDFs. Compare extraction output, equation identity, and vision-region correspondence manually.
4. **Review pilot discrepancies.** Determine whether matching rules are reliable enough for broader execution. Do not use a high match rate as proof of correctness.
5. **Authorize full run separately.** Only after pilot passes review. Write derived records to `DATASETS/cross_reference/`, leaving all source evidence untouched.

## 4. Six Safeguards

1. Every extracted page retains its original PDF identity and page number.
2. Coordinates retain their coordinate system, origin, units, and rendering scale.
3. Matching is many-to-many where appropriate; no forced one-to-one correspondence.
4. Unmatched, ambiguous, duplicate, and failed records remain explicit.
5. Every derived measurement identifies its source record and derivation version.
6. Every execution produces a manifest recording inputs, versions, timestamps, outputs, and failures.

## 5. Additional Condition: Text Extractor Scope

The full-page text extractor must **not** become an implicit mathematical parser. It captures the PDF text layer and spatial metadata only. Mathematical interpretation remains the responsibility of the existing parser and separately evaluated vision system.

## 6. Boundary Summary

| Safe to Authorize | Explicitly Excluded |
|---|---|
| Standalone implementation | Source-system modifications |
| Read-only source access | Parser or vision behavior changes |
| Synthetic tests and validation | Baseline changes |
| Limited pilot after implementation review | Pipeline integration |
| Full execution only after separate pilot approval | G2–G6 acceptance or closure |
| Additive outputs and discrepancy documentation | Automatic remediation |

## 7. Why This Boundary

Three independent evidence systems exist:
- **Math parser:** What expressions it identifies and preserves.
- **Vision pipeline:** What spatial regions it detects.
- **Full-page text layer:** What content is recoverable from the PDF's textual representation.

The cross-reference establishes where these systems agree, disagree, or cannot be linked. This is valuable evidence before any attempt to change their behavior.

## 8. Current Status

| Workstream | Status |
|---|---|
| Original execution evidence | Preserve (unchanged) |
| Field-availability matrix | Complete |
| Measurement-enrichment schema | Complete (specification only) |
| Cross-reference evaluation plan | Complete (documentation only) |
| Cross-reference authorization boundary | Complete (this document) |
| G2–G6 formal review | Pending |
| Pipeline integration | Not authorized |