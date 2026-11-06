"""Catalog Audit (P0) — Audit the 3,304-entry glyph catalog for P0/P1 readiness.

Implements the P0 milestone from the external assessment:
- Load and audit every catalog image
- Establish what the catalog actually contains
- Identify unique vs. duplicate glyphs
- Check image consistency and rendering conventions
- Report findings for template-matching readiness

Usage:
    python scripts/audit_glyph_catalog.py
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / 'DATASETS' / 'unified_manifest.json'
SYMBOLS_DIR = REPO_ROOT / 'symbols' / 'symbols'
OUTPUT_DIR = REPO_ROOT / 'DATASETS' / 'vision_comparison'


def load_catalog():
    """Load the glyph catalog from unified_manifest.json."""
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    catalog = manifest.get('symbols_zip_catalog', {}).get('catalog', [])
    return catalog


def compute_image_hash(img):
    """Compute a perceptual hash for an image (for duplicate detection)."""
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    # Resize to fixed size for comparison
    resized = cv2.resize(gray, (16, 16), interpolation=cv2.INTER_AREA)
    # Binary threshold
    _, binary = cv2.threshold(resized, 128, 255, cv2.THRESH_BINARY)
    # Flatten to tuple for hashing
    return hash(binary.tobytes())


def audit_catalog():
    """Run P0 audit on the glyph catalog."""
    catalog = load_catalog()
    print(f"Catalog entries: {len(catalog)}")

    # Track per-entry stats
    unique_names = set()
    name_counts = Counter()
    size_counts = Counter()
    format_counts = Counter()
    load_failures = []
    image_hashes = defaultdict(list)  # hash -> list of (index, name, filename)
    unique_images = 0
    duplicate_images = 0

    for entry in catalog:
        idx = entry.get('index', -1)
        name = entry.get('name', '')
        zip_file = entry.get('zip_file', '')
        img_path = SYMBOLS_DIR / zip_file

        unique_names.add(name)
        name_counts[name] += 1

        # Try to load image
        img = cv2.imread(str(img_path))
        if img is None:
            load_failures.append((idx, name, zip_file))
            continue

        h, w = img.shape[:2]
        size_counts[(w, h)] += 1
        ext = os.path.splitext(zip_file)[1].lower()
        format_counts[ext] += 1

        # Compute hash for duplicate detection
        img_hash = compute_image_hash(img)
        if img_hash is not None:
            image_hashes[img_hash].append((idx, name, zip_file))

    # Count unique vs duplicate images
    for img_hash, entries in image_hashes.items():
        if len(entries) == 1:
            unique_images += 1
        else:
            duplicate_images += len(entries) - 1

    # Report
    print(f"\n{'='*60}")
    print("P0 CATALOG AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"Total catalog entries:     {len(catalog)}")
    print(f"Unique names:              {len(unique_names)}")
    print(f"Names with duplicates:     {sum(1 for c in name_counts.values() if c > 1)}")
    print(f"Total duplicate name refs: {len(catalog) - len(unique_names)}")
    print(f"Image load failures:       {len(load_failures)}")
    print(f"Unique image hashes:       {len(image_hashes)}")
    print(f"Unique images (no dupes):  {unique_images}")
    print(f"Duplicate image instances: {duplicate_images}")
    print(f"Unique sizes:              {len(size_counts)}")
    print(f"Formats:                   {dict(format_counts)}")

    print(f"\nTop 10 most common sizes:")
    for size, count in size_counts.most_common(10):
        print(f"  {size[0]}x{size[1]}: {count}")

    print(f"\nTop 10 most duplicated names:")
    for name, count in name_counts.most_common(10):
        if count > 1:
            print(f"  '{name}': {count} variants")

    # Show load failures
    if load_failures:
        print(f"\nLoad failures ({len(load_failures)}):")
        for idx, name, zf in load_failures[:10]:
            print(f"  index={idx}, name='{name}', file='{zf}'")

    # Duplicate image analysis: show examples of images with same hash but different names
    multi_name_hashes = []
    for img_hash, entries in image_hashes.items():
        names_in_hash = set(e[1] for e in entries)
        if len(names_in_hash) > 1:
            multi_name_hashes.append((img_hash, entries))
    print(f"\nHash collisions with different names: {len(multi_name_hashes)}")
    if multi_name_hashes:
        print("  Example (same image, different names):")
        for img_hash, entries in multi_name_hashes[:3]:
            print(f"    {[(e[1], e[2]) for e in entries]}")

    # Size distribution by name
    print(f"\nSize range: width {min(s[0] for s in size_counts)}-{max(s[0] for s in size_counts)}, "
          f"height {min(s[1] for s in size_counts)}-{max(s[1] for s in size_counts)}")

    # Write audit report
    report = {
        'total_entries': len(catalog),
        'unique_names': len(unique_names),
        'names_with_duplicates': sum(1 for c in name_counts.values() if c > 1),
        'duplicate_name_refs': len(catalog) - len(unique_names),
        'load_failures': len(load_failures),
        'unique_image_hashes': len(image_hashes),
        'unique_images': unique_images,
        'duplicate_image_instances': duplicate_images,
        'unique_sizes': len(size_counts),
        'formats': dict(format_counts),
        'size_distribution': {f"{w}x{h}": c for (w, h), c in size_counts.most_common()},
        'top_duplicated_names': {n: c for n, c in name_counts.most_common(20) if c > 1},
        'hash_collisions_different_names': len(multi_name_hashes),
        'p0_ready': len(load_failures) == 0 and len(image_hashes) > 1000,
    }

    output_path = OUTPUT_DIR / 'catalog_audit_p0.json'
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"\nAudit report written to: {output_path}")

    return report


if __name__ == '__main__':
    audit_catalog()
