#!/usr/bin/env python3
"""Fix broken multi-line string literals in adjudicate_targets.py.

The file has patterns like:
    f.write("string content
")
which should be:
    f.write("string content\\n")

Each broken pattern has: f.write("...> at end of line, empty next line,
then closing ")". We need to join them into single-line strings.
"""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
fixed = 0

# Pattern to detect: f.write("... at end of line, empty line, then ")"
# We'll process the Markdown writer section
# Find the start: '# Markdown report.' and end: '# ---' separator

start = None
end = None
for i, line in enumerate(lines):
    if line.strip() == '# Markdown report.':
        start = i
    if start is not None and line.strip().startswith(b'# ---'):
        end = i
        break

if start is None or end is None:
    print('Could not find Markdown writer section')
else:
    # Build the corrected block
    new_block = [
        '    # Markdown report.',
        '    with open(MD_PATH, "w", encoding="utf-8") as f:',
        '        f.write("# Targeted Adjudication Report - 1907.04931\\n\\n")',
        '        f.write("Adjudication layer: deterministic OCR inspection + source-image ")',
        '        f.write("presence + parser association. No semantic promotion from geometry.\\n\\n")',
        '        f.write("| Status | Count |\\n|---|---|\\n")',
        '        for st in (STATUS_ADJUDICATED, STATUS_UNVERIFIED, STATUS_NO_MATCH):',
        "            f.write(f\"| {st} | {summary['status_distribution'].get(st, 0)} |\\n\")",
        '        f.write("\\n## Adjudication detail distribution\\n\\n")',
        '        f.write("| Detail | Count |\\n|---|---|\\n")',
        '        for d, c in sorted(summary["adjudication_detail_distribution"].items()):',
        '            f.write(f"| {d} | {c} |\\n")',
    ]
    
    # Replace lines[start:end] with new_block
    new_lines = lines[:start] + new_block + lines[end:]
    
    new_content = b'\r\n'.join(new_lines)
    with open(path, 'wb') as f:
        f.write(new_content)
    
    print(f'Replaced lines {start+1}-{end-1} with corrected Markdown writer ({len(new_block)} lines)')
