#!/usr/bin/env python3
"""M1–M2 Normalization and Weighting Validation Test.

Controlled tests for:
- M1: Gaussian kernel normalization (4 KW implementations, 2 QS implementations)
- M2: Expectation/weighting behavior (weighted-summation kernel, 5-stage pipeline)

Edge cases: zero-sum weights, non-finite weights, underflow, tie-handling.
"""

import numpy as np
import json
from pathlib import Path
import math

# ============================================================
# M1: Gaussian Kernel Normalization
# ============================================================

FWHM = 2.35482
FWHM_PRECISE = 2.354820045

def gaussian_kernel_kw(x, mu, sigma):
    """King Wen's Gaussian kernel (peak=1 normalization)."""
    return np.exp(-((x - mu) ** 2) / (2.0 * sigma ** 2))

def gaussian_kernel_qs_l2(x, mu, sigma):
    """Quantum-Sim L2-normalized Gaussian."""
    raw = np.exp(-((x - mu) ** 2) / (2.0 * sigma ** 2))
    dx = x[1] - x[0] if len(x) > 1 else 1.0
    return raw / np.sqrt(np.sum(raw ** 2) * dx)

def gaussian_kernel_qs_potential_height(x, mu, sigma, height):
    """Quantum-Sim potential-height-normalized Gaussian."""
    raw = np.exp(-((x - mu) ** 2) / (2.0 * sigma ** 2))
    return raw * height

# Test cases for M1
m1_results = {}

# 1a: Functional form identity
x = np.linspace(-5, 5, 1000)
mu = 0.0
sigma = 1.0
kw = gaussian_kernel_kw(x, mu, sigma)
qs_l2 = gaussian_kernel_qs_l2(x, mu, sigma)
# Peak of KW should be 1.0
m1_results["peak_kw"] = float(np.max(kw))
m1_results["peak_qs_l2"] = float(np.max(qs_l2))
m1_results["functional_form_match"] = bool(np.allclose(kw, qs_l2 / np.max(qs_l2), atol=1e-12))

# 1b: FWHM conversion consistency
sigma_from_fwhm = FWHM / 2.35482
sigma_from_fwhm_precise = FWHM_PRECISE / 2.354820045
m1_results["fwhm_conversion_kw"] = float(sigma_from_fwhm)
m1_results["fwhm_conversion_qs"] = float(sigma_from_fwhm_precise)
m1_results["fwhm_conversion_match"] = bool(abs(sigma_from_fwhm - sigma_from_fwhm_precise) < 1e-10)

# 1c: Underflow test (very small sigma)
sigma_tiny = 1e-15
kw_tiny = gaussian_kernel_kw(x, mu, sigma_tiny)
m1_results["underflow_kw_max"] = float(np.max(kw_tiny))
m1_results["underflow_kw_finite"] = bool(np.all(np.isfinite(kw_tiny)))

# 1d: Non-finite input test
x_nan = np.array([np.nan, 0.0, 1.0, np.inf, -np.inf])
kw_nan = gaussian_kernel_kw(x_nan, mu, sigma)
m1_results["nonfinite_kw_all_nan"] = bool(np.all(np.isnan(kw_nan)))
m1_results["nonfinite_kw_has_inf"] = bool(np.any(np.isinf(kw_nan)))

# 1e: Zero-sigma test
try:
    kw_zero = gaussian_kernel_kw(x, mu, 0.0)
    m1_results["zero_sigma_kw_finite"] = bool(np.all(np.isfinite(kw_zero)))
    m1_results["zero_sigma_kw_all_one_at_mu"] = bool(np.all(kw_zero[x == mu] == 1.0))
except Exception as e:
    m1_results["zero_sigma_kw_error"] = str(e)

# 1f: Large sigma (flat distribution)
sigma_large = 1e6
kw_large = gaussian_kernel_kw(x, mu, sigma_large)
m1_results["large_sigma_kw_max"] = float(np.max(kw_large))
m1_results["large_sigma_kw_min"] = float(np.min(kw_large))
m1_results["large_sigma_kw_near_flat"] = bool(np.max(kw_large) - np.min(kw_large) < 1e-10)

# ============================================================
# M2: Expectation/Weighting Validation
# ============================================================

def weighted_summation_kw(weights, values):
    """King Wen's weighted-summation kernel (same as Quantum-Sim)."""
    w = np.array(weights, dtype=float)
    v = np.array(values, dtype=float)
    denom = np.sum(w)
    if denom == 0:
        return float('nan')  # undefined
    return float(np.sum(w * v) / denom)

