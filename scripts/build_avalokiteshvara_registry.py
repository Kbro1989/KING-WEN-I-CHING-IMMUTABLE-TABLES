#!/usr/bin/env python3
"""Build full shotgun Avalokiteshvara registry from King Wen source files.

Expands the 64 verified hexagrams into a large arm registry derived only from:
- king_wen_64_verified.json
- DATASETS/kingwen_trigram_reference (1).csv
- DATASETS/kingwen_category_matrix (1).csv
- DATASETS/kingwen_oracle_yao_lines (1).csv

Writes out a single shotgun JSON with all arms.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VERIFIED_PATH = ROOT / "king_wen_64_verified.json"
TRIGRAM_CSV = ROOT / "DATASETS" / "kingwen_trigram_reference (1).csv"
CATEGORY_CSV = ROOT / "DATASETS" / "kingwen_category_matrix (1).csv"
YAO_LINES_CSV = ROOT / "DATASETS" / "kingwen_oracle_yao_lines (1).csv"
OUTPUT_PATH = ROOT / "scripts" / "avalokiteshvara_shotgun_full.json"

FACE_MAP = {
    "sovereign": {
        "face": "Peaceful",
        "direction": "Front",
        "color": "White",
        "function": "ASSERT",
    },
    "transformer": {
        "face": "Wrathful",
        "direction": "Right",
        "color": "Red",
        "function": "YIELD",
    },
    "dissipator": {
        "face": "Joyful",
        "direction": "Left",
        "color": "Green",
        "function": "ADAPT",
    },
    "boundary": {
        "face": "Neutral",
        "direction": "Back",
        "color": "Blue",
        "function": "WAIT",
    },
}

MANTRA_MAP = {
    "111111": "Om",
    "000000": "Mani",
    "101010": "Padme",
    "010101": "Hum",
    "111000": "Om",
    "000111": "Mani",
    "110011": "Padme",
    "001100": "Hum",
}

MUDRA_TOOL_MAP = {
    "Qian": "Right hand holds vajra",
    "Kun": "Left hand holds lotus",
    "Zhen": "Hand holds wheel",
    "Kan": "Hand holds mirror",
    "Gen": "Hand holds rope",
    "Xun": "Hand holds sword",
    "Li": "Hand holds banner",
    "Dui": "Hand holds vase",
}

MIRROR_BIN = {
    "0": "1",
    "1": "0",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_trigram_lookup(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out[row.get("trigram_name", "").strip()] = row
    return out


def load_csv_hex_lookup(path: Path) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hid = int(row["hexagram_id"])
            out.setdefault(hid, []).append(row)
    return out


def derive_eyes_from_trigram_order(line_rows: list[dict]) -> list[dict]:
    ordered = sorted(line_rows, key=lambda r: int(r["line_number"]))
    eyes = []
    for row in ordered:
        line_state = row.get("base_state") or row.get("ternary_state", "unknown")
        eyes.append(
            {
                "eye_number": int(row["line_number"]),
                "position": row.get("position"),
                "trigram": row.get("trigram"),
                "state": line_state.lower(),
                "direction": row.get("direction", "").lower(),
                "is_stressed": row.get("is_stressed", "").lower() == "true",
                "is_activated": row.get("is_activated", "").lower() == "true",
                "category": row.get("category"),
            }
        )
    return eyes


def invert_binary(binary: str) -> str:
    return "".join(MIRROR_BIN.get(ch, ch) for ch in binary)


def palindrome_bins() -> set[str]:
    seen = set()
    for i in range(1, 65):
        raw = f"{i:06b}"
        rev = raw[::-1]
        seen.add(rev)
        seen.add(invert_binary(raw))
    return seen


def shotgun_expand(hexagram_ids: list[int]) -> list[dict]:
    unicode_base = 0x4DC0
    arms: list[dict] = []

    mirror_bins = palindrome_bins()
    source_counter = 0

    for hid in hexagram_ids:
        hex_entry = verified.get("hexagram_by_id", {}).get(str(hid)) or next(
            (x for x in verified.get("hexagrams", []) if int(x.get("id", -1)) == hid), {}
        )
        if not hex_entry:
            continue

        hname = hex_entry.get("name", "")
        binary = hex_entry.get("binary", "")
        unicode_symbol = chr(unicode_base - 1 + hid)
        upper_name = hex_entry.get("upper_trigram", "")
        lower_name = hex_entry.get("lower_trigram", "")

        cat_rows = category_rows.get(hid, [])
        cat_row = cat_rows[0] if cat_rows else {}
        category = cat_row.get("category", "")
        action = cat_row.get("action", "")
        yang_count = int(cat_row.get("yang_count", "0") or "0")
        yin_count = int(cat_row.get("yin_count", "0") or "0")
        dominant = cat_row.get("dominant", "")
        is_palindromic = str(cat_row.get("is_palindromic", "")).lower() == "true"
        is_dual = str(cat_row.get("is_dual", "")).lower() == "true"

        upper_trigram_meta = trigram_lookup.get(upper_name, {})
        lower_trigram_meta = trigram_lookup.get(lower_name, {})
        face = FACE_MAP.get(category, {})
        mudra_tool = MUDRA_TOOL_MAP.get(upper_name, "")
        eyes = derive_eyes_from_trigram_order(yao_rows.get(hid, []))
        yao_states = "".join(
            ("1" if eye["state"] in {"yang", "yao"} else "0") for eye in eyes
        )

        primary = {
            "hexagram_id": hid,
            "arm_name": f"{hid:02d}-{hname}",
            "unicode": unicode_symbol,
            "binary": binary,
            "mantra": MANTRA_MAP.get(binary, f"mantra-{binary}"),
            "mudra": unicode_symbol,
            "mudra_tool": mudra_tool,
            "upper_trigram": upper_name,
            "lower_trigram": lower_name,
            "upper_realm": upper_name,
            "lower_realm": lower_name,
            "realm_direction": f"{upper_name}/{lower_name}",
            "trigram_meta": {
                "upper": upper_trigram_meta,
                "lower": lower_trigram_meta,
            },
            "category": category,
            "action": action,
            "method_of_compassion": category,
            "response_to_suffering": action,
            "face": face.get("face", ""),
            "direction": face.get("direction", ""),
            "color": face.get("color", ""),
            "function": face.get("function", ""),
            "category_polarity": cat_row.get("category_polarity", ""),
            "action_polarity": cat_row.get("action_polarity", ""),
            "yang_count": yang_count,
            "yin_count": yin_count,
            "dominant": dominant,
            "is_palindromic": is_palindromic,
            "is_dual": is_dual,
            "yao_count": len(eyes),
            "eyes": eyes,
            "shotgun_role": "primary",
            "shotgun_source": "king_wen_64_verified.json",
            "source_sequence": source_counter,
        }
        arms.append(primary)
        source_counter += 1

        eye_counter = 0
        for eye in eyes:
            mirror_bin = invert_binary(yao_states) if yao_states else invert_binary(binary)
            arms.append(
                {
                    "hexagram_id": hid,
                    "arm_name": f"{hid:02d}-{hname}-eye-{eye['eye_number']}",
                    "unicode": unicode_symbol,
                    "binary": binary,
                    "mantra": MANTRA_MAP.get(mirror_bin, f"mantra-{mirror_bin}"),
                    "mudra": unicode_symbol,
                    "mudra_tool": mudra_tool,
                    "upper_trigram": upper_name,
                    "lower_trigram": lower_name,
                    "upper_realm": upper_name,
                    "lower_realm": lower_name,
                    "realm_direction": f"{upper_name}/{lower_name}",
                    "trigram_meta": {
                        "upper": upper_trigram_meta,
                        "lower": lower_trigram_meta,
                    },
                    "category": category,
                    "action": action,
                    "method_of_compassion": category,
                    "response_to_suffering": action,
                    "face": face.get("face", ""),
                    "direction": face.get("direction", ""),
                    "color": face.get("color", ""),
                    "function": face.get("function", ""),
                    "category_polarity": cat_row.get("category_polarity", ""),
                    "action_polarity": cat_row.get("action_polarity", ""),
                    "yang_count": yang_count,
                    "yin_count": yin_count,
                    "dominant": dominant,
                    "is_palindromic": is_palindromic,
                    "is_dual": is_dual,
                    "yao_count": len(eyes),
                    "eyes": [eye],
                    "shotgun_role": "eye",
                    "shotgun_axis": f"eye-{eye['eye_number']}",
                    "shotgun_source": "DATASETS/kingwen_oracle_yao_lines (1).csv",
                    "source_sequence": source_counter,
                    "mirror_binary": mirror_bin,
                }
            )
            eye_counter += 1
            source_counter += 1

        mirror_bin = invert_binary(binary)
        arms.append(
            {
                "hexagram_id": hid,
                "arm_name": f"{hid:02d}-{hname}-mirror",
                "unicode": unicode_symbol,
                "binary": binary,
                "mantra": MANTRA_MAP.get(mirror_bin, f"mantra-{mirror_bin}"),
                "mudra": unicode_symbol,
                "mudra_tool": mudra_tool,
                "upper_trigram": upper_name,
                "lower_trigram": lower_name,
                "upper_realm": upper_name,
                "lower_realm": lower_name,
                "realm_direction": f"{upper_name}/{lower_name}",
                "trigram_meta": {
                    "upper": upper_trigram_meta,
                    "lower": lower_trigram_meta,
                },
                "category": category,
                "action": action,
                "method_of_compassion": category,
                "response_to_suffering": action,
                "face": face.get("face", ""),
                "direction": face.get("direction", ""),
                "color": face.get("color", ""),
                "function": face.get("function", ""),
                "category_polarity": cat_row.get("category_polarity", ""),
                "action_polarity": cat_row.get("action_polarity", ""),
                "yang_count": yang_count,
                "yin_count": yin_count,
                "dominant": dominant,
                "is_palindromic": is_palindromic,
                "is_dual": is_dual,
                "yao_count": len(eyes),
                "eyes": eyes,
                "shotgun_role": "mirror",
                "shotgun_binary": mirror_bin,
                "shotgun_source": "king_wen_64_verified.json",
                "source_sequence": source_counter,
            }
        )
        source_counter += 1

    return arms


def main() -> int:
    global verified, category_rows, yao_rows, trigram_lookup
    verified = load_json(VERIFIED_PATH)
    trigram_lookup = load_trigram_lookup(TRIGRAM_CSV)
    category_rows = load_csv_hex_lookup(CATEGORY_CSV)
    yao_rows = load_csv_hex_lookup(YAO_LINES_CSV)

    hex_ids = [i for i in range(1, 65)]
    arms = shotgun_expand(hex_ids)
    payload = {
        "metadata": {
            "name": "AvalokiteshvaraShotgun",
            "mode": "shotgun-1000",
            "count": len(arms),
            "sources": [
                str(VERIFIED_PATH.relative_to(ROOT)),
                str(TRIGRAM_CSV.relative_to(ROOT)),
                str(CATEGORY_CSV.relative_to(ROOT)),
                str(YAO_LINES_CSV.relative_to(ROOT)),
            ],
            "expansion": "primary + 6 eyes + mirror per source hexagram",
            "immutable": True,
        },
        "arms": arms,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} with {len(arms)} arms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
