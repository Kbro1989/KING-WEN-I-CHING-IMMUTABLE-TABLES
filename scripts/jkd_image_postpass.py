#!/usr/bin/env python3
"""JKD scene image substrate generator + 7/10 self-evaluation post-pass.

Reads DATASETS/jkd_ingestion_binary.jsonl.
For each scene record:
  - generates a placeholder scene image from text
  - evaluates the image with vision_parse_color_map structural criteria
  - if score < 7/10, redoes last-N images and records redos
Writes updated records back.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BINARY_OUT = ROOT / "DATASETS" / "jkd_ingestion_binary.jsonl"
SUBSTRATE_DIR = ROOT / "DATASETS" / "jkd_scene_substrate"

OPENJARVIS_SRC = Path(r"C:/Users/krist/Desktop/OpenJarvis/src")
if OPENJARVIS_SRC.exists():
    sys.path.insert(0, str(OPENJARVIS_SRC))


def _generate_placeholder_image(width: int = 512, height: int = 512, hex_id: int = 1) -> str:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise RuntimeError("Pillow required")

    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    label = f"Scene {hex_id}"
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), label, fill=(255, 255, 255), font=font)

    out_path = str(SUBSTRATE_DIR / f"scene_{hex_id}.png")
    img.save(out_path)
    return out_path


def _evaluate_image(image_path: str) -> dict:
    try:
        from openjarvis.tools.vision_parse_color_map import process_image
        result = process_image(image_path, max_colors=12)
    except Exception as exc:
        return {"score": 0.0, "passed": False, "error": str(exc), "criteria": {}}

    criteria = {
        "palette_non_empty": len(result.palette) > 0,
        "regions_non_empty": len(result.regions) > 0,
        "color_count_ok": 2 <= len(result.palette) <= 12,
        "region_count_ok": len(result.regions) >= 1,
        "has_key": bool(result.key),
        "width_ok": result.originalWidth >= 64,
        "height_ok": result.originalHeight >= 64,
        "border_coverage_ok": sum(1 for r in result.regions if r.borderPixels) >= 1,
        "pixel_count_ok": sum(len(r.pixels) for r in result.regions) == result.originalWidth * result.originalHeight,
        "digest_present": bool(result.key.get("digest")),
    }
    score = sum(1 for v in criteria.values() if v) / len(criteria)
    return {"score": round(score, 2), "passed": score >= 0.7, "error": None, "criteria": criteria}


def run_image_postpass(
    limit: int | None = None,
    max_redos: int = 1,
    pass_threshold: float = 0.7,
) -> dict:
    if not BINARY_OUT.exists():
        raise FileNotFoundError(f"Missing binary records: {BINARY_OUT}")

    SUBSTRATE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [l for l in BINARY_OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
    records = [json.loads(line) for line in lines]

    updated = 0
    redos = 0
    passed = 0
    failed = 0

    for rec in records[:limit] if limit else records:
        idx = rec.get("scene_index") or 1
        hex_item = None
        expanded = rec.get("expanded") or []
        if expanded:
            hex_item = next((h for h in expanded if h.get("hexagram_id")), None)
        hex_id = (hex_item or {}).get("hexagram_id") or idx
        img_path = str(SUBSTRATE_DIR / f"scene_{idx}.png")
        substrate = rec.get("image_substrate") or {}
        redos_done = int(substrate.get("redos") or 0)

        try:
            _generate_placeholder_image(hex_id=hex_id)
            eval_result = _evaluate_image(img_path)
        except Exception as exc:
            eval_result = {"score": 0.0, "passed": False, "error": str(exc), "criteria": {}}

        passed_flag = bool(eval_result.get("passed", False))
        redo_needed = not passed_flag and redos_done < max_redos

        rec["image_substrate"] = {
            "generated": True,
            "path": img_path,
            "status": "pending_redo" if redo_needed else ("passed" if passed_flag else "failed"),
            "eval_score": eval_result.get("score"),
            "eval_passed": passed_flag,
            "redos": redos_done + (1 if redo_needed else 0),
            "eval_breakdown": eval_result.get("criteria") or {},
            "eval_error": eval_result.get("error"),
        }

        if passed_flag:
            passed += 1
        else:
            failed += 1
            if redo_needed:
                redos += 1
                try:
                    _generate_placeholder_image(hex_id=hex_id)
                    re_eval = _evaluate_image(img_path)
                    rec["image_substrate"]["status"] = "passed" if re_eval.get("passed") else "failed"
                    rec["image_substrate"]["eval_score"] = re_eval.get("score")
                    rec["image_substrate"]["eval_breakdown"] = re_eval.get("criteria") or {}
                    if re_eval.get("passed"):
                        passed += 1
                        failed -= 1
                except Exception as exc:
                    rec["image_substrate"]["eval_error"] = str(exc)

        updated += 1

    with BINARY_OUT.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return {
        "updated": updated,
        "passed": passed,
        "failed": failed,
        "redos": redos,
        "pass_threshold": pass_threshold,
        "substrate_dir": str(SUBSTRATE_DIR),
    }


if __name__ == "__main__":
    summary = run_image_postpass()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
