# Crop Isolation Experiment Report: Geometry Refinement vs Neighboring Prose

**Date:** 2026-10-23
**Target Paper:** `1907.04931` (GraphSAINT)
**Corpus Source:** `DATASETS/candidates_1907.04931_filtered.json`

---

## 1. Executive Summary

This controlled experiment tests four crop geometries across the 4 candidates of paper `1907.04931` to evaluate
whether reducing vertical padding eliminates prose contamination while preserving mathematical character recognition.
Crucially, the original source coordinates and frozen baseline records are preserved unmodified.

### Tested Configurations
- **`baseline`**: `padding_x = 15pt, padding_y = 15pt, zoom = 4` (original pipeline geometry)
- **`tight_pad2`**: `padding_x = 2pt, padding_y = 2pt, zoom = 4` (standard minimal symmetric padding)
- **`asym_tight_y1`**: `padding_x = 3pt, padding_y = 1pt, zoom = 4` (asymmetric: tight vertical boundary, slight horizontal breathing room)
- **`zero_y_pad0`**: `padding_x = 2pt, padding_y = 0pt, zoom = 4` (zero vertical padding)

---

## 2. Quantitative Results Table

| Cand | Target | Config | Pixel Shape | Multiline? | Prose Detected | Target Present | Formula Isolated? |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 0 | `ζ(ℓ+1)` | `baseline` | 172x220 | Yes | Yes | Yes | ❌ NO |
| 0 | `ζ(ℓ+1)` | `tight_pad2` | 68x116 | No | No | Yes | ✅ YES |
| 0 | `ζ(ℓ+1)` | `asym_tight_y1` | 60x124 | No | No | Yes | ✅ YES |
| 0 | `ζ(ℓ+1)` | `zero_y_pad0` | 52x116 | No | No | Yes | ✅ YES |
| 1 | `ζ(ℓ+1)` | `baseline` | 172x220 | No | No | Yes | ✅ YES |
| 1 | `ζ(ℓ+1)` | `tight_pad2` | 68x116 | No | No | Yes | ✅ YES |
| 1 | `ζ(ℓ+1)` | `asym_tight_y1` | 60x124 | No | No | Yes | ✅ YES |
| 1 | `ζ(ℓ+1)` | `zero_y_pad0` | 52x116 | No | No | Yes | ✅ YES |
| 2 | `√pe` | `baseline` | 190x190 | Yes | Yes | Yes | ❌ NO |
| 2 | `√pe` | `tight_pad2` | 86x86 | No | No | Yes | ✅ YES |
| 2 | `√pe` | `asym_tight_y1` | 78x94 | No | No | Yes | ✅ YES |
| 2 | `√pe` | `zero_y_pad0` | 70x86 | No | No | Yes | ✅ YES |
| 3 | `∝√pe.` | `baseline` | 189x243 | Yes | Yes | Yes | ❌ NO |
| 3 | `∝√pe.` | `tight_pad2` | 85x139 | No | No | Yes | ✅ YES |
| 3 | `∝√pe.` | `asym_tight_y1` | 77x147 | No | No | Yes | ✅ YES |
| 3 | `∝√pe.` | `zero_y_pad0` | 69x139 | No | No | Yes | ✅ YES |

---

## 3. Detailed Per-Candidate Comparison

### Candidate 0: `ζ(ℓ+1)` (Page 4, inline_math)
**Original PDF BBox:** `{'x0': 179.552001953125, 'y0': 551.40673828125, 'x1': 204.29542541503906, 'y1': 564.20849609375}`

#### Configuration: `baseline` (pad_x=15, pad_y=15)
- **Image Crop:** [`cand_0_baseline_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_0_baseline_p4.png) (172×220 px)
- **Recognized LaTeX:** `\begin{array} {l} {\mathrm{a g ~ s a m p l e d ~ i n}} \\ {\mathbf{. 1 . ~} \zeta_{v}^{( \ell+1 )} \ i s \ \ell} \\ {=\frac{p_{u , v}} {n} . \ i . e . , \ \mathbb{E}} \\ \end{array}`
- **Formula Isolated:** False
- **Prose Contamination:** True (words: ['array', 'array'])
- **Agreement Category:** `embedded_in_prose`

#### Configuration: `tight_pad2` (pad_x=2, pad_y=2)
- **Image Crop:** [`cand_0_tight_pad2_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_0_tight_pad2_p4.png) (68×116 px)
- **Recognized LaTeX:** `\zeta_{v}^{( \ell+1 )}`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `asym_tight_y1` (pad_x=3, pad_y=1)
- **Image Crop:** [`cand_0_asym_tight_y1_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_0_asym_tight_y1_p4.png) (60×124 px)
- **Recognized LaTeX:** `\zeta_{v}^{( \ell+1 )}`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `zero_y_pad0` (pad_x=2, pad_y=0)
- **Image Crop:** [`cand_0_zero_y_pad0_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_0_zero_y_pad0_p4.png) (52×116 px)
- **Recognized LaTeX:** `\zeta_{v}^{( \ell+1 )}`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

### Candidate 1: `ζ(ℓ+1)` (Page 4, inline_math)
**Original PDF BBox:** `{'x0': 225.9519805908203, 'y0': 566.3507690429688, 'x1': 250.69540405273438, 'y1': 579.1525268554688}`

