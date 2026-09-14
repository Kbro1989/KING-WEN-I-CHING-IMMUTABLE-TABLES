#!/usr/bin/env python3
"""
loader_kingwen_interop.py — validator + measurement harness for the King Wen interop graph.

Loads interop_kingwen_graph_v2.0.2.json and:
  1. Validates the 5 v2.0.2 loader invariants (src/dst in V, operator in O,
     fidelity.observation non-empty, determinism.basis non-empty, BLOCKED not in O).
  2. Optionally runs measurement probes for edges that have an implemented method.

This is the first empirical testbed for the Interop Algebra — King Wen as the
candidate graph whose primary currency is transformation fidelity.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

GRAPH_PATH = Path(__file__).with_name("interop_kingwen_graph_v2.0.2.json")


def load_graph(path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or GRAPH_PATH
    if not p.exists():
        raise FileNotFoundError(f"Graph spec not found: {p}")
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Invariant enforcement
# ---------------------------------------------------------------------------

def build_node_set(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Flatten V.classes.*.members into {node_id: node_record}."""
    nodes: Dict[str, Dict[str, Any]] = {}
    v = graph.get("V", {})
    for cls_key, cls_val in v.get("classes", {}).items():
        for member in cls_val.get("members", []):
            nid = member.get("id")
            if not nid:
                continue
            nodes[nid] = {**member, "_class": cls_key, "_class_label": cls_val.get("label")}
    return nodes


