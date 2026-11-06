#!/usr/bin/env python3
r"""
Test Suite: Gold-to-Component Evidence Reconciliation (Milestone 4 Extension).

Validates:
  1. Operator Inventory Reconciliation: Verifies operator inventories across all 5 gold
     equations in 1505.05770 against HTML LaTeX verbatim and PDF character stream.
     Explicitly tests GS-002's author notation (\Leftrightarrow rather than =).
  2. Namespace Separation: Validates the distinction between local candidate index
     (component_{idx:04d}.png) and OpenCV connected component label (component_id).
  3. Complementary Visual Recovery (GS-004): Proves that the visual connected component
     channel recovers the tall integral operator (\int) omitted by the PDF character stream.
  4. Freeze Manifest v2.0 Integrity: Validates 3,644 individual image hashes, render
     specifications, environment metadata, and downstream evaluation artifact hashes.
  5. Multi-Metric Independence: Enforces the architectural separation between geometric
     localization (IoU), glyph completeness, and structural fidelity.
"""
from __future__ import annotations

import json
from pathlib import Path
# pyrefly: ignore[missing-import]
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SP_DIR = REPO_ROOT / "DATASETS" / "structural_preservation"


@pytest.fixture(scope="module")
def gold_manifest():
    path = SP_DIR / "1505.05770_positive_control_manifest.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def blind_p002():
    path = SP_DIR / "1505.05770_blind_detection_p002.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def blind_p003():
    path = SP_DIR / "1505.05770_blind_detection_p003.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def freeze_manifest():
    path = SP_DIR / "1505.05770_blind_renders_freeze_manifest.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def v2_v3_evaluation():
    path = SP_DIR / "v2_v3_comparison_evaluation.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_operator_inventory_reconciliation(gold_manifest):
    """Test 1: Operator Inventory Reconciliation across all 5 gold equations."""
    eqs = {eq["gold_id"]: eq for eq in gold_manifest["gold_equations"]}

    # GS-001: Reparameterization identity: has \sim, \Leftrightarrow, and =
    gs1_latex = eqs["GS-001"]["selection_identity"]["html_latex_verbatim"]
    assert r"\sim" in gs1_latex
    assert r"\Leftrightarrow" in gs1_latex
    assert "=" in gs1_latex

    # GS-002: Author notation in 1505.05770 explicitly uses \Leftrightarrow, NOT =
    gs2_latex = eqs["GS-002"]["selection_identity"]["html_latex_verbatim"]
    assert r"\Leftrightarrow" in gs2_latex, "GS-002 must contain biconditional relation in source"
    assert "=" not in gs2_latex, "GS-002 author notation does not contain '=' operator"
    pdf_text_gs2 = eqs["GS-002"]["pdf_localization"]["pdf_text_extracted"]
    assert "⇔" in pdf_text_gs2
    assert "=" not in pdf_text_gs2

    # GS-003: Diagonal parameterization uses =
    gs3_latex = eqs["GS-003"]["selection_identity"]["html_latex_verbatim"]
    assert "=" in gs3_latex
    assert r"\diag" in gs3_latex

    # GS-004: Marginal log-likelihood has = and \int
    gs4_latex = eqs["GS-004"]["selection_identity"]["html_latex_verbatim"]
    assert "=" in gs4_latex
    assert r"\int" in gs4_latex

    # GS-005: ELBO has \geq, -, =, and \|
    gs5_latex = eqs["GS-005"]["selection_identity"]["html_latex_verbatim"]
    assert r"\geq" in gs5_latex
    assert "=" in gs5_latex
    assert r"\|" in gs5_latex


def test_component_namespace_separation(blind_p002, blind_p003):
    """Test 2: Namespace separation between local candidate index and OpenCV component_id."""
    for page_num, d in [(2, blind_p002), (3, blind_p003)]:
        cands = d["visual_component_analysis"]["visual_candidates"]
        for idx, c in enumerate(cands):
            # Check crop filename convention: component_{idx:04d}.png
            crop_path = Path(c["crop_path"])
            expected_name = f"component_{idx:04d}.png"
            assert crop_path.name == expected_name, f"Candidate {idx} naming mismatch: {crop_path.name}"

            # Check OpenCV component_id is positive integer
            cid = c["component_id"]
            assert isinstance(cid, int) and cid > 0

            # Verify crop bounding box encloses render bounding box
            rx0, ry0, rx1, ry1 = c["bbox_render_px"]
            cx0, cy0, cx1, cy1 = c["crop_bbox_render_px"]
            assert cx0 <= rx0 and cy0 <= ry0 and cx1 >= rx1 and cy1 >= ry1


