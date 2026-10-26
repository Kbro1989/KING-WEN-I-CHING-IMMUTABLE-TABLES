#!/usr/bin/env python3
"""Fix all broken string literals in the Markdown writer section of adjudicate_targets.py."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
fixed = 0
for i, line in enumerate(lines):
    # Fix pattern: string that contains 0x0a (LF) instead of escape \n
    # Pattern: ends with '"' then 0x0a then ')' on next line
    if b'\x0a' in line and b'"' in line:
        # Check if this is a broken string (starts with f.write(" and has LF in quotes)
        idx_open = line.find(b'"')
        idx_close = line.find(b'"', idx_open + 1)
        if idx_open > 0 and idx_open < idx_close:
            # Check if there's a literal newline inside
            content = line[idx_open:idx_close]
            if b'\x0a' in content:
                print(f'  line {i+1}: replacing literal LF with \\n escape')
                # Replace the content between quotes with escaped version
                before = line[:idx_open]
                after = line[idx_close+1:]
                # The content between the quotes has the literal newline
                content = line[idx_open+1:idx_close]
                # Find the LF and replace it
                if b'\x0a' in content:
                    content = content.replace(b'\x0a', b'\\n')
                lines[i] = before + b'"' + content + b'")'
                fixed += 1
                continue

    # Fix multi-byte UTF-8 em-dash in string
    if b'\xe2\x80\x94' in line:
        print(f'  line {i+1}: replacing em-dash bytes')
        line = line.replace(b'\xe2\x80\x94', b'-')
        lines[i] = line
        fixed += 1

new_content = b'\r\n'.join(lines)

with open(path, 'wb') as f:
    f.write(new_content)

print(f'Fixed {fixed} line(s)')
