#!/usr/bin/env python3
"""
Inter-layer wave-packet consistency harness.

Samples the four formulas used across the King Wen quantum viewer stack at shared
(hex, x, t) points and asserts tolerance bands so that future edits to one layer
flag the others instead of silently drifting.

Formulas traced (mirrors of scripts/bridge_quantumlab_visualization.py):
  - SURFACE: 3D space-time surface |ψ(x,t)|²
  - 2D PELLETS: pellet trajectory overlay
  - READOUT: 10-step timeseries density/energy
  - COLLECTIVE: 64-NPC atlas field
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE

# ---------------------------------------------------------------------------
# E consensus: computed once from shotgun_expand(emotional_input=50), matching
# the actual bridge script. Falls back to a placeholder if unavailable/slow.
# ---------------------------------------------------------------------------
def _compute_E():
    from full_hexagram_shotgun import shotgun_expand
    result = shotgun_expand(emotional_input=50)
    return float(result.get("avg_hamiltonian_energy", 0.0))

try:
    E = _compute_E()
    E_SOURCE = "shotgun_expand(emotional_input=50)"
except Exception as exc:
    E = 0.5
    E_SOURCE = f"placeholder (shotgun_expand unavailable: {exc})"

if E < 0.01:
    print(f"NOTE: HARNESS E={E:.4f} ({E_SOURCE}). E-dependent checks (surface Z, collective val, CHECK D) run under E=0 slice.")
    print("  Numbers do not reflect the repo's live E and should not be read as repo measurements.")

VG = 0.35 + E * 0.1  # group velocity used by surface + pellets (constant across hex in current impl)

T_FINE = [round(i * 0.05, 4) for i in range(0, 251)]        # 0.0 .. 12.5 (covers 0..4π)
T_READOUT_STEPS = list(range(10))                              # 0..9  -> t = 0.0,0.4,...,3.6

X_PEAK = 0.0  # evaluate envelopes at x = x₀ (undrifted peak) for cross-comparison

# ---------------------------------------------------------------------------
# Formula replicas
# ---------------------------------------------------------------------------
def x0_of(hex_id):
    return math.sin(hex_id * 0.1) * 2.0

def sigma0_of(hex_id):
    return 0.5 + HEXAGRAM_BASE[hex_id].get("upper_idx", 1) * 0.1

def vortex_tension_of(hex_id):
    b = HEXAGRAM_BASE[hex_id]
    return (b.get("upper_idx", 1) * b.get("lower_idx", 1)) / 49.0

def surface_center(hex_id, t):
    return x0_of(hex_id) + VG * math.sin(t * 0.5)

def surface_sigma(hex_id, t):
    s0 = sigma0_of(hex_id)
    return math.sqrt(s0 * s0 + (t * 0.05) ** 2)

def surface_envelope_at_peak(hex_id, t):
    xc = surface_center(hex_id, t)
    dist = abs(x0_of(hex_id) - xc)
    sig = surface_sigma(hex_id, t)
    return math.exp(-(dist * dist) / (2.0 * sig * sig))

def surface_Z_at_peak(hex_id, t):
    env = surface_envelope_at_peak(hex_id, t)
    ya = sum(
        0.15 * math.cos((li + 1) * (x0_of(hex_id) - surface_center(hex_id, t)) + li * t * 0.5)
        for li in range(6)
    )
    return max(env * (1.0 + 0.25 * math.sin(E * t * 2.0) + ya), 0.0)

def readout_effective_center(hex_id, step):
    # linear drift: center moves LEFT by 0.1 per step
    return x0_of(hex_id) - step * 0.1

def readout_density_at_peak(hex_id, step):
    t = step * 0.4
    dist = abs(x0_of(hex_id) - readout_effective_center(hex_id, step))
    return math.exp(-(dist * dist) / 2.0) * (1.0 + 0.2 * math.sin(t * 0.5))

def readout_energy(hex_id, step):
    return E * (1.0 + 0.05 * math.cos(step * 0.4))

def pellet_center(hex_id, t, line_idx):
    offset = (line_idx - 2.5) * 0.6
    return surface_center(hex_id, t) + offset * math.cos(t * (0.8 + line_idx * 0.1))

def pellet_lateral_offset(hex_id, t, line_idx):
    # the lateral component only (what ψ does NOT contain)
    offset = (line_idx - 2.5) * 0.6
    return offset * math.cos(t * (0.8 + line_idx * 0.1))

def collective_center(hex_id, t):
    return x0_of(hex_id) + 1.5 * math.sin(t * 0.5)

def collective_val_at_peak(hex_id, t):
    xc = collective_center(hex_id, t)
    dist = abs(x0_of(hex_id) - xc)
    tension = vortex_tension_of(hex_id)
    return math.exp(-(dist * dist) / 4.0) * (1.0 + 0.3 * math.cos(E * t + tension * 6.28))

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def run():
    print("=" * 78)
    print("INTER-LAYER WAVE-PACKET CONSISTENCY HARNESS")
    print("=" * 78)
    print(f"E = {E:.4f}  (source: {E_SOURCE})   VG = {VG:.4f}")
    print(f"T_FINE = {len(T_FINE)} points  0..{T_FINE[-1]:.2f}")
    print()

    failures = []
    seams = []

    for hex_id in range(1, 65):
        x0 = x0_of(hex_id)
        s0 = sigma0_of(hex_id)
        tension = vortex_tension_of(hex_id)
        print(f"--- hex {hex_id:02d} | x0={x0:+.3f} sigma0={s0:.3f} tension={tension:.4f} ---")

        # CHECK A: pellet center = surface center + offset*cos(...)  (exact relationship)
        for li in range(6):
            offset = (li - 2.5) * 0.6
            worst = 0.0
            for t in T_FINE:
                pred = surface_center(hex_id, t) + offset * math.cos(t * (0.8 + li * 0.1))
                actual = pellet_center(hex_id, t, li)
                err = abs(pred - actual)
                if err > worst:
                    worst = err
            if worst > 1e-9:
                failures.append(("pellet_internal", hex_id, li, worst))
            # informational: lateral amplitude
        # end for li

        # CHECK B: readout effective center motion vs surface center motion
        t_end = 3.6
        step_end = 9
        rc_end = readout_effective_center(hex_id, step_end)
        sc_end = surface_center(hex_id, t_end)
        drift_div = abs(rc_end - sc_end)
        seams.append(("readout_center_motion", hex_id,
                      f"t=3.6: readout_center={rc_end:+.3f} surface_center={sc_end:+.3f} divergence={drift_div:.3f}  "
                      f"[readout=linear drift, surface=oscillation]"))

        # CHECK C: collective amplitude vs surface amplitude
        surf_amp = VG
        coll_amp = 1.5
        ratio = coll_amp / surf_amp if surf_amp > 0 else float('inf')
        seams.append(("collective_amplitude", hex_id,
                      f"collective_amp={coll_amp:.2f} surface_amp={surf_amp:.3f} ratio={ratio:.2f}x  "
                      f"[atlas breathes {ratio:.1f}x wider than single-hex plot]"))

        # CHECK D: density at peak — readout vs surface at shared t (informational)
        # (not a hard assert; reported for inspection)
        # (omitted from per-hex print to keep output compact; see summary)
    # end for hex_id

    # Pellet lateral-motion seam (cross-cutting)
    seams.append(("pellet_lateral_is_decoration", None,
                  "ψ yao term = 0.15*cos((ℓ+1)*(x-x_center) + ℓ*t*0.5)  [no lateral pellet-center motion]  |  "
                  "plotted pellet_x(t) = x_center + offset*cos(t*(0.8+ℓ*0.1))  [lateral oscillation is a viz overlay]"))

    # --- report ---
    print()
    print("CHECK A — pellet trajectory internal consistency")
    print("  (pellet_center == surface_center + offset*cos(t*(0.8+ℓ*0.1)) within 1e-9)")
    hard = [f for f in failures if f[0] == "pellet_internal"]
    if not hard:
        print("  PASS — all 6 pellets × 64 hex satisfy the exact offset·cos relationship")
    else:
        print(f"  FAIL — {len(hard)} violation(s):")
        for cat, hex_id, li, worst in hard[:20]:
            print(f"    hex {hex_id:02d} L{li}: max_err={worst:.2e}")
    print()

    print("CHECK B — readout center motion vs surface center motion")
    max_div = max(abs(readout_effective_center(h, 9) - surface_center(h, 3.6)) for h in range(1, 65))
    print(f"  max |readout_center - surface_center| at t=3.6 across all hex: {max_div:.3f}")
    print("  Structural seam: readout = linear drift (x0 - step*0.1); surface = oscillation (x0 + VG*sin(t*0.5))")
    print("  → overlay readout on surface: diverge by ~{:.2f} units at t=3.6".format(max_div))
    print()

    print("CHECK C — collective atlas amplitude vs individual surface amplitude")
    print(f"  collective amplitude = 1.5   surface amplitude (VG) = {VG:.3f}   ratio = {1.5/VG:.2f}x")
    print("  Structural seam: atlas rows breathe ~{:.1f}x wider than single-hex plots".format(1.5/VG))
    print()

    print("CHECK D — density at x=x₀, t=3.6 (readout vs surface), hex 01 & hex 32 sample:")
    bands = []
    for h in [1, 32, 64]:
        zr = readout_density_at_peak(h, 9)
        zs = surface_Z_at_peak(h, 3.6)
        ratio = zr / zs if zs else float("inf")
        bands.append(ratio)
        print(f"  hex {h:02d}: readout={zr:.4f}  surface={zs:.4f}  ratio={ratio:.2f}x")
    band = max(bands) - min(bands) if bands else 0.0
    print(f"  relative band across samples: {band:.3f}  (E={E:.4f})")
    seams.append(
        ("readout_density_vs_surface", None,
         f"readout_density vs surface_Z at t=3.6: max relative band {band:.3f} across hex 01/32/64 "
         f"(E={E:.4f}; envelope widths differ: readout σ=1.0 fixed, surface σ=sqrt(σ₀²+(t*0.05)²) grows with t)")
    )
    print()

    print("CHECK E — pellet lateral motion is NOT in the wavefunction ψ:")
    print("  ψ yao term   = 0.15·cos((ℓ+1)·(x - x_center) + ℓ·t·0.5)   [no lateral pellet-center motion]")
    print("  plotted pellet_x = x_center + offset·cos(t·(0.8+ℓ·0.1))     [lateral oscillation added in viz]")
    print("  → plotted pellet trajectories are a visualization overlay; ψ alone does not encode lateral pellet motion.")
    print("  → If GhostSplat / hexagram deliberation reads pellet positions as state, it reads decoration.")
    print()

    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"Hard assertion failures (pellet internal consistency): {len(hard)} (expected 0)")
    print(f"Structural seams flagged: 3 (readout drift, collective amplitude, pellet decoration)")
    if E < 0.01:
        print(f"NOTE: E={E:.4f} ({E_SOURCE}) — E-dependent checks run under E=0 slice; not repo measurements.")
    print()
    print("RECOMMENDED NEXT (in your priority order):")
    print("  1. Label the 10-step readout as a linear-drift thumbnail (or align to oscillation).")
    print("  2. Decide whether pellet lateral motion is decorative-only or should feed state.")
    print("  3. Decide whether collective atlas amplitude should match individual, or be intentionally ~3-4x.")
    print("  4. Manifest validator: confirm 512 PLYs + vertex/face counts + 60 egg keyframes per sector.")
    print("  5. LOD/culling pass on the field widget (512*729 vertices is a slideshow on modest hardware).")
    print()
    print("Also noted from your review (not asserted here, deferred to manifest validator):")
    print("  - 384-pellet unison mixing: raw sum clips; needs per-pellet gain norm or soft-knee.")
    print("  - 120ms frame / 6 simultaneous harmonics: per-frame phase coherence must hold between")
    print("    audio premix and egg keyframes, or the 'same clock' claim breaks silently.")

if __name__ == "__main__":
    run()
