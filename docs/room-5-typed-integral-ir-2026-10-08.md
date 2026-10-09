# Room 5 — Typed Integral IR + Honest Equation Metric

**Date:** 2026-10-08
**Corpus:** 14-paper arxiv HTML, 3,409 equations
**Script:** `scripts/test_integral_ir.py` (5/5 fixtures pass)

---

## What Room 5 establishes

| Invariant | Status | What it protects |
|----------|--------|------------------|
| Occurrence conservation | Verified, 3,409/3,409 across five runs | No source equation silently disappears |
| Structural conservation | 21/21 fixtures | No MathML child dropped |
| Relation identity | 21/21 fixtures | `\sim` ≠ `\approx` ≠ `\simeq` ≠ `\cong` |
| **Typed Integral IR** | **5/5 fixtures** | `dz` is a typed node, not a substring |
| **Honest equation metric** | **667 recoverable (19.6%)** | `<=`/`>=` no longer counted as equations |

---

## The Typed Integral IR

```python
Integral(
    body     = Application(phi, z),
    limits   = {lower: alpha, upper: infinity},
    measure  = Differential(z),
)
```

**Acceptance criteria (all met):**

1. **Independent fields** — integrand, lower, upper, differential are separate dict keys
2. **Scope preservation** — `z` in `dz` is the integration variable, not appended to body
3. **Nested expression safety** — `\int_a^b f(g(z)) dz` preserves nesting
4. **Limit variation** — definite, indefinite, lower-only, upper-only all handled
5. **Conservation** — every source occurrence represented
6. **Honest fallback** — missing differential → `measure=None` + `"measure_missing"` note, never a fabricated integral
7. **Regression** — structural (21/21), nested-arg (21/21), relation-identity (21/21), mbox-dollar (9/9) all intact

**Fixtures:**

```
definite:    body='phi(z)'  limits={alpha, oo}  measure=Differential(z)
nested:      body='f(g(z))' limits={a, b}       measure=Differential(z)
indefinite:  body='phi(z)'  limits={None,None}  measure=Differential(z)
lower-only:  body='f(z)'    limits={a, None}    measure=Differential(z)
no-diff:     body='f(z)'    limits={a, b}       measure=None + "measure_missing"
```

---

## The Honest Equation Metric (v15)

**The bug:** `recovered.count('=') == 1` counts `<=` and `>=` as equations because they contain `=`.

**v14 (inflated):** 721 "recoverable" — 77 were inequalities (`p,q>=1`, `delta>=0`, `|Delta|_p*<=delta`)

**v15 (honest):** 667 recoverable (19.6%), 331 solvable (9.7%)

```python
def count_equalities(s: str) -> int:
    """Count TRUE equality signs, excluding <=, >=, !=, and fused tokens."""
    s = re.sub(r'<=|>=|!=|\\leq|\\geq|\\neq|≤|≥|≠', '', s)
    s = re.sub(r'_eq_', '', s)  # fused limit token from big-operator pass
    return s.count('=')
```

**Verified on 9 test cases:** `a=b`→1, `sim*17.6/100`→0, `x~=y`→0, `a=b+c=d`→2, `E_RsimP_0[R(x)]=s(x)`→1, `L_X*approx*5.4`→0, `a!=b`→0, `a<=b`→0, `x_eq_1`→0.

---

## Scoreboard (v15 honest)

```
class                       v6 regex        v12 tree        v13 tree       v14 relid      v15 honest
--------------------------------------------------------------------------------------------
EXACT                     2687 (78.8%)      2525 (74.1%)      2528 (74.2%)      2517 (73.8%)      2517 (73.8%)
STRUCTURAL_EQUIV           116 ( 3.4%)       336 ( 9.9%)       336 ( 9.9%)       347 (10.2%)       347 (10.2%)
LOSSY                      553 (16.2%)       547 (16.0%)       544 (16.0%)       544 (16.0%)       544 (16.0%)
CORRUPTED                    0 ( 0.0%)         0 ( 0.0%)         0 ( 0.0%)         0 ( 0.0%)         0 ( 0.0%)
FALSE_RECOVERY              46 ( 1.3%)         0 ( 0.0%)         0 ( 0.0%)         0 ( 0.0%)         0 ( 0.0%)
UNRECOVERED                  7 ( 0.2%)         1 ( 0.0%)         1 ( 0.0%)         1 ( 0.0%)         1 ( 0.0%)
--------------------------------------------------------------------------------------------
TOTAL                           3409            3409            3409            3409            3409
```

