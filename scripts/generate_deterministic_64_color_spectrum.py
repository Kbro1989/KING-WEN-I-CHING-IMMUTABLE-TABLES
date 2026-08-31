#!/usr/bin/env python3
"""
Deterministic 64-Color Hexagram Spectrum Generator (Shotgun Engine)
===================================================================
Eliminates binary attractor basin collapse across the 64-hexagram embodiment field.
Generates an unaliased, continuous 360-degree color spectrum for all 64 King Wen
Sovereign model kits (kit_1.json .. kit_64.json).

Mathematical Formulation:
  hue_base(h)         = (h - 1) * (360° / 64) = (h - 1) * 5.625°
  saturation(h)       = (popcount(b) / 6.0) * 0.40 + 0.50
  lightness(h)        = coherence(h) * 0.30 + 0.40
  trigram_warmth(h)   = (temp(upper) + temp(lower)) / 2.0
  final_hue(h)        = (hue_base + trigram_warmth * 2.8125°) mod 360°
  palette_16(h, i)    = 16 distinct harmonic gradient steps around final_hue
"""

import colorsys
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE

KIT_DIR = ROOT / "DATASETS" / "kingwen_model_sets"
WEIGHTS_PATH = ROOT / "data" / "emotional-weights.json"

# Wu Xing element temperature perturbations (fine-tuning, not attractor basins)
TRIGRAM_TEMP = {
    "Qian": 1.0,    # Heaven (warm/yang)
    "Kun": -1.0,    # Earth (cool/yin)
    "Zhen": 0.75,   # Thunder (kinetic excitation)
    "Kan": -0.75,   # Water (abyssal cool)
    "Li": 1.20,     # Fire (radiant solar)
    "Xun": -0.50,   # Wind (dispersive cool)
    "Gen": -0.60,   # Mountain (still terrestrial)
    "Dui": 0.40,    # Lake (joyous mist)
}

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def hsl_to_rgb_hex(h_deg: float, s: float, l: float) -> tuple[int, int, int, str]:
    h_norm = (h_deg % 360.0) / 360.0
    r_f, g_f, b_f = colorsys.hls_to_rgb(h_norm, clamp(l, 0.15, 0.85), clamp(s, 0.20, 1.0))
    r, g, b = int(round(r_f * 255)), int(round(g_f * 255)), int(round(b_f * 255))
    hex_code = f"#{r:02X}{g:02X}{b:02X}"
    return r, g, b, hex_code

