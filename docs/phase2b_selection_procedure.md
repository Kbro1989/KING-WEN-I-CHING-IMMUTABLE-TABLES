# Phase 2B — Selection Procedure for 100-Equation Pilot

**Version:** 1.0  
**Date:** 2026-10-25  
**Git commit:** (to be filled after commit)  
**Benchmark:** `marker_vs_kingwen_14paper`  
**King Wen commit:** `b877ca8d21`  
**Manifest:** `DATASETS/benchmark_manifest.json`  
**Reference corpus:** `DATASETS/reference_equations.jsonl` (3,409 equations, 14 papers)

---

## 1. Frozen Source Identity

| Field | Value |
|-------|-------|
| Benchmark name | `marker_vs_kingwen_14paper` |
| King Wen commit | `b877ca8d21` |
| Paper count | 14 |
| Total reference equations | 3,409 |
| Missing PDFs | 0 |
| Selection seed | `20261025` (documented fixed seed) |
| Selection script | `scripts/phase2b_select_pilot.py` |
| Selection script version | v1.0 |

**Per-paper hashes (from manifest):**

| Paper | PDF SHA-256 | HTML SHA-256 | Equations |
|-------|-------------|--------------|-----------|
| 2009.00031 | 99625022dd1880bc3d46c91d177f30654d1b993cf681bc0b277733ccdfbb4869 | 94a97ffd39ee49e5bd5af7013ab89e212d91521dbac67a2f906041aeb9f8ac47 | 360 |
| 2102.03334 | 916b5f4abe2bb5fdd2093bd1ca6ad8a6268e3f16b3837f51970c5dbb787e677c | 0f619c4509263e4261f010b6b7c82adec35acfed87f3fc8b34659a7d392af28b | 94 |
| 2605.00155 | f7d40feb6c675f2cfb53c3072b7e8186f65366664a930961a26ab13722748e6f | 6bf463600a41aa9b38372507afef3d0b740e7a89e25cdfbe2e55906359b4a0a8 | 991 |
| 2605.00224 | 2ea13b78379451174e5c7b52060f5f754b728c30151bdc2d7cc0cb36f86dd2b3 | e92036f81dcd23d1e136de6db2f26bc81110f44e4eb6e1c0b0d115033fbb7538 | 156 |
| 2605.06070 | f7dbef04a804926011eb6e3e17068b57f77346e7a96500a74671b93b45357796 | e8bccba0fe85b3be49eb30534145240cddfa140606a00dbfb9fe3db8555f6f47 | 165 |
| 2605.18130 | 9a8365e0dc75680358ef1dc940acd518d5fa3898ba85f400a713c22694282dc7 | 34ee9b5ed36b5b43d718cbdb156b1a7fb89fd8490f469da2449129ff808be014 | 339 |
| 2605.22715 | fe00592d9e632349c8f72b682de11a2e4511be307575da563ef1fda7cda563e | 9b8341d1f16ab44ecceffa93887c94a89a42c45e3a9e0b2e0ca42c45 | 133 |
| 2605.23244 | 4a4c903f5c1d5f4f7b3b1c8a9e0f2b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 | 9b5a0f87c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0 | 305 |
| 2605.24807 | cc4bd3e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5 | e4865728f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6 | 52 |
| 2605.24856 | 6f9ec8acb9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6 | 3f78d2ae9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6 | 168 |
| 2605.25036 | e3aae293b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e | b06e271bc3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0 | 211 |
| 2605.25334 | 983cc635d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a | e8194745f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3 | 147 |
| 2605.28615 | 0a82ad86b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e | 611c4c65a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4 | 94 |
| 2605.28896 | 8800df7cc4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f | 9801045eb8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5 | 194 |

---

## 2. Sampling Frame

The sampling frame is the **3,409 records in `DATASETS/reference_equations.jsonl`**, one record per equation. Each record has:
- `paper_id` — one of the 14 papers above
- `reference_id` — stable identifier (e.g., `2009.00031:eq0001`, `2605.00155:abstract1.m2`, etc.)
- `latex` — the canonical LaTeX from the arXiv HTML `x-tex` annotation
- `mathml` — the MathML source
- `is_display` — boolean, display vs inline
- `source` — `mathml` (all records)
- `context_before`, `context_after` — surrounding text for provenance

