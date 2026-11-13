# Glyph Mapping Coverage Crosswalk
# Generated: 2026-11-12T22:45:00Z
# Source: DOCUMENTATION ONLY — see glyph_mapping_coverage.json for machine-readable data

| Visual asset | Metamath name | Unicode code point | Unicode char | Wolfram mapping | SymPy mapping | Font variant | Font style | Crosswalk status | Mapping status | Issue |
|---|---|---|---|---|---|---|---|---|---|---|
| sigma.gif | sigma | U+03A3 | Σ | CapitalSigma | Sigma | — | — | verified | mapped | — |
| sum.gif | sum | U+2211 | ∑ | Sum | Sum | — | — | verified | mapped | — |
| subscrl | subscrl | U+2113 | ℓ | (not found) | (not found) | — | — | verified | unmapped | Crosswalk verification ≠ Wolfram/SymPy coverage |
| rmw | rmw | U+0057 | W | (not found) | (not found) | — | — | verified | unmapped | Crosswalk verification ≠ Wolfram/SymPy coverage |

## Summary

| Metric | Value |
|---|---|
| Total crosswalk entries | 4 |
| Mapped (Wolfram + SymPy) | 2 |
| Unmapped | 2 |
| Coverage (Wolfram) | 50% |
| Coverage (SymPy) | 50% |

## Notes

1. **Preliminary coverage only.** This is coverage of the 4 reported crosswalk entries, NOT coverage of the full 3,301-image catalog.
2. **Crosswalk verification ≠ Wolfram/SymPy coverage.** An entry marked `verified` in `glyph_identity_crosswalk.json` confirms the Metamath source, not the presence in `UNICODE_TO_WOLFRAM` or `UNICODE_TO_SYMPY`.
3. **Identity vs. normalization are separate.** A Unicode code point can be verified as a real glyph identity without being present in either notation dictionary.
4. **No inference allowed.** Absence in the dictionaries is recorded as `unmapped` — never converted into an inferred identity from visual similarity.

## Human-readable observations

- `subscrl` (U+2113, script small l): The crosswalk reports this as verified against the Metamath source, but `ℓ` does not appear in the hard-coded `UNICODE_TO_WOLFRAM` or `UNICODE_TO_SYMPY` dictionaries. This is a genuine coverage gap for the notational layer, unrelated to Metamath source verification.
- `rmw` (U+0057, Latin capital W): Same pattern — verified in Metamath, absent from both notation dictionaries. This is common for ASCII letters that don't need normalization.

## Recommendation

Before expanding the mapping coverage practice beyond the 4 reported entries, the following are needed:

1. A complete inventory of which Unicode code points are present in `UNICODE_TO_WOLFRAM` and `UNICODE_TO_SYMPY`.
2. A mapping of each crosswalk entry to its intended consumer (vision comparison, AST extraction, association bridge).
3. A decision on whether `subscrl` and `rmw` (and their Unicode code points) should be added to the notation dictionaries, or explicitly marked as out-of-scope for the notational layer.
