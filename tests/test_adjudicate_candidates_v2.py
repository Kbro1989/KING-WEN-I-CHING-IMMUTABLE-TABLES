"""Regression tests for scripts/adjudicate_candidates_v2.py.

Verifies:
1. Empty token sets do not falsely evaluate to True in _text_match.
2. Identical non-empty token sets match with score 1.0.
3. Partial overlap matches according to threshold.
4. Non-overlapping tokens evaluate to False.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from adjudicate_candidates_v2 import _text_match, _normalize, _token_set


def test_text_match_empty_inputs_must_not_match():
    """Empty strings or strings with no alphanumeric tokens must never match."""
    assert _text_match("", "") is False
    assert _text_match("   ", "   ") is False
    assert _text_match("!@#$%", "^&*()") is False
    assert _text_match("x + y", "") is False
    assert _text_match("", "x + y") is False


def test_text_match_exact_and_partial():
    """Valid tokens match appropriately based on Jaccard threshold."""
    assert _text_match("alpha + beta", "alpha + beta") is True
    assert _text_match("alpha beta gamma", "alpha beta delta", threshold=0.5) is True
    assert _text_match("alpha beta", "gamma delta", threshold=0.1) is False
