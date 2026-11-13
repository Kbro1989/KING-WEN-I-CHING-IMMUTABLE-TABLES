"""Tests for Content-Addressed Deterministic Degradation Harness.

Verifies:
  1. All 15 operations across 4 stages execute successfully.
  2. Deterministic reproducibility: same image + same profile -> exact byte-for-byte match.
  3. Sensitive identity: modifying image or profile alters S and s32.
  4. Both 256-bit SHA-256 digest S and 32-bit integer s32 are captured.
  5. PRNG engine metadata and canonical JSON compliance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
# pyrefly: ignore[missing-import]
import numpy as np
# pyrefly: ignore[missing-import]
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from robustness.degradation_harness import (
    OPERATIONS,
    STAGE_MAPPING,
    DegradationHarness,
    canonical_json_bytes,
    compute_content_addressed_seed,
)


@pytest.fixture
def synthetic_math_image():
    # 100x200 grayscale image with synthetic black text / glyphs
    img = np.full((100, 200, 3), 255, dtype=np.uint8)
    # Draw some synthetic strokes
    img[40:60, 50:150] = 0
    img[20:80, 48:52] = 0
    img[20:80, 148:152] = 0
    return img


def test_fifteen_operations_registered():
    assert len(OPERATIONS) == 15
    assert len(STAGE_MAPPING) == 15
    stages = set(STAGE_MAPPING.values())
    assert stages == {"stage_1_print", "stage_2_paper", "stage_3_capture", "stage_4_digital"}


@pytest.mark.parametrize("op_name", list(OPERATIONS.keys()))
def test_individual_operation_execution(op_name, synthetic_math_image):
    harness = DegradationHarness()
    profile = {
        "profile_name": f"test_{op_name}",
        "operations": [{"name": op_name, "severity": 0.5}],
    }
    out, manifest = harness.apply_profile(synthetic_math_image, profile)
    assert isinstance(out, np.ndarray)
    assert out.shape[0] == synthetic_math_image.shape[0]
    assert out.shape[1] == synthetic_math_image.shape[1]
    assert len(manifest["experiment_identity_digest_sha256"]) == 64
    assert isinstance(manifest["prng_seed_32bit"], int)
    assert 0 <= manifest["prng_seed_32bit"] < 2**32
    assert manifest["executed_operations"][0]["stage"] == STAGE_MAPPING[op_name]


def test_deterministic_reproducibility(synthetic_math_image):
    harness = DegradationHarness()
    profile = {
        "profile_name": "multi_stage_test",
        "operations": [
            {"name": "ink_bleed", "severity": 0.3},
            {"name": "crumple_folds", "severity": 0.4},
            {"name": "gaussian_sensor_noise", "severity": 0.2},
            {"name": "jpeg_compression", "severity": 0.6},
        ],
    }

    out1, m1 = harness.apply_profile(synthetic_math_image, profile)
    out2, m2 = harness.apply_profile(synthetic_math_image, profile)

    assert m1["experiment_identity_digest_sha256"] == m2["experiment_identity_digest_sha256"]
    assert m1["prng_seed_32bit"] == m2["prng_seed_32bit"]
    np.testing.assert_array_equal(out1, out2)


def test_identity_divergence_on_profile_change(synthetic_math_image):
    harness = DegradationHarness()
    p1 = {"profile_name": "p1", "operations": [{"name": "ink_bleed", "severity": 0.3}]}
    p2 = {"profile_name": "p2", "operations": [{"name": "ink_bleed", "severity": 0.31}]}

    _, m1 = harness.apply_profile(synthetic_math_image, p1)
    _, m2 = harness.apply_profile(synthetic_math_image, p2)

    assert m1["experiment_identity_digest_sha256"] != m2["experiment_identity_digest_sha256"]


def test_canonical_json_sorting():
    obj1 = {"b": 2, "a": 1, "nested": {"z": 9, "m": 5}}
    obj2 = {"a": 1, "nested": {"m": 5, "z": 9}, "b": 2}
    assert canonical_json_bytes(obj1) == canonical_json_bytes(obj2)
    assert canonical_json_bytes(obj1) == b'{"a":1,"b":2,"nested":{"m":5,"z":9}}'


# ------------------------------------------------------------------------------
# Three Explicit Acceptance Tests Mandated for Content-Addressed Reproducibility
# ------------------------------------------------------------------------------

def test_acceptance_filename_invariance(tmp_path):
    """1. Same PDF/image bytes, same profile, same generator version, different filename -> identical identity."""
    raw_bytes = b"EXACT_SAME_RAW_IMAGE_OR_PDF_STREAM_BYTES_12345"
    file_a = tmp_path / "document_alpha.pdf"
    file_b = tmp_path / "renamed_copy_beta.pdf"
    file_a.write_bytes(raw_bytes)
    file_b.write_bytes(raw_bytes)

    profile = {"profile_name": "clean_scan", "operations": [{"name": "ink_bleed", "severity": 0.3}]}
    version = "KING-WEN-DEGRADATION-SEED-V1"

    s_a, s32_a = compute_content_addressed_seed(file_a.read_bytes(), profile, version)
    s_b, s32_b = compute_content_addressed_seed(file_b.read_bytes(), profile, version)

    assert s_a == s_b, "Experiment identity S must depend only on content bytes, not filename"
    assert s32_a == s32_b


def test_acceptance_profile_divergence():
    """2. Same bytes, changed profile -> different experiment identity."""
    raw_bytes = b"EXACT_SAME_RAW_IMAGE_OR_PDF_STREAM_BYTES_12345"
    version = "KING-WEN-DEGRADATION-SEED-V1"

    p1 = {"profile_name": "profile_one", "operations": [{"name": "ink_bleed", "severity": 0.3}]}
    p2 = {"profile_name": "profile_two", "operations": [{"name": "ink_bleed", "severity": 0.35}]}

    s1, _ = compute_content_addressed_seed(raw_bytes, p1, version)
    s2, _ = compute_content_addressed_seed(raw_bytes, p2, version)

    assert s1 != s2, "Experiment identity S must diverge when profile changes"


def test_acceptance_version_divergence():
    """3. Same bytes and profile, changed generator version -> different experiment identity."""
    raw_bytes = b"EXACT_SAME_RAW_IMAGE_OR_PDF_STREAM_BYTES_12345"
    profile = {"profile_name": "standard", "operations": [{"name": "ink_bleed", "severity": 0.3}]}

    v1 = "KING-WEN-DEGRADATION-SEED-V1"
    v2 = "KING-WEN-DEGRADATION-SEED-V2-EXPERIMENTAL"

    s1, _ = compute_content_addressed_seed(raw_bytes, profile, v1)
    s2, _ = compute_content_addressed_seed(raw_bytes, profile, v2)

    assert s1 != s2, "Experiment identity S must diverge when seed generator version changes"


def test_independent_preservation_of_digest_and_prng_seed():
    """Verify that full 256-bit SHA-256 identity is preserved independently of 32-bit execution seed."""
    raw_bytes = b"SAMPLE_INDEPENDENT_BYTES"
    profile = {"profile_name": "test", "operations": []}
    s_full, s32 = compute_content_addressed_seed(raw_bytes, profile)

    assert len(s_full) == 64  # Full 256-bit hexadecimal string
    assert isinstance(s32, int)
    assert 0 <= s32 < 2**32
    # s32 is strictly derived from the first 8 characters
    assert s32 == int(s_full[:8], 16) % (2**32)


def test_acceptance_output_reproducibility():
    """Verify Output Reproducibility: regenerated corpus images are byte-identical to manifest hashes."""
    import hashlib
    import cv2
    manifest_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "degradation_corpus" / "manifest.json"
    corpus_dir = manifest_path.parent
    assert manifest_path.exists(), "Degradation corpus manifest must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    harness = DegradationHarness()

    for entry in manifest["corpus_entries"]:
        src_path = corpus_dir / entry["source_image_file"]
        assert src_path.exists(), f"Source image missing: {src_path}"
        src_img = cv2.imread(str(src_path), cv2.IMREAD_COLOR)

        # Reconstruct profile from executed operations
        profile = {
            "profile_name": entry["profile_name"],
            "operations": [{"name": op["operation"], "severity": op["severity"]} for op in entry["executed_operations"]],
        }

        # Regenerate fresh degraded image
        fresh_degraded, fresh_meta = harness.apply_profile(src_img, profile)

        # 1. Identity must match
        assert fresh_meta["experiment_identity_digest_sha256"] == entry["experiment_identity_digest_sha256"]
        assert fresh_meta["prng_seed_32bit"] == entry["prng_seed_32bit"]

        # 2. Output image bytes must be identical to recorded hash
        _, fresh_png = cv2.imencode(".png", fresh_degraded)
        fresh_hash = hashlib.sha256(fresh_png.tobytes()).hexdigest()
        assert fresh_hash == entry["output_image_sha256"], (
            f"Output reproducibility failure on {entry['output_image_file']}: "
            f"expected {entry['output_image_sha256']}, got {fresh_hash}"
        )


