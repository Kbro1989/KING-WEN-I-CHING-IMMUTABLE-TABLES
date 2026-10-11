"""Fix RELATION_MAP corruption by rebuilding the exact block."""
import sys

FILE = "scripts/math_recovery_tool.py"

with open(FILE, "rb") as f:
    content = f.read()

start = content.find(b"RELATION_MAP = {")
end = content.find(b"\n# Relations that are NOT equations", start)

if start < 0 or end < 0:
    sys.exit("ERROR: RELATION_MAP block not found")

# Build the correct block as a proper Python string, then encode
# In the source file, each key needs: "backslash + command"
# e.g. "\\rightarrow" as Python source = bytes: 5c 5c 72 69 67 68 74 61 72 72 6f 77
# Wait, no. Python string "\\rightarrow" is ONE backslash + "rightarrow" = 5c 72 69 67 68 74 61 72 72 6f 77
# But in a Python source file, to write ONE backslash we use: "\\" = 5c 5c
# So in the source file: "\\rightarrow" = 5c 5c 72 69 67 68 74 61 72 72 6f 77
# When Python reads this file, it interprets "\\" as one backslash = 5c

# So in the actual file bytes, each key should be: 5c 5c + command_name
# Let's build the block as bytes with correct content

lines = []
lines.append(b"RELATION_MAP = {")
lines.append(b"    # Inequalities: solver-compatible")
lines.append(b'    "' + b"\\" + b'leq": "<=", "' + b"\\" + b'geq": ">=", "' + b"\\" + b'neq": "!=",')
lines.append(b'    "' + b"\\" + b'll": "<", "' + b"\\" + b'gg": ">",')
lines.append(b"    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to '='.")
lines.append(b"    # The solver adapter (solve_recovered) detects these and refuses to solve.")
lines.append(b'    "' + b"\\" + b'approx": "approx", "' + b"\\" + b'equiv": "equiv",')
lines.append(b'    "' + b"\\" + b'sim": "sim", "' + b"\\" + b'simeq": "simeq", "' + b"\\" + b'cong": "cong",')
lines.append(b'    "' + b"\\" + b'propto": "propto",')
lines.append(b'    "' + b"\\" + b'subseteq": "subseteq", "' + b"\\" + b'supseteq": "supseteq",')
lines.append(b'    "' + b"\\" + b'subset": "subset", "' + b"\\" + b'supset": "supset",')
lines.append(b'    "' + b"\\" + b'Relaightarrow": "Rightarrow", "' + b"\\" + b'Lelftarrow": "Leftarrow",')
lines.append(b'    "' + b"\\" + b'Leftrightarrow": "Leftrightarrow",')
lines.append(b'    "' + b"\\" + b'rightleftarrow": "rightarrow", "' + b"\\" + b'leftleftarrow": "leftarrow",')
lines.append(b'    "' + b"\\" + b'mapsto": "mapsto",')
lines.append(b'    "' + b"\\" + b'to": "to", "' + b"\\" + b'gets": "gets",')
lines.append(b'    "' + b"\\" + b'implies": "implies", "' + b"\\" + b'iff": "iff",')
lines.append(b"}")

block = b"\n".join(lines) + b"\n"

content = content[:start] + block + content[end:]

with open(FILE, "wb") as f:
    f.write(content)

print("RELATION_MAP rebuilt with correct escaping")
