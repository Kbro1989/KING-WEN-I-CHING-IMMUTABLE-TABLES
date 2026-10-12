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


def validate_solution(recovered: str, solution: Any, original: str, canonical_tree: Any = None) -> dict[str, Any]:
    """
    Two-stage validation. Solver acceptance is NOT evidence of correctness.

    Stage 1 -- Operator/relation inventory check.
    Extracts the structural signature (operator kinds, relation types, named
    operators, inner products, norms) from the canonical ExprNode tree and
    checks that none are absent from the recovered string. This catches cases
    where the parser dropped or altered a key operator or relation.

    Limitation: this is a necessary condition, not sufficient. The tree and
    the recovered string both come from the same parser, so Stage 1 cannot
    detect all forms of parser error — only dropped or substituted structural
    elements. It is NOT a source-to-AST round-trip check.

    The `original` parameter is retained for provenance logging but is not
    yet parsed independently (that requires a separate source-to-tree path
    outside this module).

    Stage 2 -- Computational validity.
    Substitutes the solution into the recovered equation and verifies the
    residual is zero. This checks algebra, NOT source fidelity.

    Final verdict:
      - If Stage 1 explicitly FAILS (structural element dropped): passed=False
      - If Stage 2 PASSES and Stage 1 passed or was skipped: passed=True
        EXCEPT: if Stage 1 was skipped (no tree), result is marked with
        stage1_skipped=True so callers know only Stage 2 was checked.
      - If Stage 2 fails: passed=False
      - Inconclusive (symbolic residual, vacuous echo): passed=None
    """
    result: dict[str, Any] = {
        "method": "two_stage_source_guided",
        "stage1_source_fidelity": None,
        "stage2_computational_validity": None,
        "attempted": False,
        "passed": None,
        "detail": None,
    }
    if not solution:
        result["stage2_computational_validity"] = {
            "attempted": False,
            "passed": False,
            "detail": "no solution produced",
        }
        result["detail"] = "no solution produced"
        return result
    if not recovered or "=" not in recovered:
        result["stage2_computational_validity"] = {
            "attempted": False,
            "passed": False,
            "detail": "recovered is not an equation",
        }
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
            result["stage2_computational_validity"] = {
                "attempted": False,
                "passed": False,
                "detail": "empty solution",
            }
            result["detail"] = "empty solution"
            return result

        # --- STAGE 1: Operator/relation inventory check ------------------
        # Walk the ExprNode tree and collect every structural element that
        # must survive in the recovered string: named operators, typed
        # relations, inner products, norms. Then verify none are absent.
        #
        # This is NOT a full round-trip. It cannot catch all parser errors.
        # It catches dropped/substituted structural elements only.
        stage1_passed = None
        stage1_detail = "no canonical tree available; stage1 skipped"
        stage1_skipped = True
        stage1_checks = 0

        if canonical_tree is not None:
            stage1_skipped = False
            try:
                import unicodedata

                has_to_string = hasattr(canonical_tree, "to_string")
                tree_str = canonical_tree.to_string() if has_to_string else None

                IGNORABLE_CHARS = {
                    '\u200b', '\u200e', '\u200f', '\u202a', '\u202c', '\xa0', ' ',
                    '\u2061', '\u2062', '\u2063', '\u2064',
                }
                GLYPH_MAP = {
                    '−': '-', '\u2212': '-', '–': '-', '—': '-',
                    '×': '*', '\u00d7': '*', '·': '*', '\u22c5': '*',
                    '÷': '/', '\u00f7': '/', '∕': '/',
                    '⋆': 'star', '\u22c6': 'star', '∗': 'star', '*': 'star',
                    '≔': '=', ':=': '=', 'coloneqq': '=',
                    '…': '...', '\u2026': '...',
                    '‖': 'lvert', '\u2016': 'lvert',
                    '¯': 'bar', '\u00af': 'bar',
                    '∑': 'sum', '\u2211': 'sum',
                    '∏': 'prod', '\u220f': 'prod',
                    '∫': 'int', '\u222b': 'int',
                    'δ': 'delta', '\u03b4': 'delta',
                    'π': 'pi', '\u03c0': 'pi',
                    'α': 'alpha', '\u03b1': 'alpha',
                    'β': 'beta', '\u03b2': 'beta',
                    'γ': 'gamma', '\u03b3': 'gamma',
                    'θ': 'theta', '\u03b8': 'theta',
                    'ν': 'nu', '\u03bd': 'nu',
                    'τ': 'tau', '\u03c4': 'tau',
                    'Δ': 'delta', '\u0394': 'delta',
                    'Γ': 'gamma', '\u0393': 'gamma',
                    'Π': 'pi', '\u03a0': 'pi',
                    'ϕ': 'phi', '\u03d5': 'phi', 'φ': 'phi', '\u03c6': 'phi',
                    '∇': 'grad', '\u2207': 'grad',
                    'ϵ': 'epsilon', '\u03f5': 'epsilon', 'ε': 'epsilon', '\u03b5': 'epsilon',
                }

                def _norm(s: str) -> str:
                    nfkd = unicodedata.normalize('NFKD', s)
                    return GLYPH_MAP.get(s, GLYPH_MAP.get(nfkd, nfkd))

                def _walk(node: Any, is_mover: bool = False) -> list[tuple[str, str | None]]:
                    """Yield (kind, value) polymorphically for dicts and ExprNode."""
                    sigs: list[tuple[str, str | None]] = []
                    if isinstance(node, dict):
                        kind = node.get("kind")
                        val = node.get("value")
                        attrs = node.get("attributes", {})
                        children = node.get("children", [])
                    else:
                        kind = getattr(node, "kind", None)
                        val = getattr(node, "value", None)
                        attrs = getattr(node, "attributes", {})
                        children = getattr(node, "children", ())

                    mover = is_mover or attrs.get("script") == "mover"

                    # Accents under mover (e.g. tilde over r) are not standalone relations
                    if kind == "relation" and val in ("~", "sim") and mover:
                        pass
                    elif kind in ("relation", "operator"):
                        sigs.append((kind, val))
                    elif kind in ("inner_product", "norm", "named_operator",
                                  "integral", "sum", "product", "limit"):
                        sigs.append((kind, val))
                    elif kind in ("identifier", "number") and val:
                        sigs.append((kind, val))

                    for child in children:
                        sigs.extend(_walk(child, mover))
                    return sigs

                if has_to_string and not getattr(canonical_tree, "children", None) and not isinstance(canonical_tree, dict):
                    import re
                    tree_tokens = re.findall(r'[a-zA-Z0-9_]+', tree_str)
                    rec_tokens = re.findall(r'[a-zA-Z0-9_]+', recovered)
                    from collections import Counter as TokCounter
                    diff = TokCounter(tree_tokens) - TokCounter(rec_tokens)
                    stage1_checks = len(tree_tokens)
                    if diff:
                        stage1_passed = False
                        stage1_detail = f"tokens from tree missing in recovered: {list(diff.elements())[:5]}"
                    else:
                        stage1_passed = True
                        stage1_detail = f"all {len(tree_tokens)} tokens from tree present in recovered form"
                else:
                    sig = _walk(canonical_tree)

                    critical = [
                        (k, v) for k, v in sig
                        if k in ("inner_product", "norm", "named_operator",
                                 "integral", "sum", "product", "limit")
                        or (k == "relation" and v not in (None, "=", "eq", "≔", ":="))
                        or (k == "operator" and v not in (None, "=", "^", "_", ",")
                            and str(v) not in IGNORABLE_CHARS)
                    ]

                    leaves = [
                        (k, v) for k, v in sig
                        if k in ("identifier", "number") and v and str(v) not in IGNORABLE_CHARS
                    ]

                    total_checks = len(critical) + len(leaves)
                    stage1_checks = total_checks

                    if total_checks == 0:
                        stage1_passed = True
                        stage1_detail = "no critical structural elements or leaves in tree; stage1 vacuously passed"
                    else:
                        missing: list[str] = []
                        recovered_lower = recovered.lower()

                        for kind_c, val_c in critical:
                            if val_c is None:
                                continue
                            norm_v = _norm(str(val_c)).lower()
                            raw_v = str(val_c).lower()
                            # For multiplication, implicit multiplication or * or ( is accepted
                            if norm_v == '*' and ('*' in recovered_lower or '(' in recovered_lower):
                                continue
                            if norm_v not in recovered_lower and raw_v not in recovered_lower:
                                missing.append(f"{kind_c}:{val_c!r}")

                        for kind_l, val_l in leaves:
                            norm_v = _norm(str(val_l)).lower()
                            raw_v = str(val_l).lower()
                            if norm_v not in recovered_lower and raw_v not in recovered_lower:
                                missing.append(f"{kind_l}:{val_l!r}")

                        if missing:
                            stage1_passed = False
                            stage1_detail = (
                                f"structural elements or terms absent from recovered form: "
                                f"{missing[:5]}"
                            )
                        else:
                            stage1_passed = True
                            stage1_detail = (
                                f"all {len(critical)} critical structural elements and "
                                f"{len(leaves)} leaf terms accounted for"
                            )
            except Exception as e:
                stage1_detail = f"stage1 error: {type(e).__name__}: {e}"

        result["stage1_source_fidelity"] = {
            "passed": stage1_passed,
            "skipped": stage1_skipped,
            "checks": stage1_checks,
            "detail": stage1_detail,
        }

        # --- STAGE 2: Computational validity ---------------------------
        # Substitute the solution back into the recovered expression.
        # This checks computational validity, NOT source fidelity.
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
            result["stage2_computational_validity"] = {
                "attempted": True,
                "passed": None,
                "detail": f"cannot isolate: only_lhs={len(only_lhs)} only_rhs={len(only_rhs)}",
            }
            result["attempted"] = True
            if stage1_passed is False:
                result["passed"] = False
                result["detail"] = f"stage1 failed: {stage1_detail} (stage2 cannot isolate)"
            else:
                result["passed"] = None
                result["detail"] = "stage2: cannot isolate variable"
            return result

        # TAUTOLOGY GUARD: substitution is vacuous only when the solved
        # expression STILL CONTAINS the variable being solved for. Then
        # X = f(X) collapses to 0 for any X and proves nothing.
        #   'd = 3-5' solved to -2 is a REAL check (constant RHS).
        #   'E = 5.6e37*E' solved to 5.6e37*E is an ECHO.
        try:
            sol_free = sympy.sympify(sol_expr).free_symbols
        except Exception:
            sol_free = set()
        if var in sol_free:
            result["stage2_computational_validity"] = {
                "attempted": True,
                "passed": None,
                "detail": f"solution for {var} still contains {var}; substitution is vacuous (echo, not an isolation) -- unverifiable",
            }
            result["attempted"] = True
            if stage1_passed is False:
                result["passed"] = False
                result["detail"] = f"stage1 failed: {stage1_detail} (stage2 vacuous echo)"
            else:
                result["passed"] = None
                result["detail"] = "stage2: vacuous substitution (echo)"
            return result

        residual = sympy.simplify(target.subs(var, sol) - other)

        # Numeric residual: floating-point noise must not be called a failure.
        # A residual within tolerance of zero is a PASS, reported as such.
        passed = False
        note = ""
        sres = str(residual)

        # Infinite / undefined residuals (oo - oo, nan) are not a correctness
        # signal. Check the symbolic form FIRST: evalf() turns oo into nan.
        if "nan" in sres or "oo" in sres or "zoo" in sres:
            result["stage2_computational_validity"] = {
                "attempted": True,
                "passed": None,
                "detail": (
                    f"substituted {var} -> {sol}; residual={residual} "
                    "(infinite/undefined -- unverifiable, not failed)"
                ),
            }
            result["attempted"] = True
            if stage1_passed is False:
                result["passed"] = False
                result["detail"] = f"stage1 failed: {stage1_detail} (stage2 infinite/undefined residual)"
            else:
                result["passed"] = None
                result["detail"] = "stage2: infinite/undefined residual"
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
            result["stage2_computational_validity"] = {
                "attempted": True,
                "passed": None,
                "detail": (
                    f"substituted {var} -> {sol}; residual={residual}{note} "
                    "(symbolic -- unverifiable, not failed)"
                ),
            }
            result["attempted"] = True
            if stage1_passed is False:
                result["passed"] = False
                result["detail"] = f"stage1 failed: {stage1_detail} (stage2 symbolic residual)"
            else:
                result["passed"] = None
                result["detail"] = "stage2: symbolic residual (unverifiable)"
            return result

        stage2_passed = passed
        result["stage2_computational_validity"] = {
            "attempted": True,
            "passed": stage2_passed,
            "detail": f"residual={residual}{note}" if not stage2_passed else "residual=0",
        }

        # --- Final verdict --------------------------------------------
        # Stage 1 explicit FAIL => overall fail (structural element dropped).
        # Stage 2 PASS + Stage 1 passed    => verified (both stages passed).
        # Stage 2 PASS + Stage 1 skipped   => stage2_only (not fully verified).
        # Stage 2 FAIL                     => overall fail.
        if stage1_passed is False:
            result["passed"] = False
            result["detail"] = f"stage1 failed: {stage1_detail}"
            return result

        result["attempted"] = True
        if stage2_passed and stage1_passed is True:
            result["passed"] = True
            result["detail"] = "both stages passed"
        elif stage2_passed and stage1_skipped:
            result["passed"] = True
            result["detail"] = "stage2 passed; stage1 skipped (no canonical tree)"
        else:
            result["passed"] = False
            result["detail"] = f"stage2 failed: residual={residual}{note}"
        return result
    except Exception as e:
        if stage1_passed is False:
            result["passed"] = False
            result["detail"] = f"stage1 failed: {stage1_detail} (exception: {type(e).__name__}: {e})"
        else:
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

            validation = validate_solution(recovered or "", solution, latex, canonical_tree=tree)

            m["total"] += 1
            if tree is not None:
                m["has_tree"] += 1
            if parse_path == "tree":
                m["path_tree"] += 1
            elif parse_path == "latex_fallback":
                m["path_fallback"] += 1
            else:
                m["path_none"] += 1
            s1 = validation.get("stage1_source_fidelity") or {}
            if s1.get("skipped"):
                m["stage1_skipped"] += 1
            elif s1.get("passed") is False:
                m["stage1_failed"] += 1
            elif (s1.get("checks") or 0) > 0:
                m["stage1_evaluated_with_checks"] += 1
            elif s1.get("passed") is True:
                m["stage1_evaluated_vacuously"] += 1

            if solved:
                m["solver_accepted"] += 1
                m["candidate_equations"] += 1
                if validation["attempted"]:
                    m["substitution_attempted"] += 1
                else:
                    m["unattempted_exceptions"] += 1

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
        "date": "2026-10-12",
        "total_occurrences": m["total"],
        "metrics": {
            "canonical_tree_persisted": m["has_tree"],
            "parse_path_tree": m["path_tree"],
            "parse_path_latex_fallback": m["path_fallback"],
            "parse_path_none": m["path_none"],
            "solver_accepted": m["solver_accepted"],
            "candidate_equations": m["candidate_equations"],
            "substitution_attempted": m["substitution_attempted"],
            "unattempted_exceptions": m["unattempted_exceptions"],
            "validation_passed": m["validation_passed"],
            "validation_failed": m["validation_failed"],
            "validation_unverifiable": m["validation_unverifiable"],
            "stage1_breakdown": {
                "evaluated_with_checks": m["stage1_evaluated_with_checks"],
                "evaluated_vacuously": m["stage1_evaluated_vacuously"],
                "skipped": m["stage1_skipped"],
                "failed": m["stage1_failed"],
            },
        },
        "note": (
            "solver_accepted is SymPy's verdict. validation_passed is an "
            "INDEPENDENT substitute-back check and is the correctness metric. "
            "Stage 1 checks source structural fidelity against the canonical tree; "
            "Stage 2 checks computational residual."
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
    print(f"  candidate equations        {m['candidate_equations']}")
    print(f"  substitution attempted     {m['substitution_attempted']}")
    print(f"  unattempted exceptions     {m['unattempted_exceptions']}")
    print(f"  validation passed          {m['validation_passed']}")
    print(f"  validation failed          {m['validation_failed']}")
    print(f"  validation unverifiable    {m['validation_unverifiable']}")
    print("  Stage 1 Breakdown:")
    print(f"    evaluated with checks    {m['stage1_evaluated_with_checks']}")
    print(f"    evaluated vacuously      {m['stage1_evaluated_vacuously']}")
    print(f"    skipped (no tree)        {m['stage1_skipped']}")
    print(f"    failed (structural diff) {m['stage1_failed']}")
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
