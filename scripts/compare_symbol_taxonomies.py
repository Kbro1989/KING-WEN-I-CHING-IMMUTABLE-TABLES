#!/usr/bin/env python3
"""Compare Metamath HTML symbol chart vs WDR-RLHF paper MathML."""

import re
import json
import os

# === 1. Extract Metamath symbols ===
with open(
    'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/'
    'DATASETS/GIF-and-PNG-Images-for-Math-Symbols.html',
    'r', encoding='windows-1252') as f:
    meta_content = f.read()

meta_pattern = r'<area shape="RECT" coords="([^"]+)" alt="([^"]+)" title="([^"]+)" href="([^"]+)">'
meta_areas = re.findall(meta_pattern, meta_content)

meta_symbols = set()
for coords, alt, title, href in meta_areas:
    meta_symbols.add(alt)

# === 2. Extract WDR-RLHF latex symbols ===
with open(
    'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/'
    'DATASETS/Wasserstein Distributionally Robust Regret Optimization for Reinforcement Learning from Human Feedback.html',
    'r', encoding='utf-8') as f:
    wdr_content = f.read()

wdr_pattern = r'<annotation encoding="application/x-tex">([^<]+)</annotation>'
wdr_latex = re.findall(wdr_pattern, wdr_content)
wdr_unique = set(wdr_latex)

# Normalize LaTeX to base symbol name
def normalize_latex_symbol(latex):
    s = latex.strip()
    # Simple pattern matching for common commands
    if s.startswith('\\delta'):
        return 'delta'
    if s.startswith('\\ell'):
        return 'ell'
    if s.startswith('\\mathcal'):
        return 'mathcal'
    if s.startswith('\\pi'):
        return 'pi'
    if s.startswith('\\bar'):
        return 'bar'
    if s.startswith('\\hat'):
        return 'hat'
    if s.startswith('\\star'):
        return 'star'
    if s.startswith('\\mathbb'):
        return 'mathbb'
    if s.startswith('\\Pi'):
        return 'Pi'
    if s.startswith('\\coloneqq'):
        return 'coloneq'
    if s.startswith('\\mathbb{E}'):
        return 'E'
    if s.startswith('\\mathbb{P}'):
        return 'P'
    # Check for \mathcal{X} \mathcal{D} \mathcal{Y}
    if '\\mathcal' in s:
        return 'mathcal'
    # Check for \ell_{p} \ell_{1} etc
    if '\\ell' in s:
        return 'ell'
    if '\\pi' in s:
        return 'pi'
    if '\\bar' in s:
        return 'bar'
    if '\\hat' in s:
        return 'hat'
    return s

wdr_symbols = set()
for latex in wdr_unique:
    wdr_symbols.add(normalize_latex_symbol(latex))

# === 3. Compare ===
print("=" * 70)
print("SYMBOL TAXONOMY COMPARISON: Metamath HTML vs WDR-RLHF Paper")
print("=" * 70)

print(f"\nMetamodel HTML symbol count: {len(meta_symbols)}")
print(f"WDR-RLHF unique latex symbol count: {len(wdr_symbols)}")

# Show sample
print("\n=== First 15 Metamath symbols ===")
for s in sorted(meta_symbols)[:15]:
    print(f"  {s}")

print("\n=== First 15 WDR-RLHF normalized symbols ===")
for s in sorted(wdr_symbols)[:15]:
    print(f"  {s}")

# Find overlap (normalized)
meta_norm = set()
for s in meta_symbols:
    s2 = s.strip()
    s2 = re.sub(r'\s*\(\d+x\d+\)\s*$', '', s2)
    meta_norm.add(s2.lower())

wdr_norm = set()
for s in wdr_unique:
    wdr_norm.add(normalize_latex_symbol(s))

overlap = meta_norm & wdr_norm
print(f"\nNormalized overlap: {len(overlap)}")

print("\n--- Overlap (normalized) ---")
for s in sorted(overlap):
    print(f"  {s}")

# Save results
results = {
    'metamodel_html_symbols': sorted(meta_symbols),
    'wdr_rlhf_unique_latex': sorted(wdr_unique),
    'wdr_rlhf_normalized_symbols': sorted(wdr_symbols),
    'overlap_normalized': sorted(overlap),
    'metamodel_count': len(meta_symbols),
    'wdr_rlhf_unique_count': len(wdr_unique),
    'overlap_count': len(overlap)
}

with open(
    '/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/'
    'DATASETS/symbol_taxonomy_comparison.json',
    'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to DATASETS/symbol_taxonomy_comparison.json")
