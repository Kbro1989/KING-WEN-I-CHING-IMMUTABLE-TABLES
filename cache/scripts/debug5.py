import os
os.chdir('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

idx = content.find('crop = self.crop_pdf_region(')
if idx >= 0:
    print(content[idx:idx+400])
else:
    print('Not found')