#### Configuration: `baseline` (pad_x=15, pad_y=15)
- **Image Crop:** [`cand_1_baseline_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_1_baseline_p4.png) (172×220 px)
- **Recognized LaTeX:** `\stackrel{s \ a n \ u n b i a s e d} {\mathbb{E} \left( \zeta_{v}^{( \ell+1 )} \right)}=`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `tight_pad2` (pad_x=2, pad_y=2)
- **Image Crop:** [`cand_1_tight_pad2_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_1_tight_pad2_p4.png) (68×116 px)
- **Recognized LaTeX:** `\left( \zeta_{v}^{( \ell+1 )} \right)`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `asym_tight_y1` (pad_x=3, pad_y=1)
- **Image Crop:** [`cand_1_asym_tight_y1_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_1_asym_tight_y1_p4.png) (60×124 px)
- **Recognized LaTeX:** `\left( \zeta_{v}^{( \ell+1 )} \right)`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `zero_y_pad0` (pad_x=2, pad_y=0)
- **Image Crop:** [`cand_1_zero_y_pad0_p4.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_1_zero_y_pad0_p4.png) (52×116 px)
- **Recognized LaTeX:** `\zeta_{v}^{( \ell+1 )}`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

### Candidate 2: `√pe` (Page 12, true_equation)
**Original PDF BBox:** `{'x0': 307.9109802246094, 'y0': 286.71783447265625, 'x1': 325.0057678222656, 'y1': 303.8585510253906}`

#### Configuration: `baseline` (pad_x=15, pad_y=15)
- **Image Crop:** [`cand_2_baseline_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_2_baseline_p12.png) (190×190 px)
- **Recognized LaTeX:** `\begin{aligned} {} & {{} \mathrm{e d ~ n u m b e r ~ c}} \\ {} & {{} \sum_{e} \left( \sqrt{p_{e}} \right)^{2} \geq} \\ {} & {{} \mathrm{~ z e d ~ w h e n ~ p ~}} \\ \end{aligned}`
- **Formula Isolated:** False
- **Prose Contamination:** True (words: ['aligned', 'aligned'])
- **Agreement Category:** `embedded_in_prose`

#### Configuration: `tight_pad2` (pad_x=2, pad_y=2)
- **Image Crop:** [`cand_2_tight_pad2_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_2_tight_pad2_p12.png) (86×86 px)
- **Recognized LaTeX:** `( \sqrt{p_{e}} )`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `asym_tight_y1` (pad_x=3, pad_y=1)
- **Image Crop:** [`cand_2_asym_tight_y1_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_2_asym_tight_y1_p12.png) (78×94 px)
- **Recognized LaTeX:** `( \sqrt{p_{e}} )`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `zero_y_pad0` (pad_x=2, pad_y=0)
- **Image Crop:** [`cand_2_zero_y_pad0_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_2_zero_y_pad0_p12.png) (70×86 px)
- **Recognized LaTeX:** `( \sqrt{p_{e}} )`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

### Candidate 3: `∝√pe.` (Page 12, true_equation)
**Original PDF BBox:** `{'x0': 169.0889892578125, 'y0': 306.2628173828125, 'x1': 199.6886444091797, 'y1': 323.4025573730469}`

#### Configuration: `baseline` (pad_x=15, pad_y=15)
- **Image Crop:** [`cand_3_baseline_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_3_baseline_p12.png) (189×243 px)
- **Recognized LaTeX:** `\begin{array} {l} {{\sf\zeta}_{e} \, \frac{( \sum_{\ell} {\sf b}_{e}^{{\sf c} {\sf T}} )} {{\sf p}_{e}} m \, ;} \\ {\frac{{\sf e}^{( \ell)}} {\sf e} \Big| \propto\sqrt{p_{e}} . \mathrm{~ i . e .}} \\ {\mathrm{c l l o w s ~ t h a t .}} \\ \end{array}`
- **Formula Isolated:** False
- **Prose Contamination:** True (words: ['array', 'array'])
- **Agreement Category:** `embedded_in_prose`

#### Configuration: `tight_pad2` (pad_x=2, pad_y=2)
- **Image Crop:** [`cand_3_tight_pad2_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_3_tight_pad2_p12.png) (85×139 px)
- **Recognized LaTeX:** `\propto\sqrt{p_{e}} .`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `asym_tight_y1` (pad_x=3, pad_y=1)
- **Image Crop:** [`cand_3_asym_tight_y1_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_3_asym_tight_y1_p12.png) (77×147 px)
- **Recognized LaTeX:** `\propto\sqrt{p_{e}} .`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

#### Configuration: `zero_y_pad0` (pad_x=2, pad_y=0)
- **Image Crop:** [`cand_3_zero_y_pad0_p12.png`](DATASETS\vision_comparison\crop_isolation_experiment\cand_3_zero_y_pad0_p12.png) (69×139 px)
- **Recognized LaTeX:** `\propto\sqrt{p_{e}} .`
- **Formula Isolated:** True
- **Prose Contamination:** False (words: [])
- **Agreement Category:** `high`

---

## 4. Key Findings & Synthesis

1. **Baseline Failure Mode Confirmed:** At `pad = 15pt`, a 12pt line receives 30pt additional vertical height,
   inevitably capturing lines above and below. This triggers Pix2Text to emit multi-line tables (`\begin{array}` or `\begin{aligned}`)
   with prose words from surrounding sentences.
2. **Tighter Vertical Bounds:** Tighter vertical padding drastically suppresses surrounding prose lines.
3. **Isolation Assessment:** True formula isolation requires bounding-box boundaries to respect font ascenders/descenders
   without crossing line-spacing margins.
