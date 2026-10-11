import sys
sys.path.insert(0, 'scripts')
import math_recovery_tool as mrt
import re

# Monkey-patch to trace replacements
original_replace = str.replace

test_cases = [
    (r'a \Rightarrow b', 'Rightarrow'),
    (r'a \Leftrightarrow b', 'Leftrightarrow'),
    (r'a \rightarrow b', 'rightarrow'),
]

print("=== Tracing relation collapse ===")
for latex, expected_token in test_cases:
    recovered, _ = mrt.recover_latex(latex)
    print(f"\nInput:  {latex}")
    print(f"Output: {recovered}")
    print(f"Expected token '{expected_token}' in output: {expected_token in recovered}")

# Now let's trace step by step
print("\n\n=== Step-by-step trace for \\Rightarrow ===")
s = r'a \Rightarrow b'
print(f"Start: {s}")

# Apply ZERO_ARG_RULES
for pat, rep in mrt.ZERO_ARG_RULES:
    new_s = re.sub(pat, rep, s)
    if new_s != s:
        print(f"  ZERO_ARG_RULES: {pat!r} -> {rep!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s

# Apply OPERATOR_MAP
for k, v in mrt.OPERATOR_MAP.items():
    new_s = s.replace(k, v)
    if new_s != s:
        print(f"  OPERATOR_MAP: {k!r} -> {v!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s

# Apply RELATION_MAP
for k, v in mrt.RELATION_MAP.items():
    new_s = s.replace(k, v)
    if new_s != s:
        print(f"  RELATION_MAP: {k!r} -> {v!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s

print(f"Final: {s}")
