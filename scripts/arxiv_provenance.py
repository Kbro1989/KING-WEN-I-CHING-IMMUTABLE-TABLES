#!/usr/bin/env python3
"""
arxiv_provenance.py — Deterministic arxiv paper → math provenance extractor.

Chain: arxiv_id → version → abs/html/pdf/source URLs → structured math records.

Usage:
    python3 scripts/arxiv_provenance.py 2006.11239
    python3 scripts/arxiv_provenance.py 2006.11239 --output DATASETS/provenance_2006.11239.json
"""

import argparse
import html as html_module
import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


ARXIV_ABS_BASE = "https://arxiv.org/abs/"
ARXIV_HTML_BASE = "https://arxiv.org/html/"
ARXIV_PDF_BASE = "https://arxiv.org/pdf/"
ARXIV_SOURCE_BASE = "https://arxiv.org/e-print/"


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch URL content with proper headers."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; MathParser/1.0; +https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES)"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} for {url}: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")


def fetch_binary(url: str, timeout: int = 60) -> bytes:
    """Fetch raw bytes (for TeX source archives)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; MathParser/1.0; +https://github.com/Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def extract_version(abs_html: str, arxiv_id: str) -> str:
    """Extract version from abs page HTML."""
    # Look for arXiv:XXXX.XXXXXvN pattern
    match = re.search(rf"arXiv:{re.escape(arxiv_id)}v(\d+)", abs_html)
    if match:
        return f"v{match.group(1)}"
    # Default to v1 if not found
    return "v1"


def extract_math_from_html(html_content: str) -> list:
    """
    Extract all math elements with their LaTeX annotations and MathML.
    
    Returns list of dicts with:
    - latex: raw LaTeX from <annotation encoding="application/x-tex"> or alttext
    - mathml: MathML content
    - context: surrounding text
    - equation_id: sequential ID
    - section_id: arxiv HTML id attribute (e.g., S2.p1.m1)
    - section: parsed section number
    - is_display: whether this is a display equation
    """
    results = []
    
    # Find all <math ...>...</math> blocks with their attributes
    math_pattern = re.compile(
        r'<math\s+([^>]*)>(.*?)</math>',
        re.DOTALL
    )
    
    annotation_pattern = re.compile(
        r'<annotation\s+encoding="application/x-tex"[^>]*>(.*?)</annotation>',
        re.DOTALL
    )
    
    for idx, match in enumerate(math_pattern.finditer(html_content)):
        math_attrs = match.group(1)
        math_inner = match.group(2)
        
        # Extract id attribute (section provenance)
        id_match = re.search(r'id="([^"]*)"', math_attrs)
        section_id = id_match.group(1) if id_match else None
        
        # Parse section from id (e.g., S2.p1.m1 -> section 2)
        section = None
        if section_id:
            sec_match = re.match(r'S(\d+)', section_id)
            if sec_match:
                section = int(sec_match.group(1))
        
        # Extract LaTeX from annotation or alttext
        latex_match = annotation_pattern.search(math_inner)
        if latex_match:
            latex = latex_match.group(1).strip()
        else:
            # Fallback to alttext attribute
            alttext_match = re.search(r'alttext="([^"]*)"', math_attrs)
            latex = alttext_match.group(1).strip() if alttext_match else ""
        
        # Unescape HTML entities. Raw arxiv HTML carries &gt; &lt; &amp; &nbsp;
        # inside the LaTeX annotation; leaving them corrupts relation operators
        # (e.g. \sum_{t&gt;1} instead of \sum_{t>1}).
        latex = html_module.unescape(latex)
        
        # Extract MathML (everything except the annotation)
        mathml = re.sub(r'<annotation[^>]*>.*?</annotation>', '', math_inner, flags=re.DOTALL).strip()
        
        # Get context: 200 chars before and after
        start = max(0, match.start() - 200)
        end = min(len(html_content), match.end() + 200)
        context = html_content[start:end]
        context = re.sub(r'<[^>]+>', ' ', context)
        context = re.sub(r'\s+', ' ', context).strip()
        
        # Determine if display equation from ID pattern
        # arxiv HTML IDs: S2.p1.m1 = paragraph math, S2.E1.m1 = equation math
        # The 'E' in the ID marks display equations
        is_display = False
        equation_number = None
        if section_id:
            eq_match = re.match(r'S(\d+)\.E(\d+)\.m(\d+)', section_id)
            if eq_match:
                is_display = True
                equation_number = eq_match.group(2)
                section = int(eq_match.group(1))
        
        results.append({
            "equation_id": idx + 1,
            "latex": latex,
            "mathml": mathml,
            "context": context,
            "section_id": section_id,
            "section": section,
            "is_display": is_display,
            "equation_number": equation_number,
            "source": "arxiv_html",
        })
    
    return results


def group_equations(math_records: list) -> list:
    """
    Group math fragments into complete equations.
    
    arxiv HTML fragments a single equation across multiple <math> tags:
      S2.E1.m1 + S2.E1.m2  ->  equation 1
    
    The 'E' key is equation identity; the 'm' suffix is a fragment index.
    Paragraph math (S2.p1.m1) is standalone and never grouped.
    
    Returns list of grouped equation dicts preserving fragment order.
    """
    groups = {}
    order = []
    
    for rec in math_records:
        sid = rec.get("section_id") or ""
        # Match S<sec>.E<eqn>.m<frag>
        m = re.match(r'S(\d+)\.E(\d+)\.m(\d+)$', sid)
        if m:
            key = (int(m.group(1)), int(m.group(2)))  # (section, equation)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append((int(m.group(3)), rec))
        else:
            # Standalone (paragraph or unlabeled) math
            key = ("standalone", rec["equation_id"])
            groups[key] = [(0, rec)]
            order.append(key)
    
    grouped = []
    for key in order:
        frags = sorted(groups[key], key=lambda x: x[0])
        recs = [f[1] for f in frags]
        
        if isinstance(key[0], int):
            section_num, eq_num = key
            # Join fragments in order
            joined_latex = "".join(r["latex"] for r in recs)
            grouped.append({
                "section": section_num,
                "equation_number": eq_num,
                "group_key": f"S{section_num}.E{eq_num}",
                "fragment_count": len(recs),
                "fragments": [
                    {"id": r.get("section_id"), "latex": r["latex"], "mathml": r["mathml"]}
                    for r in recs
                ],
                "latex": joined_latex,
                "mathml": "".join(r["mathml"] for r in recs),
                "context": recs[0]["context"],
                "is_display": True,
                "source": "arxiv_html",
            })
        else:
            # Standalone
            r = recs[0]
            grouped.append({
                "section": r.get("section"),
                "equation_number": None,
                "group_key": r.get("section_id"),
                "fragment_count": 1,
                "fragments": [
                    {"id": r.get("section_id"), "latex": r["latex"], "mathml": r["mathml"]}
                ],
                "latex": r["latex"],
                "mathml": r["mathml"],
                "context": r["context"],
                "is_display": False,
                "source": "arxiv_html",
            })
    
    return grouped


def extract_tex_equations(tex_source: str) -> list:
    """
    Extract math environments from raw LaTeX source.
    
    Captures the author's original markup — the top rung of the
    ground-truth ladder: TeX -> HTML/MathML -> PDF -> parser -> AST.
    """
    results = []
    
    # Display environments
    env_patterns = [
        (r'\\begin\{equation\}(.*?)\\end\{equation\}', 'equation'),
        (r'\\begin\{equation\*\}(.*?)\\end\{equation\*\}', 'equation*'),
        (r'\\begin\{align\}(.*?)\\end\{align\}', 'align'),
        (r'\\begin\{align\*\}(.*?)\\end\{align\*\}', 'align*'),
        (r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}', 'eqnarray'),
        (r'\\begin\{gather\}(.*?)\\end\{gather\}', 'gather'),
        (r'\\begin\{multline\}(.*?)\\end\{multline\}', 'multline'),
        (r'\\\[(.*?)\\\]', 'display_bracket'),
    ]
    
    for pattern, env_name in env_patterns:
        for m in re.finditer(pattern, tex_source, re.DOTALL):
            body = m.group(1).strip()
            if body:
                results.append({
                    "environment": env_name,
                    "latex": body,
                    "source": "arxiv_tex",
                    "label": None,
                })
    
    # Extract \label{} from each to get equation identity
    label_pattern = re.compile(r'\\label\{([^}]+)\}')
    for rec in results:
        lm = label_pattern.search(rec["latex"])
        if lm:
            rec["label"] = lm.group(1)
    
    return results


def extract_tex_macros(tex_source: str) -> dict:
    """
    Extract \\newcommand / \\def macro definitions from TeX source.

    Papers use author shorthand (\\bx, \\defeq, \\kl) that must be resolved
    before the TeX rung is comparable to the HTML rung. The HTML rung from
    arxiv's LaTeXML already has these expanded.
    """
    macros = {}

    pat_newcommand = re.compile(r"\\newcommand\s*\{?\\([a-zA-Z@]+)\}?\s*(?:\[(\d+)\])?\s*\{")
    for m in pat_newcommand.finditer(tex_source):
        name = m.group(1)
        nargs = m.group(2)
        i = m.end() - 1
        depth = 0
        body_start = i + 1
        j = i
        while j < len(tex_source):
            if tex_source[j] == "{":
                depth += 1
            elif tex_source[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        macros[name] = {"nargs": int(nargs) if nargs else 0, "body": tex_source[body_start:j]}

    pat_def = re.compile(r"\\def\s*\\([a-zA-Z@]+)\s*\{")
    for m in pat_def.finditer(tex_source):
        name = m.group(1)
        i = m.end() - 1
        depth = 0
        body_start = i + 1
        j = i
        while j < len(tex_source):
            if tex_source[j] == "{":
                depth += 1
            elif tex_source[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        macros[name] = {"nargs": 0, "body": tex_source[body_start:j]}

    return macros


def resolve_macros(latex: str, macros: dict, max_passes: int = 8) -> str:
    """
    Expand author macros in a LaTeX string.

    Manual left-to-right scanner (not re.sub) because N-arg macros must
    consume their argument groups as part of the match — re.sub continues
    scanning from the macro name, which re-emits consumed args as literals
    (e.g. \\Eb{q}{...} leaked a stray {q}).

    0-arg macros substitute directly. N-arg macros consume brace-matched
    arguments and substitute #1..#N. Iterates until stable so macro-of-macro
    chains resolve.
    """
    if not macros:
        return latex

    # Longest names first so \bepsilon beats \be
    names = sorted(macros.keys(), key=len, reverse=True)

    def read_group(s: str, pos: int):
        """Read a brace-matched group starting at pos. Returns (content, new_pos)."""
        while pos < len(s) and s[pos].isspace():
            pos += 1
        if pos < len(s) and s[pos] == "{":
            depth = 0
            start = pos + 1
            k = pos
            while k < len(s):
                if s[k] == "{":
                    depth += 1
                elif s[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            return s[start:k], k + 1
        elif pos < len(s):
            return s[pos], pos + 1
        return "", pos

    current = latex
    for _ in range(max_passes):
        out = []
        i = 0
        changed = False
        while i < len(current):
            if current[i] == "\\":
                # Try to match a macro name here
                matched = None
                for name in names:
                    if current.startswith("\\" + name, i):
                        after = i + 1 + len(name)
                        # must not be followed by another letter (longest-match guard)
                        if after < len(current) and current[after].isalpha():
                            continue
                        matched = name
                        break
                if matched:
                    info = macros[matched]
                    pos = i + 1 + len(matched)
                    body = info["body"]
                    if info["nargs"] > 0:
                        args = []
                        for _a in range(info["nargs"]):
                            arg, pos = read_group(current, pos)
                            args.append(arg)
                        expansion = body
                        for ai, arg in enumerate(args, start=1):
                            expansion = expansion.replace(f"#{ai}", arg)
                    else:
                        expansion = body
                    out.append(expansion)
                    i = pos
                    changed = True
                    continue
            out.append(current[i])
            i += 1
        current = "".join(out)
        if not changed:
            break

    return current


def try_fetch_tex_source(arxiv_id: str, version: str) -> Optional[dict]:
    """
    Attempt to fetch and extract TeX source. Returns None if unavailable.
    arxiv e-print serves a tar.gz or gzipped .tex.
    """
    import tarfile
    import io
    import gzip
    
    url = f"{ARXIV_SOURCE_BASE}{arxiv_id}{version}"
    try:
        raw = fetch_binary(url, timeout=60)
    except Exception as e:
        return {"available": False, "url": url, "error": str(e)}
    
    tex_files = {}
    main_tex = None
    
    # Try tar.gz first
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith(".tex"):
                    f = tar.extractfile(member)
                    if f:
                        content = f.read().decode("utf-8", errors="replace")
                        tex_files[member.name] = content
                        # Heuristic: main file contains \documentclass
                        if "\\documentclass" in content and main_tex is None:
                            main_tex = member.name
    except Exception:
        # Try single gzipped .tex
        try:
            content = gzip.decompress(raw).decode("utf-8", errors="replace")
            tex_files["main.tex"] = content
            main_tex = "main.tex"
        except Exception:
            # Try plain text
            try:
                content = raw.decode("utf-8", errors="replace")
                if "\\documentclass" in content or "\\begin{document}" in content:
                    tex_files["main.tex"] = content
                    main_tex = "main.tex"
            except Exception:
                return {"available": False, "url": url, "error": "unrecognized archive format"}
    
    if not tex_files:
        return {"available": False, "url": url, "error": "no .tex files found in archive"}
    
    # Combine all tex for equation + macro extraction
    combined = "\n".join(tex_files.values())
    macros = extract_tex_macros(combined)
    equations = extract_tex_equations(combined)
    
    # Resolve author shorthand in each equation so the TeX rung is
    # directly comparable to the (already-expanded) HTML rung.
    for eq in equations:
        eq["latex_raw"] = eq["latex"]
        eq["latex"] = resolve_macros(eq["latex"], macros)
    
    return {
        "available": True,
        "url": url,
        "main_file": main_tex,
        "file_count": len(tex_files),
        "files": list(tex_files.keys()),
        "macro_count": len(macros),
        "macros": macros,
        "equation_count": len(equations),
        "equations": equations,
    }


def build_provenance_record(arxiv_id: str, version: str, math_records: list,
                            grouped: list = None, tex_source: dict = None) -> dict:
    """Build complete provenance record for a paper."""
    base_id = f"{arxiv_id}{version}"
    
    record = {
        "arxiv_id": arxiv_id,
        "version": version,
        "paper_key": base_id,
        "urls": {
            "abs": f"{ARXIV_ABS_BASE}{arxiv_id}",
            "html": f"{ARXIV_HTML_BASE}{base_id}",
            "pdf": f"{ARXIV_PDF_BASE}{base_id}",
            "source": f"{ARXIV_SOURCE_BASE}{base_id}",
        },
        "math_fragment_count": len(math_records),
        "equations": grouped if grouped is not None else math_records,
        "metadata": {
            "extractor": "arxiv_provenance.py",
            "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "source_type": "arxiv_html_mathml",
        }
    }
    
    if tex_source is not None:
        record["tex_source"] = tex_source
    
    return record


def main():
    parser = argparse.ArgumentParser(description="Extract arxiv paper math provenance")
    parser.add_argument("arxiv_id", help="arXiv ID (e.g., 2006.11239)")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--no-tex", action="store_true", help="Skip TeX source fetch")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    arxiv_id = args.arxiv_id.strip()
    
    # Validate arxiv_id format
    if not re.match(r'^\d{4}\.\d{4,5}$', arxiv_id):
        print(f"ERROR: Invalid arxiv_id format: {arxiv_id}", file=sys.stderr)
        print("Expected format: XXXX.XXXXX (e.g., 2006.11239)", file=sys.stderr)
        sys.exit(1)
    
    print(f"[1/5] Fetching abs page for {arxiv_id}...")
    abs_html = fetch_url(f"{ARXIV_ABS_BASE}{arxiv_id}")
    
    print(f"[2/5] Extracting version...")
    version = extract_version(abs_html, arxiv_id)
    print(f"      Version: {version}")
    
    print(f"[3/5] Fetching HTML source...")
    base_id = f"{arxiv_id}{version}"
    html_content = fetch_url(f"{ARXIV_HTML_BASE}{base_id}")
    
    print(f"[4/5] Extracting math elements...")
    math_records = extract_math_from_html(html_content)
    print(f"      Found {len(math_records)} math fragments")
    
    print(f"[5/5] Grouping equation fragments...")
    grouped = group_equations(math_records)
    display_eqs = sum(1 for g in grouped if g['is_display'])
    print(f"      {len(grouped)} equations ({display_eqs} display)")
    
    # TeX source (top rung of the ladder)
    tex_source = None
    if not args.no_tex:
        print(f"[+] Fetching TeX source (ground-truth rung)...")
        tex_source = try_fetch_tex_source(arxiv_id, version)
        if tex_source.get("available"):
            print(f"      {tex_source['file_count']} .tex files, {tex_source['equation_count']} display environments")
        else:
            print(f"      unavailable: {tex_source.get('error', 'unknown')}")
    
    # Build provenance record
    record = build_provenance_record(arxiv_id, version, math_records, grouped, tex_source)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        print(f"\nOutput written to: {output_path}")
    else:
        print(json.dumps(record, indent=2, ensure_ascii=False))
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Paper: {base_id}")
    print(f"Math fragments: {len(math_records)}")
    print(f"Grouped equations: {len(grouped)}")
    print(f"  Display equations: {display_eqs}")
    print(f"  Inline math: {len(grouped) - display_eqs}")
    if tex_source and tex_source.get("available"):
        print(f"TeX source: {tex_source['file_count']} files, {tex_source['equation_count']} display envs")
        print(f"  Ladder: TeX ({tex_source['equation_count']}) -> HTML ({display_eqs}) -> parser")


if __name__ == "__main__":
    main()
