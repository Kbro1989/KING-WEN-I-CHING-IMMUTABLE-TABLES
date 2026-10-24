import re

path = 'scripts/vision_comparison_pipeline.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

old_signature = 'def crop_pdf_region(self, pdf_path: Path, bbox: dict, padding: int = 2, page_num: int = 0, zoom: int = 4, min_content_ratio: float = 0.02) -> np.ndarray | None:'
new_signature = 'def crop_pdf_region(self, pdf_path: Path, bbox: dict, padding: int | tuple[int, int] = (3, 2), page_num: int = 0, zoom: int = 4, min_content_ratio: float = 0.02) -> np.ndarray | None:'

old_rect = """        doc = fitz.open(str(pdf_path))
        page = doc[page_num]  # use specified page
        rect = fitz.Rect(bbox['x0'] - padding, bbox['y0'] - padding,
                        bbox['x1'] + padding, bbox['y1'] + padding)"""

new_rect = """        if isinstance(padding, (tuple, list)):
            pad_x, pad_y = padding[0], padding[1]
        else:
            pad_x, pad_y = padding, padding

        doc = fitz.open(str(pdf_path))
        page = doc[page_num]  # use specified page
        rect = fitz.Rect(bbox['x0'] - pad_x, bbox['y0'] - pad_y,
                        bbox['x1'] + pad_x, bbox['y1'] + pad_y)"""

old_call = 'crop = self.crop_pdf_region(source_path, bbox, padding=15, page_num=max(0, candidate.get("page", 0) - 1))'
new_call = 'crop = self.crop_pdf_region(source_path, bbox, padding=(3, 2), page_num=max(0, candidate.get("page", 0) - 1))'

assert old_signature in text, 'old_signature not found'
assert old_rect in text, 'old_rect not found'
assert old_call in text, 'old_call not found'

text = text.replace(old_signature, new_signature, 1)
text = text.replace(old_rect, new_rect, 1)
text = text.replace(old_call, new_call, 1)

with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(text)

print('Successfully patched scripts/vision_comparison_pipeline.py')