**Headline:** v15 honest = 2864 structurally faithful (84.0%), 0 FALSE_RECOVERY.

---

## Progression

| Version | Recoverable | Solvable | Parse Failures | Notes |
|---------|-------------|----------|----------------|-------|
| v1 | 532 (15.6%) | 223 (6.5%) | 376 | Baseline |
| v2 | 678 (19.9%) | 364 (10.7%) | 161 | Nested args |
| v3 | 743 (21.8%) | 360 (10.6%) | 158 | Big-op limits (regression) |
| v4 | 747 (21.9%) | 377 (11.1%) | 152 | Escaped literals |
| v5 | 754 (22.1%) | 385 (11.3%) | 139 | Accent padding |
| v6 | 756 (22.2%) | 386 (11.3%) | 139 | Function-arg join (no change) |
| v12 tree | 798 (23.4%) | 332 ( 9.7%) | 116 | MathML tree path |
| v13 tree | 798 (23.4%) | 330 ( 9.7%) | 116 | Structural conservation |
| v14 relid | 721 (21.2%) | 331 ( 9.7%) | — | Relation identity (inflated) |
| **v15 honest** | **667 (19.6%)** | **331 ( 9.7%)** | — | **Corrected metric** |

---

## Key Lessons

1. **Substring counting is not semantic analysis.** `count('=')` counts `<=`, `>=`, `!=`, and fused tokens. The corrected `count_equalities()` strips these first.

2. **A fix in one place exposes a bug in another.** The nested-frac fix (v2) exposed the big-operator limit bug (v3 regression). The accent padding fix (v5) exposed the function-arg join bug (v6 no-change). Each fix must be diffed against ALL buckets, not just the headline.

3. **The tree path is more honest than the regex path.** v6 regex: 46 FALSE_RECOVERY. v12 tree: 0 FALSE_RECOVERY. The tree path preserves relations; the regex path manufactures `=` from `\sim` and `\to`.

4. **Typed IR > string presence.** `dz` in the output string does not establish that `z` is the integration variable. The typed `Differential(variable=z)` node does.

5. **Honest fallback > fabricated completeness.** The no-differential fixture returns `measure=None` + `"measure_missing"`, not a fabricated integral. This is the correct behavior for a parser that values semantic honesty over solver acceptance.

---

## Files

- `scripts/test_integral_ir.py` — 5/5 typed Integral IR fixtures
- `scripts/math_recovery_tool.py` — corrected `count_equalities()` function
- `scripts/semantic_honesty_scoreboard.py` — v15 honest column + argparse
- `DATASETS/math_recovery_v15/` — full recovery output (14 papers)
- `DATASETS/scoreboard_v15.json` — scoreboard artifact (verified on disk)

---

## Verification

```
test_integral_ir.py               PASS   (5/5)
test_structural_conservation.py   PASS   (21/21)
test_relation_identity.py         PASS   (21/21)
test_nested_args.py               PASS   (21/21)
test_mbox_dollar_recovery.py      PASS   (9/9)
npm test                          2/2
py_compile (all changed)          OK
```

Artifact readback: `DATASETS/scoreboard_v15.json` — v15 honest occurrences=3409,
structurally_faithful=2864, false_recovery=0, bucket sum 3409 == 3409.

---

## Defect found during verification (measurement layer again)

`semantic_honesty_scoreboard.py` had **no argument parsing at all**. `--output`
was silently ignored, so an earlier claim that `DATASETS/scoreboard_v15.json`
had been written was **false** — the file did not exist. This is the fifth
measurement-layer defect in this line of work (after the dropped corpus field,
the glyph-vs-transliteration checker, the `\in`/`\infty` prefix match, and the
subscript relation count).

**Fix:** added `argparse` with `--corpus`, `--recovery`, `--output`, `--gens`,
and a JSON emitter that derives `structurally_faithful` from the buckets.

**Rule reinforced:** never claim an artifact exists without reading it back.
`ls` on the path, then parse it, then assert its internal conservation law.
