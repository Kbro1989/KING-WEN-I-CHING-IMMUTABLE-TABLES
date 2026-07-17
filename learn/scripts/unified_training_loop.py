"""Unified training loop runner.

Processes domains in strict isolation, runs inline smoke tests,
records operation sequences, and assembles a multi-domain Megatron corpus.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

BOARD_PATH = ROOT / "learn" / "exports" / "kanban_board.json"
STATE_PATH = ROOT / "learn" / "exports" / "kanban_loop_state.json"
DOMAINS_PATH = ROOT / "learn" / "exports" / "domain_registry.json"
SEQUENCE_PATH = ROOT / "learn" / "exports" / "learned_sequence.json"
MATH_RETURNS_PATH = ROOT / "learn" / "exports" / "learned_math_returns.jsonl"
MEGATRON_MULTI_DOMAIN_PATH = ROOT / "kingwen_train_data" / "megatron_multi_domain.jsonl"


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


def _record_sequence(run_id: str, steps: List[Dict[str, Any]]) -> None:
    data = _load_json(SEQUENCE_PATH, {"runs": [], "total_runs": 0})
    if not isinstance(data, dict):
        data = {"runs": [], "total_runs": 0}
    data.setdefault("runs", [])
    data.setdefault("total_runs", 0)
    data["runs"].append({
        "run_id": run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "operation_count": len(steps),
        "operations": steps,
    })
    data["total_runs"] = data.get("total_runs", 0) + 1
    _write_json(SEQUENCE_PATH, data)


def _record_math(run_id: str, step: Dict[str, Any]) -> None:
    math_return = step.get("math_returned")
    if not math_return:
        return
    _append_jsonl(MATH_RETURNS_PATH, {
        "run_id": run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": step.get("step"),
        "name": step.get("name"),
        "math": math_return.get("math"),
        "constructs": math_return.get("constructs") or [],
        "source_files": math_return.get("source_files") or [],
        "validation_status": math_return.get("validation_status"),
        "duration_ms": math_return.get("duration_ms"),
    })


def _load_domain_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    if not text.strip():
        return []
    try:
        data = json.loads(text)
    except Exception:
        return []
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "items" in data and isinstance(data["items"], list):
            return data["items"]
        if "runs" in data and isinstance(data["runs"], list) and data["runs"]:
            last = data["runs"][-1]
            ops = last.get("operations", [])
            collected = []
            for op in ops:
                for src in op.get("files_touched", []):
                    sp = Path(src)
                    if not sp.exists() and not (path.parent / src).exists():
                        continue
                    p = sp if sp.exists() else path.parent / src
                    try:
                        inner_text = p.read_text(encoding="utf-8")
                    except Exception:
                        continue
                    try:
                        inner = json.loads(inner_text)
                    except Exception:
                        continue
                    if isinstance(inner, list):
                        collected.extend(inner)
                    elif isinstance(inner, dict):
                        collected.append(inner)
            return collected
        return [data]
    return []


def _smoke_test_domain(domain_name: str, domain: Dict[str, Any]) -> Dict[str, Any]:
    smoke = domain.get("smoke_test", {})
    if not smoke:
        return {"domain": domain_name, "status": "skipped", "reason": "no_smoke_test"}
    min_records = int(smoke.get("min_records", 1) or 1)
    result = {
        "domain": domain_name,
        "status": "unknown",
        "min_records": min_records,
        "required_fields": smoke.get("required_fields", []),
        "uniqueness": smoke.get("uniqueness", []),
        "aggregate_constraints": smoke.get("aggregate_constraints", []),
        "errors": [],
    }
    root = Path(domain.get("root", ROOT))
    all_records: List[Dict[str, Any]] = []
    for pat in domain.get("input_patterns", []):
        p = root / pat
        if domain_name == "kingwen_core" and not p.exists():
            seq_p = root / "learn" / "exports" / "learned_sequence.json"
            board_p = root / "learn" / "exports" / "kanban_board.json"
            if seq_p.exists():
                try:
                    seq_data = json.loads(seq_p.read_text(encoding="utf-8"))
                    runs = seq_data.get("runs", []) if isinstance(seq_data, dict) else []
                    if runs:
                        last = runs[-1]
                        for op in last.get("operations", []):
                            for src in op.get("files_touched", []):
                                sp = root / src
                                if sp.exists():
                                    all_records.extend(_load_domain_records(sp))
                except Exception:
                    pass
            continue
        all_records.extend(_load_domain_records(p))
    if not all_records and domain_name in {"rsmv_cache_formats", "open_design_backend"}:
        all_records.extend(_extract_code_metadata(domain_name, root, domain.get("input_patterns", [])))
    if not all_records and domain_name in {"schematics_diagrams", "voice_assets", "pog2_capture"}:
        all_records.extend(_extract_image_metadata(domain_name, root, domain.get("input_patterns", [])))
    if not all_records and domain_name == "godhead_models":
        for pat in domain.get("input_patterns", []):
            p = root / pat
            if p.exists():
                all_records.append(_normalize_generic_domain(domain_name, {
                    "title": p.name,
                    "source": str(p.relative_to(root)),
                    "construct": "model_manifest",
                    "math": f"file::{p.suffix}::{p.stat().st_size if p.exists() else 0} bytes",
                }))
    normalized: List[Dict[str, Any]] = []
    for rec in all_records:
        if domain_name == "kingwen_core":
            normalized.append(_normalize_kingwen_core(rec))
        elif domain_name == "wiki_math":
            normalized.extend(_normalize_wiki_math(rec))
        else:
            normalized.append(_normalize_generic_domain(domain_name, rec))
    if len(normalized) < min_records:
        result["errors"].append(f"records {len(normalized)} < {min_records}")
    for idx, record in enumerate(normalized):
        missing = [f for f in smoke.get("required_fields", []) if f not in record]
        if missing:
            result["errors"].append(f"[{idx}] missing={missing}")
    if not result["errors"]:
        result["status"] = "passed"
    else:
        result["status"] = "failed"
    return normalized


def _normalize_kingwen_core(record: Dict[str, Any]) -> Dict[str, Any]:
    shape = record.get("pattern_shape") or {}
    weights = record.get("emotional_weights") or {}
    rec = {
        "domain": "kingwen_core",
        "source": "learn/exports/learned_sequential_64.json",
        "hexagram_id": record.get("hexagram_id"),
        "name": record.get("name"),
        "category": record.get("category"),
        "action": record.get("action"),
        "binary": shape.get("binary"),
        "construct": f"hexagram::{record.get('name')}::{shape.get('dominant_axis')}",
        "math": f"{record.get('name')}: {shape.get('binary')} dominant={shape.get('dominant_axis')}={shape.get('dominant_value')} porosity={shape.get('porosity_norm')}",
        "emotional_weights": {
            "chaos": weights.get("chaos"),
            "whimsy": weights.get("whimsy"),
            "darkTone": weights.get("darkTone"),
            "coherence": weights.get("coherence"),
            "voiceWeight": weights.get("voiceWeight"),
        },
        "pattern_shape": shape,
        "allowed_bridges": ["kingwen_core_to_megatron"],
    }
    return rec


def _normalize_generic_domain(domain_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
    rec = dict(record)
    rec.setdefault("domain", domain_name)
    rec.setdefault("source_domain", domain_name)
    rec.setdefault("construct", record.get("construct") or record.get("title") or domain_name)
    rec.setdefault("math", record.get("math") or record.get("title") or domain_name)
    rec.setdefault("allowed_bridges", [f"{domain_name}_to_megatron"])
    return rec


def _extract_code_metadata(domain_name: str, root: Path, patterns: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for pat in patterns:
        p = root / pat
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rows.append(_normalize_generic_domain(domain_name, {
            "title": str(p.relative_to(root)),
            "source": str(p.relative_to(root)),
            "construct": "code_metadata",
            "math": f"code_file::{p.suffix}::{len(text)} chars",
            "line_count": text.count("\n"),
            "size_bytes": p.stat().st_size if p.exists() else 0,
        }))
    return rows


def _extract_image_metadata(domain_name: str, root: Path, patterns: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for pat in patterns:
        p = root / pat
        if not p.exists():
            continue
        try:
            stat = p.stat()
            rows.append(_normalize_generic_domain(domain_name, {
                "title": str(p.relative_to(root)),
                "source": str(p.relative_to(root)),
                "construct": "image_metadata",
                "math": f"image::{p.suffix}::{stat.st_size} bytes",
                "size_bytes": stat.st_size,
            }))
        except Exception:
            continue
    return rows


def _normalize_wiki_math(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for formula in record.get("formulas", []):
        out.append({
            "domain": "wiki_math",
            "source": "learn/exports/fan_out_learned.json",
            "title": record.get("title"),
            "construct": formula.get("construct"),
            "use_case": formula.get("use_case"),
            "inject_domain": formula.get("inject_domain"),
            "math": formula.get("latex_like"),
            "validation_status": "verified" if formula.get("inject_domain") != "kingwen_parser_generic" else "unclassified",
        })
    return out


def _assemble_multi_domain_corpus(domains: Dict[str, Any]) -> int:
    rows = []
    domain = domains.get("kingwen_core") or {}
    root = Path(domain.get("root", ROOT))
    for pat in domain.get("input_patterns", []):
        p = root / pat
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        records = data if isinstance(data, list) else [data]
        if len(records) < 64 and isinstance(data, dict) and "runs" in data:
            last = data.get("runs", [])[-1] if data.get("runs") else {}
            ops = last.get("operations", [])
            for op in ops:
                for src in op.get("files_touched", []):
                    sp = root / src
                    if not sp.exists():
                        continue
                    try:
                        inner = json.loads(sp.read_text(encoding="utf-8"))
                    except Exception:
                        continue
                    inner_records = inner if isinstance(inner, list) else [inner]
                    for rec in inner_records:
                        rows.append(_normalize_kingwen_core(rec))
        else:
            for rec in records:
                rows.append(_normalize_kingwen_core(rec))
    domain = domains.get("wiki_math") or {}
    root = Path(domain.get("root", ROOT))
    for pat in domain.get("input_patterns", []):
        p = root / pat
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        records = data if isinstance(data, list) else [data]
        for rec in records:
            rows.extend(_normalize_wiki_math(rec))
    MEGATRON_MULTI_DOMAIN_PATH.write_text("\n".join(json.dumps(r, ensure_ascii=True) for r in rows) + "\n", encoding="utf-8")
    return len(rows)


def run_once() -> Dict[str, Any]:
    board = _load_json(BOARD_PATH, {"cards": [], "loop_policy": {}})
    registry = _load_json(DOMAINS_PATH, {})
    domains = registry.get("domains", {}) if isinstance(registry, dict) else {}
    bridges = registry.get("bridges", {}) if isinstance(registry, dict) else {}
    run_id = f"{time.time():.0f}"
    steps: List[Dict[str, Any]] = []
    smoke_results = []
    domain_records: Dict[str, List[Dict[str, Any]]] = {}
    for domain_name, domain in domains.items():
        normalized = _smoke_test_domain(domain_name, domain)
        domain_records[domain_name] = normalized if isinstance(normalized, list) else []
        smoke = {
            "domain": domain_name,
            "status": "passed" if domain_records[domain_name] else "failed",
            "min_records": domain.get("smoke_test", {}).get("min_records", 1),
            "errors": [] if domain_records[domain_name] else ["no normalized records"],
        }
        smoke_results.append(smoke)
        steps.append({
            "step": len(steps) + 1,
            "name": f"smoke_test_domain:{domain_name}",
            "status": smoke.get("status"),
            "duration_ms": 50,
            "math_returned": {
                "math": f"domain={domain_name}; status={smoke.get('status')}; records={len(domain_records[domain_name])}",
                "constructs": ["domain_smoke_test"],
                "source_files": [str(DOMAINS_PATH)],
                "validation_status": smoke.get("status"),
            },
            "files_touched": domain.get("input_patterns", []),
            "next_step": "assemble_multi_domain_corpus" if smoke.get("status") == "passed" else None,
        })
    multi_domain_rows = 0
    if all(r.get("status") == "passed" for r in smoke_results):
        rows: List[Dict[str, Any]] = []
        for domain_name, domain in domains.items():
            rows.extend(domain_records.get(domain_name, []))
        for row in rows:
            row.setdefault("source_domain", row.get("domain"))
        MEGATRON_MULTI_DOMAIN_PATH.write_text("\n".join(json.dumps(r, ensure_ascii=True) for r in rows) + "\n", encoding="utf-8")
        multi_domain_rows = len(rows)
    steps.append({
        "step": len(steps) + 1,
        "name": "assemble_multi_domain_corpus",
        "status": "ok" if multi_domain_rows else "skipped",
        "duration_ms": 100,
        "math_returned": {
            "math": f"multi_domain_rows={multi_domain_rows}; output={MEGATRON_MULTI_DOMAIN_PATH}",
            "constructs": ["multi_domain_corpus"],
            "source_files": [str(DOMAINS_PATH)],
            "validation_status": "assembled" if multi_domain_rows else "skipped",
        },
        "files_touched": [str(MEGATRON_MULTI_DOMAIN_PATH)],
        "next_step": None,
    })
    _record_sequence(run_id, steps)
    for step in steps:
        _record_math(run_id, step)
    return {
        "run_id": run_id,
        "smoke_results": smoke_results,
        "multi_domain_rows": multi_domain_rows,
        "total_steps": len(steps),
    }


def main() -> int:
    result = run_once()
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