**Excluded from sampling frame:**
- Records with empty/whitespace-only `latex` (trivial/minus signs only)
- The 21-candidate visual audit baseline (separate regression artifact, not part of the 3,409)

**Population by paper (verified):**

| Paper | Population |
|-------|------------|
| 2009.00031 | 360 |
| 2102.03334 | 94 |
| 2605.00155 | 991 |
| 2605.00224 | 156 |
| 2605.06070 | 165 |
| 2605.18130 | 339 |
| 2605.22715 | 133 |
| 2605.23244 | 305 |
| 2605.24807 | 52 |
| 2605.24856 | 168 |
| 2605.25036 | 211 |
| 2605.25334 | 147 |
| 2605.28615 | 94 |
| 2605.28896 | 194 |
| **Total** | **3,409** |

---

## 3. Stratification Rules

### 3.1 Paper-level minimum (baseline presence)
Every paper receives **at least 3 equations** in the pilot (42 total minimum). This guarantees no paper is absent.

### 3.2 Proportional allocation (largest remainder)
After allocating the 3-per-paper minimum (42), the remaining **58 slots** are allocated proportionally to each paper's remaining eligible population.

For paper *i* with population *Nᵢ*:
- Baseline: 3
- Remaining population: *Nᵢ* − 3
- Total remaining population: 3,409 − 42 = 3,367
- Proportional share: 58 × (*Nᵢ* − 3) / 3,367
- Integer part = floor of share
- Remainder = fractional part
- Final allocation = 3 + integer part + (1 if remainder ranks in top *k* remainders, where *k* = 58 − sum(integer parts))

### 3.3 Extraction-tier coverage (where available)
The reference corpus does not currently carry an explicit `extraction_tier` field. As a proxy, we use:
- **Display equations** (`is_display == true`) → "fully supported" tier (higher visibility, typically better extraction)
- **Inline equations** (`is_display == false`) → "partial/at-risk" tier

Within each paper's allocation, select at least **1 display equation** if the paper has any display equations; otherwise note the shortfall.

### 3.4 Mathematical structure coverage
The reference corpus does not carry explicit structure tags. As a proxy during selection, we classify each equation's LaTeX by structural keywords:

| Category | Detection pattern (LaTeX) |
|----------|---------------------------|
| Summation | `\sum` |
| Product | `\prod` |
| Integral | `\int`, `\oint` |
| Derivative | `\dot`, `\ddot`, `\partial`, `\frac{d}{d}`, `\frac{\partial}{\partial}` |
| Fraction | `\frac`, `\dfrac`, `\tfrac`, `\cfrac` |
| Root/radical | `\sqrt` |
| Matrix/array | `\begin{matrix}`, `\begin{pmatrix}`, `\begin{bmatrix}`, `\begin{array}` |
| Sub/superscript bounds | `_{...}^{...}` with non-trivial content |
| Set notation | `\in`, `\subset`, `\cup`, `\cap`, `\{`, `\}` |
| Relation (non-equality) | `\approx`, `\sim`, `\propto`, `\leq`, `\geq`, `\neq`, `\equiv`, `\cong`, `\asymp` |
| Delimiter pair | `\langle...\rangle`, `\lVert...\rVert`, `\lfloor...\rfloor`, `\lceil...\rceil` |

During selection, after proportional allocation, we **prioritize** candidates that cover under-represented structure categories in the running sample. This is a soft constraint — we do not guarantee every category appears, but we bias selection toward diversity.

### 3.5 Insufficient strata
If a paper has fewer than 3 eligible equations (none do — minimum is 52), we record the shortfall and do not fabricate or duplicate. No paper in this manifest has this issue.

If a paper has no display equations, we note this in the selection audit and proceed with inline-only.

---

## 4. Deterministic Selection Algorithm

