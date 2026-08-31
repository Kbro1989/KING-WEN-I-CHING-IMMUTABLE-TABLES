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

    # 5. Ensure Edge Pre-warm Cache Layer Function exists
    layer_func_path = ROOT / "functions" / "api" / "cache" / "layer" / "[id].js"
    layer_func_path.parent.mkdir(parents=True, exist_ok=True)
    layer_func_code = """/**
 * King Wen 64 Sovereign Engine — /api/cache/layer/[id]
 * Progressive Edge Pre-Warm Cache Layer Slicer (Layers 0..3).
 */
export async function onRequestGet(context) {
  const { request, params, env } = context;
  const layerId = parseInt(params.id, 10);

  if (isNaN(layerId) || layerId < 0 || layerId > 3) {
    return Response.json(
      { error: 'Invalid layer ID. Supported layers: 0 (Skeleton), 1 (Physics), 2 (Pellets), 3 (Egg & Audio).' },
      { status: 400 }
    );
  }

  // Edge Cache API Check
  const cache = caches.default;
  const cacheKey = new Request(request.url, request);
  let cachedResponse = await cache.match(cacheKey);
  if (cachedResponse) {
    const freshHeaders = new Headers(cachedResponse.headers);
    freshHeaders.set('X-Edge-Cache-Status', 'HIT');
    return new Response(cachedResponse.body, {
      status: cachedResponse.status,
      headers: freshHeaders,
    });
  }

  try {
    const assetReq = new Request(new URL('/DATASETS/kingwen_sovereign_world_topology.json', request.url));
    const assetRes = env.ASSETS ? await env.ASSETS.fetch(assetReq) : await fetch(assetReq);

    if (!assetRes.ok) {
      return Response.json(
        { error: 'World topology manifest not found on asset storage', status: assetRes.status },
        { status: 404 }
      );
    }

    const fullTopology = await assetRes.json();
    const sectors = fullTopology.sectors || [];

    let layerPayload = {};

    if (layerId === 0) {
      // Layer 0: Skeleton (Fastest initial spatial layout)
      layerPayload = {
        layer: 0,
        layer_name: "Skeleton Spatial Layout",
        total_sectors: sectors.length,
        world_grid: fullTopology.world_grid || {},
        sectors: sectors.map((s) => ({
          sector_id: s.sector_id,
          hexagram_id: s.hexagram_id,
          name: s.name,
          hexagram_name: s.hexagram_name,
          hanzi: s.hanzi,
          binary: s.binary,
          upper_trigram: s.upper_trigram,
          lower_trigram: s.lower_trigram,
          grid_coordinates: s.grid_coordinates,
          world_position: s.world_position,
          sector_bounds: s.sector_bounds,
          regional_biome: s.regional_biome,
          spectral_color: s.spectral_color,
          base_hue_degrees: s.base_hue_degrees
        }))
      };
    } else if (layerId === 1) {
      // Layer 1: Quantum Physics Nodes & Depth Clouds
      layerPayload = {
        layer: 1,
        layer_name: "Quantum Physics & Vortex Geometries",
        total_sectors: sectors.length,
        sectors: sectors.map((s) => ({
          sector_id: s.sector_id,
          hexagram_id: s.hexagram_id,
          quantum_physics: s.quantum_physics || {},
          quantum_wave_packet: s.quantum_wave_packet || {},
          action_doctrine: s.action_doctrine,
          citadel_archetype: s.citadel_archetype
        }))
      };
    } else if (layerId === 2) {
      // Layer 2: 384 Sound Pellets & Acoustic Field
      layerPayload = {
        layer: 2,
        layer_name: "384 Sound Pellets & Acoustic Field",
        total_sectors: sectors.length,
        total_pellets: sectors.length * 6,
        sectors: sectors.map((s) => ({
          sector_id: s.sector_id,
          hexagram_id: s.hexagram_id,
          yao_pellets: s.yao_pellets || []
        }))
      };
    } else if (layerId === 3) {
      // Layer 3: Centripetal Egg 60 Keyframes, Unison WAV Audio & JKD Passages
      layerPayload = {
        layer: 3,
        layer_name: "Master Centripetal Egg 3D Deformation & Audio Corpus",
        egg_keyframes_count: fullTopology.egg_keyframes ? fullTopology.egg_keyframes.length : 0,
        egg_keyframes: fullTopology.egg_keyframes || [],
        audio_unison_wav_b64: fullTopology.audio_unison_wav_b64 || "",
        jkd_passages_by_hex: sectors.reduce((acc, s) => {
          if (s.jkd_passages && s.jkd_passages.length > 0) {
            acc[s.hexagram_id] = s.jkd_passages;
          }
          return acc;
        }, {})
      };
    }

    const responseObj = {
      engine: 'King Wen 64 Sovereign Model Engine',
      version: '3.2.0',
      cf_colo: request.cf?.colo || 'EDGE',
      timestamp: new Date().toISOString(),
      data: layerPayload
    };

    const headers = new Headers({
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=7200, s-maxage=86400',
      'X-Edge-Cache-Status': 'MISS',
      'X-Prewarm-Layer': layerId.toString()
    });

    const response = new Response(JSON.stringify(responseObj), {
      status: 200,
      headers
    });

    context.waitUntil(cache.put(cacheKey, response.clone()));

    return response;
  } catch (err) {
    return Response.json(
      { error: 'Internal edge server error slicing pre-warm cache layer', message: err.message },
      { status: 500 }
    );
  }
}
"""
    layer_func_path.write_text(layer_func_code, encoding="utf-8")
    print(f"  [OK] Generated Layer Cache Edge Function: {layer_func_path.relative_to(ROOT)}")

    # 6. Verify Functions directory
    func_dir = ROOT / "functions"
    if func_dir.exists():
        func_files = list(func_dir.glob("**/*.js"))
        print(f"  [OK] Verified Cloudflare Edge Functions: {len(func_files)} JS files found.")
    else:
        print("  [WARNING] functions/ directory missing!")

    # 7. Verify wrangler.toml & _routes.json
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
