import os
os.chdir('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

# Find the source_path assignment
idx = content.find('source_path = PDF_DIR / f\"{paper}.pdf\"')
if idx >= 0:
    end = content.find('print(\'Source not found:\', source_path)', idx)
    if end < 0:
        end = content.find('logger.warning', idx)
    print(content[idx:end])
else:
    print('Not found - searching for source_path')
    idx = content.find('source_path')
    print(content[idx-50:idx+200])
