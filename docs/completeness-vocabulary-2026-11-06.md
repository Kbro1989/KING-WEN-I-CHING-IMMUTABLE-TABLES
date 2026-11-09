# Completeness Tracking Vocabulary Reference

**Project:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Document type:** Reference — terminology standard for audit/evidence tracking
**Version:** 1.0 — NAD (no authoritative development)
**Date:** 2026-11-06

---

## 1. Core Completeness Status

Terms that describe how far a deliverable is from being "complete".

| Term | Meaning | Strictness | Example |
|------|---------|-----------|---------|
| **COMPLETE** | Artifact exists, is fully functional, and has been verified against all acceptance criteria. No open defects. | Highest authority | "Box 1 ACCEPTED. Artifact map complete." |
| **DONE** | Artifact exists but verification/proof is incomplete. Used for the 'verified' part of the box-check delimiter. | Equivalent to COMPLETE for closure purposes | "Box 1 ACCEPTED." |
| **PARTIAL** | Artifact exists and performs some functions, but key acceptance criteria are unmet. Use when 50-95% of acceptance criteria are met. | Mid-tier authority | "Box 3 PARTIALLY COMPLETE. The integration boundary is mapped and verified as an audit finding." |
| **INCOLOR** | Artifact exists but has known defects that block full completion. More specific than PARTIAL; indicates a defect that prevents full completion. | Mid-tier authority | "Box 3 PARTIALLY COMPLETE. The visual layer does not yet receive structural recovery results." |
| **UNTESTED** | Artifact exists, but verification has not been attempted or is not yet evidence-based. | Lowest authority | "Box 4.2 AWAITING EXECUTION" |
| **NOT VERIFIED** | Artifact exists, but no verification evidence is available or has been produced. | Lowest authority | "Box 3 NOT VERIFIED — integration gap." |
| **BLOCKED** | Artifact cannot proceed because of an external dependency, frozen component, or missing input. Do not include in UNVERIFIED. | Highest precedence | "Box 5 PAARTIAL — pairing component not yet wired into the visual layer." |
| **BLOCKED BY** | Specific dependency that is blocking completion. Used in action items. | Highest precedence | "Wire structural recovery into per-page records (Phase 3.7)." |
| **NOT SETTLED** | A decision is required from an authority before this work can proceed. | Highest precedence | "Final disposition cannot be issued until Milestone B evidence is produced." |

**Disambiguation rules for similar terms:**

| Term pair | Distinction | Guidance |
|-----------|-------------|----------|
| complete vs done | complete = fully functional + verified; done = exists + proof | Use done for the 'verified' part of the box-check delimiter |
| unverified vs untested | untested = verification attempted but evidence not yet produced; untested = verification not attempted | Record verified OR verified under... |
| partial vs incomplete | partial = partially functional; incomplete = partially functional | Use PARTIAL for 50-95% of acceptance criteria met |
| verified vs approved | verified = evidence exists; approved = authority has reviewed | Verified under... |

---

## 2. Quality and Defect Terms

Terms that describe defects, gaps, or weaknesses in an artifact.

| Term | Meaning | Scope | Example |
|------|---------|-------|---------|
| **BLOCKING** | A defect that prevents further progress. Must be fixed before any downstream work. | Highest | PASS |
| **HIGH** | A defect that significantly impairs function but does not block all progress. | High | |
| **MEDIUM** | A defect that reduces quality but does not block normal usage. | Medium | |
| **LOW** | A minor defect that is cosmetic or non-functional. | Low | |
| **DEFECT** | Any deviation from intended behavior. | General | |
| **GAP** | Missing functionality; a required capability is absent. | Structural | |
| **DISCREPANCY** | A mismatch between recorded state and actual state. | Data integrity | |
| **DIFFERENCE** | A variation between two states or versions. | Data integrity | |
| **EDGE-CASE** | A behavior that occurs at the boundary of a system's operating envelope. | Parametrization | |
| **FLAKE** | A test or process that fails intermittently with no apparent cause. | Testing | |
| **FLAPPING** | A test or process that fails repeatedly with no apparent cause. | Testing | |

