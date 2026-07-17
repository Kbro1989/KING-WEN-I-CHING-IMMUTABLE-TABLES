"""Fan-out wiki-math /learn parser with respectful pacing.

Reads batches from a source manifest, extracts math formulas via
`standalone_wiki_math.py` logic, relates them to use cases, and
writes learned outputs without hammering providers.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys_path_additions = [
    str(ROOT),
    str(Path(r"C:/Users/krist/Desktop/mwparserfromhell_local")),
]
sys.path[:0] = sys_path_additions

from mwparserfromhell import parse as mw_parse
from mwparserfromhell.wikicode import Wikicode

from src.core.pog3_hexagram_runtime_substrate import POG3Runtime, IntentVector


def _throttle(delay: float) -> None:
    if delay > 0:
        time.sleep(delay)


def extract_math_wiki_page(title: str, wikitext: str) -> dict:
    code: Wikicode = mw_parse(wikitext)
    math_nodes = [
        str(node)
        for node in code.ifilter(
            matches=lambda n: hasattr(n, "tag")
            and str(getattr(n, "tag", "")).lower() in {"math", "ce", "chem", "sub", "sup"}
        )
    ]
    return {
        "title": title,
        "math_node_count": len(math_nodes),
        "math_nodes": math_nodes[:50],
        "source_chars": len(wikitext),
    }


def classify_formula(node: str) -> dict:
    text = node.lower()
    # Expanded from learned fan-out artifacts.
    if "\\langle" in text and "\\hat{a}" in text and "\\psi" in text:
        return {
            "use_case": "quantum_operator",
            "construct": "hermitian_operator",
            "inject_domain": "kingwen_quantum_physics",
        }
    if "f(x)=" in text and "\\sigma" in text and "\\sqrt{2\\pi}" in text and "\\exp" in text:
        return {
            "use_case": "probability_distribution",
            "construct": "gaussian_normal",
            "inject_domain": "kingwen_probability_kernel",
        }
    if "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}" in text or "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}" in text:
        return {
            "use_case": "algebraic_root_formula",
            "construct": "quadratic_formula",
            "inject_domain": "kingwen_parser_math",
        }
    if text.startswith("<math>") and "\\delta =" in text and "b^2 - 4ac" in text:
        return {
            "use_case": "polynomial_discriminant",
            "construct": "discriminant",
            "inject_domain": "kingwen_parser_math",
        }
    if "\\exp" in text or "e^{" in text or "\\sigma" in text or "\\sqrt" in text or "\\frac" in text:
        return {
            "use_case": "symbolic_math",
            "construct": "algebraic_expression",
            "inject_domain": "kingwen_parser_math",
        }
    if text.startswith("<chem>") or "\\ce{" in text:
        return {
            "use_case": "chemical_equation",
            "construct": "reaction_representation",
            "inject_domain": "kingwen_parser_chem",
        }
    if "\\hbar" in text or "\\nabla" in text or "\\partial" in text:
        return {
            "use_case": "quantum_operator",
            "construct": "schrödinger_hamiltonian",
            "inject_domain": "kingwen_quantum_physics",
        }
    return {
        "use_case": "unknown",
        "construct": "unclassified",
        "inject_domain": "kingwen_parser_generic",
    }


def learn_batch(
    items: list[dict],
    delay: float = 0.35,
    max_errors: int = 5,
) -> dict:
    learned = []
    errors = 0
    session_id = f"fan_out_learn_{time.time():.0f}"
    runtime = POG3Runtime.for_session(session_id)

    for item in items:
        title = str(item.get("title") or "")
        wikitext = str(item.get("wikitext") or "")
        try:
            extracted = extract_math_wiki_page(title, wikitext)
        except Exception as exc:
            errors += 1
            if errors >= max_errors:
                break
            continue

        # Deterministically derive emotional weights from page content
        content_str = title + " " + wikitext
        content_hash = hashlib.md5(content_str.encode("utf-8")).digest()
        chaos = (content_hash[0] % 100) / 100.0
        whimsy = (content_hash[1] % 100) / 100.0
        dark_tone = (content_hash[2] % 100) / 100.0

        # Construct intent vector
        intent = IntentVector(
            temporal=(0, 1, 0),  // present-focused
            emotional=(chaos, whimsy, dark_tone),
            action=(1, 0, 0),  // move/parse
        )

        # Consult oracle
        state_obj, capture = runtime.engine.consult(intent, context={"page_title": title})
        telemetry = capture.to_telemetry()

        formulas = []
        for node in extracted.get("math_nodes", []):
            meta = classify_formula(node)
            formulas.append({
                "latex_like": node,
                "use_case": meta["use_case"],
                "construct": meta["construct"],
                "inject_domain": meta["inject_domain"],
            })
        learned.append({
            "title": extracted.get("title"),
            "math_node_count": extracted.get("math_node_count"),
            "formulas": formulas,
            "oracle_volition": telemetry,
        })
        _throttle(delay)
    return {
        "batch_count": len(items),
        "learned_count": len(learned),
        "items": learned,
        "session_telemetry": runtime.get_telemetry(),
    }


def main() -> int:
    manifest_path = ROOT / "learn" / "exports" / "fan_out_manifest.jsonl"
    out_path = ROOT / "learn" / "exports" / "fan_out_learned.json"
    if not manifest_path.exists():
        print(f"missing manifest: {manifest_path}")
        return 1
    items = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = learn_batch(items, delay=0.35)
    out_path.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    print("learned_count=", result["learned_count"], "batch_count=", result["batch_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
