# Fix the vision_comparison_pipeline.py
with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

# Find the broken section
idx = content.find("source_path = REPO_ROOT")
if idx >= 0:
    print("Found index:", idx)
    print(content[idx:idx+300])
