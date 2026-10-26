#!/usr/bin/env python3
"""Recompute the hex of line 176 and report breakdown."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
line = lines[175]
print('Line length:', len(line))
print('Line hex:', line.hex(' '))
print('Repr:', repr(line))

# Count specific bytes
print('Count of 0x5C (backslash):', raw.count(b'\x5c'))
print('Count of 0x6E (n):', raw.count(b'\x6e'))
print('Count of 0x0A (LF):', raw.count(b'\x0a'))
print('Count of 0x0D (CR):', raw.count(b'\x0d'))
