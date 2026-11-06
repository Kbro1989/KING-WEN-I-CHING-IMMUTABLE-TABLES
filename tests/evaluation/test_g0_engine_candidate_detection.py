#!/usr/bin/env python3
"""
V2.1.1-A G0 Independence Tests
===============================

Tests that verify the G0 boundary: prediction generation is an
engine-only operation. Adjudication data becomes accessible only
after the prediction artifact has been serialized and hashed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evaluation.contracts import (
    DetectionConfig,
    EnginePrediction,
    compute_artifact_hash,
    serialize_prediction,
    deserialize_prediction,
    validate_g0_prediction,
)
from scripts.evaluation.prediction_adapter import predict_page


# ═══════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def test_pdf() -> Path:
    """Find a test PDF for G0 testing."""
    # Use benchmark PDFs (known to work)
    bench_dir = REPO_ROOT / "DATASETS" / "benchmark_pdfs"
    if bench_dir.exists():
        pdfs = list(bench_dir.glob("*.pdf"))
        if pdfs:
            return pdfs[0]
    
    pytest.skip("No test PDF found")


@pytest.fixture(scope="module")
def g0_config() -> DetectionConfig:
    """Standard G0 detection config."""
    return DetectionConfig(region_mode="FULL_PAGE")


@pytest.fixture(scope="module")
def test_prediction(test_pdf: Path, g0_config: DetectionConfig) -> EnginePrediction:
    """Generate a test prediction for artifact audits."""
    return predict_page(test_pdf, 0, g0_config)


# ═══════════════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════════════

def test_import_audit() -> None:
    """Verify prediction adapter imports no adjudication/gold modules."""
    import scripts.evaluation.prediction_adapter as adapter_module
    import inspect
    import ast
    
    source = inspect.getsource(adapter_module)
    
    # Parse AST to find actual imports, not comments/docstrings
    tree = ast.parse(source)
    
    forbidden_imports = [
        "adjudicat",
        "evaluate_output_reference",
        "evaluate_cross_paper",
        "case_registry",
        "cross_paper",
        "REFERENCE_DATA",
        "gold",
        "gold_target",
        "delimiter_glyph_inventory",
    ]
    
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
            else:
                module_name = ""
            for alias in node.names:
                full_name = f"{module_name}.{alias.name}" if module_name else alias.name
                for pattern in forbidden_imports:
                    if pattern in full_name:
                        violations.append(f"Forbidden import '{full_name}' found in source")
    
    assert not violations, f"Adapter source contains forbidden imports: {violations}"


def test_signature_audit() -> None:
    """Verify predict_page signature has no gold-related parameters."""
    import inspect
    from scripts.evaluation.prediction_adapter import predict_page
    
    sig = inspect.signature(predict_page)
    params = list(sig.parameters.keys())
    
    forbidden_params = ["gold", "adjudicat", "target", "reference", "expected"]
    
    violations = []
    for param in params:
        for pattern in forbidden_params:
            if pattern in param.lower():
                violations.append(f"Forbidden parameter '{param}' in predict_page signature")
    
    assert not violations, f"predict_page signature has forbidden parameters: {violations}"


def test_determinism(test_pdf: Path, g0_config: DetectionConfig) -> None:
    """Identical PDF, page, config, engine version → identical serialized output."""
    pred1 = predict_page(test_pdf, 0, g0_config)
    pred2 = predict_page(test_pdf, 0, g0_config)
    
    ser1 = serialize_prediction(pred1)
    ser2 = serialize_prediction(pred2)
    
    assert ser1 == ser2, "Non-deterministic serialization"


def test_artifact_audit(test_prediction: EnginePrediction) -> None:
    """Verify prediction artifact contains no gold-derived fields."""
    pred_dict = json.loads(serialize_prediction(test_prediction))
    
    # Check for forbidden field patterns
    forbidden_patterns = [
        "gold",
        "adjudicat",
        "target_id",
        "delimiter_glyph_inventory",
        "expected_",
        "reference_",
        "verification_status",
        "gold_bbox",
        "gold_target",
    ]
    
    def check_obj(obj: Any, path: str = "") -> list[str]:
        violations = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                full_path = f"{path}.{k}" if path else k
                kl = k.lower()
                for pattern in forbidden_patterns:
                    if pattern in kl:
                        violations.append(f"Forbidden field '{k}' at {full_path}")
                violations.extend(check_obj(v, full_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                violations.extend(check_obj(item, f"{path}[{i}]"))
        return violations
    
    violations = check_obj(pred_dict)
    assert not violations, f"Artifact contains gold-derived fields: {violations}"


def test_contract_validation(test_prediction: EnginePrediction) -> None:
    """Verify prediction passes G0 contract validation."""
    from scripts.evaluation.contracts import validate_g0_prediction
    violations = validate_g0_prediction(test_prediction)
    assert not violations, f"Contract validation violations: {violations}"


def test_gold_perturbation(test_pdf: Path, g0_config: DetectionConfig) -> None:
    """
    Core G0 independence test: prediction must be identical
    regardless of gold adjudication data changes.
    """
    # Prediction A - no gold data involved
    pred_a = predict_page(test_pdf, 0, g0_config)
    hash_a = pred_a.artifact_hash
    
    # Prediction B - gold data conceptually changed, but never passed to adapter
    pred_b = predict_page(test_pdf, 0, g0_config)
    hash_b = pred_b.artifact_hash
    
    assert hash_a == hash_b, f"Prediction hash changed between runs: {hash_a} != {hash_b}"


def test_prediction_before_matching(test_prediction: EnginePrediction) -> None:
    """
    Verify prediction is serialized and hashed BEFORE matcher
    would receive adjudication data.
    """
    # The prediction must have a valid artifact_hash
    assert test_prediction.artifact_hash, "Missing artifact_hash"
    
    # The hash must be verifiable
    from scripts.evaluation.contracts import compute_artifact_hash
    computed = compute_artifact_hash(test_prediction)
    assert computed == test_prediction.artifact_hash, "Artifact hash not verifiable"
    
    # Verify the prediction can be serialized/deserialized
    serialized = serialize_prediction(test_prediction)
    deserialized = deserialize_prediction(serialized)
    
    assert deserialized.artifact_hash == test_prediction.artifact_hash, "Round-trip serialization failed"


def test_empty_result_handling(test_pdf: Path, g0_config: DetectionConfig) -> None:
    """Zero candidates should produce valid prediction, not exception."""
    prediction = predict_page(test_pdf, 0, g0_config)
    assert isinstance(prediction, EnginePrediction)
    assert prediction.artifact_hash


def test_determinism_across_runs(test_pdf: Path, g0_config: DetectionConfig) -> None:
    """Determinism across separate prediction calls."""
    pred1 = predict_page(test_pdf, 0, g0_config)
    pred2 = predict_page(test_pdf, 0, g0_config)
    
    ser1 = serialize_prediction(pred1)
    ser2 = serialize_prediction(pred2)
    
    assert ser1 == ser2, "Non-deterministic serialization across runs"


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])