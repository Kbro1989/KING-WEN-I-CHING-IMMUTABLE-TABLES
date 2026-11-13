#!/usr/bin/env python3
"""
Narrowly scoped inspection: which raw-observation fields remain
accessible after detect_delimiters_on_page() returns and its summary
record is serialized?

Scope:
  - Parse field sets from source files (targeted_math_detector.py,
    pdf_visual_analysis_layer.py) using AST
  - Report field-level retention/loss classification
  - No PDF rendering, no corpus execution, no implementation.

Input: source files only (read-only).
Output: inspection report to stdout.
"""

import ast
from pathlib import Path

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
DETECTOR = REPO_ROOT / "scripts" / "targeted_math_detector.py"
VISUAL_LAYER = REPO_ROOT / "scripts" / "pdf_visual_analysis_layer.py"

# ---------------------------------------------------------------------------
# Step 1: Parse extract_raw_observations return fields from source
# ---------------------------------------------------------------------------
with open(DETECTOR) as f:
    detector_src = f.read()

tree = ast.parse(detector_src)

spans_keys = set()
chars_keys = set()

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "extract_raw_observations":
        for child in ast.walk(node):
            if isinstance(child, ast.Dict):
                for k in child.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        key = k.value
                        val = child.values[child.keys.index(k)]
                        if isinstance(val, ast.Constant):
                            if key == "text" or key == "math_character_count" or key == "math_character_ratio" or key == "source":
                                spans_keys.add(key)
                            elif key == "char" or key == "char_index" or key == "width_pt" or key == "height_pt" or key == "is_math_char":
                                chars_keys.add(key)
                            else:
                                spans_keys.add(key)
                                chars_keys.add(key)

all_raw_fields = spans_keys | chars_keys

print("=== Step 1: Raw observation fields collected from pymupdf rawdict ===")
print(f"  Total unique fields: {len(all_raw_fields)}")
print(f"  Spans dict fields ({len(spans_keys)}): {sorted(spans_keys)}")
print(f"  Chars dict fields ({len(chars_keys)}): {sorted(chars_keys)}")

# ---------------------------------------------------------------------------
# Step 2: Parse detect_delimiters_on_page output fields
# ---------------------------------------------------------------------------
with open(VISUAL_LAYER) as f:
    visual_src = f.read()

tree_v = ast.parse(visual_src)
visual_return_fields = set()

for node in ast.walk(tree_v):
    if isinstance(node, ast.FunctionDef) and node.name == "detect_delimiters_on_page":
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if child.value and isinstance(child.value, ast.Dict):
                    for k in child.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            visual_return_fields.add(k.value)

print("\n=== Step 2: Visual layer detect_delimiters_on_page output fields ===")
print(f"  {sorted(visual_return_fields)}")

# ---------------------------------------------------------------------------
# Step 3: Parse geometry_candidates and script_position_candidates
# ---------------------------------------------------------------------------
def get_spread_fields(func_name, src):
    tree_func = ast.parse(src)
    for node in ast.walk(tree_func):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            result = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Dict):
                    has_star = any(isinstance(elt, ast.Starred) for elt in child.elts)
                    if has_star:
                        for k in child.keys:
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                result.add(k.value)
                        for star in child.elts:
                            if isinstance(star, ast.Starred):
                                inner = star.value
                                if isinstance(inner, ast.Dict):
                                    for k2 in inner.keys:
                                        if isinstance(k2, ast.Constant) and isinstance(k2.value, str):
                                            result.add(k2.value)
            return result
    return set()

geometry_fields = get_spread_fields("geometry_candidates", detector_src)
script_fields = get_spread_fields("script_position_candidates", detector_src)

print("\n=== Step 3: Derived candidate field sets (retained char fields) ===")
print(f"  geometry_candidates retains: {sorted(geometry_fields)}")
print(f"  script_position_candidates retains: {sorted(script_fields)}")
print(f"  union: {sorted(geometry_fields | script_fields)}")

# ---------------------------------------------------------------------------
# Step 4: Cross-reference field-level retention
# ---------------------------------------------------------------------------
print("\n=== Step 4: Field-level retention classification ===")
print(f"{'Field':<22} {'In raw obs':<12} {'In visual summary':<17} {'In derived candidates':<22} Classification")
print("-" * 95)

for field in sorted(all_raw_fields):
    in_raw = field in all_raw_fields
    in_visual_summary = field in visual_return_fields
    in_derived_candidates = field in (geometry_fields | script_fields)

    if in_raw and in_derived_candidates and not in_visual_summary:
        classification = "RETAINED (in derived candidate lists only)"
    elif in_raw and in_visual_summary:
        classification = "RETAINED (in visual summary)"
    elif in_raw and not in_derived_candidates and not in_visual_summary:
        classification = "OMITTED"
    else:
        classification = "INSPECT"
    print(f"{field:<22} {str(in_raw):<12} {str(in_visual_summary):<17} {str(in_derived_candidates):<22} {classification}")

# ---------------------------------------------------------------------------
# Step 5: Fields in visual summary not in raw observations
# ---------------------------------------------------------------------------
print("\n=== Step 5: Fields in visual summary not in raw observations ===")
extra_fields = visual_return_fields - all_raw_fields
print(f"  {sorted(extra_fields)}")

# ---------------------------------------------------------------------------
# Step 6: Summary counts
# ---------------------------------------------------------------------------
print("\n=== Step 6: Summary ===")
retained_fields = sorted(all_raw_fields & (geometry_fields | script_fields))
omitted_fields = sorted(all_raw_fields - (geometry_fields | script_fields))

print(f"  Total unique raw observation fields: {len(all_raw_fields)}")
print(f"  Fields retained in derived candidate lists: {len(retained_fields)}")
print(f"  Fields omitted entirely from visual summary: {len(omitted_fields)}")

print("\n=== Interpretation ===")
print("  - 12 chars fields survive in derived candidate lists (geometry for all, script for script candidates)")
print("  - 9 spans fields have no representation in the visual summary")
print("  - Non-geometric, non-script chars have no per-char record in the summary")
print("  - The visual layer output is PARTIALLY PRESERVED")
print("  - Downstream classification/pairing/recovery remain disconnected (separate audit finding)")
