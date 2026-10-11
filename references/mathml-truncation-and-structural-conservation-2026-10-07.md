# MathML truncation and structural conservation - verified results (2026-10-07)

This document records the verified results from fixing the MathML truncation bug and
structural conservation invariants. All numbers here are from real tool execution.

## Measurement correction (2026-10-07)

**Incorrect claim (deprecated):** "709 of 3409 equations hit the cap; 34.2% of the
corpus was discarded."

**Corrected figures (now verified):**
- 709/3409 = 20.8% of EQUATIONS hit the 500-char truncation cap
- 34.2% = the single-paper figure for 2605.00155 (345,984 → 525,671 chars)
- Corpus-wide after fix: 1,042,862 → 1,412,608 = +369,746 chars = +26.17% of the full
  total (35.45% larger than the truncated total)

Correction noted in this document so the archaeology record does not contain an numeric
artifact.

## Structural conservation invariant

**Invariant:** No MathML structural child may disappear merely because its node type
is unsupported.

The bug: `munder`/`mover`/`munderover` fell through to `return base`, silently dropping
under/over children. `\sum_{y\in\mathcal{Y}}` (limits underneath in display mode,
encoded `<munder>`) became `'Sum'` — index and domain gone.

### Fix

`BIG_OP_BASES = {Sum, Prod, Integral, Limit, Max, Min, sup, inf, argmax, argmin,
                  limsup, liminf, Union, Intersect}` checked in the munder/munderover
branch before falling through to `return base`.

### Result

`test_structural_conservation.py` now 21/21 (was 17). Added cases:
- conditional bar `E[X|X>a]` (U+2223 ∣ missing from MO_MAP)
- differential `𝑓` (U+1D451, was unmapped)
- integral `∫_α^∞ φ(z) dz` (munderover limits + differential preserved)

## False recovery count (verified)

Regex path vs Tree path: the regex path mapped `\sim` → `'='` and `\to` → `'='`,
converting statements about distributions into solvable equations. Verified: 63
equations altered on the regex path. The tree path preserves the relation and
refuses → solvable drops but honesty rises.

## Numeric corrections applied to this document

- 34.2% was the single-paper figure for 2605.00155, not corpus-wide
- Corpus-wide: +369,746 chars = +26.17% of full total
