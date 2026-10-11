"""Fix corrupted RELATION_MAP in math_recovery_tool.py.

The file has a corrupted line: backslash + CR + 'ightarrow' which breaks
Python syntax. This script reads the file in binary mode, replaces the
corrupted RELATION_MAP block with a clean version, and writes it back.
"""
import sys

FILE = 'scripts/math_recovery_tool.py'

with open(FILE, 'rb') as f:
    content = f.read()

# Find the corrupted RELATION_MAP block
start_marker = b'RELATION_MAP = {'
end_marker = b'\n}\n# Relations that are NOT equations'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx < 0 or end_idx < 0:
    print(f"ERROR: Could not find RELATION_MAP block (start={start_idx}, end={end_idx})")
    sys.exit(1)

# Build clean RELATION_MAP block
clean = b'RELATION_MAP = {\n'
clean += b'    # Inequalities: solver-compatible\n'
clean += b'    "\\\\leq": "<=", "\\\\geq": ">=", "\\\\neq": "!=",\n'
clean += b'    "\\\\ll": "<", "\\\\gg": ">",\n'
clean += b'    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to \'=\'.\n'
clean += b'    # The solver adapter (solve_recovered) detects these and refuses to solve.\n'
clean += b'    "\\\\approx": "approx", "\\\\equiv": "equiv",\n'
clean += b'    "\\\\sim": "sim", "\\\\simeq": "simeq", "\\\\cong": "cong",\n'
clean += b'    "\\\\propto": "propto",\n'
clean += b'    "\\\\subseteq": "subseteq", "\\\\supseteq": "supseteq",\n'
clean += b'    "\\\\subset": "subset", "\\\\supset": "supset",\n'
clean += b'    "\\\\Rightarrow": "Rightarrow", "\\\\Leftarrow": "Leftarrow",\n'
clean += b'    "\\\\Leftrightarrow": "Leftrightarrow",\n'
clean += b'    "\\\\rightarrow": "rightarrow", "\\\\leftarrow": "leftarrow",\n'
clean += b'    "\\\\mapsto": "mapsto",\n'
clean += b'    "\\\\to": "to", "\\\\gets": "gets",\n'
clean += b'    "\\\\implies": "implies", "\\\\iff": "iff",\n'
clean += b'}\n'
clean += b'# Relations that are NOT equations'

# Replace
content = content[:start_idx] + clean + content[end_idx + 1:]

with open(FILE, 'wb') as f:
    f.write(content)

print("RELATION_MAP fixed")
