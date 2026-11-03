#!/usr/bin/env python3
"""Controlled numerical-equivalence test: King Wen vs Quantum-Sim split-step Fourier.

This test isolates the numerical method from application-specific differences.
Both implementations are given IDENTICAL inputs:
  - Grid: N=64, x in [-pi, pi), periodic
  - Potential: identical array (coprime-frequency sum from King Wen)
  - Initial wavefunction: identical Gaussian with momentum kick
  - Parameters: HBAR=1.0, MASS=1.0, DT=0.02, WARMUP_STEPS=3
  - Operators: U_V, U_T computed identically

No post-processing is applied. Outputs are raw complex arrays.
"""

import numpy as np
from scipy.fft import fft, ifft
import json
from pathlib import Path
import sys

# ============================================================
# King Wen implementation (inline, from prewarm_quantum_wavepackets.py)
# ============================================================
def kw_split_step(N, x, k, V, T_k, U_V, U_T, psi_init, steps):
    """King Wen's inline split-step Fourier."""
    psi = psi_init.copy()
    for _ in range(steps):
        psi = ifft(fft(psi * U_V) * U_T) * U_V
    return psi


# ============================================================
# Quantum-Sim implementation (class-based, from split_step_1d.py)
# ============================================================
class QSSplitStep1DSolver:
    """Quantum-Sim's class-based split-step solver."""
    def __init__(self, grid_x, potential, dt, hbar, m):
        self.x = grid_x
        self.V = potential
        self.dt = dt
        self.hbar = hbar
        self.m = m
        self.k = 2 * np.pi * np.fft.fftfreq(len(grid_x), (grid_x[1] - grid_x[0]))
        self.T_k = hbar**2 * self.k**2 / (2.0 * m)
        self.U_V = np.exp(-1j * self.V * self.dt / (2.0 * self.hbar))
        self.U_T = np.exp(-1j * self.T_k * self.dt / self.hbar)

    def step(self, psi):
        psi = psi.copy()
        psi *= self.U_V
        psi_k = fft(psi)
        psi_k *= self.U_T
        psi = ifft(psi_k)
        psi *= self.U_V
        return psi

    def evolve(self, psi_init, steps):
        psi = psi_init.copy()
        for _ in range(steps):
            psi = self.step(psi)
        return psi


# ============================================================
# Shared inputs (identical for both)
# ============================================================
HBAR = 1.0
MASS = 1.0
DT = 0.02
STEPS = 3
N = 64
PI = np.pi

x = np.linspace(-PI, PI, N, endpoint=False)
dx = (2 * PI) / N
k = 2 * np.pi * np.fft.fftfreq(N, dx)

# King Wen's coprime-frequency potential (identical for both)
def kw_pot_1d(x):
    V = np.zeros_like(x, dtype=float)
    for p in [97, 89, 83, 79, 73]:
        V += np.sin(p * x / np.pi) / p
    return V

V = kw_pot_1d(x)
T_k = HBAR**2 * k**2 / (2.0 * MASS)
U_V = np.exp(-1j * V * DT / (2.0 * HBAR))
U_T = np.exp(-1j * T_k * DT / HBAR)

# Initial wavefunction (identical for both)
psi_init = np.exp(-(x**2) / (4.0 * 0.5**2)) * np.exp(1j * 1.0 * x)
psi_init /= np.sqrt(np.sum(np.abs(psi_init)**2) * dx)

# ============================================================
# Run both implementations
# ============================================================
# King Wen
psi_kw = kw_split_step(N, x, k, V, T_k, U_V, U_T, psi_init, STEPS)

# Quantum-Sim
solver = QSSplitStep1DSolver(x, V, DT, HBAR, MASS)
psi_qs = solver.evolve(psi_init, STEPS)

# ============================================================
# Per-step comparison (not just final)
# ============================================================
# King Wen per-step
psi_kw_steps = [psi_init.copy()]
psi = psi_init.copy()
for _ in range(STEPS):
    psi = ifft(fft(psi * U_V) * U_T) * U_V
    psi_kw_steps.append(psi.copy())

# Quantum-Sim per-step
psi_qs_steps = [psi_init.copy()]
psi = psi_init.copy()
for _ in range(STEPS):
    psi = solver.step(psi)
    psi_qs_steps.append(psi.copy())