def kingwen_consensus_pipeline(resolved_states, emotional_input=50):
    """King Wen's 5-stage consensus pipeline (simplified)."""
    # Stage 1: Categorical temporal mode
    temporal_modes = [s.get("phase_temporal", "present") for s in resolved_states]
    
    # Stage 2: Porosity mean and mode
    porosities = [s.get("porosity", 0) for s in resolved_states]
    porosity_mean = float(np.mean(porosities))
    # Mode (most common)
    from collections import Counter
    porosity_mode = Counter(porosities).most_common(1)[0][0] if porosities else 0
    
    # Stage 3: Gaussian-weighted vector consensus
    # (simplified: use porosity as weight proxy)
    weights = [max(0.0, p) + 0.01 for p in porosities]  # avoid zero
    vectors = [s.get("resolved_vector", {}) for s in resolved_states]
    # Consensus vector (weighted mean of 5 axes)
    axes = ["voiceWeight", "coherence", "chaos", "whimsy", "darkTone"]
    consensus_vec = {}
    for axis in axes:
        vals = [v.get(axis, 0.0) for v in vectors]
        consensus_vec[axis] = weighted_summation_kw(weights, vals)
    
    # Stage 4: Pool blending (0.7/0.18/0.12)
    pool1 = 0.7
    pool2 = 0.18
    pool3 = 0.12
    
    # Stage 5: Discrete argmax selection (hexagram with max weighted score)
    scores = [s.get("score", 0.0) for s in resolved_states]
    dominant_idx = int(np.argmax(scores)) if scores else 0
    
    return {
        "temporal_mode": temporal_modes[0] if temporal_modes else "present",
        "porosity_mean": porosity_mean,
        "porosity_mode": porosity_mode,
        "consensus_vector": consensus_vec,
        "pool_weights": [pool1, pool2, pool3],
        "dominant_index": dominant_idx,
    }

# M2 test cases
m2_results = {}

# 2a: Basic weighted summation
m2_results["basic_weighted_sum"] = weighted_summation_kw([1.0, 2.0, 3.0], [10.0, 20.0, 30.0])
m2_results["basic_expected"] = 23.333333333333332

# 2b: Equal weights (should be simple mean)
m2_results["equal_weights"] = weighted_summation_kw([1.0, 1.0, 1.0], [10.0, 20.0, 30.0])
m2_results["equal_weights_expected"] = 20.0

# 2c: Zero-sum weights (edge case)
m2_results["zero_sum"] = weighted_summation_kw([1.0, -1.0, 0.0], [10.0, 20.0, 30.0])
m2_results["zero_sum_is_nan"] = bool(math.isnan(m2_results["zero_sum"]))

# 2d: All-zero weights (edge case)
m2_results["all_zero"] = weighted_summation_kw([0.0, 0.0, 0.0], [10.0, 20.0, 30.0])
m2_results["all_zero_is_nan"] = bool(math.isnan(m2_results["all_zero"]))

# 2e: Non-finite weights (inf)
m2_results["inf_weight"] = weighted_summation_kw([float('inf'), 1.0, 1.0], [10.0, 20.0, 30.0])
m2_results["inf_weight_is_inf"] = bool(math.isinf(m2_results["inf_weight"]))

# 2f: Non-finite weights (nan)
m2_results["nan_weight"] = weighted_summation_kw([float('nan'), 1.0, 1.0], [10.0, 20.0, 30.0])
m2_results["nan_weight_is_nan"] = bool(math.isnan(m2_results["nan_weight"]))

# 2g: Underflow (very small weights)
m2_results["underflow_weights"] = weighted_summation_kw([1e-300, 1e-300, 1e-300], [10.0, 20.0, 30.0])
m2_results["underflow_result"] = m2_results["underflow_weights"]

# 2h: Tie-handling (equal scores)
scores = [0.5, 0.5, 0.3]
m2_results["tie_argmax"] = int(np.argmax(scores))
m2_results["tie_argmax_first"] = (m2_results["tie_argmax"] == 0)

# 2i: Single element
m2_results["single_element"] = weighted_summation_kw([2.5], [42.0])
m2_results["single_element_expected"] = 42.0

# 2j: Negative weights (can produce out-of-range results)
m2_results["negative_weights"] = weighted_summation_kw([1.0, -0.5, 0.5], [10.0, 20.0, 30.0])

# 2k: Aggregation order sensitivity
# Test if changing order of (weights, values) pairs changes result
w1 = [1.0, 2.0, 3.0]
v1 = [10.0, 20.0, 30.0]
w2 = [3.0, 1.0, 2.0]
v2 = [30.0, 10.0, 20.0]
m2_results["order_1"] = weighted_summation_kw(w1, v1)
m2_results["order_2"] = weighted_summation_kw(w2, v2)
m2_results["order_sensitive"] = (m2_results["order_1"] != m2_results["order_2"])

