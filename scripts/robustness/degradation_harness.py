"""Content-Addressed Deterministic Degradation Harness.

Implements PureDocBench's 15 degradation operations across 4 stages:
  Stage 1 (Print): ink_bleed, low_resolution, toner_speckle, ink_fade
  Stage 2 (Paper): crumple_folds, shadow_vignette, yellowing_tint, moisture_stain
  Stage 3 (Capture): perspective_skew, motion_blur, gaussian_sensor_noise, defocus_blur
  Stage 4 (Digital): jpeg_compression, threshold_binarization, downsampling_quantization

Cryptographic Seeding Specification:
  Full experiment identity (256-bit SHA-256 digest):
    S = SHA-256(H_source || H_profile || seed_version)
  PRNG 32-bit seed:
    s32 = int(S[:8], 16) % (2**32)

  Both S and s32 are recorded. Note: SHA-256 is collision-resistant (not collision-free);
  32-bit truncation introduces seed-space collision potential, which is mitigated by
  preserving the 256-bit parent digest S.
  Canonical JSON serialization follows RFC 8785 (UTF-8, sorted keys, separators (',', ':')).
  PRNG Engine: python:random.Random(version=2) and numpy.random.default_rng(PCG64).
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

# pyrefly: ignore[missing-import]
import cv2
# pyrefly: ignore[missing-import]
import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

SEED_SPEC_VERSION = "KING-WEN-DEGRADATION-SEED-V1"
PRNG_ENGINE_METADATA = {
    "engine": "numpy.random.default_rng",
    "bit_generator": "PCG64",
    "python_random_version": 2,
    "seed_spec_version": SEED_SPEC_VERSION,
}


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize object according to RFC 8785 canonical JSON rules."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_content_addressed_seed(
    source_bytes: bytes,
    profile_dict: dict,
    seed_version: str = SEED_SPEC_VERSION,
) -> tuple[str, int]:
    """Compute 256-bit digest S and 32-bit PRNG seed s32.

    S = SHA-256(H_source || H_profile || seed_version)
    s32 = int(S[:8], 16) % (2**32)
    """
    h_source = hashlib.sha256(source_bytes).hexdigest()
    profile_canonical = canonical_json_bytes(profile_dict)
    h_profile = hashlib.sha256(profile_canonical).hexdigest()

    combined = f"{h_source}:{h_profile}:{seed_version}".encode("utf-8")
    s_full = hashlib.sha256(combined).hexdigest()
    s32 = int(s_full[:8], 16) % (2**32)
    return s_full, s32


# ==============================================================================
# STAGE 1: PRINT DEGRADATIONS
# ==============================================================================

def op_ink_bleed(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate ink absorption and fiber spreading."""
    k_size = int(max(1, round(severity * 3)))
    if k_size % 2 == 0:
        k_size += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
    # Erode bright background to expand dark ink
    return cv2.erode(img, kernel, iterations=1)


