# Phase 2B — Adversarial Challenge Set (Template)

**Version:** 1.0  
**Date:** 2026-10-25  
**Associated pilot:** `DATASETS/phase2b_pilot_selection.json`  
**Purpose:** Known defect cases for measuring detection behavior, separate from representative pilot metrics.

---

## Challenge Set Schema

Each entry in `DATASETS/phase2b_adversarial_challenge.jsonl`:

```json
{
  "challenge_id": "adv-001",
  "type": "truncation|operator_sub|token_reorder|delimiter_imbalance|duplicate_glyph|unsupported_glyph|reference_mismatch",
  "description": "Human-readable description of the defect",
  "reference_id": "optional link to reference_equations entry",
  "synthetic_latex": "optional synthetic LaTeX for the challenge",
  "expected_gate_failures": ["gate_1", "gate_3"],
  "notes": ""
}
```

---

## Initial Challenge Categories (to be populated)

### 1. Truncation
- Right-edge clipping (crop boundary cuts off equation end)
- Left-edge clipping
- Bottom clipping (subscripts/bounds cut off)
- Top clipping (superscripts/bounds cut off)

### 2. Operator Substitution
- `\sum` → `S` or `E`
- `\int` → `I` or `∫` (Unicode but wrong font)
- `\frac` → `/` or `÷`
- `\prod` → `P` or `π`
- `\sqrt` → `v` or `√` (missing radicand)
- `\partial` → `d` or `∂` (wrong variant)
- `\approx` → `~` or `≈` (spacing wrong)

### 3. Token Reordering
- Commutative operand swap (`a + b` → `b + a`)
- Bound displacement (`\sum_{i=1}^n` → `\sum_{n}^{i=1}`)
- Sub/superscript migration (`x_i^2` → `x^2_i`)
- Fraction numerator/denominator swap

### 4. Delimiter Imbalance
- Unmatched `\lVert` without `\rVert`
- `\langle` without `\rangle`
- `\lfloor` without `\rfloor`
- `\lceil` without `\rceil`
- Mismatched pair types (`\lVert ... \rangle`)

### 5. Duplicate Glyphs
- Double summation (`\sum\sum`)
- Double subscript (`x_{i_{j}}` when should be `x_{i,j}`)
- Double superscript
- Repeated operator (`\approx \approx`)

### 6. Unsupported Glyphs
- Custom Unicode not in standard math fonts
- Missing font coverage (e.g., `\mathfrak`, `\mathbb` without font)
- Private-use area characters
- Ligature breakdown

### 7. Reference Mismatch
- Reference equation differs from authoritative arXiv `x-tex` annotation
- Reference carries transcription error from PDF
- Reference uses wrong variant (e.g., `\epsilon` vs `\varepsilon`)

---

## Population Instructions

1. Draw from **known defects** observed in:
   - The 21-candidate visual audit (`DATASETS/vision_comparison/`)
   - Marker vs King Wen benchmark runs
   - Math parser regression corpus (`DATASETS/math_failure_corpus.jsonl`)

2. For each challenge, create a synthetic LaTeX variant that isolates the defect.

3. Record the **expected gate failures** — which of the 5 frozen gates should fail.

4. Keep challenge set **small and focused** (target: 20-30 challenges, one per defect class).

5. Challenge set results reported **separately** from pilot representative metrics.

---

## Status

- [ ] Populate from 21-candidate visual audit defects
- [ ] Populate from Marker benchmark failure modes
- [ ] Populate from math parser regression corpus
- [ ] Verify each challenge targets distinct defect class
- [ ] Record expected gate failures per challenge
- [ ] Write to `DATASETS/phase2b_adversarial_challenge.jsonl`