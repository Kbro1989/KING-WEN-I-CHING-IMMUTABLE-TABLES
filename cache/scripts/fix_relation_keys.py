"""Fix RELATION_MAP keys using chr(92) to avoid backslash escaping."""
import sys

FILE = "scripts/math_recovery_tool.py"
BS = chr(92)  # single backslash

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the corrupted keys
# Current corrupted: "\\Relarrow" -> should be "\\Rightarrow"
# Current corrupted: "\\rightleftarrow" -> should be "\\rightarrow"
# Current corrupted: "\\leftleftarrow" -> should be "\\leftarrow"

# The issue is that \R, \r, \l, \L are being interpreted as escape sequences
# We need to replace the corrupted keys with correct ones

# Fix \Relarrow -> \Rightarrow
content = content.replace(f'"{BS}{BS}Relarrow"', f'"{BS}{BS}Rightarrow"')

# Fix \rightleftarrow -> \rightarrow  
content = content.replace(f'"{BS}{BS}rightleftarrow"', f'"{BS}{BS}rightarrow"')

# Fix \leftleftarrow -> \leftarrow
content = content.replace(f'"{BS}{BS}leftleftarrow"', f'"{BS}{BS}leftarrow"')

# Also fix any corrupted \r + ightarrow pattern
# The corrupted pattern is: \ + CR + ightarrow
# We need to replace it with: \\rightarrow
content = content.replace(f'"{BS}{BS}\r\nightarrow"', f'"{BS}{BS}rightarrow"')

# Also check for the pattern where \r is a literal carriage return
# In the file, it might be: "\\\r\nightarrow" (backslash + CR + ightarrow)
# Let's find and fix any remaining corruption
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'ightarrow' in line and 'rightarrow' not in line:
        print(f"Found corrupted line {i+1}: {repr(line)}")
        # Replace with correct line
        lines[i] = f'    "{BS}{BS}rightarrow": "rightarrow", "{BS}{BS}leftarrow": "leftarrow",'
        print(f"Fixed to: {repr(lines[i])}")

content = '\n'.join(lines)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed RELATION_MAP keys")
