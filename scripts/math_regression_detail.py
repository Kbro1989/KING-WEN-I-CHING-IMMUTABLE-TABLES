#!/usr/bin/env python3
"""Print FULL recovered strings for the regressed equations — no truncation."""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

CASES = [
    r"\widetilde{\pi}^{(k)}\coloneqq\frac{\bar{\pi}^{(k)}}{\sum_{\ell=1}^{G}\bar{\pi}^{(\ell)}}.",
    r"F_{\text{lesion}}=\frac{\sum_{i,j}X_{\text{fused}}(i,j)\cdot M_{\text{lesion}}(i,j)}{\sum_{i,j}M_{\text{lesion}}(i,j)}",
    r"w_{j}^{\text{sal}}=\frac{\exp(s_{j}/\tau_{\text{sal}})}{\sum_{k=1}^{K}\exp(s_{k}/\tau_{\text{sal}})}",
    r"\mathcal{L}_{\text{list}}=-w\sum_{i\in\mathcal{P}}\log\frac{\exp(z_{i})}{\sum_{j=1}^{k}\exp(z_{j})}",
]

print("=" * 78)
print("FULL RECOVERED STRINGS (no truncation)")
print("=" * 78)
print()
for L in CASES:
    out, notes = recover_latex(L)
    print(f"LATEX  : {L}")
    print(f"RECOVER: {out}")
    print(f"  parens: open={out.count('(')} close={out.count(')')}"
          f"  balanced={out.count('(') == out.count(')')}")
    print(f"  notes : {notes}")
    print()

print("=" * 78)
print("ISOLATE — just the sum-limit construct")
print("=" * 78)
print()
for L in [r"\sum_{\ell=1}^{G}\bar{\pi}^{(\ell)}",
          r"\sum_{i,j}M(i,j)",
          r"\frac{a}{\sum_{k=1}^{K}b}",
          r"\sum_{k=1}^{K}\exp(s_{k}/\tau)"]:
    out, notes = recover_latex(L)
    print(f"  {L:44s} -> {out!r}")
