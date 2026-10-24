import os
import json
from pathlib import Path

os.chdir(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py') as f:
    content = f.read()

# Find PDF_DIR definition
idx = content.find('PDF_DIR =')
if idx >= 0:
    print('PDF_DIR definition:', content[idx:idx+200])
    
# Find where PDF_DIR is used
print('---')
idx = content.find('PDF_DIR')
count = 0
while idx >= 0 and count < 5:
    print(content[max(0,idx-20):idx+50].replace('\r',' '))
    idx = content.find('PDF_DIR', idx+1)
    count += 1
