import os
os.chdir('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

idx = content.find('def load_candidates')
end = content.find('\n    def ', idx + 50)
if end < 0:
    end = content.find('\n    def ', idx + 100)
print(content[idx:end])
