#!/usr/bin/env python3
"""Fix all broken multi-line string literals in adjudicate_targets.py.

Pattern: f.write("content<real LF>") which is invalid.
Solution: f.write("content\\n")
"""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
fixed = 0

# Process all lines, looking for broken strings
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line is part of a broken string:
    # - starts with f.write(" or f.write(f"
    # - has an odd number of quotes (unclosed string)
    # - the next line is empty
    # - the line after that is ")"
    
    if b'"' in line:
        first_quote = line.find(b'"')
        last_quote = line.rfind(b'"')
        
        # Count quotes - if odd, the string is unclosed
        # But some lines have escaped quotes like f\"| which complicates
        # Simpler approach: check if the line looks like it starts or continues a string
        if line.strip().startswith(b'f.write('):
            # Count quotes - for f.write("...") the quotes should be even
            quote_count = line.count(b'"')
            if quote_count % 2 == 1:
                # Unclosed string - need to join with next lines
                # Look at next 2-3 lines
                context = lines[i:i+3]
                print(f'  line {i+1}: UNCLOSED string - skip, context differs')
                i += 1
                continue
        
        # Check if this line ends with a quote (or starts one) and next line continues
        if last_quote < len(line) - 1 and line[-1] != b'"'[-1] if False else False:
            pass
    
    i += 1

# Simpler approach: rebuild the Markdown writer section
# Identify the broken section and replace with correct content
# Locate the section: from '# Markdown report.' to '# ---' separator
start = None
end = None
for i, line in enumerate(lines):
    if line.strip() == '# Markdown report.':
        start = i
    if start is not None and line.strip().startswith('# ---'):
        end = i
        break

if start is not None and end is not None:
    # Build the correct Markdown writer section
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
    print(f'Replaced Markdown writer section at lines {start+1}-{end}')
    fixed = len(new_block)
else:
    fixed = 0
    print('Could not find Markdown writer section')

print(f'Total string blocks fixed: {fixed}')