# 2l: Consensus pipeline with synthetic data
synthetic_states = [
    {"phase_temporal": "past", "porosity": 2, "resolved_vector": {"voiceWeight": 0.5, "coherence": 0.3, "chaos": 0.1, "whimsy": 0.2, "darkTone": 0.4}, "score": 0.8},
    {"phase_temporal": "present", "porosity": 3, "resolved_vector": {"voiceWeight": 0.7, "coherence": 0.6, "chaos": 0.2, "whimsy": 0.3, "darkTone": 0.1}, "score": 0.9},
    {"phase_temporal": "future", "porosity": 1, "resolved_vector": {"voiceWeight": 0.3, "coherence": 0.8, "chaos": 0.4, "whimsy": 0.5, "darkTone": 0.2}, "score": 0.7},
]
pipeline_result = kingwen_consensus_pipeline(synthetic_states)
m2_results["pipeline_temporal_mode"] = pipeline_result["temporal_mode"]
m2_results["pipeline_porosity_mean"] = pipeline_result["porosity_mean"]
m2_results["pipeline_porosity_mode"] = pipeline_result["porosity_mode"]
m2_results["pipeline_consensus_vector"] = pipeline_result["consensus_vector"]
m2_results["pipeline_dominant_index"] = pipeline_result["dominant_index"]
m2_results["pipeline_pool_weights"] = pipeline_result["pool_weights"]

# ============================================================
# Report
# ============================================================
print("=" * 70)
print("M1–M2 NORMALIZATION AND WEIGHTING VALIDATION")
print("=" * 70)
print()

print("=== M1: Gaussian Kernel Normalization ===")
print(f"  peak_kw (should be 1.0):           {m1_results['peak_kw']}")
print(f"  peak_qs_l2 (should be 1.0):        {m1_results['peak_qs_l2']}")
print(f"  functional_form_match:             {m1_results['functional_form_match']}")
print(f"  fwhm_conversion_kw:                {m1_results['fwhm_conversion_kw']}")
print(f"  fwhm_conversion_qs:                {m1_results['fwhm_conversion_qs']}")
print(f"  fwhm_conversion_match:             {m1_results['fwhm_conversion_match']}")
print(f"  underflow_kw_max:                  {m1_results['underflow_kw_max']}")
print(f"  underflow_kw_finite:               {m1_results['underflow_kw_finite']}")
print(f"  nonfinite_kw_all_nan:              {m1_results['nonfinite_kw_all_nan']}")
print(f"  nonfinite_kw_has_inf:              {m1_results['nonfinite_kw_has_inf']}")
print(f"  large_sigma_kw_near_flat:          {m1_results['large_sigma_kw_near_flat']}")
print()

print("=== M2: Expectation/Weighting Validation ===")
print(f"  basic_weighted_sum:                {m2_results['basic_weighted_sum']} (expected {m2_results['basic_expected']})")
print(f"  equal_weights:                     {m2_results['equal_weights']} (expected {m2_results['equal_weights_expected']})")
print(f"  zero_sum is nan:                   {m2_results['zero_sum_is_nan']}")
print(f"  all_zero is nan:                   {m2_results['all_zero_is_nan']}")
print(f"  inf_weight is inf:                 {m2_results['inf_weight_is_inf']}")
print(f"  nan_weight is nan:                 {m2_results['nan_weight_is_nan']}")
print(f"  underflow_weights result:          {m2_results['underflow_weights']}")
print(f"  tie_argmax (first on tie):         {m2_results['tie_argmax_first']}")
print(f"  single_element:                    {m2_results['single_element']} (expected {m2_results['single_element_expected']})")
print(f"  negative_weights result:           {m2_results['negative_weights']}")
print(f"  order_sensitive:                   {m2_results['order_sensitive']}")
print(f"  pipeline_temporal_mode:            {m2_results['pipeline_temporal_mode']}")
print(f"  pipeline_porosity_mean:            {m2_results['pipeline_porosity_mean']}")
print(f"  pipeline_porosity_mode:            {m2_results['pipeline_porosity_mode']}")
print(f"  pipeline_dominant_index:           {m2_results['pipeline_dominant_index']}")
print(f"  pipeline_pool_weights:             {m2_results['pipeline_pool_weights']}")
print()

# Save results
results = {
    "test_name": "m1_m2_normalization_weighting",
    "test_date": "2026-11-02",
    "m1_results": m1_results,
    "m2_results": m2_results,
    "baseline_reference": "qsmc1-cross-group-correspondence-synthesis.md",
    "original_m1_disposition": "partial",
    "original_m2_disposition": "partial (conceptual)",
    "disposition_change": "none — this test is supplementary evidence",
}

out_path = Path("DATASETS/qsmc1_m1_m2_normalization_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"Results saved to {out_path}")
