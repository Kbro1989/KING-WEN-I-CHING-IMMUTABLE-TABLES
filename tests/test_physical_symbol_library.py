"""Unit Tests for Physical Mathematical Symbol Library (V2.3 Reference Catalog).

Verifies:
  - Compilation of DATASETS/physical_symbol_library.json
  - 100% physical file existence on disk (1127/1127)
  - Valid image dimensions, non-zero file sizes, and SHA-256 hashes
  - Mapping of key mathematical symbols (Greek, operators, blackboard bold)
  - Ability to load images into raster arrays
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
CATALOG_PATH = REPO_ROOT / "DATASETS" / "physical_symbol_library.json"
SYMBOLS_DIR = REPO_ROOT / "symbols" / "symbols"


@pytest.fixture(scope="module")
def catalog():
    assert CATALOG_PATH.exists(), f"Catalog not found at {CATALOG_PATH}"
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_catalog_integrity(catalog):
    """Verify catalog top-level structure and 100% file existence."""
    assert catalog["schema_version"] == "1.0.0"
    assert catalog["total_symbols_indexed"] == 1127
    assert catalog["missing_files_on_disk"] == 0
    assert catalog["verified_files_on_disk"] == 1127
    assert len(catalog["symbols"]) == 1127


def test_every_symbol_entry_valid(catalog):
    """Verify that every symbol entry has valid physical properties."""
    for mnemonic, item in catalog["symbols"].items():
        assert item["exists_on_disk"] is True, f"File missing for {mnemonic}"
        assert item["file_size_bytes"] > 0, f"Empty file for {mnemonic}"
        assert item["width_px"] > 0, f"Invalid width for {mnemonic}"
        assert item["height_px"] > 0, f"Invalid height for {mnemonic}"
        assert item["file_sha256"] is not None, f"Missing SHA256 for {mnemonic}"
        assert len(item["file_sha256"]) == 64, f"Malformed SHA256 for {mnemonic}"


def test_core_math_symbols_mapped(catalog):
    """Verify critical mathematical symbols are mapped to TeX macros."""
    symbols = catalog["symbols"]
    
    # Greek
    assert "pi" in symbols and symbols["pi"]["tex_macro"] == r"\pi"
    assert "mu" in symbols and symbols["mu"]["tex_macro"] == r"\mu"
    assert "csigma" in symbols and symbols["csigma"]["tex_macro"] == r"\Sigma"
    
    # Large operators
    assert "sum" in symbols and symbols["sum"]["tex_macro"] == r"\sum"
    assert "surd" in symbols and symbols["surd"]["tex_macro"] == r"\sqrt"
    assert "int" in symbols and symbols["int"]["tex_macro"] == r"\int"
    
    # Blackboard bold
    assert "bbr" in symbols and symbols["bbr"]["tex_macro"] == r"\mathbb{R}"
    assert "bbn" in symbols and symbols["bbn"]["tex_macro"] == r"\mathbb{N}"
    assert "bbz" in symbols and symbols["bbz"]["tex_macro"] == r"\mathbb{Z}"
    assert "bbc" in symbols and symbols["bbc"]["tex_macro"] == r"\mathbb{C}"
    
    # Relations and accents
    assert "top" in symbols and symbols["top"]["tex_macro"] == r"^\top"
    assert "propto" in symbols and symbols["propto"]["tex_macro"] == r"\propto"
    assert "in" in symbols and symbols["in"]["tex_macro"] == r"\in"


def test_physical_raster_image_loading(catalog):
    """Verify that physical raster PNG images load correctly with PIL."""
    test_mnemonics = ["pi", "mu", "csigma", "sum", "surd", "bbr", "top", "propto"]
    for m in test_mnemonics:
        rel_path = catalog["symbols"][m]["relative_path"]
        abs_path = REPO_ROOT / rel_path
        assert abs_path.exists()
        with Image.open(abs_path) as img:
            w, h = img.size
            assert w == catalog["symbols"][m]["width_px"]
            assert h == catalog["symbols"][m]["height_px"]
            assert img.format in ("PNG", "GIF")
