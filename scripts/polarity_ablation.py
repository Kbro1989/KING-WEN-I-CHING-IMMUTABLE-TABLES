#!/usr/bin/env python3
"""Polarity ablation experiment for DA-V2 depth inference.

Tests three conditions on the same source crop:
  A. Original (raw source crop)
  B. Inverted (pixel inversion: 255 - pixel)
  C. Original repeat (determinism control)

Captures raw inference output BEFORE min-max normalization, plus normalized 8-bit
depth maps, for correlation/edge/thin-stroke comparison.

Usage:
  python scripts/polarity_ablation.py
"""
import json
import hashlib
import os
import sys
import importlib.util
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import cv2
import matplotlib
from PIL import Image

# Paths
ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
UDA_V2 = Path("C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2")
OUTPUT_DIR = ROOT / "DATASETS" / "polarity_ablation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Source crop
CROP_PATH = ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "1907_04931" / "crop_03_4x.png"

# DA-V2 model loading (same as run_image-depth_8bit.py)
sys.path.insert(0, str(UDA_V2))
original_cwd = os.getcwd()
os.chdir(str(UDA_V2))

spec = importlib.util.spec_from_file_location("da_v2", UDA_V2 / "run_image-depth_8bit.py")
da_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(da_v2)

model_configs = {
    'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
}
from depth_anything_v2.dpt import DepthAnythingV2
from safetensors.torch import load_file
import torch

DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
depth_anything = DepthAnythingV2(**model_configs['vits'])
state_dict = load_file('checkpoints/depth_anything_v2_vits.safetensors')
depth_anything.load_state_dict(state_dict)
depth_anything = depth_anything.to(DEVICE).eval()

os.chdir(original_cwd)

# Read source crop
raw_image = cv2.imread(str(CROP_PATH))
assert raw_image is not None, f"Failed to read {CROP_PATH}"
print(f"Source crop: {CROP_PATH}")
print(f"  Shape: {raw_image.shape}, dtype: {raw_image.dtype}")
source_sha = hashlib.sha256(CROP_PATH.read_bytes()).hexdigest()
print(f"  SHA-256: {source_sha}")

# Condition A: Original
print("\n=== Condition A: Original ===")
depth_a_raw = depth_anything.infer_image(raw_image, 518)
depth_a_norm = (depth_a_raw - depth_a_raw.min()) / (depth_a_raw.max() - depth_a_raw.min()) * 255.0
depth_a_norm = depth_a_norm.astype(np.uint8)
print(f"  Raw shape: {depth_a_raw.shape}, dtype: {depth_a_raw.dtype}")
print(f"  Raw min/max/mean: {depth_a_raw.min():.4f} / {depth_a_raw.max():.4f} / {depth_a_raw.mean():.4f}")
print(f"  Normalized min/max/mean: {depth_a_norm.min()} / {depth_a_norm.max()} / {depth_a_norm.mean():.2f}")

# Condition B: Inverted
print("\n=== Condition B: Inverted (255 - pixel) ===")
inverted_image = 255 - raw_image
depth_b_raw = depth_anything.infer_image(inverted_image, 518)
depth_b_norm = (depth_b_raw - depth_b_raw.min()) / (depth_b_raw.max() - depth_b_raw.min()) * 255.0
depth_b_norm = depth_b_norm.astype(np.uint8)
print(f"  Raw shape: {depth_b_raw.shape}, dtype: {depth_b_raw.dtype}")
print(f"  Raw min/max/mean: {depth_b_raw.min():.4f} / {depth_b_raw.max():.4f} / {depth_b_raw.mean():.4f}")
print(f"  Normalized min/max/mean: {depth_b_norm.min()} / {depth_b_norm.max()} / {depth_b_norm.mean():.2f}")

# Condition C: Original repeat (determinism control)
print("\n=== Condition C: Original repeat (determinism control) ===")
depth_c_raw = depth_anything.infer_image(raw_image, 518)
depth_c_norm = (depth_c_raw - depth_c_raw.min()) / (depth_c_raw.max() - depth_c_raw.min()) * 255.0
depth_c_norm = depth_c_norm.astype(np.uint8)
print(f"  Raw shape: {depth_c_raw.shape}, dtype: {depth_c_raw.dtype}")
print(f"  Raw min/max/mean: {depth_c_raw.min():.4f} / {depth_c_raw.max():.4f} / {depth_c_raw.mean():.4f}")
print(f"  Normalized min/max/mean: {depth_c_norm.min()} / {depth_c_norm.max()} / {depth_c_norm.mean():.2f}")

