"""Tests for OmniDocBench External Evaluation Adapter (Channel B).

Verifies:
  1. Self-contained Levenshtein distance produces exact values.
  2. CDM token normalization collapses delimiters and operators per 44-rule specification.
  3. Hungarian assignment correctly pairs bboxes and LaTeX strings under linear_sum_assignment.
  4. Precision, Recall, F1, and IoU are computed accurately.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from external_metrics.cdm_adapter import (
    HungarianCDMAdapter,
    compute_iou,
    levenshtein_distance,
    normalize_cdm_tokens,
)


def test_levenshtein_distance():
    assert levenshtein_distance("", "") == 0
    assert levenshtein_distance("abc", "abc") == 0
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("formula", "") == 7


def test_cdm_token_normalization():
    # Operator flattening
    raw = r"\lVert A \rVert \le \cdot x"
    norm = normalize_cdm_tokens(raw)
    assert norm == "|| A || <= . x"

    # Delimiter size stripping
    raw2 = r"\left[ \Big( x \Big) \right]"
    norm2 = normalize_cdm_tokens(raw2)
    assert norm2 == "[ ( x ) ]"


def test_compute_iou():
    b1 = [0, 0, 10, 10]
    b2 = [0, 0, 10, 10]
    assert compute_iou(b1, b2) == 1.0

    b3 = [5, 0, 15, 10]  # overlap 5x10 = 50, union = 100 + 100 - 50 = 150
    assert abs(compute_iou(b1, b3) - (50 / 150)) < 1e-4

    b4 = [20, 20, 30, 30]  # disjoint
    assert compute_iou(b1, b4) == 0.0


def test_hungarian_cdm_adapter_matching():
    adapter = HungarianCDMAdapter(iou_weight=0.5, text_weight=0.5)

    preds = [
        {"bbox": [10, 10, 50, 50], "latex": r"\lVert x \rVert"},
        {"bbox": [100, 100, 200, 200], "latex": r"A \cdot B"},
    ]
    gt = [
        {"bbox": [100, 100, 200, 200], "latex": r"A \cdot B"},  # exactly matches preds[1]
        {"bbox": [12, 10, 52, 50], "latex": r"|| x ||"},       # CDM normalizes to match preds[0]
    ]

    res = adapter.match_and_evaluate(preds, gt)

    assert res["channel"] == "CHANNEL_B_PERCEPTUAL_CDM"
    assert res["metric_identifier"] == "KING-WEN-LOCAL-CDM-V1.0"
    assert "upstream_reference" in res
    assert "metric_caveat" in res
    assert res["matched_pairs"] == 2
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1_score"] == 1.0
    assert res["average_iou"] > 0.8
    assert res["average_norm_edit_distance"] == 0.0  # CDM normalized edit dist is 0


def test_upstream_fixture_line_matching():
    adapter = HungarianCDMAdapter()

    gt_lines = [
        r"\begin{equation} A \cdot B = C \end{equation}",
        r"\lVert x \rVert_2 \le 1",
    ]
    pred_lines = [
        r"\lVert x \rVert \le 1",                          # Should pair with gt_lines[1]
        r"\begin{equation} A . B = C \end{equation}",       # Should pair with gt_lines[0]
    ]

    row_ind, col_ind, costs = adapter.match_upstream_fixture_lines(gt_lines, pred_lines)

    # gt[0] pairs with pred[1], gt[1] pairs with pred[0]
    assignment = dict(zip(row_ind, col_ind))
    assert assignment[0] == 1
    assert assignment[1] == 0
    # Both pairs should have low normalized cost under CDM normalization
    for c in costs:
        assert c < 0.25