def validate_invariants(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run the 5 v2.0.2 loader invariants. Returns list of violations."""
    violations: List[Dict[str, Any]] = []
    nodes = build_node_set(graph)
    O = set(graph.get("O", {}).get("primitives", []))

    def _check(condition: bool, inv_id: str, detail: str, edge_id: Optional[str] = None) -> None:
        if not condition:
            violations.append({
                "invariant": inv_id,
                "edge": edge_id or "global",
                "detail": detail,
            })

    # Inv 1: src, dst in V
    for edge in graph.get("edges", []):
        eid = edge.get("id")
        for side in ("src", "dst"):
            val = edge.get(side)
            if val is None:
                _check(False, "inv-1",
                       f"edge {eid}: missing '{side}'", eid)
                continue
            if isinstance(val, str):
                _check(val in nodes, "inv-1",
                       f"edge {eid}: {side}={val!r} not in V", eid)
            elif isinstance(val, list):
                missing = [v for v in val if v not in nodes]
                _check(not missing, "inv-1",
                       f"edge {eid}: {side} list has unknown ids: {missing}", eid)
            else:
                _check(False, "inv-1",
                       f"edge {eid}: {side} has unsupported type {type(val).__name__}", eid)

    # Inv 2: operator in O
    for edge in graph.get("edges", []):
        eid = edge.get("id")
        op = edge.get("operator")
        _check(op in O, "inv-2",
               f"edge {eid}: operator={op!r} not in O", eid)

    # Inv 3: fidelity.observation non-empty
    for edge in graph.get("edges", []):
        eid = edge.get("id")
        fid = edge.get("fidelity")
        if fid is None:
            continue
        obs = fid.get("observation")
        _check(obs is not None and str(obs).strip() != "",
               "inv-3",
               f"edge {eid}: fidelity.observation empty", eid)

    # Inv 4: determinism.basis non-empty
    for edge in graph.get("edges", []):
        eid = edge.get("id")
        det = edge.get("determinism")
        if det is None:
            continue
        basis = det.get("basis")
        _check(basis is not None and str(basis).strip() != "",
               "inv-4",
               f"edge {eid}: determinism.basis empty", eid)

    # Inv 5: BLOCKED not in O
    _check("BLOCKED" not in O, "inv-5",
           "O contains BLOCKED which must be an attempt status, not an operator")

    return violations


# ---------------------------------------------------------------------------
# Measurement probes (best-effort; some edges need a running runtime)
# ---------------------------------------------------------------------------

def probe_bin_to_ternary(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Round-trip: 64 hexagrams × 8 phases → ternary → reconstruct binary."""
    # Requires importing the King Wen modules. Defer import + try/except.
    try:
        sys.path.insert(0, str(GRAPH_PATH.parent))
        from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_LINE_MAP
        from emotional_engine import _line_state_balance
    except Exception as e:
        return {"status": "skipped", "reason": f"import failed: {e}"}

    total = 0
    passed = 0
    failures: List[Dict[str, Any]] = []
    for hid, hdata in HEXAGRAM_BASE.items():
        binary = hdata.get("binary_bottom_to_top", "")
        if not binary:
            continue
        for phase in range(8):
            total += 1
            balance = _line_state_balance(binary, phase)
            line_states = balance.get("line_states", [])
            # Reconstruct binary: for each line position, ternary_state 0→'0', 1→'1', 2→? (changing)
            reconstructed = []
            for ls in line_states:
                ts = ls.get("ternary_state")
                if ts == 0:
                    reconstructed.append("0")
                elif ts == 1:
                    reconstructed.append("1")
                else:
                    reconstructed.append("?")  # yao — can't recover original bit
            orig = list(binary)
            recon = list(reversed(reconstructed))  # balance uses bottom_to_top; match orientation
            # Compare non-yao positions
            mism = 0
            for i in range(min(len(orig), len(recon))):
                if orig[i] != recon[i] and recon[i] != "?":
                    mism += 1
            if mism == 0:
                passed += 1
            else:
                failures.append({"hex": hid, "phase": phase, "mismatches": mism})
    return {
        "status": "ok" if not failures else "partial",
        "total": total,
        "passed": passed,
        "failed": len(failures),
        "failures_sample": failures[:5],
        "note": "Yao positions cannot be reconstructed from ternary state alone (both 0→1 and 1→0 transitions produce ternary_state=2). Reversibility is partial by design."
    }


def probe_ternary_to_resolved(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Forward: ternary → 9-bit index. Inverse: index → ternary (check collisions)."""
    try:
        sys.path.insert(0, str(GRAPH_PATH.parent))
        from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_LINE_MAP, PHASE_INFO
        from emotional_engine import _line_state_balance
    except Exception as e:
        return {"status": "skipped", "reason": f"import failed: {e}"}

    # Build mapping: (hex_id, phase) → ternary signature → resolved index
    index_to_signatures: Dict[int, set] = {}
    for hid, hdata in HEXAGRAM_BASE.items():
        binary = hdata.get("binary_bottom_to_top", "")
        if not binary:
            continue
        for phase in range(8):
            balance = _line_state_balance(binary, phase)
            sig = tuple((ls["position"], ls["ternary_state"]) for ls in balance.get("line_states", []))
            # 9-bit index = (hexagram_id - 1) * 8 + phase  (row-major order)
            index = (int(hid) - 1) * 8 + phase
            index_to_signatures.setdefault(index, set()).add(sig)

    unique = sum(1 for s in index_to_signatures.values() if len(s) == 1)
    collisions = sum(1 for s in index_to_signatures.values() if len(s) > 1)
    return {
        "status": "ok",
        "indices": len(index_to_signatures),
        "unique": unique,
        "collisions": collisions,
        "note": "When only the 9-bit resolved index is retained, inverse is lossy: multiple ternary signatures can map to the same index. Reversible only if full ternary signature is retained alongside the index."
    }


def probe_observed_emotional_vector(graph: Dict[str, Any]) -> Dict[str, Any]:
    """For each hexagram 1-64, get _primary_pool_for_hex vector. Count near-collisions within eps."""
    try:
        sys.path.insert(0, str(GRAPH_PATH.parent))
        from emotional_engine import _primary_pool_for_hex, _clamp
    except Exception as e:
        return {"status": "skipped", "reason": f"import failed: {e}"}

    vectors: Dict[int, List[float]] = {}
    for hid in range(1, 65):
        try:
            vec = _primary_pool_for_hex(hid)
            vectors[hid] = vec
        except Exception:
            pass

    # Pairwise distance
    pairs_within_eps: Dict[float, int] = {}
    for eps in [0.05, 0.10, 0.20, 0.30]:
        count = 0
        for a in vectors:
            for b in vectors:
                if a >= b:
                    continue
                dist = sum((x - y) ** 2 for x, y in zip(vectors[a], vectors[b])) ** 0.5
                if dist <= eps:
                    count += 1
        pairs_within_eps[eps] = count

    return {
        "status": "ok",
        "hexagrams_with_vectors": len(vectors),
        "pairs_within_eps": pairs_within_eps,
        "note": "Many-to-one mapping confirmed if pairs_within_eps > 0 for small eps. Emotional vector is lossy for hexagram recovery."
    }


def probe_state_projector(graph: Dict[str, Any], edge_id: str) -> Dict[str, Any]:
    """Round-trip a single state projector edge from kingwen_state_transition.py."""
    try:
        scripts_dir = str(GRAPH_PATH.parent / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from kingwen_state_transition import (
            KingwenStateMachine,
            TransitionOpcode,
        )
    except Exception as e:
        return {"status": "skipped", "reason": f"import failed: {e}"}

    cases: Dict[str, Tuple[int, int, float, TransitionOpcode]] = {
        "e_state_identity": (1, 2, 0.8, TransitionOpcode.IDENTITY),
        "e_state_stereographic": (52, 1, 0.9, TransitionOpcode.STEREOGRAPHIC),
        "e_state_mobius": (1, 2, 0.8, TransitionOpcode.MOBIUS),
        "e_state_null_void": (15, 0, 0.0, TransitionOpcode.NULL_VOID),
        "e_state_gaussian_future": (1, 0, 0.5, TransitionOpcode.GAUSSIAN_FUTURE),
    }
    case = cases.get(edge_id)
    if case is None:
        return {"status": "error", "reason": f"no probe case for edge_id={edge_id!r}"}

    hid, phase, coh, opcode = case
    sm = KingwenStateMachine()
    try:
        t = sm.transition(hexagram_id=hid, phase_bits=phase, mask="PASS",
                          coherence=coh, opcode=opcode)
        if opcode == TransitionOpcode.IDENTITY:
            parsed = sm.resolve_from_key(t["state_key"])
            return {"roundtrip_ok": parsed.get("state_key") == t["state_key"]}
        elif opcode == TransitionOpcode.STEREOGRAPHIC:
            err = float(t.get("stereographic", {}).get("inverse_error", float("inf")))
            return {"inverse_error": err}
        elif opcode == TransitionOpcode.NULL_VOID:
            return {"void": bool(t.get("void")),
                    "projection": t.get("projection")}
        elif opcode == TransitionOpcode.GAUSSIAN_FUTURE:
            return {"future_weight": float(t.get("future_weight", 0)),
                    "bias_sum": float(sum(t.get("phase_bias", [])))}
        elif opcode == TransitionOpcode.MOBIUS:
            gamma = t.get("mobius_gamma", {})
            return {"gamma_real": gamma.get("real"),
                    "gamma_imag": gamma.get("imag"),
                    "mag": gamma.get("mag"),
                    "theta": gamma.get("theta")}
        else:
            return {"state_key": t.get("state_key")}
    except Exception as e:
        return {"error": str(e)}


def probe_all(graph: Dict[str, Any]) -> Dict[str, Any]:
    single_probes = {
        "e_bin_to_ternary": probe_bin_to_ternary,
        "e_ternary_to_resolved": probe_ternary_to_resolved,
        "e_resolved_to_emotional_vector": probe_observed_emotional_vector,
    }
    projector_edges = [
        "e_state_identity",
        "e_state_stereographic",
        "e_state_mobius",
        "e_state_null_void",
        "e_state_gaussian_future",
    ]
    out: Dict[str, Any] = {}
    for eid, fn in single_probes.items():
        edge = next((e for e in graph.get("edges", []) if e.get("id") == eid), None)
        if edge is None:
            out[eid] = {"status": "not_found_in_graph"}
            continue
        try:
            out[eid] = fn(graph)
        except Exception as e:
            out[eid] = {"status": "error", "reason": str(e)}
    for eid in projector_edges:
        edge = next((e for e in graph.get("edges", []) if e.get("id") == eid), None)
        if edge is None:
            out[eid] = {"status": "not_found_in_graph"}
            continue
        try:
            out[eid] = probe_state_projector(graph, eid)
        except Exception as e:
            out[eid] = {"status": "error", "reason": str(e)}
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    graph = load_graph()

    # Invariant validation
    violations = validate_invariants(graph)
    print(f"[invariants] total_edges={len(graph.get('edges', []))} violations={len(violations)}")
    if violations:
        for v in violations:
            print(f"  FAIL {v['invariant']} edge={v['edge']}: {v['detail']}")
    else:
        print("  all 5 invariants pass")

    # Measurement probes
    if "--measure" in argv:
        print("\n[measurements]")
        results = probe_all(graph)
        for eid, r in results.items():
            print(f"  {eid}: {r}")

    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
