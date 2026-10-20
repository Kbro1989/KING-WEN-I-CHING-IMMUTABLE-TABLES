import os
os.chdir('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

# Find the def crop_pdf_region
idx = content.find('def crop_pdf_region')
if idx >= 0:
    end = content.find('\n    def ', idx + 50)
    if end < 0:
        end = content.find('\n    def ', idx + 100)
    print(content[idx:end])
else:
    print('Not found')
