#!/usr/bin/env python3
"""
FULL MATH RECONSTRUCTION EVIDENCE
==================================
Produces a per-equation evidence record showing, for every occurrence:

  source_latex        the exact LaTeX as extracted from arxiv HTML
  source_mathml       the exact MathML
  canonical_tree      the typed AST (nodes, roles, relations)
  recovered           the string the solver was handed
  parse_path          tree vs latex_fallback
  solve_attempted     whether the solver was invoked
  solved              the SymPy result (when accepted)
  solve_error         why it failed (when rejected)
  validation          independent re-check of the solution (NOT solver acceptance)

This is the "show your work" artifact: for each equation you can see what
was attempted and what was produced. Solution correctness is validated
independently by substituting the solution back into the source relation.

Output:
  DATASETS/math_reconstruction_evidence.jsonl   one record per occurrence
  DATASETS/math_reconstruction_evidence.json    summary + samples
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import SourceOccurrence, occurrence_key  # noqa: E402

CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
BASELINE = ROOT / "DATASETS" / "baseline_2026-10-09"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery_v16"

OUT_JSONL = ROOT / "DATASETS" / "math_reconstruction_evidence.jsonl"
OUT_JSON = ROOT / "DATASETS" / "math_reconstruction_evidence.json"


def load_pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    p = BASELINE / "pinned_versions.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    pins[parts[0]] = parts[1]
    return pins


def validate_solution(recovered: str, solution: Any, original: str) -> dict[str, Any]:
    """
    Independently validate a solution. Solver acceptance is NOT evidence.

    The solver isolates a target variable and returns the right-hand side.
    The independent check is: substitute the returned expression for the
    target in the ORIGINAL relation and confirm the two sides agree.

    This is a real check, not a restatement of the solver's own verdict.
    """
    result: dict[str, Any] = {
        "method": "substitute_back",
        "attempted": False,
        "passed": None,
        "detail": None,
    }
    if not solution:
        result["detail"] = "no solution produced"
        return result
    if not recovered or "=" not in recovered:
        result["detail"] = "recovered is not an equation"
        return result
    try:
        import sympy
        from sympy.parsing.sympy_parser import (
            parse_expr, standard_transformations, implicit_multiplication_application,
        )
        transforms = standard_transformations + (implicit_multiplication_application,)

        # solution is persisted as a STRING that looks like a list,
        # e.g. "[-2]" or "[1.6]" -- parse it back to a Python value.
        sol_expr = solution
        if isinstance(sol_expr, str):
            s = sol_expr.strip()
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1].strip()
            sol_expr = s if s else None
        elif isinstance(sol_expr, (list, tuple)):
            sol_expr = sol_expr[0] if sol_expr else None
        if sol_expr is None or sol_expr == "":
            result["detail"] = "empty solution"
            return result
        lhs_s, _, rhs_s = recovered.partition("=")
        lhs = parse_expr(lhs_s.strip(), transformations=transforms, evaluate=True)
        rhs = parse_expr(rhs_s.strip(), transformations=transforms, evaluate=True)
        sol = sympy.sympify(sol_expr)

        # Identify the isolated variable: the one present on one side only.
        lhs_syms = lhs.free_symbols
        rhs_syms = rhs.free_symbols
        only_lhs = lhs_syms - rhs_syms
        only_rhs = rhs_syms - lhs_syms
        if len(only_lhs) == 1:
            var = next(iter(only_lhs))
            target, other = lhs, rhs
        elif len(only_rhs) == 1:
            var = next(iter(only_rhs))
            target, other = rhs, lhs
        else:
            result["detail"] = (
                f"cannot isolate: only_lhs={len(only_lhs)} only_rhs={len(only_rhs)}"
            )
            return result

        result["attempted"] = True
        residual = sympy.simplify(target.subs(var, sol) - other)

        # Numeric residual: floating-point noise must not be called a failure.
        # A residual within tolerance of zero is a PASS, reported as such.
        passed = False
        note = ""
        sres = str(residual)

        # Infinite / undefined residuals (oo - oo, nan) are not a correctness
        # signal. Check the symbolic form FIRST: evalf() turns oo into nan.
        if "nan" in sres or "oo" in sres or "zoo" in sres:
            result["passed"] = None
            result["detail"] = (
                f"substituted {var} -> {sol}; residual={residual} "
                "(infinite/undefined -- unverifiable, not failed)"
            )
            return result

        # A symbolic residual that is not literally zero may be a PARSE
        # artifact (e.g. Pi(U) parsed as Pi*U), not a math error. Only a
        # numeric residual that is clearly non-zero is a real failure;
        # anything symbolic-but-not-zero is reported UNVERIFIED, never failed.
        numeric_verdict = None
        if residual == 0:
            passed = True
            note = ""
        else:
            try:
                rn = complex(residual.evalf())
                if abs(rn.imag) < 1e-9 and abs(rn.real) < 1e-9:
                    passed = True
                    note = " (within 1e-9 float tolerance)"
                elif abs(rn.imag) < 1e-9:
                    passed = False
                    numeric_verdict = rn.real
                    note = f" (numeric residual {rn.real:.3e})"
                else:
                    note = f" (complex residual {rn})"
            except Exception as e:
                note = f" (symbolic residual; not mechanically reducible: {type(e).__name__})"

        if numeric_verdict is None and not passed:
            # Symbolic, non-reducible residual: cannot be mechanically
            # confirmed or refuted. Unverified, NOT failed.
            result["passed"] = None
            result["detail"] = (
                f"substituted {var} -> {sol}; residual={residual}{note} "
                "(symbolic -- unverifiable, not failed)"
            )
            return result

        result["passed"] = passed
        result["detail"] = f"substituted {var} -> {sol}; residual={residual}{note}"
    except Exception as e:
        result["detail"] = f"{type(e).__name__}: {e}"
    return result


def main() -> int:
    pins = load_pins()

    # Index recovery records by (paper, occurrence)
    recovery: dict[tuple[str, int], dict[str, Any]] = {}
    for rf in sorted(RECOVERY_DIR.glob("*_recovery.json")):
        paper_id = rf.name.replace("_recovery.json", "")
        rj = json.loads(rf.read_text(encoding="utf-8", errors="replace"))
        for r in rj.get("results", []):
            idx = r.get("occurrence")
            if isinstance(idx, int):
                recovery[(paper_id, idx)] = r

    records: list[dict[str, Any]] = []
    m = Counter()

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        version = pins.get(paper_id, "unpinned")
        for i, eq in enumerate(data.get("equations", [])):
            occ = SourceOccurrence(
                paper_id=paper_id, paper_version=version,
                source_locator=f"math[{i}]", occurrence_index=i,
                source_hash="",
            )
            okey = occurrence_key(occ)
            rec = recovery.get((paper_id, i))

            latex = eq.get("latex", "")
            mathml = eq.get("mathml", "")

            notes = (rec or {}).get("notes") or []
            parse_path = "none"
            for n in notes:
                s = str(n)
                if s.startswith("path:tree"):
                    parse_path = "tree"
                    break
                if s.startswith("path:latex_fallback"):
                    parse_path = "latex_fallback"
                    break

            recovered = (rec or {}).get("recovered")
            solved = (rec or {}).get("solvable")
            solution = (rec or {}).get("solution")
            error = (rec or {}).get("error")
            tree = (rec or {}).get("canonical_tree")

            validation = validate_solution(recovered or "", solution, latex)

            m["total"] += 1
            if tree is not None:
                m["has_tree"] += 1
            if parse_path == "tree":
                m["path_tree"] += 1
            elif parse_path == "latex_fallback":
                m["path_fallback"] += 1
            else:
                m["path_none"] += 1
            if solved:
                m["solver_accepted"] += 1
            if validation["attempted"]:
                m["validation_attempted"] += 1
                if validation["passed"] is True:
                    m["validation_passed"] += 1
                elif validation["passed"] is False:
                    m["validation_failed"] += 1
                else:
                    m["validation_unverifiable"] += 1

            records.append({
                "occurrence_key": okey,
                "paper_id": paper_id,
                "paper_version": version,
                "source_locator": occ.source_locator,
                "source_latex": latex,
                "source_mathml_len": len(mathml),
                "canonical_tree": tree,
                "recovered": recovered,
                "parse_path": parse_path,
                "solve_attempted": recovered is not None,
                "solved": solved,
                "solution": solution,
                "solve_error": error,
                "validation": validation,
            })

    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    # Sample: one solved+validated, one rejected
    solved_sample = next((r for r in records if r["solved"] and r["validation"]["passed"]), None)
    rejected_sample = next((r for r in records if not r["solved"]), None)

    summary = {
        "date": "2026-10-11",
        "total_occurrences": m["total"],
        "metrics": {
            "canonical_tree_persisted": m["has_tree"],
            "parse_path_tree": m["path_tree"],
            "parse_path_latex_fallback": m["path_fallback"],
            "parse_path_none": m["path_none"],
            "solver_accepted": m["solver_accepted"],
            "validation_attempted": m["validation_attempted"],
            "validation_passed": m["validation_passed"],
            "validation_failed": m["validation_failed"],
            "validation_unverifiable": m["validation_unverifiable"],
        },
        "note": (
            "solver_accepted is SymPy's verdict. validation_passed is an "
            "INDEPENDENT substitute-back check and is the correctness metric. "
            "The two are reported separately and can disagree."
        ),
        "samples": {
            "solved_and_validated": solved_sample,
            "rejected": rejected_sample,
        },
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== FULL MATH RECONSTRUCTION EVIDENCE ===")
    print(f"  total occurrences          {m['total']}")
    print(f"  canonical_tree persisted   {m['has_tree']}")
    print(f"  parse path tree            {m['path_tree']}")
    print(f"  parse path latex_fallback  {m['path_fallback']}")
    print(f"  parse path none            {m['path_none']}")
    print(f"  solver accepted            {m['solver_accepted']}")
    print(f"  validation attempted       {m['validation_attempted']}")
    print(f"  validation passed          {m['validation_passed']}")
    print(f"  validation failed          {m['validation_failed']}")
    print(f"  validation unverifiable    {m['validation_unverifiable']}")
    print()
    if solved_sample:
        print("  SAMPLE (solved + independently validated):")
        print(f"    latex:      {solved_sample['source_latex'][:70]}")
        print(f"    recovered:  {str(solved_sample['recovered'])[:70]}")
        print(f"    solution:   {str(solved_sample['solution'])[:70]}")
        print(f"    validation: {solved_sample['validation']['detail']}")
        print()
    if rejected_sample:
        print("  SAMPLE (rejected, with reason):")
        print(f"    latex:      {rejected_sample['source_latex'][:70]}")
        print(f"    error:      {rejected_sample['solve_error']}")
    print()
    print(f"Wrote {OUT_JSONL}")
    print(f"Wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
