"""Fix RELATION_MAP corruption by rebuilding the exact block with proper escaping."""
import sys

FILE = "scripts/math_recovery_tool.py"

with open(FILE, "rb") as f:
    content = f.read()

start = content.find(b"RELATION_MAP = {")
end = content.find(b"\n# Relations that are NOT equations", start)

if start < 0 or end < 0:
    sys.exit("ERROR: RELATION_MAP block not found")

# Each key in the source file is a Python string literal with a single
# backslash: e.g. "\\rightarrow" (source) == \rightarrow (value).
block = b"RELATION_MAP = {\n"
block += b"    # Inequalities: solver-compatible\n"
block += b'    "' + b"\\leq" + b'": "<=", "' + b"\\geq" + b'": ">=", "' + b"\\neq" + b'": "!=",\n'
block += b'    "' + b"\\ll" + b'": "<", "' + b"\\gg" + b'": ">",\n'
block += b"    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to '='.\n"
block += b"    # The solver adapter (solve_recovered) detects these and refuses to solve.\n"
block += b'    "' + b"\\approx" + b'": "approx", "' + b"\\equiv" + b'": "equiv",\n'
block += b'    "' + b"\\sim" + b'": "sim", "' + b"\\simeq" + b'": "simeq", "' + b"\\cong" + b'": "cong",\n'
block += b'    "' + b"\\propto" + b'": "propto",\n'
block += b'    "' + b"\\subseteq" + b'": "subseteq", "' + b"\\supseteq" + b'": "supseteq",\n'
block += b'    "' + b"\\subset" + b'": "subset", "' + b"\\supset" + b'": "supset",\n'
block += b'    "' + b"\\Rightarrow" + b'": "Rightarrow", "' + b"\\Leftarrow" + b'": "Leftarrow",\n'
block += b'    "' + b"\\Leftrightarrow" + b'": "Leftrightarrow",\n'
block += b'    "' + b"\\rightarrow" + b'": "rightarrow", "' + b"\\leftarrow" + b'": "leftarrow",\n'
block += b'    "' + b"\\mapsto" + b'": "mapsto",\n'
block += b'    "' + b"\\to" + b'": "to", "' + b"\\gets" + b'": "gets",\n'
block += b'    "' + b"\\implies" + b'": "implies", "' + b"\\iff" + b'": "iff",\n'
block += b"}\n"

content = content[:start] + block + content[end:]

with open(FILE, "wb") as f:
    f.write(content)

print("RELATION_MAP rebuilt with correct escaping")
