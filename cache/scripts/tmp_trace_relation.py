import sys
sys.path.insert(0, 'scripts')
import math_recovery_tool as mrt

# Trace the issue step by step
# The problem: "a \Rightarrow b" becomes "a Rrightarrow b"
# This means "\R" is being replaced somewhere before RELATION_MAP

# Let's check if there's an accent map that processes \R
# Look for any map that has \R or \r
for name in dir(mrt):
    obj = getattr(mrt, name)
    if isinstance(obj, dict):
        for k in obj:
            if 'R' in k or 'L' in k:
                if len(k) <= 5:
                    print(f"{name}: {repr(k)} -> {repr(obj[k])}")