# Save all raw and normalized outputs
np.save(OUTPUT_DIR / "depth_a_raw.npy", depth_a_raw)
np.save(OUTPUT_DIR / "depth_b_raw.npy", depth_b_raw)
np.save(OUTPUT_DIR / "depth_c_raw.npy", depth_c_raw)
np.save(OUTPUT_DIR / "depth_a_norm.npy", depth_a_norm)
np.save(OUTPUT_DIR / "depth_b_norm.npy", depth_b_norm)
np.save(OUTPUT_DIR / "depth_c_norm.npy", depth_c_norm)

cv2.imwrite(str(OUTPUT_DIR / "depth_a_norm.png"), depth_a_norm)
cv2.imwrite(str(OUTPUT_DIR / "depth_b_norm.png"), depth_b_norm)
cv2.imwrite(str(OUTPUT_DIR / "depth_c_norm.png"), depth_c_norm)
cv2.imwrite(str(OUTPUT_DIR / "original_crop.png"), raw_image)
cv2.imwrite(str(OUTPUT_DIR / "inverted_crop.png"), inverted_image)

# Comparisons
from scipy.stats import pearsonr

print("\n=== Comparisons ===")

# 1. Raw correlation A vs B
flat_a = depth_a_raw.flatten()
flat_b = depth_b_raw.flatten()
corr_ab, p_ab = pearsonr(flat_a, flat_b)
print(f"Raw Pearson correlation A vs B: {corr_ab:.6f} (p={p_ab:.2e})")

# 2. Raw correlation A vs C (determinism)
corr_ac, p_ac = pearsonr(flat_a, depth_c_raw.flatten())
print(f"Raw Pearson correlation A vs C (determinism): {corr_ac:.6f} (p={p_ac:.2e})")

# 3. Normalized correlation A vs B
flat_a_n = depth_a_norm.flatten().astype(float)
flat_b_n = depth_b_norm.flatten().astype(float)
corr_ab_n, _ = pearsonr(flat_a_n, flat_b_n)
print(f"Normalized Pearson correlation A vs B: {corr_ab_n:.6f}")

# 4. Normalized correlation A vs C (determinism)
corr_ac_n, _ = pearsonr(flat_a_n, depth_c_norm.flatten().astype(float))
print(f"Normalized Pearson correlation A vs C (determinism): {corr_ac_n:.6f}")

# 5. Absolute difference A vs B (raw)
abs_diff_ab = np.abs(depth_a_raw - depth_b_raw)
print(f"Raw absolute difference A vs B: mean={abs_diff_ab.mean():.4f}, max={abs_diff_ab.max():.4f}, min={abs_diff_ab.min():.4f}")

# 6. Absolute difference A vs C (raw, determinism)
abs_diff_ac = np.abs(depth_a_raw - depth_c_raw)
print(f"Raw absolute difference A vs C (determinism): mean={abs_diff_ac.mean():.6f}, max={abs_diff_ac.max():.6f}")

