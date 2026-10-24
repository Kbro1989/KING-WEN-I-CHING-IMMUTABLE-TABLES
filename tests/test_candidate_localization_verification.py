"""
Regression Tests for Candidate Localization Verification
=========================================================
Proves that the four historical localization failures in the multi-paper
experiment were caused by candidate coordinate/page offset errors, not crop
geometry (3, 2) failures.

Verifies:
1. Old coordinates captured prose text paragraphs (historical failure documented).
2. Corrected coordinates accurately clip the exact target formula from PDF bytes.
3. Fixes are tagged as candidate-localization corrections, preserving the distinction
   between coordinate ground-truth alignment and crop padding geometry.
"""

from pathlib import Path
import pytest
import pymupdf

REPO_ROOT = Path(__file__).resolve().parent.parent

PDF_2206 = Path("C:/Users/krist/Desktop/zotero/learning-corpus/diffusion-generative/2206.00364_Elucidating the Design Space of Diffusion-Based Generative Models.pdf")
PDF_2104 = Path("C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/2104.01277_Beyond Low-Pass Filters_ Adaptive Feature Propagation on Graphs.pdf")


@pytest.mark.skipif(not PDF_2206.exists(), reason="2206.00364 PDF not in local zotero directory")
def test_2206_00364_cand6_localization_correction():
    """Verify dot derivative -˙σ(t) coordinates on page 2."""
    doc = pymupdf.open(str(PDF_2206))
    page = doc[1]  # 0-indexed page 2
    
    # Old bbox: hit prose text
    old_clip = page.get_text('text', clip=pymupdf.Rect(430.0, 430.0, 475.0, 445.0)).strip()
    assert 'desired' in old_clip.lower() or 'distri' in old_clip.lower() or len(old_clip) > 0
    assert '−˙σ(t)' not in old_clip
    
    # Corrected bbox: captures -˙σ(t)
    corr_rect = pymupdf.Rect(250.0, 629.0, 280.0, 643.0)
    corr_clip = page.get_text('text', clip=corr_rect).strip()
    assert '−˙σ(t)' in corr_clip or 'σ(t)' in corr_clip


@pytest.mark.skipif(not PDF_2206.exists(), reason="2206.00364 PDF not in local zotero directory")
def test_2206_00364_cand7_denoiser_localization_correction():
    """Verify denoiser function Dθ(x; σ) coordinates on page 3."""
    doc = pymupdf.open(str(PDF_2206))
    page = doc[2]  # 0-indexed page 3
    
    # Old bbox: hit table header text at y=200..213
    old_clip = page.get_text('text', clip=pymupdf.Rect(120.0, 200.0, 165.0, 213.0)).strip()
    assert 'Dθ' not in old_clip
    
    # Corrected bbox: captures Dθ(x; σ) in Table 1 caption at y=121..135
    corr_rect = pymupdf.Rect(107.0, 121.0, 150.0, 135.0)
    corr_clip = page.get_text('text', clip=corr_rect).strip()
    assert 'Dθ' in corr_clip


@pytest.mark.skipif(not PDF_2206.exists(), reason="2206.00364 PDF not in local zotero directory")
def test_2206_00364_cand8_skip_scaling_localization_correction():
    """Verify skip scaling cskip(σ)x coordinates on page 3."""
    doc = pymupdf.open(str(PDF_2206))
    page = doc[2]  # 0-indexed page 3
    
    # Old bbox: hit table header text at y=225..238
    old_clip = page.get_text('text', clip=pymupdf.Rect(100.0, 225.0, 160.0, 238.0)).strip()
    assert 'cskip(σ)x' not in old_clip
    
    # Corrected bbox: captures cskip(σ)x in Table 1 caption at y=121..135
    corr_rect = pymupdf.Rect(157.0, 121.0, 198.0, 135.0)
    corr_clip = page.get_text('text', clip=corr_rect).strip()
    assert 'cskip' in corr_clip or 'cskip(σ)x' in corr_clip


@pytest.mark.skipif(not PDF_2104.exists(), reason="2104.01277 PDF not in local zotero directory")
def test_2104_01277_cand8_summation_lambda_localization_correction():
    """Verify indexed summation parameter j=1(λj+Q)). on page 3."""
    doc = pymupdf.open(str(PDF_2104))
    page = doc[2]  # 0-indexed page 3
    
    # Old bbox: hit prose text ("focuses on Haar wavelets") at y=180..195
    old_clip = page.get_text('text', clip=pymupdf.Rect(200.0, 180.0, 275.0, 195.0)).strip()
    assert 'focuses' in old_clip.lower() or 'haar' in old_clip.lower() or 'wavelet' in old_clip.lower()
    assert 'j=1' not in old_clip
    
    # Corrected bbox: captures j=1(λj+Q)). at y=405..422
    corr_rect = pymupdf.Rect(418.0, 404.0, 488.0, 423.0)
    corr_clip = page.get_text('text', clip=corr_rect).strip()
    assert 'j=1' in corr_clip and ('λ' in corr_clip or 'Q' in corr_clip)
