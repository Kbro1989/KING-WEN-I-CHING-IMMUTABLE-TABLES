"""Fix RELATION_MAP corruption by rebuilding the exact block."""
import sys

FILE = "scripts/math_recovery_tool.py"

with open(FILE, "rb") as f:
    content = f.read()

start = content.find(b"RELATION_MAP = {")
end = content.find(b"\n# Relations that are NOT equations", start)

if start < 0 or end < 0:
    sys.exit("ERROR: RELATION_MAP block not found")

# In the source file, each key needs TWO backslash bytes: 5c 5c
# which Python reads as ONE backslash + command name.
BS = bytes([92, 92])  # Two backslash bytes

block_lines = []
block_lines.append(b"RELATION_MAP = {")
block_lines.append(b"    # Inequalities: solver-compatible")
block_lines.append(b'    "' + BS + b'leq": "<=", "' + BS + b'geq": ">=", "' + BS + b'neq": "!=")
block_lines.append(b'    "' + BS + b'll": "<", "' + BS + b'gg": ">",')
block_lines.append(b"    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to '='.")
block_lines.append(b"    # The solver adapter (solve_recovered) detects these and refuses to solve.")
block_lines.append(b'    "' + BS + b'approx": "approx", "' + BS + b'equiv": "equiv",')
block_lines.append(b'    "' + BS + b'sim": "sim", "' + BS + b'simeq": "simeq", "' + BS + b'cong": "cong",')
block_lines.append(b'    "' + BS + b'propto": "propto",')
block_lines.append(b'    "' + BS + b'subseteq": "subseteq", "' + BS + b'supseteq": "supseteq",')
block_lines.append(b'    "' + BS + b'subset": "subset", "' + BS + b'supset": "supset",')
block_lines.append(b'    "' + BS + b'Relaightarrow": "Rightarrow", "' + BS + b'Lelftarrow": "Leftarrow",')
block_lines.append(b'    "' + BS + b'Leftrightarrow": "Leftrightarrow",')
block_lines.append(b'    "' + BS + b'rightleftarrow": "rightarrow", "' + BS + b'leftleftarrow": "leftarrow",')
block_lines.append(b'    "' + BS + b'mapsto": "mapsto",')
block_lines.append(b'    "' + BS + b'to": "to", "' + BS + b'gets": "gets",')
block_lines.append(b'    "' + BS + b'implies": "implies", "' + BS + b'iff": "iff",')
block_lines.append(b"}")

block = b"\n".join(block_lines) + b"\n"

content = content[:start] + block + content[end:]

with open(FILE, "wb") as f:
    f.write(content)

print("RELATION_MAP rebuilt with correct escaping")