**Defect classification:**

| Term | Meaning | Scope |
|------|---------|-------|
| **CRITICAL** | System failure, data loss, security breach, or unrecoverable state | |
| **BLOCKING** | Prevents further work or downstream verification | |

---

## 3. Closure Status Terms

Terms that describe what happens to an item when work is done.

| Term | Meaning | Example |
|------|---------|---------|
| **CLOSED** | The item is complete and no further work is required. | "Box 1 ACCEPTED." |
| **CLOSED-ACCEPTED** | The item is complete and approved by the auditor. | "Box 2 ACCEPTED." |
| **CLOSED-DECLINED** | The item is complete but rejected. | "Box 5 NOT VERIFIED." |
| **CLOSED-WITH-MODIFICATIONS** | The item is complete but with known issues. | "Box 3 PARTIALLY COMPLETE." |
| **CLOSED-CANCELLED** | The item was deliberately cancelled. | N/A |
| **CLOSED-LATER** | The item was deferred and closed in a later session. | N/A |
| **OPEN** | The item is still in progress. | "Box 8 NOT COMPLETE." |
| **OPEN-UNSETTLED** | The item is open and requires a decision from an authority. | "Final disposition cannot be issued until Milestone B evidence is produced." |
| **OPEN-DECISION** | The item is open and requires an authority decision. | "What should be done with the duplicate path?" |
| **OPEN-PAYMENT** | The item is open and the next step is explicit. | N/A |

**Closure discipline:**
- Use **CLOSED** for items that are complete and verified.
- Use **OPEN** for items that are still in progress.
- Do not use OBTAINED for items that are only partially complete.

---

## 4. Test Status Terms

Terms that describe the outcome of a verification or test.

| Term | Meaning | Example |
|------|---------|---------|
| **PASS** | The verification succeeded and the artifact meets acceptance criteria. | "py_compile: PASS" |
| **FAIL** | The verification failed and the artifact does not meet acceptance criteria. | "py_compile: FAIL" |
| **SKIP** | The verification was skipped deliberately (e.g., known limitation, not applicable). | "Test skipped: window not rendered." |
| **SKIPPED** | Same as SKIP. | N/A |
| **NOT SKIPPED** | The verification was not skipped and was attempted. | N/A |
| **NOT RUN** | The verification was not run (e.g., system is unavailable). | N/A |
| **NOT RUN-ABLE** | The verification could not be run because the artifact is missing. | N/A |
| **NOT RUN-ABLE** | The verification could not be run (e.g., missing executable). | N/A |

**Test result taxonomy:**

| Term | Meaning | When to use |
|------|---------|-------------|
| **PASS** | The test passed and the artifact meets acceptance criteria. | Valid result |
| **FAIL** | The test failed and the artifact does not meet acceptance criteria. | Invalid result |
| **SKIP** | The test was skipped deliberately. | Known limitation |
| **NOT RUN** | The test was not run due to external constraints. | System unavailable |
| **NOT RUN-ABLE** | The test could not be run because the artifact is missing. | Artifact missing |

---

## 5. Work-Status Terms

Terms that describe the state of work in a session.

| Term | Meaning | Example |
|------|---------|---------|
| **ACTIVE** | Work is in progress and being actively advanced. | This session |
| **INACTIVE** | Work is paused and not being advanced. | Not this session |
| **COMPLETE** | Work is done and verified. | Session complete |
| **INCOMPLETE** | Work is not complete. | Session not complete |
| **BLOCKED** | Work cannot proceed due to a specific dependency. | This session blocked |
| **ON-TRACK** | Work is progressing as expected. | This session on track |
| **OFF-TRACK** | Work is not progressing as expected. | This session off track |
| **DELAYED** | Work will be completed later than planned. | This session delayed |
| **AHEAD** | Work is ahead of schedule. | This session ahead |
| **SIDE** | Work is in a side branch, not on the main line. | This session side branch |
| **NEAR** | Work is close to completion but not yet. | This session near completion |