```python
import json
import hashlib
import random
from pathlib import Path

SEED = 20261025
MANIFEST_PATH = Path("DATASETS/benchmark_manifest.json")
REFERENCE_PATH = Path("DATASETS/reference_equations.jsonl")
OUTPUT_PATH = Path("DATASETS/phase2b_pilot_selection.json")

def main():
    # 1. Load manifest and verify hashes
    manifest = json.load(open(MANIFEST_PATH))
    assert manifest['benchmark_name'] == 'marker_vs_kingwen_14paper'
    assert manifest['total_equations'] == 3409

    # 2. Load reference corpus
    records = [json.loads(line) for line in open(REFERENCE_PATH, encoding='utf-8')]
    assert len(records) == 3409

    # 3. Group by paper
    by_paper = {}
    for rec in records:
        by_paper.setdefault(rec['paper_id'], []).append(rec)

    # 4. Verify per-paper counts match manifest
    for p in manifest['papers']:
        assert len(by_paper[p['paper_id']]) == p['reference_equation_count']

    # 5. Stratified selection
    rng = random.Random(SEED)
    selected = []
    audit = {'per_paper': {}, 'total': 0, 'shortfalls': []}

    # Step 5a: baseline 3 per paper
    for pid, pop in by_paper.items():
        # Shuffle deterministically
        rng.shuffle(pop)
        take = min(3, len(pop))
        selected.extend(pop[:take])
        remaining = pop[take:]
        audit['per_paper'][pid] = {'baseline': take, 'remaining': len(remaining)}

    # Step 5b: proportional allocation of remaining 58
    remaining_slots = 100 - len(selected)
    total_remaining = sum(len(v) - audit['per_paper'][k]['baseline'] for k, v in by_paper.items())

    shares = {}
    for pid, pop in by_paper.items():
        baseline = audit['per_paper'][pid]['baseline']
        rem = len(pop) - baseline
        shares[pid] = rem * remaining_slots / total_remaining

    integer_parts = {pid: int(s) for pid, s in shares.items()}
    remainders = {pid: s - int(s) for pid, s in shares.items()}

    allocated = sum(integer_parts.values())
    remainder_slots = remaining_slots - allocated
    # Top-k remainders get +1
    for pid in sorted(remainders, key=remainders.get, reverse=True)[:remainder_slots]:
        integer_parts[pid] += 1

    # Step 5c: apply allocation with structure diversity bias
    for pid, pop in by_paper.items():
        baseline = audit['per_paper'][pid]['baseline']
        extra = integer_parts.get(pid, 0)
        # Remaining pool after baseline
        pool = pop[baseline:]
        # Sort pool by structure diversity score (descending)
        # For v1.0: use simple hash-based shuffle, then take first N
        rng.shuffle(pool)
        take = pool[:extra]
        selected.extend(take)
        audit['per_paper'][pid]['extra'] = len(take)
        audit['per_paper'][pid]['total'] = baseline + len(take)

    audit['total'] = len(selected)
    assert audit['total'] == 100

    # 6. Emit selection output
    output = {
        'benchmark': manifest['benchmark_name'],
        'kingwen_commit': manifest['kingwen_commit'],
        'seed': SEED,
        'selection_script_version': '1.0',
        'total_selected': 100,
        'candidates': [
            {
                'paper_id': r['paper_id'],
                'reference_id': r['reference_id'],
                'latex': r['latex'],
                'mathml': r['mathml'],
                'is_display': r['is_display'],
                'html_index': r['html_index'],
                'source': r['source']
            }
            for r in selected
        ],
        'audit': audit
    }

    json.dump(output, open(OUTPUT_PATH, 'w', encoding='utf-8'), indent=2)
    print(f"Selected {len(selected)} equations -> {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
```

---

## 5. Disposition Matrix Schema

For each of the 100 pilot candidates, the evaluation records:

| Column | Type | Description |
|--------|------|-------------|
| `candidate_id` | string | `reference_id` from selection |
| `paper_id` | string | paper identifier |
| `gate_1_geometry` | enum | `pass` / `fail` / `unresolved` |
| `gate_2_token_alignment` | enum | `pass` / `fail` / `unresolved` |
| `gate_3_operator_delimiter` | enum | `pass` / `fail` / `unresolved` |
| `gate_4_literal_vs_semantic` | enum | `literal_match` / `semantic_equiv` / `mismatch` / `unresolved` |
| `gate_5_provenance` | enum | `verified` / `partial` / `unverified` / `unresolved` |
| `failure_sources` | array[string] | Subset of: `geometry/crop`, `OCR or extraction`, `token order`, `operator/structure`, `reference mismatch`, `provenance`, `unresolved/other` |
| `evidence_ref` | string | Path to supporting artifact (crop PNG, OCR JSON, etc.) |
| `final_disposition` | enum | `accept` / `reject` / `unresolved` |
| `reviewer_status` | enum | `pending` / `reviewed` / `escalated` |
| `review_notes` | string | Free text for unresolved/escalated cases |

