#!/usr/bin/env python3
"""Comprehensive fix for adjudicate_targets.py broken string literals."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
fixed = 0

for i, line in enumerate(lines):
    # Fix 1: literal LF inside string literals
    # Pattern: f.write("..." followed by empty line then ")"
    # The broken line has 0x0a (LF) at position after opening quote
    if b'\x0a' in line:
        # Check if the LF is inside what should be a string literal
        # i.e., looking for pattern: + "<LF>
        idx = line.find(b'\x0a')
        if idx > 0:
            # Check if the line starts with a string content (like "+ " or "f.write("
            # If the LF is after a quote and before end of line
            before_lf = line[:idx]
            after_lf = line[idx+1:]
            # Check if there's a matching closing quote
            quote_pos = before_lf.rfind(b'"')
            if quote_pos > 0 and idx < len(line) - 1:
                # Replace the literal LF with escape
                new_line = before_lf + b'"' + b'\\n' + after_lf
                if line != new_line:
                    lines[i] = new_line
                    fixed += 1
                    print(f'  line {i+1}: replaced LF with \\n escape')

    # Fix 2: multi-byte UTF-8 em-dash in strings
    if b'\xe2\x80\x94' in line:
        print(f'  line {i+1}: replacing em-dash bytes')
        line = line.replace(b'\xe2\x80\x94', b'-')
        lines[i] = line
        fixed += 1

new_content = b'\r\n'.join(lines)

with open(path, 'wb') as f:
    f.write(new_content)

print(f'Total fixed: {fixed}')