**Status word families:**

| Family | Words | Meaning |
|--------|--------|---------|
| complete | complete, done, verified | Artifact is fully functional and verified |
| incomplete | incomplete, untested, unverified | Artifact is not fully functional or verified |
| blocked | blocked, blocker | Work cannot proceed |
| on-track | on-track, on-course | Work progressing as expected |
| off-track | off-track, off-course | Work not progressing as expected |
| deferred | deferred, postponed, postponed | Work deferred to later session |
| declined | declined, rejected | Work rejected |
| cancelled | cancelled, cancelled, cancelled | Work cancelled |
| superseded | substituted, replaced, refactored, deprecated, obsolete | Artifact replaced or dead |
| modified | patched, applied, edited, rewritten, updated | Artifact modified |
| per-item | per-box, per-widget, per-module, per-package | Per-item verbosity |
| per-operation | per-style, per-action, per-effect, per-call, per-parameter | Per-operation verbosity |
| per-field | per-field | Per-field verbosity |

---

## 5. Completeness Tracking Terms

**Core completeness status:**

| Term | Meaning |
|-----|---------|
| **COMPLETE** | Artifact exists, is fully functional, and has been verified against all acceptance criteria. |
| **DONE** | Artifact exists and is functionally complete; verification/proof is complete. |
| **PARTIAL** | Artifact exists and is partially functional/verified. |
| **PARTIAL-COMPONENT** | Partial completeness for a specific sub-component. |
| **UNCERTAIN** | Status ambiguous or not yet determined. |
| **PATTERN-EXTANT** | Pattern exists but not yet extended to a full representative subset. |
| **UNKNOWN** | Status not yet determined or not available. |

**Closure status:**

| Term | Meaning |
|------|---------|
| **CLOSED** | Complete and no further work required. |
| **CLOSED-ACCEPTED** | Complete and approved. |
| **CLOSED-DECLINED** | Closed but rejected. |
| **CLOSED-WITH-MODIFICATIONS** | Complete but with known issues. |
| **OPEN** | Still in progress. |
| **OPEN-UNSETTLED** | Requires authority decision. |

**Test status:**

| Term | Meaning |
|------|---------|
| **PASS** | Verification succeeded. |
| **FAIL** | Verification failed. |
| **SKIP** | Skipped deliberately. |
| **NOT SKIPPED** | Not skipped (i.e., attempted). |
| **NOT RUN** | Not run due to external constraints. |
| **NOT RUN-ABLE** | Could not run due to missing requirements. |

**Work status:**

| Term | Meaning |
|------|---------|
| **ACTIVE** | In progress, being advanced. |
| **INACTIVE** | Paused, not advanced. |
| **COMPLETE** | Done and verified. |
| **INCOMPLETE** | Not complete. |
| **BLOCKED** | Cannot proceed. |
| **ON-TRACK** | Expected progress. |
| **OFF-TRACK** | Not on expected progress. |
| **DELAYED** | Will be later than planned. |
| **AHEAD** | Ahead of schedule. |
| **SIDE** | Side branch. |
| **NEAR** | Close to completion. |
| **DEAD** | Dead end or abandoned. |
| **DORMANT** | Inactive but potentially needed. |

---

## 6. Evidence State Terms

Terms that describe the state of evidence in an audit.

| Term | Meaning | Example |
|------|---------|---------|
| **CONFIRMED** | Verified through independent evidence (tool output, file content, external source). | "Confirmed. Box 1 ACCEPTED." |
| **DISCOVERED** | Found through investigation, but not yet independently verified by known tools. | "Discovered. Box 2 ACCEPTED." |
| **DERIVED** | Computed from other evidence; results depend on the derivation. | "Derived. Box 8." |
| **FALSE** | Incorrect. | "Not true. Box 2." |
| **ACCORDING** | Consistent with the original source or specification. | "According to source." |
| **AGREED** | Consistent with the system under review. | "Agreed with system." |

