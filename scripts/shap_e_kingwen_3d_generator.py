#!/usr/bin/env python3
"""Shap-E 3D Avatar & Mesh Generator for 64 King Wen Sovereign Model NPCs.

Interfaces Shap-E (Text-to-3D / Image-to-3D) with the King Wen 64-State Phase Space:
1. Generates 64 grounded Shap-E prompts based on hexagram agent_type, domain, element_subset, action, and Schauberger motion
2. Maps 5-axis vector parameters (voiceWeight, coherence, darkTone) to Shap-E diffusion guidance scale and frame parameters
3. Exports a unified 3D generation manifest (`DATASETS/shap_e_3d_manifest.json`)
4. If `shap_e` is installed, runs live mesh synthesis to PLY/OBJ format for each Kit model
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KIT_DIR = ROOT / "DATASETS" / "kingwen_model_sets"
MESH_OUT_DIR = ROOT / "DATASETS" / "kingwen_3d_meshes"
MANIFEST_PATH = ROOT / "DATASETS" / "shap_e_3d_manifest.json"


def build_shap_e_prompt(npc: Dict[str, Any]) -> str:
    """Build a grounded text-to-3D Shap-E prompt for a King Wen Model NPC."""
    h_id = npc.get("hexagram_id")
    name = npc.get("name")
    agent = npc.get("agent_type", "sovereign")
    domain = npc.get("domain", "assertion")
    element = npc.get("element_subset", "heaven")
    action = npc.get("action", "ASSERT")
    specialty = npc.get("coder_specialty", "Research")
    motion = npc.get("schauberger", {}).get("motion_type", "centripetal")
    unicode_sym = npc.get("unicode", "")

    prompt = (
        f"A detailed 3D avatar character representing {name} ({unicode_sym}), "
        f"a {agent} Sovereign NPC specializing in {specialty} and {domain}. "
        f"Constructed of {element} element materials, {action} posture, "
        f"with {motion} vortex geometry, high quality digital 3D asset."
    )
    return prompt


def generate_shap_e_manifest() -> List[Dict[str, Any]]:
    """Build complete 64-hexagram Shap-E generation manifest."""
    manifest = []
    MESH_OUT_DIR.mkdir(parents=True, exist_ok=True)

    for h_id in range(1, 65):
        kit_path = KIT_DIR / f"kit_{h_id}.json"
        if not kit_path.exists():
            continue

        kit_data = json.loads(kit_path.read_text(encoding="utf-8"))
        npc = kit_data.get("grounded_npc", {})

        prompt = build_shap_e_prompt(npc)
        vec = npc.get("baseline_vector", {})
        voice_weight = float(vec.get("voiceWeight", 0.5))
        coherence = float(vec.get("coherence", 0.85))

        # Map vector space to Shap-E diffusion parameters
        guidance_scale = round(7.5 + (voice_weight * 5.0), 2)
        num_steps = int(32 + (coherence * 32))  # 32 to 64 steps

        mesh_filename = f"shap_e_hex_{h_id:02d}_{npc.get('agent_type', 'npc')}.obj"
        mesh_path = MESH_OUT_DIR / mesh_filename

        entry = {
            "hexagram_id": h_id,
            "name": npc.get("name"),
            "codename": npc.get("codename"),
            "agent_type": npc.get("agent_type"),
            "domain": npc.get("domain"),
            "shap_e_prompt": prompt,
            "diffusion_params": {
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_steps,
                "frame_size": 64,
            },
            "output_mesh_path": str(mesh_path),
            "rs3_actionable": npc.get("rs3_actionable"),
            "hermes_voice_mode": npc.get("hermes_voice_mode"),
        }
        manifest.append(entry)

        # Also store Shap-E info back into kit JSON
        kit_data["shap_e"] = {
            "prompt": prompt,
            "guidance_scale": guidance_scale,
            "mesh_path": str(mesh_path),
        }

        # Update extra
        extra = kit_data.get("extra", [])
        extra.append({"type": 0, "key": "shap_e_prompt", "intvalue": 0, "stringvalue": prompt})
        extra.append({"type": 0, "key": "shap_e_mesh_path", "intvalue": 0, "stringvalue": str(mesh_path)})
        kit_data["extra"] = extra

        kit_path.write_text(json.dumps(kit_data, ensure_ascii=False, indent=2), encoding="utf-8")

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


SHAP_E_DIR = Path(r"C:\Users\krist\Desktop\shap-e")
if SHAP_E_DIR.exists() and str(SHAP_E_DIR) not in sys.path:
    sys.path.insert(0, str(SHAP_E_DIR))


def _create_pan_cameras(size: int, device) -> Any:
    import numpy as np
    import torch
    from shap_e.models.nn.camera import DifferentiableCameraBatch, DifferentiableProjectiveCamera

    origins, xs, ys, zs = [], [], [], []
    for theta in np.linspace(0, 2 * np.pi, num=20):
        z = np.array([np.sin(theta), np.cos(theta), -0.5])
        z /= np.sqrt(np.sum(z**2))
        origin = -z * 4
        x = np.array([np.cos(theta), -np.sin(theta), 0.0])
        y = np.cross(z, x)
        origins.append(origin)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return DifferentiableCameraBatch(
        shape=(1, len(xs)),
        flat_camera=DifferentiableProjectiveCamera(
            origin=torch.from_numpy(np.stack(origins, axis=0)).float().to(device),
            x=torch.from_numpy(np.stack(xs, axis=0)).float().to(device),
            y=torch.from_numpy(np.stack(ys, axis=0)).float().to(device),
            z=torch.from_numpy(np.stack(zs, axis=0)).float().to(device),
            width=size,
            height=size,
            x_fov=0.7,
            y_fov=0.7,
        ),
    )


def generate_standalone_ply_mesh(out_path: Path, hex_id: int, name: str) -> Path:
    """Generate standalone 729-vertex 3D Point-Cloud PLY mesh file without external libraries."""
    out_path = out_path.with_suffix(".ply")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    vertices = []
    # 729 vertices mapped to 3^6 ternary state space
    import math
    for i in range(729):
        t = (i / 729.0) * 2.0 * math.pi
        z = math.cos(t * (hex_id % 8 + 1)) * 0.5
        r = 1.0 + 0.2 * math.sin(t * 6)
        x = r * math.cos(t)
        y = r * math.sin(t)
        # RGB based on hexagram ID phase
        red = int((math.sin(t) + 1.0) * 127.5)
        green = int((math.cos(t) + 1.0) * 127.5)
        blue = (hex_id * 4) % 256
        vertices.append(f"{x:.4f} {y:.4f} {z:.4f} {red} {green} {blue}")

    header = (
        "ply\n"
        "format ascii 1.0\n"
        f"comment King Wen Hexagram #{hex_id} {name} 3D Point Cloud\n"
        f"element vertex {len(vertices)}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar red\n"
        "property uchar green\n"
        "property uchar blue\n"
        "end_header\n"
    )
    content = header + "\n".join(vertices) + "\n"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def try_run_shap_e_live(manifest: List[Dict[str, Any]], limit: int = 1) -> None:
    """Attempt live Shap-E generation if PyTorch and Shap-E are installed, fallback to standalone PLY."""
    try:
        import torch
        from shap_e.diffusion.sample import sample_latents
        from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
        from shap_e.models.download import load_model, load_config
        from shap_e.util.collections import AttrDict
        from shap_e.models.transmitter.base import Transmitter
    except ImportError as err:
        print(f"\n[INFO] Shap-E import status: {err}")
        print("[INFO] Fallback: Generating 64 Standalone Repository-Native 3D PLY Meshes...")
        for entry in manifest:
            out_p = generate_standalone_ply_mesh(Path(entry["output_mesh_path"]), entry["hexagram_id"], entry["name"])
        print(f"[SUCCESS] Generated 64 Standalone 3D Point-Cloud PLY Meshes in DATASETS/kingwen_3d_meshes/")
        return

    print(f"\n[SHAP-E LIVE] Initializing Shap-E models for top {limit} hexagrams...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[SHAP-E LIVE] Operating on compute device: {device}")

    xm = load_model("transmitter", device=device)
    model = load_model("text300M", device=device)
    diffusion = diffusion_from_config(load_config("diffusion"))

    @torch.no_grad()
    def _decode_latent_mesh(latent: torch.Tensor):
        cameras = _create_pan_cameras(2, latent.device)
        params = (xm.encoder if isinstance(xm, Transmitter) else xm).bottleneck_to_params(latent[None])
        decoded = xm.renderer.render_views(
            AttrDict(cameras=cameras),
            params=params,
            options=AttrDict(rendering_mode="stf", render_with_direction=False),
        )
        return decoded.raw_meshes[0]

    for entry in manifest[:limit]:
        print(f"\nGenerating 3D Mesh for Hex #{entry['hexagram_id']} ({entry['name']})...")
        print(f"  Prompt: {entry['shap_e_prompt']}")

        latents = sample_latents(
            batch_size=1,
            model=model,
            diffusion=diffusion,
            guidance_scale=entry["diffusion_params"]["guidance_scale"],
            model_kwargs=dict(texts=[entry["shap_e_prompt"]]),
            progress=True,
            clip_denoised=True,
            use_fp16=(device.type == "cuda"),
            use_karras=True,
            karras_steps=entry["diffusion_params"]["num_inference_steps"],
            sigma_min=1e-3,
            sigma_max=160,
            s_churn=0,
        )

        for i, latent in enumerate(latents):
            t_mesh = _decode_latent_mesh(latent)
            out_ply = Path(entry["output_mesh_path"]).with_suffix(".ply")
            out_ply.parent.mkdir(parents=True, exist_ok=True)
            with open(out_ply, "w", encoding="utf-8") as f:
                t_mesh.write_ply(f)
            print(f"  [SUCCESS] Wrote 3D PLY Mesh to: {out_ply}")


def main() -> int:
    print("=" * 80)
    print("KING WEN 64 SOVEREIGN MODEL NPCs — SHAP-E 3D AVATAR GENERATOR")
    print("=" * 80)

    manifest = generate_shap_e_manifest()
    print(f"Successfully generated Shap-E 3D Manifest for all {len(manifest)} Model NPCs!")
    print(f"Saved manifest to: {MANIFEST_PATH}")

    print("\nSample Shap-E Prompts:")
    for item in manifest[:3]:
        sample_line = (
            f"  Hex #{item['hexagram_id']:02d} [{item['agent_type'].upper()}] '{item['name']}':\n"
            f"    Prompt   : {item['shap_e_prompt']}\n"
            f"    Guidance : {item['diffusion_params']['guidance_scale']} | Mesh: {item['output_mesh_path']}\n\n"
        )
        sys.stdout.buffer.write(sample_line.encode("utf-8"))

    if "--run" in sys.argv:
        try_run_shap_e_live(manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
