import sys
import os
import json
import hashlib

sys.path.insert(0, 'scripts')
import vision_comparison_pipeline as vcp

REPO_ROOT = os.path.abspath('.')
VIS_DIR = os.path.join(REPO_ROOT, 'DATASETS', 'vision_comparison')
CROP_DIR = os.path.join(VIS_DIR, 'crop_verification_renders')
BALLOON_DIR = os.path.join(VIS_DIR, 'balloon_renders')
os.makedirs(BALLOON_DIR, exist_ok=True)

# Load visual review audit log for adjudicated border conditions
with open(os.path.join(VIS_DIR, 'visual_review_audit_log.json')) as f:
    audit = json.load(f)

# Build adjudicated border map from audit records
adjudicated_borders = {}
for r in audit['records']:
    cid = r['candidate_id']
    crop_status = r['crop_boundary_fidelity']['status']
    border_expected = crop_status in ('BOUNDARY_TOUCH', 'BOUNDARY_CLIPPED', 'LEAKAGE_NOTED')
    adjudicated_borders[cid] = {
        'crop_status': crop_status,
        'border_expected': border_expected,
        'verdict': r['overall_visual_verdict'],
        'latex': r['declared_reference_latex'],
    }

import cv2

crop_files = sorted(f for f in os.listdir(CROP_DIR) if f.endswith('.png'))

results = []
for fname in crop_files:
    fpath = os.path.join(CROP_DIR, fname)
    img = cv2.imread(fpath)
    if img is None:
        print(f"SKIP (unreadable): {fname}")
        continue

    with open(fpath, 'rb') as fh:
        img_hash = hashlib.sha256(fh.read()).hexdigest()[:16]

    border_info = vcp.detect_border_contamination(img)

    ballooned = vcp.balloon_glyph(img, factor=9)
    balloon_fname = fname.replace('.png', '__BALLOON9x.png')
    balloon_path = os.path.join(BALLOON_DIR, balloon_fname)
    cv2.imwrite(balloon_path, ballooned)

    # Match to adjudicated candidate
    matched = None
    for cid, adj in adjudicated_borders.items():
        if cid in fname:
            matched = adj
            break

    result = {
        'filename': fname,
        'source_path': fpath,
        'image_hash_sha256_16': img_hash,
        'image_shape': list(img.shape),
        'border_detection': {
            'contaminated': border_info['contaminated'],
            'border_contact': border_info['border_contact'],
            'suspected_clipping': border_info['suspected_clipping'],
            'confirmed_information_loss': border_info['confirmed_information_loss'],
            'borders': border_info['borders'],
            'edge_pixel_counts': border_info['edge_pixel_counts'],
            'border_density': border_info['border_density'],
            'overall_density': border_info['overall_density'],
            'bracket_contacts': border_info['bracket_contacts'],
            'unmatched_brackets_at_border': border_info['unmatched_brackets_at_border'],
            'stretched_symbols_at_border': border_info['stretched_symbols_at_border'],
            'has_left_vertical': border_info['has_left_vertical'],
            'has_right_vertical': border_info['has_right_vertical'],
        },
        'balloon': {
            'factor': 9,
            'output_shape': list(ballooned.shape),
            'output_path': balloon_path,
        },
        'adjudicated': matched,
        'border_agreement': None,
    }

    if matched:
        expected = matched['border_expected']
        detected = border_info['contaminated']
        result['border_agreement'] = (expected == detected)

    results.append(result)

output_path = os.path.join(VIS_DIR, 'border_evaluation_results.jsonl')
with open(output_path, 'w') as f:
    for r in results:
        f.write(json.dumps(r) + '\n')

print(f"Processed {len(results)} crops")
print(f"Balloon renders saved to: {BALLOON_DIR}")
print(f"Results saved to: {output_path}")
print()

agreed = [r for r in results if r['border_agreement'] is not None]
print(f"Border agreement (detected vs adjudicated): {sum(1 for r in agreed if r['border_agreement'])}/{len(agreed)}")
for r in agreed:
    status = "AGREE" if r['border_agreement'] else "DISAGREE"
    print(f"  {r['filename']}: detected={r['border_detection']['contaminated']}, expected={r['adjudicated']['border_expected']} -> {status}")

levels = {}
for r in results:
    borders = r['border_detection']['borders']
    key = ','.join(borders) if borders else 'none'
    levels[key] = levels.get(key, 0) + 1
print(f"\nContamination levels: {dict(levels)}")

unique = set()
for r in results:
    base = r['filename'].replace('__ORIGINAL.png','').replace('__CORRECTED.png','').replace('__CURRENT.png','')
    unique.add(base)
print(f"\nUnique crop bases: {len(unique)}")
print(f"Total files processed: {len(results)}")
print(f"Balloon files generated: {len(os.listdir(BALLOON_DIR))}")