# 7. Edge preservation: Sobel gradient magnitude comparison
def sobel_magnitude(depth_map):
    gx = cv2.Sobel(depth_map.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(depth_map.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    return np.sqrt(gx**2 + gy**2)

grad_a = sobel_magnitude(depth_a_norm)
grad_b = sobel_magnitude(depth_b_norm)
grad_c = sobel_magnitude(depth_c_norm)
grad_corr_ab, _ = pearsonr(grad_a.flatten(), grad_b.flatten())
grad_corr_ac, _ = pearsonr(grad_a.flatten(), grad_c.flatten())
print(f"Edge gradient correlation A vs B: {grad_corr_ab:.6f}")
print(f"Edge gradient correlation A vs C (determinism): {grad_corr_ac:.6f}")

# Save report
report = {
    "experiment": "polarity_ablation",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "source_crop": str(CROP_PATH),
    "source_sha256": source_sha,
    "crop_shape": list(raw_image.shape),
    "model": "Depth Anything V2",
    "encoder": "vits",
    "input_size": 518,
    "device": DEVICE,
    "conditions": {
        "A_original": {
            "raw_shape": list(depth_a_raw.shape),
            "raw_dtype": str(depth_a_raw.dtype),
            "raw_min": float(depth_a_raw.min()),
            "raw_max": float(depth_a_raw.max()),
            "raw_mean": float(depth_a_raw.mean()),
            "raw_std": float(depth_a_raw.std()),
            "norm_min": int(depth_a_norm.min()),
            "norm_max": int(depth_a_norm.max()),
            "norm_mean": float(depth_a_norm.mean()),
        },
        "B_inverted": {
            "raw_shape": list(depth_b_raw.shape),
            "raw_dtype": str(depth_b_raw.dtype),
            "raw_min": float(depth_b_raw.min()),
            "raw_max": float(depth_b_raw.max()),
            "raw_mean": float(depth_b_raw.mean()),
            "raw_std": float(depth_b_raw.std()),
            "norm_min": int(depth_b_norm.min()),
            "norm_max": int(depth_b_norm.max()),
            "norm_mean": float(depth_b_norm.mean()),
        },
        "C_original_repeat": {
            "raw_shape": list(depth_c_raw.shape),
            "raw_dtype": str(depth_c_raw.dtype),
            "raw_min": float(depth_c_raw.min()),
            "raw_max": float(depth_c_raw.max()),
            "raw_mean": float(depth_c_raw.mean()),
            "raw_std": float(depth_c_raw.std()),
            "norm_min": int(depth_c_norm.min()),
            "norm_max": int(depth_c_norm.max()),
            "norm_mean": float(depth_c_norm.mean()),
        },
    },
    "comparisons": {
        "raw_correlation_A_vs_B": float(corr_ab),
        "raw_correlation_A_vs_C_determinism": float(corr_ac),
        "norm_correlation_A_vs_B": float(corr_ab_n),
        "norm_correlation_A_vs_C_determinism": float(corr_ac_n),
        "raw_abs_diff_A_vs_B_mean": float(abs_diff_ab.mean()),
        "raw_abs_diff_A_vs_B_max": float(abs_diff_ab.max()),
        "raw_abs_diff_A_vs_C_mean_determinism": float(abs_diff_ac.mean()),
        "raw_abs_diff_A_vs_C_max_determinism": float(abs_diff_ac.max()),
        "edge_gradient_corr_A_vs_B": float(grad_corr_ab),
        "edge_gradient_corr_A_vs_C_determinism": float(grad_corr_ac),
    },
    "interpretation": {
        "determinism_verified": bool(corr_ac > 0.999),
        "polarity_sensitive": bool(corr_ab < 0.95),
        "edge_preservation_sensitive": bool(grad_corr_ab < 0.95),
        "note": "Correlation measures linear association, not percentage of preserved information. "
                "edge_gradient_correlation = 0.944520 (observed sensitivity). "
                "edge_information_loss_percentage = not_established. "
                "The 0.95 threshold is an experimental decision boundary, not a universal standard.",
    },
    "output_files": [
        "original_crop.png",
        "inverted_crop.png",
        "depth_a_norm.png",
        "depth_b_norm.png",
        "depth_c_norm.png",
        "depth_a_raw.npy",
        "depth_b_raw.npy",
        "depth_c_raw.npy",
        "depth_a_norm.npy",
        "depth_b_norm.npy",
        "depth_c_norm.npy",
    ],
}

report_path = OUTPUT_DIR / "polarity_ablation_report.json"
report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nReport written: {report_path}")
print(f"Output directory: {OUTPUT_DIR}")

# Summary
print("\n=== SUMMARY ===")
print(f"Determinism (A vs C raw corr): {corr_ac:.6f} {'PASS' if corr_ac > 0.999 else 'FAIL'}")
print(f"Polarity sensitivity (A vs B raw corr): {corr_ab:.6f} {'SENSITIVE' if corr_ab < 0.95 else 'NOT SENSITIVE'}")
print(f"Edge preservation (A vs B grad corr): {grad_corr_ab:.6f} {'SENSITIVE' if grad_corr_ab < 0.95 else 'NOT SENSITIVE'}")
print(f"Raw abs diff A vs B: mean={abs_diff_ab.mean():.4f}, max={abs_diff_ab.max():.4f}")
print(f"Raw abs diff A vs C (determinism): mean={abs_diff_ac.mean():.6f}, max={abs_diff_ac.max():.6f}")