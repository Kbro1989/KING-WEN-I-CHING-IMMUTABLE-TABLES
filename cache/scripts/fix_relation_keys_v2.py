"""Fix RELATION_MAP corruption by removing the split line and restoring \\Rightarrow."""
import sys

FILE = "scripts/math_recovery_tool.py"
BS = chr(92)

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# The corruption: line 298 ends with a single backslash, line 299 starts with "ightarrow"
# This was originally: "\\Rightarrow": "Rightarrow", "\\Leftarrow": "Leftarrow",
# We need to merge these two lines back into the correct entry

# Find and fix the corrupted pattern
# The corrupted pattern is: '\\\n' followed by 'ightarrow'
# We need to replace it with: '\\Rightarrow": "Rightarrow", "\\Leftarrow": "Leftarrow",\n'

# First, let's find the exact corrupted bytes
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip() == BS or line.strip() == BS + BS:
        # This is the corrupted line (just a backslash)
        print(f"Found corrupted line {i+1}: {repr(line)}")
        # The next line should be 'ightarrow...'
        if i + 1 < len(lines) and lines[i+1].strip().startswith('ightarrow'):
            print(f"Next line {i+2}: {repr(lines[i+1])}")
            # Merge them into the correct entry
            # The correct entry is: "\\Rightarrow": "Rightarrow", "\\Leftarrow": "Leftarrow",
            lines[i] = f'    "{BS}{BS}Rightarrow": "Rightarrow", "{BS}{BS}Leftarrow": "Leftarrow",'
            # Remove the next line (the ightarrow fragment)
            del lines[i+1]
            print(f"Fixed: merged into {repr(lines[i])}")
            break

content = '\n'.join(lines)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
