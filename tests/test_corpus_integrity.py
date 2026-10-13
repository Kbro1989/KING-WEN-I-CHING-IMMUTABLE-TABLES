import hashlib
import json
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"


def test_no_duplicate_arxiv_ids():
    """Verify all json files in arxiv_html_corpus have unique arxiv_ids."""
    seen_ids = set()
    for jf in CORPUS_DIR.glob("*.json"):
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        arxiv_id = data.get("arxiv_id", jf.stem)
        assert arxiv_id not in seen_ids, f"Duplicate paper ID {arxiv_id} in {jf.name}"
        seen_ids.add(arxiv_id)


def test_no_corpus_payload_collisions():
    """Verify no two papers share identical mathematical equation payloads (catches copy-paste corruption)."""
    payload_hashes = {}
    for jf in CORPUS_DIR.glob("*.json"):
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        arxiv_id = data.get("arxiv_id", jf.stem)
        eqs = data.get("equations", [])
        payload = json.dumps([e.get("latex") for e in eqs], sort_keys=True)
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        assert h not in payload_hashes, (
            f"Corpus payload collision: {arxiv_id} ({jf.name}) has identical equation payload to {payload_hashes[h]}"
        )
        payload_hashes[h] = arxiv_id


def test_2605_06070_restoration():
    """Verify that 2605.06070 contains the authentic Arena as Offline Reward paper."""
    target = CORPUS_DIR / "2605.06070.json"
    assert target.exists(), "2605.06070.json missing"
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("arxiv_id") == "2605.06070"
    title = data.get("structure", {}).get("title", "")
    assert "Arena as Offline Reward" in title
    eqs = data.get("equations", [])
    assert len(eqs) == 165


def test_isolation_and_substitution_accounting():
    """Verify that cannot_isolate and vacuous_echo are correctly flagged with attempted=False."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from math_reconstruction_evidence import validate_solution

    # 1. Multi-variable / cannot isolate (neither side has a single isolated variable)
    val_cannot_isolate = validate_solution("a + b = c + d", ["1"], "a + b = c + d", None)
    assert val_cannot_isolate["cannot_isolate"] is True
    assert val_cannot_isolate["attempted"] is False
    assert val_cannot_isolate["stage2_computational_validity"]["attempted"] is False

    # 2. Vacuous echo (solution for isolated variable still contains that variable)
    val_echo = validate_solution("y = x + 1", ["2*y"], "y = x + 1", None)
    assert val_echo["vacuous_echo"] is True
    assert val_echo["attempted"] is False
    assert val_echo["stage2_computational_validity"]["attempted"] is False

    # 3. Successful isolation & substitution
    val_success = validate_solution("x = 5", ["5"], "x = 5", None)
    assert val_success["cannot_isolate"] is False
    assert val_success["vacuous_echo"] is False
    assert val_success["attempted"] is True
    assert val_success["passed"] is True
