"""Fix RELATION_MAP corruption by rebuilding the exact block with proper escaping."""
import sys

with open('scripts/math_recovery_tool.py', 'rb') as f:
    content = f.read()

# Find the RELATION_MAP block and rebuild it
start = content.find(b'RELATION_MAP = {')
if start < 0:
    print("ERROR: RELATION_MAP not found")
    sys.exit(1)

# Find the end of the dict (the closing } before the comment)
end = content.find(b'\n# Relations that are NOT equations', start)
if end < 0:
    print("ERROR: End not found")
    sys.exit(1)

# Build the correct block
# In Python source, each key like "\\rightarrow" represents the string \rightarrow
# (one backslash + "rightarrow").  In the source file bytes that is:
#   "  \\  r  i  g  h  t  a  r  r  o  w  "
# So the literal bytes for a key are: 5c 72 69 67 68 74 61 72 72 6f 77
block = bytearray()
block += b'RELATION_MAP = {\n'
block += b'    # Inequalities: solver-compatible\n'
block += b'    "' + b'\\leq' + b'": "<=", "' + b'\\geq' + b'": ">=", "' + b'\\neq' + b'": "!=",\n'
block += b'    "' + b'\\ll' + b'": "<", "' + b'\\gg' + b'": ">",\n'
block += b'    # Non-equality relations: PRESERVED as typed tokens, NOT collapsed to \'=\'.\n'
block += b'    # The solver adapter (solve_recovered) detects these and refuses to solve.\n'
block += b'    "' + b'\\approx' + b'": "approx", "' + b'\\equiv' + b'": "equiv",\n'
block += b'    "' + b'\\sim' + b'": "sim", "' + b'\\simeq' + b'": "simeq", "' + b'\\cong' + b'": "cong",\n'
block += b'    "' + b'\\propto' + b'": "propto",\n'
block += b'    "' + b'\\subseteq' + b'": "subseteq", "' + b'\\supseteq' + b'": "supseteq",\n'
block += b'    "' + b'\\subset' + b'": "subset", "' + b'\\supset' + b'": "supset",\n'
block += b'    "' + b'\\Rightarrow' + b'": "Rightarrow", "' + b'\\Leftarrow' + b'": "Leftarrow",\n'
block += b'    "' + b'\\Leftrightarrow' + b'": "Leftrightarrow",\n'
block += b'    "' + b'\\rightarrow' + b'": "rightarrow", "' + b'\\leftarrow' + b'": "leftarrow",\n'
block += b'    "' + b'\\mapsto' + b'": "mapsto",\n'
block += b'    "' + b'\\to' + b'": "to", "' + b'\\gets' + b'": "gets",\n'
block += b'    "' + b'\\implies' + b'": "implies", "' + b'\\iff' + b'": "iff",\n'
block += b'}\n'

# Replace
content = content[:start] + bytes(block) + content[end:]

with open('scripts/math_recovery_tool.py', 'wb') as f:
    f.write(content)

print("RELATION_MAP rebuilt with correct escaping")
