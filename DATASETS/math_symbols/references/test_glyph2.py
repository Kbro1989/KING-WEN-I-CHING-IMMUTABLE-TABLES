import sys
sys.path.insert(0, r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\references')
import numpy as np
import non_subscription_evaluator as ns

for fname in ['0.gif', 'bfcb.gif', 'blacksquare.gif', 'rma.gif', 'sum.gif', 'ell.gif', '1.gif', 'sigma.gif']:
    img_path = r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\images\' + fname
    print(f'  Testing {fname}...')
    arr = ns.load_reference_glyph(img_path)
    if arr is not None:
        print(f'  {fname}: shape={arr.shape}, sum={arr.sum()}, nonzero={np.count_nonzero(arr)}, density={np.count_nonzero(arr)/arr.size*100:.1f}%')
    else:
        print(f'  {fname}: NOT FOUND')
