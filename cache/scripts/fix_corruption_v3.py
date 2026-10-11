import sys

with open('scripts/math_recovery_tool.py', 'rb') as f:
    content = f.read()

# Find the corrupted pattern: backslash + CR + "ightarrow"
# The file has a line break inside a string literal due to a bad patch
# We need to find: \r\nightarrow and replace with \\rightarrow
# But the actual bytes might be: \x5c\x0dightarrow or similar

# Let's search for the pattern more carefully
# The corrupted line is: "\\\r\nightarrow": "rightarrow"
# Which in bytes is: 5c 0d 69 67 68 74 61 72 72 6f 77

# Find "ightarrow" and check what's before it
idx = content.find(b'ightarrow')
while idx >= 0:
    # Check if this is the corrupted one (preceded by \r or \n)
    if idx > 0 and content[idx-1:idx] in (b'\r', b'\n'):
        print(f"Found corrupted 'ightarrow' at {idx}, preceded by {repr(content[idx-1:idx])}")
        # Find the start of this line
        line_start = content.rfind(b'\n', 0, idx)
        if line_start < 0:
            line_start = 0
        else:
            line_start += 1
        # Find the end of this line
        line_end = content.find(b'\n', idx)
        if line_end < 0:
            line_end = len(content)
        print(f"Line {line_start}-{line_end}: {repr(content[line_start:line_end])}")
        
        # Replace the entire line with the correct one
        # The correct line should be: "\\\\rightarrow": "rightarrow",
        # But we need to figure out the exact format
        # Looking at the context, it should be:
        #     "\\\\rightarrow": "rightarrow", "\\\\leftarrow": "leftarrow",
        
        # Let's just replace the corrupted line with the correct content
        correct_line = b'    "\\\\rightarrow": "rightarrow", "\\\\leftarrow": "leftarrow",\n'
        content = content[:line_start] + correct_line + content[line_end:]
        print("Fixed!")
        break
    idx = content.find(b'ightarrow', idx + 1)

with open('scripts/math_recovery_tool.py', 'wb') as f:
    f.write(content)

print("Done")
