import sys
sys.path.insert(0, r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\references')
import numpy as np
import non_subscription_evaluator as ns

evaluator = ns.NonSubscriptionEvaluator(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols')
print(f'reference_glyphs count: {len(evaluator.reference_glyphs)}')

test_files = ['0.gif', 'bfcb.gif', 'blacksquare.gif', 'sum.gif', 'ell.gif', '1.gif', 'sigma.gif']
for crop_name in test_files:
    img = ns.Image.open(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS\math_symbols\images\' + crop_name)
    arr = np.array(img.convert('L'))
    crop = (arr < 128).astype(np.float32)
    
    matches = evaluator.match_crop(crop)
    print(f'{crop_name}.gif: {len(matches)} matches')
    for name, score in matches[:3]:
        ref = evaluator.reference_glyphs[name]
        print(f'  {name}: score={score:.4f}, shape={ref.shape}, nonzero={np.count_nonzero(ref)}, density={np.count_nonzero(ref)/ref.size*100:.1f}%')
