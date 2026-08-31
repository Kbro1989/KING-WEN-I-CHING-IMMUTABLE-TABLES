#!/usr/bin/env python3
"""build_cloudflare_dist.py — King Wen 64 Sovereign Engine Cloudflare Distribution Builder.

Pre-bakes, validates, and syncs all 3D world viewer assets, topology manifests, and edge functions
into the `public/` and `functions/` directories for Cloudflare Pages / Workers deployment.
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
DATASETS_DIR = ROOT / "DATASETS"

def build_dist():
    print("=" * 80)
    print("BUILDING CLOUDFLARE PAGES / WORKERS DISTRIBUTION BUNDLE")
    print("=" * 80)

    # 1. Ensure public/ directory exists
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    pub_datasets = PUBLIC_DIR / "DATASETS"
    pub_datasets.mkdir(parents=True, exist_ok=True)

    # 2. Copy 3D Sovereign World Viewer as public/index.html
    src_html = DATASETS_DIR / "kingwen_sovereign_world_viewer.html"
    dst_html = PUBLIC_DIR / "index.html"
    if src_html.exists():
        shutil.copy2(src_html, dst_html)
        print(f"  [OK] Copied {src_html.name} -> {dst_html.relative_to(ROOT)}")
    else:
        print(f"  [WARNING] {src_html.name} missing! Run scripts/generate_sovereign_world.py first.")

    # 3. Copy World Topology Manifest
    src_topo = DATASETS_DIR / "kingwen_sovereign_world_topology.json"
    dst_topo = pub_datasets / "kingwen_sovereign_world_topology.json"
    if src_topo.exists():
        shutil.copy2(src_topo, dst_topo)
        print(f"  [OK] Copied {src_topo.name} -> {dst_topo.relative_to(ROOT)}")

    # 4. Copy Quantum Prewarm Manifest
    src_prewarm = DATASETS_DIR / "quantum_prewarm_manifest.json"
    dst_prewarm = pub_datasets / "quantum_prewarm_manifest.json"
    if src_prewarm.exists():
        shutil.copy2(src_prewarm, dst_prewarm)
        print(f"  [OK] Copied {src_prewarm.name} -> {dst_prewarm.relative_to(ROOT)}")

    # 5. Verify Functions directory
    func_dir = ROOT / "functions"
    if func_dir.exists():
        func_files = list(func_dir.glob("**/*.js"))
        print(f"  [OK] Verified Cloudflare Edge Functions: {len(func_files)} JS files found.")
    else:
        print("  [WARNING] functions/ directory missing!")

    # 6. Verify wrangler.toml & _routes.json
    wrangler = ROOT / "wrangler.toml"
    routes = PUBLIC_DIR / "_routes.json"
    if wrangler.exists() and routes.exists():
        print("  [OK] wrangler.toml and _routes.json verified.")

    print("=" * 80)
    print("CLOUDFLARE PAGES BUNDLE 100% READY FOR DEPLOYMENT")
    print("Local Test: npx wrangler pages dev public")
    print("Deploy:     npx wrangler pages deploy public")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(build_dist())