# ============================================================
# Metrics
# ============================================================
def compute_metrics(psi_kw, psi_qs, psi_init, dx):
    # Maximum absolute complex-field error
    max_abs_err = np.max(np.abs(psi_kw - psi_qs))
    
    # Relative L2 error
    norm_qs = np.sqrt(np.sum(np.abs(psi_qs)**2) * dx)
    rel_l2_err = np.sqrt(np.sum(np.abs(psi_kw - psi_qs)**2) * dx) / norm_qs
    
    # Norm before and after
    norm_init = np.sqrt(np.sum(np.abs(psi_init)**2) * dx)
    norm_kw = np.sqrt(np.sum(np.abs(psi_kw)**2) * dx)
    norm_qs = np.sqrt(np.sum(np.abs(psi_qs)**2) * dx)
    
    # Norm preservation
    delta_N_kw = abs(norm_kw**2 - norm_init**2)
    delta_N_qs = abs(norm_qs**2 - norm_init**2)
    
    # Probability density difference
    prob_kw = np.abs(psi_kw)**2
    prob_qs = np.abs(psi_qs)**2
    max_prob_diff = np.max(np.abs(prob_kw - prob_qs))
    rel_prob_diff = np.sqrt(np.sum((prob_kw - prob_qs)**2) * dx) / np.sqrt(np.sum(prob_qs**2) * dx)
    
    # Phase difference (with wrapping)
    phase_kw = np.angle(psi_kw)
    phase_qs = np.angle(psi_qs)
    phase_diff = np.angle(np.exp(1j * (phase_kw - phase_qs)))
    max_phase_diff = np.max(np.abs(phase_diff))
    mean_phase_diff = np.mean(np.abs(phase_diff))
    
    return {
        "max_abs_complex_err": float(max_abs_err),
        "rel_l2_err": float(rel_l2_err),
        "norm_init": float(norm_init),
        "norm_kw_final": float(norm_kw),
        "norm_qs_final": float(norm_qs),
        "delta_N_kw": float(delta_N_kw),
        "delta_N_qs": float(delta_N_qs),
        "max_prob_density_diff": float(max_prob_diff),
        "rel_prob_density_diff": float(rel_prob_diff),
        "max_phase_diff_rad": float(max_phase_diff),
        "mean_phase_diff_rad": float(mean_phase_diff),
    }

# Per-step metrics
per_step = []
for i in range(STEPS + 1):
    m = compute_metrics(psi_kw_steps[i], psi_qs_steps[i], psi_init, dx)
    per_step.append({"step": i, **m})

# Final metrics
final_metrics = per_step[-1]

# ============================================================
# Report
# ============================================================
print("=" * 70)
print("CONTROLLED NUMERICAL-EQUIVALENCE TEST")
print("King Wen (inline) vs Quantum-Sim (class-based) split-step Fourier")
print("=" * 70)
print()
print("Inputs: N=64, x in [-pi, pi), DT=0.02, HBAR=1.0, MASS=1.0, STEPS=3")
print("Potential: coprime-frequency sum (identical for both)")
print("Initial wavefunction: Gaussian with momentum kick (identical for both)")
print()

for ps in per_step:
    print(f"Step {ps['step']}:")
    print(f"  max_abs_complex_err = {ps['max_abs_complex_err']:.2e}")
    print(f"  rel_l2_err          = {ps['rel_l2_err']:.2e}")
    print(f"  norm_kw             = {ps['norm_kw_final']:.10f}")
    print(f"  norm_qs             = {ps['norm_qs_final']:.10f}")
    print(f"  delta_N_kw          = {ps['delta_N_kw']:.2e}")
    print(f"  delta_N_qs          = {ps['delta_N_qs']:.2e}")
    print(f"  max_prob_diff       = {ps['max_prob_density_diff']:.2e}")
    print(f"  max_phase_diff      = {ps['max_phase_diff_rad']:.2e}")
    print()

print("FINAL VERDICT:")
print(f"  max_abs_complex_err = {final_metrics['max_abs_complex_err']:.2e}")
print(f"  rel_l2_err          = {final_metrics['rel_l2_err']:.2e}")
print(f"  norm_kw             = {final_metrics['norm_kw_final']:.10f}")
print(f"  norm_qs             = {final_metrics['norm_qs_final']:.10f}")
print(f"  delta_N_kw          = {final_metrics['delta_N_kw']:.2e}")
print(f"  delta_N_qs          = {final_metrics['delta_N_qs']:.2e}")
print()

if final_metrics['max_abs_complex_err'] < 1e-14:
    print("  RESULT: NUMERICALLY IDENTICAL (machine precision)")
elif final_metrics['max_abs_complex_err'] < 1e-10:
    print("  RESULT: NUMERICALLY EQUIVALENT (within floating-point tolerance)")
else:
    print("  RESULT: NUMERICALLY DIFFERENT (error exceeds tolerance)")

# Save results
results = {
    "test_name": "controlled_numerical_equivalence",
    "test_date": "2026-11-02",
    "inputs": {
        "N": N, "dx": float(dx), "DT": DT, "HBAR": HBAR, "MASS": MASS,
        "STEPS": STEPS, "potential": "coprime-frequency sum",
        "initial_wavefunction": "Gaussian with momentum kick",
    },
    "per_step": per_step,
    "final_metrics": final_metrics,
    "baseline_reference": "qsmc1-cross-group-correspondence-synthesis.md",
    "original_m7_disposition": "undetermined",
    "disposition_change": "none — this test is supplementary evidence",
}

out_path = Path("DATASETS/qsmc1_m7_numerical_equivalence_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
