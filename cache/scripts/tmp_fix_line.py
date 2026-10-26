#!/usr/bin/env python3
"""Fix line 176 of adjudicate_targets.py: replace literal LF with escape sequence."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')

# Line 176 (0-indexed 175) should contain the escape sequence \n (0x5c 0x6e),
# not a literal newline (0x0a).
target = lines[175]
target_fixed = target.replace(b'\x0a', b'\\n')
print('Before:', target.hex(' '))
print('After:  ', target_fixed.hex(' '))

# Replace
lines[175] = target_fixed

# Verify the fix by recomputing
new_line = lines[175]
print('Fixed hex:', new_line.hex(' '))
print('Fixed repr:', repr(new_line))

# Remove the trailing empty line if it exists (line 177 in 1-indexed)
if len(lines) > 176 and lines[176] == b'':
    lines = lines[:176]  # remove the empty trailing element at index 176

new_content = b'\r\n'.join(lines)

with open(path, 'wb') as f:
    f.write(new_content)

print('File rewritten successfully')
