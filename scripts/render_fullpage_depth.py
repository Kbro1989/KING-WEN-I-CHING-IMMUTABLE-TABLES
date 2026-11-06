"""Render full PDF pages at zoom=2 and process through DA-V2 depth.

Uses the selected formula pages from the cross-reference pipeline.
Output: DATASETS/PDF_FIDELITY_RENDERINGS/fullpage_depth/
"""
import json
import os
import sys
import pymupdf
import cv2
import numpy as np
import torch
import matplotlib
from safetensors.torch import load_file
from pathlib import Path
from tqdm import tqdm

# Selected formula pages (1-indexed, from cross_reference_pipeline)
SELECTED_PAGES = {
    "0806.2366": 3,
    "1212.0957": 8,
    "2009.00031": 5,
    "2102.03334": 6,
    "2605.00155": 27,
    "2605.00224": 1,
    "2605.06070": 12,
    "2605.18130": 4,
    "2605.22715": 19,
    "2605.23244": 4,
    "2605.24807": 9,
    "2605.24856": 17,
    "2605.25036": 3,
    "2605.25334": 6,
    "2605.28615": 15,
    "2605.28896": 16,
}

ZOOM = 2
ENCODER = "vits"
INPUT_SIZE = 518
UDA_V2 = "C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2"
PDF_DIR = "DATASETS/benchmark_pdfs"
OUT_DIR = "DATASETS/PDF_FIDELITY_RENDERINGS/fullpage_depth"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load DA-V2 model
    sys.path.insert(0, UDA_V2)
    os.chdir(UDA_V2)
    from depth_anything_v2.dpt import DepthAnythingV2

    model_configs = {
        'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
    }
    depth_anything = DepthAnythingV2(**model_configs[ENCODER])
    state_dict = load_file(f'checkpoints/depth_anything_v2_{ENCODER}.safetensors')
    depth_anything.load_state_dict(state_dict)
    depth_anything = depth_anything.to('cpu').eval()
    os.chdir("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")

    cmap = matplotlib.colormaps.get_cmap('Spectral_r')

    results = []
    for paper_id, page_num in tqdm(sorted(SELECTED_PAGES.items()), desc="Full pages"):
        pdf_path = os.path.join(PDF_DIR, f"{paper_id}.pdf")
        if not os.path.exists(pdf_path):
            print(f"  SKIP (no PDF): {paper_id}")
            continue

        doc = pymupdf.open(pdf_path)
        if page_num - 1 >= len(doc):
            print(f"  SKIP (page {page_num} out of range, {len(doc)} pages): {paper_id}")
            doc.close()
            continue

        page = doc[page_num - 1]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM))
        stem = f"{paper_id}_p{page_num}_fullpage_z{ZOOM}"
        img_path = os.path.join(OUT_DIR, f"{stem}.png")
        pix.save(img_path)

        # Process through DA-V2
        raw_image = cv2.imread(img_path)
        depth = depth_anything.infer_image(raw_image, INPUT_SIZE)
        depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
        depth = depth.astype(np.uint8)

        # Save outputs
        depth_gray = np.repeat(depth[..., np.newaxis], 3, axis=-1)
        cv2.imwrite(os.path.join(OUT_DIR, f"{stem}_depth_grayscale.png"), depth_gray)

        depth_color = (cmap(depth)[:, :, :3] * 255)[:, :, ::-1].astype(np.uint8)
        cv2.imwrite(os.path.join(OUT_DIR, f"{stem}_depth.png"), depth_color)

        split_region = np.ones((raw_image.shape[0], 50, 3), dtype=np.uint8) * 255
        combined = cv2.hconcat([raw_image, split_region, depth_color])
        cv2.imwrite(os.path.join(OUT_DIR, f"{stem}_combined.png"), combined)

        results.append({
            "paper_id": paper_id,
            "page_number": page_num,
            "zoom": ZOOM,
            "image_size": [pix.width, pix.height],
            "depth_shape": list(depth.shape),
            "depth_mean": float(depth.mean()),
            "depth_min": int(depth.min()),
            "depth_max": int(depth.max()),
            "original_png": f"{stem}.png",
            "depth_grayscale_png": f"{stem}_depth_grayscale.png",
            "depth_color_png": f"{stem}_depth.png",
            "combined_png": f"{stem}_combined.png",
        })
        doc.close()
        print(f"  OK: {paper_id} p{page_num} ({pix.width}x{pix.height})")

    # Save manifest
    manifest = {
        "description": "Full-page depth renders at zoom=2 for 16 benchmark formula pages",
        "encoder": ENCODER,
        "input_size": INPUT_SIZE,
        "zoom": ZOOM,
        "paper_count": len(results),
        "results": results,
    }
    with open(os.path.join(OUT_DIR, "fullpage_depth_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nDone: {len(results)} pages processed. Output: {OUT_DIR}")

if __name__ == "__main__":
    main()
