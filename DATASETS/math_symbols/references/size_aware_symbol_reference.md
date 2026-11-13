# Size-Aware Symbol Reference Tool
## For ArXiv Math Paper Vision Analysis

### Overview
This tool uses the Metamath symbol library (n x 19 pixels = 12pt font baseline) to detect symbol size roles in ArXiv math papers.

### How It Works

**The Key Insight:** All Metamath symbols are designed at 19 pixels tall (12pt font). When analyzing a symbol in an ArXiv PDF/image:

```
detected_height / 19 = scale factor
  < 0.5 → subscript or superscript
  0.5-0.8 → script or small
  0.8-1.2 → normal inline symbol
  1.2-1.5 → large operator
  > 1.5 → equation-level operator
```

**Aspect Ratio (width/height) tells you the role:**

| Aspect Ratio | Meaning | Example |
|--------------|---------|---------|
| < 0.6 | Narrow character | x, y, f, g (variables) |
| 0.6-1.2 | Normal width | =, +, +, ∩, ∪ |
| 1.2-2.5 | Wide operator | Σ, ∏, parentheses, fractions |
| ≥ 2.5 | Very wide | Integral sign, tall symbol |

### Usage

```python
from size_tool import analyze_symbol

# Detect a symbol in a paper (width, height in pixels)
result = analyze_symbol(detected_w=328, detected_h=150)

print(result)
# {
#   'detected_w': 328,
#   'detected_h': 150,
#   'size_category': 'large_operator',
#   'role': 'large_operator',
#   'aspect': 2.19,
#   'scale_factor': 7.89
# }
```

### Reference: Metamath Symbol Positions

All symbols in `manifest.json` with their positions:

| Sym | Index | Name | Coordinates | Size Analysis |
|-----|-------|------|-------------|---------------|
| 22 | rmw | Roman uppercase W | (295,8,311,27) | w=16,h=19, aspect=0.84 |
| 75 | x | lowercase Roman | (316,49,328,67) | w=12,h=18, aspect=0.67 |
| 206 | sigma | Summation | (287,148,300,168) | w=13,h=20, aspect=0.65 |
| 256 | subscrl | Script small l | (147,228,164,248) | w=17,h=20, aspect=0.85 |
| 742 | lp | Left paren | (278,569,289,588) | w=11,h=19, aspect=0.58 |
| 743 | rp | Right paren | (289,569,299,588) | w=10,h=19, aspect=0.53 |
| 740 | int | Integral | (257,569,278,588) | w=21,h=19, aspect=1.11 |
| 741 | oint | Line integral | (278,569,298,589) | w=20,h=20, aspect=1.00 |

### Installation

Copy the flat index and images to your analysis project:

```bash
# From KING-WEN-I-CHING-IMMUTABLE-TABLES
cd DATASETS/math_symbols
cp manifest.json manifest.csv size_tool.py /path/to/your/arxiv/vision/
cp -r images /path/to/your/arxiv/vision/
```

### Example: Analyzing a Symbol from an ArXiv Paper

```python
from size_tool import analyze_symbol

# Simulated detection from paper image
detected_w = 45   # symbol is 45 pixels wide
detected_h = 20   # symbol is 20 pixels tall

result = analyze_symbol(detected_w, detected_h)

# Output:
#   Size: large_operator
#   Role: large_operator
#   Scale: 1.05x baseline
#   Aspect: 2.25
```

### Reference Tables

**Base matches (19px = 12pt):**

| Symbol | Index | w×h (px) | Height ratio | Role |
|--------|-------|----------|--------------|------|
| x | 75 | 12×18 | 0.95× | normal |
| lp/rp | 742/743 | 11×19 / 10×19 | 0.53-0.58× | normal symbol |
| sigma | 206 | 13×20 | 1.05× | normal |
| subscrl | 256 | 17×20 | 1.05× | script |
| rmw | 22 | 16×19 | 1.00× | normal |
| int | 740 | 21×19 | 1.00× | normal |
| oint | 741 | 20×20 | 1.05× | normal |

**Size categories for paper symbols:**

| Category | Height Range | Role |
|----------|-------------|------|
| superscript | < 8px | tiny script (^x) |
| tiny_sub | 8-12px | subscript (x_i) |
| small_script | 12-16px | script letter |
| normal_inline | 13-22px | inline symbol (x, y, =, +) |
| large_operator | 17-30px | big operator (Σ, ∑) |
| very_large | 22-45px | equation operator (∫, ∬) |
| equation_level | > 45px | equation-level operator |

**Role classification by aspect:**

| Aspect | Interpretation | Example |
|--------|---------------|---------|
| < 0.6 | Narrow character | x, y, f |
| 0.6-1.2 | Normal character | +, =, ∩, ∪ |
| 1.2-2.5 | Wide operator | ( ), [ ], Σ, ∑ |
| ≥ 2.5 | Very wide | Integral sign (∬), big operators |

---

**Source:** Metamath symbol set at us.metamath.org/symbols/  
**Baseline:** 19px height = 12pt browser font (per Metamath documentation)  
**Dependencies:** None (pure Python)  
**File:** `size_tool.py` in this directory

---

### Delimiter, big-operator, and variant glyphs (append section)

#### A. Delimiter pair detection (tall delimiters at multiple scale sizes)

The size classifier (`size_tool.py`) returns a `size_category` by absolute
height and a `role` by aspect. This section adds the delimiter semantics
that are missing from the base classifier.

