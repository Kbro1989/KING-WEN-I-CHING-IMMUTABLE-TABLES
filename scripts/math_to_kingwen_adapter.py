#!/usr/bin/env python3
"""Math-to-King-Wen adapter: single-equation provenance-preserving integration.

Takes one extracted math equation (from e2e_math_pipeline.py output) and
routes it through the King Wen lexical gate + shotgun expansion.

Usage:
    python scripts/math_to_kingwen_adapter.py --equation-index 0 --paper 2605.00155
    python scripts/math_to_kingwen_adapter.py --equation-index 34 --paper 2605.00155
    python scripts/math_to_kingwen_adapter.py --regression-report --paper 2605.00155
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from emotional_engine import extract_intent, expand_hexagram  # noqa: E402
# Import shotgun_expand - handle both package-style and flat imports
try:
    from scripts.full_hexagram_shotgun import shotgun_expand  # noqa: E402
except ImportError:
    from full_hexagram_shotgun import shotgun_expand  # noqa: E402


def build_request_text(eq: dict) -> str:
    """Build request_text from equation context, preserving provenance.

    Three separate fields are kept distinct:
    - equation_source: original LaTeX (preserved verbatim, never modified)
    - equation_features: mathematically derived features (symbols, keywords)
    - prose_context: surrounding text (section numbers stripped)

    Only the lexical input is constructed from these fields under an
    explicitly documented rule. Section numbers like "4.4" are NOT
    included as semantic inputs.
    """
    parts = []

    # 1. Equation symbols (mathematically derived features)
    if eq.get("symbols"):
        parts.append(" ".join(eq["symbols"]))

    # 2. Context keywords (extracted from surrounding prose)
    kw = eq.get("relations", {}).get("context_keywords", [])
    if kw:
        parts.append(" ".join(kw))

    # 3. Prose context (section numbers stripped, only alphabetic words)
    for ctx in (eq.get("context_before", ""), eq.get("context_after", "")):
        if ctx.strip():
            # Strip section numbers like "4.4", "3.2.1", etc.
            cleaned = re.sub(r"\b\d+(\.\d+)*\b", "", ctx)
            # Keep only alphabetic words (no numeric section refs)
            words = re.findall(r"[a-zA-Z]+", cleaned)
            parts.append(" ".join(words))

    # 4. LaTeX-derived tokens (strip backslashes, keep command names)
    latex = eq.get("latex", "")
    if latex.strip():
        # Extract command names like \sum, \int, \frac
        cmds = re.findall(r"\\([a-zA-Z]+)", latex)
        parts.extend(cmds)

    return " ".join(parts)


def process_equation(eq: dict, paper_id: str) -> dict:
    """Process a single equation through the King Wen pipeline.

    Returns a provenance-linked fixture with all intermediate artifacts.
    """
    # 1. Preserve original equation (immutable)
    equation_source = {
        "latex": eq.get("latex", ""),
        "mathml": eq.get("mathml", ""),
        "symbols": eq.get("symbols", []),
        "is_display": eq.get("is_display", False),
        "source": eq.get("source", ""),
        "solved": eq.get("solved", ""),
        "context_before": eq.get("context_before", ""),
        "context_after": eq.get("context_after", ""),
        "context_keywords": eq.get("relations", {}).get("context_keywords", []),
        "related_equations": eq.get("relations", {}).get("related_equations", []),
    }

    # 2. Build request_text (separate from equation_source)
    request_text = build_request_text(eq)

    # 3. Extract intent (lexical routing)
    intent = extract_intent(request_text)

    # 4. Compute emotional_input from intent vector
    iv = intent.get("intent_vector", [0.1, 0.1, 0.1, 0.8, 0.85])
    coherence = iv[3] if len(iv) > 3 else 0.8
    voice_weight = iv[4] if len(iv) > 4 else 0.85
    emotional_input = int(round((coherence + voice_weight) / 2.0 * 100))

    # 5. Run shotgun expansion
    expansion = shotgun_expand(
        request_text=request_text,
        emotional_input=emotional_input,
    )

    # 6. Build provenance-linked fixture
    fixture = {
        "provenance": {
            "paper_id": paper_id,
            "equation_index": eq.get("index", -1),
            "extraction_method": eq.get("source", "unknown"),
            "recovery_status": "recovered" if eq.get("solved") else "unrecovered",
        },
        "equation_source": equation_source,
        "request_text": request_text,
        "intent_result": {
            "query_tokens": intent.get("query_tokens", []),
            "matched_intents": intent.get("matched_intents", {}),
            "dominant_intent": intent.get("dominant_intent", "understand"),
            "intensity": intent.get("intensity", 0.0),
            "word_count": intent.get("word_count", 0),
            "intent_vector": iv,
        },
        "emotional_input": emotional_input,
        "expansion_summary": {
            "source": expansion.get("source", "unknown"),
            "total_expanded": expansion.get("total_expanded", 0),
            "total_resolved": expansion.get("total_resolved", 0),
            "ternary_line_permutations_per_hex": expansion.get("ternary_line_permutations_per_hex", 0),
            "total_ternary_line_permutations": expansion.get("total_ternary_line_permutations", 0),
            "consensus": expansion.get("consensus", None),
            "expanded_count": len(expansion.get("expanded", [])),
            "resolved_count": len(expansion.get("resolved", [])),
        },
        "identity_check": {
            "expanded_unique_hexagrams": len(set(e.get("hexagram_id") for e in expansion.get("expanded", []))),
            "resolved_unique_identities": len(set((r.get("hexagram_id"), r.get("phase_bits")) for r in expansion.get("resolved", []))),
            "expected_expanded": 64,
            "expected_resolved": 512,
        },
    }

    return fixture


def run_regression_report(paper_id: str, max_equations: int = None):
    """Run a regression report over all equations in a paper.

    Produces one row per equation with explicit pass/fail for:
    - extraction (equation has LaTeX source)
    - recovery (solved field non-empty)
    - routing (request_text non-empty)
    - identity (64 expanded + 512 resolved, unique)
    - provenance (paper_id, equation_index, extraction_method present)
    """
    e2e_path = ROOT / "DATASETS" / f"e2e_{paper_id}.json"
    if not e2e_path.exists():
        print(f"ERROR: {e2e_path} not found")
        sys.exit(1)

    with open(e2e_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    equations = data.get("equations", [])
    if max_equations:
        equations = equations[:max_equations]

    report = []
    for eq in equations:
        idx = eq.get("index", -1)
        try:
            fixture = process_equation(eq, paper_id)

            # Check each criterion
            extraction_ok = bool(eq.get("latex", "").strip())
            recovery_ok = bool(eq.get("solved", "").strip())
            routing_ok = bool(fixture["request_text"].strip())
            identity_ok = (
                fixture["identity_check"]["expanded_unique_hexagrams"] == 64
                and fixture["identity_check"]["resolved_unique_identities"] == 512
            )
            provenance_ok = (
                fixture["provenance"]["paper_id"] == paper_id
                and fixture["provenance"]["equation_index"] == idx
                and fixture["provenance"]["extraction_method"] != ""
            )

            row = {
                "equation_index": idx,
                "latex_preview": eq.get("latex", "")[:60],
                "extraction": "PASS" if extraction_ok else "FAIL",
                "recovery": "PASS" if recovery_ok else "FAIL",
                "routing": "PASS" if routing_ok else "FAIL",
                "identity": "PASS" if identity_ok else "FAIL",
                "provenance": "PASS" if provenance_ok else "FAIL",
                "dominant_intent": fixture["intent_result"]["dominant_intent"],
                "matched_intents": len(fixture["intent_result"]["matched_intents"]),
                "emotional_input": fixture["emotional_input"],
                "query_tokens_count": len(fixture["intent_result"]["query_tokens"]),
            }
            report.append(row)
        except Exception as e:
            report.append({
                "equation_index": idx,
                "latex_preview": eq.get("latex", "")[:60],
                "extraction": "ERROR",
                "recovery": "ERROR",
                "routing": "ERROR",
                "identity": "ERROR",
                "provenance": "ERROR",
                "error": str(e),
            })

    # Print summary
    total = len(report)
    extraction_pass = sum(1 for r in report if r.get("extraction") == "PASS")
    recovery_pass = sum(1 for r in report if r.get("recovery") == "PASS")
    routing_pass = sum(1 for r in report if r.get("routing") == "PASS")
    identity_pass = sum(1 for r in report if r.get("identity") == "PASS")
    provenance_pass = sum(1 for r in report if r.get("provenance") == "PASS")
    errors = sum(1 for r in report if r.get("extraction") == "ERROR")

    print(f"\n=== Regression Report: {paper_id} ===")
    print(f"  Total equations: {total}")
    print(f"  Extraction PASS: {extraction_pass}/{total}")
    print(f"  Recovery PASS: {recovery_pass}/{total}")
    print(f"  Routing PASS: {routing_pass}/{total}")
    print(f"  Identity PASS: {identity_pass}/{total}")
    print(f"  Provenance PASS: {provenance_pass}/{total}")
    print(f"  Errors: {errors}")

    # Save report
    out_path = ROOT / "DATASETS" / f"math_kingwen_regression_{paper_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"paper_id": paper_id, "total": total, "rows": report}, f, indent=2)
    print(f"  Report saved: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Math-to-King-Wen adapter")
    parser.add_argument("--paper", default="2605.00155", help="Arxiv paper ID")
    parser.add_argument("--equation-index", type=int, default=None, help="Single equation index")
    parser.add_argument("--output", default=None, help="Output JSON file")
    parser.add_argument("--regression-report", action="store_true", help="Run full regression report")
    parser.add_argument("--max-equations", type=int, default=None, help="Limit equations for regression")
    args = parser.parse_args()

    if args.regression_report:
        run_regression_report(args.paper, args.max_equations)
        return

    if args.equation_index is None:
        print("ERROR: --equation-index required (or use --regression-report)")
        sys.exit(1)

    # Load e2e math output
    e2e_path = ROOT / "DATASETS" / f"e2e_{args.paper}.json"
    if not e2e_path.exists():
        print(f"ERROR: {e2e_path} not found")
        sys.exit(1)

    with open(e2e_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    equations = data.get("equations", [])
    if args.equation_index >= len(equations):
        print(f"ERROR: equation index {args.equation_index} >= {len(equations)}")
        sys.exit(1)

    eq = equations[args.equation_index]
    print(f"Processing equation {args.equation_index} from paper {args.paper}")
    print(f"  LaTeX: {eq.get('latex', '')[:80]}")
    print(f"  Source: {eq.get('source', 'unknown')}")
    print(f"  Recovery: {'recovered' if eq.get('solved') else 'unrecovered'}")

    fixture = process_equation(eq, args.paper)

    # Print summary
    print(f"\n=== Results ===")
    print(f"  request_text: {fixture['request_text'][:100]}...")
    print(f"  query_tokens: {fixture['intent_result']['query_tokens']}")
    print(f"  matched_intents: {fixture['intent_result']['matched_intents']}")
    print(f"  dominant_intent: {fixture['intent_result']['dominant_intent']}")
    print(f"  emotional_input: {fixture['emotional_input']}")
    print(f"  expanded: {fixture['expansion_summary']['expanded_count']} (expected 64)")
    print(f"  resolved: {fixture['expansion_summary']['resolved_count']} (expected 512)")
    print(f"  unique hexagrams: {fixture['identity_check']['expanded_unique_hexagrams']}")
    print(f"  unique identities: {fixture['identity_check']['resolved_unique_identities']}")

    # Write output
    out_path = args.output or str(ROOT / "DATASETS" / f"math_kingwen_fixture_{args.paper}_{args.equation_index}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixture, f, indent=2, ensure_ascii=False)
    print(f"\n  Output: {out_path}")


if __name__ == "__main__":
    main()
