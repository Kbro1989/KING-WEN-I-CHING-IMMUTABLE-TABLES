"""
Synthetic Background Sweep — Threshold Policy Comparison
========================================================
Tests three threshold policies against controlled images with known
foreground/background intensities. Measures pixel-level TP/FP/FN and
symbol-level preservation.

Policies tested:
  1. existing:    threshold = primary_white // 2
  2. proposed:    threshold = primary_white - 127
  3. adaptive:    threshold = primary_white * 0.4 (more permissive for dark bg)

Usage:
  python scripts/test_threshold_policies.py
"""
import numpy as np
import json
from pathlib import Path

OUTPUT_DIR = Path("DATASETS/vision_comparison/threshold_policy_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_test_image(bg_intensity, fg_intensity, noise_level=0, seed=42):
    """Create a synthetic page image with known foreground/background."""
    rng = np.random.RandomState(seed)
    h, w = 200, 300
    img = np.full((h, w), bg_intensity, dtype=np.uint8)

    # Add text-like foreground (horizontal strokes)
    # Simulate text as rectangles of various sizes
    strokes = [
        (20, 30, 80, 5),   # x, y, width, height
        (20, 50, 120, 5),
        (20, 70, 60, 5),
        (150, 30, 100, 5),
        (150, 50, 80, 5),
        (150, 70, 90, 5),
    ]
    for x, y, sw, sh in strokes:
        img[y:y+sh, x:x+sw] = fg_intensity

    # Add noise
    if noise_level > 0:
        noise = rng.randint(0, noise_level, (h, w), dtype=np.uint8)
        img = np.clip(img.astype(np.int16) + noise.astype(np.int16), 0, 255).astype(np.uint8)

    return img


def detect_text_pixels(gray, threshold):
    """Classify pixels as text (dark) using gray < threshold."""
    return gray < threshold


def compute_metrics(predicted_mask, ground_truth_mask):
    """Compute TP, FP, FN, precision, recall."""
    tp = int(np.sum(predicted_mask & ground_truth_mask))
    fp = int(np.sum(predicted_mask & ~ground_truth_mask))
    fn = int(np.sum(~predicted_mask & ground_truth_mask))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-10)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(precision, 4),
            "recall": round(recall, 4), "f1": round(f1, 4)}


def policy_existing(primary_white):
    return primary_white // 2

def policy_proposed(primary_white):
    return primary_white - 127

def policy_adaptive(primary_white):
    return int(primary_white * 0.4)


def run_sweep():
    backgrounds = [255, 250, 240, 230, 220]
    foregrounds = [0, 64, 96, 112, 120, 128, 160, 192]
    noise_levels = [0, 10, 30]

    policies = {
        "existing (W//2)": policy_existing,
        "proposed (W-127)": policy_proposed,
        "adaptive (W*0.4)": policy_adaptive,
    }

    results = []
    for bg in backgrounds:
        for fg in foregrounds:
            for noise in noise_levels:
                img = make_test_image(bg, fg, noise)
                gray = img  # already grayscale
                # Ground truth: pixels that are foreground (the strokes)
                # We know the stroke positions, so create GT mask
                gt_mask = np.zeros_like(gray, dtype=bool)
                strokes = [(20, 30, 80, 5), (20, 50, 120, 5), (20, 70, 60, 5),
                           (150, 30, 100, 5), (150, 50, 80, 5), (150, 70, 90, 5)]
                for x, y, sw, sh in strokes:
                    gt_mask[y:y+sh, x:x+sw] = True

                # Add noise to GT (noise pixels are not ground truth)
                # (noise doesn't change GT)

                for pname, pfunc in policies.items():
                    threshold = pfunc(bg)
                    pred_mask = detect_text_pixels(gray, threshold)
                    metrics = compute_metrics(pred_mask, gt_mask)
                    results.append({
                        "background": bg,
                        "foreground": fg,
                        "noise": noise,
                        "policy": pname,
                        "threshold": threshold,
                        **metrics,
                    })

    return results


def main():
    results = run_sweep()

    # Save full results
    out_path = OUTPUT_DIR / "threshold_policy_sweep.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} test results to {out_path}")

    # Summary: aggregate by policy and background
    print("\n=== SUMMARY: Average F1 by Policy and Background ===")
    from collections import defaultdict
    by_policy_bg = defaultdict(list)
    for r in results:
        by_policy_bg[(r["policy"], r["background"])].append(r["f1"])

    for policy in ["existing (W//2)", "proposed (W-127)", "adaptive (W*0.4)"]:
        print(f"\n{policy}:")
        for bg in [255, 250, 240, 230, 220]:
            f1s = by_policy_bg[(policy, bg)]
            avg_f1 = np.mean(f1s) if f1s else 0
            print(f"  bg={bg}: avg F1={avg_f1:.4f} (n={len(f1s)})")

    # Symbol-level preservation: check if stroke pixels are preserved
    print("\n=== SYMBOL-LEVEL: Recall by Foreground Intensity (bg=240, noise=0) ===")
    for fg in [0, 64, 96, 112, 120, 128, 160, 192]:
        print(f"\n  fg={fg}:")
        for policy in ["existing (W//2)", "proposed (W-127)", "adaptive (W*0.4)"]:
            matching = [r for r in results
                        if r["policy"] == policy and r["background"] == 240
                        and r["foreground"] == fg and r["noise"] == 0]
            if matching:
                r = matching[0]
                print(f"    {policy}: threshold={r['threshold']}, recall={r['recall']:.4f}, precision={r['precision']:.4f}, F1={r['f1']:.4f}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
