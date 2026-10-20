#!/usr/bin/env python3
# Fix the vision_comparison_pipeline.py file

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

# Find the position of the broken code
idx = content.find('source_path = pdf_path')
if idx == -1:
    print("No broken code found")
else:
    print(f"Found at {idx}")
    # Print surrounding context
    print(content[idx:idx+300])

print("File length:", len(content))