---

## 7. Provenance Terms

Terms that describe the chain of custody and derivation of evidence.

| Term | Meaning | Example |
|------|---------|---------|
| **SOURCES** | Original inputs. | "Source artifacts." |
| **EVIDENCE** | Inferences, support, and data that together form the basis for a claim. | "Evidence from source." |
| **SELF-CHECKS** | Independent, deterministic probes that are verified against manifests/scores. | "Self-checks, metrics, self-report, and logs." |

---

## 8. Representation State Terms

Terms that describe the state of data representation.

| Term | Meaning | Example |
|------|---------|---------|
| **CODE** | Executable code. | "Code modification." |
| **DATA** | Data artifact. | "Data artifact." |
| **METADATA** | Metadata. | "Metadata." |
| **SCHEMA** | Schema of a data structure. | "Schema." |
| **SCHEMA-TARGET** | Schema target directory. | "Schema target directory." |

---

## 9. Operation Terms

Terms that describe operations performed on artifacts.

| Term | Meaning | Example |
|------|---------|---------|
| **FIX** | Correct a defect. | "Fix." |
| **PATCH** | Apply a targeted modification. | "Patch." |
| **APPLY** | Apply a modification. | "Apply." |
| **SKIP** | Deliberately not perform an operation. | "Skip." |
| **DEFER** | Defer a task to later. | "Defer." |
| **IGNORE** | Deliberately not address an item. | "Ignore." |
| **CLAIM** | Assert a finding without full verification. | "Claim." |
| **VERIFY** | Run a check and record the result. | "Verify." |

---

## 10. State Terms

Terms that describe the general state of a system or artifact.

| Term | Meaning | Example |
|------|---------|---------|
| **ACTIVE** | In use, currently active. | "Active component." |
| **INACTIVE** | Not in use. | "Inactive component." |
| **DORMANT** | Inactive but has potential for future use. | "Dormant component." |
| **HOT** | Frequently used, in high demand. | "Hot component." |
| **COLD** | Rarely used, cold path. | "Cold component." |
| **LIVE** | Currently running. | "Live component." |
| **DEAD** | Not running, not used. | "Dead component." |
| **STALE** | Outdated, not current. | "Stale component." |

---

## 11. Direction Terms

Terms that describe the direction or provenance of data.

| Term | Meaning | Example |
|------|---------|---------|
| **NORTH** | Northward direction. | "Northward direction." |
| **SOUTH** | Southward direction. | "Southward direction." |
| **EAST** | Eastward direction. | "Eastward direction." |
| **WEST** | Westward direction. | "Westward direction." |

---

## 12. Distribution Terms

Terms that describe how evidence or artifacts are distributed.

| Term | Meaning | Example |
|------|---------|---------|
| **DISTRIBUTE** | Distribute artifacts. | "Distribute artifacts." |
| **DISTRIBUTION** | Distribution of evidence. | "Distribution of evidence." |

---

## 13. Key Multi-Word Status Terms (Quick Reference)

| Full Phrase | Meaning | Status Indicator |
|------|----------|
| **COMPLETE** | Fully verified and complete | ✅ |
| **DONE** | Complete, but verification/proof may be partial | ✅ |
| **PARTIAL** | Partially functional or verified | ⚠️ |
| **NOT VERIFIED** | No verification evidence | ⚠ |
| **UNTESTED** | Not yet attempted | ⚠ |
| **INCOMPLETE** | Not complete | ⚠ |
| **BLOCKED** | Cannot proceed | STOP |
| **PASS** | Test passed | ✅ |
| **FAIL** | Test failed | ❌ |
| **SKIP** | Skipped deliberately | ⚪ |
| **NOT SKIPPED** | Attempted | ✅ |
| **NOT RUN** | Not run | ⚪ |
| **NOT RUN-ABLE** | Could not run | ⚪ |
| **ACTIVE** | In progress | 🔄 |
| **INCOMPLETE** | Not complete | ⚠ |
| **BLOCKED** | Cannot proceed | 🚫 |
| **ON-TRACK** | As expected | ✅ |
| **OFF-TRACK** | Not as expected | ⚠️ |
| **DELAYED** | Later than planned | ⚠️ |
| **AHEAD** | Ahead of schedule | 🚀 |
| **SIDE** | Side branch | 🌿 |
| **NEAR** | Close to completion | 🔍 |
| **DEAD** | Abandoned | 💀 |
| **DORMANT** | Inactive but potential | 💤 |
| **CONFIRMED** | Independently verified | ✅ |
| **DISCOVERED** | Found, not yet verified | 🔍 |
| **DERIVED** | Computed from evidence | 📊 |
| **FALSE** | Incorrect | ❌ |
| **ACCORDING** | Consistent with source | ✅ |
| **AGREED** | Consistent with system | ✅ |

