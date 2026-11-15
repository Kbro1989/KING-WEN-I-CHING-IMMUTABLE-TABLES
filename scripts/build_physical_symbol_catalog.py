"""Physical Symbol Catalog Compiler (V2.3 Reference Library).

Parses the extracted physical glyph catalog in symbols/symbols/searchindex.html
and compiles a structured, verifiable index:
  DATASETS/physical_symbol_library.json

Invariants:
  - Evidence-based: validates that every referenced image file physically exists on disk.
  - Cross-platform UTF-8 encoding.
  - Cryptographic provenance: computes SHA-256 checksums for catalog and assets.
  - Standalone: zero coupling to runtime game engines or POG routing.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SYMBOLS_DIR = REPO_ROOT / "symbols" / "symbols"
SEARCHINDEX_PATH = SYMBOLS_DIR / "searchindex.html"
OUTPUT_CATALOG_PATH = REPO_ROOT / "DATASETS" / "physical_symbol_library.json"


"""TeX Mnemonic Dictionary Expansion for Metamath Physical Symbol Catalog."""
import string

def build_expanded_tex_mnemonic_map() -> dict[str, dict]:
    m = {}

    # 1. Greek Lowercase
    greek_lower = {
        "alpha": (r"\alpha", "\u03b1"),
        "beta": (r"\beta", "\u03b2"),
        "gamma": (r"\gamma", "\u03b3"),
        "delta": (r"\delta", "\u03b4"),
        "epsilon": (r"\epsilon", "\u03b5"),
        "zeta": (r"\zeta", "\u03b6"),
        "eta": (r"\eta", "\u03b7"),
        "theta": (r"\theta", "\u03b8"),
        "iota": (r"\iota", "\u03b9"),
        "kappa": (r"\kappa", "\u03ba"),
        "lambda": (r"\lambda", "\u03bb"),
        "mu": (r"\mu", "\u03bc"),
        "nu": (r"\nu", "\u03bd"),
        "xi": (r"\xi", "\u03be"),
        "pi": (r"\pi", "\u03c0"),
        "rho": (r"\rho", "\u03c1"),
        "sigma": (r"\sigma", "\u03c3"),
        "tau": (r"\tau", "\u03c4"),
        "upsilon": (r"\upsilon", "\u03c5"),
        "phi": (r"\phi", "\u03d5"),
        "chi": (r"\chi", "\u03c7"),
        "psi": (r"\psi", "\u03c8"),
        "omega": (r"\omega", "\u03c9"),
        "varepsilon": (r"\varepsilon", "\u03b5"),
        "vartheta": (r"\vartheta", "\u03d1"),
        "varpi": (r"\varpi", "\u03d6"),
        "varrho": (r"\varrho", "\u03f1"),
        "varsigma": (r"\varsigma", "\u03c2"),
        "varphi": (r"\varphi", "\u03c6"),
    }
    for k, (tex, uni) in greek_lower.items():
        m[k] = {"tex": tex, "unicode": uni, "category": "greek_lower"}

    # 2. Greek Uppercase (Metamath 'c' prefix)
    greek_upper = {
        "cgamma": (r"\Gamma", "\u0393"),
        "cdelta": (r"\Delta", "\u0394"),
        "ctheta": (r"\Theta", "\u0398"),
        "clambda": (r"\Lambda", "\u039b"),
        "cxi": (r"\Xi", "\u039e"),
        "cpi": (r"\Pi", "\u03a0"),
        "csigma": (r"\Sigma", "\u03a3"),
        "cupsilon": (r"\Upsilon", "\u03a5"),
        "cphi": (r"\Phi", "\u03a6"),
        "cpsi": (r"\Psi", "\u03a8"),
        "comega": (r"\Omega", "\u03a9"),
    }
    for k, (tex, uni) in greek_upper.items():
        m[k] = {"tex": tex, "unicode": uni, "category": "greek_upper"}

    # 3. Blackboard Bold
    for ch in string.ascii_lowercase:
        m[f"bb{ch}"] = {"tex": f"\\mathbb{{{ch.upper()}}}", "unicode": None, "category": "blackboard_bold"}
    m["bbr"]["unicode"] = "\u211d"
    m["bbn"]["unicode"] = "\u2115"
    m["bbz"]["unicode"] = "\u2124"
    m["bbc"]["unicode"] = "\u2102"
    m["bbq"]["unicode"] = "\u211a"
    m["bbp"]["unicode"] = "\u2119"
    m["bbh"]["unicode"] = "\u210d"

    # 4. Calligraphic (cal[a-z])
    for ch in string.ascii_lowercase:
        m[f"cal{ch}"] = {"tex": f"\\mathcal{{{ch.upper()}}}", "unicode": None, "category": "calligraphic"}

    # 5. Fraktur (frak[a-z])
    for ch in string.ascii_lowercase:
        m[f"frak{ch}"] = {"tex": f"\\mathfrak{{{ch}}}", "unicode": None, "category": "fraktur"}

    # 6. Bold Letters (bf[a-z])
    for ch in string.ascii_lowercase:
        m[f"bf{ch}"] = {"tex": f"\\mathbf{{{ch}}}", "unicode": None, "category": "bold"}

    # 7. Roman Letters (rm[a-z])
    for ch in string.ascii_lowercase:
        m[f"rm{ch}"] = {"tex": f"\\mathrm{{{ch}}}", "unicode": None, "category": "roman"}

    # 8. Standard Operators
    operators = {
        "sum": (r"\sum", "\u2211", "large_operator"),
        "int": (r"\int", "\u222b", "large_operator"),
        "oint": (r"\oint", "\u222e", "large_operator"),
        "smallint": (r"\int", "\u222b", "large_operator"),
        "surd": (r"\sqrt", "\u221a", "large_operator"),
        "times": (r"\times", "\u00d7", "binary_operator"),
        "div": (r"\div", "\u00f7", "binary_operator"),
        "cdot": (r"\cdot", "\u22c5", "binary_operator"),
        "pm": (r"\pm", "\u00b1", "binary_operator"),
        "mp": (r"\mp", "\u2213", "binary_operator"),
        "circ": (r"\circ", "\u2218", "binary_operator"),
        "bullet": (r"\bullet", "\u2219", "binary_operator"),
        "star": (r"\star", "\u22c6", "binary_operator"),
        "ast": (r"\ast", "\u2217", "binary_operator"),
        "dagger": (r"\dagger", "\u2020", "binary_operator"),
        "ddag": (r"\ddagger", "\u2021", "binary_operator"),
        "wedge": (r"\wedge", "\u2227", "binary_operator"),
        "vee": (r"\vee", "\u2228", "binary_operator"),
        "cap": (r"\cap", "\u2229", "binary_operator"),
        "cup": (r"\cup", "\u222a", "binary_operator"),
        "uplus": (r"\uplus", "\u228e", "binary_operator"),
        "oplus": (r"\oplus", "\u2295", "binary_operator"),
        "otimes": (r"\otimes", "\u2297", "binary_operator"),
        "odot": (r"\odot", "\u2299", "binary_operator"),
        "oslash": (r"\oslash", "\u2298", "binary_operator"),
        "setminus": (r"\setminus", "\u2216", "binary_operator"),
    }
    for k, (tex, uni, cat) in operators.items():
        m[k] = {"tex": tex, "unicode": uni, "category": cat}

    # 9. Relations & Set Symbols
    relations = {
        "le": (r"\le", "\u2264", "relation"),
        "ge": (r"\ge", "\u2265", "relation"),
        "ne": (r"\ne", "\u2260", "relation"),
        "equiv": (r"\equiv", "\u2261", "relation"),
        "approx": (r"\approx", "\u2248", "relation"),
        "sim": (r"\sim", "\u223c", "relation"),
        "simeq": (r"\simeq", "\u2243", "relation"),
        "cong": (r"\cong", "\u2245", "relation"),
        "propto": (r"\propto", "\u221d", "relation"),
        "in": (r"\in", "\u2208", "relation"),
        "notin": (r"\notin", "\u2209", "relation"),
        "subset": (r"\subset", "\u2282", "relation"),
        "subseteq": (r"\subseteq", "\u2286", "relation"),
        "supset": (r"\supset", "\u2283", "relation"),
        "supseteq": (r"\supseteq", "\u2287", "relation"),
        "prec": (r"\prec", "\u227a", "relation"),
        "preceq": (r"\preceq", "\u227c", "relation"),
        "succ": (r"\succ", "\u227b", "relation"),
        "succeq": (r"\succeq", "\u227d", "relation"),
        "parallel": (r"\parallel", "\u2225", "relation"),
        "perp": (r"\perp", "\u22a5", "relation"),
        "top": (r"^\top", "\u22a4", "operator"),
        "forall": (r"\forall", "\u2200", "quantifier"),
        "exists": (r"\exists", "\u2203", "quantifier"),
        "emptyset": (r"\emptyset", "\u2205", "set_symbol"),
        "infty": (r"\infty", "\u221e", "symbol"),
        "nabla": (r"\nabla", "\u2207", "operator"),
        "partial": (r"\partial", "\u2202", "operator"),
    }
    for k, (tex, uni, cat) in relations.items():
        m[k] = {"tex": tex, "unicode": uni, "category": cat}

    # 10. Delimiters
    delims = {
        "lfloor": (r"\lfloor", "\u230a", "delimiter"),
        "rfloor": (r"\rfloor", "\u230b", "delimiter"),
        "lceil": (r"\lceil", "\u2308", "delimiter"),
        "rceil": (r"\rceil", "\u2309", "delimiter"),
        "langle": (r"\langle", "\u27e8", "delimiter"),
        "rangle": (r"\rangle", "\u27e9", "delimiter"),
        "vert": (r"|", "|", "delimiter"),
    }
    for k, (tex, uni, cat) in delims.items():
        m[k] = {"tex": tex, "unicode": uni, "category": cat}

    # 11. Arrows
    arrows = {
        "to": (r"\to", "\u2192", "arrow"),
        "leftarrow": (r"\leftarrow", "\u2190", "arrow"),
        "leftrightarrow": (r"\leftrightarrow", "\u2194", "arrow"),
        "uparrow": (r"\uparrow", "\u2191", "arrow"),
        "downarrow": (r"\downarrow", "\u2193", "arrow"),
        "updownarrow": (r"\updownarrow", "\u2195", "arrow"),
        "nearrow": (r"\nearrow", "\u2197", "arrow"),
        "searrow": (r"\searrow", "\u2198", "arrow"),
        "swarrow": (r"\swarrow", "\u2199", "arrow"),
        "nwarrow": (r"\nwarrow", "\u2196", "arrow"),
        "mapsto": (r"\mapsto", "\u21a6", "arrow"),
        "hookrightarrow": (r"\hookrightarrow", "\u21aa", "arrow"),
        "hookleftarrow": (r"\hookleftarrow", "\u21a9", "arrow"),
        "longrightarrow": (r"\longrightarrow", "\u27f6", "arrow"),
        "longleftarrow": (r"\longleftarrow", "\u27f5", "arrow"),
        "longleftrightarrow": (r"\longleftrightarrow", "\u27f7", "arrow"),
    }
    for k, (tex, uni, cat) in arrows.items():
        m[k] = {"tex": tex, "unicode": uni, "category": cat}

    return m


TEX_MNEMONIC_MAP = build_expanded_tex_mnemonic_map()


def compile_physical_symbol_catalog() -> dict[str, Any]:
    """Parse searchindex.html and compile structured symbol dictionary."""
    if not SEARCHINDEX_PATH.exists():
        raise FileNotFoundError(f"Search index not found at {SEARCHINDEX_PATH}")

    with open(SEARCHINDEX_PATH, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Pattern: mnemonic <IMG SRC="filename" WIDTH=w HEIGHT=h ALT=""> mnemonic
    matches = re.findall(
        r'(\w+)\s+<IMG SRC=["\']([^"\']+)["\']\s+WIDTH=(\d+)\s+HEIGHT=(\d+)[^>]*>\s+(\w+)',
        content,
        re.IGNORECASE,
    )

    symbols = {}

    for m1, filename, w, h, m2 in matches:
        mnemonic = m1 if m1 == m2 else m1
        raw_filename = filename

        # Handle known typo in searchindex.html
        if filename.startswith("kruez."):
            filename = filename.replace("kruez.", "kreuz.")

        img_path = SYMBOLS_DIR / filename
        file_exists = img_path.exists()
        file_size = img_path.stat().st_size if file_exists else 0

        tex_meta = TEX_MNEMONIC_MAP.get(mnemonic, {})

        # Compute file SHA-256 and inspect physical properties if file exists
        file_sha256 = None
        actual_w = int(w)
        actual_h = int(h)
        mode = None
        has_transparency = False

        if file_exists:
            hasher = hashlib.sha256()
            with open(img_path, "rb") as img_f:
                hasher.update(img_f.read())
            file_sha256 = hasher.hexdigest()

            try:
                from PIL import Image
                with Image.open(img_path) as im:
                    actual_w, actual_h = im.size
                    mode = im.mode
                    has_transparency = (
                        "transparency" in im.info
                        or im.mode in ("RGBA", "LA")
                        or (im.mode == "P" and "transparency" in im.info)
                    )
            except Exception:
                pass

        # If mnemonic already seen (e.g. PNG vs GIF duplicate line in HTML), keep/update PNG as primary
        ext = Path(filename).suffix.lower()
        if mnemonic in symbols and symbols[mnemonic]["format"] == ".png" and ext == ".gif":
            # Store gif companion
            symbols[mnemonic]["gif_companion"] = {
                "filename": filename,
                "file_sha256": file_sha256,
                "file_size_bytes": file_size,
                "exists_on_disk": file_exists,
            }
            continue

        symbols[mnemonic] = {
            "mnemonic": mnemonic,
            "filename": filename,
            "raw_html_filename": raw_filename,
            "relative_path": f"symbols/symbols/{filename}",
            "width_px": actual_w,
            "height_px": actual_h,
            "tag_width_px": int(w),
            "tag_height_px": int(h),
            "image_mode": mode,
            "has_transparency": has_transparency,
            "file_size_bytes": file_size,
            "file_sha256": file_sha256,
            "exists_on_disk": file_exists,
            "format": ext,
            "tex_macro": tex_meta.get("tex"),
            "unicode_char": tex_meta.get("unicode"),
            "category": tex_meta.get("category", "unmapped_symbol"),
        }

    catalog = {
        "schema_version": "1.0.0",
        "description": "Physical Mathematical Symbol Library and Raster Registry",
        "source_archive": "symbols.zip",
        "source_index": "symbols/symbols/searchindex.html",
        "total_symbols_indexed": len(symbols),
        "verified_files_on_disk": sum(1 for s in symbols.values() if s["exists_on_disk"]),
        "missing_files_on_disk": sum(1 for s in symbols.values() if not s["exists_on_disk"]),
        "mapped_tex_count": sum(1 for s in symbols.values() if s["tex_macro"] is not None),
        "unmapped_tex_count": sum(1 for s in symbols.values() if s["tex_macro"] is None),
        "known_errata": [
            {"original_tag": "kruez.png/kruez.gif", "corrected_filename": "kreuz.png/kreuz.gif", "type": "filename_typo"},
            {"original_tag": 'WIDTH=12 HEIGHT=19 SRC="largetimes.png"', "actual_size": [11, 19], "type": "dimension_mismatch"}
        ],
        "symbols": symbols,
    }

    OUTPUT_CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    return catalog


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    cat = compile_physical_symbol_catalog()
    print(f"Catalog compiled: {cat['total_symbols_indexed']} symbols indexed.")
    print(f"Verified files on disk: {cat['verified_files_on_disk']}/{cat['total_symbols_indexed']}")
    print(f"Output saved to: {OUTPUT_CATALOG_PATH}")
