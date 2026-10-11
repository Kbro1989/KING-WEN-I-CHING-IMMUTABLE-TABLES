import sys

with open('scripts/math_recovery_tool.py', 'rb') as f:
    content = f.read()

# The corruption is a literal backslash + CR + "ightarrow" in RELATION_MAP
# Find and fix it
# Pattern: b'    "\\\\\x0dightarrow"' -> b'    "\\\\rightarrow"'
# But let's be more precise - find the corrupted bytes

# The corrupted sequence is: backslash, CR, "ightarrow"
# In the file it appears as: \\\r\nightarrow
# We need to replace \\\r\nightarrow with \\rightarrow

# Actually, let's just find the exact corrupted bytes
corrupted = b'\\\x0dightarrow'
if corrupted in content:
    print(f"Found corrupted bytes at position {content.find(corrupted)}")
    # Replace with \\rightarrow
    content = content.replace(corrupted, b'\\\\rightarrow')
    with open('scripts/math_recovery_tool.py', 'wb') as f:
        f.write(content)
    print("Fixed corrupted bytes")
else:
    print("Corrupted pattern not found")
    # Try to find what's there
    idx = content.find(b'ightarrow')
    if idx >= 0:
        print(f"Found 'ightarrow' at {idx}")
        print(f"Context: {repr(content[idx-20:idx+20])}")
