import sys
sys.path.insert(0, 'scripts')
import math_recovery_tool as mrt
import re

s = r'a \rightarrow b'
print(f"Start: {s!r}")

# Apply ZERO_ARG_RULES one by one
for i, (pat, rep) in enumerate(mrt.ZERO_ARG_RULES):
    new_s = re.sub(pat, rep, s)
    if new_s != s:
        print(f"  Rule {i}: {pat!r} -> {rep!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s

print(f"After ZERO_ARG_RULES: {s!r}")
