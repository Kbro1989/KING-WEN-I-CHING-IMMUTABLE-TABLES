r"""OmniDocBench External Evaluation Adapter (Channel B: Perceptual CDM Matching).

Adapts OmniDocBench's Hungarian matching (match_quick.py) and visual token
normalization (visual_matcher.py) to provide standardized external perceptual
comparison metrics without modifying King Wen Math's source-preservation model.

Three-Channel Architecture Boundary:
  - Channel A (Raw LaTeX): Strict character-exact comparison.
  - Channel B (Perceptual CDM): Hungarian assignment with visual token normalization
    (44 rules / 30 buckets) yielding edit distance, precision, recall, and F1.
  - Channel C (Semantic Structural Validation): King Wen Math Stage 1 (AST isomorphism
    and operator preservation) and Stage 2 (mathematical residual evaluation).
    Channel C strictly forbids operator flattening (\cdot -> ., \lVert -> |, etc.).

Invariants:
  - Zero external package installation: Uses scipy.optimize.linear_sum_assignment
    and self-contained Wagner-Fischer edit distance algorithm.
  - Non-destructive: Channel B metrics never overwrite or dictate Channel C verdicts.
"""
from __future__ import annotations

import re
import sys
from typing import Any

# pyrefly: ignore[missing-import]
import numpy as np
from scipy.optimize import linear_sum_assignment

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

# OmniDocBench 44-rule token mapping (from visual_matcher.py)
CDM_TOKEN_MAP = {
    r"\quad": " ",
    r"\qquad": " ",
    r"\enspace": " ",
    r"\thinspace": " ",
    r"\;": " ",
    r"\,": " ",
    r"\:": " ",
    r"\!": "",
    r"\left": "",
    r"\right": "",
    r"\big": "",
    r"\Big": "",
    r"\bigg": "",
    r"\Bigg": "",
    r"\bigl": "",
    r"\Bigl": "",
    r"\biggl": "",
    r"\Biggl": "",
    r"\bigr": "",
    r"\Bigr": "",
    r"\biggr": "",
    r"\Biggr": "",
    r"\cdot": ".",
    r"\cdots": "...",
    r"\ldots": "...",
    r"\dots": "...",
    r"\prime": "'",
    r"\lbrace": "{",
    r"\rbrace": "}",
    r"\lbrack": "[",
    r"\rbrack": "]",
    r"\vert": "|",
    r"\mid": "|",
    r"\parallel": "||",
    r"\lVert": "||",
    r"\rVert": "||",
    r"\langle": "<",
    r"\rangle": ">",
    r"\le": "<=",
    r"\leq": "<=",
    r"\ge": ">=",
    r"\geq": ">=",
    r"\neq": "!=",
    r"\ne": "!=",
}


def levenshtein_distance(s1: str, s2: str) -> int:
    """Wagner-Fischer dynamic programming algorithm for Levenshtein edit distance."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    v0 = list(range(len(s2) + 1))
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0 = v1[:]

    return v1[len(s2)]


def normalize_cdm_tokens(latex_str: str) -> str:
    """Channel B: Apply OmniDocBench's 44-rule perceptual normalization."""
    res = latex_str
    # Replace whitespace/formatting/delimiters/operators per CDM map
    for k, v in CDM_TOKEN_MAP.items():
        res = res.replace(k, v)
    # Collapse consecutive whitespace
    res = re.sub(r"\s+", " ", res).strip()
    return res


def compute_iou(bbox1: list[float], bbox2: list[float]) -> float:
    """Compute Intersection-over-Union between two [x0, y0, x1, y1] bboxes."""
    x0 = max(bbox1[0], bbox2[0])
    y0 = max(bbox1[1], bbox2[1])
    x1 = min(bbox1[2], bbox2[2])
    y1 = min(bbox1[3], bbox2[3])

    inter_w = max(0.0, x1 - x0)
    inter_h = max(0.0, y1 - y0)
    inter_area = inter_w * inter_h

    area1 = max(0.0, bbox1[2] - bbox1[0]) * max(0.0, bbox1[3] - bbox1[1])
    area2 = max(0.0, bbox2[2] - bbox2[0]) * max(0.0, bbox2[3] - bbox2[1])
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


METRIC_IDENTIFIER = "KING-WEN-LOCAL-CDM-V1.0"
METRIC_VERSION = "1.0.0"
UPSTREAM_REFERENCE = "OmniDocBench@0604d98 (match_quick.py, visual_matcher.py)"
METRIC_CAVEAT = "Locally reproduced Hungarian bipartite matching approximation. Not an official upstream benchmark score."


