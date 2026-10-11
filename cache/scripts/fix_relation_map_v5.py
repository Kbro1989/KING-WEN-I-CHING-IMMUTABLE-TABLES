"""Fix RELATION_MAP corruption by rebuilding the exact block.

The issue: each key in the source file needs to be a Python string literal
with TWO backslashes (e.g. "\\rightarrow") which Python reads as ONE
backslash + "rightarrow". The previous fixes produced incorrect byte counts.

In the output file bytes:
- Key: "\\\\rightarrow" = 22 5c 5c 72 69 67 68 74 61 72 72 6f 77 22
- When Python reads this file, it interprets "\\\\" as one backslash (5c)
- So the string value becomes: \rightarrow (5c 72 69 67 68 74 61 72 72 6f 77)
"""
import sys

FILE = "scripts/math_recovery_tool.py"

with open(FILE, "rb") as f:
    content = f.read()

start = content.find(b"RELATION_MAP = {")
end = content.find(b"\n# Relations that are NOT equations", start)

if start < 0 or end < 0:
    sys.exit("ERROR: RELATION_MAP block not found")

# Build each line as bytes
# Each key needs: "\\\\command" in the file = 5c 5c + command_name
# In Python bytes: b"\\\\" produces 5c 5c (two backslashes)

block_lines = []
block_lines.append(b"RELATION_MAP = {")
block_lines.append(b"    # Inequalities: solver-compatible")
block_lines.append(b'    "' + b"\\\\" + b'leq": "<=", "' + b"\\\\" + b'geq": ">=", "' + b"\\\\" + b'neq": "!=")
block_lines.append(b'    "' + b"\\\\" + b'll": "<", "' + b"\\\\" + b'gg": ">",')
block_lines.append(b"    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to '='.")
block_lines.append(b"    # The solver adapter (solve_recovered) detects these and refuses to solve.")
block_lines.append(b'    "' + b"\\\\" + b'approx": "approx", "' + b"\\\\" + b'equiv": "equiv",')
block_lines.append(b'    "' + b"\\\\" + b'sim": "sim", "' + b"\\\\" + b'simeq": "simeq", "' + b"\\\\" + b'cong": "cong",')
block_lines.append(b'    "' + b"\\\\" + b'propto": "propto",')
block_lines.append(b'    "' + b"\\\\" + b'subseteq": "subseteq", "' + b"\\\\" + b'supseteq": "supseteq",')
block_lines.append(b'    "' + b"\\\\" + b'subset": "subset", "' + b"\\\\" + b'supset": "supset",')
block_lines.append(b'    "' + b"\\\\" + b'Relaightarrow": "Rightarrow", "' + b"\\\\" + b'Lelftarrow": "Leftarrow",')
block_lines.append(b'    "' + b"\\\\" + b'Leftrightarrow": "Leftrightarrow",')
block_lines.append(b'    "' + b"\\\\" + b'rightleftarrow": "rightarrow", "' + b"\\\\" + b'leftleftarrow": "leftarrow",')
block_lines.append(b'    "' + b"\\\\" + b'mapsto": "mapsto",')
block_lines.append(b'    "' + b"\\\\" + b'to": "to", "' + b"\\\\" + b'gets": "gets",')
block_lines.append(b'    "' + b"\\\\" + b'implies": "implies", "' + b"\\\\" + b'iff": "iff",')
block_lines.append(b"}")

block = b"\n".join(block_lines) + b"\n"

content = content[:start] + block + content[end:]

with open(FILE, "wb") as f:
    f.write(content)

print("RELATION_MAP rebuilt with correct escaping")
