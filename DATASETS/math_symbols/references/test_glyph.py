import sys
sys.path.insert(0, '.')
import numpy as np
from PIL import Image

# Test with absolute Windows path
path = r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\images\0.gif'
print(f'Path: {path}')
print(f'Exists: {__import__("os").path.exists(path)}')

img = Image.open(path).convert('L')
print(f'Image mode: {img.mode}, size: {img.size}')

arr = np.array(img)
print(f'arr shape: {arr.shape}, dtype: {arr.dtype}')
print(f'arr min: {arr.min()}, max: {arr.max()}, mean: {arr.mean():.1f}')
print(f'Unique values: {np.unique(arr)[:20]}')

binary = (arr < 128).astype(np.float32)
print(f'binary sum: {binary.sum()}, nonzero: {np.count_nonzero(binary)}')

# Compare with original
img2 = Image.open(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\images\0.gif')
arr2 = np.array(img2.convert('L'))
print(f'arr2 min: {arr2.min()}, max: {arr2.max()}, mean: {arr2.mean():.1f}')
print(f'arr2 binary sum: {np.count_nonzero(arr2 < 128)}')
