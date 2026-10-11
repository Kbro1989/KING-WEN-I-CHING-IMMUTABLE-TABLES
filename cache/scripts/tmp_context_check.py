import sys
sys.path.insert(0, 'scripts')
from bs4 import BeautifulSoup
import re

with open('DATASETS/Wasserstein Distributionally Robust Regret Optimization for Reinforcement Learning from Human Feedback.html', encoding='utf-8', errors='replace') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
math_tags = soup.find_all('math')

print(f"Total math tags: {len(math_tags)}")
print()

# Show context around first 30 math tags
for i, math_tag in enumerate(math_tags[:30]):
    annotation = math_tag.find('annotation')
    latex = annotation.text.strip() if annotation else "N/A"
    
    # Get parent paragraph
    parent = math_tag.find_parent(['p', 'div'])
    if parent:
        text = parent.get_text(strip=True)
        # Find a simplified version of the latex in the text
        simple = latex.replace('\\', '').replace('{', '').replace('}', '').replace(' ', '')
        math_pos = text.find(simple)
        if math_pos >= 0:
            start = max(0, math_pos - 150)
            end = min(len(text), math_pos + len(simple) + 150)
            context = text[start:end]
        else:
            context = text[:400]
        print(f"--- Math {i+1}: {latex[:60]} ---")
        print(f"Context: {context[:400]}")
        print()
