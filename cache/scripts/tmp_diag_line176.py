#!/usr/bin/env python3
"""Diagnose the broken line in adjudicate_targets.py."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

idx = 175  # 0-indexed line 176
line = raw.split(b'\r\n')[idx]
print('Line bytes:', line)
print('Length:', len(line))
print('Backslash count:', line.count(b'\\'))
print('n count:', line.count(b'n'))

start = line.find(b'+')
end = line.find(b')', start)
print('Portion between + and ):')
print(line[start:end])