class HungarianCDMAdapter:
    """Channel B evaluator performing bipartite matching and perceptual scoring."""

    def __init__(self, iou_weight: float = 0.4, text_weight: float = 0.6):
        self.iou_weight = iou_weight
        self.text_weight = text_weight

    def compute_upstream_edit_distance_matrix(
        self,
        gt_lines: list[str],
        pred_lines: list[str],
    ) -> np.ndarray:
        """Exact reproduction of OmniDocBench lines 1700-1706 cost matrix."""
        n_gt = len(gt_lines)
        n_pred = len(pred_lines)
        matrix = np.zeros((n_gt, n_pred), dtype=np.float32)
        for i in range(n_gt):
            g_norm = normalize_cdm_tokens(gt_lines[i])
            for j in range(n_pred):
                p_norm = normalize_cdm_tokens(pred_lines[j])
                max_len = max(len(g_norm), len(p_norm), 1)
                matrix[i, j] = levenshtein_distance(g_norm, p_norm) / max_len
        return matrix

    def match_upstream_fixture_lines(
        self,
        gt_lines: list[str],
        pred_lines: list[str],
    ) -> tuple[list[int], list[int], list[float]]:
        """Exact reproduction of OmniDocBench Hungarian line assignment."""
        if not gt_lines or not pred_lines:
            return [], [], []
        cost_mat = self.compute_upstream_edit_distance_matrix(gt_lines, pred_lines)
        row_ind, col_ind = linear_sum_assignment(cost_mat)
        costs = [float(cost_mat[r, c]) for r, c in zip(row_ind, col_ind)]
        return list(row_ind), list(col_ind), costs

    def match_and_evaluate(
        self,
        predictions: list[dict],
        ground_truth: list[dict],
    ) -> dict[str, Any]:
        """Perform Hungarian assignment between predictions and GT items.

        Each item must have:
          - "bbox": [x0, y0, x1, y1]
          - "latex": str
        """
        n_pred = len(predictions)
        n_gt = len(ground_truth)

        base_meta = {
            "metric_identifier": METRIC_IDENTIFIER,
            "metric_version": METRIC_VERSION,
            "upstream_reference": UPSTREAM_REFERENCE,
            "metric_caveat": METRIC_CAVEAT,
            "channel": "CHANNEL_B_PERCEPTUAL_CDM",
        }

        if n_pred == 0 or n_gt == 0:
            return {
                **base_meta,
                "matched_pairs": 0,
                "precision": 0.0 if n_pred > 0 else 1.0,
                "recall": 0.0 if n_gt > 0 else 1.0,
                "f1_score": 0.0,
                "average_iou": 0.0,
                "average_norm_edit_distance": 1.0 if (n_pred + n_gt) > 0 else 0.0,
                "matches": [],
            }

        # Build cost matrix: [n_pred, n_gt]
        cost_matrix = np.zeros((n_pred, n_gt), dtype=np.float32)

        for i, p in enumerate(predictions):
            p_text = normalize_cdm_tokens(p.get("latex", ""))
            p_bbox = p.get("bbox", [0, 0, 0, 0])
            for j, g in enumerate(ground_truth):
                g_text = normalize_cdm_tokens(g.get("latex", ""))
                g_bbox = g.get("bbox", [0, 0, 0, 0])

                # Bbox distance cost: 1.0 - IoU
                iou = compute_iou(p_bbox, g_bbox)
                iou_cost = 1.0 - iou

                # Text edit distance cost
                max_len = max(len(p_text), len(g_text), 1)
                dist = levenshtein_distance(p_text, g_text)
                norm_edit_dist = dist / max_len

                cost = (self.iou_weight * iou_cost) + (self.text_weight * norm_edit_dist)
                cost_matrix[i, j] = cost

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        matches = []
        total_iou = 0.0
        total_edit_dist = 0.0

        for r, c in zip(row_ind, col_ind):
            p = predictions[r]
            g = ground_truth[c]
            p_norm = normalize_cdm_tokens(p.get("latex", ""))
            g_norm = normalize_cdm_tokens(g.get("latex", ""))
            iou = compute_iou(p.get("bbox", [0, 0, 0, 0]), g.get("bbox", [0, 0, 0, 0]))
            max_len = max(len(p_norm), len(g_norm), 1)
            dist = levenshtein_distance(p_norm, g_norm)
            norm_dist = dist / max_len

            total_iou += iou
            total_edit_dist += norm_dist

            matches.append({
                "pred_index": int(r),
                "gt_index": int(c),
                "cost": float(cost_matrix[r, c]),
                "iou": float(iou),
                "norm_edit_distance": float(norm_dist),
                "pred_norm_latex": p_norm,
                "gt_norm_latex": g_norm,
            })

        matched_count = len(matches)
        precision = matched_count / n_pred if n_pred > 0 else 0.0
        recall = matched_count / n_gt if n_gt > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        avg_iou = total_iou / matched_count if matched_count > 0 else 0.0
        avg_dist = total_edit_dist / matched_count if matched_count > 0 else 0.0

        return {
            **base_meta,
            "matched_pairs": matched_count,
            "precision": float(round(precision, 4)),
            "recall": float(round(recall, 4)),
            "f1_score": float(round(f1, 4)),
            "average_iou": float(round(avg_iou, 4)),
            "average_norm_edit_distance": float(round(avg_dist, 4)),
            "matches": matches,
        }
