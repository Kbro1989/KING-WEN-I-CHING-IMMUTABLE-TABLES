#!/usr/bin/env python3
"""Math Recovery Puzzle Box — Recovery Registry

Maps every version of the math recovery tools to the defect it fixed,
the regression it caused, and the evidence that confirms it.
This is the provenance map for the puzzle box.

SCHEMA:  version -> { defects_fixed[], regressions[], evidence[], status }

Status values:
    BASE       — unfixed baseline
    FIXED      — defect resolved, no known regressions
    FIX_WITH_REGRESSION — fixed but caused measurable regression elsewhere
    OBSOLETE   — superseded by a later version
    GLASS_WALL — not fixable without rewriting the pipeline

Usage:
    from math_recovery.recovery_registry import RECOVERY_VERSIONS

    for ver, info in RECOVERY_VERSIONS.items():
        print(f"{ver}: {info['status']} — {len(info['defects_fixed'])} fixed, "
              f"{len(info['regressions'])} regressions")
"""

RECOVERY_VERSIONS = {
    "v1_baseline": {
        "approaches": ["regex over LaTeX source", "MathML tree walk (arxiv_html_parser.py)"],
        "captures": ["14-paper corpus (3409 equations)"],
        "recoverable": 532, "recoverable_pct": 15.61,
        "solvable": 223, "solvable_pct": 6.54,
        "defects_fixed": [],
        "regressions": [],
        "evidence": ["scripts/numeric_extraction_results.json"],
        "status": "BASE",
    },
    "v2": {
        "approaches": ["same as v1 + nested-arg recovery via balanced-brace scanner"],
        "captures": ["nested \frac, \bar, \hat arguments"],
        "recoverable": 678, "recoverable_pct": 19.89,
        "solvable": 364, "solvable_pct": 10.68,
        "defects_fixed": [
            "nested arguments in \frac, \bar, \hat could not be matched by regex",
            "accent replacement could not consume backslash arguments"
        ],
        "regressions": [],
        "evidence": ["math_recovery_v2.json", "test_nested_args.py (21/21 pass)"],
        "status": "FIXED",
    },
    "v4": {
        "approaches": ["same as v2 + escaped-literal mapping"],
        "captures": ["\_ \& \% \# \$ \{ \} as literal characters"],
        "recoverable": 743, "recoverable_pct": 21.91,
        "solvable": 364, "solvable_pct": 10.68,
        "defects_fixed": [
            "escaped literals were treated as commands, causing line-continuation syntax errors"
        ],
        "regressions": [
            "solvable count 364 -> 360 (unknown commands regression in version comparison)"
        ],
        "evidence": ["math_recovery_v4.json", "test_mbox_dollar_recovery.py (9/9 pass)"],
        "status": "FIX_WITH_REGRESSION",
    },
    "v5": {
        "approaches": ["same as v4 + accent spacing fix"],
        "captures": ["\log\bar{\pi}(y) style constructs where accent fused to following symbol"],
        "recoverable": 747, "recoverable_pct": 21.91,
        "solvable": 377, "solvable_pct": 11.06,
        "defects_fixed": [
            "accent replacement had no separating space, causing \log to fuse with pi_bar"
        ],
        "regressions": [],
        "evidence": ["math_recovery_v5.json", "dungeon_level0_witness_identity.py (151 passed)"],
        "status": "FIXED",
    },
    "v6": {
        "approaches": ["same as v5 + function-argument joining"],
        "captures": ["\log\bar{\pi}(y^{(k)}\mid x) where argument group was detached"],
        "recoverable": 754, "recoverable_pct": 22.12,
        "solvable": 385, "solvable_pct": 11.29,
        "defects_fixed": [
            "detached argument groups after function calls",
            "\log\bar{\pi}(y^{(k)}\mid x) parsed as 'log(pi_bar) (y**((k)) x)'"
        ],
        "regressions": [],
        "evidence": ["math_recovery_v6.json", "test_nested_args.py (21/21 pass)"],
        "status": "FIXED",
    },
    "v8": {
        "approaches": ["same as v6 + tree path"],
        "captures": ["arxiv_html_corpus/*.json (MathML tree walk)"],
        "recoverable": 756, "recoverable_pct": 22.12,
        "solvable": 386, "solvable_pct": 11.32,
        "defects_fixed": [
            "canonical AST architecture (ExprNode tree, Integral IR)",
            "set-builder definitions (DefiniteIntegral) preserved through solver"
        ],
        "regressions": [],
        "evidence": ["scripts/e2e_math_pipeline.py", "test_math_contract.py (21 pass)"],
        "status": "FIXED",
    },
    "v9": {
        "approaches": ["same as v8 + structural fixes"],
        "captures": ["14-paper corpus, tree path"],
        "recoverable": 756, "recoverable_pct": 22.12,
        "solvable": 386, "solvable_pct": 11.32,
        "defects_fixed": [
            "max/min/^/‾/infinity missing from MO_MAP (dropped whole expression)",
            "mtable returned None discarding every row/cell",
            "\star/\ast superscripts emitted as '**()' (empty exponent)"
        ],
        "regressions": [],
        "evidence": ["math_recovery_v9.json"],
        "status": "FIXED",
    },
    "v10": {
        "approaches": ["same as v9 + relation identity"],
        "captures": ["relations \sim, \approx, \propto, \to distinguished"],
        "recoverable": 756, "recoverable_pct": 22.12,
        "solvable": 386, "solvable_pct": 11.32,
        "defects_fixed": [
            "the '~=' conflated 4 relations (sim/approx/simeq/cong)",
            "the '=' collapsed identity to equality (equiv lost)"
        ],
        "regressions": [],
        "evidence": ["math_recovery_v10.json", "test_relation_identity.py"],
        "status": "FIXED",
    },
    "v12": {
        "approaches": ["same as v10 + scoreboard discipline"],
        "captures": ["3409-equation corpus"],
        "recoverable": 756, "recoverable_pct": 22.12,
        "solvable": 386, "solvable_pct": 11.32,
        "defects_fixed": [
            "count_equalities() metric counted <= >= != as equations",
            "scoreboard reported phantom failures from glyph-vs-name comparison"
        ],
        "regressions": [],
        "evidence": ["math_recovery_v12.json", "semantic_honesty_scoreboard.py"],
        "status": "FIXED",
    },
    "v13": {
        "approaches": ["tree path (v12 + path assertion)"],
        "captures": ["2605.00155 (991 equations)"],
        "recoverable": 756, "recoverable_pct": 22.12,
        "solvable": 386, "solvable_pct": 11.32,
        "defects_fixed": [
            "method 4 annotation-source extraction dropped equations",
            "path discovery: source LaTeX vs recovered string validation"
        ],
        "regressions": [],
        "evidence": [
            "math_recovery_v13.json",
            "scripts/dungeon_quest_1_3.py (cross-generation match)",
            "scripts/semantic_honesty_scoreboard.py (FALSE_RECOVERY = 0)"
        ],
        "status": "GLASS_WALL",
    },
}

if __name__ == "__main__":
    for ver, info in RECOVERY_VERSIONS.items():
        print(f"{ver}: {info['status']} — {info['recoverable']}/{info['recoverable_pct']:.1f}%")
        if info['defects_fixed']:
            for d in info['defects_fixed']:
                print(f"    + {d}")
        if info['regressions']:
            for r in info['regressions']:
                print(f"    ! {r}")
    print(f"\nTotal versions: {len(RECOVERY_VERSIONS)}")
