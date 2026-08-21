#!/usr/bin/env python3
"""
Build per-hex training data for 64 specialized hexagram models.

Source of truth:
- collapse_full_128_output.json for expanded[]/inject_site/yao_vocabulary/expanded_vector
- hexagram_coder_archetypes.csv for archetype metadata and opposition_pair annotations
- hexagram_shotgun_matcher.py for paper-to-hex routing

Outputs:
- output/per_hex_training/{hex_id}.jsonl : one JSON record per paper routed to that hex
- output/per_hex_training/manifest.json : hex-level stats, paper counts, adversarial notes

No hardcoded routing. No synthetic fallbacks. If shotgun matcher is missing fields,
fix shotgun matcher, not this script.
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = (Path.home() / "Desktop" / "zotero/learning-corpus/.text")
OUT_DIR = ROOT / "output/per_hex_training"
SHOTGUN = ROOT / "collapse_full_128_output.json"
ARCHETYPES = ROOT / "output/hexagram_coder_archetypes.csv"

VEC_KEYS = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
STOP = {
    "the","and","for","with","from","that","this","they","have","been","were","their",
    "would","could","should","which","where","when","what","than","then","them","also",
    "more","most","some","into","over","such","only","other","many","much","each","about",
    "because","through","during","before","after","above","below","between","same","different",
    "often","however","although","while","since","until","both","few","most","own","same",
    "too","very","just","still","already","ever","never","always","usually","sometimes",
    "really","perhaps","certainly","definitely","probably","possible","likely","clear",
    "known","given","shown","found","used","using","based","proposed","presented","introduced",
    "developed","designed","implemented","evaluated","compared","analyzed","discussed",
    "reported","demonstrated","shown","observed","results","method","approach","model",
    "models","paper","propose","present","introduce","show","result","performance","accuracy",
    "improvement","state","art","using","based","et","al","fig","figure","table","equation",
    "section","appendix","references","abstract","introduction","conclusion","future","work",
    "we","our","can","may","will","not","are","was","were","been","being","has","had",
    "does","did","say","said","could","would","should","might","must","shall","this","that",
    "these","those","there","here","where","when","how","what","why","who","whom","whose",
    "which","while","although","because","since","until","before","after","during","about",
    "against","between","through","within","without","under","over","above","below","upon",
    "between","among","throughout","despite","toward","towards","upon","regarding",
    "concerning","including","plus","minus","times","divided","equals","equal","less",
    "greater","than","less","greater","equal","one","two","three","four","five","six",
    "seven","eight","nine","zero","first","second","third","fourth","fifth","last","next",
    "previous","new","old","large","small","high","low","long","short","good","bad","best",
    "worst","better","worse","much","many","few","several","some","any","all","every","each",
    "both","either","neither","other","another","same","different","such","no","yes","true",
    "false","right","wrong","correct","incorrect","possible","impossible","necessary",
    "sufficient","important","significant","relevant","irrelevant","related","unrelated",
    "similar","different","common","rare","frequent","infrequent","typical","atypical",
    "normal","abnormal","standard","nonstandard","expected","unexpected","known","unknown",
    "given","fixed","variable","constant","changing","static","dynamic","stable","unstable",
    "simple","complex","easy","difficult","hard","soft","fast","slow","early","late",
    "recent","ancient","modern","traditional","contemporary","classic","novel","current",
    "future","past","present","ongoing","continuous","discrete","finite","infinite","single",
    "multiple","double","triple","quadruple","arxiv","abs","doi","https","http","org","com",
    "edu","pdf","html","xml","json","csv","tsv","txt","md","yml","yaml","toml","ini","cfg",
    "conf","sh","bash","zsh","fish","py","js","ts","jsx","tsx","css","scss","less","html",
    "java","cpp","c","h","rs","go","rb","php","swift","kt","scala","r","m","mat","ipynb",
    "sql","graphql","proto","cap","md5","sha","base64","zip","tar","gz","bz2","xz","dmg",
    "exe","so","dll","lib","a","o","obj","class","jar","war","egg","whl","deb","rpm","apk",
    "ipa","appx","msi","cab","iso","img","vhd","vhdx","qcow2","raw","bin","hex","srec",
    "mot","elf","pe","mach-o","wasm","github","gitlab","bitbucket","git","svn","hg","bzr",
    "cvs","npm","yarn","pnpm","pip","conda","mamba","poetry","cargo","stack","cabal","mix",
    "rebar","lein","sbt","mvn","gradle","ant","make","cmake","ninja","meson","bazel","buck",
    "pants","please","shard","dub","vcpkg","conan","portage","apt","yum","dnf","brew",
    "choco","scoop","winget","apt-get","yum","dnf","pacman","zypper","emerge","pkg","apk",
    "opkg","pipx","pipenv","virtualenv","venv"," micromamba","asdf","fnm","nvm","pyenv",
    "rbenv","nodenv","goenv","jenv","phpenv","perlbrew","plenv","swiftenv","hsenv","cargo",
    "rustup","gvm","sdkman","jabba","antigen","antibody","basher","batz","dotfiles",
    "oh-my-zsh","prezto","zinit","zgen","zplug","zap","starship","powerlevel10k","p10k",
    "oh-my-posh","clink","psreadline","psake","cake","fake","invoke","fabric","pyinvoke",
    "ansible","salt","puppet","chef","terraform","cloudformation","cdk","pulumi",
    "crossplane","terragrunt","atlantis","driftctl","checkov","tfsec","sops","vault",
    "boundary","consul","nomad","waypoint","fabio","traefik","envoy","istio","linkerd",
    "kuma","osm","cilium","calico","flannel","weave","kube-router","romana",
}


def _tokenize(text: str) -> Counter:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_/\-]*", text.lower())
    tokens = [w for w in words if w not in STOP and len(w) > 2]
    return Counter(tokens)


def _cosine_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in VEC_KEYS)
    mag_a = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in VEC_KEYS))
    mag_b = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in VEC_KEYS))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _text_overlap(paper_tokens: Counter, text: str) -> float:
    if not text:
        return 0.0
    toks = set(re.findall(r"[A-Za-z0-9_/\-]+", text.lower()))
    toks = {t for t in toks if t not in STOP and len(t) > 2}
    if not toks:
        return 0.0
    hits = sum(1 for t in toks if paper_tokens.get(t, 0) > 0)
    return hits / max(len(toks), 1)


def load_shotgun() -> Dict[str, Any]:
    with SHOTGUN.open(encoding="utf-8") as f:
        return json.load(f)


def load_archetypes() -> Dict[str, Dict[str, str]]:
    rows = []
    with ARCHETYPES.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["hexagram_id"]: r for r in rows}


def score_paper_vs_hex(
    paper_text: str,
    hex_data: Dict[str, Any],
    archetype: Dict[str, str],
) -> tuple[float, float, float]:
    tokens = _tokenize(paper_text)
    inject = hex_data.get("inject_site", {})
    reason = inject.get("reason", "")
    yao = hex_data.get("yao_vocabulary", {})
    vec = hex_data.get("expanded_vector", {})

    reason_score = _text_overlap(tokens, reason) * 4.0
    yao_score = (
        sum(_text_overlap(tokens, label) for label in yao.values() if label)
        / max(len([v for v in yao.values() if v]), 1)
    ) * 2.0

    archetype_text = " ".join([
        archetype.get("name", ""),
        archetype.get("action", ""),
        archetype.get("archetype", ""),
        archetype.get("coder_specialty", ""),
        archetype.get("rs3_actionable", ""),
    ])
    archetype_score = _text_overlap(tokens, archetype_text) * 3.0

    text_score = reason_score + yao_score + archetype_score
    vector_score = _cosine_similarity({k: 1.0 for k in VEC_KEYS}, vec) * 1.0
    combined = text_score + vector_score
    return text_score, vector_score, combined


def build_pair_map(archetypes: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    pair_map = {}
    for hid, row in archetypes.items():
        if row.get("opposition_pair") == "true" and row.get("inversion_pair_id"):
            parts = row["inversion_pair_id"].split("_")[1:]
            if len(parts) == 2:
                pair_map[hid] = parts[0] if parts[1] == hid else parts[1]
    return pair_map


def rank_hexes_for_paper(
    paper_text: str,
    shotgun: Dict[str, Any],
    archetypes: Dict[str, Dict[str, str]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    scores = []
    for hex_data in shotgun.get("expanded", []):
        hid = str(hex_data.get("hexagram_id", ""))
        text_score, vector_score, combined = score_paper_vs_hex(
            paper_text, hex_data, archetypes.get(hid, {})
        )
        scores.append((hid, combined, text_score, vector_score, hex_data))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = [(hid, combined, {"text_score": ts, "vector_score": vs, "hex_data": hd})
           for hid, combined, ts, vs, hd in scores[:top_k]]

    pair_map = build_pair_map(archetypes)
    penalized = []
    for hid, score, meta in top:
        mate = pair_map.get(hid)
        if mate:
            mate_score = next((s for h, s, _ in top if h == mate), 0.0)
            if score < mate_score:
                score = max(0.0, score - 0.4 * score)
        penalized.append((hid, score, meta))

    penalized.sort(key=lambda x: x[1], reverse=True)
    results = []
    for hid, score, meta in penalized:
        hd = meta["hex_data"]
        arch = archetypes.get(hid, {})
        results.append({
            "hexagram_id": hid,
            "name": arch.get("name", ""),
            "action": arch.get("action", ""),
            "archetype": arch.get("archetype", ""),
            "coder_specialty": arch.get("coder_specialty", ""),
            "opposition_pair": arch.get("opposition_pair", ""),
            "inversion_pair_id": arch.get("inversion_pair_id", ""),
            "pov_contrast": arch.get("pov_contrast", ""),
            "score": round(score, 4),
            "text_score": round(meta["text_score"], 4),
            "vector_score": round(meta["vector_score"], 4),
            "vector": hd.get("expanded_vector", {}),
            "inject_site": hd.get("inject_site", {}),
            "yao_vocabulary": hd.get("yao_vocabulary", {}),
        })
    return results


def build_training_set(limit: Optional[int] = None) -> Dict[str, Any]:
    shotgun = load_shotgun()
    archetypes = load_archetypes()
    files = sorted(TEXT_DIR.glob("*.txt"))
    if limit:
        files = files[:limit]

    hex_bins: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    paper_meta: Dict[str, Dict[str, Any]] = {}
    ranked_by_paper: Dict[str, List[Dict[str, Any]]] = {}

    for path in files:
        paper_id = path.stem
        text = path.read_text(encoding="utf-8", errors="ignore")
        if len(text.strip()) < 200:
            continue
        ranked = rank_hexes_for_paper(text, shotgun, archetypes, top_k=5)
        if not ranked:
            continue
        ranked_by_paper[paper_id] = ranked
        top = ranked[0]
        paper_meta[paper_id] = {
            "paper_id": paper_id,
            "filename": path.name,
            "char_count": len(text),
            "top_hexagram_id": top["hexagram_id"],
            "top_score": top["score"],
            "top_name": top["name"],
        }
        for rank, entry in enumerate(ranked, start=1):
            record = {
                "paper_id": paper_id,
                "rank": rank,
                "hexagram_id": entry["hexagram_id"],
                "name": entry["name"],
                "action": entry["action"],
                "archetype": entry["archetype"],
                "coder_specialty": entry["coder_specialty"],
                "opposition_pair": entry["opposition_pair"],
                "inversion_pair_id": entry["inversion_pair_id"],
                "pov_contrast": entry["pov_contrast"],
                "score": entry["score"],
                "text_score": entry["text_score"],
                "vector_score": entry["vector_score"],
                "vector": entry["vector"],
                "inject_site": entry["inject_site"],
                "yao_vocabulary": entry["yao_vocabulary"],
            }
            hex_bins[entry["hexagram_id"]].append(record)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source_shotgun": str(SHOTGUN),
        "source_archetypes": str(ARCHETYPES),
        "corpus_dir": str(TEXT_DIR),
        "paper_count": len(paper_meta),
        "hex_count": len(hex_bins),
        "hex_counts": {hid: len(bins) for hid, bins in sorted(hex_bins.items(), key=lambda x: int(x[0]))},
        "empty_hexes": [hid for hid in [str(i) for i in range(1, 65)] if hid not in hex_bins],
        "adversarial_pairs": [
            {
                "inversion_pair_id": row.get("inversion_pair_id", ""),
                "hex_a": row.get("hexagram_id"),
                "hex_b": pair_id.split("_")[1] if row.get("inversion_pair_id") else "",
                "name_a": row.get("name", ""),
                "pov_contrast": row.get("pov_contrast", ""),
            }
            for hid, row in archetypes.items()
            if row.get("opposition_pair") == "true"
            and (pair_id := row.get("inversion_pair_id", ""))
        ],
    }

    for hid, bins in hex_bins.items():
        out_path = OUT_DIR / f"{hid}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for rec in bins:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with (OUT_DIR / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


def main() -> None:
    manifest = build_training_set()
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