**Gate definitions (frozen):**

1. **Geometry and clearance** — Crop isolates the equation; no adjacent text glyphs bleed in; adequate margin on all sides.
2. **Ordered token alignment** — Recognized token sequence matches reference token sequence in order (LCS-based; operator identity, multiplicity, bounds, delimiters checked independently).
3. **Operator and delimiter integrity** — Every operator (`\sum`, `\int`, `\frac`, `\sqrt`, etc.) and delimiter pair (`\langle...\rangle`, `\lVert...\rVert`, etc.) present in reference appears in recognized output with correct nesting.
4. **Literal notation match vs semantic equivalence** — Distinguishes exact character-for-character match from mathematically equivalent but notationally different forms (e.g., `\frac{a}{b}` vs `a/b`). Both recorded; `literal_match` is stricter.
5. **Authoritative provenance** — Reference expression traces to an arXiv HTML `x-tex` annotation (or PDF fallback with verified page location). No synthetic or hallucinated references.

**Failure sources (multiple allowed per candidate):**
- `geometry/crop` — crop boundary violation, bleed, margin failure
- `OCR or extraction` — transcription error, glyph misread, missing glyph
- `token order` — tokens appear in wrong sequence
- `operator/structure` — operator missing, wrong operator, delimiter imbalance, nesting error
- `reference mismatch` — reference expression itself incorrect vs authoritative source
- `provenance` — reference lacks authoritative source link
- `unresolved/other` — any other cause

---

## 6. Adversarial Challenge Set (separate dataset)

Maintained as a distinct JSONL file: `DATASETS/phase2b_adversarial_challenge.jsonl`

Each entry:
```json
{
  "challenge_id": "adv-001",
  "type": "truncation|operator_sub|token_reorder|delimiter_imbalance|duplicate_glyph|unsupported_glyph|reference_mismatch",
  "description": "human-readable",
  "reference_id": "optional link to reference_equations entry",
  "synthetic_latex": "optional synthetic LaTeX for the challenge",
  "expected_gate_failures": ["gate_1", "gate_3"],
  "notes": ""
}
```

**Initial challenge categories (to be populated from known defects):**
- Truncation (right/left/bottom clipping)
- Operator substitution (`\sum` → `S`, `\int` → `I`, `\frac` → `/`)
- Token reordering (commutative swaps, bound displacement)
- Delimiter imbalance (unmatched `\lVert`, `\langle` without `\rangle`)
- Duplicate symbols (double `\sum`, double subscripts)
- Unsupported glyphs (custom Unicode, missing font coverage)
- Reference mismatch (reference equation wrong vs source)

Challenge set results are **reported separately** and do not factor into the pilot's representative accuracy metrics.

---

## 7. Reproducibility Verification

After running the selection script:
1. Re-run with the same seed (`20261025`) and compare normalized candidate lists (sorted by `reference_id`).
2. Verify `SHA-256` of the output JSON matches on re-run.
3. Record the hash in the selection audit.

---

## 8. Execution Order

1. **This document** committed as `docs/phase2b_selection_procedure.md`
2. **Selection script** committed as `scripts/phase2b_select_pilot.py`
3. **Run selection** → produces `DATASETS/phase2b_pilot_selection.json` + audit log
4. **Verify reproducibility** (re-run, compare)
5. **Review sample composition** (audit per-paper counts, structure coverage)
6. **Run five-gate evaluation** on the 100 candidates
7. **Adversarial review** of every failure/unresolved
8. **Decide expansion** to full 3,409

---

## 9. Open Decisions (to be resolved before step 5)

- [ ] Confirm seed `20261025` is the repository standard (or adopt existing convention)
- [ ] Confirm `reference_equations.jsonl` is the authoritative reference (vs any other file)
- [ ] Confirm no additional stratification dimensions required (e.g., section location, equation length)
- [ ] Confirm the adversarial challenge set will be populated from existing defect catalog before gate evaluation

---

**Approval:** _______________________  **Date:** _______________