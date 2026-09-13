#!/usr/bin/env python3
import re, pathlib, collections

root = pathlib.Path('src')
imports = collections.Counter()

for path in root.rglob('*'):
    if not path.is_file():
        continue
    if path.suffix not in {'.ts','.js'}:
        continue
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    for m in re.finditer(r'''from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)''', text):
        spec = m.group(1) or m.group(2)
        if spec and not spec.startswith('.'):
            imports[spec] += 1

print('EXTERNAL IMPORTS FOUND:')
for k,v in sorted(imports.items(), key=lambda x:-x[1]):
    print(f'{v:>3}  {k}')
