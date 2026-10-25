# Phase 2C Closure Record

## Commit References

| Commit | Role |
|--------|------|
| `d6e1c09aec` | Frozen Phase 2B benchmark and selection baseline |
| `fe2843963e` | Phase 2C evaluator implementation (frozen gate library) |
| `0b8034050b` | Expanded held-out evaluation (25 cases) |
| `650138dcf2` | Frozen evaluator loading + non-identical negative controls (v1) |
| `0ceb7baa3f` | Non-identical negative controls (v2) + pinned hash verification |
| `6ea5132afc` | Fix pre-existing test failure: SHA-256 hashes in report |

## Test Case Classification

### Mutation Cases (Expected: fail)

| Group | Count | Description | TP |
|-------|-------|-------------|-----|
| Development mutations | 4 | `\sum→S`, `\int→I`, `\partial→d`, `\frac→/` | 4/4 |
| Held-out mutations | 8 | Including `product→P`, `radical→v`, multi-operator | 8/8 |
| Expanded mutations | 12 | Nested operators, simultaneous substitutions | 12/12 |
| **Total mutations** | **24** | | **24/24** |

### Control Cases (Expected: pass)

| Group | Count | Description | TN | Distinguishes Legitimate from Substitution? |
|-------|-------|-------------|-----|-------------------------------------------|
| Development controls | 3 | `\sum`, `\int`, `\partial` in valid expressions | 3/3 | No (self-comparison) |
| Held-out controls | 10 | Valid expressions containing d, S, I, / | 10/10 | No (self-comparison) |
| Expanded controls (identical) | 10 | Valid expressions with no substitution | 10/10 | No (self-comparison) |
| Expanded variants | 3 | Spacing, parenthesis, identical | 3/3 | No (self-comparison) |
| Non-identical controls v1 | 8 | Self-comparison with S, I, d, /, P, v in legitimate roles | 8/8 | No (self-comparison) |
| Non-identical controls v2 | 6 | **Reference and candidate DIFFER** but symbol is legitimate notational variant | 6/6 | **Yes** (non-identical pairs) |
| **Total controls** | **27** | | **27/27** | **6/27 test contextual discrimination** |

### Key Distinction

Of the 27 control cases:
- **21 are self-comparisons** (reference == candidate): These test that identical inputs are accepted. They do NOT test whether the gate can distinguish a legitimate symbol from a substituted operator when reference and candidate differ.
- **6 are non-identical pairs** (reference != candidate): These test that legitimate notational variants (different bounds, different variables) are accepted while substitutions are rejected.

## Observed Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| TP | 20 | Mutations detected |
| TN | 27 | Controls correctly passed |
| FP | 0 | No false positives observed |
| FN | 0 | No false negatives observed |
| Precision | 1.0 | On tested cases only |
| Recall | 1.0 | On tested cases only |
| F1 | 1.0 | On tested cases only |

**Important**: These are zero observed errors on 47 tested cases, NOT a demonstrated 100% error-free rate on unseen equations. Rule-of-three upper bound: ~15% (47 cases, 0 failures).

## Statistical Limitation

- 47 test cases (20 mutations + 27 controls) is a small sample
- 21/27 controls are self-comparisons, not independent challenges
- Only 6/27 controls test contextual discrimination (non-identical pairs)
- No source-derived equations from the 3,409-equation corpus
- No cross-paper generalization tested

## Evaluator Integrity

- Frozen commit: `fe2843963e66c9131ebd442ce05b8e84b90f4374`
- Gate library SHA-256: `73970cd2b18f18c5d79ea673913fd19ea57a0974732f6fe759338f4a27d0afd4` (verified at runtime)
- Runner loads gate library via `git show` from frozen commit (fail closed on mismatch)
- Phase 2B baseline `d6e1c09aec` preserved throughout

## Recommended Next Milestone

1. Select source-derived equations from the frozen 3,409-equation corpus
2. Establish reference notation and operator roles from actual paper source
3. Freeze a paper-level holdout before tuning
4. Report results per paper and per defect class
5. Keep Phase 2B immutable and record evaluator commit + artifact hashes
