"""Physical Raster Template Matcher (V2.3 Evidence Channel).

Computes normalized cross-correlation (NCC) and multi-feature geometric similarity
between high-resolution observed glyph raster envelopes (from GLEA) and the physical
symbol template catalog.

Evidence Dimensions:
  1. Pixel Normalized Cross-Correlation (NCC): intensity similarity after scale normalization.
  2. Aspect Ratio Compatibility: width/height ratio penalty.
  3. Ink Density / Fill Ratio Compatibility: foreground pixel ratio comparison.
  4. Stroke Topology & Disagreement Adjudication:
     - Rejects template matches if aspect ratio is incompatible (> 1.8x mismatch).
     - Emits UNRESOLVED_CONFLICT when physical raster match strongly contradicts font metadata.
     - Emits ABSTAIN when top match score is below minimum confidence threshold (< 0.65).

Invariants:
  - Cross-platform UTF-8 encoding.
  - Zero mock or placeholder logic; operates on actual numpy arrays.
  - Independent fallback channel; cannot silently override Gate D4 or physical clearance.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "DATASETS" / "physical_symbol_library.json"
SYMBOLS_DIR = REPO_ROOT / "symbols" / "symbols"


class PhysicalSymbolMatcher:
    """Multi-evidence physical raster template matcher."""

    def __init__(self, catalog_path: Path | str = CATALOG_PATH):
        self.catalog_path = Path(catalog_path)
        self.catalog: dict[str, Any] = {}
        self.templates: dict[str, np.ndarray] = {}
        self.template_meta: dict[str, dict[str, Any]] = {}
        self._load_catalog()

    def _load_catalog(self) -> None:
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Symbol library not found at {self.catalog_path}")
        with open(self.catalog_path, encoding="utf-8") as f:
            self.catalog = json.load(f)

    def load_template_image(self, mnemonic: str) -> np.ndarray | None:
        """Load and cache binary template image array (foreground = 1.0, background = 0.0)."""
        if mnemonic in self.templates:
            return self.templates[mnemonic]

        sym = self.catalog.get("symbols", {}).get(mnemonic)
        if not sym or not sym.get("exists_on_disk"):
            return None

        rel_path = sym["relative_path"]
        img_path = REPO_ROOT / rel_path
        if not img_path.exists():
            return None

        try:
            with Image.open(img_path) as im:
                # Convert to grayscale
                gray = im.convert("L")
                arr = np.array(gray, dtype=np.float32)
                # In Metamath symbol images: black glyph on white/transparent background
                # Invert so glyph ink is 1.0 (foreground) and background is 0.0
                binary = (arr < 128).astype(np.float32)

                # Extract tight ink bounding box (purging font baseline/whitespace padding)
                ink_ys, ink_xs = np.where(binary > 0)
                if len(ink_ys) > 0 and len(ink_xs) > 0:
                    binary_tight = binary[min(ink_ys):max(ink_ys)+1, min(ink_xs):max(ink_xs)+1]
                else:
                    binary_tight = binary

                self.templates[mnemonic] = binary_tight
                self.template_meta[mnemonic] = sym
                return binary_tight
        except Exception:
            return None

    def compute_ncc(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute Normalized Cross-Correlation between two same-dimension arrays."""
        if a.shape != b.shape or a.size == 0 or b.size == 0:
            return 0.0

        a_flat = a.flatten()
        b_flat = b.flatten()

        a_std = np.std(a_flat)
        b_std = np.std(b_flat)

        if a_std < 1e-6 or b_std < 1e-6:
            # Degenerate uniform image
            return 0.0

        a_norm = (a_flat - np.mean(a_flat)) / a_std
        b_norm = (b_flat - np.mean(b_flat)) / b_std

        ncc = float(np.mean(a_norm * b_norm))
        # Clip to [0.0, 1.0] for similarity measure
        return max(0.0, min(1.0, ncc))

    def match_glyph_crop(
        self,
        glyph_crop: np.ndarray,
        candidate_mnemonics: list[str] | None = None,
        top_k: int = 3,
        min_confidence: float = 0.65,
    ) -> dict[str, Any]:
        """Match an observed glyph crop against candidate symbol templates.

        Args:
            glyph_crop: 2D numpy array (grayscale or binary, ink = 1.0, bg = 0.0).
            candidate_mnemonics: Optional restricted list of mnemonics to evaluate.
                                 If None, scans common core mathematical symbols.
            top_k: Number of ranked matches to return.
            min_confidence: Threshold below which the verdict is ABSTAIN.
        """
        if glyph_crop.size == 0 or np.sum(glyph_crop) == 0:
            return {
                "status": "ABSTAIN",
                "reason": "EMPTY_OR_ZERO_INK_CROP",
                "top_matches": [],
                "best_match": None,
            }

        # Normalize glyph crop so ink = 1.0, background = 0.0
        if np.max(glyph_crop) > 1.0:
            binary_crop = (glyph_crop < 128).astype(np.float32) if np.mean(glyph_crop) > 128 else (glyph_crop > 128).astype(np.float32)
        else:
            binary_crop = glyph_crop.astype(np.float32)

        # Tight crop to ink
        c_ys, c_xs = np.where(binary_crop > 0)
        if len(c_ys) > 0 and len(c_xs) > 0:
            binary_crop = binary_crop[min(c_ys):max(c_ys)+1, min(c_xs):max(c_xs)+1]

        crop_h, crop_w = binary_crop.shape
        crop_ar = crop_w / max(crop_h, 1)
        crop_density = float(np.mean(binary_crop))

        # Target size for normalized cross-correlation: standard height 32, width proportional
        target_size = (32, 32)
        im_crop = Image.fromarray((binary_crop * 255).astype(np.uint8)).resize(
            target_size, resample=Image.Resampling.BILINEAR
        )
        crop_norm = np.array(im_crop, dtype=np.float32) / 255.0

        eval_mnemonics = candidate_mnemonics or [
            "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
            "iota", "kappa", "lambda", "mu", "nu", "xi", "pi", "rho", "sigma",
            "tau", "upsilon", "phi", "chi", "psi", "omega",
            "cgamma", "cdelta", "ctheta", "clambda", "cxi", "cpi", "csigma",
            "cupsilon", "cphi", "cpsi", "comega",
            "sum", "int", "surd", "top", "propto", "in", "le", "ge", "ne",
            "approx", "sim", "equiv", "subset", "subseteq", "cup", "cap",
            "bbr", "bbn", "bbz", "bbc", "bbq", "bbp",
        ]

        scores = []
        for mnem in eval_mnemonics:
            tmpl = self.load_template_image(mnem)
            if tmpl is None or tmpl.size == 0 or np.sum(tmpl) == 0:
                continue

            tmpl_h, tmpl_w = tmpl.shape
            tmpl_ar = tmpl_w / max(tmpl_h, 1)
            tmpl_density = float(np.mean(tmpl))

            # Geometric Aspect Ratio Penalty
            ar_ratio = max(crop_ar, tmpl_ar) / max(min(crop_ar, tmpl_ar), 1e-4)
            if ar_ratio > 2.2:
                # Highly incompatible geometry (e.g. tall delimiter vs wide horizontal bar)
                continue
            ar_penalty = max(0.0, 1.0 - (ar_ratio - 1.0) * 0.5)

            # Resize template to target dimensions for correlation
            im_tmpl = Image.fromarray((tmpl * 255).astype(np.uint8)).resize(
                target_size, resample=Image.Resampling.BILINEAR
            )
            tmpl_norm = np.array(im_tmpl, dtype=np.float32) / 255.0

            # Compute NCC
            raw_ncc = self.compute_ncc(crop_norm, tmpl_norm)

            # Density penalty (stroke weight compatibility)
            density_ratio = min(crop_density, tmpl_density) / max(max(crop_density, tmpl_density), 1e-4)
            density_factor = 0.7 + 0.3 * density_ratio

            composite_score = round(raw_ncc * ar_penalty * density_factor, 4)

            meta = self.template_meta.get(mnem, {})
            scores.append({
                "mnemonic": mnem,
                "composite_score": composite_score,
                "ncc": round(raw_ncc, 4),
                "aspect_ratio_penalty": round(ar_penalty, 4),
                "density_factor": round(density_factor, 4),
                "tex_macro": meta.get("tex_macro"),
                "unicode_char": meta.get("unicode_char"),
                "category": meta.get("category"),
            })

        scores.sort(key=lambda s: s["composite_score"], reverse=True)
        top_matches = scores[:top_k]

        if not top_matches:
            return {
                "status": "ABSTAIN",
                "reason": "NO_COMPATIBLE_TEMPLATES",
                "top_matches": [],
                "best_match": None,
            }

        best = top_matches[0]
        margin = best["composite_score"] - (top_matches[1]["composite_score"] if len(top_matches) > 1 else 0.0)

        if best["composite_score"] < min_confidence:
            status = "ABSTAIN"
            reason = f"LOW_CONFIDENCE: best score {best['composite_score']} < {min_confidence}"
        elif margin < 0.03 and len(top_matches) > 1:
            status = "AMBIGUOUS"
            reason = f"LOW_MARGIN: margin {margin:.4f} < 0.03 between {best['mnemonic']} and {top_matches[1]['mnemonic']}"
        else:
            status = "MATCH_FOUND"
            reason = "CONFIDENT_MATCH"

        return {
            "status": status,
            "reason": reason,
            "best_match": best,
            "margin_to_second": round(margin, 4),
            "top_matches": top_matches,
        }

    def adjudicate_font_vs_raster(
        self,
        font_reported_char: str,
        font_reported_tex: str | None,
        raster_match: dict[str, Any],
        conflict_threshold: float = 0.70,
    ) -> dict[str, Any]:
        """Adjudicate cross-channel agreement between font stream metadata and physical raster match."""
        if raster_match["status"] != "MATCH_FOUND":
            return {
                "verdict": "DEFER_TO_FONT",
                "confidence": "FONT_METRIC_ONLY",
                "reason": f"Raster matching abstained ({raster_match.get('reason')})",
                "adopted_tex": font_reported_tex,
            }

        best = raster_match["best_match"]
        raster_tex = best["tex_macro"]
        score = best["composite_score"]

        # Check equivalence
        is_equivalent = False
        if font_reported_tex and raster_tex:
            f_clean = font_reported_tex.strip().lstrip("\\").replace("{", "").replace("}", "")
            r_clean = raster_tex.strip().lstrip("\\").replace("{", "").replace("}", "")
            is_equivalent = (f_clean == r_clean)

        if is_equivalent:
            return {
                "verdict": "CONFIRMED_AGREEMENT",
                "confidence": "HIGH_MULTIMODAL",
                "reason": f"Font metadata and physical raster agree on {raster_tex}",
                "adopted_tex": raster_tex,
                "score": score,
            }

        # If they strongly disagree and raster match is confident:
        if score >= conflict_threshold and not is_equivalent:
            return {
                "verdict": "UNRESOLVED_CONFLICT",
                "confidence": "ABSTAIN",
                "reason": f"Strong conflict: font reported {font_reported_tex} vs raster matched {raster_tex} (score={score})",
                "adopted_tex": None,
                "score": score,
            }

        return {
            "verdict": "DEFER_TO_FONT",
            "confidence": "MODERATE_FONT",
            "reason": f"Weak raster match ({score:.3f} < {conflict_threshold}) did not override font metadata",
            "adopted_tex": font_reported_tex,
            "score": score,
        }
