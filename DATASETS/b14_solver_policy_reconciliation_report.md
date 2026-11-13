# B-14 Solver-Policy Reconciliation Report

**Date:** 2026-11-12 00:17:24 UTC

**Pipeline:** B-14 solver-policy reconciliation (equation-level)

**Status:** Analysis complete - no modifications to parser, solver, or frozen baselines


## Source Identity


| Item | Value |

|------|-------|

| Source PDF | https://arxiv.org/pdf/2605.00155 |

| Source HTML | https://arxiv.org/html/2605.00155 (v1, unsigned) |

| Source corpus SHA-256 | 6bf463600a41aa9b |

| E2E script | scripts/e2e_math_pipeline.py (80768f61a0add0bf) |

| Recovery script | scripts/math_recovery_tool.py (782368402b506490) |

| E2E output | DATASETS/e2e_2605.00155.json (58bbae4acdee424c) |

| Recovery output | DATASETS/math_recovery/2605.00155_recovery.json (e23ca1143e57140b) |


## Population Counts


| Metric | E2E Pipeline | Recovery Pipeline |

|--------|--------------|-------------------|

| Total equations | 991 | 991 |

| Parsed equations | 991 | 991 |

| Parser failures | 0 | 0 |

| Recoverable | N/A | 183 |

| Solver-successful | 448 | 65 |


## Solver-Policy Findings


### Finding 1: E2E 'solved' field is not a solver outcome for 448 equations


The E2E pipeline reports 'solved' for 448 equations, but ALL 448 lack an equality condition (= not in latex). These are non-equality symbols (e.g. delta, ell_p, mathcal_Q) that E2E labels as 'solved' as a parser-residue fix. The recovery pipeline correctly rejects these as no_equality / empty errors.


### Finding 2: Recovery pipeline's 65 solver outcomes are genuine


The recovery pipeline's 65 solvable=True results are verified sympy solutions (e.g. [delta_r], [J_r_bar_P], [1], [delta_r_hat], [Pi_full]). These represent the only genuine solver-successful outcomes at the equation level.


### Finding 3: Zero overlap in solver outcomes


E2E's 448 'solved' and Recovery's 65 'solvable' share ZERO overlap at the equation level. The two pipelines are solving entirely different sets of equations. E2E's 'solved' set is entirely non-equality symbols.


### Finding 4: Recovery pipeline has fewer recoveries than E2E's 'solved' count


Recovery reports 65 true solver outcomes vs E2E's 448 non-equality label lookups. The 118 remaining recoverable-but-unsuccessful (183 recoverable minus 65 solved) are equations that parse but fail at the solver stage.


## Delimiter Identity Preservation


Grouping delimiters preserved across both pipelines:

- Curly braces {{: 5844 occurrences

- Round parentheses (: 1673 occurrences

- Square brackets [: 137 occurrences

- Double-bar ||: 122 occurrences

- Auto-left/auto-right pairs: 160 occurrences

- Accent_ext: 113 occurrences


## Equation-Level Matrix


**File:** DATASETS/b14_equation_reconciliation_matrix.jsonl (991 entries)


| Field | Description |

|-------|-------------|

| equation_id | 2605.00155:eqNNNN |

| latex | Original LaTeX from source |

| parser_status_e2e | recovered/null |

| parser_status_rec | recovered/null |

| solver_eligible | has = (equality condition) |

| solver_outcome_e2e | solved/failed |

| solver_outcome_rec | solved/failed |

| solver_success_valid | mathematical validity |

| solution_e2e | E2E solution string |

| solution_rec | Recovery solution (sympy) |

| error_e2e | E2E error or '' |

| error_rec | Recovery error or None |

| classification | E2E_ONLY_NON_EQUATION, REC_ONLY, BOTH_FAIL, UNCLASSIFIED |


## Equation Classification Counts


| Classification | Count |

|----------------|-------|

| E2E_ONLY_NON_EQUATION | 448 |

| REC_ONLY_SOLVER | 12 |

| BOTH_FAIL | 214 |

| UNCLASSIFIED | 264 |

| Total | 991 |



## Preservation Qualification (B-14)

The 448 E2E "solved" records have NOT demonstrated genuine mathematical solution success. The E2E pipeline forwards any expression — including non-equality symbols such as `\delta`, `\ell_{p}`, `\mathcal{Q}` — to its recovery stage and labels the result as "solved." The `solved` field is a parser-residue label, not a validated mathematical outcome.

The zero-overlap result (E2E's 448 "solved" × Recovery's 65 "solvable") is tied to the exact equation-matching and classification rules used to produce it:
- The matching is index-based (equation[i] in both pipelines, same 991-equation population)
- E2E's "solved" requires only a non-empty `solved` field; no equality-condition filter is applied
- Recovery's `solvable=True` requires a validated sympy solution with an equality condition (`=` in latex)
- The shared population is 991 equations from the same arXiv HTML source

## Delimiter Integration Audit

Separate audit deliverable (B-14.1): see `DATASETS/b14_delimiter_integration_audit.json`. Key findings:
- Delimiter identity is preserved through `mathml_parser._tidy() -> balance_norm_tokens()` and `math_recovery_tool.normalize_latex_norms()`
- `batch_math_pipeline.py` makes no delimiter reference; no delimiter detection is integrated
- `e2e_math_pipeline.py` uses MathMLParser; delimiter identity is indirect via parser internals
- TALL delimiter test (test_delimiter_structural_recovery.py) could not be executed on this host (cv2/pymupdf/numpy version mismatch); manual probe of delimiter_identity gave 8/8 PASS
- Frozen regression baseline (docs/frozen-regression-execution-results-2026-11-03.md) covers border detection only; delimiter identity scope is 0

## Recommended Next Steps


1. E2E pipeline fix: Filter equations by equality condition (=) before applying solver; reject non-equality symbols

2. Recovery pipeline: 183 recoverable - 65 solved = 118 recoverable-but-unsuccessful; investigate why

3. B-14 status: Open - solver-policy definitions must be reconciled before either number is canonical


## Source Artifact SHA-256


| Artifact | SHA-256 |

|----------|---------|

| arxiv_html_corpus/2605.00155.json | 6bf463600a41aa9b |

| e2e_2605.00155.json | 58bbae4acdee424c |

| math_recovery/2605.00155_recovery.json | e23ca1143e57140b |
