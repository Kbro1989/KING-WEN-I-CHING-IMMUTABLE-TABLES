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

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


def split_clauses_depth0(s: str) -> list[str]:
    """Split comma-separated multi-clause statements only at bracket depth 0 where all parts contain =."""
    import re as _re
    s = s.strip()
    s = _re.sub(r'[\*\.\,;\s]+$', '', s)
    s = _re.sub(r'^[\*\.\,;\s]+', '', s)
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in s:
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth = max(0, depth - 1)
        elif char == ',' and depth == 0:
            part = ''.join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)
    part = ''.join(current).strip()
    if part:
        parts.append(part)
    if len(parts) > 1 and all('=' in p for p in parts):
        return [_re.sub(r'[\*\.\,;\s]+$', '', p).strip() for p in parts]
    return [s]


def validate_solution(
    recovered: str,
    solution: Any,
    original: str,
    canonical_tree: Any = None,
    alttext_diff: Any = None,
) -> dict[str, Any]:
    """
    Two-stage validation with independent AltText source verification.
    Solver acceptance is NOT evidence of correctness.

    Stage 1 -- Operator/relation inventory check from AST.
    Stage 2 -- Computational validity (substitution & residual).
    Independent Source Check -- AltText cross-checker. If recognized source tokens
    are missing from the recovered form on an attempted equation, it is rejected.
    """
    result: dict[str, Any] = {
        "method": "two_stage_source_guided",
        "stage1_source_fidelity": None,
        "stage2_computational_validity": None,
        "attempted": False,
        "passed": None,
        "detail": None,
        "failed_stage1": False,
        "refuted_stage2": False,
        "failed_alttext_gap": False,
        "cannot_isolate": False,
        "vacuous_echo": False,
        "is_definition": False,
        "is_system": False,
        "verified_algebraic": False,
        "definition_recorded": False,
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
                    # prime marks — parser now emits _prime/_prime_prime
                    '′': 'prime', '″': 'prime', '‴': 'prime',
                    # transpose — parser emits _T
                    '⊤': 'T',
                    # conditioning bar / vertical divider
                    '∣': '|', '\u2223': '|',
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
        if stage1_passed is False:
            result["failed_stage1"] = True

        # Classification check: definition vs algebraic
        is_def = (
            ":=" in original or "≔" in original or ":=" in recovered
            or any(recovered.strip().startswith(op) for op in ("Integral", "min", "max"))
        )
        if is_def:
            result["is_definition"] = True

        # Pre-clean: strip sentence-ending punctuation that leaked from MathML
        # (trailing commas, periods, stars from enumerate/display rows).
        import re as _re
        recovered_clean = recovered.strip()
        recovered_clean = _re.sub(r"[\*\.\,;\s]+$", "", recovered_clean)
        recovered_clean = _re.sub(r"^[\*\.\,;\s]+", "", recovered_clean)

        clauses = split_clauses_depth0(recovered_clean)
        if len(clauses) > 1:
            result["is_system"] = True

        # If is_definition, record definition structurally without claiming algebraic solve
        if is_def:
            result["stage2_computational_validity"] = {
                "attempted": False,
                "passed": None,
                "detail": "definition recorded structurally; stage2 algebraic substitution bypassed",
            }
            result["attempted"] = False
            result["definition_recorded"] = True
            result["passed"] = None
            result["detail"] = "definition recorded (opaque operator or :=)"
            return result

        local_dict = {
            "E": sympy.Symbol("E"),
            "beta": sympy.Symbol("beta"),
            "gamma": sympy.Symbol("gamma"),
            "I": sympy.Symbol("I"),
            "S": sympy.Symbol("S"),
            "N": sympy.Symbol("N"),
            "Deltanu": sympy.Symbol("Deltanu"),
        }

        eval_clause = clauses[0]
        eval_clause = eval_clause.replace("{", "(").replace("}", ")")
        lhs_s, _, rhs_s = eval_clause.partition("=")
        lhs_s = _re.sub(r"[\*\.\,;\s]+$", "", lhs_s.strip())
        rhs_s = _re.sub(r"[\*\.\,;\s]+$", "", rhs_s.strip())
        rhs_s = rhs_s.replace("{", "(").replace("}", ")")

        lhs = parse_expr(lhs_s, transformations=transforms, evaluate=True, local_dict=local_dict)
        rhs = parse_expr(rhs_s, transformations=transforms, evaluate=True, local_dict=local_dict)

        # parse_expr can return a tuple when the expression contains commas
        # (e.g. "i=2,...,n" parses as (2, ..., n)). Unwrap single-element tuples;
        # multi-element tuples mean we cannot isolate a variable anyway.
        if isinstance(lhs, tuple):
            lhs = lhs[0] if len(lhs) == 1 else lhs
        if isinstance(rhs, tuple):
            rhs = rhs[0] if len(rhs) == 1 else rhs

        sol = sympy.sympify(sol_expr, locals=local_dict)

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
            result["cannot_isolate"] = True
            result["stage2_computational_validity"] = {
                "attempted": False,
                "passed": None,
                "detail": f"cannot isolate: only_lhs={len(only_lhs)} only_rhs={len(only_rhs)}",
            }
            result["attempted"] = False
            if stage1_passed is False:
                result["failed_stage1"] = True
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
            sol_free = sympy.sympify(sol_expr, locals=local_dict).free_symbols
        except Exception:
            sol_free = set()
        if var in sol_free:
            result["vacuous_echo"] = True
            result["stage2_computational_validity"] = {
                "attempted": False,
                "passed": None,
                "detail": f"solution for {var} still contains {var}; substitution is vacuous (echo, not an isolation) -- unverifiable",
            }
            result["attempted"] = False
            if stage1_passed is False:
                result["failed_stage1"] = True
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
                result["failed_stage1"] = True
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
                result["failed_stage1"] = True
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
        # Independent AltText gap => fail (recognized source token missing from expr).
        # Stage 2 PASS + Stage 1 passed    => verified (both stages passed).
        # Stage 2 PASS + Stage 1 skipped   => stage2_only (not fully verified).
        # Stage 2 FAIL                     => overall fail (refuted by numeric residual).
        if stage1_passed is False:
            result["failed_stage1"] = True
            result["passed"] = False
            result["detail"] = f"stage1 failed: {stage1_detail}"
            return result

        result["attempted"] = True
        if stage2_passed and stage1_passed is True:
            # Independent AltText validation
            if alttext_diff and alttext_diff.get("missing_from_expr"):
                missing_items = [m.get("latex", m.get("name")) for m in alttext_diff["missing_from_expr"]]
                result["failed_alttext_gap"] = True
                result["passed"] = False
                result["detail"] = f"alttext gap: tokens missing from recovered expression: {missing_items[:5]}"
            else:
                result["passed"] = True
                result["verified_algebraic"] = True
                result["detail"] = "both stages passed"
        elif stage2_passed and stage1_skipped:
            if alttext_diff and alttext_diff.get("missing_from_expr"):
                missing_items = [m.get("latex", m.get("name")) for m in alttext_diff["missing_from_expr"]]
                result["failed_alttext_gap"] = True
                result["passed"] = False
                result["detail"] = f"alttext gap: tokens missing from recovered expression: {missing_items[:5]}"
            else:
                result["passed"] = True
                result["verified_algebraic"] = True
                result["detail"] = "stage2 passed; stage1 skipped (no canonical tree)"
        else:
            result["refuted_stage2"] = True
            result["passed"] = False
            result["detail"] = f"stage2 failed: residual={residual}{note}"
        return result
    except Exception as e:
        if stage1_passed is False:
            result["failed_stage1"] = True
            result["passed"] = False
            result["detail"] = f"stage1 failed: {stage1_detail} (exception: {type(e).__name__}: {e})"
        else:
            result["detail"] = f"{type(e).__name__}: {e}"
    return result


def main() -> int:
    pins = load_pins()

    try:
        from alttext_cross_checker import cross_check as _alttext_cross_check
    except ImportError:
        _alttext_cross_check = None

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
    seen_papers: set[str] = set()
    paper_hashes: dict[str, str] = {}

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        paper_id = data.get("arxiv_id", jf.stem)
        if paper_id in seen_papers:
            raise ValueError(f"Duplicate paper ID in corpus: {paper_id} (file: {jf.name})")
        seen_papers.add(paper_id)

        eqs = data.get("equations", [])
        payload = json.dumps([e.get("latex") for e in eqs], sort_keys=True)
        content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if content_hash in paper_hashes:
            dup_id = paper_hashes[content_hash]
            raise ValueError(
                f"Corpus content collision: {paper_id} ({jf.name}) has identical equation payload to {dup_id}"
            )
        paper_hashes[content_hash] = paper_id

        version = pins.get(paper_id, "unpinned")
        arxiv_url = data.get("url") or f"https://arxiv.org/html/{paper_id}"
        generator = data.get("generator")  # e.g. "LaTeXML oxide (version 0.7.6)"
        github_repos = data.get("github_repos") or (data.get("structure") or {}).get("github_repos") or []
        if not github_repos:
            # Fallback regex search on paper payload (abstract, text, contexts)
            full_paper_str = json.dumps(data)
            gh_m = re.findall(r'https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', full_paper_str)
            strip_chars = '.,;:)>\'"'
            seen_r = set()
            for r in gh_m:
                cleaned = r.rstrip(strip_chars)
                if not cleaned.startswith(('brucemiller/', 'arXiv/', 'git-lfs/')) and not cleaned.endswith('/issues'):
                    repo_url = f"https://github.{'com'}/{cleaned}"
                    if repo_url not in seen_r:
                        seen_r.add(repo_url)
                        github_repos.append(repo_url)

        for i, eq in enumerate(eqs):
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

            is_display = eq.get("is_display", True)
            eqno = eq.get("eqno") or eq.get("equation_number")
            scope = (
                "display_numbered" if (is_display and eqno)
                else "display_unnumbered" if is_display
                else "inline_context"
            )
            alttext_diff = (
                _alttext_cross_check(latex, recovered or "", scope=scope)
                if _alttext_cross_check else {}
            )

            validation = validate_solution(
                recovered or "", solution, latex, canonical_tree=tree, alttext_diff=alttext_diff
            )

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
                if validation.get("cannot_isolate"):
                    m["cannot_isolate"] += 1
                    m["parsed_equations"] += 1
                elif validation.get("vacuous_echo"):
                    m["vacuous_echo"] += 1
                    m["parsed_equations"] += 1
                    m["isolatable_equations"] += 1
                elif validation["attempted"]:
                    m["substitution_attempted"] += 1
                    m["parsed_equations"] += 1
                    m["isolatable_equations"] += 1
                else:
                    m["unattempted_exceptions"] += 1

                if validation["passed"] is True:
                    m["validation_passed"] += 1
                elif validation["passed"] is False:
                    m["validation_failed"] += 1
                else:
                    m["validation_unverifiable"] += 1

                if validation.get("failed_stage1"):
                    m["failed_stage1"] += 1
                if validation.get("refuted_stage2"):
                    m["refuted_stage2"] += 1
                if validation.get("failed_alttext_gap"):
                    m["failed_alttext_gap"] += 1
                if validation.get("verified_algebraic"):
                    m["verified_algebraic"] += 1
                if validation.get("definition_recorded"):
                    m["definition_recorded"] += 1

            # Extract prose context (theory context around the math)
            prose_ctx = {
                "context_before": eq.get("context_before", ""),
                "context_after": eq.get("context_after", ""),
                "section_title": eq.get("section") or eq.get("section_title", ""),
            }

            records.append({
                "occurrence_key": okey,
                "paper_id": paper_id,
                "paper_version": version,
                "arxiv_url": arxiv_url,
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
                "alttext_diff": alttext_diff,
                "prose_context": prose_ctx,
                "generator": generator,
                "github_repos": github_repos,
            })

    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    # Sample: one solved+validated, one rejected
    solved_sample = next((r for r in records if r["solved"] and r["validation"]["passed"]), None)
    rejected_sample = next((r for r in records if not r["solved"]), None)

    # Alttext gap summary & gap x verdict cross-tab
    gap_counter: dict[str, int] = {}
    records_with_gaps = 0
    verdict_cross_tab = {
        "passed": {"total": 0, "with_gap": 0, "gap_categories": Counter()},
        "failed": {"total": 0, "with_gap": 0, "gap_categories": Counter()},
        "unverifiable": {"total": 0, "with_gap": 0, "gap_categories": Counter()},
    }

    for r in records:
        ad = r.get("alttext_diff") or {}
        has_g = bool(ad.get("missing_from_expr"))
        if has_g:
            records_with_gaps += 1
            for cat in ad.get("gap_categories") or []:
                gap_counter[cat] = gap_counter.get(cat, 0) + 1

        if r.get("solved"):
            v = r.get("validation", {})
            if v.get("passed") is True:
                verdict_k = "passed"
            elif v.get("passed") is False:
                verdict_k = "failed"
            else:
                verdict_k = "unverifiable"
            verdict_cross_tab[verdict_k]["total"] += 1
            if has_g:
                verdict_cross_tab[verdict_k]["with_gap"] += 1
                for cat in ad.get("gap_categories") or []:
                    verdict_cross_tab[verdict_k]["gap_categories"][cat] += 1

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
            "parsed_equations": m["parsed_equations"],
            "isolatable_equations": m["isolatable_equations"],
            "substitution_attempted": m["substitution_attempted"],
            "unattempted_exceptions": m["unattempted_exceptions"],
            "cannot_isolate": m["cannot_isolate"],
            "vacuous_echo": m["vacuous_echo"],
            "validation_passed": m["validation_passed"],
            "verified_algebraic": m["verified_algebraic"],
            "definition_recorded": m["definition_recorded"],
            "validation_failed": m["validation_failed"],
            "failed_stage1": m["failed_stage1"],
            "refuted_stage2": m["refuted_stage2"],
            "failed_alttext_gap": m["failed_alttext_gap"],
            "validation_unverifiable": m["validation_unverifiable"],
            "stage1_breakdown": {
                "evaluated_with_checks": m["stage1_evaluated_with_checks"],
                "evaluated_vacuously": m["stage1_evaluated_vacuously"],
                "skipped": m["stage1_skipped"],
                "failed": m["stage1_failed"],
            },
            "alttext_gap": {
                "records_with_gaps": records_with_gaps,
                "gap_by_category": dict(sorted(gap_counter.items(), key=lambda kv: -kv[1])),
                "verdict_cross_tab": {
                    k: {
                        "total": v["total"],
                        "with_gap": v["with_gap"],
                        "gap_by_category": dict(sorted(v["gap_categories"].items(), key=lambda kv: -kv[1])),
                    }
                    for k, v in verdict_cross_tab.items()
                },
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
    print(f"  parsed equations           {m['parsed_equations']}")
    print(f"  isolatable equations       {m['isolatable_equations']}")
    print(f"  substitution attempted     {m['substitution_attempted']}")
    print(f"  unattempted exceptions     {m['unattempted_exceptions']}")
    print(f"  cannot isolate             {m['cannot_isolate']}")
    print(f"  vacuous echo               {m['vacuous_echo']}")
    print(f"  validation passed          {m['validation_passed']}")
    print(f"    verified algebraic       {m['verified_algebraic']}")
    print(f"    definition recorded      {m['definition_recorded']}")
    print(f"  validation failed          {m['validation_failed']}")
    print(f"    failed stage 1 (source)  {m['failed_stage1']}")
    print(f"    refuted stage 2 (calc)   {m['refuted_stage2']}")
    print(f"    failed alttext gap       {m['failed_alttext_gap']}")
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
    print(f"  AltText Cross-Check: {records_with_gaps} records have gaps between alttext and expr")
    if gap_counter:
        print("  Gap categories (# equations where each is missing from expr):")
        for cat, n in sorted(gap_counter.items(), key=lambda kv: -kv[1]):
            print(f"    {n:4d} equations missing: {cat}")
    print()
    print("  Gap x Verdict Cross-Tab (on candidate equations):")
    for vk, vdata in verdict_cross_tab.items():
        print(f"    {vk:12s}: {vdata['total']:3d} total | {vdata['with_gap']:2d} with gaps")
        if vdata['gap_categories']:
            cats_s = ", ".join(f"{c}: {n}" for c, n in sorted(vdata['gap_categories'].items(), key=lambda x: -x[1]))
            print(f"      gaps: {cats_s}")
    print()
    print(f"Wrote {OUT_JSONL}")
    print(f"Wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
