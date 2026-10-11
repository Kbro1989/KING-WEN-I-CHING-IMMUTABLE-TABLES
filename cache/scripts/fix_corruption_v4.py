import sys

with open('scripts/math_recovery_tool.py', 'rb') as f:
    content = f.read()

# Find the problematic line (line 299) and replace it with correct content
# The issue is that the line has \\rightarrow which is 2 backslashes
# We need \\rightarrow which is 1 backslash

# Find line 299
lines = content.split(b'\n')
for i, line in enumerate(lines):
    if b'\\rightarrow' in line and b'\\leftarrow' in line:
        print(f"Found at line {i+1}: {repr(line)}")
        # Replace with correct line: single backslash before rightarrow
        # In the source file, it should be: "\\rightarrow" (one backslash)
        # But in bytes, that's: 5c 5c 72 69 67 68 74 61 72 72 6f 77
        # Wait, no. In Python source: "\\rightarrow" = 5c + rightarrow
        # In bytes: 5c 72 69 67 68 74 61 72 72 6f 77
        # But the current line has: 5c 5c 72 69 67 68 74 61 72 72 6f 77 (two backslashes)
        
        # The correct line should be: "\\\\rightarrow" (two backslashes in source)
        # because that's a Python string literal representing one backslash + rightarrow
        
        # Let's just write the correct line directly
        correct_line = b'    "\\\\rightarrow": "rightarrow", "\\\\leftarrow": "leftarrow",'
        lines[i] = correct_line
        print(f"Replaced with: {repr(correct_line)}")
        break

content = b'\n'.join(lines)

with open('scripts/math_recovery_tool.py', 'wb') as f:
    f.write(content)

print("Done")
