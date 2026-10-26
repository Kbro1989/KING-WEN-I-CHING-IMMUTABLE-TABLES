#!/usr/bin/env python3
"""Fix broken multi-line strings in adjudicate_targets.py Markdown writer."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

lines = raw.split(b'\r\n')
fixed = 0

# The broken pattern: string opens with " on a line but never closes,
# then next line is empty, then next line is ")"
# We need to join these into single-line strings with \n escapes

i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line ends with an unclosed string (starts with f.write(" but no closing ")
    # i.e., the line contains a " but no closing " after the first one
    if b'"' in line:
        first_quote = line.find(b'"')
        # Find the last quote on this line
        last_quote = line.rfind(b'"')
        if first_quote < last_quote:
            # There's at least one complete quoted pair
            # Check if the string is still unclosed (odd number of quotes)
            quote_count = line.count(b'"')
            if quote_count % 2 == 1:
                # Odd number of quotes = unclosed string
                # Check if next line is empty or continuation
                if i + 1 < len(lines) and lines[i+1].strip() == '':
                    # The next line is empty, and then next line is ")"
                    # This is the broken pattern: string opens on this line,
                    # closes on the line after next
                    # Join the content with \n escape
                    next_line = lines[i+1]
                    next_next = lines[i+2] if i+2 < len(lines) else ''
                    
                    if next_next.startswith(b'"') and next_next.endswith(b'")'):
                        # Line i+2 is a closing paren string
                        # Replace i, i+1, i+2 with a single fixed line
                        # Keep the content, add \n escape
                        content = line  # the content before the quote
                        # Actually, we need to reconstruct:
                        # f.write("<content>\n")
                        before_close = content  # the part after opening "
                        # next_next contains the closing part
                        closing = next_next  # like b'")'
                        # Replace three lines with one
                        lines[i] = b'        f.write("' + content + b'\\n"'
                        del lines[i+1]  # remove empty line
                        del lines[i+2]  # remove closing paren line
                        fixed += 1
                        print(f'  fixed lines {i+1}-{i+2}: joined strings')
                        continue  # recheck this position after modification
    i += 1

new_content = b'\r\n'.join(lines)
with open(path, 'wb') as f:
    f.write(new_content)

print(f'Fixed {fixed} broken string(s)')
