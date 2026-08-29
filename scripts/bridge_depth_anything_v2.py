"""
King Wen × Depth Anything V2 Bridge
====================================
Feeds 64 QuantumLab surface plot PNGs through Depth Anything V2 (16-bit)
to produce per-hexagram depth displacement maps, then converts each into
an Open3D point cloud (.ply) with depth-sculpted vertex positions.

The resulting depth maps and point clouds are written back into the
KING-WEN-I-CHING-IMMUTABLE-TABLES datasets, and a manifest JSON is
emitted linking each hexagram to its depth assets.

Requires: Upgraded-Depth-Anything-V2 venv with checkpoints installed.

Usage:
  cd KING-WEN-I-CHING-IMMUTABLE-TABLES
  python scripts/bridge_depth_anything_v2.py [--encoder vits|vitb|vitl] [--input-size 518]
"""
import argparse
import json
import sys
import os
from pathlib import Path

KINGWEN_ROOT = Path(r"c:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
DEPTH_ROOT = Path(r"c:\Users\krist\Desktop\Upgraded-Depth-Anything-V2")

def run_depth_inference(encoder="vits", input_size=518):
    """
    Run Depth Anything V2 inference on all 64 QuantumLab PNGs.
    Uses the DA-V2 library directly (no subprocess shelling).
    """
    # Add DA-V2 to path so we can import its modules
    sys.path.insert(0, str(DEPTH_ROOT))

    import cv2
    import numpy as np

    try:
        import torch
        from safetensors.torch import load_file
        from depth_anything_v2.dpt import DepthAnythingV2
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print(f"  Run oc_install.bat in {DEPTH_ROOT} first.")
        return None

    DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'cpu'
    print(f"[DEVICE] Using: {DEVICE}")

    model_configs = {
        'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
        'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
        'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]},
        'vitg': {'encoder': 'vitg', 'features': 384, 'out_channels': [1536, 1536, 1536, 1536]}
    }

    ckpt_path = DEPTH_ROOT / "checkpoints" / f"depth_anything_v2_{encoder}.safetensors"
    if not ckpt_path.exists():
        print(f"[ERROR] Checkpoint not found: {ckpt_path}")
        print(f"  Run oc_install.bat to download model weights.")
        return None

    print(f"[MODEL] Loading DepthAnythingV2 encoder={encoder} from {ckpt_path.name}...")
    model = DepthAnythingV2(**model_configs[encoder])
    state_dict = load_file(str(ckpt_path))
    model.load_state_dict(state_dict)
    model = model.to(DEVICE).eval()
    print(f"[MODEL] Loaded successfully on {DEVICE}.")

    # I/O paths
    input_dir = KINGWEN_ROOT / "DATASETS" / "quantumlab_plots"
    depth_16bit_dir = KINGWEN_ROOT / "DATASETS" / "depth_maps_16bit"
    depth_pointcloud_dir = KINGWEN_ROOT / "DATASETS" / "depth_pointclouds"
    depth_16bit_dir.mkdir(parents=True, exist_ok=True)
    depth_pointcloud_dir.mkdir(parents=True, exist_ok=True)

    manifest_records = []

    for h_id in range(1, 65):
        src_file = input_dir / f"quantum_3d_hex_{h_id:02d}.png"
        if not src_file.exists():
            print(f"  [SKIP] Missing input: {src_file.name}")
            continue

        raw_image = cv2.imread(str(src_file))
        if raw_image is None:
            print(f"  [SKIP] Could not read: {src_file.name}")
            continue

        # Infer depth
        depth = model.infer_image(raw_image, input_size)

        # --- 16-bit grayscale depth map ---
        depth_norm = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8) * 65025.0
        depth_u16 = depth_norm.astype(np.uint16)
        depth_16_path = depth_16bit_dir / f"depth_hex_{h_id:02d}_16bit.png"
        depth_gray = np.repeat(depth_u16[..., np.newaxis], 3, axis=-1)
        cv2.imwrite(str(depth_16_path), depth_gray)

        # --- Depth-to-pointcloud (pinhole projection) ---
        h, w = raw_image.shape[:2]
        # Use consistent focal length for square-ish quantum plots
        fx = fy = w * 0.6
        x_grid, y_grid = np.meshgrid(np.arange(w), np.arange(h))
        x_cam = (x_grid - w / 2.0) / fx
        y_cam = (y_grid - h / 2.0) / fy

        # Normalize depth to world-scale meters (max_depth = 20m equivalent)
        z_metric = depth / (depth.max() + 1e-8) * 20.0

        points = np.stack([
            x_cam * z_metric,
            y_cam * z_metric,
            z_metric
        ], axis=-1).reshape(-1, 3)

        # Color from source image (BGR → RGB, normalized)
        colors = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB).reshape(-1, 3) / 255.0

        # Write PLY (ASCII format, no Open3D dependency required)
        ply_path = depth_pointcloud_dir / f"depth_cloud_hex_{h_id:02d}.ply"
        n_verts = points.shape[0]
        ply_header = (
            f"ply\n"
            f"format ascii 1.0\n"
            f"element vertex {n_verts}\n"
            f"property float x\n"
            f"property float y\n"
            f"property float z\n"
            f"property uchar red\n"
            f"property uchar green\n"
            f"property uchar blue\n"
            f"end_header\n"
        )

        # Downsample for file size (every 4th pixel)
        stride = 4
        ds_points = points[::stride]
        ds_colors = (colors[::stride] * 255).astype(np.uint8)
        n_ds = ds_points.shape[0]

        ply_header_ds = (
            f"ply\n"
            f"format ascii 1.0\n"
            f"element vertex {n_ds}\n"
            f"property float x\n"
            f"property float y\n"
            f"property float z\n"
            f"property uchar red\n"
            f"property uchar green\n"
            f"property uchar blue\n"
            f"end_header\n"
        )

        with open(ply_path, 'w') as f:
            f.write(ply_header_ds)
            for i in range(n_ds):
                p = ds_points[i]
                c = ds_colors[i]
                f.write(f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f} {c[0]} {c[1]} {c[2]}\n")

        # Compute depth statistics for the manifest
        depth_stats = {
            "min_depth": round(float(depth.min()), 4),
            "max_depth": round(float(depth.max()), 4),
            "mean_depth": round(float(depth.mean()), 4),
            "std_depth": round(float(depth.std()), 4)
        }

        manifest_records.append({
            "hexagram_id": h_id,
            "source_plot": f"DATASETS/quantumlab_plots/quantum_3d_hex_{h_id:02d}.png",
            "depth_map_16bit": f"DATASETS/depth_maps_16bit/depth_hex_{h_id:02d}_16bit.png",
            "depth_pointcloud": f"DATASETS/depth_pointclouds/depth_cloud_hex_{h_id:02d}.ply",
            "depth_statistics": depth_stats,
            "encoder": encoder,
            "input_size": input_size,
            "device": DEVICE,
            "pointcloud_vertex_count": n_ds,
            "pointcloud_stride": stride
        })

        print(f"  [{h_id:02d}/64] depth_hex_{h_id:02d}_16bit.png -> {n_ds} vertices -> depth_cloud_hex_{h_id:02d}.ply")

    # Write manifest
    manifest = {
        "pipeline": "King Wen × Depth Anything V2 Bridge",
        "version": "1.0.0",
        "model": f"depth_anything_v2_{encoder}",
        "total_processed": len(manifest_records),
        "records": manifest_records
    }
    manifest_path = KINGWEN_ROOT / "DATASETS" / "depth_anything_v2_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[MANIFEST] Written: {manifest_path.name} ({len(manifest_records)} records)")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="King Wen × Depth Anything V2 Bridge")
    parser.add_argument("--encoder", type=str, default="vits",
                        choices=["vits", "vitb", "vitl", "vitg"],
                        help="DA-V2 encoder size (default: vits for speed)")
    parser.add_argument("--input-size", type=int, default=518,
                        help="Input resolution for depth inference (default: 518)")
    args = parser.parse_args()

    print("=" * 85)
    print("KING WEN x DEPTH ANYTHING V2 BRIDGE: QUANTUM PLOT -> DEPTH MAP -> POINT CLOUD")
    print("=" * 85)

    manifest = run_depth_inference(encoder=args.encoder, input_size=args.input_size)

    if manifest is None:
        print("[FAILED] Depth inference did not complete. Check errors above.")
        return 1

    print("=" * 85)
    print(f"DEPTH BRIDGE COMPLETE: {manifest['total_processed']}/64 hexagrams processed")
    print("=" * 85)
    return 0


if __name__ == "__main__":
    sys.exit(main())