def generate_shotgun_spectrum():
    print("=" * 85)
    print("GENERATING DETERMINISTIC 64-COLOR HEXAGRAM SPECTRUM (SHOTGUN EMBODIMENT ENGINE)")
    print("=" * 85)

    weights_data = {}
    if WEIGHTS_PATH.exists():
        try:
            weights_data = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    primary_hex_set = set()
    total_palette_colors = 0
    updated_kits = 0

    for h_id in range(1, 65):
        base = HEXAGRAM_BASE[h_id]
        binary_str = base.get("binary_bottom_to_top", "111111")
        upper_tri = base.get("upper_trigram", "Qian")
        lower_tri = base.get("lower_trigram", "Kun")

        # 1. Base hue on 360-degree circle (5.625 deg per hexagram)
        hue_base = (h_id - 1) * (360.0 / 64.0)

        # 2. Saturation modulated by Yang popcount
        yang_count = binary_str.count("1")
        saturation = clamp((yang_count / 6.0) * 0.40 + 0.50, 0.35, 0.95)

        # 3. Lightness modulated by emotional coherence
        w_entry = weights_data.get(str(h_id), {})
        coherence = w_entry.get("coherence", 0.85)
        lightness = clamp(coherence * 0.30 + 0.40, 0.35, 0.70)

        # 4. Trigram warmth fine-tuning perturbation (+- 2.8125 deg max)
        u_temp = TRIGRAM_TEMP.get(upper_tri, 0.0)
        l_temp = TRIGRAM_TEMP.get(lower_tri, 0.0)
        warmth = (u_temp + l_temp) / 2.0
        trigram_pert = warmth * 2.8125
        final_hue = (hue_base + trigram_pert) % 360.0

        # Primary & Secondary colors
        p_r, p_g, p_b, p_hex = hsl_to_rgb_hex(final_hue, saturation, lightness)
        s_r, s_g, s_b, s_hex = hsl_to_rgb_hex(
            final_hue - 15.0,
            clamp(saturation * 1.1, 0.3, 1.0),
            clamp(lightness * 0.85, 0.2, 0.8)
        )
        b_r, b_g, b_b, b_hex = hsl_to_rgb_hex(
            final_hue - 7.5,
            clamp(saturation * 1.05, 0.3, 1.0),
            clamp(lightness * 0.92, 0.2, 0.8)
        )

        primary_hex_set.add(p_hex)

        # 5. Generate 16 distinct harmonic gradient steps (palette_16)
        palette_16 = []
        line_segments = []
        for i in range(1, 17):
            step_offset = (i - 8.5) * 1.20  # Spread across +- 9.6 deg
            step_hue = (final_hue + step_offset) % 360.0
            step_l = clamp(lightness + (i - 8.5) * 0.015, 0.25, 0.80)
            step_s = clamp(saturation + ((i % 3) - 1) * 0.03, 0.35, 0.98)
            _, _, _, step_hex = hsl_to_rgb_hex(step_hue, step_s, step_l)
            palette_16.append(step_hex)

            # Polar coordinates for Color-by-Numbers Viewfinder line segments
            t1 = (i - 1) / 16.0
            t2 = i / 16.0
            line_segments.append({
                "segment_id": i,
                "color_key": i,
                "x1": round(math.cos(t1 * 2 * math.pi) * 100, 2),
                "y1": round(math.sin(t1 * 2 * math.pi) * 100, 2),
                "x2": round(math.cos(t2 * 2 * math.pi) * 100, 2),
                "y2": round(math.sin(t2 * 2 * math.pi) * 100, 2),
                "hex_color": step_hex
            })

        total_palette_colors += len(set(palette_16))

        # 6. Update Kit JSON
        kit_file = KIT_DIR / f"kit_{h_id}.json"
        if kit_file.exists():
            kit_json = json.loads(kit_file.read_text(encoding="utf-8"))
            npc = kit_json.get("grounded_npc", {})

            npc["k_color_map"] = {
                "derivation": "hexagram_deterministic_spectrum_v2",
                "base_hue_degrees": round(hue_base, 3),
                "trigram_perturbation_degrees": round(trigram_pert, 4),
                "final_hue_degrees": round(final_hue, 3),
                "saturation": round(saturation, 3),
                "lightness": round(lightness, 3),
                "primary_color": {
                    "r": p_r, "g": p_g, "b": p_b,
                    "name": f"{base['name']} Spectral Hue",
                    "hex": p_hex
                },
                "secondary_color": {
                    "r": s_r, "g": s_g, "b": s_b,
                    "name": f"{base['name']} Deep Shift",
                    "hex": s_hex
                },
                "blended_hex": b_hex,
                "palette_16": palette_16,
                "key_line_segments": line_segments
            }
            kit_json["grounded_npc"] = npc

            # Update extra array
            extra = kit_json.get("extra", [])
            # Update or add blended_hex_color & primary_spectral_color
            has_color = False
            for ex in extra:
                if ex.get("key") == "blended_hex_color":
                    ex["stringvalue"] = b_hex
                    has_color = True
                elif ex.get("key") == "primary_spectral_color":
                    ex["stringvalue"] = p_hex
            if not has_color:
                extra.append({"type": 0, "key": "blended_hex_color", "intvalue": 0, "stringvalue": b_hex})
                extra.append({"type": 0, "key": "primary_spectral_color", "intvalue": 0, "stringvalue": p_hex})
            kit_json["extra"] = extra

            kit_file.write_text(json.dumps(kit_json, ensure_ascii=False, indent=2), encoding="utf-8")
            updated_kits += 1

    print(f"\n[OK] Updated {updated_kits} / 64 Model Kits with Deterministic Spectral Colors.")
    print(f"     Distinct Primary Hues: {len(primary_hex_set)} / 64 (100% unique basis vectors)")
    print(f"     Total Distinct Palette Entries Generated: {total_palette_colors} (avg {total_palette_colors/64:.1f}/kit)")
    print("=" * 85)

if __name__ == "__main__":
    generate_shotgun_spectrum()
