import sys
sys.path.insert(0, 'scripts')
import math_recovery_tool as mrt
import re

s = r'a \Rightarrow b'
print(f"Start: {s!r}")

# Step 1: ZERO_ARG_RULES
for i, (pat, rep) in enumerate(mrt.ZERO_ARG_RULES):
    new_s = re.sub(pat, rep, s)
    if new_s != s:
        print(f"  ZERO_ARG_RULES[{i}]: {pat!r} -> {rep!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s
print(f"After ZERO_ARG_RULES: {s!r}")

# Step 2: OPERATOR_MAP
for k, v in mrt.OPERATOR_MAP.items():
    new_s = s.replace(k, v)
    if new_s != s:
        print(f"  OPERATOR_MAP: {k!r} -> {v!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s
print(f"After OPERATOR_MAP: {s!r}")

# Step 3: RELATION_MAP (single-pass regex)
_relation_pattern = re.compile(
    '|'.join(re.escape(k) for k, _ in sorted(mrt.RELATION_MAP.items(), key=lambda x: -len(x[0])))
)
new_s = _relation_pattern.sub(lambda m: mrt.RELATION_MAP[m.group(0)], s)
if new_s != s:
    print(f"  RELATION_MAP (regex): {s!r} -> {new_s!r}")
    s = new_s
print(f"After RELATION_MAP: {s!r}")

# Step 4: NON_EQUATION_RELATIONS
for k in mrt.NON_EQUATION_RELATIONS:
    new_s = s.replace(k, " ")
    if new_s != s:
        print(f"  NON_EQUATION_RELATIONS: {k!r} -> ' '")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s
print(f"After NON_EQUATION_RELATIONS: {s!r}")

# Step 5: FUNC_MAP
for k, v in mrt.FUNC_MAP.items():
    new_s = re.sub(r"\\" + k + r"(?![a-zA-Z])", v, s)
    if new_s != s:
        print(f"  FUNC_MAP: {k!r} -> {v!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s
print(f"After FUNC_MAP: {s!r}")

# Step 6: GREEK_MAP
for k, v in mrt.GREEK_MAP.items():
    new_s = s.replace(k, v)
    if new_s != s:
        print(f"  GREEK_MAP: {k!r} -> {v!r}")
        print(f"    {s!r} -> {new_s!r}")
        s = new_s
print(f"After GREEK_MAP: {s!r}")

# Step 7: Spacing/punctuation
s = re.sub(r"\\[,;:!>]", " ", s)
s = re.sub(r"\\quad|\\qquad|\\;|\\,|\\!|\\ ", " ", s)
s = s.replace("\\coloneqq", "=").replace("\\coloneq", "=")
s = s.replace("\\vphantom{", "(").replace("\\phantom{", "(")
s = s.replace("\\bigl", "").replace("\\bigr", "")
print(f"After spacing/punctuation: {s!r}")

# Step 8: Remaining unknown commands
leftovers = set(re.findall(r"\\[a-zA-Z]+", s))
if leftovers:
    print(f"  Remaining commands: {leftovers}")
s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s)
s = re.sub(r"\\[a-zA-Z]+", "", s)
print(f"After unknown command removal: {s!r}")

# Step 9: Final brace cleanup
s = s.replace("{", "(").replace("}", ")")
print(f"After brace cleanup: {s!r}")

# Step 10: Subscript/superscript space repair
s = re.sub(r"_\s+([A-Za-z0-9])", r"_\1", s)
s = re.sub(r"\^\s+([A-Za-z0-9])", r"^\1", s)
s = re.sub(r"([A-Za-z0-9])\s+(_[A-Za-z0-9])", r"\1\2", s)
s = re.sub(r"\(\s+", "(", s)
s = re.sub(r"\s+\)", ")", s)
s = re.sub(r"[_^]\s*(?=[,)\]}] )", "", s)
s = re.sub(r"\s+", " ", s).strip()
print(f"Final: {s!r}")