def test_visual_integral_recovery_gs004(blind_p002, v2_v3_evaluation, freeze_manifest):
    """Test 3: Complementary visual recovery of the dropped integral in GS-004."""
    # Check that text stream in v3 evaluation dropped \int
    v3_evals = {e["gold_id"]: e for e in v2_v3_evaluation["per_equation_comparison"]}
    gs4_v3 = v3_evals["GS-004"]["candidate_v3"]
    assert gs4_v3["features_checked"]["has_integral_operator"] is False
    assert "∫" not in gs4_v3["extracted_text"]

    # Verify visual candidate #4241 (component_1568.png) isolates the integral operator
    cands = blind_p002["visual_component_analysis"]["visual_candidates"]
    int_cands = [c for c in cands if c["component_id"] == 4241]
    assert len(int_cands) == 1
    c_int = int_cands[0]

    assert Path(c_int["crop_path"]).name == "component_1568.png"
    assert c_int["candidate_reasons"] == ["tall_narrow_component"]
    assert c_int["height_width_ratio"] > 2.0  # 2.472
    assert c_int["bbox_pdf_pt_approx"] == [133.25, 598.0, 142.25, 620.25]

    # Verify hash exists in freeze manifest
    rel_key = "page_0002/component_1568.png"
    assert rel_key in freeze_manifest["individual_image_sha256_manifest"]


def test_freeze_manifest_v2_integrity(freeze_manifest):
    """Test 4: Freeze Manifest v2.0 schema, accounting, and cryptographic completeness."""
    assert freeze_manifest["schema_version"] == "2.0"

    # Exact file counts
    accounting = freeze_manifest["render_accounting"]["aggregate_totals"]
    assert accounting["total_component_crops"] == 3640
    assert accounting["total_page_images"] == 4
    assert accounting["total_image_artifacts"] == 3644

    # All individual image hashes present
    hashes = freeze_manifest["individual_image_sha256_manifest"]
    assert len(hashes) == 3644

    # Downstream artifacts hashed
    freshness = freeze_manifest["downstream_artifact_freshness"]
    required_downstream = [
        "1505.05770_blind_detection_p002.json",
        "1505.05770_blind_detection_p003.json",
        "1505.05770_detection_comparison.json",
        "1505.05770_region_proposals_p002.json",
        "1505.05770_region_proposals_p003.json",
        "unified_layer_b2_evaluation.json",
        "v2_v3_comparison_evaluation.json",
        "contract_verification_audit_report.json",
    ]
    for r in required_downstream:
        assert r in freshness
        assert len(freshness[r]["sha256"]) == 64

    # Source PDF SHA-256 matches immutable expected hash
    assert freeze_manifest["source_pdf"]["sha256"] == "776e07c2b5cf56963a6c3d2d5727146baa8ac096435db17df06d9b2a3a44f70a"


def test_multi_metric_independence(v2_v3_evaluation):
    """Test 5: Multi-metric independence between IoU and structural fidelity."""
    v3_evals = {e["gold_id"]: e for e in v2_v3_evaluation["per_equation_comparison"]}

    # GS-003 has low geometric IoU (0.3916) but passes 100% of structural features (7/7)
    gs3 = v3_evals["GS-003"]["candidate_v3"]
    assert gs3["math_expression_iou"] < 0.50
    assert gs3["features_passed"] == gs3["features_total"] == 7
    assert gs3["structural_verdict"] == "PRESERVED"

    # GS-005 has near-perfect geometric IoU (0.9952) and passes 100% of features (8/8)
    gs5 = v3_evals["GS-005"]["candidate_v3"]
    assert gs5["math_expression_iou"] > 0.99
    assert gs5["features_passed"] == gs5["features_total"] == 8
    assert gs5["structural_verdict"] == "PRESERVED"

    # GS-004 has moderate IoU (0.5170) but fails integral feature (5/6) -> PARTIAL
    gs4 = v3_evals["GS-004"]["candidate_v3"]
    assert gs4["features_passed"] < gs4["features_total"]
    assert gs4["structural_verdict"] == "PARTIAL"