| Scale (height vs 19px baseline) | Delimiter pair observed | Required role |
|---------------------------------|--------------------------|---------------|
| 0.5–0.8× (tiny open/close) | `(` `)` `¥` `¦` | `delimiter_pair` only when paired with matching family |
| 0.8–1.2× | `⌊` `⌋` `⌈` `⌉` `⟨` `⟩` | `delimiter_pair` |
| 1.2–1.5× | `⌊` `⌋` `⌈` `⌉` `⟨` `⟩` with content inside | `delimiter_pair` (raised) |
| 1.5–2.0× | `⌊` `⌋` `⌈` `⌉` `⟨` `⟩` | `delimiter_pair` |
| >2.0× | `\left( ... \right)` stretched | `delimiter_pair` (stretch) |

A delimiter **pair** is two adjacent glyphs of the same family: `(`+`)`,
`[`+`]`, `{`+`}`, `⌊`+`⌋`, `⌈`+`⌉`, `⟨`+`⟩`, `∥`+`∥`, `∣`+`∣`. The size
layer classifies the pair as `delimiter_pair`; the AST layer (via
`delimiter_identity.py` and `delimiter_inference.py`) turns that token
pair into a typed node (`Floor`, `Ceil`, `Norm`, `AngleBracket`,
`Conditional`), so a 30 px glyph is never confused with a 30 px `sum`.

#### B. Larger delimiters acceptable as delimiters in "list" context

A list item rendered with a big delimiter (e.g. a numbered list where the
marker contains `∑` or a `\left[` group) is **inside a container**,
not a math big-operator. The extraction layer must not re-attribute it as
an equation operator simply because it is large:

- `sum`/`prod`/`int`/`oint`/`bigvee`/`bigcap`/`bigcup`/`bigsqcup`/`bigoplus`/`bigotimes`/`bigoplus`/`bigwedge` are big operators (labeled `big_operator` in the Metamath manifest).
- Delimiter glyphs (`lfloor`/`rfloor`, `lceil`/`rceil`, `langle`/`rangle`, `llangle`/`rrangle`, `sphericalangle`, `varangle`, `vert`, `lVert`/`rVert`) carry `kind: delimiter`.
- When a tall delimiter appears inside a list marker (low ink density,
  container context), tag the crop as `in_list` and route to the list
  normalizer, not the equation resolver. Use the existing `size_tool.py`
  classifier for height, plus a `container` flag from the layout pass.

Verification: `python -c` with a 45×30 px tall delimiter crop returns
`size_category: equation_level`, `role: delimiter_pair` after the add.

#### C. Rotated delimiters

Rotation is not a glyph identity, it is a **transform** of a glyph
family. The vision layer carries the glyph identity (which token family
the crop belongs to) and the layout pass carries the rotation flag.

| Glyph family | Identity tokens (delimiter_identity.py) | Rotation variants in manifest | Notes |
|--------------|------------------------------------------|-------------------------------|-------|
| Angle brackets | `LANGLE="langle"`, `RANGLE="rangle"` | `llangle`, `rrangle`, `sphericalangle`, `varangle` | `langle`/`rangle` are **not** parentheses |
| Norm (double bar) | `LNORM="lVert"`, `RNORM="rVert"` | `vert`, `lVert`, `rVert`, `brokenvert`, `aplvertdown` | `brokenvert` and `aplvertdown` are rotated/variant bars |
| Floor/ceiling | `LFLOOR="lfloor"`, `RFLOOR="rfloor"`, `LCEIL="lceil"`, `RCEIL="rceil"` | (none rotated in manifest) | Standalone, no rotation variants |

Rule: the vision classifier sets a `glyph_family` field from the manifest
`name` (`lfloor` → `floor`, `lfloor`+`rfloor` → `floor_pair`,
`lVert`+`rVert` → `norm_pair`). The layout pass sets `rotated: true` when
the crop's principal axis is >45° from the page horizontal. Rotation and
family are orthogonal fields; a 90°-rotated `lfloor` is still a `floor`
glyph and is resolved to `Floor(...)` in the AST layer.

#### D. Symbol sizes, fonts, and Greek caps/lowercase versioned

The size classifier (`size_tool.py`) returns a `size_category` by
absolute height. It does **not** return font/serif/bold or Greek-case.
The existing wolfram reference (`wolfram_notation_reference.md`, 143
entries) and the Metamath manifest supply those as variant metadata:

| Variant category | Example glyphs (wolfram doc / Metamath manifest) | Vision classifier tag |
|-----------------------------|---------------------------------------------------|----------------------|
| Greek lowercase | α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω | `greek_case: lower` |
| Greek uppercase | Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω | `greek_case: upper` |
| Script | ℒ ℳ ℛ 𝒞 𝒢 𝒥 𝒦 𝒩 𝒪 𝒫 𝒬 ℛ 𝒮 𝒯 𝒰 𝒱 𝒲 𝒳 𝒴 𝒵 | `font_style: script` |
| Double-struck | ℂ ℍ ℕ ℙ ℚ ℝ ℤ | `font_style: double_struck` |
| Fraktur | 𝔄 𝔅 𝔉 𝔊 𝔍 𝔎 𝔏 𝔐 𝔑 𝔒 𝔓 𝔘 𝔙 𝔚 𝔛 𝔜 | `font_style: fraktur` |
| Bold/italic | `\mathbf{x}`, `\mathit{x}` | `font_style: bold` / `italic` |

Rule: size classification and font/glyph-variant classification are
separate. A 19 px `σ` (sigma lowercase) and a 19 px `Σ` (sigma upper) are
**both** `normal_inline` by size; the case tag differs (`lower` vs
`upper`). The AST layer (mathematical engine) uses the tag to place the
symbol: `σ` (greek_case=lower) is a variable symbol; `Sum` is a big
operator and must carry `big_operator: true` with limits from the
msubsup/MathML tree, not from the size tag.


