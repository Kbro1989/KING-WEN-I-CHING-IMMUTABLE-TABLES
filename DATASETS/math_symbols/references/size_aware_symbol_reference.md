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