def op_low_resolution(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate low DPI printing by downscaling then upscaling."""
    h, w = img.shape[:2]
    scale = max(0.2, 1.0 - (severity * 0.7))
    small = cv2.resize(img, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def op_toner_speckle(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate toner scatter / speckle artifacts."""
    out = img.copy()
    num_speckles = int(round(severity * img.shape[0] * img.shape[1] * 0.001))
    ys = rng.integers(0, img.shape[0], size=num_speckles)
    xs = rng.integers(0, img.shape[1], size=num_speckles)
    values = rng.integers(30, 160, size=num_speckles, dtype=np.uint8)
    for y, x, v in zip(ys, xs, values):
        out[y, x] = [v, v, v] if out.ndim == 3 else v
    return out


def op_ink_fade(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate ink fade / low toner contrast reduction."""
    alpha = max(0.3, 1.0 - (severity * 0.5))
    beta = int(round(255 * (1.0 - alpha)))
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


# ==============================================================================
# STAGE 2: PAPER DEGRADATIONS
# ==============================================================================

def op_crumple_folds(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate paper creases / shadow creases."""
    h, w = img.shape[:2]
    num_folds = int(max(1, round(severity * 4)))
    overlay = np.ones((h, w), dtype=np.float32)
    for _ in range(num_folds):
        x0, y0 = rng.integers(0, w), rng.integers(0, h)
        x1, y1 = rng.integers(0, w), rng.integers(0, h)
        mask = np.zeros((h, w), dtype=np.uint8)
        thickness = int(rng.integers(2, 6))
        cv2.line(mask, (int(x0), int(y0)), (int(x1), int(y1)), 255, thickness)
        blur = cv2.GaussianBlur(mask.astype(np.float32), (15, 15), 0) / 255.0
        intensity_low = float(0.05 * severity)
        intensity_high = float(max(intensity_low + 0.01, 0.3 * severity))
        intensity = float(rng.uniform(intensity_low, intensity_high))
        overlay -= blur * intensity
    overlay = np.clip(overlay, 0.2, 1.0)
    if img.ndim == 3:
        overlay = overlay[:, :, np.newaxis]
    return np.clip(img.astype(np.float32) * overlay, 0, 255).astype(np.uint8)


def op_shadow_vignette(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate radial or corner shadow vignette."""
    h, w = img.shape[:2]
    Y, X = np.ogrid[:h, :w]
    center_y, center_x = h / 2.0, w / 2.0
    dist = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
    max_dist = np.sqrt(center_x**2 + center_y**2)
    vignette = 1.0 - (dist / max_dist) * (0.5 * severity)
    vignette = np.clip(vignette, 0.3, 1.0)
    if img.ndim == 3:
        vignette = vignette[:, :, np.newaxis]
    return np.clip(img.astype(np.float32) * vignette, 0, 255).astype(np.uint8)


def op_yellowing_tint(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate paper yellowing / aging tint."""
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    out = img.astype(np.float32)
    # BGR format: reduce Blue channel, slightly reduce Green
    blue_loss = severity * 40.0
    green_loss = severity * 10.0
    out[:, :, 0] = np.clip(out[:, :, 0] - blue_loss, 0, 255)
    out[:, :, 1] = np.clip(out[:, :, 1] - green_loss, 0, 255)
    return out.astype(np.uint8)


def op_moisture_stain(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate an elliptical water or fluid stain."""
    h, w = img.shape[:2]
    cx = int(rng.integers(max(1, int(w * 0.2)), max(2, int(w * 0.8))))
    cy = int(rng.integers(max(1, int(h * 0.2)), max(2, int(h * 0.8))))
    ax_w = int(rng.integers(5, max(6, int(w * 0.3))))
    ax_h = int(rng.integers(5, max(6, int(h * 0.3))))
    axes = (ax_w, ax_h)
    angle = float(rng.uniform(0, 180))

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(mask, (cx, cy), axes, angle, 0, 360, 255, -1)
    blurred_mask = cv2.GaussianBlur(mask.astype(np.float32), (25, 25), 0) / 255.0
    stain_factor = 1.0 - (blurred_mask * (0.25 * severity))
    if img.ndim == 3:
        stain_factor = stain_factor[:, :, np.newaxis]
    return np.clip(img.astype(np.float32) * stain_factor, 0, 255).astype(np.uint8)


# ==============================================================================
# STAGE 3: CAPTURE DEGRADATIONS
# ==============================================================================

def op_perspective_skew(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate angled camera perspective distortion."""
    h, w = img.shape[:2]
    max_shift = max(2.0, severity * 0.08 * min(h, w))
    pts1 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dx0, dy0 = rng.uniform(-max_shift, max_shift), rng.uniform(-max_shift, max_shift)
    dx1, dy1 = rng.uniform(-max_shift, max_shift), rng.uniform(-max_shift, max_shift)
    dx2, dy2 = rng.uniform(-max_shift, max_shift), rng.uniform(-max_shift, max_shift)
    dx3, dy3 = rng.uniform(-max_shift, max_shift), rng.uniform(-max_shift, max_shift)

    pts2 = np.float32([
        [max(0, dx0), max(0, dy0)],
        [w + min(0, dx1), max(0, dy1)],
        [w + min(0, dx2), h + min(0, dy2)],
        [max(0, dx3), h + min(0, dy3)],
    ])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, M, (w, h), borderValue=(255, 255, 255) if img.ndim == 3 else 255)


def op_motion_blur(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate 1D directional camera shake motion blur."""
    size = int(max(3, round(severity * 9)))
    if size % 2 == 0:
        size += 1
    angle = float(rng.uniform(0, 180))
    M = cv2.getRotationMatrix2D((size / 2, size / 2), angle, 1)
    kernel = np.zeros((size, size), dtype=np.float32)
    kernel[int((size - 1) / 2), :] = np.ones(size, dtype=np.float32)
    kernel = cv2.warpAffine(kernel, M, (size, size))
    k_sum = np.sum(kernel)
    if k_sum > 0:
        kernel = kernel / k_sum
    return cv2.filter2D(img, -1, kernel)


def op_gaussian_sensor_noise(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate sensor ISO electronic noise."""
    sigma = float(severity * 25.0)
    noise = rng.normal(0, sigma, img.shape)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def op_defocus_blur(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate out-of-focus camera optics."""
    k_size = int(max(3, round(severity * 7)))
    if k_size % 2 == 0:
        k_size += 1
    sigma = max(0.5, severity * 2.0)
    return cv2.GaussianBlur(img, (k_size, k_size), sigma)


# ==============================================================================
# STAGE 4: DIGITAL DEGRADATIONS
# ==============================================================================

def op_jpeg_compression(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate lossy JPEG encoding artifacts."""
    quality = int(max(10, round(95 - (severity * 75))))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, enc = cv2.imencode(".jpg", img, encode_param)
    if not success:
        return img
    return cv2.imdecode(enc, cv2.IMREAD_UNCHANGED if img.ndim == 3 else cv2.IMREAD_GRAYSCALE)


def op_threshold_binarization(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate facsimile / threshold binarization."""
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    thresh_val = int(round(128 + (rng.uniform(-20, 20) * severity)))
    _, bin_img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    if img.ndim == 3:
        return cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR)
    return bin_img


def op_downsampling_quantization(img: np.ndarray, rng: np.random.Generator, severity: float = 0.5) -> np.ndarray:
    """Simulate color quantization / posterization."""
    levels = int(max(2, round(16 - (severity * 12))))
    step = 256 // levels
    quantized = (img // step) * step + (step // 2)
    return np.clip(quantized, 0, 255).astype(np.uint8)


# Registry of 15 Operations
OPERATIONS = {
    # Stage 1
    "ink_bleed": op_ink_bleed,
    "low_resolution": op_low_resolution,
    "toner_speckle": op_toner_speckle,
    "ink_fade": op_ink_fade,
    # Stage 2
    "crumple_folds": op_crumple_folds,
    "shadow_vignette": op_shadow_vignette,
    "yellowing_tint": op_yellowing_tint,
    "moisture_stain": op_moisture_stain,
    # Stage 3
    "perspective_skew": op_perspective_skew,
    "motion_blur": op_motion_blur,
    "gaussian_sensor_noise": op_gaussian_sensor_noise,
    "defocus_blur": op_defocus_blur,
    # Stage 4
    "jpeg_compression": op_jpeg_compression,
    "threshold_binarization": op_threshold_binarization,
    "downsampling_quantization": op_downsampling_quantization,
}

STAGE_MAPPING = {
    "ink_bleed": "stage_1_print",
    "low_resolution": "stage_1_print",
    "toner_speckle": "stage_1_print",
    "ink_fade": "stage_1_print",
    "crumple_folds": "stage_2_paper",
    "shadow_vignette": "stage_2_paper",
    "yellowing_tint": "stage_2_paper",
    "moisture_stain": "stage_2_paper",
    "perspective_skew": "stage_3_capture",
    "motion_blur": "stage_3_capture",
    "gaussian_sensor_noise": "stage_3_capture",
    "defocus_blur": "stage_3_capture",
    "jpeg_compression": "stage_4_digital",
    "threshold_binarization": "stage_4_digital",
    "downsampling_quantization": "stage_4_digital",
}


class DegradationHarness:
    """Deterministic, content-addressed degradation runner."""

    def __init__(self, seed_version: str = SEED_SPEC_VERSION):
        self.seed_version = seed_version

    def apply_profile(
        self,
        img: np.ndarray,
        profile: dict,
    ) -> tuple[np.ndarray, dict]:
        """Apply a sequence of degradation operations defined by profile.

        Profile structure:
          {
            "profile_name": "clean_scan",
            "operations": [
              {"name": "ink_bleed", "severity": 0.4},
              {"name": "gaussian_sensor_noise", "severity": 0.2}
            ]
          }
        """
        img_bytes = img.tobytes()
        s_full, s32 = compute_content_addressed_seed(img_bytes, profile, self.seed_version)
        rng = np.random.default_rng(s32)

        current = img.copy()
        executed_ops = []

        for op_spec in profile.get("operations", []):
            name = op_spec.get("name")
            if name not in OPERATIONS:
                raise ValueError(f"Unknown operation: {name}")
            severity = float(op_spec.get("severity", 0.5))
            op_fn = OPERATIONS[name]
            current = op_fn(current, rng, severity)
            executed_ops.append({
                "operation": name,
                "stage": STAGE_MAPPING[name],
                "severity": severity,
            })

        result_manifest = {
            "experiment_identity_digest_sha256": s_full,
            "prng_seed_32bit": s32,
            "prng_metadata": PRNG_ENGINE_METADATA,
            "profile_name": profile.get("profile_name", "unnamed"),
            "source_image_shape": list(img.shape),
            "output_image_shape": list(current.shape),
            "executed_operations": executed_ops,
        }
        return current, result_manifest

