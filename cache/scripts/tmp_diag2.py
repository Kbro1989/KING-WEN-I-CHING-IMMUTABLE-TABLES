#!/usr/bin/env python3
"""Diagnostic: read line 176 (0-indexed 175) of adjudicate_targets.py and show hex."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
line = lines[175]
print('Length:', len(line))
print('Line as repr:', repr(line))
print('Hex:', line.hex(' '))
print('Backslash count:', line.count(b'\\'))
print('n count:', line.count(b'n'))

# Also show what the surrounding lines look like
start = max(0, 172)
end = min(len(lines), 180)
for i in range(start, end):
    print(f'line {i+1}: {lines[i]!r}')
