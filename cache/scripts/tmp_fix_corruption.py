import sys
with open('scripts/math_recovery_tool.py', 'rb') as f:
    content = f.read()

# The corrupted pattern: a literal backslash + CR followed by "ightarrow"
# We need to find and fix this. Let's look for the pattern.
corrupted = b'ightarrow'
idx = content.find(corrupted)
if idx >= 0:
    # Find the start of this line
    start = content.rfind(b'\n', 0, idx)
    # Find the end of this line
    end = content.find(b'\n', idx)
    print(f"Found corrupted line at byte {idx}")
    print(f"Context: {repr(content[max(0,idx-30):idx+30])}")
    
    # The fix: replace the corrupted line with a clean comment
    # First, find the full comment block to replace
    # Look for the "Sort by key length" comment start
    sort_idx = content.find(b'Sort by key length')
    if sort_idx >= 0:
        # Find the end of the comment block (next line that's not a comment)
        line_end = content.find(b'\n', sort_idx)
        while line_end >= 0:
            next_line = content[line_end+1:line_end+5]
            if next_line.startswith(b'    #'):
                line_end = content.find(b'\n', line_end + 1)
            else:
                break
        
        # Replace the entire comment block
        clean_comment = b'''    # Sort by key length (longest first) to prevent substring conflicts:
    # e.g. backslash-Rightarrow must be fully replaced before backslash-rightarrow
    # can match inside the already-replaced text.
'''
        content = content[:sort_idx] + clean_comment + content[line_end+1:]
        
        with open('scripts/math_recovery_tool.py', 'wb') as f:
            f.write(content)
        print("Fixed corrupted comment")
    else:
        print("Could not find sort_idx")
else:
    print("No corruption found")
