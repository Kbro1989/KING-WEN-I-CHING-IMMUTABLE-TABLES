import sys
sys.path.insert(0, '.')
import numpy as np
from PIL import Image

# Test load_reference_glyph
img_path = r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\images\0.gif'
print(f'Test path: {img_path}')
print(f'Exists: {__import__("os").path.exists(img_path)}')

img = Image.open(img_path).convert('L')
print(f'Image mode: {img.mode}, size: {img.size}')

arr = np.array(img)
print(f'arr shape: {arr.shape}, dtype: {arr.dtype}, min: {arr.min()}, max: {arr.max()}')
binary = (arr < 128).astype(np.float32)
print(f'binary sum: {binary.sum()}, nonzero: {np.count_nonzero(binary)}')