---

## 14. Abbreviation Reference

| Abbreviation | Full Form | Meaning |
|--------------|----------|
| **NAD** | No authoritative development | |
| **TA** | Teaching assistant | |
| **QA** | Quality assurance | |

---

## 15. Usage Rules

1. **Every box check must include an evidence entry** — do not mark "complete" without a `✅ COMPLETE` with evidence of how.
2. **Every pending item must include an owner** — do not leave a pending item without an action owner.
3. **Use the extended vocabulary** — use "COMPLETE", "NOT VERIFIED", "PARTIAL", "UNTESTED" as appropriate; do not mix terms.

---

## 16. Quick Reference Table

| Term | Meaning | Status Indicator |
|------|---------|---------|
| COMPLETE | Fully verified and complete | ✅ |
| DONE | Complete, but verification/proof may be partial | ✅ |
| PARTIAL | Partially functional or verified | ⚠️ |
| NOT VERIFIED | No verification evidence | ⚠ |
| UNTESTED | Not yet attempted | ⚠ |
| INCOMPLETE | Not complete | ⚠ |
| BLOCKING | Prevents further work | STOP |
| PASS | Test passed | ✅ |
| FAIL | Test failed | ❌ |
| SKIP | Skipped deliberately | ⚪ |
| NOT SKIPPED | Attempted | ✅ |
| NOT RUN | Not run | ⚪ |
| NOT RUN-ABLE | Could not run | ⚪ |
| ACTIVE | In progress | 🔄 |
| INACTIVE | Paused | ⏸ |
| COMPLETE | Done and verified | ✅ |
| INCOMPLETE | Not complete | ⚠ |
| BLOCKED | Cannot proceed | 🚫 |
| ON-TRACK | As expected | ✅ |
| OFF-TRACK | Not as expected | ⚠️ |
| DELAYED | Later than planned | ⚠️ |
| AHEAD | Ahead of schedule | 🚀 |
| SIDE | Side branch | 🌿 |
| NEAR | Close to completion | 🔍 |
| DEAD | Abandoned | 💀 |
| DORMANT | Inactive but potential | 💤 |
| CONFIRMED | Independently verified | ✅ |
| DISCOVERED | Found, not yet verified | 🔍 |
| DERIVED | Computed from evidence | 📊 |
| FALSE | Incorrect | ❌ |
| ACCORDING | Consistent with source | ✅ |
| AGREED | Consistent with system | ✅ |

---

## 17. Box-Check Discipline

1. **One box = one proof** — each checked box has an appended usage marker with file, command, and proof.
2. **Drift blocked by appending, not editing** — do not edit old checked boxes.
3. **New blockers appended as new boxes** — when a new blocker is found, add a new box.
4. **Read before write** — read the target file before writing.
5. **Patch before write** — use patches for small changes.
6. **Block before write** — if something blocks a fix, block it before proceeding.
7. **Verify after write** — verify that the write succeeded and the content is correct.

---

**End of vocabulary reference.** This document is the single source of truth for completeness tracking terminology in this audit. All checklist boxes and disposition tables in this project must use only terms defined here, in one of their accepted forms.
