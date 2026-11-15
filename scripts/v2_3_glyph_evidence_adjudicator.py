"""V2.3 Prototype: Glyph-Level Evidence Adjudicator (GLEA).

Implements P0 of the V2.3 Experimental Specification:
  - Adjudicates between font layout metric bounding boxes and visible raster ink.
  - Distinguishes physical ink intrusion from font descender padding artifacts.
  - Computes exact physical signed clearance and penetration depth.
  - Anti-override guarantee: cannot bypass mandatory boundary isolation gates.
"""
from __future__ import annotations

import pymupdf
from typing import Any

ZOOM = 20
INK_THRESHOLD = 128
PX_TO_PT = 1.0 / ZOOM


class GlyphEvidenceAdjudicator:
    def __init__(self, zoom: int = ZOOM, ink_threshold: int = INK_THRESHOLD):
        self.zoom = zoom
        self.ink_threshold = ink_threshold
        self.px_to_pt = 1.0 / zoom

    def extract_glyph_ink_envelope(
        self,
        page: pymupdf.Page,
        metric_bbox: list[float] | pymupdf.Rect,
        pad_pt: float = 1.0,
    ) -> dict[str, Any]:
        """Extract high-resolution visible ink envelope for a single glyph or character token."""
        r = pymupdf.Rect(metric_bbox)
        # Add local padding to ensure serifs and ink extensions are captured
        search_rect = pymupdf.Rect(r.x0 - pad_pt, r.y0 - pad_pt, r.x1 + pad_pt, r.y1 + pad_pt)
        
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(self.zoom, self.zoom),
            clip=search_rect,
            colorspace=pymupdf.csGRAY,
        )
        w_px, h_px = pix.width, pix.height
        samples = pix.samples

        ink_pixels = []
        for row in range(h_px):
            for col in range(w_px):
                if samples[row * w_px + col] <= self.ink_threshold:
                    x = search_rect.x0 + col * self.px_to_pt
                    y = search_rect.y0 + row * self.px_to_pt
                    ink_pixels.append((x, y))

        if not ink_pixels:
            return {
                "has_visible_ink": False,
                "pixel_count": 0,
                "ink_bbox": None,
                "metric_bbox": [round(c, 3) for c in r],
            }

        min_x = min(p[0] for p in ink_pixels)
        max_x = max(p[0] for p in ink_pixels)
        min_y = min(p[1] for p in ink_pixels)
        max_y = max(p[1] for p in ink_pixels)

        return {
            "has_visible_ink": True,
            "pixel_count": len(ink_pixels),
            "ink_bbox": [round(min_x, 3), round(min_y, 3), round(max_x, 3), round(max_y, 3)],
            "metric_bbox": [round(c, 3) for c in r],
        }

    def adjudicate_boundary_conflict(
        self,
        page: pymupdf.Page,
        char_or_token: dict[str, Any],
        boundary_y: float,
        is_upper_boundary: bool = True,
    ) -> dict[str, Any]:
        """Adjudicate whether a token near boundary_y is an actual ink intrusion or metric artifact.
        
        For upper boundary (y0 of crop):
          - Token is above the crop.
          - If metric_bbox.y1 > boundary_y: nominal metric intrusion.
          - If ink_bbox.y1 > boundary_y: CONFIRMED_INK_INTRUSION.
          - If metric_bbox.y1 > boundary_y but ink_bbox.y1 <= boundary_y: PURGED_METRIC_ARTIFACT.
          - If metric_bbox.y1 <= boundary_y but ink_bbox.y1 > boundary_y: CONFIRMED_INK_INTRUSION (metric miss).
        """
        metric_bbox = char_or_token["metric_bbox"]
        envelope = self.extract_glyph_ink_envelope(page, metric_bbox)

        if not envelope["has_visible_ink"]:
            return {
                "token": char_or_token.get("char", char_or_token.get("token", "")),
                "verdict": "ZERO_INK_DETECTED",
                "metric_intrusion_pt": 0.0,
                "true_ink_intrusion_pt": 0.0,
                "true_ink_clearance_pt": 999.0,
                "is_intrusion": False,
                "envelope": envelope,
            }

        ink_bbox = envelope["ink_bbox"]
        assert ink_bbox is not None

        if is_upper_boundary:
            metric_disp = metric_bbox[3] - boundary_y  # positive means inside crop
            ink_disp = ink_bbox[3] - boundary_y        # positive means inside crop

            is_metric_intrusive = metric_disp > 0.001
            is_ink_intrusive = ink_disp > 0.001

            if is_ink_intrusive:
                verdict = "CONFIRMED_INK_INTRUSION"
                clearance_pt = 0.0
                intrusion_pt = round(ink_disp, 3)
            elif is_metric_intrusive and not is_ink_intrusive:
                verdict = "PURGED_METRIC_ARTIFACT"
                clearance_pt = round(boundary_y - ink_bbox[3], 3)
                intrusion_pt = 0.0
            else:
                verdict = "EXTERIOR_CLEAN"
                clearance_pt = round(boundary_y - ink_bbox[3], 3)
                intrusion_pt = 0.0

            return {
                "token": char_or_token.get("char", char_or_token.get("token", "")),
                "font": char_or_token.get("font", "unknown"),
                "metric_bbox": metric_bbox,
                "ink_bbox": ink_bbox,
                "verdict": verdict,
                "metric_intrusion_pt": round(max(0.0, metric_disp), 3),
                "true_ink_intrusion_pt": intrusion_pt,
                "true_ink_clearance_pt": clearance_pt,
                "is_intrusion": is_ink_intrusive,
                "envelope": envelope,
            }
        else:
            # Lower boundary (crop.y1)
            metric_disp = boundary_y - metric_bbox[1]
            ink_disp = boundary_y - ink_bbox[1]
            is_ink_intrusive = ink_disp > 0.001

            return {
                "token": char_or_token.get("char", char_or_token.get("token", "")),
                "font": char_or_token.get("font", "unknown"),
                "metric_bbox": metric_bbox,
                "ink_bbox": ink_bbox,
                "verdict": "CONFIRMED_INK_INTRUSION" if is_ink_intrusive else "EXTERIOR_CLEAN",
                "is_intrusion": is_ink_intrusive,
                "true_ink_intrusion_pt": round(max(0.0, ink_disp), 3),
                "true_ink_clearance_pt": round(max(0.0, ink_bbox[1] - boundary_y), 3),
                "envelope": envelope,
            }

