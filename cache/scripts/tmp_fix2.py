import sys
with open('scripts/math_recovery_tool.py', 'rb') as f:
    content = f.read()

# Find the corrupted comment block and replace it
# The block starts with "    #     # Sort by key length" and ends before "    for k, v in sorted"
start_marker = b'    #     # Sort by key length'
end_marker = b'    for k, v in sorted(RELATION_MAP.items()'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx >= 0 and end_idx >= 0:
    clean_block = b'''    # Sort by key length (longest first) to prevent substring conflicts:
    # e.g. backslash-Rightarrow must be fully replaced before backslash-rightarrow
    # can match inside the already-replaced text.
'''
    content = content[:start_idx] + clean_block + content[end_idx:]
    
    with open('scripts/math_recovery_tool.py', 'wb') as f:
        f.write(content)
    print("Fixed")
else:
    print(f"start_idx={start_idx}, end_idx={end_idx}")