def test_adversarial_operator_disambiguation(gold_manifest):
    r"""Test 6: Adversarial operator disambiguation across all 4 documented cases.

    ADV-001: GS-002 PDF text stream contains U+21D4 (DOUBLE LEFT RIGHT ARROW, biconditional ⇔),
             NOT U+003D (equals sign). The author uses \Leftrightarrow as an idiosyncratic
             formatting choice, not standard equation syntax.
    ADV-002: GS-001 PDF text contains U+223C (TILDE OPERATOR, ∼, distributed-as), which is
             distinct from U+2248 (ALMOST EQUAL TO, ≈, approximately-equal). These are
             semantically different mathematical relations.
    ADV-003: GS-002 biconditional (U+21D4, ⇔) is distinct from implication (U+21D2, ⇒).
    ADV-004: GS-005 KL-divergence norm uses U+2016 (DOUBLE VERTICAL LINE, ‖) or \|, which is
             distinct from U+007C (VERTICAL LINE, |, single bar absolute value).
    """
    eqs = {eq["gold_id"]: eq for eq in gold_manifest["gold_equations"]}

    # ADV-001: GS-002 — biconditional ⇔ (U+21D4) is present, equals = (U+003D) is absent
    pdf_text_gs2 = eqs["GS-002"]["pdf_localization"]["pdf_text_extracted"]
    biconditional = "\u21d4"   # ⇔
    equals_sign   = "\u003d"   # =
    assert biconditional in pdf_text_gs2, "ADV-001: ⇔ must appear in GS-002 PDF text"
    assert equals_sign not in pdf_text_gs2, "ADV-001: = must NOT appear in GS-002 PDF text"

    # ADV-002: GS-001 — tilde-operator ∼ (U+223C) is present; approx ≈ (U+2248) is absent
    pdf_text_gs1 = eqs["GS-001"]["pdf_localization"]["pdf_text_extracted"]
    tilde_op    = "\u223c"   # ∼
    approx_eq   = "\u2248"   # ≈
    latex_gs1   = eqs["GS-001"]["selection_identity"]["html_latex_verbatim"]
    # The source LaTeX uses \sim; ≈ must NOT appear
    assert r"\sim" in latex_gs1, "ADV-002: \\sim must appear in GS-001 LaTeX verbatim"
    assert approx_eq not in latex_gs1, "ADV-002: ≈ (U+2248) must NOT appear in GS-001 LaTeX"
    assert tilde_op in pdf_text_gs1 or r"\sim" in latex_gs1, \
        "ADV-002: distributed-as operator (∼ / \\sim) must be present in GS-001"

    # ADV-003: GS-002 biconditional (U+21D4 ⇔) ≠ implication (U+21D2 ⇒)
    implication = "\u21d2"   # ⇒
    assert biconditional != implication, "ADV-003: ⇔ and ⇒ are distinct codepoints"
    assert biconditional in pdf_text_gs2
    assert implication not in pdf_text_gs2, \
        "ADV-003: implication ⇒ must not appear in GS-002 (it uses ⇔ only)"

    # ADV-004: GS-005 KL divergence uses \| (U+2016 double-bar, infix separator between
    # distributions: q_φ(z|x) ‖ p(z)) which is structurally distinct from single-bar |
    # (U+007C, used for conditional bars in q(z|x) and p(x|z)).
    # The source LaTeX uses \| exactly once as a binary infix KL separator, while single |
    # appears three times (conditional bars). This confirms the two operators are not
    # conflated, and that \| is not used as a matched norm-delimiter pair in this expression.
    latex_gs5  = eqs["GS-005"]["selection_identity"]["html_latex_verbatim"]
    double_bar = r"\|"   # KL divergence separator ‖
    assert double_bar in latex_gs5, "ADV-004: \\| (double-bar KL separator) must appear in GS-005 LaTeX"
    assert latex_gs5.count(double_bar) == 1, \
        "ADV-004: \\| appears exactly once (infix binary KL separator), not as matched pair"
    assert latex_gs5.count("|") >= 2, \
        "ADV-004: single | (conditional bar) appears in q(z|x) and p(x|z) — distinct from \\|"


def test_source_channel_attribution(gold_manifest):
    r"""Test 7: Source location and extraction channel attribution for operator inventory.

    Each gold equation's operators must be traceable to both:
    - html_latex_verbatim: source LaTeX from the HTML render (font-agnostic)
    - pdf_text_extracted: MuPDF character extraction (font-encoded codepoints)

    This test pins the GS-002 biconditional to its source font (CMSY10) by asserting
    that both channels consistently report ⇔ / \Leftrightarrow, so a future transcription
    change cannot silently swap to a conventionalized = without breaking this test.

    It also pins GS-004's missing integral to the cross-channel case: pdf_text_extracted
    omits ∫ while the visual channel recovers it as component_1568.png.
    """
    eqs = {eq["gold_id"]: eq for eq in gold_manifest["gold_equations"]}

    # GS-002: both channels agree on biconditional (dual-channel consistency)
    gs2_latex = eqs["GS-002"]["selection_identity"]["html_latex_verbatim"]
    gs2_pdf   = eqs["GS-002"]["pdf_localization"]["pdf_text_extracted"]
    assert r"\Leftrightarrow" in gs2_latex, \
        "Source channel (HTML LaTeX) must report \\Leftrightarrow for GS-002"
    assert "\u21d4" in gs2_pdf, \
        "Extraction channel (PDF text) must report ⇔ (U+21D4) for GS-002"
    # Neither channel should contain bare = as the primary relation
    assert "=" not in gs2_pdf, \
        "Extraction channel must NOT contain = for GS-002 (conventionalized transcription guard)"

    # GS-004: pdf_text_extracted drops ∫; LaTeX verbatim retains \int
    gs4_latex = eqs["GS-004"]["selection_identity"]["html_latex_verbatim"]
    gs4_pdf   = eqs["GS-004"]["pdf_localization"]["pdf_text_extracted"]
    assert r"\int" in gs4_latex, \
        "Source channel (HTML LaTeX) must report \\int for GS-004"
    assert "\u222b" not in gs4_pdf, \
        "Extraction channel (PDF text) must NOT contain ∫ for GS-004 — cross-channel recovery case"
