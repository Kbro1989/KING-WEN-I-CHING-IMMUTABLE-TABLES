#!/usr/bin/env python3
"""Fix broken string literals in adjudicate_targets.py — replace broken Markdown
writer block (lines 204-228) with corrected single-line strings."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')

# Locate the Markdown writer section
start = None
end = None
for i, line in enumerate(lines):
    if line.strip() == b'# Markdown report.':
        start = i
    if start is not None and line.strip().startswith(b'# ---'):
        end = i
        break

if start is None or end is None:
    print('Could not find section')
else:
    new_block = [
        b'    # Markdown report.',
        b'    with open(MD_PATH, "w", encoding="utf-8") as f:',
        b'        f.write("# Targeted Adjudication Report - 1907.04931\\n\\n")',
        b'        f.write("Adjudication layer: deterministic OCR inspection + source-image ")',
        b'        f.write("presence + parser association. No semantic promotion from geometry.\\n\\n")',
        b'        f.write("| Status | Count |\\n|---|---|\\n")',
        b'        for st in (STATUS_ADJUDICATED, STATUS_UNVERIFIED, STATUS_NO_MATCH):',
        b"            f.write(f\"| {st} | {summary['status_distribution'].get(st, 0)} |\\n\")",
        b'        f.write("\\n## Adjudication detail distribution\\n\\n")',
        b'        f.write("| Detail | Count |\\n|---|---|\\n")',
        b'        for d, c in sorted(summary["adjudication_detail_distribution"].items()):',
        b'            f.write(f"| {d} | {c} |\\n")',
    ]
    
    new_lines = lines[:start] + new_block + lines[end:]
    new_content = b'\r\n'.join(new_lines)
    
    with open(path, 'wb') as f:
        f.write(new_content)
    
    print(f'Replaced lines {start+1}-{end} with {len(new_block)} corrected lines')
