# Certification Discipline — King Wen Math Extraction Pipeline

**Document type:** Verification governance record
**Date:** 2026-11-12

---

## 1. Distinction That Must Be Preserved

A passing regression suite does NOT close certification gates. The following
distinction is not semantic pedantry — it is the boundary between "code runs"
and "system is certified for its intended use."

| Status | What it means | Current gate status |
|---|---|---|
| Local adapter validation | 9/9 on the tested paper | ✅ Passed |
| Full-corpus G0 certification | Corpus-wide verification | ⏳ Pending |
| G1 advancement | Milestone progression | ⏳ Not authorized |
| Delimiter detection and identity | Per-paper verification | ❌ NOT VERIFIED |
| Structural preservation | Per-paper verification | ❌ NOT VERIFIED |
| Milestone B | Association layer | ⏳ OPEN |

## 2. Why This Distinction Matters

A regression suite can pass while the system produces wrong answers on
unrepresented paper variants. The audit record must explicitly state:

- **What was verified:** the 188 tests, the 7 gate checks on 1212.0957_p8,
  the local 9/9 adapter validation
- **What was not verified:** full-corpus certification, delimiter identity
  on all papers, structural preservation across the corpus
- **What is claimed vs. what is demonstrated:** distinguish "code exists"
  from "behavior is correct on the corpus"

## 3. Projection Rule

Any report about the pipeline must use this structure:

1. **Verified state** — exact numbers from actual test runs, with paper IDs
2. **Unverified state** — claims still requiring proof, with what proof is needed
3. **Certification status** — the gate table above, updated per milestone

Example (do not generalize beyond tested paper):

> "Verified: 7/7 D1–D6 gate checks pass on 1212.0957_p8. The same gate
> checks are NOT verified on 1505.05770v6, other benchmark papers, or the
> full 14-paper corpus."

---
**End of certification discipline record.**
